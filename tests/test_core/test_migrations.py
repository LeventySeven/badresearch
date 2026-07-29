"""Migration upgrade-path tests (previously untested — audit underkill).

Exercises the v6→current upgrade with real data through the destructive v7/v8 table
rebuilds, and the crash-recovery re-run case the atomicity guard must survive.
"""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest

from bad_research.core.db import SCHEMA_VERSION, get_connection
from bad_research.core.migrations import get_schema_version, migrate

_V6_NOTES = """
CREATE TABLE _meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE notes (
    id      TEXT PRIMARY KEY,
    title   TEXT NOT NULL,
    path    TEXT NOT NULL UNIQUE,
    type    TEXT NOT NULL DEFAULT 'note' CHECK (type IN ('note','raw','index','moc')),
    created TEXT NOT NULL
);
CREATE TABLE note_content (
    note_id TEXT PRIMARY KEY REFERENCES notes(id) ON DELETE CASCADE,
    body    TEXT NOT NULL DEFAULT ''
);
INSERT INTO _meta (key, value) VALUES ('schema_version', '6');
INSERT INTO notes (id, title, path, type, created)
VALUES ('n1', 'Preserved Title', 'notes/n1.md', 'note', '2026-01-01T00:00:00Z');
INSERT INTO note_content (note_id, body) VALUES ('n1', 'body text');
"""


def _v6_db(path: Path) -> sqlite3.Connection:
    conn = get_connection(path)
    conn.executescript(_V6_NOTES)
    conn.commit()
    return conn


def test_v6_to_current_upgrade_preserves_data_and_adds_new_types():
    with tempfile.TemporaryDirectory() as d:
        conn = _v6_db(Path(d) / "v6.db")
        applied = migrate(conn, SCHEMA_VERSION)
        # the destructive rebuilds (v7 interim, v8 source-analysis) ran
        assert 7 in applied and 8 in applied
        assert get_schema_version(conn) == SCHEMA_VERSION
        # data survived the DROP/RENAME rebuild
        row = conn.execute("SELECT id, title, type FROM notes WHERE id='n1'").fetchone()
        assert row["id"] == "n1" and row["title"] == "Preserved Title" and row["type"] == "note"
        # the new CHECK types the rebuilds added are now accepted
        for t in ("interim", "source-analysis"):
            conn.execute(
                "INSERT INTO notes (id, title, path, type, created) "
                "VALUES (?, 't', ?, ?, '2026-01-01T00:00:00Z')",
                (f"id-{t}", f"notes/{t}.md", t),
            )


def test_migrate_is_idempotent():
    with tempfile.TemporaryDirectory() as d:
        conn = _v6_db(Path(d) / "v6.db")
        migrate(conn, SCHEMA_VERSION)
        assert migrate(conn, SCHEMA_VERSION) == []  # already current -> no-op
        assert get_schema_version(conn) == SCHEMA_VERSION


def test_rebuild_survives_a_stale_notes_v7_from_a_crashed_prior_run():
    # A crash mid-rebuild can leave an orphan `notes_v7`. The migration must not choke
    # on it (the DROP TABLE IF EXISTS guard) — CREATE TABLE notes_v7 would otherwise fail.
    with tempfile.TemporaryDirectory() as d:
        conn = _v6_db(Path(d) / "v6.db")
        conn.execute("CREATE TABLE notes_v7 (id TEXT PRIMARY KEY, junk TEXT)")
        conn.commit()
        migrate(conn, SCHEMA_VERSION)  # must not raise
        assert get_schema_version(conn) == SCHEMA_VERSION
        assert conn.execute("SELECT id FROM notes WHERE id='n1'").fetchone() is not None
