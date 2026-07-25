"""A browse rung that cannot run must SAY SO, not silently return weaker content.

Four shipped skills instruct agents to run `bad fetch --tier-max 3`
(bad-research-5-depth-investigation, -11.5-citation-verifier, -13-gap-fetch,
-16-readability-audit). Rungs 2.5/3 need the `agent-browser` CLI; when it is
absent — which is the default, it is not a pip dep — `get_browse_provider`
returns None, `_do_browse` returns None, and the caller keeps the plain httpx
result. Exit 0, no warning, no metadata.

So the pipeline tells its own agents to escalate to a browser it cannot launch,
and they believe the anti-bot/login-walled page they got back is the real
content. Same silent-degradation class as the funnel's empty-corpus bug: the
caller cannot tell "this rung ran and this is the best available" from "this
rung never ran at all".
"""
from __future__ import annotations

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
