# -*- coding: utf-8 -*-
"""Tool ``render_ui``: valida uma surface A2UI e a devolve para o chat."""
from __future__ import annotations

import json
from typing import Any

from qwenpaw.a2ui.schema import (
    CreateSurface,
    DeleteSurface,
    UpdateComponents,
    UpdateDataModel,
)

_MSG = {
    "createSurface": CreateSurface,
    "updateComponents": UpdateComponents,
    "updateDataModel": UpdateDataModel,
    "deleteSurface": DeleteSurface,
}


def _validate(msgs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for m in msgs:
        mt = str(m.get("messageType"))
        model = _MSG.get(mt)
        if model is None:
            raise ValueError(f"messageType desconhecido: {mt!r}")
        out.append(model.model_validate(m).model_dump(by_alias=True))
    return out


async def render_ui(surface: Any) -> str:
    """Valida a surface A2UI (lista de mensagens ou única) e a devolve.

    O resultado (JSON string) é renderizado no chat pelo bundle do
    plugin via ``registerToolRender``. Surface inválida levanta erro
    (visível como falha da tool — nunca engolido).
    """
    msgs = surface if isinstance(surface, list) else [surface]
    validated = _validate(msgs)
    return json.dumps({"surface": validated}, ensure_ascii=False)
