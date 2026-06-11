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
