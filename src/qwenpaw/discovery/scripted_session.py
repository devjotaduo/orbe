# -*- coding: utf-8 -*-
"""A canned, LLM-free discovery interview for the A2UI/AG-UI cycle and tests.

Drives a fixed 3-question e-commerce/WhatsApp interview, then emits a canned
TeamBlueprint. The real LLM-driven runner (layer 1) will replace this behind
the same DiscoverySession protocol.
"""
from __future__ import annotations

from .session import TurnResult

_QUESTIONS = [
    "Qual é o segmento da sua empresa?",
    "Quais sistemas você já usa (CRM, planilha, WhatsApp)?",
    "Qual é a dor mais urgente que um agente resolveria primeiro?",
]

_BLUEPRINT = {
    "company_profile": {"segment": "ecommerce", "name": "Sua loja"},
    "process_map": [
        {"area": "Atendimento", "processes": ["responder WhatsApp"]}
    ],
    "detected_integrations": [
        {"type": "messaging", "name": "WhatsApp"},
        {"type": "spreadsheet", "name": "Planilha"},
    ],
    "proposed_team": [
        {
            "name": "Atendente WhatsApp",
            "role": "atendimento",
            "objective": "responder clientes no WhatsApp",
            "tasks": ["responder dúvidas", "registrar pedidos"],
            "tools_integrations": [
                "mcp:evolution-whatsapp",
                "mcp:google-sheets",
            ],
            "talks_to": [],
        }
    ],
    "roadmap": [
        {"step": "atendimento WhatsApp"},
        {"step": "registro em planilha"},
    ],
    "open_questions": ["Qual o volume médio de mensagens por dia?"],
}


class ScriptedDiscoverySession:
    def __init__(self) -> None:
        self._asked = 0
        self._state: dict = {
            "company": {},
            "open_areas": [],
            "integrations": [],
        }

    async def next_turn(self, user_message: str | None) -> TurnResult:
        # Record the answer to the previously asked question.
        if user_message is not None and self._asked >= 1:
            self._absorb(user_message)

        if self._asked < len(_QUESTIONS):
            q = _QUESTIONS[self._asked]
            self._asked += 1
            return TurnResult(state=dict(self._state), question=q, done=False)

        # No more questions → emit the blueprint.
        return TurnResult(
            state=dict(self._state), blueprint=_BLUEPRINT, done=True
        )

    def _absorb(self, answer: str) -> None:
        low = answer.lower()
        if self._asked == 1:  # answer to the segment question
            if "commerc" in low or "loja" in low or "venda" in low:
                self._state["company"]["segment"] = "ecommerce"
            else:
                self._state["company"]["segment"] = "outro"
                self._state["open_areas"].append({"topic": "validar segmento"})
        elif self._asked == 2:  # answer to the systems question
            if "whats" in low:
                self._state["integrations"].append(
                    {"type": "messaging", "name": "WhatsApp"}
                )
            if "planilh" in low or "sheet" in low:
                self._state["integrations"].append(
                    {"type": "spreadsheet", "name": "Planilha"}
                )
