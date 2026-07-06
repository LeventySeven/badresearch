"""SQLite database management — schema, connection, migrations."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

SCHEMA_VERSION = 10

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS _meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
    id           TEXT PRIMARY KEY,
    title        TEXT NOT NULL,
    path         TEXT NOT NULL UNIQUE,
    status       TEXT NOT NULL DEFAULT 'draft'
                     CHECK (status IN ('draft','review','evergreen','stale','deprecated','archive')),
    type         TEXT NOT NULL DEFAULT 'note'
                     CHECK (type IN ('note','raw','index','moc','interim','source-analysis')),
    tier         TEXT
                     CHECK (tier IS NULL OR tier IN ('ground_truth','institutional','practitioner','commentary','unknown')),
    content_type TEXT
                     CHECK (content_type IS NULL OR content_type IN ('paper','docs','article','blog','forum','dataset','policy','code','book','transcript','review','unknown')),
    source       TEXT,
    parent       TEXT,
    deprecated   INTEGER NOT NULL DEFAULT 0,
    reviewed     TEXT,
    expires      TEXT,
    word_count   INTEGER NOT NULL DEFAULT 0,
    summary      TEXT,
    created      TEXT NOT NULL,
    updated      TEXT,
    file_mtime   REAL NOT NULL,
    content_hash TEXT NOT NULL,
    synced_at    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_notes_status ON notes(status);
CREATE INDEX IF NOT EXISTS idx_notes_type ON notes(type);
CREATE INDEX IF NOT EXISTS idx_notes_parent ON notes(parent);
CREATE INDEX IF NOT EXISTS idx_notes_created ON notes(created);
CREATE INDEX IF NOT EXISTS idx_notes_updated ON notes(updated);
CREATE INDEX IF NOT EXISTS idx_notes_word_count ON notes(word_count);
CREATE INDEX IF NOT EXISTS idx_notes_status_type ON notes(status, type);
CREATE INDEX IF NOT EXISTS idx_notes_parent_status ON notes(parent, status);

CREATE TABLE IF NOT EXISTS note_content (
    note_id    TEXT PRIMARY KEY REFERENCES notes(id) ON DELETE CASCADE,
    body       TEXT NOT NULL,
    body_plain TEXT NOT NULL,
    body_lines TEXT          -- JSON: [[char_start, char_end], ...]; NULL for legacy rows
);

CREATE TABLE IF NOT EXISTS tags (
    note_id TEXT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    tag     TEXT NOT NULL,
    PRIMARY KEY (note_id, tag)
);

CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag);

CREATE TABLE IF NOT EXISTS aliases (
    note_id TEXT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    alias   TEXT NOT NULL,
    PRIMARY KEY (note_id, alias)
);

CREATE INDEX IF NOT EXISTS idx_aliases_alias ON aliases(alias COLLATE NOCASE);

CREATE TABLE IF NOT EXISTS links (
    source_id   TEXT NOT NULL,
    target_ref  TEXT NOT NULL,
    target_id   TEXT,
    line_number INTEGER NOT NULL DEFAULT 0,
    context     TEXT,
    PRIMARY KEY (source_id, target_ref, line_number)
);

CREATE INDEX IF NOT EXISTS idx_links_target ON links(target_id);
CREATE INDEX IF NOT EXISTS idx_links_source ON links(source_id);

-- NOTE: the dead `embeddings` table (vestigial, never populated) was removed in
-- schema v9 — dense vectors now live in the embedded LanceDB `chunks` table
-- (bad_research.retrieval.store). Existing vaults have it dropped by the v9
-- migration (bad_research.core.migrations._migrate_v9_drop_embeddings).
--
-- The narrow hyperresearch `sources` table (url PK + status) is superseded by
-- the provenance `sources` table (source_id PK, domain_tier, fetched dates) —
-- created by bad_research.retrieval.anchors.create_provenance_tables, wired into
-- init_schema below. It is NOT created here so the new shape always wins.

CREATE TABLE IF NOT EXISTS tag_aliases (
    alias     TEXT PRIMARY KEY,
    canonical TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS assets (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id      TEXT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    type         TEXT NOT NULL CHECK (type IN ('image', 'screenshot', 'pdf', 'other')),
    filename     TEXT NOT NULL,
    url          TEXT,
    alt_text     TEXT,
    content_type TEXT,
    size_bytes   INTEGER,
    created_at   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_assets_note ON assets(note_id);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(type);

"""

FTS_SQL = """
CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
    id UNINDEXED,
    title,
    body_plain,
    tags,
    aliases,
    tokenize='porter unicode61'
);
"""

# Indexes on columns added by migrations — must run AFTER migrate() so that
# existing DBs have had the columns added by ALTER TABLE before we index them.
POST_MIGRATE_INDEXES_SQL = """
CREATE INDEX IF NOT EXISTS idx_notes_tier ON notes(tier);
CREATE INDEX IF NOT EXISTS idx_notes_content_type ON notes(content_type);
"""


def get_connection(db_path: Path) -> sqlite3.Connection:
    """Open a SQLite connection with WAL mode and FK enforcement."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    # The pipeline fans out 10-12 fetcher subagents in one wave, each shelling
    # `bad fetch` -> execute_sync -> BEGIN IMMEDIATE (an instant write-lock). Without
    # this, a second concurrent writer gets an immediate `database is locked` and no
    # retry (WAL prevents corruption, not lock contention). busy_timeout makes SQLite
    # block-and-retry the lock internally for up to 5s before erroring.
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """Create all tables if they don't exist, then run pending migrations."""
    conn.executescript(SCHEMA_SQL)
    conn.executescript(FTS_SQL)
    conn.execute(
        "INSERT OR IGNORE INTO _meta (key, value) VALUES ('schema_version', ?)",
        (str(SCHEMA_VERSION),),
    )
    conn.commit()

    # Run any pending migrations (may ALTER TABLE to add new columns, drop the
    # dead embeddings table on v8→v9, etc.)
    from bad_research.core.migrations import migrate
    migrate(conn, SCHEMA_VERSION)

    # Provenance + grounding tables (Plan 02 Task 10): the new `sources` shape
    # (source_id PK) and `claim_anchors`. Idempotent; populated by Plans 05/06.
    from bad_research.retrieval.anchors import create_provenance_tables
    create_provenance_tables(conn)

    # Indexes that depend on migration-added columns run last
    conn.executescript(POST_MIGRATE_INDEXES_SQL)
    conn.commit()


def get_body_lines(conn: sqlite3.Connection, note_id: str) -> list[tuple[int, int]] | None:
    """Return the pre-computed line index for a note body, or None if not stored.

    Callers that need line numbers should call this first; if None is returned,
    they must compute body_to_lines(body) themselves and may optionally store the
    result via store_body_lines().
    """
    row = conn.execute(
        "SELECT body_lines FROM note_content WHERE note_id = ?", (note_id,)
    ).fetchone()
    if row is None or row["body_lines"] is None:
        return None
    import json
    raw = json.loads(row["body_lines"])
    return [(r[0], r[1]) for r in raw]


def store_body_lines(
    conn: sqlite3.Connection,
    note_id: str,
    body_lines: list[tuple[int, int]],
) -> None:
    """Persist a precomputed body_lines index for a note (lazy backfill path)."""
    import json
    conn.execute(
        "UPDATE note_content SET body_lines = ? WHERE note_id = ?",
        (json.dumps(body_lines), note_id),
    )
    conn.commit()


# --- assets write/read path (multimodal host-vision rung) ---------------------
# The `assets` table existed in the schema since v-early but had ZERO writers:
# crawl4ai screenshots and rendered PDF pages were captured then dropped, so the
# host model (natively multimodal) was never pointed at a figure. These helpers
# are the real INSERT path + thin accessors the `bad assets` CLI and the figure-
# reading skill instruction depend on. `filename` is stored RELATIVE to the vault
# root (e.g. `research/assets/<note_id>/<sha>.png`) so the resolved path is
# portable across machines; the CLI joins it back to the live vault root.

_ASSET_TYPES = ("image", "screenshot", "pdf", "other")


@dataclass
class Asset:
    """One persisted asset row. `id` is None until inserted (AUTOINCREMENT)."""

    note_id: str
    type: str
    filename: str
    url: str | None = None
    alt_text: str | None = None
    content_type: str | None = None
    size_bytes: int | None = None
    created_at: str | None = None
    id: int | None = None


def insert_asset(
    conn: sqlite3.Connection,
    *,
    note_id: str,
    filename: str,
    type: str = "image",
    url: str | None = None,
    alt_text: str | None = None,
    content_type: str | None = None,
    size_bytes: int | None = None,
    created_at: str | None = None,
) -> int:
    """INSERT one row into `assets`, returning the new rowid.

    `type` must be one of {'image','screenshot','pdf','other'} (the schema CHECK).
    `created_at` defaults to an ISO-8601 UTC timestamp. This is the single real
    write path for the assets table — used by the screenshot persister and the
    PDF-page renderer so a figure becomes a Read-able PNG bound to its note.
    """
    if type not in _ASSET_TYPES:
        raise ValueError(f"asset type {type!r} not in {_ASSET_TYPES}")
    ts = created_at or datetime.now(UTC).isoformat()
    cur = conn.execute(
        "INSERT INTO assets "
        "(note_id, type, filename, url, alt_text, content_type, size_bytes, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (note_id, type, filename, url, alt_text, content_type, size_bytes, ts),
    )
    conn.commit()
    return int(cur.lastrowid or 0)


def _row_to_asset(row: sqlite3.Row) -> Asset:
    return Asset(
        id=row["id"],
        note_id=row["note_id"],
        type=row["type"],
        filename=row["filename"],
        url=row["url"],
        alt_text=row["alt_text"],
        content_type=row["content_type"],
        size_bytes=row["size_bytes"],
        created_at=row["created_at"],
    )


def list_assets(
    conn: sqlite3.Connection,
    *,
    note_id: str | None = None,
    type: str | None = None,
) -> list[Asset]:
    """Return assets, optionally filtered by note_id and/or type, newest-id first."""
    sql = "SELECT * FROM assets"
    clauses: list[str] = []
    params: list[object] = []
    if note_id is not None:
        clauses.append("note_id = ?")
        params.append(note_id)
    if type is not None:
        clauses.append("type = ?")
        params.append(type)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY id DESC"
    return [_row_to_asset(r) for r in conn.execute(sql, params).fetchall()]


def get_asset(conn: sqlite3.Connection, asset_id: int) -> Asset | None:
    """Return one asset by its integer id, or None."""
    row = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
    return _row_to_asset(row) if row is not None else None
