"""`run_funnel` must release its SQLite handles on BOTH paths (issue #35 §7).

`run_funnel` builds a RetrievalEngine (2 connections) and a Vault (1) per call
and used to drop them on the floor. In the CLI that only showed up as a
`ResourceWarning: unclosed database` at exit; in the MCP server — where
`run_funnel` is the tool body inside a long-lived process — the handles pile up
per call.

The assertions are on the connection OBJECTS, not on ResourceWarning: that
warning only exists on CPython >= 3.13, so a warnings-based test would pass
vacuously on 3.12 and prove nothing.
"""
import sqlite3

import pytest

import bad_research.cli.research as RESEARCH  # noqa: N812
from bad_research.core.vault import Vault


def _wire(monkeypatch, tmp_path):
    """A real vault + a real engine, with every network edge removed.

    No providers at all: Stage A fans out to nothing, so the run is a
    fast, offline, deterministic degraded envelope. Whether the run FOUND
    anything is orthogonal to whether it cleaned up after itself.
    """
    Vault.init(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(RESEARCH, "_build_providers", lambda cfg: [])
    monkeypatch.setattr(RESEARCH, "_build_vertical_providers", lambda q: [])
    monkeypatch.setattr(RESEARCH, "_build_tiered_fetcher", lambda cfg: object())

    engines: list[object] = []
    real_build = RESEARCH._build_engine

    def _spy_build(cfg, vault):
        eng = real_build(cfg, vault)
        engines.append(eng)
        return eng

    monkeypatch.setattr(RESEARCH, "_build_engine", _spy_build)

    vault_closes = {"n": 0}
    real_vault_close = Vault.close

    def _counting_close(self):
        vault_closes["n"] += 1
        real_vault_close(self)

    monkeypatch.setattr(Vault, "close", _counting_close)
    return engines, vault_closes


def _assert_engine_released(engine):
    with pytest.raises(sqlite3.ProgrammingError):
        engine.conn.execute("SELECT 1")
    with pytest.raises(sqlite3.ProgrammingError):
        engine.cache.conn.execute("SELECT 1")


def test_run_funnel_closes_engine_and_vault(monkeypatch, tmp_path):
    engines, vault_closes = _wire(monkeypatch, tmp_path)

    result = RESEARCH.run_funnel("keyless retrieval", mode="light", vault_tag="t")

    assert result["degraded"] is True  # no providers wired — the expected envelope
    assert len(engines) == 1, "run_funnel should build exactly one engine"
    _assert_engine_released(engines[0])
    assert vault_closes["n"] == 1, "the vault connection was never closed"


def test_run_funnel_still_closes_when_gather_raises(monkeypatch, tmp_path):
    """The error path is the one that matters: `funnel_gather_cmd` catches any
    exception out of `run_funnel` and reports `{"ok": false}`, so without a
    `finally` a failing run leaks silently AND repeatedly (an orchestrator
    retries). The original exception must reach the caller unchanged — cleanup
    must never become the reported error."""
    engines, vault_closes = _wire(monkeypatch, tmp_path)

    async def _boom(*a, **k):
        raise RuntimeError("fan-out exploded")

    monkeypatch.setattr("bad_research.funnel.gather", _boom)

    with pytest.raises(RuntimeError, match="fan-out exploded"):
        RESEARCH.run_funnel("keyless retrieval", mode="light", vault_tag="t")

    assert len(engines) == 1
    _assert_engine_released(engines[0])
    assert vault_closes["n"] == 1, "the vault leaked on the error path"


def test_retrieve_cmd_closes_the_same_two_connections(monkeypatch, tmp_path):
    """`bad retrieve` builds the identical engine + vault pair and leaked them
    per invocation for the same reason."""
    engines, vault_closes = _wire(monkeypatch, tmp_path)

    RESEARCH.retrieve_cmd("keyless retrieval", mode="light", top_k=5,
                          json_output=False)

    assert len(engines) == 1
    _assert_engine_released(engines[0])
    assert vault_closes["n"] == 1
