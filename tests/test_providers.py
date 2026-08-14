"""Keyless provider registry + external-CLI detection (no network, no subprocess)."""

from __future__ import annotations

from bad_research.providers import (
    EXTERNAL_CLIS,
    PROVIDERS,
    ProviderStatus,
    active_providers,
    external_cli_status,
    provider_status,
)


def test_registry_is_keyless_only():
    names = {p.name for p in PROVIDERS}
    # The keyless surface (INTERFACES_KEYLESS §3.5).
    assert {
        "anthropic-host",
        "websearch",
        "ddgs",
        "searxng",
        "crawl4ai",
        "agent-browser",
        "arxiv",
        "openalex",
        "crossref",
        "europepmc",
        "pubmed",
        "wikipedia",
    } <= names
    # None of the removed keyed providers may appear.
    assert not (
        names & {"cohere", "tavily", "exa", "sonar", "firecrawl", "browserbase", "browser_use", "agentql"}
    )


def test_every_provider_is_keyless():
    for s in provider_status():
        assert s.requires_key is False, f"{s.name} requires a key — not keyless"
        assert s.key_present is True, f"{s.name} should be key_present (no key needed)"


def test_active_reduces_to_import_present_for_self_contained_providers():
    """For everything that runs in-process, active == import_present.

    HOST-BRIDGE providers are the deliberate exception: `websearch` and
    `anthropic-host` are adapters over a Claude-host tool that a `bad …`
    subprocess has no wire to, and they carry no import to check, so
    `import_present` is vacuously True for them. Equating that with "active"
    made `doctor` promise capability the engine could not deliver — the plugin
    bootstrap reads doctor to decide whether it can run at all (issue #35 §2).
    They stay KEYLESS (`requires_key` False); they are simply reported honestly
    as unreachable from here.

    EXTERNAL-ENGINE providers are the same exception for the same reason: the
    social lane shells out to an engine installed out-of-band, so no import can
    tell you whether it is there.
    """
    from bad_research.providers import _EXTERNAL_ENGINE_PROVIDERS, _HOST_BRIDGE_PROVIDERS

    for s in provider_status():
        if s.name in _HOST_BRIDGE_PROVIDERS | _EXTERNAL_ENGINE_PROVIDERS:
            continue
        assert s.active == s.import_present


def test_external_engine_provider_is_inactive_when_not_installed(monkeypatch, tmp_path):
    """An uninstalled social engine reports inactive — never a phantom lane."""
    monkeypatch.setenv("LAST30DAYS_SCRIPT", str(tmp_path / "absent.py"))
    by_name = {s.name: s for s in provider_status()}
    assert by_name["last30days"].active is False
    assert by_name["last30days"].requires_key is False   # still keyless


def test_external_engine_provider_is_active_once_installed(monkeypatch, tmp_path):
    """…and the probe has teeth: point it at a real file and it flips."""
    script = tmp_path / "last30days.py"
    script.write_text("")
    monkeypatch.setenv("LAST30DAYS_SCRIPT", str(script))
    by_name = {s.name: s for s in provider_status()}
    assert by_name["last30days"].active is True


def test_host_bridge_providers_are_inactive_in_a_subprocess(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    by_name = {s.name: s for s in provider_status()}
    assert by_name["websearch"].active is False
    assert by_name["anthropic-host"].active is False
    # …and they remain keyless — this is an honesty fix, not a key requirement.
    assert by_name["websearch"].requires_key is False
    assert by_name["anthropic-host"].requires_key is False


def test_anthropic_host_becomes_active_with_a_key(monkeypatch):
    """A key gives the LLM client a real path, bypassing the absent host bridge."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    by_name = {s.name: s for s in provider_status()}
    assert by_name["anthropic-host"].active is True


def test_anthropic_host_is_base_and_keyless():
    by_name = {p.name: p for p in PROVIDERS}
    p = by_name["anthropic-host"]
    assert p.env_var is None  # host supplies inference; no key
    assert p.extra == "(base)"


def test_external_cli_status_shape():
    rows = external_cli_status()
    by = {r["name"]: r for r in rows}
    # The 4 driven CLIs are reported; SearXNG is NOT (silent/opt-in).
    assert {"agent-browser", "lightpanda", "yt-dlp", "git"} <= set(by)
    assert "searxng" not in {n.lower() for n in by}
    for name, row in by.items():
        assert set(row) == {"name", "present", "hint"}
        assert isinstance(row["present"], bool)
        assert row["hint"] == EXTERNAL_CLIS[name]


def test_git_is_detected_present():
    # git is on every dev box / CI runner.
    rows = {r["name"]: r for r in external_cli_status()}
    assert rows["git"]["present"] is True


def test_status_is_dataclass():
    s = provider_status()[0]
    assert isinstance(s, ProviderStatus)
    assert hasattr(s, "name") and hasattr(s, "active") and hasattr(s, "extra")


def test_active_providers_nonempty_offline():
    # Keyless registry: every provider whose import resolves is active, no keys needed.
    assert active_providers()  # at least the base httpx/ddgs/host rows
