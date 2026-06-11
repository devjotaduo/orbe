# QwenPaw — Architecture Overview

High-level view of how the packages documented in this folder fit together. QwenPaw is a
**personal-AI-assistant framework**: it wraps **agentscope 1.0.20** (the agent/model/tool/memory
engine) and **agentscope-runtime** (request/response + exception schemas) with a multi-agent
service layer, channels, a CLI/TUI, a desktop shell, security guards, and an extensibility system.

## Request lifecycle (the hot path)

```
 ┌─────────────┐   ┌──────────────┐   ┌──────────────────────────────────────────┐
 │ Entry points│   │  app layer   │   │  agent + agentscope engine                │
 ├─────────────┤   ├──────────────┤   ├──────────────────────────────────────────┤
 CLI / copaw ──┐                                                    docs:
 TUI (ACP) ────┤                                                    cli.md
 channels ─────┼─▶ FastAPI app  ─▶ MultiAgentManager ─▶ Workspace ─▶ AgentRunner ─┐  app-core.md
 desktop(Tauri)┘   (_app.py)        (lazy per agent)     ServiceManager  (Runner)  │  app-integrations.md
                                                            │                      │
                                                   ┌────────┴─────────┐            │
                                                   │ MCPClientManager │            │
                                                   │ CronManager      │            ▼
                                                   │ ApprovalService  │   runtime.build_agent
                                                   └──────────────────┘   ─▶ QwenPawAgent          agents-core.md
                                                                              (= agentscope
                                                                               ReActAgent subclass)
                                                                                 │ reply_stream
                              ┌──────────────────────────────────────────────────┤
                              ▼                         ▼                         ▼
                      ProviderManager           Toolkit (agentscope)       Context / Memory
                      ─▶ ChatModelBase           register_tool_function     LightContextManager
                      providers.md /             agents-tools.md            BaseMemoryManager
                      local-models.md                  │                    agents-memory-mission.md
                                                       ▼
                                          GuardedFunctionTool / ToolGuardMixin
                                          ─▶ security.ToolGuardEngine  ─▶ ApprovalService (HITL)
                                          security.md / runtime.md
                                                       │
                                                       ▼
                              stream events ─▶ SSE envelope (schemas.Message) ─▶ channel / client
                                                       foundation.md
```

## Layers

1. **Entry points** — `cli/` (Click tree + Textual TUI over ACP), `tauri/` desktop sidecar, and
   `app/channels/` (chat platforms). All converge on the FastAPI app.
2. **Service layer** (`app/`) — `MultiAgentManager` lazily materializes a `Workspace` per agent; the
   `ServiceManager` declaratively boots per-workspace services (MCP, cron, channels) in priority
   order. `AgentRunner` (a `agentscope_runtime` `Runner`) processes each request.
3. **Agent engine** (`agents/` + `runtime/`) — `runtime.build_agent` constructs a `QwenPawAgent`
   (subclass of agentscope `ReActAgent`) with a model, formatter, toolkit, context manager, memory
   backend, and middleware chain; `Runner.stream_query` drives `reply_stream` and maps agentscope
   events onto the frontend SSE envelope.
4. **Models** (`providers/`, `local_models/`) — each `Provider` builds an agentscope `ChatModelBase`;
   `ProviderManager` is the singleton registry; local GGUF models are served via embedded llama.cpp.
5. **Tools** (`agents/tools/`) — plain functions registered on the agentscope `Toolkit` via
   `register_tool_function` (qwenpaw deliberately does **not** subclass `ToolBase` for most tools).
6. **Security** (`security/`, `runtime/tool_guard.py`) — every tool call passes the
   `ToolGuardEngine`; flagged calls block on the `ApprovalService` (human-in-the-loop), paralleling
   agentscope's own permission system (see [../agentscope-v2/building-blocks/permission-system.md](../agentscope-v2/building-blocks/permission-system.md)).
7. **Extensibility** (`plugins/`, `market/`, `agents/skill_system/`) — plugins register tools /
   providers / hooks / routers; skills are scanned, installed from a hub/marketplace, and
   materialized as tools.
8. **Cross-cutting** — `plan/` (agentscope `PlanNotebook` wrapper), `token_usage/`+`agent_stats/`
   (usage accounting), `backup/` (signed backup/restore), `config/`+`envs/` (config & secrets),
   `foundation` (`constant.py`, `schemas.py`, `exceptions.py`, `_compat/` shims).

## AgentScope integration points (where qwenpaw meets the engine)

| qwenpaw piece | agentscope API | doc |
|---|---|---|
| `QwenPawAgent` | `agentscope.agent.ReActAgent` (subclassed) | [agents-core.md](./agents-core.md) |
| `create_model_and_formatter`, providers | `agentscope.model.ChatModelBase` + `*ChatModel`, `agentscope.formatter.*` | [providers.md](./providers.md) |
| `agents/tools/*` | `agentscope.tool.Toolkit.register_tool_function`, `ToolResponse` | [agents-tools.md](./agents-tools.md) |
| context / memory | `agentscope.memory.InMemoryMemory` (subclassed) | [agents-core.md](./agents-core.md), [agents-memory-mission.md](./agents-memory-mission.md) |
| middleware chain | `agentscope.middleware.MiddlewareBase` | [agents-core.md](./agents-core.md) |
| `runtime.GuardedFunctionTool` | `agentscope.tool.FunctionTool` (subclassed), `agentscope.permission.*` | [runtime.md](./runtime.md) |
| `plan/` | `agentscope.plan.PlanNotebook`, `InMemoryPlanStorage`, `Plan` | [plan.md](./plan.md) |
| token recorder | `agentscope.model.ChatModelBase`, `ChatUsage`, `agentscope.token.TokenCounterBase` | [observability.md](./observability.md) |
| `_compat` | monkey-patches `agentscope.message.Msg` (`to_dict`/`from_dict`) | [foundation.md](./foundation.md) |
| request/response/errors | `agentscope_runtime.engine.schemas.*` | [app-core.md](./app-core.md), [foundation.md](./foundation.md) |

> ⚠️ Installed engine is **agentscope 1.0.20**; the reference KB documents the **2.0** line. When
> changing any integration point above, follow the guardian checklist
> ([../agentscope-v2/_guardian-checklist.md](../agentscope-v2/_guardian-checklist.md)) — verify the
> symbol against the **installed** lib and existing usage, not just the v2 docs.
