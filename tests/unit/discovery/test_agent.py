# -*- coding: utf-8 -*-
"""build_discovery_agent (Task 5) com create_model_and_formatter mockado.

A construção do ``Agent`` real exige um modelo; aqui o
``create_model_and_formatter`` é substituído por um par mock e a classe
``Agent`` é capturada para verificar a fiação: o toolkit vem da
``InterviewSession`` (3 tools), o system prompt é o de discovery e o modo de
permissão final é ``BYPASS`` (senão o ``reply()`` pausaria a cada tool).
Nenhum LLM real é tocado.
"""

import asyncio
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock, patch

from qwenpaw.discovery import agent as agent_mod
from qwenpaw.discovery.state import DiscoveryState
from qwenpaw.discovery.tools import InterviewSession


def _make_session(tmp_path: Path) -> InterviewSession:
    state = DiscoveryState(session_id="agent-test")
    return InterviewSession(state, out_dir=tmp_path)


class _BareModel:
    """Modelo plano sem ``_inner``/``_model``/``formatter``.

    Um ``MagicMock`` não serve: ``hasattr(mock, "_inner")`` é sempre ``True``,
    o que faria o laço de attach do ``agent.py`` girar para sempre. Um objeto
    real garante ``hasattr(...) is False`` e encerra o laço de imediato.
    """


@contextmanager
def _patched_agent(model, formatter, captured):
    """Substitui ``create_model_and_formatter`` + ``Agent`` (capturando kw)."""

    class _AgentStub:
        def __init__(self, **kwargs):
            captured.update(kwargs)
            self.state = MagicMock()

    with patch.object(
        agent_mod,
        "create_model_and_formatter",
        return_value=(model, formatter),
    ):
        with patch.object(agent_mod, "Agent", _AgentStub):
            yield


def test_build_discovery_agent_wires_toolkit_and_bypass(tmp_path):
    session = _make_session(tmp_path)
    fake_model = _BareModel()
    fake_formatter = MagicMock(name="formatter")

    captured = {}
    with _patched_agent(fake_model, fake_formatter, captured):
        agent = agent_mod.build_discovery_agent(session)

    # O toolkit do agente é o da sessão: as três tools do discovery.
    toolkit = captured["toolkit"]
    schemas = asyncio.run(toolkit.get_tool_schemas())
    tool_names = {(sc.get("function") or {}).get("name") for sc in schemas}
    assert {"segment_lookup", "reflect", "emit_blueprint"} <= tool_names

    # System prompt é o de discovery (entrevista, não formulário).
    assert "consultor" in captured["system_prompt"].lower()
    assert captured["model"] is fake_model

    # Modo de permissão final = BYPASS (não pausa o reply a cada tool).
    from agentscope.permission import PermissionMode

    assert agent.state.permission_context.mode == PermissionMode.BYPASS


def test_build_discovery_agent_attaches_formatter_to_innermost(tmp_path):
    """Quando há formatter, ele é fixado no modelo mais interno."""
    session = _make_session(tmp_path)

    class _Innermost:
        formatter = None

    inner = _Innermost()
    fake_model = MagicMock(name="model")
    fake_model._inner = inner
    # _Innermost não tem _inner/_model -> o loop para no inner.
    del fake_model._model
    fake_formatter = MagicMock(name="formatter")

    with _patched_agent(fake_model, fake_formatter, {}):
        agent_mod.build_discovery_agent(session)

    assert inner.formatter is fake_formatter


def test_build_discovery_agent_passes_max_iters(tmp_path):
    """``max_iters`` chega ao ReActConfig do agente."""
    session = _make_session(tmp_path)
    fake_model = _BareModel()

    captured = {}
    with _patched_agent(fake_model, None, captured):
        agent_mod.build_discovery_agent(session, max_iters=9)

    assert captured["react_config"].max_iters == 9
