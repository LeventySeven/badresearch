"""Codex install tests: layout, frontmatter validity, roster-completeness
(derived from the LIVE source, never hardcoded), translation-leak lint, and
idempotency.

NEVER writes the real ~/.codex — every test monkeypatches HOME to tmp_path or
passes an explicit tmp home.
"""

import re
from pathlib import Path

import yaml

from bad_research.core import hooks
from bad_research.core.codex_install import (
    AGENT_FILES,
    build_agent_files,
    ensure_multi_agent,
    inject_codex_agents_md,
    install_codex,
    read_codex_asset,
    write_codex_skill,
    write_openai_yaml,
)
from bad_research.core.codex_translate import skillref_path

# --- live roster derivation (NOT hardcoded) ---------------------------------

def _live_step_count() -> int:
    return len(hooks._BAD_RESEARCH_STEP_SKILLS)


def _live_agent_count() -> int:
    """Count the _AGENT prompt constants the Claude installer actually installs.

    Derived from the install loop in hooks.py (the `_install_*_agent(home, ...)`
    calls), so this tracks the real roster rather than a frozen number.
    """
    text = Path(hooks.__file__).read_text(encoding="utf-8")
    calls = re.findall(r"_install_\w+_agent\(home", text)
    return len(calls)


# --- agent roster -----------------------------------------------------------

def test_agent_files_are_the_three_research_agents():
    """Was: 17 chain agents. The chain is gone; shipping its workers to Codex would
    leave agent types resolving to a pipeline nothing invokes."""
    assert sorted(AGENT_FILES) == [
        "research-adjudicator.md", "research-critic.md", "research-reader.md"
    ], sorted(AGENT_FILES)


def test_agent_files_have_no_leftover_placeholder():
    for name, body in AGENT_FILES.items():
        assert "{hpr_path}" not in body, name
        assert "{scaffold_only_sections}" not in body, name


def test_read_codex_asset_loads_router_preamble():
    text = read_codex_asset("router-preamble.md")
    assert "Execution model on Codex" in text


# --- skill dir layout -------------------------------------------------------

def test_write_codex_skill_lays_out_dir(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    write_codex_skill(home, hpr_path="bad")
    root = home / ".codex" / "skills" / "bad-research"
    assert (root / "SKILL.md").exists()
    # The merged skill's own references, carried across. Was: one reference per numbered
    # step plus a static stage->agent dispatch table -- both artifacts of the chain, and
    # a dispatch table with nothing to dispatch is worse than absent.
    assert (root / "references" / "critique.md").exists()
    assert (root / "references" / "evidence.md").exists()
    assert (root / "references" / "lanes" / "web-live.md").exists()
    assert (root / "scripts" / "lane-probes.sh").exists()
    # agent references: the three the merged skill spawns
    assert (root / "references" / "agents" / "research-reader.md").exists()
    assert (root / "references" / "agents" / "research-critic.md").exists()
    assert not (root / "references" / "dispatch-table.md").exists()


def test_no_step_references_ship_and_the_real_references_do(tmp_path):
    """Was: one reference per numbered step skill. Codex had the SAME defect as the
    Claude Code installer -- it rendered the chain -- so fixing one surface only would
    have been cosmetic."""
    home = tmp_path / "home"
    home.mkdir()
    write_codex_skill(home, hpr_path="bad")
    root = home / ".codex" / "skills" / "bad-research"
    for stale in ("bad-research-1-decompose", "bad-research-12-critics"):
        assert not (root / skillref_path(stale)).exists(), stale
    body = (root / "SKILL.md").read_text(encoding="utf-8")
    assert "Skill(skill:" not in body
    assert (root / "references" / "critique.md").is_file()
    assert (root / "references" / "lanes" / "web-live.md").is_file()


def test_skill_md_frontmatter_is_codex_valid(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    write_codex_skill(home, hpr_path="bad")
    fm = (home / ".codex" / "skills" / "bad-research" / "SKILL.md").read_text(encoding="utf-8")
    head = fm.split("---\n")[1]  # first frontmatter block
    # MUST actually parse as YAML — a `str.split(":")` key-name check is falsely
    # green for a folded description whose embedded `: ` breaks the scalar
    # ("mapping values are not allowed here"). Parse it for real.
    data = yaml.safe_load(head)
    assert isinstance(data, dict), f"frontmatter is not a YAML mapping: {data!r}"
    assert set(data.keys()) <= {"name", "description"}, data.keys()
    assert data["name"] == "bad-research"
    # The guard is that the SHIPPED description round-trips through YAML intact,
    # whatever it says -- it used to name the old entry skill's wording verbatim, which
    # made it a spelling test rather than a parse test. Compare against the real source.
    shipped = hooks._skill_tree_source()
    assert shipped is not None
    src_fm = (shipped / "SKILL.md").read_text(encoding="utf-8").split("---\n")[1]
    src_desc = yaml.safe_load(src_fm)["description"]
    assert data["description"].strip() == src_desc.strip()
    assert "Execution model on Codex" in fm  # preamble prepended


def test_write_openai_yaml(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    write_openai_yaml(home)
    y = (
        home / ".codex" / "skills" / "bad-research" / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    assert "display_name:" in y
    assert "default_prompt:" in y


def test_inject_agents_md_creates_marker_section(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    inject_codex_agents_md(home, hpr_path="bad")
    txt = (home / ".codex" / "AGENTS.md").read_text(encoding="utf-8")
    assert "bad-research:start" in txt
    assert "bad-research:end" in txt
    assert "bad fetch" in txt


def test_inject_agents_md_preserves_existing(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    (home / ".codex").mkdir()
    (home / ".codex" / "AGENTS.md").write_text("# My notes\nkeep me\n", encoding="utf-8")
    inject_codex_agents_md(home, hpr_path="bad")
    txt = (home / ".codex" / "AGENTS.md").read_text(encoding="utf-8")
    assert "keep me" in txt
    assert "bad-research:start" in txt


def test_inject_agents_md_no_duplicate_on_rerun(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    inject_codex_agents_md(home, hpr_path="bad")
    second = inject_codex_agents_md(home, hpr_path="bad")
    assert second == []  # nothing changed
    txt = (home / ".codex" / "AGENTS.md").read_text(encoding="utf-8")
    assert txt.count("bad-research:start") == 1


def test_ensure_multi_agent_adds_flag(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    (home / ".codex").mkdir()
    (home / ".codex" / "config.toml").write_text('model = "gpt-5.5"\n', encoding="utf-8")
    ensure_multi_agent(home)
    cfg = (home / ".codex" / "config.toml").read_text(encoding="utf-8")
    assert "[features]" in cfg
    assert "multi_agent = true" in cfg
    assert 'model = "gpt-5.5"' in cfg  # preserved


def test_ensure_multi_agent_inserts_under_existing_features(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    (home / ".codex").mkdir()
    cfg_path = home / ".codex" / "config.toml"
    cfg_path.write_text("[features]\nother = true\n", encoding="utf-8")
    ensure_multi_agent(home)
    cfg = cfg_path.read_text(encoding="utf-8")
    assert "multi_agent = true" in cfg
    assert "other = true" in cfg
    assert cfg.count("[features]") == 1


def test_ensure_multi_agent_idempotent(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    (home / ".codex").mkdir()
    cfg_path = home / ".codex" / "config.toml"
    cfg_path.write_text("[features]\nmulti_agent = true\n", encoding="utf-8")
    assert ensure_multi_agent(home) is None  # no change


# --- full install + idempotency + leak lint ---------------------------------

def test_install_codex_full(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    actions = install_codex(home, hpr_path="bad")
    root = home / ".codex" / "skills" / "bad-research"
    assert (root / "SKILL.md").exists()
    assert (root / "agents" / "openai.yaml").exists()
    assert (home / ".codex" / "AGENTS.md").exists()
    cfg = (home / ".codex" / "config.toml").read_text(encoding="utf-8")
    assert "multi_agent = true" in cfg
    assert len(actions) > 0


def test_install_codex_idempotent(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    install_codex(home, hpr_path="bad")
    second = install_codex(home, hpr_path="bad")
    assert second == []  # nothing changed on second run


def test_install_codex_via_home_default(tmp_path, monkeypatch):
    # Defensive: even the no-arg path must hit the monkeypatched HOME, never the
    # real ~/.codex.
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setattr("pathlib.Path.home", lambda: home)
    install_codex(hpr_path="bad")
    assert (home / ".codex" / "skills" / "bad-research" / "SKILL.md").exists()


_FORBIDDEN = (
    "Skill(",
    "Task(",
    "TodoWrite",
    "subagent_type",
    ".claude/",
    # Claude-only hook + slash-command vocabulary with no Codex equivalent — the
    # AGENTS.md prefer-the-vault section carries the PreToolUse intent.
    "PreToolUse",
    "/bad-research",
    # The lazy step-skill bootstrap flag does not exist on Codex.
    "--steps-only",
)

# Any `references/bad-research-*` path is DANGLING: the real rendered step refs
# are `references/<step>.md` (prefix stripped), and the entry self-reinvoke must
# point at `SKILL.md`, never `references/bad-research.md`.
_DANGLING_REF_RE = re.compile(r"references/bad-research[\w./-]*")


def test_no_claude_tokens_leak_into_codex_render(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    install_codex(home, hpr_path="bad")
    root = home / ".codex" / "skills" / "bad-research"
    offenders = []
    for f in root.rglob("*.md"):
        text = f.read_text(encoding="utf-8")
        for tok in _FORBIDDEN:
            if tok in text:
                offenders.append(f"{f.relative_to(root)}: {tok}")
        for m in _DANGLING_REF_RE.findall(text):
            offenders.append(f"{f.relative_to(root)}: dangling {m}")
    assert not offenders, "Claude tokens leaked:\n" + "\n".join(offenders)
