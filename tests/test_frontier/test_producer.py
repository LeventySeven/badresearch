"""S2-2: something must EXTRACT frontier items from a real fetched body.

The gate refuses a query naming no frontier item. That is only a real constraint if
something fills the frontier from what was actually read — otherwise the frontier
stays empty, every query after the first is refused, and the loop stalls instead of
accreting. The producer is the half that makes the rule survivable.

What counts as a frontier item is not "any noun". It is the thing the question did
NOT contain and a read did: a model name, a figure, a paper id, a named method, an
organisation. Cue diagnosticity is what predicts retrieval — how uniquely a cue
selects one item — so a producer that emits common words makes the frontier bigger
and the gate weaker at the same time.
"""
from __future__ import annotations

from pathlib import Path

from bad_research.frontier import extract_frontier_items

QUESTION = "does iterating beat one expansion in research"

BODY = (
    "Adaptive-RAG (Jeong et al., NAACL 2024, arXiv 2403.14403) is the controlled "
    "experiment. On Natural Questions the one-step arm scores 32.40 EM against 35.60 "
    "for multi-step, while no retrieval at all reaches 39.80. The oracle router "
    "reaches 51.20 EM at 1.59 steps on HotpotQA. NVIDIA GB200 NVL72 is unrelated."
)


def test_extracts_named_methods_papers_and_quantities():
    items = extract_frontier_items(BODY, QUESTION)
    assert "Adaptive-RAG" in items
    assert any("2403.14403" in i for i in items), "an arXiv id is a high-diagnosticity cue"
    assert any("32.40" in i for i in items), "a figure the question did not contain"


def test_multi_word_entities_survive_as_one_item():
    """And the LONGEST form wins — the more tokens, the more diagnostic the cue.

    This assertion originally demanded exactly "GB200 NVL72" and failed, because the
    producer had correctly emitted "NVIDIA GB200 NVL72" and dropped the shorter form
    as redundant. The code was right and the expectation was wrong; keeping the
    narrow assertion would have made the producer worse to make a test pass.
    """
    items = extract_frontier_items(BODY, QUESTION)
    assert any("GB200 NVL72" in i for i in items)
    assert "GB200" not in items, "the shorter, less diagnostic form should be dropped"


def test_a_sentence_initial_preposition_is_not_part_of_the_entity():
    items = extract_frontier_items(BODY, QUESTION)
    assert "Natural Questions" in items
    assert "On Natural Questions" not in items


def test_terms_already_in_the_question_are_not_frontier():
    """The frontier is what you did NOT know when you started."""
    items = extract_frontier_items(BODY, QUESTION)
    lowered = {i.casefold() for i in items}
    for already_known in ("iterating", "expansion", "research"):
        assert already_known not in lowered


def test_common_words_are_not_emitted():
    """A frontier of common words is a bigger frontier and a weaker gate."""
    items = extract_frontier_items("The result was that the thing did work well.", QUESTION)
    assert items == set() or all(len(i) > 3 for i in items)
    assert "the" not in {i.casefold() for i in items}


def test_items_are_nameable_by_the_gate_that_consumes_them():
    """A producer that emits items the gate can never match is worse than none."""
    from bad_research.frontier import Frontier, gate_query

    items = extract_frontier_items(BODY, QUESTION)
    assert items, "producer emitted nothing from a body full of specifics"
    nameable = [
        i for i in items
        if gate_query(f"tell me about {i}", Frontier(items={i}))[0]
    ]
    assert len(nameable) == len(items), (
        f"these items can never be named by any query: {sorted(set(items) - set(nameable))}"
    )


def test_runs_on_a_real_fetched_body_from_the_corpus():
    """The row says 'a real fetched body' — so use one, not a fixture string."""
    spec = Path("/Users/seventyleven/Desktop/researchfms/AGENTIC_SEARCH_SPEC.md")
    if not spec.is_file():
        import pytest

        pytest.skip("local corpus not present on this machine")
    body = spec.read_text(encoding="utf-8")[:20000]
    items = extract_frontier_items(body, QUESTION)
    assert len(items) >= 10, f"only {len(items)} items from 20k chars of a dense spec"
    # and they must all be gate-nameable, on real text rather than a curated string
    from bad_research.frontier import Frontier, gate_query

    for i in list(items)[:40]:
        assert gate_query(f"about {i}", Frontier(items={i}))[0], f"unnameable item: {i!r}"
