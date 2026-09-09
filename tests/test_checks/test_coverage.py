"""Recall for an open set: how many did we MISS, when nobody knows the total?

Every gate in this kit measures precision — is what I wrote supported. On a
"find all X" question that is the wrong axis entirely: the answer can be 100%
precise and still miss two thirds of the population, and no check here would
say so. The corpus named this hole twice independently, and the owner named it
as the shape of the work he actually does.

The honest instrument is capture-recapture, which ecologists use to count fish
they cannot count. Run two SEARCHES THAT DO NOT SHARE A METHOD. If the first
finds n1, the second finds n2, and m of them are the same, then under
independence the population is about n1*n2/m and your coverage is
(n1 + n2 - m) / that. It converts "I think I got most of them" into a number
with a stated assumption you can attack.

The assumption is the whole game and it fails in ONE specific direction:
if the two searches share a bias — both ranked by popularity, both seeded from
the same list — the overlap is inflated, the estimated total collapses toward
what you already have, and the method reports high coverage precisely when you
have missed the obscure tail. So this refuses to produce an estimate for two
lanes it can see are dependent, rather than producing a flattering one.
"""
from __future__ import annotations

import pytest

from bad_research.checks.coverage import CaptureRecapture, estimate_coverage


def test_two_disjoint_lanes_estimate_a_bigger_population_than_either_saw():
    r = estimate_coverage({"a", "b", "c", "d"}, {"c", "d", "e", "f"},
                          lane_a="web-live", lane_b="local-corpus")
    assert r.found == 6                       # the union is what you actually have
    assert r.overlap == 2
    assert r.estimated_total == pytest.approx(8.0)   # 4*4/2
    assert r.coverage == pytest.approx(0.75)
    assert r.missing_estimate == pytest.approx(2.0)


def test_high_overlap_means_high_coverage():
    r = estimate_coverage(set("abcdefghij"), set("abcdefghik"),
                          lane_a="web-live", lane_b="local-corpus")
    assert r.coverage > 0.9


def test_low_overlap_is_a_warning_that_you_have_barely_started():
    r = estimate_coverage({"a", "b", "c"}, {"x", "y", "z"},
                          lane_a="web-live", lane_b="local-corpus")
    assert r.overlap == 0
    assert r.estimated_total is None
    assert "no overlap" in r.caveat.lower()
    assert r.coverage is None, "zero overlap cannot estimate a total — it must refuse, not guess"


def test_it_REFUSES_an_estimate_when_the_two_lanes_are_not_independent():
    """The failure direction that matters: shared bias inflates overlap, which
    understates the population, which reports high coverage exactly when the
    obscure tail was missed by both."""
    r = estimate_coverage({"a", "b", "c"}, {"a", "b", "d"},
                          lane_a="web-live", lane_b="web-live")
    assert r.estimated_total is None
    assert "same lane" in r.caveat.lower()


@pytest.mark.parametrize("a,b", [("web-search-ranked", "web-search-ranked-2"),
                                 ("citations-top", "citations-recent")])
def test_two_popularity_ranked_lanes_are_declared_dependent(a: str, b: str):
    """'Even the most unpopular but still great' is the requirement that this
    protects. Two rank-ordered lanes agree about the head and are silent about
    the tail together, so their overlap is not evidence of coverage."""
    r = estimate_coverage({"1", "2", "3"}, {"1", "2", "4"}, lane_a=a, lane_b=b)
    assert r.estimated_total is None
    assert "rank" in r.caveat.lower()


def test_a_third_lane_can_be_added_and_the_estimate_tightens():
    cr = CaptureRecapture()
    cr.add("web-live", {"a", "b", "c", "d"})
    cr.add("local-corpus", {"c", "d", "e", "f"})
    cr.add("practitioner-video", {"a", "d", "f", "g"})
    assert cr.found == 7
    best = cr.best_estimate()
    assert best is not None and best >= 7, "an estimate below what you HAVE is incoherent"


def test_the_report_names_which_items_only_one_lane_found():
    """Singletons are the tail. A population where most items were seen by
    exactly one lane is a population you have barely sampled."""
    cr = CaptureRecapture()
    cr.add("web-live", {"a", "b", "c"})
    cr.add("local-corpus", {"c", "d", "e"})
    assert set(cr.singletons()) == {"a", "b", "d", "e"}
    assert cr.singleton_fraction() == pytest.approx(4 / 5)
