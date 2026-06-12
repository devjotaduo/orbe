# Spec Fase 5 — Console Admin Pages (plugin nexora-admin)

> Gerado por agente de pré-análise. Pronto para uso no workflow dev-team.
> Stack: Ant Design 5, plugin registry (slot primary.settings), NÃO shadcn.

## Estrutura final do plugin

```
console/src/plugins/bundle/nexora-admin/
├── plugin.json
└── ui/src/
    ├── index.ts                      (registra rotas + menus; atualizar)
    └── pages/
        ├── AuditLogs/               (já existe — Fase 3)
        ├── UserManagement/index.tsx (NOVO)
        ├── ApprovalCenter/index.tsx (NOVO)
        └── OpsGovernance/index.tsx  (NOVO)
```

## API clients a criar

### `console/src/nexora/api/users.ts`
Endpoint base: `/api/auth/*`
Funções: `usersApi.listUsers()`, `listRoles()`, `listPermissions()`, `createUser()`,
`updateUser(username, {roles?,status?,password?})`, `deleteUser()`, `createRole()`, `updateRole()`, `deleteRole()`.
Auth: `Authorization: Bearer ${localStorage.getItem("qwenpaw_auth_token")}`.

### `console/src/nexora/api/governance.ts`
Endpoint base: `/api/nexora/*`
Funções: `governanceApi.listPolicies()`, `savePolicy()`, `deletePolicy()`,
`listApprovalPolicies()`, `saveApprovalPolicy()`,
`listApprovalRequests({status?,action?})`, `approveApprovalRequest(id,reason)`, `rejectApprovalRequest(id,reason)`.

### `console/src/nexora/api/multiTenant.ts`
Endpoint base: `/api/nexora/*`
Funções: `multiTenantApi.listGrantsForAgent(agentId)`, `listGrantsForUser(username)`,
`batchGrant(agentId, usernames[])`, `batchRevoke(agentId, usernames[])`,
`listApprovalConfigs()`, `updateApprovalConfig(capType, payload)`,
`listTemplates()`, `createTemplate()`, `updateTemplate()`, `deleteTemplate()`.

## Página 1: UserManagement

Antd: `Table`, `Tabs` (Usuários / Roles), `Modal`, `Form`, `Input`, `Input.Password`,
`Select` (múltiplo p/ roles/permissions), `Popconfirm`, `Tag`, `Button`, `Space`.

Endpoints: CRUD completo de `/api/auth/users` e `/api/auth/roles`, `GET /api/auth/permissions`.

Menu item:
```typescript
{ id: "nexora.user-management", location: "primary.settings",
  parentId: "nexora.admin-group", label: "Usuários e Acessos",
  icon: UserOutlined, route: "nexora.user-management", order: 2 }
```
Rota: `/nexora/user-management`.

Permissão para mostrar: `users.view`.

## Página 2: ApprovalCenter

Antd: `Table`, `Tabs` (Requests / Config), `Card` (stats), `Form` (filtros),
`Select`, `Modal.confirm` com `Input.TextArea` (motivo de aprovação/rejeição),
`Tag` (status colorido), `Button`.

Endpoints: `listApprovalRequests`, `approveApprovalRequest`, `rejectApprovalRequest`,
`listApprovalConfigs`, `updateApprovalConfig`, `GET /api/auth/roles`.

Menu item:
```typescript
{ id: "nexora.approval-center", location: "primary.settings",
  parentId: "nexora.admin-group", label: "Centro de Aprovações",
  icon: CheckOutlined, route: "nexora.approval-center", order: 3 }
```
Rota: `/nexora/approval-center`.

Permissão: `governance.view` (leitura) / `governance.manage` (ação de aprovar/rejeitar).

## Página 3: OpsGovernance

Antd: `Table`, `Tabs` (Grants / Config / Templates), `Card`, `Modal`,
`Transfer` (seletor de usuários para grants), `Form`, `Input`, `Input.TextArea`,
`Select` (policies, approver_roles), `Button`, `Popconfirm`.

Endpoints:
- `GET /api/agents` (lista de agents)
- `listGrantsForAgent`, `batchGrant`, `batchRevoke`
- `listApprovalConfigs`, `updateApprovalConfig`
- CRUD de templates (`listTemplates`, `createTemplate`, `updateTemplate`, `deleteTemplate`)
- `GET /api/auth/users`, `GET /api/auth/roles`

Menu item:
```typescript
{ id: "nexora.ops-governance", location: "primary.settings",
  parentId: "nexora.admin-group", label: "Governança Operacional",
  icon: SafetyOutlined, route: "nexora.ops-governance", order: 4 }
```
Rota: `/nexora/ops-governance`.

Permissão: `governance.view` / `governance.manage`.

## Atualizar index.ts do plugin

O plugin index.ts já registra AuditLogs (Fase 3). Adicionar lazy imports das 3 novas páginas
e registrá-las via `QwenPaw.menu.add` e `QwenPaw.route.add`.
Grupo admin: `{ id: "nexora.admin-group", location: "primary.settings", label: "Nexora Admin", isGroup: true, order: 100 }`.
Verificar se o grupo já existe antes de adicionar (Fase 3 pode já ter criado).

## Locales

Adicionar em `console/src/locales/pt-BR.json`:
```json
{
  "nexora.userManagement": "Usuários e Acessos",
  "nexora.approvalCenter": "Centro de Aprovações",
  "nexora.opsGovernance": "Governança Operacional",
  "nexora.auditLogs": "Auditoria"
}
```

## Componentes compartilhados (extrair se >1 página usa)

- `ApprovalConfigTable.tsx` — tabela de config de capacidades (ApprovalCenter + OpsGovernance)
- `PermissionSelect.tsx` — seletor agrupado de permissões (UserManagement modal de role)
- `formatApprovalTime(ts)` — `new Date(ts * 1000).toLocaleString()`

## Critérios de aceite

- Sidebar exibe grupo "Nexora Admin" com 4 itens quando logado com `users.view`
- Navegação funciona para todas as rotas
- UserManagement: CRUD de usuários e roles com feedback de erro (403, 400)
- ApprovalCenter: listar requests, aprovar/rejeitar com motivo, configurar policies
- OpsGovernance: Transfer de usuários para grants, CRUD de templates
- Sem permissão → botões de ação ocultados (não apenas desabilitados)
- Testes vitest: render smoke + chamada de API mockada para cada página
