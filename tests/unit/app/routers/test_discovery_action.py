# -*- coding: utf-8 -*-
import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from qwenpaw.app.routers import discovery_stream as ds

VALID = {
    "company_profile": {"segment": "ecommerce", "name": "Loja X"},
    "process_map": [],
    "detected_integrations": [],
    "proposed_team": [
        {
            "name": "Atendente",
            "role": "atendimento",
            "objective": "responder clientes",
            "tasks": [],
            "tools_integrations": [],
            "talks_to": [],
        },
    ],
    "roadmap": [],
    "open_questions": [],
}


def _events(text):
    return [
        json.loads(line[len("data: ") :])
        for line in text.splitlines()
        if line.startswith("data: ")
    ]


def _client():
    app = FastAPI()
    app.include_router(ds.router)
    return TestClient(app)


def test_approve_team_finalizes_and_finishes(tmp_path, monkeypatch):
    monkeypatch.setattr(ds, "_action_out_dir", lambda sid: tmp_path / sid)
    client = _client()
    r = client.post(
        "/discovery/action",
        json={"session_id": "s1", "action": "approve_team", "data": VALID},
    )
    assert r.status_code == 200
    types = [e["type"] for e in _events(r.text)]
    assert types[0] == "RUN_STARTED"
    assert types[-1] == "RUN_FINISHED"
    assert "RUN_ERROR" not in types
    assert (tmp_path / "s1" / "blueprint.json").exists()


def test_invalid_data_emits_run_error(tmp_path, monkeypatch):
    monkeypatch.setattr(ds, "_action_out_dir", lambda sid: tmp_path / sid)
    client = _client()
    r = client.post(
        "/discovery/action",
        json={
            "session_id": "s2",
            "action": "approve_team",
            "data": {"proposed_team": [{"name": "x"}]},
        },
    )
    types = [e["type"] for e in _events(r.text)]
    assert "RUN_ERROR" in types
    assert not (tmp_path / "s2" / "blueprint.json").exists()


def test_unknown_action_emits_run_error():
    client = _client()
    r = client.post(
        "/discovery/action",
        json={"session_id": "s3", "action": "fly_to_moon", "data": {}},
    )
    assert any(e["type"] == "RUN_ERROR" for e in _events(r.text))
