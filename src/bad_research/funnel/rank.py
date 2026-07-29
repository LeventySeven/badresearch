"""Stage C — rank un-read candidates (the cheap-search -> expensive-read gate).

Two cheap signals, NO fetch:
  1. RRF k=60 over every (query, provider) rank list (INTERFACES.md; Exa/LanceDB
     canon) — provider agreement AND query agreement, not one rank per provider.
  2. 6-dimension utility score, max composite 18 (dossier 10 §3.2,
     hyperresearch width-sweep §2.3): Authority, Novelty, Stance, Coverage,
     Redundancy, Freshness — each 0-3.

This module imports NOTHING from the read/fetch layer: the whole point is that
ranking is free and happens before any expensive read.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

# Authority by domain class (dossier 10 §3.2 dim 1; quality DOMAIN_TIER spirit).
_PRIMARY = ("sec.gov", "edgar", "europa.eu", "gov.uk", ".gov", "arxiv.org",
            "ncbi.nlm.nih.gov", "doi.org", "semanticscholar.org")
_INSTITUTIONAL = ("reuters.com", "bloomberg.com", "ft.com", "nature.com",
                  "ieee.org", "acm.org", "wsj.com", "economist.com")
_BLOG = ("wordpress.com", "blogspot.com", "medium.com", "substack.com",
         "tumblr.com")


def rrf_fuse(provider_ranks: dict[str, int], *, k: int = 60) -> float:
    """Reciprocal Rank Fusion across provider rank lists. Rank 0 = unknown,
    contributes nothing (don't let an unranked hit score 1/k)."""
    total = 0.0
    for rank in provider_ranks.values():
        if rank and rank > 0:
            total += 1.0 / (k + rank)
    return total


def rrf_fuse_lists(rank_lists: dict[str, list[int]], *, k: int = 60) -> float:
    """RRF over EVERY observed rank, not one rank per provider.

    Textbook RRF fuses a set of ranked lists; in this funnel one list is one
    (query, provider) SERP, and the fan-out issues ~100 queries against each
    provider. Summing 1/(k+rank) over every sighting is therefore the correct
    fusion — and it restores the signal dedup used to throw away: a URL that
    every query surfaced at rank 1 now scores ~m/(k+1) against 1/(k+1) for a URL
    one query surfaced once, instead of the two tying exactly (issue #40).

    Consensus is deliberately UNCAPPED: appearing in every list of a 100-query
    plan is the strongest un-read relevance evidence the funnel can observe, and
    RRF's own 1/(k+rank) damping already bounds each sighting's contribution.
    """
    total = 0.0
    for ranks in rank_lists.values():
        for rank in ranks:
            if rank and rank > 0:
                total += 1.0 / (k + rank)
    return total


def _authority(domain: str) -> int:
    d = domain.lower()
    if any(p in d for p in _PRIMARY):
        return 3
    if any(p in d for p in _INSTITUTIONAL):
        return 2
    if any(p in d for p in _BLOG):
        return 0
    return 1  # default: quality journalism / unknown


def utility_score(candidate: Any, query: str) -> int:
    """6-dim utility, 0-3 each, max 18 (dossier 10 §3.2). Operates only on
    un-read SERP signals (domain, title/snippet, provider spread, recency)."""
    r = candidate.result
    domain = urlsplit(candidate.canonical_url).netloc.lower()
    title = (getattr(r, "title", "") or "").lower()
    meta = getattr(r, "metadata", {}) or {}
    q_terms = {t for t in query.lower().split() if len(t) > 2}

    authority = _authority(domain)

    # Novelty: how many distinct providers surfaced it (broad surfacing => less novel
    # niche; single-provider niche domains => more novel). Cap 3.
    n_prov = len(candidate.provider_ranks)
    novelty = 3 if n_prov == 1 else (1 if n_prov == 2 else 0)

    # Stance diversity: adversarial/critical signals in the title.
    adversarial = ("criticism", "limitations", "problems with", "against",
                   "debunk", "fails", "wrong")
    stance = 3 if any(a in title for a in adversarial) else 1

    # Coverage: title term overlap with the query (proxy for on-topic-ness).
    overlap = len(q_terms & set(title.split()))
    coverage = min(3, overlap)

    # Redundancy: penalize obvious aggregator/rewrite signals.
    redundancy = 0 if any(s in title for s in ("roundup", "everything you need", "explained")) else 2

    # Freshness: from metadata recency if present, else neutral.
    days = meta.get("age_days")
    if days is None:
        freshness = 1
    elif days <= 365:
        freshness = 3
    elif days <= 365 * 3:
        freshness = 2
    else:
        freshness = 1

    return authority + novelty + stance + coverage + redundancy + freshness


def rank_candidates(candidates: list[Any], query: str, *, rrf_k: int = 60) -> list[Any]:
    """Order candidates descending by (RRF + normalized utility). Pure: no read.

    Composite = rrf_fuse(...) + utility/18 * (1/k-scale) so utility breaks RRF
    ties without dominating the parameter-free fusion. We weight RRF as primary
    (it is the multi-provider recall signal) and utility as the quality tiebreak.

    The RRF term prefers `provider_rank_lists` (every (query, provider) sighting)
    and falls back to `provider_ranks` (one rank per provider) when the lists are
    absent — hand-built Candidates and any caller that only fills the flat dict
    keep their exact previous score.
    """
    def composite(c: Any) -> float:
        rank_lists = getattr(c, "provider_rank_lists", None)
        rrf = (rrf_fuse_lists(rank_lists, k=rrf_k) if rank_lists
               else rrf_fuse(c.provider_ranks, k=rrf_k))
        util = utility_score(c, query) / 18.0
        # RRF dominates; utility scaled into RRF's magnitude (~1/61) as tiebreak.
        return rrf + util * (1.0 / rrf_k)

    return sorted(candidates, key=composite, reverse=True)
