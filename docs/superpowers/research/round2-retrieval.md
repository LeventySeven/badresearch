# Round 2 — Retrieval & Reranking Design Fragment (R2-2)

**Date:** 2026-05-29
**Scope:** G7 (ClaudeCodeReranker stub) + G8 (URL→content cache) + hybrid fusion feasibility + URL utility scoring + redundancy audit
**Evidence read:** round1-borrowable.md (P5, P10), round1-competitors-A.md (Perplexity 3-level + failsafe), round1-hyperresearch.md (6-axis scorer, redundancy audit), SYNTHESIS.md, and the actual source files listed below.

---

## 0. The surprising finding: G7 and G8 are already solved

Before designing anything, the first obligation is to check the actual code.

**G7 — `ClaudeCodeReranker` stub (NotImplementedError / identity fallback):**
Reading `src/bad_research/retrieval/rerank.py` reveals that `ClaudeCodeReranker` is **fully implemented** — it is NOT a stub. It imports the frozen `LLM_RERANK_PROMPT_SYSTEM` and `_parse_scores` from `web/search/rerank.py` (the single shared source of truth), constructs the user message via `_build_user_message`, calls the host LLM with `temperature=0`, clamps scores to `[0,1]`, sorts descending, and degrades silently to `[0.0]*n` (BM25/initial order preserved) on exception. The `get_reranker` factory wires it as the default (`reranker="host"`). There is no `NotImplementedError` anywhere in the reranker module. The SYNTHESIS.md reference `KR-1-removal.md:103-107` likely reflects an earlier dossier state that was subsequently implemented.

**G8 — URL→content cache absent:**
Reading `src/bad_research/web/content/fetch_clean.py:26-27, 485-571` reveals a **14-day SQLite content cache already in production**. `cache_get(url)` / `cache_put(url, payload)` use `sha256(normalize_url(url))` as the key. `normalize_url` performs Firecrawl-style canonicalization (https-force, www-strip, port-drop, fragment-drop, index-file normalization) so http/https/www/fragment variants of the same URL share one cache entry. TTL is enforced at get time (`CACHE_TTL = 14 * 86400`). The cache lives at `platformdirs.user_cache_dir("bad-research") / "content_cache.sqlite"` — separate from the vault's SQLite, which is correct. There is nothing to build here.

**Conclusion for G7 and G8:** Both gaps are closed. The SYNTHESIS.md gap list is stale for these two items. No new implementation is needed. Verification action: add a unit test asserting `ClaudeCodeReranker.rerank(...)` returns `list[tuple[int, float]]` with non-zero scores on a toy LLM mock — this will confirm the path is exercised in the test suite (which the `coverage.omit` list does NOT exclude `retrieval/rerank.py`, so it should already be covered).

---

## 1. Reranker: what it actually IS (keyless)

`ClaudeCodeReranker` in `retrieval/rerank.py` and `HostModelReranker` in `web/search/rerank.py` are both LLM-based rerankers using the host model as a zero-cost frontier cross-encoder. Both share one frozen prompt:

- **Prefilter method (E6 cascade-proxy gate):** `engine.py:243-283` implements a gate-aware cascade that divides candidates into `auto_keep` / `uncertain` / `auto_drop` bands using `three_tier_fuse` pinned at (0.0, 1.0) extremes. Only the `uncertain` band pays for an LLM call. This is provably lossless w.r.t. the 0.70 gate.
- **LLM rerank prompt:** `LLM_RERANK_PROMPT_SYSTEM` in `web/search/rerank.py:30-39`. Pointwise scoring per passage, JSON array output `[{"i": int, "s": float}]`, temperature=0, injection preamble baked in.
- **I/O contract:** `rerank(query: str, docs: list[str]) -> list[tuple[int, float]]` (the `Reranker` Protocol from `retrieval/base.py`).
- **Plug-in point:** `RetrievalEngine.__init__` takes a `Reranker`; `get_reranker(config)` is the factory. In `funnel/orchestrator.py:104-106`, `deps.retrieval` is the injected engine. The reranker runs inside `_one_round` at `engine.py:280`.
- **Deps reused:** `rank-bm25>=0.2` (already core), `anthropic>=0.40` (already core), no new deps needed.

**The only gap here is documentation, not implementation.** The SYNTHESIS.md gap list should be updated to mark G7 as closed.

---

## 2. Hybrid fusion: is it worth adding BM25+dense RRF?

**Current state:**
- Keyless default (no `[local]` extra): FTS5/BM25 recall only → min-max normed `initial_score` → `ClaudeCodeReranker` over `uncertain` band.
- With `[local]` extra: BM25 ranks + bi-encoder (BGE-small) ranks → `rrf_merge(bm25_rank, vec_rank, k=60)` → renormalized RRF as `fused_initial` → cascade → reranker.

**Assessment — is adding dense to the keyless default worth it?**

Verdict: **NO — overkill for the keyless path, not overkill for [local].**

Reasoning:
1. BM25+dense RRF is already fully implemented for the `[local]` path (`engine.py:218-236`, `fusion.py:63-70`). There is nothing to add there.
2. The keyless default uses BM25 as the recall lane, then the LLM host model as the reranker. The host model IS a frontier cross-encoder — it scores (query, passage) directly with deep semantic understanding. Adding a bi-encoder on the keyless path would cost a download of BGE-small (~135 MB), a torch dependency, and inference time, in exchange for marginally better `fused_initial` ordering going INTO the cascade. But the cascade's `uncertain` band is exactly the set of documents the BM25 score alone cannot decide — and the LLM reranker resolves those correctly. The incremental gain from a bi-encoder prefilter on a 30-candidate pool that an LLM then scores is marginal.
3. The convergent industry pattern (Exa, Tavily, Perplexity P3) uses cross-encoders because their recall stage is too large and too distributed to hand to an LLM. Our recall pool is 30 candidates from a local vault — the LLM call is affordable and dominates quality.

**Simplest thing that beats identity-fallback meaningfully:** the system already has it. The `ClaudeCodeReranker` + E6 cascade is the correct keyless architecture. No new fusion code needed for the base path.

**What WOULD be overkill:** adding sentence-transformers/lancedb just for the keyless default. Users who install `[local]` already get dense+BM25+RRF.

---

## 3. URL utility scoring + redundancy audit: parity confirmed

**6-axis URL utility scorer:**
`funnel/rank.py:48-87` implements all six dimensions verbatim — Authority (domain tier), Novelty (provider spread), Stance diversity (adversarial title signals), Coverage (query-term overlap), Redundancy (aggregator detection), Freshness (age_days from metadata). Each is 0-3, composite max 18. `rank_candidates` uses `rrf_fuse(provider_ranks) + util/18 * (1/rrf_k)` as the composite sort key. This matches `hyperresearch-2-width-sweep.md:113-130` exactly.

**Evidence redundancy audit:**
`funnel/filter.py:42-53` implements Jaccard shingle-based redundancy clustering at `>60%` overlap — derivative sources are excluded before storage. The `bad-research-2-width-sweep.md:289-305` (Step 2.6) also describes a post-fetch claim-level derivative audit using `quoted_support` overlap and `suggested-by` citation ancestry. The `filter.py` covers the content-level case; the claim-level Step 2.6 operates at the skill layer on `claims-*.json`. Both paths are present.

**Wikipedia-as-source-hub rule:**
`bad-research-2-width-sweep.md:136` is explicit: "Include Wikipedia URLs in the queue… treat them as SOURCE HUBS… Wikipedia itself is NEVER cited in the final report." This is a skill-layer instruction, not a Python rule — correct location.

**Gap if any:** The `funnel/rank.py` utility scorer operates only on SERP signals (no fetch yet). The `bad-research-2-width-sweep.md:2.3` says "SKIP for light, run for full" — but the funnel's `rank_candidates` runs for all modes (it is pure and free). The tier-gating in the skill is about the explicit write to `research/temp/scored-urls.md`; the underlying scoring function always runs. No gap.

---

## 4. Content cache (G8): already built

As found above, G8 is closed. The content cache lives at:
- **Module:** `src/bad_research/web/content/fetch_clean.py:536-571`
- **Schema:** `CREATE TABLE IF NOT EXISTS content_cache (url_hash TEXT PRIMARY KEY, payload TEXT, ts INTEGER)`
- **Key:** `sha256(normalize_url(url))` — Firecrawl-style URL canonicalization
- **TTL:** 14 days (`CACHE_TTL = 14 * 86400`)
- **Location:** `platformdirs.user_cache_dir("bad-research") / "content_cache.sqlite"` — correctly separated from the vault's research SQLite

The only design note: if we ever want to co-locate this in the vault's SQLite (for single-file portability per research run), that is a migration, not a gap fix. The current separation is architecturally cleaner — content cache is global across runs; vault is per-run.

---

## 5. Minimal diff surface: what changes, what stays

**Nothing in Python source needs to change to close G7 or G8.** Both are implemented.

**What DOES need to change (documentation only):**

| File | Change |
|---|---|
| `docs/superpowers/research/SYNTHESIS.md` | Mark G7 and G8 as CLOSED with commit references |
| Any dossier referencing `KR-1-removal.md:103-107` | Verify that section no longer reflects a stub — update or note it is historical |

**What to verify (test coverage, not implementation):**

| Module | Action |
|---|---|
| `retrieval/rerank.py` | Confirm `ClaudeCodeReranker.rerank` is exercised in tests — it is NOT in `coverage.omit`, so it should be covered. If not, add a unit test with a mock `LLMProvider`. |
| `web/content/fetch_clean.py:546-571` | Confirm `cache_get` / `cache_put` are covered — likely yes since `fetch_clean` is a core fetch path. |
| `funnel/rank.py` | `utility_score` + `rank_candidates` should be covered by funnel integration tests. |

**What stays exactly as-is:** `retrieval/rerank.py`, `web/search/rerank.py`, `retrieval/engine.py`, `retrieval/fusion.py`, `funnel/rank.py`, `funnel/filter.py`, `web/content/fetch_clean.py`. Zero source changes.

---

## 6. Failsafe re-retrieve: already wired

Perplexity's documented pattern (P8 from round1-competitors-A.md: "if <30% pass quality threshold, discard and re-retrieve") is implemented at two levels:

1. **Chunk-level (vault retrieval):** `engine.py:166-171` — `RERETRIEVE_PASS_FRACTION = 0.30`; if `pass_fraction < 0.30`, expand symbols via `_expand_symbols` and retry, up to `RERETRIEVE_MAX_ROUNDS = 2`.
2. **URL-level (search loop):** `web/search/loop.py:31-46` — `retrieve_until_good` reformulates queries and re-fans when `<cfg.min_pass_fraction` of scored results clear `cfg.relevance_threshold`. Tested and injected via `expand`/`fan_out`/`rerank` callables.

---

## 7. Summary

All five design targets in this fragment resolve the same way: the work is done.

| Target | Status | Key evidence |
|---|---|---|
| ClaudeCodeReranker stub (G7) | CLOSED — full LLM reranker | `retrieval/rerank.py:109-166`, `web/search/rerank.py:141-164` |
| URL→content cache (G8) | CLOSED — 14-day SQLite cache | `web/content/fetch_clean.py:26-27, 536-571` |
| Hybrid BM25+dense RRF | HAVE ([local] path) / NOT NEEDED (keyless path) | `retrieval/engine.py:218-236`, `retrieval/fusion.py:63-70` |
| 6-axis URL utility scorer | HAVE | `funnel/rank.py:48-103` |
| Evidence redundancy audit | HAVE (content-level + claim-level) | `funnel/filter.py:42-53`, `bad-research-2-width-sweep.md §2.6` |
| Failsafe re-retrieve | HAVE (chunk + URL level) | `retrieval/engine.py:166-171`, `web/search/loop.py:31-46` |

The SYNTHESIS.md gap list is stale for G7 and G8. Both items were implemented in subsequent dossier/KR passes after the gap list was written.

---

## Key design decision

**What the reranker actually is (keyless):** a single batched LLM call to the host model with a frozen pointwise relevance prompt, wrapped in a gate-aware E6 cascade that skips obviously good/bad candidates. This is architecturally equivalent to Firecrawl's two-pass LLM URL reranker (P10) and Perplexity's L1→L2→L3 progressive reranker — the LLM IS the cross-encoder, zero cost, zero key. The quality ceiling is the host model's semantic reasoning, which is frontier-class. No external cross-encoder API is needed or desirable.

**Hybrid fusion verdict:** NOT OVERKILL for `[local]` (already built), GENUINELY OVERKILL for the keyless default (BM25 recall + LLM rerank is the right two-layer architecture for a 30-candidate vault retrieval pool; adding a bi-encoder prefilter buys noise, not signal).

---

*Written: 2026-05-29. Source files read: `retrieval/rerank.py`, `retrieval/engine.py`, `retrieval/fusion.py`, `retrieval/base.py`, `retrieval/constants.py`, `retrieval/cache.py`, `web/search/rerank.py`, `web/search/rank.py`, `web/search/loop.py`, `web/content/fetch_clean.py`, `funnel/rank.py`, `funnel/filter.py`, `funnel/orchestrator.py`, `pyproject.toml`, `bad-research-2-width-sweep.md`, `bad-research-13-gap-fetch.md`.*
