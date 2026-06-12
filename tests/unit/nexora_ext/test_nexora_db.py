# -*- coding: utf-8 -*-
"""Tests for qwenpaw_ext.nexora.db (no real PostgreSQL required)."""

# pylint: disable=protected-access,unused-argument

import pytest

from qwenpaw_ext.nexora import db


@pytest.fixture(autouse=True)
def _clean_engine_cache():
    db.reset_engine_cache()
    yield
    db.reset_engine_cache()


def test_is_database_enabled_false_without_env(monkeypatch):
    monkeypatch.delenv(db.DB_URL_ENV, raising=False)
    assert db.is_database_enabled() is False


def test_is_database_enabled_false_with_blank_env(monkeypatch):
    monkeypatch.setenv(db.DB_URL_ENV, "   ")
    assert db.is_database_enabled() is False


def test_is_database_enabled_true_with_env(monkeypatch):
    monkeypatch.setenv(db.DB_URL_ENV, "postgresql://user:pw@localhost/cj")
    assert db.is_database_enabled() is True


def test_get_database_url_strips_whitespace(monkeypatch):
    monkeypatch.setenv(db.DB_URL_ENV, "  postgresql://h/db  ")
    assert db.get_database_url() == "postgresql://h/db"


def test_get_engine_raises_without_url(monkeypatch):
    # Raises BEFORE importing sqlalchemy, so no DB deps are needed.
    monkeypatch.delenv(db.DB_URL_ENV, raising=False)
    with pytest.raises(RuntimeError, match="not configured"):
        db.get_engine()


def test_get_engine_raises_for_non_postgres_url(monkeypatch):
    monkeypatch.setenv(db.DB_URL_ENV, "mysql://user:pw@localhost/cj")
    with pytest.raises(RuntimeError, match="PostgreSQL"):
        db.get_engine()


def test_reset_engine_cache_clears_schema_flag(monkeypatch):
    monkeypatch.setattr(db, "_schema_initialized", True)
    db.reset_engine_cache()
    assert db._schema_initialized is False


def test_initialize_schema_noop_without_db(monkeypatch):
    monkeypatch.delenv(db.DB_URL_ENV, raising=False)
    db.initialize_schema()  # must not raise nor require sqlalchemy
    assert db._schema_initialized is False


def test_check_database_health_noop_without_db(monkeypatch):
    monkeypatch.delenv(db.DB_URL_ENV, raising=False)
    db.check_database_health()  # must not raise


def test_cascade_delete_agent_disabled_without_db(monkeypatch):
    monkeypatch.delenv(db.DB_URL_ENV, raising=False)
    result = db.cascade_delete_agent("agent-1")
    assert result == {"deleted": False, "reason": "database not enabled"}
