"""Keyless RetrievalEngine (INTERFACES_KEYLESS §5).

Default path (embedder is None): FTS5/BM25 recall → min-max-normed BM25 as
initial_score → ClaudeCodeReranker over top-30 → three_tier_fuse → 0.70 gate →
<30%-pass wiki-link re-retrieve → token-set LexicalCacheBackend. Zero API key,
zero local model.

Optional dense lane ([local] extra, embedder set): also embeds chunks into
LanceDB; recall = RRF k=60 over (BM25 ranks, bi-encoder ranks); cache = cosine
0.92 reusing the resident bi-encoder. Auto-enabled above NEURAL_RECALL_VAULT_
THRESHOLD chunks by the CLI builder (this engine just honors whatever embedder
it is handed).
"""
from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal

from bad_research.embed.base import EmbedProvider
from bad_research.models.note import Note
from bad_research.retrieval.base import Chunk, Reranker
from bad_research.retrieval.cache import get_cache
from bad_research.retrieval.chunker import chunk_note
from bad_research.retrieval.chunker_code import embed_text_for
from bad_research.retrieval.constants import (
    EMBED_BATCH_CAP,
    EMBED_TRUNC_CHARS,
    RELEVANCE_GATE,
    RERETRIEVE_MAX_ROUNDS,
    RERETRIEVE_PASS_FRACTION,
    RRF_K,
    TOP_K_RETRIEVE,
)
from bad_research.retrieval.fts_chunks import (
    create_chunk_fts,
    index_chunk_fts,
    search_chunk_fts,
)
from bad_research.retrieval.fusion import (
    apply_source_type_weight,
    minmax_normalize,
    rrf_merge,
    three_tier_fuse,
)

# ── E6 — cascade-proxy relevance gate (ENHANCEMENT_PLAN E6, P2) ──────────────
# Pattern: Snowflake cascade rerank (DEEPLEARNINGAI.md A12, 20-500% speedup,
# <2% acc loss) + the grounding verifier's own byte→NLI→LLM cascade, applied to
# RELEVANCE. The cheap proxy is the `initial` score (min-max-normed BM25 in the
# keyless default; renormalized RRF k=60 in the [local] dense lane) — already
# computed, free, in [0,1]. We use it to skip the EXPENSIVE host-model reranker on
# the obvious cases:
#   • auto-KEEP  — a doc whose WORST achievable final (reranker_score=0.0) already
#                  clears the frozen 0.70 gate: the reranker can only raise it, so
#                  the call is wasted → keep it, score it at its no-rerank floor.
#   • auto-DROP  — a doc whose BEST achievable final (reranker_score=1.0) still
#                  cannot reach the gate: the reranker can never save it → drop it
#                  without a call.
#   • UNCERTAIN  — everything between → the only docs the reranker pays for.
# This is provably LOSSLESS w.r.t. the gate: the keep/drop bounds are computed with
# the SAME three_tier_fuse + source-type-weight algebra the gate uses, with the
# reranker score pinned to its extremes (and the live reranker score clamped to the
# same [0,1] range at the fusion site) — so no doc that could have passed is dropped,
# and no doc that would have failed is kept. The frozen constants (RELEVANCE_GATE=0.70,
# ALPHA=0.7, RRF_K=60, the three-tier weights) are UNTOUCHED; the cascade is a band
# built AROUND the gate, not a change to it. The decision is the gate-aware bound and
# ONLY the bound — there are no extra "proxy cut" thresholds, because any raw-proxy cut
# is either redundant with the bound (it can only fire inside a band the bound already
# decided) or unsafe (it could override the bound). The bound is the whole safety story.


class _ChunkMeta:
    __slots__ = ("chunk", "content_type")

    def __init__(self, chunk: Chunk, content_type: str | None):
        self.chunk = chunk
        self.content_type = content_type


class RetrievalEngine:
    def __init__(self, *, cache_db: Path, reranker: Reranker,
                 embedder: EmbedProvider | None = None,
                 lance_dir: Path | None = None,
                 links_db: Path | None = None,
                 gate: float = RELEVANCE_GATE,
                 top_k_retrieve: int = TOP_K_RETRIEVE):
        self.embedder = embedder
        self.reranker = reranker
        self.gate = gate
        self.top_k_retrieve = top_k_retrieve
        # Vector store: ONLY when a [local] embedder is supplied. Lazy import so
        # the keyless default never touches lancedb.
        self.store: Any | None = None
        if embedder is not None:
            from bad_research.retrieval.store import LanceChunkStore

            store_dir = Path(lance_dir) if lance_dir is not None \
                else Path(cache_db).with_name("lance")
            self.store = LanceChunkStore(store_dir, dim=embedder.dim)
        self.links_db = Path(links_db) if links_db is not None else None
        # Cache backend: lexical (no embedder) | cosine 0.92 (embedder resident).
        self.cache = get_cache(Path(cache_db), embedder=embedder)
        # Chunk metadata DB (FTS lane + chunk_id→meta map), per-vault — ALWAYS on.
        self.conn = sqlite3.connect(str(Path(cache_db).with_name("chunks_meta.db")))
        self.conn.row_factory = sqlite3.Row
        create_chunk_fts(self.conn)
        self._meta: dict[str, _ChunkMeta] = {}
        self.last_cache_hit: bool = False
        # E6 cascade instrumentation (last _one_round): how many candidates reached
        # the rerank decision vs. how many actually paid for the host-model reranker.
        self.last_rerank_candidate_count: int = 0
        self.last_reranked_count: int = 0

    # ── LIFECYCLE (issue #35 §7) ─────────────────────────────────────────
    def close(self) -> None:
        """Release the engine's SQLite handles. Idempotent.

        An engine owns TWO connections — the chunk-meta/FTS DB opened here and
        the query cache's own DB — and neither was ever closed, so every
        `run_funnel` leaked a pair (`ResourceWarning: unclosed database in
        <sqlite3.Connection ...>`, twice, on CPython >= 3.13). A CLI process
        exiting masked it. The MCP server does not: it rebuilds an engine per
        tool call inside one long-lived process, so the handles accumulate.

        Deliberately NO `__del__`: it would make GC order load-bearing and can
        run during interpreter teardown. An explicit `close()` (or the context
        manager below) is the contract, mirroring `Vault.close`.

        The cache close is `getattr`-guarded because `get_cache` is a factory —
        a future backend without a SQLite handle must not turn cleanup into an
        AttributeError.
        """
        self.conn.close()
        cache_close = getattr(self.cache, "close", None)
        if cache_close is not None:
            cache_close()

    def __enter__(self) -> RetrievalEngine:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    # ── INDEX ────────────────────────────────────────────────────────────
    def index(self, notes: Iterable[Note]) -> None:
        pending: list[Chunk] = []
        ct_for: list[str | None] = []
        embed_texts: list[str] = []
        for note in notes:
            ct = getattr(note.meta, "content_type", None)
            for chunk in chunk_note(note):
                pending.append(chunk)
                ct_for.append(ct)
                if self.embedder is not None:
                    et = embed_text_for(chunk, note) if ct == "code" else chunk.text
                    embed_texts.append(et[:EMBED_TRUNC_CHARS])
        if not pending:
            return
        fts_rows: list[dict[str, Any]] = []
        for chunk, ct in zip(pending, ct_for, strict=True):
            fts_rows.append({"chunk_id": chunk.chunk_id, "body": chunk.text,
                             "note_id": chunk.note_id})
            self._meta[chunk.chunk_id] = _ChunkMeta(chunk, ct)
        index_chunk_fts(self.conn, fts_rows)
        # Dense lane ([local] only): embed + upsert into LanceDB.
        if self.embedder is not None and self.store is not None:
            vectors: list[list[float]] = []
            for i in range(0, len(embed_texts), EMBED_BATCH_CAP):
                batch = embed_texts[i:i + EMBED_BATCH_CAP]
                vectors.extend(self.embedder.embed(batch, input_type="document"))
            rows: list[dict[str, Any]] = []
            for chunk, vec in zip(pending, vectors, strict=True):
                rows.append({"chunk_id": chunk.chunk_id, "vector": vec,
                             "note_id": chunk.note_id, "char_start": chunk.char_start,
                             "char_end": chunk.char_end, "model": self.embedder.name,
                             "dim": self.embedder.dim})
            self.store.upsert(rows)
            self.store.maybe_build_index()

    # ── SEARCH ───────────────────────────────────────────────────────────
    def search(self, query: str, *, mode: Literal["light", "full"], top_k: int) -> list[Chunk]:
        cached = self.cache.get(query)
        if cached is not None:
            self.last_cache_hit = True
            return [self._meta[cid].chunk for cid in cached["payload"]["chunk_ids"]
                    if cid in self._meta][:top_k]
        self.last_cache_hit = False

        survivors: list[Chunk] = []
        extra_ids: set[str] = set()
        for round_idx in range(1 + RERETRIEVE_MAX_ROUNDS):
            survivors, pass_fraction, top_note = self._one_round(query, extra_ids)
            if pass_fraction >= RERETRIEVE_PASS_FRACTION or round_idx == RERETRIEVE_MAX_ROUNDS:
                break
            extra_ids |= self._expand_symbols(top_note)

        survivors.sort(key=lambda c: c.score, reverse=True)
        result = survivors[:top_k]
        self.cache.put(query, {"chunk_ids": [c.chunk_id for c in result]})
        return result

    def _expand_symbols(self, top_note: str | None) -> set[str]:
        """Wiki-link neighbor widening (dossier 15 §7.3). Pull chunks of the top
        note's graph neighbors (outlinks it makes + backlinks to it) from the
        `links` table, unioned with same-note neighbor chunks. Pure SQL + set
        union — keyless, only runs on the rare <30%-pass path. With no links DB
        wired it degrades to the same-note fallback."""
        if top_note is None:
            return set()
        neighbor_notes: set[str] = {top_note}
        if self.links_db is not None and self.links_db.exists():
            conn = sqlite3.connect(str(self.links_db))
            try:
                # outlinks: notes top_note links TO (resolved target_id).
                for (tid,) in conn.execute(
                    "SELECT DISTINCT target_id FROM links "
                    "WHERE source_id = ? AND target_id IS NOT NULL", (top_note,)):
                    neighbor_notes.add(tid)
                # backlinks: notes that link TO top_note.
                for (sid,) in conn.execute(
                    "SELECT DISTINCT source_id FROM links WHERE target_id = ?", (top_note,)):
                    neighbor_notes.add(sid)
            finally:
                conn.close()
        return {cid for cid, m in self._meta.items()
                if m.chunk.note_id in neighbor_notes}

    def _one_round(self, query: str,
                   extra_ids: set[str]) -> tuple[list[Chunk], float, str | None]:
        bm_hits = search_chunk_fts(self.conn, query, limit=self.top_k_retrieve)
        bm_scores = dict(bm_hits)

        if self.embedder is None or self.store is None:
            # KEYLESS DEFAULT: initial = min-max-normed BM25, no fusion lane.
            for cid in extra_ids:
                bm_scores.setdefault(cid, 0.0)
            ids = [cid for cid in bm_scores if cid in self._meta]
            if not ids:
                return [], 0.0, None
            norm = dict(zip(ids, minmax_normalize([bm_scores[c] for c in ids]), strict=True))
            fused_initial = norm
        else:
            # DENSE LANE ([local]): RRF k=60 over BM25 ranks + bi-encoder ranks (§3.1).
            from bad_research.retrieval.store import LanceChunkStore

            qv = self.embedder.embed([query], input_type="query")[0]
            vec_hits = self.store.search_vector(qv, top_k=self.top_k_retrieve)
            vec_scores = {cid: LanceChunkStore.distance_to_score(d) for cid, d in vec_hits}
            for cid in extra_ids:
                vec_scores.setdefault(cid, 0.0)
                bm_scores.setdefault(cid, 0.0)
            bm_rank = [cid for cid, _ in sorted(bm_scores.items(), key=lambda kv: kv[1], reverse=True)]
            vec_rank = [cid for cid, _ in sorted(vec_scores.items(), key=lambda kv: kv[1], reverse=True)]
            fused_initial = dict(rrf_merge(bm_rank, vec_rank, k=RRF_K))
            fused_initial = {c: s for c, s in fused_initial.items() if c in self._meta}
            if not fused_initial:
                return [], 0.0, None
            # Renormalize RRF scores into [0,1] so three_tier_fuse's blend is calibrated.
            ids = list(fused_initial)
            fused_initial = dict(zip(ids, minmax_normalize([fused_initial[c] for c in ids]),
                                     strict=True))

        # pre-rerank rank (1-based) by initial score desc.
        ranked = sorted(fused_initial.items(), key=lambda kv: kv[1], reverse=True)
        cand_ids = [cid for cid, _ in ranked]
        self.last_rerank_candidate_count = len(cand_ids)

        # ── E6 cascade-proxy gate ───────────────────────────────────────────
        # Triage every candidate on the FREE proxy (its initial score) BEFORE the
        # expensive host-model reranker. The keep/drop decision uses the gate's own
        # three_tier_fuse + source-type-weight algebra with the reranker score pinned
        # to its extremes, so it is provably lossless w.r.t. the frozen 0.70 gate.
        auto_keep: list[int] = []     # idx into cand_ids — clearly relevant, kept @ floor
        uncertain: list[int] = []     # idx into cand_ids — must be reranked
        for rank0, cid in enumerate(cand_ids):
            rank = rank0 + 1
            initial = fused_initial[cid]
            ct = self._meta[cid].content_type
            # best/worst achievable final, computed with the SAME gate algebra and the
            # reranker score pinned to its (clamped) extremes — the gate-aware bound is
            # the entire safety guarantee, so the decision is the bound and only the bound.
            worst = apply_source_type_weight(three_tier_fuse(initial, 0.0, rank), ct)
            best = apply_source_type_weight(three_tier_fuse(initial, 1.0, rank), ct)
            if worst >= self.gate:        # KEEP free — reranker can only raise it
                auto_keep.append(rank0)
            elif best < self.gate:        # DROP free — reranker can never save it
                continue
            else:                         # genuinely uncertain → pay for the reranker
                uncertain.append(rank0)

        # ONE batched host-model call over ONLY the uncertain band (the obvious
        # keep/drop bands never reach the reranker — the cascade's whole point).
        # Reranker scores are CLAMPED to [0,1] here: the cascade's keep/drop bounds
        # are computed with the reranker pinned to its extremes (0.0 / 1.0), so the
        # bound is only a valid upper/lower bound — and the cascade only LOSSLESS —
        # if the fused score also lives in [0,1]. The host (already clamps) and BGE
        # (sigmoid) rerankers are in-range, so this is a no-op for them; it is the
        # IdentityReranker (`reranker="none"`, n-i ordering pseudo-scores > 1.0) that
        # needs it — three_tier_fuse's blend is calibrated for a [0,1] relevance
        # score, and an out-of-range value would both inflate finals past 1.0 and let
        # a doc the bound auto-dropped re-pass the gate (a losslessness break).
        rer: dict[int, float] = {}
        if uncertain:
            unc_docs = [self._meta[cand_ids[r0]].chunk.text for r0 in uncertain]
            local_scores = dict(self.reranker.rerank(query, unc_docs))  # local idx → score
            rer = {uncertain[li]: max(0.0, min(1.0, float(s)))
                   for li, s in local_scores.items()}
        self.last_reranked_count = len(uncertain)

        survivors: list[Chunk] = []
        # Auto-kept docs: score at their no-rerank FLOOR (reranker_score=0.0) — the
        # conservative final we already proved clears the gate; we never inflate.
        for rank0 in auto_keep:
            cid = cand_ids[rank0]
            initial = fused_initial[cid]
            fused = apply_source_type_weight(
                three_tier_fuse(initial, 0.0, rank0 + 1), self._meta[cid].content_type)
            c = self._meta[cid].chunk
            survivors.append(Chunk(chunk_id=c.chunk_id, note_id=c.note_id, text=c.text,
                                   char_start=c.char_start, char_end=c.char_end,
                                   score=fused, source_id=c.source_id))
        # Uncertain docs: blend in the host reranker score, then apply the gate.
        for rank0 in uncertain:
            cid = cand_ids[rank0]
            rank = rank0 + 1
            initial = fused_initial[cid]
            reranker_score = rer.get(rank0, 0.0)
            fused = three_tier_fuse(initial, reranker_score, rank)
            fused = apply_source_type_weight(fused, self._meta[cid].content_type)
            if fused >= self.gate:
                c = self._meta[cid].chunk
                survivors.append(Chunk(chunk_id=c.chunk_id, note_id=c.note_id, text=c.text,
                                       char_start=c.char_start, char_end=c.char_end,
                                       score=fused, source_id=c.source_id))
        pass_fraction = (len(survivors) / len(cand_ids)) if cand_ids else 0.0
        top_note = self._meta[cand_ids[0]].chunk.note_id if cand_ids else None
        return survivors, pass_fraction, top_note


