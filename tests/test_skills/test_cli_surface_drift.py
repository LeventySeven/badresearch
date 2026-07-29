"""Guard: no prompt may instruct an agent to run a `bad` subcommand that doesn't exist.

`tests/test_core/test_agent_docs_commands.py` already pins the installer-written
CLAUDE.md blurb to the live Typer surface (issue #11/#16: the published v0.1.0 blurb
told agents to run `bad sync` / `bad tags` / `bad repair`, none of which existed).
That guard covered ONE string. The far larger prompt surface — every
`src/bad_research/skills/*.md` and every uppercase prompt constant in
`core/hooks.py`, all of which shell out to `bad` — had no equivalent check, which is
how a capability probe keyed on a fabricated `bad sources` subcommand reached a
fully-green PR: `bad sources --help` exits 2 on every build, so the probe recorded
`sources: false` everywhere and pinned every run to the degraded native-fetch path.

Scope note: only invocations inside code spans (fenced blocks or `inline code`) are
checked, so prose like "produces a bad report" is not mistaken for a command.
"""

from __future__ import annotations

import re
from pathlib import Path

from bad_research.core import hooks
from tests.test_core.test_agent_docs_commands import _real_command_map

SKILLS_DIR = Path(__file__).resolve().parents[2] / "src" / "bad_research" / "skills"

# `bad <cmd> [<sub>]`, `$HPR <cmd> …`, `{hpr_path} <cmd> …`, `{hpr} <cmd> …`
_INVOCATION = re.compile(
    r"(?:\$HPR|\{hpr_path\}|\{hpr\}|(?<![\w-])bad)\s+([a-z][a-z0-9-]+)(?:\s+([a-z][a-z0-9-]+))?"
)
_FENCE = re.compile(r"```.*?```", re.S)
_INLINE = re.compile(r"`[^`\n]+`")

# Tokens that can follow a group command but are not subcommands.
_NON_SUBCOMMAND = {"--help"}


def _code_spans(text: str) -> list[str]:
    """Fenced blocks + inline-code spans — the only places a command is a command."""
    spans = [m.group(0) for m in _FENCE.finditer(text)]
    spans += [m.group(0) for m in _INLINE.finditer(_FENCE.sub("\n", text))]
    return spans


def _phantom_commands(text: str) -> set[str]:
    real = _real_command_map()
    groups = {name for name, subs in real.items() if subs}
    bad: set[str] = set()
    for span in _code_spans(text):
        for cmd, sub in _INVOCATION.findall(span):
            if cmd not in real:
                bad.add(cmd)
            elif (cmd in groups and sub and not sub.startswith("-")
                    and sub not in real[cmd] and sub not in _NON_SUBCOMMAND):
                bad.add(f"{cmd} {sub}")
    return bad


def _prompt_surface() -> list[tuple[str, str]]:
    out = [(p.name, p.read_text(encoding="utf-8")) for p in sorted(SKILLS_DIR.glob("*.md"))]
    for name in dir(hooks):
        value = getattr(hooks, name)
        if name.isupper() and isinstance(value, str):
            out.append((f"hooks.{name}", value))
    return out


def test_every_prompt_references_only_real_cli_commands():
    offenders = {
        label: sorted(phantoms)
        for label, text in _prompt_surface()
        if (phantoms := _phantom_commands(text))
    }
    assert not offenders, (
        "prompts instruct agents to run non-existent `bad` subcommands "
        f"(an agent following them fails on its first call): {offenders}"
    )


def test_the_surface_actually_covers_the_skills_and_the_hooks_constants():
    """Guard the guard: an empty scan set would make the test above vacuous."""
    labels = [label for label, _ in _prompt_surface()]
    assert "bad-research.md" in labels
    assert sum(1 for label in labels if label.startswith("hooks.")) >= 5
    assert len(labels) >= 20


def test_scanner_catches_a_phantom_subcommand():
    """Negative control — this is the exact shape that slipped through review."""
    assert _phantom_commands("run `bad sources --help` to probe") == {"sources"}
    assert _phantom_commands("run `bad note frobnicate -j`") == {"note frobnicate"}
    # ...and does not fire on real commands or on prose.
    assert _phantom_commands("run `bad fetch <url>` and `bad note new`") == set()
    assert _phantom_commands("the light pipeline produces a bad report") == set()
