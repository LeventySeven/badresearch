"""Executable-path resolution for the `bad` CLI.

This module used to also inject a "Research Base (hyperresearch)" block into the
CLAUDE.md at every vault root. That injection has been REMOVED and must not come
back in this form.

Why it was deleted (2026-09-08): the injected block instructed agents to run
`/hyperresearch <query>` and to invoke sixteen step skills named
`hyperresearch-1-decompose` … `hyperresearch-16-readability-audit`. None of those
names has ever existed — the package ships a `bad-research` entry skill and
`bad-research-N-*` step skills. Because CLAUDE.md is the highest-priority file in
an agent's context, every session in a vault-initialised project was told, up
front, to call a slash command and sixteen skills that could not resolve. It had
reached five real projects, and in two of them this module had CREATED the
CLAUDE.md itself, so the file's entire content was the wrong instructions.

Note the guard that did not catch it: `tests/test_core/test_agent_docs_commands.py`
was added after issues #11/#16 (a blurb citing CLI commands that did not exist) and
pins every `{hpr} <command>` invocation to the live Typer surface. It checks the CLI
dimension only. The identical failure — documenting names that do not exist —
recurred in the SKILL-name dimension, which no test covered.

If agent-facing documentation is ever reintroduced, the rule it must satisfy is:
every command, skill, path and flag it names is asserted against the live registry
by a test, or it is not written to a user's context file at all.
"""

from __future__ import annotations

from pathlib import Path


def _resolve_executable() -> str:
    """Find the absolute path to the `bad` executable.

    Priority: venv sibling of current python > PATH > bare name. Both `bad` and
    the `badr` alias resolve to the same Typer app (pyproject [project.scripts]).
    """
    import shutil
    import sys

    names = ("bad", "bad.exe", "badr", "badr.exe")
    # First: find it relative to the current Python interpreter (venv installs).
    # This takes priority over PATH to avoid picking up a system-wide install.
    python_dir = Path(sys.executable).parent
    for name in names:
        candidate = python_dir / name
        if candidate.exists():
            return str(candidate)
    # Also check Scripts/ subdirectory (Windows venv layout)
    for name in names:
        candidate = python_dir / "Scripts" / name
        if candidate.exists():
            return str(candidate)

    # Second: check PATH
    for name in ("bad", "badr"):
        which = shutil.which(name)
        if which:
            return which

    # Fallback — bare name, hope it's on PATH
    return "bad"
