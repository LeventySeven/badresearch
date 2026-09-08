"""S4-2: byte-identity must bind to a LOCATED SPAN, not to the whole note body.

The defect this pins, measured on a live run: the `--note-bodies` standalone path
seeds every anchor with `quoted_support = the entire note body` and
`char_start=0, char_end=len(body)`. `tier_a_byte_identity` then reduces to
`body == body` and returns True for **any** body — including one that supports
nothing the report claims. Before the anchor-binding fix it returned False for
every row (111/111 `unsupported`); after, it returns True for every row. Neither
is a check.

Spec R9 counts byte-identity as an *executing* check. On a whole-body anchor it
executes and proves nothing, so this module gives the difference a name
(`is_vacuous_span`) and asserts that a real located span is not vacuous, that a
whole-body anchor is, and — the part that actually catches fabrication — that a
quote which cannot be found in its body is DROPPED rather than anchored.
"""
from __future__ import annotations

import sqlite3

import pytest

from bad_research.grounding.anchors import (
    AnchorStore,
    ClaimAnchor,
    build_from_claims,
    is_vacuous_span,
    quote_sha,
)
from bad_research.grounding.verifier import tier_a_byte_identity

BODY = "NVIDIA H200 rents for $2.49/hr on packet.ai, measured September 2026."


@pytest.fixture
def store() -> AnchorStore:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    s = AnchorStore(conn)
    s.init_schema()
    return s


def test_a_located_claim_anchors_to_its_span_not_the_whole_body(store: AnchorStore):
    claims = [{"source_note_id": "n1", "claim": "h200 hourly price", "quoted_support": "$2.49/hr"}]
    assert build_from_claims(store, claims, {"n1": BODY}) == 1

    anchor = next(iter(store.all()))
    assert (anchor.char_start, anchor.char_end) != (0, len(BODY)), (
        "the anchor covers the entire body — Tier A would reduce to body == body"
    )
    assert anchor.quoted_support == "$2.49/hr"
    assert tier_a_byte_identity(anchor, BODY) is True
    assert is_vacuous_span(anchor, BODY) is False


def test_a_whole_body_anchor_passes_tier_a_and_is_still_vacuous():
    """This is the shape the standalone path ships, and why it proves nothing."""
    anchor = ClaimAnchor(
        note_id="n1", char_start=0, char_end=len(BODY), claim="",
        quoted_support=BODY, verified=1, anchor_id=quote_sha(BODY),
    )
    assert tier_a_byte_identity(anchor, BODY) is True   # it passes...
    assert is_vacuous_span(anchor, BODY) is True        # ...and means nothing

    unrelated = "A body that supports no claim in the report whatsoever."
    vacuous = ClaimAnchor(
        note_id="n1", char_start=0, char_end=len(unrelated), claim="",
        quoted_support=unrelated, verified=1, anchor_id=quote_sha(unrelated),
    )
    assert tier_a_byte_identity(vacuous, unrelated) is True, (
        "demonstrates the vacuity: byte-identity passes on a body that supports nothing"
    )
    assert is_vacuous_span(vacuous, unrelated) is True


def test_a_quote_that_is_not_in_the_body_is_dropped_not_anchored(store: AnchorStore):
    """The fabrication catch: an unlocatable quote is a hallucinated quote."""
    claims = [{
        "source_note_id": "n1",
        "claim": "h200 hourly price",
        "quoted_support": "H200 costs roughly two hundred fifty dollars an hour",
    }]
    assert build_from_claims(store, claims, {"n1": BODY}) == 0
    assert list(store.all()) == []


def test_a_paraphrase_with_a_different_number_is_dropped(store: AnchorStore):
    """The subtle one — plausible wording, wrong figure, not present verbatim."""
    claims = [{"source_note_id": "n1", "claim": "price", "quoted_support": "$6.31/hr"}]
    assert build_from_claims(store, claims, {"n1": BODY}) == 0


def test_vacuity_is_about_coverage_not_length():
    """A span equal to the body by coincidence of length is still vacuous."""
    body = "exactly this"
    anchor = ClaimAnchor(
        note_id="n", char_start=0, char_end=len(body), claim="",
        quoted_support=body, verified=1, anchor_id=quote_sha(body),
    )
    assert is_vacuous_span(anchor, body) is True

    partial = ClaimAnchor(
        note_id="n", char_start=0, char_end=7, claim="",
        quoted_support="exactly", verified=1, anchor_id=quote_sha("exactly"),
    )
    assert is_vacuous_span(partial, body) is False


def test_verifier_does_not_credit_a_vacuous_anchor_with_a_tier_a_pass():
    """A whole-body anchor must not be recorded as byte-verified.

    Tier A on such an anchor cannot fail, so crediting it is how a citation gate
    reports grounding it never established. The anchor still proceeds to the
    semantic tiers — refusing it outright would recreate the 111/111 `unsupported`
    catastrophe this binding work exists to fix — but byte-identity must not be
    the thing that passed it.

    THIS TEST EXERCISES THE CODE PATH ON PURPOSE. Its first version asserted
    `"is_vacuous_span" in inspect.getsource(verifier)` and passed while the symbol
    was CALLED but never IMPORTED — a NameError waiting for the first real run.
    A source scan reports green on prose about the code; only running it catches that.
    """
    from bad_research.grounding import verifier as V

    assert hasattr(V, "is_vacuous_span"), (
        "is_vacuous_span is not resolvable in verifier's namespace — if it is called "
        "there, that call raises NameError on the first vacuous anchor"
    )

    body = "A body that supports no claim in the report whatsoever."
    anchor = ClaimAnchor(
        note_id="n1", char_start=0, char_end=len(body), claim="",
        quoted_support=body, verified=1, anchor_id=quote_sha(body), lookup_key="1",
    )
    # the guard the verifier consults must classify this as vacuous
    assert V.is_vacuous_span(anchor, body) is True
    # and a genuinely located span must not be swept up by it
    located = ClaimAnchor(
        note_id="n1", char_start=2, char_end=8, claim="",
        quoted_support=body[2:8], verified=1, anchor_id=quote_sha(body[2:8]), lookup_key="2",
    )
    assert V.is_vacuous_span(located, body) is False
    assert tier_a_byte_identity(located, body) is True
