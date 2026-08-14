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


def test_prune_removes_retired_step_skills_too(tmp_path):
    """A RETIRED step skill is the stalest thing on disk and must be prunable.

    Found in the wild: 7 projects still carried `bad-research-ultrafast` weeks
    after the route was folded into `fast`. Because exact-roster matching is the
    safety property, a name dropped FROM the roster became unreachable — the
    prune reported success while leaving the worst drift in place.
    """
    from bad_research.core.hooks import (
        _BAD_RESEARCH_STEP_SKILLS,
        _RETIRED_STEP_SKILLS,
        _prune_project_step_skills,
    )

    skills = tmp_path / ".claude" / "skills"
    skills.mkdir(parents=True)
    for name in _RETIRED_STEP_SKILLS:
        (skills / name).mkdir()
        (skills / name / "SKILL.md").write_text("stale", encoding="utf-8")
    # The three things that must still survive alongside it.
    for survivor in ("bad-research", "bad-research-notes", "my-skill"):
        (skills / survivor).mkdir()
        (skills / survivor / "SKILL.md").write_text("keep", encoding="utf-8")

    _prune_project_step_skills(tmp_path)

    for name in _RETIRED_STEP_SKILLS:
        assert not (skills / name).exists(), f"retired {name} survived the prune"
    for survivor in ("bad-research", "bad-research-notes", "my-skill"):
        assert (skills / survivor / "SKILL.md").exists(), f"{survivor} was destroyed"

    # A retired name must never also sit in the live roster — that would mean a
    # skill we still install is listed as removable.
    assert not (_RETIRED_STEP_SKILLS & set(_BAD_RESEARCH_STEP_SKILLS))


# --- the INSTALLER's own prune: same survivor guarantee as the pruner --------
# `_install_bad_research_step_skills` sweeps stale dirs as a side effect of
# every `bad install --project` / `--steps-only`. It is the third pruner in
# this file and it must share the other two's notion of "ours to delete".


def test_install_never_deletes_a_user_skill_sharing_our_prefix(tmp_path):
    """`bad install` must not eat a user skill just because it is `bad-research-*`.

    The survivor guarantee `_is_step_skill_dir_name` documents ("`bad-research-notes`
    is a perfectly plausible personal skill") is worthless if the installer's own
    sweep deletes by prefix glob on every single install.
    """
    from bad_research.core.hooks import _install_bad_research_step_skills

    root = tmp_path / "proj"
    skills = root / ".claude" / "skills"
    skills.mkdir(parents=True)
    for name in ("bad-research-notes", "bad-research-mything", "hyperresearch-notes"):
        (skills / name).mkdir()
        (skills / name / "SKILL.md").write_text(f"# {name}\nmine\n", encoding="utf-8")

    _install_bad_research_step_skills(root)

    for name in ("bad-research-notes", "bad-research-mything", "hyperresearch-notes"):
        assert (skills / name / "SKILL.md").read_text(encoding="utf-8") == (
            f"# {name}\nmine\n"
        ), f"install destroyed the user's own {name}"


def test_install_still_prunes_retired_and_legacy_step_dirs(tmp_path):
    """Closing the glob must not cost the stale-dir cleanup it was there for."""
    from bad_research.core.hooks import (
        _RETIRED_STEP_SKILLS,
        _install_bad_research_step_skills,
    )

    root = tmp_path / "proj"
    skills = root / ".claude" / "skills"
    skills.mkdir(parents=True)
    stale = [*_RETIRED_STEP_SKILLS, "hyperresearch-3-old-step"]
    for name in stale:
        (skills / name).mkdir()
        (skills / name / "SKILL.md").write_text("stale\n", encoding="utf-8")

    _install_bad_research_step_skills(root)

    for name in stale:
        assert not (skills / name).exists(), f"stale {name} survived the install sweep"


def test_install_prunes_a_stale_step_dir_holding_a_subdirectory(tmp_path):
    """A stale step dir with a nested folder must not abort the whole install.

    `_prune_step_skill_dirs` already reaches for rmtree over this exact case
    ("a step dir that picked up a nested `references/` folder would otherwise
    raise on the unlink"); the installer's sweep still runs an unlink() loop, so
    one nested dir raises PermissionError/IsADirectoryError out of `bad install`.
    """
    from bad_research.core.hooks import (
        _RETIRED_STEP_SKILLS,
        _install_bad_research_step_skills,
    )

    retired = sorted(_RETIRED_STEP_SKILLS)[0]
    root = tmp_path / "proj"
    skills = root / ".claude" / "skills"
    nested = skills / retired / "references"
    nested.mkdir(parents=True)
    (nested / "x.md").write_text("nested\n", encoding="utf-8")
    (skills / retired / "SKILL.md").write_text("stale\n", encoding="utf-8")

    _install_bad_research_step_skills(root)  # an unlink() loop raises here

    assert not (skills / retired).exists()
