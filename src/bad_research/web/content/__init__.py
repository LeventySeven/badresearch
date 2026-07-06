"""Keyless content extraction — URL -> clean markdown + the 6 source-type tiers.

KR-3. Replaces the paid Firecrawl/Exa/Tavily `URL -> clean markdown` primitive with
a deterministic local pipeline (dossier 12) + the 6 keyless non-HTML source tiers.
Zero third-party API key; the pipeline is fully deterministic (no model touch).
"""

from __future__ import annotations

# NOTE: the bare `fetch_clean` FUNCTION is deliberately NOT re-exported here — doing so
# shadows the `content.fetch_clean` SUBMODULE attribute, so
# `from bad_research.web.content import fetch_clean; fetch_clean.cache_get(...)` would
# silently grab the function and AttributeError. Callers reach the function via the
# bridge's `importlib.import_module("...fetch_clean").fetch_clean` path (unaffected).
from bad_research.web.content.fetch_clean import (
    FIRECRAWL_CLEAN_PROMPT,
    extract_metadata,
    extract_published_date,
    main_content,
    pdf_to_markdown,
    strip_boilerplate,
)
from bad_research.web.content.sources import (
    ExtractorUnavailable,
    arxiv_source_notes,
    classify_source,
    feed_notes,
    github_clone_notes,
    github_file,
    llms_txt_notes,
    sitemap_urls,
    youtube_transcript,
)

__all__ = [
    "FIRECRAWL_CLEAN_PROMPT",
    "ExtractorUnavailable",
    "arxiv_source_notes",
    "classify_source",
    "extract_metadata",
    "extract_published_date",
    "feed_notes",
    "github_clone_notes",
    "github_file",
    "llms_txt_notes",
    "main_content",
    "pdf_to_markdown",
    "sitemap_urls",
    "strip_boilerplate",
    "youtube_transcript",
]
