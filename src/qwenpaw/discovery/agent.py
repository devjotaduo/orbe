# -*- coding: utf-8 -*-
"""Fábrica do discovery agent (AgentScope v2 Agent)."""
from __future__ import annotations

from agentscope.agent import Agent, ReActConfig
from agentscope.permission import PermissionMode

from ..agents.model_factory import create_model_and_formatter
from .prompts import build_discovery_system_prompt
from .tools import DiscoverySession


def build_discovery_agent(
    session: DiscoverySession,
    max_iters: int = 6,
) -> Agent:
    """Monta o Agent de discovery com o toolkit da sessão e o modelo ativo."""
    # No agent_id: always use the global active model for discovery sessions.
    model, formatter = create_model_and_formatter()
    # Attach do formatter — padrão de react_agent.py ~171-180.
    innermost = model
    while hasattr(innermost, "_inner"):
        innermost = innermost._inner
    while hasattr(innermost, "_model"):
        innermost = innermost._model
    if hasattr(innermost, "formatter"):
        innermost.formatter = formatter
    agent = Agent(
        name="DiscoveryAgent",
        system_prompt=build_discovery_system_prompt(),
        model=model,
        toolkit=session.build_toolkit(),
        react_config=ReActConfig(max_iters=max_iters),
    )
    # Bypass the default "ask" permission gate — discovery tools are pure
    # in-process state mutations; qwenpaw's own tool_guard applies instead.
    # See react_agent.py:196-198 for the same pattern.
    agent.state.permission_context.mode = PermissionMode.BYPASS
    return agent
