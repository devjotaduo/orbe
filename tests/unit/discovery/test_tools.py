# -*- coding: utf-8 -*-
import json

import pytest

from qwenpaw.discovery.state import DiscoveryState, OpenArea
from qwenpaw.discovery.tools import InterviewSession


def _block_field(block, field):
    """Read a content-block field whether it's a dict or a Pydantic model."""
    if isinstance(block, dict):
        return block.get(field)
    return getattr(block, field, None)


def _text(chunk):
    return "".join(
        _block_field(b, "text") or ""
        for b in chunk.content
        if _block_field(b, "type") == "text"
    )


def test_package_reexports_interview_and_protocol():
    """Addendum rule (c): __init__ exports InterviewSession AND re-exports
    DiscoverySession + TurnResult from session.py."""
    import qwenpaw.discovery as disc

    assert disc.InterviewSession is InterviewSession
    # re-exported transport Protocol + result dataclass must still be present
    assert hasattr(disc, "DiscoverySession")
    assert hasattr(disc, "TurnResult")
    assert set(disc.__all__) >= {
        "InterviewSession",
        "DiscoverySession",
        "TurnResult",
    }


@pytest.mark.asyncio
async def test_segment_lookup_unknown_does_not_duplicate_open_area(tmp_path):
    s = InterviewSession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    await s.segment_lookup("mineração de asteroides")
    await s.segment_lookup("colônia em marte")
    matches = [a for a in s.state.open_areas if a.id == "validar-segmento"]
    assert len(matches) == 1


@pytest.mark.asyncio
async def test_reflect_invalid_json_returns_error_without_raising(tmp_path):
    s = InterviewSession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    before = len(s.state.transcript)
    chunk = await s.reflect("aprendi algo", "{not valid json")
    txt = _text(chunk).lower()
    assert "inválid" in txt or "invalid" in txt or "reenvie" in txt
    # estado não deve ter sido mutado em entrada inválida
    assert len(s.state.transcript) == before


@pytest.mark.asyncio
async def test_segment_lookup_known(tmp_path):
    s = InterviewSession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    chunk = await s.segment_lookup("tenho uma loja virtual")
    assert "ecommerce" in _text(chunk).lower()
    assert s.state.company.segment == "ecommerce"


@pytest.mark.asyncio
async def test_segment_lookup_unknown_records_open_question(tmp_path):
    s = InterviewSession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    chunk = await s.segment_lookup("mineração de asteroides")
    assert "livre" in _text(chunk).lower() or "não" in _text(chunk).lower()
    assert any(a.id == "validar-segmento" for a in s.state.open_areas)


@pytest.mark.asyncio
async def test_reflect_mutates_state(tmp_path):
    s = InterviewSession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    s.state.open_areas.append(
        OpenArea(
            id="segmento",
            topic="qual segmento",
            confidence=0.1,
            priority=5,
        ),
    )
    updates = json.dumps(
        {
            "learned": "e-commerce de roupas",
            "close_area_ids": ["segmento"],
            "new_areas": [
                {
                    "id": "logistica",
                    "topic": "entrega",
                    "confidence": 0.1,
                    "priority": 4,
                },
            ],
            "integrations": [
                {
                    "kind": "planilha",
                    "name": "Sheets",
                    "data_location": "drive",
                    "confidence": 0.6,
                },
            ],
            "company_updates": {"segment": "e-commerce"},
            "confidence_updates": {},
        },
    )
    await s.reflect("e-commerce de roupas", updates)
    ids = [a.id for a in s.state.open_areas]
    assert "segmento" not in ids and "logistica" in ids
    assert s.state.company.segment == "e-commerce"
    assert s.state.integrations[0].name == "Sheets"


@pytest.mark.asyncio
async def test_emit_blueprint_writes_files(tmp_path):
    s = InterviewSession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    bp = {
        "company_profile": {
            "segment": "e-commerce",
            "size": "micro",
            "business_model": "venda online",
            "pains": ["atendimento lento"],
        },
        "process_map": [{"name": "atendimento", "description": "SAC"}],
        "detected_integrations": [],
        "proposed_team": [
            {
                "name": "Atendente",
                "role": "SAC",
                "objective": "responder",
                "tasks": ["responder"],
                "tools_integrations": ["mcp:evolution-whatsapp"],
                "talks_to": [],
            },
        ],
        "roadmap": [{"order": 1, "title": "WhatsApp", "rationale": "dor"}],
        "open_questions": [],
    }
    await s.emit_blueprint(json.dumps(bp))
    assert (tmp_path / "blueprint.json").exists()
    assert (tmp_path / "blueprint.md").exists()
    assert "Atendente" in (tmp_path / "blueprint.md").read_text(
        encoding="utf-8",
    )
    assert s.emitted is True


@pytest.mark.asyncio
async def test_emit_blueprint_invalid_json_does_not_write(tmp_path):
    s = InterviewSession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    chunk = await s.emit_blueprint('{"company_profile": ')  # JSON quebrado
    assert not (tmp_path / "blueprint.json").exists()
    assert "erro" in _text(chunk).lower() or "inválid" in _text(chunk).lower()
    assert s.emitted is False
