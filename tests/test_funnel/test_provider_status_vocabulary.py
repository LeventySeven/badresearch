"""A lane that COULD NOT SEARCH must not read as a lane that FOUND NOTHING.

Every keyless provider swallows its transport failure into `[]` so one dead lane
can never abort the fan-out. Correct — and it is why a 429, a DNS failure and a
genuinely sourceless query all arrived here identical, and the report then said
"there is nothing on X" about a topic the stack never actually searched
(issue #39).

The fix leaves a note behind: `provider.last_status`. These tests pin the
vocabulary, the ranking, and the invariant the previous fix wrote a comment
about — a raised error must outrank a clean empty.
"""

from __future__ import annotations

import asyncio

import httpx
import pytest

from bad_research.funnel.fanout import _OUTCOME_RANK, fan_out
from bad_research.funnel.orchestrator import FunnelDeps, gather
from bad_research.web.search.status import classify_search_failure


def _deps(providers):
    return FunnelDeps(providers=providers, fetcher=None, postfetch_filter=None,
                      vault=None, retrieval=None, vertical_providers=[])


class _StatusProvider:
    """A provider that swallowed its failure into [] but recorded WHY."""

    def __init__(self, name: str, status: str) -> None:
        self.name = name
        self.last_status = status

    async def search_ex(self, q):
        return []


def test_a_rate_limited_lane_is_not_reported_as_no_results():
    stats: dict = {}
    asyncio.run(gather("topic", mode="light",
                       deps=_deps([_StatusProvider("ddgs", "rate-limited")]), stats=stats))
    assert stats["provider_outcomes"] == {"ddgs": "rate-limited"}


@pytest.mark.parametrize("status", ["rate-limited", "timeout", "unreachable", "error"])
def test_every_observable_failure_status_survives_the_funnel(status):
    stats: dict = {}
    asyncio.run(gather("t", mode="light",
                       deps=_deps([_StatusProvider("x", status)]), stats=stats))
    assert stats["provider_outcomes"]["x"] == status


def test_a_clean_empty_lane_is_no_results():
    """The ONE outcome that licenses an absence claim downstream."""
    stats: dict = {}
    asyncio.run(gather("t", mode="light",
                       deps=_deps([_StatusProvider("x", "ok")]), stats=stats))
    assert stats["provider_outcomes"]["x"] == "no-results"


def test_hits_beat_a_stale_failure_status():
    """`last_status` is per-instance and shared across concurrent queries, so a
    call that RETURNED HITS must never be downgraded by a sibling's status."""
    class _Hits:
        name = "x"
        last_status = "rate-limited"

        async def search_ex(self, q):
            from bad_research.web.search.base import WebResult
            return [WebResult(url="https://example.org/a", title="a", content="b")]

    stats: dict = {}
    asyncio.run(gather("t", mode="light", deps=_deps([_Hits()]), stats=stats))
    assert stats["provider_outcomes"]["x"] == "ok"


def test_a_raised_error_still_outranks_a_clean_empty():
    """The invariant fanout.py:88-90 warns about — regression-locked across the
    vocabulary widening."""
    assert _OUTCOME_RANK["error"] > _OUTCOME_RANK["no-results"]
    assert _OUTCOME_RANK["rate-limited"] > _OUTCOME_RANK["no-results"]
    assert _OUTCOME_RANK["ok"] == max(_OUTCOME_RANK.values())

    class _Flaky:
        name = "flaky"
        calls = 0

        async def search_ex(self, q):
            _Flaky.calls += 1
            if _Flaky.calls == 1:
                raise RuntimeError("boom")
            return []

    stats: dict = {}
    asyncio.run(gather("t", mode="light", deps=_deps([_Flaky()]), stats=stats))
    assert stats["provider_outcomes"]["flaky"] == "error"


def test_legacy_empty_value_is_still_accepted_as_an_input_alias():
    """Any out-of-tree caller or fake still passing the old value must not crash."""
    assert _OUTCOME_RANK["empty"] == _OUTCOME_RANK["no-results"]


def test_an_unranked_last_status_cannot_break_the_fanout():
    """A provider is free to invent a status; the fan-out must not KeyError."""
    outcomes: dict = {}
    asyncio.run(fan_out([object()], [_StatusProvider("x", "banana")], outcomes))
    assert outcomes["x"] == "no-results"  # unrecognized -> not trusted as a diagnosis


# ── the classifier that turns a live exception into a status ─────────────────
def test_classify_maps_a_429_to_rate_limited():
    resp = httpx.Response(429, request=httpx.Request("GET", "https://x.example"))
    exc = httpx.HTTPStatusError("429", request=resp.request, response=resp)
    assert classify_search_failure(exc) == "rate-limited"


def test_classify_maps_transport_failures():
    req = httpx.Request("GET", "https://x.example")
    assert classify_search_failure(httpx.ConnectTimeout("t", request=req)) == "timeout"
    assert classify_search_failure(httpx.ConnectError("c", request=req)) == "unreachable"
    assert classify_search_failure(OSError("dns")) == "unreachable"
    assert classify_search_failure(ValueError("?")) == "error"


def test_classify_falls_back_to_the_exception_name_for_optional_deps():
    """`ddgs` raises its own hierarchy and is an optional import we must not
    pull in just to name a class."""
    class RatelimitException(Exception):
        pass

    class TimeoutException(Exception):
        pass

    assert classify_search_failure(RatelimitException()) == "rate-limited"
    assert classify_search_failure(TimeoutException()) == "timeout"


def test_a_500_is_a_generic_error_not_a_rate_limit():
    resp = httpx.Response(500, request=httpx.Request("GET", "https://x.example"))
    exc = httpx.HTTPStatusError("500", request=resp.request, response=resp)
    assert classify_search_failure(exc) == "error"
