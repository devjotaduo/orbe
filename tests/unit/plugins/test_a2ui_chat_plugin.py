# -*- coding: utf-8 -*-
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PLUGIN_DIR = ROOT / "plugins" / "bundle" / "a2ui-chat"


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(
        name,
        PLUGIN_DIR / filename,
    )
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


a2ui_tool = _load("a2ui_tool", "a2ui_tool.py")


VALID = [
    {"messageType": "createSurface", "surfaceId": "s", "root": "root"},
    {
        "messageType": "updateComponents",
        "surfaceId": "s",
        "components": [
            {
                "id": "root",
                "type": "Column",
                "properties": {},
                "children": ["t"],
            },
            {
                "id": "t",
                "type": "Text",
                "properties": {"text": "oi"},
                "children": [],
            },
        ],
    },
]


@pytest.mark.asyncio
async def test_render_ui_echoes_validated_surface():
    out = await a2ui_tool.render_ui(VALID)
    data = json.loads(out)
    assert data["surface"][0]["messageType"] == "createSurface"
    assert data["surface"][1]["components"][1]["properties"]["text"] == "oi"


@pytest.mark.asyncio
async def test_render_ui_accepts_single_message():
    out = await a2ui_tool.render_ui(VALID[0])
    data = json.loads(out)
    assert len(data["surface"]) == 1


@pytest.mark.asyncio
async def test_render_ui_rejects_invalid_surface():
    bad = [{"messageType": "createSurface"}]  # falta surfaceId/root
    with pytest.raises(Exception):
        await a2ui_tool.render_ui(bad)


@pytest.mark.asyncio
async def test_render_ui_rejects_unknown_message_type():
    bad = [{"messageType": "nope"}]
    with pytest.raises(Exception):
        await a2ui_tool.render_ui(bad)


def test_plugin_registers_render_ui_tool():
    mod = _load("a2ui_plugin", "plugin.py")

    calls = []

    class FakeApi:
        def register_tool(self, **kw):
            calls.append(kw)

    mod.plugin.register(FakeApi())
    names = [c["tool_name"] for c in calls]
    assert "render_ui" in names
    rendered = [c for c in calls if c["tool_name"] == "render_ui"][0]
    assert callable(rendered["tool_func"])
    assert rendered["enabled"] is False
    assert rendered["icon"] == "🎨"


def test_manifest_valid():
    mf = json.loads(
        (PLUGIN_DIR / "plugin.json").read_text("utf-8"),
    )
    assert mf["id"] == "a2ui-chat"
    assert mf["type"] == "general"
    assert mf["entry"]["backend"] == "plugin.py"
    assert mf["entry"]["frontend"] == "ui/dist/index.js"
    tool = mf["meta"]["tools"][0]
    assert tool["name"] == "render_ui"
    cfg = {f["name"]: f for f in tool.get("config_fields", [])}
    assert "interactivity" in cfg
    assert cfg["interactivity"]["type"] == "select"
    assert cfg["interactivity"]["default"] == "read-only"


def _frontend_entry() -> Path:
    mf = json.loads((PLUGIN_DIR / "plugin.json").read_text("utf-8"))
    return PLUGIN_DIR / mf["entry"]["frontend"]


def test_frontend_bundle_built_on_disk():
    """The manifest's entry.frontend must exist (npm run build ran)."""
    entry = _frontend_entry()
    assert entry.is_file(), f"missing built bundle: {entry}"
    assert entry.stat().st_size > 0


def test_frontend_bundle_is_git_tracked():
    """entry.frontend must be committed, not gitignored.

    A clean checkout (e.g. CI / fresh clone) only ships tracked files.
    The global ``dist/`` ignore rule silently drops fresh bundle dist
    files, so the manifest's frontend entry would 404 unless force-added
    (cloudpaw's ui/dist/index.js is tracked the same way). Guards the
    gitignored-dist gap flagged in review.
    """
    entry = _frontend_entry()
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(entry)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"{entry} is not tracked by git "
        "(force-add it like plugins/bundle/cloudpaw/ui/dist/index.js)"
    )
