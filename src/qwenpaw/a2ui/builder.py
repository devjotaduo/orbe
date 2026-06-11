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
