# -*- coding: utf-8 -*-
"""Tests for qwenpaw_ext.nexora.repositories.audit_postgres (mocked engine).

No real PostgreSQL: a fake engine records the executed SQL text and bound
parameters so the query/filter building can be asserted deterministically.
"""

# pylint: disable=redefined-outer-name,unused-argument

from contextlib import contextmanager

import pytest

from qwenpaw_ext.nexora import db


@pytest.fixture()
def audit_postgres():
    """Import the repository lazily so collection never pulls sqlalchemy.

    (tests/unit/app/test_enterprise_bridge.py asserts that importing the
    bridge alone does not import sqlalchemy; a module-level import here
    would defeat that check during combined runs.)
    """
    pytest.importorskip("sqlalchemy")
    from qwenpaw_ext.nexora.repositories import (  # noqa: PLC0415
        audit_postgres as module,
    )

    return module


class _FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def mappings(self):
        return self

    def all(self):
        return self._rows


class _FakeConnection:
    def __init__(self, log, rows):
        self._log = log
        self._rows = rows

    def execute(self, query, params=None):
        self._log.append((str(query), params))
        return _FakeResult(self._rows)


class _FakeEngine:
    def __init__(self):
        self.log = []
        self.rows = []

    @contextmanager
    def begin(self):
        yield _FakeConnection(self.log, self.rows)


@pytest.fixture()
def fake_engine(monkeypatch):
    engine = _FakeEngine()
    monkeypatch.setattr(db, "initialize_schema", lambda: None)
    monkeypatch.setattr(db, "get_engine", lambda: engine)
    return engine


def test_insert_event_binds_all_columns(fake_engine, audit_postgres):
    event = {
        "id": "abc123",
        "timestamp": 1700000000,
        "actor": "alice",
        "action": "auth.login",
        "resource_type": "user",
        "resource_id": "alice",
        "status": "success",
        "ip": "10.0.0.1",
        "user_agent": "pytest",
        "detail": {"k": 1},
    }
    audit_postgres.insert_event(event)

    assert len(fake_engine.log) == 1
    sql, params = fake_engine.log[0]
    assert "INSERT INTO nexora_audit_events" in sql
    assert params["id"] == "abc123"
    assert params["actor"] == "alice"
    # detail is serialized to a compact JSON string for CAST(... AS JSONB).
    assert params["detail"] == '{"k":1}'


def test_insert_event_defaults_for_missing_fields(fake_engine, audit_postgres):
    audit_postgres.insert_event({"id": "x1", "timestamp": 1, "actor": ""})

    _, params = fake_engine.log[0]
    assert params["actor"] == "anonymous"
    assert params["action"] == ""
    assert params["status"] == "success"
    assert params["detail"] == "{}"


def test_list_events_without_filters(fake_engine, audit_postgres):
    result = audit_postgres.list_events()

    assert result == []
    sql, params = fake_engine.log[0]
    assert "WHERE" not in sql
    assert "ORDER BY created_at DESC" in sql
    assert params == {"limit": 200}


def test_list_events_builds_all_filters(fake_engine, audit_postgres):
    audit_postgres.list_events(
        limit=10,
        actor="ali",
        action="auth",
        status="denied",
        start_time=100,
        end_time=200,
    )

    sql, params = fake_engine.log[0]
    assert "actor ILIKE :actor" in sql
    assert "action ILIKE :action" in sql
    assert "status = :status" in sql
    assert "timestamp >= :start_time" in sql
    assert "timestamp <= :end_time" in sql
    assert params == {
        "limit": 10,
        "actor": "%ali%",
        "action": "%auth%",
        "status": "denied",
        "start_time": 100,
        "end_time": 200,
    }


@pytest.mark.parametrize(
    "requested,effective",
    [(0, 1), (-5, 1), (1000, 1000), (5000, 1000)],
)
def test_list_events_clamps_limit(
    fake_engine, audit_postgres, requested, effective
):
    audit_postgres.list_events(limit=requested)

    _, params = fake_engine.log[0]
    assert params["limit"] == effective


def test_list_events_converts_rows_and_parses_detail(
    fake_engine, audit_postgres
):
    fake_engine.rows = [
        {
            "id": "e1",
            "timestamp": 123,
            "actor": "alice",
            "action": "auth.login",
            "resource_type": "",
            "resource_id": "",
            "status": "success",
            "ip": "",
            "user_agent": "",
            # psycopg2 may hand JSONB back as str depending on adapters.
            "detail": '{"k":1}',
        },
        {
            "id": "e2",
            "timestamp": 124,
            "actor": "bob",
            "action": "agents.delete",
            "resource_type": "agent",
            "resource_id": "a1",
            "status": "denied",
            "ip": "10.0.0.2",
            "user_agent": "pytest",
            "detail": {"already": "dict"},
        },
    ]

    events = audit_postgres.list_events()

    assert [e["id"] for e in events] == ["e1", "e2"]
    assert events[0]["detail"] == {"k": 1}
    assert events[1]["detail"] == {"already": "dict"}


def test_list_events_detail_invalid_json_becomes_empty_dict(
    fake_engine, audit_postgres
):
    row = {
        "id": "e1",
        "timestamp": 1,
        "actor": "a",
        "action": "b",
        "resource_type": "",
        "resource_id": "",
        "status": "success",
        "ip": "",
        "user_agent": "",
        "detail": "{not json",
    }
    fake_engine.rows = [row]

    events = audit_postgres.list_events()

    assert events[0]["detail"] == {}
