"""Stage E — filter junk + redundancy, then STORE survivors to the vault.

1. Plan 05 postfetch_filter: junk/login-wall/paywall/language → drop (returns
   a reason str if junk, None if it passes).
2. Redundancy clustering: pages sharing > redundancy_overlap of their shingled
   content (Jaccard, n=3) are derivative — keep the first (canonical), discount
   the rest (dossier 10 §3.4: "N sources are really 1 source in N outfits").
   Reuses hyperresearch core/similarity.py (shingle/jaccard) verbatim.
3. Store survivors to the vault (disk/SQLite). The raw body lives ON DISK; it
   is what RetrievalEngine.index reads, never what the caller sees.

Returns list[Note] for Stage F — the EXACT type RetrievalEngine.index consumes
(it reads note.meta.{id,title,source,content_type} + note.body + note.path via
chunk_note). The vault seam exposes no load-by-id, so we build each Note inline
from the data already in hand at persist time (note_id from store_note + the
page's body/title/url) — see orchestrator Stage F. This keeps the funnel's
isolation contract (FakeVault stays a pure capture stub) while feeding the
engine real Note objects, not (note_id, body) tuples.
"""

from __future__ import annotations

from typing import Any

from bad_research.core.similarity import jaccard, shingle
from bad_research.models.note import Note, NoteMeta


def _is_prefetched(page: Any) -> bool:
    """A page whose body came from the provider, not from a fetch of ours."""
    return bool((getattr(page, "metadata", None) or {}).get("prefetched"))


def _prefetched_reject_reason(page: Any) -> str | None:
    """The junk floor a PREFETCHED body still has to clear.

    Exactly ONE junk verdict is wrong for content nobody fetched: the <300-char
    length rule, which exists to catch a failed fetch and reads a 200-character
    Reddit comment with 1,485 upvotes as truncated. So we lower that floor to 1
    and keep the rest — an EMPTY body is still junk (the engine documents its
    summary as possibly empty, and an empty body is exempt from the content-hash
    collapse, so it reached the vault as a zero-byte note), and so are a bot
    wall, an error page and binary garbage.

    The login-wall / paywall / language gates stay off: those read the SHAPE of
    a fetch, and nothing was fetched here.

    KNOWN COLLATERAL, deliberately not fixed here. The bot-wall and error-page
    rules keyword-match the body, so a thread ABOUT one reads as one: "Cloudflare
    outage megathread" is dropped as a bot wall, and a dev thread containing "an
    error occurred" as an error page (both measured). Exempting those rules for
    prefetched bodies was tried and reverted — it breaks the deliberate contract
    that a bot wall the ENGINE hit must still die, which is a real failure this
    lane has to catch. The right fix is narrowing the signals themselves (a bare
    brand name is a poor bot-wall signal), which is a change to the fetched path
    for every provider and belongs in its own review, not smuggled in here.
    """
    reason: str | None = page.looks_like_junk(min_chars=1)
    return reason


def filter_and_store(
    pages: list[Any],
    *,
    vault: Any,
    postfetch_filter: Any,
    redundancy_overlap: float,
    shingle_n: int,
) -> list[Note]:
    # 1. Junk filter (Plan 05). A prefetched body gets the same content floor
    #    minus the one fetch-specific rule (<300 chars) — never a free pass.
    clean = [
        p for p in pages
        if (_prefetched_reject_reason(p) if _is_prefetched(p) else postfetch_filter(p)) is None
    ]

    # 2. Redundancy clustering (brute Jaccard over shingles, n=3).
    kept: list[Any] = []
    kept_shingles: list[set[str]] = []
    for p in clean:
        body = getattr(p, "content", "") or ""
        sh = shingle(body, n=shingle_n)
        is_derivative = any(
            jaccard(sh, prev) > redundancy_overlap for prev in kept_shingles
        )
        if is_derivative:
            continue   # discount the derivative; the canonical is already kept
        kept.append(p)
        kept_shingles.append(sh)

    # 3. Store survivors to the vault (raw body -> disk) AND build the Note Stage F
    #    will index. Persistence stays the source of truth on disk; the in-hand Note
    #    mirrors exactly what was persisted (same note_id, body, title, url).
    stored: list[Note] = []
    for p in kept:
        body = getattr(p, "content", "") or ""
        url = p.url
        title = getattr(p, "title", "") or url
        provider = getattr(p, "serp_provider", "") or "fetch"
        note_id = vault.store_note(title=title, body=body, url=url, provider=provider)
        # Build the Note from the persisted facts. chunk_note reads meta.{id,title,
        # source,content_type} + body + path; content_type is left None (prose) — the
        # funnel reads web pages, not source code, so the prose chunker is correct.
        note = Note(
            meta=NoteMeta(title=title, id=note_id, source=url, fetch_provider=provider),
            body=body,
            path=f"research/notes/{note_id}.md",
        )
        stored.append(note)
    return stored
