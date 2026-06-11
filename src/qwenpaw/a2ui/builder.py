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


def build_blueprint_surface(
    blueprint: dict[str, Any],
    surface_id: str = "blueprint",
) -> list[A2UIMessage]:
    """Build createSurface + updateComponents + updateDataModel msgs.

    Layout: a root Column with a title, one Card per proposed team member
    (bound TextInputs for name/role + TextArea for objective + integration
    Tags), then an areas List, an open-questions List and an approve_team
    Button. Editable fields bind into the raw blueprint that rides in
    updateDataModel (paths like ``proposed_team/0/name``).
    """
    comps: list[Component] = []
    root_children: list[str] = []

    company = blueprint.get("company_profile", {}) or {}
    title = company.get("name") or company.get("segment") or "Time proposto"
    comps.append(_heading("title", f"Time proposto — {title}"))
    root_children.append("title")

    # One card per team member (scalar fields are editable, bound by index).
    for i, member in enumerate(blueprint.get("proposed_team", []) or []):
        card_id = f"card-{i}"
        name_id, role_id = f"card-{i}-name", f"card-{i}-role"
        objective_id = f"card-{i}-objective"
        card_children = [name_id, role_id, objective_id]
        comps.append(_input(name_id, f"proposed_team/{i}/name", "Nome"))
        comps.append(_input(role_id, f"proposed_team/{i}/role", "Papel"))
        comps.append(
            _textarea(
                objective_id,
                f"proposed_team/{i}/objective",
                "Objetivo",
            ),
        )
        for j, integ in enumerate(member.get("tools_integrations", []) or []):
            tid = f"card-{i}-tool-{j}"
            comps.append(_tag(tid, str(integ)))
            card_children.append(tid)
        comps.append(
            Component(id=card_id, type="Card", children=card_children),
        )
        root_children.append(card_id)

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
