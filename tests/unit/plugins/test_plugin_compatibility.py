# -*- coding: utf-8 -*-
"""Tests for plugin compatibility checks."""

import pytest

from qwenpaw.plugins.compatibility import (
    ensure_plugin_compatible,
    is_plugin_compatible,
)


def test_plugin_compatibility_accepts_supported_versions() -> None:
    assert is_plugin_compatible("1.1.7", "1.1.11.post2") is True
    assert is_plugin_compatible("1.1.11", "1.1.11.post2") is True
    assert is_plugin_compatible("", "1.1.11.post2") is True
    assert is_plugin_compatible(None, "1.1.11.post2") is True


def test_plugin_compatibility_rejects_future_versions() -> None:
    assert is_plugin_compatible("9.0.0", "1.1.11.post2") is False


def test_ensure_plugin_compatible_raises_clear_error() -> None:
    with pytest.raises(RuntimeError, match="requires QwenPaw >= 9.0.0"):
        ensure_plugin_compatible("future-plugin", "9.0.0", "1.1.11.post2")
