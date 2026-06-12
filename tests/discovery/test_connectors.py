# -*- coding: utf-8 -*-
import json

import pytest
from pydantic import ValidationError

from qwenpaw.discovery.segments import taxonomy
from qwenpaw.discovery.segments.taxonomy import (
    CANONICAL_INTEGRATION_KINDS,
    ConnectorInfo,
    load_connectors,
    lookup_connectors,
)


def test_connectors_seed_loads_and_is_nonempty():
    conns = load_connectors()
    assert len(conns) >= 25


def test_connector_ids_are_unique():
    conns = load_connectors()
    ids = [c.id for c in conns]
    assert len(ids) == len(set(ids))


def test_connector_kinds_are_canonical():
    for c in load_connectors():
        assert c.integration_kind in CANONICAL_INTEGRATION_KINDS, c.id


def test_build_entries_have_empty_slug_and_build_origin():
    builds = [c for c in load_connectors() if c.status == "build"]
    assert builds, "seed deve conter entradas status=build (lacunas BR)"
    for c in builds:
        assert c.slug_or_url == "", c.id
        assert c.origin == "build", c.id


def test_seed_covers_whatsapp_and_juridico():
    kinds = {c.integration_kind for c in load_connectors()}
    assert "whatsapp" in kinds
    assert "juridico" in kinds


def test_lookup_orders_by_status():
    conns = lookup_connectors("crm")
    statuses = [c.status for c in conns]
    assert statuses == sorted(
        statuses,
        key=lambda s: {"recomendado": 0, "validar": 1, "build": 2}[s],
    )
    assert conns[0].status == "recomendado"


def test_lookup_filters_by_segment():
    # brlaw-mcp é restrito a servicos_b2b
    juridico_b2b = lookup_connectors("juridico", segment="servicos_b2b")
    assert any(c.id == "brlaw-mcp" for c in juridico_b2b)
    juridico_eco = lookup_connectors("juridico", segment="ecommerce")
    assert not any(c.id == "brlaw-mcp" for c in juridico_eco)


def test_lookup_without_segment_includes_segmented():
    todos = lookup_connectors("delivery", segment=None)
    assert any(c.id == "ifood-clawhub" for c in todos)


def test_lookup_unknown_kind_raises():
    with pytest.raises(ValueError) as exc:
        lookup_connectors("blockchain")
    assert "whatsapp" in str(exc.value)  # lista os kinds válidos


def test_lookup_canonical_kind_without_connectors_returns_empty():
    assert lookup_connectors("pdv") == ()


# --- MISSING TESTS flagged by reviewer ---------------------------------------


def _valid_entry(**overrides):
    base = {
        "id": "x-test",
        "integration_kind": "crm",
        "name": "X Test",
        "origin": "clawhub",
        "slug_or_url": "x-test",
        "status": "recomendado",
        "notes": "",
        "segments": [],
    }
    base.update(overrides)
    return base


def test_connector_info_rejects_build_status_with_nonempty_slug():
    """status='build' exige slug_or_url vazio (validação no model)."""
    with pytest.raises(ValidationError) as exc:
        ConnectorInfo.model_validate(
            _valid_entry(
                origin="build",
                status="build",
                slug_or_url="meu-slug",
            ),
        )
    assert "build" in str(exc.value)


def test_connector_info_rejects_build_status_with_nonbuild_origin():
    """status='build' exige origin='build' (validação no model)."""
    with pytest.raises(ValidationError):
        ConnectorInfo.model_validate(
            _valid_entry(origin="clawhub", status="build", slug_or_url=""),
        )


def test_connector_info_accepts_consistent_build_entry():
    """Entrada build consistente (origin='build', slug vazio) passa."""
    c = ConnectorInfo.model_validate(
        _valid_entry(origin="build", status="build", slug_or_url=""),
    )
    assert c.status == "build" and c.origin == "build"


def test_connector_info_rejects_noncanonical_kind():
    """integration_kind fora do vocabulário canônico é rejeitado no model."""
    with pytest.raises(ValidationError) as exc:
        ConnectorInfo.model_validate(
            _valid_entry(integration_kind="blockchain"),
        )
    assert "blockchain" in str(exc.value)


def test_load_connectors_rejects_duplicate_ids(tmp_path, monkeypatch):
    """Seed com ids duplicados levanta ValueError listando os duplicados."""
    dup = _valid_entry(id="dup-id")
    seed = tmp_path / "connectors_seed.json"
    seed.write_text(json.dumps([dup, dup]), encoding="utf-8")
    monkeypatch.setattr(taxonomy, "_CONNECTORS_DATA", seed)
    taxonomy.load_connectors.cache_clear()
    try:
        with pytest.raises(ValueError) as exc:
            taxonomy.load_connectors()
        assert "dup-id" in str(exc.value)
    finally:
        # garante que os próximos testes recarreguem a seed real
        taxonomy.load_connectors.cache_clear()


def test_lookup_with_empty_string_segment_is_no_filter():
    """segment='' equivale a None: inclui conectores restritos a segmento."""
    com_vazio = lookup_connectors("juridico", segment="")
    com_none = lookup_connectors("juridico", segment=None)
    assert any(c.id == "brlaw-mcp" for c in com_vazio)
    assert [c.id for c in com_vazio] == [c.id for c in com_none]
