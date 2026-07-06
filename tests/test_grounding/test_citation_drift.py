"""Phase 1 of 'bind, not count': a NON-BLOCKING citation-drift warning.

On the keyless path the gate seeds whole-body anchors verified=1, so a cite passes if
the note FILE exists — even if the note is about something else entirely. This adds a
`minor` (non-blocking) signal when a factual claim's content tokens barely appear in the
cited note body. It must warn, never block (block-flip is phase 2).
"""

from __future__ import annotations

import sqlite3

from bad_research.grounding.anchors import AnchorStore, ClaimAnchor
from bad_research.grounding.gate import gate_blocks_ship, no_uncited_claim_gate

_OFF_TOPIC = (
    "Arctic terns undertake the longest annual migration of any bird, flying from their "
    "Arctic breeding grounds to the Antarctic and back, a round trip that can exceed ninety "
    "thousand kilometres over a lifetime that spans roughly three decades of flight."
)
_ON_TOPIC = (
    "Across the region, Southeast Asian e-commerce gross merchandise value, commonly "
    "abbreviated GMV, grew by roughly 12.4 percent during 2024, continuing the double-digit "
    "expansion of prior years as more shoppers moved online and payments matured."
)
_CLAIM = "Southeast Asian e-commerce GMV grew 12.4% in 2024."


def _store_with(anchors):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    store = AnchorStore(conn)
    store.init_schema()
    for a in anchors:
        store.upsert(a)
    return store


def _anchor(body: str) -> ClaimAnchor:
    a = ClaimAnchor("n1", 0, len(body), "", body)  # whole-body seed
    a.verified = 1
    return a


def test_off_topic_cite_warns_but_does_not_block():
    a = _anchor(_OFF_TOPIC)
    store = _store_with([a])
    report = f"{_CLAIM} [[{a.anchor_id}]]\n"
    findings = no_uncited_claim_gate(report, store)
    drift = [f for f in findings if f.failure_mode == "citation-drift"]
    assert len(drift) == 1, f"expected one drift warning, got {[f.failure_mode for f in findings]}"
    assert drift[0].severity == "minor"
    # the whole point: it is a WARNING, not a ship-block
    assert gate_blocks_ship(findings) is False


def test_on_topic_cite_has_no_drift():
    a = _anchor(_ON_TOPIC)
    store = _store_with([a])
    report = f"{_CLAIM} [[{a.anchor_id}]]\n"
    findings = no_uncited_claim_gate(report, store)
    assert not [f for f in findings if f.failure_mode == "citation-drift"]


def test_short_span_never_triggers_drift():
    # a short quoted_support (< 200 chars) is not a whole-body seed; skip it to avoid
    # false positives — this is what protects the existing short-quote gate tests.
    short = "a 12.4% expansion"
    a = ClaimAnchor("n1", 0, len(short), "", short)
    a.verified = 1
    store = _store_with([a])
    report = f"Arctic terns migrate ninety thousand kilometres each year. [[{a.anchor_id}]]\n"
    findings = no_uncited_claim_gate(report, store)
    assert not [f for f in findings if f.failure_mode == "citation-drift"]
