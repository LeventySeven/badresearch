"""`retrieve_chunks` must release its SQLite handles too (issue #35 §7, MCP seam).

`run_funnel` and `retrieve_cmd` were fixed for #35; this tool body duplicates
`retrieve_cmd`'s shape and was missed. It is the site where the leak actually
compounds: an MCP server is a LONG-LIVED process, so every tool call stranded two
connections (the chunk-meta/FTS DB and the cache backend) for the life of the
server, rather than until a CLI process exited.

Assertions are on the connection OBJECTS, not on ResourceWarning — that warning
only exists on CPython >= 3.13 and would pass vacuously on 3.12.
"""

import sqlite3

import pytest

import bad_research.cli.research as RESEARCH  # noqa: N812
from bad_research.core.vault import Vault


def test_retrieve_chunks_closes_both_connections(monkeypatch, tmp_path):
    Vault.init(tmp_path)
    monkeypatch.chdir(tmp_path)

    engines: list[object] = []
    real_build = RESEARCH._build_engine

    def _spy_build(cfg, vault):
        eng = real_build(cfg, vault)
        engines.append(eng)
        return eng

    monkeypatch.setattr(RESEARCH, "_build_engine", _spy_build)

    from bad_research.mcp import server as SERVER  # noqa: N812

    fn = getattr(SERVER.retrieve_chunks, "fn", SERVER.retrieve_chunks)
    out = fn("keyless retrieval", mode="light", top_k=5)

    assert isinstance(out, str)  # JSON list; empty vault is fine, cleanup is the point
    assert len(engines) == 1, "retrieve_chunks should build exactly one engine"

    with pytest.raises(sqlite3.ProgrammingError):
        engines[0].conn.execute("SELECT 1")
    with pytest.raises(sqlite3.ProgrammingError):
        engines[0].cache.conn.execute("SELECT 1")
