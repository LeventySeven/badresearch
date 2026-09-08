"""S3-2 / S3-3: an open contradiction BLOCKS the close, and both sides survive.

S3-1 gave the run a way to notice that two sources disagree. Noticing is worth
nothing on its own: the measured failure is not that agents miss a discrepancy,
it is that they average it away or silently take the newer number — the field's
canonical memory benchmark literally scores *overwriting the stale value* as
correct handling. So the disagreement has to be able to stop the run.

Three things are being pinned here.

**Load-bearing is COMPUTED, not judged.** A contradiction blocks the close if
and only if its subject appears in the answer being shipped. That is a fact
about two strings, so it cannot be talked out of. It also removes the incentive
the slice's `unknown` field worries about: manufacturing a disagreement the
answer never touches buys the agent no extra round, because a contradiction the
draft does not mention cannot block anything.

**Closing one is an ACT, not a mood.** The run records a disposition — `ranked`
(I believe this side, and here is why) or `unresolved` (the record genuinely
disagrees) — with a reason. Both are legal answers. Neither is the default, and
silence is not a third option.

**A disposition is not a licence to drop a side.** Even a `ranked` contradiction
must reach the reader with both values, both sources, and both dates where the
dates are known. That is the half that stops "I resolved it" from meaning "I
deleted the inconvenient number".
"""
from __future__ import annotations

import pytest

from bad_research.checks.close_gate import (
    Disposition,
    contradiction_id,
    evaluate_close,
)
from bad_research.checks.contradiction import Claim, find_contradictions

# Two vendors' pages disagree about one rate. This is the seeded conflict.
LEFT = Claim(subject="H100 on-demand", value="2.49", unit="$/hr",
             source="vendor-a.com/pricing", as_of="2026-08-01")
RIGHT = Claim(subject="H100 on-demand", value="3.35", unit="$/hr",
              source="vendor-b.com/pricing", as_of="2026-09-02")


@pytest.fixture
def conflict():
    found = find_contradictions([LEFT, RIGHT])
    assert len(found) == 1, "fixture is wrong: the seeded pair must contradict"
    return found[0]


FULL_ANSWER = (
    "The H100 on-demand rate is not one number. vendor-a.com/pricing lists "
    "$2.49/hr as of 2026-08-01; vendor-b.com/pricing lists $3.35/hr as of "
    "2026-09-02. I rank the second higher because it is the later capture."
)


def test_an_undisposed_load_bearing_contradiction_blocks_the_close(conflict):
    r = evaluate_close([conflict], FULL_ANSWER, dispositions=[])
    assert r.can_close is False
    assert r.blockers and "disposition" in r.blockers[0].reason.lower()


def test_a_ranked_disposition_with_both_sides_present_closes(conflict):
    d = Disposition(contradiction_id(conflict), "ranked", "the later capture wins")
    r = evaluate_close([conflict], FULL_ANSWER, dispositions=[d])
    assert r.can_close is True, [b.reason for b in r.blockers]


def test_unresolved_is_a_legal_close_not_a_failure(conflict):
    """'The record disagrees and I could not settle it' is an answer."""
    d = Disposition(contradiction_id(conflict), "unresolved", "no primary source for either")
    r = evaluate_close([conflict], FULL_ANSWER, dispositions=[d])
    assert r.can_close is True, [b.reason for b in r.blockers]


def test_a_disposition_with_no_reason_does_not_close(conflict):
    d = Disposition(contradiction_id(conflict), "ranked", "   ")
    r = evaluate_close([conflict], FULL_ANSWER, dispositions=[d])
    assert r.can_close is False
    assert any("reason" in b.reason.lower() for b in r.blockers)


def test_ranking_does_not_license_dropping_the_losing_side(conflict):
    """The whole point: a verdict must still carry the number it ruled against."""
    picked_a_winner = (
        "The H100 on-demand rate is $3.35/hr per vendor-b.com/pricing, "
        "captured 2026-09-02."
    )
    d = Disposition(contradiction_id(conflict), "ranked", "the later capture wins")
    r = evaluate_close([conflict], picked_a_winner, dispositions=[d])
    assert r.can_close is False
    assert any("2.49" in b.reason for b in r.blockers), [b.reason for b in r.blockers]


def test_provenance_must_survive_not_just_the_numbers(conflict):
    both_numbers_no_sources = (
        "The H100 on-demand rate is reported as both $2.49/hr and $3.35/hr, "
        "as of 2026-08-01 and 2026-09-02."
    )
    d = Disposition(contradiction_id(conflict), "unresolved", "two vendors disagree")
    r = evaluate_close([conflict], both_numbers_no_sources, dispositions=[d])
    assert r.can_close is False
    assert any("vendor-a.com/pricing" in b.reason for b in r.blockers)


def test_dual_dating_a_known_as_of_date_must_reach_the_reader(conflict):
    """Two accounts with different dates are a discrepancy, not a stale value —
    but only if the reader can see both dates."""
    undated = (
        "The H100 on-demand rate: vendor-a.com/pricing lists $2.49/hr and "
        "vendor-b.com/pricing lists $3.35/hr as of 2026-09-02."
    )
    d = Disposition(contradiction_id(conflict), "unresolved", "two vendors disagree")
    r = evaluate_close([conflict], undated, dispositions=[d])
    assert r.can_close is False
    assert any("2026-08-01" in b.reason for b in r.blockers)


def test_a_contradiction_the_answer_never_touches_is_cosmetic_and_blocks_nothing():
    """The anti-manufacture guard, and it is structural rather than a cap.

    An agent hunting a disagreement to justify another round gains nothing: a
    contradiction about a subject the draft does not discuss cannot hold the
    close open, whatever its delta.
    """
    off_topic = find_contradictions([
        Claim("A100 spot", "0.79", "$/hr", "vendor-a.com/pricing"),
        Claim("A100 spot", "1.90", "$/hr", "vendor-b.com/pricing"),
    ])
    r = evaluate_close(list(off_topic), FULL_ANSWER, dispositions=[])
    assert r.can_close is True
    assert len(r.cosmetic) == 1 and not r.blockers


def test_the_cap_is_never_silent_about_what_it_dropped():
    """S3-2's other half: suppression must be reportable, not invisible."""
    from bad_research.checks.contradiction import MAX_OPEN_CONTRADICTIONS

    claims = []
    for i in range(MAX_OPEN_CONTRADICTIONS + 5):
        claims += [Claim(f"subject {i}", "1", "u", "a.com"),
                   Claim(f"subject {i}", "9", "u", "b.com")]
    found = find_contradictions(claims)
    assert len(found) == MAX_OPEN_CONTRADICTIONS
    assert found.suppressed == 5
    assert found.total_found == MAX_OPEN_CONTRADICTIONS + 5


def test_the_id_is_stable_across_runs_and_symmetric_in_the_pair(conflict):
    """A disposition file written by one step must still match on the next."""
    again = find_contradictions([RIGHT, LEFT])[0]
    assert contradiction_id(conflict) == contradiction_id(again)
