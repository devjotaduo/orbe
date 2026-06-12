# -*- coding: utf-8 -*-
# pylint: disable=relative-beyond-top-level
"""QwenPaw Plugin Kit entry point.

This plugin is intentionally small and demonstrates the supported plugin
surfaces without touching QwenPaw core files:

- backend PluginApi registration
- startup and shutdown hooks
- FastAPI router under /api/plugin-kit
- agent tool registration
- frontend bundle declared in plugin.json
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter

from qwenpaw.plugins.api import PluginApi

from .tools import plugin_kit_describe_elements

logger = logging.getLogger(__name__)

PLUGIN_ID = "qwenpaw-plugin-kit"


def _plugin_elements() -> list[dict[str, str]]:
    """Return the extension elements this sample plugin demonstrates."""
    return [
        {
            "id": "manifest",
            "name": "plugin.json",
            "description": (
                "Manifesto com id, versao, entradas, "
                "dependencias e metadados."
            ),
        },
        {
            "id": "backend",
            "name": "plugin.py",
            "description": "Entrada Python que exporta plugin.register(api).",
        },
        {
            "id": "router",
            "name": "HTTP router",
            "description": "APIRouter montado em /api pelo PluginApi.",
        },
        {
            "id": "hooks",
            "name": "Hooks",
            "description": "Callbacks de startup e shutdown com prioridade.",
        },
        {
            "id": "tool",
            "name": "Agent tool",
            "description": "Funcao registrada para uso pelo agente.",
        },
        {
            "id": "frontend",
            "name": "Frontend bundle",
            "description": (
                "JavaScript carregado pelo Console via window.QwenPaw."
            ),
        },
        {
            "id": "i18n",
            "name": "pt-BR",
            "description": (
                "Campos localizados em portugues no manifesto e na UI."
            ),
        },
    ]


def build_router() -> APIRouter:
    """Build the plugin API router.

    The PluginApi mounts this router under /api + prefix. With
    prefix="/plugin-kit", the endpoints are served at /api/plugin-kit.
    """
    router = APIRouter()

    @router.get("/status")
    def status() -> dict[str, Any]:
        """Return a small health payload for the sample plugin."""
        return {
            "id": PLUGIN_ID,
            "ok": True,
            "language": "pt-BR",
            "message": "Plugin kit carregado.",
        }

    @router.get("/elements")
    def elements() -> dict[str, Any]:
        """Return the plugin elements demonstrated by this sample."""
        return {"items": _plugin_elements()}

    return router


class QwenPawPluginKit:
    """Basic plugin kit demonstrating QwenPaw plugin extension surfaces."""

    def register(self, api: PluginApi) -> None:
        """Register routes, hooks, and tools."""
        logger.info("Registering QwenPaw Plugin Kit")

        api.register_http_router(
            build_router(),
            prefix="/plugin-kit",
            tags=["plugin-kit"],
        )
        api.register_startup_hook(
            hook_name="plugin_kit_startup",
            callback=self._on_startup,
            priority=100,
        )
        api.register_shutdown_hook(
            hook_name="plugin_kit_shutdown",
            callback=self._on_shutdown,
            priority=100,
        )
        api.register_tool(
            tool_name="plugin_kit_describe_elements",
            tool_func=plugin_kit_describe_elements,
            description=(
                "Describe the basic QwenPaw plugin elements "
                "available to developers."
            ),
            icon="🧩",
        )

        logger.info("QwenPaw Plugin Kit registered")

    def _on_startup(self) -> None:
        """Run when QwenPaw starts."""
        logger.info("QwenPaw Plugin Kit startup hook executed")

    def _on_shutdown(self) -> None:
        """Run when QwenPaw shuts down."""
        logger.info("QwenPaw Plugin Kit shutdown hook executed")


plugin = QwenPawPluginKit()
