"""Stage A — fan-out. Many queries per step (Perplexity queries: List[str]),
fired across P providers in parallel (asyncio.gather), then flattened.

Breadth = M_QUERIES x P_PROVIDERS x K_PER_QUERY, gathered concurrently so
latency ≈ max single search, not the sum (dossier 10 §1.3, §5.1).

A dead provider degrades to the survivors (SPEC §13 provider failover) — one
provider's exception never aborts the fan-out.

Every provider call is routed through funnel._async.acall so the SYNCHRONOUS
real providers (Plan 03 blocking httpx) and the async test fakes both work.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Literal

from bad_research.funnel._async import acall


@dataclass
class SearchQuery:
    """Mirror of the Plan 03 SearchQuery (INTERFACES.md web/base.py). Redeclared
    here as the funnel's input contract; the real one is structurally identical.
    """

    query: str
    intent: Literal["keyword", "neural", "deep"] = "keyword"
    recency_days: int | None = None
    include_domains: list[str] | None = None
    exclude_domains: list[str] | None = None
    max_results: int = 10


# Deterministic lens suffixes — the programmatic fallback expansion when the
# skill doesn't supply its own lens plan (dossier 10 §1.2 lenses A/B/C/D).
#
# SIZE MATTERS: `plan_queries` can only ever emit as many seeds as there are
# entries here, so a short table silently caps the funnel's breadth far below
# its configured budget. `full` mode budgets m_queries=100; with the original
# 6-entry table it fanned out 6 — a 94% shortfall the run never reported. The
# table stays deliberately lens-DIVERSE rather than long: padding it with
# near-synonyms would spend real HTTP fan-out on redundant SERPs. The honest
# ceiling for deterministic expansion is "one seed per distinct lens"; genuine
# breadth past that comes from the width-sweep skill's own 40-100 row plan,
# threaded in via `queries=` (see gather()).
_LENS_SUFFIXES = (
    "",                              # Lens A — core fact (verbatim query first)
    "latest developments",          # Lens A — state-of-the-art
    "overview how it works",        # Lens A — explanatory framing
    "2026 current state",           # Lens A — recency-pinned breadth
    "original study foundational paper",   # Lens B — citation-chain depth
    "primary data analysis",        # Lens B — upstream sources
    "systematic review meta-analysis",     # Lens B — evidence synthesis
    "peer reviewed research",       # Lens B — scholarly lane
    "criticism limitations",        # Lens C — adversarial
    "alternative explanation",      # Lens C — dissent
    "risks drawbacks",              # Lens C — downside framing
    "controversy debunked",         # Lens C — contested claims
    "failure cases what went wrong",       # Lens C — negative evidence
    "official report filing",       # Lens D — primary/period-pinned documents
    "statistics dataset",           # Lens D — quantitative primaries
    "case study evidence",          # Lens D — grounded instances
)


def plan_queries(query: str, *, m_queries: int, k_per_query: int) -> list[SearchQuery]:
    """Expand one user query into ≤ m_queries SearchQuery seeds. Verbatim query
    is always the first seed. Cheap deterministic fallback for programmatic
    callers; the width-sweep skill (Plan 08) may pass a richer lens plan in."""
    seen: set[str] = set()
    out: list[SearchQuery] = []
    for suffix in _LENS_SUFFIXES:
        text = query if not suffix else f"{query} {suffix}"
        if text in seen:
            continue
        seen.add(text)
        out.append(SearchQuery(query=text, max_results=k_per_query))
        if len(out) >= m_queries:
            break
    return out[:m_queries]


# A provider's MOST INFORMATIVE outcome across its queries wins. "ok" tops the
# table (one query returning hits proves the lane works), but a raised error
# outranks a clean empty: a lane that threw on 9 of 10 queries and returned []
# on the 10th is broken infrastructure, not a sourceless topic. Ranking "empty"
# above "error" reintroduced the exact empty-vs-broken confusion one layer down.
_OUTCOME_RANK = {"empty": 0, "unavailable": 1, "error": 2, "ok": 3}


# Ceiling on SIMULTANEOUS provider calls. The fan-out is (queries x providers),
# so it grows multiplicatively: a full-tier 100-query plan across 4 lanes is 400
# outbound searches. Firing those at once gets a keyless HTML scraper (ddgs)
# rate-limited or blocked, and — because those providers swallow transport
# errors into [] — the whole run then looks like "this topic has no sources".
# Throttling here is what makes the threaded search plan safe to ship at all.
#
# 8 matches what comparable systems settled on for the same shape of work
# (Composio MAX_PARALLEL_WORKERS=5, Zenbu MAX_PARALLEL_TASKS=8/MAX_CONCURRENCY=4)
# — and a keyless scraped backend has strictly LESS headroom than their
# authenticated APIs, since there is no rate-limit contract to read.
_FANOUT_CONCURRENCY = 8

# Hard ceiling on the user-facing knob. Issue #36 asked for an UNBOUNDED /
# zero-limit fan-out mode; this is the deliberate refusal. Against an
# unofficial scraped endpoint, "unbounded" is a self-DoS with no upside past a
# handful of concurrent requests, and its failure mode is the worst one we
# have: a soft-block returns [] that is indistinguishable from "no results", so
# the run reports a research gap that is really our own traffic. The knob gives
# #36 the throughput control it actually wants, within a range that cannot
# brick the run.
_FANOUT_CONCURRENCY_MAX = 16


def _clamp_concurrency(n: int | None) -> int:
    """Clamp a caller-supplied concurrency to [1, _FANOUT_CONCURRENCY_MAX].

    `None` means "use the default". 0 does NOT mean unbounded — it clamps to 1,
    so the issue-#36 spelling of "no limit" degrades to the safest setting
    rather than the most dangerous one.
    """
    if n is None:
        return _FANOUT_CONCURRENCY
    return max(1, min(int(n), _FANOUT_CONCURRENCY_MAX))


async def fan_out(queries: list[Any], providers: list[Any],
                  outcomes: dict[str, str] | None = None,
                  concurrency: int = _FANOUT_CONCURRENCY) -> list[Any]:
    """Fire every (query x provider) concurrently; flatten survivors.

    Returns the raw hit pool (with duplicates — Stage B dedups). Stamps the
    representative WebResults with serp_rank/serp_provider if the provider
    didn't already (fakes do; real providers set them in search_ex).

    `concurrency`: max in-flight provider calls. Bounded because the fan-out is
    multiplicative — see `_FANOUT_CONCURRENCY`.

    `outcomes` (optional): opt-in instrumentation. When a dict is passed it is
    filled with {provider_name: "ok" | "empty" | "unavailable" | "error"}.

    "ok" means the provider RETURNED AT LEAST ONE HIT — not merely that it
    failed to raise. That distinction is load-bearing: the keyless providers
    swallow their own transport failures (`DdgsProvider.search_ex` ends
    `except Exception: return []  # scraper failure → empty lane (graceful)`),
    so a dead network reaches this layer looking exactly like a clean empty
    SERP. Treating "did not raise" as success made a fully offline run report
    itself healthy. Omitting `outcomes` leaves behaviour byte-identical.
    """
    if not providers or not queries:
        return []

    def _mark(name: str, status: str) -> None:
        if outcomes is None:
            return
        prev = outcomes.get(name)
        # `prev is None` must be handled explicitly: defaulting an unseen
        # provider to "error" made the first "error" mark fail its own
        # strictly-greater test (0 > 0) and drop the row entirely.
        if prev is None or _OUTCOME_RANK[status] > _OUTCOME_RANK[prev]:
            outcomes[name] = status

    sem = asyncio.Semaphore(max(1, concurrency))

    async def _one(provider: Any, q: Any) -> list[Any]:
        async with sem:
            return await _call(provider, q)

    async def _call(provider: Any, q: Any) -> list[Any]:
        try:
            results = await acall(provider.search_ex, q)
        except NotImplementedError:
            # A provider that cannot run in THIS context (e.g. the host
            # WebSearch tool adapter invoked from a CLI subprocess) raises
            # NotImplementedError. Skip it explicitly so it can never starve the
            # fan-out — the surviving keyless providers carry the run. This is the
            # named contract the standalone/CLI path relies on (SPEC §13 failover).
            _mark(getattr(provider, "name", "?"), "unavailable")
            return []
        except Exception:
            _mark(getattr(provider, "name", "?"), "error")
            return []  # degrade: a dead provider drops out, never aborts the run
        _mark(getattr(provider, "name", "?"), "ok" if results else "empty")
        for i, r in enumerate(results):
            if not getattr(r, "serp_provider", ""):
                r.serp_provider = provider.name
            if not getattr(r, "serp_rank", 0):
                r.serp_rank = i + 1
        return list(results)

    tasks = [_one(p, q) for q in queries for p in providers]
    batches = await asyncio.gather(*tasks)
    hits: list[Any] = []
    for b in batches:
        hits.extend(b)
    return hits
