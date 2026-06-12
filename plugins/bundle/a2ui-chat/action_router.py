# -*- coding: utf-8 -*-
"""Endpoint de acao do plugin a2ui-chat (action-back da Fase B).

Recebe o data-model editado de uma surface A2UI e o ecoa de volta. O
endpoint e autossuficiente: nao depende de estado do agente. O consumo
do data editado pelo agente (re-injetar no proximo turno) e uma camada
futura — aqui apenas validamos e devolvemos.
"""
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class A2uiAction(BaseModel):
    """Payload de uma acao disparada por uma surface A2UI editavel."""

    session_id: str
    action: str
    data: Dict[str, Any] = Field(default_factory=dict)


@router.post("/action")
async def a2ui_action(req: A2uiAction) -> Dict[str, Any]:
    """Valida a acao e ecoa o data-model editado.

    Args:
        req: ``session_id``, ``action`` e o ``data`` editado.

    Returns:
        ``{"ok": True, "action": ..., "data": ...}`` ecoando o data.

    Raises:
        HTTPException: 400 quando ``action`` esta vazio.
    """
    if not req.action:
        raise HTTPException(status_code=400, detail="action vazio")
    return {"ok": True, "action": req.action, "data": req.data}
