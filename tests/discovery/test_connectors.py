# -*- coding: utf-8 -*-
from qwenpaw.discovery.segments.taxonomy import (
    CANONICAL_INTEGRATION_KINDS,
    load_connectors,
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
