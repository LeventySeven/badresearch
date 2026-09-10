"""The gate has to fire on a subject stated in prose, not only on a verbatim echo.

Measured cold: a dated 11%-versus--51% disagreement about one metric was filed
COSMETIC and the gate allowed a one-sided answer, because "reranker nDCG@10 gain"
appears in no sentence anyone writes. The limit was documented as an edge case
where the answer "paraphrases the subject" — driven by a real user, paraphrase is
the normal case, and a gate that essentially never fires is not a floor. It is a
no-op that prints a number.
"""
from __future__ import annotations

from bad_research.checks.close_gate import evaluate_close, subject_match
from bad_research.checks.contradiction import Claim, find_contradictions

PAIR = [
    Claim(subject="reranker nDCG@10 gain", value="11", unit="%",
          source="bench-a.md:41", as_of="2025-03-01"),
    Claim(subject="reranker nDCG@10 gain", value="-51", unit="%",
          source="bench-b.md:12", as_of="2025-06-01"),
]

ONE_SIDED = "The reranker improves nDCG@10 by 11% across the suite."
UNRELATED = "The study measured index build time on a laptop."


def test_a_prose_answer_makes_the_disagreement_load_bearing():
    r = evaluate_close(find_contradictions(PAIR), ONE_SIDED, [])
    assert r.load_bearing, "the answer plainly discusses the subject"
    assert not r.can_close, "a one-sided answer must not close over a live disagreement"


def test_it_does_not_cry_wolf_on_a_subject_the_answer_never_raises():
    """The reason fuzzy matching was rejected. It has to stay true."""
    r = evaluate_close(find_contradictions(PAIR), UNRELATED, [])
    assert not r.load_bearing and r.cosmetic
    assert r.can_close


def test_an_exact_echo_still_matches_and_says_so():
    how, score = subject_match("H100 on-demand", "the H100 on-demand price moved")
    assert (how, score) == ("exact", 1.0)


def test_one_shared_word_is_a_near_miss_not_a_match():
    """A single common word must not be enough to block a close."""
    how, _ = subject_match("reranker nDCG@10 gain", "the reranker was slow")
    assert how == "none"


def test_a_near_miss_is_reported_rather_than_dropped():
    """Going quiet is the failure this module must not have."""
    r = evaluate_close(find_contradictions(PAIR), "the reranker was slow", [])
    assert not r.load_bearing
    assert r.near_miss, "a partial subject match must surface, not vanish into cosmetic"
    cid, subj, score = r.near_miss[0]
    assert subj == "reranker nDCG@10 gain" and 0 < score < 1


def test_a_single_distinctive_word_subject_still_works():
    how, _ = subject_match("HotpotQA", "we evaluated on HotpotQA")
    assert how in {"exact", "terms"}
