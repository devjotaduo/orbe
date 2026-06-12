# -*- coding: utf-8 -*-
from qwenpaw.agui.emitter import sse, text_message_events
from qwenpaw.agui.events import RunStartedEvent, TextMessageContentEvent


def test_sse_wraps_event_as_event_stream_frame():
    frame = sse(RunStartedEvent(thread_id="t", run_id="r"))
    assert frame.startswith("data: ")
    assert frame.endswith("\n\n")
    assert '"type":"RUN_STARTED"' in frame.replace(" ", "")
    assert '"threadId":"t"' in frame.replace(" ", "")


def test_text_message_events_brackets_content_with_start_end():
    evs = text_message_events("m1", "oi")
    assert [e.type for e in evs] == [
        "TEXT_MESSAGE_START",
        "TEXT_MESSAGE_CONTENT",
        "TEXT_MESSAGE_END",
    ]
    content = [e for e in evs if isinstance(e, TextMessageContentEvent)][0]
    assert content.message_id == "m1"
    assert content.delta == "oi"
