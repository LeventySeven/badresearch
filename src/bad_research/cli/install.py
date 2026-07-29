"""`bad install` — the skill/agent/hook installer.

Default target is USER-GLOBAL (`~/.claude/`): the entry skill + agents +
PreToolUse hook land once and `/bad-research` is available in every Claude Code
session. `--project` opts into project-local `.claude/` + `./research/` and
ships ALL step skills. `--steps-only` is the lazy per-project step-skill install
the entry-skill bootstrap fires on first `/bad-research` invocation, and
`--prune-steps` is its inverse — it removes those per-project step-skill dirs
again (leaving the entry skill and any unrelated skill in the same directory
untouched).
"""

from __future__ import annotations

import json
from pathlib import Path

import typer

# Re-export the idempotent installer (Plan 08's `core.hooks`) so callers and the
# Plan-09 idempotency contract test import it from the CLI surface.
from bad_research.core.hooks import install_global_hooks


def install(
    path: str = typer.Argument(".", help="Project path (only used with --project / --steps-only)"),
    project: bool = typer.Option(
        False, "--project", "-p",
        help="Install into project-local .claude/ + ./research/ instead of user-global ~/.claude/.",
    ),
    steps_only: bool = typer.Option(
        False, "--steps-only", help="(internal) lazy step-skill install into a project .claude/.",
    ),
    prune_steps: bool = typer.Option(
        False, "--prune-steps",
        help=(
            "Remove the per-project bad-research step-skill dirs from "
            "<path>/.claude/skills/ (leaves the entry skill and unrelated "
            "skills alone). Takes precedence over --steps-only."
        ),
    ),
    codex: bool = typer.Option(
        False, "--codex",
        help="Install into Codex (~/.codex/skills/) instead of Claude Code (~/.claude/).",
    ),
    json_output: bool = typer.Option(False, "--json", "-j"),
) -> None:
    from bad_research.core.agent_docs import _resolve_executable
    from bad_research.core.hooks import (
        _install_bad_research_step_skills,
        _prune_project_step_skills,
        install_global_hooks,
        install_hooks,
    )

    hpr = _resolve_executable()

    if codex:
        from bad_research.core.codex_install import install_codex

        actions = install_codex(Path.home(), hpr_path=hpr)
        msg = "Ready. bad-research available as a Codex skill (~/.codex/skills/bad-research/)."
    elif prune_steps:
        root = Path(path).resolve()
        result = _prune_project_step_skills(root)
        actions = [result] if result else []
        msg = (
            f"Project step skills removed from {root / '.claude' / 'skills'}."
            if result
            else "No bad-research step skills to prune."
        )
    elif steps_only:
        root = Path(path).resolve()
        result = _install_bad_research_step_skills(root)
        actions = [result] if result else []
        msg = "Step skills installed (lazy)."
    elif project:
        root = Path(path).resolve()
        actions = install_hooks(root, hpr_path=hpr)
        msg = f"Project install complete at {root}. /bad-research available in this project."
    else:
        actions = install_global_hooks(Path.home(), hpr_path=hpr)
        msg = "Ready. /bad-research available in every Claude Code session."

    if json_output:
        typer.echo(json.dumps({"ok": True, "actions": actions, "message": msg}))
    else:
        for a in actions:
            typer.echo(f"  • {a}")
        typer.echo(msg)


__all__ = ["install", "install_global_hooks"]
