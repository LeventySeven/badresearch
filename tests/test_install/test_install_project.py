from bad_research.core.hooks import (
    _BAD_RESEARCH_STEP_SKILLS,
    _prune_project_step_skills,
    install_hooks,
)


def test_project_install_drops_all_step_skills(tmp_path):
    root = tmp_path / "proj"
    (root / ".bad-research").mkdir(parents=True)  # vault marker
    install_hooks(root, hpr_path="bad")
    skills = root / ".claude" / "skills"
    assert (skills / "bad-research-1-decompose" / "SKILL.md").exists()
    assert (skills / "bad-research-fast" / "SKILL.md").exists()
    assert (skills / "bad-research" / "SKILL.md").exists()  # entry skill too


def test_project_install_includes_new_step_skills(tmp_path):
    root = tmp_path / "proj"
    (root / ".bad-research").mkdir(parents=True)
    install_hooks(root, hpr_path="bad")
    skills = root / ".claude" / "skills"
    for name in (
        "bad-research-0.5-clarify",
        "bad-research-query-router",
        "bad-research-11.5-citation-verifier",
        "bad-research-fresh-review",
    ):
        assert (skills / name / "SKILL.md").exists(), name


def test_project_install_writes_fresh_reviewer_agent(tmp_path):
    root = tmp_path / "proj"
    (root / ".bad-research").mkdir(parents=True)
    install_hooks(root, hpr_path="bad")
    assert (root / ".claude" / "agents" / "bad-research-fresh-reviewer.md").exists()


# --- issue #38: removing the per-project step-skill copies -------------------
# These are safety tests before they are feature tests: the pruner deletes
# directories under a user's .claude/skills/, so what it must NOT delete
# matters more than what it must.


def test_prune_project_step_skills_removes_roster_dirs(tmp_path):
    root = tmp_path / "proj"
    (root / ".bad-research").mkdir(parents=True)
    install_hooks(root, hpr_path="bad")
    skills = root / ".claude" / "skills"
    assert (skills / "bad-research-1-decompose").is_dir()

    result = _prune_project_step_skills(root)

    assert result is not None
    for name in _BAD_RESEARCH_STEP_SKILLS:
        assert not (skills / name).exists(), name


def test_prune_project_step_skills_keeps_entry_skill(tmp_path):
    root = tmp_path / "proj"
    (root / ".bad-research").mkdir(parents=True)
    install_hooks(root, hpr_path="bad")
    skills = root / ".claude" / "skills"

    _prune_project_step_skills(root)

    # `.claude/skills/bad-research/` (no trailing dash) is the /bad-research
    # entry point, never a step skill.
    assert (skills / "bad-research" / "SKILL.md").exists()


def test_prune_project_step_skills_never_touches_unrelated_skills(tmp_path):
    root = tmp_path / "proj"
    (root / ".bad-research").mkdir(parents=True)
    install_hooks(root, hpr_path="bad")
    skills = root / ".claude" / "skills"

    # An unrelated user skill, and a lookalike that a prefix glob would eat.
    for name in ("my-skill", "bad-research-notes", "hyperresearch-notes"):
        (skills / name).mkdir(parents=True, exist_ok=True)
        (skills / name / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")

    _prune_project_step_skills(root)

    for name in ("my-skill", "bad-research-notes", "hyperresearch-notes"):
        assert (skills / name / "SKILL.md").exists(), name


def test_prune_project_step_skills_removes_legacy_numbered_dirs(tmp_path):
    root = tmp_path / "proj"
    skills = root / ".claude" / "skills"
    (skills / "hyperresearch-3-old-step").mkdir(parents=True)
    (skills / "hyperresearch-3-old-step" / "SKILL.md").write_text("x\n", encoding="utf-8")

    _prune_project_step_skills(root)

    assert not (skills / "hyperresearch-3-old-step").exists()


def test_prune_project_step_skills_survives_nested_files(tmp_path):
    root = tmp_path / "proj"
    (root / ".bad-research").mkdir(parents=True)
    install_hooks(root, hpr_path="bad")
    skills = root / ".claude" / "skills"
    nested = skills / "bad-research-1-decompose" / "references"
    nested.mkdir(parents=True)
    (nested / "x.md").write_text("nested\n", encoding="utf-8")

    _prune_project_step_skills(root)  # an unlink() loop would raise here

    assert not (skills / "bad-research-1-decompose").exists()


def test_prune_project_step_skills_is_a_noop_without_skills_dir(tmp_path):
    root = tmp_path / "proj"
    root.mkdir()
    assert _prune_project_step_skills(root) is None
