# plugins

> Package path(s): `src/qwenpaw/plugins/` — `__init__.py`, `architecture.py`, `loader.py`, `registry.py`, `api.py`, `runtime.py`, `validation.py`, `download_catalog.py`

## Purpose

This package implements qwenpaw's first-party plugin system: the machinery that discovers plugin directories on disk, validates and loads their `plugin.json` manifests + Python backend modules, and lets a plugin extend the host at runtime. Plugins can register agent tools, custom LLM providers, lifecycle hooks (startup/shutdown/uninstall/workspace-created), `/`-style control commands, FastAPI HTTP routers, system-prompt sections, and workspace skill providers. The package also proxies the official remote plugin catalog so the console can offer installs/upgrades.

## Architecture

The system is built around three cooperating objects plus a manifest model:

- **`PluginManifest` / `PluginRecord`** (`architecture.py`) — the validated shape of `plugin.json` and the in-memory record of a loaded plugin.
- **`PluginLoader`** (`loader.py`) — discovers plugin dirs, installs `requirements.txt` deps, dynamically imports each backend module, and calls the plugin's `register(api)` method. Owns one `PluginRegistry`.
- **`PluginRegistry`** (`registry.py`) — a **singleton** that holds every registration (providers, hooks, control commands, HTTP routers, prompt sections, manifests). The host application drains it after load to wire capabilities into the running app.
- **`PluginApi`** (`api.py`) — the *developer-facing* facade handed to each plugin's `register()`; every `api.register_*` call delegates to the registry.

Load flow (driven by `src/qwenpaw/app/_app.py` during FastAPI lifespan):

```
PluginLoader(plugin_dirs)
  loader.registry.set_plugin_http_app(app)          # enable HTTP router mounting
  await loader.load_all_plugins(configs)
    discover_plugins()            -> [(PluginManifest, dir), ...]   (scans */plugin.json)
    for each: load_plugin(manifest, dir, config)
        _ensure_dependencies_installed()  (pip, then uv fallback)
        importlib spec_from_file_location(... submodule_search_locations=[dir])
        module.plugin.register(api)   -> api.register_provider / register_tool / ...
                                          -> registry.register_*(...)
  # host then drains the registry:
  registry.set_runtime_helpers(RuntimeHelpers(...))
  registry.get_all_providers()      -> wire into provider manager
  registry.get_control_commands()   -> wire into command dispatcher
  registry.get_startup_hooks()      -> await each (sorted by priority)
  ... on shutdown: registry.get_shutdown_hooks()
```

Unload (`loader.unload_plugin`) reverses this: runs shutdown + uninstall hooks, evicts the module (and submodules) from `sys.modules`, calls `registry.unregister_plugin`, removes the plugin's tools from `qwenpaw.agents.tools`, and optionally deletes files.

## Key Modules

### `architecture.py` — manifest & record models
- `class PluginType(str, Enum)` — canonical categories: `TOOL`, `PROVIDER`, `HOOK`, `COMMAND`, `FRONTEND`, `GENERAL`.
- `class PluginEntryPoints(BaseModel)` — `frontend: Optional[str]`, `backend: Optional[str]`.
- `class PluginManifest(BaseModel)` — validated `plugin.json`. Fields: `id`, `version` (both required, min_length 1), `name`, `description`, `author`, `entry`, `dependencies`, `min_version`, `meta: Dict`, `plugin_type`. `model_config = ConfigDict(extra="ignore")` so unknown fields are tolerated. A `@model_validator(mode="before")` `_normalise_input` handles legacy shapes: localized `{"en-US"/"zh-CN": ...}` text (via `_coerce_manifest_str`), top-level `entry_point` -> `entry.backend`, and inferring `plugin_type` from `meta` via `_infer_type_from_meta` when `type` is absent. `from_dict(data) -> PluginManifest` is the wrapper callers use.
- `@dataclass PluginRecord` — `manifest`, `source_path: Path`, `enabled: bool`, `instance: Optional[Any]`, `diagnostics: List[str]`.

### `loader.py` — `class PluginLoader`
Constructed with `plugin_dirs: List[Path]`; creates `self.registry = PluginRegistry()` and tracks `self._loaded_plugins: Dict[str, PluginRecord]`.
- `discover_plugins() -> List[Tuple[PluginManifest, Path]]` — scans each dir for subdirs containing `plugin.json`.
- `async load_plugin(manifest, source_path, config=None) -> PluginRecord` — the core loader. Installs deps, imports backend via `importlib.util.spec_from_file_location` with `submodule_search_locations=[plugin_dir]` and a unique module name `plugin_<id>` (hyphens → underscores), requires the module to export a `plugin` object exposing `register(api)` (sync or async, awaited if a coroutine). Builds a `manifest_dict`, constructs `PluginApi`, wires the registry, and registers the manifest.
- `async load_all_plugins(configs=None) -> Dict[str, PluginRecord]`.
- `async load_plugin_from_path(source_path, config=None, install_dir=None) -> PluginRecord` — runtime install: copies the dir into the plugins dir (with a **path-traversal guard** via `target_dir.is_relative_to(install_dir)`), installs deps, then loads.
- `async unload_plugin(plugin_id, delete_files=False)` — runs shutdown + uninstall hooks, purges `sys.modules`, `registry.unregister_plugin`, `_cleanup_plugin_tools`, optional file delete.
- Dependency handling: `_check_dependencies_satisfied` (via `importlib.metadata` + `packaging.requirements`), `_ensure_dependencies_installed`, `_install_requirements` (tries `python -m pip`, falls back to `uv pip install` via `_find_uv`; 300s timeout, streamed logs).
- `get_loaded_plugin(id)`, `get_all_loaded_plugins()`.

### `registry.py` — `class PluginRegistry` (singleton)
Singleton via `__new__`/`_initialized`. Stores dataclasses `ProviderRegistration`, `HookRegistration`, `ControlCommandRegistration`, `HttpRouterRegistration`, `PromptSectionRegistration`. Key methods:
- Providers: `register_provider(...)` (raises `ValueError` on duplicate id), `get_provider`, `get_all_providers`.
- Hooks (each sorted by ascending `priority`): `register_startup_hook` / `register_shutdown_hook` / `register_uninstall_hook` / `register_workspace_created_hook` and matching `get_*_hooks()`.
- HTTP: `set_plugin_http_app(app)` (must be called before any router registration), `register_http_router(plugin_id, router, *, prefix, tags=None)` — normalizes `prefix`, mounts under `/api<prefix>`, and inserts routes **before** the console SPA catch-all route (`_CONSOLE_SPA_CATCHALL_ROUTE_NAME`) so they aren't shadowed; resets `app.openapi_schema`. Rejects bare `/` and duplicate prefixes.
- Prompt sections: `register_prompt_section(...)` — validates `after` against `PromptBuilder.HOST_ANCHORS` (imported from `..agents.prompt_builder`); `get_prompt_sections`.
- Control commands: `register_control_command`, `get_control_commands`.
- Manifests: `register_plugin_manifest`, `get_plugin_manifest`, `get_all_plugin_manifests`, `get_plugin_id_for_tool(tool_name)` (handles legacy `meta.tool_name` and new `meta.tools[]`).
- Tool config (persisted in agent config): `get_tool_config(tool_name, agent_id)`, `set_tool_config(...)` — both delegate to `..config.config.load_agent_config`/`save_agent_config` against `agent_config.tools.builtin_tools`.
- `unregister_plugin(plugin_id)` — removes all in-memory registrations (HTTP routes, manifest, providers, all hook lists, control commands, prompt sections) for a plugin.

### `api.py` — `class PluginApi` (developer surface) + `get_tool_config`
Constructed `PluginApi(plugin_id, config, manifest=None)`; `set_registry(registry)` is called by the loader. Registration methods (each forwards to the registry): `register_provider`, `register_startup_hook`, `register_shutdown_hook`, `register_uninstall_hook`, `register_workspace_created_hook`, `register_http_router`, `register_control_command`, `register_prompt_section`. The `runtime` property returns the registry's `RuntimeHelpers`. Tool helpers: `get_tool_config` / `set_tool_config`.
- `register_tool(tool_name, tool_func, description="", icon="🔧", enabled=False)` — the recommended way to add an agent tool. It does **not** register immediately; it schedules a startup hook (priority 50) that injects `tool_func` into `qwenpaw.agents.tools` (and `tools.__all__`) and creates a disabled-by-default `BuiltinToolConfig` in the current agent's config.
- `register_skill_provider(skills_dir, *, enabled_by_default=True, channels=None)` — wires a startup hook, a `workspace_created` hook, and an uninstall hook to copy the plugin's skill dirs (each with `SKILL.md`) into every workspace and reconcile the workspace skill manifest (via `..agents.skill_system.store` / `...registry`), tagging entries `source="plugin:<id>"`.
- Module-level `get_tool_config(tool_name) -> Optional[Dict]` — convenience for tool code; resolves the current agent via `..app.agent_context.get_current_agent_id` then reads the registry.

### `runtime.py` — `class RuntimeHelpers`
Thin helper handed to plugins via `api.runtime`. Wraps a `provider_manager`: `get_provider(provider_id)`, `list_providers()`, plus `log_info/log_error/log_debug`.

### `validation.py` — `validate_plugin_module(plugin_id, plugin_path, backend_entry)`
Standalone validator used by the CLI (`plugin install` / `plugin validate`). Replicates the loader's import semantics (sanitized module name, registered in `sys.modules` before `exec_module`, cleaned up in `finally`) and asserts the module exports a `Plugin` class or `plugin` instance. Raises `FileNotFoundError` / `ImportError` / `AttributeError`.

### `download_catalog.py` — remote catalog proxy
`build_plugin_catalog() -> dict` and `async fetch_plugin_catalog_async()`. Fetches `PLUGIN_DOWNLOAD_CDN` (`https://download.qwenpaw.agentscope.io`) `metadata/index.json` then the plugins index, normalizes entries, and cross-references on-disk installs (`_installed_plugin_ids`) to compute `installed` / `upgrade_available`. Tolerant of CDN failure (returns empty `plugins` + `error`, never raises to the caller).

## Entry Points & Public API

Re-exported from `qwenpaw.plugins.__init__`:
`PluginLoader`, `PluginRegistry`, `PluginApi`, `PluginManifest`, `PluginRecord`, `get_tool_config`.

Consumers in the codebase:
- `src/qwenpaw/app/_app.py` — owns the lifecycle: constructs `PluginLoader`, calls `set_plugin_http_app`, `load_all_plugins`, then drains `get_all_providers` / `get_control_commands` / `get_startup_hooks` (awaited) and `get_shutdown_hooks` on teardown; installs `RuntimeHelpers`.
- `src/qwenpaw/cli/plugin_commands.py` — CLI install/validate/list using the loader + `validation.validate_plugin_module`.
- `src/qwenpaw/app/routers/plugins.py`, `frontend_plugin.py`, `tools.py`, `agent_scoped.py` — REST endpoints over the registry and catalog.
- `src/qwenpaw/agents/prompt_builder.py` — consumes `get_prompt_sections` and exposes `HOST_ANCHORS`.
- `src/qwenpaw/agents/react_agent.py`, `app/multi_agent_manager.py`, `config/config.py` — touch tool registration / `BuiltinToolConfig`.

The **plugin-author contract**: a plugin dir contains `plugin.json` and (for backend plugins) a backend module exporting a top-level `plugin` object with a `register(self, api: PluginApi)` method.

## AgentScope Integration

The plugins package contains **no direct agentscope imports** — it integrates with qwenpaw's *own* agent/tool/provider/prompt layers, which in turn sit on top of agentscope 1.0.20. The connections are indirect:
- Tools registered via `register_tool` land in `qwenpaw.agents.tools` and are surfaced to the agent's toolkit — see how that layer wires into agentscope's tool/`Toolkit` mechanism in [../agentscope-v2/overview.md](../agentscope-v2/overview.md).
- Providers registered via `register_provider` supply a `provider_class` (documented as inheriting a qwenpaw `BaseProvider`) and `meta` such as `chat_model="OpenAIChatModel"`, i.e. they ultimately back agentscope chat-model instances. See [../agentscope-v2/overview.md](../agentscope-v2/overview.md).

Do not document agentscope itself here; cross-link instead. If this package later imports `agentscope` directly, this section should be revisited.

## Extension Points & Gotchas

- **Singleton registry.** `PluginRegistry()` always returns the same instance (`__new__` + `_initialized`). Every `PluginLoader` shares it. In tests this state persists across cases unless reset — be careful about leakage. Duplicate provider ids / HTTP prefixes / prompt-section names raise `ValueError`.
- **`set_plugin_http_app` ordering.** `register_http_router` raises `RuntimeError` if the FastAPI app wasn't attached first. HTTP routes are deliberately inserted *before* the SPA catch-all route named `qwenpaw_console_spa_catchall`; if that route is renamed in `_app.py`, plugin routes will be shadowed.
- **`register_tool` is deferred.** It only schedules a startup hook (priority 50); the tool isn't live until startup hooks run, and if there's no current agent id at that point the tool only becomes available after restart. Tools default to `enabled=False` (opt-in).
- **Module isolation via `sys.modules`.** Backend modules are imported under `plugin_<sanitized_id>` with `submodule_search_locations`/`__path__` set so relative imports resolve without polluting global `sys.path`. `unload_plugin` must purge the module *and all submodules* or a reload reuses stale code. `validation.py` mirrors this exactly and cleans up in `finally`.
- **Two export conventions.** The loader requires a `plugin` instance; `validation.py` accepts either a `Plugin` class **or** a `plugin` instance. New plugins should export `plugin` to satisfy both.
- **Hook priority.** All hook lists are sorted ascending by `priority` (lower runs earlier); default 100. `register_tool` uses 50, `register_skill_provider` uses 80.
- **Dependency install side effects.** Loading a plugin can shell out to pip/uv and modify the running environment (300s timeout). This happens automatically on discovery-load, not just explicit install.
- **Path-traversal guard.** `load_plugin_from_path` rejects plugin ids that resolve outside the install dir — preserve this when refactoring install logic.
- **`prompt_builder` import at registration time.** `register_prompt_section` imports `PromptBuilder.HOST_ANCHORS` lazily; valid anchors today are `"workspace"`, `"multimodal"`, `"env_context"` (per `api.py` docs) — verify against `PromptBuilder` if extending.
- **Legacy manifest tolerance.** `PluginManifest` silently accepts old shapes (i18n text objects, `entry_point`, missing `type`). Don't tighten validation without checking real on-CDN manifests, which still use them.
