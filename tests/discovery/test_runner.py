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
                    "tools_integrations": ["mcp:evolution-whatsapp"], "talks_to": []}],
                "roadmap": [{"order": 1, "title": "Atendimento WhatsApp",
                    "rationale": "dor principal"}],
                "open_questions": ["volume de mensagens/dia?"],
            }
            await s.emit_blueprint(json.dumps(bp))
            return _MsgStub("Pronto! Gerei o blueprint do seu time.")
        return _MsgStub("...")


class _MsgStub:
    def __init__(self, text):
        self._t = text

    def get_text_content(self):
        return self._t


@pytest.mark.asyncio
async def test_runner_scripted_interview(tmp_path, monkeypatch):
    # respostas do empresário, terminando com /fim
    inputs = iter(["tenho uma loja virtual de roupas",
                   "atendo manual no zap", "/fim"])
    monkeypatch.setattr(runner_mod, "_read_user_input", lambda prompt: next(inputs))
    monkeypatch.setattr(runner_mod, "build_discovery_agent",
                        lambda session, **kw: FakeAgent(session))

    out = await runner_mod.run_discovery_session(
        session_id="t1", out_dir=tmp_path)

    assert (tmp_path / "blueprint.json").exists()
    bp = json.loads((tmp_path / "blueprint.json").read_text(encoding="utf-8"))
    assert bp["proposed_team"][0]["name"] == "Atendente WhatsApp"
    assert (tmp_path / "discovery_state.json").exists()
    assert out.emitted is True
