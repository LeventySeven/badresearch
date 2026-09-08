# Round 1 — Borrowable Patterns from Non-Deep-Research Agentic Products

**Date:** 2026-05-29  
**Corpus swept:** 221 teardowns in `/Users/seventyleven/Desktop/researchfms/teardowns/`.  
**Sampled:** ~22 highest-signal teardowns (Cursor, Devin, Manus, Claude Code, Claude Research, OpenAI Deep Research, Gemini Deep Research, Grok Heavy, Exa, Tavily, LangGraph, Magentic-One, OpenAI Agents SDK, Replit Agent, OpenHands, AI Co-Scientist, LlamaIndex, Supermemory, DSPy, NotebookLM, DeepWiki, Firecrawl). Selection criterion: named agentic product with known RE depth + mechanism terms in name/description.

---

## Ranked Borrowable-Pattern Catalog

### TIER 1 — HIGH borrow value

---

**P1 | Dedicated CitationAgent (post-processor) | Anthropic Claude Research (`CLAUDE_RESEARCH.md:98,280`) | HIGH**

A *separate, cheap model pass* (inferred Haiku-class) runs after synthesis, attributing every claim in the final report to a source URL. The orchestrator never tries to manage citations inline — they are the CitationAgent's only job. Devin's DeepWiki runs the same pattern with `<cite repo="..." path="..." start="..." end="..." />` tags mandatory on every sentence, enforced at render time (`DEVIN.md:316-333`). OpenAI Deep Research uses `【turnXsearchY†L42-L58】` line-level grounding baked into the inner-loop prompt (`OPENAI_DEEP_RESEARCH.md:370`). All three products converge on: **separate citation pass + mechanically enforced format + claim-level granularity**.  
**Upgrade target:** bad-research citation verification stage. Replace opportunistic inline citation with a dedicated post-synthesis CitationAgent that verifies every claim against the fetched corpus, assigns source+span, and rejects/flags ungrounded claims.

---

**P2 | Asymmetric Orchestrator/Worker Model Assignment | Claude Research (`CLAUDE_RESEARCH.md:96-100`); Factory AI (`FACTORY_AI.md:272`) | HIGH**

Expensive frontier model (Opus 4) at the orchestration/synthesis layer; cheaper model (Sonnet 4) at parallel worker/fetch layer; cheapest (Haiku) at pure structured-output tasks (citations, classification). Claude Research's blog: "multi-agent system with Opus 4 as lead outperformed single-agent Opus 4 by 90.2%." Factory AI: "strong orchestrator + cheaper worker + strong validator" is the recommended cost/quality tradeoff with separate model knobs per tier. Convergence in Magentic-One and Grok Heavy as well.  
**Upgrade target:** bad-research orchestration. Introduce explicit model-tier assignments — Opus/Sonnet for orchestrator+critics, Sonnet for fetchers/depth investigators, Haiku for classification/citation/grading sub-tasks.

---

**P3 | Parallel Fan-out with External Memory for Cross-Batch Continuity | Claude Research (`CLAUDE_RESEARCH.md:172,207-208,324-333`); Magentic-One (`MAGENTIC_ONE.md:887-908`) | HIGH**

Parallel subagents return findings to an orchestrator that writes a structured `memory_write(key, value)` store between batches. Fresh subagent contexts in round 2 can read the accumulated state without inheriting the full prior context. Magentic-One formalizes this as Task Ledger (persistent facts + plan) + Progress Ledger (per-turn). Claude Research blog verbatim: "Agents summarize completed phases and store essential information in external memory; can spawn fresh subagents with clean contexts while maintaining continuity." Convergent in Manus (`todo.md` durable checklist), Replit Agent (`replit.md` auto-maintained project memory).  
**Upgrade target:** bad-research parallel fetching and loci investigation stages. Implement a structured external memory store (key → value) that survives across agent batches, removing the need to carry full prior context into every new worker.

---

**P4 | LLM-as-Judge Critic with Multi-Mode Review | AI Co-Scientist (`AI_CO_SCIENTIST.md:120-127`); OpenHands (`OPENHANDS.md:128,154`) | HIGH**

AI Co-Scientist runs six distinct Reflection review modes — initial (no tools), full (web-grounded), deep-verification (assumption decomposition), observation, tournament, recurrent — against each hypothesis before it advances. OpenHands ships a `CriticMixin` that wraps every `ActionEvent` with an optional LLM-as-judge `critic_result` before emission. The Co-Scientist deep-verification mode is the most transferable: decompose the subject into constituent assumptions, decontextualize each, rate independently. The Meta-review loop then feeds recurring failure patterns back into all agent prompts without fine-tuning.  
**Upgrade target:** bad-research 4-critic stage. Expand critic specializations to include an assumption-decomposition critic (decontextualizes claims into sub-assumptions and checks each independently) and a meta-critic that accumulates cross-run review patterns to sharpen future critic prompts.

---

**P5 | Hybrid Retrieval: Dense + Sparse + Cross-Encoder Rerank | Exa (`EXA.md:27,297`); Tavily (`TAVILY.md:671,701-755`); Glean (`GLEAN.md:214-220`) | HIGH — convergent across 3+ products**

Exa: BM25 (WAND-style) + neural IVF embeddings → Reciprocal Rank Fusion (k=60) → cross-encoder Highlights scorer in <100ms. Tavily `TavilyHybridClient`: MongoDB vector search (Cohere `embed-english-v3.0`) + Tavily web results → Cohere `rerank-english-v3.0` cross-encoder on combined candidate pool — final ranking entirely from the reranker's `relevance_score`. Glean: semantic + BM25 + recency + authority + link structure + Personal Graph signals. The convergence: **hybrid dense+sparse fusion followed by a cross-encoder rerank pass** is the 2026 production standard for retrieval quality.  
**Upgrade target:** bad-research source retrieval and ranking. After URL collection, run a two-stage ranking: (1) BM25 + embedding cosine fusion via RRF, (2) cross-encoder rerank of top-40 candidates before fetching full pages.

---

**P6 | Contextualized Chunk Embedding (Document-Aware) | Perplexity Deep (`PERPLEXITY_DEEP.md:718-729`); Supermemory (`SUPERMEMORY.md:123-132`) | HIGH**

Perplexity's `pplx-embed-context-v1`: input is `List[List[str]]` (chunks per document); chunk 3 of a document is embedded with context from chunks 1-2 and 4-N. Solves the "lost antecedent" problem where a chunk like "He then founded..." loses its referent from the prior chunk. Supermemory uses three embedding slots per chunk (primary, migration, Matryoshka nested) and two-level retrieval (coarse summary-embedding filter → fine chunk retrieval). Standard isolated-chunk embedding discards document context, hurting retrieval precision on long sources.  
**Upgrade target:** bad-research source processing. When splitting fetched pages into retrieval chunks, embed with document-level context (sliding window of adjacent chunks included in embedding call), not as isolated fragments.

---

**P7 | Plan-Gate with User-Editable Plan Before Execution | Gemini Deep Research (`GEMINI_DEEP_RESEARCH.md:42-66,186-211`); Devin (`DEVIN.md:18,42-60`); Replit Agent (`REPLIT_AGENT.md:228-244`) | HIGH — convergent across 3 products**

Gemini: emits a structured numbered research plan → user can edit, add/remove steps, reorder → only then executes. Devin: planning mode (read-only) → `<suggest_plan/>` gate → user approves → standard mode (edit). Replit Agent: Plan mode toggle. The hard checkpoint between planning and execution prevents over-fan-out, scope creep, and missing sub-topics from being baked into a multi-minute run that the user can't redirect. All three cite transparency and scope control as primary motivations.  
**Upgrade target:** bad-research query decomposition. Surface the decomposed sub-questions + research plan to the user before spawning fetchers, with an optional edit step. This costs one interaction round and prevents the most common failure mode (wrong scope).

---

**P8 | Dual-Ledger Re-plan on Stall (Facts + Plan, n_stalls Counter) | Magentic-One (`MAGENTIC_ONE.md:17-20,272-290,1037-1042`) | HIGH**

Two persistent ledgers: a Task Ledger (closed-book facts known/unknown + bullet plan) regenerated at task start and on every stall; a Progress Ledger (per-turn: what's been done, what next, is task complete). On stall (n_stalls counter), the orchestrator runs `PLAN_UPDATE_PROMPT` that explicitly identifies what went wrong and what prior mistakes to avoid, then emits a new plan. Magentic-UI adds `plan-learning`: top-k past plans retrieved via memory provider and reused/hinted for similar future tasks.  
**Upgrade target:** bad-research grader loop. When the grader rejects a synthesis round, generate a structured "what failed + revised plan" rather than re-running with the same approach. Track failure patterns across runs for plan-learning retrieval.

---

**P9 | Separate Planner Service with Event-Stream Injection | Manus (`MANUS.md:20,64,79,84-89,494-502`) | MED-HIGH**

Manus's Planner, Knowledge, and Datasource modules are upstream services that inject events into a shared event stream the agent LLM consumes — the agent never writes the plan, it reads it. Knowledge module injects best-practice snippets scoped to the current state (INFERRED: vector similarity over curated procedural recipe store). The "blackboard architecture" means any service can contribute to the agent's context without coupling to the agent's reasoning. This is architecturally distinct from having the agent plan itself.  
**Upgrade target:** bad-research orchestration. Separate the planning LLM call (which decomposes the query and schedules stages) from the execution agent context. The planner emits a structured plan artifact that each stage reads, enabling restarts without re-planning.

---

**P10 | LLM URL Reranker (Two-Pass, Multi-Entity Schema) | Firecrawl (`FIRECRAWL.md:818-852,977`) | MED**

Firecrawl's `/v1/extract` URL ranking: (1) `buildPreRerankPrompt` generates a 1-2 sentence description combining schema+query → feeds as context to Gemini-2.5-Pro LLM reranker with structured output schema (relevance score 0-10, reasoning, action: include/exclude). Two passes if >100 links remain after pass 1. Handles multi-entity extraction gracefully. Critically: URL-level TF cosine for cheap map endpoints, LLM reranker only where quality matters.  
**Upgrade target:** bad-research search planning. After initial URL collection, apply a lightweight LLM reranker pass on the URL+snippet candidates before fetching full pages, with a structured include/exclude schema. Tiered: fast cosine first, then LLM pass on top-N.

---

**P11 | Elo Tournament + Pairwise Debate for Ranking Competing Hypotheses | AI Co-Scientist (`AI_CO_SCIENTIST.md:53,150`) | MED**

A Ranking agent runs Elo-rated pairwise debates between competing hypotheses (structured prompt: "judge a scientific debate between two competing hypotheses, emit a winner"). The Proximity agent deduplicates via embedding cosine similarity (threshold ≥0.92) before sending to the tournament. The Evolution agent breeds new hypotheses from the top of the Elo leaderboard.  
**Upgrade target:** bad-research loci analysis and multi-draft synthesis. Apply pairwise debate ranking to competing draft positions on contested loci before committing to a synthesis stance. Flag positions with consistently low debate win-rate for deeper investigation.

---

**P12 | Structure-Aware Sentence/Paragraph Chunking (not Fixed-Token Windows) | NotebookLM (`NOTEBOOKLM.md:78-81`); Supermemory (`SUPERMEMORY.md:123`) | MED**

NotebookLM: `TailwindDocFragment` units are character-offset sentence/short-paragraph granularity (p50 67 chars, p90 371, max 680) — structure-aware segmentation from `LoadSource`, not fixed 200-token windows. Supermemory: AST-aware chunking via tree-sitter for code (entity boundaries), semantic boundary detection for prose. Both explicitly cite "coarse, structure-aware grounding" as superior to micro-chunking for citation precision.  
**Upgrade target:** bad-research source chunking for citation verification. Split fetched pages at sentence/paragraph boundaries with structural metadata (heading level, list depth) rather than fixed token windows, enabling finer-grained citation spans.

---

**P13 | Meta-Review Prompt Augmentation Without Fine-Tuning | AI Co-Scientist (`AI_CO_SCIENTIST.md:53,67,171-175`) | MED**

The Meta-review agent reads every review and debate transcript, identifies recurring failure patterns ("reviewers consistently miss blood-brain barrier permeability"), and appends findings to the next iteration's Reflection/Generation/Evolution agent prompts. "Enables feedback propagation and learning without back-propagation." The model is never fine-tuned; all self-improvement is in-context. Paper: "while only 90% of individual reviews might correctly identify a BBB issue, the meta-review ensures 100% of future reviews address it."  
**Upgrade target:** bad-research critic loop. Add a meta-critic pass that reads all four critic outputs, extracts recurring structural weaknesses, and prepends them to the patcher's instruction set for the next revision pass.

---

**P14 | Parallel-Instance Debate Ensemble for Contested Claims | Grok Heavy (`GROK_HEAVY.md:38-66,149`) | MED**

Grok Heavy spawns N independent full-model instances on the same query, each reasons and uses tools independently, then a judge model synthesizes (debate-then-judge, not voting). Capped at 3-5 debate rounds before judge decides. Addresses the accuracy problem on hard contested claims: "chance that at least one of N=16 instances gets it right approaches 99.97%."  
**Upgrade target:** bad-research contested loci handling. For loci rated high on uncertainty + disagreement scores, spawn 2-3 depth investigators with explicitly differentiated search angles (not the same queries), then run a judge pass to synthesize the competing evidence chains.

---

**P15 | DSPy MIPROv2 Minibatch Prompt Optimization Loop | DSPy (`DSPY.md:316-354,391`) | LOW-MED**

MIPROv2 uses Optuna TPE sampler + grounded proposer to auto-optimize per-predictor instructions and few-shot demonstrations. Minibatch eval (35 examples per trial) with full-eval checkpoint every 5 trials catches overfit candidates. `GroundedProposer` generates candidate instructions using scored prior attempts as context (`GenerateInstructionGivenAttempts`). Not immediately deployable, but the framework is available for optimizing bad-research's fixed prompt stages.  
**Upgrade target:** bad-research internal prompt calibration. Use DSPy MIPROv2 to optimize the prompt instructions for each fixed stage (critic prompts, synthesizer gates, grader rubric) against the RACE eval dataset.

---

## Convergence Table (patterns in 3+ products)

| Pattern | Products |
|---|---|
| Hybrid dense+sparse rerank | Exa, Tavily, Glean, DeepWiki |
| Citation-mandatory post-processing | Claude Research, Devin/DeepWiki, OpenAI DR |
| Plan-gate before execution | Gemini DR, Devin, Replit Agent, Magentic-One |
| Parallel fan-out + external memory | Claude Research, Magentic-One, Manus, Replit Agent |
| Asymmetric model tiering | Claude Research, Factory AI, Magentic-One, Grok Heavy |

---

## Source File Index

| Teardown | Path |
|---|---|
| Claude Research | `/Users/seventyleven/Desktop/researchfms/teardowns/CLAUDE_RESEARCH.md` |
| Devin | `/Users/seventyleven/Desktop/researchfms/teardowns/DEVIN.md` |
| Manus | `/Users/seventyleven/Desktop/researchfms/teardowns/MANUS.md` |
| Cursor | `/Users/seventyleven/Desktop/researchfms/teardowns/CURSOR.md` |
| Claude Code | `/Users/seventyleven/Desktop/researchfms/teardowns/CLAUDE_CODE.md` |
| Exa | `/Users/seventyleven/Desktop/researchfms/teardowns/EXA.md` |
| Tavily | `/Users/seventyleven/Desktop/researchfms/teardowns/TAVILY.md` |
| LangGraph | `/Users/seventyleven/Desktop/researchfms/teardowns/LANGGRAPH.md` |
| OpenAI Deep Research | `/Users/seventyleven/Desktop/researchfms/teardowns/OPENAI_DEEP_RESEARCH.md` |
| Gemini Deep Research | `/Users/seventyleven/Desktop/researchfms/teardowns/GEMINI_DEEP_RESEARCH.md` |
| Grok Heavy | `/Users/seventyleven/Desktop/researchfms/teardowns/GROK_HEAVY.md` |
| Magentic-One | `/Users/seventyleven/Desktop/researchfms/teardowns/MAGENTIC_ONE.md` |
| OpenAI Agents SDK | `/Users/seventyleven/Desktop/researchfms/teardowns/OPENAI_AGENTS_SDK.md` |
| Replit Agent | `/Users/seventyleven/Desktop/researchfms/teardowns/REPLIT_AGENT.md` |
| OpenHands | `/Users/seventyleven/Desktop/researchfms/teardowns/OPENHANDS.md` |
| AI Co-Scientist | `/Users/seventyleven/Desktop/researchfms/teardowns/AI_CO_SCIENTIST.md` |
| LlamaIndex | `/Users/seventyleven/Desktop/researchfms/teardowns/LLAMAINDEX.md` |
| Supermemory | `/Users/seventyleven/Desktop/researchfms/teardowns/SUPERMEMORY.md` |
| DSPy | `/Users/seventyleven/Desktop/researchfms/teardowns/DSPY.md` |
| NotebookLM | `/Users/seventyleven/Desktop/researchfms/teardowns/NOTEBOOKLM.md` |
| DeepWiki | `/Users/seventyleven/Desktop/researchfms/teardowns/DEEPWIKI.md` |
| Glean | `/Users/seventyleven/Desktop/researchfms/teardowns/GLEAN.md` |
| Firecrawl | `/Users/seventyleven/Desktop/researchfms/teardowns/FIRECRAWL.md` |
| Perplexity Deep | `/Users/seventyleven/Desktop/researchfms/teardowns/PERPLEXITY_DEEP.md` |
| Factory AI | `/Users/seventyleven/Desktop/researchfms/teardowns/FACTORY_AI.md` |
| HyperResearch product code | `/Users/seventyleven/Desktop/researchfms/products/HYPERRESEARCH_PRODUCT_CODE.md` |
