# -*- coding: utf-8 -*-
"""Tests for qwenpaw_ext.nexora.rbac (no real PostgreSQL required).

Pure helpers (required_permission table, expand_permissions,
default_roles) plus the storage-coupled user/role management functions,
which exercise the qwenpaw.app.auth multi-user helpers added in
enterprise phase 2 (auth.json isolated under tmp_path).
"""

# pylint: disable=protected-access,redefined-outer-name,unused-argument

import pytest

from qwenpaw_ext.nexora import rbac


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def test_default_roles_structure():
    roles = rbac.default_roles()
    assert set(roles) == {"admin", "operator"}
    for role in roles.values():
        assert role["builtin"] is True
    assert set(roles["admin"]["permissions"]) == set(rbac.DEFAULT_PERMISSIONS)
    assert "users.manage" not in roles["operator"]["permissions"]
    assert "agents.use" in roles["operator"]["permissions"]


def test_list_permissions_matches_defaults():
    assert rbac.list_permissions() == list(rbac.DEFAULT_PERMISSIONS)


@pytest.mark.parametrize(
    "method,path,expected",
    [
        # users/roles management: MUTATE -> users.manage, read -> users.view
        ("POST", "/api/auth/users", "users.manage"),
        ("DELETE", "/api/auth/users/alice", "users.manage"),
        ("PUT", "/api/auth/roles/operator", "users.manage"),
        ("GET", "/api/auth/users", "users.view"),
        ("GET", "/api/auth/roles", "users.view"),
        ("GET", "/api/auth/permissions", "users.view"),
        # unmapped auth endpoints stay permission-free
        ("GET", "/api/auth/verify", None),
        ("POST", "/api/auth/login", None),
        # models: local-models always, /api/models only on mutation
        ("GET", "/api/local-models/status", "models.manage"),
        ("POST", "/api/models", "models.manage"),
        ("GET", "/api/models", None),
        # tools / mcp
        ("GET", "/api/mcp", "mcp.manage"),
        ("GET", "/api/tools", "tools.manage"),
        # governance: MUTATE row wins over the read row
        ("POST", "/api/nexora/governance/policies", "governance.manage"),
        ("GET", "/api/nexora/governance/policies", "governance.view"),
        ("GET", "/api/nexora/approval-requests", "approval.manage"),
        ("GET", "/api/nexora/audit", "audit.view"),
        # agents (non-scoped): MUTATE -> manage, read -> use
        ("POST", "/api/agents", "agents.manage"),
        ("GET", "/api/agents", "agents.use"),
        ("DELETE", "/api/workspace/files", "agents.manage"),
        ("GET", "/api/workspace", "agents.use"),
        ("GET", "/api/config", "agents.manage"),
        ("GET", "/api/envs", "agents.manage"),
        ("GET", "/api/approval", "approval.manage"),
        ("GET", "/api/plugins", "system.admin"),
        ("POST", "/api/backups", "system.admin"),
        ("GET", "/api/settings", "system.admin"),
        ("GET", "/api/plan", "system.admin"),
        ("GET", "/api/cron", "agents.manage"),
        ("GET", "/api/security", "system.admin"),
        ("GET", "/api/token-usage", "audit.view"),
        ("GET", "/api/agent-stats", "audit.view"),
        ("GET", "/api/console", "agents.use"),
        ("GET", "/api/chats", "agents.use"),
        ("POST", "/api/messages", "agents.use"),
        ("GET", "/api/files/foo.txt", "agents.use"),
        ("GET", "/api/skills", "agents.use"),
        # unmapped paths -> no permission check
        ("GET", "/api/unknown", None),
        ("POST", "/api/unknown", None),
        ("GET", "/api/version", None),
    ],
)
def test_required_permission_table(method, path, expected):
    assert rbac.required_permission(path, method) == expected


def test_required_permission_normalizes_method_case():
    assert rbac.required_permission("/api/agents", "post") == "agents.manage"
    assert rbac.required_permission("/api/agents", "get") == "agents.use"


@pytest.mark.parametrize(
    "method,path,expected",
    [
        # short path (no scope segment): mutate vs read
        ("GET", "/api/agents/a1", "agents.use"),
        ("POST", "/api/agents/a1", "agents.manage"),
        # chat-ish scopes
        ("GET", "/api/agents/a1/chats/c1", "agents.use"),
        ("GET", "/api/agents/a1/console", "agents.use"),
        ("GET", "/api/agents/a1/messages", "agents.use"),
        ("GET", "/api/agents/a1/files/f.txt", "agents.use"),
        ("GET", "/api/agents/a1/agent-status", "agents.use"),
        # capability scopes
        ("POST", "/api/agents/a1/mcp", "mcp.manage"),
        ("GET", "/api/agents/a1/skills", "tools.manage"),
        ("GET", "/api/agents/a1/tools", "tools.manage"),
        # observability scopes
        ("GET", "/api/agents/a1/token-usage", "audit.view"),
        ("GET", "/api/agents/a1/agent-stats", "audit.view"),
        # admin scopes
        ("GET", "/api/agents/a1/config", "system.admin"),
        ("PUT", "/api/agents/a1/settings", "system.admin"),
        ("GET", "/api/agents/a1/backups", "system.admin"),
        ("GET", "/api/agents/a1/envs", "system.admin"),
        ("GET", "/api/agents/a1/plugins", "system.admin"),
        # management scopes
        ("GET", "/api/agents/a1/cron", "agents.manage"),
        ("GET", "/api/agents/a1/plan", "agents.manage"),
        ("GET", "/api/agents/a1/workspace", "agents.manage"),
        # unknown scope falls back to agents.use
        ("DELETE", "/api/agents/a1/whatever", "agents.use"),
    ],
)
def test_agent_scoped_permission(method, path, expected):
    assert rbac._agent_scoped_permission(path, method) == expected
    # required_permission must honour the scoped result.
    assert rbac.required_permission(path, method) == expected


def test_agent_scoped_permission_ignores_other_paths():
    assert rbac._agent_scoped_permission("/api/chats", "GET") is None
    assert rbac._agent_scoped_permission("/api/agents", "POST") is None


def test_expand_permissions_implications():
    assert rbac.expand_permissions({"users.manage"}) == {
        "users.manage",
        "users.view",
    }
    expanded = rbac.expand_permissions(
        {"agents.manage", "tools.manage", "governance.manage"},
    )
    assert {"agents.use", "tools.execute", "governance.view"} <= expanded
    # narrow permissions do not expand upwards
    assert rbac.expand_permissions({"users.view"}) == {"users.view"}
    assert rbac.expand_permissions(set()) == set()


# ---------------------------------------------------------------------------
# Storage-coupled user management (auth.json isolated in tmp_path)
# ---------------------------------------------------------------------------


@pytest.fixture
def auth_env(monkeypatch, tmp_path):
    """Isolated qwenpaw.app.auth storage; returns the auth module."""
    from qwenpaw.app import auth

    monkeypatch.setattr(auth, "AUTH_FILE", tmp_path / "auth.json")
    monkeypatch.setattr(auth, "encrypt_dict_fields", lambda data, fields: data)
    monkeypatch.setattr(auth, "decrypt_dict_fields", lambda data, fields: data)
    monkeypatch.setattr(auth, "is_encrypted", lambda value: True)
    monkeypatch.delenv("NEXORA_DB_URL", raising=False)
    auth._invalidate_auth_data_cache()
    yield auth
    auth._invalidate_auth_data_cache()


def test_create_user_starts_without_roles(auth_env):
    auth_env.register_user("boss", "pw")

    user = rbac.create_user("plain", "pw2")
    assert user is not None
    assert user["roles"] == []
    assert user["status"] == "active"


def test_create_user_filters_unknown_roles(auth_env):
    auth_env.register_user("boss", "pw")
    user = rbac.create_user("op", "pw2", ["operator", "ghost-role"])
    assert user is not None
    assert user["roles"] == ["operator"]


def test_create_user_duplicate_username_rejected(auth_env):
    auth_env.register_user("boss", "pw")
    assert rbac.create_user("op", "pw2") is not None
    assert rbac.create_user("op", "pw3") is None


def test_user_has_permission_paths(auth_env):
    auth_env.register_user("boss", "pw")
    rbac.create_user("op", "pw2", ["operator"])
    rbac.create_user("plain", "pw3", [])

    # admin shortcut: everything
    assert rbac.user_has_permission("boss", "users.manage") is True
    # operator: capability yes, user management no
    assert rbac.user_has_permission("op", "agents.use") is True
    assert rbac.user_has_permission("op", "users.manage") is False
    # role-less user and unknown user: nothing
    assert rbac.user_has_permission("plain", "agents.use") is False
    assert rbac.user_has_permission("ghost", "agents.use") is False
    # disabled user: nothing, even with roles
    rbac.update_user("op", status="disabled")
    assert rbac.user_has_permission("op", "agents.use") is False


def test_delete_user_last_admin_blocked(auth_env):
    auth_env.register_user("boss", "pw")
    assert rbac.delete_user("boss") is False  # last active admin

    rbac.create_user("admin2", "pw2", ["admin"])
    assert rbac.delete_user("boss") is True  # another active admin exists
    assert rbac.delete_user("ghost") is False


def test_update_user_cannot_strip_last_admin_roles(auth_env):
    """Clearing the last active admin's roles must be rejected."""
    auth_env.register_user("boss", "pw")
    assert rbac.update_user("boss", roles=[]) is None
    assert rbac.user_has_permission("boss", "users.manage") is True


def test_update_user_cannot_disable_last_admin(auth_env):
    """Disabling the last active admin must be rejected."""
    auth_env.register_user("boss", "pw")
    assert rbac.update_user("boss", status="disabled") is None
    assert rbac.user_has_permission("boss", "users.manage") is True
