# local_models

> Package path(s): `src/qwenpaw/local_models/` — `__init__.py`, `manager.py`, `model_manager.py`, `llamacpp.py`, `download_manager.py`, `tag_parser.py`

## Purpose

This area gives qwenpaw the ability to run language models **locally** instead of calling a remote provider. It downloads GGUF model weights (from Hugging Face or ModelScope), downloads and installs the embedded **llama.cpp** server binary, launches/monitors that server as a child process exposing an OpenAI-compatible HTTP endpoint on localhost, and provides a small text-tag parser that extracts `<think>` reasoning and `<tool_call>` function-calling blocks from raw local-model output. Everything is fronted by a single facade, `LocalModelManager`, used as a process-wide singleton.

## Architecture

```
LocalModelManager (manager.py)          <- single public facade / singleton
  ├── ModelManager (model_manager.py)   -> download & manage GGUF model repos
  │     └── ProcessDownloadController ───┐
  ├── LlamaCppBackend (llamacpp.py)     -> install binary + run llama-server
  │     └── ProcessDownloadController ───┤  (shared download machinery)
  └── LocalModelConfig (pydantic)        │  persisted to local_models/config.json
                                         │
download_manager.py  <───────────────────┘
  DownloadProgressTracker, ProcessDownloadController,
  ProcessDownloadTask(Spec), DownloadProgress/Result/Update, DownloadTaskStatus

tag_parser.py  (standalone, no deps on the above) -> consumed by providers/
```

Two distinct concerns share the same generic background-download engine in `download_manager.py`:

1. **Model weights** — `ModelManager` spawns a `multiprocessing` (spawn-context) child process that runs the blocking `huggingface_hub.snapshot_download` / `modelscope.snapshot_download` SDK call. Downloads land in a `tmp/<task_id>` staging dir and are atomically promoted (via `shutil.move`) into `local_models/models/<repo/id>/` on success.
2. **llama.cpp binary** — `LlamaCppBackend` spawns its own child process that streams the release archive over HTTP (`httpx`), then unpacks it into `local_models/bin/`.

The generic engine (`ProcessDownloadController`) owns: a child process, a result `Queue`, a monitor thread that polls progress + drains the queue, and a `DownloadProgressTracker` (thread-safe, computes throughput). Only one download per controller can be active at a time. Each owner injects three callbacks via `ProcessDownloadTask`: `progress_probe` (disk-size sampling), `finalize_result` (promote staging → final), and `cleanup`.

Server lifecycle: `LocalModelManager.setup_server(model_id)` resolves the model dir, picks/validates a free port, launches `llama-server` via `start_command_async`, then polls `http://127.0.0.1:<port>/health` until ready (or times out). An `asyncio.Lock` (`_server_lifecycle_lock`) serializes start/stop/config mutations. An `atexit` hook ensures the server process is torn down on exit.

## Key Modules

### `manager.py` — `LocalModelManager`
The single entry point. Composes a `ModelManager` and a `LlamaCppBackend` and exposes a flat async/sync API the rest of qwenpaw calls. Holds `LocalModelConfig` (persisted to `local_models/config.json`, written with `chmod 0o600`) and a module-level singleton via `get_instance()`.
- `LocalModelConfig(BaseModel)`: `max_context_length: int = 65536 (ge=32768)`, `port: int | None`.
- llama.cpp: `check_llamacpp_installation()`, `check_llamacpp_installability()`, `async start_llamacpp_download() -> bool`, `async has_update() -> bool`, `async check_llamacpp_server_ready(timeout=120.0)`, `get_llamacpp_download_progress()`, `get_llamacpp_server_status()`, `is_llamacpp_server_transitioning()`, `cancel_llamacpp_download()`.
- models: `get_recommended_models()`, `is_model_downloaded(name)`, `list_downloaded_models()`, `start_model_download(model_id, source=None)`, `get_model_download_progress()`, `cancel_model_download()`, `remove_downloaded_model(model_id)`.
- server: `async setup_server(model_id) -> LlamaCppServerSetupResult`, `async shutdown_server()`, `shutdown_server_sync()`.
- config: `get_config()`, `async set_max_context_length(int)`, `async set_port(int|None)`.
- `DEFAULT_LLAMA_CPP_BASE_URL` points at a qwenpaw mirror of the ggml-org llama.cpp releases; `DEFAULT_LLAMA_CPP_RELEASE_TAG = "b8744"`.

### `model_manager.py` — `ModelManager`, `LocalModelInfo`, `DownloadSource`
Downloads and manages GGUF model repositories under `local_models/models/`.
- `DownloadSource(str, Enum)`: `HUGGINGFACE`, `MODELSCOPE`, `AUTO` (probe HF reachability, else ModelScope).
- `LocalModelInfo(ModelInfo)`: adds `size_bytes`, `downloaded`, `source`.
- `get_recommended_models()`: returns a hardware-tiered list of `AgentScope/QwenPaw-Flash-*` models based on detected VRAM (preferred) or system RAM via `utils.system_info`; returns `[]` under 4 GB.
- `start_download(model_id, source=None)` / `download_model(...)`: validates the remote repo actually contains `.gguf` files (`_check_gguf_exists`), estimates total size, then launches the background download. Raises `RuntimeError` if a download is already active, `ValueError` if no GGUF present.
- `is_downloaded()`, `list_downloaded_models()`, `remove_downloaded_model()`, `get_model_dir()`, `get_download_progress()`, `cancel_download()`.
- Static workers `_download_worker` / `_download_to_directory` run in the child process; HF and ModelScope SDKs are imported lazily so they are optional dependencies.

### `llamacpp.py` — `LlamaCppBackend`, `LlamaCppServerSetupResult`
Installs the llama.cpp binary and manages the `llama-server` child process.
- Resolves OS/arch/CUDA at construction (`_resolve_os_name/_resolve_arch/_resolve_cuda_version/_resolve_backend`). Windows can select a CUDA build (`12.4`/`13.1`); macOS/Linux are CPU-only. macOS requires ≥ 13.3.
- `_build_filename(tag)` maps platform → release asset name (e.g. `llama-<tag>-bin-win-cuda-12.4-x64.zip`).
- `start_download(base_url, tag, ...)`: streams archive with `httpx`, unpacks via `shutil.unpack_archive`, merges into `local_models/bin/`.
- `async setup_server(model_path, model_name, max_context_length=None, port=None) -> LlamaCppServerSetupResult`: resolves the model `.gguf` (and optional `mmproj-*.gguf` for multimodal), reuses an already-running server if the same model+port is requested, otherwise launches `llama-server --host 127.0.0.1 --port ... --model ... --alias ... --gpu-layers auto [--ctx-size ...] [--mmproj ...]` and waits on `/health`.
- `LlamaCppServerSetupResult(BaseModel)`: `port: int`, `model_info: ModelInfo`.
- Other: `list_devices()`, `get_version()`, `server_ready(timeout=120.0)`, `shutdown_server()`, `shutdown_server_sync()`, `get_server_status()`, `is_server_transitioning()`. Registers `_shutdown_server_at_exit` with `atexit`.

### `download_manager.py` — generic background-download engine
Shared, reusable machinery (no qwenpaw-model specifics).
- Status enum `DownloadTaskStatus`: `IDLE/PENDING/DOWNLOADING/CANCELING/COMPLETED/FAILED/CANCELLED`.
- Frozen dataclasses `DownloadProgress`, `DownloadTaskResult`, `DownloadProgressUpdate` with `to_message`/`from_message` helpers for crossing the process/queue boundary.
- `ProcessDownloadTask` / `ProcessDownloadTaskSpec`: bundle the worker target + injected `progress_probe`, `finalize_result`, `cleanup` callbacks.
- `DownloadProgressTracker`: thread-safe lifecycle + throughput (bytes/sec) tracking; `snapshot()` returns the dict shape polled by HTTP routes.
- `ProcessDownloadController`: starts the child process (`start_multiprocessing_process` from `utils.command_runner`), runs a monitor thread, enforces single-active-download, and handles cancel/cleanup/result finalization.

### `tag_parser.py` — special-tag extraction (standalone)
Pure-function module (regex + `dataclasses`, no other intra-package deps) for parsing raw local-model text. Consumed by the provider compat layer, not by the managers above.
- `text_contains_think_tag(text) -> bool`, `extract_thinking_from_text(text) -> TextWithThinking` — handles `<think>...</think>`, including unclosed streaming tags (`has_open_tag`).
- `text_contains_tool_call_tag(text) -> bool`, `parse_tool_calls_from_text(text) -> TextWithToolCalls` — extracts `<tool_call>...</tool_call>` blocks. Each block is parsed first as JSON (`{"name", "arguments"}`), then falling back to strict XML (`<function=...><parameter=...>`), then a lenient XML form with missing closing tags.
- Result dataclasses: `TextWithThinking`, `ParsedToolCall(id, name, arguments, raw_arguments)`, `TextWithToolCalls`.

## Entry Points & Public API

`__init__.py` exports: `DownloadSource`, `LocalModelInfo`, `LocalModelConfig`, `LocalModelManager`, `ModelManager`, `LlamaCppBackend`.

Known consumers inside `src/qwenpaw`:
- `app/routers/local_models.py` — FastAPI router; the primary HTTP surface. Resolves `LocalModelManager` from app state and exposes endpoints for recommended models, downloads (model + llama.cpp), progress polling, server setup/teardown, and config.
- `app/_app.py`, `app/routers/__init__.py` — wire the manager into app state / router registration.
- `providers/provider_manager.py` — at startup/auto-setup, reads the `"qwenpaw-local"` provider's `extra_models`, takes the first model id, and calls `local_manager.setup_server(model_id)` to bring the local server online.
- `providers/openai_chat_model_compat.py` — imports `parse_tool_calls_from_text` (and uses the `<think>`/`<tool_call>` parsing) to translate raw local-model text into structured tool calls when the local OpenAI-compatible endpoint does not emit native tool-call fields.
- `cli/providers_cmd.py`, `cli/doctor_checks.py` — CLI surfacing of local-model state/health.

Filesystem layout (rooted at `constant.DEFAULT_LOCAL_PROVIDER_DIR = WORKING_DIR / "local_models"`): `config.json`, `bin/` (llama-server), `models/<repo/id>/` (GGUF), `tmp/` (download staging), `logs/`.

## AgentScope Integration

This area mostly does **not** depend on agentscope directly — it manages binaries, processes, and downloads. The agentscope connection is **indirect**: `setup_server` launches an OpenAI-compatible `llama-server`, and the rest of qwenpaw (the `providers/` layer) then talks to that endpoint and bridges it into agentscope's model abstraction. The only agentscope-adjacent type used here is `qwenpaw.providers.provider.ModelInfo` (qwenpaw's own provider model, subclassed as `LocalModelInfo` and returned inside `LlamaCppServerSetupResult`). The recommended-model ids live under the `AgentScope/QwenPaw-Flash-*` namespace on ModelScope but are just repo identifiers, not agentscope code. For how the local endpoint is consumed as a model within agentscope, see the agentscope v2 KB — [../agentscope-v2/building-blocks/](../agentscope-v2/building-blocks/) and [../agentscope-v2/overview.md](../agentscope-v2/overview.md). (Note: qwenpaw runs on agentscope 1.0.20; the v2 KB is reference material, not a guarantee of API parity.)

## Extension Points & Gotchas

- **Single-download invariant**: each `ProcessDownloadController` allows only one active download. `start_download` raises `RuntimeError("...already in progress")`. There are two separate controllers (one in `ModelManager`, one in `LlamaCppBackend`), so a model download and a binary download can run concurrently, but two of the same kind cannot.
- **Spawn context everywhere**: child processes use `mp.get_context("spawn")`. Worker functions (`_download_worker`) must be top-level/static and picklable, and they call `ensure_standard_streams()` first because spawned processes (notably on Windows / frozen builds) may lack valid stdio. Don't capture closures or non-picklable state in worker payloads.
- **Optional SDKs**: `huggingface_hub` and `modelscope` are imported lazily inside methods. Adding a new download source means adding lazy imports plus the `_check_*_gguf_exists` / `_estimate_*_size` pair so progress and validation keep working.
- **GGUF-only**: `setup_server` and download validation reject repos/files without `.gguf`. A repo may also contain `mmproj-*.gguf`; the first non-mmproj GGUF is chosen as the model and the first mmproj enables multimodal. Multiple model GGUFs → only `model_files[0]` is used (no sharded-GGUF handling).
- **Server reuse subtlety**: `setup_server` short-circuits only when the requested `model_name` matches `_server_model_name` AND the process is alive AND the port matches/`None`. Any mismatch triggers a shutdown + restart. Always go through `setup_server`/`shutdown_server` (which hold `_server_lifecycle_lock`) rather than poking `_server_process`.
- **Config bounds**: `max_context_length` has `ge=32768`; `port` is `1..65535`. Persisted config that fails validation is silently replaced by defaults (`_load_config` logs a warning and returns `LocalModelConfig()`).
- **Hardware tiers are hard-coded**: `get_recommended_models` has fixed model lists/sizes per RAM/VRAM bracket (≤8 GB → 2B, ≤16 GB → 4B, else 9B). Updating recommendations means editing those literals (including the `size_bytes`).
- **Version check is brittle**: `LlamaCppBackend.has_update`/`get_version` parse the release tag as `int(tag[1:])` and slice version strings (`line[9:13]`); a release-tag scheme change will break update detection (it intentionally returns `True` on parse failure to be safe).
- **`tag_parser` is independent** of the managers and is the piece most likely to need changes as new local models emit different tool-call formats. It already supports JSON, strict-XML, and lenient-XML (unclosed-tag) tool calls plus streaming `has_open_tag` handling — extend the regexes/`_parse_single_tool_call` there, not in the provider layer.
- **Atexit teardown**: `LlamaCppBackend` registers a best-effort sync shutdown at exit; for explicit process-teardown paths use `LocalModelManager.shutdown_server_sync()`.
