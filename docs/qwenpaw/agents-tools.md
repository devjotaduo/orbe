# agents/tools

> Package path(s): `src/qwenpaw/agents/tools/` (entry: `__init__.py`); registration consumers `src/qwenpaw/agents/react_agent.py`, `src/qwenpaw/agents/coding_mode_mixin.py`.

## Purpose
This package defines every callable tool the QwenPaw ReAct agent can invoke: file IO, content/file search, shell execution, headless/headed browser automation, desktop & media viewing, time, token-usage introspection, inter-agent messaging (chat/spawn/delegate), AST and LSP code navigation, skill materialization, and batched tool execution. Each tool is a plain async (or sync) function that returns an agentscope `ToolResponse`; the functions are registered onto an agentscope `Toolkit` at agent construction time. The package does NOT subclass any agentscope `ToolBase`/`StateToolBase` — QwenPaw uses the *function-registration* path of agentscope's toolkit (`Toolkit.register_tool_function`), where each function's signature + docstring is auto-converted into the tool's JSON schema.

## Architecture
Tools are ordinary Python coroutines. Three registration paths feed them into a per-agent `Toolkit`:

```
agent_config.tools.builtin_tools (enable/disable + async_execution flags)
            │
react_agent._create_toolkit()
   ├─ hardcoded tool_functions map (file/search/shell/browser/agent-mgmt/run_tool_batch ...)
   ├─ plugin tools discovered from tools.__init__.__all__ (gated: must be in config)
   ├─ materialize_skill  ── only when "make-skill" skill is enabled
   └─ toolkit.register_tool_function(fn, namesake_strategy=..., async_execution=...)
            │
coding_mode_mixin._register_coding_mode_tools()  (only in Coding Mode)
   ├─ make_lsp_tool(detected_langs)  ── only if an LSP server is reachable
   └─ ast_tool.ast_search            ── only if the ast-grep CLI is on PATH
```

Cross-cutting concerns:
- **Path resolution**: `file_io._resolve_file_path` resolves relative paths against the context workspace dir (`config.context.get_current_workspace_dir()`) falling back to `constant.WORKING_DIR`. `file_search` and others reuse it.
- **Output truncation**: `utils.truncate_text_output` / `read_file_safe` keep large file/shell output within a byte budget and emit a `TRUNCATION_NOTICE_MARKER` continuation hint that `read_file` understands for paging.
- **Context plumbing**: `config.context` exposes ContextVars (`current_toolkit`, workspace dir, recent-max-bytes, shell timeout) so tools behave per-agent without threading state through arguments.
- **Re-entrancy**: `run_tool_batch` and `ast/lsp` call other tools through `get_current_toolkit().call_tool_function(...)`, preserving ToolGuard interception, preset kwargs, postprocess hooks, and group-activity checks.

## Key Modules

### `__init__.py`
Re-exports the public tool set and defines `__all__` (the list react_agent and plugins treat as discoverable). Also imports `materialize_skill` and `run_tool_batch` (the former kept OUT of `__all__` so it is gated by react_agent on the `make-skill` skill). Re-exports three agentscope-native tools directly: `execute_python_code`, `view_text_file`, `write_text_file` (from `agentscope.tool`).

### `utils.py`
Shared helpers. `truncate_text_output(text, start_line, total_lines, max_bytes, file_path, encoding)` — byte-bounded truncation with line integrity, dispatching to `_truncate_fresh` / `_retruncate` around `TRUNCATION_NOTICE_MARKER`. `read_file_safe(file_path, max_bytes)` — async read with `utf-8-sig` BOM stripping and a fallback `errors="ignore"` pass. Constants: `DEFAULT_MAX_BYTES` (50 KB), `MAX_FILE_READ_BYTES` (200 MB).

### `file_io.py`
File tools, all returning `ToolResponse`:
- `read_file(file_path, start_line=None, end_line=None)` — read full file or a 1-based line range; applies smart truncation + continuation hint.
- `write_file(file_path, content)` — create/overwrite; encoding chosen by `_get_encoding_for_file` (BOM for csv/tsv/txt/log).
- `edit_file(file_path, old_text, new_text)` — find-and-replace ALL occurrences (errors if `old_text` absent).
- `append_file(file_path, content)`.
Internal `_resolve_file_path` is the canonical relative→absolute resolver reused across the package.

### `file_search.py`
- `grep_search(pattern, path=None, is_regex=False, case_sensitive=True, context_lines=0, include_pattern=None, ...)` — content search; skips a `_BINARY_EXTENSIONS` set.
- `glob_search(pattern, path=None)` — file discovery by glob (`"*.py"`, `"**/*.json"`). Both resolve paths from the workspace.

### `shell.py`
`execute_shell_command(command, timeout=60.0, cwd=None)` — runs each command in a fresh subprocess (no persisted cd/env). Heavy Windows handling: `_kill_process_tree_win32`, `_windows_shell_creationflags`, PowerShell/cmd detection (`_is_powershell`, `_is_cmd`, `_extract_powershell_command`), newline collapsing/sanitizing, and `smart_decode` for output. Honors a context-configured default timeout (`get_current_shell_command_timeout`). Marked `async_capable` (`async_execution`) in react_agent.

### `browser_control.py` (largest module, ~170 KB)
`browser_use(action, ...)` — a single mega-tool dispatching on `action` over a Playwright-managed (Chromium default, WebKit fallback) browser with per-workspace state, an idle watchdog, and `atexit` cleanup. Actions include: `start`/`stop`/`open`/`close`, `navigate`/`navigate_back`, `screenshot`, `snapshot`, `click`/`hover`/`type`/`press_key`/`drag`/`select_option`, `eval`/`evaluate`/`run_code`, `fill_form`, `file_upload`/`file_download`, `console_messages`, `network_requests`, `handle_dialog`, `tabs`, `wait_for`, `pdf`, `cookies_get`/`cookies_set`/`cookies_clear`, `clear_browser_cache`, `connect_cdp`/`list_cdp_targets`, `install`, and `batch` (a JSON array of sub-actions: navigate/click/type/press_key/evaluate/snapshot/screenshot/wait_for/hover/select_option/drag/resize). Has very many optional keyword args (selector/ref/element addressing, `headed`, `cdp_url`/`cdp_port`, `private_mode`, `executable_path`, etc.).

### `browser_snapshot.py`
Helper (not a registered tool). `build_role_snapshot_from_aria(...)` converts an ARIA tree into a compact role-based accessibility snapshot consumed by `browser_use`'s `snapshot` action; includes tree-compaction helpers.

### `desktop_screenshot.py`
`desktop_screenshot(...)` — captures the host desktop via `mss` (cross-platform) or `screencapture` (macOS), saving to the workspace and returning a `ToolResponse`.

### `view_media.py`
`view_image(image_path)` and `view_video(video_path)` — load local/remote media into the conversation. Includes multimodal-support probing (`_check_multimodal_support`, `_probe_multimodal_if_needed`) and text fallback hints when the model lacks vision. URL and path validation via `_validate_url_extension` / `_validate_media_path`.

### `send_file.py`
`send_file_to_user(...)` — surfaces a workspace file to the end user (builds a `file://` URL, auto-detects MIME type) as a tool result.

### `get_current_time.py`
`get_current_time()` and `set_user_timezone(timezone_name)` — timezone-aware clock for the agent.

### `get_token_usage.py`
`get_token_usage(...)` — returns a formatted summary of the current session's token usage.

### `agent_management.py`
Inter-agent tools against the QwenPaw agent service:
- `list_agents(base_url=None)` — list configured agents (id/name/description/workspace).
- `chat_with_agent(to_agent, text, session_id=None, timeout=300)` — foreground call to a *different* agent; returns final reply with a `[SESSION: ...]` header.
- `submit_to_agent(...)` — background submission, returns a task handle.
- `check_agent_task(...)` — poll a background agent task.
- `spawn_subagent(task, fork=False, background=False, timeout=600)` — ephemeral one-shot subagent in the *current* workspace; `fork=True` inherits session state and (if a git repo) runs in an isolated worktree/branch (`[FORK_BRANCH: ...]`). Rich helper layer for SSE streaming, request building, and id/session normalization.

### `delegate_external_agent.py`
`delegate_external_agent(action, runner="", message="", cwd="", max_runtime=300)` — drives an external **ACP** (Agent Client Protocol) runner (`qwen_code`, `opencode`, `claude_code`, `codex`, ...). Actions: `list`, `status`, `start`, `message`, `respond` (answer a pending permission request with an exact option id), `close`. Can return a streaming `AsyncGenerator[ToolResponse, ...]`. Maintains per-runner `_RunnerState` and integrates with the ACP service (`_get_acp_service`). Marked `async_capable` in react_agent.

### `ast_tool.py` (Coding Mode only)
`ast_search(pattern, ..., path=...)` — read-only structural code search via the external **ast-grep** CLI (`_ast_grep_binary`, `is_ast_grep_available`). Registered with `async_execution=True` only when the CLI is present.

### `lsp_tool.py` (Coding Mode only)
`make_lsp_tool(available_languages)` is a **factory** that returns a freshly-built coroutine whose docstring (and thus tool schema) is generated from the detected languages (`_build_description`). The returned coroutine bridges to language servers via `_lsp_client.py` / `_lsp_servers.py`. Registered with `async_execution=True` only when a server is reachable.

### `make_skill_tools.py`
`materialize_skill(name, description, body, extra_files=None)` — persists a confirmed skill: runs format validation + the security scanner, writes `SKILL.md` and the manifest entry, and enables the skill. Gated on the `make-skill` skill being enabled. Helpers analyze `run_tool_batch` JSON refs bundled in `extra_files`.

### `run_tool_batch.py`
`run_tool_batch(actions=None, file_path="", args=None, stop_on_error=True, last_only=False)` — executes a sequence of tool calls (inline list or loaded from a JSON file). Supports `${args.<name>}` and `${steps.<index>.<path>}` placeholder substitution. Internally each step calls `get_current_toolkit().call_tool_function(...)` (via `_call_tool`) so ToolGuard, preset kwargs, postprocess hooks and group checks all apply. Returns a JSON summary `TextBlock` followed by every step's content blocks.

## Entry Points & Public API
The canonical public surface is `tools.__init__.__all__`:
`execute_python_code`, `execute_shell_command`, `view_text_file`, `write_text_file`, `read_file`, `write_file`, `edit_file`, `append_file`, `grep_search`, `glob_search`, `send_file_to_user`, `desktop_screenshot`, `view_image`, `view_video`, `browser_use`, `get_current_time`, `set_user_timezone`, `get_token_usage`, `delegate_external_agent`, `list_agents`, `chat_with_agent`, `submit_to_agent`, `check_agent_task`, `spawn_subagent`, `run_tool_batch`.

Consumers:
- `react_agent.py::_create_toolkit` — builds the hardcoded `tool_functions` map, discovers plugin tools from `__all__` (only registered if present in `agent_config.tools.builtin_tools`), and registers everything onto a `Toolkit`. Also auto-registers agentscope's background-task tools (`toolkit.view_task`, `wait_task`, `cancel_task`) when any enabled tool sets `async_execution`.
- `coding_mode_mixin.py::_register_coding_mode_tools` — adds `lsp` and `ast_search` in Coding Mode.
- `materialize_skill` / `run_tool_batch` are imported directly and registered out-of-band (the former skill-gated).
- Other subsystems reuse individual functions directly: memory managers (`reme_light_memory_manager`, proactive responder) build their own `Toolkit`s registering `read_file`/`write_file`/`edit_file`/`execute_shell_command`/`browser_use`/`desktop_screenshot`.

## AgentScope Integration
All tools target agentscope **1.0.20**'s tool subsystem via the *function-registration* path (no `ToolBase` subclassing here):
- `agentscope.tool.ToolResponse` — every tool returns one; content is a list of message blocks.
- `agentscope.message.TextBlock` (and Image/File/Video blocks for media tools) — the building blocks of `ToolResponse.content`.
- `agentscope.tool.Toolkit` — created per agent; `Toolkit.register_tool_function(fn, namesake_strategy=..., async_execution=...)` converts each function (signature + Google-style docstring) into a tool schema. `Toolkit.call_tool_function(tool_call)` is reused by `run_tool_batch` for nested calls; `Toolkit.tools` is the live registry; `Toolkit.view_task/wait_task/cancel_task` are agentscope-provided async-task tools auto-registered when `async_execution` tools exist.
- `agentscope.tool.FunctionTool` — referenced by `runtime/tool_guard.py` for interception (ToolGuard wraps registered functions).
- Three tools are agentscope built-ins re-exported as-is: `execute_python_code`, `view_text_file`, `write_text_file`.

For how agentscope's toolkit/tool machinery works in v2 terms, see [../agentscope-v2/building-blocks](../agentscope-v2/building-blocks/) and [../agentscope-v2/api-reference](../agentscope-v2/api-reference/). Note this codebase pins agentscope 1.0.20, so treat the v2 KB as conceptual reference, not an exact API match.

## Extension Points & Gotchas
- **Adding a built-in tool**: write an async fn returning `ToolResponse`, export it from `tools/__init__.py.__all__`, and add it to react_agent's `tool_functions` map (or rely on plugin discovery). Discovered-but-not-hardcoded tools are SKIPPED unless explicitly enabled in `agent_config.tools.builtin_tools` — a deliberate security gate. Hardcoded tools default to enabled.
- **Docstring IS the schema**: the function signature and Google-style docstring (`Args:` blocks) are parsed by agentscope into the JSON tool schema. Inaccurate/missing arg docs degrade tool calling. `make_lsp_tool` exploits this by generating its docstring dynamically.
- **`async_execution`**: only `execute_shell_command` and `delegate_external_agent` are declared async-capable in react_agent; setting it elsewhere has no effect unless wired into `async_capable_tool_names`. Enabling any async tool auto-adds `view_task`/`wait_task`/`cancel_task`.
- **Coding-Mode tools are conditional**: `lsp` and `ast_search` register only when an LSP server / the `ast-grep` CLI is actually reachable; registration failures are logged, never raised. Don't assume they exist.
- **Path & context coupling**: relative paths resolve against the *context* workspace dir, not the process CWD. Tools that bypass `_resolve_file_path` will misbehave across agents. Likewise, nested tool execution must go through `get_current_toolkit()` (as `run_tool_batch` does) to preserve ToolGuard/hook semantics — calling tool functions directly skips guarding.
- **Truncation marker contract**: `read_file` and `utils._retruncate` depend on the exact `TRUNCATION_NOTICE_MARKER` text and the "starts at line N / covers the next M bytes" phrasing; changing that format breaks paging and the `ToolResultCompactor`.
- **`browser_use` is a monolith**: ~170 KB and dozens of optional args dispatched by string `action`. Adding capability means extending the dispatch chain and the (single) docstring; per-workspace state and the idle watchdog/atexit cleanup must be respected to avoid leaking browser processes.
- This package edits fall under the `qwenpaw/agentscope` Guardian workflow (see user memory); changes touching agentscope APIs should pass `/agentscope-guardian` review.
