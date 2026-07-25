"""The fan-out is multiplicative — it must be throttled and diagnostically honest.

Threading the width-sweep plan raised a `full` run from 6 seed queries to as many
as 100. Across 4 lanes that is 400 outbound searches; fired at once, a keyless
HTML scraper gets rate-limited, swallows the 429 into [], and the whole run then
reports "this topic has no sources" — a self-inflicted outage misreported as a
research gap. Found in review of the breadth fix, before it shipped.
"""
from __future__ import annotations

import asyncio

from bad_research.funnel.fanout import _FANOUT_CONCURRENCY, fan_out
from bad_research.funnel.orchestrator import FunnelDeps, gather
from bad_research.web.search.base import SearchQuery, WebResult


class _ConcurrencyProbe:
    """Records the high-water mark of simultaneous in-flight calls."""

    def __init__(self) -> None:
        self.name = "probe"
        self.live = 0
        self.peak = 0

    async def search_ex(self, q):
        self.live += 1
        self.peak = max(self.peak, self.live)
        await asyncio.sleep(0.01)  # hold the slot so overlap is observable
        self.live -= 1
        return [WebResult(url=f"https://e.org/{q.query}", title="t", content="c")]


def test_fan_out_is_bounded_by_the_concurrency_cap():
    probe = _ConcurrencyProbe()
    queries = [SearchQuery(query=f"q{i}", max_results=5) for i in range(60)]
    asyncio.run(fan_out(queries, [probe]))
    assert probe.peak <= _FANOUT_CONCURRENCY, (
        f"fan_out ran {probe.peak} searches at once against a cap of "
        f"{_FANOUT_CONCURRENCY} — an unthrottled scraper gets rate-limited"
    )


def test_fan_out_still_returns_every_result_under_the_cap():
    """Throttling must not drop work — only stagger it."""
    probe = _ConcurrencyProbe()
    queries = [SearchQuery(query=f"q{i}", max_results=5) for i in range(25)]
    hits = asyncio.run(fan_out(queries, [probe]))
    assert len(hits) == 25


def test_explicit_concurrency_is_honoured():
    probe = _ConcurrencyProbe()
    queries = [SearchQuery(query=f"q{i}", max_results=5) for i in range(20)]
    asyncio.run(fan_out(queries, [probe], None, 2))
    assert probe.peak <= 2


def test_a_raised_error_outranks_a_clean_empty_in_the_outcome_map():
    """9 errors + 1 empty is broken infrastructure, not a sourceless topic."""

    class _MostlyBroken:
        name = "ddgs"
        calls = 0

        async def search_ex(self, q):
            _MostlyBroken.calls += 1
            if _MostlyBroken.calls > 1:
                raise RuntimeError("connection reset")
            return []

    deps = FunnelDeps(providers=[_MostlyBroken()], fetcher=None, postfetch_filter=None,
                      vault=None, retrieval=None, vertical_providers=[])
    stats: dict = {}
    asyncio.run(gather("topic", mode="light", deps=deps, stats=stats))
    assert stats["provider_outcomes"]["ddgs"] == "error", (
        "ranking 'empty' above 'error' hid the infrastructure failure behind "
        "the sourceless-topic reason"
    )


def test_ok_still_beats_every_failure_status():
    class _Flaky:
        name = "ddgs"
        calls = 0

        async def search_ex(self, q):
            _Flaky.calls += 1
            if _Flaky.calls == 1:
                return [WebResult(url="https://e.org/a", title="t", content="c")]
            raise RuntimeError("later failure")

    deps = FunnelDeps(providers=[_Flaky()], fetcher=None, postfetch_filter=None,
                      vault=None, retrieval=None, vertical_providers=[])
    stats: dict = {}
    asyncio.run(gather("topic", mode="light", deps=deps, stats=stats))
    assert stats["provider_outcomes"]["ddgs"] == "ok"
    assert stats["degraded"] is False
