"""Head-to-head benchmark harness — deterministic, offline, keyless tests.

Covers the parts that must be reproducible without a network or a key:
  - blinding strips known tool markers (and `markers_present` confirms it);
  - the W/T/L tally math (win/loss/tie, ties never silently a win, missing side = tie);
  - the `bad headtohead` CLI runs offline on a stub entrant pair and emits a scorecard.
"""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from bad_research.calibrate.headtohead import (
    LOSS,
    TIE,
    WIN,
    Entrant,
    Scorecard,
    blind_report,
    load_query_set,
    markers_present,
    run_head_to_head,
)
from bad_research.calibrate.judge import AxisRails, JudgeVerdict, StubJudge
from bad_research.cli import app

runner = CliRunner()


# ── blinding ──────────────────────────────────────────────────────────────────
def test_blind_strips_known_tool_markers():
    report = (
        "# Comparison\n\n"
        "This report was produced by Gemini Deep Research using Google DeepMind models.\n"
        "bad-research and hyperresearch reach the same conclusion as Perplexity and Grok [1].\n"
    )
    blinded = blind_report(report)
    low = blinded.lower()
    for marker in ("gemini", "deepmind", "bad-research", "hyperresearch", "perplexity", "grok"):
        assert marker not in low, f"{marker!r} survived blinding: {blinded!r}"
    # The substantive content (the citation) is preserved.
    assert "[1]" in blinded


def test_markers_present_reports_then_clears():
    report = "Answer from ChatGPT and Claude [1]."
    found = markers_present(report)
    assert "chatgpt" in found and "claude" in found
    # After blinding, no known marker remains.
    assert markers_present(blind_report(report)) == []


def test_blind_strips_attribution_line():
    report = "Source: Perplexity Pro\n\nThe sky is blue [1].\n"
    blinded = blind_report(report)
    assert "perplexity" not in blinded.lower()
    assert "[1]" in blinded


def test_blind_longest_marker_first_no_orphan():
    # 'gemini deep research' must be removed as a unit, not leave 'deep research'
    # dangling because 'gemini' was stripped first.
    report = "Produced by Gemini Deep Research.\nClaim [1]."
    blinded = blind_report(report).lower()
    assert "gemini" not in blinded


# ── tally math ──────────────────────────────────────────────────────────────────
def _verdict(rails: dict[str, str]) -> JudgeVerdict:
    return JudgeVerdict.from_rails(AxisRails.from_raw(rails), rationale="test")


class _PerEntrantJudge:
    """Deterministic judge that returns a fixed rail set per entrant NAME — lets us
    drive exact pass-rates to exercise the win/tie/loss arithmetic. The entrant name
    is recovered from the (blinded) report's first line, which the test seeds."""

    def __init__(self, rails_by_tag: dict[str, dict[str, str]]):
        self._rails_by_tag = rails_by_tag

    def judge(self, query, report, corpus):
        for tag, rails in self._rails_by_tag.items():
            if tag in report:
                return _verdict(rails)
        return _verdict({a: "fail" for a in ("factual", "citation", "completeness", "source_quality", "efficiency")})


_ALL_PASS = {a: "pass" for a in ("factual", "citation", "completeness", "source_quality", "efficiency")}
_ONE_FAIL = {**_ALL_PASS, "citation": "fail"}  # pass-rate 0.8 still, but a hard-fail axis
_THIN = {**_ALL_PASS, "completeness": "borderline", "efficiency": "borderline"}  # 0.8 < 1.0


def _entrants(bad_rails_tag: str, comp_rails_tag: str):
    # Each report embeds a tag the _PerEntrantJudge keys on; blinding leaves tags intact.
    return [
        Entrant(name="bad", report=f"TAG::{bad_rails_tag}\nclaim [1]", cost_usd=0.02, latency_s=540),
        Entrant(name="comp", report=f"TAG::{comp_rails_tag}\nclaim [1]", cost_usd=0.0, latency_s=300),
    ]


def test_tally_win_when_bad_beats_competitor():
    qset = [{"id": "q1", "query": "?"}]
    judge = _PerEntrantJudge({"TAG::A": _ALL_PASS, "TAG::B": _THIN})
    card = run_head_to_head(
        qset, {"q1": _entrants("A", "B")}, bad_name="bad", competitor_name="comp", judge=judge
    )
    assert card.results[0].outcome == WIN
    assert card.tally == {WIN: 1, TIE: 0, LOSS: 0}


def test_tally_loss_when_competitor_beats_bad():
    qset = [{"id": "q1", "query": "?"}]
    judge = _PerEntrantJudge({"TAG::A": _THIN, "TAG::B": _ALL_PASS})
    card = run_head_to_head(
        qset, {"q1": _entrants("A", "B")}, bad_name="bad", competitor_name="comp", judge=judge
    )
    assert card.results[0].outcome == LOSS
    assert card.tally == {WIN: 0, TIE: 0, LOSS: 1}


def test_tally_equal_passrate_is_tie_not_win():
    qset = [{"id": "q1", "query": "?"}]
    # Both all-pass -> identical pass-rate -> honest TIE, never rounded to a win.
    judge = _PerEntrantJudge({"TAG::A": _ALL_PASS, "TAG::B": _ALL_PASS})
    card = run_head_to_head(
        qset, {"q1": _entrants("A", "A")}, bad_name="bad", competitor_name="comp", judge=judge
    )
    assert card.results[0].outcome == TIE
    assert card.tally == {WIN: 0, TIE: 1, LOSS: 0}


def test_missing_competitor_counts_as_tie_not_win():
    qset = [{"id": "q1", "query": "?"}]
    judge = StubJudge(rails=_ALL_PASS)
    only_bad = [Entrant(name="bad", report="claim [1]")]
    card = run_head_to_head(
        qset, {"q1": only_bad}, bad_name="bad", competitor_name="comp", judge=judge
    )
    assert card.results[0].outcome == TIE
    assert card.tally == {WIN: 0, TIE: 1, LOSS: 0}


def test_verdict_line_only_claims_lead_when_wins_exceed_losses():
    qset = [{"id": "q1", "query": "?"}, {"id": "q2", "query": "?"}]
    judge = _PerEntrantJudge({"TAG::A": _ALL_PASS, "TAG::B": _THIN})
    ents = {"q1": _entrants("A", "B"), "q2": _entrants("A", "B")}
    card = run_head_to_head(qset, ents, bad_name="bad", competitor_name="comp", judge=judge)
    assert card.tally == {WIN: 2, TIE: 0, LOSS: 0}
    assert "bad-research leads" in card.verdict_line()

    # A trailing tally must NOT read as a bad-research lead.
    judge2 = _PerEntrantJudge({"TAG::A": _THIN, "TAG::B": _ALL_PASS})
    card2 = run_head_to_head(qset, ents, bad_name="bad", competitor_name="comp", judge=judge2)
    assert "bad-research leads" not in card2.verdict_line()
    assert "competitor leads" in card2.verdict_line()


def test_scorecard_carries_disclaimer_and_axis_breakdown():
    qset = [{"id": "q1", "query": "?"}]
    judge = _PerEntrantJudge({"TAG::A": _ALL_PASS, "TAG::B": _ONE_FAIL})
    card = run_head_to_head(
        qset, {"q1": _entrants("A", "B")}, bad_name="bad", competitor_name="comp", judge=judge
    )
    d = card.to_dict()
    assert "disclaimer" in d and "pasted by a human" in d["disclaimer"]
    assert d["llm_judged"] is True or d["llm_judged"] is False  # present + boolean
    assert set(d["axis_breakdown"]["bad"]) == {
        "factual", "citation", "completeness", "source_quality", "efficiency"
    }
    # cost/latency metadata rides along on each entrant score.
    md = card.to_markdown()
    assert "0.0200" in md  # bad cost column
    assert "540" in md  # bad latency column


# ── starter query set ───────────────────────────────────────────────────────────
def test_starter_query_set_loads_and_spans_modalities():
    starter = (
        Path(__file__).resolve().parents[2]
        / "docs" / "benchmarks" / "queries" / "starter_set.json"
    )
    qs = load_query_set(starter)
    assert 8 <= len(qs) <= 12
    ids = {q["id"] for q in qs}
    assert len(ids) == len(qs)  # ids unique
    # Every modality in the golden taxonomy is represented somewhere in the ids.
    raw = json.loads(starter.read_text(encoding="utf-8"))
    modalities = {item["modality"] for item in raw}
    for m in (
        "causal", "comparison", "multi-domain", "contested",
        "definitional", "recency", "breadth-list", "numeric",
    ):
        assert m in modalities, f"modality {m} missing from starter set"


# ── CLI offline ───────────────────────────────────────────────────────────────
def test_cli_help_works():
    result = runner.invoke(app, ["headtohead", "--help"])
    assert result.exit_code == 0, result.output
    assert "head-to-head" in result.output.lower()


def test_cli_single_pair_offline_emits_scorecard(tmp_path: Path):
    bad_md = tmp_path / "bad.md"
    comp_md = tmp_path / "comp.md"
    # A grounded, cited bad report; an uncited competitor report (RubricJudge will
    # fail the competitor's citation axis -> bad wins, deterministically, offline).
    bad_md.write_text(
        "# Postgres vs MySQL\n\nPostgres defaults to READ COMMITTED [1]. "
        "MySQL InnoDB defaults to REPEATABLE READ [2].\n",
        encoding="utf-8",
    )
    comp_md.write_text(
        "# Postgres vs MySQL\n\nThe two databases differ in their default isolation.\n",
        encoding="utf-8",
    )
    result = runner.invoke(
        app,
        [
            "headtohead",
            "--query-id", "h2h_02_comparison",
            "--bad-report", str(bad_md),
            "--competitor-report", str(comp_md),
            "--bad-name", "bad-research-fast",
            "--competitor-name", "gemini-deep-research",
            "--out", str(tmp_path),
        ],
    )
    assert result.exit_code == 0, result.output
    sc_json = tmp_path / "headtohead-scorecard.json"
    sc_md = tmp_path / "headtohead-scorecard.md"
    assert sc_json.exists() and sc_md.exists()
    data = json.loads(sc_json.read_text())
    assert data["bad_entrant"] == "bad-research-fast"
    assert data["competitor_entrant"] == "gemini-deep-research"
    assert data["blinded"] is True
    assert data["llm_judged"] is False
    assert set(data["tally"]) == {"win", "tie", "loss"}
    assert len(data["queries"]) == 1


def test_cli_json_stdout_offline(tmp_path: Path):
    bad_md = tmp_path / "bad.md"
    comp_md = tmp_path / "comp.md"
    bad_md.write_text("# Q\n\nGrounded claim [1].\n", encoding="utf-8")
    comp_md.write_text("# Q\n\nUngrounded claim.\n", encoding="utf-8")
    result = runner.invoke(
        app,
        [
            "headtohead",
            "--query-id", "h2h_01_causal",
            "--bad-report", str(bad_md),
            "--competitor-report", str(comp_md),
            "--out", str(tmp_path),
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["ok"] is True
    assert "tally" in payload["data"]
    assert "disclaimer" in payload["data"]


def test_cli_single_pair_requires_all_three_flags(tmp_path: Path):
    bad_md = tmp_path / "bad.md"
    bad_md.write_text("# Q\n\nClaim [1].\n", encoding="utf-8")
    # Missing --competitor-report and --query-id -> clean exit(2), not a crash.
    result = runner.invoke(
        app, ["headtohead", "--bad-report", str(bad_md), "--out", str(tmp_path)]
    )
    assert result.exit_code == 2, result.output


def test_cli_manifest_offline_full_set(tmp_path: Path):
    runs = tmp_path / "runs"
    runs.mkdir()
    (runs / "bad_01.md").write_text("# A\n\nGrounded claim [1].\n", encoding="utf-8")
    (runs / "comp_01.md").write_text("# A\n\nUngrounded prose.\n", encoding="utf-8")
    manifest = {
        "bad_name": "bad-research-full",
        "competitor_name": "openai-deep-research",
        "entrants": {
            "h2h_01_causal": [
                {"name": "bad-research-full", "report_file": "bad_01.md",
                 "cost_usd": 0.05, "latency_s": 5400},
                {"name": "openai-deep-research", "report_file": "comp_01.md",
                 "cost_usd": 0.0, "latency_s": 360},
            ]
        },
    }
    man_path = runs / "manifest.json"
    man_path.write_text(json.dumps(manifest), encoding="utf-8")
    out_dir = tmp_path / "cards"
    result = runner.invoke(
        app, ["headtohead", "--manifest", str(man_path), "--out", str(out_dir)]
    )
    assert result.exit_code == 0, result.output
    data = json.loads((out_dir / "headtohead-scorecard.json").read_text())
    # Manifest names flow through.
    assert data["bad_entrant"] == "bad-research-full"
    assert data["competitor_entrant"] == "openai-deep-research"
    # Only the manifested query is scored; the rest of the starter set is absent
    # from the manifest, so the harness scores just q with both sides present.
    scored_ids = {q["id"] for q in data["queries"]}
    assert "h2h_01_causal" in scored_ids


def test_scorecard_to_dict_roundtrips_json():
    card = Scorecard(
        bad_name="bad", competitor_name="comp", results=[], llm_judged=False, blinded=True
    )
    parsed = json.loads(card.to_json())
    assert parsed["tally"] == {"win": 0, "tie": 0, "loss": 0}
    assert parsed["benchmark"] == "head-to-head"
