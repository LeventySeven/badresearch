"""claim_anchors -- the byte-identity citation-anchor store. dossier 08 §1.2;
schema verbatim from INTERFACES.md (anchor_id = quote_sha 8-char)."""

from __future__ import annotations

import hashlib
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass, field

from .extract import extract_spans


def quote_sha(quoted_support: str) -> str:
    """8-char SHA-256 of the verbatim quote -- the byte-identity key (frozen)."""
    return hashlib.sha256(quoted_support.encode("utf-8")).hexdigest()[:8]


@dataclass
class ClaimAnchor:
    """One claim->span binding. anchor_id == quote_sha(quoted_support).

    `lookup_key` is how a citation marker ADDRESSES this anchor (a note id, a
    1-based `[N]` ordinal, or -- by default -- the quote SHA itself). It is a
    separate fact from `anchor_id`, which Tier-A byte-identity compares against
    quote_sha(quoted_support)."""

    note_id: str
    char_start: int
    char_end: int
    claim: str
    quoted_support: str
    verified: int = 0  # 0 = unchecked; 1 = passed the verifier (§2)
    verify_score: float | None = None
    anchor_id: str = field(default="")
    line_start: int | None = None   # 1-based line number of span start (nullable for legacy)
    line_end: int | None = None     # 1-based line number of span end (nullable for legacy)
    # Vision-grounding rung: when a claim's evidence is a figure/chart/scanned page,
    # `quoted_support` holds the host's VERBATIM transcription (written into the note
    # body so Tier-A byte-identity still round-trips) and `asset_path` points at the
    # saved PNG. The Tier-C judge re-shows that PNG to the host on the neutral band,
    # so a figure-derived number stays inside the uncited + recitation + verify gates
    # — NOT an ungrounded escape hatch. NULL for ordinary text anchors.
    asset_path: str | None = None
    # How the gate addresses this anchor: `[[note-id]]` -> the note id, `[N]` ->
    # the 1-based ordinal, and by default the quote SHA. Defaults to anchor_id.
    lookup_key: str = ""

    def __post_init__(self) -> None:
        if not self.anchor_id:
            self.anchor_id = quote_sha(self.quoted_support)
        # The gate addresses an anchor by citation marker ("2") or note id; Tier A
        # compares anchor_id against quote_sha(quoted_support). Different facts --
        # sharing one field made Tier A unsatisfiable for every numeric marker.
        if not self.lookup_key:
            self.lookup_key = self.anchor_id


_CLAIM_ANCHORS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS {table} (
    lookup_key     TEXT PRIMARY KEY,   -- how a citation marker addresses this anchor:
                                       -- a note id, a 1-based [N] ordinal, or the SHA
    anchor_id      TEXT NOT NULL,      -- == quote_sha (8-char SHA-256 of quoted_support)
    note_id        TEXT NOT NULL,
    char_start     INTEGER NOT NULL,
    char_end       INTEGER NOT NULL,
    claim          TEXT NOT NULL,
    quoted_support TEXT NOT NULL,
    verified       INTEGER NOT NULL DEFAULT 0,
    verify_score   REAL,
    line_start     INTEGER,            -- 1-based; NULL for legacy anchors
    line_end       INTEGER,            -- 1-based; NULL for legacy anchors
    asset_path     TEXT                -- vision rung: saved PNG for figure-derived claims; NULL otherwise
);
"""

CLAIM_ANCHORS_DDL = _CLAIM_ANCHORS_TABLE_SQL.format(table="claim_anchors") + """
CREATE INDEX IF NOT EXISTS idx_claim_anchors_note ON claim_anchors(note_id);
"""

# Column order used when carrying rows across the legacy-table rebuild.
_ANCHOR_COLUMNS = (
    "anchor_id", "note_id", "char_start", "char_end", "claim", "quoted_support",
    "verified", "verify_score", "line_start", "line_end", "asset_path",
)


class AnchorStore:
    """Thin DAL over the claim_anchors table. Markdown/claims-*.json is truth;
    this table is a cache rebuilt by sync (dossier §1.2)."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def init_schema(self) -> None:
        self.conn.executescript(CLAIM_ANCHORS_DDL)
        cols = {r[1] for r in self.conn.execute("PRAGMA table_info(claim_anchors)")}
        # Forward-compat: a pre-existing claim_anchors table (created before the
        # vision rung) lacks asset_path. CREATE TABLE IF NOT EXISTS won't add it,
        # so ALTER it in (idempotent — ignore "duplicate column").
        if "asset_path" not in cols:
            try:
                self.conn.execute("ALTER TABLE claim_anchors ADD COLUMN asset_path TEXT")
            except sqlite3.OperationalError:
                pass
            else:
                cols = cols | {"asset_path"}
        # Forward-compat: a table older still made anchor_id the PRIMARY KEY *and*
        # the Tier-A quote SHA. Moving the key onto lookup_key cannot be done with
        # ALTER in SQLite, so rebuild (this table is a cache — markdown is truth).
        if "lookup_key" not in cols:
            self._rebuild_without_anchor_id_pk(cols)
        self.conn.commit()

    def _rebuild_without_anchor_id_pk(self, cols: set[str]) -> None:
        """Carry a pre-lookup_key table over to the split-key schema.

        Every legacy row's lookup key IS its old anchor_id — that column doubled as
        the gate's address — so the rebuild is a straight copy plus that aliasing.
        Rebuilding (rather than ALTERing a column in) is what drops the UNIQUE
        constraint on anchor_id: two anchors may now legitimately share a quote SHA
        while being addressed by different citation markers."""
        carried = [c for c in _ANCHOR_COLUMNS if c in cols]
        names = ", ".join(carried)
        self.conn.executescript(_CLAIM_ANCHORS_TABLE_SQL.format(table="claim_anchors__new"))
        self.conn.execute(
            f"INSERT INTO claim_anchors__new (lookup_key, {names}) "
            f"SELECT anchor_id, {names} FROM claim_anchors"
        )
        self.conn.execute("DROP TABLE claim_anchors")
        self.conn.execute("ALTER TABLE claim_anchors__new RENAME TO claim_anchors")
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_claim_anchors_note ON claim_anchors(note_id)"
        )

    def upsert(self, anchor: ClaimAnchor) -> None:
        self.conn.execute(
            "INSERT INTO claim_anchors "
            "(lookup_key, anchor_id, note_id, char_start, char_end, claim, quoted_support, "
            " verified, verify_score, line_start, line_end, asset_path) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(lookup_key) DO UPDATE SET "
            "  anchor_id=excluded.anchor_id, "
            "  note_id=excluded.note_id, char_start=excluded.char_start, "
            "  char_end=excluded.char_end, claim=excluded.claim, "
            "  quoted_support=excluded.quoted_support, "
            "  line_start=excluded.line_start, line_end=excluded.line_end, "
            "  asset_path=excluded.asset_path",
            (
                anchor.lookup_key, anchor.anchor_id, anchor.note_id,
                anchor.char_start, anchor.char_end,
                anchor.claim, anchor.quoted_support, anchor.verified, anchor.verify_score,
                anchor.line_start, anchor.line_end, anchor.asset_path,
            ),
        )
        self.conn.commit()

    def _row_to_anchor(self, row: sqlite3.Row) -> ClaimAnchor:
        # asset_path is absent on legacy rows whose table predates the ALTER — guard
        # on the row's column names (sqlite3.Row `in` matches VALUES, not keys, so we
        # must inspect keys() explicitly) so get/all work against such tables.
        keys = set(row.keys())
        asset_path = row["asset_path"] if "asset_path" in keys else None
        # A row read straight from an un-migrated table has no lookup_key column;
        # there the old anchor_id column WAS the gate's address.
        lookup_key = row["lookup_key"] if "lookup_key" in keys else row["anchor_id"]
        return ClaimAnchor(
            note_id=row["note_id"], char_start=row["char_start"], char_end=row["char_end"],
            claim=row["claim"], quoted_support=row["quoted_support"],
            verified=row["verified"], verify_score=row["verify_score"],
            anchor_id=row["anchor_id"],
            line_start=row["line_start"], line_end=row["line_end"],
            asset_path=asset_path, lookup_key=lookup_key,
        )

    def get(self, lookup_key: str) -> ClaimAnchor | None:
        """Resolve a citation marker (note id, `[N]` ordinal, or quote SHA)."""
        row = self.conn.execute(
            "SELECT * FROM claim_anchors WHERE lookup_key = ?", (lookup_key,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_anchor(row)

    def all(self) -> Iterable[ClaimAnchor]:
        for row in self.conn.execute("SELECT * FROM claim_anchors"):
            yield self._row_to_anchor(row)

    def set_verified(self, lookup_key: str, *, verified: int, score: float | None) -> None:
        """Stamp the disposition on the row the citation marker addresses."""
        self.conn.execute(
            "UPDATE claim_anchors SET verified = ?, verify_score = ? WHERE lookup_key = ?",
            (verified, score, lookup_key),
        )
        self.conn.commit()


def _as_str(value: object) -> str:
    """Coerce a claims-*.json field (str|None) to a plain str ('' for missing)."""
    return value if isinstance(value, str) else ""


def is_vacuous_span(anchor: ClaimAnchor, body: str) -> bool:
    """True when the anchor covers the WHOLE note body, so Tier A proves nothing.

    `tier_a_byte_identity` asks whether `body[char_start:char_end] == quoted_support`.
    When the span is the entire body that reduces to `body == body` and returns True
    for any body at all — including one supporting nothing the report claims. It is a
    check that executes and cannot fail, which is the shape this codebase has already
    shipped once (a coverage checker reporting clean at 11% coverage).

    Measured on a live run of the `--note-bodies` standalone path: all 111 cited
    sentences were seeded whole-body. Before the anchor-binding fix Tier A returned
    False for all 111; after it, True for all 111. Neither number was evidence.

    Callers should treat a vacuous anchor as UNVERIFIED rather than as verified —
    a byte-identity pass over a whole-body span is not grounding, and reporting it
    as one is how a citation gate turns green while checking nothing.
    """
    return anchor.char_start == 0 and anchor.char_end >= len(body)


def build_from_claims(
    store: AnchorStore,
    claims: Iterable[dict[str, object]],
    note_bodies: dict[str, str],
) -> int:
    """Materialize claim_anchors from claims-*.json dicts. Returns the count of
    anchors upserted. A claim whose quoted_support can't be located in its note
    body is DROPPED (dossier §1.1: an unlocatable quote is a hallucinated quote).
    """
    count = 0
    for c in claims:
        quote = _as_str(c.get("quoted_support")).strip()
        note_id = _as_str(c.get("source_note_id"))
        claim_text = _as_str(c.get("claim"))
        if not quote or not note_id:
            continue
        body = note_bodies.get(note_id)
        if body is None:
            continue
        span = extract_spans(claim_text, quote, body)
        if span is None:
            continue  # drop: hallucinated quote
        start, end = span
        # Store the ACTUAL matched body substring as quoted_support, not the
        # (possibly normalized) input quote. For an exact find these are equal;
        # for a fuzzy-located span they differ, and storing the input quote would
        # make Tier-A byte-identity (body[start:end] == quoted_support) ALWAYS
        # fail -> the rescued anchor would be permanently unverifiable. Anchoring
        # to the body slice guarantees the Tier-A round-trip holds (dossier §1.1).
        located = body[start:end]
        # Vision rung: a claim carrying an `asset_path` is figure-derived. The quote
        # is the host's transcription — it MUST already be in the note body (the
        # figure-reading skill writes the transcription verbatim into the note before
        # this binding), so the SAME locate-or-drop discipline applies: an asset_path
        # does NOT bypass the body locate. That keeps figure numbers inside the gates.
        asset_path = _as_str(c.get("asset_path")) or None
        store.upsert(ClaimAnchor(
            note_id=note_id, char_start=start, char_end=end,
            claim=claim_text, quoted_support=located, asset_path=asset_path,
        ))
        count += 1
    return count


def build_figure_anchor(
    store: AnchorStore,
    *,
    note_id: str,
    claim: str,
    transcription: str,
    note_body: str,
    asset_path: str,
) -> ClaimAnchor | None:
    """Bind a figure-derived claim to its host transcription + saved asset (#6).

    The host model (Read on `bad assets path <id>`) transcribes a figure/chart/
    scanned page VERBATIM into the note body; this stores that transcription as the
    anchor's `quoted_support` and records the PNG as `asset_path`. Because the
    transcription must locate inside the live note body (extract_spans, same
    discipline as build_from_claims), the figure-derived number is NOT an
    ungrounded escape hatch: Tier-A byte-identity round-trips, the uncited gate
    sees a real anchor, the recitation gate sees a real quoted span, and the
    Tier-C judge can re-show the PNG. Returns the anchor, or None if the
    transcription is not in the body (a transcription that isn't in the note is a
    hallucinated quote, dossier §1.1)."""
    transcription = (transcription or "").strip()
    if not transcription or not note_id or not asset_path:
        return None
    span = extract_spans(claim, transcription, note_body)
    if span is None:
        return None  # drop: transcription not located in the note body
    start, end = span
    located = note_body[start:end]
    anchor = ClaimAnchor(
        note_id=note_id, char_start=start, char_end=end,
        claim=claim, quoted_support=located, asset_path=asset_path,
    )
    store.upsert(anchor)
    return anchor
