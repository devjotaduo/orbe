# security

> Package path(s): `src/qwenpaw/security/` — `__init__.py`, `secret_store.py`, `tool_guard/`, `skill_scanner/`

## Purpose

The `qwenpaw.security` package centralises three independent, defence-in-depth
mechanisms for the personal-assistant agent: **tool-call guarding** (scanning a
tool's parameters *before* the agent invokes it to detect command injection,
sensitive-file access and other dangerous patterns), **skill scanning** (static
analysis of a skill directory before it is installed/activated), and **secret
storage** (transparent at-rest encryption of API keys, tokens and JWT secrets).
The three sub-modules are deliberately decoupled so each concern can evolve or be
disabled without affecting the others, and heavy dependencies (`keyring`,
`cryptography`, `yaml`) are lazily imported to keep import-time cost near zero.

## Architecture

Three sub-systems, each with the same conceptual vocabulary (severity → threat
category → finding → result) but separate model classes so they evolve
independently:

```
tool_guard/   ToolGuardEngine ──runs──▶ [FilePathToolGuardian,
                                          RuleBasedToolGuardian,
                                          ShellEvasionGuardian]  (BaseToolGuardian)
              guard(tool, params) ──▶ ToolGuardResult(findings, max_severity, is_safe)
              consumed by runtime/tool_guard.GuardedFunctionTool +
              agents/tool_guard_mixin (deny / guard / approve flow,
              gated by ToolExecutionLevel OFF/AUTO/SMART/STRICT)

skill_scanner/ SkillScanner ──runs──▶ [PatternAnalyzer]  (BaseAnalyzer, policy-driven)
              scan_skill(dir) ──▶ ScanResult; module-level
              scan_skill_directory() adds mode (block/warn/off), whitelist,
              mtime cache, timeout, blocked-history persistence

secret_store.py  encrypt()/decrypt() via Fernet, master key from OS keyring
              (keyring lib) or SECRET_DIR/.master_key fallback (mode 0600)
```

Both `tool_guard` and `skill_scanner` follow the same pattern: an **abstract base**
(`BaseToolGuardian` / `BaseAnalyzer`), one or more concrete implementations, and an
**orchestrator** that runs all of them, swallows per-component exceptions, and
aggregates findings into a result object with `is_safe` / `max_severity`
convenience properties. Both expose a **lazy singleton** accessor
(`get_guard_engine()` / `_get_scanner()`).

## Key Modules

### `secret_store.py`
At-rest encryption layer. Uses Fernet (AES-128-CBC + HMAC-SHA256). Master key
resolution order: in-process cache → OS keyring (`keyring`, service `"qwenpaw"`,
legacy `"copaw"`) → `SECRET_DIR/.master_key` (64 hex chars, `0o600`) → generate
new. Keyring access is skipped in containers/headless-Linux/CI and wrapped in a
daemon-thread timeout (`_KEYRING_TIMEOUT = 10s`) to avoid D-Bus hangs.
Encrypted values carry an `ENC:` prefix for transparent legacy-plaintext
migration.
Public functions:
- `encrypt(plaintext: str) -> str` / `decrypt(value: str) -> str` — `decrypt` passes
  through non-`ENC:` values and returns raw ciphertext (logging a warning) on
  failure instead of raising.
- `is_encrypted(value: str) -> bool`
- `reload_master_key_from_disk() -> None` — invalidates cache + re-syncs keyring after a backup restore.
- `encrypt_dict_fields(data, secret_fields) -> dict` / `decrypt_dict_fields(...)` plus
  the field sets `PROVIDER_SECRET_FIELDS = {"api_key"}` and `AUTH_SECRET_FIELDS = {"jwt_secret"}`.

### `tool_guard/engine.py` — `ToolGuardEngine`
Orchestrator. Default guardians: `FilePathToolGuardian`, `RuleBasedToolGuardian`,
`ShellEvasionGuardian`. Enable/disable via `QWENPAW_TOOL_GUARD_ENABLED` env >
`config.security.tool_guard.enabled` > default `True`.
- `guard(tool_name, params, *, only_always_run=False) -> ToolGuardResult | None` — returns
  `None` when disabled; runs each guardian, isolating failures into
  `guardians_failed`.
- `register_guardian` / `unregister_guardian`, `reload_rules`, `is_denied`,
  `is_guarded`, `should_auto_deny_result`. Tool/rule scope is loaded from config
  via `utils.resolve_*`.
- `get_guard_engine()` — lazy singleton.

### `tool_guard/guardians/` — `BaseToolGuardian` + concrete guardians
- `BaseToolGuardian` (abstract): `guard(tool_name, params) -> list[GuardFinding]`,
  `always_run` flag (run even for tools outside the guarded scope).
- `FilePathToolGuardian` (`file_guardian.py`): blocks tool calls targeting sensitive
  files/dirs (e.g. `SECRET_DIR`, `.qwenpaw.secret`); maps tools→path params via
  `_TOOL_FILE_PARAMS`; handles Windows/UNC paths and shell redirect operators;
  `ensure_file_guard_paths()` merges compatibility secret dirs.
- `RuleBasedToolGuardian` (`rule_guardian.py`): loads YAML regex signatures from
  `tool_guard/rules/` (default `dangerous_shell_commands.yaml`), matches against the
  string form of each param; has `rm`/`Remove-Item` evasion normalisation.
- `ShellEvasionGuardian` (`shell_evasion_guardian.py`): detects obfuscation/evasion in shell commands.

### `tool_guard/models.py`
Dataclasses + enums: `GuardSeverity`, `GuardThreatCategory`, `GuardFinding`,
`ToolGuardResult` (`is_safe` = no CRITICAL/HIGH, `max_severity`,
`get_findings_by_severity/category`, `to_dict`). Module constant
`TOOL_GUARD_DENIED_MARK = "tool_guard_denied"` tags denied messages across modules.

### `tool_guard/execution_level.py` — `ToolExecutionLevel`
Str enum `STRICT` / `SMART` / `AUTO` / `OFF` controlling *when* a guarded tool needs
user approval. `from_config(value)` (defaults to `AUTO`), `requires_approval_for_all_tools()`,
`is_disabled()`, `is_smart_mode()`.

### `tool_guard/approval.py` & `i18n.py`
`ApprovalDecision` enum (`APPROVED`/`DENIED`/`TIMEOUT`), `format_findings_summary()`
markdown helper; `_TOOL_GUARD_I18N` bundles (en/zh/ru/ja) for user-facing prompts.

### `skill_scanner/__init__.py` — public scan facade
- `scan_skill_directory(skill_dir, *, skill_name, block, timeout) -> ScanResult | None` —
  the main entry. Honours mode `block`/`warn`/`off`
  (`QWENPAW_SKILL_SCAN_MODE` env > config > default `block`), whitelist
  (`is_skill_whitelisted`, optional `content_hash` match), mtime-based result cache,
  thread-pool timeout, and raises `SkillScanError` when `block` and not `is_safe`.
- Blocked-history persistence: `BlockedSkillRecord`, `get_blocked_history`,
  `clear_blocked_history`, `remove_blocked_entry`, written to
  `WORKING_DIR/skill_scanner_blocked.json`.
- `compute_skill_content_hash(skill_dir)` — SHA-256 of all file contents.

### `skill_scanner/scanner.py` — `SkillScanner`
Discovers files (`_discover_files` skips symlinks and any real path escaping the
skill dir — anti path-traversal — plus binary/archive extensions and oversized
files), runs analyzers, de-dupes findings, returns `ScanResult`. Default analyzer:
`PatternAnalyzer`. Limits/skip-extensions come from `ScanPolicy.file_limits` /
`file_classification`.

### `skill_scanner/` supporting modules
- `analyzers/__init__.py` `BaseAnalyzer.analyze(skill_dir, files, *, skill_name) -> list[Finding]`,
  carries a `ScanPolicy`.
- `analyzers/pattern_analyzer.py` `PatternAnalyzer` — YAML regex signature engine.
- `scan_policy.py` `ScanPolicy` (`.default()`, `.from_yaml(...)`) — rule scoping,
  severity overrides, allowlists, file limits/classification.
- `models.py` — `Severity`, `ThreatCategory`, `Finding`, `SkillFile`, `ScanResult`.

## Entry Points & Public API

Used by the rest of qwenpaw (17 call sites outside `security/`):
- **Tool guarding**: `runtime/tool_guard.py` `GuardedFunctionTool` (wraps each tool;
  routes through `get_guard_engine()`), `agents/tool_guard_mixin.py` (the
  deny/guard/approve flow on the agent), `agents/skill_system/store.py`,
  `app/approvals/service.py`, `app/routers/approval.py`,
  `app/runner/control_commands/approval_handler.py`.
- **Skill scanning**: `agents/tools/make_skill_tools.py`, `app/routers/skills.py`,
  `cli/skills_cmd.py`, `cli/doctor_checks.py`, `app/routers/files.py`.
- **Secret storage**: `envs/store.py` (`encrypt`/`decrypt`/`is_encrypted` for
  `envs.json`), `providers/provider_manager.py` and `app/auth.py`
  (`encrypt_dict_fields`/`decrypt_dict_fields`), `backup/_ops/restore.py`
  (`reload_master_key_from_disk`).
- **Config**: `config/config.py` exposes `security.tool_guard` and
  `security.skill_scanner` Pydantic config; `app/routers/config.py` surfaces it.

Stable symbols are re-exported from `tool_guard/__init__.py`
(`ToolGuardEngine`, `ToolGuardResult`, `GuardFinding`, `GuardSeverity`,
`GuardThreatCategory`, `TOOL_GUARD_DENIED_MARK`, the guardian classes) and
`skill_scanner/__init__.py` (`SkillScanner`, `ScanResult`, `Severity`,
`scan_skill_directory`, `SkillScanError`, the whitelist/history helpers).

## AgentScope Integration

The security package itself is **qwenpaw-native** and does not import agentscope. The
bridge lives one layer up in `runtime/tool_guard.py`: `GuardedFunctionTool`
lazily subclasses agentscope's `agentscope.tool.FunctionTool` (via `__new__`, so
importing the module never hard-requires agentscope) and translates a
`ToolGuardResult` into ALLOW / DENY / ASK behaviour. `agents/tool_guard_mixin.py`
imports `agentscope.message.Msg` to surface guard decisions to the conversation.

Conceptually this layer parallels — and runs alongside, not on top of —
agentscope v2's own permission system (deny/ask/allow verdicts, `EXPLORE`/`BYPASS`
modes, per-tool `check_permissions()`); see
[../agentscope-v2/building-blocks/permission-system.md](../agentscope-v2/building-blocks/permission-system.md).
qwenpaw's guard adds parameter-content scanning (regex/path/shell-evasion) and a
user-approval workflow that the agentscope permission system does not provide.

## Extension Points & Gotchas

- **Add a guardian/analyzer** by subclassing `BaseToolGuardian` / `BaseAnalyzer` and
  registering it (`engine.register_guardian(...)` / `scanner.register_analyzer(...)`)
  or adding it to `_default_guardians` / `_default_analyzers`. The orchestrators
  isolate per-component exceptions, so a buggy plugin degrades to "no findings"
  rather than crashing the call.
- **Prefer YAML rules over code** for new signatures: drop a file in
  `tool_guard/rules/` (rule-based) or extend the `ScanPolicy` YAML — both are
  hot-reloadable (`engine.reload_rules()`).
- **Fail-open by design** in several places: a disabled guard returns `None`; a scan
  timeout returns `None`; `decrypt` returns raw ciphertext on failure. Callers
  must treat `None`/passthrough as "not blocked" and not assume a verdict.
- **`is_safe` ignores MEDIUM and below** — it is `True` unless a CRITICAL/HIGH finding
  exists. Approval gating for MEDIUM is the job of `ToolExecutionLevel` (SMART
  asks on MEDIUM+), not `is_safe`.
- **Master-key fragility**: changing/losing `SECRET_DIR/.master_key` (or a keyring
  swap) silently makes all `ENC:` values undecryptable — `decrypt` returns the raw
  ciphertext. After a backup restore you **must** call `reload_master_key_from_disk()`
  to re-sync the running process and keyring.
- **Legacy compatibility**: many paths carry dual `.qwenpaw`/`.copaw` (and
  `qwenpaw`/`copaw` keyring) names. When adding new on-disk locations, follow the
  existing `ensure_file_guard_paths` / legacy-fallback pattern.
- **Path-traversal safety** in `SkillScanner._discover_files` (symlink skip +
  `is_relative_to` boundary check) is load-bearing — do not loosen it when adding
  file-discovery features.
- **Config precedence** is consistently env var > `config.json` > built-in default
  across all three sub-systems (`QWENPAW_TOOL_GUARD_*`, `QWENPAW_SKILL_SCAN_MODE`,
  `QWENPAW_RUNNING_IN_CONTAINER`); honour it in new options.
