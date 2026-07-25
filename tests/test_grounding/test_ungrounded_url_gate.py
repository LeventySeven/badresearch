"""A URL in the prose must be one we actually fetched.

The uncited gate validates `[N]` markers against claim_anchors, but nothing
checked bare `http(s)://` URLs written into the report body. A model can write
"according to https://example.com/fake-study [3]" and sail through: the
sentence carries a valid citation, so the uncited gate is satisfied, while the
URL itself is invented.

Adapted from Silver's `ungroundedUrlWarning` — the discipline of failing loud
when the grounding mechanism did NOT engage, rather than trusting the prompt.
bad-research's extractor currently asks the model "do not fabricate values",
which is a request; this is the deterministic check that a request needs.

Keyless and deterministic: pure string work against the set of URLs already in
the vault. No model call, no network.
"""
from __future__ import annotations

from bad_research.grounding.gate import gate_blocks_ship, ungrounded_url_gate

FETCHED = {
    "https://example.org/real-study",
    "https://arxiv.org/abs/2401.00001",
}


def test_a_url_we_actually_fetched_is_clean():
    report = "# Q\n\nThe study found X [1] (https://example.org/real-study).\n"
    assert ungrounded_url_gate(report, FETCHED) == []


def test_a_fabricated_url_is_flagged():
    report = "# Q\n\nAccording to https://example.com/fake-study [3], X holds.\n"
    findings = ungrounded_url_gate(report, FETCHED)
    assert len(findings) == 1
    assert findings[0].failure_mode == "ungrounded-url"
    assert "example.com/fake-study" in findings[0].recommendation


def test_the_sources_section_is_exempt():
    """The Sources list legitimately enumerates every URL — not prose."""
    report = (
        "# Q\n\nA finding [1].\n\n"
        "## Sources\n\n[1] https://example.org/real-study\n"
        "[2] https://elsewhere.example/other\n"
    )
    assert ungrounded_url_gate(report, FETCHED) == []


def test_trailing_punctuation_does_not_break_the_match():
    """`(https://x/y).` must match the fetched `https://x/y`."""
    report = "# Q\n\nSee (https://example.org/real-study), and also X [1].\n"
    assert ungrounded_url_gate(report, FETCHED) == []


def test_a_url_differing_only_by_trailing_slash_is_still_grounded():
    report = "# Q\n\nSee https://example.org/real-study/ for detail [1].\n"
    assert ungrounded_url_gate(report, FETCHED) == []


def test_multiple_fabrications_are_each_reported_once():
    report = (
        "# Q\n\nPer https://fake.example/a [1] and https://fake.example/b [2].\n"
        "Again https://fake.example/a [1] repeats.\n"
    )
    findings = ungrounded_url_gate(report, FETCHED)
    assert len(findings) == 2, "each distinct fabricated URL reported once"


def test_it_warns_but_does_not_block_ship():
    """A URL can legitimately be the SUBJECT of research, not a citation.

    Blocking would punish a report about a website. `minor` routes it to the
    uncited-gate's non-blocking `warnings` channel — visible to the orchestrator
    and polish, never failing the run — matching Silver's `warning`.
    """
    report = "# Q\n\nThe breach at https://victim.example/login was reported [1].\n"
    findings = ungrounded_url_gate(report, FETCHED)
    assert len(findings) == 1
    assert findings[0].severity == "minor"
    assert gate_blocks_ship(findings) is False


def test_empty_known_set_flags_every_prose_url():
    report = "# Q\n\nSee https://anything.example/x [1].\n"
    assert len(ungrounded_url_gate(report, set())) == 1


def test_no_urls_at_all_is_clean():
    assert ungrounded_url_gate("# Q\n\nA plain finding [1].\n", FETCHED) == []
