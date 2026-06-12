import json
from pathlib import Path

PLUGINS = Path("plugins/bundle")
TOOL_PLUGINS = Path("plugins/tool")

def test_cloudpaw_has_ptbr_description():
    p = json.loads((PLUGINS / "cloudpaw/plugin.json").read_text(encoding="utf-8"))
    assert "pt-BR" in p["description_i18n"], "cloudpaw/plugin.json sem pt-BR"

def test_qwenpaw_pet_has_ptbr_description():
    p = json.loads((PLUGINS / "qwenpaw-pet/plugin.json").read_text(encoding="utf-8"))
    assert "pt-BR" in p["description_i18n"], "qwenpaw-pet/plugin.json sem pt-BR"

def test_gpt_image2_has_ptbr_description():
    p = json.loads((TOOL_PLUGINS / "gpt-image2/plugin.json").read_text(encoding="utf-8"))
    assert "pt-BR" in p["description_i18n"], "gpt-image2/plugin.json sem pt-BR"

def test_qwen_image_has_ptbr_description():
    p = json.loads((TOOL_PLUGINS / "qwen-image/plugin.json").read_text(encoding="utf-8"))
    assert "pt-BR" in p["description_i18n"], "qwen-image/plugin.json sem pt-BR"

def test_wan27_has_ptbr_description():
    p = json.loads((TOOL_PLUGINS / "wan27/plugin.json").read_text(encoding="utf-8"))
    assert "pt-BR" in p["description_i18n"], "wan27/plugin.json sem pt-BR"

def test_qwenpaw_plugin_kit_has_ptbr_description():
    p = json.loads(
        (PLUGINS / "qwenpaw-plugin-kit/plugin.json").read_text(
            encoding="utf-8",
        ),
    )
    assert "pt-BR" in p["description_i18n"], "qwenpaw-plugin-kit/plugin.json sem pt-BR"
