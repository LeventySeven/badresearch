"""Keyless posture: no CLI, no libs, no keys → factories None; the ladder degrades."""

from __future__ import annotations

import builtins

import bad_research.browse.base as base
from bad_research.browse.base import get_browse_provider, get_extract_provider
from bad_research.browse.ladder import fetch_tiered
from tests.test_browse.conftest import make_result


def _no_optional_imports(monkeypatch):
    """Force crawl4ai / browser_use / agentql / stagehand to look uninstalled."""
    real = builtins.__import__

    def fake(name, *a, **k):
        bad = ("crawl4ai", "browser_use", "agentql", "stagehand")
        if name in bad or name.startswith(tuple(b + "." for b in bad)):
            raise ImportError(f"No module named {name!r}")
        return real(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake)


def test_no_browse_cli_factory_returns_none(monkeypatch):
    monkeypatch.setattr(base, "silver_is_available", lambda program="silver": False)
    monkeypatch.setattr(base, "is_available", lambda program="agent-browser": False)
    assert get_browse_provider() is None
    assert get_browse_provider("silver") is None
    assert get_browse_provider("agent-browser") is None
    # the LLM + AQL extractors are pure-Python and always constructible
    assert get_extract_provider("llm") is not None
    assert get_extract_provider("aql") is not None


def test_ladder_degrades_to_rung1_when_nothing_else_available(monkeypatch):
    monkeypatch.setattr(base, "silver_is_available", lambda program="silver": False)
    monkeypatch.setattr(base, "is_available", lambda program="agent-browser": False)
    _no_optional_imports(monkeypatch)

    class _T0:
        def fetch(self, url):
            return make_result("short", url=url)  # < 300 chars — would want rung 2

    r = fetch_tiered("https://x.test", tier_max=3,
                     instruction="paginate", schema={"type": "object"}, _tier0=_T0())
    assert r.content == "short"               # no exception; best lower-tier result
    assert "extracted" not in r.metadata      # LLM extractor with no LLM → {} → not attached


def test_ladder_extract_no_llm_no_crash():
    class _T0:
        def fetch(self, url):
            return make_result("Substantial content. " * 40, url=url)

    r = fetch_tiered("https://x.test", tier_max=2, schema={"type": "object"}, _tier0=_T0())
    assert r.content.startswith("Substantial content")
    assert "extracted" not in r.metadata


def test_no_keyed_backends_resolve():
    assert get_browse_provider("browserbase") is None
    assert get_browse_provider("browser-use") is None
    assert get_extract_provider("agentql") is None
    assert get_extract_provider("stagehand") is None
