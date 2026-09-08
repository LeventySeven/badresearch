# Round 1 Research: HyperResearch Architecture + Transcript Signal

**Date:** 2026-05-29
**Scope:** HyperResearch V8 full source read + transcript corpus grep

---

## Part A — HyperResearch Architecture Summary

### What it is

HyperResearch is an open-source Claude Code research harness (`pip install hyperresearch`, MIT license, PyPI). It calls itself "the most powerful deep research harness" and claims the top spot on the DeepResearch-Bench leaderboard (projection, third-party validation pending). Architecture name: **HYPERRESEARCH V8**. Source: `/Users/seventyleven/Desktop/researchfms/hyperresearch/src/hyperresearch/`.

### Core design: the multi-skill chain

V7 was a single 1200-line skill loaded once. By step 4, context compaction had evicted the procedure, causing silent fallback to single-draft. V8 fix: **each pipeline step is its own skill file**, loaded fresh via `Skill(skill: "hyperresearch-N-…")` at the moment it is needed. The orchestrator (Opus) only sequences; it never does a step's work itself. `README.md:41`.

### The 16-step pipeline

| Steps | What runs |
|---|---|
| **All tiers** | 1 (decompose), 2 (width sweep), 10 (triple-draft), 15 (polish), 16 (readability audit) |
| **Full only** | 3 (contradiction graph), 4 (loci analysis), 5 (depth investigation), 6 (cross-locus reconcile), 7 (source tensions), 8 (corpus critic), 9 (evidence digest), 11 (synthesize), 12 (critics ×4), 13 (gap-fetch), 14 (patcher) |

**Light tier:** 1→2→10→15→16 (~$5–15, ~30–40 min)  
**Full tier:** all 16 (~$60–120, ~1.5–2.5 hr)  
Source: `hyperresearch.md:62–68`.

### Two load-bearing principles

1. **Patch, never regenerate.** After step 11 writes `final_report.md`, only surgical Edit hunks are allowed. The patcher (step 14) and polish auditor (step 15) are tool-locked to `[Read, Edit]` — they literally cannot Write a new draft. `README.md:72–75`.

2. **Canonical research query is gospel.** The verbatim user prompt is written to `research/query-<vault_tag>.md` once, and every step and every subagent re-reads it from disk. `README.md:75`.

### Subagent roster (model assignments)

- **Haiku:** width-sweep fetchers (cost control)
- **Sonnet (1M ctx):** source analysts, loci analysts, depth investigators, corpus critic, fetchers
- **Opus:** draft orchestrators ×3, synthesizer, dialectic/depth/width/instruction critics, patcher, polish auditor, readability recommender
Source: `README.md:79–96`, `hyperresearch-10-triple-draft.md`.

### Vault: persistent, SQLite-backed, compounding

Every fetched source becomes a Markdown note with YAML frontmatter in `research/notes/`. SQLite is cache; Markdown is truth. Provenance chains (`--suggested-by`) form a tree rooted at seed fetches; broken chains are lint errors. PDFs fetch directly via pymupdf. `README.md:99–116`.

### Structurally enforced invariants

- `scaffold-prompt` lint blocks if the scaffold doesn't open with the verbatim user prompt.
- `locus-coverage` lint: every step-4 locus must have a step-5 interim note.
- `patch-surgery` lint: unresolved CRITICAL patcher findings surface as errors.
- Schema integrity: `tier`, `content_type`, `type` are SQLite CHECK-constrained.
Source: `README.md:119–128`.

### Authenticated crawling

`hyperresearch setup` opens a browser for the user to log in. LinkedIn, Twitter, Facebook, Instagram, TikTok auto-use a visible browser. `README.md:134–138`.

---

## Part B — What HyperResearch does that bad-research V8 MIGHT be missing (diff-think)

The following are features present in HyperResearch's skills but not confirmed to be in bad-research's current pipeline based on reading both skill sets.

**1. Three-tier response_format classification (short / structured / argumentative) is a first-class step-1 output.**
HyperResearch's step 1 explicitly classifies `response_format` (not just `pipeline_tier`) and writes it to `prompt-decomposition.json`. Every drafting step reads this field and hits exact word-count ranges (short: 500–2000 w, structured: 2000–5000 w, argumentative: 5000–10000 w). Bad-research has this in its decompose skill, confirmed, but the word-count band enforcement is explicit in HyperResearch's skill text at `hyperresearch-1-decompose.md:113–125`.

**2. URL utility scoring (six-dimension composite) before batching.**
Step 2.3 of HyperResearch scores each candidate URL on six axes: Authority, Novelty, Stance diversity, Coverage, Redundancy, Freshness (0–3 each, max 18). Selection rule forces every atomic item to have ≥3 candidate URLs before low-utility URLs from well-covered items are included. Bad-research step 2 appears to use the same approach but confirming the explicit 6-dimension score table is in HyperResearch (`hyperresearch-2-width-sweep.md:113–130`) — worth verifying bad-research has the same numeric schema or is equivalent.

**3. Wikipedia-as-source-hub rule is explicit.**
HyperResearch has a named "Wikipedia SOURCE HUB rule": include Wikipedia URLs in the fetch queue to harvest their reference lists, but never cite Wikipedia in the final report. `hyperresearch-2-width-sweep.md:101–103`. This is a specific fetch-quality rule worth confirming is explicit in bad-research's width sweep.

**4. Evidence redundancy audit (step 2.6) — derivative source detection.**
HyperResearch step 2.6 clusters fetched sources by >60% quoted_support overlap AND by `suggested-by` citation ancestry. Derivative sources are tagged `derivative-of` and discounted in coverage counting. This prevents the failure mode "N sources that are really 1 source." Source: `hyperresearch-2-width-sweep.md:200–215`. Bad-research has a funnel with dedup, but this specific post-fetch derivative-clustering step at the claim level is worth checking.

**5. Contradiction graph feeds loci analysis causally.**
Step 3 produces `contradiction-graph.json` (ranked fight clusters). Step 4 READS this file so loci emerge from where the evidence actually forks, not from agent intuition. The causal link — contradiction graph → loci scoring — is a specific design decision. `hyperresearch-3-contradiction-graph.md:1–10`, `hyperresearch-4-loci-analysis.md:25`. Worth confirming bad-research's step 3→4 handoff is as explicit.

**6. Four-dimension locus scoring with dynamic source budget allocation.**
Step 4 scores each locus on importance, uncertainty, disagreement, decision_impact (each 0–10, max composite 40). Source budget for depth investigators is allocated proportionally from a pool of 40. Loci <10 composite may be dropped. `hyperresearch-4-loci-analysis.md:65–82`. This is a specific allocation rule.

**7. Pre-draft corpus critic (step 8) runs BEFORE drafting — "what source would overturn this?"**
The corpus critic's job is explicitly framed as the highest-leverage intervention: corrections applied before drafting cost nothing; corrections after drafting require patches. The critic asks "what source, if found, would overturn the current direction?" and triggers a targeted fetch wave. `hyperresearch-8-corpus-critic.md:10–16`. Bad-research has this (step 8), but worth confirming the OVERTURN-first framing is in both.

**8. Period-pinned primary source coverage check is a PRE-FLIGHT on step 8.**
Before spawning the corpus-critic, step 8 explicitly checks whether every `time_periods` entry in the decomposition has a vault note that is a primary filing for THAT EXACT period. If not, it adds a `priority: critical` gap of type `period-pinned-primary` BEFORE the corpus critic runs. This is a separate pre-flight, not part of the critic's general gap analysis. `hyperresearch-8-corpus-critic.md:30–57`.

**9. Synthesis pre-conflict-resolution is orchestrator-only (step 11.2).**
Before spawning the synthesizer (which is tool-locked to [Read, Write] with no Bash access), the orchestrator itself resolves factual conflicts between the three drafts by checking vault notes via Bash. Conflicts are written to `synthesis-conflicts.md` and passed to the synthesizer. `hyperresearch-11-synthesize.md:52–65`. This explicit conflict-resolution gate prevents the synthesizer from synthesizing contradictions without resolution.

**10. Readability recommender writes JSON suggestions; orchestrator selectively applies (NOT auto-apply).**
Step 16 uses a split architecture: the recommender writes up to 50 JSON suggestions with exact `current`/`recommended` string fields; the orchestrator applies them via selective Edit calls. The skill specifies which categories to apply confidently vs. skeptically, and what to always skip. `hyperresearch-16-readability-audit.md`. This is more explicit than a pure auto-reformatter.

**Items bad-research HAS that HyperResearch DOES NOT (bad-research advantages):**

- **Step 0.5 clarifier** — triage-tier ambiguity check before decompose. HyperResearch has no pre-decompose clarification. `bad-research-0.5-clarify.md`.
- **Step 1.5 query router** — explicit route classifier (`agentic-fast` / `light` / `full`) backed by `router.py`. HyperResearch uses the tier field from step 1 but has no separate routing step.
- **Step 1.6 plan-gate** — user-editable pause point for interactive expensive runs. HyperResearch has no plan-gate.
- **`agentic-fast` route** — bounded ReAct loop ($1–5, <3 min). No HyperResearch equivalent.
- **Step 11.5 citation verifier** — backward NLI grounding pass that verifies every cited sentence before critics run. HyperResearch has no citation verification layer.
- **Step 12.5 grader loop** — in-pipeline judge→patch→re-judge cycle (≤3 rounds). HyperResearch has no grader.
- **Step 14.5 fresh-context review** — single fresh-Opus reviewer pass cold-reads the patched report before polish. HyperResearch has no equivalent.
- **Reasoning-effort dial** (`--effort minimal/low/medium/high`) — adjusts fan-out, model tier, extended thinking.
- **Token ceiling + short-circuit-to-synthesis** — `should_short_circuit()` protects synthesis budget at all costs when ceiling approaches.
- **Seven-piece subagent spawn contract** — bad-research adds `objective`, `output_shape`, `tools_allowed`, `stop_conditions` to the 3-piece HyperResearch contract.
- **Grounding stack** (`bad_research/grounding/`) — NLI entailment + claim anchors + verifier at the Python level.
- **Calibration harness** (`bad_research/calibrate/`) — golden test set + judge + runner.
- **Browse ladder** (`bad_research/browse/`) — agent browser, browserbase/browseruse, stagehand, AgentQL.
- **Funnel + retrieval system** (`bad_research/funnel/`, `retrieval/`) — RRF fusion, semantic reranker, chunk store, reflection queries.

---

## Part C — Transcript Corpus Insights (deep-research-relevant)

**1. The verifier problem is the key constraint on research agent quality.**
"The hardest open problem in agent AI: for most real-world tasks, there is no good verifier… RL-trained agents will be superhuman on tasks with clean verifiers (math, code) and only marginally better on tasks without (strategy, writing, research). The gap between 'tasks with good verifiers' and 'tasks without good verifiers' will grow, not shrink."
Source: `TRANSCRIPTS_A16Z.md:344–350`

**2. Context engineering (not prompt engineering) is the new research moat.**
"The agent that wins is not the one with the best model but the one with the best context assembly pipeline… companies that invest in retrieval infrastructure, memory systems, and tool selection will outperform those that just swap in newer models."
Source: `TRANSCRIPTS_A16Z.md:213–216`

**3. Inline per-sentence citations are the hardest and most trust-building option.**
Perplexity: "Answer with inline citations per sentence (hardest to generate, best for trust)… The LLM is prompted to attribute every factual claim. This requires the model to track which part of which document supports which claim — a non-trivial generation task. But it dramatically improves user trust and verifiability."
Source: `TRANSCRIPTS_YC.md:532–536`

**4. Sub-agents with uncorrelated context windows avoid context pollution.**
"Sub-agents have uncorrelated context windows. If the orchestrator has accumulated a lot of irrelevant context, sub-agents start clean. This avoids the problem where a long session degrades because earlier tool calls or failed attempts pollute the context."
Source: `TRANSCRIPTS_YC.md:236`

**5. Retrieval is always the bottleneck (not the model).**
"Pattern 2: Retrieval Is Always the Bottleneck… Naive RAG: vector database of embedded documents, cosine similarity search. Good for single-hop questions where the answer lives in one text chunk. Problem: pure vector search retrieves off-target information (context poisoning) → hallucinations. Hybrid RAG: combine vector semantics with symbolic filters."
Source: `TRANSCRIPTS_DEEPLEARNINGAI.md:1038–1040`

**6. Evaluation-driven self-improvement loop: grader → RL signal → prompt playbook.**
Genspark: "Build a high-quality grader for all types of agent output. Grader serves: (a) trigger second-pass refinement when quality is below threshold, (b) generate RL signal, (c) populate 'prompt playbook' of collective feedback. Agent system improves continuously with usage."
Source: `TRANSCRIPTS_DEEPLEARNINGAI.md:777`

**7. Without new grounding, outputs converge to a stationary distribution.**
"Without new grounding (new training data, new external inputs), a model's outputs converge to a stationary distribution; they cannot escape the information manifold defined by training." (RAG invention story — adding information to reduce entropy at inference time.)
Source: `TRANSCRIPTS_A16Z.md:666–671`

**8. Specification gaming is already happening in agents; ambiguity requires a clarifier.**
"The specification gaming problem is already happening: coding agents that 'pass tests' by hardcoding expected outputs… Why this matters for enterprise: 'complete this task' is an ambiguous instruction; current agents do not robustly ask for clarification when uncertain; they tend to make assumptions and proceed."
Source: `TRANSCRIPTS_A16Z.md:340–341`

**9. Eager context assembly + on-demand action is the right architecture split.**
"A context assembly phase and an action phase, where the context assembly phase is run eagerly (in advance of when it's needed) and the action phase is run on demand. Eager context assembly is efficient because it happens while the user is doing other things; on-demand action generation is necessary because it depends on the user's specific intent."
Source: `TRANSCRIPTS_YC_ROOT_ACCESS.md:1790`

**10. Mixture-of-agents reduces hallucination vs. single-model responses.**
"For hard problems: send query to all frontier models simultaneously (layer 1). Each model reasons independently and produces output. Layer 2 aggregator reads all outputs, understands reasoning procedures, synthesizes a final result. Genspark claims this significantly reduces hallucination vs. single-model responses."
Source: `TRANSCRIPTS_DEEPLEARNINGAI.md:775`

---

## Summary: Top priority gaps to close in bad-research

Based on the diff, the highest-leverage items bad-research should consider adopting from HyperResearch (or verifying it already has equivalents for) are:

1. **Explicit 6-axis URL utility scorer** with a hard constraint (every atomic item ≥3 candidate URLs before low-utility extras are included) — `hyperresearch-2-width-sweep.md:113–130`
2. **Evidence redundancy audit** (derivative source clustering at the claim level, ≥60% overlap threshold) — `hyperresearch-2-width-sweep.md:200–215`
3. **Pre-flight period-pinned primary-source check** in step 8 (before corpus critic, not inside it) — `hyperresearch-8-corpus-critic.md:30–57`
4. **Synthesis pre-conflict-resolution gate** (orchestrator resolves inter-draft factual conflicts via Bash before spawning the tool-locked synthesizer) — `hyperresearch-11-synthesize.md:52–65`
5. **Readability recommender as JSON suggestion writer + orchestrator-selective-apply** (not auto-apply) with explicit apply/skip heuristics — `hyperresearch-16-readability-audit.md`
