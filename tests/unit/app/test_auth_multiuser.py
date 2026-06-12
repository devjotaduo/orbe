# -*- coding: utf-8 -*-
"""Tests for multi-user auth + RBAC middleware (enterprise phase 2).

Covers the Nexora port on top of the existing single-user auth:
- auth disabled -> middleware passes everything (no RBAC, no audit)
- legacy single-user auth.json migrated in place to users[] with admin
- admin creates operator; operator gets 403/200 per permission map
- JWT carries a roles claim; legacy tokens fall back to live roles
- token revocation (single + revoke-all) and file-backed persistence
  of the revocation list under DB (repository) mode
- audit middleware records api.mutate / api.denied and skips
  /api/auth/* and /api/nexora/audit prefixes
- allow_no_auth_hosts never bypasses RBAC when a token is present

No real PostgreSQL and no model/network calls: the auth file lives in
tmp_path, field encryption is stubbed out, and the enterprise bridge's
``record_audit_event`` / ``auth_repository`` are mocked where needed.
"""

# pylint: disable=protected-access,redefined-outer-name,unused-argument

import base64
import copy
import hashlib
import hmac
import json
import secrets
import time
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

from qwenpaw.app import auth, enterprise
from qwenpaw.app.auth import AuthMiddleware
from qwenpaw.app.routers.auth import router as auth_router


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def auth_env(monkeypatch, tmp_path):
    """Isolated auth storage + auth enabled; returns the auth.json path."""
    auth_file = tmp_path / "auth.json"
    monkeypatch.setattr(auth, "AUTH_FILE", auth_file)
    # Field encryption is orthogonal here; keep auth.json plain JSON.
    monkeypatch.setattr(auth, "encrypt_dict_fields", lambda data, fields: data)
    monkeypatch.setattr(auth, "decrypt_dict_fields", lambda data, fields: data)
    monkeypatch.setattr(auth, "is_encrypted", lambda value: True)
    monkeypatch.setenv("QWENPAW_AUTH_ENABLED", "true")
    monkeypatch.delenv("COPAW_AUTH_ENABLED", raising=False)
    monkeypatch.delenv("NEXORA_DB_URL", raising=False)
    # Deterministic config for the no-token whitelist path.
    monkeypatch.setattr(
        auth,
        "_get_config_cached",
        lambda: SimpleNamespace(
            security=SimpleNamespace(allow_no_auth_hosts=[]),
        ),
    )
    # Keep the extension's JSONL audit fallback away from the real dir.
    from qwenpaw_ext.nexora import audit as nexora_audit

    monkeypatch.setattr(
        nexora_audit,
        "AUDIT_FILE",
        tmp_path / "nexora_audit.jsonl",
    )
    auth._invalidate_auth_data_cache()
    yield auth_file
    auth._invalidate_auth_data_cache()


@pytest.fixture
def audit_mock(monkeypatch):
    """Mock the bridge's record_audit_event (shared by middleware+router)."""
    mock = MagicMock(return_value={})
    monkeypatch.setattr(enterprise, "record_audit_event", mock)
    return mock


def _build_app() -> FastAPI:
    app = FastAPI()
    app.include_router(auth_router, prefix="/api")

    @app.get("/api/chats")
    async def list_chats(request: Request):  # agents.use
        return {
            "user": getattr(request.state, "user", ""),
            "roles": list(getattr(request.state, "roles", []) or []),
        }

    @app.post("/api/agents")
    async def create_agent():  # agents.manage (MUTATE)
        return {"created": True}

    @app.post("/api/widgets")
    async def create_widget():  # unmapped path: no permission required
        return {"ok": True}

    @app.post("/api/widgets-fail")
    async def create_widget_fail():
        raise HTTPException(status_code=500, detail="boom")

    @app.post("/api/nexora/audit/export")
    async def audit_export():  # audit.view; middleware must NOT audit it
        return {"ok": True}

    app.add_middleware(AuthMiddleware)
    return app


@pytest.fixture
def client(auth_env):
    return TestClient(_build_app())


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _register_admin(client, username="boss", password="pw123") -> str:
    resp = client.post(
        "/api/auth/register",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["roles"] == ["admin"]
    return resp.json()["token"]


def _create_user(client, admin_token, username, password, roles):
    return client.post(
        "/api/auth/users",
        json={"username": username, "password": password, "roles": roles},
        headers=_auth_headers(admin_token),
    )


def _login(client, username, password) -> str:
    resp = client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["token"]


def _token_payload(token: str) -> dict:
    payload_b64 = token.split(".", 1)[0]
    return json.loads(base64.urlsafe_b64decode(payload_b64))


def _make_token(username: str, extra_claims: dict | None = None) -> str:
    """Sign a token like create_token but with a custom claim set."""
    secret = auth._get_jwt_secret()
    now = int(time.time())
    payload = {
        "sub": username,
        "exp": now + 3600,
        "iat": now,
        "jti": secrets.token_hex(16),
    }
    payload.update(extra_claims or {})
    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(payload).encode(),
    ).decode()
    sig = hmac.new(
        secret.encode(),
        payload_b64.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload_b64}.{sig}"


class FakeAuthRepo:
    """In-memory stand-in for repositories.auth_postgres."""

    def __init__(self, data: dict | None = None):
        self.data = data if data is not None else {"users": [], "roles": {}}
        self.load_calls = 0
        self.saved: list[dict] = []

    def load_auth_data(self) -> dict:
        self.load_calls += 1
        return copy.deepcopy(self.data)

    def save_auth_data(self, data: dict) -> None:
        self.saved.append(copy.deepcopy(data))
        self.data = {
            "users": copy.deepcopy(data.get("users", [])),
            "roles": copy.deepcopy(data.get("roles", {})),
        }


def _user_record(username: str, password: str, roles: list[str]) -> dict:
    pw_hash, salt = auth._hash_password(password)
    ts = auth._now()
    return {
        "id": secrets.token_hex(8),
        "username": username,
        "password_hash": pw_hash,
        "password_salt": salt,
        "roles": roles,
        "status": "active",
        "created_at": ts,
        "updated_at": ts,
    }


# ---------------------------------------------------------------------------
# (a) auth disabled -> zero checks, zero audit
# ---------------------------------------------------------------------------


def test_auth_disabled_middleware_passes_everything(
    monkeypatch,
    auth_env,
    audit_mock,
):
    monkeypatch.setenv("QWENPAW_AUTH_ENABLED", "false")
    perm_mock = MagicMock(return_value="system.admin")
    monkeypatch.setattr(enterprise, "required_permission", perm_mock)
    client = TestClient(_build_app())

    assert client.get("/api/chats").status_code == 200
    assert client.post("/api/agents").status_code == 200
    assert client.post("/api/widgets").status_code == 200
    status = client.get("/api/auth/status")
    assert status.status_code == 200
    assert status.json()["enabled"] is False

    perm_mock.assert_not_called()
    audit_mock.assert_not_called()


# ---------------------------------------------------------------------------
# (b) legacy single-user auth.json -> migrated, treated as admin
# ---------------------------------------------------------------------------


def test_legacy_single_user_migrated_to_admin(auth_env, client):
    pw_hash, salt = auth._hash_password("secret")
    auth_env.write_text(
        json.dumps(
            {
                "user": {
                    "username": "boss",
                    "password_hash": pw_hash,
                    "password_salt": salt,
                },
                "jwt_secret": "topsecret",
            },
        ),
        encoding="utf-8",
    )
    auth._invalidate_auth_data_cache()

    data = auth._load_normalized_auth_data()
    assert [u["username"] for u in data["users"]] == ["boss"]
    assert data["users"][0]["roles"] == ["admin"]
    # Migration is persisted in place.
    on_disk = json.loads(auth_env.read_text(encoding="utf-8"))
    assert on_disk["users"][0]["roles"] == ["admin"]
    assert on_disk["users"][0]["status"] == "active"

    # login / verify / logout flow stays intact.
    resp = client.post(
        "/api/auth/login",
        json={"username": "boss", "password": "secret"},
    )
    assert resp.status_code == 200
    assert resp.json()["roles"] == ["admin"]
    token = resp.json()["token"]

    verify = client.get("/api/auth/verify", headers=_auth_headers(token))
    assert verify.status_code == 200
    assert verify.json() == {
        "valid": True,
        "username": "boss",
        "roles": ["admin"],
    }

    # Implicit admin: no 403 on any mapped route.
    assert (
        client.get(
            "/api/chats",
            headers=_auth_headers(token),
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/agents",
            headers=_auth_headers(token),
        ).status_code
        == 200
    )
    assert (
        client.get(
            "/api/auth/users",
            headers=_auth_headers(token),
        ).status_code
        == 200
    )

    # Logout (revoke current token).
    out = client.post(
        "/api/auth/revoke-token",
        json={},
        headers=_auth_headers(token),
    )
    assert out.status_code == 200
    assert out.json()["revoked_current_token"] is True
    assert (
        client.get(
            "/api/auth/verify",
            headers=_auth_headers(token),
        ).status_code
        == 401
    )


# ---------------------------------------------------------------------------
# (c) admin creates operator; RBAC enforced per route
# ---------------------------------------------------------------------------


def test_admin_creates_operator_rbac_enforced(auth_env, client):
    admin_token = _register_admin(client)

    resp = _create_user(client, admin_token, "op", "oppw", ["operator"])
    assert resp.status_code == 200, resp.text
    assert resp.json()["roles"] == ["operator"]

    op_token = _login(client, "op", "oppw")

    # 403 on a users.manage route (middleware-level denial).
    denied = _create_user(client, op_token, "other", "pw", [])
    assert denied.status_code == 403
    assert denied.json()["permission"] == "users.manage"

    # operator role grants agents.manage, so POST /api/agents passes...
    assert (
        client.post(
            "/api/agents",
            headers=_auth_headers(op_token),
        ).status_code
        == 200
    )
    # ...and agents.use grants the chats route.
    assert (
        client.get(
            "/api/chats",
            headers=_auth_headers(op_token),
        ).status_code
        == 200
    )
    # but system.admin-mapped routes stay closed (no such route mounted,
    # the middleware rejects before routing).
    denied = client.get("/api/settings", headers=_auth_headers(op_token))
    assert denied.status_code == 403
    assert denied.json()["permission"] == "system.admin"


def test_new_user_without_roles_has_no_permissions(auth_env, client):
    admin_token = _register_admin(client)
    resp = _create_user(client, admin_token, "plain", "pw", [])
    assert resp.status_code == 200
    assert resp.json()["roles"] == []

    plain_token = _login(client, "plain", "pw")
    denied = client.get("/api/chats", headers=_auth_headers(plain_token))
    assert denied.status_code == 403
    assert denied.json()["permission"] == "agents.use"


def test_me_expands_implied_permissions(auth_env, client):
    admin_token = _register_admin(client)
    role = client.post(
        "/api/auth/roles",
        json={
            "id": "helpdesk",
            "name": "Helpdesk",
            "permissions": ["users.manage"],
        },
        headers=_auth_headers(admin_token),
    )
    assert role.status_code == 200, role.text
    assert (
        _create_user(
            client,
            admin_token,
            "hd",
            "pw",
            ["helpdesk"],
        ).status_code
        == 200
    )

    hd_token = _login(client, "hd", "pw")
    me = client.get("/api/auth/me", headers=_auth_headers(hd_token))
    assert me.status_code == 200
    body = me.json()
    assert body["roles"] == ["helpdesk"]
    # users.manage implies users.view (PERMISSION_IMPLICATIONS).
    assert "users.manage" in body["permissions"]
    assert "users.view" in body["permissions"]
    # and the implied permission is honoured by the middleware too.
    assert (
        client.get(
            "/api/auth/users",
            headers=_auth_headers(hd_token),
        ).status_code
        == 200
    )


def test_user_management_endpoint_edge_cases(auth_env, client):
    admin_token = _register_admin(client)
    headers = _auth_headers(admin_token)

    assert _create_user(client, admin_token, "op", "pw", []).status_code == 200
    # Duplicate username -> 400.
    dup = _create_user(client, admin_token, "op", "pw2", [])
    assert dup.status_code == 400
    # Delete self -> 400.
    self_del = client.delete("/api/auth/users/boss", headers=headers)
    assert self_del.status_code == 400
    assert "yourself" in self_del.json()["detail"]
    # Deleting an ordinary user works.
    assert (
        client.delete(
            "/api/auth/users/op",
            headers=headers,
        ).status_code
        == 200
    )


def test_user_endpoints_501_without_extension(monkeypatch, auth_env, client):
    admin_token = _register_admin(client)
    monkeypatch.setattr(enterprise, "get_rbac", lambda: None)

    assert (
        client.get(
            "/api/auth/users",
            headers=_auth_headers(admin_token),
        ).status_code
        == 501
    )
    assert (
        client.get(
            "/api/auth/me",
            headers=_auth_headers(admin_token),
        ).status_code
        == 501
    )


# ---------------------------------------------------------------------------
# (d) JWT roles claim + middleware behaviour
# ---------------------------------------------------------------------------


def test_jwt_payload_carries_roles_claim(auth_env, client):
    admin_token = _register_admin(client)
    assert _token_payload(admin_token)["roles"] == ["admin"]

    _create_user(client, admin_token, "op", "oppw", ["operator"])
    op_token = _login(client, "op", "oppw")
    assert _token_payload(op_token)["roles"] == ["operator"]


def test_middleware_sets_state_roles_from_token(auth_env, client):
    admin_token = _register_admin(client)
    _create_user(client, admin_token, "op", "oppw", ["operator"])
    op_token = _login(client, "op", "oppw")

    resp = client.get("/api/chats", headers=_auth_headers(op_token))
    assert resp.status_code == 200
    assert resp.json() == {"user": "op", "roles": ["operator"]}


def test_legacy_token_without_roles_claim_falls_back(auth_env, client):
    admin_token = _register_admin(client)
    _create_user(client, admin_token, "op", "oppw", ["operator"])

    legacy = _make_token("op")  # no "roles" claim (pre-RBAC token)
    resp = client.get("/api/chats", headers=_auth_headers(legacy))
    assert resp.status_code == 200
    # Fallback to _roles_for_user (live storage).
    assert resp.json()["roles"] == ["operator"]


def test_permission_enforcement_uses_live_data(auth_env, client):
    admin_token = _register_admin(client)
    _create_user(client, admin_token, "op", "oppw", ["operator"])
    op_token = _login(client, "op", "oppw")
    assert (
        client.get(
            "/api/chats",
            headers=_auth_headers(op_token),
        ).status_code
        == 200
    )

    # Admin strips the operator's roles; the old token still carries
    # the stale "operator" claim but enforcement must use live data.
    resp = client.put(
        "/api/auth/users/op",
        json={"roles": []},
        headers=_auth_headers(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["roles"] == []

    denied = client.get("/api/chats", headers=_auth_headers(op_token))
    assert denied.status_code == 403


# ---------------------------------------------------------------------------
# (e) revocation
# ---------------------------------------------------------------------------


def test_revoked_jti_rejected_by_middleware(auth_env, client):
    token = _register_admin(client)
    assert (
        client.get(
            "/api/chats",
            headers=_auth_headers(token),
        ).status_code
        == 200
    )

    out = client.post(
        "/api/auth/revoke-token",
        json={},
        headers=_auth_headers(token),
    )
    assert out.status_code == 200

    assert auth.verify_token_payload(token) is None
    denied = client.get("/api/chats", headers=_auth_headers(token))
    assert denied.status_code == 401


def test_revoke_all_tokens_invalidates_existing(auth_env, client):
    token = _register_admin(client)
    second = _login(client, "boss", "pw123")

    out = client.post(
        "/api/auth/revoke-all-tokens",
        headers=_auth_headers(token),
    )
    assert out.status_code == 200

    for stale in (token, second):
        assert auth.verify_token(stale) is None
        assert (
            client.get(
                "/api/auth/verify",
                headers=_auth_headers(stale),
            ).status_code
            == 401
        )


def test_revocation_list_stays_file_backed_in_db_mode(auth_env, monkeypatch):
    repo = FakeAuthRepo(
        {
            "users": [_user_record("boss", "pw123", ["admin"])],
            "roles": auth._default_roles(),
        },
    )
    monkeypatch.setattr(enterprise, "auth_repository", lambda: repo)
    auth._invalidate_auth_data_cache()

    token = auth.create_token("boss")
    assert auth.verify_token(token) == "boss"

    assert auth.revoke_token(token) is True
    assert auth.verify_token(token) is None

    jti = _token_payload(token)["jti"]
    on_disk = json.loads(auth_env.read_text(encoding="utf-8"))
    # jwt secret + revocation list are file-backed even in DB mode...
    assert jti in on_disk["revoked_tokens_meta"]
    assert jti in on_disk["revoked_tokens"]
    assert on_disk["jwt_secret"]
    # ...while identity (users/roles) never touches the file.
    assert "users" not in on_disk
    # Identity writes (if any) went to the repository, not the file.
    for saved in repo.saved:
        assert "users" in saved or "roles" in saved


def test_dual_storage_identity_goes_to_repository(auth_env, monkeypatch):
    repo = FakeAuthRepo()
    monkeypatch.setattr(enterprise, "auth_repository", lambda: repo)
    auth._invalidate_auth_data_cache()

    auth._save_auth_data(
        {
            "users": [_user_record("boss", "pw123", ["admin"])],
            "roles": auth._default_roles(),
            "jwt_secret": "s3cret",
            "revoked_tokens": ["j1"],
            "revoked_tokens_meta": {"j1": 9999999999},
        },
    )

    assert repo.saved, "identity payload must reach the repository"
    assert repo.data["users"][0]["username"] == "boss"

    on_disk = json.loads(auth_env.read_text(encoding="utf-8"))
    assert on_disk["jwt_secret"] == "s3cret"
    assert on_disk["revoked_tokens"] == ["j1"]
    assert "users" not in on_disk
    assert "roles" not in on_disk


def test_db_auth_data_cache_ttl_and_invalidation(auth_env, monkeypatch):
    repo = FakeAuthRepo(
        {
            "users": [_user_record("boss", "pw123", ["admin"])],
            "roles": auth._default_roles(),
        },
    )
    monkeypatch.setattr(enterprise, "auth_repository", lambda: repo)
    auth._invalidate_auth_data_cache()

    first = auth._load_normalized_auth_data()
    auth._load_normalized_auth_data()
    assert repo.load_calls == 1  # second hit served from cache

    # Returned data is a deep copy: mutating it must not poison the cache.
    first["users"].append({"username": "evil"})
    again = auth._load_normalized_auth_data()
    assert [u["username"] for u in again["users"]] == ["boss"]

    # Saving invalidates the cache.
    auth._save_auth_data(
        {"users": repo.data["users"], "roles": repo.data["roles"]},
    )
    auth._load_normalized_auth_data()
    assert repo.load_calls == 2

    # TTL expiry forces a reload too.
    key, _, cached = auth._auth_data_cache
    monkeypatch.setattr(
        auth,
        "_auth_data_cache",
        (key, time.time() - 1, cached),
    )
    auth._load_normalized_auth_data()
    assert repo.load_calls == 3


# ---------------------------------------------------------------------------
# (g) audit middleware
# ---------------------------------------------------------------------------


def test_audit_mutating_request_recorded(auth_env, client, audit_mock):
    token = _register_admin(client)
    audit_mock.reset_mock()

    resp = client.post("/api/widgets", headers=_auth_headers(token))
    assert resp.status_code == 200

    audit_mock.assert_called_once()
    kwargs = audit_mock.call_args.kwargs
    assert kwargs["actor"] == "boss"
    assert kwargs["action"] == "api.mutate"
    assert kwargs["resource_type"] == "api"
    assert kwargs["resource_id"] == "/api/widgets"
    assert kwargs["status"] == "success"
    assert kwargs["detail"]["method"] == "POST"
    assert kwargs["detail"]["status_code"] == 200


def test_audit_failed_mutation_recorded_as_failure(
    auth_env,
    client,
    audit_mock,
):
    token = _register_admin(client)
    audit_mock.reset_mock()

    resp = client.post("/api/widgets-fail", headers=_auth_headers(token))
    assert resp.status_code == 500

    audit_mock.assert_called_once()
    kwargs = audit_mock.call_args.kwargs
    assert kwargs["action"] == "api.mutate"
    assert kwargs["status"] == "failure"
    assert kwargs["detail"]["status_code"] == 500


def test_audit_get_request_not_recorded(auth_env, client, audit_mock):
    token = _register_admin(client)
    audit_mock.reset_mock()

    assert (
        client.get(
            "/api/chats",
            headers=_auth_headers(token),
        ).status_code
        == 200
    )
    audit_mock.assert_not_called()


def test_audit_skips_auth_and_audit_prefixes(auth_env, client, audit_mock):
    token = _register_admin(client)
    audit_mock.reset_mock()

    # /api/auth/* mutations are recorded by the router itself (auth.*),
    # never as api.mutate by the middleware.  add_user records nothing.
    resp = _create_user(client, token, "op", "pw", [])
    assert resp.status_code == 200
    audit_mock.assert_not_called()

    # /api/nexora/audit* must not audit itself.
    resp = client.post(
        "/api/nexora/audit/export",
        headers=_auth_headers(token),
    )
    assert resp.status_code == 200
    audit_mock.assert_not_called()


def test_audit_denied_request_recorded(auth_env, client, audit_mock):
    admin_token = _register_admin(client)
    _create_user(client, admin_token, "plain", "pw", [])
    plain_token = _login(client, "plain", "pw")
    audit_mock.reset_mock()

    denied = client.get("/api/chats", headers=_auth_headers(plain_token))
    assert denied.status_code == 403

    audit_mock.assert_called_once()
    kwargs = audit_mock.call_args.kwargs
    assert kwargs["actor"] == "plain"
    assert kwargs["action"] == "api.denied"
    assert kwargs["status"] == "denied"
    assert kwargs["resource_id"] == "/api/chats"
    assert kwargs["detail"]["permission"] == "agents.use"


# ---------------------------------------------------------------------------
# allow_no_auth_hosts: a token always goes through RBAC (bypass fix)
# ---------------------------------------------------------------------------


def test_allow_no_auth_hosts_skips_only_tokenless_requests(
    monkeypatch,
    auth_env,
    client,
    audit_mock,
):
    _register_admin(client)
    monkeypatch.setattr(
        auth,
        "_get_config_cached",
        lambda: SimpleNamespace(
            security=SimpleNamespace(allow_no_auth_hosts=["testclient"]),
        ),
    )

    # Without a token the whitelisted host is let through (legacy flow).
    assert client.get("/api/chats").status_code == 200

    # With an (invalid) token the request must NOT be skipped: 401.
    resp = client.get(
        "/api/chats",
        headers=_auth_headers("garbage.token"),
    )
    assert resp.status_code == 401
