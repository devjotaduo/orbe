# -*- coding: utf-8 -*-
"""Taxonomia híbrida de segmento: trilhos curados (CNAE) + fallback p/ LLM."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, field_validator, model_validator

_DATA = Path(__file__).parent / "data" / "cnae_seed.json"

CANONICAL_INTEGRATION_KINDS: frozenset[str] = frozenset(
    {
        "whatsapp",
        "crm",
        "planilha",
        "agenda",
        "erp",
        "pagamento",
        "fiscal",
        "ecommerce",
        "helpdesk",
        "email",
        "delivery",
        "voz",
        "juridico",
        "lms",
        "pdv",
        "prontuario",
        "chat-interno",
        "analytics",
    },
)


class SegmentInfo(BaseModel):
    key: str
    label: str
    cnae: str = ""
    keywords: list[str] = []
    typical_areas: list[str] = []
    typical_processes: list[str] = []
    common_pains: list[str] = []
    common_integrations: list[str] = []


_CONNECTORS_DATA = Path(__file__).parent / "data" / "connectors_seed.json"

_STATUS_ORDER = {"recomendado": 0, "validar": 1, "build": 2}


class ConnectorInfo(BaseModel):
    id: str
    integration_kind: str
    name: str
    origin: Literal[
        "clawhub",
        "lobehub",
        "modelscope",
        "skills-sh",
        "skillsmp",
        "github",
        "build",
    ]
    slug_or_url: str = ""
    status: Literal["recomendado", "validar", "build"]
    notes: str = ""
    segments: list[str] = []

    @field_validator("integration_kind")
    @classmethod
    def _kind_is_canonical(cls, v: str) -> str:
        if v not in CANONICAL_INTEGRATION_KINDS:
            raise ValueError(
                f"integration_kind '{v}' fora do vocabulário canônico",
            )
        return v

    @model_validator(mode="after")
    def _build_entries_consistent(self) -> "ConnectorInfo":
        if self.status == "build" and (
            self.origin != "build" or self.slug_or_url
        ):
            raise ValueError(
                f"conector build '{self.id}' deve ter origin='build' "
                f"e slug_or_url vazio",
            )
        return self


@lru_cache(maxsize=1)
def load_connectors() -> tuple[ConnectorInfo, ...]:
    raw = json.loads(_CONNECTORS_DATA.read_text(encoding="utf-8"))
    conns = tuple(ConnectorInfo.model_validate(item) for item in raw)
    ids = [c.id for c in conns]
    if len(ids) != len(set(ids)):
        dupes = {i for i in ids if ids.count(i) > 1}
        raise ValueError(f"connectors_seed.json: ids duplicados: {dupes}")
    return conns


def lookup_connectors(
    kind: str,
    segment: str | None = None,
) -> tuple[ConnectorInfo, ...]:
    """Conectores curados de um tipo de integração, ordenados por status.

    Levanta ValueError quando `kind` não é canônico. Quando `segment` é
    informado, exclui conectores restritos a outros segmentos; quando é
    None/vazio, retorna todos do kind (inclusive os segmentados).
    """
    if kind not in CANONICAL_INTEGRATION_KINDS:
        raise ValueError(
            f"integration_kind desconhecido: '{kind}'. "
            f"Válidos: {', '.join(sorted(CANONICAL_INTEGRATION_KINDS))}",
        )
    result = [
        c
        for c in load_connectors()
        if c.integration_kind == kind
        and (not segment or not c.segments or segment in c.segments)
    ]
    result.sort(key=lambda c: _STATUS_ORDER[c.status])
    return tuple(result)


@lru_cache(maxsize=1)
def load_segments() -> tuple[SegmentInfo, ...]:
    raw = json.loads(_DATA.read_text(encoding="utf-8"))
    return tuple(SegmentInfo.model_validate(item) for item in raw)


def lookup_segment(query: str) -> SegmentInfo | None:
    """Casa o texto do empresário com um segmento da seed por palavra-chave.

    Retorna None quando nenhum trilho casa (cai no raciocínio livre do LLM).
    """
    q = (query or "").lower()
    best: SegmentInfo | None = None
    best_hits = 0
    for seg in load_segments():
        hits = sum(1 for kw in seg.keywords if kw.lower() in q)
        if hits > best_hits:
            best, best_hits = seg, hits
    return best if best_hits > 0 else None
