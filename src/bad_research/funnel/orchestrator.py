"""gather() — the public funnel entry point. Wires Stage A→B→C→D→E→F.

INVARIANT: callers receive list[Chunk] (reranked top chunks) + [[note-id]]
pointers — NEVER raw page bodies. Sources scale (12→80 notes); context stays
flat (~5-15k tokens) because only Stage-F chunks ever cross into the prompt.

Stages A-E run at $0 model cost. The seams (providers/fetch_tiered/postfetch_
filter/RetrievalEngine/vault) are injected via FunnelDeps so the funnel logic
is testable in isolation; the width-sweep skill backend (Plan 08) assembles the
real wiring. Every SYNCHRONOUS seam (search_ex, fetch_tiered) is reached through
funnel._async.acall inside fan_out / read_top_k.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Literal

from bad_research.funnel.config import FunnelConfig
from bad_research.funnel.dedup import dedup
from bad_research.funnel.fanout import fan_out, plan_queries
from bad_research.funnel.filter import filter_and_store
from bad_research.funnel.rank import rank_candidates
from bad_research.funnel.read import read_top_k
from bad_research.quality.prefilter import (
    SEO_FARM_BLOCK_THRESHOLD,
    _SEO_EXEMPT_TIERS,
    domain_tier,
    is_blocklisted,
    passes_recency_gate,
    seo_farm_score,
)


@dataclass
class FunnelDeps:
    """The cross-plan seams the funnel composes (all behind Protocols).

    providers:        list[WebSearchProvider]  (Plan 03 cascade survivors)
    fetcher:          obj with async fetch_tiered(url, *, tier_max, ...) (Plan 04)
    postfetch_filter: callable(WebResult) -> str | None  (Plan 05)
    vault:            obj with store_note(*, title, body, url, provider) -> note_id
    retrieval:        RetrievalEngine (Plan 02) - .index(notes), .search(q, mode, top_k)
    """

    providers: list[Any]      # list[WebSearchProvider]
    fetcher: object           # has: async fetch_tiered(url, *, tier_max, ...)
    postfetch_filter: object  # callable(WebResult) -> str | None
    vault: object             # has: store_note(*, title, body, url, provider) -> note_id
    retrieval: object         # RetrievalEngine: .index(notes), .search(q, *, mode, top_k)


def recency_gate(candidates: list[Any], *, max_age_days: int | None) -> list[Any]:
    """Stage B.5 — drop candidates staler than the query's recency window.

    Wires the previously-orphaned quality/prefilter recency machinery into the
    funnel: each funnel Candidate's `published_days_ago` (stamped at dedup) is
    tested against `max_age_days` via the existing `passes_recency_gate`, which
    honors RECENCY_MAX_AGE_DAYS' tiers — primaries are exempt, undatable hits
    pass, evergreen (max_age_days is None) is a no-op. Stale sources are dropped
    here so they never even reach the read budget.
    """
    if max_age_days is None:
        return candidates              # evergreen / no recency window → no-op
    kept: list[Any] = []
    for c in candidates:
        tier = domain_tier(c.url)
        age = getattr(c, "published_days_ago", None)
        if passes_recency_gate(age, tier.name, max_age_days):
            kept.append(c)
    return kept


def prefetch_garbage_gate(candidates: list[Any], query: str) -> list[Any]:
    """Stage B.6 — drop garbage sources BEFORE they can spend a read.

    Wires the previously-orphaned quality/prefilter pre-fetch machinery into the
    funnel: a candidate is dropped when its URL is blocklisted (Pinterest/Quora/
    Scribd/… + tag/category/page paths) OR — for non-authority tiers only — its
    SERP snippet trips the deterministic SEO-farm classifier
    (`seo_farm_score >= SEO_FARM_BLOCK_THRESHOLD`, i.e. listicle + clickbait +
    money-page + thin/stuffed signals). Primary/docs/reference tiers are exempt
    from the SEO gate exactly as `prefetch_filter` does, so a spammy-looking
    headline on a .gov/docs page never gets a real source rejected.

    The snippet comes from the un-read WebResult's SERP body (`result.content`),
    falling back to its title when the provider returned no snippet. Pure and
    deterministic (regex + set membership); no network, microseconds/candidate.
    Runs after the recency gate and before the pool cap so garbage never even
    fills the candidate pool.
    """
    kept: list[Any] = []
    for c in candidates:
        if is_blocklisted(c.url):
            continue
        tier = domain_tier(c.url)
        if tier.name not in _SEO_EXEMPT_TIERS:
            r = getattr(c, "result", None)
            snippet = (getattr(r, "content", "") or "").strip() or (
                getattr(r, "title", "") or "")
            if seo_farm_score(c.url, snippet, query) >= SEO_FARM_BLOCK_THRESHOLD:
                continue
        kept.append(c)
    return kept


async def gather(
    query: str,
    *,
    mode: Literal["light", "full"],
    deps: FunnelDeps,
    queries: list[Any] | None = None,
    recency_max_age_days: int | None = None,
    today: date | datetime | None = None,
) -> list[Any]:
    """Run the six-stage funnel and return reranked Chunk[] (never raw pages).

    `queries` (optional): a caller-supplied lens-driven SearchQuery plan
    (the width-sweep skill passes its 3-lens A/B/C/D plan). When omitted we fall
    back to plan_queries (deterministic expansion).

    `recency_max_age_days` (optional): the query's freshness window (one of the
    RECENCY_MAX_AGE_DAYS tiers, e.g. 7 breaking / 180 current / None evergreen).
    When set, Stage B.5 drops candidates older than the window (primaries exempt).
    `today` is injected into dedup's age computation for deterministic dating.
    """
    cfg = FunnelConfig.for_mode(mode)

    # ── Stage A — FAN-OUT (parallel, cheap, never near the model) ──────────
    if queries is None:
        queries = plan_queries(query, m_queries=cfg.m_queries, k_per_query=cfg.k_per_query)
    active_providers = deps.providers[: cfg.p_providers]
    raw_hits = await fan_out(queries, active_providers)

    # ── Stage B — DEDUP (URL-canonical + content-hash, free) ───────────────
    # dedup also DATES each survivor (metadata['age_days'] + published_days_ago).
    candidates = dedup(raw_hits, today=today)

    # ── Stage B.5 — RECENCY GATE (drop stale sources per the query window) ──
    candidates = recency_gate(candidates, max_age_days=recency_max_age_days)

    # ── Stage B.6 — GARBAGE GATE (blocklist + SEO farm; primaries exempt) ───
    # Reject blocklisted domains + SEO listicles BEFORE the pool cap so garbage
    # never fills the pool or spends one of the ≤80 reads.
    candidates = prefetch_garbage_gate(candidates, query)

    candidates = candidates[: cfg.candidate_pool]   # cap the pool

    # ── Stage C — RANK un-read candidates (RRF k=60 + utility) ─────────────
    ranked = rank_candidates(candidates, query, rrf_k=cfg.rrf_k)

    # ── Stage D — READ top-K (≤80 ceiling, batched, chained-crawl) ─────────
    pages = await read_top_k(
        ranked,
        fetcher=deps.fetcher,
        read_top_k=cfg.read_top_k,
        concurrency=cfg.read_concurrency,
        max_chain_depth=cfg.max_chain_depth,
        max_links_per_hub=cfg.max_links_per_hub,
        query=query,
        ceiling=FunnelConfig.READ_CEILING,
    )

    # ── Stage E — FILTER (junk + >60% redundancy) + STORE to vault ─────────
    # `notes` is list[Note] — the EXACT type Stage F's RetrievalEngine.index
    # consumes. filter_and_store persists each survivor to disk (raw body) AND
    # returns the in-hand Note mirroring it, so Stage F never sees a raw tuple.
    notes = filter_and_store(
        pages,
        vault=deps.vault,
        postfetch_filter=deps.postfetch_filter,
        redundancy_overlap=cfg.redundancy_overlap,
        shingle_n=cfg.shingle_n,
    )
    if not notes:
        return []   # honest gap, never hallucinate (SPEC §13)

    # ── Stage F — RERANK chunks via RetrievalEngine -> top set ─────────────
    # The vault holds the breadth (raw bodies on disk); the engine indexes the
    # Notes and returns only the reranked top chunks the model will see.
    # deps.retrieval is a duck-typed Protocol (RetrievalEngine) resolved at
    # wiring time (Plan 08); typed `object` here for isolation -> ignore attr.
    deps.retrieval.index(notes)  # type: ignore[attr-defined]
    chunks: list[Any] = deps.retrieval.search(  # type: ignore[attr-defined]
        query, mode=mode, top_k=cfg.top_chunks)
    return chunks
