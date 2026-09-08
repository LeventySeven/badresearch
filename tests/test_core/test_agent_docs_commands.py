"""Live Typer command map, plus a guard that the CLAUDE.md injection stays deleted.

HISTORY. This file used to pin the installer-written CLAUDE.md blurb to the real
CLI surface. Issues #11/#16: the published v0.1.0 blurb instructed `bad sync`,
`bad note list/update`, `bad tags`, `bad repair`, `bad status`, `bad setup` and a
`fetch --save-assets` flag, none of which existed, so every agent following the
documented mechanics failed on its first call.

The guard worked for the dimension it checked and was blind to the one next to it.
The blurb also named a `/hyperresearch` slash command and sixteen step skills
(`hyperresearch-1-decompose` … `hyperresearch-16-readability-audit`) that have
never existed under those names — the package ships `bad-research` and
`bad-research-N-*`. Nothing asserted skill names, so the same failure class
recurred and shipped into five real projects.

The injection was deleted on 2026-09-08 (see `core/agent_docs.py`). The blurb tests
are therefore gone; what remains is `_real_command_map`, which
`tests/test_skills/test_cli_surface_drift.py` imports, plus a regression guard
that nothing re-adds a writer for a user's context file.

If agent-facing docs are ever reintroduced, the rule is: every command, skill,
path and flag they name is asserted against the live registry by a test, or they
are not written to a user's context file at all.
"""
from __future__ import annotations

import inspect

from bad_research.cli import app
from bad_research.core import agent_docs, vault


def _real_command_map() -> dict[str, set[str]]:
    """{top-level command -> set of its subcommands} for the live Typer app.

    A leaf command maps to an empty set; a group (note/assets) maps to its
    subcommand names."""
    out: dict[str, set[str]] = {}
    for c in app.registered_commands:
        name = c.name or (c.callback.__name__ if c.callback else None)
        if name:
            out[name] = set()
    for g in app.registered_groups:
        subs: set[str] = set()
        ti = g.typer_instance
        if ti is not None:
            for sc in ti.registered_commands:
                sname = sc.name or (sc.callback.__name__ if sc.callback else None)
                if sname:
                    subs.add(sname)
        out[g.name] = subs
    return out


def test_command_map_is_non_empty():
    """Sanity: the helper other tests import actually sees the live app."""
    real = _real_command_map()
    assert real, "Typer app exposed no commands — the command map is broken"
    assert "doctor" in real, f"expected `doctor` on every build; got {sorted(real)}"


def test_agent_docs_no_longer_injects_anything():
    """The CLAUDE.md blurb and its injector must stay deleted.

    Re-adding a writer that targets a user's context file is the regression this
    guards. `_resolve_executable` is the module's only remaining export.
    """
    for gone in (
        "inject_agent_docs",
        "_inject_into_file",
        "HYPERRESEARCH_BLURB",
        "HYPERRESEARCH_SECTION_MARKER",
        "HYPERRESEARCH_SECTION_END",
    ):
        assert not hasattr(agent_docs, gone), (
            f"agent_docs.{gone} is back. The CLAUDE.md injection was deleted "
            "because it named a slash command and sixteen skills that do not "
            "exist. Do not reintroduce it without a test asserting every name "
            "it writes against the live registry."
        )
    assert hasattr(agent_docs, "_resolve_executable")


def test_vault_create_does_not_write_agent_docs():
    """`bad init` must not touch any file outside the vault it is creating."""
    src = inspect.getsource(vault)
    assert "inject_agent_docs" not in src, (
        "vault.py calls inject_agent_docs again — `bad init` must not write to a "
        "user's CLAUDE.md."
    )
