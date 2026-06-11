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
