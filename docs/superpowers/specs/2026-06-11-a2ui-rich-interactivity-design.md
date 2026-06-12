# Design — Interatividade A2UI rica (edição e aprovação do time no console)

- **Data:** 2026-06-11
- **Status:** Aprovado (brainstorming) — decisões delegadas pelo usuário
- **Stack:** qwenpaw (AgentScope 2.0.0, Python ≥3.11) + console (React 18 + TS + Ant Design 5) — Windows
- **Gate (backend):** `/agentscope-guardian`
- **Execução:** `/dev-team` em 2 fases (ver §8)
- **Depende de:** specs `2026-06-11-a2ui-agui-discovery-ui-design.md` (camada A2UI/AG-UI, implementada) e `2026-06-11-discovery-agent-design.md` (cérebro, implementado)

---

## 1. Contexto e visão

Hoje a surface A2UI do blueprint (time proposto) é **read-only** e a sessão de discovery termina ao emitir. Este ciclo expande o §6 da spec A2UI/AG-UI ("subset mínimo de ação") para **interatividade rica e spec-compliant**: o empresário ajusta o time direto na tela — edita campos dos agentes, adiciona/remove/reordena agentes, edita tasks e integrações — e clica **Aprovar**, que envia o blueprint final ao backend.

### Decisões de design (brainstorming 2026-06-11, delegadas)

1. **Escopo = "Tudo":** editar campos escalares + add/remove/reorder de agentes + editar tasks/integrações (arrays de string).
2. **Fonte da verdade da edição = client-side.** Edições mutam o **data-model A2UI local** no console; o agente **não re-raciocina por edição** (sem custo LLM, determinístico). Só o "Aprovar" volta ao backend, com o blueprint editado completo.
3. **Fidelidade = spec-compliant A2UI:** data-model **binding** (`$bind` + JSON-pointer), componentes editáveis ligados a paths, repeater por template, e um event de **ação canônico**. Reaproveitável por clientes externos.
4. **Sintaxe de binding:** valor de propriedade pode ser `{"$bind": "proposed_team/0/name"}` — JSON-pointer-like com `/` (sem `#`, relativo ao `surface.data`). Dentro de um Repeater, paths são **relativos ao item**.

### Escopo

- ✅ Binding no renderer; `TextInput`/`TextArea` editáveis; `Repeater` (instancia template por item de array; add/remove/reorder mutando o array); ações locais no cliente (`add_agent`, `remove_agent`, `move_agent`); ação remota `approve_team` (única que vai ao backend); endpoint `/discovery/action`; validação + persistência do blueprint editado; builder reescrito data-driven; estado "time aprovado" na página.
- ❌ Fora (futuro): "pedir ajuste" em NL (agente re-propõe); colaboração multiusuário; histórico/undo de versões; deploy do time.

---

## 2. Conceitos A2UI novos

### Data-model binding
- Propriedade com valor `{"$bind": "<path>"}` é resolvida contra `surface.data` na renderização.
- Componentes editáveis **escrevem de volta** no data-model local pelo mesmo path (set imutável).
- Path inexistente → **fallback visível** (texto de aviso), nunca quebra a tela.

### Componentes novos no catálogo
| Componente | Render (Ant Design) | Comportamento |
|---|---|---|
| `TextInput` | `Input` | `properties.bind` = path; onChange escreve no data-model |
| `TextArea` | `Input.TextArea` | idem, multilinha |
| `Repeater` | — | `properties.bind` = path de array; `properties.itemTemplate` = id do componente-raiz do template; instancia o template por item com paths relativos; `children` ignorado |
| `Button` (estendido) | `Button` | `properties.action = {"name": "...", "params": {...}}` → dispatch de ação |

### Ações
- **Locais (só cliente, mutam o data-model):** `add_agent` (apende um `AgentSpec` vazio-padrão), `remove_agent {index}`, `move_agent {index, dir:+1|-1}`, `add_item {path}` / `remove_item {path, index}` (para tasks/integrações).
- **Remota (vai ao backend):** `approve_team` — envia o data-model completo (blueprint editado).

---

## 3. Arquitetura

```
Backend (src/qwenpaw/, gated — pequeno):
  a2ui/schema.py        → helpers bind()/action() (properties já é dict[str,Any];
                          sem mudança de shape de mensagem)
  a2ui/builder.py       → build_blueprint_surface reescrito DATA-DRIVEN:
                          Repeater bound a proposed_team; campos TextInput/TextArea
                          bound; botões de ação local por card; botão Aprovar
  discovery/finalize.py → finalize_blueprint(session_id, data, out_dir):
                          valida dict contra TeamBlueprint, grava blueprint.json
                          + blueprint.md (reusa render md do runner)
  app/routers/discovery_stream.py → POST /discovery/action
                          {session_id, action, data} → approve_team chama
                          finalize, emite RUN_FINISHED (+ surface de confirmação);
                          ação desconhecida/data inválida → RUN_ERROR

Frontend (console/src/, não-gated — o grosso):
  components/a2ui/binding.ts   → isBind(), resolveBind(data, path),
                                 setPath(data, path, value) imutável,
                                 resolveProps(properties, data, basePath)
  components/a2ui/catalog.ts   → + TextInput, TextArea (controlados)
  components/a2ui/A2uiRenderer → binding-aware: resolve props contra o data;
                                 Repeater (instancia template por item, basePath
                                 relativo); dispatch de onAction(name, params)
  pages/Discovery/index.tsx    → o data-model editável vive aqui (useState);
                                 onAction local muta o data-model; approve_team
                                 → discoveryApi.action(...); estado "aprovado"
  api/modules/discovery.ts     → + action(sessionId, name, data) (POST
                                 /discovery/action, parseia o mesmo SSE)
```

O `LiveDiscoverySession`/`ScriptedDiscoverySession` **não mudam**: o blueprint emitido por elas continua igual; o que muda é como o builder o apresenta (editável) e o caminho de volta (`/discovery/action`).

## 4. Fluxo de dados

1. Turno final → builder emite a surface **data-driven**: `updateDataModel` carrega o blueprint; `updateComponents` traz Repeater + templates + inputs bound + botões.
2. Console renderiza resolvendo bindings contra o data-model **local** (inicializado da surface).
3. Edição de campo → `setPath` no data-model local (re-render). Ações estruturais (`add_agent`, `remove_agent`, `move_agent`, `add_item`, `remove_item`) mutam arrays localmente. Nada vai ao backend.
4. **Aprovar** → `POST /discovery/action {session_id, action:"approve_team", data:<data-model>}`.
5. Backend valida contra `TeamBlueprint`:
   - válido → grava `blueprint.json` + `blueprint.md`, emite `RUN_FINISHED` + surface de confirmação ("Time aprovado"); página troca para o estado aprovado.
   - inválido → `RUN_ERROR` com a mensagem Pydantic; página mostra o erro e **mantém** o data-model editável (nada se perde).

## 5. Erros (sem falha silenciosa)

- Binding a path inexistente → fallback visível no componente + warning no console.
- `approve_team` com data inválida → `RUN_ERROR` com a validação Pydantic; edição preservada.
- Ação desconhecida no endpoint → `RUN_ERROR` explícito.
- Sessão desconhecida/expirada no `approve_team` → ainda finaliza (o blueprint vem completo no payload; a sessão não é necessária para validar/persistir) — registrado como decisão: o payload é autossuficiente.

## 6. Testes

- **Backend (pytest, sem LLM):** `finalize_blueprint` válido/inválido; `/discovery/action` approve_team feliz (RUN_FINISHED + arquivos) e triste (RUN_ERROR); builder data-driven (Repeater bound + itemTemplate existe + botão Aprovar presente + bindings apontam para paths reais do blueprint).
- **Frontend (vitest):** binding (resolve/set, path inexistente → fallback); TextInput escreve de volta; Repeater instancia N itens e paths relativos; ações locais mutam o data-model (add/remove/move/add_item/remove_item); approve_team envia o data-model editado; RUN_ERROR mantém a edição.
- Regressão: testes existentes de a2ui/agui/discovery/página continuam verdes.

## 7. Critérios de aceite

1. A surface do blueprint renderiza **editável**: campos dos agentes em inputs, tasks/integrações como listas editáveis, botões add/remover/mover por agente.
2. Edições e mudanças estruturais acontecem **sem chamada de LLM/backend** e refletem na tela imediatamente.
3. "Aprovar time" envia o blueprint editado; backend valida, persiste `blueprint.json`/`.md` e confirma; dado inválido volta erro claro sem perder a edição.
4. Mensagens A2UI continuam spec-compliant (4 message-types intactos; binding/ação via `properties`).
5. Suítes backend+frontend verdes; guardian aprova a parte backend.

## 8. Execução em 2 fases (mesmo spec, planos/rodadas separadas)

- **Fase 1 — edição escalar + aprovar:** binding + TextInput/TextArea + builder data-driven (sem Repeater: cards ainda gerados por agente, mas com inputs bound por índice) + ações `approve_team` (remota) — backend finalize/endpoint completo. Entrega edição+aprovação ponta a ponta.
- **Fase 2 — estrutural:** Repeater + template + ações locais `add_agent/remove_agent/move_agent/add_item/remove_item` (tasks/integrações editáveis como arrays dinâmicos).

## 9. Camadas futuras
"Pedir ajuste" em NL por agente (volta ao `next_turn` com contexto da edição); undo/histórico; deploy do time a partir do blueprint aprovado.
