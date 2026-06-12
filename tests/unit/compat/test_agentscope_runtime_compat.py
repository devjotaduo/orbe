# -*- coding: utf-8 -*-
"""Shim agentscope-runtime 1.1.6 <-> agentscope 2.0.

Regressão do CI: ``Runner.stream_query`` (framework_type="agentscope")
morria com ``ImportError("cannot import name 'ToolUseBlock' from
'agentscope.message'")`` no import lazy dos adapters do runtime —
derrubando o heartbeat (e qualquer execução do agente). O shim injeta os
nomes 1.x que o adapter precisa; aqui pinamos o contrato.
"""
import sys

from qwenpaw.compat import ensure_agentscope_runtime_compat


def test_adapters_import_after_shim():
    """O critério real: os dois adapters do runtime importam sob 2.0."""
    ensure_agentscope_runtime_compat()
    from agentscope_runtime.adapters.agentscope.message import (
        message_to_agentscope_msg,
    )
    from agentscope_runtime.adapters.agentscope.stream import (
        adapt_agentscope_message_stream,
    )

    assert callable(message_to_agentscope_msg)
    assert callable(adapt_agentscope_message_stream)


def test_tool_use_block_aliases_tool_call_block():
    ensure_agentscope_runtime_compat()
    import agentscope.message as asmsg

    assert asmsg.ToolUseBlock is asmsg.ToolCallBlock


def test_media_blocks_have_1x_key_shape():
    """O adapter compara ``__annotations__.keys()`` com as chaves do dict
    (``matches_typed_dict_structure``); a forma 1.x é {type, source}."""
    ensure_agentscope_runtime_compat()
    import agentscope.message as asmsg

    for name in ("ImageBlock", "AudioBlock", "VideoBlock"):
        cls = getattr(asmsg, name)
        assert set(cls.__annotations__.keys()) == {"type", "source"}, name


def test_mcp_client_base_module_injected():
    ensure_agentscope_runtime_compat()
    assert "agentscope.mcp._client_base" in sys.modules
    from agentscope.mcp._client_base import MCPClientBase
    from agentscope.mcp import MCPClient

    assert MCPClientBase is MCPClient


def test_inbound_message_conversion_roundtrip():
    """Conversão de input runtime -> Msg 2.0 (o caminho do heartbeat)."""
    ensure_agentscope_runtime_compat()
    from agentscope_runtime.adapters.agentscope.message import (
        message_to_agentscope_msg,
    )
    from agentscope_runtime.engine.schemas.agent_schemas import Message

    m = Message.model_validate(
        {"role": "user", "content": [{"type": "text", "text": "oi"}]},
    )
    msgs = message_to_agentscope_msg([m])
    msg = msgs[0] if isinstance(msgs, list) else msgs
    assert msg.get_text_content() == "oi"


def test_idempotent():
    ensure_agentscope_runtime_compat()
    import agentscope.message as asmsg

    before = asmsg.ToolUseBlock
    ensure_agentscope_runtime_compat()
    assert asmsg.ToolUseBlock is before
