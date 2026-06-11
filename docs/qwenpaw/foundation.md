# utils, _compat, top-level

> Package path(s): `src/qwenpaw/utils/`, `src/qwenpaw/_compat/`, and the top-level modules `src/qwenpaw/__init__.py`, `src/qwenpaw/__main__.py`, `src/qwenpaw/__version__.py`, `src/qwenpaw/constant.py`, `src/qwenpaw/schemas.py`, `src/qwenpaw/exceptions.py`

## Purpose

This is the shared foundation layer of qwenpaw: package bootstrap and logging setup (`__init__.py`), the canonical configuration / constants surface (`constant.py`), the streaming envelope protocol consumed by every channel (`schemas.py`), the business-exception hierarchy plus an LLM-error converter (`exceptions.py`), backward-compat shims for agentscope 1.x on-disk session formats (`_compat/`), and a grab-bag of cross-cutting helpers (`utils/`) for system info, subprocess management, logging, HTTP loopback detection, stdio sanitizing, telemetry, console-asset discovery, and the startup banner. Almost every other subpackage imports from here.

## Architecture

Import-time bootstrap flows through `__init__.py`: it loads persisted env vars via `qwenpaw.envs.load_envs_into_environ()` (best-effort, swallows failures into a warning), then calls `utils.logging.setup_logger()` with the level from `QWENPAW_LOG_LEVEL`. `constant.py` is the env-reading hub — `EnvVarLoader` (typed getters with bounds) and `_get_env` (with automatic `COPAW_` legacy fallback) resolve every `QWENPAW_*` knob and derive paths like `WORKING_DIR`, `SECRET_DIR`, `MEMORY_DIR`. `utils.logging` imports `PROJECT_NAME` / `WORKING_DIR` from `constant.py`, so `constant.py` is the lowest layer.

```
__init__.py  ──(load_envs)──>  envs.load_envs_into_environ
     │
     └──> utils.logging.setup_logger ──> constant.{PROJECT_NAME,WORKING_DIR}

schemas.py (Message/Content/AgentRequest/AgentResponse)  ──>  channels + runtime.stream_query
exceptions.py (convert_model_exception)  ──>  runtime + providers + local_models
_compat/__init__ (monkey-patches agentscope.message.Msg) ──> _compat.message.msg_from_dict ──> /load_history
```

## Key Modules

### `__init__.py`
Package entry. Side-effects at import: env bootstrap (`load_envs_into_environ`), logger setup, and a debug timing log. Defines the fallback constant `LOG_LEVEL_ENV = "QWENPAW_LOG_LEVEL"`. Env-bootstrap failures are non-fatal (captured in `_bootstrap_err`, logged as a warning).

### `__main__.py`
Enables `python -m qwenpaw`. Imports `cli` from `qwenpaw.cli.main` and invokes it.

### `__version__.py`
Single source of truth: `__version__ = "1.1.11"`. Read by `utils/telemetry.py` and surfaced through the CLI.

### `constant.py`
Configuration hub. Key public symbols:
- `EnvVarLoader` — static methods `get_bool(env_var, default)`, `get_int(env_var, default, min_value, max_value)`, `get_float(env_var, default, min_value, max_value, allow_inf)`, `get_str(env_var, default)`. All route through `_get_env`, which falls back from a `QWENPAW_*` key to the corresponding legacy `COPAW_*` key.
- Path constants: `WORKING_DIR` (priority: `QWENPAW_WORKING_DIR` env → existing `~/.copaw` → `~/.qwenpaw`), `SECRET_DIR`, `MEMORY_DIR`, `BACKUP_DIR`, `MODELS_DIR`, `PLUGINS_DIR`, `CUSTOM_CHANNELS_DIR`, `DEFAULT_MEDIA_DIR`, `DOCS_DIR` (resolved by `_resolve_docs_dir`).
- Identity / files: `PROJECT_NAME = "QwenPaw"`, `CONFIG_FILE`, `JOBS_FILE`, `CHATS_FILE`, `TOKEN_USAGE_FILE`, `HEARTBEAT_FILE`, `DEBUG_HISTORY_FILE`.
- Builtin QA agent: `BUILTIN_QA_AGENT_ID = "QwenPaw_QA_Agent_0.2"`, `LEGACY_QA_AGENT_ID`, `SUPPORTED_AGENT_LANGUAGES` (discovered from `agents/md_files/`, defaults `{"en","zh","ru"}`).
- LLM tuning: `LLM_MAX_RETRIES`, `LLM_BACKOFF_BASE/CAP`, `LLM_MAX_CONCURRENT`, `LLM_MAX_QPM`, `LLM_RATE_LIMIT_PAUSE/JITTER`, `LLM_ACQUIRE_TIMEOUT`.
- Tool-guard timeouts, `TRUNCATION_NOTICE_MARKER = "<<<TRUNCATED>>>"`, `MEDIA_UNSUPPORTED_PLACEHOLDER`.

### `schemas.py`
qwenpaw's own streaming envelope protocol — explicitly "independent of agentscope's internal event types". Enums: `Role`, `MessageType`, `RunStatus`, `ContentType`. Content blocks (all pydantic, `extra="allow"`): `TextContent`, `ImageContent`, `AudioContent`, `VideoContent`, `FileContent`, `DataContent`, `RefusalContent`, unioned as `Content`. Tool payloads: `FunctionCall`, `FunctionCallOutput`. The central `Message` model has `id`/`type`/`role`/`content`/`status`/`metadata` and chainable methods `add_content(*, new_content)`, `completed()`, `in_progress()`; a `field_validator` coerces raw dict content items to typed `*Content` subclasses via `_CONTENT_TYPE_REGISTRY` / `_coerce_content_item`. Envelopes: `Event`, `AgentRequest`, `AgentResponse`. The runner builds an empty `Message`, calls `add_content` repeatedly, then `completed()`.

### `exceptions.py`
Business exceptions subclassing agentscope-runtime base types: `ProviderError`, `ModelFormatterError`, `SystemCommandException`, `SkillsError`, `AgentStateError` (extend `AgentRuntimeErrorException`), and `ChannelError` (extends `ExternalServiceException`). The load-bearing function is `convert_model_exception(exc, model_name=None) -> AgentRuntimeErrorException`: a 3-level classifier that (0) routes non-model errors to `UnknownAgentException`, special-cases pydantic `ValidationError` → `ModelExecutionException`, then maps by HTTP status code (401/403→unauthorized, 429→quota) and by keyword (auth, rate-limit, timeout, context-length), defaulting to `ModelExecutionException`. Helpers `_is_model_related_error`, `_extract_error_summary`, `_append_error_detail`.

### `_compat/__init__.py` + `_compat/message.py`
agentscope 1.x backward-compat. `__init__.py` runs `_install_msg_dict_shim()` at import, monkey-patching `agentscope.message.Msg` with `to_dict` (= `model_dump`), a `from_dict` classmethod (delegates to `msg_from_dict`), and a read-only `timestamp` property aliasing 2.0's `created_at` (ISO `T` → space). `message.py` exports `msg_from_dict(data)`: rehydrates 1.x session JSON — renames `timestamp`→`created_at`, coerces legacy `image/audio/video` blocks to `DataBlock` and `tool_use`→`ToolCallBlock` (`_coerce_block` / `_coerce_source`), promotes `system`/`user` messages carrying tool blocks to `assistant` (2.0 role validation), and drops unknown fields. Used by `agents/command_handler.py:_load_history`. Intended for deletion once all on-disk sessions are re-saved in 2.0 format.

### `utils/system_info.py` (the `utils` package's public face)
`utils/__init__.py` re-exports `get_architecture`, `get_cuda_version`, `get_memory_size_gb`, `get_os_name`, `get_system_info`, `get_vram_size_gb`. Normalizes OS (`windows/macos/linux`), arch (`x64/arm64`), CUDA version (parses `nvidia-smi`/`nvcc`), total RAM (sysconf/sysctl/`/proc/meminfo`/Windows `GlobalMemoryStatusEx`), and VRAM. Also `summarize_python_environment()` and `get_macos_version()`.

### `utils/command_runner.py`
Cross-platform subprocess layer. Dataclasses `CommandResult`, `ShutdownResult`; errors `CommandExecutionError`, `ProcessLaunchError`; wrappers `ThreadedProcess`, `ManagedProcess` (unified API over asyncio/threaded/multiprocessing launches). Public functions: `run_command(...)`, `run_command_async(...)` (delegates to `subprocess.run` in a worker thread to dodge Windows asyncio-subprocess `NotImplementedError`), `start_command_async(...)`, `start_multiprocessing_process(...)`, `shutdown_process(...)` / `shutdown_process_sync(...)`, and the Windows console-suppression helper `windows_hidden_subprocess_kwargs()`.

### `utils/logging.py`
`setup_logger(level)` attaches a `ColorFormatter` `StreamHandler` only to the `qwenpaw` namespace (`LOG_NAMESPACE = PROJECT_NAME.lower()`), suppresses third-party logs, and sets `propagate = False`. `add_project_file_handler(log_path)` adds an idempotent `_SafeRotatingFileHandler` (Windows-lock tolerant, 5 MiB × 3). Also `PlainFormatter`, `SuppressPathAccessLogFilter`, `_enable_windows_ansi()`, `LOG_FILE_PATH`.

### `utils/http.py`
`is_loopback_host(host)`, `is_loopback_url(url)`, `trust_env_for_url(url)` — used to decide whether httpx should trust proxy/cert env vars (loopback ⇒ don't).

### `utils/stdio.py`
`ensure_standard_streams()` replaces unusable `sys.stdout`/`sys.stderr` with `os.devnull`-backed fallbacks (encoding-keyed, atexit-cleaned).

### `utils/console_static.py`
`resolve_console_static_dir()` and `find_qwenpaw_source_repo_root()` — locate the web console `index.html` / git checkout root across pip/wheel/source installs.

### `utils/telemetry.py`
Anonymous install analytics: `get_system_info()` (UUID install_id, version, install method, OS, GPU detect), `collect_and_upload_telemetry(working_dir)`, opt-out / version-marker helpers (`has_telemetry_been_collected`, `is_telemetry_opted_out`, `mark_telemetry_collected`). Uploads to a fixed `TELEMETRY_ENDPOINT` with silent failure.

### `utils/startup_display.py`
`print_ready_banner(api_info=None, elapsed_seconds=None)` — rich-formatted startup banner.

## Entry Points & Public API

- `python -m qwenpaw` → `__main__.cli` (from `qwenpaw.cli.main`).
- Config: `from qwenpaw.constant import EnvVarLoader, WORKING_DIR, ...` (imported by `app/_app.py`, `config/utils.py`, `envs/store.py`, `utils/logging.py`, `utils/telemetry.py`, and many more).
- Envelope protocol: `from qwenpaw.schemas import Message, Content, AgentRequest, AgentResponse, ...` — consumed by channels and `runtime/stream_query.py`.
- Error mapping: `from qwenpaw.exceptions import convert_model_exception, ProviderError, ...` — used in `runtime/stream_query.py`, `local_models/`, and providers.
- System info: `from qwenpaw.utils import get_system_info, get_os_name, ...`.
- Subprocess: `from qwenpaw.utils.command_runner import run_command_async, start_command_async, ...` (heavy use in `local_models/`).
- Logging: `setup_logger`, `add_project_file_handler`, `LOG_FILE_PATH`.

## AgentScope Integration

This area is mostly agentscope-agnostic, with two touch points:

- `exceptions.py` builds on the agentscope-runtime exception schema, importing `AgentRuntimeErrorException`, `ModelExecutionException`, `ModelTimeoutException`, `UnauthorizedModelAccessException`, `ModelQuotaExceededException`, `ModelContextLengthExceededException`, `UnknownAgentException`, `ExternalServiceException` from `agentscope_runtime.engine.schemas.exception`. qwenpaw's business exceptions subclass these so runtime callers see a uniform type, and `convert_model_exception` normalizes raw provider/SDK exceptions into them.
- `_compat/` patches and consumes `agentscope.message` — monkey-patching `Msg` (`to_dict`/`from_dict`/`timestamp`) and using `Base64Source`, `URLSource`, `DataBlock`, `ToolCallBlock`, `Msg` to translate 1.x session JSON into the 2.0 message model.

Note `schemas.py` deliberately defines qwenpaw's **own** streaming envelope and is *not* agentscope's event protocol. For agentscope message/runtime concepts see ../agentscope-v2/overview.md and ../agentscope-v2/README.md.

## Extension Points & Gotchas

- **`constant.py` is import-time and side-effecting.** Paths (`WORKING_DIR`, etc.) are resolved once at first import, *after* `__init__.py` loads persisted envs. Setting `QWENPAW_*` env vars after import has no effect on already-derived constants. New config knobs should be added via `EnvVarLoader` with explicit bounds.
- **`COPAW_` legacy fallback is automatic.** `_get_env` maps any `QWENPAW_*` key to a `COPAW_*` variant; don't read `os.environ` directly for these keys or you'll lose the fallback. Likewise `WORKING_DIR` silently prefers an existing `~/.copaw`.
- **`schemas.Message` vs agentscope `Msg` are different types.** `schemas.py` is the channel-facing envelope; `agentscope.message.Msg` is the runtime message. Don't conflate them. All `schemas` content models use `extra="allow"`, so unexpected fields pass silently.
- **`convert_model_exception` is keyword/heuristic-driven.** Classification leans on substring matches in the error message and exception type name; provider SDK wording changes can re-route an error. Prefer status codes where available.
- **`_compat/` is intentionally temporary.** The `Msg` monkey-patch and `msg_from_dict` exist only for loading 1.x sessions; both are slated for removal once on-disk data is migrated. Changes here must keep `/load_history` working.
- **`command_runner` has deliberate Windows fallbacks.** `run_command_async`/`start_command_async` route around asyncio-subprocess `NotImplementedError` and add `CREATE_NO_WINDOW`; process-group kill is POSIX-only. Don't replace these with naive `asyncio.create_subprocess_exec`.
- **Logging only attaches to the `qwenpaw` namespace** with `propagate = False`; library logs are suppressed by design, so a stray top-level `logging.getLogger()` call won't appear unless namespaced under `qwenpaw`.
- **Telemetry endpoint is hard-coded** and fails silently; opt-out is persisted in `<working_dir>/.telemetry_collected`.
