"""`--concurrency` — the bounded answer to issue #36 (unbounded fan-out request).

Issue #36 asks for a zero-limit/uncapped fan-out mode. Against a KEYLESS scraped
backend (ddgs) that is a self-DoS: no rate-limit contract, no `Retry-After`, and
a soft-block returns [] that is indistinguishable from "no results". The
reference corpus is unanimous that real systems use small FIXED caps —
Composio `MAX_PARALLEL_WORKERS=5`, Zenbu `MAX_CONCURRENCY=4`/`MAX_PARALLEL_TASKS=8`
— and none exposes unbounded client-side fan-out.

So #36 gets the knob it actually wants (throughput control) with a bounded
range, not an infinity escape hatch.
"""
from __future__ import annotations

import asyncio
import inspect

import bad_research.cli.research as RESEARCH  # noqa: N812
from bad_research.funnel.fanout import _FANOUT_CONCURRENCY, _clamp_concurrency, fan_out
from bad_research.web.search.base import SearchQuery, WebResult


class _Probe:
    def __init__(self) -> None:
        self.name = "probe"
        self.live = 0
        self.peak = 0

    async def search_ex(self, q):
        self.live += 1
        self.peak = max(self.peak, self.live)
        await asyncio.sleep(0.01)
        self.live -= 1
        return [WebResult(url=f"https://e.org/{q.query}", title="t", content="c")]


def test_concurrency_is_clamped_to_a_sane_range():
    """A bounded knob, never an infinity switch."""
    assert _clamp_concurrency(None) == _FANOUT_CONCURRENCY
    assert _clamp_concurrency(4) == 4
    assert _clamp_concurrency(0) == 1          # 0 must not mean "unbounded"
    assert _clamp_concurrency(-5) == 1
    assert _clamp_concurrency(9999) == 16      # hard ceiling
    assert _clamp_concurrency(16) == 16


def test_raising_the_knob_actually_raises_in_flight_calls():
    probe = _Probe()
    queries = [SearchQuery(query=f"q{i}", max_results=5) for i in range(40)]
    asyncio.run(fan_out(queries, [probe], None, _clamp_concurrency(12)))
    assert probe.peak <= 12
    assert probe.peak > 8, "the knob must genuinely lift the default ceiling"


def test_lowering_the_knob_actually_lowers_in_flight_calls():
    probe = _Probe()
    queries = [SearchQuery(query=f"q{i}", max_results=5) for i in range(40)]
    asyncio.run(fan_out(queries, [probe], None, _clamp_concurrency(2)))
    assert probe.peak <= 2


def test_zero_does_not_unleash_unbounded_fanout():
    """The literal issue-#36 request, refused on purpose."""
    probe = _Probe()
    queries = [SearchQuery(query=f"q{i}", max_results=5) for i in range(30)]
    asyncio.run(fan_out(queries, [probe], None, _clamp_concurrency(0)))
    assert probe.peak == 1


def test_cli_and_run_funnel_expose_the_knob():
    assert "concurrency" in inspect.signature(RESEARCH.run_funnel).parameters
    src = inspect.getsource(RESEARCH.funnel_gather_cmd)
    assert "--concurrency" in src
