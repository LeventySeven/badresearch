"""A filter that LEARNS from the run's own decisions — and a canary that catches it overreaching.

The owner's thesis: the more context and knowledge you have, the better you can
find AND filter. Everything in this kit accretes ENTITIES; nothing accretes a
model of what garbage looks like. So every reader last night made its cut cold,
from a definition, with no memory of what the previous cut had learned.

The measured cost of that: a reader screening a staff directory cut 156 rows for
"no observed artifact" and named three well-known researchers among the
casualties — its words, "my false-negative, not their false-positive." It could
not know, because nothing was watching what the filter killed.

Two halves here, and the second is the one nobody ships.

**Accretion.** Reject-signals are derived from the decisions already made: a
token that recurs in rejected items and appears in NO accepted item is
discriminative. Two decisions give you almost nothing; twenty give you a real
filter. The filter is a function of the run's history, which is the thesis made
executable.

**The canary.** Known-good items are planted in the candidate pool. If the
current rules would kill one, the filter is too aggressive and the run is told
WHICH RULE did it — before the cut ships. This is the cheapest instrument that
detects a false negative, and it is the half that turns a filter from a guess
into something with an error bar.
"""
from __future__ import annotations

import pytest

from bad_research.checks.discriminate import Decision, Discriminator


def _seed(d: Discriminator) -> None:
    """Decisions a reader would actually have made screening a staff directory."""
    for name in ("Karen Ops Manager | recruiting coordinator",
                 "Dan Recruiter | technical recruiter",
                 "Ann Facilities | facilities coordinator",
                 "Joe Comms | communications manager",
                 "Sue Events | events coordinator"):
        d.record(Decision(name, "reject", "no research output; operations role"))
    for name in ("Sewon Min | Silo LM, retrieval-scaling papers",
                 "Iz Beltagy | Longformer",
                 "Tim Dettmers | QLoRA, bitsandbytes",
                 "Pradeep Dasigi | Tulu"):
        d.record(Decision(name, "accept", "named first-author artifact"))


def test_two_decisions_buy_almost_nothing():
    """The filter is weak when it has seen little — that is the thesis, stated
    from the other end."""
    d = Discriminator()
    d.record(Decision("Karen Ops | recruiting coordinator", "reject", "ops"))
    d.record(Decision("Sewon Min | Silo LM", "accept", "artifact"))
    assert len(d.reject_signals()) <= 1


def test_the_filter_sharpens_as_decisions_accumulate():
    d = Discriminator()
    d.record(Decision("Karen Ops | recruiting coordinator", "reject", "ops"))
    d.record(Decision("Sewon Min | Silo LM", "accept", "artifact"))
    weak = len(d.reject_signals())
    _seed(d)
    assert len(d.reject_signals()) > weak, "more decisions must buy a sharper filter"
    assert "coordinator" in d.reject_signals()


def test_it_screens_new_candidates_using_what_it_learned():
    d = Discriminator()
    _seed(d)
    r = d.screen(["Pat Newperson | events coordinator",
                  "Rae Researcher | first-author on a retrieval paper"])
    assert r.rejected and r.rejected[0].item.startswith("Pat")
    assert "coordinator" in r.rejected[0].because, "a cut must name the rule that made it"
    assert [k.item for k in r.kept] == ["Rae Researcher | first-author on a retrieval paper"]


def test_THE_CANARY_refuses_a_filter_that_would_kill_a_known_good_item():
    """The exact failure that happened: a filter that removes Tim Dettmers.

    Here the run has wrongly rejected two people for carrying the word 'papers',
    which makes 'papers' discriminative and lethal.
    """
    canary = "Tim Dettmers | QLoRA and bitsandbytes papers"
    d = Discriminator(canaries={canary})
    for n in ("A Person | writes papers", "B Person | reads papers", "C Person | papers"):
        d.record(Decision(n, "reject", "mistake"))
    d.record(Decision("Someone Else | a talk", "accept", "artifact"))
    r = d.screen(["Dana Nobody | papers", canary])   # the canary is IN the pool
    assert r.safe is False
    assert r.canaries_killed, "the canary must fire"
    assert "Tim Dettmers" in r.canaries_killed[0].item
    assert "papers" in r.canaries_killed[0].because


def test_a_canary_survives_AND_was_actually_at_risk():
    """Corrected after driving the tool: the original asserted safe=True for a
    canary that was never screened. Survival of an unscreened canary is not
    safety — the canary has to be IN the pool."""
    canary = "Rae Researcher | first-author on a retrieval paper"
    d = Discriminator(canaries={canary})
    _seed(d)
    r = d.screen(["Pat Newperson | events coordinator", canary])
    assert r.safe is True and not r.canaries_killed
    assert r.rejected


def test_a_signal_appearing_in_ANY_accepted_item_is_not_discriminative():
    """The whole guard against learning a rule that cuts the good ones."""
    d = Discriminator()
    for n in ("X | research coordinator", "Y | research assistant"):
        d.record(Decision(n, "reject", "support role"))
    d.record(Decision("Z | research scientist, first author", "accept", "artifact"))
    assert "research" not in d.reject_signals(), "it appears in an accepted item"


def test_screening_reports_its_own_denominator():
    d = Discriminator()
    _seed(d)
    r = d.screen(["a | events coordinator", "b | recruiting coordinator", "c | wrote a paper"])
    assert r.considered == 3 and len(r.rejected) == 2 and len(r.kept) == 1


def test_with_no_canaries_it_says_UNMEASURED_rather_than_safe():
    """A filter nobody is measuring is not a safe filter; it is an unmeasured one."""
    d = Discriminator()
    _seed(d)
    r = d.screen(["x | events coordinator"])
    assert r.safe is None
    assert "unmeasured" in r.caveat.lower()


def test_a_canary_that_shares_no_vocabulary_with_the_pool_tested_NOTHING():
    """Found by driving the tool, not by writing this test first.

    A canary written as "Tim Dettmers | QLoRA, bitsandbytes" reported SURVIVED
    while the filter cut "Tim Dettmers | Allen Institute for AI" out of the
    candidate pool — the two share no token, so no rule this pool could teach was
    ever capable of killing the canary. A canary that cannot fail is not a
    canary, which is the same rule as a check that can only pass.
    """
    d = Discriminator(canaries={"Tim Dettmers | QLoRA, bitsandbytes"})
    for n in ("A | Allen Institute for AI", "B | Allen Institute for AI",
              "C | Allen Institute for AI"):
        d.record(Decision(n, "reject", "bare directory row"))
    d.record(Decision("Noah Smith | personal site", "accept", "linked artifact"))
    r = d.screen(["Tim Dettmers | Allen Institute for AI"])
    assert r.rejected, "the pool item is cut"
    assert r.canaries_untested == ("Tim Dettmers | QLoRA, bitsandbytes",)  # never screened
    assert r.safe is None, "survival of an unexercised canary is not safety"
    assert "was in the candidate pool" in r.caveat


def test_a_canary_drawn_FROM_the_pool_does_fire():
    canary = "Tim Dettmers | Allen Institute for AI"
    d = Discriminator(canaries={canary})
    for n in ("A | Allen Institute for AI", "B | Allen Institute for AI",
              "C | Allen Institute for AI"):
        d.record(Decision(n, "reject", "bare directory row"))
    d.record(Decision("Noah Smith | personal site", "accept", "linked artifact"))
    r = d.screen(["Someone Else | Allen Institute for AI", canary])
    assert r.safe is False and r.canaries_killed
    assert "allen" in r.canaries_killed[0].because or "institute" in r.canaries_killed[0].because


# ── cold start: the cheap structural signal you can run before ANY decision ────

def test_a_cheap_signal_ranks_a_pool_before_a_single_read():
    """Measured on the owner's corpus: 407 teardowns, 5 known to carry researcher
    names. Counting author/arXiv markers — free, no reading — puts all five in the
    top 20 and gives 313 files a score of zero. A 20x cut in reading cost at full
    recall on the known set.

    This is the cold-start half of discrimination: reject-signals need decisions
    to learn from, and at the start of a run there are none.
    """
    from bad_research.checks.discriminate import rank_by_signal
    pool = {
        "A": "**Authors:** X, Y\narXiv:2501.00001\net al. more",
        "B": "a product page with no bylines at all",
        "C": "et al.",
        "D": "nothing here either",
    }
    r = rank_by_signal(pool, r"\*\*Authors?:|et al\.|arXiv")
    assert [n for n, _ in r.ranked] == ["A", "C", "B", "D"]
    assert r.zero == ("B", "D"), "a zero-scoring item is free to exclude"
    assert r.scored == 4


def test_the_cold_signal_reports_recall_against_planted_known_good():
    """Same discipline as the canary: a screen you cannot measure is not a screen."""
    from bad_research.checks.discriminate import rank_by_signal
    pool = {"good1": "arXiv et al.", "good2": "**Authors:** Z", "junk1": "", "junk2": "x"}
    r = rank_by_signal(pool, r"\*\*Authors?:|et al\.|arXiv", known_good={"good1", "good2"}, top_k=2)
    assert r.recall_at_k == 1.0
    r2 = rank_by_signal(pool, r"\*\*Authors?:|et al\.|arXiv", known_good={"good1", "junk2"}, top_k=2)
    assert r2.recall_at_k == 0.5
    assert "junk2" in r2.missed_at_k


def test_with_no_known_good_the_recall_is_None_not_one():
    from bad_research.checks.discriminate import rank_by_signal
    r = rank_by_signal({"a": "arXiv"}, r"arXiv")
    assert r.recall_at_k is None, "an unmeasured screen must not report perfect recall"


# ── the abstain rule: where the recall actually comes from ────────────────────

def test_an_item_too_thin_to_judge_is_ABSTAINED_not_rejected():
    """From the sweep, verified in the survivor slate: a shipped clinical screening
    classifier's 5.7 points of recall came ENTIRELY from an abstain rule, not from
    the model — records below a minimum length are never classified and always
    passed through. Without it the pipeline silently deleted 3,600 real included
    studies; with it, 224. A 3,376-study difference from one rule about
    insufficient input.

    A short item matches few tokens, so a token-based filter is at its least
    reliable exactly where it looks most confident.
    """
    d = Discriminator(min_evidence_chars=25)
    for n in ("Karen Ops | recruiting coordinator", "Dan Ops | events coordinator",
              "Ann Ops | facilities coordinator"):
        d.record(Decision(n, "reject", "ops"))
    d.record(Decision("Sewon Min | Silo LM retrieval work", "accept", "artifact"))
    r = d.screen(["A. Coordinator", "Pat Newperson | events coordinator, no papers"])
    assert [a.item for a in r.abstained] == ["A. Coordinator"]
    assert "too little" in r.abstained[0].because.lower()
    assert [c.item for c in r.rejected] == ["Pat Newperson | events coordinator, no papers"]


def test_abstention_is_reported_in_the_denominator():
    d = Discriminator(min_evidence_chars=25)
    d.record(Decision("X | recruiting coordinator role", "reject", "ops"))
    d.record(Decision("Y | events coordinator role", "reject", "ops"))
    d.record(Decision("Z | first-author paper on retrieval", "accept", "artifact"))
    r = d.screen(["tiny", "also tiny", "Q | events coordinator role here"])
    assert r.considered == 3 and len(r.abstained) == 2 and len(r.rejected) == 1


def test_abstain_defaults_OFF_so_it_is_a_choice_not_a_surprise():
    d = Discriminator()
    d.record(Decision("X | recruiting coordinator", "reject", "ops"))
    d.record(Decision("Y | events coordinator", "reject", "ops"))
    d.record(Decision("Z | first-author paper", "accept", "artifact"))
    assert d.screen(["tiny"]).abstained == ()
