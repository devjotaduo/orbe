# -*- coding: utf-8 -*-
"""A2UI Chat plugin — registra a tool ``render_ui``."""
from __future__ import annotations

import importlib.util
import logging
import os

from qwenpaw.plugins.api import PluginApi

logger = logging.getLogger(__name__)

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_module(name: str, filename: str):
    """Carrega ``filename`` do diretório do plugin via importlib."""
    path = os.path.join(_PLUGIN_DIR, filename)
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class A2uiChatPlugin:
    """Registra a tool ``render_ui`` (render A2UI no chat)."""

    def register(self, api: PluginApi) -> None:
        tool = _load_module("a2ui_tool", "a2ui_tool.py")

        api.register_tool(
            tool_name="render_ui",
            tool_func=tool.render_ui,
            description="Renderiza uma surface A2UI no chat",
            icon="🎨",
            enabled=False,
        )

        action_router = _load_module(
            "a2ui_action_router",
            "action_router.py",
        )
        api.register_http_router(action_router.router, prefix="/a2ui")

        logger.info("a2ui-chat plugin registrado")


plugin = A2uiChatPlugin()
