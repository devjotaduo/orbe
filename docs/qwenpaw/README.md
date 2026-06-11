# QwenPaw — Codebase Knowledge Base

Per-package developer documentation for **qwenpaw** (`src/qwenpaw/`), the personal-AI-assistant
framework built on **agentscope 1.0.20** + **agentscope-runtime**. Built by a team of 17
research agents reading the actual source. Companion to the AgentScope reference in
[`../agentscope-v2/`](../agentscope-v2/README.md).

Use this together with the [`dev-team`](../../.claude/skills/dev-team/SKILL.md) pipeline and the
[`agentscope-guardian`](../../.claude/skills/agentscope-guardian/SKILL.md) gate: before changing a
package, read its doc here to match the existing pattern.

> See [ARCHITECTURE.md](./ARCHITECTURE.md) for the high-level request flow that ties these together.

## Package map

### Agent core (`src/qwenpaw/agents/`)

| Doc | Covers | Key entry points |
|---|---|---|
| [agents-core.md](./agents-core.md) | The `QwenPawAgent` ReAct loop, model/formatter factory, routing, middleware chain, slash commands, tool-guard/coding mixins, system-prompt build, context & hooks | `QwenPawAgent`, `create_model_and_formatter`, `RoutingChatModel`, context managers, `build_agent_template` |
| [agents-memory-mission.md](./agents-memory-mission.md) | Pluggable memory backends + proactive triggers, PRD-driven mission mode, 3-tier skill system + hub, ACP server/client | `BaseMemoryManager`, `proactive_trigger_loop`, `SkillPoolService`/`SkillService`, `QwenPawACPAgent`, `run_qwenpaw_agent` |
| [agents-tools.md](./agents-tools.md) | Every agent-callable tool (file IO, search, shell, browser, media, inter-agent, AST/LSP, skills) and how each registers on the agentscope `Toolkit` | `read_file`/`edit_file`/`grep_search`/`execute_shell_command`/`browser_use`/`spawn_subagent`/`run_tool_batch`/… |

### Service / runtime (`src/qwenpaw/app/`, `runtime/`)

| Doc | Covers | Key entry points |
|---|---|---|
| [app-core.md](./app-core.md) | FastAPI app + 2-phase lifespan, `MultiAgentManager → Workspace → ServiceManager`, `AgentRunner`, channel bridge, routers | `qwenpaw.app._app.app`, `MultiAgentManager`, `Workspace`, `AgentRunner`, `ChannelManager` |
| [app-integrations.md](./app-integrations.md) | Approval service (HITL gating), per-agent cron/heartbeat scheduler, hot-reloadable MCP client manager | `ApprovalService`, `CronManager`, `MCPClientManager`, `MCPConfigWatcher` |
| [runtime.md](./runtime.md) | agentscope-2.0 request lifecycle: per-request agent build, streaming reply → SSE envelope, per-tool permission guard | `Runner.stream_query`, `build_agent`, `GuardedFunctionTool` |

### Models & providers

| Doc | Covers | Key entry points |
|---|---|---|
| [providers.md](./providers.md) | Uniform LLM-backend abstraction → agentscope `ChatModelBase`; `ProviderManager` singleton; OAuth | `ProviderManager`, `Provider.get_chat_model_instance`, `OpenAI/Anthropic/Gemini/DashScope/Ollama/...Provider` |
| [local-models.md](./local-models.md) | GGUF download + embedded llama.cpp server + think/tool-call tag parsing | `LocalModelManager`, `LlamaCppBackend`, `parse_tool_calls_from_text` |

### Security, planning, extensibility

| Doc | Covers | Key entry points |
|---|---|---|
| [security.md](./security.md) | Tool-guard engine + guardians, skill scanner + analyzers, Fernet secret store | `get_guard_engine`, `ToolGuardEngine.guard`, `scan_skill_directory`, `encrypt`/`decrypt` |
| [plan.md](./plan.md) | Thin layer over agentscope `PlanNotebook`: confirmation-gated hints, tool gating, SSE plan broadcast, response schemas | `SimplePlanToHint`, `set_plan_gate`, `broadcast_plan_update`, `plan_to_response` |
| [plugins.md](./plugins.md) | Plugin discovery/install/import, `PluginRegistry`, `PluginApi` facade (tools/providers/hooks/routers/commands) | `PluginLoader`, `PluginRegistry`, `PluginApi`, `PluginManifest` |
| [market.md](./market.md) | Skill marketplace search fan-out (ClawHub / ModelScope / Aliyun) → `MarketResult` | `search_market`, `list_providers`, `PROVIDERS` |

### Interfaces, platform, foundation

| Doc | Covers | Key entry points |
|---|---|---|
| [cli.md](./cli.md) | Lazy Click command tree, HTTP client, doctor diagnostics, Textual TUI over ACP | `qwenpaw.cli.main:cli` (`qwenpaw`/`copaw`), `run_doctor_checks`, `run_tui` |
| [platform.md](./platform.md) | Tauri desktop sidecar, Cloudflare tunnel, encrypted env store, `config.json` schema | `qwenpaw.tauri.entry:main`, `CloudflareTunnelDriver`, `load_envs`, `Config`/`load_config` |
| [backup.md](./backup.md) | Signed-zip workspace/config/secret backup + crash-safe transactional restore | `create_stream`, `execute_restore`, `import_backup` |
| [observability.md](./observability.md) | Token-usage recorder (model wrapper + buffered JSON), agent-stats service, bundled tokenizer | `get_token_usage_manager`, `TokenRecordingModelWrapper`, `AgentStatsService` |
| [foundation.md](./foundation.md) | Package bootstrap/logging, `constant.py` env hub, streaming envelope schemas, exception hierarchy, agentscope-1.x `_compat` shims, shared utils | `EnvVarLoader`, `schemas.Message`, `convert_model_exception`, `_compat msg_from_dict` |

## Provenance

- Built by the `document-qwenpaw` agent workflow (17 agents, one per package area), 2026-06-10.
- Each file lists the package paths it covers and grounds every symbol in real code.
- Refresh by re-running the workflow after significant code changes.
