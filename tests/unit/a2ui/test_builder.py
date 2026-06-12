# -*- coding: utf-8 -*-
from qwenpaw.a2ui.builder import build_blueprint_surface
from qwenpaw.a2ui.schema import (
    CreateSurface,
    UpdateComponents,
    UpdateDataModel,
)

BLUEPRINT = {
    "company_profile": {"segment": "ecommerce", "name": "Loja X"},
    "process_map": [
        {"name": "Atendimento", "description": "responder WhatsApp"},
    ],
    "detected_integrations": [{"kind": "messaging", "name": "WhatsApp"}],
    "proposed_team": [
        {
            "name": "Atendente WhatsApp",
            "role": "atendimento",
            "objective": "responder clientes",
            "tasks": ["responder dúvidas"],
            "tools_integrations": ["mcp:evolution-whatsapp"],
            "talks_to": [],
        },
    ],
    "roadmap": [{"order": 1, "title": "atendimento WhatsApp"}],
    "open_questions": ["qual volume de mensagens?"],
}


def test_returns_create_then_components_then_datamodel():
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    assert isinstance(msgs[0], CreateSurface)
    assert isinstance(msgs[1], UpdateComponents)
    assert isinstance(msgs[2], UpdateDataModel)
    assert msgs[0].surface_id == "bp"
    assert msgs[0].root == msgs[1].components[0].id  # root is first component


def test_one_card_per_team_member_with_bound_name_input():
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    comps = msgs[1].components
    cards = [c for c in comps if c.type == "Card"]
    assert len(cards) == 1
    name_inputs = [
        c
        for c in comps
        if c.type == "TextInput"
        and c.properties.get("bind") == "proposed_team/0/name"
    ]
    assert len(name_inputs) == 1
    assert name_inputs[0].id in cards[0].children


def test_team_member_fields_are_bound_inputs():
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    name_inputs = [
        c
        for c in msgs[1].components
        if c.type == "TextInput"
        and c.properties.get("bind") == "proposed_team/0/name"
    ]
    assert len(name_inputs) == 1
    role_inputs = [
        c
        for c in msgs[1].components
        if c.type == "TextInput"
        and c.properties.get("bind") == "proposed_team/0/role"
    ]
    assert len(role_inputs) == 1
    objective = [
        c
        for c in msgs[1].components
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
