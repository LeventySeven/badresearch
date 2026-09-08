# Round 1 Competitor Deep-Dive — B: Grok Heavy, Claude Research, Nia Oracle, HyperResearch

_Source vault: `/Users/seventyleven/Desktop/researchfms/`_

---

## 1. Per-Product Summaries

### Anthropic Claude Research (multi-agent system)
A **parallel-orchestrator** system: Opus 4 LeadResearcher plans and spawns 3–5 (up to 10+) Sonnet 4 SubAgents in parallel batches; each subagent runs isolated in its own context, performs 3+ parallel tool calls, returns only a typed `SubAgentReport` to the orchestrator. A separate Haiku-class CitationAgent does the final claim-attribution pass. Key number: multi-agent Opus 4 + Sonnet 4 workers outperformed single-agent Opus 4 by **+90.2%** on Anthropic's internal eval; token use explains **80% of performance variance**; system uses **~15× more tokens** than a single chat interaction. Core weakness: **batches are sequential** — the orchestrator waits for all subagents in a batch before spawning the next, so inter-batch latency is serialized.
- Source: `teardowns/CLAUDE_RESEARCH.md` lines 3, 40, 54–58, 66–72, 88, 100, 351–361

### Grok 4 Heavy (xAI parallel-instance debate ensemble)
Not a sub-agent architecture: **N full Grok 4 instances** (rumored N ∈ {8, 16, 32} depending on query tier) each receive the same query, each independently use the full tool set (web_search, x_search, code_execution, image understanding), then output candidate answers that enter a **debate-then-judge aggregation** (not majority vote — instances see each other's answers, may revise, a judge model synthesizes). Citation format is a render-component primitive (`<grok:render type="render_inline_citation">`), not markdown. Grok's unique moat is X firehose (~68M English tweets/day) as a native parallel research surface. Weaknesses: API does **not** expose Heavy mode; multi-agent API blocks custom tools; reasoning verbosity inflates token cost (61M tokens vs ~35M median at eval).
- Source: `teardowns/GROK_HEAVY.md` lines 38–68, 145–151, 463–501; `teardowns/GROK_420_AGENTIC.md` lines 600–650, 926–934

### Nia Oracle / deep-search mode
Nia's **deep-search mode is not their own pipeline** — it is a thin proxy to Exa.ai `/research/v1` running OpenAI GPT-4, confirmed by 8+ prompt-injection probes leaking Exa's verbatim system prompt. Oracle itself is a **JSON-action ReAct loop** (not native Anthropic tool-use) running inside OpenCode-in-Daytona micro-sandbox with an 8-tool registry; it runs Anthropic models but bypasses the native tool-use layer. Nia's genuine architectural contribution is its **retrieval stack**: hybrid TurboPuffer vector+BM25 (α=0.7), two-stage fusion with Cohere cross-encoder rerank, L2 semantic-LSH cache shared across tenants, and AST-headers-in-chunks (tree-sitter call-graph + control-flow prepended as natural-language text before embedding). Nia does zero verification: the rerank cache is broken (0 hits / 133 misses observed), deep-search outsources to Exa, no contradiction detection.
- Source: `teardowns/NIA.md` lines 8, 22–34, 695–806, 890–944, 1054–1084

### HyperResearch (bad-research's own prior art)
A **16-stage Claude Code skill pipeline**: Opus orchestrator drives the state machine, spawning Sonnet/Haiku subagents at well-defined fan-out points (10–12 fetchers in wave 1, 2 parallel loci-analysts, up to 6 parallel depth-investigators, 3 parallel draft-orchestrators, all in a single message for true parallelism). Unique pattern: **skill-as-pipeline-stage** defeats context-rot by loading each stage fresh into context via the `Skill` tool rather than keeping a 1,200-line monolith (documented 100%-of-runs failure mode with the monolith). State lives on disk, not in context. **Patch-not-regenerate invariant**: post-synthesis modifications are surgical `Edit` hunks only, tool-locked to `[Read, Edit]`. Evidence redundancy audit flags derivative sources (>60% quoted_support overlap). Four adversarial search lenses at width-sweep; four critics post-draft.
- Source: `teardowns/HYPERRESEARCH.md` lines 15–31, 43–302, 645–785

---

## 2. Ranked Must-Steal Patterns

### Tier 1 — Critical (steal immediately)

**1. Typed orchestrator-worker interface contract (Anthropic)**
Every SubAgentTask carries four typed fields: objective, output_format, tools/sources to use, task boundaries. This is not free-text delegation — it is a formal interface that prevents duplicated work, prevents unbounded searching, and allows the orchestrator to plan synthesis before results return. The +90.2% eval gain flows directly from this discipline.
- Source: `teardowns/CLAUDE_RESEARCH.md` lines 69, 77–85, 276

**2. Two-level parallelism: orchestrator→workers AND within-worker parallel tool calls (Anthropic)**
Subagents call 3+ tools in parallel (Claude API parallel-tool-call feature). This means a 3-subagent batch is effectively 9+ simultaneous web fetches. Most systems parallelize at only one level.
- Source: `teardowns/CLAUDE_RESEARCH.md` lines 171, 245

**3. Asymmetric model assignment: Opus at coordination, Sonnet at work layer (Anthropic)**
Upgrading workers Sonnet 3.7 → Sonnet 4 is "a larger gain than doubling the token budget on Sonnet 3.7." Concentrate reasoning cost at the orchestrator; distribute cheaper models where work is embarrassingly parallel.
- Source: `teardowns/CLAUDE_RESEARCH.md` lines 96–102

**4. Skill-as-pipeline-stage / context-rot prevention (HyperResearch)**
Loading each stage as a fresh skill call + keeping only a thin router + TodoWrite list in hot context, with canonical artifacts on disk. Documented failure rate of 100% for monolithic 1,200-line prompt across runs before this fix.
- Source: `teardowns/HYPERRESEARCH.md` lines 23–25, 62–66

**5. Four adversarial search lenses + minimum 5 adversarial searches at width-sweep (HyperResearch)**
Lens A (breadth), B (citation-chain depth), C (adversarial/contrarian — "criticism of X", "why X doesn't work"), D (period-pinned primary sources). Most competitors do only Lens A. The dialectic critic scores against one-sided coverage.
- Source: `teardowns/HYPERRESEARCH.md` lines 126–131

**6. Triple-draft ensemble with differentiated analytical angles (HyperResearch)**
Draft A = strongest-thesis; Draft B = steelman-contrarian; Draft C = synthesis-reconciler. Written from *curated, differentiated* source lists by separate Opus subagents, then merged by a fresh tool-locked Opus synthesizer. Beats single-draft generation; the orchestrator resolves factual conflicts before spawning the synthesizer.
- Source: `teardowns/HYPERRESEARCH.md` lines 281–301

### Tier 2 — High Value

**7. External memory + checkpointing across subagent batches (Anthropic)**
Orchestrator writes summarized phase results to external memory; fresh subagent batches in round 2+ get clean contexts but inherit the memory state. Enables research beyond any single context window.
- Source: `teardowns/CLAUDE_RESEARCH.md` lines 172, 328–334

**8. Debate-then-judge aggregation, not majority vote (Grok Heavy)**
Instances see each other's reasoning, can revise, a judge synthesizes. This is productionized multi-agent debate (Du et al. 2023). Better than voting because the judge can identify load-bearing disagreements and surface them explicitly to the user.
- Source: `teardowns/GROK_HEAVY.md` lines 46–66, 125–133

**9. Evidence redundancy audit (HyperResearch)**
Sources sharing >60% `quoted_support` passages are tagged `derivative-of`. Independent source count is re-checked after dedup; if an atomic item's independent count drops below 2, a Wave 3 fetch is triggered. Prevents "N sources that are really 1 source in N outfits."
- Source: `teardowns/HYPERRESEARCH.md` lines 150

**10. Committed-position requirement on depth investigators (HyperResearch)**
Every depth-investigator's interim note MUST end with `## Committed position` — a forced stance with confidence calibration and "what evidence would change your mind." Descriptive-only endings are defective and trigger re-spawn. Forces synthesis over paraphrase.
- Source: `teardowns/HYPERRESEARCH.md` lines 207–213

**11. Effort-scaling tier contract (Anthropic + HyperResearch)**
Simple queries: 1 subagent, 3–10 tool calls. Complex: 3–5 subagents, multi-round. Deep-dive: 10+ subagents. HyperResearch has light/full tiers with "when uncertain tier up." Without this, the system wastes token budget on trivial queries or under-invests on hard ones.
- Source: `teardowns/CLAUDE_RESEARCH.md` lines 188, 211–215; `teardowns/HYPERRESEARCH.md` lines 47–56

**12. Wikipedia-as-source-hub rule (HyperResearch)**
Include Wikipedia URLs for citation-chain discovery, extract their references into Wave 2, but never cite Wikipedia in the final report. Converts a low-authority source into a high-value reference graph.
- Source: `teardowns/HYPERRESEARCH.md` line 134

---

## 3. Patterns Notably Worse Than a Parallel Adversarial Pipeline

- **Nia's deep-search is outsourced to Exa/GPT-4.** It is a ~150-line polling wrapper around `api.exa.ai/research/v1`. No internal retrieval, no contradiction detection, no adversarial coverage. The rerank cache is broken (0 cache hits ever observed). Source: `teardowns/NIA.md` lines 695–825, 532.

- **Grok DeepSearch cap is 10 tool calls per query** with a minimum 3 function calls. At max 10 calls this is architecturally shallower than any multi-round fan-out system. Source: `teardowns/GROK_420_AGENTIC.md` lines 642–644.

- **Claude Research's inter-batch execution is synchronous** — the LeadResearcher waits for all subagents in a batch before proceeding to the next batch. Anthropic acknowledges this as a known performance ceiling. An adversarial pipeline can overlap batch N+1 planning with batch N execution. Source: `teardowns/CLAUDE_RESEARCH.md` lines 88, 170.

- **Grok Heavy API exposure is zero** — Heavy mode is only on grok.com, not the API. Developers wanting N-instance ensemble must orchestrate it themselves. Source: `teardowns/GROK_HEAVY.md` lines 603.

- **Nia Oracle uses JSON-action ReAct instead of native tool-use**, adding a parsing layer that leaks the model's chain-of-thought onto the wire and breaks when the model fails to emit valid action JSON. Source: `teardowns/NIA.md` lines 1060–1078.

---

## 4. File Written

`/Users/seventyleven/Desktop/badresearch/docs/superpowers/research/round1-competitors-B.md`
