"""BrowseProvider / ExtractProvider Protocols + keyless availability-gated factories.

Both Protocols match docs/INTERFACES_KEYLESS.md §4.3 verbatim (KEPT). The factories are
100% keyless: get_browse_provider returns the local AgentBrowserProvider iff the
agent-browser CLI is on PATH (no API key, local Chrome over CDP); get_extract_provider
returns the host-model LLM extractor ('llm', default) or the ported AQL resolver ('aql').
Factories return None (never raise) when the CLI/backend is absent — the ladder treats
None as "this tier is not available" and keeps the best lower-tier result.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from bad_research.web.base import WebResult


@runtime_checkable
class BrowseProvider(Protocol):
    """Tier-3: LLM-driven, multi-step browse. Returns a WebResult like any provider,
    but reaches it through an agent loop (login, paginate, click, dismiss modals)."""

    name: str

    def browse(
        self,
        url: str,
        instruction: str,
        *,
        max_steps: int = 12,
        variables: dict | None = None,
        replay_key: str | None = None,
    ) -> WebResult: ...


@runtime_checkable
class ExtractProvider(Protocol):
    """Tier-2: schema-driven typed extraction. Returns a dict conforming to `schema`;
    missing fields are null — never fabricated."""

    name: str

    def extract(
        self,
        source: str | WebResult,
        schema: dict[str, Any] | str,
        instruction: str = "",
    ) -> dict: ...


from bad_research.browse.agent_browser import is_available  # re-export for test monkeypatch
from bad_research.browse.silver import is_available as silver_is_available  # ditto


def get_extract_provider(name: str | None = None) -> ExtractProvider | None:
    """Resolve an ExtractProvider. Default 'llm' = the zero-dep host-model extractor
    (always constructible; no-ops to {} without an LLM). 'aql' = the AQL resolver.
    Unknown / removed keyed names → None (graceful)."""
    if name in (None, "llm"):
        from bad_research.browse.extract_llm import LLMExtractProvider
        return LLMExtractProvider()
    if name == "aql":
        from bad_research.browse.aql import AqlExtractProvider
        return AqlExtractProvider()
    return None  # 'agentql'/'stagehand' (keyed) are gone → None


def get_browse_provider(name: str | None = None) -> BrowseProvider | None:
    """Resolve a BrowseProvider. Both backends are keyless local-Chromium drivers with
    the same @eN grounding contract; the default prefers silver and falls back to
    agent-browser, so a machine with only one of the two still gets a browse rung.

    Returns None when the requested CLI (or, for the default, neither CLI) is installed —
    the ladder then degrades to crawl4ai/httpx. No env var, no API key.
    """
    if name in (None, "silver"):
        if silver_is_available():
            from bad_research.browse.silver import SilverProvider
            return SilverProvider()
        if name == "silver":
            return None  # explicitly asked for silver and it is not installed
    if name in (None, "agent-browser"):
        if not is_available():
            return None
        from bad_research.browse.agent_browser import AgentBrowserProvider
        return AgentBrowserProvider()
    return None  # 'browserbase'/'browser-use' (keyed) are gone → None
