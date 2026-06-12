# -*- coding: utf-8 -*-
import pytest

from qwenpaw.discovery.segments.taxonomy import (
    CANONICAL_INTEGRATION_KINDS,
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
        statuses, key=lambda s: {"recomendado": 0, "validar": 1, "build": 2}[s]
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
