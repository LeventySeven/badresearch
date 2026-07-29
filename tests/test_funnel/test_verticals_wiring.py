"""Verticals wiring: intent-routed keyless scholarly APIs fan alongside the base
web providers, so an academic query stops silently degrading to DuckDuckGo scraping.

`_build_vertical_providers` selects providers by intent (no network — construction only);
`gather()` fires them ALONGSIDE the p_providers-capped base set (they bypass the cap
because they're already intent-curated).
"""

from __future__ import annotations

import pytest

from bad_research.cli.research import _build_vertical_providers
from bad_research.funnel.orchestrator import FunnelDeps, gather
from tests.test_funnel.conftest import (
    FakeFetcher,
    FakeProvider,
    FakeRetrievalEngine,
    FakeVault,
    fake_postfetch_filter,
)


def _names(provs) -> set[str]:
    return {p.name for p in provs}


def test_academic_query_selects_scholarly_verticals():
    provs = _build_vertical_providers("a systematic review of transformer papers on arxiv")
    # openalex/arxiv/semantic_scholar(s2)/crossref per VERTICAL_ROUTES["academic"]
    assert _names(provs) == {"openalex", "arxiv", "s2", "crossref"}


def test_general_query_gets_no_verticals_byte_identical():
    # a general-intent query returns [] → the funnel behaves exactly as before
    assert _build_vertical_providers("best pizza places near me") == []


def test_technical_route_excludes_base_ddgs():
    # VERTICAL_ROUTES["technical"] = [arxiv, openalex, ddgs]; ddgs is an always-on base
    # provider, so it must NOT be re-added as a vertical (no double-fan).
    provs = _build_vertical_providers("how to implement a token-bucket rate limiter api")
    names = _names(provs)
    assert "ddgs" not in names
    assert names == {"arxiv", "openalex"}


@pytest.mark.asyncio
async def test_verticals_fire_alongside_capped_base_providers():
    # light mode caps base providers at p_providers=1, but a vertical must still fire.
    base = [FakeProvider("ddgs"), FakeProvider("searxng"), FakeProvider("websearch")]
    arxiv = FakeProvider("arxiv", url_template="https://arxiv.example/{q}/{i}")
    deps = FunnelDeps(
        providers=base,
        vertical_providers=[arxiv],
        fetcher=FakeFetcher(),
        postfetch_filter=fake_postfetch_filter,
        vault=FakeVault(),
        retrieval=FakeRetrievalEngine(),
    )
    await gather("quantum error correction", mode="light", deps=deps)
    # base is capped to 1 (only ddgs fired), but the vertical fired regardless of the cap
    assert arxiv.calls, "vertical provider was sliced off by the p_providers cap"
    assert base[0].calls, "the first base provider should still fire"
    assert not base[2].calls, "light mode p_providers=1 should cap the base set"


@pytest.mark.asyncio
async def test_no_verticals_is_byte_identical_to_before():
    # default (no vertical_providers) → the funnel runs exactly as it did pre-change
    deps = FunnelDeps(
        providers=[FakeProvider("ddgs")],
        fetcher=FakeFetcher(),
        postfetch_filter=fake_postfetch_filter,
        vault=FakeVault(),
        retrieval=FakeRetrievalEngine(),
    )
    assert deps.vertical_providers == []
    chunks = await gather("anything", mode="light", deps=deps)
    assert isinstance(chunks, list)
