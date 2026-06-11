# -*- coding: utf-8 -*-
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
