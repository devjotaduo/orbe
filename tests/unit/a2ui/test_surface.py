# -*- coding: utf-8 -*-
from qwenpaw.a2ui.surface import card, column, surface, tag, text
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
    msgs = surface(
        "s1",
        column("root", [text("t", "abc"), tag("g", "z")]),
    )
    comps = {c.id: c for c in msgs[1].components}
    assert comps["t"].properties["text"] == "abc"
    assert comps["g"].properties["text"] == "z"


def test_data_appends_update_data_model():
    from qwenpaw.a2ui.schema import UpdateDataModel

    msgs = surface(
        "s1",
        column("root", [text("t", "x")]),
        data={"k": 1},
    )
    assert len(msgs) == 3
    assert isinstance(msgs[2], UpdateDataModel)
    assert msgs[2].data == {"k": 1}
