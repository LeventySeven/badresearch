# Bad Research V8 — Current State Capability Map

**Date:** 2026-05-29  
**Purpose:** Exact baseline for competitive gap analysis. Every claim is file:line cited.

---

## 1. Pipeline Map

### 1.1 Tier Routing Logic

The route is decided at step 1.5 by a deterministic CLI `bad route`, reading the step-1 decomposition.  
Source: `skills/bad-research-query-router.md:36-47` and `skills/routing_constants.py:7-25`.

**Decision tree:**
- **`agentic-fast`** — atomic_items ≤ 2, no contradiction terms, no time_periods, response_format == "short", single domain  
- **`light`** — response_format == "structured" OR atomic_items 3–6  
- **`full`** — multi-domain, contested, argumentative, time_periods present, ≥7 items  

The router also emits a `query_shape` field (`straightforward` / `breadth_first` / `depth_first`) that is **orthogonal** to the cost tier — it decides fan-out arrangement, not cost.  
Source: `skills/routing_constants.py:84-126` (SHAPE_FANOUT map).

An additional **modality + contestedness factor** (`BREADTH_MODALITIES`, `CONTESTEDNESS_*` constants) prevents broad-but-shallow curation queries from being up-routed to `full` on atomic-item count alone.  
Source: `skills/routing_constants.py:27-82`.

### 1.2 Per-Route Pipelines

| Route | Cost | Time | Pipeline |
|---|---|---|---|
| `agentic-fast` | ~$1–5 | <3 min | 0.5 → 1 → 1.5 → agentic-fast → 12(slim) → 15 → 16(+gate) |
| `light` | ~$5–15 | ~30–40 min | 0.5 → 1 → 1.5 → 1.6 → 2(funnel) → 10(single draft) → 12(slim) → 15 → 16(+gate) |
| `full` | ~$60–120 | ~1.5–2.5 h | 0.5 → 1 → 1.5 → 1.6 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 11.5 → 12 → 13 → 12.5 → 14 → 14.5 → 15 → 16(+gate) |

Source: `skills/bad-research.md:94-95`.

### 1.3 Stage-by-Stage Map

#### Step 0.5 — Clarify (all tiers, skipped on `--auto`/wrapped)
- **Produces:** `research/clarify.json` (action, ≤3 questions, distilled brief)
- **Subagent:** Haiku-class triage decision; no subagent spawn
- **Parallelism:** none
- Source: `skills/bad-research-0.5-clarify.md`

#### Step 1 — Decompose (all tiers)
- **Produces:** `research/prompt-decomposition.json` (sub_questions, entities, time_periods, required_section_headings, pipeline_tier, query_shape, citation_style); `research/temp/coverage-matrix.md`
- **Subagent:** orchestrator itself (no spawn)
- **Parallelism:** none
- **Key feature:** coverage-matrix self-audit catches scope-narrowing before any fetch runs; required_section_headings enforced structurally
- Source: `skills/bad-research-1-decompose.md:2-48`

#### Step 1.5 — Query Router (all tiers)
- **Produces:** `route` + `query_shape` written into `research/prompt-decomposition.json`
- **Subagent:** deterministic CLI `bad route --apply`; no LLM call
- Source: `skills/bad-research-query-router.md:35-43`

#### Step 1.6 — Plan Gate (interactive + expensive only; skipped otherwise)
- **Produces:** user-approved/edited sub-questions before the expensive fan-out
- **Subagent:** none (orchestrator pauses interactively)
- **Parallelism:** none; SKIP on non-interactive / `--auto` / wrapped / cheap
- Source: `skills/bad-research-1.6-plan-gate.md`; constant `PLAN_GATE_COST_THRESHOLD = 15.0` USD at `skills/routing_constants.py:140`

#### Step 2 — Width Sweep (all tiers)
- **Produces:** 15–80 vault notes (sources), `research/temp/search-plan.md`, `research/temp/coverage-gaps.md`, `research/temp/reflections.md`
- **Subagent:** `bad-research-fetcher` × 10–12 parallel (full), 3–5 parallel (light); `bad-research-source-analyst` for long sources (≤6 cap)
- **Parallelism:** 10–12 parallel fetchers; gap-fetch wave if needed
- **Key feature:** 4-lens search planning (breadth / depth / adversarial / period-pinned primary sources); deterministic 6-stage funnel (`bad funnel-gather`); distilled-reflection memory keeps context linear; source-quality negative-signal flags (aggregator/false_authority/marketing_spin/etc.)
- Source: `skills/bad-research-2-width-sweep.md:28-367`

#### Step 3 — Contradiction Graph (full only)
- **Produces:** `research/temp/contradiction-graph.json` (ranked fight clusters), `research/temp/consensus-claims.json`
- **Subagent:** orchestrator (reads claims-*.json files)
- **Parallelism:** none (sequential claim-pairing)
- Source: `skills/bad-research-3-contradiction-graph.md`

#### Step 4 — Loci Analysis (full only)
- **Produces:** `research/loci.json` (scored loci with source budgets + fanout key)
- **Subagent:** 2 parallel `bad-research-loci-analyst`; orchestrator deduplicates
- **Parallelism:** 2 analysts in parallel
- **Key feature:** composite scoring (importance + uncertainty + disagreement + decision_impact); dynamic source-budget allocation; fan-out shape (parallel/sequential/single) recorded; invariant — at least one dialectical locus required
- Source: `skills/bad-research-4-loci-analysis.md:33-108`

#### Step 5 — Depth Investigation (full only)
- **Produces:** one interim note per locus, each ending in `## Committed position`
- **Subagent:** `bad-research-depth-investigator` × K (breadth_first → parallel K≤6; depth_first → 2–4 sequential; straightforward → 1)
- **Parallelism:** depends on query_shape: breadth_first = K parallel; depth_first = 2–4 sequential (each reads prior committed position); straightforward = 1
- **Key feature:** committed-position invariant (investigators must take a side, not both-sides-summarize); Tier 0→3 browse ladder escalation for JS-heavy sources
- Source: `skills/bad-research-5-depth-investigation.md:30-118`

#### Step 6 — Cross-Locus Reconcile (full only)
- **Produces:** `research/comparisons.md`
- **Subagent:** orchestrator
- Source: `skills/bad-research-6-cross-locus-reconcile.md`

#### Step 7 — Source Tensions (full only)
- **Produces:** `research/temp/source-tensions.json`
- **Subagent:** orchestrator
- Source: `skills/bad-research-7-source-tensions.md`

#### Step 8 — Corpus Critic (full only)
- **Produces:** `research/corpus-critic-gaps.json`; targeted gap-fill fetch
- **Subagent:** orchestrator ("what source would overturn this?")
- Source: `skills/bad-research-8-corpus-critic.md`

#### Step 9 — Evidence Digest (full only)
- **Produces:** `research/temp/evidence-digest.md` (top claims + verbatim quotes)
- **Subagent:** orchestrator
- Source: `skills/bad-research-9-evidence-digest.md`

#### Step 10 — Triple Draft (all tiers — full = triple, light = single)
- **Produces:** `research/temp/draft-{a,b,c}.md` (full) or `research/notes/final_report_<vault_tag>.md` (light)
- **Subagent:** 3 parallel `bad-research-draft-orchestrator` (full); 1 for light
- **Parallelism:** 3 simultaneous angle-specific draft subagents (full)
- Source: `skills/bad-research-10-triple-draft.md`

#### Step 11 — Synthesize (full only)
- **Produces:** `research/notes/final_report_<vault_tag>.md`
- **Subagent:** fresh Opus `bad-research-synthesizer` (Read+Write locked); two-pass write
- **Parallelism:** none (single fresh-context subagent)
- **Key feature:** spawned fresh to avoid 200K+ orchestrator context fatigue; PATCH NEVER REGENERATE invariant activated from here
- Source: `skills/bad-research-11-synthesize.md:1-16`

#### Step 11.5 — Citation Verifier (full only)
- **Produces:** `research/temp/citation-verify-actions.json`
- **Subagent:** none (Read-locked orchestrator runs `bad verify-citations`)
- **Mechanism:** byte-identity (SHA) → NLI entailment (local `nli-deberta-v3-base`) → re-fetch arbitration (contradicted + critical only); high-effort lane uses N-sample self-consistency vote
- Source: `skills/bad-research-11.5-citation-verifier.md:31-70`

#### Step 12 — Adversarial Critics (full = 4 critics; light/agentic-fast = 1 slim critic)
- **Produces:** `research/critic-findings-{dialectic,depth,width,instruction}.json` (full); `research/critic-findings-light.json` (light/af)
- **Subagent:** 4 parallel: dialectic-critic, depth-critic, width-critic, instruction-critic (full); 1 slim critic (light/af)
- **Parallelism:** 4 simultaneous critics (full); instruction-critic never skipped
- Source: `skills/bad-research-12-critics.md:68-117`

#### Step 13 — Gap Fetch (full only)
- **Produces:** `research/temp/post-critic-fetch-log.md`; new vault notes for critic-identified gaps
- **Subagent:** fetchers (small wave)
- Source: `skills/bad-research-13-gap-fetch.md`

#### Step 12.5 — Grader Loop (full only; runs AFTER step 13)
- **Produces:** `research/grader-log.json`; `research/critic-findings-grader.json`
- **Mechanism:** `bad grade-report` → 5-axis judge → if FAIL, patcher → re-judge; ≤3 rounds (`MAX_GRADER_REVISIONS = 3`)
- **Subagent:** patcher subagent per round
- Source: `skills/bad-research-12.5-grader.md:61-108`; constant at `skills/routing_constants.py:147`

#### Step 14 — Patcher (full only)
- **Produces:** edited `final_report_<vault_tag>.md`
- **Subagent:** Read+Edit-locked patcher subagent
- **Key feature:** surgical Edit hunks only; no regeneration
- Source: `skills/bad-research-14-patcher.md`

#### Step 14.5 — Fresh Review (full only)
- **Produces:** `research/temp/fresh-review.json`
- **Subagent:** fresh Opus Read-locked reviewer (no pipeline context)
- **Key feature:** catches drift/structural issues in-context critics missed; single pass, not a loop
- Source: `skills/bad-research-fresh-review.md:18-20`

#### Step 15 — Polish (all tiers)
- **Produces:** edited `final_report_<vault_tag>.md`; `research/polish-log.json`
- **Subagent:** Read+Edit-locked polish-auditor
- Source: `skills/bad-research-15-polish.md`

#### Step 16 — Readability Audit + Ship Gates (all tiers)
- **Produces:** `research/readability-recommendations.json`, `research/readability-decisions.json`; final report with coalesced citations
- **Mechanism:** recommender subagent → orchestrator selective apply → `bad uncited-gate` (hard ship-block) → `bad recitation-gate` (major finding, not block) → citation coalescing
- **Subagent:** Read+Write-locked readability-recommender
- Source: `skills/bad-research-16-readability-audit.md`

#### Agentic-Fast Route
- **Produces:** `research/notes/final_report_<vault_tag>.md`; `research/temp/react-trace.md`
- **Mechanism:** bounded ReAct loop (planner + writer split); max 10 steps / 15 tool calls / 300s; `bad funnel-gather` per iteration; final report 500–2000 words with per-sentence `[N]` citations
- Source: `skills/bad-research-agentic-fast.md:37-78`

---

## 2. Existing Strengths

### 2.1 Multi-Layer Adversarial Verification (full tier)
- **4 parallel critics** at step 12: dialectic (counter-evidence), depth (shallow spots), width (ignored corpus), instruction (structural prompt adherence) — `skills/bad-research-12-critics.md:82-87`
- **In-pipeline grader loop** (step 12.5): judge → surgical patch → re-judge, ≤3 rounds — `skills/bad-research-12.5-grader.md`
- **Fresh-context final review** (step 14.5): a fresh Opus instance with no dispatch history catches whole-report drift — `skills/bad-research-fresh-review.md:18-20`
- **Citation verifier** (step 11.5): byte-identity + local NLI entailment, per-sentence dispositions, high-effort self-consistency vote — `skills/bad-research-11.5-citation-verifier.md`

### 2.2 Deterministic Ship Gates
- **`bad uncited-gate`**: hard ship-block for ALL routes; blocks any non-trivial factual claim without a verifiable citation — `skills/bad-research-16-readability-audit.md:147-166`
- **`bad recitation-gate`**: flags verbatim lifts > 12 words or > 50% of sentence — `skills/bad-research-16-readability-audit.md:168-199`
- Citation coalescing as a final $0 deterministic pass — `skills/bad-research-16-readability-audit.md:204-228`

### 2.3 Parallel Fetch Architecture
- 10–12 parallel fetcher subagents in a single wave (full), with a 7-field delegation contract including stop_conditions — `skills/bad-research-2-width-sweep.md:164-223`
- Each fetcher carries source-quality negative-signal flags (aggregator / false_authority / marketing_spin / cherry_picked / etc.) — `skills/bad-research-2-width-sweep.md:192-213`
- 6-stage deterministic funnel (`bad funnel-gather`): fan-out → dedup → rank → read Tier 0→3 → filter → chunk+store → rerank — `skills/bad-research-2-width-sweep.md:98-119`
- Distilled-reflection memory (`research/temp/reflections.md`) keeps mid-pipeline context linear (≤3 bullets + note_id per source, raw body stays on disk) — `skills/bad-research-2-width-sweep.md:307-364`

### 2.4 Deep Analysis Machinery (full tier)
- **Contradiction graph** (step 3): explicit fight clusters ranked by decision_relevance — `skills/bad-research-3-contradiction-graph.md`
- **Loci analysis** (step 4): 2 parallel analysts, composite scoring (importance + uncertainty + disagreement + decision_impact), dynamic source-budget allocation — `skills/bad-research-4-loci-analysis.md:63-98`
- **Committed-position invariant**: depth investigators MUST take a side — `skills/bad-research-5-depth-investigation.md:133`
- **Triple-draft ensemble** + fresh synthesizer subagent for final report — `skills/bad-research.md:344`
- **PATCH NEVER REGENERATE** invariant after step 11 — `skills/bad-research.md:335-337`

### 2.5 Routing Intelligence
- Query-shape classifier (depth_first / breadth_first / straightforward) orthogonal to cost tier — `skills/routing_constants.py:84-126`
- Modality + contestedness factor prevents survey queries from up-routing on breadth alone — `skills/routing_constants.py:27-82`
- 4-level reasoning-effort dial (`minimal/low/medium/high`) with per-tier model/fan-out mappings — `skills/routing_constants.py:158-168`
- Token-ceiling degrade order with terminal short-circuit to synthesis (RESERVE_FOR_SYNTHESIS = 40K tokens) — `skills/routing_constants.py:177-193`

### 2.6 Compaction-Resistance
- Multi-skill chain: each step procedure loads fresh via `Skill` tool, so compaction cannot evict a step's logic before it runs — `skills/bad-research.md:349-354`
- Disk-based artifact recovery: each step writes a canonical artifact; recovery from any point is deterministic — `skills/bad-research.md:268-298`
- TodoWrite list survives context compaction — `skills/bad-research.md:270`

### 2.7 Zero-Key Architecture
- No paid API required; host model (Claude Code) supplies all inference
- Keyless search: host WebSearch + DuckDuckGo (ddgs) + 7 scholarly APIs (arXiv, OpenAlex, Crossref, S2, Europe PMC, PubMed, Wikipedia) — `README.md:66`
- RRF k=60 fusion of ranked lists (constant: `retrieval/constants.py::RRF_K = 60`) — `docs/plans/2026-05-27-bad-research-KR-2-search.md:46`
- 87.81% test coverage baseline — `docs/plans/2026-05-27-bad-research-KR-1-removal.md:19`

### 2.8 Operator Surface
- Simple entry: `/bad-research <question>` or plain natural language in Claude Code — `README.md:47-57`
- `--reasoning-effort` / `--effort` flag for explicit budget control — `skills/bad-research.md:128-137`
- `--max-tokens <N>` ceiling with graceful degradation — `skills/bad-research.md:139-158`
- `--auto` flag for headless / wrapped pipeline runs — `skills/bad-research.md:93`
- `bad install` / `bad doctor` / `bad calibrate` CLI surface — `README.md:24-36`

---

## 3. Known Gaps / TODOs / Weaknesses

All items below are sourced from the improvement documents.

### 3.1 Grounding — Active Bugs and Missing Features

**A-2. Gate sentence-splitter false positives (grounding)**  
The `uncited-gate` produced 57/31/57 false-positive "blocks" in the live benchmark — bold pseudo-headings, citations placed after the period, numbered-list fragments, table-header rows all tripped the gate.  
Source: `docs/plans/2026-05-27-bad-research-IMPROVE.md:11-24`  
Fix path: `src/bad_research/grounding/gate.py` (skip non-sentence lines before classifying)

**A-3. Standalone CLI `uncited-gate` crashes with `OperationalError: no such table: claim_anchors`**  
Only works inside Claude Code; standalone invocation dies with a traceback.  
Source: `docs/plans/2026-05-27-bad-research-IMPROVE.md:26-36`  
Fix path: `cli/` + `core/db.py`/`core/vault.py`

**A-4. NLI entailment not auto-on (ship path)**  
`uncited-gate` currently only checks that a citation EXISTS, not that the cited source actually SUPPORTS the claim. `grounding/nli.py` (local nli-deberta-v3-base) exists but is not in the default ship path.  
Source: `docs/plans/2026-05-27-bad-research-IMPROVE.md:48-57`

**A-1. Generation-time grounding (highest leverage, deferred)**  
The pipeline writes an ungrounded draft then has the gate block-and-patch it iteratively (57 blocks in q1, causing the uncited-gate stall). The fix is to require an inline `[N]` before every factual sentence's terminal period from the first draft.  
Source: `docs/plans/2026-05-27-bad-research-IMPROVE.md:60-72` ("do LAST in the cluster")

**A-9. Recitation gate false positives on URL/reference lines**  
13 false positives in q2, all on `**URL:**` label lines (they inherently repeat source strings).  
Source: `docs/plans/2026-05-27-bad-research-IMPROVE.md:39-46`

### 3.2 Routing — Known Mis-routing

**B-5. Router up-routed a survey query to `full`**  
q1 ("best tech stack") was routed to `full` because it had 17 atomic items, then ran the full contradiction-graph/loci/depth machinery on a survey — ~2× the correct cost. Partially fixed via the modality factor, but the semantic-tiering note at `routing_constants.py:49-54` documents that **lexically-inferred breadth modality NO LONGER buys the raised survey ceiling** — only an explicit `modality` field set in the decomposition triggers the down-route.  
Source: `docs/plans/2026-05-27-bad-research-IMPROVE.md:77-86`; `skills/routing_constants.py:49-54`

### 3.3 Quality / Calibration Gaps

**E1 (P0): No golden-set eval corpus or per-step regression gate**  
The existing eval is 8 test cases (`golden-eval-report.json`), all offline stubs with `pass_rate: 1.0` against a deterministic rubric. There is no stored real-query corpus and no per-component score tracking across changes.  
Source: `docs/enhancements/ENHANCEMENT_PLAN.md:27-28`

**E2 (P1): Grader uses numeric float scores (0–1) — the Arize hallucination pattern**  
The in-pipeline grader (`quality/grader.py`) uses continuous 0.0–1.0 numeric scores. Arize's verbatim finding: numeric scores hallucinate; switch to categorical rails / single-constraint judges. The CitationVerifier already does this right.  
Source: `docs/enhancements/ENHANCEMENT_PLAN.md:29-30`

**E9 (P1): Paraphrase-band span support-check missing**  
Byte-identity citation check (good default) passes when claim text is a substring of `quoted_support`. The gap is the paraphrase band — when the claim text is NOT a substring, the keyless `CitationPresentNLI` is a no-op; only `[local]` (torch + NLI model) fills this.  
Source: `docs/enhancements/ENHANCEMENT_PLAN.md:79-81`

**E7 (P2): No prompt-cache discipline (`cache_control` breakpoints)**  
The multi-skill chain's fresh-load-per-skill design partly conflicts with append-only prompt caching. No `cache_control` breakpoints implemented; estimated 5–10× cost win available on the headless/MCP path.  
Source: `docs/enhancements/ENHANCEMENT_PLAN.md:33-34`

### 3.4 Retrieval Gaps

**E13 (P2): URL→content cache is only a query→results semantic cache**  
`retrieval/cache.py` is a query→results cache (0.92 cosine similarity). The fetch-engine-level URL→content cache (`retrieval/url_cache.py`) does NOT exist yet — every fetch of the same URL re-hits the network.  
Source: `docs/enhancements/ENHANCEMENT_PLAN.md:75-77`

**E14 (P2): `[local]` reranker defaults to `ms-marco-MiniLM-L-6-v2` not `zerank-2`**  
zerank-2 is +8.7pp NDCG@10 over the current default. Swap is one-line but gated behind `[local]`.  
Source: `docs/enhancements/ENHANCEMENT_PLAN.md:83-84`

**ClaudeCodeReranker stub not filled (KR-5 pending)**  
The default `ClaudeCodeReranker` in `retrieval/rerank.py` raises `NotImplementedError("KR-5")`. All non-`[local]` reranking falls back to identity until KR-5 ships.  
Source: `docs/plans/2026-05-27-bad-research-KR-1-removal.md:103-107`

### 3.5 Infrastructure / Cost Gaps

**q2 stall (documented, partially fixed)**  
bad-research q2 stalled mid uncited-gate fix loop (watchdog triggered), relaunched with an anti-stall brief. Root cause was the ungrounded-draft → gate-blocks-57 → iterative-patch cycle. A-1/A-2 grounding fixes address this.  
Source: `docs/enhancements/DR_RUN_NOTES.md:39-40`

**~2× cost on survey queries (partially mitigated)**  
q1 ran the full 16-step pipeline on a survey query. The modality factor now down-routes on explicit `modality` field but NOT on lexically-inferred cues.  
Source: `docs/enhancements/DR_RUN_NOTES.md:67-69`; `skills/routing_constants.py:49-54`

**E6 (P3): No cascade-proxy relevance gate (20–500% speedup available)**  
Cheap lexical/BM25 proxy could auto-keep clearly-relevant and auto-drop clearly-irrelevant candidates, only hitting the host-model reranker for the uncertain band.  
Source: `docs/enhancements/ENHANCEMENT_PLAN.md:32-33`

### 3.6 Competitive Gaps vs Keyed Systems (structural, not closeable keyless)

- **Index freshness/breadth**: Exa 1-min crawl, Tavily/Perplexity proprietary corpus — bad-research relies on host WebSearch + ddgs (scraper-fragile). SimpleQA recall ceiling: Tavily 93.3 > Perplexity 85.9 > Exa 71.2 > bad-research (keyless ceiling sits below). Source: `docs/enhancements/ENHANCEMENT_PLAN.md:55-58`
- **Anti-bot extraction**: Firecrawl fire-engine TLS-spoof — bad-research Tier-3 agentic browse is the best available keyless substitute
- **Warm-cache latency**: keyed systems have pre-warmed corpora

---

## 4. Operator Surface Today

### 4.1 Entry Points

**Simple path** (recommended):
```
/bad-research <question>
```
Or just ask a research-shaped question in Claude Code — the skill auto-loads via the `description` field.

**CLI flags:**
- `--reasoning-effort minimal|low|medium|high` (alias `--effort`) — nudges route and fan-out
- `--max-tokens <N>` — optional hard ceiling; triggers graceful degradation
- `--auto` — skip 0.5-clarify and 1.6-plan-gate; for headless runs

**Install flow:**
```bash
pipx install bad-research   # or: uv tool install bad-research
bad install                 # writes entry skill to ~/.claude/skills/bad-research/
bad doctor                  # verifies everything is wired
```

Per-project vault initialized lazily on first run: `bad init .` (auto-runs if vault missing).  
Source: `README.md:24-36`; `skills/bad-research.md:166-171`

### 4.2 Simplicity Assessment

The surface is genuinely simple: one slash command, one optional effort flag, zero API keys. The complexity lives entirely in the 22-step pipeline (hidden from the user). On interactive runs, the only user-visible interactions are:
1. Step 0.5: ≤3 clarifying questions (default-proceed; most runs skip questions entirely)
2. Step 1.6: plan-gate on expensive interactive runs (one approve/edit/proceed choice)
3. Final report delivery

The "deep core, simple surface" design goal is substantially met today.

---

## 5. Eval Baseline

The golden-eval-report.json records 8 test cases, all passing:
- `pass_rate: 1.0` (all 8 cases)
- Components: `decompose: 1.0`, `retrieval: 1.0`, `synthesis: 1.0`
- All 5 rail categories pass: factual, citation, completeness, source_quality, efficiency
- **Caveat:** all 8 use the deterministic `StubJudge` offline rubric, not live LLM judgement. The live `LLMJudge` path was verified working at `overall = 0.850` on `bad calibrate --offline` — `docs/plans/2026-05-27-bad-research-KR-7-calibration-plan.md:31-34`

Prior live A/B benchmark vs hyperresearch (3 queries × 2 tools):
- Overall quality score: bad-research 55.9 vs single-draft fallback 52.6 (`skills/bad-research.md:354`)
- bad-research won on: fresher specifics, harder dated facts, adversarial coverage, sentence-level citations
- hyperresearch won on: readability (paragraph-level cites), lower cost on surveys, no stall risk
- Source: `docs/enhancements/DR_RUN_NOTES.md:39-80`

---

## 6. In-Flight Improvements (Priority Order)

| Pri | Item | Status | Files |
|---|---|---|---|
| P0 | A-2 Gate sentence-splitter false-positives | planned | `grounding/gate.py` |
| P0 | A-3 Standalone `uncited-gate` robustness | planned | `cli/`, `core/db.py` |
| P0 | E1 Golden-set eval corpus + regression gate | planned | `calibrate/golden/` |
| P1 | A-4 NLI entailment auto-on in ship path | planned | `grounding/verifier.py` |
| P1 | A-1 Generation-time grounding (do LAST in cluster) | planned | step-10/11 prompts |
| P1 | E8 Source-quality negative-signal list (fetcher prompts) | SHIPPED — `skills/-2/-5` |
| P1 | E12 Query-shape classifier | SHIPPED — `routing_constants.py:84-126` |
| P1 | E9 Keyless paraphrase-band span support-check | planned | `grounding/verifier.py` |
| P1 | E2 Categorical-rails grader judge | planned | `calibrate/judge.py`, `quality/grader.py` |
| P2 | E11 Plan-gate (collaborative_planning) | SHIPPED — `skills/bad-research-1.6-plan-gate.md` |
| P2 | E3 Light-route adversarial critic | SHIPPED — `skills/bad-research-12-critics.md` slim variant |
| P2 | E4 Self-consistency vote on high-stakes claims | SHIPPED — `skills/bad-research-11.5-citation-verifier.md` (effort=high lane) |
| P2 | E13 URL→content cache | planned | `retrieval/url_cache.py` |
| P2 | E14 zerank-2 `[local]` reranker | planned | `retrieval/rerank.py` |
| P3 | KR-5 ClaudeCodeReranker body | planned | `retrieval/rerank.py` |
| P3 | E10 Short-circuit-to-synthesis terminal action | SHIPPED — `routing_constants.py:192-193` |
| P3 | E6 Cascade-proxy relevance gate | planned | `quality/relevance.py` |
| P3 | E7 Prompt-cache discipline | planned | orchestrator, `llm/anthropic.py` |

KR-2 (keyless search layer) and KR-1 (provider removal) are complete/in-progress per `docs/plans/` directory.
