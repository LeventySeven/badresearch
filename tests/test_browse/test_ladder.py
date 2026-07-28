"""fetch_tiered escalation — 4-rung keyless ladder. All providers mocked, no subprocess."""

from __future__ import annotations

from unittest.mock import MagicMock

from bad_research.browse.ladder import fetch_tiered
from tests.test_browse.conftest import make_result


def _good(url="https://x.test"):
    return make_result("Substantial real article content. " * 30, url=url, title="Real")


def _empty(url="https://x.test"):
    return make_result("tiny", url=url, title="Stub")


def _bot(url="https://x.test"):
    return make_result("Just a moment... checking your browser ray id " * 10,
                       url=url, title="Just a moment...")


def _login(url="https://x.test/login"):
    return make_result("Please sign in. create account.", url=url, title="Sign in")


def test_rung1_good_result_no_escalation() -> None:
    t0 = MagicMock()
    t0.fetch.return_value = _good()
    t1 = MagicMock()
    r = fetch_tiered("https://x.test", tier_max=3, _tier0=t0, _tier1_factory=lambda: t1)
    assert r.content.startswith("Substantial real")
    t0.fetch.assert_called_once()
    t1.fetch.assert_not_called()


def test_rung1_empty_escalates_to_rung2_crawl4ai() -> None:
    t0 = MagicMock()
    t0.fetch.return_value = _empty()
    t1 = MagicMock()
    t1.fetch.return_value = _good()
    r = fetch_tiered("https://x.test", tier_max=3, _tier0=t0, _tier1_factory=lambda: t1)
    assert r.content.startswith("Substantial real")
    t1.fetch.assert_called_once()


def test_rung2_unavailable_keeps_rung1() -> None:
    t0 = MagicMock()
    t0.fetch.return_value = _empty()
    r = fetch_tiered("https://x.test", tier_max=3, _tier0=t0, _tier1_factory=lambda: None)
    assert r.content == "tiny"


def test_tier_max_caps_at_rung1() -> None:
    t0 = MagicMock()
    t0.fetch.return_value = _empty()
    t1 = MagicMock()
    t1.fetch.return_value = _good()
    r = fetch_tiered("https://x.test", tier_max=0, _tier0=t0, _tier1_factory=lambda: t1)
    assert r.content == "tiny"
    t1.fetch.assert_not_called()


def test_bot_wall_escalates_to_browse_rung() -> None:
    t0 = MagicMock()
    t0.fetch.return_value = _empty()
    t1 = MagicMock()
    t1.fetch.return_value = _bot()
    ab = MagicMock()
    ab.browse.return_value = make_result("The recovered article body. " * 20)
    r = fetch_tiered("https://x.test", tier_max=3,
                     _tier0=t0, _tier1_factory=lambda: t1, _browse=ab)
    assert "The recovered article body" in r.content
    ab.browse.assert_called_once()


def test_bot_wall_that_survives_the_browse_rung_is_not_stored() -> None:
    # Escalating to beat a wall and landing on the same wall is a FAILED fetch: the
    # interstitial must not be handed back as if it were the source.
    t0 = MagicMock()
    t0.fetch.return_value = _empty()
    t1 = MagicMock()
    t1.fetch.return_value = _bot()
    ab = MagicMock()
    ab.browse.return_value = make_result(
        "Performing security verification. Ray ID: a224d90e. Cloudflare. " * 10
    )
    r = fetch_tiered("https://x.test", tier_max=3,
                     _tier0=t0, _tier1_factory=lambda: t1, _browse=ab)
    ab.browse.assert_called_once()
    assert "Ray ID" not in r.content          # the browse wall was rejected
    assert r.content == t1.fetch.return_value.content   # kept the lower-tier result


def test_login_wall_escalates_to_agent_browser_with_instruction() -> None:
    t0 = MagicMock()
    t0.fetch.return_value = _empty("https://x.test/login")
    t1 = MagicMock()
    t1.fetch.return_value = _login()
    ab = MagicMock()
    ab.browse.return_value = make_result("Logged-in dashboard content. " * 20)
    r = fetch_tiered("https://x.test/login", tier_max=3, instruction="log in",
                     _tier0=t0, _tier1_factory=lambda: t1, _browse=ab)
    assert "Logged-in dashboard" in r.content
    ab.browse.assert_called_once()


def test_instruction_triggers_rung3_browse() -> None:
    t0 = MagicMock()
    t0.fetch.return_value = _empty()
    t1 = MagicMock()
    t1.fetch.return_value = _good()
    ab = MagicMock()
    ab.browse.return_value = make_result("All 50 reviews loaded. " * 10)
    r = fetch_tiered("https://x.test", tier_max=3, instruction="load all reviews",
                     _tier0=t0, _tier1_factory=lambda: t1, _browse=ab)
    assert "All 50 reviews" in r.content
    ab.browse.assert_called_once()


def test_no_browse_provider_stays_on_lower_tier() -> None:
    # `_browse=None` means "the caller resolved a provider and found none" — the rung is
    # skipped. (It must NOT fall through to resolving a real CLI off PATH, or this test
    # drives a live browser on any machine that has one installed.)
    t0 = MagicMock()
    t0.fetch.return_value = _good()
    r = fetch_tiered("https://x.test", tier_max=3, instruction="paginate",
                     _tier0=t0, _tier1_factory=lambda: MagicMock(), _browse=None)
    assert r.content.startswith("Substantial real")


def test_schema_triggers_aql_or_llm_extract_attaches_dict() -> None:
    t0 = MagicMock()
    t0.fetch.return_value = _good()
    extractor = MagicMock()
    extractor.extract.return_value = {"title": "Real", "n": 3}
    r = fetch_tiered("https://x.test", tier_max=2,
                     schema={"type": "object", "properties": {"title": {"type": "string"}}},
                     _tier0=t0, _tier1_factory=lambda: MagicMock(), _extractor=extractor)
    assert r.metadata["extracted"] == {"title": "Real", "n": 3}
    assert r.content.startswith("Substantial real")
    extractor.extract.assert_called_once()


def test_replay_key_threaded_to_browse() -> None:
    t0 = MagicMock()
    t0.fetch.return_value = _empty("https://x.test/login")
    t1 = MagicMock()
    t1.fetch.return_value = _login()
    ab = MagicMock()
    ab.browse.return_value = make_result("dashboard " * 60)
    fetch_tiered("https://x.test/login", tier_max=3, instruction="log in",
                 replay_key="rk-123",
                 _tier0=t0, _tier1_factory=lambda: t1, _browse=ab)
    _, kwargs = ab.browse.call_args
    assert kwargs["replay_key"] == "rk-123"


def test_ssrf_blocked_entry_url_skips_browse_rung() -> None:
    # An internal target must never drive the browser. The browse rung is skipped; the
    # best lower-tier result is returned (no raise out of the ladder).
    t0 = MagicMock()
    t0.fetch.return_value = _empty("http://169.254.169.254/latest/")
    t1 = MagicMock()
    t1.fetch.return_value = _bot("http://169.254.169.254/")
    ab = MagicMock()
    ab.browse.return_value = make_result("should never be reached " * 20)
    r = fetch_tiered("http://169.254.169.254/", tier_max=3, instruction="read it",
                     _tier0=t0, _tier1_factory=lambda: t1, _browse=ab)
    ab.browse.assert_not_called()           # SSRF entry-gate skipped the browse rung
    assert "should never be reached" not in r.content


def test_ssrf_browse_lands_on_internal_url_is_discarded() -> None:
    # agent-browser reports a final/landed URL that is internal (a mid-nav redirect) →
    # the result is discarded and the lower-tier result kept (final-URL re-validation).
    t0 = MagicMock()
    t0.fetch.return_value = _bot("https://public.test/")
    ab = MagicMock()
    ab.browse.return_value = make_result("leaked internal page " * 20,
                                         url="http://127.0.0.1:8080/admin")
    r = fetch_tiered("https://public.test/", tier_max=3, instruction="read it",
                     _tier0=t0, _tier1_factory=lambda: None, _browse=ab)
    assert "leaked internal page" not in r.content   # landed-URL re-validation discarded it
