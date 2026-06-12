# -*- coding: utf-8 -*-
"""Valida e persiste um blueprint editado pelo usuário (approve_team)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .state import TeamBlueprint
from .tools import _blueprint_to_markdown


def finalize_blueprint(data: dict[str, Any], out_dir: Path) -> TeamBlueprint:
    """Valida ``data`` contra TeamBlueprint e grava blueprint.json/.md.

    Levanta ``pydantic.ValidationError`` se inválido (nada é gravado).
    """
    bp = TeamBlueprint.model_validate(data)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "blueprint.json").write_text(
        bp.model_dump_json(indent=2),
        encoding="utf-8",
    )
    (out_dir / "blueprint.md").write_text(
        _blueprint_to_markdown(bp),
        encoding="utf-8",
    )
    return bp
