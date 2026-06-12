# -*- coding: utf-8 -*-
"""Unit tests for the plan-tool gate path.

Regression coverage for the agentscope 1.x -> 2.0 migration: a revert deleted
the ``src/qwenpaw/plan/`` package but left live imports of it in
``react_agent._acting`` (``from ..plan.hints import check_plan_tool_gate``) and
in ``app/runner/runner.py``. With ``self.plan_notebook`` set, ``_acting``
raised ``ModuleNotFoundError`` at runtime. These tests construct/use the plan
gate path so that regression — and the 2.0 ``Msg``/``ToolCallBlock`` shape on
that path — stays covered.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from qwenpaw.plan.hints import (
    check_plan_tool_gate,
    clear_plan_awaiting_user_confirm,
    set_plan_gate,
    should_skip_auto_continue,
)


def _notebook(**attrs) -> SimpleNamespace:
    """A duck-typed stand-in for an AgentScope ``PlanNotebook``.

    The gate helpers only read/write plain attributes, so a namespace is enough
    (AgentScope 2.0 ships no ``agentscope.plan`` module to build a real one).
    """
    attrs.setdefault("current_plan", None)
    return SimpleNamespace(**attrs)


# --------------------------------------------------------------------------- #
# Package restoration                                                         #
# --------------------------------------------------------------------------- #
def test_plan_package_imports() -> None:
    """The restored package must import cleanly under agentscope 2.0."""
    from qwenpaw.plan import (  # pylint: disable=unused-import  # noqa: F401
        broadcast,
        hints,
        schemas,
    )

    # No agentscope.plan in 2.0 -> the hint generator degrades to None rather
    # than exploding at import time.
    assert hints.SimplePlanToHint is None


# --------------------------------------------------------------------------- #
# Gate helpers (pure logic)                                                   #
# --------------------------------------------------------------------------- #
def test_set_and_clear_gate_flags() -> None:
    nb = _notebook()
    set_plan_gate(nb, enabled=True)
    assert nb._plan_tool_gate is True
    set_plan_gate(nb, enabled=False)
    assert nb._plan_tool_gate is False
    # None notebook must be a no-op, never raise.
    set_plan_gate(None, enabled=True)


def test_clear_plan_awaiting_user_confirm_resets_same_turn_flags() -> None:
    nb = _notebook(
        _plan_awaiting_user_confirm=True,
        _plan_just_mutated=True,
        _plan_text_only_after_mutation=True,
    )
    clear_plan_awaiting_user_confirm(nb)
    assert nb._plan_awaiting_user_confirm is False
    assert nb._plan_just_mutated is False
    assert nb._plan_text_only_after_mutation is False
    clear_plan_awaiting_user_confirm(None)  # no-op, no raise


def test_gate_none_notebook_never_blocks() -> None:
    assert check_plan_tool_gate(None, "run_python") is None


def test_gate_blocks_non_create_until_plan_exists() -> None:
    nb = _notebook(current_plan=None)
    set_plan_gate(nb, enabled=True)
    # Only create_plan is allowed before a plan exists.
    assert check_plan_tool_gate(nb, "create_plan") is None
    err = check_plan_tool_gate(nb, "run_python")
    assert err is not None and "create_plan" in err


def test_gate_clears_itself_once_a_plan_exists() -> None:
    nb = _notebook(current_plan=object())
    set_plan_gate(nb, enabled=True)
    assert check_plan_tool_gate(nb, "run_python") is None
    # The gate disarms itself the first time a plan is present.
    assert nb._plan_tool_gate is False


def test_gate_disabled_allows_everything() -> None:
    nb = _notebook(current_plan=None)
    assert check_plan_tool_gate(nb, "run_python") is None


def test_awaiting_user_confirm_blocks_execution_tools() -> None:
    nb = _notebook(_plan_awaiting_user_confirm=True)
    # Plan-management tools stay allowed while awaiting confirmation...
    for allowed in ("create_plan", "revise_current_plan", "finish_plan"):
        assert check_plan_tool_gate(nb, allowed) is None
    # ...everything else is blocked.
    err = check_plan_tool_gate(nb, "run_python")
    assert err is not None and "confirm" in err.lower()


@pytest.mark.parametrize(
    "flags,expected",
    [
        ({}, False),
        ({"_plan_awaiting_user_confirm": True}, True),
        ({"_plan_just_mutated": True}, True),
        (
            {
                "_plan_recently_finished": True,
                "_plan_tool_gate": False,
                "current_plan": None,
            },
            True,
        ),
    ],
)
def test_should_skip_auto_continue(flags, expected) -> None:
    nb = _notebook(**flags)
    assert should_skip_auto_continue(nb) is expected
    assert should_skip_auto_continue(None) is False


def test_should_skip_auto_continue_consumes_just_mutated() -> None:
    nb = _notebook(_plan_just_mutated=True)
    assert should_skip_auto_continue(nb) is True
    # The flag is one-shot: cleared after it is observed.
    assert nb._plan_just_mutated is False
    assert should_skip_auto_continue(nb) is False


# --------------------------------------------------------------------------- #
# Regression: react_agent._acting with a non-None plan_notebook               #
# --------------------------------------------------------------------------- #
def _make_agent(notebook) -> object:
    """Build a minimal QwenPawAgent that only exercises the gate branch."""
    from qwenpaw.agents.react_agent import QwenPawAgent

    agent = QwenPawAgent.__new__(QwenPawAgent)
    agent.plan_notebook = notebook
    agent.print = AsyncMock()
    agent.memory = MagicMock()
    agent.memory.add = AsyncMock()
    return agent


@pytest.mark.asyncio
@pytest.mark.parametrize("as_object", [False, True])
async def test_acting_gate_blocks_tool_without_module_error(as_object) -> None:
    """The previously-broken ``from ..plan.hints import ...`` must resolve.

    With the gate armed and no plan yet, a non-``create_plan`` tool is blocked:
    ``_acting`` yields nothing (the tool never executes) and a synthetic
    assistant ``ToolResultBlock`` carrying the gate error is added to memory —
    all without raising ``ModuleNotFoundError``.
    """
    nb = _notebook(current_plan=None)
    set_plan_gate(nb, enabled=True)
    agent = _make_agent(nb)

    if as_object:
        from agentscope.message import ToolCallBlock

        tool_call = ToolCallBlock(
            type="tool_call",
            id="call_abc",
            name="run_python",
            input="{}",
        )
    else:
        tool_call = {"id": "call_abc", "name": "run_python", "input": {}}

    chunks = [chunk async for chunk in agent._acting(tool_call)]

    # Gated tool did not execute -> no delegation to super()._acting().
    assert chunks == []
    agent.memory.add.assert_awaited_once()

    msg = agent.memory.add.call_args.args[0]
    # ToolResultBlock is only valid on an assistant-role Msg in 2.0.
    assert msg.role == "assistant"
    block = msg.content[0]
    assert block.type == "tool_result"
    assert block.id == "call_abc"
    assert block.name == "run_python"
    assert "create_plan" in block.output[0].text


@pytest.mark.asyncio
async def test_acting_pre_locks_before_plan_mutation(monkeypatch) -> None:
    """create_plan/revise arm the awaiting-confirm lock and run the tool.

    create_plan is allowed through the gate, so ``_acting`` delegates to
    ``super()._acting`` (``Agent._acting``, stubbed here to a no-op stream).
    The pre-lock and the post-mutation text-only flag must both be set.
    """
    from agentscope.agent import Agent

    async def _fake_acting(self, _tool_call):  # pragma: no cover - trivial
        return
        yield  # makes this an async generator

    monkeypatch.setattr(Agent, "_acting", _fake_acting)

    nb = _notebook(current_plan=None)
    set_plan_gate(nb, enabled=True)
    agent = _make_agent(nb)

    chunks = [
        chunk
        async for chunk in agent._acting(
            {"id": "c1", "name": "create_plan", "input": {}},
        )
    ]

    assert chunks == []
    # create_plan was allowed through the gate (no synthetic error message).
    agent.memory.add.assert_not_awaited()
    # Pre-lock set before delegation; text-only flag armed after it.
    assert nb._plan_awaiting_user_confirm is True
    assert nb._plan_text_only_after_mutation is True
