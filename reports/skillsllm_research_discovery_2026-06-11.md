# Pesquisa SkillsLLM.com — Ferramentas, plugins, skills e agentes para o QwenPaw

- **Data:** 2026-06-11
- **Fonte:** https://skillsllm.com/ (catálogo de ~2.989 skills/MCP servers/agentes open-source para Claude Code, Codex CLI e ChatGPT — 2.260 AI Agents, 478 MCP Servers, 130 CLI Tools)
- **Base do cruzamento:** taxonomia CNAE do discovery agent (`src/qwenpaw/discovery/segments/data/cnae_seed.json`, 10 segmentos) + design spec (`docs/superpowers/specs/2026-06-11-discovery-agent-design.md`)
- **Método:** 4 agentes de pesquisa em paralelo (clusters: comunicação/atendimento, vendas/CRM/marketing, operações/dados, plataforma/infra + verticais), usando a busca interna do catálogo (`skillsllm.com/?q=TERMO`), sitemap e listagens por categoria/stars. Todos os itens listados têm URL confirmada no catálogo. Stars conforme exibido pelo site em jun/2026 (alguns contadores divergem do GitHub — confirmar no upstream antes de fixar em blueprint).

---

## 1. Resumo executivo

O catálogo resolve bem o **núcleo genérico** dos blueprints do discovery agent — planilhas/agenda (Google Workspace), ERP (Odoo/ERPNext), e-commerce Shopify, helpdesk Zendesk, CRM HubSpot, marketing/SEO, memória de agentes, RAG/scraping, browser automation e segurança de conectores.

O **miolo "Brasil"** — exatamente o que o design já apontava como diferencial — **não existe no catálogo**: Evolution API/WhatsApp Business oficial, RD Station, Pipedrive, Mercado Pago/Pix, iFood, Mercado Livre/Nuvemshop/VTEX, Chatwoot, prontuário/PDV/LMS, jurídico BR (PJe/LGPD) e STT em pt-BR. Isso **confirma a estratégia do spec**: construir os conectores BR do zero (ou plugar MCPs oficiais fora do catálogo) é onde o qwenpaw gera valor único.

WhatsApp existe no catálogo apenas via **protocolo não-oficial** (Baileys/whatsmeow) — útil para protótipo, arriscado (ban/ToS) para produção multi-tenant, reforçando o alerta já registrado no spec.

---

## 2. Top picks por necessidade do discovery agent

### 2.1 WhatsApp (integração nº 1 em 8 dos 10 segmentos)

| Item | URL | Stars | O que é |
|---|---|---|---|
| **nanoclaw** | skillsllm.com/skill/nanocoai-nanoclaw | ~29,8k | Plataforma leve de agentes em containers (Claude Agent SDK) com WhatsApp (Baileys), Telegram, Slack, Gmail; memória e tarefas agendadas |
| **whatsapp-cli** | skillsllm.com/skill/whatsapp-cli | 173 | CLI Go standalone (WhatsApp Web multidevice), JSON estruturado, binário único — peça mínima componível |
| **moltis** | skillsllm.com/skill/moltis | 2,7k | Servidor de agente em Rust com voz, memória, WhatsApp/Telegram/Discord/Teams |

⚠️ Todos usam protocolo WhatsApp Web **não-oficial**. `?q=evolution` e `?q=baileys` no catálogo = zero MCPs dedicados. **Lacuna**: MCP de Evolution API e de WhatsApp Business Cloud API oficial — ambos fora do catálogo (ex.: `aiteks-ltda/mcp-evolution-whatsapp-api`, já citado no spec).

### 2.2 Planilhas + Agenda (citadas em todos os segmentos)

| Item | URL | Stars | O que é |
|---|---|---|---|
| **google_workspace_mcp** | skillsllm.com/skill/google-workspace-mcp | 2,6k | MCP MIT (Python) p/ Gmail, Calendar, Sheets, Docs, Drive — 12 serviços, OAuth 2.0/2.1. **Cobre planilha + agenda + e-mail num só conector** |
| **mcp-google-sheets** | skillsllm.com/skill/mcp-google-sheets | 903 | MCP dedicado de Sheets (19 tools, Service Account) — é o **mesmo `xing5/mcp-google-sheets` já citado no spec** ✓ |
| **googleworkspace-cli (gws)** | skillsllm.com/skill/googleworkspace-cli | — | CLI **oficial do Google** (Rust) com 40+ agent skills e saída JSON; pré-1.0 |
| **excel-mcp-server** | skillsllm.com/skill/excel-mcp-server | 3,9k | Cria/edita .xlsx sem Excel instalado — PME que vive de planilha local |
| **keeper.sh** | skillsllm.com/skill/keeper-sh | 1,1k | MCP universal de calendário (Google, Outlook 365, iCloud, CalDAV); AGPL |

**Lacuna**: Cal.com/Calendly = zero resultados.

### 2.3 CRM e vendas (serviços, tecnologia, B2B/advocacia)

| Item | URL | Stars | O que é |
|---|---|---|---|
| **mcp-hubspot** | skillsllm.com/skill/baryhuang-mcp-hubspot | 126 | **Único CRM real do catálogo** — mesmo `baryhuang/mcp-hubspot` já citado no spec ✓ (com vector storage p/ contornar limites da API) |
| **b2b-sdr-agent-template** | skillsllm.com/skill/b2b-sdr-agent-template | 117 | AI SDR open-source: pipeline de 10 estágios, memória 4 camadas, multicanal **WhatsApp+Telegram+Email** — template direto para o agente comercial dos blueprints |
| **linkedin-mcp-server** | skillsllm.com/skill/linkedin-mcp-server | 2,3k | Prospecção/outreach B2B via LinkedIn |

**Lacunas graves**: RD Station, Pipedrive, Salesforce, Attio/Twenty/EspoCRM = zero. Confirma o spec: **conector RD Station é build próprio**. Fallback catalogado: **n8n** (192k★) tem nodes nativos de Pipedrive/HubSpot/RD Station.

### 2.4 Marketing (e-commerce, varejo, serviços locais)

| Item | URL | Stars | O que é |
|---|---|---|---|
| **claude-seo** | skillsllm.com/skill/claude-seo | 8,6k | 25 sub-skills + 18 sub-agentes de SEO (técnico, local, e-commerce, GEO/AEO) — maior tração do cluster |
| **claude-ads** | skillsllm.com/skill/claude-ads | 5,9k | 250+ checks de mídia paga (Google/Meta/TikTok Ads) + geração de criativos |
| **ai-marketing-claude** | skillsllm.com/skill/ai-marketing-claude | 1,9k | 15 skills: copy, sequências de e-mail, campanhas, calendário de conteúdo, relatórios PDF |
| **google-meta-ads-ga4-mcp** | skillsllm.com/skill/google-meta-ads-ga4-mcp | 1,0k | MCP com 250+ tools de Google Ads, Meta Ads e GA4 |
| **postiz-agent** | skillsllm.com/skill/postiz-agent | 284 | Agendamento de posts em redes sociais (Postiz ~20k★) |
| **instagram_dm_mcp / ig-mcp** | skillsllm.com/skill/instagram-dm-mcp | 171/141 | DMs do Instagram — forte em varejo/beleza/moda BR |

### 2.5 ERP e dados da empresa (varejo, e-commerce, construção, B2B)

| Item | URL | Stars | O que é |
|---|---|---|---|
| **mcp-odoo** | skillsllm.com/skill/mcp-odoo | 332 | 36 tools sobre Odoo 16–19, ferramentas contábeis (aging de contas), escrita com tokens de aprovação e audit trail |
| **mcp-server-odoo** | skillsllm.com/skill/mcp-server-odoo | 312 | Alternativa MPL-2.0, instalação `uvx mcp-server-odoo` |
| **Frappe_Assistant_Core** | skillsllm.com/skill/frappe-assistant-core | 246 | ERPNext: 24 tools (faturas, clientes, estoque), respeita permissões; **AGPL-3.0** |
| **dbhub** | skillsllm.com/skill/dbhub | 2,9k | MCP de banco (Postgres/MySQL/SQL Server/SQLite), modo read-only — ERP legado via SQL |
| **pgmcp** | skillsllm.com/skill/pgmcp | 533 | Postgres em linguagem natural, somente-leitura — "perguntas ao banco" seguras p/ dono de PME |
| **airtable-mcp-server** | skillsllm.com/skill/airtable-mcp-server | 447 | Mini-CRM/estoque em Airtable. ⚠️ scan do site marca ReDoS high-severity em dependência |
| **notion-mcp-server** | skillsllm.com/skill/notion-mcp-server | 154 | 35+ operações Notion em 2 tools agente-otimizadas |

### 2.6 E-commerce e atendimento

| Item | URL | Stars | O que é |
|---|---|---|---|
| **shopify-mcp** | skillsllm.com/skill/shopify-mcp | 217 | 31 tools GraphQL Admin API: pedidos, reembolso, inventário — **única plataforma de e-commerce no catálogo** |
| **zendesk-mcp-server** | skillsllm.com/skill/zendesk-mcp-server | 102 | CRUD de tickets + Help Center como base de conhecimento — único helpdesk catalogado |
| **agent-desk** | skillsllm.com/skill/agent-desk | 128 | Atendimento AI-first self-hosted: RAG com answerability gate, handoff humano, widget web |
| **anythingmcp** | skillsllm.com/skill/anythingmcp | 117 | **Gateway API→MCP** (REST/SOAP/GraphQL/SQL, inclui WooCommerce) — workaround genérico p/ APIs BR sem MCP (Mercado Pago, iFood, Nuvemshop) |

**Lacunas**: Mercado Livre, Nuvemshop, VTEX, iFood, Chatwoot, Freshdesk, Intercom = zero.

### 2.7 Plataforma do próprio QwenPaw (camadas futuras do spec)

| Item | URL | Stars | Camada |
|---|---|---|---|
| **n8n** | skillsllm.com/skill/n8n | 192k | Backbone de workflows dos times gerados (licença fair-code — atenção em multi-tenant comercial) |
| **n8n-mcp** | skillsllm.com/skill/n8n-mcp | 21,7k | Agentes constroem workflows n8n (1.851 nós). ⚠️ scan FAILED: 147 vulns npm — passar pelo security-reviewer antes |
| **claude-mem** | skillsllm.com/skill/claude-mem | 81,7k | Memória entre sessões (candidato concreto p/ "nano-memory" do spec) |
| **TencentDB-Agent-Memory** | skillsllm.com/skill/tencentdb-agent-memory | 4,5k | Memória local-first em 4 camadas (SQLite + sqlite-vec), zero APIs externas — boa p/ multi-tenant por PME |
| **deep-research** | skillsllm.com/skill/deep-research | 4,6k | Implementação de referência do padrão deep_research já adotado no motor do discovery |
| **Scrapling** | skillsllm.com/skill/scrapling | 62,8k | Scraping adaptativo em Python (mesmo stack do qwenpaw) — ingestão de sites de PMEs sem API |
| **firecrawl-mcp-server** | skillsllm.com/skill/firecrawl-mcp-server | 6,5k | Scrape+search MCP p/ RAG (scan WARNING) |
| **SwarmVault** | skillsllm.com/skill/swarmvault | 538 | Wiki/knowledge-graph local-first: transcrições da entrevista de discovery → base RAG por tenant |
| **dev-browser / browsermcp / BrowserAct** | skillsllm.com/skill/dev-browser | 6,2k/6,7k/2,3k | Browser automation p/ integrações sem API (portais, ERPs web) |
| **AgentShield** | skillsllm.com/skill/agentshield | 845 | `npx ecc-agentshield scan` — audita config de agentes/MCP (segredos, prompt injection) — candidato ao pipeline de security review de conectores |
| **graphify** | skillsllm.com/skill/graphify | 65,1k | Pasta → knowledge graph consultável |

### 2.8 Verticais (advocacia, saúde, educação, voz)

| Item | URL | Stars | O que é |
|---|---|---|---|
| **claude-legal-skill** | skillsllm.com/skill/claude-legal-skill | 320 | Revisão de contratos (dataset CUAD, 41 categorias de risco), redlines .docx — template p/ segmento advocacia, **precisa adaptação a direito BR/pt-BR** |
| **legal-ai-agent** | skillsllm.com/skill/legal-ai-agent | 182 | Agente jurídico localizado (Vietnã) — arquitetura de referência p/ versão BR |
| **Patter** | skillsllm.com/skill/patter | 515 | SDK de voz/telefonia p/ agentes (Twilio/Telnyx, STT/TTS, transferência de chamada) |
| **FunASR** | skillsllm.com/skill/funasr | 17,8k | ASR industrial 50+ idiomas — ⚠️ não declara português; validar antes |

**Lacunas totais**: saúde/prontuário, educação/LMS, jurídico Brasil (PJe, CNJ, LGPD), STT pt-BR dedicado (alternativa fora do catálogo: faster-whisper/WhisperX atrás de MCP próprio).

---

## 3. Mapa segmento → itens do catálogo

| Segmento (cnae_seed) | Itens recomendados |
|---|---|
| E-commerce | shopify-mcp, claude-seo, claude-ads, nanoclaw/whatsapp-cli, google_workspace_mcp, anythingmcp (gateway p/ Nuvemshop/ML) |
| Varejo | excel-mcp-server, instagram_dm_mcp, postiz-agent, whatsapp-cli, dbhub (PDV via SQL) |
| Serviços | google_workspace_mcp (agenda), mcp-hubspot, b2b-sdr-agent-template, keeper.sh |
| Alimentação/Delivery | nanoclaw (pedidos por WhatsApp), google_workspace_mcp — iFood = lacuna (gateway anythingmcp ou conector próprio) |
| Saúde/Clínica | google_workspace_mcp + keeper.sh (agendamento/lembrete) — prontuário = lacuna |
| Educação | notion-mcp-server, mcp-hubspot (captação), nanoclaw — LMS = lacuna |
| Beleza/Salão | keeper.sh/google_workspace_mcp (agenda), instagram_dm_mcp, whatsapp-cli |
| Tecnologia/SaaS | mcp-hubspot, zendesk-mcp-server, linkedin-mcp-server, dbhub, claude-seo |
| Construção | excel-mcp-server, mcp-odoo (ERP de obra), google_workspace_mcp, whatsapp-cli |
| Serviços B2B/Advocacia | claude-legal-skill (adaptar), linkedin-mcp-server, mcp-hubspot, b2b-sdr-agent-template, Frappe_Assistant_Core (financeiro) |

---

## 4. Lacunas consolidadas = roadmap de diferencial BR do QwenPaw

Nada disso existe no skillsllm.com (confirmado por busca em jun/2026):

1. **WhatsApp oficial/Evolution API** — MCP próprio (spec já prevê; Evolution fora do catálogo: `aiteks-ltda/mcp-evolution-whatsapp-api`)
2. **RD Station** — build próprio (spec já prevê; API REST simples)
3. **Pagamentos BR** — Mercado Pago/Pix (MCP oficial do Mercado Pago existe fora do catálogo); Stripe Agent Toolkit oficial também fora (`stripe/agent-toolkit`)
4. **iFood / Mercado Livre / Nuvemshop / VTEX** — conectores próprios ou via gateway anythingmcp
5. **Chatwoot** (helpdesk OSS mais popular no BR) — zero no catálogo
6. **Jurídico BR** (PJe, CNJ, LGPD), **prontuário**, **LMS**, **PDV** — verticais vazias
7. **STT pt-BR** — faster-whisper/WhisperX via MCP próprio
8. **mem0** — não catalogado (404); upstream `mem0ai/mem0` fora do catálogo

## 5. Alertas de segurança (gate `security-reviewer` do spec)

- **n8n-mcp**: scan do catálogo **FAILED** (147 vulns npm, várias críticas)
- **airtable-mcp-server**: ReDoS high-severity no MCP TypeScript SDK
- **firecrawl-mcp / exa-mcp**: WARNING (vulns em deps)
- **WhatsApp não-oficial** (nanoclaw/whatsapp-cli/moltis): risco de ban/ToS Meta em produção multi-tenant — manter a decisão do spec de migrar p/ Cloud API oficial
- O próprio SkillsLLM publica scan diário (Semgrep + npm audit + pip-audit) com selo PASS/WARNING/FAIL por item — **usar como critério de curadoria automática de conectores nos blueprints**

## 6. Próximos passos sugeridos

1. **Curto prazo (camada de conectores do spec):** adotar do catálogo `google_workspace_mcp` (planilha+agenda+email), `mcp-hubspot`, `mcp-odoo`/`Frappe_Assistant_Core` e `shopify-mcp` como referências de `tools_integrations` nos blueprints; manter Evolution/WhatsApp oficial como build próprio.
2. **Enriquecer o `cnae_seed.json`:** adicionar em cada segmento um campo opcional de "conectores conhecidos" (slug skillsllm/repo) para o `emit_blueprint` citar integrações concretas, não genéricas.
3. **Pipeline de curadoria:** incorporar o selo de segurança do SkillsLLM + `AgentShield` no fluxo `security-reviewer` de conectores.
4. **Templates verticais:** usar `b2b-sdr-agent-template` (comercial multi-canal) e `claude-legal-skill` (advocacia) como base de `AgentSpec` prontos por segmento.
5. **Memória:** avaliar `claude-mem` vs `TencentDB-Agent-Memory` (local-first, bom p/ multi-tenant) como sucessor do `DiscoveryState` persistido.
