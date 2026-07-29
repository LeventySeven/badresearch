from __future__ import annotations

from bad_research.funnel.config import FunnelConfig


def test_full_tier_constants_match_dossier():
    cfg = FunnelConfig.for_mode("full")
    assert cfg.m_queries == 100          # upper bound of 40-100 (dossier 10 §6.2)
    assert cfg.p_providers == 4          # 2-4
    assert cfg.k_per_query == 10
    assert cfg.candidate_pool == 120
    assert cfg.read_top_k == 80          # the ceiling IS the full read budget
    assert cfg.read_concurrency == 12
    assert cfg.max_chain_depth == 2
    assert cfg.max_links_per_hub == 5
    assert cfg.rrf_k == 60
    assert cfg.dedup_jaccard == 0.60
    assert cfg.shingle_n == 3
    assert cfg.redundancy_overlap == 0.60
    assert cfg.utility_max == 18
    assert cfg.top_chunks == 30          # upper bound of 10-30
    assert cfg.relevance_threshold == 0.70


def test_light_tier_constants_match_dossier():
    cfg = FunnelConfig.for_mode("light")
    assert cfg.m_queries == 12           # lower bound of 12-20
    assert cfg.p_providers == 1          # 1-2 → 1 (seed-only)
    assert cfg.k_per_query == 5
    assert cfg.candidate_pool == 20
    assert cfg.read_top_k == 12          # 12-20
    assert cfg.read_concurrency == 3
    assert cfg.max_chain_depth == 0      # no chained crawl on light
    assert cfg.max_links_per_hub == 0
    assert cfg.top_chunks == 8           # lower bound of 8-15


def test_diversity_guards_are_identical_across_tiers():
    # The Stage C.5 guards are about the SHAPE of the pool, not its width, so a
    # light run must be as spread across hosts/lanes as a full one (issue #40).
    for mode in ("light", "full"):
        cfg = FunnelConfig.for_mode(mode)
        assert cfg.max_per_domain == 3       # netloc port of the 3-per-author cap
        assert cfg.min_per_provider == 2     # reserved head slots per search lane


def test_read_top_k_never_exceeds_ceiling():
    # The ceiling is global and load-bearing (degrades past 80, hyperresearch).
    for mode in ("light", "full"):
        assert FunnelConfig.for_mode(mode).read_top_k <= FunnelConfig.READ_CEILING
    assert FunnelConfig.READ_CEILING == 80


def test_unknown_mode_raises():
    import pytest
    with pytest.raises(ValueError, match="mode"):
        FunnelConfig.for_mode("deep")  # 'deep' is full@max-effort, not a 4th mode
