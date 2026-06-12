# -*- coding: utf-8 -*-
"""Entrevista roteirizada ponta a ponta com LLM mockado (FakeAgent).

O ``build_discovery_agent`` real é substituído por um ``FakeAgent`` que, em
vez de chamar o LLM, aciona as tools da ``InterviewSession`` na ordem de uma
entrevista de e-commerce/WhatsApp e emite o blueprint. ``_read_user_input``
também é mockado — nenhum terminal nem LLM real é tocado.
"""

import json

from qwenpaw.discovery import runner as runner_mod
from qwenpaw.discovery.tools import InterviewSession
from qwenpaw.discovery.state import TeamBlueprint


class _MsgStub:
    def __init__(self, text: str) -> None:
        self._t = text

    def get_text_content(self) -> str:
        return self._t


class FakeAgent:
    """Agente falso: aciona as tools da sessão como numa entrevista real."""

    def __init__(self, session: InterviewSession) -> None:
        self.session = session
        self._turn = 0

    async def reply(self, msg):
        self._turn += 1
        s = self.session
        if self._turn == 1:
            await s.segment_lookup("tenho uma loja virtual de roupas")
            await s.reflect(
                "e-commerce de roupas",
                json.dumps(
                    {
                        "learned": "e-commerce de roupas",
                        "close_area_ids": ["segmento"],
                        "new_areas": [
                            {
                                "id": "atendimento",
                                "topic": "como atende hoje",
                                "confidence": 0.1,
                                "priority": 5,
                            },
                        ],
                        "integrations": [],
                        "company_updates": {"segment": "ecommerce"},
                        "confidence_updates": {},
                    },
                ),
            )
            return _MsgStub("Como você atende seus clientes hoje?")
        if self._turn == 2:
            await s.reflect(
                "atende manual no WhatsApp",
                json.dumps(
                    {
                        "learned": "atendimento manual no WhatsApp",
                        "close_area_ids": ["atendimento"],
                        "new_areas": [],
                        "integrations": [
                            {
                                "kind": "whatsapp",
                                "name": "WhatsApp",
                                "data_location": "celular",
                                "confidence": 0.9,
                            },
                        ],
                        "company_updates": {},
                        "confidence_updates": {},
                    },
                ),
            )
            bp = {
                "company_profile": {
                    "segment": "ecommerce",
                    "size": "micro",
                    "business_model": "venda online de roupas",
                    "pains": ["atendimento manual lento"],
                },
                "process_map": [
                    {"name": "atendimento", "description": "SAC WhatsApp"},
                ],
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
                        "tasks": ["responder dúvidas", "rastrear pedido"],
                        "tools_integrations": ["mcp:evolution-whatsapp"],
                        "talks_to": [],
                    },
                ],
                "roadmap": [
                    {
                        "order": 1,
                        "title": "Atendimento WhatsApp",
                        "rationale": "dor principal",
                    },
                ],
                "open_questions": ["volume de mensagens/dia?"],
            }
            await s.emit_blueprint(json.dumps(bp))
            return _MsgStub("Pronto! Gerei o blueprint do seu time.")
        return _MsgStub("...")


async def test_runner_scripted_interview(tmp_path, monkeypatch):
    inputs = iter(
        ["tenho uma loja virtual de roupas", "atendo manual no zap", "/fim"],
    )
    monkeypatch.setattr(
        runner_mod,
        "_read_user_input",
        lambda prompt: next(inputs),
    )
    monkeypatch.setattr(
        runner_mod,
        "build_discovery_agent",
        lambda session, **kw: FakeAgent(session),
    )

    session = await runner_mod.run_discovery_session(
        session_id="t1",
        out_dir=tmp_path,
    )

    assert session.emitted is True
    assert (tmp_path / "blueprint.json").exists()
    assert (tmp_path / "blueprint.md").exists()
    assert (tmp_path / "discovery_state.json").exists()

    raw = json.loads((tmp_path / "blueprint.json").read_text(encoding="utf-8"))
    bp = TeamBlueprint.model_validate(raw)
    assert bp.proposed_team[0].name == "Atendente WhatsApp"

    # O dict do blueprint bate com os campos lidos por a2ui/builder.py.
    assert raw["company_profile"]["segment"] == "ecommerce"
    assert raw["detected_integrations"][0]["name"] == "WhatsApp"
    assert raw["proposed_team"][0]["tools_integrations"]
    assert raw["open_questions"]


async def test_runner_persists_state_before_emit(tmp_path, monkeypatch):
    """Estado é persistido a cada turno (mesmo antes do blueprint)."""

    class _OneQuestionAgent:
        def __init__(self, session):
            self.session = session

        async def reply(self, msg):
            return _MsgStub("E quais sistemas você usa?")

    inputs = iter(["loja virtual", "/sair"])
    monkeypatch.setattr(
        runner_mod,
        "_read_user_input",
        lambda prompt: next(inputs),
    )
    monkeypatch.setattr(
        runner_mod,
        "build_discovery_agent",
        lambda session, **kw: _OneQuestionAgent(session),
    )

    session = await runner_mod.run_discovery_session(
        session_id="t2",
        out_dir=tmp_path,
    )

    assert session.emitted is False
    assert (tmp_path / "discovery_state.json").exists()
    assert not (tmp_path / "blueprint.json").exists()


async def test_run_discovery_cli_uses_discovery_subdir(tmp_path, monkeypatch):
    """``run_discovery_cli`` grava em <workspace>/discovery/<id>."""

    class _EmitAgent:
        def __init__(self, session):
            self.session = session

        async def reply(self, msg):
            bp = {
                "company_profile": {"segment": "ecommerce"},
                "proposed_team": [
                    {
                        "name": "A",
                        "role": "r",
                        "objective": "o",
                        "tasks": [],
                        "tools_integrations": [],
                        "talks_to": [],
                    },
                ],
            }
            await self.session.emit_blueprint(json.dumps(bp))
            return _MsgStub("ok")

    monkeypatch.setattr(
        runner_mod,
        "_read_user_input",
        lambda prompt: "loja virtual",
    )
    monkeypatch.setattr(
        runner_mod,
        "build_discovery_agent",
        lambda session, **kw: _EmitAgent(session),
    )

    session = await runner_mod.run_discovery_cli(workspace_dir=tmp_path)
    assert session.emitted is True
    assert (tmp_path / "discovery").exists()
