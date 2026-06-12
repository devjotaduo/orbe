# -*- coding: utf-8 -*-
import importlib.util
import json
import sys
from pathlib import Path

PLUGIN_DIR = Path("plugins/bundle/qwenpaw-plugin-kit")


def test_plugin_kit_manifest_declares_backend_frontend_and_ptbr():
    manifest = json.loads((PLUGIN_DIR / "plugin.json").read_text(encoding="utf-8"))

    assert manifest["id"] == "qwenpaw-plugin-kit"
    assert manifest["type"] == "general"
    assert manifest["entry"]["backend"] == "plugin.py"
    assert manifest["entry"]["frontend"] == "dist/index.js"
    assert "pt-BR" in manifest["description_i18n"]
    assert "tools" in manifest["meta"]


def test_plugin_kit_router_exposes_status_and_elements():
    sys.path.insert(0, str(PLUGIN_DIR.parent.resolve()))
    spec = importlib.util.spec_from_file_location(
        "qwenpaw_plugin_kit.plugin",
        PLUGIN_DIR / "plugin.py",
        submodule_search_locations=[str(PLUGIN_DIR)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["qwenpaw_plugin_kit.plugin"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)

    router = module.build_router()
    paths = {route.path for route in router.routes}

    assert "/status" in paths
    assert "/elements" in paths
    assert module.plugin.__class__.__name__ == "QwenPawPluginKit"


def test_plugin_kit_tool_defaults_to_portuguese():
    sys.path.insert(0, str(PLUGIN_DIR.resolve()))
    spec = importlib.util.spec_from_file_location(
        "plugin_kit_tools",
        PLUGIN_DIR / "tools.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    text = module.plugin_kit_describe_elements()

    assert "Plugins QwenPaw podem usar" in text
    assert "plugin.json" in text
