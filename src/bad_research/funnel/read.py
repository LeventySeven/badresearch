"""Stage D — read ONLY the top-K ranked candidates (≤80 ceiling), batched.

The cheap-search -> expensive-read gate pays off here: we fetch the Stage-C
winners and NEVER the full pool. The ~80-read ceiling is load-bearing
(dossier 10 §3.3: reading past it degrades synthesis) and enforced even if a
caller misconfigures read_top_k.

Reads run through fetch_tiered (Plan 04, the Tier 0->3 escalation ladder),
wrapped in funnel._async.acall (the real fetch_tiered is SYNCHRONOUS), bounded
by an asyncio.Semaphore (read_concurrency 10-12 full / 3-5 light).

Chained crawl (browse_page pattern, dossier 10 §2.2): a hub page's outbound
links are ranked by a free JS-cosine score against the query and the top
max_links_per_hub are queued, depth <= max_chain_depth; queued links re-enter
the seen-set so they are never double-read.
"""

from __future__ import annotations

import asyncio
import math
import re
from collections import Counter
from typing import Any

from bad_research.funnel._async import acall

_DEFAULT_CEILING = 80

# Failed URLs are a diagnostic, not a dataset. The count is the load-bearing
# number; the sample exists so a human can see WHICH hosts refused us without the
# envelope growing by 80 URLs on a fully-blocked run.
_MAX_RECORDED_FAILED_URLS = 10


def _js_cosine(query: str, text: str) -> float:
    """Firecrawl-style pure-JS bag-of-words cosine (dossier 10 §2.2 / FC §28.6).
    No embedding model — tokenize on \\W+, count, dot/magnitudes. Dirt cheap."""
    qt = [t for t in re.split(r"\W+", query.lower()) if t]
    dt = [t for t in re.split(r"\W+", text.lower()) if t]
    if not qt or not dt:
        return 0.0
    qc, dc = Counter(qt), Counter(dt)
    common = set(qc) & set(dc)
    dot = sum(qc[t] * dc[t] for t in common)
    qmag = math.sqrt(sum(v * v for v in qc.values()))
    dmag = math.sqrt(sum(v * v for v in dc.values()))
    return dot / (qmag * dmag) if qmag and dmag else 0.0


def _rank_hub_links(query: str, links: list[dict[str, Any]], limit: int) -> list[str]:
    """Rank a hub's outbound links by JS-cosine of (anchor text) vs query, keep top `limit`."""
    scored: list[tuple[float, str]] = []
    for ln in links:
        href = ln.get("href") or ""
        if not href.startswith("http"):
            continue
        text = (ln.get("text") or "") + " " + href
        scored.append((_js_cosine(query, text), href))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [href for _, href in scored[:limit]]


async def read_top_k(
    ranked: list[Any],
    *,
    fetcher: Any,
    read_top_k: int,
    concurrency: int,
    max_chain_depth: int,
    max_links_per_hub: int,
    query: str = "",
    ceiling: int = _DEFAULT_CEILING,
    outcomes: dict[str, Any] | None = None,
) -> list[Any]:
    """Read the top candidates via fetch_tiered, batched + chained.

    Returns the list of read WebResults (junk not yet filtered — Stage E does
    that). Never reads more than min(read_top_k, ceiling) primary candidates;
    chained-crawl children also count against the same read budget.

    `outcomes` (optional, opt-in like `fan_out`'s): when a dict is passed it is
    filled with {"n_fetch_attempted", "n_fetch_failed", "failed_urls"}. A run
    where 60 of 80 reads 403'd was previously byte-identical in the envelope to
    one where 60 pages were genuinely thin — the read-stage half of issue #39.
    Omitting it leaves behaviour byte-identical.
    """
    if outcomes is not None:
        outcomes.setdefault("n_fetch_attempted", 0)
        outcomes.setdefault("n_fetch_failed", 0)
        outcomes.setdefault("failed_urls", [])
    budget = min(read_top_k, ceiling)
    sem = asyncio.Semaphore(max(1, concurrency))
    seen: set[str] = set()
    results: list[Any] = []
    reads_done = 0
    lock = asyncio.Lock()

    async def _fetch(url: str) -> Any:
        async with sem:
            if outcomes is not None:
                outcomes["n_fetch_attempted"] += 1
            try:
                return await acall(fetcher.fetch_tiered, url, tier_max=1)
            except Exception:
                # A single page's fetch failure (403/paywall/timeout/parse error)
                # must NEVER abort the whole read wave — asyncio.gather would
                # propagate the first exception and zero the run. Degrade to
                # "skip this URL"; the survivors carry the funnel (the same
                # failover contract fan_out applies per-provider, SPEC §13).
                #
                # Degrading SILENTLY was the defect: count it, so a corpus that
                # is short because the web refused us is distinguishable from a
                # corpus that is short because the topic is thin (issue #39).
                # No await between the read and the write, so the increment is
                # atomic on the single-threaded event loop.
                if outcomes is not None:
                    outcomes["n_fetch_failed"] += 1
                    if len(outcomes["failed_urls"]) < _MAX_RECORDED_FAILED_URLS:
                        outcomes["failed_urls"].append(url)
                return None

    async def _claim(url: str) -> bool:
        """Take one read from the budget for `url`, or refuse it (already seen,
        or the budget is spent)."""
        nonlocal reads_done
        async with lock:
            if url in seen or reads_done >= budget:
                return False
            seen.add(url)
            reads_done += 1
            return True

    async def _try_read(url: str) -> Any:
        return await _fetch(url) if await _claim(url) else None

    async def _read_candidate(cand: Any) -> Any:
        """Fetch the candidate, unless it already arrived with its body.

        A prefetched candidate comes from a provider that had already read the
        content at SERP time (the social lane: the thread, its top comments, the
        transcript). Re-fetching its permalink is worse than useless — reddit.com
        and x.com answer an anonymous fetch with a login wall, which Stage E then
        drops as junk, so the evidence would be gathered and discarded one stage
        later. It still spends a read from the budget: the budget bounds how much
        content enters the corpus, not how many HTTP calls we make.
        """
        result = getattr(cand, "result", None)
        if not (getattr(result, "metadata", None) or {}).get("prefetched"):
            return await _try_read(cand.canonical_url)
        return result if await _claim(cand.canonical_url) else None

    # Primary wave: the top-budget ranked candidates, batched.
    primaries = ranked[:budget]
    primary_results = await asyncio.gather(*[_read_candidate(c) for c in primaries])
    results.extend(r for r in primary_results if r is not None)

    # Chained crawl: follow the best outbound links of hub pages, bounded.
    if max_chain_depth > 0 and max_links_per_hub > 0:
        frontier = list(results)
        depth = 1
        while frontier and depth <= max_chain_depth:
            next_frontier: list[Any] = []
            queued: list[str] = []
            for page in frontier:
                links = getattr(page, "links", []) or []
                # A page with no outbound links is a leaf, not a hub: skip it.
                # Pages with links (hub-like or merely linky) get their top
                # max_links_per_hub followed (the per-hub fan-out cap is the
                # binding bound on the chained crawl, not a link-count floor).
                if not links:
                    continue
                for href in _rank_hub_links(query, links, max_links_per_hub):
                    if href not in seen:
                        queued.append(href)
            # read queued links under the SAME budget; re-dedup via seen-set
            child_results = await asyncio.gather(*[_try_read(u) for u in queued])
            for cr in child_results:
                if cr is not None:
                    results.append(cr)
                    next_frontier.append(cr)
            frontier = next_frontier
            depth += 1

    return results
