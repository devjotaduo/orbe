# -*- coding: utf-8 -*-
import json
from pathlib import Path

import pytest

from qwenpaw.discovery.state import DiscoveryState
from qwenpaw.discovery.tools import DiscoverySession
from qwenpaw.discovery import runner as runner_mod


class FakeAgent:
    """Agent falso: em vez de chamar LLM, chama as tools da sessão na ordem
    de uma entrevista de e-commerce e emite o blueprint."""

    def __init__(self, session: DiscoverySession):
        self.session = session
        self._turn = 0

    async def reply(self, msg):
        self._turn += 1
        s = self.session
        if self._turn == 1:
            await s.segment_lookup("tenho uma loja virtual de roupas")
            await s.reflect("e-commerce de roupas", json.dumps({
                "learned": "e-commerce de roupas", "close_area_ids": [],
                "new_areas": [{"id": "atendimento", "topic": "como atende hoje",
                               "confidence": 0.1, "priority": 5}],
                "integrations": [], "company_updates": {"segment": "ecommerce"},
                "confidence_updates": {}}))
            return _MsgStub("Como você atende seus clientes hoje?")
        if self._turn == 2:
            await s.reflect("atende manual no WhatsApp", json.dumps({
                "learned": "atendimento manual no WhatsApp",
                "close_area_ids": ["atendimento"],
                "new_areas": [],
                "integrations": [{"kind": "whatsapp", "name": "WhatsApp",
                                  "data_location": "celular", "confidence": 0.9}],
                "company_updates": {}, "confidence_updates": {}}))
            await s.connector_lookup("whatsapp")
            await s.register_onboarding("11 98765-4321", "Maria")
            bp = {
                "company_profile": {"segment": "ecommerce", "size": "micro",
                    "business_model": "venda online de roupas",
                    "pains": ["atendimento manual lento"]},
                "process_map": [{"name": "atendimento", "description": "SAC WhatsApp"}],
                "detected_integrations": [{"kind": "whatsapp", "name": "WhatsApp",
                    "data_location": "celular", "confidence": 0.9}],
                "proposed_team": [{"name": "Atendente WhatsApp", "role": "SAC",
                    "objective": "responder clientes 24/7",
                    "tasks": ["responder dúvidas", "rastrear pedido"],
                    "tools_integrations": ["clawhub:evolution-api"], "talks_to": []}],
                "roadmap": [{"order": 1, "title": "Atendimento WhatsApp",
                    "rationale": "dor principal"}],
                "open_questions": ["volume de mensagens/dia?"],
                "recommended_connectors": [
                    {"integration_kind": "whatsapp",
                     "name": "Evolution API v2",
                     "origin": "clawhub",
                     "slug_or_url": "evolution-api",
                     "status": "recomendado",
                     "notes": "não-oficial; risco de ban"}],
            }
            await s.emit_blueprint(json.dumps(bp))
            return _MsgStub("Pronto! Gerei o blueprint do seu time.")
        return _MsgStub("...")


class _MsgStub:
    def __init__(self, text):
        self._t = text

    def get_text_content(self):
        return self._t


class FakeRequirementsAgent:
    """Fase de requisitos sem LLM: emite um RequirementsReport mínimo."""

    def __init__(self, session: DiscoverySession):
        self.session = session

    async def reply(self, msg):
        await self.session.emit_requirements(json.dumps({
            "summary_for_owner": "Olá! Por este grupo vamos pedir o que "
                                 "falta e você testa o atendente.",
            "items": [{
                "agent_name": "Atendente WhatsApp",
                "requests": [{
                    "item": "perguntas frequentes dos clientes",
                    "why": "para o atendente responder sozinho",
                    "group_message": "Pode nos mandar as 5 perguntas que "
                                     "seus clientes mais fazem?",
                }],
            }],
        }))
        return _MsgStub("Pendências levantadas.")


@pytest.mark.asyncio
async def test_runner_scripted_interview(tmp_path, monkeypatch):
    # respostas do empresário. Nota: o loop sai quando session.emitted=True após o
    # 2º turno, então "/fim" nunca é lido — esse caminho é testado separadamente
    # em test_runner_fim_path.
    inputs = iter(["tenho uma loja virtual de roupas",
                   "atendo manual no zap"])
    monkeypatch.setattr(runner_mod, "_read_user_input", lambda prompt: next(inputs))
    monkeypatch.setattr(runner_mod, "build_discovery_agent",
                        lambda session, **kw: FakeAgent(session))
    monkeypatch.setattr(runner_mod, "build_requirements_agent",
                        lambda session, **kw: FakeRequirementsAgent(session))

    out = await runner_mod.run_discovery_session(
        session_id="t1", out_dir=tmp_path)

    assert (tmp_path / "blueprint.json").exists()
    bp = json.loads((tmp_path / "blueprint.json").read_text(encoding="utf-8"))
    assert bp["proposed_team"][0]["name"] == "Atendente WhatsApp"
    assert bp["recommended_connectors"], "blueprint deve recomendar conectores"
    rc = bp["recommended_connectors"][0]
    assert rc["origin"] == "clawhub" and rc["slug_or_url"] == "evolution-api"
    # onboarding capturado no estado e persistido no blueprint
    assert bp["onboarding"]["responsible_name"] == "Maria"
    assert "8765" in bp["onboarding"]["whatsapp_number"]
    md = (tmp_path / "blueprint.md").read_text(encoding="utf-8")
    # relatório leigo: título amigável, próximos passos, zero slug técnico
    assert "Seu Time de Agentes" in md
    assert "Próximos passos" in md
    assert "clawhub:evolution-api" not in md
    # fase de requisitos rodou e gravou os artefatos
    assert out.requirements_emitted is True
    assert (tmp_path / "requirements.json").exists()
    pend = (tmp_path / "informacoes_pendentes.md").read_text(encoding="utf-8")
    assert "Atendente WhatsApp" in pend
    msgs = (tmp_path / "mensagens_grupo.md").read_text(encoding="utf-8")
    assert "5 perguntas" in msgs
    assert (tmp_path / "discovery_state.json").exists()
    assert out.emitted is True

    # -- reviewer-flagged: user turns must appear in session.state.transcript --
    user_turns = [t for t in out.state.transcript if t.role == "user"]
    assert len(user_turns) >= 2, (
        f"Esperado >= 2 turnos de usuário no transcript, encontrado {len(user_turns)}: "
        f"{out.state.transcript}"
    )
    assert user_turns[0].text == "tenho uma loja virtual de roupas"
    assert user_turns[1].text == "atendo manual no zap"


class _NeverEmitAgent:
    """Agent falso que nunca chama emit_blueprint — força o caminho /fim."""

    async def reply(self, msg):
        return _MsgStub("Pode continuar me contando...")


@pytest.mark.asyncio
async def test_runner_fim_path(tmp_path, monkeypatch):
    """Exercita o branch /fim: o loop deve persistir e sair sem blueprint."""
    inputs = iter(["minha empresa vende sapatos", "/fim"])
    monkeypatch.setattr(runner_mod, "_read_user_input", lambda prompt: next(inputs))
    monkeypatch.setattr(runner_mod, "build_discovery_agent",
                        lambda session, **kw: _NeverEmitAgent())

    out = await runner_mod.run_discovery_session(
        session_id="fim_test", out_dir=tmp_path)

    # blueprint não foi emitido
    assert out.emitted is False
    # estado foi persistido mesmo sem blueprint
    assert (tmp_path / "discovery_state.json").exists()


@pytest.mark.asyncio
async def test_runner_eoferror_persists_and_returns_not_emitted(tmp_path, monkeypatch):
    """EOFError em _read_user_input (stdin fechado em CI/pipe) deve persistir o
    estado já coletado e retornar com emitted=False, sem levantar exceção."""

    call_count = 0

    def _raise_eof(prompt: str) -> str:
        nonlocal call_count
        call_count += 1
        raise EOFError("stdin fechado")

    monkeypatch.setattr(runner_mod, "_read_user_input", _raise_eof)
    monkeypatch.setattr(runner_mod, "build_discovery_agent",
                        lambda session, **kw: _NeverEmitAgent())

    # Não deve levantar exceção
    out = await runner_mod.run_discovery_session(
        session_id="eof_test", out_dir=tmp_path)

    # EOFError deve ter sido capturado na primeira leitura
    assert call_count == 1, "EOFError deve ser capturado na primeira chamada de _read_user_input"
    # Não emitiu blueprint (encerrou antes)
    assert out.emitted is False
    # Estado deve ter sido persistido mesmo assim
    assert (tmp_path / "discovery_state.json").exists(), (
        "discovery_state.json deve ser salvo mesmo quando stdin fecha inesperadamente"
    )
    # O arquivo de estado deve ser JSON válido
    state_data = json.loads(
        (tmp_path / "discovery_state.json").read_text(encoding="utf-8")
    )
    assert state_data["session_id"] == "eof_test"
