---
name: bad-research-4-loci-analysis
user-invocable: false
description: >
  Step 4 of the Bad Research pipeline (full tier) — builds the contradiction graph
  (Step 4.0 preamble: pairs opposing claims across the corpus into ranked "fight"
  clusters + consensus claims), then spawns 2 parallel analysts to surface 1-6 loci
  (the contested sub-questions worth deep investigation), scoring and
  source-budgeting each into research/loci.json.
---

# Step 4 — Loci analysis (contradiction-graph preamble + parallel analysts)

**Tier gate:** SKIP entirely for `light` tier — proceed directly to step 10. Only `full` tier runs loci analysis.

**Goal:** identify 1–6 specific questions where depth investigation will pay off. Loci should emerge from where the evidence actually forks, not from agent intuition about what seems interesting — so this step first builds an explicit contradiction graph (Step 4.0), then runs loci analysis on top of it.

---

## Recover state

Read these inputs:
- `research/scaffold.md` — vault_tag
- `research/prompt-decomposition.json` — atomic items, sub-questions, pipeline_tier, **`query_shape`** (set by step 1.5 — drives the step-5 fan-out arrangement, see step 6 below)
- All `research/temp/claims-*.json` files (one per fetched note) — Step 4.0 below pairs these into the contradiction graph
- `research/temp/coverage-gaps.md` — which atomic items have weak coverage

Survey the corpus: `bad search "" --tag <vault_tag> -j` to confirm width sweep is complete.

(The contradiction graph + consensus claims are no longer a separate step's input — Step 4.0 below WRITES them from the claims files, and the loci procedure that follows READS them in-context.)

---

## Step 4.0 — Contradiction graph (preamble)

**Two mechanisms — the prose-scan is the DEFAULT, not a fallback.** The mechanical
claim-pairing below needs `research/temp/claims-*.json` (one distilled-claims file per note).
Those are produced ONLY by the legacy hand-dispatched fetcher path. The **preferred**
step-2 path — `bad funnel-gather` (deterministic, $0, flat-context) — has **no model to
distill claims, so it does NOT emit `claims-*.json`**. So on the default path these files are
**absent, and that is EXPECTED, not a failure**: skip the mechanical claim-pairing and use
**Step 1 below (the prose-scan of the corpus) as the first-class contradiction-finding
mechanism** — read it as the primary procedure, do it well (it feeds the loci scoring's
*disagreement* dimension), not as a degraded afterthought. The mechanical claim-graph is the
higher-rigor path available only when a claim-producing fetcher wave was actually run; do NOT
treat its absence as an error or go hunting for the missing files.

**Goal:** before loci analysis (loci = the contested focal points / sub-debates the report must engage), build an explicit graph of opposing claims via **claim-pairing** across the corpus, plus the consensus claims that are settled ground. This is the procedure that was the former step 3.

1. **(Step 4.0 substep 1) Load all claims** from `research/temp/claims-*.json` files.

2. **(Step 4.0 substep 2) Pair contradictions (claim-pairing).** For each claim, find claims from OTHER sources that contradict it. Match on:
   - Same `stance_target` with opposing `stance` (supports vs. refutes)
   - Same `entities` with opposite conclusions
   - Same scope but different `numbers` (e.g., "market grew 15%" vs. "market shrank 3%")
   - Overlapping `scope_conditions` but different `evidence_type` pointing different directions

3. **(Step 4.0 substep 3) Cluster contradiction pairs into fights.** Group related pairs into clusters — each cluster is one contested question:
   ```json
   {
     "cluster_id": "short-slug",
     "fight": "one-sentence description of what's contested",
     "side_a": {"position": "...", "claims": ["claim-text-1"], "sources": ["note-id-1"]},
     "side_b": {"position": "...", "claims": ["claim-text-1"], "sources": ["note-id-1"]},
     "evidence_quality_delta": "which side has stronger evidence types (empirical > theoretical > anecdotal)",
     "scope_overlap": "genuine disagreement, or scoped differently and both right?",
     "decision_relevance": "high|medium|low — does resolving this matter for the research_query"
   }
   ```

4. **(Step 4.0 substep 4) Rank clusters** by decision_relevance (high first), then by evidence_quality_delta (tighter fights rank higher).

5. **(Step 4.0 substep 5) Write `research/temp/contradiction-graph.json`** — array of ranked fight clusters.

6. **(Step 4.0 substep 6) Identify consensus claims.** Claims where 3+ INDEPENDENT sources (after redundancy audit if step 2.6 ran) agree. Write these to `research/temp/consensus-claims.json`. These are the "settled ground" the draft can assert confidently without hedging.

**Step 4.0 outputs (both may be empty arrays if the corpus is univocal):**
- `research/temp/contradiction-graph.json` — ranked fight clusters
- `research/temp/consensus-claims.json` — consensus claims

The loci procedure below reads `contradiction-graph.json` (the fight clusters feed the uncertainty/disagreement scoring) directly from what you just wrote.

---

## Procedure

1. **Spawn 2 `bad-research-loci-analyst` subagents in parallel** (ONE message, both Task calls). Both read the same width corpus but return independently.

   **Spawn template:**
   ```
   subagent_type: bad-research-loci-analyst
   prompt: |
     RESEARCH QUERY (verbatim, gospel):
     > {{paste research/query-<vault_tag>.md body}}

     QUERY FILE: research/query-<vault_tag>.md

     PIPELINE POSITION: You are step 4 (loci-analyst, instance A or B) of
     the Bad Research pipeline. The width sweep (step 2) populated the vault
     tagged <vault_tag>. The contradiction graph (built in Step 4.0 of this
     same step) lives at research/temp/contradiction-graph.json. After you
     and the other analyst return, the orchestrator dedupes your loci and
     assigns budgets.

     YOUR INPUTS:
     - corpus_tag: <vault_tag>
     - analyst_id: "a" (for one) / "b" (for the other)
     - output_path: research/loci-a.json (or research/loci-b.json)
   ```

2. **Wait for both.** If one fails, proceed with the single successful output. If both fail (empty loci lists), tell the user the width sweep was too thin and stop — do not force depth on a weak corpus.

3. **Deduplicate and clamp to 6.**
   - Read both JSON outputs.
   - Dedupe on `name` (exact match) or near-match (same core question, different phrasing). When in doubt, prefer the entry with stronger `corpus_evidence`.
   - If the deduped list exceeds 6, drop the weakest entries — rank by how load-bearing the rationale is for the canonical research query.
   - **Persist both analysts' `skip_loci` arrays** in the merged output — union them under a top-level `skip_loci` key. These justifications matter downstream.

4. **Score and budget each locus (dynamic depth allocation).** For each surviving locus, compute four dimensions:
   - **importance** (0-10): how central is this locus to the research_query? A locus that directly answers a primary sub-question scores 8-10; tangential enrichment scores 2-4.
   - **uncertainty** (0-10): how uncertain is the current evidence? If the contradiction graph shows a sharp fight with equal-quality evidence on both sides, uncertainty is high (8-10). If one side has clearly stronger evidence, moderate (4-6). If the corpus already resolves this, low (1-3).
   - **disagreement** (0-10): how many independent sources disagree? Proxy from the contradiction cluster size. Singletons score low (2-3); multi-source fights score high (7-10). If no contradiction graph exists, estimate from the loci analyst's `opposing_positions`.
   - **decision_impact** (0-10): would resolving this locus change the draft's recommendation or thesis? If yes, high (8-10). If it adds nuance but doesn't change direction, moderate (4-6).

   **Composite score** = importance + uncertainty + disagreement + decision_impact (max 40).

   **Allocate source budgets.** Total source budget for step 5 is 40. Distribute proportionally:
   - Loci scoring 30-40: `source_budget` up to 15 (deep dive)
   - Loci scoring 20-29: `source_budget` up to 10 (standard)
   - Loci scoring 10-19: `source_budget` up to 5 (shallow pass)
   - Loci scoring <10: `source_budget` 0-3, or skip investigation entirely

   It's fine if only 1-2 loci score above 20 — allocate heavily to them.

5. **Write scored loci to `research/loci.json`.** Schema:
   ```json
   {
     "loci": [
       {
         "name": "...",
         "one_line": "...",
         "flavor": "dialectical|synthesis|technical",
         "importance": 8,
         "uncertainty": 7,
         "disagreement": 6,
         "decision_impact": 9,
         "composite_score": 30,
         "source_budget": 12,
         "rationale": "..."
       }
     ],
     "skip_loci": [...union from both analysts...]
   }
   ```

6. **Decide investigator count AND fan-out arrangement (branch on `query_shape`).** Read `query_shape` from `research/prompt-decomposition.json` (set by step 1.5). The fan-out *shape* — orthogonal to the tier — decides how step 5's investigators are *arranged* (Claude Research `research_lead_agent.md:12-29`):

   - **`breadth_first`** → investigators run **in parallel** across the independent sub-questions / loci, **importance-ordered** (highest composite-score locus first), `K = min(n_subq, cap)` capped at 6. This is the default arrangement for surveys/comparisons/collections — the loci are independent so they go wide simultaneously.
   - **`depth_first`** → **2–4 SEQUENTIAL** perspectives on the **one** highest-impact locus. Do NOT fan out across many loci; instead pick the single most contested/load-bearing locus and queue 2–4 investigators that run one after another, each reading the prior's committed position (set up in step 5). One topic, many angles, going deep.
   - **`straightforward`** → a **single** investigator on the one locus that matters. No ensemble.

   Record the chosen arrangement (`parallel` / `sequential` / `single`) and the ordered locus list in `research/loci.json` under a top-level `"fanout"` key so step 5 dispatches accordingly. Absent a `query_shape` (older runs), default to the legacy parallel-per-locus behavior. The base rule still holds: one depth-investigator per locus with `source_budget > 0`, capped at 6; if only 1 locus passes scoring, spawn 1.

**INVARIANT:** at least one `flavor: "dialectical"` locus must be present unless an analyst's `skip_loci` justifies its absence with specific evidence of a univocal corpus. No dialectical locus + no justification = re-spawn the loci-analyst with a tighter prompt.

**Placeholder-breadcrumb ban:** depth investigators will fetch sources; do not hand them breadcrumb placeholders like `bad-research-locus-seed` — use real source note ids from the vault or omit `--suggested-by` entirely.

---

## Exit criterion

- `research/loci.json` exists with at least 1 locus (or both analysts justified skip with `skip_loci`)
- At least one dialectical locus OR a documented justification in `skip_loci`
- All retained loci have `source_budget` allocated

---

## Next step

Return to the entry skill (`bad-research`). Invoke step 5:

```
Skill(skill: "bad-research-5-depth-investigation")
```
