"""S4-3: one adjudicator, one rubric, and an isolation enforced by the allowlist.

Two failures this pins down, and they pull in opposite directions.

**The judge must not reach the author's context.** A control agent in a prior
eval found the harness it was supposed to be blind to by walking its own output
directory — nobody granted it that, it simply had the tools to look. So the
isolation cannot live in the prompt: an instruction not to look is worth
whatever the agent's curiosity is worth that run, while a tool it does not have
is worth exactly what it says. `Grep` and `Glob` are the specific escape
hatches, because a Read-only agent with either can enumerate the whole repo and
reconstruct the reasoning it was meant never to see.

**The judge must not certify.** On long-form attribution every published
groundedness judge lands between 55 and 60 balanced accuracy, on a scale where
50 is chance. An instrument that weak can usefully RANK what a human or a
deterministic check should look at first; it cannot pronounce work correct, and
a design that lets it emit a verdict will have that verdict quoted as one.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ADJ = Path(__file__).resolve().parents[2] / "agents" / "research-adjudicator.md"


def _frontmatter(p: Path) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---\n", p.read_text(encoding="utf-8"), re.S)
    assert m, f"{p.name} has no YAML frontmatter"
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def test_the_adjudicator_exists_as_a_spawnable_agent():
    assert ADJ.is_file(), "S4-3 names an adjudicator; a rubric with no agent is a document"


def test_the_allowlist_is_exactly_read():
    """Isolation by capability, not by request."""
    tools = {t.strip() for t in _frontmatter(ADJ)["tools"].split(",")}
    assert tools == {"Read"}, f"adjudicator grants {sorted(tools)}; it may hold only Read"


@pytest.mark.parametrize("escape", ["Grep", "Glob", "Bash", "WebFetch", "WebSearch", "Task", "Agent"])
def test_the_named_escape_hatches_are_absent(escape: str):
    """Each of these lets a 'read-only' judge enumerate its way to the author's context."""
    assert escape not in _frontmatter(ADJ)["tools"]


def test_it_ranks_and_is_forbidden_from_certifying():
    body = ADJ.read_text(encoding="utf-8").lower()
    assert "rank" in body
    assert "55" in body and "60" in body, "the BAcc ceiling is the REASON; state it, don't assert the rule bare"
    assert re.search(r"(never|not|refuse)[^.]{0,80}(certif|verdict|pass/fail|approve)", body), (
        "the agent must be told in words that it cannot certify correctness"
    )


def test_there_is_exactly_one_rubric():
    """A panel of rubrics is a panel of judges wearing one name — and averaging
    three ~60-BAcc instruments buys agreement, not accuracy."""
    body = ADJ.read_text(encoding="utf-8")
    assert len(re.findall(r"^## .*[Rr]ubric", body, re.M)) == 1


def test_it_reads_only_the_artifact_it_is_handed():
    body = ADJ.read_text(encoding="utf-8").lower()
    assert "only the artifact" in body or "only the file you are given" in body
