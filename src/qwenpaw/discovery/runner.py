# -*- coding: utf-8 -*-
"""Loop de terminal do discovery agent + persistência da sessão."""
from __future__ import annotations

from pathlib import Path

from agentscope.message import UserMsg

from .agent import build_discovery_agent
from .requirements import build_requirements_agent, build_requirements_input
from .state import DiscoveryState, OpenArea, Turn
from .tools import DiscoverySession

_GREETING = """\
Olá! Seja muito bem-vindo(a). 🤝

Meu nome é Orbe e sou especialista em implementação de inteligência \
artificial para negócios. Já ajudei dezenas de empresas brasileiras a \
montar times de agentes que trabalham 24 horas por dia — atendendo \
clientes, criando conteúdo para redes sociais, gerenciando pedidos, \
automatizando orçamentos e muito mais.

Antes de qualquer proposta, quero entender bem a sua realidade. Não \
existe solução pronta: o plano certo depende do que você faz, de como \
você opera e de onde você quer chegar.

Então me conta: **o que a sua empresa faz** e qual é o maior desafio \
que você enfrenta hoje no dia a dia?\
"""
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
    state.open_areas.append(_SEED_AREA.model_copy())  # cópia: evita mutar o singleton
    session = DiscoverySession(state, out_dir=out_dir)
    agent = build_discovery_agent(session)

    print(_GREETING)
    while not session.emitted:
        try:
            user_text = _read_user_input("\nVocê: ").strip()
        except EOFError:
            # stdin encerrado (pipe/CI): persiste o que já foi coletado e sai
            _persist(state, out_dir)
            break
        if user_text.lower() in ("/fim", "/sair", "exit", "quit"):
            # pede ao agente que feche com o que já sabe
            close_text = (
                "Pode encerrar a entrevista e gerar o blueprint com o "
                "que já temos, listando o que ficou em aberto. Antes de "
                "emitir, peça meu WhatsApp para o onboarding."
            )
            state.transcript.append(Turn(role="user", text="/fim"))
            reply = await agent.reply(UserMsg(name="user", content=close_text))
            _persist(state, out_dir)
            print(f"\nConsultor: {reply.get_text_content()}")
            if not session.emitted:
                break
            # /fim com onboarding pendente: dá UMA chance de informar o número
            if state.onboarding is None:
                try:
                    contact = _read_user_input("\nVocê: ").strip()
                except EOFError:
                    break
                if contact:
                    state.transcript.append(Turn(role="user", text=contact))
                    reply = await agent.reply(
                        UserMsg(name="user", content=contact)
                    )
                    _persist(state, out_dir)
                    print(f"\nConsultor: {reply.get_text_content()}")
            break
        state.transcript.append(Turn(role="user", text=user_text))
        reply = await agent.reply(UserMsg(name="user", content=user_text))
        _persist(state, out_dir)
        print(f"\nConsultor: {reply.get_text_content()}")

    if session.emitted:
        await _run_requirements_phase(session)
        _persist(state, out_dir)
    else:
        print("\n(Entrevista encerrada sem blueprint — estado salvo para retomar.)")
    return session


async def _run_requirements_phase(session: DiscoverySession) -> None:
    """Fase pós-blueprint: levanta informações pendentes por agente."""
    print("\n(Levantando as informações que faltam para o seu time começar...)")
    try:
        agent = build_requirements_agent(session)
        await agent.reply(
            UserMsg(name="user", content=build_requirements_input(session))
        )
    except Exception as exc:  # não derruba a sessão: blueprint já está salvo
        print(f"\n(Não consegui gerar a lista de pendências agora: {exc})")
        return
    if not session.requirements_emitted or session.requirements is None:
        print("\n(Lista de pendências não foi gerada — tente novamente depois.)")
        return
    report = session.requirements
    print(f"\nConsultor: {report.summary_for_owner}")
    print("\nO que vamos pedir no grupo do WhatsApp:")
    for item in report.items:
        if not item.requests:
            continue
        print(f"\n  {item.agent_name}:")
        for req in item.requests:
            print(f"   - {req.item}")
    print(
        f"\n(Detalhes em {session.out_dir / 'informacoes_pendentes.md'} e "
        f"mensagens prontas em {session.out_dir / 'mensagens_grupo.md'})"
    )
