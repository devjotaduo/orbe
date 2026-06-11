# -*- coding: utf-8 -*-
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient
from qwenpaw.app.routers import discovery_stream as ds


def _events_from(resp_text: str) -> list[dict]:
    out = []
    for line in resp_text.splitlines():
        if line.startswith("data: "):
            out.append(json.loads(line[len("data: ") :]))
    return out


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(ds.router)
    return TestClient(app)


def test_opening_turn_streams_run_started_text_and_state():
    client = _client()
    r = client.post(
        "/discovery/stream", json={"session_id": "s1", "message": None}
    )
    assert r.status_code == 200
    types = [e["type"] for e in _events_from(r.text)]
    assert types[0] == "RUN_STARTED"
    assert "TEXT_MESSAGE_CONTENT" in types
    assert "STATE_SNAPSHOT" in types
    assert types[-1] == "RUN_FINISHED"


def test_final_turn_emits_custom_a2ui_surface():
    client = _client()
    client.post(
        "/discovery/stream", json={"session_id": "s2", "message": None}
    )
    for msg in [
        "e-commerce de roupas",
        "uso WhatsApp e planilha",
        "responder clientes",
    ]:
        r = client.post(
            "/discovery/stream", json={"session_id": "s2", "message": msg}
        )
    events = _events_from(r.text)
    custom = [
        e for e in events if e["type"] == "CUSTOM" and e["name"] == "a2ui"
    ]
    assert custom, "expected an A2UI CUSTOM event on the final turn"
    # The CUSTOM value is one A2UI message; createSurface should
    # appear across the turn.
    msg_types = {c["value"]["messageType"] for c in custom}
    assert "createSurface" in msg_types
    assert {"updateComponents", "updateDataModel"} <= msg_types


def test_unknown_segment_still_completes(monkeypatch):
    client = _client()
    client.post(
        "/discovery/stream", json={"session_id": "s3", "message": None}
    )
    for msg in ["consultoria jurídica", "uso email", "organizar processos"]:
        r = client.post(
            "/discovery/stream", json={"session_id": "s3", "message": msg}
        )
    types = [e["type"] for e in _events_from(r.text)]
    assert types[-1] == "RUN_FINISHED"
