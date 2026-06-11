# -*- coding: utf-8 -*-
"""Testes de unidade do scoring de scripts/eval_discovery.py (sem LLM)."""
from __future__ import annotations

import importlib.util
import json
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
    from qwenpaw.discovery.state import DiscoveryState, Integration, Turn
    from qwenpaw.discovery.tools import DiscoverySession

    def _make(*, segment=None, emitted=True, n_integrations=2, n_turns=6):
        state = DiscoveryState(session_id="t")
        state.company.segment = segment
        state.integrations = [
            Integration(kind="whatsapp", name=f"tool{i}") for i in range(n_integrations)
        ]
        state.transcript = [
            Turn(role="user", text=f"resposta {i}") for i in range(n_turns)
        ]
        session = DiscoverySession(state, out_dir=tmp_path)
        session.emitted = emitted
        return session

    return _make


def _write_blueprint(tmp_path, *, agents=3, roadmap=3, processes=2, questions=2):
    bp = {
        "company_profile": {"segment": "ecommerce", "pains": []},
        "process_map": [
            {"name": f"p{i}", "description": "d"} for i in range(processes)
        ],
        "detected_integrations": [],
        "proposed_team": [
            {"name": f"A{i}", "role": "r", "objective": "o"} for i in range(agents)
        ],
        "roadmap": [
            {"order": i + 1, "title": f"t{i}", "rationale": "x"} for i in range(roadmap)
        ],
        "open_questions": [f"q{i}" for i in range(questions)],
    }
    path = tmp_path / "blueprint.json"
    path.write_text(json.dumps(bp), encoding="utf-8")
    return path


def test_perfect_session_scores_100(eval_mod, make_session, tmp_path):
    persona = eval_mod.PERSONAS[0]  # ecommerce_roupas
    session = make_session(segment="ecommerce")
    bp = _write_blueprint(tmp_path, agents=3, roadmap=3, processes=2, questions=2)
    result = eval_mod.score_session(persona, session, bp)
    assert result.total == result.max_total == 100


def test_wrong_segment_partial_credit(eval_mod, make_session, tmp_path):
    persona = eval_mod.PERSONAS[0]
    session = make_session(segment="varejo")
    bp = _write_blueprint(tmp_path)
    result = eval_mod.score_session(persona, session, bp)
    seg = next(c for c in result.criteria if c.name == "Segmento")
    assert seg.score == 8
    assert any("incorretamente" in i for i in result.issues)


def test_no_blueprint_zeroes_quality_criteria(eval_mod, make_session, tmp_path):
    persona = eval_mod.PERSONAS[0]
    session = make_session(segment="ecommerce", emitted=False)
    result = eval_mod.score_session(persona, session, tmp_path / "missing.json")
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
            )
        )
    report = eval_mod.generate_report(runs, "20260611_000000")
    for run in runs:
        assert run.persona.name in report
    assert "Média geral" in report
