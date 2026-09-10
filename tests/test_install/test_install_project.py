from bad_research.core.hooks import (
    _BAD_RESEARCH_STEP_SKILLS,
    _prune_project_step_skills,
    install_hooks,
)


def test_prune_project_step_skills_removes_roster_dirs(tmp_path):
    root = tmp_path / "proj"
    (root / ".bad-research").mkdir(parents=True)
    install_hooks(root, hpr_path="bad")
    skills = root / ".claude" / "skills"
    # Plant the chain by hand. `install_hooks` no longer creates these -- that is the
    # point of the change -- but prune must still remove what an OLDER install left, so
    # the capability under test is unchanged and only its fixture moved.
    for name in _BAD_RESEARCH_STEP_SKILLS:
        (skills / name).mkdir(parents=True, exist_ok=True)
        (skills / name / "SKILL.md").write_text("# planted", encoding="utf-8")
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


# ── the chain must not come back through the installer ────────────────────────────
#
# These replace three tests that asserted the OPPOSITE — that `bad install` writes the
# 20 numbered step skills and the chain's agents. That was the shipped behaviour and it
# is the defect the owner named as "it's first error": the revamped skill lived only at
# the repo root, the installer could not reach it, and every install reinstated the
# chain. The machine looked clean only because someone had moved the files by hand.


def test_install_ships_the_merged_skill_not_the_chain(tmp_path):
    install_hooks(tmp_path, hpr_path="bad")
    skill = tmp_path / ".claude" / "skills" / "bad-research" / "SKILL.md"
    assert skill.is_file()
    body = skill.read_text(encoding="utf-8")
    assert 'Skill(skill:' not in body, "the installer is writing a chain orchestrator again"
    assert "bad-research-1-decompose" not in body


def test_install_ships_the_skills_references_and_scripts(tmp_path):
    """A single SKILL.md is not the skill — its detail is read on demand from here."""
    install_hooks(tmp_path, hpr_path="bad")
    root = tmp_path / ".claude" / "skills" / "bad-research"
    assert (root / "references" / "critique.md").is_file()
    assert (root / "references" / "lanes" / "web-live.md").is_file()
    assert (root / "scripts" / "lane-probes.sh").is_file()


def test_install_writes_exactly_the_three_research_agents(tmp_path):
    install_hooks(tmp_path, hpr_path="bad")
    agents = sorted(p.name for p in (tmp_path / ".claude" / "agents").glob("*.md"))
    assert agents == ["research-adjudicator.md", "research-critic.md", "research-reader.md"], agents


def test_installing_over_a_previous_chain_removes_it(tmp_path):
    """An upgrade must REPLACE the chain, not sit beside it."""
    skills = tmp_path / ".claude" / "skills"
    for d in ("bad-research-1-decompose", "bad-research-12-critics"):
        (skills / d).mkdir(parents=True)
        (skills / d / "SKILL.md").write_text("# old chain step", encoding="utf-8")
    (tmp_path / ".claude" / "agents").mkdir(parents=True)
    (tmp_path / ".claude" / "agents" / "bad-research-patcher.md").write_text("x", encoding="utf-8")

    install_hooks(tmp_path, hpr_path="bad")

    assert not list(skills.glob("bad-research-*-*")), "step-skill dirs survived the upgrade"
    assert not list((tmp_path / ".claude" / "agents").glob("bad-research-*.md")), \
        "chain agents survived the upgrade"


def test_the_GLOBAL_install_ships_the_same_thing_as_the_project_install(tmp_path, monkeypatch):
    """The global path is a separate function and it was missed by the first fix.

    `install_hooks` (project) and `install_global_hooks` (user-wide) each carry their own
    installer list. Repointing only the project one looked complete — the suite went
    green — and then a real `bad install` with no flags put all seventeen chain agents
    back on the owner's profile. Two lists, one behaviour, and only one of them tested.
    """
    from bad_research.core.hooks import install_global_hooks

    home = tmp_path / "home"
    (home / ".claude" / "agents").mkdir(parents=True)
    # a chain left by an older version must not survive the upgrade
    (home / ".claude" / "agents" / "bad-research-synthesizer.md").write_text("x", encoding="utf-8")

    install_global_hooks(home, hpr_path="bad")

    skill = home / ".claude" / "skills" / "bad-research" / "SKILL.md"
    assert skill.is_file()
    assert "Skill(skill:" not in skill.read_text(encoding="utf-8")
    assert (home / ".claude" / "skills" / "bad-research" / "references" / "critique.md").is_file()

    agents = sorted(p.name for p in (home / ".claude" / "agents").glob("*.md"))
    assert agents == ["research-adjudicator.md", "research-critic.md", "research-reader.md"], agents
