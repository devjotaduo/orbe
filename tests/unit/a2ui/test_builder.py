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


def _by_id(msgs):
    return {c.id: c for c in msgs[1].components}


def _walk(comps, cid):
    """Yield a component subtree following children AND itemTemplate refs."""
    c = comps[cid]
    yield c
    for ch in c.children:
        yield from _walk(comps, ch)
    tpl = c.properties.get("itemTemplate")
    if tpl:
        yield from _walk(comps, tpl)


def test_team_is_a_repeater_with_template():
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    comps = _by_id(msgs)
    reps = [
        c
        for c in msgs[1].components
        if c.type == "Repeater" and c.properties.get("bind") == "proposed_team"
    ]
    assert len(reps) == 1
    assert reps[0].properties["itemTemplate"] in comps
    # The team repeater is wired into the root, the template is not.
    root = msgs[1].components[0]
    assert reps[0].id in root.children
    assert reps[0].properties["itemTemplate"] not in root.children


def test_template_binds_are_relative():
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    comps = _by_id(msgs)
    rep = next(
        c
        for c in msgs[1].components
        if c.type == "Repeater" and c.properties.get("bind") == "proposed_team"
    )
    binds = [
        c.properties["bind"]
        for c in _walk(comps, rep.properties["itemTemplate"])
        if "bind" in c.properties
    ]
    assert binds
    assert all(not b.startswith("proposed_team/") for b in binds)


def test_card_template_fields_and_string_lists():
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    comps = _by_id(msgs)
    rep = next(
        c
        for c in msgs[1].components
        if c.type == "Repeater" and c.properties.get("bind") == "proposed_team"
    )
    tpl = list(_walk(comps, rep.properties["itemTemplate"]))
    binds = {
        (c.type, c.properties.get("bind"))
        for c in tpl
        if "bind" in c.properties
    }
    assert ("TextInput", "name") in binds
    assert ("TextInput", "role") in binds
    assert ("TextArea", "objective") in binds
    # tasks/tools_integrations are nested repeaters of TextInput bind=".".
    assert ("Repeater", "tasks") in binds
    assert ("Repeater", "tools_integrations") in binds
    for nested in [c for c in tpl if c.type == "Repeater"]:
        item = comps[nested.properties["itemTemplate"]]
        inputs = [
            c
            for c in _walk(comps, item.id)
            if c.type == "TextInput" and c.properties.get("bind") == "."
        ]
        assert inputs, f"no bind='.' input in {nested.id} template"


def test_structural_buttons_present():
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    actions = {}
    for c in msgs[1].components:
        if c.type == "Button":
            action = c.properties.get("action", {})
            actions.setdefault(action.get("name"), action.get("params", {}))
    for name in (
        "add_agent",
        "remove_agent",
        "move_agent",
        "add_item",
        "remove_item",
        "approve_team",
    ):
        assert name in actions, f"missing structural button {name}"
    # Per-card buttons rely on the renderer-injected repeater index.
    assert actions["remove_agent"]["indexFromRepeater"] is True
    assert actions["remove_agent"]["path"] == "proposed_team"
    assert actions["move_agent"]["indexFromRepeater"] is True
    assert actions["move_agent"]["path"] == "proposed_team"
    assert actions["remove_item"]["indexFromRepeater"] is True
    # add_item paths are template-relative, absolutized by the renderer.
    assert actions["add_item"]["pathFromBase"] is True


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
        tpl = c.properties.get("itemTemplate")
        if tpl is not None:
            assert tpl in ids, f"dangling itemTemplate id {tpl}"


def test_every_component_reachable_via_children_or_item_template():
    # Templates are NOT children of the root: they live in the flat list and
    # are reachable only through Repeater itemTemplate references.
    msgs = build_blueprint_surface(BLUEPRINT, surface_id="bp")
    comps = {c.id: c for c in msgs[1].components}
    seen = set()
    stack = [msgs[0].root]
    while stack:
        cid = stack.pop()
        if cid in seen:
            continue
        seen.add(cid)
        c = comps[cid]
        stack.extend(c.children)
        tpl = c.properties.get("itemTemplate")
        if tpl:
            stack.append(tpl)
    assert seen == set(comps), f"orphan components: {set(comps) - seen}"
