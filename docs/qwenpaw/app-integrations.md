# app (approvals, crons, mcp)

> Package path(s): `src/qwenpaw/app/approvals/`, `src/qwenpaw/app/crons/` (incl. `crons/repo/`), `src/qwenpaw/app/mcp/`

## Purpose

These three sub-packages provide qwenpaw's runtime *integration* services that sit alongside the agent runner: a process-wide **approval service** that gates sensitive tool execution behind human confirmation, a per-agent **cron / heartbeat scheduler** that runs the agent on a schedule and dispatches results to channels or the inbox, and a hot-reloadable **MCP (Model Context Protocol) client manager** that connects external tool servers and exposes their tools to the agent. All three are instantiated per-`Workspace` (except the approval service, which is a global singleton) and wired through the workspace `ServiceManager`.

## Architecture

```
Workspace.ServiceManager (priority-ordered init)
  ├─ mcp_manager      = MCPClientManager()                  [prio 20]
  │     └─ mcp_config_watcher = MCPConfigWatcher(...)       (polls agent.json, hot-reload)
  ├─ cron_manager     = CronManager(repo=JsonJobRepository(jobs.json), runner, channel_manager) [prio 40]
  └─ (global)          ApprovalService  via get_approval_service()

Runner.stream_query  --get_clients()-->  MCPClientManager  --> agentscope toolkit
Tool guard (runtime/tool_guard.py, agents/tool_guard_mixin.py)
     --create_pending()/wait_for_approval()-->  ApprovalService  <--resolve--  /approval router & control command
CronManager._scheduled_callback --> CronExecutor.execute --> runner.stream_query + channel_manager.send_event
```

**Approvals flow.** When the tool guard flags a tool call, it calls `get_approval_service().create_pending(...)`, then blocks on `wait_for_approval(request_id, timeout)`. The pending record holds an `asyncio.Future`. A human resolves it (via the `/approval` router or the `approval_handler` control command) which calls `resolve_request(request_id, decision)`, setting the future result and unblocking the guarded tool.

**Crons flow.** `CronManager` wraps an APScheduler `AsyncIOScheduler`. Each job spec (`CronJobSpec`) becomes an APScheduler job whose callback runs `CronExecutor.execute(job)`. The executor either sends fixed text (`task_type="text"`) or runs the agent via `runner.stream_query(req)` and streams events to a channel (`task_type="agent"`). Job specs and per-job history persist through `JsonJobRepository`. Two special jobs are managed directly from config: `_heartbeat` (runs `HEARTBEAT.md` as a query) and `_dream` (memory optimization).

**MCP flow.** `MCPClientManager` builds and connects `StdIOStatefulClient` / `HttpStatefulClient` instances from `MCPConfig`. The runner calls `get_clients()` on every query to obtain the live client set. `MCPConfigWatcher` polls the agent config file and hot-swaps individual clients when their config changes (or hot-patches just the tool whitelist when only `tools` changed).

## Key Modules

### `app/approvals/service.py`
Central in-memory store for tool-approval requests. Exports `ApprovalService`, `PendingApproval`, `get_approval_service()`.
- `PendingApproval` (dataclass): one pending request — carries `request_id`, `session_id`, `root_session_id`, `owner_agent_id`, `agent_id`, `tool_name`, an `asyncio.Future[ApprovalDecision]`, `severity`, `findings_count`, `result_summary`, and an `extra` dict (may hold the originating `tool_call`).
- `ApprovalService` methods:
  - `set_channel_manager(channel_manager)` — store reference for push notifications.
  - `async create_pending(*, session_id, root_session_id, owner_agent_id, user_id, channel, agent_id, tool_name, result: ToolGuardResult, timeout_seconds=TOOL_GUARD_APPROVAL_TIMEOUT_SECONDS, extra=None) -> PendingApproval`
  - `async resolve_request(request_id, decision: ApprovalDecision) -> PendingApproval | None`
  - `async wait_for_approval(request_id, timeout_seconds) -> ApprovalDecision` (auto-resolves to `TIMEOUT` on `asyncio.TimeoutError`)
  - Query helpers: `get_request`, `get_pending_by_session`, `get_all_pending_by_session`, `list_pending_by_session`, `get_pending_by_root_session`, `get_all_pending_by_agent`.
  - Cancellation: `cancel_stale_pending_for_tool_call(session_id, tool_call_id)` (supersedes replayed calls), `cancel_all_pending_by_root_session(root_session_id)` (auto-denies on `/stop` or SSE disconnect).
  - `_gc_pending_locked()` — GC of stale/overflow pending records (max age 1800s, max 200 pending).
- `get_approval_service()` returns the module-level singleton.

### `app/crons/manager.py`
`CronManager` — orchestrates an APScheduler `AsyncIOScheduler`.
- `__init__(*, repo: BaseJobRepository, runner, channel_manager, timezone="UTC", agent_id=None)`.
- Lifecycle: `async start()` (loads jobs, prunes orphan history, schedules heartbeat/dream from config), `async stop()`.
- Read: `list_jobs`, `get_job`, `get_state`, `get_history`.
- Write/control: `create_or_replace_job(spec)`, `delete_job(job_id)`, `pause_job`, `resume_job`, `run_job(job_id)` (fire-and-forget manual trigger), `reschedule_heartbeat()`, `reschedule_dream()`.
- Internals: `_register_or_update` (builds APScheduler trigger via `_build_trigger`; per-job concurrency semaphore from `runtime.max_concurrency`), `_execute_once` (runs `CronExecutor`, records state + history, appends inbox events on success/delivery-failure). Constants: `HEARTBEAT_JOB_ID="_heartbeat"`, `DREAM_JOB_ID="_dream"`, `CRON_HISTORY_LIMIT=50`.

### `app/crons/executor.py`
`CronExecutor(*, runner, channel_manager)` with `async execute(job: CronJobSpec) -> dict`. For `text` jobs sends `channel_manager.send_text(...)`; for `agent` jobs builds a request, calls `runner.stream_query(req)` and forwards each event via `channel_manager.send_event(...)`, wrapped in inbox tracing (`create_trace` / `append_trace_from_session_delta` / `finalize_trace`) with a `timeout_seconds` guard. Returns a dict with `delivery_status`/`delivery_error`/`run_id`. Honors `runtime.share_session` to either reuse the target session or create a dedicated `…:cron:<job_id>` session.

### `app/crons/models.py`
Pydantic models (the cron schema). Key types: `ScheduleSpec` (`type: cron|once`, validates/normalizes the cron string to 5 fields and to weekday *names* — see Gotchas), `DispatchTarget`, `DispatchSpec`, `JobRuntimeSpec` (`max_concurrency`, `timeout_seconds`, `misfire_grace_seconds`, `share_session`), `CronJobRequest` (permissive passthrough to `runner.stream_query`), `CronJobSpec` (top-level job; validates `task_type` text/agent fields and the `save_result_to_inbox` default rule), `JobsFile`, `CronJobState`, `CronExecutionRecord`, `CronJobView`, `CronDispatchTargetItem`, `CronDispatchTargetsResponse`. Also exports `_crontab_dow_to_name` (reused by heartbeat).

### `app/crons/heartbeat.py`
Standalone heartbeat runner. `is_cron_expression(every)`, `parse_heartbeat_cron(every)`, `parse_heartbeat_every(every)` (parses `"30m"`/`"1h"`/`"90s"` → seconds), and `async run_heartbeat_once(*, runner, channel_manager, agent_id=None, workspace_dir=None)` which reads `HEARTBEAT.md`, checks `active_hours`, runs the agent, and dispatches to `last` channel / `inbox` / `main` depending on `hb.target`.

### `app/crons/api.py`
FastAPI `APIRouter(prefix="/cron")`. Endpoints: `GET /cron/dispatch-targets`, `GET/POST /cron/jobs`, `GET/PUT/DELETE /cron/jobs/{job_id}`, `POST /cron/jobs/{job_id}/{pause|resume|run}`, `GET /cron/jobs/{job_id}/{state|history}`. Resolves the per-agent `CronManager` via `get_cron_manager` → `get_agent_for_request(request)`. Server generates the job `id` on create. Raises HTTP 422 on `ConfigurationException`/`ValueError`.

### `app/crons/repo/base.py` + `repo/json_repo.py`
`BaseJobRepository` (ABC) defines `load/save/get_history/append_history/delete_history/prune_orphan_history` plus convenience `list_jobs/get_job/upsert_job/delete_job`. `JsonJobRepository(path)` is the single-file implementation: `jobs.json` for specs (atomic tmp-then-`shutil.move`), and per-job `jobs_history/<url-encoded id>.json` for history with per-job `asyncio.Lock`. Module function `migrate_legacy_weixin_jobs_file(path)` rewrites legacy `weixin:` session ids to `wechat:`.

### `app/mcp/manager.py`
`MCPClientManager` — hot-reloadable lifecycle for MCP clients.
- `async init_from_config(config: MCPConfig, timeout=60)` / `init_from_config_background(config, timeout=10)` (non-blocking startup).
- `async get_clients() -> List` (called by runner per query), `async get_client(key)`.
- `async replace_client(key, client_config, timeout=60)` — connect-new-outside-lock → atomic dict swap → close-old-outside-lock; `async remove_client(key)`; `async close_all()` (parallel close with 30s budget, then `kill_orphaned_mcp_children`).
- `_build_client(client_config)` selects `StdIOStatefulClient` (stdio) or `HttpStatefulClient` (streamable_http/sse), expands `$ENV` in headers, and injects an OAuth bearer token via `_inject_oauth_token` (skips expired tokens). Stamps each client with `_qwenpaw_rebuild_info`.

### `app/mcp/stateful_client.py`
The largest module. Drop-in replacements for agentscope's MCP clients that fix a CPU/process leak by running the *entire* client context-manager lifecycle inside one dedicated background asyncio task (avoids anyio cross-task cancel-scope errors). Shared logic lives in `_MCPClientMixin`; concrete classes `StdIOStatefulClient` and `HttpStatefulClient` both extend `_MCPClientMixin` and `agentscope.mcp.StatefulClientBase`.
- Lifecycle: `connect`, `reload`, `close` driven by `_stop_event`/`_reload_event`/`_ready_event`; `_run_lifecycle` owns the `AsyncExitStack`.
- Tools: `list_tools` / `list_all_tools` (whitelist filtering), `call_tool` (pass-through), and `get_callable_function(func_name, ...) -> MCPToolFunction` which is what the agentscope toolkit dispatches.
- Tool-name sanitization: `_sanitize_tool_name` / `_sanitize_server_tools` rewrite MCP names to `^[a-zA-Z0-9_-]+$` (OpenAI/Anthropic constraint); `_SessionAliasProxy` wraps the `ClientSession` so dispatch translates sanitized names back to the real MCP names.
- Transport-error recovery (`_handle_transport_error`) detects dead streams/broken pipes and fires a reconnect.
- Subprocess hygiene: a global PID registry (`_stdio_pids`, `_stdio_pgids`, `_orphan_stdio_pids`) and `kill_orphaned_mcp_children(include_active=False)` SIGTERM→SIGKILL reap orphaned stdio children (no-op SIGKILL phase on Windows).

### `app/mcp/watcher.py`
`MCPConfigWatcher(mcp_manager, config_loader, poll_interval=2.0, config_path=None)` — polls the config file mtime + a hash of the MCP section; on change it diffs old vs new client configs and calls `replace_client` / `remove_client`, or `_hot_patch_whitelist` when only the `tools` field changed. Tracks per-client failures with `_max_retries=3` to avoid infinite reload loops. `start()` / `stop()` manage the polling task.

## Entry Points & Public API

- **Approvals**: `from qwenpaw.app.approvals import ApprovalService, PendingApproval, get_approval_service`. Consumed by `runtime/tool_guard.py`, `runtime/stream_query.py`, `agents/tool_guard_mixin.py`, `app/runner/runner.py`, and the `/approval` router + `app/runner/control_commands/approval_handler.py`. Wired in `_app.py` via `get_approval_service().set_channel_manager(...)`.
- **Crons**: `CronManager` registered as the `cron_manager` workspace service (`app/workspace/workspace.py`, priority 40). HTTP surface is `app/crons/api.py`'s `router` (`/cron/...`). `CronJobSpec` and the rest of `models.py` are the public schema for the cron UI / API.
- **MCP**: `from qwenpaw.app.mcp import MCPClientManager, MCPConfigWatcher, HttpStatefulClient, StdIOStatefulClient`. `MCPClientManager` registered as the `mcp_manager` workspace service (priority 20); `MCPConfigWatcher` created in `app/workspace/service_factories.py::create_mcp_config_watcher`. The runner reads clients via `get_clients()` (`app/runner/runner.py`, `runtime/stream_query.py`).

## AgentScope Integration

- **MCP clients build directly on agentscope.** `stateful_client.py` imports `from agentscope.mcp import MCPToolFunction, StatefulClientBase`; both `StdIOStatefulClient` and `HttpStatefulClient` subclass `StatefulClientBase` and are documented as *drop-in replacements* for `agentscope.mcp.StdIOStatefulClient` / `HttpStatefulClient` that fix a cross-task lifecycle leak. `get_callable_function` returns an `agentscope.mcp.MCPToolFunction`, which the agentscope toolkit invokes; the live client list flows from `MCPClientManager.get_clients()` into the agent's toolkit at query time. See [../agentscope-v2/building-blocks/tool.md](../agentscope-v2/building-blocks/tool.md) for how agentscope models tools and MCP, and [../agentscope-v2/building-blocks/workspace.md](../agentscope-v2/building-blocks/workspace.md) for the workspace/service model these managers plug into.
- **Crons reuse agentscope-runtime exceptions.** `crons/manager.py` and `crons/api.py` import `ConfigurationException` from `agentscope_runtime.engine.schemas.exception`. Cron execution drives the qwenpaw runner's `stream_query`, which is the agentscope-backed agent loop (see [../agentscope-v2/deploy-agent-service.md](../agentscope-v2/deploy-agent-service.md)).
- **Approvals** are agentscope-agnostic; they integrate with qwenpaw's own tool-guard layer (`qwenpaw.security.tool_guard`), not directly with agentscope.

## Extension Points & Gotchas

- **Approval is a global singleton.** `get_approval_service()` returns one process-wide `ApprovalService`; all agents/workspaces share it. Records are **in-memory only** — never persisted across restarts. The GC thresholds (`_GC_PENDING_MAX_AGE_SECONDS=1800`, `_GC_MAX_PENDING=200`) silently time out old pending requests; long-blocking tools must use a sensible `timeout_seconds`. Always resolve via `resolve_request` / cancellation helpers so the underlying `Future` is set and the waiting tool unblocks.
- **Cron day-of-week numbering trap.** APScheduler v3 uses ISO weekday numbering (0=Mon) while crontab uses 0=Sun; `from_crontab()` does **not** convert. `ScheduleSpec.normalize_cron_5_fields` + `_crontab_dow_to_name` normalize the 5th field to abbreviations (`mon`…`sun`) at validation time. Only **5-field** cron is supported (4/3 fields are padded, 6-field "seconds" is rejected). If you add new schedule shapes, mirror the validation in both `models.py` and `manager.py::_build_trigger`.
- **`CronManager` is per-agent and assumes it is started.** `reschedule_heartbeat`/`reschedule_dream` warn and no-op if `_started` is False. Heartbeat/dream jobs are driven from config (`get_heartbeat_config`, `get_dream_cron`), not from `jobs.json`.
- **`save_result_to_inbox` default rule.** When unset, it defaults OFF only for `text` + recurring(`cron`) jobs, ON for everything else (`models.py::_validate_task_type_fields`). Changing this changes inbox behavior for existing jobs.
- **MCP lifecycle must stay single-task.** The whole reason `stateful_client.py` exists is to keep `__aenter__`/`__aexit__` in one task. Do **not** refactor `connect`/`close` to enter/exit the `AsyncExitStack` in different tasks, or the original anyio cancel-scope leak returns. `replace_client` is deliberately three-phase (connect new → swap under lock → close old outside lock); keep async I/O out of the locked section.
- **Tool-name sanitization is load-bearing.** MCP allows `.`/`/`/`:` in tool names but model APIs do not. The whitelist (`MCPClientConfig.tools`) stores **sanitized** names. If you bypass `get_callable_function` and call `call_tool` directly, you must pass the **real** MCP name (it does not translate aliases).
- **Subprocess reaping.** `kill_orphaned_mcp_children(include_active=False)` only reaps orphans; passing `include_active=True` is for final shutdown only — using it mid-reload could kill a freshly-registered workspace's children. The PID registry is module-global and shared across all `StdIOStatefulClient` instances.
- **`MCPConfigWatcher` gives up after 3 failures** per client (per config hash). A persistently failing MCP server won't be retried until its config changes — edit the config to force a retry.
- **Empty `crons/__init__.py`.** The crons package has no re-exports; import concrete modules directly (`from ..crons.manager import CronManager`, `from ..crons.repo.json_repo import JsonJobRepository`).
- **Other `app/` subpackages** (`channels/`, `routers/`, `runner/`, `workspace/`) are out of scope here and are (or should be) covered by app-core / channel docs; this file intentionally covers only approvals, crons, and mcp.
