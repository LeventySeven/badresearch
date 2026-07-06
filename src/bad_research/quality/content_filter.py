"""Stage 2 — post-fetch content filtering (dossier 07 §2).

Reuses hyperresearch's two verbatim gates (WebResult.looks_like_junk /
looks_like_login_wall, base.py:32-118) and ADDS the paywall + language gates
(dossier 07 §2.2). No LLM. Boilerplate strip (BS4 §2.3) happens in the fetcher
before this runs; this is the keep/drop decision layer.
"""

from __future__ import annotations

from bad_research.web.base import WebResult

# Re-export the verbatim hyperresearch gates so callers import one module (dossier 07 §8).
# (They live as WebResult methods; we expose function aliases for symmetry.)
__all__ = [
    "looks_like_junk",
    "looks_like_login_wall",
    "looks_like_paywall",
    "postfetch_filter",
    "postfetch_reject_reason",
]


def looks_like_login_wall(result: WebResult, original_url: str | None = None) -> bool:
    return result.looks_like_login_wall(original_url or result.url)


def looks_like_junk(result: WebResult) -> str | None:
    return result.looks_like_junk()


# --- Paywall gate (dossier 07 §2.2) — distinct from login wall ---

_PAYWALL_SIGNALS = (
    "subscribe to read", "subscribers only", "this article is for subscribers",
    "metered", "to continue reading", "unlock this article",
    "sign up to read the full",
)
PAYWALL_CONTENT_FLOOR = 1500  # chars; below this + a paywall marker -> paywall


def looks_like_paywall(result: WebResult) -> bool:
    """True if the page is a short paywall teaser (dossier 07 §2.2).

    These fall through looks_like_junk because they're >300 chars and lack the
    exact cookie/login strings.
    """
    content = result.content or ""
    if len(content.strip()) >= PAYWALL_CONTENT_FLOOR:
        return False
    low = content.lower()
    return any(s in low for s in _PAYWALL_SIGNALS)


# --- Language gate (dossier 07 §2.2) — off-language is pure context bloat ---

def _detect_lang(text: str) -> str | None:
    """Best-effort language detect. Returns ISO code or None if undetectable/unavailable."""
    sample = (text or "")[:2000].strip()
    if len(sample) < 40:
        return None
    try:
        from langdetect import DetectorFactory, detect  # optional dep
        DetectorFactory.seed = 0  # deterministic mode (langdetect is RNG-seeded by default)
        return detect(sample)
    except Exception:
        return None  # langdetect missing or failed -> never drop on language


def postfetch_filter(result: WebResult, *, query_lang: str | None = None,
                     original_url: str | None = None) -> WebResult | None:
    """Stage 2 keep/drop sequence (dossier 07 §7.1, steps 2c-2f). Returns None to DROP.

    Order: login wall -> junk -> paywall -> language. (BS4 strip + base64 strip +
    empty->onlyMainContent fallback happen upstream in the fetcher, §2.3.)
    """
    # 2c. login wall
    if result.looks_like_login_wall(original_url or result.url):
        return None
    # 2d. junk (returns a reason string when junk)
    if result.looks_like_junk() is not None:
        return None
    # 2e. paywall
    if looks_like_paywall(result):
        return None
    # 2f. language: only when caller pins a query language
    if query_lang:
        detected = _detect_lang(result.content)
        if detected is not None and detected != query_lang:
            return None
    return result


def postfetch_reject_reason(result: WebResult, *, query_lang: str | None = None,
                            original_url: str | None = None) -> str | None:
    """Stage 2 keep/drop as a REASON: a short cause string to DROP, ``None`` to KEEP.

    This is the contract the funnel relies on (``funnel/filter.py``:
    ``[p for p in pages if postfetch_reject_reason(p) is None]`` — ``None`` keeps).
    It mirrors :func:`postfetch_filter`'s order (login wall -> junk -> paywall ->
    language) but names the cause so the drop is observable, not silent.
    """
    if result.looks_like_login_wall(original_url or result.url):
        return "login_wall"
    if result.looks_like_junk() is not None:
        return "junk"
    if looks_like_paywall(result):
        return "paywall"
    if query_lang:
        detected = _detect_lang(result.content)
        if detected is not None and detected != query_lang:
            return "language"
    return None
