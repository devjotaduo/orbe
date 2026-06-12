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


def _button(
    cid: str,
    text: str,
    action: dict[str, Any],
    variant: str | None = None,
) -> Component:
    props: dict[str, Any] = {"text": text, "action": action}
    if variant:
        props["variant"] = variant
    return Component(id=cid, type="Button", properties=props)


def _string_list_section(
    prefix: str,
    bind: str,
    title: str,
    add_label: str,
) -> tuple[list[Component], list[str]]:
    """Editable string-array section for the card template.

    Returns (components, card_children_ids). The item template is a Row of
    ``TextInput bind="."`` (the item itself) + a remove_item Button whose
    index/path are injected by the renderer (``indexFromRepeater``). The
    add_item Button carries a template-relative path absolutized by the
    renderer (``pathFromBase``).
    """
    item_id = f"{prefix}-item"
    comps = [
        Component(
            id=item_id,
            type="Row",
            children=[f"{prefix}-item-input", f"{prefix}-item-remove"],
        ),
        _input(f"{prefix}-item-input", ".", ""),
        _button(
            f"{prefix}-item-remove",
            "Remover",
            {"name": "remove_item", "params": {"indexFromRepeater": True}},
        ),
        _text(f"{prefix}-title", title),
        Component(
            id=f"{prefix}-rep",
            type="Repeater",
            properties={"bind": bind, "itemTemplate": item_id},
        ),
        _button(
            f"{prefix}-add",
            add_label,
            {
                "name": "add_item",
                "params": {"path": bind, "pathFromBase": True},
            },
        ),
    ]
    children = [f"{prefix}-title", f"{prefix}-rep", f"{prefix}-add"]
    return comps, children


def _card_template() -> list[Component]:
    """Single per-agent card template (binds RELATIVE to the team item).

    The template (``tpl-card`` and descendants) is appended to the flat
    component list but is NOT a child of the root: it is reachable only via
    the team Repeater's ``itemTemplate`` reference, which is a valid extra
    edge in the adjacency.
    """
    tasks, tasks_children = _string_list_section(
        "tpl-tasks",
        "tasks",
        "Tarefas",
        "+ Tarefa",
    )
    tools, tools_children = _string_list_section(
        "tpl-tools",
        "tools_integrations",
        "Integrações",
        "+ Integração",
    )
    per_card = {"indexFromRepeater": True, "path": "proposed_team"}
    actions = [
        Component(
            id="tpl-card-actions",
            type="Row",
            children=["tpl-card-up", "tpl-card-down", "tpl-card-remove"],
        ),
        _button(
            "tpl-card-up",
            "Mover ↑",
            {"name": "move_agent", "params": {**per_card, "dir": -1}},
        ),
        _button(
            "tpl-card-down",
            "Mover ↓",
            {"name": "move_agent", "params": {**per_card, "dir": 1}},
        ),
        _button(
            "tpl-card-remove",
            "Remover agente",
            {"name": "remove_agent", "params": dict(per_card)},
        ),
    ]
    card = Component(
        id="tpl-card",
        type="Card",
        children=[
            "tpl-card-name",
            "tpl-card-role",
            "tpl-card-objective",
            *tasks_children,
            *tools_children,
            "tpl-card-actions",
        ],
    )
    return [
        card,
        _input("tpl-card-name", "name", "Nome"),
        _input("tpl-card-role", "role", "Papel"),
        _textarea("tpl-card-objective", "objective", "Objetivo"),
        *tasks,
        *tools,
        *actions,
    ]


def build_blueprint_surface(
    blueprint: dict[str, Any],
    surface_id: str = "blueprint",
) -> list[A2UIMessage]:
    """Build createSurface + updateComponents + updateDataModel msgs.

    Layout: a root Column with a title, a ``Repeater`` over the proposed
    team that instantiates a single per-agent card template (binds RELATIVE
    to the item — ``name``, ``tasks``, ``.`` for string items), structural
    buttons (add/remove/move agents, add/remove string items) and the
    approve_team Button. The template components live in the flat list but
    are NOT children of the root: they are reachable only through the
    Repeater's ``itemTemplate`` reference (a valid extra adjacency edge).
    Editable fields bind into the raw blueprint riding in updateDataModel.
    """
    comps: list[Component] = []
    root_children: list[str] = []

    company = blueprint.get("company_profile", {}) or {}
    title = company.get("name") or company.get("segment") or "Time proposto"
    comps.append(_heading("title", f"Time proposto — {title}"))
    root_children.append("title")

    # One Repeater + a single card template instead of per-index cards: the
    # renderer instantiates the template per team member and rebinding
    # survives client-side add/remove/move without rebuilding the surface.
    comps.append(
        Component(
            id="team-rep",
            type="Repeater",
            properties={
                "bind": "proposed_team",
                "itemTemplate": "tpl-card",
            },
        ),
    )
    root_children.append("team-rep")
    comps.extend(_card_template())

    comps.append(
        _button(
            "add-agent-btn",
            "Adicionar agente",
            {"name": "add_agent"},
        ),
    )
    root_children.append("add-agent-btn")

    # Detected integrations as tags under a small section.
    integ_section_children: list[str] = []
    detected = blueprint.get("detected_integrations", []) or []
    for i, integ in enumerate(detected):
        tid = f"integ-{i}"
        comps.append(_tag(tid, integ.get("name", str(integ))))
        integ_section_children.append(tid)
    if integ_section_children:
        comps.append(_heading("integ-title", "Integrações detectadas"))
        comps.append(
            Component(
                id="integ-row",
                type="Row",
                children=integ_section_children,
            ),
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
        comps.append(
            Component(id="oq-list", type="List", children=oq_children),
        )
        root_children.extend(["oq-title", "oq-list"])

    # Approve action: ships the (possibly edited) data model back.
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

    root = Component(id="root", type="Column", children=root_children)
    # Root must be first (test asserts components[0] is the root).
    components = [root, *comps]

    return [
        CreateSurface(surface_id=surface_id, root="root"),
        UpdateComponents(surface_id=surface_id, components=components),
        UpdateDataModel(surface_id=surface_id, data=blueprint),
    ]
