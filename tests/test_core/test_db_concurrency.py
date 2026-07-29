"""Concurrency-hardening for the vault DB.

The pipeline spawns 10-12 fetcher subagents in one wave, each shelling `bad fetch`
-> execute_sync -> BEGIN IMMEDIATE (an instant write-lock). Without busy_timeout a
second writer gets an immediate `database is locked` OperationalError and no retry.
WAL prevents corruption but not spurious write failures. busy_timeout makes SQLite
block-and-retry internally up to the timeout instead of erroring instantly.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from bad_research.core.db import get_connection


def test_get_connection_sets_busy_timeout():
    with tempfile.TemporaryDirectory() as d:
        conn = get_connection(Path(d) / "t.db")
        (val,) = conn.execute("PRAGMA busy_timeout").fetchone()
        assert val >= 5000, f"busy_timeout should be >=5s, got {val}ms"


def test_get_connection_keeps_wal():
    with tempfile.TemporaryDirectory() as d:
        conn = get_connection(Path(d) / "t.db")
        (mode,) = conn.execute("PRAGMA journal_mode").fetchone()
        assert mode.lower() == "wal"
