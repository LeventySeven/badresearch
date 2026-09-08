"""Research lanes — retrieval surfaces the pipeline can call directly.

A *lane* is a bounded search over one kind of source. It returns a
`LaneResult` that always renders an enumeration line, so a lane that finds
nothing is distinguishable from a lane that is broken.

`local_corpus` is the first lane: a flat glob over the owner's on-disk
libraries (teardowns, transcripts, articles, x-guides, operating specs) — the
one capability a web-only research agent cannot match.
"""

from __future__ import annotations

from bad_research.lanes.local_corpus import DEFAULT_ROOTS, Hit, LaneResult, search_local

__all__ = ["DEFAULT_ROOTS", "Hit", "LaneResult", "search_local"]
