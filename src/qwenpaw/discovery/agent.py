# -*- coding: utf-8 -*-
"""Fábrica do discovery agent (AgentScope v2 Agent)."""
from __future__ import annotations

from agentscope.agent import Agent, ReActConfig

from ..agents.model_factory import create_model_and_formatter
from .prompts import build_discovery_system_prompt
from .tools import DiscoverySession


def build_discovery_agent(
    session: DiscoverySession,
    max_iters: int = 6,
) -> Agent:
    """Monta o Agent de discovery com o toolkit da sessão e o modelo ativo."""
    model, formatter = create_model_and_formatter()
    # Attach do formatter — padrão de react_agent.py ~171-180.
    if formatter is not None:
        innermost = model
        while hasattr(innermost, "_inner"):
            innermost = innermost._inner
        while hasattr(innermost, "_model"):
            innermost = innermost._model
        if hasattr(innermost, "formatter"):
            innermost.formatter = formatter
    return Agent(
        name="DiscoveryAgent",
        system_prompt=build_discovery_system_prompt(),
        model=model,
        toolkit=session.build_toolkit(),
        react_config=ReActConfig(max_iters=max_iters),
    )
