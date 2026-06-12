# -*- coding: utf-8 -*-
"""Testes de unidade do scoring de scripts/eval_discovery.py (sem LLM)."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).parent.parent.parent / "scripts" / "eval_discovery.py"


@pytest.fixture(scope="module")
def eval_mod():
    spec = importlib.util.spec_from_file_location("eval_discovery", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    # @dataclass exige o módulo em sys.modules para resolver anotações
    sys.modules["eval_discovery"] = mod
    try:
        spec.loader.exec_module(mod)
        yield mod
    finally:
        sys.modules.pop("eval_discovery", None)


@pytest.fixture()
def make_session(tmp_path):
    from qwenpaw.discovery.state import (
        DiscoveryState,
        Integration,
        OnboardingInfo,
        Turn,
    )
    from qwenpaw.discovery.tools import DiscoverySession

    def _make(
        *,
        segment=None,
        emitted=True,
        n_integrations=2,
        n_turns=6,
        onboarding=True,
    ):
        state = DiscoveryState(session_id="t")
        state.company.segment = segment
        state.integrations = [
            Integration(kind="whatsapp", name=f"tool{i}")
            for i in range(n_integrations)
        ]
        state.transcript = [
            Turn(role="user", text=f"resposta {i}") for i in range(n_turns)
        ]
        if onboarding:
            state.onboarding = OnboardingInfo(
                whatsapp_number="+55 (11) 98765-4321",
                responsible_name="João",
            )
        session = DiscoverySession(state, out_dir=tmp_path)
        session.emitted = emitted
        return session

    return _make


def _write_requirements(tmp_path, *, agents=3):
    rep = {
        "summary_for_owner": "Olá! Por aqui vamos pedir o que falta.",
        "items": [
            {
                "agent_name": f"A{i}",
                "requests": [
                    {
                        "item": "info",
                        "why": "necessária",
                        "group_message": "Pode nos mandar?",
                    },
                ],
            }
            for i in range(agents)
        ],
    }
    path = tmp_path / "requirements.json"
    path.write_text(json.dumps(rep), encoding="utf-8")
    return path


def _write_blueprint(
    tmp_path,
    *,
    agents=3,
    roadmap=3,
    processes=2,
    questions=2,
):
    bp = {
        "company_profile": {"segment": "ecommerce", "pains": []},
        "process_map": [
            {"name": f"p{i}", "description": "d"} for i in range(processes)
        ],
        "detected_integrations": [],
        "proposed_team": [
            {"name": f"A{i}", "role": "r", "objective": "o"}
            for i in range(agents)
        ],
        "roadmap": [
            {"order": i + 1, "title": f"t{i}", "rationale": "x"}
            for i in range(roadmap)
        ],
        "open_questions": [f"q{i}" for i in range(questions)],
    }
    path = tmp_path / "blueprint.json"
    path.write_text(json.dumps(bp), encoding="utf-8")
    return path


def test_perfect_session_scores_full(eval_mod, make_session, tmp_path):
    persona = eval_mod.PERSONAS[0]  # ecommerce_roupas
    session = make_session(segment="ecommerce")
    bp = _write_blueprint(
        tmp_path,
        agents=3,
        roadmap=3,
        processes=2,
        questions=2,
    )
    _write_requirements(tmp_path, agents=3)
    result = eval_mod.score_session(persona, session, bp)
    # 100 originais + 10 onboarding + 10 requisitos
    assert result.total == result.max_total == 120


def test_missing_onboarding_flagged(eval_mod, make_session, tmp_path):
    persona = eval_mod.PERSONAS[0]
    session = make_session(segment="ecommerce", onboarding=False)
    bp = _write_blueprint(tmp_path)
    _write_requirements(tmp_path)
    result = eval_mod.score_session(persona, session, bp)
    ob = next(c for c in result.criteria if c.name == "Onboarding WhatsApp")
    assert ob.score == 0
    assert any("Onboarding NÃO registrado" in i for i in result.issues)


def test_missing_requirements_flagged(eval_mod, make_session, tmp_path):
    persona = eval_mod.PERSONAS[0]
    session = make_session(segment="ecommerce")
    bp = _write_blueprint(tmp_path)  # sem requirements.json
    result = eval_mod.score_session(persona, session, bp)
    req = next(c for c in result.criteria if c.name == "Requisitos por agente")
    assert req.score == 0
    assert any("Requisitos NÃO gerados" in i for i in result.issues)


def test_wrong_segment_partial_credit(eval_mod, make_session, tmp_path):
    persona = eval_mod.PERSONAS[0]
    session = make_session(segment="varejo")
    bp = _write_blueprint(tmp_path)
    result = eval_mod.score_session(persona, session, bp)
    seg = next(c for c in result.criteria if c.name == "Segmento")
    assert seg.score == 8
    assert any("incorretamente" in i for i in result.issues)


def test_no_blueprint_zeroes_quality_criteria(
    eval_mod,
    make_session,
    tmp_path,
):
    persona = eval_mod.PERSONAS[0]
    session = make_session(segment="ecommerce", emitted=False)
    result = eval_mod.score_session(
        persona,
        session,
        tmp_path / "missing.json",
    )
    by_name = {c.name: c for c in result.criteria}
    assert by_name["Blueprint gerado"].score == 0
    assert by_name["Agentes propostos"].score == 0
    assert by_name["Roadmap"].score == 0


def test_single_agent_flagged_as_issue(eval_mod, make_session, tmp_path):
    persona = eval_mod.PERSONAS[0]
    session = make_session(segment="ecommerce")
    bp = _write_blueprint(tmp_path, agents=1)
    result = eval_mod.score_session(persona, session, bp)
    assert any("1 agente" in i for i in result.issues)


def test_grade_thresholds(eval_mod):
    assert eval_mod._grade(95).startswith("A")
    assert eval_mod._grade(80).startswith("B")
    assert eval_mod._grade(65).startswith("C")
    assert eval_mod._grade(50).startswith("D")
    assert eval_mod._grade(10).startswith("F")


def test_advocacia_persona_maps_to_servicos_b2b(eval_mod):
    """A persona de advocacia existe e sua 1ª fala casa o segmento na seed."""
    from qwenpaw.discovery.segments.taxonomy import lookup_segment

    persona = next(p for p in eval_mod.PERSONAS if p.id == "advocacia")
    assert persona.expected_segment == "servicos_b2b"
    info = lookup_segment(persona.script[0])
    assert info is not None
    assert info.key == "servicos_b2b"


def test_recommendations_derived_from_issues(eval_mod, make_session, tmp_path):
    """Recomendações citam só os problemas encontrados na rodada."""
    persona = eval_mod.PERSONAS[0]
    session = make_session(segment="varejo")  # segmento errado de propósito
    bp = _write_blueprint(tmp_path, agents=1)  # time insuficiente
    score = eval_mod.score_session(persona, session, bp)
    run = eval_mod.SessionRun(
        persona=persona,
        score=score,
        stdout_log="",
        session=session,
        out_dir=tmp_path,
    )
    recs = eval_mod._build_recommendations([run])
    joined = " ".join(recs)
    assert "classificação de segmento" in joined
    assert "time mínimo" in joined
    # nada de recomendação genérica de manutenção quando há problemas
    assert "Nenhum problema recorrente" not in joined


def test_recommendations_fall_back_to_maintenance(
    eval_mod,
    make_session,
    tmp_path,
):
    """Rodada perfeita gera recomendações de manutenção, não de conserto."""
    persona = eval_mod.PERSONAS[0]
    session = make_session(segment=persona.expected_segment)
    bp = _write_blueprint(tmp_path)
    _write_requirements(tmp_path)
    score = eval_mod.score_session(persona, session, bp)
    assert score.total == score.max_total  # sanidade: rodada perfeita
    run = eval_mod.SessionRun(
        persona=persona,
        score=score,
        stdout_log="",
        session=session,
        out_dir=tmp_path,
    )
    recs = eval_mod._build_recommendations([run])
    assert any("Nenhum problema recorrente" in r for r in recs)


@pytest.mark.skipif(
    not os.environ.get("QWENPAW_EVAL_E2E"),
    reason="smoke e2e usa LLM real — setar QWENPAW_EVAL_E2E=1 para rodar",
)
def test_e2e_smoke_single_persona(eval_mod, tmp_path):
    """Gate de regressão: 1 persona real de ponta a ponta com o LLM ativo."""
    import asyncio

    persona = next(p for p in eval_mod.PERSONAS if p.id == "ecommerce_roupas")
    run = asyncio.run(eval_mod._run_persona(persona, tmp_path))
    assert run.score.error is None, run.score.error
    assert (
        run.score.pct >= 60
    ), f"Regressão de qualidade: {run.score.pct:.0f}% < 60%"


def test_out_of_seed_persona_accepts_free_description(
    eval_mod,
    make_session,
    tmp_path,
):
    """Persona fora da seed pontua 20 se a descrição livre menciona o ramo."""
    persona = next(p for p in eval_mod.PERSONAS if p.id == "petshop")
    assert persona.expected_segment is None
    session = make_session(segment="Pet shop / banho e tosa")
    bp = _write_blueprint(tmp_path)
    result = eval_mod.score_session(persona, session, bp)
    seg = next(c for c in result.criteria if c.name == "Segmento")
    assert seg.score == 20


def test_out_of_seed_persona_rejects_unrelated_description(
    eval_mod,
    make_session,
    tmp_path,
):
    persona = next(p for p in eval_mod.PERSONAS if p.id == "petshop")
    session = make_session(segment="restaurante")
    bp = _write_blueprint(tmp_path)
    result = eval_mod.score_session(persona, session, bp)
    seg = next(c for c in result.criteria if c.name == "Segmento")
    assert seg.score == 8
    assert any("incorretamente" in i for i in result.issues)


def test_out_of_seed_persona_zero_when_missing(
    eval_mod,
    make_session,
    tmp_path,
):
    persona = next(p for p in eval_mod.PERSONAS if p.id == "oficina_mecanica")
    session = make_session(segment=None)
    bp = _write_blueprint(tmp_path)
    result = eval_mod.score_session(persona, session, bp)
    seg = next(c for c in result.criteria if c.name == "Segmento")
    assert seg.score == 0


def test_qualitative_issue_maps_to_recommendation(
    eval_mod,
    make_session,
    tmp_path,
):
    """Nota baixa do juiz vira issue e recomendação conversacional."""
    persona = eval_mod.PERSONAS[0]
    session = make_session(segment=persona.expected_segment)
    bp = _write_blueprint(tmp_path)
    score = eval_mod.score_session(persona, session, bp)
    score.issues.append(
        "Qualidade conversacional abaixo do esperado (não-repetição: 4/10) — "
        "repetiu a mesma pergunta 4 vezes",
    )
    run = eval_mod.SessionRun(
        persona=persona,
        score=score,
        stdout_log="",
        session=session,
        out_dir=tmp_path,
        qual={
            "clareza": 9,
            "empatia": 9,
            "nao_repeticao": 4,
            "linguagem_simples": 9,
            "justificativa": "repetiu a mesma pergunta 4 vezes",
        },
    )
    recs = eval_mod._build_recommendations([run])
    assert any("condução conversacional" in r for r in recs)


def test_report_renders_qualitative_section(eval_mod, make_session, tmp_path):
    persona = eval_mod.PERSONAS[0]
    session = make_session(segment=persona.expected_segment)
    bp = _write_blueprint(tmp_path)
    score = eval_mod.score_session(persona, session, bp)
    run = eval_mod.SessionRun(
        persona=persona,
        score=score,
        stdout_log="Você: oi",
        session=session,
        out_dir=tmp_path,
        qual={
            "clareza": 8,
            "empatia": 9,
            "nao_repeticao": 7,
            "linguagem_simples": 9,
            "justificativa": "Condução clara e acolhedora.",
        },
    )
    report = eval_mod.generate_report([run], "20260611_000000")
    assert "LLM-as-judge" in report
    assert "33/40" in report
    assert "Condução clara e acolhedora." in report


def test_report_includes_all_personas(eval_mod, make_session, tmp_path):
    runs = []
    for persona in eval_mod.PERSONAS[:2]:
        session = make_session(segment=persona.expected_segment)
        bp = _write_blueprint(tmp_path)
        score = eval_mod.score_session(persona, session, bp)
        runs.append(
            eval_mod.SessionRun(
                persona=persona,
                score=score,
                stdout_log="Você: oi\nConsultor: olá",
                session=session,
                out_dir=tmp_path,
            ),
        )
    report = eval_mod.generate_report(runs, "20260611_000000")
    for run in runs:
        assert run.persona.name in report
    assert "Média geral" in report
