"""`grounding-surface` must grade a report that has no vault behind it.

The adapter `_verify_report` has accepted `note_bodies_path` all along, and the two
sibling commands (`verify-citations`, `uncited-gate`) expose it as
`--note-bodies`/`--sources`. This one did not, so on a report whose sources are
files or URLs it bound zero anchors and printed "No cited claims found" — an empty
that reads exactly like a clean bill.
"""
from __future__ import annotations

import json
import subprocess
import sys

BODY = (
    "Adaptive-RAG (Jeong et al., NAACL 2024). On Natural Questions the one-step arm "
    "scores 32.40 EM against 35.60 for multi-step. The oracle router reaches 51.20 EM "
    "at 1.59 steps on HotpotQA."
)


def _run(tmp_path, *extra):
    report = tmp_path / "r.md"
    report.write_text(
        "# T\n\nAdaptive-RAG scores 32.40 EM on Natural Questions [[src-1]].\n",
        encoding="utf-8",
    )
    return subprocess.run(
        [sys.executable, "-m", "bad_research", "grounding-surface",
         "--report", str(report), *extra],
        capture_output=True, text=True,
    )


def test_without_sources_it_reports_an_empty_ledger(tmp_path):
    """The pre-existing behaviour, pinned so the difference is visible."""
    r = _run(tmp_path)
    assert r.returncode == 0, r.stderr
    assert "No cited claims found" in r.stdout


def test_with_sources_it_grades_the_claim(tmp_path):
    notes = tmp_path / "notes.json"
    notes.write_text(json.dumps({"src-1": BODY}), encoding="utf-8")
    r = _run(tmp_path, "--note-bodies", str(notes))
    assert r.returncode == 0, r.stderr
    assert "1 cited claim" in r.stdout
    assert "supported" in r.stdout


def test_the_sources_alias_works_too(tmp_path):
    notes = tmp_path / "notes.json"
    notes.write_text(json.dumps({"src-1": BODY}), encoding="utf-8")
    r = _run(tmp_path, "--sources", str(notes))
    assert r.returncode == 0, r.stderr
    assert "1 cited claim" in r.stdout
