# -*- coding: utf-8 -*-
"""Tests for the qwenpaw.app.enterprise bridge module."""

import importlib
import sys

import pytest

from qwenpaw.app import enterprise


def test_bridge_delegates_when_extension_present(monkeypatch, tmp_path):
    """Extension importable but DB disabled: everything degrades safely."""
    assert enterprise.ENTERPRISE_AVAILABLE is True
    monkeypatch.delenv("NEXORA_DB_URL", raising=False)

    from qwenpaw_ext.nexora import audit as nexora_audit

    monkeypatch.setattr(
        nexora_audit,
        "AUDIT_FILE",
        tmp_path / "audit.jsonl",
    )

    assert enterprise.is_database_enabled() is False
    assert enterprise.get_engine() is None
    assert enterprise.check_database_health() is None
    assert enterprise.initialize_schema() is None

    event = enterprise.record_audit_event(
        actor="alice",
        action="test.action",
        detail={"k": 1},
    )
    assert event["actor"] == "alice"
    assert event["action"] == "test.action"
    assert event["status"] == "success"
    # Delegated to the extension: persisted in the JSONL fallback.
    assert (tmp_path / "audit.jsonl").is_file()


def test_bridge_fallback_when_extension_missing():
    """Simulate qwenpaw_ext absent: bridge must expose no-ops."""
    saved = {
        name: sys.modules[name]
        for name in list(sys.modules)
        if name == "qwenpaw_ext" or name.startswith("qwenpaw_ext.")
    }
    for name in saved:
        del sys.modules[name]
    # A None entry makes any import of the package raise ImportError.
    sys.modules["qwenpaw_ext"] = None  # type: ignore[assignment]
    try:
        reloaded = importlib.reload(enterprise)
        assert reloaded.ENTERPRISE_AVAILABLE is False
        assert reloaded.is_database_enabled() is False
        assert reloaded.get_engine() is None
        assert reloaded.check_database_health() is None
        assert reloaded.initialize_schema() is None

        event = reloaded.record_audit_event(
            actor="",
            action="a.b",
            resource_type="tool",
            resource_id="t1",
            status="denied",
            detail={"k": 1},
        )
        assert event["actor"] == "anonymous"
        assert event["action"] == "a.b"
        assert event["resource_type"] == "tool"
        assert event["resource_id"] == "t1"
        assert event["status"] == "denied"
        assert event["detail"] == {"k": 1}
        assert event["id"]
        assert event["timestamp"] > 0
    finally:
        del sys.modules["qwenpaw_ext"]
        sys.modules.update(saved)
        importlib.reload(enterprise)
    assert enterprise.ENTERPRISE_AVAILABLE is True


def test_bridge_import_does_not_pull_sqlalchemy():
    """Importing the bridge must never require sqlalchemy."""
    if "sqlalchemy" in sys.modules:
        pytest.skip("sqlalchemy already imported elsewhere in this run")
    importlib.import_module("qwenpaw.app.enterprise")
    assert "sqlalchemy" not in sys.modules


def test_bridge_check_database_health_raises_when_db_unreachable(monkeypatch):
    """DB enabled but unreachable: the RuntimeError surfaces via the bridge."""
    pytest.importorskip("sqlalchemy")
    from qwenpaw_ext.nexora import db

    monkeypatch.setenv(db.DB_URL_ENV, "postgresql://user:pw@localhost:1/cj")

    class _FailingEngine:
        def connect(self):
            raise ConnectionError("connection refused")

    monkeypatch.setattr(db, "get_engine", lambda: _FailingEngine())

    with pytest.raises(RuntimeError, match="health check failed"):
        enterprise.check_database_health()


def test_bridge_get_engine_delegates_when_db_enabled(monkeypatch):
    """DB enabled: the bridge returns the extension's engine, not None."""
    from qwenpaw_ext.nexora import db

    monkeypatch.setenv(db.DB_URL_ENV, "postgresql://user:pw@localhost/cj")
    sentinel = object()
    monkeypatch.setattr(db, "get_engine", lambda: sentinel)

    assert enterprise.get_engine() is sentinel
