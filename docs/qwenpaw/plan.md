# plan

> Package path(s): `src/qwenpaw/plan/` (`__init__.py`, `hints.py`, `broadcast.py`, `schemas.py`)

## Purpose
The `plan` package is QwenPaw's thin customization layer on top of AgentScope's
plan subsystem (`agentscope.plan`). It does **not** reimplement planning — it
supplies (1) a custom plan-to-hint generator (`SimplePlanToHint`) that adds a
user-confirmation gate and compact, language-consistent prompt hints, (2) a set
of gate/flag helper functions that constrain which tools the ReAct agent may run
while a plan is being confirmed or executed, (3) an in-process SSE broadcast +
live-plan cache so API clients can stream plan updates, and (4) Pydantic response
schemas that serialize an AgentScope `Plan` for HTTP endpoints.

## Architecture
The actual `Plan`, `SubTask`, `PlanNotebook`, and `InMemoryPlanStorage` objects
come from AgentScope. The runner (`app/runner/runner.py`) builds the
`PlanNotebook` and injects this package's pieces into it:

```
/plan <desc> query
      │
      ▼
runner.py ── creates PlanNotebook(plan_to_hint=SimplePlanToHint(),
      │                            storage=InMemoryPlanStorage())
      │       hint_gen.bind_notebook(nb)   # weakref back to notebook
      │       set_plan_gate(nb, True)      # only on explicit /plan entry
      │       nb.register_plan_change_hook("broadcast", _on_plan_change)
      ▼
ReActAgent._acting(tool_call)
      │   check_plan_tool_gate(nb, tool_name)  → blocks non-plan tools
      │   should_skip_auto_continue(nb)         → suppress auto-continue
      ▼
PlanNotebook mutates plan → _on_plan_change(nb, plan)
      │   sets nb._plan_just_mutated / _plan_recently_finished flags
      │   broadcast_plan_update(agent_id, payload, session_id)
      ▼
broadcast.py ── updates _live_plan_cache + pushes to SSE queues
      ▼
app/routers/plan.py ── GET /plan/current, SSE /plan/stream
```

Confirmation flow: after `create_plan`/`revise_current_plan` the agent sets
`nb._plan_awaiting_user_confirm = True` (pre-lock in `_acting`), which
`check_plan_tool_gate` uses to block every tool except the three plan-management
tools until the next user turn. The runner calls
`clear_plan_awaiting_user_confirm(nb)` at the start of each user query to reset
the same-turn-only flags.

## Key Modules

### `__init__.py`
Public surface of the package. Re-exports five symbols from `hints`:
`SimplePlanToHint`, `set_plan_gate`, `check_plan_tool_gate`,
`clear_plan_awaiting_user_confirm`, `should_skip_auto_continue`. Note that
`broadcast` and `schemas` symbols are **not** re-exported here — callers import
them via their submodule paths (e.g. `from ...plan.broadcast import ...`).

### `hints.py` — hint generation + tool gating
The largest module. Imports `DefaultPlanToHint` from
`agentscope.plan._plan_notebook` inside a `try/except ImportError`; if the import
fails, `SimplePlanToHint` is set to `None` and the class is not defined
(callers must tolerate this). Manipulates several **private** notebook
attributes (prefixed `_plan_`).

Module-level helpers:
- `set_plan_gate(plan_notebook, enabled: bool = True) -> None` — sets
  `nb._plan_tool_gate`.
- `clear_plan_awaiting_user_confirm(plan_notebook) -> None` — resets
  `_plan_awaiting_user_confirm`, `_plan_just_mutated`,
  `_plan_text_only_after_mutation`. Called once per user turn by the runner.
- `check_plan_tool_gate(plan_notebook, tool_name) -> str | None` — returns an
  error string (injected as a tool result) if `tool_name` must be blocked, else
  `None`. Two gates: the post-mutation confirmation lock
  (`_plan_awaiting_user_confirm`, only `create_plan`/`revise_current_plan`/
  `finish_plan` allowed — see `_PLAN_TOOLS_WHILE_AWAITING_USER_CONFIRM`) and the
  initial `/plan` gate (`_plan_tool_gate`, only `create_plan` until a plan
  exists). Auto-clears `_plan_tool_gate` once a plan exists.
- `should_skip_auto_continue(plan_notebook) -> bool` — True when auto-continue
  must be suppressed: while awaiting confirmation, just after a mutation
  (consumes `_plan_just_mutated`), or right after a plan was finished and not
  re-entered via `/plan`.
- `_compact_plan_text(plan) -> str` and `_count_states(plan)` — internal
  helpers; the former drops outcomes of done/abandoned subtasks to keep
  per-iteration context cost constant (`_DESC_LIMIT=80`, `_PLAN_DESC_LIMIT=200`).

`class SimplePlanToHint(DefaultPlanToHint)` — overrides the hint templates
(`at_the_beginning`, `when_a_subtask_in_progress`, `when_no_subtask_in_progress`,
`at_the_end`, `no_plan`) and adds new ones (`at_the_beginning_after_mutation`,
`recently_finished_guard`). All include the `_LANG_BLOCK` language-consistency
instruction. Key methods:
- `__call__(self, plan: "Plan | None") -> str | None` — resolves the bound
  notebook (via stored weakref), dispatches to `_hint_no_plan` or
  `_hint_with_plan`, wraps with `hint_prefix`/`hint_suffix`.
- `_hint_no_plan(self, nb)` / `_hint_with_plan(self, plan, nb)` — branch logic
  keyed on notebook flags and subtask state counts.
- `bind_notebook(self, plan_notebook) -> None` — stores a `weakref.ref` to the
  notebook in `_bound_notebook` so the hint generator can read gate flags
  without a strong reference cycle.

### `broadcast.py` — SSE fan-out + live plan cache
Module-level globals (process-wide, no auth/scoping):
- `_queues: dict[str, set[asyncio.Queue]]` keyed by `agent_id`.
- `_live_plan_cache: dict[str, dict[str, dict | None]]` keyed by
  `agent_id` then `session_id`.

Functions:
- `register_sse_client(agent_id) -> asyncio.Queue` — creates a bounded
  (`maxsize=256`) queue and registers it.
- `unregister_sse_client(agent_id, q) -> None`.
- `get_live_plan(agent_id, session_id=None) -> tuple[bool, dict | None]` —
  returns `(found, plan_data)` from cache; session-scoped if `session_id` given,
  else any cached plan for the agent.
- `clear_live_plan(agent_id, session_id=None) -> None`.
- `broadcast_plan_update(agent_id, payload, session_id=None) -> None` — on
  `payload["type"] == "plan_update"` updates the live cache, then pushes the
  payload (enriched with `session_id`) to every registered queue using
  `put_nowait`; silently drops on `asyncio.QueueFull`.

### `schemas.py` — HTTP response models
Pydantic v2 models:
- `SubTaskResponse` — `name`, `description`, `expected_outcome`, optional
  `outcome`, `state` (`Literal["todo","in_progress","done","abandoned"]`),
  `created_at`, `finished_at`.
- `PlanStateResponse` — top-level plan returned by `GET /plan/current`
  (`id`, `name`, `description`, `expected_outcome`, `state`, `subtasks`, plus
  timestamps and `outcome`).
- `PlanConfigResponse` — `{ enabled: bool }`.
- `plan_to_response(plan) -> PlanStateResponse` — converts an AgentScope `Plan`
  (with `.subtasks`) into the response model. Accepts an untyped `plan` and
  reads attributes directly, so it works for any object with the expected shape.

## Entry Points & Public API
Consumers inside `src/qwenpaw`:
- `app/runner/runner.py` — imports `SimplePlanToHint`, `set_plan_gate`
  (build/gate the notebook), `broadcast_plan_update`, `plan_to_response`
  (the `_on_plan_change` hook), and `clear_plan_awaiting_user_confirm`
  (per-turn reset).
- `agents/react_agent.py` — `_acting()` imports `check_plan_tool_gate`;
  auto-continue logic imports `should_skip_auto_continue`.
- `app/routers/plan.py` — imports `get_live_plan`, `register_sse_client`,
  `unregister_sse_client` (SSE endpoint) and `PlanConfigResponse`,
  `PlanStateResponse`, `plan_to_response` (REST endpoints `GET /plan/current`,
  config toggle, `/plan/stream`). It also reconstructs a `Plan` from persisted
  session state via `_plan_from_session_state`.
- `app/runner/command_dispatch.py` — imports `broadcast_plan_update`.

The package itself does not register routes; `app/routers/plan.py` (mounted via
`app/routers/__init__.py` and `agent_scoped.py`) owns the HTTP layer.

## AgentScope Integration
This area sits directly on AgentScope's plan module:
- `SimplePlanToHint` subclasses `agentscope.plan._plan_notebook.DefaultPlanToHint`
  (a private module path — see Gotchas).
- The runner constructs `agentscope.plan.PlanNotebook` and
  `agentscope.plan.InMemoryPlanStorage`, wires `SimplePlanToHint` as
  `plan_to_hint`, and uses `PlanNotebook.register_plan_change_hook(...)`.
- `schemas.plan_to_response` and `routers/plan.py` consume `agentscope.plan.Plan`
  / `SubTask` objects (and reconstruct `Plan(**plan_data)` from session state).
- Hint generation relies on AgentScope `Plan`/`SubTask` methods such as
  `plan.to_markdown()` and `subtask.to_markdown(detailed=True)`.

There is no dedicated plan page in the AgentScope v2 KB; the nearest relevant
reference is the agent building block:
[../agentscope-v2/building-blocks/agent.md](../agentscope-v2/building-blocks/agent.md)
and [../agentscope-v2/api-reference/agent.md](../agentscope-v2/api-reference/agent.md).
(Note: the KB documents AgentScope **v2**, whereas QwenPaw pins **1.0.20**, so
exact plan APIs may differ — verify against the installed package.)

## Extension Points & Gotchas
- **Private AgentScope API.** `SimplePlanToHint` imports from
  `agentscope.plan._plan_notebook` (underscore module). This is brittle across
  AgentScope versions; the `try/except ImportError` degrades `SimplePlanToHint`
  to `None`. Any caller (including the runner's `try/except`) must tolerate the
  class being absent.
- **Private notebook attributes.** All gating logic mutates undocumented
  `PlanNotebook` attributes: `_plan_tool_gate`, `_plan_awaiting_user_confirm`,
  `_plan_just_mutated`, `_plan_recently_finished`,
  `_plan_text_only_after_mutation`, plus QwenPaw-added `_qp_had_plan` /
  `_qp_prev_plan_id` (set in the runner's `_on_plan_change`). These are not part
  of AgentScope's public contract and may break on upgrade.
- **Flag lifecycle is split across files.** Flags are *set* in
  `react_agent._acting` (pre-lock for `create_plan`/`revise_current_plan`) and
  in the runner's `_on_plan_change` hook, *read* in `hints.py`, and *cleared* in
  `clear_plan_awaiting_user_confirm` (per user turn) and inside
  `should_skip_auto_continue` (which consumes `_plan_just_mutated`). When adding
  a new gate, update all three sites or the gate will leak between turns.
- **Confirmation gate set BEFORE execution.** `_acting` sets
  `_plan_awaiting_user_confirm = True` *before* running the mutation tool so that
  parallel tool calls (`asyncio.gather`) cannot slip an execution tool past the
  gate. Preserve this ordering.
- **Broadcast state is process-global and unauthenticated.** `_queues` and
  `_live_plan_cache` are plain module dicts with no scoping/tickets/auth
  (documented in the module docstring). Suitable for single-process serving
  only; multi-process/multi-worker deployments would not share this state.
- **Queue overflow is silent.** `broadcast_plan_update` drops messages on a full
  (256-deep) queue with only a warning log — slow SSE clients can miss updates;
  clients should reconcile via `GET /plan/current` rather than relying solely on
  the stream.
- **`weakref` binding.** `bind_notebook` stores a weakref; if the notebook is
  garbage-collected the hint generator's `__call__` resolves `nb` to `None` and
  falls back to no-flag behavior. Keep the notebook alive for the agent's
  lifetime.
- **`no_plan` is scoped.** The `no_plan` hint is only emitted when
  `_plan_tool_gate` is set (explicit `/plan` entry), so ordinary chat is not
  pushed into plan creation.
