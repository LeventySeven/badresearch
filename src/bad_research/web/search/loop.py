"""retrieve_until_good — the keyless quality gate (dossier 13 §3.4).

Perplexity's failsafe rebuilt keyless: rerank scores feed the 0.70 threshold; if
<30% of candidates clear it, reformulate and re-fan, up to max_rounds. The loop
is pure — expand/fan_out/rerank are injected callables (no I/O here)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from urllib.parse import urlsplit

from bad_research.web.base import WebResult
from bad_research.web.search.base import KeylessSearchConfig

Expand = Callable[..., list[str]]                       # expand(question, findings=, gaps=) -> queries
FanOut = Callable[[list[str]], list[WebResult]]         # fan_out(queries) -> deduped pool
Rerank = Callable[[str, list[WebResult]], list[WebResult]]  # rerank(question, pool) -> pool w/ metadata["score"]


def _top(scored: list[WebResult], n: int) -> list[WebResult]:
    return sorted(scored, key=lambda r: r.metadata.get("score", 0.0), reverse=True)[:n]


def _infer_gaps(scored: list[WebResult]) -> list[str]:
    """DESIGNED: thin heuristic gap signal for re-expansion — the titles of the
    low-scoring half (the host-model expander turns these into reformulations)."""
    low = [r for r in scored if r.metadata.get("score", 0.0) < 0.5]
    return [r.title for r in low[:5] if r.title]


def _dedup_queries(queries: list[str], issued: set[str]) -> list[str]:
    """Within-run dedup guard. A query already fanned out this run is skipped
    rather than re-issued; new ones are recorded in `issued` (mutated in place).
    The plan's ideal key is (provider, args), but at this seam `fan_out` is opaque
    (`list[str] -> list[WebResult]` — provider routing happens inside it), so the
    query string is the granularity available and IS the key. Order-preserving,
    and it also collapses duplicates within a single round."""
    fresh: list[str] = []
    for q in queries:
        if q in issued:
            continue
        issued.add(q)
        fresh.append(q)
    return fresh


def _domain_of(url: str) -> str:
    """Lowercased host of a URL ('' when empty/unparseable) — the unit the
    saturation stop counts. Host-level, NOT PSL registrable-domain: `sub.a.com`
    and `a.com` count as distinct, which is the right signal here ("are results
    still coming from anywhere new?") and needs no public-suffix dependency."""
    if not url:
        return ""
    try:
        return (urlsplit(url).hostname or "").lower()
    except ValueError:
        return ""


def retrieve_until_good(question: str, *, cfg: KeylessSearchConfig,
                        expand: Expand, fan_out: FanOut, rerank: Rerank,
                        trace: dict[str, Any] | None = None) -> list[WebResult]:
    """≥ min_pass_fraction clear relevance_threshold → return; else reformulate +
    re-fan, ≤ max_rounds. Returns the best-effort passing set after the cap.

    A within-run dedup guard (`_dedup_queries`) skips any query already fanned out
    this run, so a reformulation that re-proposes an earlier query is not
    re-searched (keyless; query-string keyed at this seam).

    Two keyless terminators are checked each round, in order:
      1. QUALITY (unchanged): ≥ min_pass_fraction of the reranked pool clear
         relevance_threshold → return them.
      2. SATURATION (Perplexity's evidenced coverage stop, PD:3849-3855): when a
         round's NEW-distinct-domain ratio falls below cfg.sat_tau, further fan-out
         is returning mostly already-seen hosts, so stop. Pure counting, no
         scoring — the evidence-based replacement for the refuted "0.85 entropy"
         cutoff. Round 1 is never saturated (seen is empty → ratio 1.0), so at
         least one full round always runs.

    Pass a `trace` dict to record {"rounds_run", "stopped_reason"} (reason ∈
    {"quality","empty","saturation","exhausted","max_rounds"}); "exhausted" means a
    reformulation proposed only already-issued queries. It never changes the return.
    """

    def _record(rounds_run: int, reason: str) -> None:
        if trace is not None:
            trace["rounds_run"] = rounds_run
            trace["stopped_reason"] = reason

    queries = expand(question)
    passing: list[WebResult] = []
    seen_domains: set[str] = set()
    issued: set[str] = set()               # within-run dedup guard (see _dedup_queries)
    for _round in range(cfg.max_rounds):
        fresh = _dedup_queries(queries, issued)
        if not fresh:
            # every proposed query was already issued this run — no new ground to
            # cover. Return the best-effort set gathered so far rather than fanning
            # out an empty list (which would rerank [] and DROP the accumulated
            # `passing` via the not-scored branch). Best-effort > empty (docstring).
            _record(_round + 1, "exhausted")
            return passing
        pool = fan_out(fresh)
        domains = {d for r in pool if (d := _domain_of(r.url))}
        new_ratio = len(domains - seen_domains) / max(1, len(domains))
        seen_domains |= domains

        scored = rerank(question, pool)
        passing = [r for r in scored if r.metadata.get("score", 0.0) >= cfg.relevance_threshold]
        if scored and len(passing) >= cfg.min_pass_fraction * len(scored):
            _record(_round + 1, "quality")
            return passing                       # ≥30% cleared 0.70 → good enough
        if not scored:
            _record(_round + 1, "empty")
            return passing                       # nothing came back; nothing to reformulate from
        if new_ratio < cfg.sat_tau:
            _record(_round + 1, "saturation")
            return passing                       # new results stopped adding distinct domains → stop
        # <30% passed AND still finding fresh domains → reformulate and go wider.
        queries = expand(question, findings=_top(scored, 5), gaps=_infer_gaps(scored))
    _record(cfg.max_rounds, "max_rounds")
    return passing                               # best-effort after max_rounds
