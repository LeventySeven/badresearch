"""Baselines are keyless: only the host-driven hyperresearch comparator survives.

The keyed deep-research baselines (Perplexity via PPLX_API_KEY, Grok via
XAI_API_KEY) were REMOVED in the keyless re-architecture — they needed third-party
keys, which the keyless rule forbids. `available_baselines()` is now keyless-clean
regardless of any env key.
"""

from __future__ import annotations

from bad_research.calibrate.baselines import (
    available_baselines,
)


def test_keyed_baselines_are_gone():
    """The PerplexityBaseline / GrokBaseline classes no longer exist (keyless)."""
    import bad_research.calibrate.baselines as bl

    assert not hasattr(bl, "PerplexityBaseline")
    assert not hasattr(bl, "GrokBaseline")
    assert "PerplexityBaseline" not in bl.__all__
    assert "GrokBaseline" not in bl.__all__


def test_available_baselines_keyless_clean(monkeypatch):
    """No keyed baseline is offered, even when keyed env vars are set."""
    monkeypatch.setenv("PPLX_API_KEY", "pplx-xxx")
    monkeypatch.setenv("XAI_API_KEY", "xai-xxx")
    names = {b.name for b in available_baselines()}
    assert "perplexity" not in names
    assert "grok" not in names
    # No keyless baseline currently ships under the keyless architecture.
    assert names == set()
