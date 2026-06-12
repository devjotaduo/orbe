# -*- coding: utf-8 -*-
import importlib.util
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[3]
PLUGIN_DIR = ROOT / "plugins" / "bundle" / "a2ui-chat"

spec = importlib.util.spec_from_file_location(
    "a2ui_action_router",
    PLUGIN_DIR / "action_router.py",
)
assert spec is not None
assert spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(mod.router, prefix="/api/a2ui")
    return TestClient(app)


def test_action_echoes_data():
    r = _client().post(
        "/api/a2ui/action",
        json={"session_id": "s1", "action": "submit", "data": {"k": 1}},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["action"] == "submit"
    assert body["data"] == {"k": 1}


def test_action_rejects_empty_action():
    r = _client().post(
        "/api/a2ui/action",
        json={"session_id": "s1", "action": "", "data": {}},
    )
    assert r.status_code == 400


def test_action_defaults_empty_data():
    r = _client().post(
        "/api/a2ui/action",
        json={"session_id": "s1", "action": "click"},
    )
    assert r.status_code == 200
    assert r.json()["data"] == {}
