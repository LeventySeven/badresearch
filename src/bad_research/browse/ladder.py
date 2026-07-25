"""fetch_tiered — the 4-rung KEYLESS escalation ladder (INTERFACES_KEYLESS §4.4, dossier 14 §7).

  rung 1   httpx GET (core/fetcher) ............... $0  static HTML/APIs
  rung 2   crawl4ai local JS render → fit_markdown . $0  clean MD, no interaction
  rung 2.5 agent-browser --engine lightpanda ....... $0  fast keyless JS render (snapshot/eval)
  rung 3   agent-browser --engine chrome ........... $0  login/click/typed/screenshot

Escalation gates KEPT verbatim from web/base.py (looks_like_junk / looks_like_login_wall).
There is NO rung that costs money. The lightpanda→chrome fallback lives inside
AgentBrowserProvider.browse (it retries on an empty snapshot). Every optional rung degrades
gracefully: a missing provider/CLI means the rung is skipped and the best lower-tier result
is returned. Providers are injectable for tests (_tier0/_tier1_factory/_browse/_extractor/_llm).

SSRF (same contract as the KR-3 content fix): agent-browser drives a REAL browser, so a
malicious page could redirect/navigate to an internal host. We reuse the shared denylist
predicate `core.fetcher.is_blocked_url` (the DRY single source of truth) to (a) gate the
browse-rung entry URL before driving the CLI, and (b) re-validate the final/landed URL the
provider reports (Snapshot.url → WebResult.url) and discard the result if it is internal.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any, Literal

from bad_research.web.base import WebResult


def _is_empty(result: WebResult) -> bool:
    return (result.looks_like_junk() or "").startswith("Empty or near-empty")


def _is_bot_wall(result: WebResult) -> bool:
    return (result.looks_like_junk() or "").startswith("Bot detection page")


def fetch_tiered(
    url: str,
    *,
    tier_max: int,
    instruction: str | None = None,
    schema: dict[str, Any] | str | None = None,
    replay_key: str | None = None,
    variables: dict[str, Any] | None = None,
    # ---- injection seams (tests pass mocks; production gets real keyless defaults) ----
    _tier0: Any | None = None,
    _tier1_factory: Callable[[], Any | None] | None = None,
    _browse: Any | None = None,
    _extractor: Any | None = None,
    _llm: Any | None = None,
) -> WebResult:
    # ---------- Rung 1: httpx (core/fetcher builtin) ----------
    if _tier0 is None:
        from bad_research.web.base import get_provider
        _tier0 = get_provider("builtin")
    result = _tier0.fetch(url)

    # ---------- Rung 2: crawl4ai local JS render ----------
    if tier_max >= 1 and _is_empty(result):
        if _tier1_factory is None:
            def _tier1_factory() -> Any | None:
                try:
                    from bad_research.web.base import get_provider
                    return get_provider("crawl4ai")
                except ImportError:
                    return None
        t1 = _tier1_factory()
        if t1 is not None:
            try:
                t1_result = t1.fetch(url)
                if len(t1_result.content.strip()) >= len(result.content.strip()):
                    result = t1_result
            except Exception:
                pass  # keep the rung-1 result

    # ---------- Rung 2.5 / 3: agent-browser (local Chrome/lightpanda over CDP) ----------
    want_anti_bot = tier_max >= 3 and _is_bot_wall(result)
    want_login = tier_max >= 3 and result.looks_like_login_wall(url)
    want_interactive = tier_max >= 3 and bool(instruction)

    if want_anti_bot or want_login or want_interactive:
        browse_result = _do_browse(
            url, instruction or "Read the main content of this page.",
            replay_key=replay_key, variables=variables, browse=_browse,
        )
        if browse_result is not None and browse_result.content.strip():
            result = browse_result
        elif _browse is None and not _browse_cli_available():
            # SAY SO. The escalation was REQUESTED (tier_max>=3 plus a bot wall,
            # a login wall, or an instruction) and could not run because the
            # `agent-browser` CLI is not on PATH — it is not a pip dependency,
            # so this is the DEFAULT state, not an edge case.
            #
            # Four shipped skills tell agents to run `bad fetch --tier-max 3`.
            # Silently returning the rung-1 httpx body makes those agents treat
            # an anti-bot interstitial as the article. Recording it lets the
            # caller tell "this is the best available" from "the renderer never
            # ran", and tells the user what to install.
            result.metadata["browse_unavailable"] = True
            result.metadata["browse_unavailable_reason"] = (
                "the `agent-browser` CLI is not on PATH, so browse rungs 2.5/3 "
                "could not run; this content is the plain httpx fetch. Install "
                "it with `agent-browser install` to enable JS render, anti-bot "
                "and login-walled pages."
            )
            logging.getLogger(__name__).warning(
                "browse rung requested (tier_max=%s) but agent-browser is not "
                "installed — returning the un-rendered rung-1 body for %s",
                tier_max, url,
            )

    # ---------- Rung 2: typed extraction (schema / AQL request) ----------
    if schema is not None and tier_max >= 2:
        extractor = _extractor
        if extractor is None:
            from bad_research.browse.base import get_extract_provider
            # An AQL string selects the AQL resolver; a JSON-schema dict selects the LLM extractor.
            extractor = get_extract_provider("aql") if isinstance(schema, str) else \
                get_extract_provider("llm")
            if extractor is not None and _llm is not None and hasattr(extractor, "_llm"):
                extractor._llm = _llm
        if extractor is not None:
            try:
                data = extractor.extract(result, schema, instruction or "")
            except Exception:
                data = {}
            if data:
                result.metadata["extracted"] = data

    return result


def _browse_cli_available() -> bool:
    """Is the external browse CLI actually installed? Never raises."""
    try:
        from bad_research.browse.agent_browser import is_available

        return is_available()
    except Exception:
        return False


def _do_browse(
    url: str,
    instruction: str,
    *,
    replay_key: str | None,
    variables: dict[str, Any] | None,
    browse: Any | None,
) -> WebResult | None:
    """Drive the keyless AgentBrowserProvider (rung 2.5 lightpanda → 3 chrome inside browse()).
    Returns None if no provider is available (caller keeps the lower-tier result).

    SSRF gating (reuses core.fetcher.is_blocked_url — the DRY denylist from the KR-3 fix):
      (a) ENTRY gate: refuse to drive the browser at an internal target up front.
      (b) FINAL-URL re-validation: agent-browser reports the landed URL (Snapshot.url →
          WebResult.url); if a mid-navigation redirect landed on an internal host, discard
          the result rather than return content scraped from inside the perimeter.

      # SSRF LIMITATION: agent-browser is an external CLI and exposes no per-navigation
      # request-interception hook we can drive from Python (unlike the crawl4ai render rung,
      # which uses a Playwright `route` handler in KR-3). So intermediate redirects that
      # *transit* an internal host but land back on a public URL are not individually gated
      # here — only the entry URL and the final landed URL are validated. A future
      # `agent-browser --proxy`/interception surface (dossier 14 §11) would close this.
    """
    from bad_research.core.fetcher import is_blocked_url

    # (a) entry gate — never drive a real browser at an internal/loopback/metadata host.
    if is_blocked_url(url):
        return None

    prov = browse
    if prov is None:
        from bad_research.browse.base import get_browse_provider
        prov = get_browse_provider("agent-browser")  # None when CLI absent (graceful)
    if prov is None:
        return None
    try:
        landed: WebResult | None = prov.browse(
            url, instruction, replay_key=replay_key, variables=variables
        )
    except Exception:
        return None

    # (b) final-URL re-validation — discard if the browser landed on an internal host.
    if landed is not None and is_blocked_url(landed.url):
        return None
    return landed


class TieredFetcher:
    """Object wrapper over the module-level keyless `fetch_tiered` ladder, with the
    configured browse engine bound for the rung-2.5/3 agent-browser rungs.

    The funnel (`FunnelDeps.fetcher`) and the skill CLI hold a `TieredFetcher` and
    call `.fetch_tiered(url, tier_max=...)`. The wrapper threads `engine` (lightpanda
    by default → chrome fallback inside `AgentBrowserProvider.browse`) into the
    browse rung by lazily constructing an engine-configured `AgentBrowserProvider`
    and injecting it as the `_browse` seam — so the rung uses the configured engine
    rather than `get_browse_provider`'s default. Constructing the wrapper does NOT
    touch the CLI/network: the provider is built only on first browse-rung use, and
    a missing CLI degrades to None (the ladder keeps the best lower-tier result).
    """

    def __init__(self, engine: Literal["lightpanda", "chrome"] = "lightpanda") -> None:
        self.engine = engine
        self._browse_provider: Any | None = None
        self._browse_resolved = False

    def _browse_seam(self) -> Any | None:
        """Lazily build the engine-configured AgentBrowserProvider (keyless, local
        Chrome/lightpanda over CDP). Returns None when the agent-browser CLI is
        absent — the ladder then degrades to crawl4ai/httpx (graceful)."""
        if not self._browse_resolved:
            self._browse_resolved = True
            try:
                from bad_research.browse.agent_browser import (
                    AgentBrowserProvider,
                    is_available,
                )

                if is_available():
                    self._browse_provider = AgentBrowserProvider(engine=self.engine)
            except Exception:
                self._browse_provider = None
        return self._browse_provider

    def fetch_tiered(
        self,
        url: str,
        *,
        tier_max: int,
        instruction: str | None = None,
        schema: dict[str, Any] | str | None = None,
        replay_key: str | None = None,
        variables: dict[str, Any] | None = None,
    ) -> WebResult:
        """Run the 4-rung keyless ladder for `url` up to `tier_max`, using the
        configured browse engine for the agent-browser rungs."""
        return fetch_tiered(
            url,
            tier_max=tier_max,
            instruction=instruction,
            schema=schema,
            replay_key=replay_key,
            variables=variables,
            _browse=self._browse_seam(),
        )
