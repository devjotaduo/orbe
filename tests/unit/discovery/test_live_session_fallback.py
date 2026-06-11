# -*- coding: utf-8 -*-
"""Critério de parada por ``ready_to_emit`` (Addendum) na LiveDiscoverySession.

Além do caminho em que o agente chama ``emit_blueprint`` (coberto em
``test_live_session.py``), há o fallback: quando as áreas críticas estão
satisfeitas E o perfil mínimo (``company.segment``) está preenchido,
``_is_done`` dispara e ``next_turn`` deriva um blueprint do estado — sem o
agente ter gravado ``blueprint.json``. Aqui o ``FakeAgent`` só preenche o
estado (sem emitir) e checamos a derivação. LLM mockado.
"""

from qwenpaw.discovery import live_session as live_mod
from qwenpaw.discovery.live_session import LiveDiscoverySession
from qwenpaw.discovery.state import Integration, TeamBlueprint


class _MsgStub:
    def __init__(self, text: str) -> None:
        self._t = text

    def get_text_content(self) -> str:
        return self._t


class _StateFillingAgent:
    """Preenche o estado de modo a satisfazer ``ready_to_emit`` SEM emitir."""

    def __init__(self, session) -> None:
        self.session = session
        self._turn = 0

    async def reply(self, msg):
        self._turn += 1
        st = self.session.state
        if self._turn == 1:
            return _MsgStub("O que a sua empresa faz?")
        # 2º turno: fecha a área crítica (confiança alta) e preenche o
        # perfil mínimo + uma integração — mas NÃO chama emit_blueprint.
        st.company.segment = "ecommerce"
        for area in st.open_areas:
            area.confidence = 0.95
        st.integrations.append(
            Integration(kind="whatsapp", name="WhatsApp", confidence=0.9),
        )
        return _MsgStub("Como você atende seus clientes hoje?")


def _patch_agent(monkeypatch):
    monkeypatch.setattr(
        live_mod.runner_mod,
        "build_discovery_agent",
        lambda session, **kw: _StateFillingAgent(session),
    )


async def test_ready_to_emit_derives_blueprint_from_state(
    tmp_path,
    monkeypatch,
):
    _patch_agent(monkeypatch)
    sess = LiveDiscoverySession(session_id="fb1", out_dir=tmp_path)

    r0 = await sess.next_turn(None)
    assert r0.done is False

    # 2ª resposta satisfaz ready_to_emit; o agente NÃO emitiu blueprint.json.
    r1 = await sess.next_turn("tenho uma loja virtual")
    assert sess._session.emitted is False  # nada gravado pelo agente
    assert r1.done is True
    assert r1.question is None
    assert r1.blueprint is not None

    # Blueprint derivado é válido contra o schema e carrega os campos-contrato.
    bp = TeamBlueprint.model_validate(r1.blueprint)
    assert bp.company_profile.segment == "ecommerce"
    assert r1.blueprint["detected_integrations"][0]["name"] == "WhatsApp"
    # open_questions vem das áreas que sobraram em aberto.
    assert isinstance(r1.blueprint["open_questions"], list)


async def test_not_done_without_segment_even_if_areas_closed(
    tmp_path,
    monkeypatch,
):
    """Sem ``company.segment``, ``ready_to_emit`` sozinho não encerra."""

    class _NoSegmentAgent:
        def __init__(self, session) -> None:
            self.session = session

        async def reply(self, msg):
            st = self.session.state
            # Fecha as áreas, mas deixa o perfil sem segmento.
            for area in st.open_areas:
                area.confidence = 0.99
            return _MsgStub("E quais sistemas você usa?")

    monkeypatch.setattr(
        live_mod.runner_mod,
        "build_discovery_agent",
        lambda session, **kw: _NoSegmentAgent(session),
    )
    sess = LiveDiscoverySession(session_id="fb2", out_dir=tmp_path)
    r0 = await sess.next_turn(None)
    # Áreas fechadas mas sem segmento -> não encerra (evita blueprint raso).
    assert r0.done is False
    assert r0.question
