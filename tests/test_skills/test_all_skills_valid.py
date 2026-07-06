import re

from tests.test_skills.validate import validate_skill


def test_every_skill_validates(skills_dir, known_skills):
    errors = []
    for p in sorted(skills_dir.glob("bad-research*.md")):
        errors += validate_skill(p, known_skills)
    assert errors == [], "\n".join(errors)


def test_every_step_skill_in_roster_has_a_file(skills_dir):
    from bad_research.core.hooks import _BAD_RESEARCH_STEP_SKILLS

    for name in _BAD_RESEARCH_STEP_SKILLS:
        assert (skills_dir / f"{name}.md").exists(), f"missing skill file for {name}"


def test_step_skill_roster_is_exactly_19_full_tier_stages():
    """The full-tier stage roster must contain exactly 19 invocable stages (excludes
    bad-research-fast, which is its own route, not a full-tier step). The real roster
    is 20 entries; 20 - fast = 19.

    History: after the C-1/C-2/C-3 merges this was 18 (roster of 20 incl. ultrafast).
    The audit (2026-06-01) found bad-research-12.5-grader was invoked by the entry
    skill on every full run but missing from the install roster, so the grader loop
    never ran — adding it brought the full-tier count to 19. The `ultrafast` route
    skill was folded away 2026-07-06 (its breadth need lands on the `fast` route),
    dropping the roster from 21 to 20 while the full-tier count stays 19.
    """
    from bad_research.core.hooks import _BAD_RESEARCH_STEP_SKILLS

    full_tier_steps = [s for s in _BAD_RESEARCH_STEP_SKILLS
                       if s != "bad-research-fast"]
    removed = {
        "bad-research-3-contradiction-graph",
        "bad-research-7-source-tensions",
        "bad-research-9-evidence-digest",
    }
    for name in removed:
        assert name not in full_tier_steps, f"{name} must be removed (C-1/C-2/C-3)"
    assert "bad-research-12.5-grader" in full_tier_steps, \
        "the grader stage must be in the install roster (audit 2026-06-01 fix)"
    assert len(full_tier_steps) == 19, \
        f"Expected 19 full-tier stages, got {len(full_tier_steps)}: {full_tier_steps}"


def test_entry_skill_critic_count_matches_step12(skills_dir):
    """Guard against critic-count drift (audit 2026-06-01): the full tier runs 5
    critics including the assumption critic. The entry skill's prose + integrity gate
    must reflect all 5, not a stale 4, and the step-12 skill must actually produce the
    5th critic's findings."""
    entry = (skills_dir / "bad-research.md").read_text(encoding="utf-8")
    assert "critic-findings-assumption.json" in entry, \
        "entry skill must reference the 5th (assumption) critic's findings"
    assert "4 adversarial critics" not in entry, "stale '4 adversarial critics' wording"
    assert "4-critic fan-out" not in entry, "stale '4-critic fan-out' wording"
    critics = (skills_dir / "bad-research-12-critics.md").read_text(encoding="utf-8")
    assert "critic-findings-assumption.json" in critics, \
        "step-12 critics skill must produce the assumption critic's findings"


def test_entry_skill_skill_targets_are_all_installed(skills_dir):
    """Guard against the grader-install-gap class of bug (audit 2026-06-01): every
    concrete Skill(skill: "bad-research-...") target the entry orchestrator invokes
    MUST be in the install roster, or a real run hits an unresolvable skill. Template
    placeholders (bad-research-N-...) are excluded."""
    from bad_research.core.hooks import _BAD_RESEARCH_STEP_SKILLS

    entry = (skills_dir / "bad-research.md").read_text(encoding="utf-8")
    targets = set(re.findall(r'Skill\(skill:\s*"(bad-research-[^"]+)"', entry))
    targets = {t for t in targets if not t.startswith("bad-research-N-")}
    assert targets, "entry skill should invoke at least one concrete Skill() target"
    roster = set(_BAD_RESEARCH_STEP_SKILLS)
    missing = sorted(t for t in targets if t not in roster)
    assert not missing, \
        f"entry skill invokes Skill() targets absent from the install roster: {missing}"
