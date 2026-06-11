# cli

> Package path(s): `src/qwenpaw/cli/` — `main.py`, the `*_cmd.py` / `*_commands.py` command groups, the `doctor_*.py` diagnostic system, shared helpers (`http.py`, `utils.py`, `process_utils.py`), and the `tui/` subpackage (Textual chat UI + `transport/` + `widgets/`).

## Purpose

This package is the entire command-line surface of QwenPaw. It defines the `qwenpaw` / `copaw` console-script entry point, a lazily-loaded Click command tree (server, agents, channels, skills, cron, models, auth, plugins, doctor, etc.), a read-only/repair diagnostic system (`doctor`), and a bundled Textual terminal chat UI (`tui/`). Most commands are thin clients that either talk to a running QwenPaw FastAPI server over HTTP (`/api/...`) or read/validate local config and workspace files directly; a few (`app`, `acp`, `tui`, `desktop`) start long-running processes.

## Architecture

The console script `qwenpaw` resolves to `qwenpaw.cli.main:cli` (see `pyproject.toml` `[project.scripts]`; `copaw` is an alias). `python -m qwenpaw` reaches the same `cli` via `src/qwenpaw/__main__.py`.

`main.cli` is a custom `click.Group` subclass, `LazyGroup`, whose `lazy_subcommands` dict maps a command name to `(module_path, attr_name, label)`. Subcommand modules are imported only when first invoked (via `__import__` in `LazyGroup.get_command`), so `qwenpaw --help` and fast subcommands avoid paying the import cost of heavy ones; load timings are recorded in `main._init_timings` and can be re-emitted by `log_init_timings()` once `app_cmd` raises the log level to debug. The root group accepts global `--host` / `--port`, defaulting from `read_last_api()` then `127.0.0.1:8088`, and stows them in `ctx.obj` for HTTP-client commands.

Two broad command shapes:
- **HTTP-client commands** (`chats`, `cron`, `daemon`, `agents`, `task`, `mission`, parts of `doctor`): build an `httpx.Client` via `http.client(base_url)` and call the server's `/api/...` routes. `http.resolve_base_url(ctx, base_url)` resolves the target with priority command `--base-url` → global `--host/--port`.
- **Local commands** (`init`, `clean`, `env`, `skills`, `channels`, `models`, `auth`, `update`, `uninstall`, `doctor` checks): read/validate/repair config and workspace files directly. Interactive prompts go exclusively through `utils.py` (a *questionary* wrapper) so no other module imports questionary.

Process-launching commands: `app_cmd` runs the FastAPI app under `uvicorn` (`qwenpaw.app._app:app`); `acp_cmd` runs QwenPaw as an ACP agent over stdio; `desktop_cmd` opens the app in a native webview; the `tui/` package runs a Textual chat client that itself spawns `qwenpaw acp` as a subprocess.

The `doctor` subsystem is split: `doctor_cmd.py` orchestrates and prints; `doctor_checks.py` holds pure read-only check functions; `doctor_connectivity.py` adds `--deep` network probes; `doctor_fix_runner.py` performs conservative, backed-up repairs; `doctor_registry.py` lets plugins contribute extra checks via entry points or programmatic registration.

## Key Modules

### `main.py` — root CLI group & lazy loader
- `class LazyGroup(click.Group)`: `__init__(*args, lazy_subcommands=None, **kwargs)`, overrides `list_commands(ctx)` and `get_command(ctx, cmd_name)` to import-on-demand and cache.
- `cli(ctx, host, port)`: root group decorated with `@click.group(cls=LazyGroup, lazy_subcommands={...})`, `@click.version_option(prog_name="QwenPaw")`, global `--host/--port`. Populates `ctx.obj["host"|"port"]`.
- `log_init_timings()`: replays recorded import timings as debug lines.
- Registered subcommands (name → attr): `acp`, `app`, `channels`/`channel`→`channels_group`, `daemon`→`daemon_group`, `chats`/`chat`→`chats_group`, `clean`, `cron`→`cron_group`, `env`→`env_group`, `init`, `models`→`models_group`, `skills`→`skills_group`, `uninstall`, `desktop`, `update`, `shutdown`, `auth`→`auth_group`, `agents`/`agent`→`agents_group`, `plugin`, `task`, `doctor`.

### `http.py` — shared HTTP client helpers
- `client(base_url) -> httpx.Client`: normalizes base to end with `/api`, 30s timeout, `trust_env` from `qwenpaw.utils.http.trust_env_for_url`.
- `print_json(data)`, `resolve_base_url(ctx, base_url)`.

### `app_cmd.py` — `qwenpaw app`
- `app_cmd(host, port, reload, workers, log_level, hide_access_paths)`: persists last host/port (`write_last_api`), sets `LOG_LEVEL_ENV`, sets/clears `QWENPAW_RELOAD_MODE`, warns when bound non-loopback without auth (`_warn_if_auth_off_non_loopback_bind`), then `uvicorn.run("qwenpaw.app._app:app", workers=1, ...)`. `--workers` is deprecated/ignored.

### `acp_cmd.py` — `qwenpaw acp`
- `acp_cmd(agent, workspace, debug)`: runs `qwenpaw.agents.acp.server.run_qwenpaw_agent(...)` over stdio. This is the bridge the TUI spawns.

### `doctor_cmd.py` — `qwenpaw doctor` / `qwenpaw doctor fix`
- `doctor_cmd(ctx, timeout, llm_timeout, deep)`: group with `invoke_without_command=True`; runs checks when no subcommand.
- `run_doctor_checks(ctx, timeout, llm_timeout, deep)`: the big read-only pass — Environment, Config (+unknown keys), Agents/workspaces/profiles, Channels, Doctor extensions, MCP, Skills, Browser, Security, Memory, Cron, Working dir, Console static, Web auth, Providers, Active LLM, per-agent models, and live `/api/agent/health` + `/api/version` + console `GET /` probes. Exits 1 on any FAIL.
- `doctor_fix_cli(...)` (subcommand `fix`): `--dry-run`, `--yes/-y`, `--non-interactive`, `--only IDS`, `--no-backup`, `--backup-dir`; delegates to `doctor_fix_runner.run_doctor_fix`.

### `doctor_checks.py` — pure read-only checks
Large module of functions returning `(bool, str)` or `list[str]` notes, e.g. `check_agent_profile_workspaces`, `check_agent_json_profiles`, `check_enabled_agents_model_connections` (async), `check_cron_jobs_files`, `mcp_client_notes`, `skill_layout_notes`, `security_baseline_notes`, `browser_automation_notes`, `environment_summary_lines`, `qwenpaw_local_llm_deep_notes`. No disk mutations.

### `doctor_connectivity.py` — `--deep` probes
- `collect_deep_channel_connectivity_notes(cfg, timeout)`: non-fatal channel reachability notes; custom channels can override probes.

### `doctor_fix_runner.py` — conservative repairs
- `run_doctor_fix(...)`: allowlisted fix ids with backup + atomic write. Fix ids include `ensure-working-dir`, `ensure-workspace-dirs` (safe defaults), `validate-all-jobs-json`, `reconcile-workspace-skills`, `seed-missing-agent-json`, `reset-invalid-agent-json`, `write-empty-jobs-json`, `normalize-jobs-cron`, `rebuild-console-npm`. `--non-interactive` rejects risky ids even with `-y`.

### `doctor_registry.py` — plugin-extensible checks
- `@dataclass DoctorRunContext(cfg, raw_cfg, cli_base_url, timeout, deep)`.
- `register_doctor_contribution(contrib_id, fn)`, `reset_doctor_registry_state()`, `run_extension_contributions(ctx)`. Discovers entry-point groups `qwenpaw.doctor` (and legacy `copaw.doctor`); manual registrations run first.

### Command groups (one per file)
- `agents_cmd.py` (`agents`/`agent`), `channels_cmd.py` (`channels`/`channel` — list + scaffold/install custom channels), `chats_cmd.py` (`chats` — HTTP `/chats`), `cron_cmd.py` (`cron`), `daemon_cmd.py` (`daemon`: status/restart/reload-config/version/logs), `env_cmd.py` (`env`: list/set/delete), `providers_cmd.py` (`models`: list/config/set-llm/custom providers), `skills_cmd.py` (`skills`: list/configure/info/install), `auth_cmd.py` (`auth`: reset-password), `plugin_commands.py` (`plugin`), `mission_cmd.py` (`mission`).
- Single commands: `init_cmd.py` (`init`), `clean_cmd.py` (`clean`), `update_cmd.py` (`update`), `uninstall_cmd.py` (`uninstall`), `desktop_cmd.py` (`desktop`), `shutdown_cmd.py` (`shutdown`), `task_cmd.py` (`task`).

### Shared helpers
- `utils.py`: centralized *questionary* interactive-prompt helpers (the only place questionary is imported).
- `process_utils.py`: process listing/parsing helpers (CSV/IO based) used by daemon/shutdown-style commands.

### `tui/` — bundled Textual chat UI
- `tui/launch.py`: `run_tui(*, agent=None, resume=None)` builds an `AcpTransport` (default command `[sys.executable, "-m", "qwenpaw", "acp"]`) and runs `PawApp`; also defines `tui_cmd` (`qwenpaw tui`, options `--agent`, `--resume`).
- `tui/app.py`: `PawApp(App)` — the Textual application; consumes only normalized `TuiEvent`s and the `TuiTransport` interface.
- `tui/transport/base.py`: `@runtime_checkable class TuiTransport(Protocol)` — `start`, `send`, `interrupt`, `list_sessions`, `load_session`, `events`, `resolve_permission`, `close`. The swappable seam.
- `tui/transport/acp.py`: `AcpTransport` — default backend; spawns `qwenpaw acp` and connects an ACP client to it.
- `tui/events.py`: normalized event union (`Connected`, `TextDelta`, `ToolCall`, `PermissionRequest`, `PlanUpdate`, `TokenUsage`, `TurnEnded`, `SessionSummary`, …).
- `tui/normalize.py`: translates ACP `session_update` objects into `TuiEvent`s (kept free of Textual).
- `tui/paths.py`: paw's self-owned state dir (`state_dir()`), independent of QwenPaw's working dir.
- `tui/themes.py`: theme gallery; `tui/widgets/`: Textual widgets (`messages`, `permission_modal`, `session_picker`, `status_bar`, `theme_picker`, `tool_panel`, `command_menu`).

## Entry Points & Public API

- **Console scripts** (`pyproject.toml`): `qwenpaw = "qwenpaw.cli.main:cli"` and alias `copaw = "qwenpaw.cli.main:cli"`. Also reachable via `python -m qwenpaw` (`__main__.py` imports `cli`).
- **`qwenpaw.cli.main:cli`** is the canonical Click group imported by tests (`tests/unit/cli/*`), `qwenpaw/tauri/cli_entry.py`, and `qwenpaw/tauri/entry.py` (which uses `log_init_timings`).
- **`run_tui(agent=..., resume=...)`** in `tui/launch.py` is the public entry to start the terminal UI programmatically.
- **`register_doctor_contribution` / `DoctorRunContext`** in `doctor_registry.py` are the public extension API for diagnostics.
- Each subcommand module exposes the `*_cmd` / `*_group` symbol named in `main.LazyGroup.lazy_subcommands`.

## AgentScope Integration

The `cli` package does **not** import agentscope directly. The agentscope-backed runtime is reached indirectly: `acp_cmd.py` calls `qwenpaw.agents.acp.server.run_qwenpaw_agent`, and the TUI (`tui/transport/acp.py`) spawns `qwenpaw acp` as a subprocess — so all agentscope usage is encapsulated in the `qwenpaw.agents` layer, not here. `app_cmd.py` only launches the FastAPI app (`qwenpaw.app._app:app`) under uvicorn. For how the agent runtime uses agentscope, see the agents-area docs and the agentscope KB at [../agentscope-v2/overview.md](../agentscope-v2/overview.md) and [../agentscope-v2/api-reference/](../agentscope-v2/api-reference/). (This repo targets agentscope 1.0.20; the v2 KB is reference material only.)

## Extension Points & Gotchas

- **Adding a subcommand**: create a module exposing a Click `command`/`group` object, then add one `name → (module_path, attr_name, label)` entry to `main.LazyGroup.lazy_subcommands`. Don't import the module eagerly in `main.py` — that defeats lazy loading and slows `--help`.
- **`tui` is NOT wired into the root group.** `tui_cmd` is defined in `tui/launch.py` and the docstrings describe `qwenpaw` (bare) and `qwenpaw tui` launching the UI, but **the current `main.cli` neither registers `tui_cmd` in `lazy_subcommands` nor sets `invoke_without_command=True`** on the root group. So `qwenpaw tui` / bare-`qwenpaw`→TUI is not reachable through the standard console script as wired today (it is reached programmatically via `run_tui`, e.g. from the tauri/desktop entry). A developer expecting that behavior must add the registration. (Flagging as observed-from-code, not inferred intent.)
- **HTTP vs local commands**: HTTP-client commands need a running `qwenpaw app`; target resolution is command `--base-url` → global `--host/--port` → last-used → `127.0.0.1:8088`. `http.client` always force-appends `/api`.
- **Interactive prompts** must go through `utils.py` (questionary wrapper) — do not import questionary elsewhere.
- **doctor checks vs fixes are strictly separated**: `doctor_checks.py` must stay side-effect-free (read-only); all mutations belong in `doctor_fix_runner.py`, which is allowlist + backup + atomic-write driven and treats most ids as "risky" (rejected under `--non-interactive`). New diagnostics for plugins should be added via `register_doctor_contribution` or the `qwenpaw.doctor` entry-point group, returning `list[str]` notes — never raise (errors are caught and surfaced as `(extension error)` lines).
- **Legacy aliases everywhere**: `copaw` console script, `copaw.doctor` entry-point group, `COPAW_*` env vars, and `copaw-local` provider id are still honored alongside the `qwenpaw`/`QWENPAW_*` names. Preserve both when touching these.
- **Windows/UTF-8**: `main.py` reconfigures stdout/stderr to UTF-8 on `win32` at import time (via `ensure_standard_streams`) so cron and non-ASCII output work; keep that import early.
- **TUI transport seam**: widgets and `PawApp` only see `TuiTransport` (Protocol) and normalized `TuiEvent`s, so a future in-process transport can replace `AcpTransport` without touching UI code. Keep `tui/normalize.py` free of Textual imports.
- `mission` (`mission_cmd.py`) is a defined group but, like `tui`, is **not** present in `main.LazyGroup.lazy_subcommands` — confirm wiring before assuming it is invokable via the console script.
