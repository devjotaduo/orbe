# Design — Conectores conhecidos (whitelist curada) no Discovery Agent

- **Data:** 2026-06-11
- **Status:** Aprovado (brainstorming) — aguardando revisão do spec antes do plano
- **Base:** relatórios `reports/skillsllm_research_discovery_2026-06-11.md` e `reports/marketplaces_research_discovery_2026-06-11.md`
- **Gate obrigatório:** `/agentscope-guardian` (mexe em `src/qwenpaw/`)
- **Execução prevista:** `/dev-team` (backend)

---

## 1. Contexto e objetivo

Hoje o blueprint do discovery agent cita integrações genéricas (`"whatsapp"`, `"crm"`, `"planilha"`). As pesquisas de marketplace mapearam conectores concretos instaláveis pelas origens nativas do qwenpaw (`hub.py`: clawhub, lobehub, modelscope, skills-sh, skillsmp, github) e as lacunas BR onde o conector é build próprio.

**Objetivo:** o blueprint passa a recomendar conectores concretos — com origem, slug, status e notas de risco — a partir de uma whitelist curada, sem mudar o tom leigo da entrevista.

### Decisões do brainstorming

1. **Consumo via tool separada** — nova tool `connector_lookup`, chamada pelo agente na hora de montar o blueprint (a entrevista continua em linguagem leiga).
2. **Curadoria "top picks + lacunas com flag"** — ~30 entradas: confiáveis (`recomendado`), suspeitas (`validar`) e lacunas BR (`build`).
3. **Blueprint com seção estruturada** — `TeamBlueprint.recommended_connectors` (lista de objetos), retrocompatível.
4. **Abordagem A de dados** — catálogo separado `connectors_seed.json` indexado por tipo canônico de integração; segmentos continuam listando tipos em `common_integrations` (normalizados); o join é feito pelo lookup.

---

## 2. Arquitetura (tudo em `src/qwenpaw/discovery/`)

| Unidade | Mudança |
|---|---|
| `segments/data/connectors_seed.json` | **Novo.** Whitelist curada (seção 4). |
| `segments/data/cnae_seed.json` | `common_integrations` normalizado para o vocabulário canônico (seção 3). |
| `segments/taxonomy.py` | **Novo model** `ConnectorInfo` + `load_connectors()` (cache, igual `load_segments`) + `lookup_connectors(kind, segment=None)`. Validação Pydantic no load — seed inválida falha alto e claro. |
| `state.py` | **Novo model** `ConnectorRef` (campos de `ConnectorInfo` sem `id`/`segments`); `TeamBlueprint.recommended_connectors: list[ConnectorRef] = []` (default vazio → blueprints antigos seguem válidos). |
| `tools.py` | 4ª tool `connector_lookup(integration_kind: str)` no `DiscoverySession`; filtra por `state.company.segment` automaticamente quando o conector declara `segments`. `_blueprint_to_markdown` ganha a seção "Conectores recomendados" (nome, origem, status, notas — incluindo avisos de risco). |
| `prompts.py` | Instrução: antes de `emit_blueprint`, chamar `connector_lookup` para cada integração detectada/proposta e preencher `recommended_connectors`; em `AgentSpec.tools_integrations` usar a referência curta `"<origin>:<slug>"`. |

### Contratos

```python
class ConnectorInfo(BaseModel):
    id: str                      # único na seed
    integration_kind: str        # vocabulário canônico (seção 3)
    name: str
    origin: Literal["clawhub", "lobehub", "modelscope",
                    "skills-sh", "skillsmp", "github", "build"]
    slug_or_url: str             # slug no marketplace, repo, ou "" p/ build
    status: Literal["recomendado", "validar", "build"]
    notes: str = ""              # pt-BR; riscos, licença, dependência de SaaS
    segments: list[str] = []     # vazio = vale p/ todos os segmentos

class ConnectorRef(BaseModel):   # em state.py, vai no blueprint
    integration_kind: str
    name: str
    origin: str
    slug_or_url: str
    status: str
    notes: str = ""
```

`lookup_connectors(kind, segment=None)` → `tuple[ConnectorInfo, ...]` ordenada por status (`recomendado` → `validar` → `build`). Quando `segment` é informado, exclui conectores cujo `segments` (não-vazio) não contém esse segmento; quando `segment` é `None`/vazio, retorna todos do kind (inclusive os segmentados).

---

## 3. Vocabulário canônico de `integration_kind`

`whatsapp`, `crm`, `planilha`, `agenda`, `erp`, `pagamento`, `fiscal`, `ecommerce`, `helpdesk`, `email`, `delivery`, `voz`, `juridico`, `lms`, `pdv`, `prontuario`, `chat-interno`, `analytics`.

Normalização do `cnae_seed.json` atual (mapa aplicado uma vez, na implementação):

| Valor atual | Canônico |
|---|---|
| `plataforma de e-commerce` | `ecommerce` |
| `planilha/erp` | `planilha`, `erp` (divide em dois) |
| `gateway de pagamento`, `stripe/pagamento` | `pagamento` |
| `agenda/calendar`, `agenda`, `agenda online` | `agenda` |
| `ifood/cardápio` | `delivery` |
| `prontuário/erp` | `prontuario`, `erp` |
| `plataforma/lms` | `lms` |
| `helpdesk/tickets` | `helpdesk` |
| `slack/discord` | `chat-interno` |
| `e-mail` | `email` |
| `erp de obra`, `erp/financeiro` | `erp` |
| `pdv` | `pdv` |
| demais (`whatsapp`, `crm`, `planilha`, `analytics`) | inalterados |

Kinds sem conector curado (ex.: `pdv`, `prontuario`, `lms`, `chat-interno`, `analytics`) são válidos — o lookup responde "sem conector curado" (seção 5).

---

## 4. Seed inicial (`connectors_seed.json`, ~30 entradas)

Fonte: os dois relatórios de pesquisa. Notas resumidas; texto final na implementação.

| id | kind | name | origin | slug_or_url | status | notas-chave | segments |
|---|---|---|---|---|---|---|---|
| evolution-api-clawhub | whatsapp | Evolution API v2 | clawhub | evolution-api | recomendado | Não-oficial (risco ban); integra Chatwoot | — |
| whatsapp-cloud-api-lobehub | whatsapp | WhatsApp Cloud API (oficial Meta) | lobehub | techwavedev-agi-agent-kit-whatsapp-cloud-api | recomendado | Rota compliance p/ produção | — |
| mcp-evolution-whatsapp | whatsapp | MCP Evolution API | github | aiteks-ltda/mcp-evolution-whatsapp-api | recomendado | MCP já citado no design do discovery | — |
| hubspot-clawhub | crm | HubSpot | clawhub | hubspot | recomendado | 26 installs reais; publisher kwall1 | — |
| mcp-hubspot | crm | mcp-hubspot (baryhuang) | github | baryhuang/mcp-hubspot | recomendado | Vector storage p/ limites de API | — |
| rd-station-clawhub | crm | RD Station | clawhub | rd-station | validar | Gerada em massa (gora050); testar antes | — |
| rd-station-build | crm | Conector RD Station próprio | build | — | build | API REST simples; diferencial BR | — |
| pipedrive-clawhub | crm | Pipedrive | clawhub | pipedrive-api | validar | OAuth gerenciado (byungkyu) | — |
| google-sheets-clawhub | planilha | Google Sheets | clawhub | google-sheets | recomendado | 15k dl / 50 installs; skill mais usada | — |
| mcp-google-sheets | planilha | mcp-google-sheets (xing5) | github | xing5/mcp-google-sheets | recomendado | Já citado no design do discovery | — |
| excel-mcp-server | planilha | Excel MCP (xlsx local) | github | haris-musa/excel-mcp-server | recomendado | PME que vive de planilha local | — |
| google-workspace-mcp | agenda | Google Workspace MCP | github | taylorwilsdon/google_workspace_mcp | recomendado | Cobre agenda + email + planilha (MIT) | — |
| calendar-scheduling-clawhub | agenda | calendar-scheduling | clawhub | calendar-scheduling | recomendado | Google/Outlook/CalDAV + datetime | — |
| keeper-sh | agenda | keeper.sh | github | ridafkih/keeper.sh | validar | AGPL; tier grátis sincroniza a cada 30min | — |
| mcp-odoo | erp | mcp-odoo (tuanle96) | github | tuanle96/mcp-odoo | recomendado | 36 tools, contábil, audit trail | — |
| odoo-clawhub | erp | Odoo | clawhub | odoo | validar | read-before-write (ivangdavila) | — |
| frappe-assistant-core | erp | ERPNext (Frappe Assistant) | github | buildswithpaul/Frappe_Assistant_Core | validar | AGPL-3.0 — atenção em multi-tenant | — |
| mercado-pago-mcp | pagamento | Mercado Pago MCP | lobehub | hdbookie-mercado-pago-mcp | validar | Pix com QR; baixa tração | — |
| pix-mcp | pagamento | Pix MCP | lobehub | regenerating-world-pix-mcp | validar | Pix standalone; baixa tração | — |
| stripe-agent-toolkit | pagamento | Stripe Agent Toolkit (oficial) | github | stripe/agent-toolkit | recomendado | Sem Pix; SaaS/recorrência | — |
| nfe-build | fiscal | Conector NF-e/NFS-e próprio | build | — | build | Lacuna em todos os marketplaces | — |
| shopify-mcp | ecommerce | shopify-mcp (GeLi2001) | github | GeLi2001/shopify-mcp | recomendado | 31 tools GraphQL Admin | — |
| vtex-mcp | ecommerce | mcp-vtex | lobehub | leosepulveda-mcp-vtex | validar | Único VTEX encontrado | — |
| mercadolivre-mcp | ecommerce | Mercado Livre MCP (oficial) | github | mercadolibre/mercadolibre-mcp-server | validar | Recém-criado | — |
| nuvemshop-build | ecommerce | Conector Nuvemshop próprio | build | — | build | BridgeAPI embrionário (3★) | — |
| chatwoot-fazer-ai | helpdesk | Chatwoot skills (fazer.ai) | github | fazer-ai/chatwoot-skills | validar | Empresa BR; par natural do Evolution | — |
| zendesk-mcp | helpdesk | zendesk-mcp-server | github | reminia/zendesk-mcp-server | recomendado | Tickets + Help Center | — |
| ifood-clawhub | delivery | iFood | clawhub | ifood | validar | Gerada em massa; único iFood achado | alimentacao |
| ifood-build | delivery | Conector iFood próprio | build | — | build | Lacuna real do segmento | alimentacao |
| qwen3-asr | voz | Qwen3-ASR | modelscope | Qwen/Qwen3-ASR-1.7B | recomendado | 52 idiomas incl. português; ecossistema Qwen | — |
| audio-ptbr-clawhub | voz | audio-ptbr-autoreply | clawhub | audio-ptbr-autoreply | validar | Única skill pt-BR do ClawHub (wav2vec2) | — |
| brlaw-mcp | juridico | Brazilian Law Research MCP | github | pdmtt/brlaw_mcp_server | recomendado | Jurisprudência STF/STJ/TST, tools em pt | servicos_b2b |

---

## 5. Fluxo e tratamento de erros

**Fluxo:** entrevista inalterada → ao preparar o blueprint, para cada integração detectada (`state.integrations`) ou proposta no time, o agente chama `connector_lookup(kind)` → escolhe entre os retornados (prompt orienta: preferir `recomendado`; incluir `validar` com a nota de risco; `build` vira item de roadmap) → preenche `recommended_connectors` e usa `"<origin>:<slug>"` em `tools_integrations`.

**Erros (sem falha silenciosa):**
- Kind desconhecido → `ToolChunk` de erro (`_err`, mesmo padrão do `reflect` com JSON inválido) com a lista de kinds válidos e instrução de reenviar.
- Kind válido sem conector curado → mensagem orientando registrar `ConnectorRef` com `origin="build"`, `status="build"` e abrir `open_question`.
- Seed inválida (id duplicado, kind/origin/status fora do vocabulário) → `ValidationError` no primeiro load, com mensagem apontando a entrada.

---

## 6. Testes (pytest, em `tests/discovery/`)

- **Unit — seed:** carrega e valida; ids únicos; kinds/origins/status dentro dos vocabulários; entradas `build` têm `slug_or_url` vazio.
- **Unit — lookup:** kind com conectores (ordenação por status); kind válido sem conector; kind desconhecido; filtro por segmento (`brlaw-mcp` só aparece p/ `servicos_b2b`; `ifood-*` só p/ `alimentacao`).
- **Unit — taxonomia normalizada:** `common_integrations` de todos os segmentos ⊆ vocabulário canônico (teste guarda contra regressão).
- **Unit — state:** `TeamBlueprint` valida com e sem `recommended_connectors`; markdown renderiza a nova seção (e omite quando vazia).
- **Integração (LLM mockado):** entrevista roteirizada de e-commerce produz blueprint com ≥1 `ConnectorRef` de `whatsapp` e referência curta correspondente em `tools_integrations`.
- Sem chamadas reais de LLM (mock de `create_model_and_formatter`), como nos testes existentes.

---

## 7. Critérios de aceite

1. `connector_lookup` disponível como 4ª tool; responde com conectores curados filtrados por segmento.
2. `cnae_seed.json` usa apenas kinds canônicos; teste de regressão garante.
3. Blueprint emitido contém `recommended_connectors` estruturado e a seção correspondente no `blueprint.md`, com notas de risco visíveis.
4. Blueprints antigos (sem o campo) continuam validando.
5. Testes unit + integração mockada passam; `/agentscope-guardian` aprova.

## 8. Fora de escopo (camadas futuras)

- Instalação automática dos conectores (camada de conectores do produto).
- Atualização automática da whitelist a partir dos marketplaces (re-pesquisa periódica).
- Gate de segurança automatizado (skill-vetter/agent-scan) no fluxo de instalação do `hub.py`.
