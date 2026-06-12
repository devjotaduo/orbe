# -*- coding: utf-8 -*-
"""LiveDiscoverySession ponta a ponta com LLM mockado (FakeAgent).

Espelha o teste do runner, mas pela interface ``next_turn`` da Protocol
``DiscoverySession``: ``next_turn(None)`` abre a entrevista,
``next_turn(texto)`` injeta respostas e, ao final, o ``TurnResult`` traz um
``blueprint`` válido contra ``TeamBlueprint`` e ``done=True``.
"""

import json

from qwenpaw.discovery import live_session as live_mod
from qwenpaw.discovery.live_session import (
    LiveDiscoverySession,
    make_live_session_factory,
)
from qwenpaw.discovery.session import DiscoverySession, TurnResult
from qwenpaw.discovery.state import TeamBlueprint

_BLUEPRINT = {
    "company_profile": {
        "segment": "ecommerce",
        "size": "micro",
        "business_model": "venda online de roupas",
        "pains": ["atendimento manual lento"],
    },
    "process_map": [{"name": "atendimento", "description": "SAC WhatsApp"}],
    "detected_integrations": [
        {
            "kind": "whatsapp",
            "name": "WhatsApp",
            "data_location": "celular",
            "confidence": 0.9,
        },
    ],
    "proposed_team": [
        {
            "name": "Atendente WhatsApp",
            "role": "SAC",
            "objective": "responder clientes 24/7",
            "tasks": ["responder dúvidas"],
            "tools_integrations": ["mcp:evolution-whatsapp"],
            "talks_to": [],
        },
    ],
    "roadmap": [
        {"order": 1, "title": "Atendimento WhatsApp", "rationale": "dor"},
    ],
    "open_questions": ["volume de mensagens/dia?"],
}


class _MsgStub:
    def __init__(self, text: str) -> None:
        self._t = text

    def get_text_content(self) -> str:
        return self._t


class FakeAgent:
    """Faz perguntas nos 2 primeiros turnos e emite o blueprint no 3º."""

    def __init__(self, session) -> None:
        self.session = session
        self._turn = 0

    async def reply(self, msg):
        self._turn += 1
        if self._turn == 1:
            return _MsgStub("O que a sua empresa faz?")
        if self._turn == 2:
            return _MsgStub("Como você atende seus clientes hoje?")
        # 3º turno: o agente "decide" emitir o blueprint.
        await self.session.emit_blueprint(json.dumps(_BLUEPRINT))
        return _MsgStub("Pronto! Gerei o blueprint do seu time.")


def _patch_agent(monkeypatch):
    monkeypatch.setattr(
        live_mod.runner_mod,
        "build_discovery_agent",
        lambda session, **kw: FakeAgent(session),
    )


async def test_live_session_runs_turns_then_blueprint(tmp_path, monkeypatch):
    _patch_agent(monkeypatch)
    sess = LiveDiscoverySession(session_id="live1", out_dir=tmp_path)

    # Implementa a Protocol de transporte.
    assert isinstance(sess, DiscoverySession)

    # Turno de abertura: 1ª pergunta, sem blueprint.
    r0 = await sess.next_turn(None)
    assert isinstance(r0, TurnResult)
    assert r0.done is False
    assert r0.question
    assert r0.blueprint is None
    assert isinstance(r0.state, dict)

    # Resposta 1 -> próxima pergunta.
    r1 = await sess.next_turn("tenho uma loja virtual de roupas")
    assert r1.done is False
    assert r1.question
    assert r1.blueprint is None

    # Resposta 2 -> o agente emite o blueprint.
    r2 = await sess.next_turn("atendo manual no WhatsApp")
    assert r2.done is True
    assert r2.question is None
    assert r2.blueprint is not None

    # Blueprint válido contra o schema e com os campos que o builder lê.
    bp = TeamBlueprint.model_validate(r2.blueprint)
    assert bp.proposed_team[0].name == "Atendente WhatsApp"
    assert r2.blueprint["company_profile"]["segment"] == "ecommerce"
    assert r2.blueprint["detected_integrations"][0]["name"] == "WhatsApp"
    assert r2.blueprint["proposed_team"][0]["tools_integrations"]
    assert r2.blueprint["open_questions"]


async def test_live_session_keeps_state_alive(tmp_path, monkeypatch):
    """O DiscoveryState segue vivo entre chamadas de next_turn."""
    _patch_agent(monkeypatch)
    sess = LiveDiscoverySession(session_id="live2", out_dir=tmp_path)
    await sess.next_turn(None)
    # Semente do segmento presente desde a construção.
    assert any(a.id == "segmento" for a in sess._state.open_areas)


def test_make_live_session_factory_returns_live_sessions(
    tmp_path,
    monkeypatch,
):
    _patch_agent(monkeypatch)
    factory = make_live_session_factory(out_root=tmp_path)
    # A fábrica satisfaz a assinatura esperada por set_session_factory.
    assert callable(factory)
    sess = factory()
    assert isinstance(sess, LiveDiscoverySession)


def test_wire_live_session_flips_router_factory(monkeypatch):
    """Com a env ligada, o wiring troca a fábrica do router para a ao vivo."""
    from qwenpaw.app.routers import discovery_stream as ds
    from qwenpaw.discovery.scripted_session import ScriptedDiscoverySession

    original = ds._session_factory
    try:
        monkeypatch.setenv("QWENPAW_DISCOVERY_LIVE", "1")
        assert live_mod.wire_live_session_if_enabled() is True
        # A fábrica não é mais a scriptada; cria uma LiveDiscoverySession.
        _patch_agent(monkeypatch)
        assert ds._session_factory is not ScriptedDiscoverySession
        assert isinstance(ds._session_factory(), LiveDiscoverySession)
    finally:
        ds.set_session_factory(original)


def test_wire_live_session_disabled_is_noop(monkeypatch):
    """Sem a env, o default seguro (scriptada) é preservado."""
    from qwenpaw.app.routers import discovery_stream as ds

    original = ds._session_factory
    try:
        monkeypatch.delenv("QWENPAW_DISCOVERY_LIVE", raising=False)
        assert live_mod.wire_live_session_if_enabled() is False
        assert ds._session_factory is original
    finally:
        ds.set_session_factory(original)


async def test_live_session_records_transcript(tmp_path, monkeypatch):
    """next_turn registra as respostas do empresário no transcript (parity)."""
    _patch_agent(monkeypatch)
    sess = LiveDiscoverySession(session_id="live3", out_dir=tmp_path)
    await sess.next_turn(None)
    await sess.next_turn("tenho uma loja virtual de roupas")
    roles_texts = [(t.role, t.text) for t in sess._state.transcript]
    assert ("user", "tenho uma loja virtual de roupas") in roles_texts
