# agents (memory, mission, skills, acp)

> Package path(s): `src/qwenpaw/agents/memory/` (+ `memory/proactive/`), `src/qwenpaw/agents/mission/`, `src/qwenpaw/agents/skill_system/`, `src/qwenpaw/agents/skills/` (content, not code), `src/qwenpaw/agents/acp/`, `src/qwenpaw/agents/utils/`, `src/qwenpaw/agents/md_files/` (content, not code)

## Purpose

This area bundles several semi-independent subsystems that hang off the qwenpaw ReAct agent: **memory** (pluggable long-term memory backends + a Markdown file manager + a "proactive" idle-trigger feature), **mission** (an autonomous PRD-driven iterative execution mode adapted from snarktank/ralph), the **skill system** (a three-tier model of built-in / pool / workspace "skills" backed by `SKILL.md` directories, plus a remote hub installer), **ACP** (Agent Client Protocol server + hosted client letting qwenpaw act as, and delegate to, ACP agents), shared **agent utilities** (tokenization, file/media handling, message sanitization, MD-file setup), and the static **skills/** and **md_files/** content packages that the code copies into workspaces.

## Architecture

Each subsystem connects to the agent runner independently:

- **memory/** uses a registry+factory pattern. `BaseMemoryManager` (ABC) defines the contract; concrete backends register themselves via the `@memory_registry.register(...)` decorator (`"adbpg"` → `ADBPGMemoryManager`, `"remelight"` → `ReMeLightMemoryManager`). `get_memory_manager_backend(name)` resolves a class by name with fallback to the first registered backend. `AgentMdManager` is a separate, non-registry helper for reading/writing `.md` files in the working and memory dirs. `proactive/` is a lazily-imported submodule (re-exported via `__getattr__` in `memory/__init__.py` to break a `proactive → react_agent → agents.memory` circular-import loop).
- **mission/** is a thin command parser (`handler.py`) → state-file layer (`state.py`) → execution engine (`mission_runner.py`) → prompt library (`prompts.py`). A `/mission` user message is detected by `handler.is_mission_command`, sets up `missions/{loop_id}/` state files, and hands a `dict` back to the runner which delegates to `mission_runner`. Phase 1 generates `prd.json`; Phase 2 is a code-controlled loop that deactivates implementation tools and iterates until every PRD story `passes`.
- **skill_system/** layers cleanly: `store.py` (pure filesystem + manifest JSON I/O, path-safety, frontmatter) → `pool_service.py` / `workspace_service.py` (`SkillPoolService`, `SkillService` — CRUD over the shared pool vs. a per-workspace dir) → `registry.py` (built-in skill discovery, manifest reconciliation, env-override application, language preference) → `hub.py` (remote install client for GitHub/clawhub/lobehub/modelscope/etc.). `models.py` holds shared dataclasses/pydantic models.
- **acp/** has `core.py` (shared exceptions + `SuspendedPermission`), `server.py` (`QwenPawACPAgent` exposing qwenpaw over ACP), `client.py` + `service.py` + `tool_adapter.py` + `permissions.py` (the *hosted-client* side that lets qwenpaw delegate to an external ACP agent and surface its permission prompts).
- **utils/** is a flat grab-bag of stateless helpers consumed across the agent package.

## Key Modules

### `memory/base_memory_manager.py`
Defines `BaseMemoryManager(ABC)` — the backend contract. Abstract: `start()`, `close() -> bool`, `get_memory_prompt(language="zh") -> str`, `list_memory_tools() -> list[Callable[..., ToolResponse]]`. Optional overridable hooks (base returns empty/None/no-op): `summarize(messages, **kwargs)`, `retrieve(...)`, `dream(*, runner, channel_manager, agent_id, workspace_dir, ...)`, `auto_memory_search(...)`, `summarize_when_compact(...)`, `auto_memory(...)`. Also implements a built-in serial background summarize queue (`add_summarize_task`, `_summarize_worker`, `list_summarize_status`). Module-level `memory_registry: Registry[BaseMemoryManager]` and `get_memory_manager_backend(backend) -> type[BaseMemoryManager]` are the factory entry points.

### `memory/agent_md_manager.py`
`AgentMdManager(working_dir, agent_id=None)` — reads/writes `.md` files in the working dir and a configurable `memory_dir` (from `agent_config.running.daily_memory_dir`, default `"memory"`). Public: `list_working_mds()`, `read_working_md(name)`, `write_working_md(name, content)`, and `*_memory_md` equivalents. Notable for its hardened path-safety helpers `_sanitize_md_name` (rejects `..` and path separators) and `_assert_within_dir` (resolves symlinks before a `relative_to` containment check).

### `memory/adbpg_memory_manager.py` / `memory/reme_light_memory_manager.py`
The two concrete backends. `ADBPGMemoryManager` (registered `"adbpg"`, uses `adbpg_client.py` + `adbpg_prompts.py`) is an AnalyticDB-for-PostgreSQL vector backend. `ReMeLightMemoryManager` (registered `"remelight"`) wraps the ReMe library (pinned `_EXPECTED_REME_VERSION = "0.3.1.10"`) and notably implements `dream()` by spawning a `ReActAgent` with file tools to consolidate memory. Both implement `get_memory_prompt` and `list_memory_tools`.

### `memory/proactive/`
Idle-driven proactive messaging. `proactive_types.py` defines `ProactiveConfig`, `ProactiveTask`, `ProactiveQueryResult` (dataclasses). `proactive_trigger.py` is the loop: `enable_proactive_for_session(...)`, `proactive_trigger_loop(...)`, plus module-level state dicts `proactive_tasks` / `proactive_configs`. `proactive_responder.generate_proactive_response(...)` produces the message; `proactive_utils.extract_content(...)` is a helper.

### `mission/handler.py`
Thin parser. `is_mission_command(query)`, `MISSION_COMMANDS = {"/mission"}`, `MISSION_COMMAND_DESCRIPTIONS` (advertised to ACP clients), `_parse_mission_args` (handles `--max-iterations`, default 20, clamped 1–100). Returns a `str` for info sub-commands (status/list/help) or a `dict` (`mission_phase`, `loop_dir`, `max_iterations`) to start a mission.

### `mission/state.py`
State-file management under `{workspace_dir}/missions/{loop_id}/` (`loop_config.json`, `prd.json`, `progress.txt`, `task.md`). Each loop dir IS the isolated working dir. Includes async git probing `detect_git_context(workspace_dir) -> dict` and the create/read/write helpers (`create_loop_dir`, `read_prd`, `read_loop_config`, `write_loop_config`, `get_active_loop_dir`, `list_loop_dirs`, `init_progress_txt`, `write_task_md`).

### `mission/mission_runner.py`
The execution engine — the only place that knows about mission phases. Phase 1: agent writes `prd.json` with all tools available. Phase 2: a code-controlled loop that deactivates implementation tools (via the agentscope Toolkit group mechanism) and re-runs the agent until all stories pass or `max_iterations` is hit. Localized status strings live in `_MESSAGES` (zh/en). `mission/prompts.py` is the (large, ralph-derived) prompt library; `build_master_prompt` is its public entry.

### `skill_system/models.py`
Shared types: `SkillInfo` (pydantic; `name` is the stable runtime identity, deliberately NOT derived from frontmatter), `SkillRequirements`, `BuiltinSkillVariant`/`BuiltinSkillIdentity` (frozen dataclasses), `SkillConflictError`, and `ALL_SKILL_ROUTING_CHANNELS`.

### `skill_system/store.py`
Pure filesystem/manifest layer (~50 functions). Path resolution (`get_skill_pool_dir`, `get_skill_pool_dirs`, `get_workspace_skills_dir`, `resolve_pool_skill_dir`), atomic JSON with file locks (`write_json_atomic`, `mutate_json`, `read_json`), frontmatter parsing (`read_frontmatter_safe_from_path`, `extract_version`), manifest readers (`read_skill_manifest`, `read_skill_pool_manifest`), conflict naming (`suggest_conflict_name`), zip-import safety (`_extract_and_validate_zip`, `_safe_child_path`, `safe_skill_dir`), and `read_skill_from_dir(skill_dir, source) -> SkillInfo | None`.

### `skill_system/pool_service.py` & `workspace_service.py`
`SkillPoolService` (CRUD over the shared global pool: `list_all_skills`, `create_skill`, `import_from_zip`, `delete_skill`, `save_pool_skill`, `upload_from_workspace`, `download_to_workspace`, `preflight_download_to_workspace`). `SkillService(workspace_dir)` (per-workspace: `list_all_skills`, `list_available_skills`, `create_skill`, `save_skill`, `enable_skill`/`disable_skill`, `set_skill_channels`, `set_skill_tags`, `delete_skill`, `load_skill_file`).

### `skill_system/registry.py`
Top-level orchestration. Built-in discovery/import (`list_builtin_import_candidates`, `import_builtin_skills`, `get_builtin_skills_dir`, `get_packaged_builtin_versions`), language preference (`get/set_builtin_skill_language_preference`), env overrides (`apply_skill_config_env_overrides`), and reconciliation/init entry points (`ensure_skill_pool_initialized`, `ensure_skills_initialized`, `reconcile_pool_manifest`, `reconcile_workspace_manifest`, `resolve_effective_skills`).

### `skill_system/hub.py`
Remote skill installer (~2150 lines). `InstallOrigin` literal enumerates sources (`skills-sh`, `github`, `lobehub`, `modelscope`, `aliyun`, `skillsmp`, `clawhub`, `url`, `zip`). Async httpx client with retry/backoff, per-source URL/spec parsers, GitHub response caching, bundle normalization, and download-size guards. `HubSkillResult` / `HubInstallResult` dataclasses; `aclose_hub_client()` for shutdown.

### `acp/server.py`
`QwenPawACPAgent(Agent)` — exposes a qwenpaw agent over the Agent Client Protocol. Implements the ACP surface: `initialize`, `new_session`, `load_session`, `prompt`, `close_session`, `list_sessions`, `resume_session`, `set_session_model`, `set_config_option`, `cancel`. Internal `_StreamTracker` + `_msg_to_updates` translate agentscope `Msg` streams into ACP `session_update`s. Advertises slash commands (including `/mission`) via `_build_available_commands`. `run_qwenpaw_agent(...)` is the module-level launcher.

### `acp/service.py`, `client.py`, `permissions.py`, `tool_adapter.py`, `core.py`
The hosted-client side (qwenpaw *consuming* an external ACP agent). `ACPService` (`run_turn`, `resume_permission`, `cancel_turn`, session lifecycle) is a process-managed turn runner; module-level `get_acp_service`/`init_acp_service`/`close_acp_service` manage per-agent singletons. `ACPHostedClient` implements the ACP client callbacks (`request_permission`, `session_update`) and accumulates assistant/tool events. `ACPPermissionAdapter` builds `SuspendedPermission` payloads and detects hard-blocked tool calls. `tool_adapter.py` renders ACP stream events into `ToolResponse`/`TextBlock`. `core.py` holds the exception hierarchy (`ACPErrors` → `ACPConfigurationError`/`ACPTransportError`/`ACPProtocolError`/`ACPSessionError`) and the `SuspendedPermission` dataclass.

### `utils/`
Stateless helpers re-exported from `utils/__init__.py`: `Registry` (the generic register/get container used by `memory_registry`), token counting (`get_token_counter`, `EstimatedTokenCounter`), file/media (`download_file_from_url`, `download_file_from_base64`, `process_file_and_media_blocks_in_message`, `read_text_file_with_encoding_fallback`), message hygiene (`normalize_messages_for_model_request`, `_sanitize_tool_messages`, `check_valid_messages`, `extract_tool_ids` and other `_*_tool_blocks` repair helpers), audio transcription (`transcribe_audio`, `list_transcription_providers`), and MD-file setup (`copy_md_files`, `copy_template_md_files`, `copy_workspace_md_files`, `copy_builtin_qa_md_files`, `normalize_agent_language`).

### `md_files/` and `skills/` (content, not code)
`md_files/{en,zh,id,ru,local,qa}/` ships the agent persona/config templates (`AGENTS.md`, `BOOTSTRAP.md`, `PROFILE.md`, `SOUL.md`, `MEMORY.md`, `HEARTBEAT.md`) that `utils/setup_utils.copy_md_files` copies into a workspace by language (with `en` fallback). `skills/<name>-{en,zh}/SKILL.md` are the packaged built-in skills (e.g. `make_plan`, `make-skill`, `docx`, `pdf`, `pptx`, `xlsx`, `browser_cdp`, `news`, `cron`, `multi_agent_collaboration`) that `skill_system/registry.py` discovers and imports; each is a frontmatter-headed Markdown doc, sometimes with bundled `scripts/` and `references/`.

## Entry Points & Public API

- **memory:** `from qwenpaw.agents.memory import BaseMemoryManager, AgentMdManager, ADBPGMemoryManager, ReMeLightMemoryManager` plus the lazily-exported proactive symbols. The factory `get_memory_manager_backend` and `memory_registry` live in `base_memory_manager.py`. Consumed by `react_agent.py`, `command_handler.py`, `prompt.py`, `app/runner/runner.py`, `app/workspace/workspace.py`, `app/routers/workspace.py`.
- **mission:** `handler.is_mission_command` / `MISSION_COMMAND_DESCRIPTIONS` and `mission_runner` (Phase-1/Phase-2 generators). Consumed by `app/runner/runner.py`, `app/runner/mission_dispatch.py`, and advertised by `agents/acp/server.py`.
- **skill_system:** the broad surface re-exported from `skill_system/__init__.py` — `SkillInfo`, `SkillConflictError`, `SkillPoolService`, `SkillService`, plus the `ensure_*`, `reconcile_*`, `resolve_effective_skills`, `apply_skill_config_env_overrides`, and `store` path/manifest helpers. Consumed by `react_agent.py`, `middlewares.py`, `tools/make_skill_tools.py`, `app/routers/{skills,agents,settings}.py`, `app/runner/control_commands/skills_handler.py`, `app/migration.py`.
- **acp:** `from qwenpaw.agents.acp import QwenPawACPAgent, run_qwenpaw_agent, ACPService, get_acp_service, init_acp_service, close_acp_service, SuspendedPermission, ACPErrors`. Consumed by `cli/acp_cmd.py`, `tools/delegate_external_agent.py`, `app/routers/config.py`.
- **utils:** flat helper imports used pervasively across the agents package (see `utils/__init__.py` `__all__`).

## AgentScope Integration

This area is built on agentscope 1.x and agentscope-runtime primitives — see the v2 KB for the API shapes (note: the docs there describe the v2 surface; qwenpaw currently pins 1.0.20):

- **Messages & blocks** — `agentscope.message.Msg`, `TextBlock`, `ToolUseBlock`, `ToolResultBlock` are the lingua franca across memory summarization, mission streaming, and ACP translation. See [../agentscope-v2/building-blocks/message-and-event.md](../agentscope-v2/building-blocks/message-and-event.md).
- **Tools** — `agentscope.tool.Toolkit` and `ToolResponse`: memory backends return `list[Callable[..., ToolResponse]]` from `list_memory_tools`; mission Phase 2 toggles tool availability via the Toolkit group mechanism; ACP `tool_adapter` emits `ToolResponse`. See [../agentscope-v2/building-blocks/tool.md](../agentscope-v2/building-blocks/tool.md).
- **Agents** — `agentscope.agent.ReActAgent` is instantiated inside `ReMeLightMemoryManager.dream()` and is the core driven by mission/ACP. `acp/server.py`'s `QwenPawACPAgent` subclasses the ACP-runtime `Agent`. See [../agentscope-v2/building-blocks/agent.md](../agentscope-v2/building-blocks/agent.md).
- **Pipelines** — `agentscope.pipeline.stream_printing_messages` is used by `mission_runner.py` to surface streamed turns.
- **Runtime** — `hub.py` imports `agentscope_runtime.engine.schemas.exception.ConfigurationException`.
- **Permissions** — ACP's permission flow conceptually parallels the agentscope permission system; see [../agentscope-v2/building-blocks/permission-system.md](../agentscope-v2/building-blocks/permission-system.md).

## Extension Points & Gotchas

- **Adding a memory backend:** subclass `BaseMemoryManager`, decorate with `@memory_registry.register("yourname")`, and ensure the module is imported (registration is import-time — `memory/__init__.py` imports the two existing backends precisely so they self-register). Implement the four abstract methods; override the optional hooks only as needed. `get_memory_manager_backend` silently falls back to the *first registered* backend on an unknown name — a misspelling will not raise.
- **Proactive circular import:** never import `memory.proactive` eagerly at module top-level of anything in the `memory` import chain. It is intentionally lazy via `memory/__init__.__getattr__`; breaking that re-introduces the `proactive → react_agent → agents.memory` loop.
- **Skill identity is the directory/manifest key, NOT frontmatter** (`SkillInfo.name`). Frontmatter `name` can drift; the on-disk identity must stay stable, so code keys sync state and channel routing off the directory name. Always go through `store.py`'s path helpers (`safe_skill_dir`, `_safe_child_path`, `normalize_skill_dir_name`) — they enforce traversal/zip-slip safety. Manifest writes must use `write_json_atomic`/`mutate_json` (file-locked) to avoid corrupting the shared pool manifest under concurrency.
- **Three skill tiers:** built-in (packaged, language-variant), pool (shared global `SkillPoolService`), workspace (`SkillService(workspace_dir)`). `registry.reconcile_*_manifest` and `resolve_effective_skills` mediate between them — run `ensure_skill_pool_initialized` / `ensure_skills_initialized` before relying on a workspace's skill set.
- **Mission Phase 2 disables implementation tools by design.** The master agent physically cannot run `npm`/`pip`/etc. during the loop; the loop is code-controlled and reads `passes` flags from `prd.json`. Each `missions/{loop_id}/` dir is the isolated CWD — do not assume the shared workspace dir. Mission prompts are MIT-licensed adaptations of snarktank/ralph; preserve the license notices in `prompts.py` / `__init__.py`.
- **ACP has two distinct sides** that are easy to confuse: `server.py` (qwenpaw *is* the ACP agent) vs. `service.py`+`client.py` (qwenpaw *delegates to* an external ACP agent, spawning a subprocess managed by `ACPService`). `init_acp_service`/`get_acp_service`/`close_acp_service` are per-agent singletons — leaking them leaves child processes alive (`_kill_process_tree`, `_shutdown_acp_services` handle teardown).
- **`md_files/` language fallback:** `copy_md_files` falls back to `en` when a language dir is missing; `_TEMPLATE_OVERRIDE_FILENAMES` (`AGENTS/BOOTSTRAP/PROFILE/SOUL.md`) get special template-override handling. `skills/` and `md_files/` are static content packaged with the wheel — they are not Python modules and are loaded relative to `__file__`, so they must remain inside the package on install.
- **utils tool-message helpers** prefixed with `_` (`_sanitize_tool_messages`, `_dedup_tool_blocks`, `_repair_empty_tool_inputs`, `_remove_invalid_tool_blocks`) are exported in `__all__` despite the underscore — they are effectively public to the agent runner and exist to keep model requests valid (orphaned/duplicate tool blocks break provider APIs). Treat changes here as load-bearing for request validity.
