"""Quality / no-bullshit filtering pipeline (SPEC §8, dossier 07).

Public API — the contract every other plan imports. Five-stage cheap-before-expensive
filter + the mandatory untrusted-content injection preamble.
"""

from __future__ import annotations

from bad_research.quality.content_filter import looks_like_paywall, postfetch_filter
from bad_research.quality.injection import (
    INJECTION_PREAMBLE,
    UNTRUSTED_EVIDENCE_RULE,
    strip_untrusted,
    wrap_untrusted,
)
from bad_research.quality.prefilter import (
    DOMAIN_TIER,
    TierInfo,
    canonical_url,
    domain_tier,
    is_blocklisted,
    seo_farm_score,
)
from bad_research.quality.sources import build_source_row, source_id, upsert_source

__all__ = [  # noqa: RUF022 — grouped by pipeline stage (the filter contract), not alphabetical
    # Stage 1 — pre-fetch source signals
    "seo_farm_score", "DOMAIN_TIER", "domain_tier", "TierInfo",
    "canonical_url", "is_blocklisted",
    # Stage 2 — post-fetch content filter
    "postfetch_filter", "looks_like_paywall",
    # Injection defense
    "INJECTION_PREAMBLE", "UNTRUSTED_EVIDENCE_RULE", "strip_untrusted", "wrap_untrusted",
    # sources provenance
    "source_id", "build_source_row", "upsert_source",
]
