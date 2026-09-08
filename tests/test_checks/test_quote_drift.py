"""S4-5, defect (a): a quoted span whose note no longer says that.

The slice's adversarial check names two planted defects. One — asserting an
absence the corpus contradicts — already has a gate. The other has none: swap a
cited note's body for a paraphrase supporting a different number and every
existing check stays green. `recitation-gate` exits 0 by construction,
`uncited-gate` only asks whether a marker is present, and the semantic verifier
lands in the 55-60 BAcc band where the slice's own shape forbids it from
closing anything.

So this one is decided by bytes. A quotation is a promise that a source says
exactly this; that promise is true or false, and a hash settles it for nothing.

Four outcomes, because they are not interchangeable and only one is innocent:
MATCHED, DRIFTED (the note says something else — the span is in a DIFFERENT
note), ABSENT (no note contains it), UNRESOLVED (the marker points nowhere).
"""
from __future__ import annotations

import pytest

from bad_research.checks.quote_drift import check_quote_drift

NOTES = {
    "n1": "The vendor build sheet records a measured PUE of 1.2 across the facility.",
    "n2": "Unrelated background on export controls and end-user certificates.",
}
SOURCES = ["n1", "n2"]


def _report(quote: str, marker: str = "[1]") -> str:
    return f'The facility efficiency is settled: "{quote}" {marker}\n'


def test_a_span_that_still_matches_its_note_passes():
    r = check_quote_drift(
        _report("The vendor build sheet records a measured PUE of 1.2 across the facility."),
        NOTES, SOURCES)
    assert r.ok is True
    assert [f.outcome for f in r.findings] == ["MATCHED"]


def test_the_planted_defect_a_paraphrase_with_a_different_number_is_caught():
    """The note now says 1.6; the report still quotes 1.2 as verbatim."""
    swapped = dict(NOTES, n1="The build sheet records a measured PUE of 1.6 facility-wide.")
    r = check_quote_drift(
        _report("The vendor build sheet records a measured PUE of 1.2 across the facility."),
        swapped, SOURCES)
    assert r.ok is False
    assert r.findings[0].outcome == "ABSENT"


def test_a_span_living_in_a_different_note_is_DRIFTED_not_absent():
    """Misattribution and fabrication are different failures and get different names."""
    r = check_quote_drift(
        _report("Unrelated background on export controls and end-user certificates."),
        NOTES, SOURCES)
    assert r.ok is False
    assert r.findings[0].outcome == "DRIFTED"
    assert r.findings[0].found_in == "n2"


def test_a_marker_pointing_nowhere_is_UNRESOLVED():
    r = check_quote_drift(
        _report("The vendor build sheet records a measured PUE of 1.2 across the facility.", "[9]"),
        NOTES, SOURCES)
    assert r.ok is False
    assert r.findings[0].outcome == "UNRESOLVED"


def test_short_scare_quotes_are_not_treated_as_quotations():
    """'so-called "agentic" systems' is not a citation promise; flagging it would
    make the gate noisy, and a noisy gate gets switched off."""
    r = check_quote_drift('So-called "agentic" retrieval is common [1]\n', NOTES, SOURCES)
    assert r.ok is True and not r.findings


def test_an_unattributed_quotation_is_not_this_gate_s_business():
    """No marker, nothing to check against. uncited-gate owns that failure."""
    r = check_quote_drift(
        'Someone wrote "The vendor build sheet records a measured PUE of 1.2 across '
        'the facility." and left it there.\n', NOTES, SOURCES)
    assert r.ok is True and not r.findings


@pytest.mark.parametrize("quoted,body", [
    # whitespace and smart quotes are rendering, not content
    ("a measured PUE of 1.2 across the facility",
     "The vendor build sheet records a measured PUE of 1.2\nacross the facility."),
])
def test_line_wrapping_is_not_drift(quoted: str, body: str):
    r = check_quote_drift(_report(quoted), {"n1": body, "n2": ""}, SOURCES)
    assert r.ok is True, [f.outcome for f in r.findings]
