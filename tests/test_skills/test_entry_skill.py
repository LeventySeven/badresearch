from tests.test_skills.validate import validate_skill


def test_entry_skill_valid(skills_dir, known_skills):
    p = skills_dir / "bad-research.md"
    assert p.exists()
    assert validate_skill(p, known_skills) == []


def test_entry_skill_has_two_route_sequences(skills_dir):
    body = (skills_dir / "bad-research.md").read_text()
    for route in ("fast", "full"):
        assert route in body
    assert "bad-research-0.5-clarify" in body
    assert "bad-research-query-router" in body
    assert "bad-research-fast" in body
    assert "bad-research-11.5-citation-verifier" in body
    assert "bad-research-fresh-review" in body
    # lazy step-skill install on first invocation
    assert "bad install --steps-only" in body
    # the deterministic ship gate
    assert "uncited" in body.lower()


def test_entry_skill_bootstrap_uses_bad_not_bare_hyperresearch(skills_dir):
    # issue #12: the bootstrap called bare `hyperresearch archive-run` / `vault-tag`,
    # which exits 127 on a uv-tool install where only `bad` is on PATH. The whole
    # skill must invoke the CLI as `bad …` consistently (the installer also documents
    # the absolute path in CLAUDE.md for the not-on-PATH case).
    import re
    body = (skills_dir / "bad-research.md").read_text()
    bare = re.findall(r"hyperresearch [a-z][a-z-]+", body)
    assert bare == [], f"entry skill invokes bare `hyperresearch <cmd>` (use `bad`): {bare}"
    # the bootstrap names the real commands via `bad`
    assert "bad archive-run" in body
    assert "bad vault-tag" in body


def test_no_step_skill_leaks_stale_cli_name_or_template_var(skills_dir):
    """Every step-skill .md is installed VERBATIM (hooks._install_bad_research_step_skills
    write_texts the raw source — no .format/.replace). So a bare `hyperresearch <cmd>` or an
    un-substituted `{hpr_path}` in ANY step skill reaches the model literally: a subagent that
    copies it runs a nonexistent binary. The entry-skill-only guard (issue #12) missed leaks
    in depth-investigation / corpus-critic — this covers the whole skill set."""
    import re

    offenders: dict[str, list[str]] = {}
    for p in sorted(skills_dir.glob("bad-research*.md")):
        body = p.read_text(encoding="utf-8")
        bad = re.findall(r"hyperresearch [a-z][a-z-]+", body)
        if "{hpr_path}" in body:
            bad.append("{hpr_path}")
        if bad:
            offenders[p.name] = bad
    assert offenders == {}, f"step skills leak stale CLI name / template var (use `bad`): {offenders}"


def test_no_skill_doc_invokes_undefined_HPR_variable(skills_dir):
    # issue #25: step skills invoked `$HPR …` (e.g. `$HPR lint`, `$HPR note show`)
    # across 11 files, but $HPR is never exported — only `bad` is on PATH, so the
    # var expands to "" and the command silently runs as `lint …` and fails. Every
    # skill doc must invoke the CLI as `bad …` (the absolute-path fallback for the
    # not-on-PATH case is documented separately in the entry skill).
    offenders = {
        p.name: p.read_text().count("$HPR")
        for p in skills_dir.glob("*.md")
        if "$HPR" in p.read_text()
    }
    assert offenders == {}, f"skill docs still invoke undefined $HPR: {offenders}"


def test_entry_skill_documents_unknown_skill_read_fallback(skills_dir):
    # The step skills are installed mid-session by `bad install --steps-only`; the host's
    # Skill registry is loaded at session start, so `Skill(skill: "bad-research-0.5-clarify")`
    # can return "Unknown skill" on the install run. The entry skill MUST document the
    # read-the-file recovery path so the orchestrator doesn't abort the pipeline.
    body = (skills_dir / "bad-research.md").read_text()
    low = body.lower()
    assert "unknown skill" in low, "entry skill must name the `Unknown skill` failure mode"
    # the recovery: Read the installed SKILL.md directly
    assert ".claude/skills/bad-research-" in body
    assert "skill.md" in low
    assert "read" in low
