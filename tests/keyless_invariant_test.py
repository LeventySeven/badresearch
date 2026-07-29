"""Keyless invariant (Task 1) — the CI guard that keeps bad-research install-and-go.

Delegates to ``bad_research.tests.keyless_invariant`` so the CI test and the
runnable gate (``python -m bad_research.tests.keyless_invariant``) share ONE
source of truth. See that module for the two invariants.
"""

from __future__ import annotations

from bad_research.tests import keyless_invariant as ki


def test_base_requires_dist_has_no_keyed_provider() -> None:
    """No keyed search/browse provider may leak into base project.dependencies."""
    keyed = ki.keyed_base_deps()
    assert keyed == [], f"keyed provider(s) leaked into base dependencies: {keyed}"


def test_skill_path_modules_never_import_the_key_bridge() -> None:
    """No skill-path module may import llm.anthropic or read ANTHROPIC_API_KEY."""
    bridged = ki.skill_path_bridge_imports()
    assert bridged == [], f"skill-path module(s) import the key bridge: {bridged}"


def test_check_reports_clean() -> None:
    """The combined gate is green on the current tree."""
    assert ki.check() == []


def test_guard_has_teeth_for_keyed_deps(monkeypatch) -> None:
    """Prove the base-dep check is not vacuous: a crafted keyed dep IS flagged."""
    monkeypatch.setattr(ki, "base_dependencies", lambda: ["anthropic>=0.40", "tavily>=0.3"])
    assert ki.keyed_base_deps() == ["tavily>=0.3"]


def test_guard_has_teeth_for_bridge_imports(monkeypatch) -> None:
    """Prove the skill-path check is not vacuous: pointed at the bridge module
    itself (which genuinely reads ANTHROPIC_API_KEY), the scan flags it."""
    monkeypatch.setattr(ki, "SKILL_PATH_MODULES", ("bad_research.llm.anthropic",))
    assert ki.skill_path_bridge_imports() == ["bad_research.llm.anthropic"]
