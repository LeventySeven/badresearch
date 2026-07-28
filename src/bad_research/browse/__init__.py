"""Keyless browse subsystem: SilverProvider (local silver CLI, the default) and
AgentBrowserProvider (local agent-browser CLI, the fallback), the AQL parser + resolver,
the LLM extractor, the 4-rung keyless ladder, and the action-replay cache."""

from __future__ import annotations

from bad_research.browse.agent_browser import (
    AGENT_LOOP_SYSTEM_PROMPT,
    AgentBrowserProvider,
    BrowseStep,
    Snapshot,
    is_available,
    parse_snapshot,
)
from bad_research.browse.aql import (
    AqlExtractProvider,
    ContainerListNode,
    ContainerNode,
    IdListNode,
    IdNode,
    QuerySyntaxError,
    parse_aql,
)
from bad_research.browse.base import (
    BrowseProvider,
    ExtractProvider,
    get_browse_provider,
    get_extract_provider,
)
from bad_research.browse.cache import ActCache, replay_key_for
from bad_research.browse.extract_llm import LLMExtractProvider
from bad_research.browse.ladder import BrowseEngine, TieredFetcher, fetch_tiered
from bad_research.browse.silver import SilverProvider

__all__ = [
    "AGENT_LOOP_SYSTEM_PROMPT",
    "ActCache",
    "AgentBrowserProvider",
    "AqlExtractProvider",
    "BrowseEngine",
    "BrowseProvider",
    "BrowseStep",
    "ContainerListNode",
    "ContainerNode",
    "ExtractProvider",
    "IdListNode",
    "IdNode",
    "LLMExtractProvider",
    "QuerySyntaxError",
    "SilverProvider",
    "Snapshot",
    "TieredFetcher",
    "fetch_tiered",
    "get_browse_provider",
    "get_extract_provider",
    "is_available",
    "parse_aql",
    "parse_snapshot",
    "replay_key_for",
]
