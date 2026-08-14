"""Tests for the 6 vault lifecycle / corpus-inspection CLI commands.

Covers init, vault-tag, archive-run, search (data.results envelope, filters,
--include-body), lint (4 rules, exit-code on error severity), and note show
(single + multi-id, data.notes envelope). All offline, tmp_path vaults.
"""

import json

from typer.testing import CliRunner

from bad_research.cli import app

runner = CliRunner()


# ── fixtures / helpers ────────────────────────────────────────────────────────

def _init_vault(tmp_path):
    """Create a fresh vault at tmp_path; return the research/notes dir."""
    res = runner.invoke(app, ["init", str(tmp_path), "--json"])
    assert res.exit_code == 0, res.stdout
    return tmp_path / "research" / "notes"


def _write_note(notes_dir, *, note_id, title, tags, note_type="note",
                source=None, body="Some body text."):
    fm = [
        "---",
        f"title: {title}",
        f"id: {note_id}",
        f"tags: [{', '.join(tags)}]",
        f"type: {note_type}",
        "status: draft",
    ]
    if source:
        fm.append(f"source: {source}")
    fm += ["---", "", f"# {title}", "", body, ""]
    (notes_dir / f"{note_id}.md").write_text("\n".join(fm), encoding="utf-8")


# ── init ──────────────────────────────────────────────────────────────────────

def test_init_creates_vault_and_json_shape(tmp_path):
    res = runner.invoke(app, ["init", str(tmp_path), "--json"])
    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    assert out["ok"] is True
    assert set(out["data"]) >= {"vault_root", "research_dir", "db"}
    assert (tmp_path / ".hyperresearch").is_dir()
    assert (tmp_path / "research" / "notes").is_dir()


def test_init_twice_fails_cleanly(tmp_path):
    runner.invoke(app, ["init", str(tmp_path), "--json"])
    res = runner.invoke(app, ["init", str(tmp_path), "--json"])
    assert res.exit_code == 1
    out = json.loads(res.stdout)
    assert out["ok"] is False
    assert out["error_code"] == "VAULT_EXISTS"


def test_init_human_output(tmp_path):
    res = runner.invoke(app, ["init", str(tmp_path)])
    assert res.exit_code == 0
    assert "vault_root" in res.stdout


# ── vault-tag ───────────────────────────────────────────────────────────────

def test_vault_tag_returns_field_with_suffix(tmp_path, monkeypatch):
    _init_vault(tmp_path)
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["vault-tag", "efield-dft-sac", "--json"])
    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    vt = out["data"]["vault_tag"]
    assert vt.startswith("efield-dft-sac-")
    suffix = out["data"]["suffix"]
    assert len(suffix) == 6
    assert vt == f"efield-dft-sac-{suffix}"


def test_vault_tag_avoids_existing_query_file(tmp_path, monkeypatch):
    _init_vault(tmp_path)
    monkeypatch.chdir(tmp_path)
    # First mint, then materialise the query file so the suffix is "taken".
    first = json.loads(
        runner.invoke(app, ["vault-tag", "topic", "--json"]).stdout
    )["data"]["vault_tag"]
    (tmp_path / "research" / f"query-{first}.md").write_text("x", encoding="utf-8")
    # A second mint must not collide with the taken tag.
    second = json.loads(
        runner.invoke(app, ["vault-tag", "topic", "--json"]).stdout
    )["data"]["vault_tag"]
    assert second != first


# ── archive-run ───────────────────────────────────────────────────────────────

def test_archive_run_noops_on_fresh_vault(tmp_path, monkeypatch):
    _init_vault(tmp_path)
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["archive-run", "--json"])
    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    assert out["data"]["archived"] is False
    assert out["data"]["moved_files"] == []


def test_archive_run_moves_scratch_files(tmp_path, monkeypatch):
    _init_vault(tmp_path)
    monkeypatch.chdir(tmp_path)
    research = tmp_path / "research"
    (research / "scaffold.md").write_text("scaffold", encoding="utf-8")
    (research / "loci.json").write_text("[]", encoding="utf-8")
    (research / "critic-findings-a.json").write_text("{}", encoding="utf-8")
    (research / "temp" / "scratch.md").write_text("tmp", encoding="utf-8")
    res = runner.invoke(app, ["archive-run", "--json"])
    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    assert out["data"]["archived"] is True
    moved = set(out["data"]["moved_files"])
    assert {"scaffold.md", "loci.json", "critic-findings-a.json", "temp/"} <= moved
    # Originals are gone; temp dir was re-created empty.
    assert not (research / "scaffold.md").exists()
    assert (research / "temp").is_dir()
    assert (research / "runs").is_dir()
    archive_dir = out["data"]["archive_dir"]
    assert archive_dir and (research / "scaffold.md").parent == research


def test_archive_run_moves_the_per_analyst_loci_files(tmp_path, monkeypatch):
    """`loci-a.json`/`loci-b.json` are step-4 scratch like `loci.json`.

    Left behind they leak the previous run's loci into the next one.
    """
    _init_vault(tmp_path)
    monkeypatch.chdir(tmp_path)
    research = tmp_path / "research"
    (research / "loci-a.json").write_text("[]", encoding="utf-8")
    (research / "loci-b.json").write_text("[]", encoding="utf-8")
    res = runner.invoke(app, ["archive-run", "--json"])
    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    assert {"loci-a.json", "loci-b.json"} <= set(out["data"]["moved_files"])
    assert not (research / "loci-a.json").exists()
    assert not (research / "loci-b.json").exists()


# --- issue #43: archive-run must not archive over an INTERRUPTED run ---------
# A session-limit kill leaves a run mid-pipeline. The next invocation runs step
# 0.5 (`bad archive-run`) first, and archiving the scaffold / loci /
# prompt-decomposition / research/temp/ tree is exactly what makes the documented
# step-granular Recovery path find nothing.

def _start_run(tmp_path, tag):
    """Write the artifacts a run has on disk once it is past step 3."""
    research = tmp_path / "research"
    (research / f"query-{tag}.md").write_text(f"# {tag}\n", encoding="utf-8")
    (research / "scaffold.md").write_text("scaffold", encoding="utf-8")
    (research / "prompt-decomposition.json").write_text("{}", encoding="utf-8")
    (research / "temp" / "coverage-matrix.md").write_text("m", encoding="utf-8")
    return research


def test_archive_run_refuses_to_bury_an_interrupted_run(tmp_path, monkeypatch):
    _init_vault(tmp_path)
    monkeypatch.chdir(tmp_path)
    research = _start_run(tmp_path, "efield-dft-sac-a3f9b7")  # no final report

    res = runner.invoke(app, ["archive-run", "--json"])

    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    assert out["data"]["archived"] is False
    assert out["data"]["interrupted_run"] == "efield-dft-sac-a3f9b7"
    assert "--force" in out["data"]["reason"]
    # The Recovery ledger's artifacts are all still where it looks for them.
    assert (research / "scaffold.md").exists()
    assert (research / "prompt-decomposition.json").exists()
    assert (research / "temp" / "coverage-matrix.md").exists()


def test_archive_run_force_archives_an_interrupted_run(tmp_path, monkeypatch):
    _init_vault(tmp_path)
    monkeypatch.chdir(tmp_path)
    research = _start_run(tmp_path, "efield-dft-sac-a3f9b7")

    res = runner.invoke(app, ["archive-run", "--force", "--json"])

    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    assert out["data"]["archived"] is True
    assert not (research / "scaffold.md").exists()


def test_archive_run_archives_a_finished_run(tmp_path, monkeypatch):
    """The normal case: the previous run has a final report, so it is done."""
    notes = _init_vault(tmp_path)
    monkeypatch.chdir(tmp_path)
    research = _start_run(tmp_path, "efield-dft-sac-a3f9b7")
    (notes / "final_report_efield-dft-sac-a3f9b7.md").write_text("r", encoding="utf-8")

    res = runner.invoke(app, ["archive-run", "--json"])

    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    assert out["data"]["archived"] is True
    assert not (research / "scaffold.md").exists()


def test_archive_run_only_judges_the_newest_run(tmp_path, monkeypatch):
    """An older abandoned run must not block archiving after a finished one."""
    notes = _init_vault(tmp_path)
    monkeypatch.chdir(tmp_path)
    research = tmp_path / "research"
    (research / "query-old-abandoned-000000.md").write_text("old\n", encoding="utf-8")
    _start_run(tmp_path, "newer-run-111111")
    (notes / "final_report_newer-run-111111.md").write_text("r", encoding="utf-8")

    res = runner.invoke(app, ["archive-run", "--json"])

    assert res.exit_code == 0, res.stdout
    assert json.loads(res.stdout)["data"]["archived"] is True


# ── search ────────────────────────────────────────────────────────────────────

def test_search_empty_vault_returns_empty_results(tmp_path, monkeypatch):
    _init_vault(tmp_path)
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["search", "", "--json"])
    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    assert out["data"]["results"] == []
    assert out["data"]["count"] == 0


def test_search_data_results_envelope(tmp_path, monkeypatch):
    notes = _init_vault(tmp_path)
    _write_note(notes, note_id="src-a", title="Alpha", tags=["mytag"],
                source="https://example.com/a")
    _write_note(notes, note_id="src-b", title="Beta", tags=["other"])
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["search", "", "--json"])
    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    # canonical envelope: data.results (NOT a flat notes/count)
    results = out["data"]["results"]
    assert out["data"]["count"] == 2
    ids = {r["id"] for r in results}
    assert ids == {"src-a", "src-b"}
    a = next(r for r in results if r["id"] == "src-a")
    assert a["url"] == "https://example.com/a"
    # body excluded unless --include-body
    assert "body" not in a


def test_search_tag_filter(tmp_path, monkeypatch):
    notes = _init_vault(tmp_path)
    _write_note(notes, note_id="src-a", title="Alpha", tags=["mytag"])
    _write_note(notes, note_id="src-b", title="Beta", tags=["other"])
    monkeypatch.chdir(tmp_path)
    out = json.loads(
        runner.invoke(app, ["search", "", "--tag", "mytag", "--json"]).stdout
    )
    assert [r["id"] for r in out["data"]["results"]] == ["src-a"]


def test_search_type_filter(tmp_path, monkeypatch):
    notes = _init_vault(tmp_path)
    _write_note(notes, note_id="src-a", title="Alpha", tags=["t"], note_type="interim")
    _write_note(notes, note_id="src-b", title="Beta", tags=["t"], note_type="note")
    monkeypatch.chdir(tmp_path)
    out = json.loads(
        runner.invoke(app, ["search", "", "--type", "interim", "--json"]).stdout
    )
    assert [r["id"] for r in out["data"]["results"]] == ["src-a"]
    assert out["data"]["results"][0]["type"] == "interim"


def test_search_include_body(tmp_path, monkeypatch):
    notes = _init_vault(tmp_path)
    _write_note(notes, note_id="src-a", title="Alpha", tags=["t"],
                body="Perovskite tandem cells reached 33.9% efficiency.")
    monkeypatch.chdir(tmp_path)
    out = json.loads(
        runner.invoke(app, ["search", "", "--include-body", "--json"]).stdout
    )
    r = out["data"]["results"][0]
    assert "body" in r
    assert "Perovskite" in r["body"]
    # body is frontmatter-stripped
    assert "title:" not in r["body"]


def test_search_query_scores_body(tmp_path, monkeypatch):
    notes = _init_vault(tmp_path)
    _write_note(notes, note_id="src-a", title="Alpha", tags=["t"],
                body="quantum computing breakthrough")
    _write_note(notes, note_id="src-b", title="Beta", tags=["t"],
                body="ordinary classical note")
    monkeypatch.chdir(tmp_path)
    out = json.loads(
        runner.invoke(app, ["search", "quantum", "--json"]).stdout
    )
    # the matching note ranks first
    assert out["data"]["results"][0]["id"] == "src-a"


# ── lint ──────────────────────────────────────────────────────────────────────

def test_lint_unknown_rule_exits_nonzero(tmp_path, monkeypatch):
    _init_vault(tmp_path)
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["lint", "--rule", "nonsense", "--json"])
    assert res.exit_code == 1
    out = json.loads(res.stdout)
    assert out["error_code"] == "UNKNOWN_RULE"


def test_lint_scaffold_prompt_error_exits_nonzero(tmp_path, monkeypatch):
    _init_vault(tmp_path)
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["lint", "--rule", "scaffold-prompt", "--json"])
    assert res.exit_code == 1
    out = json.loads(res.stdout)
    assert out["ok"] is False
    issues = out["data"]["issues"]
    assert any(i["rule"] == "scaffold-prompt" and i["severity"] == "error" for i in issues)


def test_lint_wrapper_report_missing_report_errors(tmp_path, monkeypatch):
    _init_vault(tmp_path)
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["lint", "--rule", "wrapper-report", "--json"])
    assert res.exit_code == 1
    out = json.loads(res.stdout)
    assert any(i["rule"] == "wrapper-report" for i in out["data"]["issues"])


def test_lint_all_rules_names_present(tmp_path, monkeypatch):
    # On a vault with a clean report present + loci/patch absent (info), all four
    # rule names appear in rules_run and no error fires → exit 0.
    notes = _init_vault(tmp_path)
    (tmp_path / "research" / "scaffold.md").write_text(
        "## User Prompt\n\nResearch the thing.\n", encoding="utf-8"
    )
    (notes / "final_report_topic-abc123.md").write_text(
        "# Report\n\nA claim with a citation [1].\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["lint", "--json"])
    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    assert out["ok"] is True
    assert out["data"]["rules_run"] == [
        "wrapper-report", "locus-coverage", "scaffold-prompt", "patch-surgery",
    ]


def test_lint_locus_coverage_flags_missing_locus(tmp_path, monkeypatch):
    notes = _init_vault(tmp_path)
    research = tmp_path / "research"
    (research / "scaffold.md").write_text(
        "## User Prompt\n\nResearch.\n", encoding="utf-8"
    )
    (research / "loci.json").write_text(
        json.dumps([{"id": "locus-uncovered"}]), encoding="utf-8"
    )
    (notes / "final_report_t-1.md").write_text(
        "# Report\n\nNothing about that topic [1].\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["lint", "--rule", "locus-coverage", "--json"])
    # warning, not error → exit 0
    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    assert any("locus-uncovered" in i["message"] for i in out["data"]["issues"])


def test_lint_patch_surgery_invalid_json_errors(tmp_path, monkeypatch):
    _init_vault(tmp_path)
    (tmp_path / "research" / "patch-log.json").write_text("{not json", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["lint", "--rule", "patch-surgery", "--json"])
    assert res.exit_code == 1
    out = json.loads(res.stdout)
    assert any(i["severity"] == "error" for i in out["data"]["issues"])


def test_lint_wrapper_report_accepts_wikilink_citations(tmp_path, monkeypatch):
    # issue #20: [[note-id]] is the DEFAULT citation_style; a report carrying only
    # wikilinks (no [N]) must NOT warn "has no citation markers".
    notes = _init_vault(tmp_path)
    (notes / "final_report_topic-abc123.md").write_text(
        "# Report\n\nVietnam led the export market in 2023 [[vietnam-rice]].\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["lint", "--rule", "wrapper-report", "--json"])
    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    assert not any(
        "no citation markers" in i["message"] for i in out["data"]["issues"]
    ), out["data"]["issues"]


def test_lint_patch_surgery_accepts_canonical_schema(tmp_path, monkeypatch):
    # issue #20: the step-14 skill mandates {total_findings, applied, skipped,
    # conflicts, orchestrator_escalated} and forbids alternate schemas — the lint
    # rule must accept that shape, not only legacy hunks/patches.
    _init_vault(tmp_path)
    (tmp_path / "research" / "patch-log.json").write_text(
        json.dumps({"total_findings": 3, "applied": 2, "skipped": 1,
                    "conflicts": 0, "orchestrator_escalated": 0}),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["lint", "--rule", "patch-surgery", "--json"])
    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    assert not any(
        "lacks" in i["message"] for i in out["data"]["issues"]
    ), out["data"]["issues"]


def test_uncited_gate_resolves_file_based_wikilinks(tmp_path, monkeypatch):
    # issue #18: a corpus written straight to research/notes/*.md (no DB ingestion)
    # must not make every [[note-id]] a dangling-cite ship-block. The gate seeds
    # verified anchors from the notes dir, so a cite to a real note file resolves.
    notes = _init_vault(tmp_path)
    _write_note(notes, note_id="vietnam-rice", title="Vietnam rice", tags=["t"],
                body="Vietnam exported 7 million tonnes of rice in 2023.")
    report = tmp_path / "report.md"
    report.write_text(
        "# Report\n\nVietnam exported 7 million tonnes of rice in 2023 [[vietnam-rice]].\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(
        app, ["uncited-gate", "--report", str(report), "--vault-tag", "t", "--json"]
    )
    out = json.loads(res.stdout)
    assert not any(u["reason"] == "dangling-cite" for u in out["uncited"]), out["uncited"]
    assert res.exit_code == 0, out


# ── note show ─────────────────────────────────────────────────────────────────

def test_note_show_single_id(tmp_path, monkeypatch):
    notes = _init_vault(tmp_path)
    _write_note(notes, note_id="src-a", title="Alpha", tags=["t"],
                body="Body of alpha.")
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["note", "show", "src-a", "--json"])
    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    note_list = out["data"]["notes"]
    assert out["data"]["count"] == 1
    assert note_list[0]["id"] == "src-a"
    assert "Body of alpha." in note_list[0]["body"]


def test_note_show_multiple_ids(tmp_path, monkeypatch):
    notes = _init_vault(tmp_path)
    _write_note(notes, note_id="src-a", title="Alpha", tags=["t"], body="alpha body")
    _write_note(notes, note_id="src-b", title="Beta", tags=["t"], body="beta body")
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["note", "show", "src-a", "src-b", "--json"])
    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    assert out["data"]["count"] == 2
    ids = [n["id"] for n in out["data"]["notes"]]
    assert ids == ["src-a", "src-b"]
    assert all(n["ok"] for n in out["data"]["notes"])


def test_note_show_missing_id_exits_nonzero(tmp_path, monkeypatch):
    notes = _init_vault(tmp_path)
    _write_note(notes, note_id="src-a", title="Alpha", tags=["t"], body="alpha")
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["note", "show", "src-a", "ghost", "--json"])
    assert res.exit_code == 1
    out = json.loads(res.stdout)
    assert out["error_code"] == "NOTE_NOT_FOUND"
    # the present note is still returned alongside the missing one
    by_id = {n["id"]: n for n in out["data"]["notes"]}
    assert by_id["src-a"]["ok"] is True
    assert by_id["ghost"]["ok"] is False


def test_note_show_finds_note_in_temp_dir(tmp_path, monkeypatch):
    _init_vault(tmp_path)
    temp = tmp_path / "research" / "temp"
    (temp / "interim-1.md").write_text(
        "---\ntitle: Interim\nid: interim-1\ntype: interim\n---\n\n# Interim\nbody\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["note", "show", "interim-1", "--json"])
    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    assert out["data"]["notes"][0]["id"] == "interim-1"


# ── entry points / registration ───────────────────────────────────────────────

def test_all_vault_commands_registered():
    for cmd in ("init", "vault-tag", "archive-run", "search", "lint"):
        res = runner.invoke(app, [cmd, "--help"])
        assert res.exit_code == 0, cmd
    for sub in ("show", "new", "update"):
        assert runner.invoke(app, ["note", sub, "--help"]).exit_code == 0, sub


# ── note new / note update (issue #11/#16: programmatic grounding + curation) ───

def test_note_new_creates_note_with_frontmatter(tmp_path, monkeypatch):
    _init_vault(tmp_path)
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, [
        "note", "new", "Vietnam Rice 2023",
        "--tag", "rice", "--type", "interim",
        "--body", "Vietnam exported 7 million tonnes of rice.",
        "--summary", "rice exports", "--json",
    ])
    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    nid = out["data"]["note_id"]
    assert nid == "vietnam-rice-2023"
    # round-trips through note show
    show = runner.invoke(app, ["note", "show", nid, "--json"])
    note = json.loads(show.stdout)["data"]["notes"][0]
    assert "Vietnam exported 7 million tonnes" in note["body"]
    assert note["tags"] == ["rice"]
    assert note["type"] == "interim"


def test_note_new_body_file(tmp_path, monkeypatch):
    _init_vault(tmp_path)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "body.md").write_text("Body loaded from a file.", encoding="utf-8")
    res = runner.invoke(app, [
        "note", "new", "From File", "--tag", "t",
        "--body-file", str(tmp_path / "body.md"), "--json",
    ])
    assert res.exit_code == 0, res.stdout
    nid = json.loads(res.stdout)["data"]["note_id"]
    show = runner.invoke(app, ["note", "show", nid, "--json"])
    assert "Body loaded from a file." in json.loads(show.stdout)["data"]["notes"][0]["body"]


def test_note_update_patches_frontmatter_keeps_body(tmp_path, monkeypatch):
    notes = _init_vault(tmp_path)
    _write_note(notes, note_id="src-a", title="Alpha", tags=["t"], body="Original body kept.")
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, [
        "note", "update", "src-a",
        "--summary", "a tight summary", "--add-tag", "extra",
        "--status", "review", "--json",
    ])
    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)["data"]
    assert out["status"] == "review"
    assert set(out["tags"]) == {"t", "extra"}
    assert out["summary"] == "a tight summary"
    # body untouched
    show = runner.invoke(app, ["note", "show", "src-a", "--json"])
    note = json.loads(show.stdout)["data"]["notes"][0]
    assert "Original body kept." in note["body"]
    assert note["status"] == "review"


def test_note_update_missing_note_exits_nonzero(tmp_path, monkeypatch):
    _init_vault(tmp_path)
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["note", "update", "ghost", "--status", "review", "--json"])
    assert res.exit_code == 1
    assert json.loads(res.stdout)["error_code"] == "NOTE_NOT_FOUND"
