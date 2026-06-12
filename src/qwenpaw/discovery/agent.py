# -*- coding: utf-8 -*-
"""Fábrica do discovery agent (AgentScope v2 ``Agent``).

``build_discovery_agent`` monta um ``Agent`` com o toolkit da
``InterviewSession`` e o modelo ativo do workspace, espelhando a construção
do ``QwenPawAgent`` (``agents/react_agent.py``): modelo + formatter via
``create_model_and_formatter``, attach do formatter no modelo mais interno e
``PermissionMode.BYPASS`` para o engine de permissão padrão não pausar o
``reply()`` a cada chamada de tool.
"""

from __future__ import annotations

from agentscope.agent import Agent, ReActConfig
from agentscope.permission import PermissionMode

from ..agents.model_factory import create_model_and_formatter
from .prompts import build_discovery_system_prompt
from .tools import InterviewSession


def build_discovery_agent(
    session: InterviewSession,
    max_iters: int = 6,
) -> Agent:
    """Monta o ``Agent`` de discovery com o toolkit da sessão e o modelo ativo.

    Args:
        session: A ``InterviewSession`` que detém o estado e expõe as tools
            ``segment_lookup`` / ``reflect`` / ``emit_blueprint``.
        max_iters: Tetos de iterações do laço ReAct por turno.

    Returns:
        Um ``agentscope.agent.Agent`` pronto para ``reply()``.
    """
    model, formatter = create_model_and_formatter()
    # Mesmo attach de formatter feito pelo QwenPawAgent (react_agent.py):
    # encontra o modelo mais interno e sobrescreve o formatter padrão.
    if formatter is not None:
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

    # Sem isto, o FunctionTool cai no modo "ask" padrão e pausa o reply()
    # a cada tool. As tools do discovery não tocam recursos sensíveis.
    agent.state.permission_context.mode = PermissionMode.BYPASS
    return agent
