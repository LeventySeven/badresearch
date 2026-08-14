"""Tests for BadResearchConfig — defaults, env precedence, TOML precedence."""

from __future__ import annotations

from pathlib import Path

import pytest

from bad_research.config import BadResearchConfig


def test_defaults_match_interfaces() -> None:
    """The frozen defaults from INTERFACES.md."""
    cfg = BadResearchConfig()
    assert cfg.vault_root == Path.home() / ".bad-research"
    assert cfg.model_tiers == {
        "triage": "claude-haiku-4-5",
        "work": "claude-sonnet-4-6",
        "heavy": "claude-opus-4-7",
    }
    assert cfg.reranker == "host"
    assert cfg.neural_recall is False
    assert cfg.searxng_endpoint == "http://localhost:8080"
    assert cfg.browse_engine == "silver"
    assert cfg.effort == "medium"
    assert cfg.cheap is False


def test_dead_budget_dials_are_gone(tmp_path: Path) -> None:
    """`max_tokens` and `budget_usd` were parsed from TOML+env and read by NOTHING —
    three dials that silently did nothing (there is no token/cost meter in the
    package; the run-level ceiling the orchestrator honours is the `--max-tokens`
    CLI value it tracks in prose). A dial that does nothing is worse than no dial."""
    cfg = BadResearchConfig.load(config_path=tmp_path / "missing.toml")
    assert not hasattr(cfg, "max_tokens")
    assert not hasattr(cfg, "budget_usd")


def test_removed_dials_in_toml_or_env_are_ignored_not_fatal(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """An existing user config that still carries the removed keys must keep loading —
    unknown TOML keys and stale env vars are ignored, never a crash."""
    toml = tmp_path / "config.toml"
    toml.write_text("[bad-research]\nbudget_usd = 7.0\nmax_tokens = 500000\ncheap = true\n")
    monkeypatch.setenv("BAD_RESEARCH_BUDGET_USD", "99.0")
    monkeypatch.setenv("BAD_RESEARCH_MAX_TOKENS", "123")
    cfg = BadResearchConfig.load(config_path=toml)
    assert cfg.cheap is True
    assert not hasattr(cfg, "budget_usd")
    assert not hasattr(cfg, "max_tokens")


def test_load_returns_defaults_when_no_env_no_toml(tmp_path: Path) -> None:
    cfg = BadResearchConfig.load(config_path=tmp_path / "missing.toml")
    assert cfg.cheap is False
    assert cfg.reranker == "host"


def test_env_overrides_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("BAD_RESEARCH_CHEAP", "1")
    monkeypatch.setenv("BAD_RESEARCH_RERANKER", "local")
    cfg = BadResearchConfig.load(config_path=tmp_path / "missing.toml")
    assert cfg.cheap is True
    assert cfg.reranker == "local"


def test_toml_overrides_default(tmp_path: Path) -> None:
    toml = tmp_path / "config.toml"
    toml.write_text(
        "[bad-research]\n"
        "cheap = true\n"
        'reranker = "local"\n'
        'browse_engine = "chrome"\n'
        'searxng_endpoint = "http://searx.local:9000"\n'
        'vault_root = "/tmp/custom-vault"\n'
    )
    cfg = BadResearchConfig.load(config_path=toml)
    assert cfg.cheap is True
    assert cfg.reranker == "local"
    assert cfg.browse_engine == "chrome"
    assert cfg.searxng_endpoint == "http://searx.local:9000"
    assert cfg.vault_root == Path("/tmp/custom-vault")


def test_env_beats_toml(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    toml = tmp_path / "config.toml"
    toml.write_text('[bad-research]\ncheap = false\nreranker = "none"\n')
    monkeypatch.setenv("BAD_RESEARCH_CHEAP", "true")
    monkeypatch.setenv("BAD_RESEARCH_RERANKER", "local")
    cfg = BadResearchConfig.load(config_path=toml)
    assert cfg.cheap is True         # env wins
    assert cfg.reranker == "local"   # env wins


def test_cheap_falsey_env_values(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for falsey in ("0", "false", "False", "no", ""):
        monkeypatch.setenv("BAD_RESEARCH_CHEAP", falsey)
        cfg = BadResearchConfig.load(config_path=tmp_path / "missing.toml")
        assert cfg.cheap is False, f"{falsey!r} should parse falsey"
