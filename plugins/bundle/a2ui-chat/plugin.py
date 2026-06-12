# -*- coding: utf-8 -*-
"""A2UI Chat plugin — registra a tool ``render_ui``."""
from __future__ import annotations

import importlib.util
import logging
import os

from qwenpaw.plugins.api import PluginApi

logger = logging.getLogger(__name__)

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_tool_module():
    """Carrega a2ui_tool.py do diretório do plugin via importlib."""
    tool_path = os.path.join(_PLUGIN_DIR, "a2ui_tool.py")
    spec = importlib.util.spec_from_file_location(
        "a2ui_tool",
        tool_path,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class A2uiChatPlugin:
    """Registra a tool ``render_ui`` (render A2UI no chat)."""

    def register(self, api: PluginApi) -> None:
        tool = _load_tool_module()

        api.register_tool(
            tool_name="render_ui",
            tool_func=tool.render_ui,
            description="Renderiza uma surface A2UI no chat",
            icon="🎨",
            enabled=False,
        )
        logger.info("a2ui-chat plugin registrado")


plugin = A2uiChatPlugin()
