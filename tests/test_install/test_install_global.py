import json

from bad_research.core.hooks import install_global_hooks


def test_global_install_drops_entry_skill(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    install_global_hooks(home, hpr_path="bad")
    # entry skill lands at ~/.claude/skills/bad-research/SKILL.md
    entry = home / ".claude" / "skills" / "bad-research" / "SKILL.md"
    assert entry.exists()
    assert "name: bad-research" in entry.read_text(encoding="utf-8")


def test_global_install_drops_agents(tmp_path):
    """Was: assert the chain's fresh-reviewer and synthesizer land. They must not — the
    chain is gone, and its workers would resolve to a pipeline nothing invokes."""
    home = tmp_path / "home"
    home.mkdir()
    install_global_hooks(home, hpr_path="bad")
    agents = home / ".claude" / "agents"
    assert sorted(p.name for p in agents.glob("*.md")) == [
        "research-adjudicator.md", "research-critic.md", "research-reader.md"
    ]


def test_global_install_skips_step_skills(tmp_path):
    # step skills must NOT install globally (system-reminder bloat) — lazy per-project
    home = tmp_path / "home"
    home.mkdir()
    install_global_hooks(home, hpr_path="bad")
    assert not (home / ".claude" / "skills" / "bad-research-1-decompose").exists()


def test_global_install_writes_pretooluse_hook(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    install_global_hooks(home, hpr_path="bad")
    settings = home / ".claude" / "settings.json"
    assert settings.exists()
    data = json.loads(settings.read_text(encoding="utf-8"))
    cmds = [h["command"] for entry in data["hooks"]["PreToolUse"] for h in entry["hooks"]]
    assert any("bad-research" in c for c in cmds)


def test_global_install_read_only_judge_is_tool_locked(tmp_path):
    """The tool-lock still matters; it moved to the agent that still exists.

    A judge holding Grep/Glob can walk the output directory and reconstruct the author's
    reasoning, and a judge that has seen the reasoning inherits the blind spot that
    produced the error. Was asserted on the chain's fresh-reviewer.
    """
    home = tmp_path / "home"
    home.mkdir()
    install_global_hooks(home, hpr_path="bad")
    body = (home / ".claude" / "agents" / "research-adjudicator.md").read_text()
    assert "tools: Read" in body
    assert "name: research-adjudicator" in body
