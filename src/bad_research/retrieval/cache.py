"""Negation-guarded semantic query cache (dossier 04 §4.1-§4.3).

0.92-cosine over cached query embeddings; a HIT is suppressed when the new
query adds a negation marker the cached query lacked (NIA's documented defect —
the embedder is negation-blind, so an affirmative query and its negation embed
nearly identically; without this guard the cache would serve the wrong answer)."""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from bad_research.embed.base import EmbedProvider
from bad_research.retrieval.constants import (
    LLM_RERANK_STOPWORDS,
    NEGATION_PATTERN,
    SEMANTIC_CACHE_THRESHOLD,
    SEMANTIC_CACHE_THRESHOLD_LEXICAL,
)
from bad_research.search.fts import preprocess_query

_NEG_RE = re.compile(NEGATION_PATTERN, re.IGNORECASE)

_DDL = """
CREATE TABLE IF NOT EXISTS query_cache (
    query_text   TEXT PRIMARY KEY,
    embedding    TEXT NOT NULL,   -- json list[float]
    has_negation INTEGER NOT NULL,
    payload      TEXT NOT NULL,   -- json
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def has_negation(query: str) -> bool:
    return bool(_NEG_RE.search(query))


def negation_markers(query: str) -> frozenset[str]:
    """The SET of distinct negation markers in a query (lowercased). Comparing
    marker SETS (not just the has-negation boolean) is what lets the lexical cache
    distinguish e.g. "...in no_std" (markers {no_std}) from "...NOT ... in no_std"
    (markers {not, no_std}) — the second adds a negation the first lacked, so it
    must MISS even though both are "negated" and the token overlap is 1.0."""
    return frozenset(m.lower() for m in _NEG_RE.findall(query))


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = sum(x * x for x in a) ** 0.5 or 1.0
    nb = sum(y * y for y in b) ** 0.5 or 1.0
    return dot / (na * nb)


class SemanticCache:
    def __init__(self, db_path: Path, embedder: EmbedProvider,
                 *, threshold: float = SEMANTIC_CACHE_THRESHOLD):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.embedder = embedder
        self.threshold = threshold
        self.conn = sqlite3.connect(str(self.path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_DDL)
        self.conn.commit()

    def get(self, query: str) -> dict[str, Any] | None:
        qv = self.embedder.embed([query], input_type="query")[0]
        q_neg = has_negation(query)
        best = None
        best_sim = -1.0
        for row in self.conn.execute(
            "SELECT query_text, embedding, has_negation, payload FROM query_cache"
        ):
            cv = json.loads(row["embedding"])
            if len(cv) != len(qv):
                continue
            sim = _cosine(qv, cv)
            if sim > best_sim:
                best_sim, best = sim, row
        if best is None or best_sim < self.threshold:
            return None
        # Negation guard: a HIT requires the new query and the cached query to
        # AGREE on negation. If they disagree (one negates, the other doesn't),
        # force a miss (NIA §4.3) — negation-blind embeddings make them look
        # near-identical, but they are semantically opposite.
        if q_neg != bool(best["has_negation"]):
            return None
        return {"payload": json.loads(best["payload"]),
                "cache_similarity": best_sim,
                "original_query": best["query_text"]}

    def put(self, query: str, payload: dict[str, Any]) -> None:
        qv = self.embedder.embed([query], input_type="query")[0]
        self.conn.execute(
            "INSERT OR REPLACE INTO query_cache (query_text, embedding, has_negation, payload) "
            "VALUES (?, ?, ?, ?)",
            (query, json.dumps(qv), int(has_negation(query)), json.dumps(payload)),
        )
        self.conn.commit()

    def close(self) -> None:
        """Release the SQLite handle (issue #35 §7). Idempotent — sqlite3 tolerates
        a repeated close, and every `put` already commits, so nothing is lost."""
        self.conn.close()


# ── Keyless token-set cache (dossier 15 §6.2) — the FTS-default backend ───────

_LEX_DDL = """
CREATE TABLE IF NOT EXISTS query_cache_lex (
    query_text   TEXT PRIMARY KEY,
    tokens       TEXT NOT NULL,   -- json sorted list[str]
    has_negation INTEGER NOT NULL,
    neg_markers  TEXT NOT NULL DEFAULT '[]',  -- json sorted list[str] of negation markers
    payload      TEXT NOT NULL,   -- json
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def _normalize_tokens(query: str) -> frozenset[str]:
    """Lowercase, strip FTS markers, drop the tiny stopword set (dossier 15 §6.2)."""
    raw = preprocess_query(query).replace('"', "").replace("*", "")
    toks = (w.lower() for w in raw.split())
    return frozenset(t for t in toks if t and t not in LLM_RERANK_STOPWORDS)


def _token_sim(a: frozenset[str], b: frozenset[str]) -> float:
    """Overlap coefficient: |a∩b| / min(|a|,|b|). Recall-biased so suffix noise
    on the larger side still scores high (dossier 15 §6.2)."""
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


class LexicalCacheBackend:
    """Keyless token-set semantic cache (dossier 15 §6.2). HIT at overlap ≥ 0.85
    with the negation guard. Catches reorder + suffix-noise; misses true
    paraphrase (which just re-runs — never a wrong answer). Same get/put surface
    as SemanticCache."""

    def __init__(self, db_path: Path,
                 *, threshold: float = SEMANTIC_CACHE_THRESHOLD_LEXICAL):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.threshold = threshold
        self.conn = sqlite3.connect(str(self.path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_LEX_DDL)
        self.conn.commit()

    def get(self, query: str) -> dict[str, Any] | None:
        q_tokens = _normalize_tokens(query)
        q_markers = negation_markers(query)
        best = None
        best_sim = -1.0
        for row in self.conn.execute(
            "SELECT query_text, tokens, neg_markers, payload FROM query_cache_lex"
        ):
            cached = frozenset(json.loads(row["tokens"]))
            sim = _token_sim(q_tokens, cached)
            if sim > best_sim:
                best_sim, best = sim, row
        if best is None or best_sim < self.threshold:
            return None
        # Negation guard: the new query must not introduce a negation marker the
        # cached query lacked (and vice-versa). Comparing marker SETS — not the
        # has-negation boolean — distinguishes "...in no_std" from "...NOT...no_std"
        # even though both are "negated" and overlap is 1.0 (dossier 15 §6.2).
        cached_markers = frozenset(json.loads(best["neg_markers"]))
        if q_markers != cached_markers:
            return None
        return {"payload": json.loads(best["payload"]),
                "cache_similarity": best_sim,
                "original_query": best["query_text"]}

    def put(self, query: str, payload: dict[str, Any]) -> None:
        tokens = sorted(_normalize_tokens(query))
        markers = sorted(negation_markers(query))
        self.conn.execute(
            "INSERT OR REPLACE INTO query_cache_lex "
            "(query_text, tokens, has_negation, neg_markers, payload) "
            "VALUES (?, ?, ?, ?, ?)",
            (query, json.dumps(tokens), int(has_negation(query)),
             json.dumps(markers), json.dumps(payload)),
        )
        self.conn.commit()

    def close(self) -> None:
        """Release the SQLite handle (issue #35 §7). Idempotent — sqlite3 tolerates
        a repeated close, and every `put` already commits, so nothing is lost."""
        self.conn.close()


def get_cache(db_path: Path, *, embedder: EmbedProvider | None = None) -> Any:
    """Select the cache backend (INTERFACES_KEYLESS §5.5): token-set lexical when
    no embedder (the keyless default), cosine 0.92 when a [local] bi-encoder is
    resident."""
    if embedder is None:
        return LexicalCacheBackend(Path(db_path))
    return SemanticCache(Path(db_path), embedder)
