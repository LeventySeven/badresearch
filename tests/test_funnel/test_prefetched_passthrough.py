"""Prefetched candidates keep the body their provider already read.

The social lane returns content-complete results (the thread, its top comments,
the transcript). Re-fetching a reddit.com or x.com permalink anonymously returns
a login wall, which Stage E drops as junk — so a re-fetch would gather the
evidence and discard it one stage later. Stage D passes those through; Stage E
does not apply its post-FETCH junk rules to them.
"""

from __future__ import annotations

from bad_research.funnel.dedup import Candidate
from bad_research.funnel.filter import filter_and_store
from bad_research.funnel.read import read_top_k
from tests.test_funnel.conftest import FakeFetcher, FakeVault, FakeWebResult, fake_postfetch_filter


def _cand(url, *, prefetched=False, content="snippet", title=""):
    meta = {"prefetched": True} if prefetched else {}
    return Candidate(
        canonical_url=url,
        result=FakeWebResult(url=url, title=title, content=content, metadata=meta),
        provider_ranks={"last30days" if prefetched else "ddgs": 1},
    )


async def test_prefetched_candidate_is_not_fetched():
    ranked = [_cand("https://www.reddit.com/r/x/comments/1/", prefetched=True)]
    fetcher = FakeFetcher()
    results = await read_top_k(ranked, fetcher=fetcher, read_top_k=80, concurrency=4,
                               max_chain_depth=0, max_links_per_hub=0)
    assert fetcher.read_urls == []                       # no HTTP call at all
    assert [r.url for r in results] == ["https://www.reddit.com/r/x/comments/1/"]


async def test_prefetched_body_survives_verbatim():
    body = "u/someone: it broke my fine-tunes (1,485 upvotes)"
    ranked = [_cand("https://www.reddit.com/r/x/comments/2/", prefetched=True, content=body)]
    results = await read_top_k(ranked, fetcher=FakeFetcher(), read_top_k=80, concurrency=4,
                               max_chain_depth=0, max_links_per_hub=0)
    assert results[0].content == body


async def test_normal_candidates_are_still_fetched():
    ranked = [_cand("https://blog.example/post")]
    fetcher = FakeFetcher()
    await read_top_k(ranked, fetcher=fetcher, read_top_k=80, concurrency=4,
                     max_chain_depth=0, max_links_per_hub=0)
    assert fetcher.read_urls == ["https://blog.example/post"]


async def test_mixed_pool_reads_only_the_unfetched_half():
    ranked = [
        _cand("https://www.reddit.com/r/x/comments/3/", prefetched=True),
        _cand("https://blog.example/a"),
        _cand("https://news.ycombinator.com/item?id=1", prefetched=True),
        _cand("https://blog.example/b"),
    ]
    fetcher = FakeFetcher()
    results = await read_top_k(ranked, fetcher=fetcher, read_top_k=80, concurrency=4,
                               max_chain_depth=0, max_links_per_hub=0)
    assert sorted(fetcher.read_urls) == ["https://blog.example/a", "https://blog.example/b"]
    assert len(results) == 4                              # all four reach Stage E


async def test_prefetched_still_spends_the_read_budget():
    # The budget bounds how much content enters the corpus, not how many HTTP
    # calls we make — otherwise a social-heavy pool silently blows past the ceiling.
    ranked = [_cand(f"https://s{i}.example/p", prefetched=True) for i in range(10)]
    results = await read_top_k(ranked, fetcher=FakeFetcher(), read_top_k=4, concurrency=4,
                               max_chain_depth=0, max_links_per_hub=0)
    assert len(results) == 4


def test_stage_e_does_not_junk_filter_a_short_prefetched_body():
    # 200 chars of Reddit comment is short on purpose; the <300 rule exists to
    # catch a FAILED FETCH, and nothing was fetched here.
    short = FakeWebResult(url="https://www.reddit.com/r/x/comments/4/", title="t",
                          content="short but load-bearing", metadata={"prefetched": True})
    assert fake_postfetch_filter(short) is not None       # the filter WOULD drop it
    vault = FakeVault()
    stored = filter_and_store([short], vault=vault, postfetch_filter=fake_postfetch_filter,
                              redundancy_overlap=0.7, shingle_n=3)
    assert len(stored) == 1                               # kept anyway


def test_stage_e_still_junk_filters_a_short_fetched_body():
    short = FakeWebResult(url="https://blog.example/thin", title="t", content="thin")
    stored = filter_and_store([short], vault=FakeVault(), postfetch_filter=fake_postfetch_filter,
                              redundancy_overlap=0.7, shingle_n=3)
    assert stored == []
