# agents (core)

> Package path(s): `src/qwenpaw/agents/` top-level modules — `react_agent.py`, `model_factory.py`, `routing_chat_model.py`, `middlewares.py`, `command_handler.py`, `coding_mode_mixin.py`, `tool_guard_mixin.py`, `prompt.py`, `prompt_builder.py`, `schema.py`, `templates.py` — plus subpackages `src/qwenpaw/agents/context/` and `src/qwenpaw/agents/hooks/`.
>
> (Sibling subpackages `tools/`, `skill_system/`, `memory/`, `mission/`, `acp/`, `skills/`, `md_files/`, `utils/` are referenced here but documented elsewhere.)

## Purpose

This area is the heart of the QwenPaw agent: it defines `QwenPawAgent`, a subclass of agentscope's `ReActAgent` that wires together built-in tools, dynamically loaded skills, MCP clients, memory/context management, model+formatter selection, system-prompt assembly, slash-command handling, tool-guard security interception, and Coding Mode. It owns the ReAct loop overrides (`_reasoning`, `_acting`, `_summarizing`, `reply`) and the surrounding plumbing (middlewares, hooks, context managers) that adapt agentscope 1.0.20 / 2.0 to QwenPaw's needs.

## Architecture

```
                       create_model_and_formatter()   ──►  (RetryChatModel( TokenRecordingModelWrapper( provider model )), formatter)
                                  │                                  ▲
                                  │                                  │ (optional)  RoutingChatModel  → local / cloud endpoints
                                  ▼
   QwenPawAgent(CodingModeMixin, ToolGuardMixin, ReActAgent)
      ├─ _create_toolkit()      → agentscope Toolkit (+ builtin tools, plugin tools, task tools, coding tools)
      ├─ _register_skills()     → toolkit.register_agent_skill(...) per effective skill
      ├─ _build_sys_prompt()    → prompt.build_system_prompt_from_working_dir() + PromptBuilder (host anchors + plugin sections)
      ├─ memory = AgentContext  ← context_manager.get_agent_context()   (token-aware InMemoryMemory)
      ├─ command_handler        = CommandHandler(...)        (/compact, /new, /clear, /history, /plan ...)
      ├─ _register_hooks()      → BootstrapHook + context_manager lifecycle hooks
      └─ ReAct loop overrides:  _reasoning / _acting / _summarizing / reply / print

   Per-request setup is applied via agentscope middlewares (middlewares.py):
      BootstrapMiddleware  (on_reasoning)  and  RequestSetupMiddleware (on_reply)
```

Construction order inside `QwenPawAgent.__init__` (`react_agent.py`): resolve effective skills → build toolkit → register skills → build system prompt → `create_model_and_formatter()` → `super().__init__()` (ReActAgent) → register memory tools → attach `AgentContext` as `self.memory` → create `CommandHandler` → `_register_hooks()`. MCP clients are registered *after* construction via the async `register_mcp_clients()`.

The MRO is **`QwenPawAgent → CodingModeMixin → ToolGuardMixin → ReActAgent`**. Each mixin override of `_acting` / `_reasoning` / `_build_sys_prompt` must call `super()` so the whole chain stays active (documented in the class docstring).

## Key Modules

### `react_agent.py` — `class QwenPawAgent(CodingModeMixin, ToolGuardMixin, ReActAgent)`
The main agent. Responsibilities and notable public/override methods:
- `__init__(agent_config: AgentProfileConfig, env_context=None, mcp_clients=None, memory_manager=None, context_manager=None, request_context=None, namesake_strategy="skip", workspace_dir=None, task_tracker=None, plan_notebook=None)` — full wiring described above.
- `_create_toolkit(namesake_strategy, effective_skills)` — builds an agentscope `Toolkit`; registers a hardcoded built-in tool map (e.g. `execute_shell_command`, `read_file`, `write_file`, `edit_file`, `grep_search`, `glob_search`, `browser_use`, `spawn_subagent`, `delegate_external_agent`, ...), discovers plugin tools from `tools.__all__` (gated by config for security), auto-registers background-task tools (`view_task`/`wait_task`/`cancel_task`) when any enabled tool sets `async_execution`, and delegates Coding Mode tools to `_register_coding_mode_tools`.
- `_register_skills(toolkit, effective_skills)` — `toolkit.register_agent_skill(...)` per resolved skill dir.
- `_build_sys_prompt()` — combines `build_system_prompt_from_working_dir(...)` with `PromptBuilder` (host anchors `workspace`/`multimodal`/`env_context` + plugin sections). Overridden again by `CodingModeMixin`.
- `_register_hooks()` — registers `BootstrapHook` (pre_reasoning) and, if a context manager is present, its `pre_reply`/`pre_reasoning`/`post_acting`/`post_reply` lifecycle hooks via `register_instance_hook`.
- `rebuild_sys_prompt()` — rebuilds prompt and patches the stored system message (used after `load_session_state`).
- `async register_mcp_clients(namesake_strategy="skip")` — registers each MCP client on the toolkit with recovery/reconnect/rebuild logic (`_recover_mcp_client`, `_reconnect_mcp_client`, `_rebuild_mcp_client`) for broken `StdIOStatefulClient` / `HttpStatefulClient` sessions.
- `async _reasoning(tool_choice=None)` — override adding (1) proactive media stripping when the model is not multimodal or capability-cache says `rejects_media`, (2) passive fallback that strips media and retries on a 400/media error then records the learning, (3) the plan-gate `tool_choice="none"` enforcement, and (4) the text-only auto-continue nudge (`_auto_continue_if_text_only`). Calls `super()._reasoning` to keep ToolGuardMixin active.
- `async _acting(tool_call)` — fixes stringified JSON args for plan tools, applies the plan-tool gate (`check_plan_tool_gate`) pre-locking `_plan_awaiting_user_confirm`, then delegates to `super()._acting` (ToolGuardMixin).
- `async _summarizing()` — same media-strip layers as `_reasoning`, plus stripping stray `tool_use` blocks (some models emit them with no tools) and appending the bilingual `_ROUND_END_NOTICE`.
- `async reply(msg=None, structured_model=None)` — sets per-request ContextVars, processes file/media blocks, short-circuits slash-commands via `command_handler`, wraps the call in `apply_skill_config_env_overrides`. (Note: `RequestSetupMiddleware` covers the same setup for the streaming path.)
- `print(...)`, `interrupt(...)`, `_broadcast_to_subscribers(...)`, `_strip_media_blocks_from_memory()` and the capability helpers `_model_rejects_media`/`_get_model_key`.

### `model_factory.py` — `create_model_and_formatter(agent_id=None) -> (ChatModelBase, FormatterBase)`
Central factory (largest module, ~1100 lines). Resolves the agent-specific or global active model via `ProviderManager`, builds a matching formatter through `_create_formatter_instance` (a "file-block-support" wrapper that also runs request-time message normalization), then wraps the model as `RetryChatModel(TokenRecordingModelWrapper(provider_id, model), retry_config, rate_limit_config)`. Contains extensive media/formatter normalization helpers per provider family — `_format_anthropic_messages`, `_format_openai_video_block`, `_fixup_media_list`, `_promote_tool_result_videos`, `_fix_image_mime_types`, `_file_url_to_path`, etc. The `_qwenpaw_force_strip_media` formatter flag (set by `react_agent`) routes through `_normalize_messages_for_formatter`.

### `routing_chat_model.py` — `class RoutingChatModel(ChatModelBase)`
A `ChatModelBase` that dispatches each call to a `local` or `cloud` `RoutingEndpoint` based on `RoutingPolicy.decide()` (driven by `AgentsLLMRoutingConfig.mode`, `local_first` vs `cloud_first`). Supporting types: `RoutingDecision`, `RoutingEndpoint`, `RoutingPolicy`, `Route = Literal["local","cloud"]`.

### `middlewares.py` — agentscope 2.0 `MiddlewareBase` implementations
- `BootstrapMiddleware(bootstrap_hook)` — runs the bootstrap hook in `on_reasoning` before delegating to `next_handler()`.
- `RequestSetupMiddleware(workspace_dir, agent_id, agent_config, request_context)` — `on_reply` per-reply setup that is the single source of truth for both `reply()` and `reply_stream()`: sets workspace/session/recent-bytes/shell ContextVars, processes file/media blocks on `input_kwargs["inputs"]`, and wraps the reply in `apply_skill_config_env_overrides`. Its docstring explains *why* this moved out of `reply()` (the 2.0 streaming split).

### `tool_guard_mixin.py` — `class ToolGuardMixin`
Adds tool-guard security interception to the ReAct loop via `_acting`/`_reasoning` overrides implementing a deny / guard / approve flow. Lazy-inits `_tool_guard_engine` (`security.tool_guard.engine.get_guard_engine`) and `_tool_guard_approval_service` (`app.approvals.get_approval_service`); reads the agent's `ToolExecutionLevel`; localizes user messages via `_TOOL_GUARD_I18N`. Approval is only required when a `session_id` is present (`_should_require_approval`).

### `coding_mode_mixin.py` — `class CodingModeMixin`
Activated when `agent_config.coding_mode.enabled`. Overrides `_build_sys_prompt` to append `_CODING_SYSTEM_PROMPT_TEMPLATE` (task-tracking `*_TODO.md`, code-reference `path:line` convention, lsp/ast_search tool preference, absolute-path/cwd rules, active project dir). `_register_coding_mode_tools(toolkit, ...)` smart-registers the `lsp` tool (`make_lsp_tool` over `detect_available_lsp_languages`) and `ast_search` (`ast_tool`, gated on `is_ast_grep_available()`); both failures are logged, never raised. `_get_coding_project_dir()` reloads agent config from disk to avoid stale `project_dir`.

### `command_handler.py` — `class CommandHandler(ConversationCommandHandlerMixin)`
Handles slash/system commands. `SYSTEM_COMMANDS` = `{compact, new, clear, history, compact_str, summarize_status, message, dump_history, load_history, proactive, plan}`. `is_command()`/`is_conversation_command()` detect commands (note `/plan <args>` passes through to plan mode; bare `/plan` is a status command). `SYSTEM_COMMAND_DESCRIPTIONS` is the small curated subset (`clear`, `compact`) advertised to ACP/console clients. Constructed with the agent's `memory` (`AgentContext`), `memory_manager`, and `context_manager`; compaction delegates to `context_manager.compact_context`.

### `prompt.py` — system-prompt building
`build_system_prompt_from_working_dir(working_dir, enabled_files=None, agent_id=None, heartbeat_enabled=False, language="zh", memory_manager=None)` loads ordered markdown files (default `AGENTS.md`, `SOUL.md`, `PROFILE.md`) via `PromptBuilder`, stripping YAML frontmatter and processing `<!-- heartbeat:* -->` / `<!-- memory:* -->` sections, then prepends an agent-identity header. Also exposes `build_bootstrap_guidance(language)`, multimodal helpers `get_active_model_supports_multimodal()`, `get_active_model_multimodal_raw()`, `build_multimodal_hint()`/`format_multimodal_hint()`, and `_get_active_model_info()` (resolves the active `ModelInfo` via `ProviderManager` + agent config). Note: this `PromptBuilder` is **distinct** from the one in `prompt_builder.py`.

### `prompt_builder.py` — `class PromptBuilder`
Assembles the final system prompt from host anchors (`HOST_ANCHORS = ("workspace", "multimodal", "env_context")`) plus plugin-registered `PromptSection`s inserted after their declared anchor, filtered by `agent_id`. Takes a `PluginRegistry`. Security note in-code: plugin text is concatenated verbatim — only trusted plugins reach this path.

### `templates.py` — builtin agent templates
`build_agent_template(template_id, *, agent_id, workspace_dir, fallback_language, ...) -> AgentTemplateBuildResult`. Supported templates: `DEFAULT_AGENT_TEMPLATE="default"`, `LOCAL_AGENT_TEMPLATE="local"`, `QA_AGENT_TEMPLATE="qa"`. Produces an `AgentProfileConfig` plus `initial_skill_names` and a workspace-markdown template id.

### `schema.py` — `FileBlock` (TypedDict)
Tool-response file block: `type: "file"`, `source: Base64Source | URLSource` (from `agentscope.message`), optional `filename`.

### `context/` subpackage — active-window management
- `__init__.py` exports `AgentContext`, `AsMsgHandler`, `AsBlockStat`, `AsMsgStat`, `BaseContextManager`, `LightContextManager`.
- `base_context_manager.py` — `class BaseContextManager(ABC)` defines the interface: `start()`, `close()`, lifecycle hooks `pre_reply`/`pre_reasoning`/`post_acting`/`post_reply`, `get_agent_context()`, `compact_context(messages, previous_summary, extra_instruction) -> dict`. Includes a `context_registry: Registry[BaseContextManager]` and `get_context_manager_backend(backend)` factory (falls back to first registered backend).
- `light_context_manager.py` — `@context_registry.register("light") class LightContextManager(BaseContextManager)`, the default backend; implements compaction + tool-result pruning over the lifecycle hooks (largest file in the subpackage).
- `agent_context.py` — `class AgentContext(InMemoryMemory)`: token-aware memory with optional JSONL dialog persistence (`{dialog_path}/{YYYY-mm-dd}.jsonl`); attached to the agent as `self.memory`.
- `as_msg_handler.py` (`AsMsgHandler`), `as_msg_stat.py` (`AsMsgStat`, `AsBlockStat`) — token accounting / per-message breakdown used by `/history`.
- `compactor_prompts.py` (e.g. `SUMMARY_PROMPT_EN`), `context_helpers.py` — thin helpers over agentscope 2.0 `AgentState` (`state.context` / `state.summary`); see its module docstring for the 1.x→2.0 memory-model migration notes.

### `hooks/` subpackage
- `__init__.py` exports `BootstrapHook`.
- `bootstrap.py` — `class BootstrapHook(working_dir, language="zh")`: on the first user interaction (`is_first_user_interaction`) and if `BOOTSTRAP.md` exists (and `.bootstrap_completed` flag does not), prepends `build_bootstrap_guidance(language)` to the first user message, then touches the completion flag. Conforms to agentscope's pre_reasoning hook signature `async __call__(agent, kwargs)`.

## Entry Points & Public API

- `from qwenpaw.agents import QwenPawAgent, create_model_and_formatter` — the package `__init__.py` lazily exposes exactly these two (`__getattr__` defers the heavy `react_agent` import so `agents.skill_system` can be imported cheaply from the CLI).
- The application wires the agent in `src/qwenpaw/app/runner/runner.py` (`QwenPawAgent(...)` then `await agent.register_mcp_clients()`).
- `context.BaseContextManager` / `LightContextManager` / `get_context_manager_backend` are the public context-manager API consumed by the runner and command handler.
- `templates.build_agent_template` / `list_supported_agent_templates` are used by CLI/app agent-creation flows.
- `prompt.build_system_prompt_from_working_dir` and the multimodal helpers are reused across the codebase (e.g. model_factory request-time normalization).
- Widely imported across `src/qwenpaw/providers/**`, `src/qwenpaw/app/**`, `src/qwenpaw/cli/**`, `src/qwenpaw/plugins/**`, and `src/qwenpaw/plan/hints.py`.

## AgentScope Integration

QwenPaw builds directly on agentscope 1.0.20 (with 2.0-era constructs present):
- **Agent base & ReAct loop**: `agentscope.agent.ReActAgent` (subclassed by `QwenPawAgent`); overrides `_reasoning`, `_acting`, `_summarizing`, `reply`, `print`, `_broadcast_to_subscribers`; uses `_MemoryMark` from `agentscope.agent._react_agent` and `register_instance_hook`. See [../agentscope-v2/building-blocks/agent.md](../agentscope-v2/building-blocks/agent.md) and [../agentscope-v2/api-reference/agent.md](../agentscope-v2/api-reference/agent.md).
- **Tools**: `agentscope.tool.Toolkit` (`register_tool_function`, `register_agent_skill`, `register_mcp_client`, built-in `view_task`/`wait_task`/`cancel_task`). See [../agentscope-v2/building-blocks/tool.md](../agentscope-v2/building-blocks/tool.md).
- **Models & formatters**: `agentscope.model.ChatModelBase` / `OpenAIChatModel` / `AnthropicChatModel` / `GeminiChatModel`; `agentscope.formatter.FormatterBase` / `OpenAIChatFormatter` / `AnthropicChatFormatter` / `GeminiChatFormatter`; `ChatResponse`. See [../agentscope-v2/building-blocks/model.md](../agentscope-v2/building-blocks/model.md) and [../agentscope-v2/api-reference/chat-and-model.md](../agentscope-v2/api-reference/chat-and-model.md).
- **Memory**: `agentscope.memory.InMemoryMemory` (subclassed by `AgentContext`). See [../agentscope-v2/building-blocks/context.md](../agentscope-v2/building-blocks/context.md).
- **Middleware**: `agentscope.middleware.MiddlewareBase` (`on_reasoning`, `on_reply`). See [../agentscope-v2/building-blocks/middleware.md](../agentscope-v2/building-blocks/middleware.md).
- **Messages**: `agentscope.message.Msg`, `TextBlock`, `ToolResultBlock`, `Base64Source`, `URLSource`. See [../agentscope-v2/building-blocks/message-and-event.md](../agentscope-v2/building-blocks/message-and-event.md).
- **Runtime**: `agentscope_runtime.engine.schemas.exception.ConfigurationException` (in `prompt.py`).

## Extension Points & Gotchas

- **MRO discipline**: any new `_acting`/`_reasoning`/`_build_sys_prompt` override in a mixin **must** call `super()`. Dropping the `super()` call silently disables tool-guard, plan-gate, media-strip, or coding-prompt behavior. Order is fixed: `QwenPawAgent → CodingModeMixin → ToolGuardMixin → ReActAgent`.
- **Two `PromptBuilder` classes**: `prompt.py::PromptBuilder` (markdown-file loader) vs `prompt_builder.py::PromptBuilder` (host-anchor + plugin-section assembler). They are unrelated — import the right one.
- **`reply()` vs middleware duplication**: per-request setup exists in *both* `QwenPawAgent.reply()` and `RequestSetupMiddleware.on_reply`. The middleware is the path that also covers streaming (`reply_stream`); when changing per-request ContextVars (workspace/session/shell/recent-bytes), update both or prefer the middleware to avoid the streaming path losing setup (this is exactly the bug the middleware docstring documents).
- **Plugin tools are config-gated**: tools discovered from `tools.__all__` are skipped unless present in `agent_config.tools.builtin_tools` (security). Hardcoded built-ins default to enabled.
- **Plugin prompt text is verbatim**: `prompt_builder.PromptBuilder._render` concatenates plugin-provided strings straight into the system prompt — only trusted plugins must reach it (in-code SECURITY note).
- **Media handling is layered**: proactive stripping (capability cache / multimodal flag), request-time formatter normalization (`_qwenpaw_force_strip_media`), and passive retry-on-400 all interact. `_strip_media_blocks_from_memory` mutates stored history irreversibly, whereas the formatter normalization only affects the copied request — choose deliberately.
- **Plan gate races**: `create_plan` / `revise_current_plan` pre-lock `plan_notebook._plan_awaiting_user_confirm` *before* sibling tools run (to survive `asyncio.gather`) and force one text-only pass afterward (`_plan_text_only_after_mutation`). Touch `_filter_plan_tools` / `_acting` / `_reasoning` together.
- **MCP recovery**: clients carry a `_qwenpaw_rebuild_info` dict so `_rebuild_mcp_client` can reconstruct a `StdIOStatefulClient`/`HttpStatefulClient` after a dead session; `_reuse_shared_client_reference` keeps the manager-shared reference stable. Removing that metadata breaks recovery.
- **Context manager is pluggable** via `context_registry` + `get_context_manager_backend`; new backends subclass `BaseContextManager` and `@context_registry.register("<name>")`. Unknown backends silently fall back to the first registered (`"light"`).
- **Lazy package import**: don't add eager top-level imports of `react_agent` into `agents/__init__.py` — the lazy `__getattr__` exists so the CLI can import `skill_system` without pulling agentscope/tools.
- **Unclear from code**: the codebase mixes agentscope 1.x and 2.0 idioms (e.g. `context_helpers.py` references 2.0 `AgentState`/`compress_context` while `AgentContext` still subclasses 1.x `InMemoryMemory`); the `LightContextManager` compactor is noted as "currently dormant without `memory_manager`". Treat the active context path as `AgentContext` + `LightContextManager` lifecycle hooks until verified otherwise.
