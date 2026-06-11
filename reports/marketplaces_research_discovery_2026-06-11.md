# Pesquisa de Marketplaces — ClawHub, ModelScope e origens nativas do QwenPaw

- **Data:** 2026-06-11
- **Complementa:** `reports/skillsllm_research_discovery_2026-06-11.md` (mesma metodologia, mesmo cruzamento)
- **Base do cruzamento:** taxonomia CNAE do discovery agent (10 segmentos PME BR) + design spec (`docs/superpowers/specs/2026-06-11-discovery-agent-design.md`)
- **Marketplaces cobertos:** ClawHub (clawhub.ai), ModelScope (modelscope.cn / .ai), skills.sh, SkillsMP, LobeHub, Aliyun AgentExplorer
- **Método:** 4 agentes de pesquisa em paralelo, usando APIs públicas dos catálogos quando disponíveis

---

## 1. Fato central: o QwenPaw já fala com esses marketplaces nativamente

`src/qwenpaw/agents/skill_system/hub.py` define as origens de instalação aceitas (`InstallOrigin`):

```
"skills-sh" | "github" | "lobehub" | "modelscope" | "aliyun" | "skillsmp" | "clawhub" | "url" | "zip"
```

- **ClawHub é o hub default** (`QWENPAW_SKILLS_HUB_BASE_URL=https://clawhub.ai`, API `GET /api/v1/search?q=`, detalhe em `/api/v1/skills/{slug}`).
- LobeHub instala via `market.lobehub.com/api/v1/skills/<id>/download` (exige `SKILL.md` no zip).
- ModelScope via `modelscope.cn/openapi/v1/skills` (provider em `src/qwenpaw/market/providers/modelscope.py`).
- Aliyun via API AgentExplorer (`agentexplorer.aliyuncs.com`, exige AccessKey Alibaba Cloud).

**Implicação:** tudo que existir nesses catálogos no formato SKILL.md é instalável com 1 clique no produto. MCP servers (LobeHub /mcp, ModelScope /mcp) entram por outro caminho (`.mcp.json`/tools) — o blueprint precisa distinguir.

---

## 2. Visão geral comparativa

| Marketplace | Tamanho | Formato | Curadoria | Valor p/ PME BR | Acesso |
|---|---|---|---|---|---|
| **ClawHub** | ~52,7k tools (12M downloads) | Skills SKILL.md + plugins + audits | Fraca; muito spam gerado em massa | **Alto** — único com RD Station, iFood, Mercado Pago, Chatwoot, Evolution API como *skills* nativas | Público, API aberta; hub default do qwenpaw |
| **ModelScope** | 9.626 MCP (2.138 hosted) + 75,5k skills | MCP + SKILL.md | `is_verified` raro; espelho em massa | Médio-alto — Evolution MCP, Mercado Livre hosted, **Qwen3-ASR com português** | Busca/instalação anônimas; hosted exige conta (.ai aceita e-mail intl.) |
| **skills.sh** | ~670k skills indexadas | SKILL.md (`npx skills add`) | **Melhor métrica**: installs reais + seção Official + audits | Médio — oficiais (Google, Shopify, HubSpot) + skill-vetter | Público, `GET /api/search?q=` |
| **SkillsMP** | ~1,73M skills (crawler GitHub) | SKILL.md | **Nenhuma** (o site avisa) | Alto na cauda longa BR — small-business-br, flowgrammers (401 skills pt-BR), Mercado Pago suite, Chatwoot da fazer.ai | Público, `/search?q=` + API REST |
| **LobeHub** | 10k+ MCP servers + Skills marketplace | MCP + SKILL.md | Fraca; typosquatting observado | **Alto** — BridgeAPI (Pix/NFe/Nuvemshop), VTEX, Pix MCP, **Brazilian Law MCP** | Público (site bloqueia bots; usar API de download) |
| **Aliyun AgentExplorer** | Pequeno, first-party Alibaba | Skills curadas | Oficial Alibaba | **Baixo** — só operação de nuvem (ECS/OSS/RDS), em chinês | Exige conta + AccessKey Alibaba Cloud |

---

## 3. Top picks por necessidade (cruzando todos os marketplaces)

### 3.1 WhatsApp — a lacuna do skillsllm.com ESTÁ resolvida aqui

| Item | Onde | Tração | Observação |
|---|---|---|---|
| **Evolution Api v2** (`evolution-api`, impa365) | ClawHub (skill nativa!) | v2.3.0, 1.383 dl | Instâncias, mídia, grupos, webhooks, **integração Chatwoot** — instalável 1-click no qwenpaw |
| **mcp-evolution-whatsapp-api** (aiteks-ltda) | ModelScope MCP + LobeHub | upstream Evolution 8,6k★ | O mesmo MCP já citado no design spec ✓ |
| **WAHA MCP** | LobeHub | upstream 6,7k★ | WhatsApp HTTP API self-hosted, 3 engines |
| **whatsapp-mcp** (lharries) | LobeHub | 5,8k★ | whatsmeow/Go — bom p/ piloto |
| **whatsapp-cloud-api** (skill) | LobeHub Skills + SkillsMP | — | **API oficial Meta** (templates, webhooks HMAC), descrição em português — rota compliance-safe |
| **gokapso/agent-skills** (3 skills) | skills.sh | 2,3k+1,8k+1,5k installs | SKILL.md exemplar, mas depende do SaaS Kapso |

⚠️ Tudo que é Evolution/WAHA/whatsmeow/Baileys viola ToS do WhatsApp (risco de ban). Estratégia: não-oficial no piloto, `whatsapp-cloud-api` oficial em produção — igual à decisão já registrada no spec.

### 3.2 Pagamentos BR — Pix e Mercado Pago existem (fora do skillsllm)

| Item | Onde | Observação |
|---|---|---|
| **Mercado Pago MCP** (hdbookie) | LobeHub | 27+ tools: **Pix com QR**, fraude, export contábil |
| **Pix MCP Server** (regenerating-world) | LobeHub | Cobranças Pix por linguagem natural |
| **mercadopago-claude-marketplace** (10 skills, diegomarcuz) | SkillsMP | API oficial MP: orders/QR Pix, webhooks x-signature, split — 0★, usar como referência |
| **mercado-pago** (gora050) | ClawHub | Skill nativa, mas gerada em massa — validar antes |
| **Stripe agent-toolkit oficial** | ModelScope MCP + LobeHub | 1,6k★ — SaaS/recorrência |

### 3.3 CRM e marketing BR

| Item | Onde | Observação |
|---|---|---|
| **rd-station** (gora050) | ClawHub | **Único RD Station de todos os 6 catálogos** — 418 dl, descrição template; validar ou usar como semente do conector próprio |
| **hubspot** (kwall1) | ClawHub | 6,9k dl, 26 installs reais — CRM mais maduro do hub nativo |
| **Pipedrive** | ClawHub (byungkyu, OAuth) + LobeHub MCP | Cobre o CRM nº 2 de PME BR |
| **hubspot/agent-cli-skills** (oficial) | skills.sh | Skill oficial da HubSpot |
| **flowgrammers-skills** (401 skills pt-BR) | SkillsMP | Mercado Livre, Shopee, Magalu, Meta/Google Ads BR, SEO, LGPD — maior acervo em português encontrado (100★) |

### 3.4 E-commerce e delivery BR

| Item | Onde | Observação |
|---|---|---|
| **mercadolibre-mcp** (lumile) | ModelScope (**hosted**) | Busca, reviews, reputação — só leitura; há também MCP oficial do Mercado Livre recém-criado (github.com/mercadolibre) |
| **VTEX MCP** (leosepulveda) | LobeHub | Catálogo, estoque, preços, pedidos — único VTEX encontrado |
| **BridgeAPI** | LobeHub | Conectores MCP brasileiros: WhatsApp, **Pix, NFe, Nuvemshop**, Mercado Livre, Hotmart — projeto novo (3★), monitorar |
| **ifood** (gora050) | ClawHub | Único iFood de todos os catálogos — qualidade incerta |
| **shopify-ai-toolkit** (oficial) | skills.sh | 4,8k–6,8k installs por skill |
| **tray-etiquetas-mercado-livre** | SkillsMP | **Skill oficial da Tray** (plataforma BR) — sinal de que players BR começaram a publicar |

### 3.5 Atendimento/helpdesk

| Item | Onde | Observação |
|---|---|---|
| **chatwoot** (gora050) | ClawHub | Chatwoot = par natural do Evolution API; validar qualidade |
| **fazer-ai/chatwoot-skills** (6 skills) | SkillsMP | **Empresa brasileira**; contatos, conversas, automações, admin |
| **zendesk-support** | ClawHub + ModelScope + LobeHub | Coberto em todos |

### 3.6 Planilhas, agenda, ERP (núcleo já coberto no skillsllm — confirmado aqui)

- **google-sheets** (byungkyu, ClawHub): 15k dl, 50 installs — skill nativa mais instalada do recorte.
- **gws-sheets/gws-calendar oficiais Google** (skills.sh): 32k installs cada.
- **Odoo**: `odoo` (ivangdavila, ClawHub — read-before-write) + `mcp-odoo`/`mcp-server-odoo` (ModelScope/LobeHub, mesmos do skillsllm ✓). ERPNext: `erpnext-server` no ModelScope; zero no skills.sh.
- **calendar-scheduling** (billylui, ClawHub): Google/Outlook/CalDAV + sub-skills de datetime.

### 3.7 Verticais e voz — dois achados raros

| Item | Onde | Observação |
|---|---|---|
| **Brazilian Law Research MCP** (`brlaw_mcp_server`, pdmtt) | LobeHub | **Jurisprudência STF/STJ/TST em fontes oficiais, tools em português** (31★) — match direto com a persona advocacia da avaliação |
| **Qwen3-ASR-1.7B/0.6B** | ModelScope (modelos) | ASR open-source com **52 idiomas incluindo português**, 328k downloads — melhor opção de voz pt-BR do ecossistema Qwen (casa do qwenpaw) |
| **audio-ptbr-autoreply** (henrique-simoes) | ClawHub | Única skill em português do hub inteiro: transcrição + resposta de áudio pt-BR (wav2vec2 local) |
| **claude-small-business-br** (12 skills, CarvalhoJeo) | SkillsMP | Fluxo de caixa, Simples Nacional, cobrança, lead triage com RD Station/Pix/boleto — match quase perfeito com o discovery, tração zero (fork/referência) |
| **brazil-lgpd** + **brazilian-fintech-compliance** | SkillsMP | LGPD e regras BCB/Pix — compliance |

### 3.8 Infra do próprio QwenPaw

- **memory** (ivangdavila, ClawHub): 16,1k dl, **230 installs** — item de uso real mais alto do hub nativo.
- **Mem0 MCP oficial** (LobeHub, 655★) — o mem0 que faltava no skillsllm.
- **episodic-memory** (obra, skills.sh, 8,5k installs).
- **Playwright MCP** (Microsoft, 33,8k★, LobeHub/ModelScope) — browser automation p/ portais sem API (bancos, prefeituras, NFS-e).
- **skill-vetter** (useai-pro, skills.sh, **19,3k installs**) + **skill-security-audit** (ClawHub) + **snyk/agent-scan** (2,6k★) — gates de segurança para instalação de skills de terceiros.
- **sequentialthinking** (ModelScope, 62k views) e **knowledge-graph-memory** (MCP oficial).

---

## 4. Lacunas consolidadas (agora cruzando os 6 marketplaces + skillsllm)

Resolvido em algum catálogo (✓) vs ainda vazio em todos (✗):

| Necessidade | Status | Onde |
|---|---|---|
| Evolution API / WhatsApp | ✓ | ClawHub (skill), ModelScope/LobeHub (MCP) |
| WhatsApp oficial Meta | ✓ | LobeHub Skills / SkillsMP (`whatsapp-cloud-api`) |
| Mercado Pago / Pix | ✓ (imaturo) | LobeHub (2 MCPs), SkillsMP (suite oficial 0★), ClawHub |
| RD Station | ✓ (frágil) | Só ClawHub (`rd-station`, gerada em massa) — **conector próprio continua justificado** |
| Mercado Livre | ✓ | ModelScope hosted (leitura) + MCP oficial do ML no GitHub |
| Nuvemshop / VTEX | ✓ (embrionário) | BridgeAPI e mcp-vtex no LobeHub (0–3★) |
| iFood | ✓ (suspeito) | Só ClawHub (gora050) |
| Chatwoot | ✓ | ClawHub + SkillsMP (fazer.ai BR) + LobeHub |
| Jurídico BR (STF/STJ/TST) | ✓ | LobeHub (`brlaw_mcp_server`) |
| STT português | ✓ | Qwen3-ASR (ModelScope) + audio-ptbr-autoreply (ClawHub) |
| **NF-e/NFS-e, boleto** | ✗ (quase) | Só módulo NFe do BridgeAPI (3★) |
| **ERPs SaaS BR (Bling, Tiny, Omie, Conta Azul)** | ✗ | Zero em todos os catálogos |
| **Asaas / PagSeguro / Gerencianet (Pix PSPs)** | ✗ | Zero |
| **Saúde/clínica BR (TISS, prontuário, Doctoralia)** | ✗ | Zero em todos |
| **Educação BR (gestão escolar; só Moodle genérico)** | ✗ | Zero |
| **Beleza/salão (Trinks, Booksy)** | ✗ | Zero |
| **PJe / prazos processuais / Astrea / Projuris** | ✗ | Zero (só jurisprudência) |

---

## 5. Riscos e observações de qualidade

1. **Spam gerado em massa no ClawHub:** o publisher `gora050` publica WhatsApp, Mercado Pago, iFood, RD Station, Chatwoot e ERPNext com descrições template ("Manage Recordses") — provável geração automática. Installs reais ≈ 0. **Testar antes de citar em blueprint.** Publishers com engenharia real: `byungkyu`/`hith3sh` (OAuth gerenciado), `ivangdavila`, `impa365`.
2. **Stars do SkillsMP enganam** (são do repo agregador, não do skill). Métrica confiável = installs do skills.sh.
3. **Dependência de SaaS oculta:** muitos skills são wrappers de plataformas pagas (Rube/Composio, Membrane, Kapso, Chompute). O blueprint deve sinalizar custo/dependência.
4. **MCP hosted da ModelScope roda na China** — latência alta e risco LGPD para dados de clientes (grave em saúde/jurídico). Preferir self-hosted; para conta, usar modelscope.**ai** (aceita e-mail internacional).
5. **Aliyun AgentExplorer não serve para PME BR** — só skills de operação Alibaba Cloud, em chinês, com AccessKey obrigatória. Tratar como origem de DevOps (se o deploy do time for em ECS).
6. **Typosquatting no LobeHub** (ex.: "anthropics-whatsapp-mcp" que não é da Anthropic). Gate de segurança obrigatório: `skill-vetter` (19,3k installs) ou `snyk/agent-scan` no fluxo de instalação.
7. **WhatsApp não-oficial = risco de ban** em produção multi-tenant (já registrado no spec; confirmado em todos os catálogos).

---

## 6. Recomendações

1. **Whitelist curada por origem:** o discovery agent não deve recomendar busca livre nos hubs — manter uma whitelist (slug + origem + versão validada) embutida na taxonomia. Sugestão de campo novo no `cnae_seed.json`: `known_connectors: [{origin, slug, status}]`.
2. **Prioridade de origem para PME BR:** ClawHub (1-click nativo) → LobeHub Skills → skills.sh (installs como sinal) → SkillsMP (só cauda longa BR, com vetting) → ModelScope (MCP self-hosted + Qwen3-ASR) → Aliyun (só DevOps).
3. **Gate de segurança automatizado:** integrar `skill-vetter`/`agent-scan` ao fluxo `hub.py` de instalação (o spec já exige security review de conectores; aqui está a ferramenta).
4. **Oportunidade estratégica — publicar no ClawHub:** o hub nativo tem **1 única skill em pt-BR** entre ~52,7k. Publicar as skills BR do qwenpaw (RD Station, Pix/NF-e, agendamento clínica/salão, iFood) daria domínio imediato das buscas em português no próprio hub default do produto.
5. **Voz pt-BR:** adotar Qwen3-ASR (ModelScope, ecossistema-irmão do qwenpaw) como engine de transcrição de áudio de WhatsApp — hábito fortíssimo de PME BR.
6. **Persona advocacia:** incluir `brlaw_mcp_server` (jurisprudência STF/STJ/TST) no blueprint do segmento servicos_b2b.
7. **Estender o provider ModelScope:** o endpoint `/openapi/v1/mcp/servers` (mesma base, PUT, sem auth) permitiria ao discovery recomendar MCPs além de skills.
