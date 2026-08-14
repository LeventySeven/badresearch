"""Shared test fixtures for bad-research."""

from __future__ import annotations

import os

import pytest

# Keys that mark a "live" run as possible. A `live`-marked test runs only when
# one of these is set AND BAD_RUN_LIVE=1; otherwise it is auto-skipped so the
# default suite is offline + key-free.
# Keyless: ANTHROPIC_API_KEY is the only key any path reads (the headless/calibration
# bridge). Every other capability is keyless (host tools + local OSS/CLIs).
_LIVE_KEYS = ("ANTHROPIC_API_KEY",)


def pytest_collection_modifyitems(config, items):
    """Auto-skip `live` tests unless a provider key is set AND BAD_RUN_LIVE=1."""
    have_any_key = any(os.environ.get(k) for k in _LIVE_KEYS)
    if have_any_key and os.environ.get("BAD_RUN_LIVE") == "1":
        return  # opted into live tests
    skip_live = pytest.mark.skip(
        reason="live test: set a provider key + BAD_RUN_LIVE=1 to run"
    )
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


@pytest.fixture(autouse=True)
def _clear_provider_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure no real provider keys leak into tests from the host environment."""
    for var in (
        "ANTHROPIC_API_KEY",
        "BAD_RESEARCH_CHEAP",
        "BAD_RESEARCH_VAULT_ROOT",
    ):
        monkeypatch.delenv(var, raising=False)
