"""`--json` must put JSON and ONLY JSON on stdout.

Found in prod: crawl4ai's browse rung writes progress lines to STDOUT
(`[INIT].... → Crawl4AI 0.8.6`, `[FETCH]... ↓ https://…`), so roughly every
other `bad funnel-gather --json` run emitted a stream that `json.loads` refuses:

    '[INIT].... -> Crawl4AI 0.8.6 \\n[EXPORT].. Exporting media ...{"note_ids": ...'

The skills parse this envelope to branch (and now to read `degraded`), so a
polluted stdout is an intermittent hard failure of the whole pipeline — the
"sometimes it breaks" class. Library chatter belongs on stderr; stdout is the
machine contract.
"""
from __future__ import annotations

import json

from typer.testing import CliRunner

import bad_research.cli.research as RESEARCH  # noqa: N812
from bad_research.cli import app


def test_library_stdout_noise_never_reaches_the_json_envelope(monkeypatch):
    """A backend that prints to stdout must not corrupt the contract."""
    import sys

    def _noisy_run_funnel(q, *, mode, vault_tag, search_plan=None, max_queries=None,
                          read_top_k=None, concurrency=None, raw=False):
        # Exactly what crawl4ai does mid-run.
        sys.stdout.write("[INIT].... → Crawl4AI 0.8.6 \n")
        sys.stdout.write("[FETCH]... ↓ https://example.org/a\n")
        return {"note_ids": ["n1"], "top_chunks": [], "n_read": 1, "n_stored": 1,
                "ok": True, "degraded": False, "degraded_reasons": [],
                "warnings": [], "provider_outcomes": {"ddgs": "ok"}}

    monkeypatch.setattr(RESEARCH, "run_funnel", _noisy_run_funnel)
    res = CliRunner().invoke(
        app, ["funnel-gather", "topic", "--mode", "light", "--json"]
    )
    assert res.exit_code == 0, res.stdout
    parsed = json.loads(res.stdout)  # must not raise
    assert parsed["note_ids"] == ["n1"]
    assert parsed["ok"] is True


def test_the_captured_noise_is_still_visible_on_stderr(monkeypatch):
    """Suppressing the chatter entirely would destroy debuggability."""
    import sys

    def _noisy_run_funnel(q, *, mode, vault_tag, search_plan=None, max_queries=None,
                          read_top_k=None, concurrency=None, raw=False):
        sys.stdout.write("[FETCH]... ↓ https://example.org/a\n")
        return {"note_ids": [], "top_chunks": [], "n_read": 0, "n_stored": 0,
                "ok": True, "degraded": False, "degraded_reasons": [],
                "warnings": [], "provider_outcomes": {}}

    monkeypatch.setattr(RESEARCH, "run_funnel", _noisy_run_funnel)
    res = CliRunner().invoke(
        app, ["funnel-gather", "topic", "--mode", "light", "--json"]
    )
    assert "[FETCH]" in res.stderr
    json.loads(res.stdout)


def test_degraded_envelope_still_parses_when_stdout_is_noisy(monkeypatch):
    """The degraded branch is exactly when the orchestrator MUST parse cleanly."""
    import sys

    def _noisy_run_funnel(q, *, mode, vault_tag, search_plan=None, max_queries=None,
                          read_top_k=None, concurrency=None, raw=False):
        sys.stdout.write("[INIT].... → Crawl4AI 0.8.6 \n")
        return {"note_ids": [], "top_chunks": [], "n_read": 0, "n_stored": 0,
                "ok": False, "degraded": True,
                "degraded_reasons": ["no_search_provider_available"],
                "warnings": [], "provider_outcomes": {"ddgs": "unavailable"}}

    monkeypatch.setattr(RESEARCH, "run_funnel", _noisy_run_funnel)
    res = CliRunner().invoke(
        app, ["funnel-gather", "topic", "--mode", "light", "--json"]
    )
    assert res.exit_code == 3
    assert json.loads(res.stdout)["degraded"] is True


def test_a_fenced_envelope_is_still_strict_json_on_a_noisy_stdout(monkeypatch):
    """Issue #39 put untrusted-content MARKERS inside `top_chunks[*].text` and a
    ~700-char preamble on `untrusted_notice`. Both carry angle brackets, quotes
    and newlines, and both share stdout with crawl4ai's progress chatter — so the
    strict-JSON contract the skills parse has to survive all three at once.
    """
    import sys

    from bad_research.quality.injection import INJECTION_PREAMBLE, wrap_untrusted

    body = 'page text with "quotes", <tags> and\nnewlines'

    def _noisy_run_funnel(q, *, mode, vault_tag, search_plan=None, max_queries=None,
                          read_top_k=None, concurrency=None, raw=False):
        sys.stdout.write("[FETCH]... ↓ https://example.org/a\n")
        return {"note_ids": ["n1"],
                "top_chunks": [{"note_id": "n1",
                                "text": wrap_untrusted(body, include_preamble=False)}],
                "n_read": 1, "n_stored": 1, "ok": True, "degraded": False,
                "degraded_reasons": [], "warnings": [],
                "provider_outcomes": {"ddgs": "ok"},
                "coverage_gaps": [{"provider": "s2", "outcome": "rate-limited"}],
                "n_fetch_failed": 4,
                "untrusted_notice": INJECTION_PREAMBLE}

    monkeypatch.setattr(RESEARCH, "run_funnel", _noisy_run_funnel)
    res = CliRunner().invoke(app, ["funnel-gather", "topic", "--mode", "light", "--json"])

    assert res.exit_code == 0, res.stdout
    parsed = json.loads(res.stdout)  # must not raise
    assert parsed["untrusted_notice"] == INJECTION_PREAMBLE
    assert parsed["top_chunks"][0]["text"].startswith("<BEGIN UNTRUSTED CONTENT>")
    assert parsed["coverage_gaps"] == [{"provider": "s2", "outcome": "rate-limited"}]
    assert parsed["n_fetch_failed"] == 4
