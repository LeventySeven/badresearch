from __future__ import annotations

from bad_research.funnel.dedup import Candidate
from bad_research.funnel.read import read_top_k
from tests.test_funnel.conftest import FakeFetcher, FakeWebResult


def _ranked(n):
    out = []
    for i in range(n):
        url = f"https://src{i}.com/p"
        out.append(Candidate(canonical_url=url,
                             result=FakeWebResult(url=url, content="snippet"),
                             provider_ranks={"sonar": i + 1}))
    return out


async def test_reads_only_top_k_not_full_pool():
    ranked = _ranked(120)              # post-dedup candidate pool ~120
    fetcher = FakeFetcher()
    results = await read_top_k(ranked, fetcher=fetcher, read_top_k=80,
                               concurrency=12, max_chain_depth=0, max_links_per_hub=0)
    assert len(fetcher.read_urls) == 80          # only 80 fetched
    assert len(results) == 80


async def test_81st_candidate_is_never_read():
    ranked = _ranked(120)
    # mark the 81st (index 80) with a sentinel URL; assert it's absent from reads
    sentinel = "https://NEVER-READ.com/p"
    ranked[80] = Candidate(canonical_url=sentinel,
                           result=FakeWebResult(url=sentinel, content="x"),
                           provider_ranks={"sonar": 81})
    fetcher = FakeFetcher()
    await read_top_k(ranked, fetcher=fetcher, read_top_k=80, concurrency=12,
                     max_chain_depth=0, max_links_per_hub=0)
    assert sentinel not in fetcher.read_urls


async def test_ceiling_caps_even_if_top_k_misconfigured():
    # Defense in depth: even if a caller passes read_top_k > ceiling, never read >80.
    ranked = _ranked(200)
    fetcher = FakeFetcher()
    await read_top_k(ranked, fetcher=fetcher, read_top_k=999, concurrency=12,
                     max_chain_depth=0, max_links_per_hub=0, ceiling=80)
    assert len(fetcher.read_urls) == 80


async def test_batched_read_concurrency_bounded():
    # The semaphore bounds in-flight reads; we assert it completes and reads all.
    ranked = _ranked(20)
    fetcher = FakeFetcher()
    results = await read_top_k(ranked, fetcher=fetcher, read_top_k=20, concurrency=5,
                               max_chain_depth=0, max_links_per_hub=0)
    assert len(results) == 20


async def test_chained_crawl_follows_top_hub_links_bounded():
    # src0 is a hub linking 8 outbound URLs; with max_links_per_hub=5 we follow 5.
    hub = "https://hub.com/p"
    extra = [f"https://child{i}.com/a" for i in range(8)]
    ranked = [Candidate(canonical_url=hub,
                        result=FakeWebResult(url=hub, content="hub"),
                        provider_ranks={"sonar": 1})]
    fetcher = FakeFetcher(hub_links={hub: extra})
    await read_top_k(ranked, fetcher=fetcher, read_top_k=80, concurrency=12,
                     max_chain_depth=2, max_links_per_hub=5,
                     query="topic")
    read = set(fetcher.read_urls)
    assert hub in read
    followed = [c for c in extra if c in read]
    assert len(followed) == 5            # exactly max_links_per_hub, not all 8


async def test_chain_depth_zero_follows_nothing():
    hub = "https://hub.com/p"
    ranked = [Candidate(canonical_url=hub,
                        result=FakeWebResult(url=hub, content="hub"),
                        provider_ranks={"sonar": 1})]
    fetcher = FakeFetcher(hub_links={hub: ["https://child.com/a"]})
    await read_top_k(ranked, fetcher=fetcher, read_top_k=80, concurrency=12,
                     max_chain_depth=0, max_links_per_hub=0, query="topic")
    assert fetcher.read_urls == [hub]    # no link-following on light tier


class _RaisingFetcher(FakeFetcher):
    """A fetcher that raises on one specific URL (e.g. a 401/timeout), like the
    real tiered fetcher does on a non-2xx, so we can prove one bad read never
    aborts the whole gather."""

    def __init__(self, *, raise_url: str):
        super().__init__()
        self._raise_url = raise_url

    async def fetch_tiered(self, url, *, tier_max=1, instruction=None, schema=None):
        if url == self._raise_url:
            self.read_urls.append(url)
            raise RuntimeError("HTTP 401 Unauthorized")
        return await super().fetch_tiered(url, tier_max=tier_max)


async def test_one_failing_url_does_not_abort_the_read_wave():
    # issue #27 / #14: a single URL raising (401/403/timeout) inside the primary
    # asyncio.gather must NOT propagate and zero the whole run. The offender is
    # dropped to None; every other candidate is still read and returned.
    ranked = _ranked(10)
    bad_url = ranked[3].canonical_url
    fetcher = _RaisingFetcher(raise_url=bad_url)
    results = await read_top_k(ranked, fetcher=fetcher, read_top_k=10, concurrency=5,
                               max_chain_depth=0, max_links_per_hub=0)
    assert len(results) == 9                        # 10 attempted, 1 raised → dropped
    assert bad_url in fetcher.read_urls             # it WAS attempted
    assert all(r is not None for r in results)      # survivors, no None leaks


async def test_chained_links_reenter_dedup_no_double_read():
    # A hub links to a URL already in the read set → it is NOT read twice.
    hub = "https://hub.com/p"
    dup = "https://src1.com/p"
    ranked = [
        Candidate(canonical_url=hub, result=FakeWebResult(url=hub, content="hub"),
                  provider_ranks={"sonar": 1}),
        Candidate(canonical_url=dup, result=FakeWebResult(url=dup, content="x"),
                  provider_ranks={"sonar": 2}),
    ]
    fetcher = FakeFetcher(hub_links={hub: [dup]})
    await read_top_k(ranked, fetcher=fetcher, read_top_k=80, concurrency=12,
                     max_chain_depth=2, max_links_per_hub=5, query="topic")
    assert fetcher.read_urls.count(dup) == 1   # read once, not twice
