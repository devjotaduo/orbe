# -*- coding: utf-8 -*-
"""Compat agentscope-runtime 1.1.6 <-> agentscope 2.0.

O ``agentscope-runtime`` 1.1.6 (pin do pyproject; aceita
``agentscope>=1.0.14``) ainda importa nomes que só existiam no agentscope
1.x. No 2.0:

- ``agentscope.message.ToolUseBlock``  -> renomeado para ``ToolCallBlock``;
- ``ImageBlock``/``AudioBlock``/``VideoBlock`` -> removidos (mídia passa por
  ``URLSource``/``Base64Source``);
- ``agentscope.mcp._client_base`` (com ``MCPClientBase``) -> módulo removido
  (o 2.0 expõe ``MCPClient``).

Sem este shim, ``Runner.stream_query()`` (``framework_type="agentscope"``)
morre com ``ImportError`` no import lazy de
``agentscope_runtime.adapters.agentscope.{message,stream}`` — derrubando
toda execução do agente (chat, heartbeat, crons). Visto no CI como
``heartbeat_error: ImportError("cannot import name 'ToolUseBlock' ...")``.

O shim injeta apenas o que o adapter precisa para importar e operar:

- os TypedDicts de mídia precisam só das chaves ``{type, source}`` — o
  adapter os usa em ``matches_typed_dict_structure``, que compara
  ``__annotations__.keys()`` com as chaves do dict;
- ``MCPClientBase`` vira alias de ``MCPClient``; o único uso no adapter
  (``_convert_mcp_content_to_as_blocks``, helper privado do 1.x) está
  dentro de ``try/except`` com fallback para o output cru, então a
  ausência do helper degrada com segurança.
"""
from __future__ import annotations

import sys
import types
from typing import Literal, TypedDict, Union

_applied = False


class _ImageBlock(TypedDict):
    """Forma 1.x de ``ImageBlock`` (só as chaves importam ao adapter)."""

    type: Literal["image"]
    source: Union[dict, object]


class _AudioBlock(TypedDict):
    """Forma 1.x de ``AudioBlock``."""

    type: Literal["audio"]
    source: Union[dict, object]


class _VideoBlock(TypedDict):
    """Forma 1.x de ``VideoBlock``."""

    type: Literal["video"]
    source: Union[dict, object]


def ensure_agentscope_runtime_compat() -> None:
    """Garante (idempotente) os nomes 1.x que o runtime 1.1.6 importa."""
    global _applied  # pylint: disable=global-statement
    if _applied:
        return

    import agentscope.message as asmsg

    if not hasattr(asmsg, "ToolUseBlock"):
        asmsg.ToolUseBlock = asmsg.ToolCallBlock

    for name, cls in (
        ("ImageBlock", _ImageBlock),
        ("AudioBlock", _AudioBlock),
        ("VideoBlock", _VideoBlock),
    ):
        if not hasattr(asmsg, name):
            setattr(asmsg, name, cls)

    mod_name = "agentscope.mcp._client_base"
    if mod_name not in sys.modules:
        import agentscope.mcp as asmcp

        mod = types.ModuleType(mod_name)
        mod.MCPClientBase = asmcp.MCPClient
        sys.modules[mod_name] = mod
        asmcp._client_base = mod  # pylint: disable=protected-access

    _applied = True
