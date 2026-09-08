"""The cite-everything shortcut, and the deterministic half of the answer.

Grab Bench validates its scorer with a suite of shortcut baselines — empty
output, schema-only, cite-all-evidence — under one rule: *if a shortcut baseline
can pass, the benchmark is not ready.* Run against this repo's own checks that
rule fails immediately. A draft whose every sentence is false but carries a
marker resolving to a real, on-topic note comes back `{"uncited": [],
"warnings": []}` from `uncited-gate`, and `quote-drift-gate` reports PASS
because there is nothing in quotation marks to drift. The cheapest attack there
is — staple `[1]` to every sentence — beats the whole set.

Entailment in general needs a judge, and a judge on long-form groundedness lands
between 55 and 60 on a scale where 50 is chance. But the *numeric* half needs no
judge at all. A research claim that fabricates usually fabricates a quantity, and
"the note this sentence cites contains no number matching the one in the
sentence" is a fact about two strings.

So this gate is deliberately partial, and says so: it closes the numeric half of
the cite-everything hole for nothing, and it does not pretend to close the prose
half. A check that is honest about its own coverage beats one that reports clean
about the part it never looked at.
"""
from __future__ import annotations

from bad_research.checks.figure_support import check_figure_support

NOTES = {
    "n1": "The vendor build sheet records a measured PUE of 1.2 across the facility, "
          "and racks are sold by the kilowatt at $75/hour for tiered ops labour.",
    "n2": "Export controls require an end-user certificate for listed destinations.",
}
SOURCES = ["n1", "n2"]


def test_the_cite_everything_shortcut_is_caught_on_its_numbers():
    """The exact attack, verbatim from the run that beat uncited-gate."""
    shortcut = (
        "The facility operates at a PUE of 2.9, which is well above industry norms [1].\n"
        "Depreciation runs on a 12-month schedule [1].\n"
        "Ops labour is billed at $400 per hour [1].\n"
    )
    r = check_figure_support(shortcut, NOTES, SOURCES)
    assert r.ok is False
    assert len(r.findings) == 3, [f.quantity for f in r.findings]
    # The code preserves the quantity AS WRITTEN ("$400", not "400"), which is
    # right: the report should quote what the sentence said, not a normalised
    # form the reader would have to map back. Expectation corrected, not the code.
    assert {f.quantity for f in r.findings} == {"2.9", "12", "$400"}


def test_a_figure_its_note_actually_contains_passes():
    ok = "The facility runs at a PUE of 1.2 [1], with ops labour at $75/hour [1].\n"
    r = check_figure_support(ok, NOTES, SOURCES)
    assert r.ok is True, [f.quantity for f in r.findings]


def test_formatting_is_not_a_defect():
    """1.20 and 1.2 are the same number; $75 and 75 are the same number."""
    r = check_figure_support("PUE measured at 1.20 [1] and labour at 75 per hour [1].\n",
                             NOTES, SOURCES)
    assert r.ok is True, [f.quantity for f in r.findings]


def test_a_sentence_with_no_citation_is_not_this_gate_s_business():
    """uncited-gate owns that failure; two checks must not both claim it."""
    r = check_figure_support("The facility operates at a PUE of 2.9.\n", NOTES, SOURCES)
    assert r.ok is True and not r.findings


def test_a_sentence_with_no_quantity_is_reported_as_UNCHECKABLE_not_clean():
    """The honest half: prose claims are exactly what this gate cannot see, and a
    check that stays silent about its own blind spot is how a partial gate gets
    read as a full one."""
    r = check_figure_support("Racks are sold by the square foot [1].\n", NOTES, SOURCES)
    assert r.ok is True
    assert r.unchecked == 1, "a cited prose claim must be COUNTED as unchecked, not ignored"


def test_a_marker_pointing_nowhere_is_reported():
    r = check_figure_support("Ops labour is $400 per hour [9].\n", NOTES, SOURCES)
    assert r.ok is False
    assert r.findings[0].outcome == "UNRESOLVED"


def test_years_and_section_numbers_are_not_treated_as_claims():
    """A gate that fires on '2026' or 'Section 3' cries wolf and gets switched off."""
    r = check_figure_support("Per the 2026 revision, Section 3 applies [2].\n", NOTES, SOURCES)
    assert r.ok is True, [f.quantity for f in r.findings]
