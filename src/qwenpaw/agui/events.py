# -*- coding: utf-8 -*-
"""AG-UI event schemas (spec-compliant subset).

Mirrors the AG-UI protocol (https://docs.ag-ui.com/): each event has a
SCREAMING_SNAKE ``type`` discriminator and camelCase wire fields. Pure Pydantic,
no agentscope dependency — testable in isolation.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


def _camel(s: str) -> str:
    head, *tail = s.split("_")
    return head + "".join(w.capitalize() for w in tail)


class BaseEvent(BaseModel):
    """Common config: camelCase aliases on the wire, populate by python name."""

    model_config = ConfigDict(
        alias_generator=_camel,
        populate_by_name=True,
    )


class RunStartedEvent(BaseEvent):
    type: Literal["RUN_STARTED"] = "RUN_STARTED"
    thread_id: str
    run_id: str


class RunFinishedEvent(BaseEvent):
    type: Literal["RUN_FINISHED"] = "RUN_FINISHED"
    thread_id: str
    run_id: str


class RunErrorEvent(BaseEvent):
    type: Literal["RUN_ERROR"] = "RUN_ERROR"
    message: str
    code: str | None = None


class TextMessageStartEvent(BaseEvent):
    type: Literal["TEXT_MESSAGE_START"] = "TEXT_MESSAGE_START"
    message_id: str
    role: str = "assistant"


class TextMessageContentEvent(BaseEvent):
    type: Literal["TEXT_MESSAGE_CONTENT"] = "TEXT_MESSAGE_CONTENT"
    message_id: str
    delta: str


class TextMessageEndEvent(BaseEvent):
    type: Literal["TEXT_MESSAGE_END"] = "TEXT_MESSAGE_END"
    message_id: str


class StateSnapshotEvent(BaseEvent):
    type: Literal["STATE_SNAPSHOT"] = "STATE_SNAPSHOT"
    snapshot: dict[str, Any]


class StateDeltaEvent(BaseEvent):
    # delta is a JSON Patch (RFC 6902) list of ops, per AG-UI.
    type: Literal["STATE_DELTA"] = "STATE_DELTA"
    delta: list[dict[str, Any]]


class CustomEvent(BaseEvent):
    type: Literal["CUSTOM"] = "CUSTOM"
    name: str
    value: dict[str, Any] = Field(default_factory=dict)
