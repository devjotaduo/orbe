# Design — A2UI/AG-UI como plugin de chat configurável

- **Data:** 2026-06-11
- **Status:** Aprovado (brainstorming) — decisões delegadas pelo usuário
- **Stack:** qwenpaw (AgentScope 2.0.0, Python ≥3.11) + console (React 18 + TS + Ant Design 5) — Windows
- **Gate (backend):** `/agentscope-guardian`
- **Execução:** `/dev-team` em 2 fases (ver §8)
- **Reaproveita:** `src/qwenpaw/a2ui/`, `src/qwenpaw/agui/`, `console/src/components/a2ui/` (já construídos na branch); sistema de plugins do console (`window.QwenPaw.*`, doc `website/public/docs/plugins.en.md`).

---

## 1. Contexto e objetivo

A camada A2UI/AG-UI hoje está acoplada ao discovery (página `/discovery` + router SSE dedicado). O objetivo é torná-la **genérica e reusável no chat principal**, entregue como um **plugin configurável**: qualquer agente que rode no chat poderá desenhar **UI generativa** (cards, listas, inputs, botões) na própria bolha de resposta, chamando uma tool. O cérebro de discovery (e seus arquivos) **não** entra neste ciclo — o discovery passa a ser apenas um possível consumidor.

### Decisões (brainstorming 2026-06-11, delegadas)

1. **Transporte = tool render.** A surface A2UI é o **resultado de uma tool** (`render_ui`). O plugin registra `window.QwenPaw.chat.toolRender(...)` e desenha o resultado com o `A2uiRenderer`. Usa o streaming de chat já existente — **nenhum router SSE novo no chat**.
2. **Motor no core + plugin fino.** `a2ui/` e `agui/` ficam em `src/qwenpaw/`; o `A2uiRenderer`/binding/catalog ficam em `console/src/components/a2ui/` (fonte compartilhada). O plugin é a cola: a tool `render_ui` (backend) + o registro `chat.toolRender` (bundle frontend) + a config.
3. **Config = enable/disable + interatividade** (`read-only` vs `editable`). Default `read-only`.
4. **Action-back (Fase B) = `host.fetch` → endpoint do plugin.** O host SDK **não** expõe envio programático de turno; o que há é `host.fetch` (API com escopo do plugin) + `host.getCurrentSessionId/getSelectedAgentId`. A ação de uma surface editável faz `host.fetch` para um endpoint do próprio plugin, que valida e persiste/retorna o data-model editado.

### Escopo

- ✅ Tool backend `render_ui(surface)` (valida a surface via `a2ui.schema`); helper `a2ui.surface(...)` para montar surfaces programaticamente; bundle frontend do plugin registrando `chat.toolRender` → `A2uiRenderer`; manifesto + config (enable + interactivity); **Fase A** read-only e **Fase B** editável com action-back via endpoint do plugin.
- ❌ Fora: nosso cérebro de discovery (state/tools/agent/runner/prompts/segments/session/scripted/live/finalize), a página `/discovery` e o router `/discovery/*` — **ficam só na nossa branch**, não vão para a `main` neste ciclo. Sem AG-UI streaming no chat (a Fase de live/STATE em chat é futura).

---

## 2. Por que isso evita o conflito com a `main`

A `main` tem um cérebro de discovery paralelo (conectores/onboarding) que conflita em 18 arquivos com a nossa branch. **Nada disso entra aqui.** O que vai para a `main` é só material **novo e não-conflitante**:

- `src/qwenpaw/a2ui/` + `src/qwenpaw/agui/` (não existem na `main` → adição limpa).
- `console/src/components/a2ui/` (componentes novos).
- `plugins/a2ui-chat/` (plugin novo).

Os arquivos que conflitavam (`discovery/*`, locales, routes, cli) **não** são tocados.

---

## 3. Arquitetura (3 camadas)

```
CORE (genérico)                       PLUGIN (a cola)                 CHAT (host)
src/qwenpaw/a2ui/                      plugins/a2ui-chat/
  schema.py    (4 msgs + Component)      plugin.json   (manifest+config)   agente chama
  builder/surface helpers              plugin.py:                          render_ui(surface)
src/qwenpaw/agui/  (eventos; p/ uso       └ tool render_ui                    │ result = surface JSON
  futuro de streaming/live)               └ (Fase B) endpoint de ação        ▼ (stream de chat existente)
console/src/components/a2ui/           frontend bundle (dist/index.js):    chat.toolRender("a2ui-chat",
  A2uiRenderer+binding+catalog           └ chat.toolRender → A2uiRenderer    "render_ui") → A2uiRenderer
  (fonte compartilhada)                  └ lê config (interactivity)         (host.React/antd)
```

### Unidades

- **`a2ui/schema.py`** (já existe) — contrato das mensagens/Component. **Sem mudança** além de talvez um helper.
- **`a2ui/surface.py`** (novo, opcional) — helpers genéricos para um agente montar uma surface (`column/card/text/tag/button/...`) sem conhecer o JSON cru. Não específico a blueprint.
- **Plugin `plugins/a2ui-chat/plugin.py`** — registra a tool `render_ui(surface: dict|str) -> dict` que valida a surface (`a2ui.schema`) e a devolve como resultado da tool; (Fase B) registra um endpoint de ação.
- **Plugin frontend bundle** — build separado (padrão de plugin) que importa a fonte compartilhada `components/a2ui/` e registra `window.QwenPaw.chat.toolRender("a2ui-chat", "render_ui", renderer)`; usa `window.QwenPaw.host.React/antd`; lê a config do plugin para `read-only` vs `editable`.
- **`A2uiRenderer`/binding/catalog** (já existem) — o motor de render, agora consumido também pelo bundle do plugin.

---

## 4. Fluxo de dados (chat)

1. Um agente no chat chama a tool **`render_ui(surface)`** — `surface` é o JSON A2UI (montado via `a2ui.surface(...)` ou passado pronto).
2. O `plugin.py` valida a surface contra `a2ui.schema` (inválida → erro de tool visível, não engolido) e retorna a surface como resultado.
3. O resultado trafega no **stream de chat existente**; o `chat.toolRender("a2ui-chat","render_ui", …)` intercepta e renderiza com o `A2uiRenderer` dentro da bolha.
4. **Read-only:** renderiza e fim. **Editable (Fase B):** inputs/listas editam o data-model **local** ao componente renderizado; um botão de ação chama `host.fetch("/<endpoint do plugin>", { sessionId, action, data })`; o endpoint valida e persiste/retorna; o renderer reflete sucesso/erro (erro → aviso, edição preservada).

## 5. Configuração

Exposta no `meta`/settings do plugin e lida pelo bundle frontend:
- **`enabled`** — padrão do sistema de plugins (instalar/desinstalar/ligar).
- **`interactivity`** — `"read-only"` (default) | `"editable"`. Em `read-only`, o renderer ignora inputs/botões de ação (renderiza estático). Em `editable`, ativa edição + action-back.

## 6. Erros (sem falha silenciosa)

- Surface inválida em `render_ui` → erro de validação Pydantic propagado como erro da tool (visível no chat).
- Componente fora do catálogo → fallback visível no `A2uiRenderer` (já implementado).
- `host.fetch` de ação falho → aviso no chat, data-model editado preservado.
- Bundle/host indisponível (`window.QwenPaw.host` ausente) → o registro não acontece e o resultado cai no render padrão de tool (degradação graciosa, sem tela branca).

## 7. Testes

- **Backend (pytest, sem LLM):** `render_ui` valida surface (válida → devolve; inválida → erro); `a2ui.surface(...)` helpers montam adjacency-list correta; manifesto do plugin válido + tool registrada (carregamento do plugin). (Fase B) endpoint de ação valida/persiste data editado e recusa inválido.
- **Frontend (vitest):** o registro `chat.toolRender` monta o `A2uiRenderer` com a surface do `result`; config `read-only` desativa inputs/ações; config `editable` ativa; (Fase B) a ação chama `host.fetch` com `{action, data}` editado; surface malformada → fallback.
- Regressão: testes existentes de `a2ui`/`agui`/renderer continuam verdes; nada do discovery é tocado.

## 8. Execução em 2 fases

- **Fase A — render read-only no chat:** `a2ui/surface.py` helpers + tool `render_ui` (backend) + plugin (`plugin.json` + `plugin.py`) + bundle frontend com `chat.toolRender` (read-only) + config `enabled`. Entrega UI generativa no chat principal.
- **Fase B — interatividade configurável:** toggle `interactivity=editable`, renderer editável já existente ligado no contexto do chat, endpoint de ação do plugin + `host.fetch` action-back.

## 9. Critérios de aceite

1. Com o plugin ligado, um agente no chat que chama `render_ui(surface)` faz a UI A2UI aparecer **renderizada em Ant Design** na bolha de resposta (read-only).
2. Surface inválida vira erro visível; componente desconhecido → fallback; sem o plugin, degrada para o render padrão de tool.
3. Config `interactivity=editable` (Fase B) habilita edição + action-back via endpoint do plugin; `read-only` mantém estático.
4. O material que vai para a `main` (`a2ui/`, `agui/`, `components/a2ui/`, `plugins/a2ui-chat/`) **não conflita** com a `main` (nada de discovery tocado).
5. Suítes backend+frontend verdes; guardian aprova a parte backend.

## 10. Camadas futuras

AG-UI streaming/STATE ao vivo dentro do chat (surfaces que atualizam em tempo real); catálogo restringível por config; o agente de discovery da `main` adotando `render_ui` para mostrar o time; extrair `a2ui`/`agui` como pacote/SDK.
