"""The no-source-claim check: an absence claim the run's own corpus contradicts.

Reproduces a live defect. A report asserted "No source was found for GPU
depreciation schedules... PUE, cooling overhead. This is the largest evidentiary
gap in this report" while a note the SAME report cited elsewhere carried a
36-month straight-line schedule, an explicit PUE of 1.2, and tiered ops-labour
rates. A model critic caught it; these tests make it a script.
"""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from bad_research.checks.no_source_claim import (
    UnfoundedAbsenceClaim,
    content_words,
    find_unfounded_absence_claims,
)
from bad_research.cli import app

REPORT = "No source was found for GPU depreciation schedules or datacenter PUE.\n"
NOTES = {"n21": "36-month straight-line depreciation; PUE of 1.2; $75/hour labour."}

FIXTURES = Path(__file__).parent / "fixtures"
runner = CliRunner()


# ── the three behaviours the check exists for ────────────────────────────────
def test_flags_an_absence_claim_the_corpus_contradicts():
    f = find_unfounded_absence_claims(REPORT, NOTES)
    assert len(f) == 1 and "depreciation" in f[0].subject.lower()


def test_passes_when_the_corpus_really_is_silent():
    assert find_unfounded_absence_claims(REPORT, {"n1": "entirely unrelated text"}) == []


def test_does_not_fire_on_a_single_incidental_word():
    # one common word overlapping is not evidence the corpus covers the subject
    assert find_unfounded_absence_claims("No source was found for the cost of tunnelling.",
                                         {"n1": "the cost of a coffee"}) == []


# ── the finding carries what a reader needs to act ───────────────────────────
def test_finding_carries_note_id_sentence_and_matched_words():
    f = find_unfounded_absence_claims(REPORT, NOTES)[0]
    assert isinstance(f, UnfoundedAbsenceClaim)
    assert f.note_id == "n21"
    assert f.sentence.startswith("No source was found for GPU")
    assert set(f.matched_words) == {"depreciation", "pue"}
    assert f.to_dict()["note_id"] == "n21"


# ── the trigger surface ──────────────────────────────────────────────────────
def test_other_absence_phrasings_trigger():
    notes = {"n1": "Quarterly cooling overhead ran to 14% of facility draw."}
    for report in (
        "There is no published cooling overhead figure for this facility.",
        "No data on cooling overhead for the facility was located.",
        "I could not establish cooling overhead for the facility.",
        "Cooling overhead for the facility is not available.",
    ):
        assert find_unfounded_absence_claims(report, notes), report


def test_a_sentence_with_no_absence_phrasing_is_never_examined():
    # the corpus plainly covers this, but the report never claimed it did not
    assert find_unfounded_absence_claims(
        "GPU depreciation schedules are discussed at length below.",
        {"n21": "36-month straight-line depreciation of the GPU fleet"},
    ) == []


# ── false-positive guards (a check that cries wolf gets disabled) ────────────
def test_short_acronyms_count_but_bare_numbers_do_not():
    assert content_words("GPU depreciation in 2024") == ["gpu", "depreciation"]


def test_substring_overlap_is_not_a_match():
    # "pue" inside "Puerto" is not the metric PUE
    assert find_unfounded_absence_claims(
        "No source was found for datacenter PUE ratios.",
        {"n1": "Puerto Rico ratiocination"},
    ) == []


def test_stopwords_cannot_carry_a_finding():
    assert find_unfounded_absence_claims(
        "No source was found for the annual figures.",
        {"n1": "the annual report of the figures committee"},
    ) != []
    assert content_words("that which would have been") == []


def test_every_contradicting_note_gets_its_own_finding():
    notes = {"a": "depreciation and PUE", "b": "PUE plus depreciation", "c": "nothing"}
    got = find_unfounded_absence_claims(REPORT, notes)
    assert [f.note_id for f in got] == ["a", "b"]


# ── the CLI gate ─────────────────────────────────────────────────────────────
def test_cli_exits_1_on_the_planted_defect_fixture():
    res = runner.invoke(app, [
        "no-source-claim-gate",
        "--report", str(FIXTURES / "planted" / "report.md"),
        "--notes", str(FIXTURES / "planted" / "notes.json"),
        "--json",
    ])
    assert res.exit_code == 1, res.stdout
    payload = json.loads(res.stdout)
    assert payload["notes_scanned"] == 3
    assert payload["absence_claims_examined"] == 1
    assert len(payload["findings"]) == 1
    assert payload["findings"][0]["note_id"] == "n21"


def test_cli_exits_0_on_the_clean_fixture():
    res = runner.invoke(app, [
        "no-source-claim-gate",
        "--report", str(FIXTURES / "clean" / "report.md"),
        "--notes", str(FIXTURES / "clean" / "notes.json"),
        "--json",
    ])
    assert res.exit_code == 0, res.stdout
    assert json.loads(res.stdout)["findings"] == []


def test_cli_human_output_leads_with_the_enumeration_line():
    res = runner.invoke(app, [
        "no-source-claim-gate",
        "--report", str(FIXTURES / "planted" / "report.md"),
        "--notes", str(FIXTURES / "planted" / "notes.json"),
    ])
    assert res.exit_code == 1
    lines = res.stdout.strip().splitlines()
    assert lines[0] == (
        "no-source-claim | notes scanned 3 | absence claims examined 1 | findings 1"
    )
    assert "n21" in lines[1]


def test_cli_reads_a_directory_of_notes(tmp_path):
    d = tmp_path / "notes"
    d.mkdir()
    (d / "n21.md").write_text("36-month straight-line depreciation; PUE of 1.2.")
    (d / "n99.md").write_text("nothing relevant here")
    (d / "ignored.bin").write_bytes(b"\x00")
    report = tmp_path / "r.md"
    report.write_text(REPORT)
    res = runner.invoke(app, [
        "no-source-claim-gate", "--report", str(report), "--notes", str(d), "--json",
    ])
    assert res.exit_code == 1, res.stdout
    payload = json.loads(res.stdout)
    assert payload["notes_scanned"] == 2
    assert payload["findings"][0]["note_id"] == "n21"


def test_cli_accepts_a_json_list_of_note_records(tmp_path):
    notes = tmp_path / "corpus.json"
    notes.write_text(json.dumps([{"note_id": "n21", "text": NOTES["n21"]}]))
    report = tmp_path / "r.md"
    report.write_text(REPORT)
    res = runner.invoke(app, [
        "no-source-claim-gate", "--report", str(report), "--notes", str(notes), "--json",
    ])
    assert res.exit_code == 1, res.stdout
    assert json.loads(res.stdout)["findings"][0]["note_id"] == "n21"


def test_cli_errors_on_a_missing_report(tmp_path):
    res = runner.invoke(app, [
        "no-source-claim-gate", "--report", str(tmp_path / "nope.md"),
        "--notes", str(FIXTURES / "clean" / "notes.json"),
    ])
    assert res.exit_code == 2
    assert "nope.md" in res.stdout


def test_cli_errors_on_an_unusable_notes_payload(tmp_path):
    notes = tmp_path / "bad.json"
    notes.write_text(json.dumps("just a string"))
    report = tmp_path / "r.md"
    report.write_text(REPORT)
    res = runner.invoke(app, [
        "no-source-claim-gate", "--report", str(report), "--notes", str(notes),
    ])
    assert res.exit_code == 2


def test_a_one_word_subject_is_never_examined():
    # a single content word cannot clear the co-occurrence bar, so the claim is
    # dropped before any note is read -- the check would rather stay quiet
    assert find_unfounded_absence_claims(
        "No source was found for tunnelling.", {"n1": "tunnelling, tunnelling, tunnelling"}
    ) == []


def test_cli_errors_on_a_missing_notes_path(tmp_path):
    report = tmp_path / "r.md"
    report.write_text(REPORT)
    res = runner.invoke(app, [
        "no-source-claim-gate", "--report", str(report), "--notes", str(tmp_path / "gone.json"),
    ])
    assert res.exit_code == 2
    assert "gone.json" in res.stdout


def test_cli_errors_on_malformed_json(tmp_path):
    notes = tmp_path / "bad.json"
    notes.write_text("{not json")
    report = tmp_path / "r.md"
    report.write_text(REPORT)
    res = runner.invoke(app, [
        "no-source-claim-gate", "--report", str(report), "--notes", str(notes),
    ])
    assert res.exit_code == 2
    assert "could not parse" in res.stdout


def test_cli_errors_on_a_list_of_non_objects(tmp_path):
    notes = tmp_path / "list.json"
    notes.write_text(json.dumps(["a string, not a note record"]))
    report = tmp_path / "r.md"
    report.write_text(REPORT)
    res = runner.invoke(app, [
        "no-source-claim-gate", "--report", str(report), "--notes", str(notes),
    ])
    assert res.exit_code == 2
    assert "item 0" in res.stdout
