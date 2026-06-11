# backup

> Package path(s): `src/qwenpaw/backup/` — including `backup/__init__.py`, `models.py`, `orchestration.py`, `_ops/` (create, restore, storage + helpers), and `_utils/` (constants, meta, safe_swap, _mount_swap, signing/).

## Purpose
The backup area implements QwenPaw's backup/restore subsystem: it packages selected portions of the local installation (agent workspaces, the global `config.json`, the secrets directory, and the skill pool) into a single signed `.zip` archive, and restores them back transactionally. It is the engine behind the `/backups` HTTP router — it handles backup creation (with SSE progress streaming), listing/detail/delete/export/import, local HMAC signing for trust decisions, and a crash-safe, Windows-aware directory-swap restore that stops affected agents, swaps directories atomically, and restarts them.

## Architecture
The package is layered into a thin public façade over private operation and utility modules:

- **`__init__.py`** re-exports the public API (`create_stream`, `list_backups`, `get_backup`, `delete_backups`, `export_backup`, `import_backup`, `execute_restore`).
- **`models.py`** — Pydantic request/response/metadata models plus two custom exceptions.
- **`orchestration.py`** — top-level `execute_restore` flow used by the router: preflight trust check → stop agents/browsers → restore → background restart.
- **`_ops/`** — the core operations, each delegating heavy lifting to a `*_helpers` sibling:
  - `create.py` (+ `create_helpers.py`) — build the zip, stream progress.
  - `restore.py` (+ `restore_helpers.py`) — two-phase staged restore.
  - `storage.py` — list/detail/delete/export/import.
- **`_utils/`** — shared infrastructure:
  - `constants.py` — zip path prefixes, ID validation, zip-path lookup.
  - `meta.py` — backup-ID generation, system info, `meta.json` reading.
  - `safe_swap.py` — crash-safe three-phase directory swap, per-path + cross-process locking, startup recovery.
  - `_mount_swap.py` — mount-point fallback (swap children, not the mount dir) for Docker volumes / `EBUSY`/`EXDEV`.
  - `signing/` — local HMAC signing, verification, and trust resolution.

Create flow (SSE):
```
create_stream(req) → asyncio.Queue ← background thread (_create_with_progress)
  → _compress_to_tmp: load_config, add_files_to_zip (workspaces/config/secrets/skill_pool)
  → finalize meta.json → replace_meta_with_local_signature (sign) → atomic .tmp→.zip
  → yields start / agent / saving / done | error events
```

Restore flow:
```
execute_restore(backup_id, req, *fns)
  → get_backup → preflight_restore (trust + version, no writes)
  → stop affected (and, for secrets/skill_pool, all running) agents + browsers
  → restore(): async lock → process file lock → _restore_sync_locked
       Phase 1 _stage_all: extract config/secrets/skill_pool/agents into sibling .restore_tmp dirs
       Phase 2 _commit_and_finalize: atomic swaps, reload master key, rewrite agent.json, save config
  → finally: background preload (restart) of stopped agents
```

## Key Modules

### `models.py`
Pydantic models and errors.
- `BackupScope` — booleans `include_agents`, `include_global_config`, `include_secrets` (default False), `include_skill_pool`.
- `BackupMeta` — archive metadata: `id` (default `generate_backup_id`), `name`, `created_at`, `version` (`"1"`), `scope`, `agent_count`, `qwenpaw_version`, `system_info`, `signature` (`"<scheme>:<hex>"` or None), `accepted_via_trust` (None=legacy/unknown, False=local-signed, True=trusted foreign/legacy).
- `BackupDetail(BackupMeta)` — adds `workspace_stats: {agent_id: {files,size,name?}}`.
- `CreateBackupRequest` — `name`, `description`, `scope`, `agents: list[str]` (explicit IDs).
- `RestoreBackupRequest` — `include_agents`, `agent_ids`, `include_global_config`, `include_secrets`, `include_skill_pool`, `default_workspace_dir`, `mode: "full"|"custom"` (default `custom`), `preserve_local_protected_config`, `trust_mode: "legacy"|"foreign"|None`.
- `DeleteBackupsRequest` / `DeleteBackupsResponse`.
- `BackupConflictError(Exception)` — carries `existing_meta`, raised on import ID collision.
- `BackupValidationError(ValueError)` — `code`, `message`, `details`; user-actionable failures (e.g. `restore_target_busy`, signature errors).

### `orchestration.py`
- `async execute_restore(backup_id, req, *, stop_agent_fn=None, stop_browsers_fn=None, preload_agent_fn=None, list_running_agent_ids_fn=None) -> BackupMeta` — orchestrates stop → restore → restart. Runs `preflight_restore` before stopping anything so the trust prompt does not race agent restarts on Windows. Expands the stop set to all running agents when secrets/skill-pool are restored (shared dirs may hold open handles). Always reschedules background preload in `finally`, even on failure.
- `_workspace_dirs_for_agents(agent_ids)` — resolves workspace dirs from `config.agents.profiles` before config on disk may be replaced.

### `_ops/create.py` + `create_helpers.py`
- `async create_stream(req) -> AsyncGenerator[dict]` — public entry; compression runs in a worker thread, events delivered via `loop.call_soon_threadsafe` into an `asyncio.Queue`; `threading.Event` cancels on client disconnect. Writes to a `.tmp` then atomically replaces the final `.zip`.
- `add_files_to_zip(zf, meta, progress_callback, stop_event, valid_agents)` — dispatches to `add_agent_workspaces`, `add_global_config`, `add_secrets`, `add_skill_pool` by scope. Returns backed-up agent IDs (empty if cancelled). Arc-name prefixes are `data/workspaces/<aid>/…`, `data/secrets/…`, `data/skill_pool/…`, `data/config.json`.

### `_ops/restore.py` + `restore_helpers.py`
- `async restore(backup_id, req) -> BackupMeta` — guarded by module-level `_RESTORE_LOCK` (asyncio) then a process file lock.
- `preflight_restore(backup_id, req)` — validates trust + version with no writes.
- `_restore_sync_locked` — verifies signature, (re-)signs trusted archives, verifies again, plans destinations (`_plan_agent_destinations` guards against same-dir collisions and clobbering unrelated agents), probes target availability (`_assert_restore_targets_available`), then `_stage_all` (phase 1) and `_commit_and_finalize` (phase 2).
- `_stage_global_config` / `_merge_profiles_into` — `full` mode replaces config verbatim; `custom` mode keeps local `agents.profiles` and only overrides profiles for agents actually restored (`restore_aids`), preventing "ghost agents".
- Helpers: `resolve_preserve_flag`, `overlay_local_keys` (preserve local `security`/`mcp` keys), `collect_workspace_agents_from_zip`, `resolve_workspace_dst` (handles new/cross-machine agents), `rewrite_agent_workspace_dir` (atomic agent.json fix-up), `handle_master_key_conflict` (backs up old `.master_key` outside SECRET_DIR before overwrite).

### `_ops/storage.py`
- `async list_backups() -> list[BackupMeta]`, `get_backup(id) -> BackupDetail|None`, `delete_backups(ids) -> DeleteBackupsResponse`, `export_backup(id) -> (Path, name)`, `import_backup(tmp_path, *, overwrite=False, trust_mode=None) -> BackupMeta`. All wrap sync impls via `asyncio.to_thread`. Import validates zip + meta, resolves signature action, enforces ID uniqueness (raises `BackupConflictError`), and re-signs trusted archives.

### `_utils/safe_swap.py` + `_mount_swap.py`
- Three-phase swap: `extract_to_tmp` (phase 1, into `<dst>.restore_tmp`, with Zip-Slip guard), `commit_tmp` (phases 2+3: rename `dst`→`.restore_old`, `tmp`→`dst`, rmtree old), `discard_tmp` (rollback). Per-`dst` `threading.Lock` (`_lock_for`) plus cross-process `restore_process_lock` (msvcrt on Windows, fcntl on POSIX).
- `assert_directory_renamable` / `find_busy_restore_paths` — Windows reversible-rename probe to detect locked dirs before partial restore.
- `cleanup_stale_restore_artifacts` / `cleanup_startup_restore_artifacts` — recover interrupted restores at startup (called from `app/_app.py`).
- `_mount_swap.py` — `prepare_destination_for_swap` falls back to child-by-child content swap (with `.qwenpaw_restore_state` markers) when `dst` is a mount point or rename returns `EBUSY`/`EXDEV`; `recover_mount_point_swap` rolls back/commits per the state marker.

### `_utils/signing/`
- `digest.py` — `SCHEME = "hmac-sha256-v1"`, `compute_signature(zf, meta)` / `verify_signature` over canonical `_SIGNED_FIELDS` (signature field excluded) plus a framed transcript of all non-meta zip entries; `signature_error` maps to stable `BackupValidationError` codes.
- `key.py` — `get_signing_key()` reads/creates `BACKUP_DIR/.signing_key` (32 bytes, `O_EXCL`+`O_NOFOLLOW`, 0o600), mtime-cached, refuses symlinks.
- `trust.py` — `resolve_signature_action(...) -> "none"|"sign_trusted"` (the trust boundary) and `sign_trusted_backup(...)`.
- `resign.py` — `replace_meta_with_local_signature(...)` streams a zip rewrite swapping in a locally signed `meta.json`.

## Entry Points & Public API
Exported from `qwenpaw.backup.__init__`:
- `create_stream(req)` — SSE backup creation.
- `list_backups()`, `get_backup(id)`, `delete_backups(ids)`, `export_backup(id)`, `import_backup(tmp_path, …)` — storage operations.
- `execute_restore(backup_id, req, …)` — orchestrated restore.

Primary consumer: `src/qwenpaw/app/routers/backup.py` (FastAPI `APIRouter(prefix="/backups")`) with `app/routers/_backup_helpers.py`. The restore callables (`stop_agent_fn`, `preload_agent_fn`, etc.) are injected by the router from the `MultiAgentManager` / browser manager. Separately, `app/_app.py` calls `cleanup_startup_restore_artifacts()` on startup and `envs/store.py` imports from `backup._utils.safe_swap` to reuse the swap primitives.

## AgentScope Integration
None. The backup subsystem operates purely on QwenPaw-local artifacts (config, secrets, agent workspace directories, skill pool) and standard-library facilities (`zipfile`, `hmac`, `asyncio`, filesystem renames). It does not import or call any `agentscope` API directly. (Agent *workspaces* it archives are produced elsewhere; see `../agentscope-v2/overview.md` only for background on what agents are — it is not used by this area.)

## Extension Points & Gotchas
- **Bumping the format**: `version` defaults to `"1"`; `restore._SUPPORTED_BACKUP_VERSIONS = {"1"}` gates restores. Add new versions there and handle migration in restore staging.
- **Adding a `BackupMeta` field**: update `digest._SIGNED_FIELDS` (or `_EXPLICIT_UNSIGNED`). `_assert_signed_fields_cover_model()` enforces that every model field has an explicit signing policy — forgetting it breaks the guard test.
- **Zip path prefixes are hardcoded** in `_utils/constants.py` (`PREFIX_CONFIG = "data/config.json"`, etc.) deliberately, so archives are portable regardless of `QWENPAW_CONFIG_FILE`. Do not derive them from env vars.
- **Signatures are local trust markers, not portable certificates.** A backup verifies only against the instance whose `.signing_key` created it; rotating the key forces `trust_mode="foreign"` on old backups. Legacy unsigned archives need `trust_mode="legacy"`. Trusted archives are re-signed in place, which mutates `meta.json` and `accepted_via_trust`.
- **Windows file-handle hazard is the dominant design constraint.** Directory renames fail while any process holds a handle inside the tree, so: agents are stopped before restore; secrets/skill-pool restores stop *all* running agents; targets are probed via reversible rename first; and a `restore_target_busy` `BackupValidationError` is raised rather than corrupting a partial restore.
- **Two-phase staging must stay atomic.** Never write files into a `dst` before `extract_to_tmp`/`commit_tmp` — phase 2/3 replaces the whole tree and would lose them (e.g. `handle_master_key_conflict` deliberately backs up the old master key *outside* `SECRET_DIR`).
- **Secrets restore reloads the master key** (`reload_master_key_from_disk()`); a differing `.master_key` is preserved as a timestamped `.bak` under `BACKUP_DIR/_pre_restore_keys/` so older credentials remain decryptable.
- **`include_secrets=False` is the default** in `BackupScope` — secrets are opt-in for creation.
- **Empty-prefix guard**: restore skips staging a category if the archive has no entries for it (e.g. `include_secrets=True` but no secrets in zip) to avoid wiping existing data.
- **Mount-point/Docker volumes**: rename of the mount dir itself fails; `_mount_swap.py` handles this by swapping children with crash-recoverable state markers. Reserved names (`.qwenpaw_restore_old`, state files) are skipped during extraction via `should_skip_restore_internal_path`.
