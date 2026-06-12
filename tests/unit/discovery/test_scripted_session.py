# -*- coding: utf-8 -*-
import pytest
from qwenpaw.discovery.scripted_session import ScriptedDiscoverySession
from qwenpaw.discovery.session import DiscoverySession, TurnResult
from qwenpaw.discovery.state import TeamBlueprint


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


@pytest.mark.asyncio
async def test_blueprint_validates_against_team_blueprint_schema():
    """approve_team round-trips this dict — it must validate losslessly."""
    s = ScriptedDiscoverySession()
    r = await s.next_turn(None)
    for a in ["e-commerce", "WhatsApp e planilha", "responder clientes"]:
        r = await s.next_turn(a)
    bp = TeamBlueprint.model_validate(r.blueprint)
    assert bp.company_profile.name == "Sua loja"  # not dropped
    assert bp.detected_integrations[0].kind == "messaging"
    assert bp.process_map[0].name == "Atendimento"
    assert [item.order for item in bp.roadmap] == [1, 2]
