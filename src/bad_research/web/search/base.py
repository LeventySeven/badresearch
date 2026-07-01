"""Keyless generic search providers + the KeylessSearchConfig knob-bag.

Every provider here is keyless: the host WebSearch tool (host-provided), the
ddgs multi-engine lib, or a self-hosted SearXNG JSON endpoint. All return the
kept `web/base.py::WebResult` and carry cost_per_search=0.0.

Dossier 13: §0 (source tiers + WebSearch shape), §1 (SearXNG self-host JSON),
§8.1(7) (ddgs lib). Constants frozen in INTERFACES_KEYLESS §3.2.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

import httpx

from bad_research.web.base import SearchQuery, WebResult, recency_cutoff_date


def _is_fetchable_url(url: str) -> bool:
    """True only for an absolute http(s) URL that carries a host. SERP scrapers
    (notably Startpage via ddgs) sometimes emit click-tracking redirect URLs with
    an EMPTY host — `https:///clev?event=StartpageResultClick&...`. Such a URL is
    non-empty (so a bare `if not url` skip misses it) yet has no host, so it trips
    the SSRF guard ("refusing URL with no host") downstream and wastes a read slot.
    Drop it at parse time so it never reaches the fetch ladder (issue #14)."""
    if not url:
        return False
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    return parts.scheme in ("http", "https") and bool(parts.hostname)


def with_after_operator(query: str, recency_days: int | None) -> str:
    """Append a Google-style `after:YYYY-MM-DD` date operator when a recency
    window is set. The host WebSearch tool, ddgs, and SearXNG all consume a
    Google-style query string, so a date operator is the keyless way to bias
    these providers toward fresh results. No-op when recency_days is unset, or
    when an `after:` operator is already present (idempotent)."""
    cutoff = recency_cutoff_date(recency_days)
    if cutoff is None or "after:" in query:
        return query
    return f"{query} after:{cutoff.isoformat()}"


@dataclass
class KeylessSearchConfig:
    """Frozen knobs for the keyless search loop (INTERFACES_KEYLESS §3.2)."""

    # KNOWN: every value traces to dossier 13.
    rrf_k: int = 60                      # §3.2 (RRF sweet spot, Cormack 2009)
    relevance_threshold: float = 0.70    # §3.4 — CALIBRATE §7.2; OWN default (the "Perplexity 0.70 / L3 gate" attribution was refuted, PERPLEXITY_DEEP R5 — not a copied constant)
    min_pass_fraction: float = 0.30      # §3.4 (<30% pass → re-retrieve)
    max_rounds: int = 3                  # §3.4/§6.1 (light=2, full=3)
    rerank_top_n: int = 30               # §4.1 (LLM-rerank only L1 survivors)
    sat_tau: float = 0.20                # saturation stop: halt fan-out when a round's new-distinct-domain
                                         # ratio < sat_tau (Perplexity PD:3849-3855). CALIBRATE; the
                                         # evidence-based replacement for the refuted "0.85 entropy" cutoff.


# A pluggable source of the host-tool Links array (injected for tests; in
# production the orchestrator supplies the parsed links and we just normalize).
LinksSource = Callable[..., Any]


class WebSearchToolProvider:
    """DESIGNED: adapter over the Claude Code host WebSearch tool (dossier 13 §0).

    The host tool is invoked by the ORCHESTRATOR (Claude Code), not by this Python
    layer. This adapter normalizes the tool's `Links:` output — a list of
    {title,url} already rank-ordered by the tool — into content-less WebResult
    rows. Array position is the only score signal the tool gives, so it becomes
    metadata["rank"]; content is "" (filled later by the content layer / WebFetch).
    """

    name: str = "websearch"
    capabilities = frozenset({"keyword", "batch_via_loop"})
    cost_per_search: float = 0.0
    p50_ms: int = 0

    def __init__(self, links_source: LinksSource | None = None) -> None:
        # links_source(query, allowed=..., blocked=...) -> list[{title,url}] | "Links: [...]"
        self._links_source = links_source

    @staticmethod
    def parse_links(raw: Any) -> list[WebResult]:
        """Normalize a host Links payload into rank-ordered content-less rows.

        Accepts either a list[{title,url}] or a 'Links: [...]'-prefixed string.
        """
        if isinstance(raw, str):
            blob = raw.strip()
            if blob.lower().startswith("links:"):
                blob = blob[len("links:"):].strip()
            raw = json.loads(blob) if blob else []
        rows: list[WebResult] = []
        for i, x in enumerate(raw or [], start=1):
            url = x.get("url") or x.get("href") or ""
            if not url:
                continue
            rows.append(
                WebResult(
                    url=url,
                    title=x.get("title", ""),
                    content="",
                    metadata={"rank": i, "source": "websearch"},
                )
            )
        return rows

    def _fetch_links(self, query: str, *, allowed: list[str] | None = None,
                     blocked: list[str] | None = None) -> Any:
        if self._links_source is None:
            raise NotImplementedError(
                "WebSearchToolProvider has no links_source — the host WebSearch "
                "tool is invoked by the orchestrator; pass its Links array to "
                "parse_links()/search_ex() or inject a links_source for tests."
            )
        return self._links_source(query, allowed=allowed, blocked=blocked)

    def search(self, query: str, max_results: int = 10,
               allowed: list[str] | None = None,
               blocked: list[str] | None = None) -> list[WebResult]:
        rows = self.parse_links(self._fetch_links(query, allowed=allowed, blocked=blocked))
        return rows[:max_results]

    def search_ex(self, q: SearchQuery) -> list[WebResult]:
        return self.search(
            with_after_operator(q.query, q.recency_days), max_results=q.max_results,
            allowed=q.include_domains, blocked=q.exclude_domains,
        )

    def fetch(self, url: str) -> WebResult:
        """Delegate to the keyless content layer (KR-3 fetch_clean). Stubbed
        here so the provider satisfies WebProvider; KR-3 fills the body."""
        return _fetch_clean_bridge(url)


def _fetch_clean_bridge(url: str) -> WebResult:
    """DESIGNED: bridge to KR-3 web/content/fetch_clean.py (frozen signature,
    INTERFACES_KEYLESS §4.1/§4.2). Until KR-3 lands, raise a clear error rather
    than guess content. Uses importlib so the soft KR-3 dependency is resolved at
    call time, not import time."""
    import importlib

    try:
        mod = importlib.import_module("bad_research.web.content.fetch_clean")  # KR-3
    except ImportError as e:  # pragma: no cover - exercised once KR-3 lands
        raise NotImplementedError(
            "fetch() needs the KR-3 content layer (web/content/fetch_clean.py)."
        ) from e
    d = mod.fetch_clean(url)
    return WebResult(
        url=d.get("url", url),
        title=(d.get("metadata") or {}).get("title", ""),
        content=d.get("markdown", ""),
        links=d.get("links", []),
        metadata={**(d.get("metadata") or {}),
                  "published_date": d.get("published_date"),
                  "highlights": d.get("highlights")},
    )


# Lazy module-level handle so tests can patch("...base.DDGS") and prod imports
# the lib only when a DdgsProvider is constructed.
try:  # pragma: no cover - import shim
    from ddgs import DDGS
except Exception:  # pragma: no cover
    DDGS = None  # type: ignore[assignment, misc]


class DdgsProvider:
    """DESIGNED: keyless multi-engine aggregator (dossier 13 §8.1(7)).

    Wraps `ddgs.DDGS().text(...)` (Bing/Brave/DuckDuckGo/Google/Mojeek/StartPage/
    Wikipedia). Scrapes public engines → fragile; a failure degrades to [] so one
    dead lane never aborts the fan-out (dossier 13 §7.2 / SPEC provider failover).
    """

    name: str = "ddgs"
    capabilities = frozenset({"keyword", "multi_engine", "news", "books"})
    cost_per_search: float = 0.0
    p50_ms: int = 800

    def __init__(self, backend: str | None = None) -> None:
        if DDGS is None:  # pragma: no cover - exercised only without the dep
            raise ImportError("DdgsProvider requires: pip install ddgs")
        self._backend = backend  # e.g. "google,bing,brave"; None = ddgs default union

    def search(self, query: str, max_results: int = 10) -> list[WebResult]:
        try:
            kw: dict[str, Any] = {"max_results": max_results}
            if self._backend:
                kw["backend"] = self._backend
            rows = DDGS().text(query, **kw)
        except Exception:
            return []  # scraper failure → empty lane (graceful)
        out: list[WebResult] = []
        for i, x in enumerate(rows or [], start=1):
            url = x.get("href") or x.get("url") or ""
            if not _is_fetchable_url(url):
                continue  # empty / host-less (e.g. Startpage redirect-tracking) URL — issue #14
            out.append(
                WebResult(url=url, title=x.get("title", ""),
                          content=x.get("body", ""),
                          metadata={"rank": i, "source": "ddgs"})
            )
        return out

    def search_ex(self, q: SearchQuery) -> list[WebResult]:
        return self.search(with_after_operator(q.query, q.recency_days),
                           max_results=q.max_results)

    def fetch(self, url: str) -> WebResult:
        return _fetch_clean_bridge(url)


class SearxngProvider:
    """KNOWN endpoint (dossier 13 §1.4) / DESIGNED mapping. Keyless self-host JSON.

    Default endpoint localhost:8080, no env var, no key. A non-200 / network error
    degrades to [] (graceful; ddgs is the no-self-host default breadth source so
    SearXNG absence is non-fatal).
    """

    name: str = "searxng"
    capabilities = frozenset({"keyword", "multi_engine", "academic"})
    cost_per_search: float = 0.0
    p50_ms: int = 800

    def __init__(self, endpoint: str = "http://localhost:8080",
                 client: httpx.Client | None = None) -> None:
        self.endpoint = endpoint.rstrip("/")
        self._client = client

    def _get(self, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.endpoint}/search"
        if self._client is not None:
            resp = self._client.get(url, params=params, timeout=20.0)
        else:
            resp = httpx.get(url, params=params, timeout=20.0,
                             headers={"User-Agent": "bad-research/keyless (research tool)"})
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        return data

    def search(self, query: str, max_results: int = 10,
               engines: list[str] | None = None,
               categories: str = "general", pageno: int = 1) -> list[WebResult]:
        params: dict[str, Any] = {"q": query, "format": "json",
                                  "categories": categories, "pageno": pageno}
        if engines:
            params["engines"] = ",".join(engines)
        try:
            data = self._get(params)
        except Exception:
            return []
        out: list[WebResult] = []
        for i, x in enumerate(data.get("results", []) or [], start=1):
            url = x.get("url") or ""
            if not _is_fetchable_url(url):
                continue  # empty / host-less URL — issue #14
            out.append(WebResult(
                url=url, title=x.get("title", ""), content=x.get("content", ""),
                metadata={"rank": i, "source": "searxng",
                          "engine": x.get("engine"), "native_score": x.get("score")},
            ))
            if len(out) >= max_results:
                break
        return out

    def search_ex(self, q: SearchQuery) -> list[WebResult]:
        return self.search(with_after_operator(q.query, q.recency_days),
                           max_results=q.max_results)

    def fetch(self, url: str) -> WebResult:
        return _fetch_clean_bridge(url)
