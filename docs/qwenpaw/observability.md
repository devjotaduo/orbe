# token_usage, tokenizer, agent_stats

> Package path(s): `src/qwenpaw/token_usage/`, `src/qwenpaw/tokenizer/`, `src/qwenpaw/agent_stats/`
> Related: `src/qwenpaw/agents/tools/get_token_usage.py`, `src/qwenpaw/agents/utils/estimate_token_counter.py`, `src/qwenpaw/app/routers/token_usage.py`, `src/qwenpaw/app/routers/agent_stats.py`

## Purpose

This area is qwenpaw's usage accounting and statistics layer. `token_usage/` transparently records prompt/completion token counts for every LLM call (by wrapping the agentscope chat model), buffers them in memory, and periodically flushes a per-day/per-`provider:model` aggregate to a JSON file on disk, then serves summaries/details back to the console UI and to an in-agent tool. `agent_stats/` computes higher-level conversation statistics (messages, sessions, channels, tool calls) by scanning the workspace's chat/session files and fuses in the token totals from `token_usage`. `tokenizer/` is **not Python** — it is a bundled HuggingFace-format Qwen tokenizer data directory (`tokenizer.json`, `vocab.json`, `merges.txt`, `tokenizer_config.json`) packaged with the app; qwenpaw's own runtime token counting uses a lightweight character-based estimator instead (see Gotchas).

## Architecture

LLM call path (recording):

```
model_factory.create_*  -> TokenRecordingModelWrapper(provider_id, model)   # wraps a ChatModelBase
       (then wrapped again by RetryChatModel)
  __call__ / _wrap_stream
       -> _record_usage(ChatUsage)
            -> get_token_usage_manager().enqueue(_UsageEvent)   # sync, fire-and-forget
            -> _store_usage(...)  # per-session snapshot for ACP _meta
```

Buffer/persistence path (async producer–consumer):

```
TokenUsageManager (singleton)
  └─ TokenUsageBuffer(path = WORKING_DIR / TOKEN_USAGE_FILE)
       asyncio.Queue  --consumer_loop--> _disk_cache (dict)
                       --flush_loop (every flush_interval s)--> storage.save_data_sync (atomic tmp->replace)
       _seed_cache <-- storage.load_data (on first access)
```

Query path (serving):

```
TokenUsageManager.get_summary / get_details
  -> buffer.get_merged_data()   # deepcopy(_disk_cache) + peek pending queue items
  -> _query()  -> [TokenUsageRecord]  -> aggregate -> TokenUsageSummary
```

`agent_stats` sits on top: `AgentStatsService.get_summary()` scans `workspace_dir/chats.json` and `workspace_dir/sessions/<channel>/*.json` concurrently, derives message/session/tool-call counts, then calls `get_token_usage_manager().get_summary()` and merges its `by_date` totals into the daily rows.

Lifecycle is owned by the app: `app/_app.py` calls `token_usage_manager.start(flush_interval=10)` on startup and `await token_usage_manager.stop()` on shutdown.

## Key Modules

### `token_usage/manager.py` — `TokenUsageManager` (singleton orchestrator)
Thin orchestrator over `TokenUsageBuffer`. Holds the process-wide instance.
- Pydantic models: `TokenUsageStats` (`prompt_tokens`, `completion_tokens`, `call_count`), `TokenUsageRecord` (adds `date`, `provider_id`, `model`), `TokenUsageByModel`, `TokenUsageByDateModel`, `TokenUsageSummary` (`total_prompt_tokens`, `total_completion_tokens`, `total_calls`, `by_model: dict[str, TokenUsageByModel]`, `by_date: dict[str, TokenUsageStats]`).
- `start(flush_interval: int = 10) -> None` — start background buffer tasks (must be called from async context).
- `async stop() -> None` — drain + final flush.
- `enqueue(event: _UsageEvent) -> None` — sync hot-path entry used by the wrapper.
- `async record(provider_id, model_name, prompt_tokens, completion_tokens, at_date=None) -> None` — async convenience wrapper around `enqueue` (tests/tools).
- `async get_summary(start_date=None, end_date=None, model_name=None, provider_id=None) -> TokenUsageSummary` — defaults to last 30 days.
- `async get_details(...) -> list[TokenUsageRecord]` — raw per-day per-model rows.
- `get_instance()` / module fn `get_token_usage_manager() -> TokenUsageManager`.

### `token_usage/buffer.py` — `TokenUsageBuffer`, `_UsageEvent`
Async producer–consumer write buffer.
- `_UsageEvent(NamedTuple)`: `provider_id`, `model_name`, `prompt_tokens`, `completion_tokens`, `date_str` (YYYY-MM-DD, precomputed by producer), `now_iso`.
- `start()` spawns `_consumer_loop` (drains queue into `_disk_cache`) and `_flush_loop` (sleeps `flush_interval`, calls `_flush_once`).
- `enqueue(event)` uses `put_nowait`; on `QueueFull` it logs a warning and **drops** the event.
- `async get_merged_data() -> dict` returns `deepcopy(_disk_cache)` folded with a peek of pending (not-yet-consumed) queue items via `_apply_event`.
- `async stop()` cancels flush, `await queue.join()`, cancels consumer, then forces a final flush.
- Cache shape: `{ "YYYY-MM-DD": { "provider:model": {provider_id, model_name, prompt_tokens, completion_tokens, call_count} } }`. Module fn `_apply_event(cache, ev)` accumulates one event (increments `call_count` by 1 per event).

### `token_usage/model_wrapper.py` — `TokenRecordingModelWrapper(ChatModelBase)`
Wraps a real agentscope `ChatModelBase` to record usage on each call.
- `__init__(provider_id, model)` — copies `model_name`/`stream` from the wrapped model.
- `async __call__(messages, tools, tool_choice, structured_model, **kwargs)` — delegates to the inner model; for `AsyncGenerator` results it returns `_wrap_stream`, else records `result.usage`. **Also drops `tool_choice="auto"` → `None`** for vLLM compatibility (vLLM without `--enable-auto-tool-choice` rejects `auto`).
- `_record_usage(usage: ChatUsage | None)` — reads `input_tokens`/`output_tokens`, enqueues a `_UsageEvent`, and stores a per-session snapshot.
- Class-level `_usage_by_session: dict[str, dict]` plus `pop_usage_for_session(session_id)` / `_store_usage(...)` — used by the ACP server (`agents/acp/server.py`) to surface per-call usage in QwenCode-style `_meta`. Session id comes from `app.agent_context.get_current_session_id()`.

### `token_usage/storage.py` — file I/O
- `async load_data(path) -> dict` — reads JSON via `aiofiles`; returns `{}` on missing/corrupt file (logs warning).
- `save_data_sync(path, data) -> None` — **atomic** write (`path.with_suffix(".tmp")` then `os.replace`), intentionally sync so the buffer can call it via `asyncio.to_thread`.

### `token_usage/__init__.py` — public exports
Exports `TokenUsageByModel`, `TokenUsageRecord`, `TokenUsageStats`, `TokenUsageSummary`, `get_token_usage_manager`, `TokenRecordingModelWrapper`, `_UsageEvent`.

### `agent_stats/models.py` — Pydantic models
`ChannelStats` (channel + session/message counts), `DailyStats` (per-day chats/sessions/messages/tokens/llm_calls/tool_calls), `AgentStatsSummary` (totals + `by_date: list[DailyStats]` + `channel_stats: list[ChannelStats]` + `start_date`/`end_date`).

### `agent_stats/service.py` — `AgentStatsService`
- `async get_summary(workspace_dir: Path, start_date: date, end_date: date) -> AgentStatsSummary`.
- Loads chats via `app.runner.repo.JsonChatRepository(chats_file).list_chats()` for the `chats` count.
- Scans `sessions/<channel>/*.json` concurrently (`asyncio.gather`, bounded by a `Semaphore((os.cpu_count() or 4) * 2)`), reading with `orjson`.
- Cheap skips: `_should_skip_by_mtime` (file mtime before range) and `_should_skip_by_content_range` (first/last message timestamp outside range).
- `_process_session_file` walks `agent.memory.memories` (falls back to `agent.memory.content`), counting user/assistant messages and `tool_use` content blocks; populates `daily_stats`, `channel_stats`, `active_sessions`.
- Fuses token totals from `get_token_usage_manager().get_summary()` into `prompt_tokens`/`completion_tokens`/`llm_calls` per day. Singleton accessor `get_agent_stats_service()`.

### `tokenizer/` — bundled tokenizer data (no Python)
HuggingFace-format Qwen tokenizer assets: `tokenizer.json` (~7 MB), `vocab.json`, `merges.txt`, `tokenizer_config.json`. Shipped as package data (`pyproject.toml` `tokenizer/**`, PyInstaller `scripts/pack-tauri/qwenpaw.spec` maps `tokenizer -> qwenpaw/tokenizer`). No module under `src/qwenpaw` loads it by path; it is present for offline/bundled tokenization by external consumers or the packaged runtime. (No in-repo Python loader was found — if one is expected, it is not in this area.)

## Entry Points & Public API

- `get_token_usage_manager()` — the singleton; `start`/`stop` (lifecycle, called from `app/_app.py`), `enqueue`/`record` (write), `get_summary`/`get_details` (read).
- `TokenRecordingModelWrapper` — installed in `agents/model_factory.py` (`wrapped_model = TokenRecordingModelWrapper(provider_id, model)`), then wrapped by `RetryChatModel`. Its `pop_usage_for_session` is consumed by `agents/acp/server.py`.
- HTTP API: `app/routers/token_usage.py` (`GET /token-usage`, `GET /token-usage/details`) and `app/routers/agent_stats.py` (`GET /agent-stats`); both registered in `app/routers/__init__.py`.
- In-agent tool: `agents/tools/get_token_usage.py::get_token_usage(days, model_name, provider_id)` returns a formatted `ToolResponse`; wired as builtin `get_token_usage` in `agents/react_agent.py` and `config/config.py`.
- `get_agent_stats_service()` and `AgentStatsSummary` / `ChannelStats` / `DailyStats`.
- `EstimatedTokenCounter` (in `agents/utils/estimate_token_counter.py`) — the runtime token-counting primitive.

## AgentScope Integration

- `TokenRecordingModelWrapper` subclasses **`agentscope.model.ChatModelBase`** and consumes `agentscope.model._model_response.ChatResponse` and `agentscope.model._model_usage.ChatUsage` (`input_tokens`/`output_tokens`). See [model](../agentscope-v2/building-blocks/model.md) and [chat-and-model](../agentscope-v2/api-reference/chat-and-model.md).
- `EstimatedTokenCounter` subclasses **`agentscope.token.TokenCounterBase`** (implements `async count(text) -> int`).
- The in-agent tool returns **`agentscope.tool.ToolResponse`** with **`agentscope.message.TextBlock`**. See [tool](../agentscope-v2/building-blocks/tool.md).
- `agent_stats` reads agentscope-shaped session memory (the `agent.memory.memories` list and `tool_use` content blocks). See [context](../agentscope-v2/building-blocks/context.md) and [sessions](../agentscope-v2/api-reference/sessions.md).

> Note: this fork targets agentscope **1.0.20**; the linked v2 docs are a reference for concepts/APIs, not an exact version match (some symbols above are private `_model_*` modules).

## Extension Points & Gotchas

- **Singleton lifecycle**: `TokenUsageManager` is a process-wide singleton. `start()`/`stop()` are owned by `app/_app.py`. Recording (`enqueue`) is safe before `start()` (events sit in the queue), but the background flush only runs after `start()`; nothing persists until then. `start()` recreates the buffer **only** if `flush_interval != 10` — passing the default twice keeps the existing buffer.
- **Fire-and-forget + lossy on overload**: `_record_usage` never awaits and `enqueue` drops events on `QueueFull`. Token accounting is best-effort, not exact billing. A crash before a flush loses up to `flush_interval` seconds (default 10s) of buffered events; `stop()` does a final flush, so use it on graceful shutdown.
- **`call_count` semantics**: incremented by exactly 1 per `_UsageEvent` in `_apply_event`; it is a count of recorded usage events (≈ LLM calls), not tool calls.
- **Streaming**: only the **last** chunk carrying a non-null `usage` is recorded (`_wrap_stream`). If the provider never emits usage in the stream, nothing is recorded for that call.
- **`tool_choice="auto"` rewrite**: the wrapper silently rewrites `auto` → `None`. Anything relying on an explicit `auto` being forwarded to the model will not get it.
- **Persisted file format is a contract**: the on-disk JSON shape `{date: {"provider:model": {...}}}` is read back by `load_data` and merged in `_apply_event`. Changing keys breaks historical reads. File path = `WORKING_DIR / TOKEN_USAGE_FILE` (default `token_usage.json`, overridable via `QWENPAW_TOKEN_USAGE_FILE`).
- **`agent_stats` is filesystem-scan-based** and can be expensive on large workspaces; it relies on mtime/content-range pre-filters and a bounded semaphore. It assumes the agentscope memory layout (`agent.memory.memories` / `.content`, message `role`, `timestamp` prefix `[:10]` as the date, `tool_use` blocks). Schema drift in session files silently undercounts (errors are caught and logged at debug).
- **Token counts in `agent_stats` come from `token_usage`**, not by re-tokenizing transcripts — a day with no recorded usage events shows zero tokens even if messages exist.
- **The `tokenizer/` data dir is unused by this area's runtime counting** — qwenpaw counts via `EstimatedTokenCounter` (byte-length / divisor, default 4). Don't assume edits to the tokenizer data change recorded/estimated counts.
