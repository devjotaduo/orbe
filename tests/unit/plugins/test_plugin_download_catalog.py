# -*- coding: utf-8 -*-
"""Tests for official plugin catalog normalization."""

from __future__ import annotations

from typing import Any

from qwenpaw.plugins import download_catalog


def test_catalog_filters_incompatible_plugins(monkeypatch) -> None:
    main_index = {
        "products": {
            "plugins": {
                "index_url": "/metadata/plugins/index.json",
            },
        },
    }
    plugins_index = {
        "updated_at": "2026-06-11T00:00:00Z",
        "files": {
            "compatible-1.0.0": {
                "id": "compatible-1.0.0",
                "plugin_id": "compatible",
                "name": "Compatible",
                "description": "Runs here",
                "version": "1.0.0",
                "min_version": "1.1.7",
                "platform": "tool",
                "url": "/files/plugins/tool/compatible/compatible.zip",
            },
            "future-1.0.0": {
                "id": "future-1.0.0",
                "plugin_id": "future",
                "name": "Future",
                "description": "Requires a newer host",
                "version": "1.0.0",
                "min_version": "9.0.0",
                "platform": "tool",
                "url": "/files/plugins/tool/future/future.zip",
            },
        },
    }

    def fake_fetch_json(url: str) -> dict[str, Any]:
        if url.endswith("/metadata/index.json"):
            return main_index
        if url.endswith("/metadata/plugins/index.json"):
            return plugins_index
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(download_catalog, "_fetch_json", fake_fetch_json)
    monkeypatch.setattr(download_catalog, "_installed_plugin_ids", lambda: {})

    payload = download_catalog.build_plugin_catalog()

    plugin_ids = [item["plugin_id"] for item in payload["plugins"]]
    assert plugin_ids == ["compatible"]
    assert payload["plugins"][0]["min_version"] == "1.1.7"
