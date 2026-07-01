"""_synthesize's keyless-skill banner (Task 6) — the honest headless fallback.

When host inference is unavailable (no API key in a headless run) but evidence WAS
gathered, `_synthesize` must NOT crash: it degrades to a stitched, best-effort report
LED BY a banner that makes the core promise unmistakable — Bad Research runs keyless
as a Claude Code skill, and the `bad` CLI is deterministic helpers only. This tests
that fallback directly (no vault / no network), the way test_run_query stubs the seams.
"""

from __future__ import annotations

from bad_research.config import BadResearchConfig
from bad_research.pipeline import SimpleCostMeter, _synthesize


def test_synthesize_no_key_leads_with_keyless_skill_banner(monkeypatch):
    """No key + non-empty chunks: _synthesize returns (never raises) a stitched
    report that LEADS with the keyless-skill banner and still carries the evidence."""
    # Force the headless no-key path: with the key gone, get_llm_provider() raises,
    # so the except-branch (has-chunks-but-no-inference) fires deterministically.
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    chunks = [
        {"note_id": "n1", "text": "The observed warming trend is 0.2 C per decade."},
        {"note_id": "n2", "text": "A second grounded finding from another source."},
    ]

    report = _synthesize(
        "what is the trend", chunks, "fast", BadResearchConfig(), SimpleCostMeter()
    )

    # It did not raise (we reached here) and returns a string.
    assert isinstance(report, str)
    # It leads with the keyless-skill banner (the exact substring the promise rests on).
    assert "runs KEYLESS as a Claude Code skill" in report
    # It points back to the interactive skill entrypoint.
    assert "/bad-research" in report
    # It still stitches the gathered evidence below the banner (honest, best-effort).
    assert "0.2 C per decade" in report
