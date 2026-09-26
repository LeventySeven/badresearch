"""Shape guards for `skills/bad-research/SKILL.md` — the rebuilt research skill.

Three of these encode findings that cost real money to learn, so they are checks
rather than conventions:

* **Size.** The skill must stay inside the per-skill compaction head. The thing it
  replaced was a 411-line, 36,983-char entry file that was almost entirely a
  dispatch table for a mechanism that never fired.
* **Description budget.** A skill's `description` is its routing signal, and the
  listing is *shortened* when the budget overflows — measured live on this machine
  at 40,139 chars across 109 personal skills. A dropped description reads as a
  skill that does not work, which is indistinguishable from the bug this rebuild
  exists to fix, so the budget is asserted rather than hoped for.
* **Named commands resolve.** The predecessor shipped a CLAUDE.md block naming a
  `/hyperresearch` slash command and sixteen `hyperresearch-N-*` step skills that
  have never existed. A guard was added afterwards (`tests/test_core/
  test_agent_docs_commands.py`) — but it pinned only the *CLI* names, and the same
  failure class recurred in the dimension nobody asserted. This test closes that
  dimension for the new skill: every `bad <cmd>` it names is checked against the
  live Typer app.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from bad_research.cli import app

SKILL = Path(__file__).resolve().parents[2] / "skills" / "bad-research" / "SKILL.md"

MAX_LINES = 360          # Anthropic's own guidance: keep SKILL.md under 500 lines.
                         # Moved twice, each time for a NAMED capability rather than for
                         # prose that would not fit:
                         #   250 -> 300  the adversarial pass over a finished draft, which
                         #               is the one thing a 4,592-line predecessor beat
                         #               this skill on, blind-judged.
                         #   300 -> 360  diagnosticity (name the rivals, delete evidence
                         #               that cannot separate them) — 4 independent
                         #               primaries, 2 from outside the AI industry, and a
                         #               zero verified 7 ways in the skill; plus the
                         #               confidence/accuracy decoupling that is the
                         #               counterweight to "reach is the largest lever".
                         # The cap is not a line budget. It guards against the specific
                         # thing the 411-line predecessor was: a dispatch table for a
                         # mechanism that never fired. `test_the_skill_is_not_a_chain`
                         # is the real guard; this number is the coarse one.
MAX_DESCRIPTION = 500    # well inside the documented 1,536-char per-skill cap, because
                         # the binding constraint here is the SHARED listing budget.


def _frontmatter() -> str:
    m = re.search(r"\A---\n(.*?)\n---", SKILL.read_text(encoding="utf-8"), re.S)
    assert m, "SKILL.md must open with a YAML frontmatter block"
    return m.group(1)


def _field(name: str) -> str:
    m = re.search(rf"^{name}:\s*(.*?)(?=^\w[\w-]*:|\Z)", _frontmatter(), re.S | re.M)
    assert m, f"frontmatter is missing `{name}:`"
    return m.group(1).strip()


def test_skill_file_exists():
    assert SKILL.is_file(), f"expected the research skill at {SKILL}"


def _body() -> str:
    """The prose after the frontmatter. The cap is on the BODY, per this test's name.

    It used to count the whole file, which meant folding the `description` into a valid
    YAML block scalar — a correctness fix, since the description contains an unquoted
    `: ` and failed strict parsing — read as +4 lines of bloat. Metadata is not detail
    that could "move into references/", so counting it measured the wrong thing. The
    NUMBER did not move; what it measures was corrected.
    """
    text = SKILL.read_text(encoding="utf-8")
    parts = text.split("---\n", 2)
    return parts[2] if len(parts) == 3 else text


def test_body_stays_within_the_compaction_head():
    n = len(_body().splitlines())
    assert n <= MAX_LINES, (
        f"SKILL.md is {n} lines (cap {MAX_LINES}). Past this it stops being a skill and "
        "starts being the dispatch table it replaced — move detail into references/."
    )


def test_description_stays_inside_the_shared_listing_budget():
    d = _field("description")
    assert d, "description must not be empty — it is the routing signal"
    assert len(d) <= MAX_DESCRIPTION, (
        f"description is {len(d)} chars (cap {MAX_DESCRIPTION}). The listing is shortened "
        "when the shared budget overflows, and a dropped description reads as a skill "
        "that does not work."
    )


def test_description_describes_the_user_request_not_the_skill():
    """Routing signals are matched against what the user asked, not what the skill is."""
    d = _field("description").lower()
    assert "use when" in d or "answer" in d, (
        "the description should say when to reach for this, in the user's terms"
    )


def test_every_bad_command_it_names_resolves_against_the_live_cli():
    real = {c.name or (c.callback.__name__ if c.callback else "") for c in app.registered_commands}
    real |= {g.name for g in app.registered_groups}
    # The backtick/code-fence context is REQUIRED, not optional. The old pattern made it
    # optional and so matched the English word: prose reading "base rate, not bad luck"
    # was reported as a missing CLI command `bad luck`. That is the check mis-reading its
    # input, not a real dead name — a documented command always appears in backticks or a
    # fenced block. Narrowed to those two contexts; the planted-defect test below proves
    # it still catches a name that genuinely does not resolve.
    body = SKILL.read_text(encoding="utf-8")
    fenced = "\n".join(re.findall(r"^```bash\n(.*?)^```", body, re.S | re.M))
    inline = "\n".join(re.findall(r"`(bad [a-z][a-z0-9 -]*)`", body))
    named = set(re.findall(r"(?:^|\s)bad ([a-z][a-z-]+)", fenced + "\n" + inline, re.M))
    missing = named - real
    assert not missing, (
        f"SKILL.md names commands that do not exist: {sorted(missing)}. "
        "This is the exact failure class that shipped a /hyperresearch roster into five "
        "real projects — a documented name that cannot resolve."
    )


def test_every_referenced_lane_file_exists():
    """A lane pointer that resolves to nothing is a lane that silently never runs."""
    body = SKILL.read_text(encoding="utf-8")
    refs = set(re.findall(r"`(references/[\w/\-]+\.md)`", body))
    assert refs, "the skill should point at its lane recipes by relative path"
    missing = [r for r in sorted(refs) if not (SKILL.parent / r).is_file()]
    assert not missing, f"SKILL.md references files that do not exist: {missing}"


@pytest.mark.parametrize(
    "phrase",
    [
        "frontier",              # the loop's one mechanism
        "Captions are substance",  # the quotation rule that has already been violated once
        "silver",                # the browser constraint, non-negotiable
        "not in corpus",         # abstention as a first-class output
    ],
)
def test_load_bearing_rules_survive_edits(phrase: str):
    """These are not style. Each one is here because its absence produced a wrong answer."""
    assert phrase.lower() in SKILL.read_text(encoding="utf-8").lower(), (
        f"SKILL.md no longer carries {phrase!r} — that rule was removed, not refactored."
    )


def test_every_script_the_skill_tells_you_to_run_ships_with_it():
    """Found by COLD USE, not by audit: an arm following SKILL.md hit a dead path.

    `test_every_command_named_in_skill_exists` covers `bad <cmd>` names and passed
    the whole time, because the hole was a different shape — a `bash scripts/...`
    line whose target lived in the REPO but not in the packaged skill. The
    installed skill had no `scripts/` directory at all, so the one command in the
    Checks block that is not a `bad` subcommand could never run for its actual
    reader.

    This is the exact defect the owner filed as "first error" — a documented name
    that cannot resolve — reintroduced inside the fix for it, and it took an
    agent actually following the file to surface it.
    """
    body = SKILL.read_text(encoding="utf-8")
    scripts = set(re.findall(r"(?:bash|sh)\s+(scripts/[\w./-]+)", body))
    assert scripts, "the Checks block should still name at least one runnable script"
    missing = [s for s in sorted(scripts) if not (SKILL.parent / s).is_file()]
    assert not missing, (
        f"SKILL.md tells its reader to run {missing}, which does not ship inside the "
        f"skill directory ({SKILL.parent}). A path that resolves only from the repo "
        "root is a dead name for everyone who installed the skill."
    )


def test_the_command_check_still_catches_a_name_that_does_not_resolve():
    """Red-first proof that narrowing the pattern did not neuter the check.

    The pattern was narrowed because it read the English word "bad" in prose as a CLI
    name ("base rate, not bad luck" -> a missing command `bad luck`). Narrowing a check
    to stop it mis-firing is only legitimate if it still fires on the real thing, so this
    plants one and watches it go red.
    """
    import subprocess
    body = SKILL.read_text(encoding="utf-8")
    planted = body.replace("bad lane-local", "bad definitely-not-a-command", 1)
    fenced = "\n".join(re.findall(r"^```bash\n(.*?)^```", planted, re.S | re.M))
    inline = "\n".join(re.findall(r"`(bad [a-z][a-z0-9 -]*)`", planted))
    named = set(re.findall(r"(?:^|\s)bad ([a-z][a-z-]+)", fenced + "\n" + inline, re.M))
    assert "definitely-not-a-command" in named, "the narrowed pattern no longer sees commands at all"
    bad = SKILL.parents[2] / ".venv" / "bin" / "bad"
    rc = subprocess.run([str(bad), "definitely-not-a-command", "--help"],
                        capture_output=True).returncode
    assert rc != 0, "fixture is wrong: that command should not exist"


def test_the_skill_is_not_a_chain():
    """No step numbers, no Skill() dispatch — the refusal, in executable form.

    The predecessor was a 19-stage chain: an entry file that sequenced 21 step skills by
    number, each invoked with `Skill(skill: "bad-research-N-...")`. Its stated purpose was
    to reload each procedure fresh so a long run could not silently degrade — a property
    the on-demand `references/` layout already has, in a fifth of the lines.

    This is a test rather than a sentence because the failure mode is gradual: one
    numbered step is a clarification, three are a pipeline, and by then the skill has
    stopped being a judgment about the question and become a form to complete.
    """
    body = SKILL.read_text(encoding="utf-8")
    # The refusals section quotes the predecessor's shape in order to refuse it, so it is
    # exempt — but ONLY it. This used to exempt everything from that heading to the end of
    # the file, which left the closing sections unguarded: a planted eight-stage pipeline
    # appended to the file passed this test cleanly. Cut out the refusals block and check
    # everything on both sides of it.
    before, sep, rest = body.partition("## What this skill refuses")
    after = rest.partition("## The answer")[2] if sep else ""
    head = before + "\n" + after
    for pattern, what in (
        (r"Skill\(skill:", "a Skill() dispatch call"),
        (r"^\s*\|?\s*(?:Step\s+)?\d+(?:\.\d+)?\s*\|\s*`?bad-research-", "a numbered step table row"),
        (r"\bstep \d+(?:\.\d+)? →", "a step arrow"),
        # Ordinal PROSE, which is how a chain grows back without ever naming a step
        # skill. A Reckon restored an eight-stage pipeline into this file using nothing
        # but these words, and the guard above stayed green because it only knew the old
        # chain's vocabulary. One numbered stage is a clarification; three are a pipeline.
        (r"^#{2,3}\s+(?:Stage|Phase|Step)\s+\d", "a numbered stage heading"),
        (r"\b(?:Stage|Phase)\s+\d+\s*(?:->|→)", "a stage arrow"),
        (r"\bin this exact order\b", "an imposed execution order"),
        (r"\bdo not skip (?:a|any) (?:stage|step|phase)\b", "a do-not-skip rule"),
    ):
        m = re.search(pattern, head, re.M)
        assert not m, f"SKILL.md has {what}: {m.group(0)!r} — the chain is coming back"


def test_the_five_refusals_are_stated_with_reasons():
    """A rule dropped silently comes back. These five were MUSTs in the predecessor.

    Each is refused by name because each is refutable-sounding-but-wrong in a way that
    reads as rigour: a quota on disagreements manufactures them, a reader forced to
    conclude returns opinions, a mandatory ensemble fans out judgment, and a word floor
    makes padding mandatory.

    The third needle was "17.2" until 2026-09-26. That figure (Kim et al., arXiv
    2512.08296) turned out, read in the primary, to be trace-level amplification that is
    not significant after controls, and the refusal built on it had banned parallel depth
    outright. The refusal now names the two shapes the evidence does refuse -- parallel
    readers that NEVER EXCHANGE (-35% vs one agent on the paper's web-research benchmark)
    and free, continuous sharing (it herded >90% of 533 agents onto one workstream) -- so
    the needle follows the idea, not the number that was misread.
    """
    body = SKILL.read_text(encoding="utf-8")
    _, sep, refusals = body.partition("## What this skill refuses")
    assert sep, "SKILL.md must carry a `## What this skill refuses` section"
    # Normalise the wrap: these are prose paragraphs, so a phrase the section genuinely
    # carries can sit across a line break. The assertion is about the idea being named,
    # never about where the wrap fell — a first version failed on "never\n  concludes"
    # and would have been "fixed" by editing the skill to satisfy the test.
    refusals = " ".join(refusals.partition("## The answer")[0].split())
    for needle in ("quota", "never concludes", "never exchange", "ensemble", "Word floors"):
        assert needle in refusals, f"the refusals section no longer names {needle!r}"
