# -*- coding: utf-8 -*-
"""Loop de terminal do discovery agent + persistência da sessão."""
from __future__ import annotations

from pathlib import Path

from agentscope.message import UserMsg

from .agent import build_discovery_agent
from .state import DiscoveryState, OpenArea, Turn
from .tools import DiscoverySession

_GREETING = (
    "Olá! Vou te ajudar a montar um time de agentes para a sua empresa. "
    "Me conta: o que a sua empresa faz?"
)
_SEED_AREA = OpenArea(
    id="segmento",
    topic="qual o segmento/negócio da empresa",
    confidence=0.0,
    priority=5,
)


def _read_user_input(prompt: str) -> str:  # isolado p/ teste (monkeypatch)
    return input(prompt)


def _persist(state: DiscoveryState, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "discovery_state.json").write_text(
        state.model_dump_json(indent=2), encoding="utf-8"
    )


async def run_discovery_session(
    session_id: str, out_dir: Path
) -> DiscoverySession:
    """Conduz a entrevista no terminal e retorna a sessão (com estado/flags)."""
    out_dir = Path(out_dir)
    state = DiscoveryState(session_id=session_id)
    state.open_areas.append(_SEED_AREA)
    session = DiscoverySession(state, out_dir=out_dir)
    agent = build_discovery_agent(session)

    print(_GREETING)
    while not session.emitted:
        user_text = _read_user_input("\nVocê: ").strip()
        if user_text.lower() in ("/fim", "/sair", "exit", "quit"):
            # pede ao agente que feche com o que já sabe
            close_text = (
                "Pode encerrar a entrevista e gerar o blueprint com o "
                "que já temos, listando o que ficou em aberto."
            )
            state.transcript.append(Turn(role="user", text="/fim"))
            reply = await agent.reply(UserMsg(name="user", content=close_text))
            _persist(state, out_dir)
            print(f"\nConsultor: {reply.get_text_content()}")
            break
        state.transcript.append(Turn(role="user", text=user_text))
        reply = await agent.reply(UserMsg(name="user", content=user_text))
        _persist(state, out_dir)
        print(f"\nConsultor: {reply.get_text_content()}")

    if not session.emitted:
        print("\n(Entrevista encerrada sem blueprint — estado salvo para retomar.)")
    return session
