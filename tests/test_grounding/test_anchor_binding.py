"""Regression: the gate's lookup key and the Tier-A quote SHA are different facts.

A live run returned 111/111 cited sentences `unsupported` (score 0.0) because the
numeric `[N]` anchors were built with `anchor_id=str(idx)` so `gate.get("2")` would
hit — but Tier A requires `quote_sha(quoted_support) == anchor_id`, and a SHA is
never `"2"`. One field, two incompatible contracts.
"""

from __future__ import annotations

import json

from bad_research.grounding.anchors import ClaimAnchor, quote_sha
from bad_research.grounding.verifier import tier_a_byte_identity

BODY = "DeepSeek-V4-Flash costs $0.66 per million output tokens off-peak."


def test_numeric_marker_anchor_passes_tier_a_and_stays_findable():
    span = "$0.66 per million output tokens"
    start = BODY.index(span)
    a = ClaimAnchor(note_id="n1", claim="", quoted_support=span,
                    char_start=start, char_end=start + len(span),
                    verified=1, anchor_id=quote_sha(span), lookup_key="2")
    assert tier_a_byte_identity(a, BODY) is True   # SHA matches the span
    assert a.lookup_key == "2"                     # gate still finds it by ordinal


def test_lookup_key_defaults_to_anchor_id_when_unset():
    a = ClaimAnchor(note_id="n1", claim="", quoted_support="x", char_start=0,
                    char_end=1, verified=1, anchor_id=quote_sha("x"))
    assert a.lookup_key == a.anchor_id


def test_numeric_citation_end_to_end_is_supported_not_unsupported(tmp_path):
    """The measured production failure: 111/111 cited sentences came back
    `unsupported` with score 0.0 though the figure was verbatim in the note."""
    from bad_research.cli.research import _verify_report

    report = tmp_path / "report.md"
    report.write_text(f"# Q\n\n{BODY} [1]\n", encoding="utf-8")
    sources = tmp_path / "sources.json"
    sources.write_text(json.dumps({"n1": BODY}), encoding="utf-8")

    results = _verify_report(str(report), "tag", note_bodies_path=str(sources))
    assert results, "the [1] marker must still resolve"
    assert [r["verdict"] for r in results] == ["supported"]
    assert results[0]["anchor_id"] == "1"  # the marker, not the SHA
