# -*- coding: utf-8 -*-
from qwenpaw.discovery.segments.taxonomy import load_segments, lookup_segment


def test_seed_loads_and_has_ecommerce():
    segs = load_segments()
    assert any(s.key == "ecommerce" for s in segs)
    eco = next(s for s in segs if s.key == "ecommerce")
    assert eco.typical_areas
    assert eco.common_integrations


def test_lookup_matches_known_segment_by_keyword():
    info = lookup_segment("tenho uma loja virtual de roupas")
    assert info is not None
    assert info.key == "ecommerce"


def test_lookup_unknown_returns_none():
    assert lookup_segment("mineração de asteroides") is None
