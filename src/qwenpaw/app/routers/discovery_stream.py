# -*- coding: utf-8 -*-
"""SSE endpoint that drives a discovery interview over AG-UI + A2UI.

One POST advances the session by one turn and streams that turn's AG-UI events.
A2UI surfaces ride inside CUSTOM events (name="a2ui"). Sessions are held in
memory keyed by session_id (multi-tenant is a future layer).

Single-process / dev-only constraint: ``_sessions`` and ``_session_factory``
are process-global, so this router assumes one worker and no horizontal
scaling. The registry only evicts on the final blueprint turn, so an interview
abandoned mid-way leaks its session for the life of the process — there is no
TTL or size cap yet. Persistence, eviction, and multi-tenant isolation are
deferred to a future layer.
"""
from __future__ import annotations

import logging
import os
import re
import uuid
from pathlib import Path
from typing import Any, Callable

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from qwenpaw.agui.emitter import sse, text_message_events
from qwenpaw.agui.events import (
    CustomEvent,
    RunErrorEvent,
    RunFinishedEvent,
    RunStartedEvent,
    StateSnapshotEvent,
)
from qwenpaw.a2ui.builder import build_blueprint_surface
from qwenpaw.discovery.finalize import finalize_blueprint
from qwenpaw.discovery.scripted_session import ScriptedDiscoverySession
from qwenpaw.discovery.session import DiscoverySession

logger = logging.getLogger(__name__)
router = APIRouter()

# Injectable so tests / layer-1 can swap the real LLM session in.
_session_factory: Callable[[], DiscoverySession] = ScriptedDiscoverySession
_sessions: dict[str, DiscoverySession] = {}


def set_session_factory(factory: Callable[[], DiscoverySession]) -> None:
    global _session_factory
    _session_factory = factory


class DiscoveryTurnRequest(BaseModel):
    session_id: str
    message: str | None = None


def _get_or_create(session_id: str) -> DiscoverySession:
    if session_id not in _sessions:
        _sessions[session_id] = _session_factory()
    return _sessions[session_id]


@router.post("/discovery/stream")
async def discovery_stream(req: DiscoveryTurnRequest) -> StreamingResponse:
    session = _get_or_create(req.session_id)
    thread_id, run_id = req.session_id, uuid.uuid4().hex

    async def generate():
        yield sse(RunStartedEvent(thread_id=thread_id, run_id=run_id))
        try:
            result = await session.next_turn(req.message)
            yield sse(StateSnapshotEvent(snapshot=result.state))

            if result.question is not None:
                msg_id = uuid.uuid4().hex
                for ev in text_message_events(msg_id, result.question):
                    yield sse(ev)

            if result.blueprint is not None:
                for a2ui_msg in build_blueprint_surface(result.blueprint):
                    payload: dict[str, Any] = a2ui_msg.model_dump(
                        by_alias=True,
                    )
                    yield sse(CustomEvent(name="a2ui", value=payload))
                _sessions.pop(req.session_id, None)  # session complete

        except Exception as exc:  # surface, never swallow
            logger.exception("discovery turn failed")
            yield sse(RunErrorEvent(message=str(exc)))
        finally:
            yield sse(RunFinishedEvent(thread_id=thread_id, run_id=run_id))

    return StreamingResponse(generate(), media_type="text/event-stream")


class DiscoveryActionRequest(BaseModel):
    session_id: str
    action: str
    data: dict[str, Any] = Field(default_factory=dict)


# session_id keys a directory on disk — confine it to a single safe path
# segment so a crafted id (e.g. "../../x") cannot escape the out dir.
_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def _action_out_dir(session_id: str) -> Path:
    base = Path(
        os.environ.get("QWENPAW_DISCOVERY_OUT", "discovery_sessions"),
    )
    return base / session_id


@router.post("/discovery/action")
async def discovery_action(req: DiscoveryActionRequest) -> StreamingResponse:
    thread_id, run_id = req.session_id, uuid.uuid4().hex

    async def generate():
        yield sse(RunStartedEvent(thread_id=thread_id, run_id=run_id))
        try:
            if not _SESSION_ID_RE.fullmatch(req.session_id):
                raise ValueError(
                    f"session_id inválido: {req.session_id!r}",
                )
            if req.action != "approve_team":
                raise ValueError(f"ação desconhecida: {req.action!r}")
            bp = finalize_blueprint(
                req.data,
                _action_out_dir(req.session_id),
            )
            for ev in text_message_events(
                uuid.uuid4().hex,
                f"Time aprovado: {len(bp.proposed_team)} agente(s). "
                "Blueprint gravado.",
            ):
                yield sse(ev)
            _sessions.pop(req.session_id, None)
        except Exception as exc:  # surface, never swallow
            logger.exception("discovery action failed")
            yield sse(RunErrorEvent(message=str(exc)))
        finally:
            yield sse(RunFinishedEvent(thread_id=thread_id, run_id=run_id))

    return StreamingResponse(generate(), media_type="text/event-stream")
