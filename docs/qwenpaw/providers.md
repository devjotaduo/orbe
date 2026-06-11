# providers

> Package path(s): `src/qwenpaw/providers/` (incl. `src/qwenpaw/providers/oauth/`)

## Purpose

The `providers` area defines QwenPaw's model/credential provider layer: a uniform abstraction over every LLM backend (OpenAI, Anthropic, Google Gemini, DashScope/Aliyun, Ollama, LM Studio, OpenRouter, and ~30 built-in vendor endpoints). Each provider stores connection config (base URL, API key, headers, auth mode) and a list of `ModelInfo`s, knows how to check connectivity, discover and probe models for multimodal capability, and — most importantly — how to construct a concrete agentscope `ChatModelBase` instance for a given model. A singleton `ProviderManager` registers all built-in providers, persists custom/plugin providers and secrets to disk, tracks the active model slot, and is the single entry point the rest of QwenPaw uses to obtain a ready-to-call chat model.

## Architecture

```
ProviderManager (singleton, persistence + registry)
  ├─ builtin_providers   {id -> Provider instance}   PROVIDER_OPENAI, PROVIDER_ANTHROPIC, ...
  ├─ custom_providers    {id -> Provider instance}   user-created, saved to SECRET_DIR/providers/custom
  ├─ plugin_providers    {id -> {info, class}}       registered by plugins
  └─ active_model        ModelSlotConfig             persisted in active_model.json

Provider (ABC, subclass of ProviderInfo pydantic model)
  ├─ OpenAIProvider          ──┬─ OllamaProvider, LMStudioProvider
  │   (OpenAI-compatible HTTP)  ├─ OpenCodeProvider, KiloProvider (free-suffix mixin)
  │                            └─ DashScopeProvider (overrides get_chat_model_instance)
  ├─ AnthropicProvider       (Messages API; MiniMax reuses it)
  ├─ GeminiProvider          (google-genai SDK)
  └─ OpenRouterProvider      (OpenAI-compatible + OAuth)

get_chat_model_instance(model_id) -> agentscope ChatModelBase
  e.g. OpenAIChatModelCompat / AnthropicChatModel / GeminiChatModel / DashScopeChatModel
       (later wrapped by RetryChatModel in agents/model_factory.py)
```

Flow to obtain a callable model: `ProviderManager.get_active_chat_model()` reads the active `ModelSlotConfig`, looks up the `Provider` by `provider_id`, and calls `provider.get_chat_model_instance(model.model)`. The returned agentscope chat model is later wrapped with retry/rate-limit logic (`RetryChatModel`) by `agents/model_factory.py` — that wrapping is *not* done inside this area's factory method.

Persistence lives under `SECRET_DIR/providers/{builtin,custom,plugin}/<id>.json` (dirs chmod `0700`); secret fields (`api_key`) are encrypted via `qwenpaw.security.secret_store` before writing and decrypted on load, with deferred plaintext→encrypted migration.

## Key Modules

### `provider.py` — base abstractions
- `ModelInfo(BaseModel)`: per-model record — `id`, `name`, multimodal flags (`supports_image/video/multimodal`, `probe_source`), `is_free`, `max_tokens`, `max_input_length`, per-model `generate_kwargs`. `ExtendedModelInfo` adds provider/modalities/pricing.
- `ProviderInfo(BaseModel)`: provider config/metadata — `id`, `name`, `base_url`, `api_key`, `chat_model` (the agentscope ChatModel class name, default `"OpenAIChatModel"`), `models`/`extra_models`, `auth_mode` (`api_key`|`auth_token`), `custom_headers`, `generate_kwargs`, `supports_oauth`, flags like `is_local`, `freeze_url`, `require_api_key`, `support_model_discovery`, `meta`.
- `Provider(ProviderInfo, ABC)`: the runtime provider. Abstract: `check_connection`, `fetch_models`, `check_model_connection`, `get_chat_model_instance`. Concrete helpers: `add_model`/`delete_model`/`update_config`/`update_model_config`, `get_effective_generate_kwargs(model_id)` (deep-merges provider + model kwargs, injects `max_tokens`), `get_chat_model_cls()` (resolves `self.chat_model` against `agentscope.model`), `get_info(mock_secret=True)` (masks api_key, re-serializes models to avoid pydantic class-identity issues across dual imports), default `probe_model_multimodal` (returns empty `ProbeResult`).

### `provider_manager.py` — registry, persistence, active model (largest file, ~76 KB)
- Top of file (lines ~50–1150): built-in `ModelInfo` lists and `PROVIDER_*` instances (`PROVIDER_OPENAI`, `PROVIDER_ANTHROPIC`, `PROVIDER_GEMINI`, `PROVIDER_DASHSCOPE`, `PROVIDER_QWENPAW`/`qwenpaw-local`, Aliyun coding/token plans, Kimi, DeepSeek, Zhipu, SiliconFlow, Volcengine, etc.). Each is a plain instance of one of the provider classes with `id`, `base_url`, `models`, flags.
- `class ProviderManager` (singleton via `get_instance()`): `_init_builtins()` registers all `PROVIDER_*`; `get_provider(id)` resolves plugin→builtin→custom (with `_normalize_provider_id` mapping legacy `copaw-local`→`qwenpaw-local`); `list_provider_info`, `update_provider`, `add_custom_provider`/`remove_custom_provider`, `fetch_provider_models`, `activate_model`/`get_active_model`/`save_active_model`/`clear_active_model`, `add_model_to_provider`/`update_model_config`/`delete_model_from_provider`, `probe_model_multimodal`/`maybe_probe_multimodal`, plugin registration (`register_plugin_provider`/`unregister_plugin_provider`), and migration helpers (`_migrate_legacy_providers`, `_migrate_copaw_config`).
- `@staticmethod get_active_chat_model() -> ChatModelBase`: the primary public entry — resolves active provider+model and returns `provider.get_chat_model_instance(model.model)`.

### `openai_provider.py` — OpenAI-compatible base for most providers
`OpenAIProvider(Provider)` uses the `openai` `AsyncOpenAI` client (optionally `langfuse.openai` for tracing when `LANGFUSE_SECRET_KEY` is set). Implements `check_connection`/`fetch_models` (via `models.list`), `check_model_connection` (streaming ping), multimodal image/video probes (`_probe_image_support`, `_probe_video_support`, with semantic colour checks to catch silent text-only models), and `get_chat_model_instance` → `OpenAIChatModelCompat`. Injects DashScope tracking headers (`x-dashscope-agentapp` / `X-DashScope-Cdpl`) when the base URL matches known DashScope endpoints. `_FreeSuffixProviderMixin` + `OpenCodeProvider`/`KiloProvider` mark models free by id suffix (`-free` / `:free`).

### `anthropic_provider.py`
`AnthropicProvider(Provider)` uses `anthropic.AsyncAnthropic`. Supports `auth_mode="auth_token"` (Bearer) via a custom `_StripApiKeyTransport` that removes the `x-api-key` header to avoid double-auth on proxies. `check_connection` falls back from `models.list` to a `messages.create` ping for proxies that lack the models endpoint. `get_chat_model_instance` → agentscope `AnthropicChatModel`. Reused by MiniMax (`PROVIDER_MINIMAX`/`-cn`).

### `gemini_provider.py`
`GeminiProvider(Provider)` uses the `google.genai` SDK; strips the `models/` prefix from model ids; `get_chat_model_instance` → agentscope `GeminiChatModel`.

### `dashscope_provider.py`
`DashScopeProvider(OpenAIProvider)` reuses OpenAI-compat connection/probing but overrides `get_chat_model_instance` to build the agentscope **2.0 native** `DashScopeChatModel(credential=DashScopeCredential(api_key, base_url), parameters=DashScopeChatModel.Parameters(...), ...)`. `_DashScopeChatModelCompat.__new__` dynamically subclasses `DashScopeChatModel` to inject tracking headers into every `_call_api` via `extra_headers`.

### `openai_chat_model_compat.py`
`OpenAIChatModelCompat(OpenAIChatModel)` — a subclass of agentscope's `OpenAIChatModel` that adds tolerant streaming tool-call handling: `_sanitize_tool_call`, `_clone_with_overrides`, and integration with `qwenpaw.local_models.tag_parser` (`parse_tool_calls_from_text`) so local/loose models that emit tool calls as text are still parsed. This is the concrete model returned by most OpenAI-compatible providers.

### `ollama_provider.py` / `lmstudio_provider.py`
Local-hosting subclasses of `OpenAIProvider`. `OllamaProvider` normalizes base URL (`OLLAMA_HOST` default, strips/re-adds `/v1`) and overrides `check_model_connection` to match against `fetch_models`. `LMStudioProvider` only overrides `check_model_connection` similarly.

### `openrouter_provider.py`
`OpenRouterProvider(OpenAIProvider)` — OpenAI-compatible with model discovery and OAuth support (pairs with `oauth/openrouter_flow.py`).

### `retry_chat_model.py` / `rate_limiter.py`
`RetryChatModel(ChatModelBase)` transparently retries transient LLM errors (`RETRYABLE_STATUS_CODES = {429,500,502,503,504,529}`) with exponential backoff, and coordinates a global concurrency semaphore + QPM limit via `LLMRateLimiter`/`get_rate_limiter`. Tuned by `LLM_*` constants from `qwenpaw.constant`. Note: it is applied by `agents/model_factory.py` (`RetryChatModel(...)` at line ~1094), not by the provider factory methods themselves.

### `multimodal_prober.py` / `model_capability_cache.py` / `capability_baseline.py`
`multimodal_prober.py` holds shared probe constants (`_PROBE_IMAGE_B64`, `_PROBE_VIDEO_B64`/`_URL`, prompts) and the `ProbeResult` dataclass plus `evaluate_image_probe_answer` / `_is_media_keyword_error`; the actual probe HTTP calls live in each provider. `model_capability_cache.py` caches probe results; `capability_baseline.py` (~28 KB) holds documented capability baselines.

### `oauth/` — one-click auth flows
- `base.py`: `OAuthFlow(ABC)` (`start`/`exchange`/`refresh`/`get_credential_dict`), result models `OAuthStartResult`/`OAuthTokenResult`, and PKCE helpers (`generate_code_verifier`, `generate_code_challenge`, `generate_state`).
- `openrouter_flow.py`: `OpenRouterOAuthFlow` concrete flow. `session_store.py`: `OAuthSessionStore` for in-flight state.

## Entry Points & Public API

- Package exports (`providers/__init__.py`): `Provider`, `ProviderInfo`, `ModelInfo`, `ProviderManager`.
- `ProviderManager.get_instance()` — singleton accessor used across the app (`app/_app.py`, `config/config.py`, `cli/providers_cmd.py`, `app/runner/control_commands/model_handler.py`).
- `ProviderManager.get_active_chat_model() -> ChatModelBase` — the main way to get a usable model.
- `Provider.get_chat_model_instance(model_id)` — per-provider factory returning an agentscope chat model.
- `oauth/__init__.py` exports `OAuthFlow`, `OAuthStartResult`, `OAuthTokenResult`, `OAuthSessionStore`, `OpenRouterOAuthFlow`.

## AgentScope Integration

This area is the bridge between QwenPaw config and agentscope's model layer (built on agentscope 1.0.20; for the v2 model/credential concepts see [../agentscope-v2/overview.md](../agentscope-v2/overview.md)).

- `agentscope.model.ChatModelBase` — the abstract type every `get_chat_model_instance` returns; `RetryChatModel` also subclasses it.
- Concrete agentscope chat models constructed here: `OpenAIChatModel` (subclassed as `OpenAIChatModelCompat`), `AnthropicChatModel`, `GeminiChatModel`, `DashScopeChatModel` (with its `.Parameters`).
- `agentscope.credential.DashScopeCredential` — used by `DashScopeProvider` to build the native 2.0 `DashScopeChatModel(credential=...)`. This is the clearest "credential → chat model" mapping in the codebase.
- `Provider.get_chat_model_cls()` resolves the string in `ProviderInfo.chat_model` against the `agentscope.model` namespace via `getattr`, so any agentscope ChatModel class name is usable for custom providers.
- `agentscope.model._model_response.ChatResponse` is consumed in the compat/retry layers.
- `agentscope_runtime.engine.schemas.exception` (`ModelNotFoundException`, `RateLimitExceededException`) is used by `provider_manager.py` and `retry_chat_model.py`.

## Extension Points & Gotchas

- **Adding a provider type:** subclass `Provider` (or `OpenAIProvider` if the endpoint is OpenAI-compatible) and implement the four abstract methods. For a built-in, add a `PROVIDER_*` instance and register it in `ProviderManager._init_builtins()`. For OpenAI-compatible endpoints you usually only override `get_chat_model_instance`.
- **`chat_model` string must resolve in `agentscope.model`:** `get_chat_model_cls()` does `getattr(agentscope.model, self.chat_model, None)` and raises `ProviderError` if missing. Custom providers can set any valid agentscope ChatModel class name.
- **`generate_kwargs` precedence:** `get_effective_generate_kwargs` deep-merges provider-level kwargs (base) with model-level kwargs (override) and injects the model's `max_tokens` if absent. Mutate the returned dict freely — it is always a fresh copy. Note DashScope/Anthropic only forward a whitelist of keys into their native parameter objects.
- **Secrets & persistence:** `api_key` (and fields in `PROVIDER_SECRET_FIELDS`) are encrypted on disk; never write plaintext secrets yourself — go through `_save_provider`/`_save_plugin_provider`. `get_info(mock_secret=True)` masks the key for UI — do not log raw `provider.api_key`.
- **Pydantic dual-import hazard:** `get_info` and `update_config` deliberately re-serialize `ModelInfo` via `model_dump()`/`model_validate` because the same module can be loaded under two import paths (PYTHONPATH + pip install), producing class-identity mismatches. Preserve this pattern when touching model serialization.
- **Anthropic `auth_token` mode:** when `auth_mode="auth_token"`, a `_StripApiKeyTransport` removes `x-api-key`; both `_client()` and `get_chat_model_instance` must stay consistent or proxies may reject dual-auth requests.
- **Multimodal probing is semantic, not just API-error based:** image/video probes verify the model actually *perceives* a known-colour test asset, because some models (e.g. qwen3-max via OpenAI-compat) silently accept media and ignore it. The image probe must pass before the video probe runs. Probe HTTP lives per-provider; only constants/eval helpers are shared in `multimodal_prober.py`.
- **Retry/rate-limit is applied downstream:** providers return a bare agentscope model. Concurrency/backoff comes from `RetryChatModel` wrapping in `agents/model_factory.py`, not from this area — don't add retry logic inside `get_chat_model_instance`.
- **Legacy id migration:** `copaw-local` is silently mapped to `qwenpaw-local` in `get_provider`/active-model load; keep both working when renaming the local provider.
- `capability_baseline.py` is large and was not read in full — treat its exact contents as unverified beyond "documented capability baselines."
