# -*- coding: utf-8 -*-
import pytest
from qwenpaw.discovery.scripted_session import ScriptedDiscoverySession
from qwenpaw.discovery.session import DiscoverySession, TurnResult


@pytest.mark.asyncio
async def test_implements_protocol():
    assert isinstance(ScriptedDiscoverySession(), DiscoverySession)


@pytest.mark.asyncio
async def test_opening_turn_asks_first_question_and_is_not_done():
    s = ScriptedDiscoverySession()
    r = await s.next_turn(None)
    assert isinstance(r, TurnResult)
    assert r.question is not None
    assert r.done is False
    assert r.blueprint is None


@pytest.mark.asyncio
async def test_state_segment_set_after_first_answer():
    s = ScriptedDiscoverySession()
    await s.next_turn(None)
    r = await s.next_turn("tenho um e-commerce de roupas")
    assert r.state.get("company", {}).get("segment") == "ecommerce"


@pytest.mark.asyncio
async def test_runs_to_a_blueprint_and_then_done():
    s = ScriptedDiscoverySession()
    r = await s.next_turn(None)
    answers = [
        "e-commerce de roupas",
        "uso WhatsApp e planilha",
        "responder clientes",
    ]
    for a in answers:
        r = await s.next_turn(a)
    assert r.done is True
    assert r.blueprint is not None
    assert r.blueprint["company_profile"]["segment"] == "ecommerce"
    assert len(r.blueprint["proposed_team"]) >= 1
    assert r.question is None
