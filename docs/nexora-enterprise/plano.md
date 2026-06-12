# Plano — Camada Enterprise (porte do Nexora AI Platform)

> Fonte analisada: https://github.com/lb08111/nexora-ai-platform (Apache 2.0, fork do mesmo
> upstream QwenPaw que o nosso). Clone local de referência: `C:\Users\ruthe\Desktop\orb\nexora-ai-platform`.
> Status: **plano aprovado para execução em fases via /dev-team** (guardian gate no backend).

## 1. A ideia

O Nexora transforma o QwenPaw num **workspace de IA enterprise multi-tenant**: vários usuários
na mesma instância, cada um com seus agentes e permissões, com governança central:

| Camada Nexora | O que faz |
|---|---|
| **RBAC multi-tenant** | Roles `admin`/`operator`, permissões por rota (`users.manage`, `agents.use`, `audit.view`…) |
| **Agent grants** | Concessão fina: quem pode usar qual agente |
| **Capability approval** | Workflow de aprovação por risco p/ instalar tools/skills/MCP/plugins |
| **Audit log** | Trilha completa (auth, chat, tool use, config, admin) em PostgreSQL |
| **Token analytics por usuário** | Consumo LLM por usuário/agente/modelo/data com dashboard |
| **Governance** | Políticas de recurso por agente (quais tools/MCP cada agente enxerga) |
| **PostgreSQL opcional** | Dual storage: JSON (default) ou Postgres se `NEXORA_DB_URL` setada |

**Por que nos interessa (Jotaduo):** o serviço de discovery atende empresários — multi-tenant +
grants + auditoria + custo de token por cliente é exatamente a camada de operação/cobrança
que falta para rodar vários clientes numa instância só, com governança.

## 2. O que a análise revelou (resumo dos achados)

### Arquitetura do Nexora (favorável ao porte)
- Backend isolado em **`src/qwenpaw_ext/nexora/`** (rbac, audit, governance, grants,
  capability_approval, agent_templates, db + `repositories/*_postgres.py`).
- Frontend isolado em **`console/src/nexora/`** (pages: UserManagement, AuditLogs,
  ApprovalCenter, OpsGovernance + api client).
- ~71 pontos de costura no core, mas todos no padrão **condicional**:
  `if db.is_database_enabled(): usa Postgres; senão JSON` — o core funciona sem a extensão.
- 4 migrations alembic (`0001`–`0004`). Postgres só guarda dados enterprise; o core continua JSON.
- docker-compose com `postgres:16-alpine` + app (`QWENPAW_AUTH_ENABLED=true`).

### Nosso fork (o que JÁ existe — não reimplementar)
- ✅ `auth.py` + `AuthMiddleware` + JWT custom (HMAC-SHA256, revocation list, `auth.json`),
  routers `/api/auth/*` — **single-user**, ativado por `QWENPAW_AUTH_ENABLED`.
- ✅ `token_usage/` e `agent_stats/` + routers + páginas no console (upstream).
- ✅ Console com **plugin registry** (slots `primary.agentScoped` / `primary.settings`),
  AuthGuard, página de Login, locales (incl. pt-BR), tema AionUi/antd.
- ❌ Não existe: `qwenpaw_ext/`, RBAC/roles, audit, grants, governance, alembic,
  SQLAlchemy/psycopg (nenhuma dep ORM no pyproject).

### Divergências do fork a preservar (risco de conflito BAIXO, mas atenção)
- `src/qwenpaw/discovery/` (cérebro discovery + `connectors_seed.json`) — self-contained.
- `a2ui/` + `agui/` + plugin `a2ui-chat` — não interagem com RBAC.
- Canal WhatsApp (neonize) — isolado via channel registry.

### Riscos reais
1. 🔴 **Base de upstream diferente**: o Nexora pode estar em outro snapshot do QwenPaw.
   Nunca copiar arquivo core inteiro — **portar só os hunks** de costura (diff dirigido).
2. 🔴 **AuthMiddleware**: estender o nosso com permissões/roles, não substituir pelo deles.
3. 🟡 **Deps novas**: `sqlalchemy>=2.0`, `psycopg[binary]` (Nexora usa psycopg2 sync —
   manter sync p/ portar os repositories sem reescrita), `alembic`.
4. 🟡 **Console**: o Nexora edita `MainLayout`/`Sidebar` na mão; nós temos plugin registry —
   usar a nossa via (ver melhorias).

## 3. Melhorias sobre o plano original do Nexora

1. **Costura por hooks, não por imports espalhados.** Em vez de 71 imports diretos de
   `qwenpaw_ext` no core, criar **um módulo ponte** `src/qwenpaw/app/enterprise.py` com a
   API de costura (`filter_agent_ids_for_user`, `ensure_resource_access`, `record_audit_event`,
   `is_database_enabled`…) usando `try: import qwenpaw_ext.nexora except ImportError: no-ops`.
   Os routers do core importam só a ponte → ~10 pontos de toque em vez de 71, e os merges
   de upstream (que fazemos com frequência) param de conflitar nesses arquivos.
2. **Admin pages via plugin registry, não editando MainLayout.** Registrar as 4 páginas
   admin como entradas no slot `primary.settings` (grupo "Administração") com gating por
   permissão (`NAV_PERMISSIONS`-style no item do registry). Mesma receita conflito-free
   usada no a2ui-chat.
3. **Postgres estritamente opcional.** Manter o dual-storage do Nexora e garantir fallback
   JSON para *tudo* (incl. users/roles), para a instalação single-user continuar zero-config.
4. **Atribuição por usuário no token_usage existente** (não duplicar módulo): estender o
   payload JWT com `roles` e propagar `user_id` para o `model_wrapper` — analytics por
   cliente sem fork do módulo upstream.
5. **pt-BR primeiro nas telas admin** (Nexora só tem en/zh) + terminologia leiga coerente
   com o produto (ex.: "Aprovações", "Auditoria", "Usuários e acessos", "Consumo").
6. **Tenant = cliente do discovery.** Grants de agente por usuário casam com o pareamento
   WhatsApp↔empresário: cada cliente enxerga só o(s) agente(s) dele. Incluir no escopo da
   Fase 4 um helper `grant_agent_to_user()` chamável pelo fluxo de pairing.
7. **Migrations idempotentes + `initialize_schema()`**: manter o esquema do Nexora de criar
   tabelas se não existirem (bom p/ dev), com alembic como caminho oficial em produção.
8. **Atribuição Apache 2.0**: NOTICE/comentário de origem nos arquivos portados.

## 4. Fases de execução (cada uma = um run do /dev-team)

> Backend passa pelo **agentscope-guardian**; console não é gated. Testes: pytest p/ backend
> (lembrar PYTHONPATH no worktree), vitest p/ console.

- **Fase 1 — Fundação** *(backend)*: deps (`sqlalchemy`, `psycopg[binary]`, `alembic` como
  extra opcional `[enterprise]`), copiar `src/qwenpaw_ext/nexora/{db,rbac,audit}.py` +
  repositories correspondentes, `alembic/` (0001+0002), módulo ponte `app/enterprise.py`
  com no-ops. Critério: app sobe sem Postgres e sem regressão; com `NEXORA_DB_URL` cria schema.
- **Fase 2 — RBAC sobre o auth existente** *(backend)*: estender JWT payload (roles),
  `_API_PERMISSION_PREFIXES`, endpoints de users/roles (multi-user), audit no middleware.
  Critério: single-user continua funcionando com auth desligado/ligado; admin cria operator.
- **Fase 3 — Audit + token analytics por usuário** *(backend + console)*: router
  `/api/nexora/audit`, propagação de `user_id` no token_usage, página AuditLogs + filtro
  por usuário no TokenUsage existente.
- **Fase 4 — Grants + governance + capability approval** *(backend)*: authorization.py,
  governance.py, capability_approval.py + costura via ponte nos routers
  agents/tools/mcp/skills; helper p/ pairing do discovery. Migrations 0003+0004.
- **Fase 5 — Console admin** *(frontend)*: portar `console/src/nexora/` adaptando ao nosso
  tema/registry (slot `primary.settings`, grupo Administração, gating por permissão),
  locales pt-BR/en.
- **Fase 6 — Deploy** *(infra, sem dev-team)*: docker-compose com postgres opcional
  (profile `enterprise`), docs de env vars (`QWENPAW_AUTH_ENABLED`, `NEXORA_DB_URL`…).

## 5. Fora de escopo (por ora)

- Agent templates do Nexora (baixo valor p/ nós agora).
- Reescrita async dos repositories (manter sync/psycopg como no original).
- SSO/OIDC (futuro; a base RBAC deixa o caminho aberto).
