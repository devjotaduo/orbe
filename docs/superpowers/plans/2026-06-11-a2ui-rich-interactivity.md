# Interatividade A2UI rica — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tornar a surface A2UI do blueprint editável (campos, agentes, tasks/integrações) com edição client-side e ação `approve_team` que valida e persiste o blueprint final no backend.

**Architecture:** Data-model binding spec-compliant (`{"$bind": "<json-pointer>"}` resolvido contra `surface.data`); componentes editáveis (`TextInput`/`TextArea`) e `Repeater` no catálogo; ações locais mutam o data-model no console; só `approve_team` vai ao backend (`POST /discovery/action` → `finalize_blueprint` valida contra `TeamBlueprint` e grava `blueprint.json`/`.md`). Builder reescrito data-driven. Sessões (`Live`/`Scripted`) não mudam.

**Tech Stack:** Python 3.11 + Pydantic v2 + FastAPI (backend, gate guardian); React 18 + TS + Ant Design 5 + Vitest (console).

**Spec:** `docs/superpowers/specs/2026-06-11-a2ui-rich-interactivity-design.md`

**Gates/conhecidos:** black 23.3.0 `--line-length=79` + flake8(79) + add-trailing-comma + mypy via pre-commit; pytest com `PYTHONPATH=<worktree>/src` e python de `orbe/.venv`; cuidado com churn CRLF (conferir `git diff --ignore-cr-at-eol --stat`); `_blueprint_to_markdown` já existe em `src/qwenpaw/discovery/tools.py:36` (reusar).

---

## File Structure

**FASE 1 (edição escalar + aprovar):**
- Create: `src/qwenpaw/discovery/finalize.py` — valida dict editado + persiste json/md.
- Modify: `src/qwenpaw/app/routers/discovery_stream.py` — + `POST /discovery/action`.
- Modify: `src/qwenpaw/a2ui/builder.py` — cards com `TextInput`/`TextArea` bound + botão Aprovar.
- Create: `console/src/components/a2ui/binding.ts` — resolve/set de paths + resolveProps.
- Modify: `console/src/components/a2ui/catalog.ts` — + TextInput/TextArea/Button-com-ação.
- Modify: `console/src/components/a2ui/A2uiRenderer.tsx` — binding-aware + onDataChange/onAction.
- Modify: `console/src/api/modules/discovery.ts` — + `action(sessionId, name, data, onEvent)`.
- Modify: `console/src/pages/Discovery/index.tsx` — data-model editável + estado aprovado.
- Tests: `tests/unit/discovery/test_finalize.py`, `tests/unit/app/routers/test_discovery_action.py`, ampliar `tests/unit/a2ui/test_builder.py`, `console/src/components/a2ui/binding.test.ts`, ampliar `A2uiRenderer.test.tsx` e `discovery.test.ts`.

**FASE 2 (estrutural):**
- Modify: `console/src/components/a2ui/A2uiRenderer.tsx` — `Repeater` (template por item, basePath relativo).
- Modify: `console/src/pages/Discovery/index.tsx` — ações locais `add_agent/remove_agent/move_agent/add_item/remove_item`.
- Modify: `src/qwenpaw/a2ui/builder.py` — emite `Repeater` + template + botões estruturais; tasks/integrações como listas editáveis.
- Tests: ampliar `A2uiRenderer.test.tsx` (repeater), `index.test.tsx` (ações estruturais), `test_builder.py` (repeater/template).

---

# FASE 1 — edição escalar + aprovar

### Task 1: `finalize_blueprint` (backend)

**Files:**
- Create: `src/qwenpaw/discovery/finalize.py`
- Test: `tests/unit/discovery/test_finalize.py`

- [ ] **Step 1: Write the failing test**

```python
# -*- coding: utf-8 -*-
# tests/unit/discovery/test_finalize.py
import json

import pytest
from pydantic import ValidationError

from qwenpaw.discovery.finalize import finalize_blueprint

VALID = {
    "company_profile": {"segment": "ecommerce", "name": "Loja X"},
    "process_map": [],
    "detected_integrations": [{"kind": "messaging", "name": "WhatsApp"}],
    "proposed_team": [
        {
            "name": "Atendente",
            "role": "atendimento",
            "objective": "responder clientes",
            "tasks": ["responder"],
            "tools_integrations": ["mcp:evolution-whatsapp"],
            "talks_to": [],
        },
    ],
    "roadmap": [],
    "open_questions": [],
}


def test_valid_blueprint_persists_json_and_md(tmp_path):
    bp = finalize_blueprint(VALID, tmp_path)
    assert bp.company_profile.segment == "ecommerce"
    data = json.loads((tmp_path / "blueprint.json").read_text("utf-8"))
    assert data["proposed_team"][0]["name"] == "Atendente"
    md = (tmp_path / "blueprint.md").read_text("utf-8")
    assert "Atendente" in md


def test_invalid_blueprint_raises_and_writes_nothing(tmp_path):
    bad = dict(VALID, proposed_team=[{"name": "sem-campos"}])
    with pytest.raises(ValidationError):
        finalize_blueprint(bad, tmp_path)
    assert not (tmp_path / "blueprint.json").exists()
```

> Atenção ao shape real de `Integration`/`AgentSpec` em `src/qwenpaw/discovery/state.py` (Tasks 1–3 do cérebro). Se `Integration` usar outro campo que `kind`, ajustar `VALID` ao schema real — o teste deve usar o schema verdadeiro.

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=<worktree>/src <venv-python> -m pytest tests/unit/discovery/test_finalize.py -v`
Expected: FAIL — `ModuleNotFoundError: qwenpaw.discovery.finalize`

- [ ] **Step 3: Write minimal implementation**

```python
# -*- coding: utf-8 -*-
# src/qwenpaw/discovery/finalize.py
"""Valida e persiste um blueprint editado pelo usuário (approve_team)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .state import TeamBlueprint
from .tools import _blueprint_to_markdown


def finalize_blueprint(data: dict[str, Any], out_dir: Path) -> TeamBlueprint:
    """Valida ``data`` contra TeamBlueprint e grava blueprint.json/.md.

    Levanta ``pydantic.ValidationError`` se inválido (nada é gravado).
    """
    bp = TeamBlueprint.model_validate(data)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "blueprint.json").write_text(
        bp.model_dump_json(indent=2),
        encoding="utf-8",
    )
    (out_dir / "blueprint.md").write_text(
        _blueprint_to_markdown(bp),
        encoding="utf-8",
    )
    return bp
```

- [ ] **Step 4: Run test to verify it passes** — mesmo comando, Expected: PASS (2).

- [ ] **Step 5: Commit** — `git add src/qwenpaw/discovery/finalize.py tests/unit/discovery/test_finalize.py && git commit -m "feat(discovery): finalize_blueprint valida+persiste blueprint editado"`

---

### Task 2: `POST /discovery/action` (backend)

**Files:**
- Modify: `src/qwenpaw/app/routers/discovery_stream.py`
- Test: `tests/unit/app/routers/test_discovery_action.py`

- [ ] **Step 1: Write the failing test**

```python
# -*- coding: utf-8 -*-
# tests/unit/app/routers/test_discovery_action.py
import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from qwenpaw.app.routers import discovery_stream as ds

VALID = {  # mesmo shape do test_finalize (ajustar ao schema real)
    "company_profile": {"segment": "ecommerce", "name": "Loja X"},
    "process_map": [],
    "detected_integrations": [],
    "proposed_team": [
        {
            "name": "Atendente",
            "role": "atendimento",
            "objective": "responder clientes",
            "tasks": [],
            "tools_integrations": [],
            "talks_to": [],
        },
    ],
    "roadmap": [],
    "open_questions": [],
}


def _events(text):
    return [
        json.loads(line[len("data: "):])
        for line in text.splitlines()
        if line.startswith("data: ")
    ]


def _client():
    app = FastAPI()
    app.include_router(ds.router)
    return TestClient(app)


def test_approve_team_finalizes_and_finishes(tmp_path, monkeypatch):
    monkeypatch.setattr(ds, "_action_out_dir", lambda sid: tmp_path / sid)
    client = _client()
    r = client.post(
        "/discovery/action",
        json={"session_id": "s1", "action": "approve_team", "data": VALID},
    )
    assert r.status_code == 200
    types = [e["type"] for e in _events(r.text)]
    assert types[0] == "RUN_STARTED"
    assert types[-1] == "RUN_FINISHED"
    assert "RUN_ERROR" not in types
    assert (tmp_path / "s1" / "blueprint.json").exists()


def test_invalid_data_emits_run_error(tmp_path, monkeypatch):
    monkeypatch.setattr(ds, "_action_out_dir", lambda sid: tmp_path / sid)
    client = _client()
    r = client.post(
        "/discovery/action",
        json={
            "session_id": "s2",
            "action": "approve_team",
            "data": {"proposed_team": [{"name": "x"}]},
        },
    )
    types = [e["type"] for e in _events(r.text)]
    assert "RUN_ERROR" in types
    assert not (tmp_path / "s2" / "blueprint.json").exists()


def test_unknown_action_emits_run_error():
    client = _client()
    r = client.post(
        "/discovery/action",
        json={"session_id": "s3", "action": "fly_to_moon", "data": {}},
    )
    assert any(e["type"] == "RUN_ERROR" for e in _events(r.text))
```

- [ ] **Step 2: Run to verify FAIL** (endpoint inexistente → 404/AssertionError).

- [ ] **Step 3: Implement** — acrescentar ao `discovery_stream.py` (NÃO tocar no endpoint existente; manter endings/formato — diff cirúrgico):

```python
import os  # junto aos imports existentes

from qwenpaw.discovery.finalize import finalize_blueprint  # idem


class DiscoveryActionRequest(BaseModel):
    session_id: str
    action: str
    data: dict[str, Any] = {}


def _action_out_dir(session_id: str) -> Path:
    base = Path(
        os.environ.get("QWENPAW_DISCOVERY_OUT", "discovery_sessions"),
    )
    return base / session_id


@router.post("/discovery/action")
async def discovery_action(req: DiscoveryActionRequest) -> StreamingResponse:
    thread_id, run_id = req.session_id, uuid.uuid4().hex

    async def generate():
        yield sse(RunStartedEvent(thread_id=thread_id, run_id=run_id))
        try:
            if req.action != "approve_team":
                raise ValueError(f"ação desconhecida: {req.action!r}")
            bp = finalize_blueprint(req.data, _action_out_dir(req.session_id))
            for ev in text_message_events(
                uuid.uuid4().hex,
                f"Time aprovado: {len(bp.proposed_team)} agente(s). "
                "Blueprint gravado.",
            ):
                yield sse(ev)
            _sessions.pop(req.session_id, None)
        except Exception as exc:  # noqa: BLE001 — sempre vira RUN_ERROR
            logger.exception("discovery action failed")
            yield sse(RunErrorEvent(message=str(exc)))
        finally:
            yield sse(RunFinishedEvent(thread_id=thread_id, run_id=run_id))

    return StreamingResponse(generate(), media_type="text/event-stream")
```

(`Path` e `Any` já podem estar importados; conferir imports do arquivo.)

- [ ] **Step 4: Run to verify PASS** (3 testes) + regressão `test_discovery_stream_router.py`.

- [ ] **Step 5: Commit** — `feat(app): POST /discovery/action (approve_team -> finalize + SSE)`

---

### Task 3: Builder data-driven (Fase 1: inputs bound por índice + Aprovar)

**Files:**
- Modify: `src/qwenpaw/a2ui/builder.py`
- Test: ampliar `tests/unit/a2ui/test_builder.py`

- [ ] **Step 1: Failing tests (acrescentar)**

```python
def test_team_member_fields_are_bound_inputs():
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    comps = {c.id: c for c in msgs[1].components}
    name_inputs = [
        c for c in msgs[1].components
        if c.type == "TextInput"
        and c.properties.get("bind") == "proposed_team/0/name"
    ]
    assert len(name_inputs) == 1
    objective = [
        c for c in msgs[1].components
        if c.type == "TextArea"
        and c.properties.get("bind") == "proposed_team/0/objective"
    ]
    assert len(objective) == 1


def test_approve_button_present_with_action():
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    buttons = [c for c in msgs[1].components if c.type == "Button"]
    assert any(
        c.properties.get("action", {}).get("name") == "approve_team"
        for c in buttons
    )
```

- [ ] **Step 2: FAIL** (sem TextInput/Button hoje).

- [ ] **Step 3: Implement** — no card de cada membro `i`, substituir o Heading/Text estáticos de nome/role/objective por:

```python
def _input(cid: str, bind: str, label: str) -> Component:
    return Component(
        id=cid,
        type="TextInput",
        properties={"bind": bind, "label": label},
    )


def _textarea(cid: str, bind: str, label: str) -> Component:
    return Component(
        id=cid,
        type="TextArea",
        properties={"bind": bind, "label": label},
    )
```

No loop de membros: `_input(f"card-{i}-name", f"proposed_team/{i}/name", "Nome")`, `_input(f"card-{i}-role", f"proposed_team/{i}/role", "Papel")`, `_textarea(f"card-{i}-objective", f"proposed_team/{i}/objective", "Objetivo")` como filhos do card (tags continuam read-only na Fase 1). Ao final, antes do root, botão:

```python
comps.append(
    Component(
        id="approve-btn",
        type="Button",
        properties={
            "text": "Aprovar time",
            "variant": "primary",
            "action": {"name": "approve_team"},
        },
    ),
)
root_children.append("approve-btn")
```

Manter os testes antigos passando (os que checam Heading do título, Tags de integrações e datamodel cru) — ajustar apenas os que assertavam nome como Heading/Text (agora é TextInput bound).

- [ ] **Step 4: PASS** em `tests/unit/a2ui/` inteiro.
- [ ] **Step 5: Commit** — `feat(a2ui): builder data-driven (inputs bound + acao approve_team)`

---

### Task 4: `binding.ts` (console)

**Files:**
- Create: `console/src/components/a2ui/binding.ts`
- Test: `console/src/components/a2ui/binding.test.ts`

- [ ] **Step 1: Failing test**

```typescript
import { describe, it, expect } from "vitest";
import { isBind, resolveBind, setPath, resolveProps } from "./binding";

const DATA = { proposed_team: [{ name: "Atendente", tasks: ["a", "b"] }] };

describe("binding", () => {
  it("isBind detects $bind objects", () => {
    expect(isBind({ $bind: "x" })).toBe(true);
    expect(isBind("x")).toBe(false);
    expect(isBind(null)).toBe(false);
  });

  it("resolveBind walks json-pointer-like paths", () => {
    expect(resolveBind(DATA, "proposed_team/0/name")).toBe("Atendente");
    expect(resolveBind(DATA, "proposed_team/0/tasks/1")).toBe("b");
  });

  it("resolveBind returns undefined on missing path", () => {
    expect(resolveBind(DATA, "proposed_team/9/name")).toBeUndefined();
  });

  it("setPath writes immutably", () => {
    const next = setPath(DATA, "proposed_team/0/name", "Novo");
    expect(next.proposed_team[0].name).toBe("Novo");
    expect(DATA.proposed_team[0].name).toBe("Atendente");
    expect(next).not.toBe(DATA);
  });

  it("resolveProps resolves $bind values with basePath", () => {
    const props = { label: "Nome", value: { $bind: "name" } };
    const out = resolveProps(props, DATA, "proposed_team/0");
    expect(out.value).toBe("Atendente");
    expect(out.label).toBe("Nome");
  });
});
```

- [ ] **Step 2: FAIL.**

- [ ] **Step 3: Implement**

```typescript
// console/src/components/a2ui/binding.ts
export interface BindRef {
  $bind: string;
}

export function isBind(v: unknown): v is BindRef {
  return (
    typeof v === "object" &&
    v !== null &&
    typeof (v as BindRef).$bind === "string"
  );
}

function joinPath(basePath: string | undefined, path: string): string {
  return basePath ? `${basePath}/${path}` : path;
}

export function resolveBind(data: unknown, path: string): unknown {
  let cur: unknown = data;
  for (const seg of path.split("/")) {
    if (cur === null || typeof cur !== "object") return undefined;
    cur = (cur as Record<string, unknown>)[seg];
  }
  return cur;
}

/** Immutable deep-set along a json-pointer-like path. */
export function setPath<T>(data: T, path: string, value: unknown): T {
  const segs = path.split("/");
  function rec(node: unknown, i: number): unknown {
    if (i === segs.length) return value;
    const seg = segs[i];
    if (Array.isArray(node)) {
      const idx = Number(seg);
      const copy = node.slice();
      copy[idx] = rec(node[idx], i + 1);
      return copy;
    }
    const obj = (node ?? {}) as Record<string, unknown>;
    return { ...obj, [seg]: rec(obj[seg], i + 1) };
  }
  return rec(data, 0) as T;
}

/** Resolve every {$bind} in properties against data (paths relative to basePath). */
export function resolveProps(
  properties: Record<string, unknown>,
  data: unknown,
  basePath?: string,
): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(properties)) {
    out[k] = isBind(v) ? resolveBind(data, joinPath(basePath, v.$bind)) : v;
  }
  return out;
}
```

- [ ] **Step 4: PASS.**
- [ ] **Step 5: Commit** — `feat(console): a2ui data-model binding (resolve/set/resolveProps)`

---

### Task 5: Renderer + catálogo binding-aware (console)

**Files:**
- Modify: `console/src/components/a2ui/catalog.ts`, `A2uiRenderer.tsx`
- Test: ampliar `console/src/components/a2ui/A2uiRenderer.test.tsx`

Interface nova do renderer (props):

```typescript
export interface A2uiRendererProps {
  surface: A2uiSurface;
  data?: Record<string, unknown>;          // default: surface.data
  onDataChange?: (next: Record<string, unknown>) => void;
  onAction?: (name: string, params?: Record<string, unknown>) => void;
}
```

- [ ] **Step 1: Failing tests (acrescentar)**

```tsx
const EDIT_MSGS: A2uiMessage[] = [
  { messageType: "createSurface", surfaceId: "bp", root: "root" },
  {
    messageType: "updateComponents",
    surfaceId: "bp",
    components: [
      { id: "root", type: "Column", properties: {}, children: ["n", "ok"] },
      {
        id: "n",
        type: "TextInput",
        properties: { bind: "proposed_team/0/name", label: "Nome" },
        children: [],
      },
      {
        id: "ok",
        type: "Button",
        properties: { text: "Aprovar", action: { name: "approve_team" } },
        children: [],
      },
    ],
  },
  {
    messageType: "updateDataModel",
    surfaceId: "bp",
    data: { proposed_team: [{ name: "Atendente" }] },
  },
];

it("TextInput renders bound value and writes back via onDataChange", () => {
  let surf = emptySurface("bp");
  for (const m of EDIT_MSGS) surf = applyA2uiMessage(surf, m);
  const onDataChange = vi.fn();
  render(
    <A2uiRenderer surface={surf} onDataChange={onDataChange} />,
  );
  const input = screen.getByDisplayValue("Atendente");
  fireEvent.change(input, { target: { value: "Vendedor" } });
  expect(onDataChange).toHaveBeenCalled();
  const next = onDataChange.mock.calls[0][0];
  expect(next.proposed_team[0].name).toBe("Vendedor");
});

it("Button with action dispatches onAction", () => {
  let surf = emptySurface("bp");
  for (const m of EDIT_MSGS) surf = applyA2uiMessage(surf, m);
  const onAction = vi.fn();
  render(<A2uiRenderer surface={surf} onAction={onAction} />);
  fireEvent.click(screen.getByText("Aprovar"));
  expect(onAction).toHaveBeenCalledWith("approve_team", undefined);
});
```

- [ ] **Step 2: FAIL.**

- [ ] **Step 3: Implement.** No `A2uiRenderer`: aceitar as novas props (`data` default `surface.data`); criar um contexto interno de render `{data, basePath, onDataChange, onAction}` passado na recursão; antes de renderizar um nó, `const resolved = resolveProps(node.properties, data, basePath)`. Tipos editáveis e botão são tratados no renderer (não no catálogo estático), porque precisam dos callbacks:

```tsx
if (node.type === "TextInput" || node.type === "TextArea") {
  const bindPath = joinBase(basePath, String(node.properties.bind ?? ""));
  const value = String(resolveBind(data, bindPath) ?? "");
  const Cmp = node.type === "TextInput" ? Input : Input.TextArea;
  return (
    <div className={styles.field}>
      {resolved.label ? (
        <Typography.Text type="secondary">{String(resolved.label)}</Typography.Text>
      ) : null}
      <Cmp
        value={value}
        aria-label={String(resolved.label ?? bindPath)}
        onChange={(e) =>
          onDataChange?.(setPath(data, bindPath, e.target.value))
        }
      />
    </div>
  );
}
if (node.type === "Button" && resolved.action) {
  const action = resolved.action as { name: string; params?: Record<string, unknown> };
  return (
    <Button
      type={resolved.variant === "primary" ? "primary" : "default"}
      onClick={() => onAction?.(action.name, action.params)}
    >
      {String(resolved.text ?? "")}
    </Button>
  );
}
```

Demais tipos seguem pelo catálogo com `resolved` no lugar de `node.properties`. (`joinBase(base, p) = base ? `${base}/${p}` : p` — exportar de `binding.ts` se preferir.)

- [ ] **Step 4: PASS** em todos os testes do renderer (antigos + novos).
- [ ] **Step 5: Commit** — `feat(console): renderer A2UI binding-aware (inputs editaveis + acoes)`

---

### Task 6: `discoveryApi.action` + página (console)

**Files:**
- Modify: `console/src/api/modules/discovery.ts` (+ teste), `console/src/pages/Discovery/index.tsx` (+ teste)

- [ ] **Step 1: Failing tests.** Em `discovery.test.ts`:

```typescript
it("action POSTs to /api/discovery/action and streams events", async () => {
  (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(
    streamResponse(['data: {"type":"RUN_FINISHED","threadId":"t","runId":"r"}\n\n']),
  );
  const seen: string[] = [];
  await discoveryApi.action("s1", "approve_team", { a: 1 }, (ev) =>
    seen.push(ev.type),
  );
  const [url, init] = (fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[0];
  expect(url).toBe("/api/discovery/action");
  expect(JSON.parse(init.body)).toEqual({
    session_id: "s1",
    action: "approve_team",
    data: { a: 1 },
  });
  expect(seen).toEqual(["RUN_FINISHED"]);
});
```

Em `index.test.tsx` (com `mockStreamTurn` entregando a surface editável de `EDIT_MSGS`-like): editar o input do nome e clicar "Aprovar time" → `discoveryApi.action` chamado com o data-model contendo o nome editado; sucesso → página mostra estado aprovado; `RUN_ERROR` → erro visível e inputs preservados.

- [ ] **Step 2: FAIL.**

- [ ] **Step 3: Implement.** Em `discovery.ts`, extrair o loop de leitura SSE de `streamTurn` para um helper interno `streamPost(path, body, onEvent, signal)` e:

```typescript
async action(
  sessionId: string,
  name: string,
  data: Record<string, unknown>,
  onEvent: (ev: AguiEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  return streamPost(
    "/discovery/action",
    { session_id: sessionId, action: name, data },
    onEvent,
    signal,
  );
}
```

Na página: novo estado `dataModel` (inicializado de `surface.data` quando a surface chega) e `approved`; `<A2uiRenderer surface={surface} data={dataModel} onDataChange={setDataModel} onAction={handleAction}/>`; `handleAction("approve_team")` → `discoveryApi.action(sessionId, "approve_team", dataModel, onEvent)`; `RUN_FINISHED` sem erro → `setApproved(true)` (card de confirmação); `RUN_ERROR` → alert de erro, edição preservada.

- [ ] **Step 4: PASS** + `tsc --noEmit` + eslint nos arquivos tocados.
- [ ] **Step 5: Commit** — `feat(console): edicao client-side + approve_team na pagina Discovery`

---

# FASE 2 — estrutural (Repeater + ações locais)

### Task 7: `Repeater` no renderer

**Files:**
- Modify: `console/src/components/a2ui/A2uiRenderer.tsx`
- Test: ampliar `A2uiRenderer.test.tsx`

- [ ] **Step 1: Failing test**

```tsx
const REPEAT_MSGS: A2uiMessage[] = [
  { messageType: "createSurface", surfaceId: "bp", root: "root" },
  {
    messageType: "updateComponents",
    surfaceId: "bp",
    components: [
      { id: "root", type: "Column", properties: {}, children: ["rep"] },
      {
        id: "rep",
        type: "Repeater",
        properties: { bind: "proposed_team", itemTemplate: "tpl" },
        children: [],
      },
      {
        id: "tpl",
        type: "TextInput",
        properties: { bind: "name", label: "Nome" },
        children: [],
      },
    ],
  },
  {
    messageType: "updateDataModel",
    surfaceId: "bp",
    data: { proposed_team: [{ name: "A1" }, { name: "A2" }] },
  },
];

it("Repeater instantiates the template per item with relative binds", () => {
  let surf = emptySurface("bp");
  for (const m of REPEAT_MSGS) surf = applyA2uiMessage(surf, m);
  render(<A2uiRenderer surface={surf} />);
  expect(screen.getByDisplayValue("A1")).toBeTruthy();
  expect(screen.getByDisplayValue("A2")).toBeTruthy();
});

it("editing inside a repeater writes to the right index", () => {
  let surf = emptySurface("bp");
  for (const m of REPEAT_MSGS) surf = applyA2uiMessage(surf, m);
  const onDataChange = vi.fn();
  render(<A2uiRenderer surface={surf} onDataChange={onDataChange} />);
  fireEvent.change(screen.getByDisplayValue("A2"), {
    target: { value: "A2-edit" },
  });
  const next = onDataChange.mock.calls[0][0];
  expect(next.proposed_team[1].name).toBe("A2-edit");
  expect(next.proposed_team[0].name).toBe("A1");
});
```

- [ ] **Step 2: FAIL.**

- [ ] **Step 3: Implement.** No renderer, caso `Repeater`:

```tsx
if (node.type === "Repeater") {
  const arrPath = joinBase(basePath, String(node.properties.bind ?? ""));
  const arr = resolveBind(data, arrPath);
  const tplId = String(node.properties.itemTemplate ?? "");
  if (!Array.isArray(arr) || !surface.components[tplId]) {
    return fallback(node); // mesmo fallback visível existente
  }
  return (
    <>
      {arr.map((_, i) => (
        <div key={`${node.id}-${i}`} className={styles.node}>
          {renderNode(surface, tplId, { ...ctx, basePath: `${arrPath}/${i}` })}
        </div>
      ))}
    </>
  );
}
```

(O template e seus descendentes herdam `basePath = "<arrPath>/<i>"`; binds dentro dele são relativos ao item.)

- [ ] **Step 4: PASS** (novos + antigos).
- [ ] **Step 5: Commit** — `feat(console): Repeater A2UI (template por item, binds relativos)`

---

### Task 8: Ações locais estruturais na página

**Files:**
- Modify: `console/src/pages/Discovery/index.tsx`
- Test: ampliar `console/src/pages/Discovery/index.test.tsx`

- [ ] **Step 1: Failing tests.** Com surface contendo botões `{action:{name:"add_agent"}}`, `{action:{name:"remove_agent",params:{path:"proposed_team",index:0}}}`, `{action:{name:"move_agent",params:{path:"proposed_team",index:1,dir:-1}}}`: clicar cada um muta o `dataModel` local (mais um agente vazio-padrão; um a menos; ordem trocada) **sem** chamar `discoveryApi.action`.

- [ ] **Step 2: FAIL.**

- [ ] **Step 3: Implement.** Em `handleAction`:

```tsx
const EMPTY_AGENT = {
  name: "Novo agente",
  role: "",
  objective: "",
  tasks: [],
  tools_integrations: [],
  talks_to: [],
};

function mutateArray(
  data: Record<string, unknown>,
  path: string,
  fn: (arr: unknown[]) => unknown[],
): Record<string, unknown> {
  const arr = resolveBind(data, path);
  return setPath(data, path, fn(Array.isArray(arr) ? arr.slice() : []));
}

// dentro de handleAction(name, params):
switch (name) {
  case "add_agent":
    setDataModel((d) => mutateArray(d, "proposed_team", (a) => [...a, { ...EMPTY_AGENT }]));
    return;
  case "remove_agent":
    setDataModel((d) =>
      mutateArray(d, String(params?.path ?? "proposed_team"), (a) => {
        a.splice(Number(params?.index ?? -1), 1);
        return a;
      }),
    );
    return;
  case "move_agent": {
    const i = Number(params?.index ?? 0);
    const j = i + Number(params?.dir ?? 0);
    setDataModel((d) =>
      mutateArray(d, String(params?.path ?? "proposed_team"), (a) => {
        if (j < 0 || j >= a.length) return a;
        const copy = a.slice();
        [copy[i], copy[j]] = [copy[j], copy[i]];
        return copy;
      }),
    );
    return;
  }
  case "add_item":
    setDataModel((d) => mutateArray(d, String(params?.path ?? ""), (a) => [...a, ""]));
    return;
  case "remove_item":
    setDataModel((d) =>
      mutateArray(d, String(params?.path ?? ""), (a) => {
        a.splice(Number(params?.index ?? -1), 1);
        return a;
      }),
    );
    return;
  case "approve_team":
    // fluxo remoto já implementado na Fase 1
    void approve();
    return;
  default:
    return;
}
```

- [ ] **Step 4: PASS** + tsc + eslint.
- [ ] **Step 5: Commit** — `feat(console): acoes locais estruturais (add/remove/move agentes e itens)`

---

### Task 9: Builder Fase 2 — Repeater + listas editáveis + botões estruturais

**Files:**
- Modify: `src/qwenpaw/a2ui/builder.py`
- Test: ampliar `tests/unit/a2ui/test_builder.py`

- [ ] **Step 1: Failing tests**

```python
def test_team_is_a_repeater_with_template():
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    comps = {c.id: c for c in msgs[1].components}
    reps = [c for c in msgs[1].components if c.type == "Repeater"]
    assert len(reps) == 1
    rep = reps[0]
    assert rep.properties["bind"] == "proposed_team"
    assert rep.properties["itemTemplate"] in comps


def test_template_binds_are_relative():
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    comps = {c.id: c for c in msgs[1].components}
    tpl_root = comps[
        [c for c in msgs[1].components if c.type == "Repeater"][0]
        .properties["itemTemplate"]
    ]
    # percorre o template e coleta binds — nenhum começa com proposed_team/
    def walk(cid):
        c = comps[cid]
        yield c
        for ch in c.children:
            yield from walk(ch)
    binds = [
        c.properties["bind"]
        for c in walk(tpl_root.id)
        if "bind" in c.properties
    ]
    assert binds and all(not b.startswith("proposed_team/") for b in binds)


def test_structural_buttons_present():
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    actions = [
        c.properties.get("action", {}).get("name")
        for c in msgs[1].components
        if c.type == "Button"
    ]
    assert "add_agent" in actions
    assert "approve_team" in actions
```

- [ ] **Step 2: FAIL** (Fase 1 gera cards por índice).

- [ ] **Step 3: Implement.** Substituir o loop por-índice por um **template único**: card-template (`tpl-card`) com `TextInput bind="name"`, `TextInput bind="role"`, `TextArea bind="objective"` (binds relativos), e um `Repeater id="team-rep" properties={"bind":"proposed_team","itemTemplate":"tpl-card"}` no root. Botão `add_agent` no root. Tasks/integrações: dentro do template, um `Repeater bind="tasks" itemTemplate="tpl-task"` com `tpl-task = TextInput bind=""`… **Decisão de simplicidade:** para arrays de string, o template é um `TextInput` com `bind: "."` — e o renderer trata `bind: "."` como "o próprio item" (`basePath` sem sufixo). Adicionar esse caso no renderer (`joinBase(base, ".") === base`) com teste correspondente no Task 7 (acrescentar se ainda não coberto). Botões `remove_agent`/`move_agent` **não** entram no template neste ciclo se exigirem índice dinâmico no backend — o builder não sabe o índice; em vez disso o **renderer** injeta `params.index` automaticamente quando um Button com `action.params.indexFromRepeater === true` está dentro de um Repeater (o renderer conhece o índice). Teste no renderer: botão no template com `{action:{name:"remove_agent",params:{indexFromRepeater:true,path:"proposed_team"}}}` → `onAction` recebido com `index` do item.

- [ ] **Step 4: PASS** backend (`tests/unit/a2ui/`) + frontend (renderer com indexFromRepeater).
- [ ] **Step 5: Commit** — `feat(a2ui): builder fase 2 (Repeater + template + botoes estruturais)`

---

### Task 10: Fechamento

- [ ] Backend: `pytest tests/unit/a2ui tests/unit/agui tests/unit/discovery tests/unit/app/routers -q` → tudo PASS.
- [ ] Frontend: `vitest run` nos arquivos tocados + `tsc --noEmit -p tsconfig.app.json` + eslint.
- [ ] Pre-commit pinado (black/add-trailing-comma/mypy) nos arquivos backend tocados; conferir `git diff --ignore-cr-at-eol --stat` (sem churn CRLF).
- [ ] Smoke: rodar o app + console dev, `/discovery` com sessão scriptada → editar nome, remover agente, adicionar agente, aprovar → `blueprint.json` gravado com as edições.
- [ ] Commit final.

---

## Self-review

**Cobertura do spec:** §2 binding/componentes/ações → Tasks 3–5, 7–9. §3 arquitetura → Tasks 1–9 (finalize=T1, action=T2, builder=T3/T9, binding=T4, renderer=T5/T7, página=T6/T8). §4 fluxo → T2+T5+T6. §5 erros → T2 (RUN_ERROR), T4/T5 (fallback de path), T6 (edição preservada). §6 testes → todos os tasks têm testes. §7 aceite → T10 smoke. §8 fases → Fase 1 = T1–T6, Fase 2 = T7–T9. ✔

**Placeholders:** nenhum TBD; os pontos "ajustar ao schema real" são verificações contra código existente (state.py), não lacunas de design. ✔

**Consistência:** `finalize_blueprint(data, out_dir)` igual em T1/T2; `resolveBind/setPath/resolveProps/joinBase` iguais em T4/T5/T7/T8; `action(sessionId, name, data, onEvent, signal?)` igual em T6; `properties.bind` (string) nos componentes vs `{$bind}` em valores de props — **convenção dupla intencional**: componentes editáveis/Repeater usam `properties.bind` (path string), valores read-only podem usar `{$bind}`; ambas documentadas no spec §2. ✔
