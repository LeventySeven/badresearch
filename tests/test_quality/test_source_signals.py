"""Task 4 (E8): SOURCE_QUALITY_SIGNALS is the single DRY source-quality
negative-signal list, embedded behind a `<!-- source-quality-signals -->` marker
in the width-sweep, depth-investigation, and critics skill prompts. This is the
drift guard binding those three skill MDs to the canonical constant — flag, don't
silently drop or suppress."""

from __future__ import annotations

import pathlib

from bad_research.quality.source_signals import (
    SOURCE_QUALITY_FLAGS,
    SOURCE_QUALITY_SIGNALS,
)

MARKER = "<!-- source-quality-signals -->"

# parents[2] is the repo root: tests/test_quality/<file> -> tests -> repo root.
# The flag taxonomy used to be embedded in three chain step skills. The chain is gone
# and the taxonomy moved into the merged skill's evidence reference -- so this points at
# where it lives now. The capability under test is unchanged: the shipped constant and
# the prose a researcher reads must not drift apart.
_SKILLS_DIR = pathlib.Path(__file__).resolve().parents[2] / "skills/bad-research"
_SKILL_FILES = ("references/evidence.md",)


def _read(name: str) -> str:
    return (_SKILLS_DIR / name).read_text(encoding="utf-8")


def test_signals_constant_nonempty_and_has_core_terms():
    assert SOURCE_QUALITY_SIGNALS.strip(), "SOURCE_QUALITY_SIGNALS must be non-empty"
    assert "aggregator" in SOURCE_QUALITY_SIGNALS
    assert "flag" in SOURCE_QUALITY_SIGNALS.lower()


def test_eight_flags_each_backtick_wrapped_in_signals():
    assert len(SOURCE_QUALITY_FLAGS) == 8
    for flag in SOURCE_QUALITY_FLAGS:
        assert f"`{flag}`" in SOURCE_QUALITY_SIGNALS, f"{flag} not backtick-wrapped"


def test_each_skill_md_embeds_marker_flags_and_discipline():
    for name in _SKILL_FILES:
        text = _read(name)
        lower = text.lower()
        assert MARKER in text, f"{name} missing marker"
        for flag in SOURCE_QUALITY_FLAGS:
            assert flag in text, f"{name} missing flag {flag}"
        assert "flag" in lower, f"{name} missing 'flag'"
        assert "suppress" in lower, f"{name} missing 'suppress'"


def test_marker_appears_exactly_once_per_skill_md():
    total = 0
    for name in _SKILL_FILES:
        count = _read(name).count(MARKER)
        assert count == 1, f"{name} should embed the marker exactly once, got {count}"
        total += count
    assert total == len(_SKILL_FILES)
