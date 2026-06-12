# -*- coding: utf-8 -*-
"""Memory Distillation Tool Plugin Entry Point."""

import importlib.util
import logging
import os

from qwenpaw.plugins.api import PluginApi

logger = logging.getLogger(__name__)

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_tool_module():
    """Load memory_distill_tool.py from this plugin's directory via importlib."""
    tool_path = os.path.join(_PLUGIN_DIR, "memory_distill_tool.py")
    spec = importlib.util.spec_from_file_location(
        "memory_distill_tool",
        tool_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Failed to load memory distill tool module from {tool_path}",
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MemoryDistillToolPlugin:
    """Memory Distillation Tool Plugin.

    Registers distill_memory, consolidate_memory, and inspect_memory tools
    into the Agent's toolkit (disabled by default — opt-in).
    """

    def register(self, api: PluginApi):
        """Register memory distillation tools.

        Args:
            api: PluginApi instance.
        """
        logger.info("Registering Memory Distillation tools...")
        tool = _load_tool_module()

        api.register_tool(
            tool_name="distill_memory",
            tool_func=tool.distill_memory,
            description=(
                "Distill daily notes into MEMORY.md using title-diffing "
                "to find genuinely new information."
            ),
            icon="🧠",
            enabled=False,
        )
        api.register_tool(
            tool_name="consolidate_memory",
            tool_func=tool.consolidate_memory,
            description=(
                "Run the full memory consolidation pipeline: "
                "distill, archive, clean, and audit."
            ),
            icon="🧠",
            enabled=False,
        )
        api.register_tool(
            tool_name="inspect_memory",
            tool_func=tool.inspect_memory,
            description=(
                "Inspect MEMORY.md and daily notes health, size, "
                "and recent activity."
            ),
            icon="🔍",
            enabled=False,
        )
        logger.info("Memory Distillation tool plugin registered")


# Export plugin instance
plugin = MemoryDistillToolPlugin()
