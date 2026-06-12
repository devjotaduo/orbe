# -*- coding: utf-8 -*-
"""build_discovery_system_prompt (Task 4): prompt de entrevista + schema.

O prompt precisa (a) instruir a entrevista de raciocínio (uma pergunta por
vez, ``reflect`` antes de perguntar, desencorajar blueprint cedo) e (b)
embutir um JSON schema do ``TeamBlueprint`` que o modelo possa seguir em
``emit_blueprint``. Sem LLM — só verifica o texto e o JSON embutido.
"""

import json
import re

from qwenpaw.discovery.prompts import build_discovery_system_prompt
from qwenpaw.discovery.state import TeamBlueprint


def test_prompt_contains_reasoning_interview_rules():
    prompt = build_discovery_system_prompt()
    low = prompt.lower()
    # Entrevista, não formulário.
    assert "não é um formulário" in low or "nao e um formulario" in low
    # reflect antes da próxima pergunta.
    assert "reflect" in prompt
    # Uma pergunta por vez.
    assert "uma pergunta" in low
    # Desencoraja emitir o blueprint cedo.
    assert "emit_blueprint" in prompt
    assert "cedo" in low


def test_prompt_embeds_valid_teamblueprint_schema():
    prompt = build_discovery_system_prompt()
    # O schema é embutido como JSON; extrai o último bloco { ... }.
    start = prompt.index("{")
    embedded = prompt[start:]
    schema = json.loads(embedded)
    # É de fato o schema do TeamBlueprint (campos lidos pelo a2ui/builder).
    assert schema == TeamBlueprint.model_json_schema()
    assert "properties" in schema or "$defs" in schema
    # Campos-contrato presentes no schema (diretos ou via $defs).
    blob = json.dumps(schema)
    for field in (
        "company_profile",
        "proposed_team",
        "detected_integrations",
        "open_questions",
    ):
        assert field in blob


def test_prompt_is_deterministic_and_portuguese():
    a = build_discovery_system_prompt()
    b = build_discovery_system_prompt()
    assert a == b  # determinístico (sem timestamp/random)
    # Português do Brasil no corpo do prompt.
    assert re.search(r"\bvocê\b|\bempres", a, re.IGNORECASE)
