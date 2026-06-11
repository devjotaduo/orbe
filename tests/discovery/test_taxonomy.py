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


# ---------------------------------------------------------------------------
# Reviewer-flagged MISSING TESTS
# ---------------------------------------------------------------------------


def test_lookup_tie_break_returns_first_wins():
    """When two segments score equal keyword hits the algorithm does NOT update
    on equal scores (uses strict ``>``) so the first matching segment in seed
    iteration order wins.

    Query "meu varejo oferece serviços" hits exactly 1 keyword in both 'varejo'
    (keyword "varejo") and 'servicos' (keyword "serviços").  Because 'varejo'
    appears before 'servicos' in cnae_seed.json and the code only replaces on
    ``hits > best_hits``, 'varejo' wins.  This test documents that first-wins
    behaviour so any future reordering of the seed is caught immediately.
    """
    result = lookup_segment("meu varejo oferece serviços")
    assert result is not None
    assert result.key == "varejo", (
        "Tie-break must resolve to 'varejo' (first in seed) — "
        "if this fails, either the seed order or the strict-'>' tie-break "
        "logic changed."
    )


def test_lookup_substring_false_positive_is_documented():
    """The keyword matching uses a plain ``kw in query`` substring check.
    This means a keyword can match mid-word or as a suffix of a longer token.

    Example: the 'educacao' keyword "curso" is a substring of "percurso".
    A query like "gerencio o percurso de logística" contains no reference to
    education, yet the algorithm returns 'educacao' because "curso" appears
    inside "percurso".

    This test documents the *current* behaviour so that:
    - Developers are aware of the false-positive risk.
    - Any future word-boundary guard (e.g. ``re.search(r'\\bkw\\b', query)``)
      will be detected here because the result would flip to None.
    """
    # "percurso" embeds the educacao keyword "curso"
    result = lookup_segment("gerencio o percurso de logística")
    # Current behaviour: false-positive match on the 'educacao' segment
    assert result is not None, (
        "Expected a false-positive match on 'educacao' via substring 'curso' "
        "inside 'percurso'.  If this is now None a word-boundary guard was "
        "introduced — update this test to reflect the new behaviour."
    )
    assert result.key == "educacao", (
        f"Expected 'educacao' false-positive but got '{result.key}'. "
        "Update this test if the seed or matching logic changed."
    )
