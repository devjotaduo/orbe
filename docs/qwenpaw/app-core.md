# app (core: routers, runner, channels, workspace)

> Package path(s): `src/qwenpaw/app/` (top-level: `_app.py`, `__init__.py`, `auth.py`, `agent_context.py`, `multi_agent_manager.py`, `migration.py`, plus stores: `inbox_store.py`, `console_push_store.py`, etc.) and subpackages `routers/`, `runner/`, `channels/`, `workspace/`.

## Purpose

This is the service/runtime hosting layer of qwenpaw. It builds the FastAPI application (`_app.py`), wires up the REST/streaming API surface (`routers/`), manages the lifecycle of one or more independent agent runtimes (`workspace/` + `multi_agent_manager.py`), processes agent requests through the agentscope-runtime `Runner` abstraction (`runner/`), and bridges external messaging platforms (Telegram, Feishu, DingTalk, WeChat, voice/SIP, etc.) into that runtime (`channels/`). In short: it is the HTTP/streaming front door plus the per-agent component orchestration behind it.

## Architecture

The runtime is built around a **multi-agent, workspace-per-agent** model layered on top of the `agentscope_runtime` engine.

```
FastAPI app (_app.py)
 ├─ Middleware: AgentContextMiddleware → AuthMiddleware → (CORS)
 ├─ Routers (/api/...)           ← routers/__init__.py aggregates ~30 sub-routers
 ├─ Agent-scoped routers         ← /api/agents/{agentId}/...  (routers/agent_scoped.py)
 ├─ AgentApp.router (/api/agent) ← agentscope_runtime AgentApp wrapping a runner
 ├─ Voice router (/voice/...)    ← Twilio-facing, root-level
 └─ Console SPA static + catch-all
        │
        ▼
DynamicMultiAgentRunner (_app.py)   ← single runner the AgentApp talks to
        │  inspects X-Agent-Id / context → picks workspace
        ▼
MultiAgentManager (multi_agent_manager.py)  ← lazy-loads + caches Workspaces
        │
        ▼
Workspace (workspace/workspace.py)  ← one independent agent runtime
        │  registers services declaratively via ServiceDescriptor
        ▼
ServiceManager (workspace/service_manager.py)  ← priority-ordered start/stop
        ├─ runner (AgentRunner)            P10
        ├─ memory_manager / context_manager P20 (concurrent)
        ├─ mcp_manager / chat_manager       P20 (concurrent)
        ├─ channel_manager                  P20 (start_all in background)
        ├─ cron_manager                     P40
        └─ agent/mcp config watchers        P50/P51
```

Request flow: an HTTP request enters FastAPI → `AgentContextMiddleware` extracts the agent id (from path `/api/agents/{id}/...` or `X-Agent-Id` header) and stores it in a `ContextVar` → for agent queries the `AgentApp` calls `DynamicMultiAgentRunner.stream_query`/`query_handler`, which resolves the agent id via `agent_context.get_current_agent_id()`, asks `MultiAgentManager.get_agent(id)` for the `Workspace`, registers the run with the workspace `TaskTracker`, and delegates to `workspace.runner` (an `AgentRunner`). Channels feed the same `AgentRunner` from the other direction: external platform messages are normalized to `AgentRequest`, queued by `ChannelManager`, and processed through the runner, with replies rendered back to the platform.

Startup is two-phase (`_app.py` `lifespan`): a fast synchronous phase (< ~100ms target) that creates the managers and exposes them on `app.state`, then a background task (`_background_startup`) that loads plugins, starts all configured agents (`MultiAgentManager.start_all_configured_agents()`), registers plugin providers/commands/hooks, and wires the approval service. The server begins accepting requests immediately; the first request needing an agent awaits its lazy readiness.

## Key Modules

### `app/_app.py`
Builds the `FastAPI` `app` and the agentscope `AgentApp`. Defines:
- `class DynamicMultiAgentRunner` — a runner shim passed to `AgentApp(runner=...)`. Methods `async stream_query(request, ...)` and `async query_handler(request, ...)` resolve the target `Workspace` (`_get_workspace`), register/unregister the run with `workspace.task_tracker` (external task keys `ext-<uuid>`), and delegate to the real `workspace.runner`. `set_multi_agent_manager(manager)` injects the manager after lifespan init.
- `agent_app = AgentApp(app_name="QwenPaw", runner=runner, enable_stream_task=True, stream_task_queue="stream_query", stream_task_timeout=1800)`.
- `async lifespan(app)` — the two-phase startup/shutdown described above; sets `app.state.multi_agent_manager`, `provider_manager`, `local_model_manager`, `plugin_loader`, `plugin_registry`, `get_agent_by_id`.
- Router mounting: `/api` (aggregate), `/api/approval`, `/api/coding-mode`, agent-scoped `/api`, `agent_app.router` at `/api/agent`, voice at root, custom channel routes, then console SPA static + `/{full_path:path}` catch-all (with path-traversal guards). Also `GET /`, `/api/version`, `/api/doctor/runtime`.

### `app/multi_agent_manager.py` — `class MultiAgentManager`
Central registry of `Workspace` objects with **lazy loading** and concurrency-safe dedup.
- `async get_agent(agent_id) -> Workspace` — fast path returns cached; otherwise validates against `config.agents.profiles`, claims startup via a per-id `asyncio.Event` in `_pending_starts` (so concurrent callers wait rather than double-create), constructs/starts the `Workspace` outside the lock for parallel init, and caches it. Raises `ConfigurationException` for unknown/failed agents.
- Also exposes lifecycle helpers used in `_app.py`: `start_all_configured_agents()`, `stop_all()`, plus reload/cleanup machinery (`_cleanup_tasks`).

### `app/workspace/workspace.py` — `class Workspace`
Encapsulates one independent agent runtime. Owns an `agent_id`, a `workspace_dir`, a `TaskTracker`, and a `ServiceManager`. Components are exposed as read-only properties that delegate to the service manager: `runner`, `memory_manager`, `context_manager`, `mcp_manager`, `chat_manager`, `channel_manager`, `cron_manager`, `task_tracker`, `config`.
- `_register_services()` declares every component as a `ServiceDescriptor` with a `priority` (10/20/25/40/50/51) and `concurrent_init` flag — this is the heart of startup ordering.
- `async start()` — loads agent config, runs legacy weixin→wechat data migrations (`_migrate_legacy_weixin_data`), then `ServiceManager.start_all()`. On failure it calls `stop()` and re-raises.
- `async set_reusable_components(components)` — must be called before `start()`; supports hot-reload by reusing `memory_manager`/`context_manager`/`chat_manager` from a previous instance.
- `async stop(final=True)` — `final=False` skips reusable services (reload path).
- `set_manager(manager)` — back-reference for `/daemon` restart, also propagated to the runner.

### `app/workspace/service_manager.py` — `ServiceDescriptor`, `ServiceManager`
Declarative lifecycle framework. `ServiceDescriptor` (dataclass) fields: `name`, `service_class` (type or `Callable[[Workspace], type]`), `init_args` (callable returning kwargs), `post_init`/`reload_func` hooks (sync or async), `start_method`/`stop_method` names, `reusable`, `dependencies`, `priority` (lower starts earlier, reversed on shutdown), `concurrent_init`. `ServiceManager.register(descriptor)`, `set_reusable(name, instance)`, and `start_all()`/`stop_all()` resolve order by priority and run same-priority concurrent-init services together. `workspace/service_factories.py` holds the `create_mcp_service`, `create_chat_service`, `create_channel_service`, `create_agent_config_watcher`, `create_mcp_config_watcher` factory hooks referenced by the descriptors.

### `app/runner/runner.py` — `class AgentRunner(Runner)`
Subclass of `agentscope_runtime.engine.runner.Runner`; `framework_type = "agentscope"`. The actual request processor for a workspace.
- Constructor takes `agent_id`, `workspace_dir`, `task_tracker`; holds references to `memory_manager`, `context_manager`, `_chat_manager`, `_mcp_manager`, `_workspace`, `_manager`.
- `async query_handler(msgs, request=None, **kwargs)` — main entry. Detects slash-commands (`_is_command` → `run_command_path`), sets agent/session/user/channel context vars, drives the `QwenPawAgent` (agentscope react agent), and persists exchanges to the session.
- `async stream_query(request, **kwargs)` — overrides the base to stamp `created_at` on response events, otherwise delegates to `super().stream_query`.
- `_stream_printing_messages_interruptible(...)` — an interruptible variant of agentscope's `stream_printing_messages` that promptly cancels the agent task when the outer stream stops.

### `app/runner/` supporting modules
`manager.py` (`ChatManager` — ChatSpec CRUD over a `BaseChatRepository`, persistence only, not session state), `models.py` (`ChatSpec`, `ChatHistory`, `ChatsFile`, `ChatUpdate`, `SessionSource`), `repo/` (`BaseChatRepository`, `JsonChatRepository`), `session.py` (`SafeJSONSession` + legacy weixin session migration), `task_tracker.py` (`TaskTracker` — per-run task/queues/event buffer enabling streaming reconnect, multi-subscriber, and external-task registration via `register_external_task`/`unregister_external_task`), `command_dispatch.py` / `mission_dispatch.py` / `control_commands.py` (slash-command + mission handling), `api.py` (`/api/chats` router), `title_generator.py`, `query_error_dump.py`, `daemon_commands.py`.

### `app/channels/` — `ChannelManager`, `BaseChannel`, registry
- `manager.py` `class ChannelManager(channels)` — owns the per-channel queues and consumer loops; channels only implement how to consume. Uses `CommandRegistry` and `UnifiedQueueManager`; `_process_batch` merges native payloads / requests before dispatch; lifecycle via `start_all()`/`stop_all()` (the descriptor methods).
- `base.py` `class BaseChannel(ABC)` — base for all platform channels; bound to agentscope `AgentRequest`/`AgentResponse`/`Event` schemas, with `MessageRenderer`/`RenderStyle`, access control (`get_access_control_store`), and a `consume_one()` contract. Class attribute `uses_manager_queue` controls whether the manager owns its queue.
- `registry.py` — `_BUILTIN_SPECS` maps channel keys (`telegram`, `feishu`, `dingtalk`, `wechat`, `qq`, `voice`, `sip`, `console`, `matrix`, `mqtt`, `onebot`, `wecom`, `xiaoyi`, `yuanbao`, `imessage`, `discord`, `mattermost`) to module/class; `console` is required. Lazily imports channel classes so optional SDK deps don't break CLI startup; also loads custom channels from `CUSTOM_CHANNELS_DIR`. `register_custom_channel_routes(app)` (used in `_app.py`) mounts custom channel HTTP routes. `schema.py` defines `ChannelType`, `DEFAULT_CHANNEL`. Per-platform subpackages (`telegram/`, `feishu/`, `voice/`, `sip/`, etc.) implement `*Channel` classes plus card/dispatcher/codec helpers.

### `app/agent_context.py`
Context-propagation utilities backed by `ContextVar`s: `set/get_current_agent_id`, `_session_id`, `_root_session_id`, `_user_id`, `_channel`. `async get_agent_for_request(request, agent_id=None)` resolves the workspace with priority: explicit arg → `request.state.agent_id` (set by agent-scoped router) → `X-Agent-Id` header → active agent from config; raises `HTTPException` 404/403/500. `get_coding_dir(workspace)` returns the coding-mode project dir or the workspace dir. Used pervasively by routers as a FastAPI dependency.

### `app/auth.py` and `app/routers/agent_scoped.py`
`auth.py` — stdlib-only password hashing + JWT, `AuthMiddleware`, `auto_register_from_env`; auth is **off by default**, enabled via `QWENPAW_AUTH_ENABLED`; single-user, credentials in `auth.json` under `SECRET_DIR`. `agent_scoped.py` — `AgentContextMiddleware` (injects `agent_id`/`root_session_id` from path/headers into `request.state` and context vars) and `create_agent_scoped_router()` which re-mounts the standard routers under `/agents/{agentId}/`.

### `app/routers/__init__.py`
Aggregates ~30 feature routers into one `APIRouter` mounted at `/api`: `agents`, `config`, `console`, `cron`, `local_models`, `mcp`/`mcp_oauth`, `messages`, `providers`/`provider_oauth`, `runner` (chats), `market`, `skills`/`skills_stream`, `tools`, `workspace`, `envs`, `token_usage`, `agent_stats`, `auth`, `files`, `settings`, `plugins`/`frontend_plugin`, `backup`, `plan`, `fork`, `git`, `coding_project`, `access_control`. Also separate: `approval`, `coding_mode`, `voice`.

## Entry Points & Public API

- **App object**: `qwenpaw.app._app.app` (the `FastAPI` instance) and `agent_app` (`AgentApp`). This is what the server process serves.
- **Routers**: `qwenpaw.app.routers.router` (aggregate) and `create_agent_scoped_router()`.
- **Runtime managers** (exposed on `app.state` for routers/external callers): `multi_agent_manager`, `provider_manager`, `local_model_manager`, `plugin_loader`, `plugin_registry`, `get_agent_by_id`.
- **Workspace API**: `qwenpaw.app.workspace.{Workspace, ServiceManager, ServiceDescriptor}`.
- **Runner API**: `qwenpaw.app.runner.{AgentRunner, ChatManager, router, ChatSpec, ChatHistory, ChatsFile, BaseChatRepository, JsonChatRepository}`.
- **Channels**: `qwenpaw.app.channels.ChannelManager` (lazy `__getattr__`); `channels.registry.register_custom_channel_routes`, `get_channel_registry`.
- **Context helpers** (used by most routers as dependencies): `agent_context.get_agent_for_request`, `get_current_agent_id`, etc.

## AgentScope Integration

This area is the primary embedding point for the agentscope-runtime engine. Used APIs:
- `agentscope_runtime.engine.app.AgentApp` — wraps the runner and exposes the `/api/agent` router (`_app.py`).
- `agentscope_runtime.engine.runner.Runner` — base class of `AgentRunner` (`runner/runner.py`).
- `agentscope_runtime.engine.schemas.agent_schemas` — `AgentRequest`, `AgentResponse`, `Event`, `RunStatus`, content types (`TextContent`, `ImageContent`, …), `MessageType` (consumed throughout `channels/base.py` and the runner).
- `agentscope_runtime.engine.schemas.exception` — `AppBaseException`, `AgentException`, `ConfigurationException` (used in `_app.py`, `multi_agent_manager.py`, `runner.py`).
- `agentscope.message.Msg` / `TextBlock`, `agentscope.memory.InMemoryMemory`, and the agentscope streaming/printing pattern (`stream_printing_messages`) in the runner.

This codebase pins agentscope 1.0.20 (1.x APIs), not v2. The v2 knowledge base under [../agentscope-v2/](../agentscope-v2/) describes the newer runtime — see [deploy-agent-service.md](../agentscope-v2/deploy-agent-service.md) and [deploy-agent-team.md](../agentscope-v2/deploy-agent-team.md) for how AgentApp/runner deployment evolves; treat it as reference, not a description of the symbols above.

## Extension Points & Gotchas

- **Adding a workspace service**: register a new `ServiceDescriptor` in `Workspace._register_services()` with the right `priority` and a factory in `service_factories.py`. Mind ordering — runner is P10, core services P20 (concurrent), runner start is P25, cron P40, watchers P50/P51. Same-priority `concurrent_init=True` services start together, so do not introduce hidden cross-dependencies without declaring `dependencies`.
- **Adding a channel**: add an entry to `_BUILTIN_SPECS` in `channels/registry.py` and implement a `*Channel` subclass of `BaseChannel` (implement `consume_one`; respect `uses_manager_queue`). Imports are intentionally lazy so a missing optional SDK only disables that one channel — keep heavy SDK imports inside the channel module, not at registry import time. Only `console` is a required channel.
- **Adding a router**: create `routers/<name>.py` exporting `router`, then add it to the aggregate list in `routers/__init__.py`. To make it agent-scoped, it is automatically re-mounted under `/api/agents/{agentId}/` by `create_agent_scoped_router()` — write handlers to resolve the agent via `get_agent_for_request(request)` rather than hardcoding `default`.
- **Agent resolution precedence** is non-obvious and duplicated in two places (`agent_context.get_agent_for_request` and `DynamicMultiAgentRunner._get_workspace` via `get_current_agent_id`): path `agent_id` → `request.state.agent_id` → `X-Agent-Id` header → active agent from config. Context vars are set by `AgentContextMiddleware`; if you call runner code off the request path (crons, background tasks) you must set the context vars yourself or the wrong agent will be used.
- **Startup is asynchronous/lazy**: routers may receive requests before agents finish loading. `MultiAgentManager.get_agent` blocks on a per-id `asyncio.Event` until ready — do not assume `app.state.plugin_loader`/`plugin_registry` are populated early (they're set in the background task and start as `None`).
- **Background-task tracking for graceful reload**: external streaming runs must be registered with `workspace.task_tracker.register_external_task(run_key)` and unregistered in a `finally` (see `DynamicMultiAgentRunner`). Skipping this breaks graceful shutdown during agent reload (referenced as issue #3275).
- **Hot reload** reuses `memory_manager`/`context_manager`/`chat_manager` via `set_reusable_components` before `start()`; `Workspace.stop(final=False)` preserves them. Only services with `reusable=True` survive a non-final stop.
- **Legacy migrations** run at two layers: global on app startup (`migration.py`: `migrate_legacy_workspace_to_default_agent`, `ensure_default_agent_exists`, `ensure_qa_agent_exists`, `migrate_legacy_skills_to_skill_pool`) and per-workspace weixin→wechat data migration in `Workspace._migrate_legacy_weixin_data` (chats.json, jobs.json, sessions). These are guarded to warn-not-fail; a failure leaves files in their legacy state.
- **Route registration order matters**: the SPA catch-all `/{full_path:path}` in `_app.py` is registered last and must stay last, or it will shadow API routes. It contains explicit path-traversal guards (`..`, absolute-path rejection) — preserve them when editing.
