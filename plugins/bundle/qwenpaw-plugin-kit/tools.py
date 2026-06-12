# -*- coding: utf-8 -*-
"""Example tool functions for QwenPaw Plugin Kit."""

from __future__ import annotations


def plugin_kit_describe_elements(language: str = "pt-BR") -> str:
    """Describe available plugin elements.

    Args:
        language: Response language. Supports "pt-BR" and "en-US".
    """
    if language == "en-US":
        return (
            "QwenPaw plugins can use plugin.json, Python backend entrypoints, "
            "startup/shutdown hooks, FastAPI routers, agent tools, metadata "
            "config fields, frontend menu entries, routes, slots, and chat "
            "customizations."
        )

    return (
        "Plugins QwenPaw podem usar plugin.json, entrada backend em Python, "
        "hooks de startup/shutdown, rotas FastAPI, ferramentas do agente, "
        "campos de configuracao em meta, menus frontend, rotas, slots e "
        "customizacoes do chat."
    )
