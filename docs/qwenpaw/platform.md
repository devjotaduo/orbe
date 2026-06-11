# tauri, tunnel, envs, config

> Package path(s): `src/qwenpaw/tauri/`, `src/qwenpaw/tunnel/`, `src/qwenpaw/envs/`, `src/qwenpaw/config/`

## Purpose

This area holds qwenpaw's *platform plumbing*: how the backend boots inside the Tauri desktop shell (`tauri/`), how a local server is exposed to the public internet via a Cloudflare Quick Tunnel (`tunnel/`), how user-set environment variables are persisted and re-injected across restarts (`envs/`), and the canonical `config.json` schema plus load/save/migration helpers and per-request context variables (`config/`). These are foundational, mostly dependency-light modules that run very early in the process lifecycle — several of them are imported and executed *before* `qwenpaw.constant` and the FastAPI app are loaded.

## Architecture

Boot order matters in this area:

```
Tauri (Rust) spawns sidecar
        │
        ▼
qwenpaw.tauri.entry:main()
   1. _ensure_utf8_stdio()
   2. _install_desktop_runtime()        # sets QWENPAW_DESKTOP_APP, CORS origins
        - ensure_desktop_cors_origins()  (tauri/env.py)
        - guards: app must NOT be imported yet
   3. install_sidecar_logging()         (tauri/sidecar_logging.py -> desktop.log)
   4. _install_certifi_env()            # SSL_CERT_FILE etc.
   5. auto-run `qwenpaw init` if no config.json
   6. _run_backend_server()             # uvicorn on 127.0.0.1:0 (ephemeral port)
        - write_last_api(host, port)     (config/utils.py)
        - emit "QWENPAW_BACKEND_READY {\"port\": N}" on stdout

App import (qwenpaw/__init__.py, app/_app.py)
        │
        ▼
envs.load_envs_into_environ()           # re-hydrate os.environ from envs.json

config.load_config() -> Config          # pydantic root model, mtime-cached

Voice channel (app/channels/voice) ──> tunnel.CloudflareTunnelDriver.start(port)
                                          -> public *.trycloudflare.com URL
```

`envs/` and `config/` are read at runtime by the rest of the app; `tauri/` and `tunnel/` are entry/driver code invoked at the edges. The four directories do not depend on each other except that `tauri.entry` calls `config.utils.write_last_api` and the init command.

## Key Modules

### `tauri/entry.py`
Tauri sidecar entry point — `main()` is what the bundled Python process runs. Responsibilities, in strict order: force UTF-8 stdio (`_ensure_utf8_stdio`), set up the desktop runtime (`_install_desktop_runtime` → sets `QWENPAW_DESKTOP_APP=1` and CORS origins, asserting the FastAPI app is not yet imported because CORS middleware is applied from `qwenpaw.constant.CORS_ORIGINS` at import time), install sidecar logging, set certifi SSL env vars, auto-run `init --defaults --accept-security` if `config.json` is missing, then `_run_backend_server`. The server binds uvicorn to `127.0.0.1` on port `0` (OS picks a free port via `config.bind_socket()`), persists it with `write_last_api`, and prints `QWENPAW_BACKEND_READY {"port": N}` (`_emit_backend_ready`) so the Rust shell can connect. Key functions: `main()`, `_run_backend_server(log_level)`, `_emit_backend_ready(port)`, `_run_click_command(...)`.

### `tauri/env.py`
Dependency-light env constants and helper, intentionally importable before `qwenpaw.constant`. Defines `DESKTOP_APP_ENV="QWENPAW_DESKTOP_APP"`, `DESKTOP_CORS_ORIGINS_ENV="QWENPAW_CORS_ORIGINS"`, `DESKTOP_READY_PREFIX="QWENPAW_BACKEND_READY"`, the `DESKTOP_CORS_ORIGINS` tuple (`tauri://localhost`, `https://tauri.localhost`, `http://tauri.localhost`), and `ensure_desktop_cors_origins()` which merges those defaults into the env var.

### `tauri/sidecar_logging.py`
`install_sidecar_logging(log_path) -> Path` tees `sys.stdout`/`sys.stderr` to a log file via the `_TeeStream` wrapper, enables `faulthandler` for native crash traces, and attaches a project file handler. Writes a header with platform/python/argv/cwd. Called by `entry.main()` with `WORKING_DIR / "desktop.log"`.

### `tauri/cli_entry.py`
Trivial PyInstaller entry point for the bundled CLI: `mp.freeze_support()` then `qwenpaw.cli.main.cli()`.

### `tunnel/cloudflare.py`
`CloudflareTunnelDriver` manages a `cloudflared tunnel --url http://localhost:<port>` subprocess (Cloudflare *Quick Tunnel*). `async start(local_port) -> TunnelInfo` spawns the process, then `_wait_for_url(timeout=30)` scans stderr with `_URL_RE` (`https://<sub>.trycloudflare.com`) until the public URL appears. `TunnelInfo` (dataclass) carries `public_url`, `public_wss_url` (https→wss rewrite), `started_at`, and `pid`. Other methods: `stop()`, `health_check()`, `get_public_url()`, `get_info()`, and a background `_monitor()` that drains stderr and logs unexpected exit but deliberately does **not** auto-restart (a restart would issue a new URL).

### `tunnel/binary_manager.py`
`BinaryManager.get_binary_path() -> str` locates `cloudflared` on PATH, else under `WORKING_DIR/bin`, else downloads it. Version is pinned (`_CLOUDFLARED_VERSION = "2026.2.0"`) with per-platform URLs in `_DOWNLOAD_URLS` and SHA256s in `_SHA256_CHECKSUMS`; `_verify_checksum` enforces integrity and deletes the file on mismatch. Handles `.tgz` (macOS) extraction and chmod +x on non-Windows. Platform key is `(platform.system(), platform.machine())`.

### `envs/store.py`
Two-layer env var persistence: **envs.json** (canonical, under `SECRET_DIR`, encrypted) + **os.environ** (live process). Values are encrypted/decrypted transparently via `qwenpaw.security.secret_store` (`encrypt`/`decrypt`/`is_encrypted`); legacy plaintext is detected on load and re-encrypted (`_rewrite_encrypted`). Public API: `load_envs(path=None)`, `save_envs(envs, path=None)` (writes encrypted + `_sync_environ`), `set_env_var(key, value)`, `delete_env_var(key)`, and `load_envs_into_environ()` — called once at startup to re-hydrate `os.environ` *without overwriting* explicit runtime values (`overwrite=False`) and skipping `_PROTECTED_BOOTSTRAP_KEYS` (`QWENPAW_WORKING_DIR`, `QWENPAW_SECRET_DIR`). It also takes `restore_process_lock()` and cleans stale restore artifacts from `backup`. `_migrate_legacy_envs_json` copies an old `envs.json` (from the package dir or `WORKING_DIR`) into `SECRET_DIR` once. Files are chmod'd `0o600`/`0o700` best-effort.

### `config/config.py` (~78 KB — the schema)
Defines the entire `config.json` pydantic model tree. Root `Config(BaseModel)` fields: `channels` (`ChannelConfig`), `mcp` (`MCPConfig`), `tools` (`ToolsConfig`), `last_api` (`LastApiConfig`), `agents` (`AgentsConfig`), `last_dispatch`, `security` (`SecurityConfig`), `acp` (`ACPConfig`), `show_tool_details`, `user_timezone` (defaults via `detect_system_timezone`), `plugins`, `skill_paths`. Notable sub-models: channel configs (`IMessageChannelConfig`, `DiscordConfig`, `TelegramConfig`, `FeishuConfig`, `MatrixConfig`, `WeChatConfig`, … unioned as `ChannelConfigUnion`), `AgentsConfig`/`AgentProfileConfig`/`AgentsRunningConfig`/`AgentsLLMRoutingConfig`, `HeartbeatConfig`, security models (`SecurityConfig`, `ToolGuardConfig`, `ToolGuardRuleConfig`, `FileGuardConfig`, `SkillScannerConfig`), tool/MCP models (`ToolsConfig`, `BuiltinToolConfig`, `MCPConfig`, `MCPClientConfig`, `MCPOAuthConfig`), memory/context models (`AutoMemorySearchConfig`, `EmbeddingModelConfig`, `ADBPGMemoryConfig`, `ReMeLightMemoryConfig`, `ContextCompactConfig`, `ToolResultPruningConfig`, `LightContextConfig`, `AutoTitleConfig`). Agent-helpers: `build_fallback_agent_profile_config`, `load_agent_config`, `save_agent_config`, `migrate_legacy_config_to_multi_agent`, `generate_short_agent_id`, `sanitize_agent_id`, `validate_agent_id`.

### `config/utils.py` (~28 KB — load/save/IO)
Disk IO and environment-aware helpers. `load_config(path=None) -> Config` reads `config.json` with **mtime-based caching** (`_config_cache`/`_config_mtime` under `_config_lock`), normalizing legacy `~/.copaw`-bound paths (`_normalize_working_dir_bound_paths`) and self-healing invalid configs by removing bad fields then backing up (`_backup_config_file`) and falling back to defaults. `save_config(config, path=None)` writes JSON (`model_dump(mode="json", by_alias=True)`) and invalidates cache. `strict_validate_config_file` validates without auto-repair (for `doctor`). Path helpers: `get_config_path` (`WORKING_DIR/config.json`), `get_heartbeat_query_path`, `get_jobs_path`, `get_chats_path`, `get_plugins_dir`, `get_agent_dirs`. Runtime helpers: `read_last_api`/`write_last_api`, `get_heartbeat_config`, `get_dream_cron`, `update_last_dispatch`, `is_qwenpaw_running`, `is_running_in_container`, `get_available_channels`, browser discovery (`get_playwright_chromium_executable_path`, `get_system_default_browser`, `_discover_system_chromium_path`).

### `config/context.py`
`contextvars.ContextVar` registry passing per-request/per-agent state into tool functions (avoids threading args through every call): `current_workspace_dir`, `current_recent_max_bytes`, `current_shell_command_timeout`, `current_shell_command_executable`, `current_session_id`, `current_toolkit` (typed `agentscope.tool.Toolkit`). Each has matching `get_*`/`set_*` accessors.

### `config/timezone.py`
Standard-library-only system IANA timezone detection. `detect_system_timezone() -> str` never raises (falls back to `"UTC"`). Probes Python runtime, `$TZ`, then OS-specific sources (Windows registry via `_WIN_TO_IANA` map, `/etc/timezone`, `/etc/localtime` symlink, `/etc/sysconfig/clock`, `timedatectl`). `normalize_tz` canonicalizes via `_NON_STANDARD_ALIASES` and `zoneinfo.ZoneInfo`. Kept separate from `config.py`/`utils.py` to avoid circular imports.

## Entry Points & Public API

- **`config/__init__.py`** re-exports the public config surface: models (`Config`, `ChannelConfig`, `ChannelConfigUnion`, `AgentsRunningConfig`, `FileGuardConfig`, `HeartbeatConfig`, `SecurityConfig`, `ToolGuardConfig`, `ToolGuardRuleConfig`, `ModelSlotConfig`, `ActiveModelsInfo`, `ACPConfig`, `ACPAgentConfig`) and helpers (`load_config`, `save_config`, `get_config_path`, `strict_validate_config_file`, `get_heartbeat_config`, `get_dream_cron`, `get_available_channels`, `is_running_in_container`, `update_last_dispatch`, `get_playwright_chromium_executable_path`, `get_system_default_browser`, …).
- **`envs/__init__.py`** exports `load_envs`, `save_envs`, `set_env_var`, `delete_env_var`, `load_envs_into_environ`. The latter is invoked at startup from both `qwenpaw/__init__.py` and `app/_app.py`.
- **`tunnel/__init__.py`** exports `CloudflareTunnelDriver` and `TunnelInfo`; the only current consumer is `app/channels/voice/channel.py` (`self.tunnel_mgr = CloudflareTunnelDriver()`).
- **`tauri/`** is process-entry code, not a library API. `tauri.entry:main` is the sidecar entry; `tauri.cli_entry` is the PyInstaller CLI entry. `tauri.env` constants/`ensure_desktop_cors_origins` are imported by `entry.py`.
- `config/context.py` accessors are consumed by tools/guardians (e.g. `security/tool_guard/guardians/rule_guardian.py` uses `get_current_workspace_dir`).

## AgentScope Integration

Minimal and indirect. The only direct touch point is `config/context.py`, which stores an `agentscope.tool.Toolkit` instance in the `current_toolkit` ContextVar (imported under `TYPE_CHECKING`) so tool functions can reach the active agent's toolkit. The config schema (`config.py`) describes models, tools, MCP clients, and agent profiles that agentscope agents are later built from, but this area does not call agentscope APIs itself. For the Toolkit type and agent/tool model concepts, see [../agentscope-v2/api-reference/](../agentscope-v2/api-reference/) and [../agentscope-v2/building-blocks/](../agentscope-v2/building-blocks/).

## Extension Points & Gotchas

- **Import-order is load-bearing in `tauri/entry.py`.** CORS origins must be set before `qwenpaw.app._app` (and `qwenpaw.constant`) are imported — `_ensure_qwenpaw_app_not_loaded()` raises `RuntimeError` if the app was imported too early. Keep `tauri/env.py` and `tauri/sidecar_logging.py` dependency-light; do not import `qwenpaw.constant` at module top level there (note the lazy import in `_add_project_file_handler`).
- **Ephemeral backend port.** The desktop backend binds to port `0`; the actual port is discovered after `bind_socket()`, persisted via `write_last_api`, and announced on stdout with the `QWENPAW_BACKEND_READY` prefix. Anything parsing that line must match `DESKTOP_READY_PREFIX` exactly.
- **`cloudflared` is pinned with checksums.** When bumping `_CLOUDFLARED_VERSION` in `tunnel/binary_manager.py`, update *all* entries in `_SHA256_CHECKSUMS` and `_DOWNLOAD_URLS`; a mismatch deletes the download and raises. Quick Tunnels are intentionally **not** auto-restarted (a restart yields a new public URL), so callers must treat `get_info()` returning `None` as "tunnel gone" and re-`start()` if needed. New platforms require adding both a URL and a checksum.
- **Env vars are encrypted secrets.** `envs.json` lives under `SECRET_DIR`, is encrypted via `secret_store`, and chmod'd `0o600`. `load_envs_into_environ()` uses `overwrite=False` so real process/system env always wins, and skips `_PROTECTED_BOOTSTRAP_KEYS` (`QWENPAW_WORKING_DIR`, `QWENPAW_SECRET_DIR`) — do not add bootstrap-critical keys to envs.json expecting them to be injected.
- **Config is mtime-cached and self-healing.** `load_config` caches by file mtime under a lock; writes outside `save_config` won't invalidate the cache within the same process unless mtime changes. Invalid configs are auto-repaired (bad fields stripped) or backed up and replaced with defaults — meaning a malformed `config.json` silently reverts to defaults at runtime; use `strict_validate_config_file` for diagnostics that must *not* auto-repair. Legacy `~/.copaw` paths in `workspace_dir`/`media_dir` are rewritten to `WORKING_DIR` on load.
- **Timezone detection must never raise.** `detect_system_timezone()` swallows all errors and returns `"UTC"`. When adding probes, preserve that contract and prefer the alias table over raw `ZoneInfo` backward links so deprecated names normalize to modern IDs.
- `config/timezone.py` is split out specifically to avoid circular imports between `config.py` and `utils.py`; keep timezone logic there.
