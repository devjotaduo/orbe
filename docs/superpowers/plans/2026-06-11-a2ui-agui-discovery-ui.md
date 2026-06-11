# Camada A2UI + AG-UI (UI conversacional do discovery) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Levar a entrevista do discovery agent para o console web, transmitindo a conversa ao vivo via **AG-UI** (eventos SSE) e renderizando o blueprint/time como **UI generativa A2UI** mapeada para Ant Design.

**Architecture:** Duas bibliotecas de protocolo nativas e spec-compliant no backend (`src/qwenpaw/agui`, `src/qwenpaw/a2ui`, só dependem de Pydantic), um router SSE (`discovery_stream`) que dirige uma **sessão de discovery** atrás de uma `Protocol` (com uma sessão "scriptada" para este ciclo, costura para o runner LLM real da camada 1), e no console um cliente SSE + um renderer A2UI→Ant Design numa página nova.

**Tech Stack:** Python 3.11, Pydantic v2, FastAPI (`StreamingResponse`), pytest; React 18, TypeScript, Ant Design 5, Vite, Vitest, `@testing-library/react`.

**Referências do spec:** `docs/superpowers/specs/2026-06-11-a2ui-agui-discovery-ui-design.md`. Protocolos: AG-UI (https://docs.ag-ui.com/), A2UI v0.9 (https://a2ui.org/specification/v0.9-a2ui/).

**Dependência / seam:** a camada 1 (`src/qwenpaw/discovery/` do spec `2026-06-11-discovery-agent-design.md`) ainda não está implementada. Este plano não depende dela: consome o **contrato `blueprint.json`** (dict) e dirige a entrevista por uma `DiscoverySession` Protocol, com uma `ScriptedDiscoverySession` canned. Quando o runner real existir, ele implementa a mesma Protocol.

**Gate:** todos os arquivos em `src/qwenpaw/**` são gated pelo `/agentscope-guardian` — a execução final via `/dev-team` cuida disso. Arquivos em `console/**` não são gated.

---

## File Structure

**Backend (`src/qwenpaw/`, gated):**
- `agui/__init__.py` — exporta os eventos + helpers.
- `agui/events.py` — schemas Pydantic dos event-types AG-UI (puro).
- `agui/emitter.py` — serialização SSE + helpers de sequência de eventos.
- `a2ui/__init__.py` — exporta schemas + builder.
- `a2ui/schema.py` — schemas das 4 mensagens A2UI + `Component` (adjacency-list).
- `a2ui/builder.py` — `blueprint(dict) → list[A2UIMessage]`.
- `discovery/session.py` — `DiscoverySession` Protocol + `TurnResult`.
- `discovery/scripted_session.py` — sessão canned (e-commerce/WhatsApp) para este ciclo + testes.
- `app/routers/discovery_stream.py` — endpoint SSE por turno + registry de sessões em memória.
- `app/routers/__init__.py` — registrar o router (modify).

**Frontend (`console/src/`, não gated):**
- `api/types/agui.ts` — tipos TS dos eventos.
- `api/types/a2ui.ts` — tipos TS das mensagens/componentes.
- `api/modules/discovery.ts` — cliente SSE (fetch + ReadableStream).
- `components/a2ui/catalog.ts` — mapa componentType → componente Ant Design.
- `components/a2ui/A2uiRenderer.tsx` — renderer da adjacency-list.
- `pages/Discovery/index.tsx` — página da entrevista conversacional.

**Tests:**
- `tests/unit/agui/test_events.py`, `tests/unit/agui/test_emitter.py`
- `tests/unit/a2ui/test_schema.py`, `tests/unit/a2ui/test_builder.py`
- `tests/unit/discovery/test_scripted_session.py`
- `tests/unit/app/routers/test_discovery_stream_router.py`
- `console/src/api/modules/discovery.test.ts`
- `console/src/components/a2ui/A2uiRenderer.test.tsx`

---

## PHASE A — Biblioteca AG-UI (eventos + emitter)

### Task 1: Schemas dos eventos AG-UI

**Files:**
- Create: `src/qwenpaw/agui/events.py`
- Create: `src/qwenpaw/agui/__init__.py`
- Test: `tests/unit/agui/test_events.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/agui/test_events.py
import json
from qwenpaw.agui.events import (
    RunStartedEvent, RunErrorEvent, TextMessageContentEvent,
    StateSnapshotEvent, CustomEvent,
)


def test_run_started_serializes_camelcase_with_type():
    ev = RunStartedEvent(thread_id="t1", run_id="r1")
    data = json.loads(ev.model_dump_json(by_alias=True, exclude_none=True))
    assert data == {"type": "RUN_STARTED", "threadId": "t1", "runId": "r1"}


def test_text_message_content_carries_delta():
    ev = TextMessageContentEvent(message_id="m1", delta="Olá")
    data = json.loads(ev.model_dump_json(by_alias=True, exclude_none=True))
    assert data == {"type": "TEXT_MESSAGE_CONTENT", "messageId": "m1", "delta": "Olá"}


def test_state_snapshot_holds_arbitrary_dict():
    ev = StateSnapshotEvent(snapshot={"company": {"segment": "ecommerce"}})
    data = json.loads(ev.model_dump_json(by_alias=True, exclude_none=True))
    assert data["type"] == "STATE_SNAPSHOT"
    assert data["snapshot"]["company"]["segment"] == "ecommerce"


def test_custom_event_wraps_named_payload():
    ev = CustomEvent(name="a2ui", value={"messageType": "createSurface"})
    data = json.loads(ev.model_dump_json(by_alias=True, exclude_none=True))
    assert data == {"type": "CUSTOM", "name": "a2ui", "value": {"messageType": "createSurface"}}


def test_run_error_omits_optional_code_when_absent():
    ev = RunErrorEvent(message="boom")
    data = json.loads(ev.model_dump_json(by_alias=True, exclude_none=True))
    assert data == {"type": "RUN_ERROR", "message": "boom"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/agui/test_events.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'qwenpaw.agui'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/qwenpaw/agui/events.py
# -*- coding: utf-8 -*-
"""AG-UI event schemas (spec-compliant subset).

Mirrors the AG-UI protocol (https://docs.ag-ui.com/): each event has a
SCREAMING_SNAKE ``type`` discriminator and camelCase wire fields. Pure Pydantic,
no agentscope dependency — testable in isolation.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


def _camel(s: str) -> str:
    head, *tail = s.split("_")
    return head + "".join(w.capitalize() for w in tail)


class BaseEvent(BaseModel):
    """Common config: camelCase aliases on the wire, populate by python name."""

    model_config = ConfigDict(
        alias_generator=_camel,
        populate_by_name=True,
    )


class RunStartedEvent(BaseEvent):
    type: Literal["RUN_STARTED"] = "RUN_STARTED"
    thread_id: str
    run_id: str


class RunFinishedEvent(BaseEvent):
    type: Literal["RUN_FINISHED"] = "RUN_FINISHED"
    thread_id: str
    run_id: str


class RunErrorEvent(BaseEvent):
    type: Literal["RUN_ERROR"] = "RUN_ERROR"
    message: str
    code: str | None = None


class TextMessageStartEvent(BaseEvent):
    type: Literal["TEXT_MESSAGE_START"] = "TEXT_MESSAGE_START"
    message_id: str
    role: str = "assistant"


class TextMessageContentEvent(BaseEvent):
    type: Literal["TEXT_MESSAGE_CONTENT"] = "TEXT_MESSAGE_CONTENT"
    message_id: str
    delta: str


class TextMessageEndEvent(BaseEvent):
    type: Literal["TEXT_MESSAGE_END"] = "TEXT_MESSAGE_END"
    message_id: str


class StateSnapshotEvent(BaseEvent):
    type: Literal["STATE_SNAPSHOT"] = "STATE_SNAPSHOT"
    snapshot: dict[str, Any]


class StateDeltaEvent(BaseEvent):
    # delta is a JSON Patch (RFC 6902) list of ops, per AG-UI.
    type: Literal["STATE_DELTA"] = "STATE_DELTA"
    delta: list[dict[str, Any]]


class CustomEvent(BaseEvent):
    type: Literal["CUSTOM"] = "CUSTOM"
    name: str
    value: dict[str, Any] = Field(default_factory=dict)
```

```python
# src/qwenpaw/agui/__init__.py
# -*- coding: utf-8 -*-
"""AG-UI protocol layer for qwenpaw (events + SSE emitter)."""
from .events import (
    BaseEvent,
    CustomEvent,
    RunErrorEvent,
    RunFinishedEvent,
    RunStartedEvent,
    StateDeltaEvent,
    StateSnapshotEvent,
    TextMessageContentEvent,
    TextMessageEndEvent,
    TextMessageStartEvent,
)

__all__ = [
    "BaseEvent",
    "CustomEvent",
    "RunErrorEvent",
    "RunFinishedEvent",
    "RunStartedEvent",
    "StateDeltaEvent",
    "StateSnapshotEvent",
    "TextMessageContentEvent",
    "TextMessageEndEvent",
    "TextMessageStartEvent",
]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/agui/test_events.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add src/qwenpaw/agui/events.py src/qwenpaw/agui/__init__.py tests/unit/agui/test_events.py
git commit -m "feat(agui): AG-UI event schemas (spec-compliant subset)"
```

---

### Task 2: Emitter SSE + helpers de sequência

**Files:**
- Create: `src/qwenpaw/agui/emitter.py`
- Modify: `src/qwenpaw/agui/__init__.py` (export `sse`, `text_message_events`)
- Test: `tests/unit/agui/test_emitter.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/agui/test_emitter.py
from qwenpaw.agui.emitter import sse, text_message_events
from qwenpaw.agui.events import RunStartedEvent, TextMessageContentEvent


def test_sse_wraps_event_as_event_stream_frame():
    frame = sse(RunStartedEvent(thread_id="t", run_id="r"))
    assert frame.startswith("data: ")
    assert frame.endswith("\n\n")
    assert '"type":"RUN_STARTED"' in frame.replace(" ", "")
    assert '"threadId":"t"' in frame.replace(" ", "")


def test_text_message_events_brackets_content_with_start_end():
    evs = text_message_events("m1", "oi")
    assert [e.type for e in evs] == [
        "TEXT_MESSAGE_START", "TEXT_MESSAGE_CONTENT", "TEXT_MESSAGE_END",
    ]
    content = [e for e in evs if isinstance(e, TextMessageContentEvent)][0]
    assert content.message_id == "m1"
    assert content.delta == "oi"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/agui/test_emitter.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'qwenpaw.agui.emitter'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/qwenpaw/agui/emitter.py
# -*- coding: utf-8 -*-
"""SSE serialization + event-sequence helpers for AG-UI."""
from __future__ import annotations

from .events import (
    BaseEvent,
    TextMessageContentEvent,
    TextMessageEndEvent,
    TextMessageStartEvent,
)


def sse(event: BaseEvent) -> str:
    """Serialize one AG-UI event as a text/event-stream frame."""
    return f"data: {event.model_dump_json(by_alias=True, exclude_none=True)}\n\n"


def text_message_events(message_id: str, text: str) -> list[BaseEvent]:
    """The START/CONTENT/END triplet for a complete assistant message."""
    return [
        TextMessageStartEvent(message_id=message_id),
        TextMessageContentEvent(message_id=message_id, delta=text),
        TextMessageEndEvent(message_id=message_id),
    ]
```

Append to `src/qwenpaw/agui/__init__.py`:

```python
from .emitter import sse, text_message_events  # noqa: E402

__all__ += ["sse", "text_message_events"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/agui/ -v`
Expected: PASS (all of Task 1 + Task 2)

- [ ] **Step 5: Commit**

```bash
git add src/qwenpaw/agui/emitter.py src/qwenpaw/agui/__init__.py tests/unit/agui/test_emitter.py
git commit -m "feat(agui): SSE emitter + text-message sequence helper"
```

---

## PHASE B — Biblioteca A2UI (schema + builder)

### Task 3: Schemas A2UI (mensagens + componente adjacency-list)

**Files:**
- Create: `src/qwenpaw/a2ui/schema.py`
- Create: `src/qwenpaw/a2ui/__init__.py`
- Test: `tests/unit/a2ui/test_schema.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/a2ui/test_schema.py
import json
import pytest
from pydantic import ValidationError
from qwenpaw.a2ui.schema import (
    Component, CreateSurface, UpdateComponents, UpdateDataModel, DeleteSurface,
)


def test_component_defaults_empty_props_and_children():
    c = Component(id="root", type="Column")
    assert c.properties == {}
    assert c.children == []


def test_create_surface_serializes_message_type():
    msg = CreateSurface(surface_id="blueprint", root="root")
    data = json.loads(msg.model_dump_json(by_alias=True))
    assert data == {"messageType": "createSurface", "surfaceId": "blueprint", "root": "root"}


def test_update_components_carries_component_list():
    msg = UpdateComponents(
        surface_id="bp",
        components=[Component(id="t", type="Text", properties={"text": "oi"})],
    )
    data = json.loads(msg.model_dump_json(by_alias=True))
    assert data["messageType"] == "updateComponents"
    assert data["components"][0] == {"id": "t", "type": "Text", "properties": {"text": "oi"}, "children": []}


def test_update_data_model_and_delete_surface():
    assert UpdateDataModel(surface_id="bp", data={"k": 1}).message_type == "updateDataModel"
    assert DeleteSurface(surface_id="bp").message_type == "deleteSurface"


def test_component_type_is_required():
    with pytest.raises(ValidationError):
        Component(id="x")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/a2ui/test_schema.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'qwenpaw.a2ui'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/qwenpaw/a2ui/schema.py
# -*- coding: utf-8 -*-
"""A2UI message + component schemas (adjacency-list model).

Mirrors the A2UI protocol (https://a2ui.org/specification/v0.9-a2ui/): the UI is
a flat list of components; the tree is built implicitly by ``children`` id refs.
Server→client messages: createSurface / updateComponents / updateDataModel /
deleteSurface. Pure Pydantic — testable in isolation.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


def _camel(s: str) -> str:
    head, *tail = s.split("_")
    return head + "".join(w.capitalize() for w in tail)


class _A2UIModel(BaseModel):
    model_config = ConfigDict(alias_generator=_camel, populate_by_name=True)


class Component(_A2UIModel):
    """One node in the adjacency list. ``children`` references child ids."""

    id: str
    type: str
    properties: dict[str, Any] = Field(default_factory=dict)
    children: list[str] = Field(default_factory=list)


class CreateSurface(_A2UIModel):
    message_type: Literal["createSurface"] = "createSurface"
    surface_id: str
    root: str  # id of the root component


class UpdateComponents(_A2UIModel):
    message_type: Literal["updateComponents"] = "updateComponents"
    surface_id: str
    components: list[Component]


class UpdateDataModel(_A2UIModel):
    message_type: Literal["updateDataModel"] = "updateDataModel"
    surface_id: str
    data: dict[str, Any]


class DeleteSurface(_A2UIModel):
    message_type: Literal["deleteSurface"] = "deleteSurface"
    surface_id: str


A2UIMessage = CreateSurface | UpdateComponents | UpdateDataModel | DeleteSurface
```

```python
# src/qwenpaw/a2ui/__init__.py
# -*- coding: utf-8 -*-
"""A2UI generative-UI protocol layer for qwenpaw."""
from .schema import (
    A2UIMessage,
    Component,
    CreateSurface,
    DeleteSurface,
    UpdateComponents,
    UpdateDataModel,
)

__all__ = [
    "A2UIMessage",
    "Component",
    "CreateSurface",
    "DeleteSurface",
    "UpdateComponents",
    "UpdateDataModel",
]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/a2ui/test_schema.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add src/qwenpaw/a2ui/schema.py src/qwenpaw/a2ui/__init__.py tests/unit/a2ui/test_schema.py
git commit -m "feat(a2ui): A2UI message + adjacency-list component schemas"
```

---

### Task 4: Builder `blueprint(dict) → surfaces A2UI`

**Files:**
- Create: `src/qwenpaw/a2ui/builder.py`
- Modify: `src/qwenpaw/a2ui/__init__.py` (export `build_blueprint_surface`)
- Test: `tests/unit/a2ui/test_builder.py`

O builder consome o **contrato `blueprint.json`** (campos do `TeamBlueprint` do spec da camada 1): `company_profile`, `process_map`, `detected_integrations`, `proposed_team`, `roadmap`, `open_questions`. Para o 1º ciclo o texto vai literal nas `properties` (sem data-binding por path); o `updateDataModel` ainda carrega o blueprint cru para uso futuro.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/a2ui/test_builder.py
from qwenpaw.a2ui.builder import build_blueprint_surface
from qwenpaw.a2ui.schema import CreateSurface, UpdateComponents, UpdateDataModel

BLUEPRINT = {
    "company_profile": {"segment": "ecommerce", "name": "Loja X"},
    "process_map": [{"area": "Atendimento", "processes": ["responder WhatsApp"]}],
    "detected_integrations": [{"type": "messaging", "name": "WhatsApp"}],
    "proposed_team": [
        {
            "name": "Atendente WhatsApp",
            "role": "atendimento",
            "objective": "responder clientes",
            "tasks": ["responder dúvidas"],
            "tools_integrations": ["mcp:evolution-whatsapp"],
            "talks_to": [],
        }
    ],
    "roadmap": [{"step": "atendimento WhatsApp"}],
    "open_questions": ["qual volume de mensagens?"],
}


def test_returns_create_then_components_then_datamodel():
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    assert isinstance(msgs[0], CreateSurface)
    assert isinstance(msgs[1], UpdateComponents)
    assert isinstance(msgs[2], UpdateDataModel)
    assert msgs[0].surface_id == "bp"
    assert msgs[0].root == msgs[1].components[0].id  # root is first component


def test_one_card_per_team_member_with_name_text():
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    comps = msgs[1].components
    cards = [c for c in comps if c.type == "Card"]
    assert len(cards) == 1
    texts = [c.properties.get("text", "") for c in comps if c.type in ("Text", "Heading")]
    assert any("Atendente WhatsApp" in t for t in texts)


def test_integration_becomes_tag():
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    tags = [c for c in msgs[1].components if c.type == "Tag"]
    assert any(c.properties.get("text") == "WhatsApp" for c in tags)


def test_datamodel_carries_raw_blueprint():
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    assert msgs[2].data == BLUEPRINT


def test_adjacency_children_reference_existing_ids():
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    comps = msgs[1].components
    ids = {c.id for c in comps}
    for c in comps:
        for child in c.children:
            assert child in ids, f"dangling child id {child}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/a2ui/test_builder.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'qwenpaw.a2ui.builder'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/qwenpaw/a2ui/builder.py
# -*- coding: utf-8 -*-
"""Turn a blueprint dict (the blueprint.json contract) into A2UI surfaces."""
from __future__ import annotations

from typing import Any

from .schema import (
    A2UIMessage,
    Component,
    CreateSurface,
    UpdateComponents,
    UpdateDataModel,
)


def _heading(cid: str, text: str) -> Component:
    return Component(id=cid, type="Heading", properties={"text": text})


def _text(cid: str, text: str) -> Component:
    return Component(id=cid, type="Text", properties={"text": text})


def _tag(cid: str, text: str) -> Component:
    return Component(id=cid, type="Tag", properties={"text": text})


def build_blueprint_surface(
    blueprint: dict[str, Any], surface_id: str = "blueprint"
) -> list[A2UIMessage]:
    """Build [createSurface, updateComponents, updateDataModel] for a blueprint.

    Layout: a root Column with a title, one Card per proposed team member
    (name Heading + role/objective Text + integration Tags), then an areas
    List and an open-questions List. Text is inlined in properties; the raw
    blueprint also rides in updateDataModel for future data-binding.
    """
    comps: list[Component] = []
    root_children: list[str] = []

    company = blueprint.get("company_profile", {}) or {}
    title = company.get("name") or company.get("segment") or "Time proposto"
    comps.append(_heading("title", f"Time proposto — {title}"))
    root_children.append("title")

    # One card per team member.
    for i, member in enumerate(blueprint.get("proposed_team", []) or []):
        card_id = f"card-{i}"
        name_id, role_id = f"card-{i}-name", f"card-{i}-role"
        card_children = [name_id, role_id]
        comps.append(_heading(name_id, member.get("name", "Agente")))
        role = member.get("role", "")
        objective = member.get("objective", "")
        comps.append(_text(role_id, f"{role} — {objective}".strip(" —")))
        for j, integ in enumerate(member.get("tools_integrations", []) or []):
            tid = f"card-{i}-tool-{j}"
            comps.append(_tag(tid, str(integ)))
            card_children.append(tid)
        comps.append(Component(id=card_id, type="Card", children=card_children))
        root_children.append(card_id)

    # Detected integrations as tags under a small section.
    integ_section_children: list[str] = []
    for i, integ in enumerate(blueprint.get("detected_integrations", []) or []):
        tid = f"integ-{i}"
        comps.append(_tag(tid, integ.get("name", str(integ))))
        integ_section_children.append(tid)
    if integ_section_children:
        comps.append(_heading("integ-title", "Integrações detectadas"))
        comps.append(
            Component(id="integ-row", type="Row", children=integ_section_children)
        )
        root_children.extend(["integ-title", "integ-row"])

    # Open questions as a list.
    oq = blueprint.get("open_questions", []) or []
    if oq:
        oq_children: list[str] = []
        for i, q in enumerate(oq):
            qid = f"oq-{i}"
            comps.append(_text(qid, str(q)))
            oq_children.append(qid)
        comps.append(_heading("oq-title", "Perguntas em aberto"))
        comps.append(Component(id="oq-list", type="List", children=oq_children))
        root_children.extend(["oq-title", "oq-list"])

    root = Component(id="root", type="Column", children=root_children)
    # Root must be first (test asserts components[0] is the root).
    components = [root, *comps]

    return [
        CreateSurface(surface_id=surface_id, root="root"),
        UpdateComponents(surface_id=surface_id, components=components),
        UpdateDataModel(surface_id=surface_id, data=blueprint),
    ]
```

Append to `src/qwenpaw/a2ui/__init__.py`:

```python
from .builder import build_blueprint_surface  # noqa: E402

__all__ += ["build_blueprint_surface"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/a2ui/ -v`
Expected: PASS (Task 3 + Task 4)

- [ ] **Step 5: Commit**

```bash
git add src/qwenpaw/a2ui/builder.py src/qwenpaw/a2ui/__init__.py tests/unit/a2ui/test_builder.py
git commit -m "feat(a2ui): builder blueprint dict -> A2UI surface"
```

---

## PHASE C — Integração backend (sessão + router SSE)

### Task 5: `DiscoverySession` Protocol + `TurnResult`

**Files:**
- Create: `src/qwenpaw/discovery/__init__.py` (se ainda não existir; se a camada 1 já tiver criado, só adicionar export)
- Create: `src/qwenpaw/discovery/session.py`
- Test: `tests/unit/discovery/test_scripted_session.py` (Task 6 escreve os testes; aqui só o contrato)

> ⚠️ Se a camada 1 já criou `src/qwenpaw/discovery/__init__.py`, **não sobrescreva** — apenas garanta que `session.py` é importável. Caso contrário, crie um `__init__.py` vazio.

- [ ] **Step 1: Write the contract (no test yet — exercised by Task 6)**

```python
# src/qwenpaw/discovery/session.py
# -*- coding: utf-8 -*-
"""Seam between the discovery interview and the AG-UI/A2UI transport.

A DiscoverySession advances one turn at a time. The router feeds the user's
message (None to start) and gets back the agent's next question + current state,
or the final blueprint. The real LLM-driven runner (layer 1) and the scripted
session for this cycle both implement this Protocol.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class TurnResult:
    """Outcome of advancing the interview by one turn."""

    state: dict[str, Any] = field(default_factory=dict)
    question: str | None = None        # next agent question (None when done)
    blueprint: dict[str, Any] | None = None  # set on the final turn
    done: bool = False


@runtime_checkable
class DiscoverySession(Protocol):
    async def next_turn(self, user_message: str | None) -> TurnResult:
        """Advance one turn. ``user_message`` is None on the opening turn."""
        ...
```

Create `src/qwenpaw/discovery/__init__.py` **only if absent**:

```python
# src/qwenpaw/discovery/__init__.py
# -*- coding: utf-8 -*-
"""Discovery agent package (layer 1 brain + AG-UI/A2UI seam)."""
```

- [ ] **Step 2: Commit**

```bash
git add src/qwenpaw/discovery/session.py src/qwenpaw/discovery/__init__.py
git commit -m "feat(discovery): DiscoverySession protocol + TurnResult seam"
```

---

### Task 6: `ScriptedDiscoverySession` (canned e-commerce/WhatsApp)

**Files:**
- Create: `src/qwenpaw/discovery/scripted_session.py`
- Test: `tests/unit/discovery/test_scripted_session.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/discovery/test_scripted_session.py
import pytest
from qwenpaw.discovery.scripted_session import ScriptedDiscoverySession
from qwenpaw.discovery.session import DiscoverySession, TurnResult


@pytest.mark.asyncio
async def test_implements_protocol():
    assert isinstance(ScriptedDiscoverySession(), DiscoverySession)


@pytest.mark.asyncio
async def test_opening_turn_asks_first_question_and_is_not_done():
    s = ScriptedDiscoverySession()
    r = await s.next_turn(None)
    assert isinstance(r, TurnResult)
    assert r.question is not None
    assert r.done is False
    assert r.blueprint is None


@pytest.mark.asyncio
async def test_state_segment_set_after_first_answer():
    s = ScriptedDiscoverySession()
    await s.next_turn(None)
    r = await s.next_turn("tenho um e-commerce de roupas")
    assert r.state.get("company", {}).get("segment") == "ecommerce"


@pytest.mark.asyncio
async def test_runs_to_a_blueprint_and_then_done():
    s = ScriptedDiscoverySession()
    r = await s.next_turn(None)
    answers = ["e-commerce de roupas", "uso WhatsApp e planilha", "responder clientes"]
    for a in answers:
        r = await s.next_turn(a)
    assert r.done is True
    assert r.blueprint is not None
    assert r.blueprint["company_profile"]["segment"] == "ecommerce"
    assert len(r.blueprint["proposed_team"]) >= 1
    assert r.question is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/discovery/test_scripted_session.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'qwenpaw.discovery.scripted_session'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/qwenpaw/discovery/scripted_session.py
# -*- coding: utf-8 -*-
"""A canned, LLM-free discovery interview for the A2UI/AG-UI cycle and tests.

Drives a fixed 3-question e-commerce/WhatsApp interview, then emits a canned
TeamBlueprint. The real LLM-driven runner (layer 1) will replace this behind
the same DiscoverySession protocol.
"""
from __future__ import annotations

from .session import TurnResult

_QUESTIONS = [
    "Qual é o segmento da sua empresa?",
    "Quais sistemas você já usa (CRM, planilha, WhatsApp)?",
    "Qual é a dor mais urgente que um agente resolveria primeiro?",
]

_BLUEPRINT = {
    "company_profile": {"segment": "ecommerce", "name": "Sua loja"},
    "process_map": [{"area": "Atendimento", "processes": ["responder WhatsApp"]}],
    "detected_integrations": [
        {"type": "messaging", "name": "WhatsApp"},
        {"type": "spreadsheet", "name": "Planilha"},
    ],
    "proposed_team": [
        {
            "name": "Atendente WhatsApp",
            "role": "atendimento",
            "objective": "responder clientes no WhatsApp",
            "tasks": ["responder dúvidas", "registrar pedidos"],
            "tools_integrations": ["mcp:evolution-whatsapp", "mcp:google-sheets"],
            "talks_to": [],
        }
    ],
    "roadmap": [{"step": "atendimento WhatsApp"}, {"step": "registro em planilha"}],
    "open_questions": ["Qual o volume médio de mensagens por dia?"],
}


class ScriptedDiscoverySession:
    def __init__(self) -> None:
        self._asked = 0
        self._state: dict = {"company": {}, "open_areas": [], "integrations": []}

    async def next_turn(self, user_message: str | None) -> TurnResult:
        # Record the answer to the previously asked question.
        if user_message is not None and self._asked >= 1:
            self._absorb(user_message)

        if self._asked < len(_QUESTIONS):
            q = _QUESTIONS[self._asked]
            self._asked += 1
            return TurnResult(state=dict(self._state), question=q, done=False)

        # No more questions → emit the blueprint.
        return TurnResult(state=dict(self._state), blueprint=_BLUEPRINT, done=True)

    def _absorb(self, answer: str) -> None:
        low = answer.lower()
        if self._asked == 1:  # answer to the segment question
            if "commerc" in low or "loja" in low or "venda" in low:
                self._state["company"]["segment"] = "ecommerce"
            else:
                self._state["company"]["segment"] = "outro"
                self._state["open_areas"].append({"topic": "validar segmento"})
        elif self._asked == 2:  # answer to the systems question
            if "whats" in low:
                self._state["integrations"].append({"type": "messaging", "name": "WhatsApp"})
            if "planilh" in low or "sheet" in low:
                self._state["integrations"].append({"type": "spreadsheet", "name": "Planilha"})
```

> Nota TDD: o teste `test_state_segment_set_after_first_answer` chama `next_turn(None)` (pergunta 1, `_asked`→1) e depois `next_turn("...e-commerce...")` — aí `_asked>=1` e `_absorb` roda com `_asked==1`. Confere com a implementação.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/discovery/test_scripted_session.py -v`
Expected: PASS (4 passed). Se `pytest-asyncio` não estiver configurado em modo auto, confirmar que `tests/conftest.py` define `asyncio_mode = auto` ou marcar com `@pytest.mark.asyncio` (já marcado).

- [ ] **Step 5: Commit**

```bash
git add src/qwenpaw/discovery/scripted_session.py tests/unit/discovery/test_scripted_session.py
git commit -m "feat(discovery): scripted LLM-free interview session for AG-UI cycle"
```

---

### Task 7: Router SSE `discovery_stream` (um turno por POST)

**Files:**
- Create: `src/qwenpaw/app/routers/discovery_stream.py`
- Modify: `src/qwenpaw/app/routers/__init__.py` (importar + `include_router`)
- Test: `tests/unit/app/routers/test_discovery_stream_router.py`

Modelo: cada `POST /discovery/stream` avança **um turno** e transmite os eventos daquele turno (pergunta+estado, ou blueprint+RUN_FINISHED). Sessões ficam num registry em memória por `session_id` (multi-tenant é camada futura). Uma fábrica de sessão injetável permite o teste usar a `ScriptedDiscoverySession`.

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/app/routers/test_discovery_stream_router.py
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient
from qwenpaw.app.routers import discovery_stream as ds


def _events_from(resp_text: str) -> list[dict]:
    out = []
    for line in resp_text.splitlines():
        if line.startswith("data: "):
            out.append(json.loads(line[len("data: "):]))
    return out


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(ds.router)
    return TestClient(app)


def test_opening_turn_streams_run_started_text_and_state():
    client = _client()
    r = client.post("/discovery/stream", json={"session_id": "s1", "message": None})
    assert r.status_code == 200
    types = [e["type"] for e in _events_from(r.text)]
    assert types[0] == "RUN_STARTED"
    assert "TEXT_MESSAGE_CONTENT" in types
    assert "STATE_SNAPSHOT" in types
    assert types[-1] == "RUN_FINISHED"


def test_final_turn_emits_custom_a2ui_surface():
    client = _client()
    client.post("/discovery/stream", json={"session_id": "s2", "message": None})
    for msg in ["e-commerce de roupas", "uso WhatsApp e planilha", "responder clientes"]:
        r = client.post("/discovery/stream", json={"session_id": "s2", "message": msg})
    events = _events_from(r.text)
    custom = [e for e in events if e["type"] == "CUSTOM" and e["name"] == "a2ui"]
    assert custom, "expected an A2UI CUSTOM event on the final turn"
    # The CUSTOM value is one A2UI message; createSurface should appear across the turn.
    msg_types = {c["value"]["messageType"] for c in custom}
    assert "createSurface" in msg_types
    assert {"updateComponents", "updateDataModel"} <= msg_types


def test_unknown_segment_still_completes(monkeypatch):
    client = _client()
    client.post("/discovery/stream", json={"session_id": "s3", "message": None})
    for msg in ["consultoria jurídica", "uso email", "organizar processos"]:
        r = client.post("/discovery/stream", json={"session_id": "s3", "message": msg})
    types = [e["type"] for e in _events_from(r.text)]
    assert types[-1] == "RUN_FINISHED"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/app/routers/test_discovery_stream_router.py -v`
Expected: FAIL — `ModuleNotFoundError: ... discovery_stream`

- [ ] **Step 3: Write minimal implementation**

```python
# src/qwenpaw/app/routers/discovery_stream.py
# -*- coding: utf-8 -*-
"""SSE endpoint that drives a discovery interview over AG-UI + A2UI.

One POST advances the session by one turn and streams that turn's AG-UI events.
A2UI surfaces ride inside CUSTOM events (name="a2ui"). Sessions are held in
memory keyed by session_id (multi-tenant is a future layer).
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Callable

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from qwenpaw.agui.emitter import sse, text_message_events
from qwenpaw.agui.events import (
    CustomEvent,
    RunErrorEvent,
    RunFinishedEvent,
    RunStartedEvent,
    StateSnapshotEvent,
)
from qwenpaw.a2ui.builder import build_blueprint_surface
from qwenpaw.discovery.scripted_session import ScriptedDiscoverySession
from qwenpaw.discovery.session import DiscoverySession

logger = logging.getLogger(__name__)
router = APIRouter()

# Injectable so tests / layer-1 can swap the real LLM session in.
_session_factory: Callable[[], DiscoverySession] = ScriptedDiscoverySession
_sessions: dict[str, DiscoverySession] = {}


def set_session_factory(factory: Callable[[], DiscoverySession]) -> None:
    global _session_factory
    _session_factory = factory


class DiscoveryTurnRequest(BaseModel):
    session_id: str
    message: str | None = None


def _get_or_create(session_id: str) -> DiscoverySession:
    if session_id not in _sessions:
        _sessions[session_id] = _session_factory()
    return _sessions[session_id]


@router.post("/discovery/stream")
async def discovery_stream(req: DiscoveryTurnRequest) -> StreamingResponse:
    session = _get_or_create(req.session_id)
    thread_id, run_id = req.session_id, uuid.uuid4().hex

    async def generate():
        yield sse(RunStartedEvent(thread_id=thread_id, run_id=run_id))
        try:
            result = await session.next_turn(req.message)
            yield sse(StateSnapshotEvent(snapshot=result.state))

            if result.question is not None:
                for ev in text_message_events(uuid.uuid4().hex, result.question):
                    yield sse(ev)

            if result.blueprint is not None:
                for a2ui_msg in build_blueprint_surface(result.blueprint):
                    payload: dict[str, Any] = a2ui_msg.model_dump(by_alias=True)
                    yield sse(CustomEvent(name="a2ui", value=payload))
                _sessions.pop(req.session_id, None)  # session complete

        except Exception as exc:  # surface, never swallow
            logger.exception("discovery turn failed")
            yield sse(RunErrorEvent(message=str(exc)))
        finally:
            yield sse(RunFinishedEvent(thread_id=thread_id, run_id=run_id))

    return StreamingResponse(generate(), media_type="text/event-stream")
```

Modify `src/qwenpaw/app/routers/__init__.py` — add the import next to the other imports and register it next to `skills_stream_router`:

```python
from .discovery_stream import router as discovery_stream_router
```

```python
router.include_router(discovery_stream_router)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/app/routers/test_discovery_stream_router.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Run the AG-UI + A2UI backend suite together**

Run: `python -m pytest tests/unit/agui tests/unit/a2ui tests/unit/discovery tests/unit/app/routers/test_discovery_stream_router.py -v`
Expected: PASS (all)

- [ ] **Step 6: Commit**

```bash
git add src/qwenpaw/app/routers/discovery_stream.py src/qwenpaw/app/routers/__init__.py tests/unit/app/routers/test_discovery_stream_router.py
git commit -m "feat(app): discovery SSE router streaming AG-UI events + A2UI surfaces"
```

---

## PHASE D — Frontend: tipos + cliente SSE

### Task 8: Tipos TS dos protocolos

**Files:**
- Create: `console/src/api/types/agui.ts`
- Create: `console/src/api/types/a2ui.ts`
- Modify: `console/src/api/types/index.ts` (re-export, seguindo o padrão do diretório)

- [ ] **Step 1: Write the types (no test — pure types; exercised by Task 9/10)**

```typescript
// console/src/api/types/agui.ts
export type AguiEvent =
  | { type: "RUN_STARTED"; threadId: string; runId: string }
  | { type: "RUN_FINISHED"; threadId: string; runId: string }
  | { type: "RUN_ERROR"; message: string; code?: string }
  | { type: "TEXT_MESSAGE_START"; messageId: string; role?: string }
  | { type: "TEXT_MESSAGE_CONTENT"; messageId: string; delta: string }
  | { type: "TEXT_MESSAGE_END"; messageId: string }
  | { type: "STATE_SNAPSHOT"; snapshot: Record<string, unknown> }
  | { type: "STATE_DELTA"; delta: Array<Record<string, unknown>> }
  | { type: "CUSTOM"; name: string; value: Record<string, unknown> };
```

```typescript
// console/src/api/types/a2ui.ts
export interface A2uiComponent {
  id: string;
  type: string;
  properties: Record<string, unknown>;
  children: string[];
}

export type A2uiMessage =
  | { messageType: "createSurface"; surfaceId: string; root: string }
  | { messageType: "updateComponents"; surfaceId: string; components: A2uiComponent[] }
  | { messageType: "updateDataModel"; surfaceId: string; data: Record<string, unknown> }
  | { messageType: "deleteSurface"; surfaceId: string };

export interface A2uiSurface {
  surfaceId: string;
  root: string;
  components: Record<string, A2uiComponent>; // id -> component
  data: Record<string, unknown>;
}
```

Add to `console/src/api/types/index.ts` (follow the existing re-export style in that file):

```typescript
export * from "./agui";
export * from "./a2ui";
```

- [ ] **Step 2: Typecheck**

Run: `cd console && npx tsc --noEmit -p tsconfig.app.json`
Expected: no new errors from these files.

- [ ] **Step 3: Commit**

```bash
git add console/src/api/types/agui.ts console/src/api/types/a2ui.ts console/src/api/types/index.ts
git commit -m "feat(console): AG-UI + A2UI TypeScript types"
```

---

### Task 9: Cliente SSE `discoveryApi.streamTurn`

**Files:**
- Create: `console/src/api/modules/discovery.ts`
- Test: `console/src/api/modules/discovery.test.ts`

Como o turno é um POST que devolve `text/event-stream`, usamos `fetch` + leitura do `ReadableStream` (não `EventSource`, que só faz GET). Uma função `parseSseChunk` isolada e pura facilita o teste.

- [ ] **Step 1: Write the failing test**

```typescript
// console/src/api/modules/discovery.test.ts
import { describe, it, expect } from "vitest";
import { parseSseFrames } from "./discovery";

describe("parseSseFrames", () => {
  it("extracts JSON objects from complete data frames", () => {
    const buf =
      'data: {"type":"RUN_STARTED","threadId":"t","runId":"r"}\n\n' +
      'data: {"type":"TEXT_MESSAGE_CONTENT","messageId":"m","delta":"oi"}\n\n';
    const { events, rest } = parseSseFrames(buf);
    expect(events.map((e) => (e as { type: string }).type)).toEqual([
      "RUN_STARTED",
      "TEXT_MESSAGE_CONTENT",
    ]);
    expect(rest).toBe("");
  });

  it("keeps an incomplete trailing frame in rest", () => {
    const buf = 'data: {"type":"RUN_FINISHED"}\n\ndata: {"type":"CUST';
    const { events, rest } = parseSseFrames(buf);
    expect(events).toHaveLength(1);
    expect(rest).toBe('data: {"type":"CUST');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd console && npx vitest run src/api/modules/discovery.test.ts`
Expected: FAIL — cannot find `./discovery` / `parseSseFrames` not exported.

- [ ] **Step 3: Write minimal implementation**

```typescript
// console/src/api/modules/discovery.ts
import { getApiUrl, getApiToken } from "../config";
import { buildAuthHeaders } from "../authHeaders";
import type { AguiEvent } from "../types/agui";

/**
 * Split an SSE buffer into parsed JSON events plus the unparsed remainder.
 * Pure + synchronous so it is unit-testable without a network stream.
 */
export function parseSseFrames(buffer: string): {
  events: unknown[];
  rest: string;
} {
  const events: unknown[] = [];
  let rest = buffer;
  let idx: number;
  while ((idx = rest.indexOf("\n\n")) !== -1) {
    const frame = rest.slice(0, idx);
    rest = rest.slice(idx + 2);
    const line = frame.split("\n").find((l) => l.startsWith("data: "));
    if (!line) continue;
    const json = line.slice("data: ".length);
    try {
      events.push(JSON.parse(json));
    } catch {
      // malformed frame: skip it (never throw inside the stream loop)
    }
  }
  return { events, rest };
}

export const discoveryApi = {
  /**
   * Advance the interview by one turn; invoke onEvent for each AG-UI event.
   * Resolves when the turn's stream ends.
   */
  async streamTurn(
    sessionId: string,
    message: string | null,
    onEvent: (ev: AguiEvent) => void,
  ): Promise<void> {
    const resp = await fetch(getApiUrl("/discovery/stream"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...buildAuthHeaders(getApiToken()),
      },
      body: JSON.stringify({ session_id: sessionId, message }),
    });
    if (!resp.body) throw new Error("discovery stream: no response body");

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const { events, rest } = parseSseFrames(buffer);
      buffer = rest;
      for (const ev of events) onEvent(ev as AguiEvent);
    }
  },
};
```

> Verificar a assinatura real de `buildAuthHeaders` e `getApiToken` em `console/src/api/authHeaders.ts` / `config.ts` e ajustar a chamada se divergir (o teste mocka ambos, então o unit test não depende disso).

- [ ] **Step 4: Run test to verify it passes**

Run: `cd console && npx vitest run src/api/modules/discovery.test.ts`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add console/src/api/modules/discovery.ts console/src/api/modules/discovery.test.ts
git commit -m "feat(console): discovery SSE client (fetch + SSE frame parser)"
```

---

## PHASE E — Frontend: renderer A2UI → Ant Design

### Task 10: Catálogo + renderer A2UI

**Files:**
- Create: `console/src/components/a2ui/catalog.ts`
- Create: `console/src/components/a2ui/A2uiRenderer.tsx`
- Create: `console/src/components/a2ui/surfaceReducer.ts`
- Test: `console/src/components/a2ui/A2uiRenderer.test.tsx`

`surfaceReducer` aplica as 4 mensagens A2UI a um `A2uiSurface` (estado), e `A2uiRenderer` percorre a adjacency-list a partir do `root`. Componente desconhecido → fallback visível.

- [ ] **Step 1: Write the failing test**

```tsx
// console/src/components/a2ui/A2uiRenderer.test.tsx
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { applyA2uiMessage, emptySurface } from "./surfaceReducer";
import { A2uiRenderer } from "./A2uiRenderer";
import type { A2uiMessage } from "../../api/types/a2ui";

const MSGS: A2uiMessage[] = [
  { messageType: "createSurface", surfaceId: "bp", root: "root" },
  {
    messageType: "updateComponents",
    surfaceId: "bp",
    components: [
      { id: "root", type: "Column", properties: {}, children: ["h", "u"] },
      { id: "h", type: "Heading", properties: { text: "Time proposto" }, children: [] },
      { id: "u", type: "Unknownz", properties: { text: "x" }, children: [] },
    ],
  },
];

function buildSurface() {
  let s = emptySurface("bp");
  for (const m of MSGS) s = applyA2uiMessage(s, m);
  return s;
}

describe("A2uiRenderer", () => {
  it("renders a heading from the adjacency list", () => {
    render(<A2uiRenderer surface={buildSurface()} />);
    expect(screen.getByText("Time proposto")).toBeTruthy();
  });

  it("shows a visible fallback for unknown component types", () => {
    render(<A2uiRenderer surface={buildSurface()} />);
    expect(screen.getByText(/Unknownz/)).toBeTruthy();
  });
});

describe("surfaceReducer", () => {
  it("createSurface sets the root", () => {
    const s = applyA2uiMessage(emptySurface("bp"), MSGS[0]);
    expect(s.root).toBe("root");
  });

  it("updateComponents indexes components by id", () => {
    const s = buildSurface();
    expect(Object.keys(s.components).sort()).toEqual(["h", "root", "u"]);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd console && npx vitest run src/components/a2ui/A2uiRenderer.test.tsx`
Expected: FAIL — modules not found.

- [ ] **Step 3: Write minimal implementation**

```typescript
// console/src/components/a2ui/surfaceReducer.ts
import type { A2uiMessage, A2uiSurface } from "../../api/types/a2ui";

export function emptySurface(surfaceId: string): A2uiSurface {
  return { surfaceId, root: "", components: {}, data: {} };
}

export function applyA2uiMessage(
  surface: A2uiSurface,
  msg: A2uiMessage,
): A2uiSurface {
  switch (msg.messageType) {
    case "createSurface":
      return { ...surface, surfaceId: msg.surfaceId, root: msg.root };
    case "updateComponents": {
      const components = { ...surface.components };
      for (const c of msg.components) components[c.id] = c;
      return { ...surface, components };
    }
    case "updateDataModel":
      return { ...surface, data: { ...surface.data, ...msg.data } };
    case "deleteSurface":
      return emptySurface(msg.surfaceId);
    default:
      return surface;
  }
}
```

```typescript
// console/src/components/a2ui/catalog.ts
import type { ComponentType } from "react";
import { Card, Col, Divider, List, Row, Tag, Typography } from "antd";

// Renderers receive the resolved props + already-rendered children.
export interface CatalogProps {
  properties: Record<string, unknown>;
  children?: React.ReactNode;
}

const text = (p: Record<string, unknown>) => String(p.text ?? "");

export const A2UI_CATALOG: Record<string, ComponentType<CatalogProps>> = {
  Column: ({ children }) => <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>{children}</div>,
  Row: ({ children }) => <Row gutter={[8, 8]}>{children}</Row>,
  Card: ({ children }) => <Card>{children}</Card>,
  List: ({ children }) => <List>{children}</List>,
  Heading: ({ properties }) => <Typography.Title level={5}>{text(properties)}</Typography.Title>,
  Text: ({ properties }) => <Typography.Text>{text(properties)}</Typography.Text>,
  Tag: ({ properties }) => <Tag>{text(properties)}</Tag>,
  Button: ({ properties }) => <button type="button">{text(properties)}</button>,
  Divider: () => <Divider />,
};
```

```tsx
// console/src/components/a2ui/A2uiRenderer.tsx
import { Typography } from "antd";
import type { A2uiSurface } from "../../api/types/a2ui";
import { A2UI_CATALOG } from "./catalog";

function renderNode(surface: A2uiSurface, id: string): React.ReactNode {
  const node = surface.components[id];
  if (!node) return null;
  const children = node.children.map((cid) => (
    <span key={cid}>{renderNode(surface, cid)}</span>
  ));
  const Comp = A2UI_CATALOG[node.type];
  if (!Comp) {
    // Visible fallback — never a blank screen.
    return (
      <Typography.Text type="warning">
        [componente desconhecido: {node.type}] {String(node.properties.text ?? "")}
      </Typography.Text>
    );
  }
  return <Comp properties={node.properties}>{children}</Comp>;
}

export function A2uiRenderer({ surface }: { surface: A2uiSurface }) {
  if (!surface.root) return null;
  return <>{renderNode(surface, surface.root)}</>;
}
```

> Confirmar que `@testing-library/react` e `@testing-library/jest-dom` (ou matchers do vitest) estão nas devDependencies do `console/package.json` e que o setup do vitest (`console/src/test/`) os registra. Se `toBeTruthy()` for usado (como no teste acima), nenhum matcher extra é necessário.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd console && npx vitest run src/components/a2ui/A2uiRenderer.test.tsx`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add console/src/components/a2ui/
git commit -m "feat(console): A2UI renderer + Ant Design catalog + surface reducer"
```

---

## PHASE F — Frontend: página Discovery

### Task 11: Página `pages/Discovery` ligando tudo

**Files:**
- Create: `console/src/pages/Discovery/index.tsx`
- Modify: roteamento do console (onde as rotas são declaradas — provavelmente `console/src/App.tsx` ou um arquivo de rotas; seguir o padrão das páginas existentes em `pages/Chat`).

> Esta task é de integração de UI (sem teste unitário novo — a lógica testável já está coberta nas tasks 9/10). Validação é manual via `npm run dev` no console.

- [ ] **Step 1: Implement the page**

```tsx
// console/src/pages/Discovery/index.tsx
import { useCallback, useRef, useState } from "react";
import { Button, Input, Space, Typography } from "antd";
import { discoveryApi } from "../../api/modules/discovery";
import type { AguiEvent } from "../../api/types/agui";
import type { A2uiMessage, A2uiSurface } from "../../api/types/a2ui";
import { applyA2uiMessage, emptySurface } from "../../components/a2ui/surfaceReducer";
import { A2uiRenderer } from "../../components/a2ui/A2uiRenderer";

export default function DiscoveryPage() {
  const sessionId = useRef(`sess-${Date.now()}`).current;
  const [transcript, setTranscript] = useState<string[]>([]);
  const [state, setState] = useState<Record<string, unknown>>({});
  const [surface, setSurface] = useState<A2uiSurface | null>(null);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [started, setStarted] = useState(false);

  const runTurn = useCallback(
    async (message: string | null) => {
      setBusy(true);
      let pendingText = "";
      let surf = surface ?? emptySurface("blueprint");
      await discoveryApi.streamTurn(sessionId, message, (ev: AguiEvent) => {
        switch (ev.type) {
          case "TEXT_MESSAGE_CONTENT":
            pendingText += ev.delta;
            break;
          case "STATE_SNAPSHOT":
            setState(ev.snapshot);
            break;
          case "CUSTOM":
            if (ev.name === "a2ui") {
              surf = applyA2uiMessage(surf, ev.value as unknown as A2uiMessage);
              setSurface({ ...surf });
            }
            break;
          case "RUN_ERROR":
            setTranscript((t) => [...t, `⚠️ ${ev.message}`]);
            break;
          default:
            break;
        }
      });
      if (pendingText) setTranscript((t) => [...t, `🤖 ${pendingText}`]);
      setBusy(false);
    },
    [sessionId, surface],
  );

  const start = async () => {
    setStarted(true);
    await runTurn(null);
  };

  const send = async () => {
    const msg = input.trim();
    if (!msg) return;
    setTranscript((t) => [...t, `🧑 ${msg}`]);
    setInput("");
    await runTurn(msg);
  };

  return (
    <div style={{ padding: 24, maxWidth: 920, margin: "0 auto" }}>
      <Typography.Title level={3}>Descoberta do seu time de agentes</Typography.Title>
      {!started ? (
        <Button type="primary" onClick={start} loading={busy}>
          Começar entrevista
        </Button>
      ) : (
        <Space direction="vertical" style={{ width: "100%" }} size="large">
          <div>
            {transcript.map((line, i) => (
              <Typography.Paragraph key={i} style={{ marginBottom: 4 }}>
                {line}
              </Typography.Paragraph>
            ))}
          </div>
          {!surface && (
            <Space.Compact style={{ width: "100%" }}>
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onPressEnter={send}
                placeholder="Responda aqui…"
                disabled={busy}
              />
              <Button type="primary" onClick={send} loading={busy}>
                Enviar
              </Button>
            </Space.Compact>
          )}
          {surface && (
            <div>
              <Typography.Title level={4}>Time proposto</Typography.Title>
              <A2uiRenderer surface={surface} />
            </div>
          )}
          <details>
            <summary>Estado do discovery (debug)</summary>
            <pre>{JSON.stringify(state, null, 2)}</pre>
          </details>
        </Space>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Register the route**

Inspecionar como as páginas são roteadas (ex.: `console/src/App.tsx` ou um `routes` central — seguir `pages/Chat`). Adicionar uma rota `"/discovery"` apontando para `DiscoveryPage` e, se houver menu/nav lateral, um item "Descoberta". Replicar exatamente o padrão de uma rota existente (lazy import se as outras usam lazy).

Exemplo (ajustar ao padrão real do arquivo de rotas):

```tsx
// onde as outras rotas são declaradas
const DiscoveryPage = lazy(() => import("./pages/Discovery"));
// ...
<Route path="/discovery" element={<DiscoveryPage />} />
```

- [ ] **Step 3: Typecheck + build**

Run: `cd console && npx tsc --noEmit -p tsconfig.app.json && npm run build`
Expected: build passa sem erros novos.

- [ ] **Step 4: Manual smoke test**

Run (dois terminais): backend do qwenpaw + `cd console && npm run dev`. Abrir `/discovery`, clicar "Começar entrevista", responder 3 perguntas, ver o time renderizado como cards Ant Design.
Expected: perguntas chegam por streaming; ao final, cards do time + tags de integração + perguntas em aberto aparecem.

- [ ] **Step 5: Commit**

```bash
git add console/src/pages/Discovery/ console/src/App.tsx
git commit -m "feat(console): Discovery page wiring AG-UI stream + A2UI surface"
```

---

## PHASE G — Fechamento

### Task 12: Suíte completa afetada + gate

- [ ] **Step 1: Backend — rodar a suíte das novas áreas**

Run: `python -m pytest tests/unit/agui tests/unit/a2ui tests/unit/discovery tests/unit/app/routers/test_discovery_stream_router.py -v`
Expected: PASS (todas).

- [ ] **Step 2: Frontend — rodar vitest das novas áreas**

Run: `cd console && npx vitest run src/api/modules/discovery.test.ts src/components/a2ui/A2uiRenderer.test.tsx`
Expected: PASS (todas).

- [ ] **Step 3: Lint/format conforme o projeto**

Run (conforme `Makefile`/`pyproject.toml` do projeto): o linter Python configurado (ex.: `ruff`/`flake8`) sobre `src/qwenpaw/agui src/qwenpaw/a2ui src/qwenpaw/discovery`; e `cd console && npm run lint`.
Expected: sem erros novos.

- [ ] **Step 4: Gate `/agentscope-guardian` (backend)**

Como toda mudança em `src/qwenpaw/**` é gated, a execução via `/dev-team` aciona o `/agentscope-guardian`. Os módulos novos só usam Pydantic/FastAPI (sem APIs do AgentScope), então a aprovação deve ser direta; se o guardião apontar `concerns`, corrigir antes de fechar.

- [ ] **Step 5: Commit final / PR**

```bash
git add -A
git commit -m "chore(discovery-ui): A2UI + AG-UI cycle complete (tests green)"
```

---

## Self-Review (preenchido pelo autor do plano)

**Cobertura do spec:**
- §1 visão + AG-UI=transporte / A2UI=UI generativa → Tasks 1–4, 7, 9–11. ✔
- §2 arquitetura (`agui/`, `a2ui/`, adapter/router, console) → Tasks 1–11. ✔
- §3 subset de eventos AG-UI + catálogo A2UI→Ant Design → Task 1 (eventos), Task 10 (catálogo). ✔
- §4 unidades isoladas → cada módulo numa task própria. ✔
- §5 fluxo de dados (RUN_STARTED → texto → estado → CUSTOM/A2UI → RUN_FINISHED) → Task 7 (router) + Task 11 (página). ✔
- §6 interatividade subset mínimo → inbound de texto (Task 7/11); ação "confirmar/seguir" = a página fecha ao receber a surface (sem novo turno) — o event-type de ação fica para a camada futura, conforme o spec ("sem fechar a porta"). ✔
- §7 erros sem falha silenciosa → `RUN_ERROR` no router (Task 7); fallback visível no renderer (Task 10). ✔ Testes pytest+vitest → todas as tasks. ✔
- §8 critérios de aceite → Task 11 (smoke) + Task 12 (suíte). ✔

**Placeholder scan:** sem "TBD/TODO". As notas de "verificar assinatura de `buildAuthHeaders`/rota real" são passos de verificação contra o código existente (mockados nos testes), não comportamento a inventar.

**Consistência de tipos:** `Component{id,type,properties,children}` idêntico em `schema.py` (Py) e `a2ui.ts` (TS); `CustomEvent.value` (dict) ↔ `A2uiMessage`; `surface_id`/`surfaceId`, `messageType` consistentes via camelCase alias. `next_turn`/`TurnResult` idênticos entre `session.py`, `scripted_session.py` e o router. `parseSseFrames`/`streamTurn`/`applyA2uiMessage`/`emptySurface` usados com a mesma assinatura nos testes e na página.

**Nota de escopo:** o §6 do spec previa "um único event de ação"; na implementação a fatia fina não exige um turno de ação (a sessão completa ao emitir o blueprint), então o event-type de ação foi deixado para a camada futura sem perda — o seam (CUSTOM + inbound POST) já suporta adicioná-lo.
