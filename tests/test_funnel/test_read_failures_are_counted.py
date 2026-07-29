"""A corpus short because the web refused us must not read as a thin topic.

`read_top_k`'s `_fetch` swallowed every 403 / paywall / timeout into `None` with
no counter anywhere, so a run where 60 of 80 reads failed was byte-identical in
the envelope to one where 60 pages were genuinely thin (issue #39). The degrade
itself is correct — one page must never abort the wave — the SILENCE was the bug.
"""

from __future__ import annotations

import asyncio

from bad_research.funnel.read import read_top_k


class _Candidate:
    def __init__(self, url: str) -> None:
        self.canonical_url = url


class _Page:
    links: list = []

    def __init__(self, url: str = "https://example.org/read") -> None:
        self.url = url
        self.title = "read page"
        self.content = "a fetched page body long enough to survive Stage E filtering"
        self.metadata: dict = {}


class _PickyFetcher:
    """Refuses every URL whose path is in `blocked` — the 403/paywall shape."""

    def __init__(self, blocked: set[str]) -> None:
        self.blocked = blocked

    def fetch_tiered(self, url, *, tier_max=1):
        if url in self.blocked:
            raise RuntimeError(f"403 for {url}")
        return _Page(url)


def _read(blocked, urls, outcomes=None):
    return asyncio.run(read_top_k(
        [_Candidate(u) for u in urls],
        fetcher=_PickyFetcher(blocked),
        read_top_k=len(urls),
        concurrency=4,
        max_chain_depth=0,
        max_links_per_hub=0,
        outcomes=outcomes,
    ))


URLS = [f"https://example.org/{i}" for i in range(5)]


def test_failed_reads_are_counted():
    outcomes: dict = {}
    pages = _read(set(URLS[:3]), URLS, outcomes)

    assert len(pages) == 2, "the survivors still carry the funnel"
    assert outcomes["n_fetch_failed"] == 3
    assert outcomes["n_fetch_attempted"] == 5


def test_failed_urls_are_sampled_for_diagnosis():
    outcomes: dict = {}
    _read(set(URLS[:3]), URLS, outcomes)
    assert sorted(outcomes["failed_urls"]) == sorted(URLS[:3])


def test_a_fully_successful_wave_reports_zero():
    outcomes: dict = {}
    pages = _read(set(), URLS, outcomes)
    assert len(pages) == 5
    assert outcomes["n_fetch_failed"] == 0


def test_omitting_outcomes_is_byte_identical():
    """Opt-in instrumentation, same contract as fan_out's."""
    assert len(_read(set(URLS[:3]), URLS)) == 2


def test_the_count_reaches_the_funnel_envelope():
    """End-to-end: gather threads the read outcomes into stats."""
    from bad_research.funnel.orchestrator import FunnelDeps, gather

    # Distinct domains AND distinct snippets: Stage B dedups on URL AND content
    # hash, and Stage C.5 caps per domain — five identical example.org hits
    # collapse to one candidate and there is nothing left to fail on.
    hosts = [f"https://site{i}.example/page" for i in range(5)]

    class _Provider:
        name = "ddgs"

        async def search_ex(self, q):
            from bad_research.web.search.base import WebResult
            return [WebResult(url=u, title=f"title {i}",
                              content=f"distinct snippet body number {i} about the topic")
                    for i, u in enumerate(hosts)]

    class _Store:
        def store_note(self, **kw):
            return "n1"

    class _Engine:
        def index(self, notes): ...
        def search(self, q, mode="light", top_k=10):
            return []

    deps = FunnelDeps(providers=[_Provider()], fetcher=_PickyFetcher(set(hosts[:3])),
                      postfetch_filter=lambda r: None, vault=_Store(), retrieval=_Engine())
    stats: dict = {}
    asyncio.run(gather("topic", mode="light", deps=deps, stats=stats))

    assert stats["n_fetch_failed"] == 3
    assert stats["read_outcomes"]["n_fetch_attempted"] == 5
