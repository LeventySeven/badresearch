"""Base protocol and data types for web providers."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from typing import Literal, Protocol, runtime_checkable


@dataclass
class WebResult:
    """A single web fetch or search result."""

    url: str
    title: str
    content: str  # clean markdown or plain text
    fetched_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    raw_html: str | None = None
    metadata: dict = field(default_factory=dict)  # author, date, domain, etc.
    media: list[dict] = field(default_factory=list)  # images: {src, alt, score, ...}
    links: list[dict] = field(default_factory=list)  # {href, text, type}
    screenshot: bytes | None = None  # PNG screenshot of the rendered page
    raw_bytes: bytes | None = None  # Raw file bytes (PDF, etc.)
    raw_content_type: str | None = None  # MIME type of raw file (application/pdf, etc.)

    @property
    def domain(self) -> str:
        from urllib.parse import urlparse

        return urlparse(self.url).netloc

    def looks_like_login_wall(self, original_url: str) -> bool:
        """Check if the result appears to be a login/signup redirect rather than real content."""
        login_signals = (
            "sign in", "sign up", "log in", "login", "create account",
            "auth", "register", "sso", "verify your identity",
        )
        title_lower = (self.title or "").lower()
        content_lower = (self.content or "")[:500].lower()

        # Title contains login language
        title_match = any(s in title_lower for s in login_signals)

        # Content is mostly login form (very short with login keywords)
        content_match = (
            len(self.content or "") < 1000
            and any(s in content_lower for s in login_signals)
        )

        # URL changed to a login/auth path
        from urllib.parse import urlparse

        result_path = urlparse(self.url).path.lower()
        auth_paths = ("/login", "/signin", "/signup", "/auth", "/sso", "/register")
        url_redirected = any(p in result_path for p in auth_paths)

        return title_match or content_match or url_redirected

    def looks_like_junk(self, *, min_chars: int = 300) -> str | None:
        """Check if the result is junk that shouldn't be saved.

        Returns a reason string if junk, None if OK.

        `min_chars` is the FETCH-FAILURE floor and the only rule here that judges
        the fetch rather than the text: a body this short means the fetch came
        back empty. A caller holding content that was never fetched — the social
        lane's prefetched thread bodies — lowers it (funnel/filter.py), which
        leaves every rule below still judging that text.
        """
        content = self.content or ""
        title_lower = (self.title or "").lower()
        content_lower = content[:2000].lower()

        # Empty or near-empty content
        if len(content.strip()) < min_chars:
            return "Empty or near-empty content"

        # Cloudflare / bot detection pages
        cf_signals = (
            "just a moment", "checking your browser", "ray id", "cloudflare",
            "please wait while we verify", "unusual activity", "captcha",
            "recaptcha", "verify you are human", "verify you are not a robot",
            "please complete the security check", "access denied",
            "enable javascript and cookies", "browser check",
            "ddos protection", "attention required",
        )
        if any(s in title_lower or s in content_lower for s in cf_signals):
            return f"Bot detection page: {self.title}"

        # Error pages
        error_signals = (
            "404 not found", "page not found", "403 forbidden",
            "500 internal server error", "502 bad gateway",
            "an error occurred", "this page isn't available",
            "the page you requested", "sorry, we couldn't find",
        )
        if any(s in title_lower or s in content_lower for s in error_signals):
            return f"Error page: {self.title}"

        # Search result / index pages (not actual content)
        search_signals = ("search results for", "results for query")
        if any(s in title_lower for s in search_signals):
            return f"Search results page: {self.title}"

        # Binary garbage from PDFs that weren't properly extracted
        pdf_binary_signals = ("endstream", "endobj", "/FlateDecode", "%PDF-")
        sample = content[:2000]
        if any(m in sample for m in pdf_binary_signals):
            return "Binary PDF garbage in content"

        # NON-PRINTABLE means non-printable, NOT non-ASCII. This counted every
        # `ord(c) > 127` char, so any source more than 15% Cyrillic, CJK or emoji
        # was discarded as "binary garbage" — measured: a Russian Reddit thread and
        # a Japanese one both died here, in a tool whose whole job is gathering
        # evidence. Unicode categories starting with `C` are the genuinely
        # unprintable ones (Cc control, Cf format, Cs surrogate, Co private-use,
        # Cn unassigned); `�` is the decoder's own "this was mojibake" marker.
        # Real binary garbage is still caught — it is dense in control bytes — while
        # every human script now passes.
        non_printable = sum(
            1
            for c in sample
            if (unicodedata.category(c).startswith("C") and c not in "\t\n\r") or c == "�"
        )
        if non_printable > len(sample) * 0.15:
            return "High ratio of binary/non-printable content"

        # Cookie consent / boilerplate pages (short with mostly nav/cookie text)
        if len(content.strip()) < 1500:
            cookie_signals = (
                "we use cookies", "cookie policy", "accept cookies", "cookie consent",
                "there appears to be a technical issue", "please enable javascript",
            )
            if any(s in content_lower for s in cookie_signals):
                return "Cookie/boilerplate page"

        return None


@runtime_checkable
class WebProvider(Protocol):
    """Protocol for web content providers.

    Implementations must support at least fetch(). search() is optional —
    providers that don't support search raise NotImplementedError.
    """

    name: str

    def fetch(self, url: str) -> WebResult:
        """Fetch a single URL and return clean content."""
        ...

    def search(self, query: str, max_results: int = 5) -> list[WebResult]:
        """Search the web and return results with content."""
        ...


# --- Cascade error classes (Plan 03; cite dossier 02 §6.5) ---------------------


class ProviderError(Exception):
    """A provider failed in a way that should advance the cascade ladder.

    5xx, timeouts, malformed responses. The cascade catches this and tries the
    next provider immediately.
    """


class QuotaExceeded(ProviderError):
    """Plan/pay-as-you-go limit hit — permanent for this run, do NOT retry.

    Tavily 432 (plan quota) / 433 (PAYG limit); Exa x402. The cascade skips this
    provider for the remainder of the run.
    """


class RateLimited(ProviderError):
    """Transient 429 — back off (2s -> x1.5 -> 10s cap) then advance the ladder."""


# --- Rich search surface (Plan 03; INTERFACES.md "Seam signatures") ------------


@dataclass
class SearchQuery:
    """A normalized search request that the rich `search_ex()` path consumes.

    `intent` picks the cascade lane: keyword (fast SERP), neural (semantic),
    deep (full extraction). `recency_days` maps to each provider's recency
    filter (Tavily time_range / Sonar search_recency_filter / Exa published-date).
    """

    query: str
    intent: Literal["keyword", "neural", "deep"] = "keyword"
    recency_days: int | None = None
    include_domains: list[str] | None = None
    exclude_domains: list[str] | None = None
    max_results: int = 10


def recency_cutoff_date(recency_days: int | None, *, today: date | None = None) -> date | None:
    """The publication-date floor implied by a recency window: today minus recency_days.

    Returns None when no window is set (recency_days is None / non-positive), so
    every provider's date-filter injection is a clean no-op for evergreen queries.
    `today` is injectable for deterministic tests (defaults to UTC today).
    """
    if not recency_days or recency_days <= 0:
        return None
    ref = today or datetime.now(UTC).date()
    return ref - timedelta(days=recency_days)


@runtime_checkable
class WebSearchProvider(WebProvider, Protocol):
    """Extends WebProvider with the rich, capability-aware search surface.

    `capabilities` advertises what the provider can do so the cascade can route
    (subset of {"keyword","neural","extract","crawl"}). `cost_per_search` and
    `p50_ms` let the cascade order/budget providers.
    """

    name: str
    capabilities: set[str]
    cost_per_search: float
    p50_ms: int

    def fetch(self, url: str) -> WebResult: ...

    def search_ex(self, q: SearchQuery) -> list[WebResult]: ...


def get_provider(
    name: str | None = None,
    profile: str | None = None,
    magic: bool = False,
    headless: bool = True,
) -> WebProvider:
    """Keyless web provider factory (INTERFACES_KEYLESS §3.1). Default = the host
    WebSearch tool adapter. Every branch is keyless (host tool / local lib /
    self-host / free API). No env var, no key."""
    if name is None or name == "websearch":
        from bad_research.web.search.base import WebSearchToolProvider

        return WebSearchToolProvider()

    if name == "ddgs":
        from bad_research.web.search.base import DdgsProvider

        return DdgsProvider()

    if name == "searxng":
        from bad_research.web.search.base import SearxngProvider

        return SearxngProvider()

    if name == "builtin":
        from bad_research.web.builtin import BuiltinProvider

        return BuiltinProvider()

    if name == "crawl4ai":
        try:
            from bad_research.web.crawl4ai_provider import Crawl4AIProvider

            return Crawl4AIProvider(profile=profile or None, magic=magic, headless=headless)
        except ImportError as e:
            raise ImportError("crawl4ai provider requires: pip install bad-research[browse]") from e

    # keyless scholarly verticals (INTERFACES_KEYLESS §3.3)
    _verticals = {
        "arxiv": "ArxivProvider", "openalex": "OpenAlexProvider",
        "crossref": "CrossrefProvider", "semantic_scholar": "SemanticScholarProvider",
        "s2": "SemanticScholarProvider", "europe_pmc": "EuropePMCProvider",
        "europepmc": "EuropePMCProvider", "pubmed": "PubMedProvider",
        "wikipedia": "WikipediaProvider",
    }
    if name in _verticals:
        from typing import cast

        import bad_research.web.search.verticals as v

        return cast("WebProvider", getattr(v, _verticals[name])())

    # keyless social vertical — external engine, absent by default (raises
    # FileNotFoundError when it is not installed, which _build_vertical_providers
    # treats as "skip this lane" like any other build failure).
    if name == "last30days":
        from typing import cast

        from bad_research.web.search.social import Last30DaysProvider

        return cast("WebProvider", Last30DaysProvider())

    raise ValueError(
        f"Unknown keyless web provider: {name!r}. Available: websearch (default), "
        f"ddgs, searxng, builtin, crawl4ai, arxiv, openalex, crossref, "
        f"semantic_scholar, europepmc, pubmed, wikipedia, last30days"
    )
