"""Tests for Stage-1 pre-fetch source filtering (dossier 07 §1)."""

from __future__ import annotations

from bad_research.quality.prefilter import seo_farm_score


def test_seo_farm_score_blocks_listicle_plus_money_path(farm_candidates):
    url, snippet = farm_candidates[0]  # best-laptops-2026-review + "17 best ... top picks"
    assert seo_farm_score(url, snippet, query="laptops") >= 2


def test_seo_farm_score_blocks_clickbait_plus_money_path(farm_candidates):
    url, snippet = farm_candidates[1]
    assert seo_farm_score(url, snippet, query="vpn") >= 2


def test_seo_farm_score_blocks_keyword_stuffing(farm_candidates):
    url, snippet = farm_candidates[2]
    assert seo_farm_score(url, snippet, query="vpn") >= 2


def test_seo_farm_score_keeps_arxiv(clean_candidates):
    url, snippet = clean_candidates[0]
    assert seo_farm_score(url, snippet, query="scaling laws") < 2


def test_seo_farm_score_keeps_single_signal_blog(clean_candidates):
    url, snippet = clean_candidates[2]  # one listicle signal only
    assert seo_farm_score(url, snippet, query="postgres") == 1


def test_seo_farm_score_thin_snippet_signal():
    # snippet < 120 chars AND ends mid-sentence "..." = +1
    score = seo_farm_score("https://x.example/p",
                           "A short teaser that cuts off mid thought and ...",
                           query="anything")
    assert score == 1


from bad_research.quality.prefilter import DOMAIN_TIER, TierInfo, domain_tier


def test_domain_tier_table_has_seven_tiers_with_frozen_multipliers():
    assert DOMAIN_TIER["primary"].multiplier == 1.30
    assert DOMAIN_TIER["docs"].multiplier == 1.15
    assert DOMAIN_TIER["reference"].multiplier == 1.10
    assert DOMAIN_TIER["news_tier1"].multiplier == 1.00
    assert DOMAIN_TIER["blog"].multiplier == 0.85
    assert DOMAIN_TIER["forum"].multiplier == 0.80
    assert DOMAIN_TIER["seo_farm"].multiplier == 0.50


def test_domain_tier_classifies_primary_by_tld():
    assert domain_tier("https://www.sec.gov/x").name == "primary"
    assert domain_tier("https://cs.stanford.edu/paper").name == "primary"


def test_domain_tier_classifies_reference_and_docs():
    assert domain_tier("https://arxiv.org/abs/1.2").name == "reference"
    assert domain_tier("https://en.wikipedia.org/wiki/X").name == "reference"
    assert domain_tier("https://docs.python.org/3/").name == "docs"


def test_domain_tier_classifies_forum_and_news():
    assert domain_tier("https://news.ycombinator.com/item?id=1").name == "forum"
    assert domain_tier("https://www.reddit.com/r/x").name == "forum"
    assert domain_tier("https://www.reuters.com/tech").name == "news_tier1"


def test_domain_tier_defaults_to_blog():
    assert domain_tier("https://someones-personal-site.example/post").name == "blog"


def test_domain_tier_returns_tierinfo_with_priority():
    info = domain_tier("https://www.sec.gov/x")
    assert isinstance(info, TierInfo)
    assert info.prefetch_priority == 0  # fetch primaries first


from bad_research.quality.prefilter import (
    canonical_url,
    is_blocklisted,
    passes_recency_gate,
)


def test_canonical_url_strips_tracking_and_amp_and_fragment():
    assert canonical_url("https://Site.com/Post/?utm_source=x&id=5&fbclid=z#frag") \
        == "https://site.com/post?id=5"
    assert canonical_url("https://amp.site.com/post/amp/") == "https://site.com/post"
    assert canonical_url("https://m.site.com/a/") == "https://site.com/a"


def test_canonical_url_collapses_duplicates():
    a = canonical_url("https://x.com/p?utm_campaign=spring")
    b = canonical_url("https://x.com/p")
    assert a == b


def test_blocklist_domains_and_paths():
    assert is_blocklisted("https://www.pinterest.com/pin/123")
    assert is_blocklisted("https://quora.com/What-is")
    assert is_blocklisted("https://site.com/amp/article")
    assert is_blocklisted("https://site.com/tag/python")
    assert not is_blocklisted("https://arxiv.org/abs/1")


def test_recency_gate_drops_stale_non_primary():
    # query is time-sensitive "current" (180d). A 400-day-old blog is dropped.
    assert not passes_recency_gate(published_days_ago=400, tier_name="blog",
                                   max_age_days=180)
    # ...but a primary source is NEVER recency-dropped (2019 SEC filing rule).
    assert passes_recency_gate(published_days_ago=400, tier_name="primary",
                               max_age_days=180)
    # fresh blog passes
    assert passes_recency_gate(published_days_ago=10, tier_name="blog",
                               max_age_days=180)
    # unknown age passes (don't drop what we can't date)
    assert passes_recency_gate(published_days_ago=None, tier_name="blog",
                               max_age_days=180)
