"""Tests for the pre-fetch garbage gate now WIRED into the funnel (Stage B.6).

`quality/prefilter.py`'s `is_blocklisted` / `seo_farm_score` / `domain_tier`
machinery was orphaned (test-only). It is now called from
`funnel/orchestrator.py::prefetch_garbage_gate`, a stage that runs AFTER the
recency gate (B.5) and BEFORE the candidate-pool cap — so blocklisted farms
(Pinterest/Quora/…) and SEO listicles never fill the pool or spend one of the
funnel's ≤80 reads. Authority tiers (primary/docs/reference) are exempt from the
SEO gate exactly as `prefetch_filter` does.

These tests prove: blocklisted URLs drop, SEO-farm candidates drop, authority
sources with spammy snippets survive (tier-exempt), and a normal source survives
— both as a unit and end-to-end through `gather`.
"""

from __future__ import annotations

from bad_research.funnel.dedup import dedup
from bad_research.funnel.orchestrator import (
    FunnelDeps,
    gather,
    prefetch_garbage_gate,
)
from tests.test_funnel.conftest import (
    FakeFetcher,
    FakeProvider,
    FakeRetrievalEngine,
    FakeVault,
    FakeWebResult,
    fake_postfetch_filter,
)

# Spammy SERP snippet that trips >= 2 SEO signals (listicle + clickbait + year).
_SPAM_SNIPPET = "17 Best Tools You Won't Believe Exist in 2026..."
_GOOD_SNIPPET = (
    "The central bank held rates steady, citing persistent core inflation "
    "and a cooling but still-tight labor market."
)


def _hit(url, *, snippet, provider="sonar"):
    # The SERP snippet lives in WebResult.content at the un-read stage.
    return FakeWebResult(url=url, title=url, content=snippet,
                         serp_rank=1, serp_provider=provider)


def _urls(cands):
    return {c.url for c in cands}


# ---- prefetch_garbage_gate unit (operates on funnel Candidates) -----------

def test_gate_drops_blocklisted_url():
    cands = dedup([_hit("https://www.pinterest.com/pin/123", snippet=_GOOD_SNIPPET)])
    kept = prefetch_garbage_gate(cands, query="anything")
    assert kept == []


def test_gate_drops_seo_farm_candidate():
    cands = dedup([_hit("https://seofarm.example/best-tools", snippet=_SPAM_SNIPPET)])
    kept = prefetch_garbage_gate(cands, query="tools")
    assert kept == []


def test_gate_exempts_primary_source_with_spammy_snippet():
    # A .gov primary is exempt from the SEO gate even with a listicle snippet.
    cands = dedup([_hit("https://www.sec.gov/reports/overview", snippet=_SPAM_SNIPPET)])
    kept = prefetch_garbage_gate(cands, query="tools")
    assert len(kept) == 1


def test_gate_exempts_docs_source_with_spammy_snippet():
    cands = dedup([_hit("https://docs.python.org/3/library/asyncio.html",
                        snippet=_SPAM_SNIPPET)])
    kept = prefetch_garbage_gate(cands, query="asyncio")
    assert len(kept) == 1


def test_gate_keeps_normal_good_source():
    cands = dedup([_hit("https://reuters.com/markets/rates", snippet=_GOOD_SNIPPET)])
    kept = prefetch_garbage_gate(cands, query="rates")
    assert len(kept) == 1


def test_gate_keeps_good_drops_garbage_in_mixed_pool():
    cands = dedup([
        _hit("https://reuters.com/markets/rates", snippet=_GOOD_SNIPPET,
             provider="sonar"),
        _hit("https://www.pinterest.com/pin/999", snippet=_GOOD_SNIPPET,
             provider="exa"),
        _hit("https://seofarm.example/best-tools", snippet=_SPAM_SNIPPET,
             provider="searxng"),
    ])
    kept = _urls(prefetch_garbage_gate(cands, query="rates"))
    assert kept == {"https://reuters.com/markets/rates"}


def test_gate_falls_back_to_title_when_snippet_empty():
    # snippet (content) empty -> the gate scores the title instead.
    cand = dedup([FakeWebResult(url="https://seofarm.example/best-tools",
                                title=_SPAM_SNIPPET, content="",
                                serp_rank=1, serp_provider="sonar")])
    kept = prefetch_garbage_gate(cand, query="tools")
    assert kept == []


# ---- end-to-end through gather --------------------------------------------

class GarbageProvider(FakeProvider):
    """Returns one blocklisted, one SEO-farm, and one clean hit (distinct
    bodies so Stage-2 content-hash dedup keeps all three)."""

    async def search_ex(self, q):
        self.calls.append(q.query)
        return [
            FakeWebResult(url="https://www.pinterest.com/pin/42", title="pin",
                          content="pinned image board " * 20, serp_rank=1,
                          serp_provider=self.name),
            FakeWebResult(url="https://seofarm.example/best-tools",
                          title="farm", content=_SPAM_SNIPPET, serp_rank=2,
                          serp_provider=self.name),
            FakeWebResult(url="https://reuters.com/markets/rates", title="news",
                          content=_GOOD_SNIPPET, serp_rank=3,
                          serp_provider=self.name),
        ]


async def test_gather_garbage_never_reaches_the_read_budget():
    fetcher = FakeFetcher()
    deps = FunnelDeps(providers=[GarbageProvider("sonar")], fetcher=fetcher,
                      postfetch_filter=fake_postfetch_filter, vault=FakeVault(),
                      retrieval=FakeRetrievalEngine())
    await gather("rates", mode="full", deps=deps)
    assert "https://www.pinterest.com/pin/42" not in fetcher.read_urls
    assert "https://seofarm.example/best-tools" not in fetcher.read_urls
    assert "https://reuters.com/markets/rates" in fetcher.read_urls
