# -*- coding: utf-8 -*-
import json
from qwenpaw.agui.events import (
    RunStartedEvent,
    RunErrorEvent,
    TextMessageContentEvent,
    StateSnapshotEvent,
    CustomEvent,
)


def test_run_started_serializes_camelcase_with_type():
    ev = RunStartedEvent(thread_id="t1", run_id="r1")
    data = json.loads(ev.model_dump_json(by_alias=True, exclude_none=True))
    assert data == {"type": "RUN_STARTED", "threadId": "t1", "runId": "r1"}


def test_text_message_content_carries_delta():
    ev = TextMessageContentEvent(message_id="m1", delta="Olá")
    data = json.loads(ev.model_dump_json(by_alias=True, exclude_none=True))
    assert data == {
        "type": "TEXT_MESSAGE_CONTENT",
        "messageId": "m1",
        "delta": "Olá",
    }


def test_state_snapshot_holds_arbitrary_dict():
    ev = StateSnapshotEvent(snapshot={"company": {"segment": "ecommerce"}})
    data = json.loads(ev.model_dump_json(by_alias=True, exclude_none=True))
    assert data["type"] == "STATE_SNAPSHOT"
    assert data["snapshot"]["company"]["segment"] == "ecommerce"


def test_custom_event_wraps_named_payload():
    ev = CustomEvent(name="a2ui", value={"messageType": "createSurface"})
    data = json.loads(ev.model_dump_json(by_alias=True, exclude_none=True))
    assert data == {
        "type": "CUSTOM",
        "name": "a2ui",
        "value": {"messageType": "createSurface"},
    }


def test_run_error_omits_optional_code_when_absent():
    ev = RunErrorEvent(message="boom")
    data = json.loads(ev.model_dump_json(by_alias=True, exclude_none=True))
    assert data == {"type": "RUN_ERROR", "message": "boom"}
