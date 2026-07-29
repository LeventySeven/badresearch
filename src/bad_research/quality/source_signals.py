"""SOURCE_QUALITY_SIGNALS — the canonical source-quality negative-signal list.

The working mechanism Anthropic KEPT after deleting its broken
``evaluate_source_quality`` tool (CLAUDE_RESEARCH.md:1313): a prompt-embedded list
a reader flags a source against — flag, don't silently drop (the lead reconciles
the flags downstream). This module is the single source of truth for that list; the
fetcher (width + depth) and critic skill prompts each embed it at a
``<!-- source-quality-signals -->`` marker, and tests/test_quality/test_source_signals.py
binds those skill MDs to this constant (drift guard).

Each signal maps to a typed flag that flows into a note's ``source_quality_flags``
array and is reconciled in ``bad-research-11-synthesize.md``.
"""

from __future__ import annotations

# The typed flag vocabulary carried in a note's `source_quality_flags` array and
# reconciled at synthesis. Keep in sync with the list in SOURCE_QUALITY_SIGNALS
# and with the three skill MDs (the drift test enforces this).
SOURCE_QUALITY_FLAGS: tuple[str, ...] = (
    "aggregator",
    "false_authority",
    "nameless_source",
    "vague_qualifier",
    "unconfirmed",
    "marketing_spin",
    "speculation",
    "cherry_picked",
)

SOURCE_QUALITY_SIGNALS = """SOURCE-QUALITY NEGATIVE SIGNALS (down-weight or FLAG, do NOT suppress):
As you read each source, judge it against this list (Anthropic worker-prompt
discipline — the things a regex/domain check CANNOT see). FLAG the source; do NOT
silently drop it (the lead reconciles flags downstream — flag, don't suppress):
- news aggregators rather than original sources       -> flag `aggregator`
- false authority (cites authority it lacks / misattributes)  -> `false_authority`
- passive voice with nameless sources ("experts say", "it is reported")  -> `nameless_source`
- general qualifiers without specifics ("many", "often", "significant")  -> `vague_qualifier`
- unconfirmed reports (rumor not yet verified)        -> flag `unconfirmed`
- marketing language / spin language (promotional, sales copy)  -> `marketing_spin`
- speculation presented as finding, incl. future-tense predictions ("could", "may", projections) stated as things that happened  -> `speculation`
- cherry-picked data (selective evidence, no counter-data)  -> `cherry_picked`
A source with NONE of these gets no flags (it is unchanged). A primary filing or
peer-reviewed paper is almost never flagged; a vendor "X is the best" listicle on a
good domain SHOULD be flagged `marketing_spin` even though its domain tier is high."""

__all__ = ["SOURCE_QUALITY_FLAGS", "SOURCE_QUALITY_SIGNALS"]
