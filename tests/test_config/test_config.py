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
    assert cfg.max_tokens is None
    assert cfg.budget_usd is None
    assert cfg.cheap is False


def test_load_returns_defaults_when_no_env_no_toml(tmp_path: Path) -> None:
    cfg = BadResearchConfig.load(config_path=tmp_path / "missing.toml")
    assert cfg.budget_usd is None
    assert cfg.cheap is False
    assert cfg.reranker == "host"


def test_env_overrides_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("BAD_RESEARCH_BUDGET_USD", "12.50")
    monkeypatch.setenv("BAD_RESEARCH_CHEAP", "1")
    cfg = BadResearchConfig.load(config_path=tmp_path / "missing.toml")
    assert cfg.budget_usd == 12.50
    assert cfg.cheap is True


def test_toml_overrides_default(tmp_path: Path) -> None:
    toml = tmp_path / "config.toml"
    toml.write_text(
        "[bad-research]\n"
        "budget_usd = 7.0\n"
        "cheap = true\n"
        'reranker = "local"\n'
        'browse_engine = "chrome"\n'
        'searxng_endpoint = "http://searx.local:9000"\n'
        'vault_root = "/tmp/custom-vault"\n'
    )
    cfg = BadResearchConfig.load(config_path=toml)
    assert cfg.budget_usd == 7.0
    assert cfg.cheap is True
    assert cfg.reranker == "local"
    assert cfg.browse_engine == "chrome"
    assert cfg.searxng_endpoint == "http://searx.local:9000"
    assert cfg.vault_root == Path("/tmp/custom-vault")


def test_env_beats_toml(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    toml = tmp_path / "config.toml"
    toml.write_text("[bad-research]\nbudget_usd = 7.0\ncheap = false\n")
    monkeypatch.setenv("BAD_RESEARCH_BUDGET_USD", "99.0")
    monkeypatch.setenv("BAD_RESEARCH_CHEAP", "true")
    cfg = BadResearchConfig.load(config_path=toml)
    assert cfg.budget_usd == 99.0  # env wins
    assert cfg.cheap is True       # env wins


def test_cheap_falsey_env_values(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for falsey in ("0", "false", "False", "no", ""):
        monkeypatch.setenv("BAD_RESEARCH_CHEAP", falsey)
        cfg = BadResearchConfig.load(config_path=tmp_path / "missing.toml")
        assert cfg.cheap is False, f"{falsey!r} should parse falsey"
