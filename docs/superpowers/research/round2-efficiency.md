# Round 2 — Efficiency & Orchestration Design Fragment (R2-3)

**Scope:** Token-efficiency + orchestration upgrades — reflections-only context, model-tiering
audit, batch pipelining, and programmatic tool orchestration.
**Constraint:** keyless, Claude-Code-native (subagents via Skill/Task, SQLite vault).
**Date:** 2026-05-29

---

## 1. Reflections-Only Context Propagation

### What Tavily measured vs what we already have

Tavily's "reflections-only" pattern cuts tokens ~66% by keeping only ≤3 distilled claim bullets
per round between iterations rather than re-injecting raw source text.

**We already implemented this correctly.** Evidence:

- `src/bad_research/retrieval/reflections.py::ReflectionLog` — an append-only artifact at
  `research/temp/reflections.md` that stores exactly ≤3 distilled claim bullets + `cited_note_ids`
  per round (`REFLECTION_BULLET_CAP = 3`). The cap is enforced at construction
  (`reflections.py:71-72`).
- `src/bad_research/retrieval/reflections.py:39-40` — the synthesis ceiling is 10 000 tokens
  (`SYNTHESIS_CONTEXT_TOKEN_CEILING = 10_000`), matching the Chroma context-rot ceiling from
  `YC_ROOT_ACCESS.md:L14075`.
- Step 2.7 in `skills/bad-research-2-width-sweep.md:306-364` mandates: "DROP the raw note body
  from working context. Once a source is distilled to its reflection bullets…" The `open_gaps`
  aggregator (`reflections.py:154-159`) is what the next-round planner reads — never the raw corpus.
- Step 11.4b in `skills/bad-research-11-synthesize.md:133-159` implements Tavily's "re-inject
  raw only at the end": the synthesizer re-injects raw verbatim spans ONLY for the `cited_note_ids`
  a section will actually cite, not the whole corpus.

### Where we still pass raw text (residual cost)

There is one identified place where raw source bodies can still bleed into the orchestrator
context: **depth investigators (step 5)**.

The spawn template in `skills/bad-research-5-depth-investigation.md:84-86` explicitly instructs
investigators: "Read the full source text of relevant vault notes… BEFORE writing your interim
note." That is correct for the investigator's own fresh context (it needs the raw text to
synthesize from primary evidence). The issue is step 5 procedure step 4: after all K investigators
return, the orchestrator reads their interim notes back:
```
$HPR note show <id1> <id2> ... -j
```
These interim notes are already synthesized (committed-position format), NOT raw source bodies —
so this is actually fine. The orchestrator holds the committed-position sections (step 5 procedure
step 4 in the skill), not the raw bodies.

**The one genuine gap:** the orchestrator at step 11.1 is instructed to "read each draft in full"
from `research/temp/draft-{a,b,c}.md`. Three drafts at 5 000–8 000 words each = 15 000–24 000
tokens of raw draft text in orchestrator context before spawning the synthesizer. The orchestrator
already off-loads the writing to a fresh synthesizer subagent (`skills/bad-research-11-synthesize.md:13-16`)
for exactly this reason — but the orchestrator still reads all three drafts at step 11.1 to do the
conflict-spot-check (step 11.2) and write the synthesis plan (step 11.3). This is necessary but it
means the orchestrator pays full draft-body cost once at step 11.

**Verdict on reflections-only:** HAVE it, implemented correctly end-to-end. The ~66% token
reduction vs quadratic re-reading is already captured by the reflections architecture.
The vault ("disk is memory, context is scratchpad") is the mechanism; the reflections log is the
carry-forward; raw re-injection happens once at synthesis for cited notes only.

### Remaining saving: compress synthesis-evidence.md handoff

The one incremental win available: step 11.4b currently calls `bad retrieve` per section topic
and writes `research/temp/synthesis-evidence.md` containing verbatim quoted_support spans for all
sections before spawning the synthesizer. That file can be large (up to 10 000 tokens of spans
across 6-8 sections). Since the synthesizer is tool-locked to `[Read, Write]`, it reads this
file directly — there is no redundant injection into the orchestrator context. **No action needed.**

**Token-saving estimate from reflections-only (net new):** ~0% — already implemented.
The 66% figure applies to the width-sweep loop (step 2) and depth-investigation loop (step 5),
and both correctly use the reflections artifact.

**Tag: HAVE**

---

## 2. Token-Budget-as-Quality-Lever + Asymmetric Model Tiering Audit

### Our three-tier map

From `src/bad_research/config.py:33-38`:
```
triage → claude-haiku-4-5
work   → claude-sonnet-4-6
heavy  → claude-opus-4-7
```

The `--cheap` flag demotes `heavy→work` globally (`config.py:61-63`).
EFFORT_MAP in `routing_constants.py:159-168` maps effort levels to tiers:
- `minimal` → triage, `low` → work, `medium` → default, `high` → heavy.

### Stage-by-stage tiering audit

| Stage | Step | Current tier (production) | Recommended tier | Notes |
|---|---|---|---|---|
| Clarifier (0.5) | triage-tier (`bad-research.md:219`) | triage (Haiku) | triage | Correct — simple ≤3 yes/no Qs |
| Decompose (1) | no explicit assignment → orchestrator (Opus) | heavy | **work** | SIMPLE-WIN — structured JSON extraction, no contested reasoning; Sonnet handles it perfectly. Only needs the model's tool-use + JSON output, not frontier reasoning. |
| Query router (1.5) | Python deterministic (`router.py`) | $0 | $0 | Correct |
| Plan-gate (1.6) | orchestrator (Opus) | heavy | heavy | Correct — needs user-facing judgment |
| Width-sweep planning (2.1) | orchestrator (Opus) | heavy | **work** | SIMPLE-WIN — search-plan generation is structured heuristic work, not frontier analysis. Sonnet generates the search table correctly. |
| Fetchers (2.4) | subagents, unspecified (defaults to work/Sonnet) | work | work | Correct |
| Source analysts (2, long-source) | Sonnet 1M context (`bad-research-2-width-sweep.md:381`) | work | work | Correct |
| Contradiction graph (3) | orchestrator (Opus) | heavy | **work** | MEDIUM — contradiction clustering is pair-analysis over structured claims JSON; Sonnet handles it. Only escalate to heavy if the query has ≥3 contested political/scientific loci. |
| Loci analysis (4) | 2 parallel subagents, unspecified | work | work | Correct |
| Depth investigators (5) | subagents, unspecified | work | work | Correct — investigators need reasoning to commit to a position |
| Cross-locus reconcile (6) | orchestrator (Opus) | heavy | heavy | Correct — requires synthesis of conflicting committed positions; heavy earns its cost here |
| Source tensions (7) | orchestrator (Opus) | heavy | **work** | SIMPLE-WIN — structured extraction of expert disagreements from vault notes; deterministic format, not frontier reasoning |
| Corpus critic (8) | orchestrator (Opus) | heavy | heavy | Correct — "what source would overturn this?" requires adversarial reasoning |
| Evidence digest (9) | orchestrator (Opus) | heavy | **work** | SIMPLE-WIN — top-claim extraction + verbatim quote pulling; structured task |
| Triple-draft sub-orchestrators (10) | 3 subagents, unspecified | work | work | Correct — drafting is the work tier's job |
| Synthesizer (11) | spawn template says "fresh Opus session" (`bad-research-11-synthesize.md:13`) | heavy | heavy | Correct — synthesis is THE 80%-variance stage; never cut |
| Citation verifier (11.5) | `grounding/verifier.py:181`: tier="triage" | triage | triage | Correct — deterministic byte-match, Haiku sufficient |
| Critics fan-out (12, full) | 4 subagents, unspecified | work | work | Correct — critic analysis is work-tier |
| Light slim critic (12) | spawn as subagent | work | work | Correct |
| Grader / LLM-judge (12.5) | `calibrate/constants.py:23`: JUDGE_TIER="heavy" (with comment "Sonnet acceptable") | heavy | **work** | MEDIUM — the comment "Sonnet acceptable" is in the code. The judge emits categorical rails (pass/borderline/fail) not numeric scores (E2). Sonnet is sufficient for categorical rail output. Save 5x on judge calls per grader loop iteration. |
| Gap-fetch (13) | orchestrator (Opus) | heavy | heavy | Correct — gap targeting requires judgment |
| Patcher (14) | tool-locked subagent, unspecified | work | work | Correct — surgical Edit hunks |
| Fresh review (14.5) | subagent, unspecified | work | work | Correct |
| Polish (15) | tool-locked subagent | work | work | Correct |
| Readability audit (16) | subagent, unspecified | work | **triage** | SIMPLE-WIN — a JSON list of readability recommendations; Haiku is sufficient. The orchestrator applies selectively anyway. |
| Search/web rerank | `web/search/rerank.py:159`: tier="work" | work | work | Correct — reranking needs relevance judgment |
| Retrieval rerank | `retrieval/rerank.py:123`: tier="work" (default) | work | work | Correct |
| Browse extract (LLM) | `browse/extract_llm.py:108`: tier="triage" | triage | triage | Correct |
| Browse AQL | `browse/aql.py:472`: tier="triage" | triage | triage | Correct |
| Consistency vote | `quality/consistency.py:115`: tier="triage" | triage | triage | Correct |
| Headless pipeline synthesize | `pipeline.py:193`: tier="heavy" if full else "work" | heavy/work | heavy/work | Correct |

### Summary of over-tiered stages

Five stages run at Opus cost where Sonnet suffices:

1. **Step 1 (decompose)** — orchestrator is Opus; the decompose sub-task is JSON extraction. SIMPLE-WIN.
2. **Step 2.1 (search planning)** — orchestrator is Opus; the search-plan is a structured table. SIMPLE-WIN.
3. **Step 7 (source tensions)** — orchestrator is Opus; the task is claim extraction. SIMPLE-WIN.
4. **Step 9 (evidence digest)** — orchestrator is Opus; the task is verbatim quote pulling. SIMPLE-WIN.
5. **Grader/judge (12.5)** — JUDGE_TIER="heavy", but comment says "Sonnet acceptable"; categorical rails, not numeric. MEDIUM.
6. **Step 16 (readability audit)** — unspecified subagent; task is low-stakes JSON recommendations. SIMPLE-WIN.

**Root cause:** steps 1, 2.1, 7, and 9 are all executed by the orchestrator itself rather than
delegated to a work-tier subagent. The orchestrator is always Opus (per `bad-research.md:15`:
"You are the orchestrator (Opus)"). This is architecturally correct for coordination — but when
the orchestrator *does* the structured extraction work inline rather than delegating it,
those work items run at Opus rate unnecessarily.

**The fix is NOT to downgrade the orchestrator** (it coordinates the whole pipeline and handles
contested reconciliation). The fix is to **delegate structured extraction steps to a work-tier
subagent** for steps 1, 7, 9, and the search-plan portion of step 2.1.

**Estimated cost impact:**
- A full-tier run currently spends orchestrator (Opus) tokens across ~12 orchestrator-inline steps.
- Steps 1, 7, 9 are each ~2 000–5 000 input tokens + 500–1 000 output tokens at the orchestrator.
- At Opus rates vs Sonnet: 5x input savings, 5x output savings per delegated step.
- Rough estimate for 3 steps delegated: ~(3 × 4 000 input + 800 output) × (Opus - Sonnet rate)
  = ~3 × 4 800 × (15 - 3) μ$/token = ~172 800 μ$ = ~$0.17 per full run.
- On a $90 full run: ~0.2%. Small per-step but meaningful across many runs and easy to implement.

**The grader (12.5) saving is larger:** each grader loop iteration currently costs
~5 000 input + 2 048 output at Opus = $0.075 + $0.153 = ~$0.23/call, up to 3 calls = ~$0.69.
Switching to Sonnet: ~$0.015 + $0.031 = ~$0.046/call × 3 = ~$0.14. Saving: ~$0.55 per full run.
Still small on a $90 run (~0.6%) but the code comment already endorsed this.

**Tag for grader: SIMPLE-WIN** (comment already in constants.py:23)
**Tag for delegation: MEDIUM** (requires spawning subagents for steps currently done inline)

---

## 3. Batch Pipelining — Stage Barriers Audit

### The Anthropic synchronous-batch limitation (confirmed)

From `round1-competitors-B.md:10`:
> "Core weakness: batches are sequential — the orchestrator waits for all subagents in a batch
> before spawning the next, so inter-batch latency is serialized."

From `round1-competitors-B.md:89`:
> "An adversarial pipeline can overlap batch N+1 planning with batch N execution."

This is a fundamental constraint of the Claude Code subagent model via the `Task` tool: you
cannot fire wave N+1 until wave N's tasks complete. This is not a bug in our pipeline; it is
a platform constraint.

### Our current barrier structure

The full-tier pipeline has these sequential barriers (each = wait for all subagents before next):

```
Wave A — fetchers (step 2.4): 10-12 parallel → BARRIER → coverage check
Wave B — gap fetchers (step 2.5): 2-3 parallel → BARRIER
Wave C — loci analysts (step 4): 2 parallel → BARRIER
Wave D — depth investigators (step 5): K=1-6 parallel → BARRIER
Wave E — draft sub-orchestrators (step 10): 3 parallel → BARRIER
Wave F — synthesizer (step 11): 1 → BARRIER
Wave G — critics (step 12): 4 parallel → BARRIER
Wave H — patcher (step 14): 1 → BARRIER
```

Steps 3, 6, 7, 8, 9 run in the orchestrator context itself (no spawned subagents, no barrier
in the Task sense — they are synchronous orchestrator work). This is correct.

### Can any barrier be converted to a pipeline?

**Option A — Overlap step 3 (contradiction graph) with wave B (gap fetchers).**
Currently: wave A fetchers complete → orchestrator runs step 3 (contradiction graph) → step 4
(loci analysis). Step 3 reads the vault corpus from wave A and produces
`research/temp/contradiction-graph.json`. Gap fetchers (wave B) also read wave A's corpus and add
MORE notes. If wave B and step 3 ran concurrently, step 3 would miss wave B's notes.
**Verdict: NOT safe.** Step 3 must see the full corpus.

**Option B — Overlap step 3 + step 7 (source tensions) with step 4 (loci analysis).**
Steps 3 and 4 currently run sequentially (3 → 4) because step 4 reads
`contradiction-graph.json`. But step 7 (source tensions) runs AFTER step 5 and reads
the interim notes + corpus — it does not depend on anything from steps 3 or 4 specifically.
Step 7 could theoretically be moved to overlap with step 6.
**Verdict: marginal win.** Step 7 is orchestrator-inline (no subagents), fast (~30s). Not a
real barrier elimination; just removes ~30s from the sequential chain on a 90-minute run.
**Tag: SKIP-as-overkill** (wall-clock impact: <1% on a 90-minute run)

**Option C — Overlap orchestrator planning (steps 11.1-11.5) with gap-fetch (step 13).**
Currently: critics complete (wave G) → gap-fetch (step 13) → grader → patcher. The orchestrator
could in principle write the synthesis plan (steps 11.3-11.4) while step 13's gap fetchers are
running, since the synthesis plan reads the existing three drafts + reflections, not the new
gap-fetch notes. But this would require the synthesizer to be re-spawned after gap-fetch adds
notes — which violates the write-once invariant.
**Verdict: NOT safe.** Gap-fetch enriches the corpus that the synthesizer draws from. The current
order (gap-fetch → grader → patcher) is load-bearing.

**Option D — Overlap corpus critic (step 8) with evidence digest (step 9).**
Step 8 asks "what source would overturn this?" and may trigger a targeted fetch. Step 9 distills
top claims + verbatim quotes. They read the same corpus but write to different artifacts and have
no read dependency on each other.
**Verdict: SAFE and cheap to implement.** Spawning step-8 as a subagent while the orchestrator
runs step 9 inline would save wall-clock time. However: step 8 is currently orchestrator-inline
(no subagent spawn), runs for ~2-3 minutes, and triggers a targeted fetch if gaps are found.
Delegating step 8 to a subagent while doing step 9 in parallel IS the pipelining win here.
**Tag: MEDIUM** — saves ~2-3 minutes wall-clock on a 90-minute run (~2-3%), moderate complexity.

**Option E — The biggest potential win: critics (step 12) run while patcher waits.**
Currently all 4 critics complete before the patcher spawns. Within the existing design this is
correct. There is no "streaming" pipeline option because the patcher needs ALL critic findings
before applying surgical edits (to avoid conflicting hunks from partial critic input).
**Verdict: NOT actionable under Claude Code's Task model.**

**Option F — depth_first query_shape: pipeline perspectives.**
For `depth_first` queries (`skills/bad-research-5-depth-investigation.md:98-102`),
investigators run SEQUENTIALLY already by design (each perspective reads the prior's committed
position). This is correct and already the most efficient arrangement — there is no barrier to
eliminate here.

### Verdict on pipelining

The Anthropic synchronous-batch limitation is real and constrains the pipeline. Our existing
structure is already well-adapted: most barriers ARE necessary (corpus completeness, write-once
invariant, patch conflict avoidance). The only actionable pipeline win is options D above
(overlap step 8 and step 9), saving ~2-3 minutes wall-clock on full runs.

**No token saving from pipelining** — it only affects wall-clock latency.
**Wall-clock win: ~2-3 minutes on a ~90-minute full run.**
**Tag: MEDIUM** (worth doing if wall-clock matters; marginal on a deep-research task)

---

## 4. Programmatic Tool Orchestration: Fits or N/A?

### The pattern (P8, `round1-core-docs.md:91-98`)

Model writes Python code that calls tools in a loop; only the final `print()` output enters
context. Token usage dropped 37% on complex research tasks (43 588 → 27 297 average, 19+ inference
passes collapsed to 1). The key requirement: the model emits one code-execution tool call that
internally batches N tool calls; stdout-only enters context.

### Does it fit our subagent-spawn model?

Our pipeline uses the Claude Code `Task` tool to spawn subagents, not a tool-execution sandbox
where the model writes Python that calls tools directly. The mechanism is:
- Orchestrator calls `Skill(skill: "bad-research-2-width-sweep")` → orchestrator then uses its
  own tool calls (Bash, web_search, fetch_url) or spawns Task subagents.
- There is no "code-execution tool" in the Claude Code environment where the orchestrator
  can write `for url in urls: fetch(url)` and have it run server-side with stdout-only context.

The `execute_python` tool (referenced in fetcher spawn templates, e.g.
`bad-research-2-width-sweep.md:218`) is a Bash invocation of `python -c`, NOT a sandboxed
code-execution environment that collapses tool-call inference passes. Each `execute_python`
call IS a tool call, not a code block that replaces multiple tool calls.

**The pattern requires:** a code sandbox where calling tools from within the code does NOT add
inference passes (only the print() output counts). In Claude Code's architecture, every tool call
— whether issued directly or via Bash-spawned Python — adds a round-trip. The pattern's efficiency
gain comes from collapsing N inference passes into 1; that's not available here.

**Where it might partially apply:** the funnel (`funnel/orchestrator.py`) is ALREADY a programmatic
implementation of this pattern — `gather()` runs six deterministic stages (fan-out, dedup, rank,
read, filter, store, rerank) without ANY LLM inference passes, and returns only `top_chunks` to the
model. The model sees `~5-15k tokens` of top chunks, not `~80 × raw page bodies`
(`funnel/orchestrator.py:7-8`). This is the spirit of programmatic tool orchestration applied to
our fetch-and-retrieve loop.

**Verdict: N/A for the subagent-spawn layer.** Our Claude Code environment does not provide a
model-writes-code-calls-tools-stdout-only sandbox at the orchestrator level. The funnel already
implements the spirit of this pattern for the retrieval loop (the one place where batching many
tool calls into one LLM-invisible pipeline is beneficial). No new implementation needed.

**Tag: SKIP-as-overkill** (platform constraint, not an implementation gap)

---

## 5. Consolidated Recommendations Table

| # | Recommendation | Current state | Win type | Complexity | Tag |
|---|---|---|---|---|---|
| E1 | Switch JUDGE_TIER from "heavy" to "work" in `calibrate/constants.py:23` | JUDGE_TIER = "heavy" (comment already says "Sonnet acceptable") | ~$0.55/full-run save | 1-line change | SIMPLE-WIN |
| E2 | Downgrade step 16 (readability audit) subagent to triage tier | Unspecified (defaults to work) | ~$0.03/run save | 1-line in spawn template | SIMPLE-WIN |
| E3 | Delegate step 1 (decompose structured extraction) to work-tier subagent | Runs in Opus orchestrator inline | ~$0.06/run save | Medium refactor | MEDIUM |
| E4 | Delegate steps 7 + 9 (source tensions + evidence digest extraction) to work-tier subagents | Runs in Opus orchestrator inline | ~$0.11/run save | Medium refactor | MEDIUM |
| E5 | Spawn step 8 (corpus critic) as a subagent and overlap with step 9 | Sequential orchestrator-inline | ~2-3 min wall-clock | Medium refactor | MEDIUM |
| E6 | Reflections-only context | Already fully implemented | — | Already done | HAVE |
| E7 | Programmatic tool orchestration | Platform N/A; funnel already covers it | — | N/A | SKIP |

---

## 6. Top 3 Efficiency Wins Ranked by (Token-Saved ÷ Complexity)

### Win 1: JUDGE_TIER "heavy" → "work" (SIMPLE-WIN)

**File:** `src/bad_research/calibrate/constants.py:23`
**Current:** `JUDGE_TIER = "heavy"  # Opus; Sonnet acceptable (dossier 09 §A4 table L223)`
**Change:** `JUDGE_TIER = "work"   # Sonnet — categorical rails only; Opus acknowledged overkill`

The code comment already endorses this. The grader emits categorical pass/borderline/fail rails,
not numeric scores. The E2 principle (Arize: "words not numbers") was introduced precisely because
categorical labeling does not require frontier reasoning. Sonnet reliably emits consistent
categorical labels. On 3 grader iterations per full run: ~$0.55 saved per run, 1-line change.

**Token-saved ÷ complexity: extremely high.** 1-line change, code already endorses it.

### Win 2: Delegate steps 7 + 9 to work-tier subagents (MEDIUM)

**Files:** `src/bad_research/skills/bad-research-7-source-tensions.md`,
`src/bad_research/skills/bad-research-9-evidence-digest.md`

Both steps are currently orchestrator-inline structured extraction tasks running at Opus rate.
Step 7 extracts expert disagreements from vault notes into `source-tensions.json`. Step 9 pulls
top claims + verbatim quotes into `evidence-digest.md`. Neither requires frontier reasoning.
Delegating each to a `Task` subagent with `tier="work"` in the spawn template cuts both to Sonnet
rate. Combined saving: ~$0.11/run. Complexity: adding spawn templates to two skill files, similar
to how step 5's investigators are already spawned.

**Token-saved ÷ complexity: high.** Two-skill refactor, clear precedent from step 5's pattern.

### Win 3: Delegate step 1 (decompose) to work-tier subagent (MEDIUM)

**File:** `src/bad_research/skills/bad-research-1-decompose.md`

Step 1 converts the raw query into a structured JSON decomposition. It requires good
instruction-following and JSON production but not frontier analytical reasoning. The orchestrator
currently does this inline (at Opus cost). Delegating to a work-tier subagent saves ~$0.06/run.
More importantly, it establishes the pattern for further orchestrator-delegation of structured tasks,
reducing the "orchestrator does everything at Opus cost" anti-pattern across the pipeline.

**Token-saved ÷ complexity: medium-high.** Single-skill refactor, sets delegation precedent.

---

## 7. What We Are NOT Recommending (and Why)

- **Downgrading the orchestrator itself:** The orchestrator drives cross-locus reconciliation
  (step 6), corpus-critic adversarial targeting (step 8), gap-fetch judgment (step 13), and the
  synthesis plan (steps 11.1-11.4). These require frontier reasoning. The "Opus orchestrator,
  Sonnet workers" asymmetry is load-bearing for quality. Cutting the orchestrator to Sonnet
  would violate the P1/P11 coordinator-mode economics that explain +90.2% eval gain
  (`round1-competitors-B.md:33`).

- **Further pipelining:** The Anthropic synchronous-batch limitation is a platform constraint.
  Our existing barriers are necessary for correctness (corpus completeness, write-once invariant).
  The only safe overlap (steps 8+9) saves <3 minutes on a 90-minute run.

- **Reflections-only as a new implementation:** Already implemented completely and correctly.

- **Programmatic tool orchestration:** Platform N/A. The funnel already captures this pattern
  for retrieval. No new implementation needed at the subagent-spawn layer.

---

## Sources

- `src/bad_research/retrieval/reflections.py` — ReflectionLog, REFLECTION_BULLET_CAP, SYNTHESIS_CONTEXT_TOKEN_CEILING
- `src/bad_research/calibrate/constants.py:23` — JUDGE_TIER with "Sonnet acceptable" comment
- `src/bad_research/config.py:33-38` — model_tiers map
- `src/bad_research/skills/routing_constants.py:159-168` — EFFORT_MAP tier assignments
- `src/bad_research/skills/bad-research.md:15` — "You are the orchestrator (Opus)"
- `src/bad_research/skills/bad-research-2-width-sweep.md:306-364` — step 2.7 distilled-reflection drop
- `src/bad_research/skills/bad-research-11-synthesize.md:133-159` — step 11.4b re-inject raw at end
- `src/bad_research/skills/bad-research-5-depth-investigation.md:84-86` — investigator reads full text
- `src/bad_research/funnel/orchestrator.py:7-8` — "NEVER raw page bodies", flat ~5-15k token context
- `src/bad_research/web/search/rerank.py:159` — web rerank tier="work"
- `src/bad_research/retrieval/rerank.py:123` — retrieval rerank tier="work" (default)
- `src/bad_research/grounding/verifier.py:181` — citation verifier tier="triage"
- `src/bad_research/quality/grader.py:90` — Grader uses JUDGE_TIER
- `src/bad_research/browse/extract_llm.py:108` — tier="triage"
- `docs/superpowers/research/round1-core-docs.md:P3` — reflections-only 66% token reduction
- `docs/superpowers/research/round1-core-docs.md:P8` — programmatic tool orchestration 37% cut
- `docs/superpowers/research/round1-competitors-B.md:10,89` — Anthropic synchronous-batch limitation
