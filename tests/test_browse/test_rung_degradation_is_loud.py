"""A browse rung that cannot run must SAY SO, not silently return weaker content.

Four shipped skills instruct agents to run `bad fetch --tier-max 3`
(bad-research-5-depth-investigation, -11.5-citation-verifier, -13-gap-fetch,
-16-readability-audit). Rungs 2.5/3 need an external browse CLI — `silver` (the
default) or `agent-browser` (the fallback). When neither is present — which is
the default state, neither is a pip dep — `get_browse_provider` returns None,
`_do_browse` returns None, and the caller keeps the plain httpx result. Exit 0,
no warning, no metadata.

So the pipeline tells its own agents to escalate to a browser it cannot launch,
and they believe the anti-bot/login-walled page they got back is the real
content. Same silent-degradation class as the funnel's empty-corpus bug: the
caller cannot tell "this rung ran and this is the best available" from "this
rung never ran at all".
"""
from __future__ import annotations

import bad_research.browse.base as browse_base
from bad_research.browse.ladder import fetch_tiered
from bad_research.web.base import WebResult


class _HttpxOnly:
    """Rung-0 stand-in.

    Body must exceed the `_is_empty` floor, or the ladder falls through to a
    REAL crawl4ai fetch and the test hits the network.
    """

    def fetch(self, url: str) -> WebResult:
        return WebResult(url=url, title="t", content="page body. " * 80)


_httpx_only = _HttpxOnly()

# Keep the crawl4ai rung hermetic — never touch the network in a unit test.
def _no_tier1():
    return None


def test_unavailable_browse_rung_is_recorded_in_metadata():
    """tier_max=3 requested, no browse provider => the result must admit it."""
    res = fetch_tiered(
        "https://example.org/a",
        tier_max=3,
        instruction="Read the main content.",
        _tier0=_httpx_only,
        _tier1_factory=_no_tier1,
        _browse=None,          # the real-world case: agent-browser not installed
    )
    assert res.metadata.get("browse_unavailable") is True, (
        "a requested-but-unrunnable browse rung left no trace — the caller "
        "cannot distinguish it from a rung that ran and found nothing better"
    )
    assert "agent-browser" in str(res.metadata.get("browse_unavailable_reason", ""))


def test_no_flag_when_the_rung_was_never_requested():
    """tier_max=1 never wanted a browser — that is not a degradation."""
    res = fetch_tiered("https://example.org/a", tier_max=1, _tier0=_httpx_only,
                       _tier1_factory=_no_tier1)
    assert "browse_unavailable" not in res.metadata


def test_no_flag_when_the_rung_actually_ran():
    """A working provider must not be reported as unavailable."""

    class _Browse:
        def browse(self, url, instruction, *, replay_key=None, variables=None):
            return WebResult(url=url, title="t", content="full rendered content")

    res = fetch_tiered(
        "https://example.org/a",
        tier_max=3,
        instruction="Read the main content.",
        _tier0=_httpx_only,
        _tier1_factory=_no_tier1,
        _browse=_Browse(),
    )
    assert "browse_unavailable" not in res.metadata
    assert res.content == "full rendered content"


# ---------------------------------------------------------------------------
# The DEFAULT seam. Every production caller (core/fetcher.py, cli/vault_cmds.py)
# omits `_browse` entirely, so it takes the `_UNSET` default rather than None.
# The tests above all pass `_browse=` explicitly and therefore cannot see a
# regression on that path — which is exactly how `elif _browse is None` survived
# a conflict-free merge as dead code once `_UNSET` became the default.
# ---------------------------------------------------------------------------


def test_default_seam_records_unavailable_when_no_cli_resolves(monkeypatch):
    """No `_browse=` kwarg at all — the production shape. When the default
    resolution finds no CLI, the flag must STILL be stamped."""
    monkeypatch.setattr(browse_base, "get_browse_provider", lambda name=None: None)

    res = fetch_tiered(
        "https://example.org/a",
        tier_max=3,
        instruction="Read the main content.",
        _tier0=_httpx_only,
        _tier1_factory=_no_tier1,
        # NO _browse= — this is what core/fetcher.py and cli/vault_cmds.py do.
    )
    assert res.metadata.get("browse_unavailable") is True, (
        "the honesty flag is dead on the default seam: production callers omit "
        "`_browse`, so a condition keyed on `_browse is None` never fires"
    )
    reason = str(res.metadata.get("browse_unavailable_reason", ""))
    assert "silver" in reason, "the remedy must name silver — it is the default backend"
    assert "agent-browser" in reason, "the agent-browser fallback must still be offered"


def test_default_seam_uses_the_resolved_provider_and_sets_no_flag(monkeypatch):
    """The default seam must actually RESOLVE a provider, not skip the rung."""

    class _Browse:
        def browse(self, url, instruction, *, replay_key=None, variables=None):
            return WebResult(url=url, title="t", content="rendered by the default seam")

    monkeypatch.setattr(browse_base, "get_browse_provider", lambda name=None: _Browse())

    res = fetch_tiered(
        "https://example.org/a",
        tier_max=3,
        instruction="Read the main content.",
        _tier0=_httpx_only,
        _tier1_factory=_no_tier1,
    )
    assert res.content == "rendered by the default seam"
    assert "browse_unavailable" not in res.metadata


def test_no_false_flag_when_a_bound_provider_simply_found_nothing_better(monkeypatch):
    """A provider that ran and returned junk is NOT 'unavailable'. The flag must
    distinguish "the rung never ran" from "the rung ran and lost"."""

    class _EmptyBrowse:
        def browse(self, url, instruction, *, replay_key=None, variables=None):
            return WebResult(url=url, title="", content="   ")

    monkeypatch.setattr(browse_base, "get_browse_provider", lambda name=None: _EmptyBrowse())

    res = fetch_tiered(
        "https://example.org/a",
        tier_max=3,
        instruction="Read the main content.",
        _tier0=_httpx_only,
        _tier1_factory=_no_tier1,
    )
    assert "browse_unavailable" not in res.metadata
    assert res.content.startswith("page body.")


def test_browse_cli_available_covers_silver_not_just_agent_browser(monkeypatch):
    """The probe must cover BOTH backends. Probing agent-browser only would tell a
    silver-only machine to install the wrong CLI (and vice versa)."""
    import bad_research.browse.agent_browser as ab
    import bad_research.browse.silver as sv
    from bad_research.browse.ladder import _browse_cli_available

    monkeypatch.setattr(sv, "is_available", lambda program="silver": True)
    monkeypatch.setattr(ab, "is_available", lambda program="agent-browser": False)
    assert _browse_cli_available() is True, "silver alone must count as available"

    monkeypatch.setattr(sv, "is_available", lambda program="silver": False)
    monkeypatch.setattr(ab, "is_available", lambda program="agent-browser": True)
    assert _browse_cli_available() is True, "agent-browser alone must count as available"

    monkeypatch.setattr(ab, "is_available", lambda program="agent-browser": False)
    assert _browse_cli_available() is False
