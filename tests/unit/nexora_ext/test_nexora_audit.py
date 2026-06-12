# -*- coding: utf-8 -*-
"""Tests for qwenpaw_ext.nexora.audit JSONL fallback (no PostgreSQL)."""

# pylint: disable=redefined-outer-name,unused-argument

import json
import sys
import types

import pytest

from qwenpaw_ext.nexora import audit, db, repositories


@pytest.fixture()
def audit_file(tmp_path, monkeypatch):
    """Redirect the JSONL audit file to tmp and disable the database."""
    monkeypatch.delenv(db.DB_URL_ENV, raising=False)
    path = tmp_path / "nexora_audit.jsonl"
    monkeypatch.setattr(audit, "AUDIT_FILE", path)
    return path


@pytest.fixture()
def pg_stub(monkeypatch):
    """Enable the DB and replace the audit_postgres repository by a stub.

    Returns the stub module; tests assign ``insert_event`` / ``list_events``
    on it.  Avoids importing the real repository (and thus sqlalchemy).
    """
    monkeypatch.setenv(db.DB_URL_ENV, "postgresql://user:pw@localhost/cj")
    stub = types.ModuleType("qwenpaw_ext.nexora.repositories.audit_postgres")
    monkeypatch.setattr(repositories, "audit_postgres", stub, raising=False)
    monkeypatch.setitem(sys.modules, stub.__name__, stub)
    return stub


def test_record_audit_event_writes_jsonl(audit_file):
    event = audit.record_audit_event(
        actor="alice",
        action="auth.login",
        resource_type="user",
        resource_id="alice",
        detail={"channel": "console"},
    )
    assert audit_file.is_file()
    lines = audit_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    stored = json.loads(lines[0])
    assert stored["id"] == event["id"]
    assert stored["actor"] == "alice"
    assert stored["action"] == "auth.login"
    assert stored["status"] == "success"
    assert stored["detail"] == {"channel": "console"}


def test_record_audit_event_defaults_anonymous_actor(audit_file):
    event = audit.record_audit_event(actor="", action="x.y")
    assert event["actor"] == "anonymous"


def test_list_audit_events_filters(audit_file):
    audit.record_audit_event(actor="alice", action="auth.login")
    audit.record_audit_event(
        actor="bob",
        action="agents.delete",
        status="denied",
    )
    audit.record_audit_event(actor="bob", action="auth.login")

    by_actor = audit.list_audit_events(actor="bob")
    assert len(by_actor) == 2
    assert all("bob" in e["actor"] for e in by_actor)

    by_action = audit.list_audit_events(action="agents.delete")
    assert len(by_action) == 1

    by_status = audit.list_audit_events(status="denied")
    assert len(by_status) == 1
    assert by_status[0]["actor"] == "bob"


def test_list_audit_events_time_window_and_limit(audit_file):
    for i in range(5):
        audit.record_audit_event(actor=f"user{i}", action="a.b")

    events = audit.list_audit_events(limit=2)
    assert len(events) == 2
    # Newest first: last recorded actor comes first.
    assert events[0]["actor"] == "user4"

    now = events[0]["timestamp"]
    assert audit.list_audit_events(start_time=now + 100) == []
    assert audit.list_audit_events(end_time=now - 100) == []
    assert len(audit.list_audit_events(start_time=0, end_time=now + 100)) == 5


def test_list_audit_events_empty_without_file(audit_file):
    assert audit.list_audit_events() == []


def test_record_audit_event_uses_postgres_when_db_enabled(
    audit_file, pg_stub
):
    inserted = []
    pg_stub.insert_event = inserted.append

    event = audit.record_audit_event(actor="alice", action="auth.login")

    assert inserted == [event]
    # Persisted in PG: the JSONL fallback must NOT be written.
    assert not audit_file.exists()


def test_record_audit_event_falls_back_to_jsonl_when_pg_fails(
    audit_file, pg_stub
):
    def _boom(event):
        raise RuntimeError("pg down")

    pg_stub.insert_event = _boom

    event = audit.record_audit_event(
        actor="alice",
        action="auth.login",
        detail={"k": 1},
    )

    # The event is still returned and persisted in the JSONL fallback.
    assert event["actor"] == "alice"
    assert audit_file.is_file()
    lines = audit_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    stored = json.loads(lines[0])
    assert stored["id"] == event["id"]
    assert stored["detail"] == {"k": 1}


def test_list_audit_events_uses_postgres_when_db_enabled(
    audit_file, pg_stub
):
    sentinel = [{"id": "abc", "action": "auth.login"}]
    calls = []

    def _list_events(**kwargs):
        calls.append(kwargs)
        return sentinel

    pg_stub.list_events = _list_events

    result = audit.list_audit_events(limit=7, actor="alice")

    assert result is sentinel
    assert calls == [
        {
            "limit": 7,
            "actor": "alice",
            "action": None,
            "status": None,
            "start_time": None,
            "end_time": None,
        }
    ]


def test_list_audit_events_returns_empty_when_pg_fails(audit_file, pg_stub):
    def _boom(**kwargs):
        raise RuntimeError("pg down")

    pg_stub.list_events = _boom

    assert audit.list_audit_events() == []


def test_safe_preview_passthrough_scalars():
    assert audit.safe_preview(None) is None
    assert audit.safe_preview(5) == 5
    assert audit.safe_preview(True) is True
    assert audit.safe_preview("short") == "short"


def test_safe_preview_truncates_long_values():
    long_string = "x" * 3000
    preview = audit.safe_preview(long_string, max_length=100)
    assert preview.endswith("...")
    assert len(preview) == 103

    rendered = audit.safe_preview({"k": "y" * 3000}, max_length=100)
    assert isinstance(rendered, str)
    assert rendered.endswith("...")
