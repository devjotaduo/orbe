# -*- coding: utf-8 -*-
import json

import pytest
from pydantic import ValidationError

from qwenpaw.discovery.finalize import finalize_blueprint

VALID = {
    "company_profile": {"segment": "ecommerce", "name": "Loja X"},
    "process_map": [],
    "detected_integrations": [{"kind": "messaging", "name": "WhatsApp"}],
    "proposed_team": [
        {
            "name": "Atendente",
            "role": "atendimento",
            "objective": "responder clientes",
            "tasks": ["responder"],
            "tools_integrations": ["mcp:evolution-whatsapp"],
            "talks_to": [],
        },
    ],
    "roadmap": [],
    "open_questions": [],
}


def test_valid_blueprint_persists_json_and_md(tmp_path):
    bp = finalize_blueprint(VALID, tmp_path)
    assert bp.company_profile.segment == "ecommerce"
    data = json.loads((tmp_path / "blueprint.json").read_text("utf-8"))
    assert data["proposed_team"][0]["name"] == "Atendente"
    md = (tmp_path / "blueprint.md").read_text("utf-8")
    assert "Atendente" in md


def test_invalid_blueprint_raises_and_writes_nothing(tmp_path):
    bad = dict(VALID, proposed_team=[{"name": "sem-campos"}])
    with pytest.raises(ValidationError):
        finalize_blueprint(bad, tmp_path)
    assert not (tmp_path / "blueprint.json").exists()
