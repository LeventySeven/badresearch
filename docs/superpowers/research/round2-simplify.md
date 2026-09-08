# Round 2 — Consolidation Map: Simplest Equivalent Pipeline

**Scope:** 24 skill files (bad-research.md + 23 step skills), plus router.py and routing_constants.py.
**Goal:** quantify whether 4 adversarial passes are justified or redundant; produce a ranked list of consolidation proposals that preserve the pipeline's verification edge.

---

## 1. Stage Dependency Graph

### Full-tier (canonical artifact chain)

```
query (GOSPEL)
  │
  ├─ 0.5-clarify           → clarify.json
  ├─ 1-decompose           → prompt-decomposition.json, coverage-matrix.md
  ├─ 1.5-query-router      → route + query_shape written into decomposition
  ├─ 1.6-plan-gate         → (interactive expensive only; patches sub_questions)
  │
  ├─ 2-width-sweep         → vault notes (40–80), reflections.md, coverage-gaps.md,
  │                          claims-*.json, redundancy-audit.md
  ├─ 3-contradiction-graph → contradiction-graph.json, consensus-claims.json
  ├─ 4-loci-analysis       → loci.json (scored, with fanout key)
  ├─ 5-depth-investigation → interim-{locus}.md notes (each: ## Committed position)
  ├─ 6-cross-locus-reconcile → comparisons.md
  ├─ 7-source-tensions     → source-tensions.json (3–7 tensions, pre-committed)
  ├─ 8-corpus-critic       → corpus-critic-gaps.json, fetches gaps → vault, comparisons.md updated
  ├─ 9-evidence-digest     → evidence-digest.md (top claims + verbatim quotes)
  │
  ├─ 10-triple-draft       → draft-{a,b,c}.md  (3 parallel angle-specific drafts)
  ├─ 11-synthesize         → synthesis-plan/outline/conflicts/evidence.md,
  │                          synthesis-pass1.md, final_report.md
  │
  ├─ 11.5-citation-verifier → citation-verify-actions.json (disposition per cited sentence)
  │
  ├─ 12-critics            → critic-findings-{dialectic,depth,width,instruction}.json
  ├─ 13-gap-fetch          → post-critic-fetch-log.md + new vault notes (≤5 gaps)
  ├─ 12.5-grader           → grade-round-N.json, grader-log.json
  │   (calls 14-patcher ≤3×)
  ├─ 14-patcher            → patch-log.json + edited final_report.md
  ├─ 14.5-fresh-review     → fresh-review.json + surgical edits
  │
  ├─ 15-polish             → polish-log.json + edited final_report.md
  └─ 16-readability-audit  → readability-recommendations.json,
                             readability-decisions.json,
                             + uncited-gate (ship-block), recitation-gate (major),
                             + citation-coalescing
```

### Light-tier (artifact chain)

```
0.5-clarify → 1-decompose → 1.5-router → 1.6-plan-gate →
2-width-sweep (funnel, 12–20 sources) →
10-triple-draft (single draft, no subagents) →
12-critics (slim single: dialectic+instruction merged, inline apply) →
15-polish → 16-readability+gates
```

### Agentic-fast (artifact chain)

```
0.5-clarify → 1-decompose → 1.5-router →
agentic-fast (bounded ReAct ≤10 steps, ≤15 tool calls) →
12-critics (slim single, inline apply) →
15-polish → 16-readability+gates
```

---

## 2. Overlap Analysis — Checking Stages × Failure Mode Guarded

Each of the four adversarial passes (8, 12-fan-out, 12.5, 14.5) plus 11.5, 16-gates is analyzed for the **distinct failure mode** it guards.

| Stage | When | Failure mode guarded | Distinct from others? |
|---|---|---|---|
| **2.6 redundancy-audit** | full | Derivative sources over-counted as independent evidence | TRUE-DISTINCT (only deduplication pass) |
| **3 contradiction-graph** | full | Loci driven by intuition rather than actual corpus forks | TRUE-DISTINCT (feeds loci; no other stage pairs claim-vs-claim across corpus) |
| **4 loci-analysis** | full | Shallow equal-treatment of all sub-questions; misses contested focal points | TRUE-DISTINCT (produces scored loci.json consumed by step 5) |
| **5 depth-investigation** | full | Width corpus gives breadth but not committed positions; draft hedges everything | TRUE-DISTINCT (produces interim notes with Committed Position) |
| **6 cross-locus-reconcile** | full | Report treats each locus in isolation; misses cross-locus contradictions and convergences | TRUE-DISTINCT (comparisons.md is the argumentative spine; no other stage does cross-locus tensioning before draft) |
| **7 source-tensions** | full | Orphan tensions invisible to locus analysis (nuance in corpus bodies not elevated as loci) | PARTIAL-REDUNDANT-WITH-3+6: 3 already built contradiction-graph; 6 already extracted cross-locus tensions; step 7 adds orphan-scan of body text for tensions that slipped past both — its unique value is reading full source bodies specifically for "however" clauses and buried caveats |
| **8 corpus-critic** | full | Pre-draft overturning sources exist but weren't fetched; period-pinned primary filings missing | TRUE-DISTINCT — only stage that asks "what source would overturn THIS direction?" before drafting; period-pinned check is unique to step 8's preflight |
| **9 evidence-digest** | full | Draft sub-orchestrators re-read raw vault bodies inefficiently; no compact top-claims layer | TRUE-DISTINCT for efficiency (distilled evidence layer for drafters; compresses token cost and ensures high-fidelity verbatim quotes surface) |
| **11.5 citation-verifier** | full | Synthesizer hallucinated citation markers or fabricated quoted_support spans; forward binding missed paraphrases | TRUE-DISTINCT — only stage running Tier-A byte-identity → Tier-B NLI → Tier-C judge on every cite; catches fabricated quotes at $0 before critics even see them |
| **12-critics (4-fan-out)** | full | Post-synthesis omissions, weak spots, prompt-adherence gaps that the in-context orchestrator can't see from the draft's own vantage point | TRUE-DISTINCT as a SET; but each sub-critic is specialized: |
| ↳ dialectic-critic | | Counter-evidence the draft straw-manned or ignored | |
| ↳ depth-critic | | Shallow spots where interim-note substance was abandoned in synthesis | |
| ↳ width-critic | | Width-corpus clusters draft ignored despite evidence | |
| ↳ instruction-critic | | Structural prompt-adherence: headings, ordering, entity coverage | |
| **12.5-grader** | full | Critics catch textual/logical issues; grader catches axis-level metric failures (factual, completeness, source_quality, efficiency) that no critic maps to quantifiably | PARTIAL-REDUNDANT-WITH-12: grader's `completeness` axis overlaps width-critic findings; `factual` axis overlaps dialectic-critic; however grader's QUANTIFIED 5-axis scoring + convergence-loop distinguishes it — it turns qualitative findings into a pass/fail loop that terminates when axes >= 0.70 |
| **13-gap-fetch** | full | Critics flag gaps that patcher can't address because vault has no sources for them | TRUE-DISTINCT — no other stage adds vault sources after synthesis; it's the bridge between critic findings and patchable evidence |
| **14-patcher** | full | Critics+verifier produce findings but nothing applies them to the text | TRUE-DISTINCT (the only applying stage; other stages are read-only) |
| **14.5-fresh-review** | full | In-context critics are contaminated by 30+ minutes of dispatch history; whole-report drift invisible to someone who watched it grow | TRUE-DISTINCT — the only stage with zero pipeline context; catches gestalt issues (thesis drift, unanswered sub-questions, structural incoherence) that in-context critics cannot perceive |
| **15-polish** | all | Pipeline vocabulary leaks, filler prose, run-on sentences, YAML frontmatter | TRUE-DISTINCT (hygiene pass; no other stage strips leaks) |
| **16-uncited-gate** | all | Factual claims without verifiable citations | TRUE-DISTINCT (only deterministic $0 ship-block; non-bypassable) |
| **16-recitation-gate** | all | Verbatim copying from sources | TRUE-DISTINCT (only stage detecting verbatim reproduction) |

### Summary verdict on the 4 adversarial passes:

- **Corpus-critic (8):** TRUE-DISTINCT — pre-draft adversarial; unique "would overturn" framing
- **4-critic fan-out (12):** TRUE-DISTINCT as a set; each critic targets a non-overlapping failure class
- **Grader loop (12.5):** PARTIALLY REDUNDANT with 12 on qualitative axis but its quantified convergence loop is the only stage that raises axis scores against a metric floor; the MERGE target is to collapse grader's `completeness` + `factual` scan back into width+dialectic critic output and use grader only for the convergence gate, not the full axis-scan
- **Fresh-context review (14.5):** TRUE-DISTINCT — sole zero-context reader; catches what no in-context pass can

---

## 3. Consolidation Proposals

### P1 — MERGE: step 7 (source-tensions) into step 6 (cross-locus-reconcile)

**What merges:** step 6 already reads all committed positions and scans for cross-locus tensions. Step 7's orphan-scan (reading full source bodies for tensions not elevated as loci) is genuinely valuable but its output (source-tensions.json) is just a richer version of what step 6 produces. Merged, step 6 ends with: (a) cross-locus tensions table, (b) an orphan-scan of the top 8–12 source bodies for tensions that slipped past loci analysis, (c) all written to a single tensions artifact.

**What's preserved:** every tension currently surfaced by step 7's orphan-scan (the "however" clause pass), the pre-committed resolutions, the decision_relevance filter.

**What's saved:** one full-tier skill invocation (step 7 as a separate stage), one Skill() call, the step 7 subagent spawn (it's an orchestrator-executed scan, not a subagent, so the save is latency and context overhead rather than a Task). The `comparisons.md` + `source-tensions.json` artifacts collapse into one richer `tensions.md` that drafters read.

**Loss:** none on quality; slight increase in step 6's prompt size/responsibility.

**Files:** `bad-research-7-source-tensions.md` content folds into `bad-research-6-cross-locus-reconcile.md` (lines 34–83 of step 7 become a new "Step 6.5 — Orphan tension scan" subsection).

---

### P2 — MERGE: step 3 (contradiction-graph) into step 4 (loci-analysis), making step 3 a sub-step

**What merges:** step 3 is a precondition for step 4 — it builds the graph that step 4 converts into loci. They have sequential dependency (step 4 reads step 3's output) but are described as separate skills. The contradiction-graph logic (pairs-claims-across-corpus) is <100 lines of orchestrator procedure and requires no subagent. It's mechanical bookkeeping between the width sweep and the loci analysts.

**What's preserved:** all claim-pairing logic, fight-cluster ranking, consensus-claims.json, the dialectical invariant enforced by loci analysis.

**What's saved:** one full-tier Skill() invocation, one separate step in the orchestrator's todo list. The procedure currently in `bad-research-3-contradiction-graph.md` becomes "Step 4.0 — Contradiction graph" inside `bad-research-4-loci-analysis.md`.

**Loss:** none — step 3 has no subagent, no external output besides the two JSON files; step 4 already reads them as inputs.

**Files:** `bad-research-3-contradiction-graph.md` content (lines 20–68) folds into `bad-research-4-loci-analysis.md` as a preamble sub-step.

---

### P3 — SURFACE-SIMPLIFY: grader loop (12.5) — collapse axis-scan into critic output, keep only convergence gate

**What changes:** currently the grader runs its own 5-axis scan against the report + corpus JSON, THEN feeds findings to the patcher. The `completeness` and `factual` axes substantially re-detect what the width-critic and dialectic-critic already found in step 12. The unique value of 12.5 is the **convergence loop** (judge→patch→re-judge ≤3) and the **quantified pass/fail gate** (axes >= 0.70).

**Proposal:** the 5-axis scan is hidden from the operator but simplified internally — instead of a fresh full-corpus scan, the grader's judge reads the critic findings JSONs already present (`critic-findings-*.json`) and scores the report against them rather than independently rediscovering the same findings. This turns grader round 1 from a $3–5 fresh scan into a $0.50 verdict-aggregation, while rounds 2 and 3 (if needed) remain full grader calls since the first patch may introduce new issues.

**What's preserved:** the convergence loop (≤3 rounds), the quantified axis floor (0.70), the patch-not-regenerate discipline, the grader-log.json audit trail.

**What's saved:** ~1 full Opus-tier grader call per run on average (the 80% of runs that pass on round 1 now pay a fraction of the current round-1 cost).

**Loss:** grader round 1 loses the ability to catch issues the critics missed entirely (it only scores what critics flagged). Risk: low — step 14.5 (fresh-review) is the backstop for critic blind-spots.

---

### P4 — CUT: step 9 (evidence-digest) as a separate stage; fold into step 10's 10.0b sub-step

**What's cut:** `bad-research-9-evidence-digest.md` as a named step. The evidence digest is a filtered, grouped view of `claims-*.json` files. Step 10.0b already describes "plan from reflections, re-inject raw only at the end" — the evidence digest is just the pre-digested form of what step 10.0b re-injects anyway. The work is identical.

**What's preserved:** the top-claims + verbatim-quotes layer still gets built; it's just built inside step 10.0b rather than as a separate step with its own skill invocation.

**What's saved:** one full-tier Skill() invocation, one step in the todo list, one disk artifact that only steps 10 and 11 read (both of which can generate it inline). Removes the `research/temp/evidence-digest.md` dependency chain — steps 10 and 11 call the distilled reflections + targeted re-inject directly.

**Loss:** the digest artifact is currently a recoverable state checkpoint (if step 10 crashes, step 9's output is still there). Moving it inline removes that checkpoint. Mitigation: step 10.0b already writes `research/temp/reflections.md` which is the lighter-weight equivalent checkpoint.

**Note:** this is the mildest cut on the list; if the checkpoint value outweighs the simplicity gain, KEEP it as-is.

---

### P5 — KEEP: 4-critic parallel fan-out (step 12, full tier)

**Defense:** the four critics guard four **non-overlapping** failure classes:
- `dialectic`: counter-evidence straw-manning (content correctness)
- `depth`: synthesis abandoned interim-note substance (depth fidelity)
- `width`: coverage gaps the draft silently dropped (breadth fidelity)
- `instruction`: structural prompt-adherence (format fidelity)

No other stage catches all four simultaneously. Collapsing to 2–3 critics would merge non-overlapping concerns into one pass, reducing finding specificity without saving meaningful cost (critics are Sonnet-tier, ~$0.50 each). The $2 total for 4 parallel critics on a $60–120 full run is 0.2–3% of total cost — not a meaningful savings target. Parallelism means they add ~0 wall-clock time. **KEEP.**

---

### P6 — KEEP: 11.5 citation-verifier

**Defense:** this is the only stage that verifies byte-identity between a cited sentence and its source note. It catches fabricated quotes at $0 (Tier-A byte-identity) before any expensive method runs. Without it, fabricated `quoted_support` spans pass through to step 16's uncited-gate, which is a sentence-level ship-block, not a span-integrity check. The two gates guard orthogonal properties: 11.5 checks *span integrity* (is the quoted text actually in the source?); step 16's uncited-gate checks *sentence-level citation presence*. **KEEP.**

---

### P7 — KEEP: 14.5 fresh-context review

**Defense:** explicitly the only stage with zero pipeline context. In-context critics (step 12) have been present for 30+ minutes of dispatch history; they cannot perceive whole-report drift, unanswered sub-questions introduced by synthesis, or thesis-level contradictions that only emerge when reading cold. This is the "cold reader before ship" architectural pattern. Cost: 1 Opus read call, cheap. **KEEP.**

---

## 4. Simplest Operator Surface

The pipeline currently has one entry command: `/bad-research` (or `bad run` in CLI mode). The operator surface is clean. Flags that exist:

| Flag | Current behavior | Simplification verdict |
|---|---|---|
| `--effort minimal/low/medium/high` | 4-level dial over route + fan-out | KEEP — one dial is the simplest possible complexity knob |
| `--auto` | Skip 0.5-clarify and 1.6-plan-gate | KEEP — needed for wrapped/eval runs |
| `--max-tokens N` | Token-ceiling with short-circuit-to-synthesis | KEEP — opt-in budget cap, inert by default |
| `--cheap` | Demotes heavy→work model tier | KEEP — one-word cost cut |
| `--interactive` | Fires plan-gate | AUTO-DEFAULT — `plan_gate_fires()` already defaults to `interactive=False`; the operator doesn't pass a flag, the CLI detects it. Already correct. |
| `--reasoning-effort` | Alias for `--effort` | MERGE with `--effort`; one name |

The pipeline has **one command, one meaningful dial (`--effort`)**, two operational modes (`--auto` for batch, default for interactive). That's already a minimal surface. No additional flags should be exposed.

---

## 5. Proposed Minimal-but-Equivalent Full-Tier Pipeline

Applies proposals P1–P4 (P5–P7 are KEEP). Numbered steps after consolidation:

```
0.5 → 1 → 1.5 → 1.6 →
2 →                            (width sweep, unchanged)
4* →                           (was 3+4: contradiction-graph is now step 4.0 preamble)
5 → 6* →                       (was 6+7: orphan-scan is now step 6.5 subsection)
8 → 10* →                      (was 9+10: evidence digest built in step 10.0b)
11 →
11.5 →
12 → 13 → 12.5 → 14 → 14.5 →  (adversarial block, unchanged)
15 → 16
```

**Net step count:** from 21 full-tier stages (including half-steps) to **17 stages** — 4 skill invocations removed without removing any adversarial capability. The contradiction-graph, source-tensions, and evidence-digest logic all survive; they're just no longer separate Skill() calls.

**Preserved capabilities:**
- Parallel breadth+depth: unchanged (steps 5, 10 triple-draft, 12 4-critic fan-out)
- Contradiction handling: unchanged (step 4.0 preamble + step 6.5 orphan-scan)
- Adversarial verification: unchanged (all 4 critics + grader + fresh-review)
- Citation verification: unchanged (11.5 byte-identity + NLI + triage-judge)
- Deterministic ship-gates: unchanged (16-uncited-gate + recitation-gate)

---

## 6. Verdict on the 4 Adversarial Passes

| Pass | Verdict | Distinct failure mode |
|---|---|---|
| Corpus-critic (8) | **JUSTIFIED** | Pre-draft overturning sources; period-pinned primary coverage |
| 4-critic fan-out (12) | **JUSTIFIED** | 4 non-overlapping classes (counter-evidence / depth-fidelity / coverage / instruction) |
| Grader loop (12.5) | **JUSTIFIED but SURFACE-SIMPLIFIABLE** | Quantified convergence loop is load-bearing; round-1 axis-scan partially overlaps critic output → P3 reduces round-1 cost while preserving the convergence gate |
| Fresh-context review (14.5) | **JUSTIFIED** | Sole zero-context reader; catches whole-report drift |

**Short answer:** four passes are justified, not redundant — they guard four genuinely non-overlapping failure modes at four distinct pipeline positions. The apparent redundancy is positional (they all "check" the report) not functional. No pass can be cut without a capability loss. The grader loop's only real redundancy is in its first-round independent scan, which P3 collapses into critic-output aggregation.
