# -*- coding: utf-8 -*-
import json

import pytest

from qwenpaw.discovery.state import DiscoveryState, OpenArea
from qwenpaw.discovery.tools import DiscoverySession


def _text(chunk):
    # TextBlock is a typed object (not dict) — use attribute access.
    return "".join(b.text for b in chunk.content if b.type == "text")


@pytest.mark.asyncio
async def test_segment_lookup_known(tmp_path):
    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    chunk = await s.segment_lookup("tenho uma loja virtual")
    assert "ecommerce" in _text(chunk).lower()
    assert s.state.company.segment == "ecommerce"


@pytest.mark.asyncio
async def test_segment_lookup_unknown_records_open_question(tmp_path):
    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    chunk = await s.segment_lookup("mineração de asteroides")
    assert "livre" in _text(chunk).lower() or "não" in _text(chunk).lower()
    assert any(a.id == "validar-segmento" for a in s.state.open_areas)


@pytest.mark.asyncio
async def test_reflect_mutates_state(tmp_path):
    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
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
    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
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
    _ = await s.emit_blueprint(json.dumps(bp))
    assert (tmp_path / "blueprint.json").exists()
    assert (tmp_path / "blueprint.md").exists()
    md = (tmp_path / "blueprint.md").read_text(encoding="utf-8")
    assert "Atendente" in md
    assert s.emitted is True


@pytest.mark.asyncio
async def test_emit_blueprint_invalid_json_does_not_write(tmp_path):
    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    chunk = await s.emit_blueprint('{"company_profile": ')  # JSON quebrado
    assert not (tmp_path / "blueprint.json").exists()
    assert "erro" in _text(chunk).lower() or "inválid" in _text(chunk).lower()
    assert s.emitted is False


# --- MISSING TESTS flagged by reviewer --------------------------------------


@pytest.mark.asyncio
async def test_reflect_error_path_returns_error_state(tmp_path):
    """reflect() com JSON inválido deve retornar state=ERROR."""
    from agentscope.message import ToolResultState

    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    chunk = await s.reflect("aprendizado qualquer", "{json quebrado }")
    assert chunk.state == ToolResultState.ERROR


@pytest.mark.asyncio
async def test_emit_blueprint_error_state(tmp_path):
    """emit_blueprint() inválido retorna state=ERROR e não cria arquivo."""
    from agentscope.message import ToolResultState

    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    chunk = await s.emit_blueprint('{"company_profile": ')
    assert chunk.state == ToolResultState.ERROR
    assert not (tmp_path / "blueprint.json").exists()
    assert s.emitted is False


@pytest.mark.asyncio
async def test_segment_lookup_unknown_idempotent(tmp_path):
    """Chamadas repetidas com segmento desconhecido não duplicam a área."""
    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    await s.segment_lookup("mineração de asteroides")
    await s.segment_lookup("mineração de asteroides")
    ids = [a.id for a in s.state.open_areas]
    assert ids.count("validar-segmento") == 1


@pytest.mark.asyncio
async def test_reflect_confidence_clamped(tmp_path):
    """confidence_updates acima de 1.0 é fixada em 1.0 (clamping)."""
    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    s.state.open_areas.append(
        OpenArea(
            id="estoque",
            topic="controle de estoque",
            confidence=0.3,
            priority=3,
        ),
    )
    updates = json.dumps(
        {
            "learned": "usa planilha",
            "close_area_ids": [],
            "new_areas": [],
            "integrations": [],
            "company_updates": {},
            "confidence_updates": {"estoque": 2.0},
        },
    )
    await s.reflect("usa planilha", updates)
    area = next(a for a in s.state.open_areas if a.id == "estoque")
    assert area.confidence == 1.0


# --- connector_lookup (spec known-connectors) --------------------------------


@pytest.mark.asyncio
async def test_connector_lookup_known_kind(tmp_path):
    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    chunk = await s.connector_lookup("whatsapp")
    text = _text(chunk)
    assert "evolution-api" in text
    assert "recomendado" in text


@pytest.mark.asyncio
async def test_connector_lookup_unknown_kind_errors_with_valid_list(tmp_path):
    from agentscope.message import ToolResultState

    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    chunk = await s.connector_lookup("blockchain")
    assert chunk.state == ToolResultState.ERROR
    assert "whatsapp" in _text(chunk)  # lista os kinds válidos


@pytest.mark.asyncio
async def test_connector_lookup_kind_without_connectors_guides_build(tmp_path):
    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    chunk = await s.connector_lookup("pdv")
    text = _text(chunk).lower()
    assert "build" in text
    assert "open_question" in text


@pytest.mark.asyncio
async def test_connector_lookup_filters_by_state_segment(tmp_path):
    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    s.state.company.segment = "ecommerce"
    chunk = await s.connector_lookup("juridico")
    # brlaw-mcp é restrito a servicos_b2b: para ecommerce não aparece
    assert "brlaw" not in _text(chunk)

    s.state.company.segment = "servicos_b2b"
    chunk = await s.connector_lookup("juridico")
    assert "brlaw" in _text(chunk)


def test_toolkit_has_five_tools(tmp_path):
    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    tk = s.build_toolkit()
    # Toolkit do agentscope 2.0.0 não expõe `.tools` público: as tools do
    # construtor entram no ToolGroup público 'basic' (tool_groups[0]).
    # Deve registrar segment_lookup, reflect, register_onboarding,
    # emit_blueprint, connector_lookup.
    assert len(tk.tool_groups[0].tools) == 5


def test_requirements_toolkit_has_one_tool(tmp_path):
    s = DiscoverySession(DiscoveryState(session_id="s1"), out_dir=tmp_path)
    tk = s.build_requirements_toolkit()
    assert len(tk.tool_groups[0].tools) == 1


# --- conectores no blueprint (MD leigo + JSON técnico) + prompt --------------


def test_blueprint_markdown_uses_friendly_connector_names():
    """O MD é para o empresário: nomes amigáveis, sem slugs técnicos.

    A informação técnica (origin:slug, status, notas de risco) continua
    íntegra no blueprint.json — aqui só validamos a tradução leiga.
    """
    from qwenpaw.discovery.state import (
        AgentSpec,
        CompanyProfile,
        ConnectorRef,
        TeamBlueprint,
    )
    from qwenpaw.discovery.tools import _blueprint_to_markdown

    bp = TeamBlueprint(
        company_profile=CompanyProfile(segment="ecommerce"),
        proposed_team=[
            AgentSpec(
                name="Atendente WhatsApp",
                role="SAC",
                objective="responder clientes",
                tools_integrations=["clawhub:evolution-api"],
            ),
        ],
        recommended_connectors=[
            ConnectorRef(
                integration_kind="whatsapp",
                name="Evolution API v2",
                origin="clawhub",
                slug_or_url="evolution-api",
                status="recomendado",
                notes="não-oficial; risco de ban",
            ),
        ],
    )
    md = _blueprint_to_markdown(bp)
    # nome amigável visível; referência técnica origin:slug NÃO aparece
    assert "Evolution API v2" in md
    assert "clawhub:evolution-api" not in md


def test_blueprint_markdown_omits_empty_connectors_section():
    from qwenpaw.discovery.state import CompanyProfile, TeamBlueprint
    from qwenpaw.discovery.tools import _blueprint_to_markdown

    bp = TeamBlueprint(company_profile=CompanyProfile(segment="ecommerce"))
    assert "Conectores recomendados" not in _blueprint_to_markdown(bp)


def test_system_prompt_mentions_connector_lookup():
    from qwenpaw.discovery.prompts import build_discovery_system_prompt

    assert "connector_lookup" in build_discovery_system_prompt()


# --- _friendly_tool_name: fallback p/ conectores sem slug (status build) -----
# Adaptação do MISSING TEST do reviewer ("empty slug_or_url renders origin
# alone"): a renderização `origin:slug` no MD foi substituída pelo relatório
# leigo — o fallback agora vive em _friendly_tool_name.


def _bp_with_build_connector():
    from qwenpaw.discovery.state import (
        AgentSpec,
        CompanyProfile,
        ConnectorRef,
        TeamBlueprint,
    )

    return TeamBlueprint(
        company_profile=CompanyProfile(segment="ecommerce"),
        proposed_team=[
            AgentSpec(
                name="Agente Delivery",
                role="pedidos",
                objective="acompanhar pedidos",
                tools_integrations=["Conector iFood próprio"],
            ),
        ],
        recommended_connectors=[
            ConnectorRef(
                integration_kind="delivery",
                name="Conector iFood próprio",
                origin="build",
                slug_or_url="",
                status="build",
                notes="sem conector curado — construir",
            ),
        ],
    )


def test_friendly_tool_name_resolves_origin_slug_ref():
    from qwenpaw.discovery.state import (
        CompanyProfile,
        ConnectorRef,
        TeamBlueprint,
    )
    from qwenpaw.discovery.tools import _friendly_tool_name

    bp = TeamBlueprint(
        company_profile=CompanyProfile(segment="ecommerce"),
        recommended_connectors=[
            ConnectorRef(
                integration_kind="whatsapp",
                name="Evolution API v2",
                origin="clawhub",
                slug_or_url="evolution-api",
                status="recomendado",
            ),
        ],
    )
    friendly = _friendly_tool_name("clawhub:evolution-api", bp)
    assert friendly == "Evolution API v2"


def test_friendly_tool_name_build_connector_matches_by_name():
    """Conector build (slug vazio): a referência por nome resolve no MD."""
    from qwenpaw.discovery.tools import _friendly_tool_name

    bp = _bp_with_build_connector()
    assert (
        _friendly_tool_name("conector ifood próprio", bp)
        == "Conector iFood próprio"
    )


def test_friendly_tool_name_unknown_ref_falls_back_to_title():
    from qwenpaw.discovery.state import CompanyProfile, TeamBlueprint
    from qwenpaw.discovery.tools import _friendly_tool_name

    bp = TeamBlueprint(company_profile=CompanyProfile(segment="ecommerce"))
    assert _friendly_tool_name("mcp:google-sheets", bp) == "Google Sheets"


def test_blueprint_markdown_build_connector_has_no_technical_ref():
    """Build connector (slug vazio) não vaza 'build:' nem slug no relatório."""
    from qwenpaw.discovery.tools import _blueprint_to_markdown

    md = _blueprint_to_markdown(_bp_with_build_connector())
    assert "Conector iFood próprio" in md
    assert "build:" not in md
