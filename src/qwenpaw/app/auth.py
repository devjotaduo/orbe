# -*- coding: utf-8 -*-
"""Authentication module: password hashing, JWT tokens, and FastAPI middleware.

Login is disabled by default and only enabled when the environment
variable ``QWENPAW_AUTH_ENABLED`` is set to a truthy value (``true``,
``1``, ``yes``).  Credentials are created through a web-based
registration flow rather than environment variables, so that agents
running inside the process cannot read plaintext passwords.

Multi-user design (ported from nexora-ai-platform, Apache-2.0): the
first registered account becomes an administrator.  Additional users
can be managed through the authenticated user-management API when the
``qwenpaw_ext.nexora`` enterprise extension is installed.  Legacy
single-user ``auth.json`` files are migrated in place.  If the admin
forgets their password, delete ``auth.json`` from ``SECRET_DIR`` and
restart the service to re-register.

Uses only Python stdlib (hashlib, hmac, secrets) to avoid adding new
dependencies.  The password is stored as a salted SHA-256 hash in
``auth.json`` under ``SECRET_DIR``.
"""

from __future__ import annotations

import copy
import hashlib
import hmac
import json
import logging
import os
import secrets
import time
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from . import enterprise
from ..constant import SECRET_DIR, EnvVarLoader
from ..security.secret_store import (
    AUTH_SECRET_FIELDS,
    decrypt_dict_fields,
    encrypt_dict_fields,
    is_encrypted,
)

logger = logging.getLogger(__name__)

AUTH_FILE = SECRET_DIR / "auth.json"

# Token validity: 7 days (default)
TOKEN_EXPIRY_SECONDS = 7 * 24 * 3600

# Maximum token validity: 100 years (for "permanent" tokens)
TOKEN_EXPIRY_MAX = 100 * 365 * 24 * 3600

# Paths that do NOT require authentication
_PUBLIC_PATHS: frozenset[str] = frozenset(
    {
        "/api/auth/login",
        "/api/auth/status",
        "/api/auth/register",
        "/api/version",
        "/api/settings/language",
        "/api/settings/upload-limit",
        "/api/frontend_plugin",
    },
)

# Prefixes that do NOT require authentication (static assets)
# /api/frontend_plugin/ is safe: only read-only GET handlers are registered
# under that prefix (list + static file serving).  All write operations
# remain under /api/plugins/ which requires authentication.
_PUBLIC_PREFIXES: tuple[str, ...] = (
    "/assets/",
    "/logo.png",
    "/qwenpaw-symbol.svg",
    "/api/frontend_plugin/",
)

# HTTP methods that mutate state (audited by the middleware)
_MUTATING_METHODS: frozenset[str] = frozenset(
    {"POST", "PUT", "PATCH", "DELETE"},
)

# Paths whose mutating requests are NOT audited by the middleware:
# /api/auth/* events are recorded by the auth router itself (auth.*)
# and the audit endpoints must not audit themselves.
_AUDIT_SKIP_PREFIXES: tuple[str, ...] = (
    "/api/auth/",
    "/api/nexora/audit",
)


# ---------------------------------------------------------------------------
# Helpers (reuse SECRET_DIR patterns from envs/store.py)
# ---------------------------------------------------------------------------


def _chmod_best_effort(path, mode: int) -> None:
    try:
        os.chmod(path, mode)
    except OSError:
        pass


def _prepare_secret_parent(path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _chmod_best_effort(path.parent, 0o700)


# ---------------------------------------------------------------------------
# Password hashing (salted SHA-256, no external deps)
# ---------------------------------------------------------------------------


def _hash_password(
    password: str,
    salt: Optional[str] = None,
) -> tuple[str, str]:
    """Hash *password* with *salt*.  Returns ``(hash_hex, salt_hex)``."""
    if salt is None:
        salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return h, salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verify *password* against a stored hash."""
    h, _ = _hash_password(password, salt)
    return hmac.compare_digest(h, stored_hash)


# ---------------------------------------------------------------------------
# Token generation / verification (HMAC-SHA256, no PyJWT needed)
# ---------------------------------------------------------------------------


def _get_jwt_secret() -> str:
    """Return the signing secret, creating one if absent."""
    data = _load_auth_data()
    secret = data.get("jwt_secret", "")
    if not secret:
        secret = secrets.token_hex(32)
        data["jwt_secret"] = secret
        _save_auth_data(data)
    return secret


def create_token(username: str, expiry_seconds: Optional[int] = None) -> str:
    """Create an HMAC-signed token: ``base64(payload).signature``.

    Args:
        username: The username to encode in the token.
        expiry_seconds: Custom expiry time in seconds.
            Use -1 or 0 for permanent tokens.
            Defaults to TOKEN_EXPIRY_SECONDS (7 days).
    """
    import base64

    if expiry_seconds is None:
        expiry_seconds = TOKEN_EXPIRY_SECONDS
    elif expiry_seconds <= 0:
        # Permanent token: 100 years
        expiry_seconds = TOKEN_EXPIRY_MAX
    else:
        # Cap at maximum allowed expiry
        expiry_seconds = min(expiry_seconds, TOKEN_EXPIRY_MAX)

    secret = _get_jwt_secret()
    # Generate unique token ID (jti) for revocation support
    token_id = secrets.token_hex(16)
    payload = json.dumps(
        {
            "sub": username,
            "exp": int(time.time()) + expiry_seconds,
            "iat": int(time.time()),
            "jti": token_id,  # JWT ID for individual revocation
            "roles": _roles_for_user(username),
        },
    )
    payload_b64 = base64.urlsafe_b64encode(payload.encode()).decode()
    sig = hmac.new(
        secret.encode(),
        payload_b64.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload_b64}.{sig}"


def verify_token_payload(  # pylint: disable=too-many-return-statements
    token: str,
) -> Optional[dict]:
    """Verify *token*, return its payload dict if valid, ``None`` otherwise.

    Checks signature, expiry, the revocation list, and that the subject
    is still a registered, active user.
    """
    import base64

    try:
        parts = token.split(".", 1)
        if len(parts) != 2:
            return None
        payload_b64, sig = parts
        secret = _get_jwt_secret()
        expected_sig = hmac.new(
            secret.encode(),
            payload_b64.encode(),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        if payload.get("exp", 0) < time.time():
            return None

        # Check if token is revoked
        jti = payload.get("jti")
        if jti and _is_token_revoked(jti):
            return None

        username = payload.get("sub")
        if not username:
            return None
        data = _load_normalized_auth_data()
        _, user = _find_user(data, username)
        if not user or user.get("status") != "active":
            return None
        return payload
    except (json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
        logger.debug("Token verification failed: %s", exc)
        return None


def verify_token(token: str) -> Optional[str]:
    """Verify *token*, return username if valid, ``None`` otherwise.

    Also checks if the token has been revoked (appears in the revocation list).
    """
    payload = verify_token_payload(token)
    return payload.get("sub") if payload else None


# ---------------------------------------------------------------------------
# Auth data persistence (auth.json in SECRET_DIR)
# ---------------------------------------------------------------------------


def _load_auth_data(allow_rewrite: bool = True) -> dict:
    """Load ``auth.json`` from ``SECRET_DIR``.

    Returns the parsed dict, or a sentinel with ``_auth_load_error``
    set to ``True`` when the file exists but cannot be read/parsed so
    that callers can fail closed instead of silently bypassing auth.

    Encrypted fields (``jwt_secret``) are transparently decrypted.
    Legacy plaintext values trigger an automatic re-encryption unless
    *allow_rewrite* is ``False`` (used by ``_save_auth_data`` to avoid
    re-entering itself while merging file-backed fields).
    """
    if AUTH_FILE.is_file():
        try:
            with open(AUTH_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)

            needs_rewrite = any(
                isinstance(data.get(field), str)
                and data.get(field)
                and not is_encrypted(data[field])
                for field in AUTH_SECRET_FIELDS
            )
            data = decrypt_dict_fields(data, AUTH_SECRET_FIELDS)
            if needs_rewrite and allow_rewrite:
                try:
                    _save_auth_data(data)
                except Exception as enc_err:
                    logger.debug(
                        "Deferred plaintext→encrypted migration for"
                        " auth.json: %s",
                        enc_err,
                    )
            return data
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to load auth file %s: %s", AUTH_FILE, exc)
            return {"_auth_load_error": True}
    return {}


def _save_auth_file(data: dict) -> None:
    """Save ``auth.json`` to ``SECRET_DIR`` with restrictive permissions.

    Sensitive fields (``jwt_secret``) are encrypted before writing.
    """
    _prepare_secret_parent(AUTH_FILE)
    encrypted_data = encrypt_dict_fields(data, AUTH_SECRET_FIELDS)
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(encrypted_data, f, indent=2, ensure_ascii=False)
    _chmod_best_effort(AUTH_FILE, 0o600)


_FILE_BACKED_KEYS: frozenset[str] = frozenset(AUTH_SECRET_FIELDS) | {
    "revoked_tokens",
    "revoked_tokens_meta",
}


def _has_identity_payload(data: dict) -> bool:
    return "users" in data or "roles" in data


def _has_file_secret_payload(data: dict) -> bool:
    return any(key in data for key in _FILE_BACKED_KEYS)


def _save_auth_data(data: dict) -> None:
    """Persist auth data.

    When PostgreSQL is enabled, user/role identity data is stored in
    the DB.  JWT secrets and token revocation metadata remain
    file-backed for this phase so existing token handling stays
    compatible.
    """
    _invalidate_auth_data_cache()
    repo = enterprise.auth_repository()
    if repo is not None:
        if _has_identity_payload(data):
            repo.save_auth_data(data)
        if not _has_file_secret_payload(data):
            return

        file_data = _load_auth_data(allow_rewrite=False)
        if file_data.get("_auth_load_error"):
            file_data = {}
        for key in _FILE_BACKED_KEYS:
            if key in data:
                file_data[key] = data[key]
        _save_auth_file(file_data)
        return

    _save_auth_file(data)


# ---------------------------------------------------------------------------
# Multi-user helpers (ported from nexora-ai-platform, Apache-2.0)
# ---------------------------------------------------------------------------


def _now() -> int:
    return int(time.time())


def _public_user(user: dict) -> dict:
    return {
        "id": user.get("id", ""),
        "username": user.get("username", ""),
        "roles": list(user.get("roles") or []),
        "status": user.get("status", "active"),
        "created_at": user.get("created_at", 0),
        "updated_at": user.get("updated_at", 0),
    }


def _default_roles() -> dict[str, dict]:
    """Built-in roles from the enterprise extension (``{}`` without it)."""
    return enterprise.default_roles()


def _normalize_auth_data(data: dict) -> dict:
    """Migrate legacy single-user auth data to the multi-user schema."""
    if data.get("_auth_load_error"):
        return data

    if not isinstance(data.get("users"), list):
        legacy_user = data.get("user")
        if isinstance(legacy_user, dict) and legacy_user.get("username"):
            ts = _now()
            data["users"] = [
                {
                    "id": legacy_user.get("id") or secrets.token_hex(8),
                    "username": legacy_user.get("username", ""),
                    "password_hash": legacy_user.get("password_hash", ""),
                    "password_salt": legacy_user.get("password_salt", ""),
                    "roles": legacy_user.get("roles") or ["admin"],
                    "status": legacy_user.get("status") or "active",
                    "created_at": legacy_user.get("created_at") or ts,
                    "updated_at": legacy_user.get("updated_at") or ts,
                },
            ]
            _save_auth_data(data)
        else:
            data["users"] = []

    # Role normalisation only applies when the enterprise extension is
    # installed (otherwise there are no built-in role definitions).
    defaults = _default_roles()
    if not defaults:
        return data

    if not isinstance(data.get("roles"), dict):
        data["roles"] = defaults
        _save_auth_data(data)
        return data

    changed = False
    roles = data["roles"]
    for role_id, role in defaults.items():
        if role_id not in roles:
            roles[role_id] = role
            changed = True
            continue
        existing_permissions = list(
            roles[role_id].get("permissions") or [],
        )
        merged_permissions = list(
            dict.fromkeys(
                [*existing_permissions, *role.get("permissions", [])],
            ),
        )
        if merged_permissions != existing_permissions:
            roles[role_id]["permissions"] = merged_permissions
            changed = True
        if not roles[role_id].get("builtin"):
            roles[role_id]["builtin"] = True
            changed = True
    if changed:
        data["roles"] = roles
        _save_auth_data(data)
    return data


def _normalize_db_auth_data(data: dict) -> dict:
    """Ensure DB-backed auth data carries the built-in role definitions."""
    if data.get("_auth_load_error"):
        return data

    changed = False
    if not isinstance(data.get("users"), list):
        data["users"] = []
        changed = True

    defaults = _default_roles()
    roles = data.get("roles")
    if not isinstance(roles, dict):
        data["roles"] = defaults
        changed = True
    elif defaults:
        for role_id, role in defaults.items():
            if role_id not in roles:
                roles[role_id] = role
                changed = True
                continue
            existing_permissions = list(
                roles[role_id].get("permissions") or [],
            )
            merged_permissions = list(
                dict.fromkeys(
                    [*existing_permissions, *role.get("permissions", [])],
                ),
            )
            if merged_permissions != existing_permissions:
                roles[role_id]["permissions"] = merged_permissions
                changed = True
            if not roles[role_id].get("builtin"):
                roles[role_id]["builtin"] = True
                changed = True
        data["roles"] = roles

    if changed:
        repo = enterprise.auth_repository()
        if repo is not None:
            repo.save_auth_data(data)
    return data


# Cache for normalized auth data: the middleware permission check reads
# auth data on every authenticated request, which would otherwise cost a
# file read (or Postgres round-trips) per request.  File-backed data is
# keyed on the auth.json mtime (exact invalidation); DB-backed data uses
# a short TTL.  ``_save_auth_data`` invalidates the cache on every write.
_AUTH_DB_CACHE_TTL_SECONDS = 2.0
_auth_data_cache: tuple = (None, 0.0, None)  # (source_key, expires_at, data)


def _invalidate_auth_data_cache() -> None:
    global _auth_data_cache  # noqa: PLW0603
    _auth_data_cache = (None, 0.0, None)


def _load_normalized_auth_data() -> dict:
    """Load auth data in the multi-user schema (DB or auth.json).

    Returns a deep copy so callers can mutate the result freely without
    corrupting the cache.
    """
    global _auth_data_cache  # noqa: PLW0603
    repo = enterprise.auth_repository()
    if repo is not None:
        cached_key, expires_at, cached = _auth_data_cache
        if cached_key == "db" and time.time() < expires_at:
            return copy.deepcopy(cached)
        data = _normalize_db_auth_data(repo.load_auth_data())
        if not data.get("_auth_load_error"):
            _auth_data_cache = (
                "db",
                time.time() + _AUTH_DB_CACHE_TTL_SECONDS,
                copy.deepcopy(data),
            )
        return data

    try:
        mtime_ns = AUTH_FILE.stat().st_mtime_ns
    except OSError:
        mtime_ns = 0
    source_key = (str(AUTH_FILE), mtime_ns)
    cached_key, _, cached = _auth_data_cache
    if cached_key == source_key:
        return copy.deepcopy(cached)
    # _normalize_auth_data may persist a migration, changing the mtime;
    # the stale key then simply misses once on the next call.
    data = _normalize_auth_data(_load_auth_data())
    if not data.get("_auth_load_error"):
        _auth_data_cache = (source_key, 0.0, copy.deepcopy(data))
    return data


def _find_user(data: dict, username: str) -> tuple[int, dict | None]:
    for idx, user in enumerate(data.get("users", [])):
        if user.get("username") == username:
            return idx, user
    return -1, None


def _roles_for_user(username: str) -> list[str]:
    """Roles for *username*; legacy/unknown users default to admin."""
    data = _load_normalized_auth_data()
    _, user = _find_user(data, username)
    if user is None:
        return ["admin"]
    return list(user.get("roles") or [])


def get_user(username: str) -> dict | None:
    """Return the public view of *username*, or ``None`` if unknown."""
    data = _load_normalized_auth_data()
    _, user = _find_user(data, username)
    return _public_user(user) if user else None


# ---------------------------------------------------------------------------
# Token revocation (blacklist management)
# ---------------------------------------------------------------------------


def _is_token_revoked(jti: str) -> bool:
    """Check if a token ID (jti) is in the revocation list.

    Uses O(1) dict lookup via revoked_tokens_meta for performance.
    """
    data = _load_auth_data()
    meta = data.get("revoked_tokens_meta", {})
    return jti in meta


def _add_to_revocation_list(jti: str, exp: int) -> None:
    """Add a token ID to the revocation list with its expiry time.

    Uses revoked_tokens_meta dict for O(1) lookups. The revoked_tokens list
    is kept for backwards compatibility but not used for membership checks.
    """
    data = _load_auth_data()
    if data.get("_auth_load_error"):
        return

    # Initialize revoked_tokens_meta if not present
    if "revoked_tokens_meta" not in data:
        data["revoked_tokens_meta"] = {}

    # O(1) check using dict
    if jti not in data["revoked_tokens_meta"]:
        data["revoked_tokens_meta"][jti] = exp

        # Also add to list for backwards compatibility
        if "revoked_tokens" not in data:
            data["revoked_tokens"] = []
        data["revoked_tokens"].append(jti)

    _save_auth_data(data)


def _clean_expired_revocations() -> None:
    """
    Remove expired tokens from the revocation list to prevent unbounded growth.
    """
    data = _load_auth_data()
    if data.get("_auth_load_error"):
        return

    revoked = data.get("revoked_tokens", [])
    meta = data.get("revoked_tokens_meta", {})
    current_time = int(time.time())

    # Remove expired tokens
    cleaned_revoked = []
    cleaned_meta = {}

    for jti in revoked:
        exp = meta.get(jti, 0)
        if exp > current_time:
            cleaned_revoked.append(jti)
            cleaned_meta[jti] = exp

    if len(cleaned_revoked) < len(revoked):
        data["revoked_tokens"] = cleaned_revoked
        data["revoked_tokens_meta"] = cleaned_meta
        _save_auth_data(data)
        logger.info(
            "Cleaned %d expired tokens from revocation list",
            len(revoked) - len(cleaned_revoked),
        )


def is_auth_enabled() -> bool:
    """Check whether authentication is enabled via environment variable.

    Returns ``True`` when ``QWENPAW_AUTH_ENABLED`` is set to a truthy
    value (``true``, ``1``, ``yes``).  The presence of a registered
    user is checked separately by the middleware so that the first
    user can still reach the registration page.
    """
    env_flag = EnvVarLoader.get_str("QWENPAW_AUTH_ENABLED", "").strip().lower()
    return env_flag in ("true", "1", "yes")


def has_registered_users() -> bool:
    """Return ``True`` if a user has been registered."""
    data = _load_normalized_auth_data()
    return bool(data.get("users"))


# ---------------------------------------------------------------------------
# Registration (first user becomes administrator)
# ---------------------------------------------------------------------------


def register_user(
    username: str,
    password: str,
    expiry_seconds: Optional[int] = None,
) -> Optional[str]:
    """Register the first user account.

    Args:
        username: The username to register.
        password: The password to register.
        expiry_seconds: Custom token expiry time in seconds.

    Returns a token on success, ``None`` if a user already exists.
    """
    data = _load_normalized_auth_data()

    # The first registered user becomes platform administrator.
    if data.get("users"):
        return None

    pw_hash, salt = _hash_password(password)
    ts = _now()
    data["users"] = [
        {
            "id": secrets.token_hex(8),
            "username": username,
            "password_hash": pw_hash,
            "password_salt": salt,
            "roles": ["admin"],
            "status": "active",
            "created_at": ts,
            "updated_at": ts,
        },
    ]

    # Ensure jwt_secret exists
    if not data.get("jwt_secret"):
        data["jwt_secret"] = secrets.token_hex(32)

    _save_auth_data(data)
    logger.info("User '%s' registered", username)
    return create_token(username, expiry_seconds)


def auto_register_from_env() -> None:
    """Auto-register admin user from environment variables.

    Called once during application startup.  If ``QWENPAW_AUTH_ENABLED``
    is truthy and both ``QWENPAW_AUTH_USERNAME`` and ``QWENPAW_AUTH_PASSWORD``
    are set, the admin account is created automatically — useful for
    Docker, Kubernetes, server-panel, and other automated deployments
    where interactive web registration is not practical.

    Skips silently when:
    - authentication is not enabled
    - a user has already been registered
    - either env var is missing or empty
    """
    if not is_auth_enabled():
        return
    if has_registered_users():
        return

    username = EnvVarLoader.get_str("QWENPAW_AUTH_USERNAME", "").strip()
    password = EnvVarLoader.get_str("QWENPAW_AUTH_PASSWORD", "").strip()
    if not username or not password:
        return

    token = register_user(username, password)
    if token:
        logger.info(
            "Auto-registered user '%s' from environment variables",
            username,
        )


def update_credentials(
    current_password: str,
    new_username: Optional[str] = None,
    new_password: Optional[str] = None,
    expiry_seconds: Optional[int] = None,
    username: Optional[str] = None,
) -> Optional[str]:
    """Update a registered user's username and/or password.

    Requires the current password for verification.  Returns a new
    token on success (because the username may have changed), or
    ``None`` if verification fails or the new username is already
    taken by another user.

    Args:
        current_password: The current password for verification.
        new_username: The new username (optional).
        new_password: The new password (optional).
        expiry_seconds: Custom token expiry time in seconds.
        username: Which account to update; defaults to the first
            registered user (single-user compatibility).
    """
    data = _load_normalized_auth_data()
    user_idx = 0
    user = None
    if username:
        user_idx, user = _find_user(data, username)
    elif data.get("users"):
        user = data["users"][0]
    if not user:
        return None

    stored_hash = user.get("password_hash", "")
    stored_salt = user.get("password_salt", "")
    if not verify_password(current_password, stored_hash, stored_salt):
        return None

    if new_username and new_username.strip():
        candidate = new_username.strip()
        other_idx, other = _find_user(data, candidate)
        if other is not None and other_idx != user_idx:
            logger.warning(
                "Username '%s' is already taken; rename rejected",
                candidate,
            )
            return None
        user["username"] = candidate

    if new_password:
        pw_hash, salt = _hash_password(new_password)
        user["password_hash"] = pw_hash
        user["password_salt"] = salt
        # Rotate JWT secret to invalidate all existing sessions
        data["jwt_secret"] = secrets.token_hex(32)

    user["updated_at"] = _now()
    data["users"][user_idx] = user
    _save_auth_data(data)
    logger.info("Credentials updated for user '%s'", user["username"])
    return create_token(user["username"], expiry_seconds)


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


def authenticate(
    username: str,
    password: str,
    expiry_seconds: Optional[int] = None,
) -> Optional[str]:
    """Authenticate *username* / *password*.  Returns a token if valid.

    Args:
        username: The username to authenticate.
        password: The password to verify.
        expiry_seconds: Custom token expiry time in seconds.
    """
    data = _load_normalized_auth_data()
    _, user = _find_user(data, username)
    if not user:
        return None
    if user.get("status") != "active":
        return None
    stored_hash = user.get("password_hash", "")
    stored_salt = user.get("password_salt", "")
    if (
        stored_hash
        and stored_salt
        and verify_password(password, stored_hash, stored_salt)
    ):
        return create_token(username, expiry_seconds)
    return None


def revoke_token(token: str) -> bool:
    """Revoke a single token by adding its jti to the blacklist.

    Args:
        token: The token string to revoke.

    Returns True on success, False on failure.
    """
    import base64

    try:
        # Extract jti and exp from token
        parts = token.split(".", 1)
        if len(parts) != 2:
            return False

        payload_b64 = parts[0]
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        jti = payload.get("jti")
        exp = payload.get("exp", 0)

        if not jti:
            logger.warning("Token has no jti, cannot revoke individually")
            return False

        _add_to_revocation_list(jti, exp)
        logger.info("Token %s revoked", jti[:8])

        # Clean up expired tokens periodically
        _clean_expired_revocations()

        return True
    except Exception as exc:
        logger.error("Failed to revoke token: %s", exc)
        return False


def revoke_all_tokens() -> bool:
    """Revoke all existing tokens by rotating the JWT secret.

    This will invalidate all tokens that were issued before this call.
    Also clears the revocation list since all tokens are invalid anyway.
    Returns True on success, False on failure.
    """
    try:
        data = _load_auth_data()
        if data.get("_auth_load_error"):
            return False

        # Rotate JWT secret to invalidate all existing tokens
        data["jwt_secret"] = secrets.token_hex(32)

        # Clear revocation list since all tokens are now invalid
        data["revoked_tokens"] = []
        data["revoked_tokens_meta"] = {}

        _save_auth_data(data)
        logger.info("All tokens revoked (JWT secret rotated)")
        return True
    except Exception as exc:
        logger.error("Failed to revoke tokens: %s", exc)
        return False


# ---------------------------------------------------------------------------
# FastAPI middleware
# ---------------------------------------------------------------------------


def _resolve_client_ip(request: Request) -> str:
    """Return the real client IP, respecting reverse-proxy headers."""
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip", "")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else ""


# Cached config for hot-path auth checks (avoids disk read per request)
_auth_config_cache: tuple = (0, None)  # (mtime_ns, config)


def _get_config_cached():
    """Return config with mtime-based cache (stat is ~1us vs read ~1ms)."""
    global _auth_config_cache  # noqa: PLW0603
    from ..config import load_config
    from ..config.utils import get_config_path

    config_path = get_config_path()
    try:
        mtime_ns = config_path.stat().st_mtime_ns
    except OSError:
        mtime_ns = 0
    if mtime_ns != _auth_config_cache[0] or _auth_config_cache[1] is None:
        _auth_config_cache = (mtime_ns, load_config())
    return _auth_config_cache[1]


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware that checks Bearer token on protected routes."""

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        """Check Bearer token on protected API routes; skip public paths."""
        if self._should_skip_auth(request):
            return await call_next(request)

        token = self._extract_token(request)
        if not token:
            return Response(
                content=json.dumps({"detail": "Not authenticated"}),
                status_code=401,
                media_type="application/json",
            )

        payload = verify_token_payload(token)
        if payload is None:
            return Response(
                content=json.dumps(
                    {"detail": "Invalid or expired token"},
                ),
                status_code=401,
                media_type="application/json",
            )

        user = payload.get("sub", "")
        # request.state.roles mirrors the token's "roles" claim, so it can
        # lag behind storage until the token is reissued.  Permission
        # enforcement below always checks live data through the bridge.
        roles = payload.get("roles")
        if roles is None:  # tokens issued before the roles claim
            roles = _roles_for_user(user)
        request.state.user = user
        request.state.roles = list(roles)

        permission = enterprise.required_permission(
            request.url.path,
            request.method,
        )
        if permission and not enterprise.user_has_permission(
            user,
            permission,
        ):
            self._record_denied_audit(request, user, permission)
            return Response(
                content=json.dumps(
                    {
                        "detail": "Permission denied",
                        "permission": permission,
                    },
                ),
                status_code=403,
                media_type="application/json",
            )

        response = await call_next(request)
        self._record_request_audit(request, response, user, permission)
        return response

    @staticmethod
    def _should_skip_auth(request: Request) -> bool:
        """Return ``True`` when the request does not require auth."""
        if not is_auth_enabled() or not has_registered_users():
            return True

        path = request.url.path

        if request.method == "OPTIONS":
            return True

        if path in _PUBLIC_PATHS or any(
            path.startswith(p) for p in _PUBLIC_PREFIXES
        ):
            return True

        # Only protect /api/ routes
        if not path.startswith("/api/"):
            return True

        # A logged-in request must always pass through RBAC and the audit
        # trail, even when it comes from an allow_no_auth_hosts address
        # (ported from nexora-ai-platform).
        if AuthMiddleware._extract_token(request):
            return False

        # Check if client host is in allow_no_auth_hosts whitelist
        client_host = _resolve_client_ip(request)
        config = _get_config_cached()
        allowed_hosts = config.security.allow_no_auth_hosts
        return client_host in allowed_hosts

    @staticmethod
    def _extract_token(request: Request) -> Optional[str]:
        """Extract Bearer token from header or WebSocket query param."""
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        if "upgrade" in request.headers.get("connection", "").lower():
            return request.query_params.get("token")

        token = request.query_params.get("token")
        if token:
            return token
        return None

    @staticmethod
    def _record_request_audit(
        request: Request,
        response: Response,
        username: str,
        permission: Optional[str],
    ) -> None:
        """Audit mutating API requests (best-effort, never raises)."""
        path = request.url.path
        if request.method not in _MUTATING_METHODS:
            return
        if any(path.startswith(prefix) for prefix in _AUDIT_SKIP_PREFIXES):
            return

        try:
            query_str = str(request.url.query) if request.url.query else ""
            enterprise.record_audit_event(
                actor=username,
                action="api.mutate",
                resource_type="api",
                resource_id=path,
                status=(
                    "success" if response.status_code < 400 else "failure"
                ),
                detail={
                    "method": request.method,
                    "status_code": response.status_code,
                    "permission": permission or "",
                    **({"query": query_str} if query_str else {}),
                },
                request=request,
            )
        except Exception:
            logger.debug("Failed to record audit event", exc_info=True)

    @staticmethod
    def _record_denied_audit(
        request: Request,
        username: str,
        permission: Optional[str],
        detail: Optional[dict] = None,
    ) -> None:
        """Audit a permission-denied request (best-effort, never raises)."""
        try:
            enterprise.record_audit_event(
                actor=username,
                action="api.denied",
                resource_type="api",
                resource_id=request.url.path,
                status="denied",
                detail={
                    "method": request.method,
                    "permission": permission or "",
                    **(detail or {}),
                },
                request=request,
            )
        except Exception:
            logger.debug(
                "Failed to record denied audit event",
                exc_info=True,
            )
