"""When may you STOP screening a ranked pool — with a recall guarantee, not a feeling.

`bad coverage` estimates how big the population is. That is the wrong question
for a screening run: what you actually need is "have I now seen enough of the
relevant items to stop reading?", with a confidence level attached.

Evidence synthesis solved this. The mechanism, verified from the primary source
(Callaghan & Müller-Hansen 2020, Syst Rev 9:273): screen in ranked order, then
periodically draw a RANDOM sample from the not-yet-screened remainder. If that
sample turns up (almost) nothing relevant, the remainder is depleted and you can
reject the hypothesis that you have missed your recall target. Their reported
result: a reliable recall level at an average 17% work reduction.

It accretes in the exact sense the owner means — the criterion is recomputed
every round from everything screened so far, and its power grows as the screened
set grows. Early on you cannot stop no matter what; later, one clean sample is
enough.

The arithmetic is a hypergeometric tail probability and needs no dependency:
under H0 the remainder holds at least K relevant items, so P(seeing this few in a
sample of n) is exact from math.comb.
"""
from __future__ import annotations

import pytest

from bad_research.checks.screening_stop import can_stop


def test_a_clean_sample_of_a_depleted_remainder_licenses_stopping():
    """Numbers corrected after running it: a sample of 60 from 200 gives p=0.114
    when 6 items could still hide — genuinely not significant. The stop needs
    ~half the remainder sampled, and that cost is the honest finding, not a bug."""
    r = can_stop(found_relevant=95, unseen=200, sample_n=110, sample_relevant=0,
                 target_recall=0.95, alpha=0.05)
    assert r.stop is True
    assert r.p_value < 0.05
    assert r.max_missable == 5


def test_early_in_a_run_you_cannot_stop_however_clean_the_sample():
    """Power comes from the screened set. With almost nothing screened, a clean
    sample proves nothing — which is the accretion property, stated from the
    other end."""
    r = can_stop(found_relevant=2, unseen=5000, sample_n=20, sample_relevant=0,
                 target_recall=0.95, alpha=0.05)
    assert r.stop is False
    assert "not enough" in r.why.lower() or r.p_value >= 0.05


def test_finding_a_relevant_item_in_the_sample_blocks_the_stop():
    clean = can_stop(found_relevant=95, unseen=200, sample_n=110, sample_relevant=0,
                     target_recall=0.95, alpha=0.05)
    dirty = can_stop(found_relevant=95, unseen=200, sample_n=110, sample_relevant=3,
                     target_recall=0.95, alpha=0.05)
    assert clean.stop is True and dirty.stop is False
    assert dirty.p_value > clean.p_value


def test_a_bigger_sample_of_the_remainder_buys_more_confidence():
    small = can_stop(found_relevant=95, unseen=400, sample_n=20, sample_relevant=0)
    big = can_stop(found_relevant=95, unseen=400, sample_n=120, sample_relevant=0)
    assert big.p_value < small.p_value


def test_a_stricter_recall_target_is_harder_to_satisfy():
    lax = can_stop(found_relevant=95, unseen=300, sample_n=50, sample_relevant=0, target_recall=0.80)
    strict = can_stop(found_relevant=95, unseen=300, sample_n=50, sample_relevant=0, target_recall=0.99)
    assert lax.max_missable > strict.max_missable
    assert strict.p_value >= lax.p_value


def test_an_exhausted_pool_stops_trivially_and_says_so():
    r = can_stop(found_relevant=40, unseen=0, sample_n=0, sample_relevant=0)
    assert r.stop is True and "nothing left" in r.why.lower()


def test_it_refuses_a_sample_larger_than_the_remainder():
    with pytest.raises(ValueError):
        can_stop(found_relevant=10, unseen=5, sample_n=9, sample_relevant=0)


def test_the_sample_must_be_RANDOM_and_the_report_says_so():
    """The whole guarantee rests on the sample being drawn at random from the
    remainder. A sample taken in rank order measures the ranker, not the pool."""
    r = can_stop(found_relevant=95, unseen=200, sample_n=110, sample_relevant=0)
    assert "random" in r.why.lower() or "random" in r.caveat.lower()


def test_the_cost_of_the_guarantee_is_real_and_worth_knowing():
    """How much of the remainder must you sample to license a 95%-recall stop?
    Measured here, not assumed — and it is roughly half."""
    need = next(n for n in range(5, 200, 5)
                if can_stop(found_relevant=95, unseen=200, sample_n=n,
                            sample_relevant=0, target_recall=0.95).stop)
    assert need == 80, f"needed {need} of 200"   # measured: 40% of the remainder
