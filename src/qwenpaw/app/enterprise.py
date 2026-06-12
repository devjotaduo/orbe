# -*- coding: utf-8 -*-
"""Bridge between QwenPaw core and the optional Nexora enterprise layer.

This module is the ONLY seam between ``qwenpaw`` core code and the
``qwenpaw_ext.nexora`` extension (ported from nexora-ai-platform,
Apache-2.0).  Core routers/middleware must import these helpers instead of
importing ``qwenpaw_ext`` directly, so the app keeps working when the
extension (or its ``[enterprise]`` dependencies) is not installed and when
``NEXORA_DB_URL`` is not configured.

When the extension cannot be imported every helper degrades to a no-op with
the same signature.
"""

from __future__ import annotations

import secrets
import time
from typing import Any, Optional

try:
    from qwenpaw_ext.nexora import audit as _audit
    from qwenpaw_ext.nexora import db as _db
    from qwenpaw_ext.nexora import rbac as _rbac

    ENTERPRISE_AVAILABLE = True
except ImportError:  # extension not installed
    _audit = None  # type: ignore[assignment]
    _db = None  # type: ignore[assignment]
    _rbac = None  # type: ignore[assignment]
    ENTERPRISE_AVAILABLE = False


def is_database_enabled() -> bool:
    """True when the enterprise PostgreSQL storage should be used."""
    if not ENTERPRISE_AVAILABLE:
        return False
    return _db.is_database_enabled()


def get_engine() -> Optional[Any]:
    """Return the cached SQLAlchemy engine, or None when DB is disabled.

    Unlike ``qwenpaw_ext.nexora.db.get_engine`` this never raises when the
    database is not configured; core callers can rely on ``None``.
    """
    if not ENTERPRISE_AVAILABLE or not _db.is_database_enabled():
        return None
    return _db.get_engine()


def initialize_schema() -> None:
    """Create enterprise tables if needed; no-op without the extension."""
    if not ENTERPRISE_AVAILABLE:
        return
    _db.initialize_schema()


def check_database_health() -> None:
    """Verify PostgreSQL is reachable; no-op without the extension.

    Raises RuntimeError only when the extension is installed, the database
    is enabled, and the health check fails.
    """
    if not ENTERPRISE_AVAILABLE:
        return
    _db.check_database_health()


def get_rbac() -> Optional[Any]:
    """Return the RBAC module, or None when the extension is missing.

    Used by the user/role management endpoints; callers must answer
    501 (not implemented) when this returns ``None``.
    """
    return _rbac if ENTERPRISE_AVAILABLE else None


def default_roles() -> dict:
    """Built-in role definitions, or ``{}`` without the extension."""
    if not ENTERPRISE_AVAILABLE:
        return {}
    return _rbac.default_roles()


def required_permission(path: str, method: str) -> Optional[str]:
    """Permission required for *method* + *path*, or None for no check."""
    if not ENTERPRISE_AVAILABLE:
        return None
    return _rbac.required_permission(path, method)


def user_has_permission(username: str, permission: str) -> bool:
    """Check RBAC permission for *username*.

    Without the extension this returns ``True``, which is coherent:
    ``required_permission`` returns ``None`` in that case so the
    middleware never reaches this check.
    """
    if not ENTERPRISE_AVAILABLE:
        return True
    return _rbac.user_has_permission(username, permission)


def auth_repository() -> Optional[Any]:
    """PostgreSQL auth repository module when DB storage is enabled.

    Returns ``None`` when the extension is missing or ``NEXORA_DB_URL``
    is not configured.  The import is lazy because the repository module
    imports sqlalchemy at module level.
    """
    if not is_database_enabled():
        return None
    from qwenpaw_ext.nexora.repositories import auth_postgres

    return auth_postgres


def record_audit_event(
    *,
    actor: str,
    action: str,
    resource_type: str = "",
    resource_id: str = "",
    status: str = "success",
    detail: Optional[dict] = None,
    request: Any = None,
) -> dict:
    """Record one audit event; same signature as the real implementation.

    Without the extension the event dict is returned but not persisted.
    """
    if not ENTERPRISE_AVAILABLE:
        return {
            "id": secrets.token_hex(12),
            "timestamp": int(time.time()),
            "actor": actor or "anonymous",
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "status": status,
            "ip": "",
            "user_agent": "",
            "detail": detail or {},
        }
    return _audit.record_audit_event(
        actor=actor,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        status=status,
        detail=detail,
        request=request,
    )
