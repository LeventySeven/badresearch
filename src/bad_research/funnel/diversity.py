"""Stage C.5 — pool diversity guards. Pure, stdlib-only, no I/O, no model.

Runs between the rank (Stage C) and the pool cap, so the ~120 candidates that
reach the read budget are spread across hosts and provider lanes instead of
being owned by whichever domain the fan-out happened to flood.

BOTH guards only RE-ORDER. Nothing here drops a candidate: the pool cap in
`diversify_pool` is the single place a candidate is cut, and it always cuts the
lowest-ranked survivors of the re-ordering. That matters because Stage D reads
`ranked[:read_top_k]` (funnel/read.py) — position in the head, not membership in
the pool, is what actually buys a read. A guard that DROPPED instead would
starve a legitimately single-domain topic (every hit on reuters.com would leave
a pool of 3).

Ported from mvanhorn/last30days' `_MAX_ITEMS_PER_AUTHOR = 3` / `_diversify_pool`.
That repo caps per social-post AUTHOR; a funnel Candidate (funnel/dedup.py) has
no author field because these are general web pages, so the honest translation
is the URL's netloc — one loud DOMAIN is what "one prolific source owns the
pool" means here.

NOT ported: last30days' `_DIVERSITY_RELEVANCE_THRESHOLD = 0.25`, which gates a
lane's reservation on its best item's `local_relevance`. This funnel has no
per-candidate relevance score before the read; the only absolute signal is
`utility_score`, and a 0.25 floor over `utility_score/18` would be worse than
useless here — its Novelty dimension awards 3 to a single-provider hit and 0 to
a 3+-provider one (rank.py), so the floor is unreachable for any single-provider
candidate (arithmetic minimum 5/18 = 0.278) and can ONLY ever fire on a
multi-provider one, i.e. it would reject exactly the best-corroborated results.
The absolute quality floor the port was reaching for already exists upstream and
already runs before the rank: Stage B.6's blocklist + SEO-farm gate.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from bad_research.quality.prefilter import _SEO_EXEMPT_TIERS as _AUTHORITY_TIERS
from bad_research.quality.prefilter import domain_tier


def _netloc(candidate: Any) -> str:
    return urlsplit(getattr(candidate, "canonical_url", "") or "").netloc.lower()


def _providers_of(candidate: Any) -> list[str]:
    """The lanes that surfaced this candidate (falls back to the SERP stamp)."""
    provs = [p for p in (getattr(candidate, "provider_ranks", None) or {}) if p]
    if provs:
        return provs
    one = getattr(getattr(candidate, "result", None), "serp_provider", "") or ""
    return [one] if one else []


def cap_per_domain(ranked: list[Any], *, max_per_domain: int) -> list[Any]:
    """Demote every candidate past `max_per_domain` for its netloc to the TAIL.

    Rank order is preserved within both the head and the demoted tail, and no
    candidate is dropped — a topic that genuinely lives on one host still fills
    the pool, it just no longer gets the whole read budget by default.

    Authority lanes (primary/docs/reference — .gov, arxiv.org, wikipedia.org,
    docs.*) are EXEMPT from the cap, mirroring the exemption Stage B.6 already
    applies: many pages from one .gov or one arXiv is the shape of a good
    corpus, not a flood. Without it the intent-routed scholarly verticals — which
    all live on one host and deliberately bypass the p_providers cap — would be
    cut to `max_per_domain` papers per run.
    """
    if max_per_domain <= 0:
        return list(ranked)
    seen: dict[str, int] = {}
    head: list[Any] = []
    tail: list[Any] = []
    for c in ranked:
        if domain_tier(getattr(c, "canonical_url", "") or "").name in _AUTHORITY_TIERS:
            head.append(c)
            continue
        host = _netloc(c)
        n = seen.get(host, 0)
        if n >= max_per_domain:
            tail.append(c)
            continue
        seen[host] = n + 1
        head.append(c)
    return head + tail


def diversify_pool(ranked: list[Any], *, limit: int,
                   min_per_provider: int = 2) -> list[Any]:
    """Reserve `min_per_provider` head slots per provider, then cap to `limit`.

    A lane that returned few hits — most importantly an intent-routed vertical,
    whose handful of arXiv/OpenAlex results are corroborated by far fewer queries
    than a mainstream URL and so score low under consensus RRF — is guaranteed
    its best `min_per_provider` candidates in the head of the pool, where the
    read budget can actually reach them. Everything else follows in rank order.
    """
    if limit <= 0:
        return []
    reserved_idx: list[int] = []
    if min_per_provider > 0:
        taken: dict[str, int] = {}
        for i, c in enumerate(ranked):
            if len(reserved_idx) >= limit:
                break
            provs = _providers_of(c)
            if not any(taken.get(p, 0) < min_per_provider for p in provs):
                continue
            for p in provs:
                taken[p] = taken.get(p, 0) + 1
            reserved_idx.append(i)
    chosen = list(reserved_idx)
    seen = set(reserved_idx)
    for i in range(len(ranked)):
        if len(chosen) >= limit:
            break
        if i not in seen:
            chosen.append(i)
    return [ranked[i] for i in chosen[:limit]]
