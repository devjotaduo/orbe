# Relatório de Implementação — Recursos do Ecossistema QwenPaw / AgentScope

**Data:** 2026-06-12 · **Método:** time de agentes dev (3 agentes em paralelo) — pesquisa GitHub do ecossistema AgentScope, pesquisa do QwenPaw upstream + forks, e inventário do nosso código local. Cruzamento → análise de lacunas → priorização.

> Fonte da verdade: `gh` CLI (autenticado) + leitura do código em `src/qwenpaw/`. Itens não verificados em código-fonte estão marcados **(não confirmado)**.

---

## 1. Sumário executivo

O nosso fork já cobre **a maior parte** do núcleo do QwenPaw upstream (ACP, skills, memória proativa/ADB-PG/ReMe, mission runner, roteamento de modelos, MCP, canais de chat, tool guard, console/Tauri, plugins, crons, backup) **mais** adições próprias do fork (camada **A2UI/AG-UI**, módulo **discovery**, canal **WhatsApp/neonize**).

As **lacunas reais** — recursos que existem no ecossistema e que **não temos** — concentram-se em cinco frentes:

1. **Camada enterprise** (RBAC / multi-tenant / audit / governança) — maior lacuna, só existe em repo externo (Nexora) e já há plano nosso.
2. **Sandbox de execução real** (Docker/E2B) para tool-calls perigosas — temos `tool_guard` + `app/workspace/`, mas não isolamento real nos moldes do AgentScope 2.0.
3. **Self-Evolution / auto-criação de skills** com gate AST (draft→active).
4. **Agent OS Driver** — abstração unificada de MCP/A2A/ACP (PR upstream #5067).
5. **RAG / vector store / embeddings nativos** + **observabilidade visual** (tracing OpenTelemetry estilo agentscope-studio).

---

## 2. Inventário local (baseline) — o que JÁ temos

Resumo do que está implementado em `src/qwenpaw/` (maturidade: sólida / parcial / stub):

| Capacidade | Módulo | Maturidade | Origem |
|---|---|---|---|
| ACP (Agent Client Protocol) | `agents/acp/` | sólida | upstream |
| Sistema de skills + pool | `agents/skill_system/`, `agents/skills/` | sólida | upstream |
| Memória ADB-PG / ReMe / AGENT.md | `agents/memory/adbpg_*`, `reme_*`, `agent_md_manager` | sólida | upstream |
| Memória proativa | `agents/memory/proactive/` | parcial | upstream |
| Mission runner | `agents/mission/`, `app/runner/mission_dispatch.py` | sólida | upstream |
| Roteamento de modelos | `agents/routing_chat_model.py`, `model_factory.py` | sólida | upstream |
| MCP / tool-use | `app/mcp/`, `agents/tools/` | sólida | upstream |
| Tool guard / aprovações | `security/tool_guard/`, `app/approvals/` | sólida | upstream |
| Skill scanner (AST) | `security/skill_scanner/` | parcial | upstream |
| Secret store | `security/secret_store.py`, `envs/store.py` | sólida | upstream |
| Canais de chat (telegram, discord, feishu, dingtalk, wecom, wechat, qq, matrix, mattermost, imessage, mqtt, onebot, voice/sip…) | `app/channels/` | sólida | upstream |
| **Canal WhatsApp (neonize)** | `app/channels/whatsapp/` | sólida | **fork** (porte #3498) |
| **A2UI (generative UI)** | `a2ui/` | sólida | **fork** |
| **AG-UI (eventos + SSE)** | `agui/` | sólida | **fork** |
| **Plugin de chat A2UI (frontend)** | `console/src/plugins/` | parcial | **fork** |
| **Discovery agent (entrevista→blueprint)** | `discovery/` | sólida | **fork** |
| Providers (anthropic, openai, openrouter+OAuth, gemini, dashscope, ollama, lmstudio) | `providers/` | sólida | upstream |
| Modelos locais (llama.cpp/Ollama/LMStudio) | `local_models/` | sólida | upstream |
| Console / Tauri / TUI | `console/`, `tauri/`, `cli/tui/` | sólida | upstream |
| Observabilidade / stats / token usage | `agent_stats/`, `token_usage/`, `utils/telemetry.py` | sólida | upstream |
| Compactação de contexto | `agents/context/` | sólida | upstream |
| Multi-agente / subagentes | `app/multi_agent_manager.py`, `runtime/agent_factory.py` | sólida | upstream |
| Crons / backup / plan mode / tunnel / workspace | `app/crons/`, `backup/`, `plan/`, `tunnel/`, `app/workspace/` | sólida/parcial | upstream |

**Docs:** existe `docs/agentscope-v2/` (KB do guardião, descreve o alvo 2.0) e `docs/design/`. **Não existe `docs/qwenpaw/`.** Base instalada = AgentScope **1.0.20** (docs miram 2.0 — breaking change).

---

## 3. Recursos do ecossistema (o que existe lá fora)

### 3.1 Framework AgentScope v2 — `agentscope-ai/agentscope` (⭐26.7k)
Módulos do core v2 dignos de porte:
- **`permission/`** — motor de regras de permissão para tool-use (autorização/HITL estruturado).
- **`middleware/`** — cadeia de hooks ao redor de reasoning/acting/tool-call (tracing, políticas, TTS).
- **`workspace/`** — sandbox real com backends **Docker / E2B / local**, `_mcp_gateway`, `offload_protocol`.
- **`app/`** — Agent-as-a-Service embutido (router, service, message_bus, `_redis_storage`, lifespan).
- **`compress_context`** — gestão automática de janela de contexto no `Agent`.
- Toolkit builtin estilo Claude Code (`bash/read/write/edit/glob/grep/skill`) + `_tool_group` (ativação dinâmica de tools).
- MCP nativo, multi-provider+formatter+credential, embedding com cache, TTS+TTS-middleware, state/task.

> `agentscope-runtime` está **arquivado** — capacidades migraram para o core v2. Usar como referência de design; o código vivo está em `workspace/` + `app/`.

### 3.2 QwenPaw upstream — `agentscope-ai/QwenPaw` (⭐17.4k, v1.1.11, cadência semanal)
**PRs abertos de alto valor** (ainda não mergeados):
| PR | Feature | Valor |
|---|---|---|
| #5067 | **Agent OS Driver** — abstração unificada MCP/A2A/ACP | Alto |
| #4443 / #4655 | **Lightweight Goal Mode** | Alto |
| #4622 | **Datapaw** — plugin data-analysis com 12 skills de BI | Alto |
| #5088 | Interface de **governança & sandbox** | Alto |
| #4532 | **OAuth 2.1** para MCP remoto | Alto |
| #4630 | MCP marketplace + health-check + validação de chave | Médio |
| #4171 | **memory-distill** (destilação por title-diffing) | Médio |
| #4902 | PRD CRUD tool built-in + renderer | Médio |
| #5069 | Fallback de modelo visual → texto | Médio |

**Recém-mergeados (jun/2026):** Runtime 2.0 modular com coordenação de tool-call (#5078), Plugin Market + AgentScope Platform (#5023), isolamento de keychain por install (#5028), multi-path skill pool (#4891).

### 3.3 Forks / repos satélite notáveis
| Repo | Adiciona | Valor |
|---|---|---|
| [lb08111/nexora-ai-platform](https://github.com/lb08111/nexora-ai-platform) (59★) | **Enterprise**: RBAC, grants por agente, audit trail PostgreSQL, token analytics, aprovação risk-based, governança centralizada | **Alto** |
| [plhys/qwenpaw-evolution](https://github.com/plhys/qwenpaw-evolution) (4★) | **Self-Evolution**: auto-criação de skills a partir de requisitos, com auditoria AST e workflow draft→active | Alto |
| [kingsa2026/QwenPaw_HumanThinking_plugin](https://github.com/kingsa2026/QwenPaw_HumanThinking_plugin) (10★) | Memória com mecanismo de "sono", merge de memórias similares, resolução de contradições cross-session | Médio |
| [One-sixth/qwenpaw-plugin-session-tools](https://github.com/One-sixth/qwenpaw-plugin-session-tools) (3★) | **Fork/rewind/regen** de sessões | Médio |
| [agentscope-ai/PawBench](https://github.com/agentscope-ai/PawBench) (57★) | Benchmark LLM × harness | Médio |
| [log-z/copaw-docker](https://github.com/log-z/copaw-docker) (53★) | Deploy Docker enxuto | Médio |
| [huxuehao/apboa](https://github.com/huxuehao/apboa) (131★) | Tools/hooks online dinâmicos, HITL, AGUI, RAG (plataforma AgentScope) | Médio-Alto |
| [agentscope-ai/agentscope-samples](https://github.com/agentscope-ai/agentscope-samples) (319★) | Receitas: `deep_research`, `browser_use`, `evaluation`, `tuner` | Alto |
| [agentscope-ai/agentscope-studio](https://github.com/agentscope-ai/agentscope-studio) (572★) | Observabilidade visual / tracing OpenTelemetry | Médio-Alto |

---

## 4. Análise de lacunas (gap analysis)

Recursos do ecossistema **ausentes** no nosso fork, ordenados por impacto:

| # | Lacuna | Existe em | Esforço | Impacto |
|---|---|---|---|---|
| L1 | **Enterprise: RBAC / multi-tenant / audit / governança** | nexora-ai-platform; plano já em `docs/nexora-enterprise/` | Alto | Alto |
| L2 | **Sandbox de execução real (Docker/E2B)** para tool-calls | AgentScope v2 `workspace/`; QwenPaw #5088 | Médio-Alto | Alto |
| L3 | **Agent OS Driver** (MCP/A2A/ACP unificado) | QwenPaw #5067 | Médio | Alto |
| L4 | **Self-Evolution / auto-skill-creation** com gate AST | qwenpaw-evolution | Médio | Alto |
| L5 | **Goal Mode leve** (sobre o mission runner atual) | QwenPaw #4443/#4655 | Médio | Médio-Alto |
| L6 | **MCP OAuth 2.1 + marketplace/health-check** | QwenPaw #4532/#4630 | Médio | Médio-Alto |
| L7 | **RAG / vector store / embeddings nativos** | AgentScope `embedding/`; agentscope-bricks | Médio | Médio |
| L8 | **Observabilidade visual / tracing** (OpenTelemetry) | agentscope-studio; QwenPaw #5128 | Médio | Médio |
| L9 | **Datapaw (BI/data-analysis, 12 skills)** | QwenPaw #4622 | Médio | Médio |
| L10 | **Session fork/rewind/regen** | plugin session-tools | Baixo-Médio | Médio |
| L11 | **memory-distill** (destilação de memória) | QwenPaw #4171 | Baixo-Médio | Médio |
| L12 | **Migração AgentScope 2.0** (event system tipado, `reply_stream`) | core v2 | Alto | Estratégico |

> Já cobrimos com adições do fork: A2UI/AG-UI (≈ camada AGUI do apboa), canal WhatsApp, discovery agent. Não recomendar reimplementar.

---

## 5. Recomendações priorizadas (roadmap)

### Fase 1 — Ganhos de produção rápidos (baixo/médio esforço, alto valor)
1. **L6 — MCP OAuth 2.1 + health-check** (#4532/#4630): porte direto, fortalece o `app/mcp/` que já temos.
2. **L11 — memory-distill** (#4171): incremento pequeno sobre `agents/memory/`, alto retorno em qualidade de contexto.
3. **L10 — Session fork/rewind/regen**: melhora UX no `app/runner/session.py` + console; baixo risco.

### Fase 2 — Diferenciais de plataforma (médio esforço)
4. **L3 — Agent OS Driver** (#5067): unifica MCP/A2A/ACP — encaixa na nossa base ACP+MCP existente.
5. **L4 — Self-Evolution / auto-skill** com gate AST: aproveita `security/skill_scanner/` (já temos AST) + `skill_system/`.
6. **L5 — Goal Mode leve** (#4443): camada fina sobre `agents/mission/`.
7. **L8 — Observabilidade visual**: integrar tracing OpenTelemetry sobre `agent_stats/` + `token_usage/`.

### Fase 3 — Frentes estruturais (alto esforço, estratégico)
8. **L1 — Enterprise (RBAC/audit/governança)**: já há plano nosso (`docs/nexora-enterprise/plano.md`, 6 fases via /dev-team). Maior lacuna de mercado.
9. **L2 — Sandbox real (Docker/E2B)**: alinhar `app/workspace/` ao `workspace/` do AgentScope v2; pré-requisito de segurança para tools arbitrárias.
10. **L7 — RAG/embeddings nativos** + **L9 — Datapaw**.
11. **L12 — Migração AgentScope 2.0**: decisão estratégica (breaking change 1.0.20→2.0); destrava sandbox, app server e event system nativos. **Sujeito ao gate `agentscope-guardian`.**

---

## 6. Próximos passos sugeridos
- Escolher 1–2 itens da Fase 1 e rodar o fluxo padrão: brainstorming/spec → plano → **/dev-team** (backend passa pelo gate `agentscope-guardian`).
- Itens marcados **(não confirmado)** nos forks devem ser inspecionados em código antes de qualquer porte.
- Toda feature de backend toca AgentScope → revisão obrigatória do guardião (KB em `docs/agentscope-v2/`).

---

*Relatório gerado pelo time de agentes dev (pesquisa paralela GitHub + inventário de código). Estrelas/PRs conforme GitHub em 2026-06-12.*
