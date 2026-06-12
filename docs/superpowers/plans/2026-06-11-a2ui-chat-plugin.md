# Plugin de chat A2UI configurável — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Disponibilizar a UI generativa A2UI no chat principal via um plugin configurável: um agente chama a tool `render_ui(surface)` e o resultado é renderizado como UI Ant Design dentro da bolha de resposta.

**Architecture:** Motor genérico no core (`a2ui/` já existe + helper `surface.py`; `A2uiRenderer` exposto em `window.QwenPaw.host`). Plugin `type=general` em `plugins/bundle/a2ui-chat/` no molde de `plugins/bundle/cloudpaw/`: backend registra a tool `render_ui` (+ Fase B um router de ação) via `PluginApi`; bundle frontend registra `registerToolRender` montando `host.A2uiRenderer`. Config em `meta.tools[].config_fields` (interactivity). **Não toca nada do discovery** → sem conflito com a `main`.

**Tech Stack:** Python 3.11 + Pydantic v2 + FastAPI (backend, gated); React 18 + Ant Design 5 + Vite (lib build) + Vitest (console/plugin).

**Spec:** `docs/superpowers/specs/2026-06-11-a2ui-chat-plugin-design.md`

**Referências concretas (copiar/seguir):**
- `plugins/bundle/cloudpaw/plugin.json` (manifest general + entry backend/frontend), `cloudpaw/ui/vite.config.ts` (lib ES, externals react/react-dom), `cloudpaw/ui/src/index.ts` (uso de `window.QwenPaw.host` + `registerToolRender(pluginId, {tool: FC})`).
- `plugins/tool/qwen-image/plugin.json` (`meta.tools[].config_fields`).
- `src/qwenpaw/plugins/api.py`: `register_tool(tool_name, tool_func, description, icon, enabled=False)` (399), `register_http_router(router, *, prefix, tags=None)` (271).
- `src/qwenpaw/a2ui/schema.py` (Component + 4 mensagens), `console/src/components/a2ui/{A2uiRenderer.tsx,surfaceReducer.ts}`.

**Gates/conhecidos:** black 23.3.0 `--line-length=79` + flake8(79) + add-trailing-comma + mypy (pre-commit); pytest com `PYTHONPATH=<worktree>/src` e python de `orbe/.venv`; conferir `git diff --ignore-cr-at-eol --stat` (sem churn CRLF) ao editar arquivos existentes.

---

## File Structure

**FASE A (render read-only no chat):**
- Create: `src/qwenpaw/a2ui/surface.py` — helpers genéricos p/ montar surfaces (column/card/text/tag/button/list...).
- Create: `plugins/bundle/a2ui-chat/plugin.json` — manifest general (config interactivity).
- Create: `plugins/bundle/a2ui-chat/plugin.py` — registra a tool `render_ui`.
- Create: `plugins/bundle/a2ui-chat/a2ui_tool.py` — a função `render_ui` (valida surface, devolve).
- Modify: `console/src/plugins/hostExternals.ts` — expor `A2uiRenderer` (+ `applyA2uiMessage`/`emptySurface`) em `window.QwenPaw.host`.
- Create: `plugins/bundle/a2ui-chat/ui/{package.json,tsconfig.json,vite.config.ts}` — build (copiar de cloudpaw).
- Create: `plugins/bundle/a2ui-chat/ui/src/index.tsx` — `registerToolRender("a2ui-chat", {render_ui: A2uiToolRender})`.
- Tests: `tests/unit/a2ui/test_surface.py`, `tests/unit/plugins/test_a2ui_chat_plugin.py`, `console/src/plugins/hostExternals.test.ts` (ampliar/criar).

**FASE B (interatividade configurável):**
- Create: `plugins/bundle/a2ui-chat/action_router.py` — `POST /api/a2ui/action` (valida + ecoa data editado).
- Modify: `plugins/bundle/a2ui-chat/plugin.py` — `register_http_router(..., prefix="/a2ui")`.
- Modify: `plugins/bundle/a2ui-chat/ui/src/index.tsx` — ler config `interactivity`; quando `editable`, passar `onDataChange`/`onAction` ao `A2uiRenderer` e fazer `host.fetch("/a2ui/action", ...)`.
- Tests: `tests/unit/plugins/test_a2ui_action_router.py`; ampliar o teste do bundle.

---

# FASE A — render read-only no chat

### Task 1: helper `a2ui.surface` (core)

**Files:**
- Create: `src/qwenpaw/a2ui/surface.py`
- Modify: `src/qwenpaw/a2ui/__init__.py` (exportar)
- Test: `tests/unit/a2ui/test_surface.py`

Objetivo: dar ao agente uma forma ergonômica de montar uma surface válida (sem escrever o JSON cru da adjacency-list). Retorna a lista das 4 mensagens A2UI (igual ao builder do discovery, mas **genérico**).

- [ ] **Step 1: Write the failing test**

```python
# -*- coding: utf-8 -*-
# tests/unit/a2ui/test_surface.py
from qwenpaw.a2ui.surface import column, card, text, tag, surface
from qwenpaw.a2ui.schema import CreateSurface, UpdateComponents


def test_surface_builds_create_and_components():
    root = column("root", [text("t", "Olá"), tag("g", "novo")])
    msgs = surface("s1", root)
    assert isinstance(msgs[0], CreateSurface)
    assert isinstance(msgs[1], UpdateComponents)
    assert msgs[0].root == "root"
    ids = {c.id for c in msgs[1].components}
    assert {"root", "t", "g"} <= ids


def test_nested_children_are_flattened_with_refs():
    root = column("root", [card("c", [text("ct", "x")])])
    msgs = surface("s1", root)
    comps = {c.id: c for c in msgs[1].components}
    assert comps["root"].children == ["c"]
    assert comps["c"].children == ["ct"]
    assert comps["c"].type == "Card"


def test_text_and_tag_carry_text_property():
    msgs = surface("s1", column("root", [text("t", "abc"), tag("g", "z")]))
    comps = {c.id: c for c in msgs[1].components}
    assert comps["t"].properties["text"] == "abc"
    assert comps["g"].properties["text"] == "z"
```

- [ ] **Step 2: Run to verify FAIL**

Run: `PYTHONPATH=<worktree>/src <venv-python> -m pytest tests/unit/a2ui/test_surface.py -v`
Expected: FAIL — `ModuleNotFoundError: qwenpaw.a2ui.surface`

- [ ] **Step 3: Implement**

```python
# -*- coding: utf-8 -*-
# src/qwenpaw/a2ui/surface.py
"""Helpers genéricos para montar surfaces A2UI (adjacency-list).

Um ``Node`` é uma árvore aninhada; ``surface()`` a achata na lista de
componentes (filhos por id) e devolve as mensagens createSurface +
updateComponents [+ updateDataModel]. Não conhece nenhum domínio.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .schema import (
    A2UIMessage,
    Component,
    CreateSurface,
    UpdateComponents,
    UpdateDataModel,
)


@dataclass
class Node:
    id: str
    type: str
    properties: dict[str, Any] = field(default_factory=dict)
    children: list["Node"] = field(default_factory=list)


def column(cid: str, children: list[Node]) -> Node:
    return Node(cid, "Column", children=children)


def row(cid: str, children: list[Node]) -> Node:
    return Node(cid, "Row", children=children)


def card(cid: str, children: list[Node]) -> Node:
    return Node(cid, "Card", children=children)


def lst(cid: str, children: list[Node]) -> Node:
    return Node(cid, "List", children=children)


def text(cid: str, value: str) -> Node:
    return Node(cid, "Text", {"text": value})


def heading(cid: str, value: str) -> Node:
    return Node(cid, "Heading", {"text": value})


def tag(cid: str, value: str) -> Node:
    return Node(cid, "Tag", {"text": value})


def button(cid: str, label: str, action: dict[str, Any]) -> Node:
    return Node(cid, "Button", {"text": label, "action": action})


def _flatten(node: Node, out: list[Component]) -> None:
    out.append(
        Component(
            id=node.id,
            type=node.type,
            properties=dict(node.properties),
            children=[c.id for c in node.children],
        ),
    )
    for c in node.children:
        _flatten(c, out)


def surface(
    surface_id: str,
    root: Node,
    data: dict[str, Any] | None = None,
) -> list[A2UIMessage]:
    comps: list[Component] = []
    _flatten(root, comps)
    msgs: list[A2UIMessage] = [
        CreateSurface(surface_id=surface_id, root=root.id),
        UpdateComponents(surface_id=surface_id, components=comps),
    ]
    if data is not None:
        msgs.append(UpdateDataModel(surface_id=surface_id, data=data))
    return msgs
```

Append em `src/qwenpaw/a2ui/__init__.py`:

```python
from .surface import (  # noqa: E402
    Node,
    button,
    card,
    column,
    heading,
    lst,
    row,
    surface,
    tag,
    text,
)

__all__ += [
    "Node", "surface", "column", "row", "card", "lst",
    "text", "heading", "tag", "button",
]
```

- [ ] **Step 4: Run PASS** (`tests/unit/a2ui/test_surface.py` + suíte `tests/unit/a2ui`).
- [ ] **Step 5: Commit** — `feat(a2ui): helper generico surface() para montar adjacency-list`

---

### Task 2: tool `render_ui` (plugin backend)

**Files:**
- Create: `plugins/bundle/a2ui-chat/a2ui_tool.py`
- Test: `tests/unit/plugins/test_a2ui_chat_plugin.py`

A tool recebe uma surface (lista de mensagens A2UI como dict, ou um único dict), valida cada mensagem contra `a2ui.schema` e devolve a surface validada como **resultado de tool** (string JSON), que o frontend renderiza.

- [ ] **Step 1: Write the failing test**

```python
# -*- coding: utf-8 -*-
# tests/unit/plugins/test_a2ui_chat_plugin.py
import json

import pytest

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "a2ui_tool",
    ROOT / "plugins" / "bundle" / "a2ui-chat" / "a2ui_tool.py",
)
a2ui_tool = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a2ui_tool)

VALID = [
    {"messageType": "createSurface", "surfaceId": "s", "root": "root"},
    {
        "messageType": "updateComponents",
        "surfaceId": "s",
        "components": [
            {"id": "root", "type": "Column", "properties": {},
             "children": ["t"]},
            {"id": "t", "type": "Text", "properties": {"text": "oi"},
             "children": []},
        ],
    },
]


@pytest.mark.asyncio
async def test_render_ui_echoes_validated_surface():
    out = await a2ui_tool.render_ui(VALID)
    data = json.loads(out)
    assert data["surface"][0]["messageType"] == "createSurface"


@pytest.mark.asyncio
async def test_render_ui_rejects_invalid_surface():
    bad = [{"messageType": "createSurface"}]  # falta surfaceId/root
    with pytest.raises(Exception):
        await a2ui_tool.render_ui(bad)
```

- [ ] **Step 2: Run FAIL** (módulo não existe).

- [ ] **Step 3: Implement**

```python
# -*- coding: utf-8 -*-
# plugins/bundle/a2ui-chat/a2ui_tool.py
"""Tool `render_ui`: valida uma surface A2UI e a devolve para o chat."""
from __future__ import annotations

import json
from typing import Any

from pydantic import TypeAdapter

from qwenpaw.a2ui.schema import (
    CreateSurface,
    DeleteSurface,
    UpdateComponents,
    UpdateDataModel,
)

_MSG = {
    "createSurface": CreateSurface,
    "updateComponents": UpdateComponents,
    "updateDataModel": UpdateDataModel,
    "deleteSurface": DeleteSurface,
}


def _validate(msgs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for m in msgs:
        mt = m.get("messageType")
        model = _MSG.get(mt)
        if model is None:
            raise ValueError(f"messageType desconhecido: {mt!r}")
        out.append(model.model_validate(m).model_dump(by_alias=True))
    return out


async def render_ui(surface: Any) -> str:
    """Valida a surface A2UI (lista de mensagens ou única) e a devolve.

    O resultado (JSON string) é renderizado no chat pelo bundle do
    plugin via `registerToolRender`. Surface inválida levanta erro
    (visível como falha da tool — nunca engolido).
    """
    msgs = surface if isinstance(surface, list) else [surface]
    validated = _validate(msgs)
    return json.dumps({"surface": validated}, ensure_ascii=False)
```

- [ ] **Step 4: Run PASS** (2). Garantir `tests/unit/plugins/__init__.py` existe (criar vazio se preciso).
- [ ] **Step 5: Commit** — `feat(plugin): tool render_ui valida surface A2UI`

---

### Task 3: manifest + entrypoint do plugin (backend)

**Files:**
- Create: `plugins/bundle/a2ui-chat/plugin.json`
- Create: `plugins/bundle/a2ui-chat/plugin.py`
- Test: ampliar `tests/unit/plugins/test_a2ui_chat_plugin.py`

- [ ] **Step 1: Write the failing test**

```python
def test_plugin_registers_render_ui_tool():
    spec = importlib.util.spec_from_file_location(
        "a2ui_plugin",
        ROOT / "plugins" / "bundle" / "a2ui-chat" / "plugin.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    calls = []

    class FakeApi:
        def register_tool(self, **kw):
            calls.append(kw)

    mod.plugin.register(FakeApi())
    names = [c["tool_name"] for c in calls]
    assert "render_ui" in names
    rendered = [c for c in calls if c["tool_name"] == "render_ui"][0]
    assert callable(rendered["tool_func"])
```

E um teste que o manifest é JSON válido com os campos exigidos:

```python
def test_manifest_valid():
    mf = json.loads(
        (ROOT / "plugins" / "bundle" / "a2ui-chat"
         / "plugin.json").read_text("utf-8"),
    )
    assert mf["id"] == "a2ui-chat"
    assert mf["type"] == "general"
    assert mf["entry"]["backend"] == "plugin.py"
    assert mf["entry"]["frontend"] == "ui/dist/index.js"
    tool = mf["meta"]["tools"][0]
    assert tool["name"] == "render_ui"
    cfg = {f["name"] for f in tool.get("config_fields", [])}
    assert "interactivity" in cfg
```

- [ ] **Step 2: Run FAIL.**

- [ ] **Step 3: Implement**

`plugins/bundle/a2ui-chat/plugin.json`:

```json
{
  "id": "a2ui-chat",
  "name": "A2UI Chat",
  "version": "1.0.0",
  "type": "general",
  "description": "Renderiza UI generativa A2UI no chat. Agentes chamam a tool render_ui(surface) para desenhar cards, listas, inputs e botões na resposta.",
  "author": "QwenPaw Team",
  "entry": {
    "backend": "plugin.py",
    "frontend": "ui/dist/index.js"
  },
  "dependencies": [],
  "min_version": "1.1.6",
  "meta": {
    "tools": [
      {
        "name": "render_ui",
        "description": "Renderiza uma surface A2UI no chat",
        "icon": "🎨",
        "requires_config": false,
        "config_fields": [
          {
            "name": "interactivity",
            "label": "Interatividade",
            "type": "select",
            "required": false,
            "default": "read-only",
            "options": ["read-only", "editable"],
            "help": "read-only renderiza estático; editable habilita edição + envio ao agente."
          }
        ]
      }
    ]
  }
}
```

`plugins/bundle/a2ui-chat/plugin.py`:

```python
# -*- coding: utf-8 -*-
"""A2UI Chat plugin — registra a tool render_ui."""
from __future__ import annotations

import logging

from qwenpaw.plugins.api import PluginApi

from a2ui_tool import render_ui

logger = logging.getLogger(__name__)


class A2uiChatPlugin:
    def register(self, api: PluginApi) -> None:
        api.register_tool(
            tool_name="render_ui",
            tool_func=render_ui,
            description="Renderiza uma surface A2UI no chat",
            icon="🎨",
            enabled=False,
        )
        logger.info("✓ a2ui-chat plugin registrado")


plugin = A2uiChatPlugin()
```

> Nota: `from a2ui_tool import render_ui` funciona porque o loader de plugin executa `plugin.py` com o diretório do plugin no path (padrão dos plugins existentes; conferir com `plugins/tool/qwen-image`). Se o loader usar import por pacote, ajustar para import relativo conforme o padrão real observado nesse plugin.

- [ ] **Step 4: Run PASS** (todos os testes do plugin backend).
- [ ] **Step 5: Commit** — `feat(plugin): manifest + entrypoint a2ui-chat (config interactivity)`

---

### Task 4: expor `A2uiRenderer` no host SDK (console)

**Files:**
- Modify: `console/src/plugins/hostExternals.ts`
- Test: `console/src/plugins/hostExternals.test.ts` (criar se não existir)

Para o plugin ser fino (sem duplicar antd), o host expõe o renderer já buildado.

- [ ] **Step 1: Write the failing test**

```typescript
// console/src/plugins/hostExternals.test.ts
import { describe, it, expect } from "vitest";
import { installHostExternals } from "./hostExternals";

describe("host A2UI surface", () => {
  it("exposes A2uiRenderer + applyA2uiMessage + emptySurface on host", () => {
    installHostExternals();
    const host = (window as unknown as {
      QwenPaw: { host: Record<string, unknown> };
    }).QwenPaw.host;
    expect(typeof host.A2uiRenderer).toBe("function");
    expect(typeof host.applyA2uiMessage).toBe("function");
    expect(typeof host.emptySurface).toBe("function");
  });
});
```

> Conferir o nome real da função que monta `window.QwenPaw.host` em `hostExternals.ts` (vimos `window.QwenPaw.host = {...}` por volta da linha 234, dentro de uma função de install). Usar esse nome no import do teste; se a função tiver outro nome, ajustar.

- [ ] **Step 2: Run FAIL** (`cd console && npx vitest run src/plugins/hostExternals.test.ts`).

- [ ] **Step 3: Implement.** Em `hostExternals.ts`: adicionar à interface `HostExternals` e ao objeto `window.QwenPaw.host`:

```typescript
// imports no topo
import { A2uiRenderer } from "../components/a2ui/A2uiRenderer";
import {
  applyA2uiMessage,
  emptySurface,
} from "../components/a2ui/surfaceReducer";

// na interface HostExternals:
//   A2uiRenderer?: typeof A2uiRenderer;
//   applyA2uiMessage?: typeof applyA2uiMessage;
//   emptySurface?: typeof emptySurface;

// no objeto window.QwenPaw.host = { ...existentes,
//   A2uiRenderer, applyA2uiMessage, emptySurface,
// }
```

(Edição cirúrgica; não reescrever o arquivo — conferir `git diff --ignore-cr-at-eol --stat`.)

- [ ] **Step 4: Run PASS** + `cd console && npx tsc --noEmit -p tsconfig.app.json`.
- [ ] **Step 5: Commit** — `feat(console): expoe A2uiRenderer no window.QwenPaw.host`

---

### Task 5: bundle frontend do plugin (registerToolRender read-only)

**Files:**
- Create: `plugins/bundle/a2ui-chat/ui/package.json`, `tsconfig.json`, `vite.config.ts` (copiar de `plugins/bundle/cloudpaw/ui/`)
- Create: `plugins/bundle/a2ui-chat/ui/src/index.tsx`

Sem teste unitário próprio do bundle (a lógica de render já é coberta pelos testes de `components/a2ui`); validação por build + smoke. O `index.tsx` é a cola.

- [ ] **Step 1: Implement build config** — copiar `cloudpaw/ui/vite.config.ts`, `package.json`, `tsconfig.json` ajustando nome/entry. `vite.config.ts`:

```typescript
import { defineConfig } from "vite";

export default defineConfig({
  define: { "process.env.NODE_ENV": JSON.stringify("production") },
  build: {
    lib: {
      entry: "src/index.tsx",
      formats: ["es"],
      fileName: () => "index.js",
    },
    outDir: "dist",
    rollupOptions: { external: ["react", "react-dom"] },
  },
});
```

- [ ] **Step 2: Implement `ui/src/index.tsx`**

```tsx
// plugins/bundle/a2ui-chat/ui/src/index.tsx
// React/antd e o A2uiRenderer vêm do host (window.QwenPaw.host).
type AnyRec = Record<string, unknown>;

interface SurfaceMsg { messageType: string; surfaceId?: string }

function parseSurface(result: unknown): { root: string; components: AnyRec; data: AnyRec; surfaceId: string } | null {
  const QP = (window as AnyRec).QwenPaw as AnyRec;
  const host = QP.host as AnyRec;
  const apply = host.applyA2uiMessage as (s: AnyRec, m: SurfaceMsg) => AnyRec;
  const empty = host.emptySurface as (id: string) => AnyRec;
  let raw: AnyRec;
  try {
    raw = typeof result === "string" ? JSON.parse(result) : (result as AnyRec);
  } catch {
    return null;
  }
  const msgs = (raw.surface ?? raw) as SurfaceMsg[];
  if (!Array.isArray(msgs)) return null;
  let surf = empty("chat");
  for (const m of msgs) surf = apply(surf, m);
  return surf as never;
}

function A2uiToolRender({ result }: { result: unknown }) {
  const QP = (window as AnyRec).QwenPaw as AnyRec;
  const host = QP.host as AnyRec;
  const React = host.React as typeof import("react");
  const Renderer = host.A2uiRenderer as React.FC<{ surface: AnyRec }>;
  const surf = parseSurface(result);
  if (!surf || !Renderer) {
    return React.createElement(
      "div",
      { style: { color: "#cf1322" } },
      "A2UI: surface inválida",
    );
  }
  return React.createElement(Renderer, { surface: surf });
}

function install() {
  const QP = (window as AnyRec).QwenPaw as AnyRec | undefined;
  if (!QP) return;
  const reg = QP.registerToolRender as
    | ((id: string, r: AnyRec) => void)
    | undefined;
  reg?.("a2ui-chat", { render_ui: A2uiToolRender });
}

install();
```

- [ ] **Step 3: Build** — `cd plugins/bundle/a2ui-chat/ui && npm install && npm run build` → gera `dist/index.js`.
Expected: build OK, `dist/index.js` existe.

- [ ] **Step 4: Smoke manual** — instalar/ativar o plugin no console; num chat, fazer um agente chamar `render_ui` com uma surface simples (ex.: `surface("s", column("root",[heading("h","Olá"), tag("g","novo")]))`); ver os componentes Ant Design na bolha.
Expected: heading + tag renderizados.

- [ ] **Step 5: Commit** — `feat(plugin): bundle frontend a2ui-chat (registerToolRender read-only)`

---

### Task 6: fechamento Fase A

- [ ] Backend: `pytest tests/unit/a2ui tests/unit/plugins -q` (PYTHONPATH worktree) → PASS.
- [ ] Console: `npx vitest run src/plugins/hostExternals.test.ts src/components/a2ui` + `tsc --noEmit` + `eslint` → limpo.
- [ ] Gates pinados (black/flake8/add-trailing-comma/mypy) nos arquivos backend; `git diff --ignore-cr-at-eol --stat` sem churn CRLF.
- [ ] Commit final da Fase A.

---

# FASE B — interatividade configurável

### Task 7: endpoint de ação do plugin (backend)

**Files:**
- Create: `plugins/bundle/a2ui-chat/action_router.py`
- Modify: `plugins/bundle/a2ui-chat/plugin.py`
- Test: `tests/unit/plugins/test_a2ui_action_router.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/plugins/test_a2ui_action_router.py
import importlib.util
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "a2ui_action_router",
    ROOT / "plugins" / "bundle" / "a2ui-chat" / "action_router.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def _client():
    app = FastAPI()
    app.include_router(mod.router, prefix="/api/a2ui")
    return TestClient(app)


def test_action_echoes_data():
    r = _client().post(
        "/api/a2ui/action",
        json={"session_id": "s1", "action": "submit", "data": {"k": 1}},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["data"] == {"k": 1}


def test_action_rejects_empty_action():
    r = _client().post(
        "/api/a2ui/action",
        json={"session_id": "s1", "action": "", "data": {}},
    )
    assert r.status_code == 400
```

- [ ] **Step 2: Run FAIL.**

- [ ] **Step 3: Implement**

```python
# -*- coding: utf-8 -*-
# plugins/bundle/a2ui-chat/action_router.py
"""Endpoint de ação do plugin a2ui-chat (action-back da Fase B)."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class A2uiAction(BaseModel):
    session_id: str
    action: str
    data: dict[str, Any] = {}


@router.post("/action")
async def a2ui_action(req: A2uiAction) -> dict[str, Any]:
    if not req.action:
        raise HTTPException(status_code=400, detail="action vazio")
    # Neste ciclo a ação ecoa o data-model editado (autossuficiente). O
    # consumo pelo agente (próximo turno) é responsabilidade da feature.
    return {"ok": True, "action": req.action, "data": req.data}
```

E em `plugin.py`, dentro de `register`:

```python
        from action_router import router as a2ui_action_router

        api.register_http_router(a2ui_action_router, prefix="/a2ui")
```

- [ ] **Step 4: Run PASS** (2) + o teste de registro (Task 3) agora confere que `register_http_router` foi chamado (estender o `FakeApi` com `register_http_router` coletando `prefix`).
- [ ] **Step 5: Commit** — `feat(plugin): POST /api/a2ui/action (action-back editavel)`

---

### Task 8: bundle editável (interactivity)

**Files:**
- Modify: `plugins/bundle/a2ui-chat/ui/src/index.tsx`

- [ ] **Step 1: Implement.** Tornar o render reativo à config e ligar edição:

```tsx
function A2uiToolRender({ result }: { result: unknown }) {
  const QP = (window as AnyRec).QwenPaw as AnyRec;
  const host = QP.host as AnyRec;
  const React = host.React as typeof import("react");
  const Renderer = host.A2uiRenderer as React.FC<AnyRec>;
  const cfg = (QP.config as AnyRec | undefined)?.["a2ui-chat"] as AnyRec | undefined;
  const editable = cfg?.interactivity === "editable";

  const initial = parseSurface(result);
  const [data, setData] = React.useState<AnyRec>(
    (initial?.data as AnyRec) ?? {},
  );
  if (!initial || !Renderer) {
    return React.createElement("div", { style: { color: "#cf1322" } }, "A2UI: surface inválida");
  }
  const props: AnyRec = { surface: initial, data };
  if (editable) {
    props.onDataChange = setData;
    props.onAction = async (name: string, params?: AnyRec) => {
      const fetcher = host.fetch as (p: string, init?: AnyRec) => Promise<Response>;
      const sid = (host.getCurrentSessionId as () => string | null)?.() ?? "chat";
      await fetcher("/a2ui/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sid, action: name, data, params }),
      });
    };
  }
  return React.createElement(Renderer, props);
}
```

> Verificar como a config do plugin chega ao frontend (ex.: `window.QwenPaw.config[pluginId]` vs um endpoint). Se não houver objeto de config global, ler via `host.fetch` do endpoint de config do plugin e default `read-only`. Ajustar `cfg` à fonte real (não inventar) — fallback seguro: `read-only`.

- [ ] **Step 2: Build** — `cd plugins/bundle/a2ui-chat/ui && npm run build` → OK.
- [ ] **Step 3: Smoke** — config `editable`: editar um input na surface do chat e clicar um botão de ação → `POST /api/a2ui/action` recebido com o data editado; `read-only`: inputs inertes.
- [ ] **Step 4: Commit** — `feat(plugin): bundle editavel + action-back via host.fetch`

---

### Task 9: fechamento Fase B

- [ ] `pytest tests/unit/a2ui tests/unit/plugins -q` (worktree) → PASS.
- [ ] Console: vitest + tsc + eslint limpos; build do bundle OK.
- [ ] Gates pinados backend; CRLF check.
- [ ] Commit final.

---

## Self-review

**Cobertura do spec:** §1/§3 motor core + plugin fino + tool render → Tasks 1–5; §4 fluxo (render_ui→toolRender→A2uiRenderer; action-back) → Tasks 2,5,7,8; §5 config interactivity → Tasks 3 (manifest) + 8 (bundle lê config); §6 erros (surface inválida, fallback, host ausente, fetch falho) → Tasks 2 (raise), 5 (fallback/host-guard), 8 (fetch); §7 testes → todas as tasks; §8 fases → A=Tasks1–6, B=Tasks7–9; §2 sem conflito (nada de discovery/locales/routes tocado) → confirmado pela File Structure. ✔

**Placeholders:** as notas "conferir o nome real de X / como a config chega" são **verificações contra código existente** (hostExternals install fn, fonte de config do plugin, loader de import do plugin) com fallback explícito definido — não comportamento inventado. Sem TBD de design.

**Consistência:** `surface()/column()/text()/tag()/heading()/card()/button()` idênticos entre Task 1 e o smoke da Task 5; `render_ui(surface)->str{surface:[...]}` igual em Tasks 2,3,5; `registerToolRender("a2ui-chat",{render_ui:FC})` igual em Tasks 5,8; `host.A2uiRenderer/applyA2uiMessage/emptySurface` definidos na Task 4 e usados nas Tasks 5,8; endpoint `POST /api/a2ui/action {session_id,action,data}` igual em Tasks 7,8.

**Nota de escopo:** o consumo do data editado pelo agente (re-injetar no turno) fica fora — o endpoint ecoa o data (autossuficiente); fechar esse laço é camada futura, como no spec §10.
