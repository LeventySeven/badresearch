"""RetrievalEngine lifecycle (issue #35 §7).

An engine opens TWO SQLite connections — the chunk-meta/FTS DB and the query
cache's own DB — and before this fix closed NEITHER, so every `funnel-gather`
leaked a pair (`ResourceWarning: unclosed database`, reported twice).

These tests assert the CONNECTIONS ARE CLOSED, not that no ResourceWarning was
emitted: that warning is CPython >= 3.13 behavior, so a warnings-based test
would pass vacuously on the 3.12 the repo's venv runs and prove nothing.
"""
import sqlite3

import pytest

from bad_research.retrieval.engine import RetrievalEngine
from bad_research.retrieval.rerank import IdentityReranker


def _engine(tmp_path):
    """The keyless default: embedder=None → FTS-only, LexicalCacheBackend."""
    return RetrievalEngine(cache_db=tmp_path / "cache.db", reranker=IdentityReranker())


def test_close_closes_the_chunk_meta_connection(tmp_path):
    eng = _engine(tmp_path)
    conn = eng.conn
    conn.execute("SELECT 1")  # open before
    eng.close()
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")


def test_close_also_closes_the_cache_backend(tmp_path):
    """The second of the reporter's two leaked handles — the one most easily
    forgotten, because it belongs to the cache the engine merely owns."""
    eng = _engine(tmp_path)
    cache_conn = eng.cache.conn
    cache_conn.execute("SELECT 1")
    eng.close()
    with pytest.raises(sqlite3.ProgrammingError):
        cache_conn.execute("SELECT 1")


def test_close_is_idempotent(tmp_path):
    """`finally` blocks and context managers can both fire; a second close must
    not raise, or cleanup becomes the thing that kills the run."""
    eng = _engine(tmp_path)
    eng.close()
    eng.close()


def test_engine_works_as_a_context_manager(tmp_path):
    """Mirrors the Vault.__enter__/__exit__ contract so the codebase keeps one
    lifecycle idiom."""
    with _engine(tmp_path) as eng:
        conn, cache_conn = eng.conn, eng.cache.conn
        conn.execute("SELECT 1")
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")
    with pytest.raises(sqlite3.ProgrammingError):
        cache_conn.execute("SELECT 1")


def test_semantic_cache_backend_closes_too(tmp_path, stub_embedder):
    """The [local] lane's cache backend (cosine 0.92) is a different class with
    its own connection — it needs the same close, or enabling neural_recall
    silently reintroduces the leak."""
    from bad_research.retrieval.cache import SemanticCache

    cache = SemanticCache(tmp_path / "sem.db", stub_embedder)
    conn = cache.conn
    conn.execute("SELECT 1")
    cache.close()
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")
