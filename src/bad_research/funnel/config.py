"""FunnelConfig — the tiered numeric spine of the scraper funnel.

Every constant traces to INTERFACES.md (frozen constants) and dossier
10_SCRAPER_SOURCING.md §6.2. We ship the upper bound of each `full` range and
the lower bound of each `light` range so the ~80-read CEILING is always the
binding constraint (dossier 10 §3.3: reading past ~80 degrades synthesis).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Mode = Literal["light", "full"]


@dataclass(frozen=True)
class FunnelConfig:
    # Stage A — fan-out
    m_queries: int
    p_providers: int
    k_per_query: int
    # Stage B — dedup / pool
    candidate_pool: int
    dedup_jaccard: float
    shingle_n: int
    # Stage C.5 — pool diversity (funnel/diversity.py). Both tiers share these:
    # the guards are about SHAPE, not width, so a light run should be as spread
    # as a full one. max_per_domain is the netloc translation of last30days'
    # 3-per-author cap; min_per_provider reserves head slots per search lane.
    max_per_domain: int
    min_per_provider: int
    # Stage C — rank
    rrf_k: int
    utility_max: int
    # Stage D — read
    read_top_k: int
    read_concurrency: int
    max_chain_depth: int
    max_links_per_hub: int
    # Stage E — filter
    redundancy_overlap: float
    # Stage F — rerank/feed
    top_chunks: int
    relevance_threshold: float

    # The load-bearing global ceiling (INTERFACES.md frozen constants).
    READ_CEILING: int = 80

    @classmethod
    def for_mode(cls, mode: str) -> FunnelConfig:
        if mode == "full":
            cfg = cls(
                m_queries=100, p_providers=4, k_per_query=10,
                candidate_pool=120, dedup_jaccard=0.60, shingle_n=3,
                max_per_domain=3, min_per_provider=2,
                rrf_k=60, utility_max=18,
                read_top_k=80, read_concurrency=12,
                max_chain_depth=2, max_links_per_hub=5,
                redundancy_overlap=0.60,
                top_chunks=30, relevance_threshold=0.70,
            )
        elif mode == "light":
            cfg = cls(
                m_queries=12, p_providers=1, k_per_query=5,
                candidate_pool=20, dedup_jaccard=0.60, shingle_n=3,
                max_per_domain=3, min_per_provider=2,
                rrf_k=60, utility_max=18,
                read_top_k=12, read_concurrency=3,
                max_chain_depth=0, max_links_per_hub=0,
                redundancy_overlap=0.60,
                top_chunks=8, relevance_threshold=0.70,
            )
        else:
            raise ValueError(
                f"unknown mode {mode!r}; valid modes are 'light' and 'full' "
                "('deep' is full@max-effort, not a 4th mode — see SPEC §6)")
        # Invariant: never read past the ceiling.
        assert cfg.read_top_k <= cls.READ_CEILING
        return cfg
