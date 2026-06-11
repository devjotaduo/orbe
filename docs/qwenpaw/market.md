# market

> Package path(s): `src/qwenpaw/market/` — `__init__.py`, `schema.py`, `service.py`, and `providers/` (`__init__.py`, `base.py`, `clawhub.py`, `modelscope.py`, `aliyun.py`)

## Purpose

The `market` package is qwenpaw's **skill/plugin marketplace search layer**. It fans a single user query out across several remote skill registries (ClawHub, ModelScope, Aliyun AgentExplorer), normalizes their heterogeneous responses into one `MarketResult` dataclass, and returns a merged, paginated result set with per-provider availability and "load more" metadata. It is a read-only discovery layer — it surfaces remote skills for the UI; actual fetching/installation of a skill lives elsewhere (in `agents.skill_system.hub`).

## Architecture

Three layers, cleanly separated:

```
app/routers/market.py  (FastAPI: /market/providers, /market/search)
        │  calls list_providers() / search_market()
        ▼
service.py             (orchestration: fan-out, gather, merge, cap)
        │  iterates PROVIDERS, calls provider.search(...)
        ▼
providers/             (one module per remote source)
  base.py     → MarketProvider Protocol + MARKET_SEARCH_TIMEOUT_S
  clawhub.py  → ClawHubProvider   (reuses skill_system.hub.search_hub_skills)
  modelscope.py → ModelScopeProvider (reuses skill_system.hub.http_json_get)
  aliyun.py   → AliyunProvider    (signed Alibaba Cloud SDK client)
  __init__.py → PROVIDERS registry dict
        │  every provider returns
        ▼
schema.py              (MarketResult, MarketSearchError, ProviderInfo)
```

Flow of a search: the router validates that requested provider keys exist in `PROVIDERS`, then calls `search_market(query, provider_pages, limit, lang)`. `search_market` builds one coroutine per selected provider via `_run_one`, runs them concurrently with `asyncio.gather`, and concatenates the results. Each provider independently does its own paging (page numbers come per-provider in `provider_pages`), so the registries advance independently. Failures are isolated: a provider that raises is converted to a `MarketSearchError` rather than failing the whole request.

## Key Modules

### `schema.py` — normalized data types
Three frozen dataclasses, the shared contract across the package:
- `MarketResult` — one skill: `source`, `slug`, `name`, `description`, `source_url`, `version`, `author`, `icon_url`, and optional `stats: dict[str, str | int] | None` (per-provider extras like downloads/likes/category/updated_at, rendered in the UI).
- `MarketSearchError(provider: str, message: str)` — a provider-level failure surfaced to the UI.
- `ProviderInfo(key, label, available: bool, reason: str | None)` — availability descriptor for the provider list.

### `service.py` — orchestration
- `list_providers() -> list[ProviderInfo]` — maps every entry in `PROVIDERS` to a `ProviderInfo`, calling each provider's `available()`.
- `async search_market(query, provider_pages: dict[str, int], limit=10, lang="en") -> tuple[list[MarketResult], list[MarketSearchError], dict[str, tuple[bool, int]]]` — caps `limit` to `_MAX_LIMIT = 50`, filters `provider_pages` to known keys, fans out concurrently, returns `(results, errors, by_provider)` where `by_provider[key] = (has_more, total)`.
- `async _run_one(...)` — checks `available()`, calls `provider.search(...)`, traps any `Exception` into a `MarketSearchError` (logged at WARNING).
- `_supported_kwargs(func, **candidates)` — introspects a provider's `search` signature so optional kwargs (currently `lang`) are only passed to providers that declare them (or accept `**kwargs`). This is why `ModelScopeProvider.search` can take `lang` while the others don't.

### `providers/base.py` — provider contract
- `MARKET_SEARCH_TIMEOUT_S = 15.0` — single source of truth for the per-provider search budget.
- `MarketProvider` — a `@runtime_checkable` `Protocol` with attributes `key: str`, `label: str`, and methods `available() -> tuple[bool, str | None]` and async `search(query, limit, page) -> tuple[list[MarketResult], bool, int | None]` (returns `(results, has_more, total)`).

### `providers/__init__.py` — registry
- `PROVIDERS: dict[str, MarketProvider]` keyed by each provider's `.key`, in order: `clawhub`, `modelscope`, `aliyun`. Adding a provider = drop a module exposing a module-level `provider` instance and append it here.

### `providers/clawhub.py` — `ClawHubProvider` (key `clawhub`, label `ClawHub`)
Always available. Delegates to `qwenpaw.agents.skill_system.hub.search_hub_skills` with an over-fetch limit (`_OVERFETCH_LIMIT = 500`), then **paginates in-memory** (`all_results[start:end]`) since the upstream `/search` endpoint has no paging. `has_more` = `end < total`.

### `providers/modelscope.py` — `ModelScopeProvider` (key `modelscope`, label `ModelScope`)
Always available. Calls the public ModelScope OpenAPI (`GET /openapi/v1/skills?search=&page_number=&page_size=`) via `hub.http_json_get`. Enforces the upstream `_MAX_PAGE_SIZE = 100`. Locale-aware: `_localized(item, field, lang)` picks `locales[lang][field]` for `description`/`category`, falling back across `en`/`zh`. `_to_market_result` builds `stats` from `downloads`, `view_count`, `category`. This is the only provider that accepts a `lang` kwarg.

### `providers/aliyun.py` — `AliyunProvider` (key `aliyun`, label `Aliyun`)
Conditionally available — `available()` returns `False` with a human-readable reason if the env vars `ALIBABA_CLOUD_ACCESS_KEY_ID` / `ALIBABA_CLOUD_ACCESS_KEY_SECRET` are missing or the `alibabacloud-*` packages aren't installed. Uses a lazily-built, thread-safe cached `tea_openapi` client (`_get_client`) with ACS3-HMAC-SHA256 signing. Upstream `SearchSkills` is **cursor-paginated** (`nextToken`); the provider walks tokens forward from page 1 to the requested page (capped by `_MAX_PAGE_WALK = 50`), which means deep pages cost multiple signed round-trips. Exposes helpers `call_aliyun_action_async` / `call_aliyun_action` reused by `agents.skill_system.hub` (which imports from this module at `hub.py:1749`).

## Entry Points & Public API

`src/qwenpaw/market/__init__.py` re-exports the stable surface:
- `search_market`, `list_providers` (from `service`)
- `MarketResult`, `MarketSearchError`, `ProviderInfo` (from `schema`)
- `MARKET_SEARCH_TIMEOUT_S` (from `providers.base`)

**Primary consumer:** `src/qwenpaw/app/routers/market.py` (FastAPI router, prefix `/market`) — `GET /market/providers` → `list_providers()`, `POST /market/search` → `search_market()`. It validates provider keys against `PROVIDERS` (imported from `...market.providers`) and maps the dataclasses to Pydantic specs (`MarketResultSpec`, `ProviderInfoSpec`, `MarketSearchResponse`).

**Cross-package coupling:** `agents.skill_system.hub` imports Aliyun helpers from `qwenpaw.market.providers.aliyun` and synthesizes/parses the Aliyun detail URLs that this package produces (`hub.py:1021`, `hub.py:1749`). The dependency between `market` and `skill_system.hub` is bidirectional: providers reuse `hub`'s HTTP helpers (`search_hub_skills`, `http_json_get`) while `hub` reuses the Aliyun signed-call helpers.

## AgentScope Integration

This package does **not** use agentscope directly. Its remote-access plumbing comes from qwenpaw's own `agents.skill_system.hub` (httpx-based helpers) and the Alibaba Cloud `tea_openapi` SDK — not from agentscope's model/agent/tool building blocks. No link to `../agentscope-v2/` applies here. (For how discovered skills are actually loaded and run as agentscope tools, see the `skill_system` area, which is the package that bridges into agentscope.)

## Extension Points & Gotchas

- **Adding a provider:** create `providers/<name>.py` exposing a module-level `provider` instance that satisfies the `MarketProvider` Protocol (`key`, `label`, `available()`, async `search()`), then append it to `PROVIDERS` in `providers/__init__.py`. Because `MarketProvider` is a `Protocol`, you do not subclass it. The router's key-validation and the service's fan-out pick it up automatically.
- **Optional kwargs:** `service._supported_kwargs` only forwards `lang` (and future candidate kwargs) to providers whose `search` signature declares the parameter or accepts `**kwargs`. If you add a provider that needs `lang`, declare it explicitly in the signature like ModelScope does.
- **Per-provider paging is non-uniform.** ClawHub paginates in-memory after over-fetching; ModelScope is page-based with a hard 100 page-size; Aliyun is cursor-based and walks tokens (deep pages = many signed calls, capped at 50). The `(has_more, total)` contract hides this, but `total` may be `0`/unknown for some providers (`service.py` coerces non-positive totals to `0`).
- **Error isolation:** any exception inside a provider's `search` is swallowed into a `MarketSearchError` by `_run_one`; it will not propagate. Conversely, an unavailable provider short-circuits to an error before its `search` is called.
- **Timeout budget** is centralized in `MARKET_SEARCH_TIMEOUT_S` (15s) — change it in `base.py`, not per-provider, to keep them in sync.
- **Aliyun availability is environment-dependent.** It will silently appear as unavailable (with a `reason`) if AK/SK env vars or the SDK packages are absent; tests/local runs without credentials will only see ClawHub + ModelScope results.
- **`limit` is double-capped:** the router constrains it to `1..50` via Pydantic and `search_market` caps again to `_MAX_LIMIT = 50` — keep these aligned if either changes.
