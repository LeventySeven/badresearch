"""Stage A→B dedup — URL-canonical + content-hash, $0, no model.

URL-canonical collapse uses canonicalize_url (Firecrawl-style). Content-hash
collapse uses sha256(content)[:16] (matches core/fetcher.py:137) to catch
mirror/syndicated pages with different URLs but identical bodies.

Output: list[Candidate] — the un-read candidate pool. Each Candidate carries
the SERP signals (provider_ranks + provider_rank_lists) the rank stage (Stage C)
fuses via RRF.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from bad_research.funnel.canonical import canonicalize_url
from bad_research.funnel.recency import stamp_age


@dataclass
class Candidate:
    """An un-read search hit. The funnel ranks these BEFORE fetching (Stage C)."""

    canonical_url: str
    result: Any                          # the representative WebResult (un-read SERP shape)
    provider_ranks: dict[str, int] = field(default_factory=dict)  # provider -> FIRST 1-based rank
    # provider -> EVERY 1-based rank this URL was seen at, across all queries.
    # `provider_ranks` keeps one entry per DISTINCT provider (rank.py's Novelty
    # dimension counts it); this keeps the full multiset so Stage C can fuse
    # ACROSS THE QUERY PLAN, not just across providers. A URL that every one of
    # the ~100 fan-out queries surfaced at rank 1 must out-score a URL one query
    # surfaced once — before this field they scored identically (issue #40).
    provider_rank_lists: dict[str, list[int]] = field(default_factory=dict)
    # Age in days since publication, computed at build from result.metadata['year']
    # and/or the content layer's published_date. None ⇒ undatable (gate passes it,
    # rank scores it neutral). Read by quality/prefilter.py::passes_recency_gate.
    published_days_ago: int | None = None

    @property
    def url(self) -> str:
        return self.canonical_url


def _content_hash(content: str) -> str:
    return hashlib.sha256((content or "").encode("utf-8")).hexdigest()[:16]


def _is_prefetched(result: Any) -> bool:
    """Did this hit arrive with the body its provider had already read?"""
    return bool((getattr(result, "metadata", None) or {}).get("prefetched"))


def _stamp_candidate_age(cand: Candidate, today: date | datetime | None) -> None:
    """Compute age_days from the survivor's WebResult and stamp BOTH consumers.

    Writes `result.metadata['age_days']` (read by funnel/rank.py Freshness) and
    `cand.published_days_ago` (read by quality/prefilter.py recency gate). The
    age comes from metadata['year'] and/or an ISO published_date the content
    layer may have stashed in metadata['published_date'].
    """
    meta = getattr(cand.result, "metadata", None)
    if not isinstance(meta, dict):
        return
    published = meta.get("published_date") or meta.get("date")
    age = stamp_age(meta, today=today, published_date=published)
    cand.published_days_ago = age


def dedup(hits: list[Any], *, today: date | datetime | None = None) -> list[Candidate]:
    """Collapse raw fan-out hits into the candidate pool.

    Stage 1: URL-canonical dedup (cosmetic variants → one).
    Stage 2: content-hash dedup (mirrors/syndication → one).
    Provider ranks from every duplicate are merged onto the survivor.

    Each survivor is dated: age_days is computed from its WebResult's date
    signals and stamped onto BOTH result.metadata['age_days'] (rank.py) and
    Candidate.published_days_ago (recency gate). `today` is injected for
    determinism (defaults to UTC today only when omitted).
    """
    by_url: dict[str, Candidate] = {}
    for h in hits:
        cu = canonicalize_url(h.url)
        prov = getattr(h, "serp_provider", "") or "unknown"
        rank = getattr(h, "serp_rank", 0) or 0
        if cu in by_url:
            # keep first-seen representative; merge this provider's rank
            existing = by_url[cu]
            if prov not in existing.provider_ranks:
                existing.provider_ranks[prov] = rank
            # ...but NEVER discard the repeat: every (query, provider) SERP is its
            # own ranked list, so a repeat sighting is real fusion evidence.
            if rank > 0:
                existing.provider_rank_lists.setdefault(prov, []).append(rank)
            # First-seen wins EXCEPT on the one asymmetry that matters: a hit that
            # already carries its body beats a snippet. Base lanes are fanned before
            # the verticals, so for any popular thread the snippet is seen first and
            # the prefetched body would be thrown away — after which Stage D refetches
            # the permalink into a login wall and Stage E drops it as junk. The merged
            # SERP signals above stay on the Candidate; only the body changes hands.
            if _is_prefetched(h) and not _is_prefetched(existing.result):
                existing.result = h
        else:
            by_url[cu] = Candidate(canonical_url=cu, result=h,
                                   provider_ranks={prov: rank} if rank else {prov: 0},
                                   provider_rank_lists={prov: [rank]} if rank > 0 else {})

    # Stage 2 — content-hash collapse across distinct URLs.
    by_hash: dict[str, Candidate] = {}
    out: list[Candidate] = []
    for cand in by_url.values():
        body = getattr(cand.result, "content", "") or ""
        # Pages with no body yet (snippet-only) can't be content-deduped; keep them.
        if not body.strip():
            out.append(cand)
            continue
        ch = _content_hash(body)
        if ch in by_hash:
            # merge provider ranks onto the canonical survivor, drop the mirror
            survivor = by_hash[ch]
            for p, r in cand.provider_ranks.items():
                survivor.provider_ranks.setdefault(p, r)
            # The mirror occupied its own slot in every list that surfaced it —
            # that is the same page being corroborated, so the ranks accumulate.
            for p, rl in cand.provider_rank_lists.items():
                survivor.provider_rank_lists.setdefault(p, []).extend(rl)
        else:
            by_hash[ch] = cand
            out.append(cand)

    # Date every survivor (writes metadata['age_days'] + Candidate.published_days_ago).
    for cand in out:
        _stamp_candidate_age(cand, today)
    return out
