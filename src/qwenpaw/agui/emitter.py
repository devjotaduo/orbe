# -*- coding: utf-8 -*-
"""SSE serialization + event-sequence helpers for AG-UI."""
from __future__ import annotations

from .events import (
    BaseEvent,
    TextMessageContentEvent,
    TextMessageEndEvent,
    TextMessageStartEvent,
)


def sse(event: BaseEvent) -> str:
    """Serialize one AG-UI event as a text/event-stream frame."""
    body = event.model_dump_json(by_alias=True, exclude_none=True)
    return f"data: {body}\n\n"


def text_message_events(message_id: str, text: str) -> list[BaseEvent]:
    """The START/CONTENT/END triplet for a complete assistant message."""
    return [
        TextMessageStartEvent(message_id=message_id),
        TextMessageContentEvent(message_id=message_id, delta=text),
        TextMessageEndEvent(message_id=message_id),
    ]
