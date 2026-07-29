"""PARTIAL degradation was invisible — the specific defect issue #39 is right about.

`gather` only flagged a problem when NO lane returned a hit
(`if not any(v == "ok" ...)`). One lane 429-ing while another returned hits gave
`degraded: false` and no signal anywhere downstream, so the report presented a
half-searched corpus as a complete one — and any silence in it as a finding.

`coverage_gaps` is the fix, and it is deliberately ORTHOGONAL to `degraded`:
`degraded` is a hard STOP the skills branch on, so widening it would break those
STOP tables and kill runs that are perfectly usable.
"""

from __future__ import annotations

import asyncio

from bad_research.funnel.orchestrator import FunnelDeps, gather


def _deps(providers):
    return FunnelDeps(providers=providers, fetcher=None, postfetch_filter=None,
                      vault=None, retrieval=None, vertical_providers=[])


class _Working:
    name = "ddgs"

    async def search_ex(self, q):
        from bad_research.web.search.base import WebResult
        return [WebResult(url="https://example.org/a", title="a", content="body")]


class _RateLimited:
    name = "s2"
    last_status = "rate-limited"

    async def search_ex(self, q):
        return []


class _Dead:
    """The host-tool adapter: cannot run HERE, by documented contract."""

    name = "websearch"

    async def search_ex(self, q):
        raise NotImplementedError("host WebSearch tool is not reachable in a subprocess")


def _gather(providers) -> dict:
    stats: dict = {}
    # p_providers is 1 in light mode, so ask for full to keep both base lanes.
    asyncio.run(gather("topic", mode="full", deps=_deps(providers), stats=stats))
    return stats


def test_a_rate_limited_lane_beside_a_working_one_is_a_coverage_gap():
    stats = _gather([_Working(), _RateLimited()])

    assert stats["degraded"] is False, "the run is usable — this must NOT be a STOP"
    assert stats["degraded_reasons"] == []
    assert stats["coverage_gaps"] == [{"provider": "s2", "outcome": "rate-limited"}]


def test_a_clean_empty_lane_is_not_a_coverage_gap():
    """`no-results` is an ANSWER: we searched, there was nothing. It is the only
    outcome that licenses an absence claim, so it must not be listed as a gap."""
    class _Empty:
        name = "openalex"

        async def search_ex(self, q):
            return []

    stats = _gather([_Working(), _Empty()])
    assert stats["provider_outcomes"]["openalex"] == "no-results"
    assert stats["coverage_gaps"] == []


def test_the_always_unavailable_host_tool_lane_is_not_a_coverage_gap():
    """`WebSearchToolProvider` is appended to EVERY CLI run and always raises in a
    subprocess. Listing it would put a gap on every run and train the reader to
    ignore the field."""
    stats = _gather([_Working(), _Dead()])
    assert stats["provider_outcomes"]["websearch"] == "unavailable"
    assert stats["coverage_gaps"] == []


def test_gaps_are_reported_even_when_the_run_is_fully_degraded():
    """A hard STOP still names WHICH lanes broke and how."""
    stats = _gather([_RateLimited()])
    assert stats["degraded"] is True
    assert stats["coverage_gaps"] == [{"provider": "s2", "outcome": "rate-limited"}]


def test_a_rate_limited_only_run_is_an_infrastructure_failure_not_an_empty_topic():
    """The extended NON_ANSWERING set: every lane throttled must report
    `no_search_provider_available`, not "every lane ran and found nothing"."""
    stats = _gather([_RateLimited()])
    assert stats["degraded_reasons"] == ["no_search_provider_available"]


def test_stats_is_still_optional():
    out = asyncio.run(gather("t", mode="light", deps=_deps([_RateLimited()])))
    assert out == []
