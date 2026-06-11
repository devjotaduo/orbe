# runtime

> Package path(s): `src/qwenpaw/runtime/` — `__init__.py`, `agent_factory.py`, `heartbeat.py`, `message_convert.py`, `stream_query.py`, `tool_guard.py`

## Purpose

The `runtime` package is qwenpaw's **agentscope 2.0 request-lifecycle layer**. It builds a fresh agent per request (`build_agent`), drives that agent's streaming reply loop, and translates the agentscope `AgentEvent` stream into the frontend's SSE "envelope" protocol (`Runner.stream_query`). It also provides the permission gate (`GuardedFunctionTool`) that routes every tool call through qwenpaw's tool-guard engine + approval service, and a heartbeat wrapper that keeps long SSE connections alive during idle waits. The modules are written against AS 2.0 APIs (note the many `from agentscope...` imports done lazily inside function bodies, and docstrings referencing "stock 2.0 agent" / "AS 2.0").

> Note: as of this writing the package's two public exports (`Runner`, `GuardedFunctionTool`) are **not imported anywhere else under `src/qwenpaw`**. The production request path is `src/qwenpaw/app/runner/runner.py`'s `AgentRunner`, which subclasses `agentscope_runtime.engine.runner.Runner` (the SDK Runner, on the agentscope 1.x runtime) rather than this package's `Runner`. This `runtime/` package therefore reads as the AS-2.0 counterpart/reference implementation that mirrors the 1.x `app/runner` path. Treat statements about "callers" below as the intended/internal wiring, not verified live call sites.

## Architecture

```
request (AgentRequest | dict)
        │
        ▼
Runner.stream_query  ──────────────────────────────────────────┐  (stream_query.py)
  │ 1. set ContextVars (workspace/agent/session/root_session)   │
  │ 2. build request_context dict (for tool approval routing)   │
  │ 3. _request_input_to_msgs(raw_input) ───► [Msg]  ───────────┼─► message_convert.py
  │ 4. build_agent(...) ──────────────────────► QwenPawAgent ───┼─► agent_factory.py
  │ 5. session.load_session_state(agent)                        │
  │ 6. slash-command intercept (dispatch_command)               │
  │ 7. agent.rebuild_sys_prompt()                               │
  │ 8. agent.reply_stream(inputs=msgs)                          │
  │       └─ wrapped by _iter_with_heartbeat ──────────────────┼─► heartbeat.py
  │ 9. for each AgentEvent → emit envelope(s):                  │
  │      TEXT_BLOCK_* → message/content (type=text)             │
  │      THINKING_BLOCK_* → message (type=reasoning)            │
  │      TOOL_CALL_* → message (type=plugin_call)               │
  │      TOOL_RESULT_* → message (type=plugin_call_output)      │
  │ 10. session.save_session_state(agent)                       │
        ▼
SSE envelope stream (AgentResponse / Message / TextContent / DataContent)

During tool execution, agentscope's PermissionEngine calls:
   GuardedFunctionTool.check_permissions(input_data, context) ──► tool_guard.py
        └─ guard engine + ApprovalService (ASK blocks on a Future)
```

`stream_query.py` is the orchestrator; the other four modules are its collaborators. `agent_factory` constructs the agent, `message_convert` adapts inbound messages, `heartbeat` protects the outbound stream, and `tool_guard` gates tools out-of-band (invoked by agentscope's permission engine, not directly by the Runner).

## Key Modules

### `stream_query.py` — `class Runner`

The base class providing the lifecycle hooks and the core translation loop.

- `__init__(self, *_args, **_kwargs)` — sets `self.session = None`.
- `async start()` / `async stop()` — default lifecycle; delegate to optional `init_handler` / `shutdown_handler` attributes if present.
- `async stream_query(self, request, *_args, **_kwargs) -> AsyncGenerator[Any, None]` — the heart of the module. Accepts an `AgentRequest` (or a dict, coerced via `AgentRequest(**request)`); fills in `session_id`/`user_id`; sets per-request ContextVars (`set_current_workspace_dir`, `set_current_agent_id`, `set_current_session_id`, `set_current_root_session_id`); builds the `request_context` dict; calls `build_agent`; loads session state; intercepts `/`-prefixed slash commands via `dispatch_command`; then iterates `agent.reply_stream(inputs=msgs)` (wrapped in `_iter_with_heartbeat`) and maps each event to envelopes. It reads instance attributes that subclasses are expected to provide: `workspace_dir`, `agent_id`, `session`, `_mcp_manager`, `memory_manager`, `context_manager`.

Event→envelope mapping (driven by `agentscope.event.EventType`):
- `TEXT_BLOCK_START/DELTA/END` → one assistant `Message` plus streamed `TextContent` (delta then final).
- `THINKING_BLOCK_START/DELTA/END` → a separate `Message` with `type=reasoning`.
- `TOOL_CALL_START/DELTA/END` → accumulates JSON args, emits a `plugin_call` `Message` with a `DataContent` `{name, call_id, arguments}`.
- `TOOL_RESULT_START/TEXT_DELTA/DATA_DELTA/END` → emits a `plugin_call_output` `Message` (in_progress stub, then completed with `{name, call_id, output, state}`); binary/structured output accumulates into `output_data_blocks`.
- Error handling: `Exception` is normalized via `convert_model_exception` and dumped via `write_query_error_dump`; `BaseException` (e.g. `CancelledError`) cancels pending approvals (`cancel_all_pending_by_root_session`), calls `agent.interrupt()`, and re-raises.

### `agent_factory.py` — `build_agent(...)`

`build_agent(session_id, agent_id=None, workspace_dir=None, mcp_clients=None, request_context=None, memory_manager=None, context_manager=None) -> QwenPawAgent`. Constructs a fresh `QwenPawAgent` per request (no agent-instance caching — continuity comes from session load/save). Resolves agent config via `load_agent_config`, **validates an active model is configured** (raises `RuntimeError("No active model configured; pick one in the UI")` otherwise, checking both `agent_config.active_model` and `ProviderManager.get_instance().get_active_model()`), builds an env context via `build_env_context` (time/session/working-dir/OS/shell), defaulting the shell to the configured `shell_command_executable`, then `$SHELL`, then `cmd.exe`/`/bin/sh`. Wires in `LightContextManager` when no `context_manager` is supplied.

### `message_convert.py`

Converts inbound 1.x-style messages to AS 2.0 `Msg` objects and maps media types for the frontend.
- `_request_input_to_msgs(input_list) -> List[Msg]` — builds `agentscope.message.Msg` objects from `AgentRequest.input`, producing `TextBlock` and `DataBlock(source=URLSource(...))` content; handles `text`/`image`/`audio`/`video`/`file`; maps `tool` role → `assistant`; skips messages with no blocks. Imports of `agentscope.message` are guarded — on failure it logs and **drops user input** (returns `[]`).
- `_ensure_url_scheme(url)` — `unquote()`s then prepends `file://` for absolute/`~` local paths (avoids `Path.as_uri()` re-encoding).
- `_media_type_to_block_type(media_type)` — maps a MIME major type to the 1.x block type the frontend renderer expects (`image`/`video`/`audio`, else `data`).
- `_get_last_user_text(msgs)` — returns the last message's `get_text_content()` (used for slash-command detection).

### `heartbeat.py`

- `HEARTBEAT_INTERVAL_SECONDS = 25.0`, sentinel `_HEARTBEAT_TICK`.
- `async _iter_with_heartbeat(source_iter, interval)` — wraps an async iterator so that on each `interval`-second idle gap it yields `_HEARTBEAT_TICK` instead of blocking. Key detail: it uses `asyncio.shield(pending)` around the in-flight `__anext__()` task so `wait_for`'s timeout cancellation does **not** kill the underlying task — critical because a tool-guard ASK can block up to 300s and must survive many heartbeats. Cancels the pending task in `finally`.

### `tool_guard.py` — `class GuardedFunctionTool`

A permission-checked `FunctionTool` wrapper. `GuardedFunctionTool` itself subclasses nothing at import time; its `__new__` **lazily** builds a real subclass of `agentscope.tool.FunctionTool` (so importing the module doesn't require agentscope present). Construction binds `agent_id` and `request_context` onto the instance (`_qp_agent_id`, `_qp_request_context`) — explicit context passing, not ContextVars.

- `_resolve_execution_level(self) -> str` — reads the per-agent `approval_level` from `load_agent_config` and normalizes via `ToolExecutionLevel.from_config(...)` to one of `off`/`auto`/`smart`/`strict`; returns `"bypass"` when no `agent_id` is bound or config loading fails (keeps tools runnable in degraded environments).
- `async check_permissions(self, input_data=None, context=None, *_extra_args, **_extra_kwargs)` — matches agentscope's `PermissionEngine.check_permission` call site. Returns an `agentscope.permission.PermissionDecision` (`ALLOW`/`DENY`). Logic order: `bypass`/`off` → ALLOW; denied-list → DENY (`_with_no_retry_instruction`); STRICT → guard all tools (synthesize INFO result if none); auto-deny rules → DENY; SMART → auto-allow `INFO`/`LOW` severity; everything else → `_ask_user_approval`.
- `_ask_user_approval(...)` — creates a `PendingApproval` via `get_approval_service()` and **blocks on its Future** (`wait_for_approval`, timeout `TOOL_GUARD_APPROVAL_TIMEOUT_SECONDS`). ASK is implemented by creating the pending record (the frontend polls `/console/push-messages`) rather than emitting `PermissionBehavior.ASK`. Maps `ApprovalDecision.APPROVED/DENIED`/timeout → `PermissionDecision`. Denials append a "do not retry" system instruction via `_with_no_retry_instruction`.

### `__init__.py`

Public surface: `from .stream_query import Runner` and `from .tool_guard import GuardedFunctionTool`; `__all__ = ["Runner", "GuardedFunctionTool"]`.

## Entry Points & Public API

- **`Runner`** (`runtime.Runner`) — base class meant to be subclassed by a workspace runner; the subclass supplies `workspace_dir`, `agent_id`, `session`, `_mcp_manager`, `memory_manager`, `context_manager`, and consumers iterate `stream_query(request)` to get the SSE envelope stream. (The shipped production runner, `app/runner/runner.py::AgentRunner`, currently extends the SDK Runner instead — see the note in Architecture.)
- **`GuardedFunctionTool`** — a drop-in `FunctionTool` replacement that the agent toolkit would register so agentscope's permission engine routes each call through qwenpaw's guard. Invoked by agentscope (via `check_permissions`), not called directly.
- **`build_agent`** — module-level factory imported by `stream_query` (`from .agent_factory import build_agent`); usable standalone to construct a wired `QwenPawAgent`.
- The envelope/event helpers in `message_convert.py` and `heartbeat.py` are underscore-prefixed internals of `stream_query`.

## AgentScope Integration

This area is tightly coupled to agentscope 2.0:

- **Messages** — `agentscope.message.Msg`, `TextBlock`, `DataBlock`, and `agentscope.message._block.URLSource` (`message_convert.py`). See [../agentscope-v2/building-blocks/message-and-event.md](../agentscope-v2/building-blocks/message-and-event.md).
- **Events** — `agentscope.event.EventType` and the agent's `reply_stream(...)` async event API drive the translation loop (`stream_query.py`). See [../agentscope-v2/building-blocks/message-and-event.md](../agentscope-v2/building-blocks/message-and-event.md) and [../agentscope-v2/building-blocks/agent.md](../agentscope-v2/building-blocks/agent.md).
- **Tools / Permissions** — `agentscope.tool.FunctionTool` (subclassed) and `agentscope.permission.{PermissionBehavior, PermissionDecision}` (`tool_guard.py`); the `check_permissions(input_data, context)` signature matches `PermissionEngine.check_permission`. See [../agentscope-v2/building-blocks/tool.md](../agentscope-v2/building-blocks/tool.md) and [../agentscope-v2/building-blocks/permission-system.md](../agentscope-v2/building-blocks/permission-system.md).
- **Agent** — `build_agent` constructs qwenpaw's `QwenPawAgent` (a subclass of the agentscope ReAct agent); `stream_query` calls `agent.reply_stream`, `agent.rebuild_sys_prompt`, `agent.interrupt`, and reads `agent.toolkit.tool_groups[0].tools`. See [../agentscope-v2/building-blocks/agent.md](../agentscope-v2/building-blocks/agent.md) and [../agentscope-v2/api-reference/agent.md](../agentscope-v2/api-reference/agent.md).

## Extension Points & Gotchas

- **One agent per request.** `build_agent` deliberately does not cache agents; conversation continuity lives entirely in `session.load_session_state` / `save_session_state`. Don't add agent caching expecting state to persist there.
- **Active-model validation throws.** `build_agent` raises `RuntimeError("No active model configured; pick one in the UI")` before construction. Any new caller must handle that.
- **Lazy agentscope imports are intentional.** Both `tool_guard.py` (via `__new__`) and most of `stream_query.py`/`message_convert.py` import `agentscope` inside function bodies so the modules import cleanly without agentscope. Preserve this — don't hoist `import agentscope` to module top-level.
- **Heartbeat shielding is load-bearing.** The `asyncio.shield` in `_iter_with_heartbeat` is what lets a 300s tool-approval wait survive ~12 heartbeats without losing the pending `__anext__()`. Removing the shield would silently drop in-flight events on every timeout tick.
- **Tool-guard `bypass`.** When no `agent_id` is bound (or config load fails), `GuardedFunctionTool` falls back to `bypass` = ALLOW. This is a real security-relevant default: a tool with no `agent_id` runs unguarded. Ensure `agent_id`/`request_context` are passed at construction in any production wiring.
- **ASK is poll-based, not push.** Approvals are surfaced by creating a `PendingApproval` that the frontend discovers via `/console/push-messages` polling, resolved by `/approval/{approve,deny}` endpoints. There is no SSE event for ASK; changing this contract requires frontend coordination.
- **Envelope contract mirrors `Builder.tsx` / `mergeToolMessages`.** The exact two-message (`plugin_call` + `plugin_call_output`) shape, the shared `call_id` in `content[0].data`, and the `in_progress`→`completed` status transitions are what drive the frontend's merged `<ToolCall>` accordion + spinner. Changing field names or emission order will break rendering. The module docstring documents the full envelope sequence.
- **Media block-type translation.** AS 2.0 uses `"data"` for all media; `_media_type_to_block_type` re-derives `image`/`video`/`audio` for the frontend. New media handling must keep this mapping consistent.
- **Relationship to `app/runner`.** Because the production path (`AgentRunner`) currently extends the SDK 1.x `Runner`, edits here may not affect live behavior. Before changing this package, confirm whether the intent is the AS-2.0 migration target or a still-inactive parallel implementation. (This is the one ambiguity not fully resolvable from the code alone.)
