# -*- coding: utf-8 -*-
"""Compatibility checks for plugin manifests."""

from __future__ import annotations

from packaging.version import InvalidVersion, Version

from ..__version__ import __version__


def current_app_version() -> str:
    """Return the current QwenPaw application version."""
    return __version__


def is_plugin_compatible(
    min_version: str | None,
    current_version: str | None = None,
) -> bool:
    """Return whether a plugin requiring ``min_version`` can run here."""
    required = str(min_version or "").strip()
    if not required:
        return True

    current = str(current_version or current_app_version()).strip()
    try:
        return Version(current) >= Version(required)
    except InvalidVersion:
        # Be conservative for non-PEP 440 versions: only exact matches pass.
        return current == required


def format_plugin_incompatibility(
    plugin_id: str,
    min_version: str | None,
    current_version: str | None = None,
) -> str:
    """Build a user-facing incompatibility diagnostic."""
    current = str(current_version or current_app_version()).strip()
    required = str(min_version or "").strip() or "(unspecified)"
    return (
        f"Plugin '{plugin_id}' requires QwenPaw >= {required}; "
        f"current version is {current}."
    )


def ensure_plugin_compatible(
    plugin_id: str,
    min_version: str | None,
    current_version: str | None = None,
) -> None:
    """Raise ``RuntimeError`` if the plugin cannot run on this app."""
    if is_plugin_compatible(min_version, current_version):
        return
    raise RuntimeError(
        format_plugin_incompatibility(
            plugin_id,
            min_version,
            current_version,
        ),
    )
