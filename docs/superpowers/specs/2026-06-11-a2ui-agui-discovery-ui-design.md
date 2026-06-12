# Design — Camada A2UI + AG-UI (UI conversacional do discovery no console)

- **Data:** 2026-06-11
- **Status:** Aprovado (brainstorming) — aguardando revisão do spec antes do plano de implementação
- **Stack:** qwenpaw (fork de AgentScope 2.0.0, Python ≥3.11) + console (React 18 + TS + Ant Design 5 + Tauri) — Windows / PowerShell
- **Gate obrigatório (backend):** `/agentscope-guardian` (KB em `docs/agentscope-v2/`)
- **Execução prevista:** `/dev-team` (surface-aware: backend gated + `qwenpaw-coder`; frontend `qwenpaw-frontend-designer`)
- **Depende de:** `docs/superpowers/specs/2026-06-11-discovery-agent-design.md` (camada 1 — o "cérebro" que produz o blueprint)

---

## 1. Contexto e visão

A spec do discovery agent decompõe o produto em camadas e entrega a **camada 1** (o discovery roda em CLI e grava `blueprint.json` + `blueprint.md`). A **camada 3** prevista é a *UI conversacional no console*. Este ciclo entrega essa camada como a ligação entre o backend Python/AgentScope e o console React, usando **dois protocolos abertos e complementares**:

- **AG-UI** (Agent–User Interaction, CopilotKit — open): protocolo **de eventos** que padroniza a comunicação agente↔frontend (deltas de texto, sincronização de estado, ciclo de vida) via stream. É o **transporte**.
- **A2UI** (Agent-to-UI, a2ui.org / Google — open): protocolo de **UI generativa** — o agente envia JSON declarativo (`createSurface`, `updateComponents`, `updateDataModel`, `deleteSurface`) descrevendo a *intenção* da UI; o cliente renderiza com o **próprio catálogo de componentes** (Ant Design). Modelo de componentes em **adjacency-list** (árvore montada por referência de `id`).

A2UI trafega **por cima** do AG-UI (um event-type AG-UI carrega o payload A2UI), o mesmo padrão da integração oficial CopilotKit AG-UI ↔ A2UI.

### Escopo deste ciclo (decomposição)

- ✅ **No escopo:** backend emite eventos AG-UI **spec-compliant** durante a sessão de discovery; emite **surfaces A2UI spec-compliant** para blueprint/time/áreas; console com cliente AG-UI (SSE) + renderer A2UI→Ant Design; uma página nova de discovery conversacional ponta-a-ponta (entrevista ao vivo → blueprint visual).
- ❌ **Fora (camadas futuras):** deploy/geração real do time; conectores MCP reais; multi-tenant / banco; billing; interatividade A2UI avançada (forms ricos editáveis devolvendo ao agente) — fica um **subset mínimo** de ação (§6).

### Decisões de design tomadas no brainstorming (2026-06-11)

1. **Abordagem = nativa e spec-compliant.** Implementação própria no qwenpaw mapeada sobre o transporte que já existe (`StreamingResponse`/SSE, padrão de `app/routers/skills_stream.py`), mas seguindo fielmente o schema dos eventos AG-UI e das mensagens A2UI — sem dependências novas pesadas, interoperável com clientes externos no futuro.
2. **Escopo = fatia fina do discovery** (primeiro caso real ponta-a-ponta), não uma camada de protocolo genérica abstrata.
3. **Superfície = console web (Ant Design)**; o Tauri desktop embrulha o mesmo console e ganha de graça.
4. **Página nova** `console/src/pages/Discovery/`, isolada do `Chat` atual (shell próprio).
5. **Não mexe no `channels/` existente** — a camada AG-UI fica ao lado, dedicada ao discovery, via router SSE novo.

---

## 2. Arquitetura

```
Discovery runner (Python, camada 1)
   │  passos do loop (reflect → pergunta → emit_blueprint)
   ▼
AG-UI emitter (src/qwenpaw/agui)  ──SSE──▶  AG-UI client (console/src/api)
   │  eventos tipados (lifecycle/text/state/custom)        │
   └─ surfaces A2UI (src/qwenpaw/a2ui) viajam num          ▼
      event AG-UI CUSTOM                         A2UI renderer → Ant Design
                                                 (console/src/components/a2ui)
```

- **`src/qwenpaw/agui/`** — schema dos event-types AG-UI (Pydantic) + emitter que serializa SSE. Exposto por `app/routers/discovery_stream.py` (molde de `skills_stream.py`). Fica **ao lado** do `channels/`, não o substitui.
- **`src/qwenpaw/a2ui/`** — schemas das 4 mensagens A2UI + componentes (adjacency-list) + builder de surfaces a partir do blueprint.
- **`src/qwenpaw/discovery/`** (camada 1) ganha um **adapter** que, além de gravar `blueprint.json`, dirige o emitter AG-UI + o builder A2UI. O contrato `blueprint.json` permanece intacto.
- **Console** — cliente SSE AG-UI, renderer A2UI→Ant Design, página Discovery.

---

## 3. Subset de protocolo do 1º ciclo

### Eventos AG-UI (subconjunto dos 17 oficiais)

- **Lifecycle:** `RUN_STARTED`, `RUN_FINISHED`, `RUN_ERROR`.
- **Texto (pergunta do agente, streaming):** `TEXT_MESSAGE_START`, `TEXT_MESSAGE_CONTENT`, `TEXT_MESSAGE_END`.
- **Estado (DiscoveryState visível/auditável):** `STATE_SNAPSHOT`, `STATE_DELTA`.
- **Custom (carrega A2UI):** `CUSTOM`.
- **Inbound (usuário → agente):** mensagem de texto (resposta da entrevista) + **uma** ação A2UI ("confirmar/seguir").
- Deferidos para camadas futuras: `TOOL_CALL_*`, `MESSAGES_SNAPSHOT`, eventos de thinking, etc. — registrados, não implementados.

### Catálogo A2UI → Ant Design (1º ciclo)

| Componente A2UI | Ant Design |
|---|---|
| `Surface` (raiz) | container da página |
| `Column` / `Row` | `Row`/`Col` (flex) |
| `Card` | `Card` |
| `List` | `List` |
| `Heading` / `Text` | `Typography.Title` / `Typography.Text` |
| `Tag` | `Tag` |
| `Button` (ação) | `Button` |
| `Divider` | `Divider` |

Componente fora do catálogo → renderer mostra **fallback visível** (não tela branca) e registra warning. Catálogo é extensível em camadas futuras.

---

## 4. Componentes (unidades isoladas e testáveis)

### Backend (`src/qwenpaw/`) — **gated** pelo `/agentscope-guardian`

- **`agui/events.py`** — schemas Pydantic dos event-types (puro, sem agentscope; testável isolado). *O quê:* define os eventos. *Usa:* nada. *Depende de:* Pydantic.
- **`agui/emitter.py`** — converte passos do discovery em eventos AG-UI e serializa SSE (`data: {json}\n\n`). *Depende de:* `events.py`.
- **`a2ui/schema.py`** — schemas das 4 mensagens + componentes adjacency-list. *Puro, testável isolado.*
- **`a2ui/builder.py`** — `TeamBlueprint → surface A2UI` (Cards do time, lista de áreas, tags de integração). *Depende de:* `schema.py` + os schemas do blueprint (camada 1).
- **`discovery/agui_adapter.py`** — liga o runner do discovery ao emitter + builder (sem alterar a lógica de raciocínio da camada 1).
- **`app/routers/discovery_stream.py`** — endpoint SSE da sessão (`StreamingResponse`), molde de `skills_stream.py`; recebe inbound (texto/ação) e devolve o stream de eventos.

### Frontend (`console/`) — `qwenpaw-frontend-designer`, **sem gate**

- **`api/types/agui.ts`, `api/types/a2ui.ts`** — tipos TS espelhando o schema do backend.
- **`api/modules/discovery.ts`** — cliente SSE: abre o stream, parseia eventos, expõe estado.
- **`components/a2ui/`** — renderer: percorre a adjacency-list e monta Ant Design; faz data-model binding (`updateDataModel`); fallback visível para componente desconhecido.
- **`pages/Discovery/`** — página nova: campo de resposta da entrevista + painel de estado (DiscoveryState) + área onde as surfaces A2UI renderizam (blueprint/time).

---

## 5. Fluxo de dados

1. Usuário abre a página Discovery → o console abre o SSE em `/discovery/stream`.
2. Runner roda o loop; o emitter emite `RUN_STARTED` → `TEXT_MESSAGE_*` (pergunta) → `STATE_SNAPSHOT/DELTA` (DiscoveryState atualizado).
3. Usuário responde (texto) → inbound → próximo turno (volta ao passo 2).
4. Ao emitir o blueprint, o `a2ui/builder` gera `createSurface` + `updateComponents` + `updateDataModel`, empacotados num event `CUSTOM`; o renderer monta o time/áreas em Ant Design.
5. Ação "confirmar/seguir" do usuário → inbound de ação → `RUN_FINISHED`. `blueprint.json` + `blueprint.md` continuam gravados (contrato para camadas futuras intacto).

---

## 6. Interatividade — subset mínimo deste ciclo

A entrevista é conversacional → **inbound de texto (usuário → agente) entra** no escopo. **Ações de componente A2UI** ficam num subset mínimo: **um único event de ação** (`A2UI action → AG-UI inbound`) para o caso "confirmar/seguir". Forms ricos editáveis (editar um card do time e devolver ao agente) ficam para a próxima camada — sem fechar a porta (o catálogo e o event-type de ação já existem, só não expandidos).

---

## 7. Erros, testes e gate

### Tratamento de erros (sem falha silenciosa)

- Evento AG-UI / mensagem A2UI inválida → erro de validação Pydantic propagado como `RUN_ERROR` (não engolido).
- SSE interrompido → o cliente reconecta; o estado é reconstruído do próximo `STATE_SNAPSHOT`.
- Surface malformada ou componente fora do catálogo → renderer mostra **fallback visível** + warning, nunca tela branca.

### Testes

- **Backend (pytest, sem LLM real):** validação dos schemas AG-UI/A2UI (válido vs. inválido); `emitter` produz a sequência de eventos esperada num discovery mockado; `builder` gera surface válida a partir de um `TeamBlueprint` canned (e-commerce/atendimento WhatsApp, reusando o caso da camada 1).
- **Frontend (vitest):** renderer monta a árvore adjacency-list correta em Ant Design (inclui o caso de componente desconhecido → fallback); cliente SSE parseia a sequência de eventos e atualiza o estado.

### Gate

A parte backend mexe em `src/qwenpaw/` sobre AgentScope 2.x → passa por **`/agentscope-guardian`** antes de fechar. Frontend (`console/`) não é gated. Implementação conduzida pelo **`/dev-team`**.

---

## 8. Critérios de aceite do ciclo

1. Página Discovery no console abre uma entrevista **ao vivo**: perguntas chegam por streaming (AG-UI `TEXT_MESSAGE_*`) e o DiscoveryState é visível e atualiza (`STATE_*`).
2. O caso simples (atendimento WhatsApp para e-commerce) roda ponta-a-ponta da entrevista até o blueprint **renderizado como surface A2UI** (cards do time + áreas + tags de integração) em Ant Design.
3. Eventos AG-UI e mensagens A2UI são **spec-compliant** (schema fiel; interoperáveis com clientes externos no futuro).
4. Componente A2UI fora do catálogo degrada para fallback visível, sem quebrar a tela.
5. Ação "confirmar/seguir" fecha a sessão; `blueprint.json` + `blueprint.md` continuam sendo gravados.
6. Testes (pytest backend + vitest frontend) passam; `/agentscope-guardian` aprova a parte backend.

---

## 9. Camadas futuras (fora deste ciclo, para contexto)

1. **Interatividade A2UI rica** — forms editáveis, aprovar/ajustar o time componente a componente devolvendo ao agente (expandir o subset do §6).
2. **AG-UI genérico** — generalizar a camada para qualquer agente do console (Chat, etc.), não só o discovery.
3. **Tool-call streaming** — `TOOL_CALL_*` para mostrar ao vivo o agente consultando taxonomia/integrações.
4. **Deploy do time / conectores / multi-tenant** — camadas já previstas na spec do discovery agent.
