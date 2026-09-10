"""The absence gate, pinned against the two REAL sentences that motivated it.

A blind judge falsified one of these in a single fetch and passed the other. They are
the same fact; the only difference is whether the sentence says where the author
looked. That is the whole discriminator, so it is the test.
"""
from __future__ import annotations

from bad_research.checks.absence_claim import find_absence_claims

# Shipped, and overturned by a judge who found Thomas et al. (SIGIR 2024) in one fetch.
SHIPPED = (
    "**No source measures the false-negative rate of a source-quality filter directly.** "
    "CRAG's 84.3% and Self-RAG's 93.5% are overall agreement against LLM-derived labels."
)
# The comparison run, on the same fact, correct because it bounds the SEARCH.
CORRECT = (
    "A learned judge's discard-side error rate has been measured once, in retrieval, and "
    "no published work in this corpus has sampled and read at comparable scale what a "
    "production pretraining quality classifier threw away."
)


def test_the_sentence_that_shipped_is_refused():
    r = find_absence_claims(SHIPPED)
    assert r.claims, "the gate must SEE the claim before it can judge it"
    assert not r.ok
    assert any("No source measures" in c.sentence for c in r.unscoped)


def test_the_sentence_that_was_right_passes():
    r = find_absence_claims(CORRECT)
    assert r.claims, "same claim shape — it must still be detected, then cleared"
    assert r.ok, [c.sentence for c in r.unscoped]
    assert any("corpus" in c.scope for c in r.claims)


def test_narrowing_the_SUBJECT_does_not_rescue_it():
    """The shipped claim had a very narrow subject and was still false of the field.

    This is the rule that makes the gate worth having: a qualifier has to bound where
    you looked, not what you were looking for. Without it the gate would wave through
    exactly the sentence it exists to catch.
    """
    subject_narrow = (
        "No paper measures the direction-split false-negative rate of a "
        "source-quality classifier under domain shift at production scale."
    )
    assert not find_absence_claims(subject_narrow).ok


def test_rhetoric_is_not_an_absence_claim():
    """Measured false positives from the first version, kept as a regression."""
    for rhetoric in (
        "Without this dataset there is no neural retrieval era.",
        "Without this there is no TREC, no MS MARCO, no BEIR, no MTEB.",
        "The corpus discusses these mechanisms as though they had no authors.",
        "This is how a system trains a retriever when nobody has labelled which passage helped.",
    ):
        assert find_absence_claims(rhetoric).claims == (), rhetoric


def test_someone_elses_absence_claim_is_not_ours():
    """A quotation is the source's assertion, not the report's."""
    quoted = 'Exa\'s founder: "Our model predicts links people share, and no one shares SEO blog posts."'
    assert find_absence_claims(quoted).claims == ()


def test_a_fenced_block_is_quoted_material():
    fenced = "```\nNo source measures this.\n```\n"
    assert find_absence_claims(fenced).claims == ()


def test_an_empty_result_says_it_is_unchecked_not_clean():
    """The four kinds of nothing apply to this gate's own output too."""
    r = find_absence_claims("A report that asserts nothing about absence.")
    assert r.ok
    assert "unchecked" in r.caveat


def test_first_person_reach_counts_as_scope():
    for scoped in (
        "I could not find any published measurement of the discard-side rate.",
        "Of the 44 sources I read, no paper splits the error by direction.",
        "In the pretraining lane, no study reports what the classifier threw away.",
    ):
        assert find_absence_claims(scoped).ok, scoped
