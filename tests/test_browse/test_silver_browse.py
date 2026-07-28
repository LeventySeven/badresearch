"""The SilverProvider browse loop. FakeRunner feeds canned silver envelopes."""

from __future__ import annotations

import pytest

import bad_research.browse.silver as sv
from bad_research.browse.agent_browser import BrowseStep
from bad_research.browse.silver import SilverProvider, parse_snapshot, strip_fence
from bad_research.web.base import WebResult
from tests.test_browse.conftest import (
    SILVER_EMPTY_SNAPSHOT_JSON,
    SILVER_OK_JSON,
    SILVER_OPEN_JSON,
    SILVER_READ_JSON,
    SILVER_SNAPSHOT_JSON,
    FakeRunner,
)

_ROUTE = {
    "open": SILVER_OPEN_JSON,
    "wait": SILVER_OK_JSON,
    "snapshot": SILVER_SNAPSHOT_JSON,
    "read": SILVER_READ_JSON,
    "close": SILVER_OK_JSON,
    "click": SILVER_OK_JSON,
    "fill": SILVER_OK_JSON,
    "keyboard": SILVER_OK_JSON,
}


@pytest.fixture(autouse=True)
def _cli_present(monkeypatch):
    """The loop tests inject a FakeRunner (the CLI stand-in); default the availability
    gate to True so the loop runs without the real silver binary."""
    monkeypatch.setattr(sv, "is_available", lambda program="silver": True)


def _provider(runner: FakeRunner) -> SilverProvider:
    return SilverProvider(runner=runner, session="test")


def test_provider_name() -> None:
    assert _provider(FakeRunner()).name == "silver"


def test_parse_snapshot_builds_refs_from_inline_markers() -> None:
    snap = parse_snapshot(SILVER_SNAPSHOT_JSON)
    assert snap.title == "Example - Log in"
    assert snap.url == "https://example.com/login"
    assert set(snap.refs) == {"e1", "e2", "e3", "e4", "e5", "e6"}
    assert snap.refs["e5"] == {"role": "button", "name": "Continue"}
    # `[level=1, ref=e1]` — the ref is found among other bracket attrs
    assert snap.refs["e1"]["role"] == "heading"
    assert snap.has_ref("@e3") and not snap.has_ref("@e99")


def test_parse_snapshot_strips_the_untrusted_fence() -> None:
    snap = parse_snapshot(SILVER_SNAPSHOT_JSON)
    assert "⟦" not in snap.text and "⟧" not in snap.text


def test_parse_snapshot_tolerates_malformed_or_failed_envelope() -> None:
    assert parse_snapshot("not json").refs == {}
    assert parse_snapshot('{"success": false, "data": null}').refs == {}
    assert parse_snapshot('{"success": true, "data": {"not": "a string"}}').refs == {}


def test_empty_snapshot_is_flagged_empty() -> None:
    assert parse_snapshot(SILVER_EMPTY_SNAPSHOT_JSON).is_empty


def test_strip_fence_is_idempotent_on_unfenced_text() -> None:
    assert strip_fence("plain body") == "plain body"


def test_browse_returns_read_body_not_the_axtree() -> None:
    runner = FakeRunner(route=_ROUTE)
    result = _provider(runner).browse("https://example.com/login", "read the login page")
    assert isinstance(result, WebResult)
    # `read` output wins: prose, not `* button "Continue" [ref=e5]`
    assert "Enter your email and password" in result.content
    assert "[ref=e5]" not in result.content
    assert result.title == "Example - Log in"
    assert result.metadata["engine"] == "silver"
    assert result.metadata["provider"] == "silver"
    assert set(result.metadata["refs"]) == {"e1", "e2", "e3", "e4", "e5", "e6"}


def test_observe_path_never_passes_enable_actions() -> None:
    # No steps → read-only posture. silver refuses actor verbs outright, so a hostile
    # page cannot talk the driver into clicking.
    runner = FakeRunner(route=_ROUTE)
    _provider(runner).browse("https://example.com/login", "just read it")
    assert all("--enable-actions" not in argv for argv in runner.argvs())


def test_first_command_opens_the_requested_url_with_session_flags() -> None:
    runner = FakeRunner(route=_ROUTE)
    _provider(runner).browse("https://example.com/login", "read")
    first = runner.argvs()[0]
    assert first[:3] == ["silver", "open", "https://example.com/login"]
    assert first[-1] == "--json"
    assert "--session" in first and "test" in first
    assert "--namespace" in first and "bad-research" in first


def test_steps_unlock_actions_and_force_a_resnapshot() -> None:
    runner = FakeRunner(route=_ROUTE)
    steps = [
        BrowseStep("fill", "@e3", "user@example.com"),
        BrowseStep("fill", "@e4", "secret"),
        BrowseStep("click", "@e5"),
    ]
    _provider(runner).browse("https://example.com/login", "log in", steps=steps)
    verbs = [argv[1] for argv in runner.argvs()]
    assert verbs.count("fill") == 2
    assert verbs.count("click") == 1
    assert verbs.count("snapshot") >= 2       # initial perception + re-perceive
    # acting posture is granted for the whole session once steps exist
    assert all("--enable-actions" in argv for argv in runner.argvs())


def test_step_grounding_skips_refs_absent_from_snapshot() -> None:
    runner = FakeRunner(route=_ROUTE)
    _provider(runner).browse("https://example.com/login", "click ghost",
                             steps=[BrowseStep("click", "@e99")])
    assert [argv[1] for argv in runner.argvs()].count("click") == 0


def test_press_step_uses_raw_keyboard_not_a_ref() -> None:
    # BrowseStep('press') carries the KEY in `target` (agent-browser parity).
    runner = FakeRunner(route=_ROUTE)
    _provider(runner).browse("https://example.com/login", "submit",
                             steps=[BrowseStep("press", "Enter")])
    kb = [argv for argv in runner.argvs() if argv[1] == "keyboard"]
    assert kb and kb[0][1:4] == ["keyboard", "press", "Enter"]


def test_unknown_step_kind_is_a_noop() -> None:
    runner = FakeRunner(route=_ROUTE)
    result = _provider(runner).browse("https://example.com/login", "weird",
                                      steps=[BrowseStep("teleport", "@e5")])
    assert result.metadata["steps_executed"] == 1  # counted, dispatched to nothing
    assert isinstance(result, WebResult)


def test_max_steps_caps_execution() -> None:
    runner = FakeRunner(route=_ROUTE)
    steps = [BrowseStep("fill", "@e3", str(i)) for i in range(10)]
    result = _provider(runner).browse("https://x.example/", "spam", steps=steps, max_steps=2)
    assert result.metadata["steps_executed"] == 2


def test_read_failure_falls_back_to_the_snapshot_tree() -> None:
    route = dict(_ROUTE, read='{"success": false, "data": null, "error": "boom"}')
    runner = FakeRunner(route=route)
    result = _provider(runner).browse("https://example.com/login", "read")
    assert "Continue" in result.content      # the a11y tree, not an empty note


def test_cli_absent_returns_empty_webresult_no_raise(monkeypatch) -> None:
    monkeypatch.setattr(sv, "is_available", lambda program="silver": False)
    result = _provider(FakeRunner()).browse("https://x.test", "do stuff")
    assert isinstance(result, WebResult)
    assert result.content == ""
    assert result.metadata.get("unavailable") is True


def test_allowed_domains_threads_into_every_command() -> None:
    runner = FakeRunner(route=_ROUTE)
    prov = SilverProvider(runner=runner, session="test", allowed_domains="example.com")
    prov.browse("https://example.com/login", "read")
    assert all("--allowedDomains" in argv for argv in runner.argvs())


def test_state_and_cookie_argv() -> None:
    runner = FakeRunner(replies=[SILVER_OK_JSON])
    SilverProvider(runner=runner, session="s").save_state("/auth/src.json")
    assert runner.last()[:4] == ["silver", "state", "save", "/auth/src.json"]

    runner = FakeRunner(replies=[SILVER_OK_JSON])
    SilverProvider(runner=runner, session="s").cookies_set_curl("/auth/src.curl")
    assert runner.last()[:5] == ["silver", "cookies", "set", "--curl", "/auth/src.curl"]


def test_state_is_loaded_before_navigating() -> None:
    runner = FakeRunner(route=dict(_ROUTE, state=SILVER_OK_JSON))
    _provider(runner).browse("https://src.example/article/1", "read it",
                             state="/auth/src.json")
    assert runner.argvs()[0][1:4] == ["state", "load", "/auth/src.json"]


def test_session_defaults_to_one_per_process() -> None:
    assert sv.default_session(pid=4242) == "br-4242"
