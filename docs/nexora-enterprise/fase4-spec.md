# Spec Fase 4 — Grants / Governance / Capability Approval

> Gerado por agente de pré-análise do clone nexora-ai-platform.
> Pronto para ser passado como task ao workflow dev-team.

## Arquivos a portar (backend only)

### 1. `src/qwenpaw_ext/nexora/agent_grants.py` (154 linhas)
CRUD de concessões agente↔usuário. Dual-backend (JSON em `SECRET_DIR/nexora_agent_grants.json` ou Postgres).
Funções: `list_grants_for_agent`, `list_grants_for_user`, `get_authorized_agent_ids`, `is_user_granted`,
`grant_agent_to_user`, `revoke_agent_from_user`, `batch_grant_agent`, `batch_revoke_agent`.

### 2. `src/qwenpaw_ext/nexora/governance.py` (768 linhas)
Políticas de recurso (tool/MCP/skill) por agent, políticas de agent, políticas de aprovação por ação.
Funções chave: `agent_can_use_resource`, `filter_resource_ids_for_agent`, `ensure_resource_access`,
`role_ids_can_approve_action`, `migrate_governance_data`. Dual-backend (JSON / 3 tabelas Postgres).

### 3. `src/qwenpaw_ext/nexora/capability_approval.py` (208 linhas)
Config de aprovação por tipo de capacidade (skill/mcp/tool/plugin/acp).
Funções: `requires_approval`, `should_auto_approve`, `get_approver_roles`, `ensure_default_configs`.
CAPABILITY_TYPES = ("skill", "mcp", "tool", "acp", "plugin"). Dual-backend.

### 4. `src/qwenpaw_ext/nexora/authorization.py` (116 linhas)
Filtros de runtime: `filter_agent_ids_for_user`, `ensure_agent_access`, `enforce_agent_access_for_request`.
Helpers: `_is_auth_active`, `_is_admin`, `_get_username`, `_get_roles`, `_agent_id_from_path`.

### 5. Repositories (4 arquivos)
- `repositories/agent_grants_postgres.py` (166 linhas) — tabela `nexora_agent_user_grants(agent_id, username, granted_by, granted_at)` PK composta
- `repositories/governance_postgres.py` (326 linhas) — 3 tabelas (resource_policies, agent_policies, approval_policies) com JSONB
- `repositories/capability_approval_postgres.py` (147 linhas) — tabela `nexora_capability_approval_config`; `partial_update` com SET clauses dinâmico

### 6. Router nexora.py — seções novas a adicionar
Endpoints de agent-grants (`GET/POST/DELETE /api/nexora/agent-grants/{agent_id}`) e
capability-approval-config (`GET/PUT /api/nexora/capability-approval-config/{cap_type}`).
Permissão: `governance.view` (leitura) / `governance.manage` (escrita).
Helpers internos: `_current_username`, `_require_governance_view`, `_require_governance_manage`, `_current_role_ids`.

### 7. `src/qwenpaw/app/routers/_capability_approval.py` (NOVO, 153 linhas)
Helpers para routers de skills/mcp/tools:
`capability_create_requires_approval(request, action)`,
`capability_remove_requires_approval(request, action) -> (bool, bool)`,
`submit_capability_approval(...)`,
`record_auto_approved(...)`,
`pending_approval_response(approval, message)`.

### 8. Costura nos routers core (HUNKS pequenos, não substituição de arquivo)
- `routers/agents.py`: `filter_agent_ids_for_user` em list_agents; `ensure_agent_access` em get_agent
- `routers/mcp.py`: `filter_resource_ids_for_agent(..., "mcp", ...)` e `ensure_resource_access` + approval em create/delete
- `routers/tools.py`: `filter_resource_ids_for_agent(..., "builtin_tool", ...)` e `ensure_resource_access`
- `routers/skills.py`: `filter_resource_ids_for_agent(..., "skill", ...)` + approval workflow em create/delete
- `app/_app.py` lifespan: chamar `enterprise.initialize_governance(agent_ids)` no startup

### 9. Migrations
- `alembic/versions/0003_nexora_multi_tenant.py`: tabelas `nexora_agent_user_grants`, `nexora_capability_approval_config` (BOOL schema legado), `nexora_agent_templates` (skip templates na fase 4)
- `alembic/versions/0004_nexora_capability_approval_policy_enum.py`: migrar BOOL→TEXT enum (add_approval→add_policy, remove_approval/auto_approve_remove→remove_policy)

## Novas funções na ponte enterprise.py

```python
# Agent grants
filter_agent_ids_for_user(agent_ids, username, roles) -> list[str]  # fallback: retorna agent_ids
ensure_agent_access(username, roles, agent_id) -> None               # fallback: no-op
grant_agent_to_user(agent_id, username, granted_by) -> dict          # ← pairing do discovery
get_authorized_agent_ids(username) -> list[str]                      # fallback: []

# Governance
filter_resource_ids_for_agent(agent_id, source, resource_ids) -> list[str]  # fallback: retorna resource_ids
ensure_resource_access(agent_id, source, resource_id) -> None                # fallback: no-op
ensure_resource_policy(source, resource_id, *, ...) -> dict                  # fallback: dict vazio válido
initialize_governance(agent_ids: list[str]) -> None                          # fallback: no-op
```

## Critérios de aceite
- Sem extension/DB: zero mudança de comportamento (nenhum 403 novo)
- Com auth+grants: admin vê todos os agents; operator vê só agents concedidos
- Approval workflow: `skill.create` → 202 Accepted + request ID se requires_approval
- `grant_agent_to_user()` funciona isolado (chamável pelo pairing do discovery)
- Migrations 0003+0004 idempotentes; 0004 transforma legado corretamente
- Testes: sem Postgres real (mocks); PYTHONPATH do worktree
