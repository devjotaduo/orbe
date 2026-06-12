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
from .builder import build_blueprint_surface

__all__ = [
    "A2UIMessage",
    "Component",
    "CreateSurface",
    "DeleteSurface",
    "UpdateComponents",
    "UpdateDataModel",
    "build_blueprint_surface",
]

from .surface import (  # noqa: E402
    Node,
    button,
    card,
    column,
    heading,
    lst,
    row,
    surface,
    tag,
    text,
)

__all__ += [
    "Node",
    "surface",
    "column",
    "row",
    "card",
    "lst",
    "text",
    "heading",
    "tag",
    "button",
]
