# -*- coding: utf-8 -*-
import pytest
from pydantic import ValidationError

from qwenpaw.discovery.state import (
    DiscoveryState,
    OpenArea,
    TeamBlueprint,
    ReflectUpdate,
)


def test_open_area_confidence_bounds():
    OpenArea(
        id="vendas", topic="processo de vendas", confidence=0.5, priority=3
    )
    with pytest.raises(ValidationError):
        OpenArea(id="x", topic="t", confidence=1.5, priority=1)


def test_discovery_state_defaults_and_helpers():
    st = DiscoveryState(session_id="s1")
    assert st.open_areas == []
    assert st.integrations == []
    # next_focus picks lowest-confidence, highest-priority open area
    st.open_areas = [
        OpenArea(id="a", topic="A", confidence=0.9, priority=1),
        OpenArea(id="b", topic="B", confidence=0.2, priority=2),
    ]
    assert st.next_focus().id == "b"
    # ready_to_emit() True quando todas as áreas prio>=3 superam limiar
    # (áreas "a" e "b" têm prio 1 e 2 — nenhuma é crítica, mas há áreas → True)
    assert st.ready_to_emit(threshold=0.7) is True


def test_blueprint_roundtrip_json():
    bp = TeamBlueprint(
        company_profile={
            "segment": "e-commerce",
            "size": "micro",
            "business_model": "venda online",
            "pains": ["atendimento lento"],
        },
        process_map=[
            {"name": "atendimento", "description": "SAC via WhatsApp"}
        ],
        detected_integrations=[
            {
                "kind": "whatsapp",
                "name": "Evolution",
                "data_location": "instância própria",
                "confidence": 0.8,
            }
        ],
        proposed_team=[
            {
                "name": "Atendente WhatsApp",
                "role": "SAC",
                "objective": "responder clientes",
                "tasks": ["responder dúvidas"],
                "tools_integrations": ["mcp:evolution-whatsapp"],
                "talks_to": [],
            }
        ],
        roadmap=[
            {
                "order": 1,
                "title": "Atendimento WhatsApp",
                "rationale": "dor principal",
            }
        ],
        open_questions=["confirmar volume de mensagens/dia"],
    )
    data = bp.model_dump_json()
    again = TeamBlueprint.model_validate_json(data)
    assert again.proposed_team[0].name == "Atendente WhatsApp"


def test_reflect_update_parses():
    upd = ReflectUpdate.model_validate_json(
        '{"learned":"empresa é e-commerce de roupas",'
        '"close_area_ids":["segmento"],'
        '"new_areas":[{"id":"logistica","topic":"como entrega",'
        '"confidence":0.1,"priority":4}],'
        '"integrations":[{"kind":"planilha","name":"Google Sheets",'
        '"data_location":"drive","confidence":0.6}],'
        '"company_updates":{"segment":"e-commerce"}}'
    )
    assert upd.new_areas[0].id == "logistica"


# --- MISSING TESTS (flagged by reviewer) ------------------------------------

def test_open_area_id_uniqueness_enforced():
    """DiscoveryState deve rejeitar duas OpenArea com o mesmo id."""
    with pytest.raises(ValidationError):
        DiscoveryState(
            session_id="s",
            open_areas=[
                OpenArea(id="dup", topic="A", confidence=0.1, priority=3),
                OpenArea(id="dup", topic="B", confidence=0.2, priority=4),
            ],
        )


def test_ready_to_emit_false_when_no_areas():
    """ready_to_emit() retorna False quando open_areas está vazio."""
    st = DiscoveryState(session_id="x")
    assert st.open_areas == []
    assert st.ready_to_emit() is False


def test_reflect_update_confidence_updates():
    """ReflectUpdate stores float confidence_updates keyed by area id."""
    upd = ReflectUpdate(
        learned="empresa usa planilha para controle",
        confidence_updates={"area1": 0.85},
    )
    assert upd.confidence_updates["area1"] == pytest.approx(0.85)
    # validate via JSON round-trip as well
    from pydantic import TypeAdapter
    raw_json = upd.model_dump_json()
    upd2 = ReflectUpdate.model_validate_json(raw_json)
    assert upd2.confidence_updates["area1"] == pytest.approx(0.85)
