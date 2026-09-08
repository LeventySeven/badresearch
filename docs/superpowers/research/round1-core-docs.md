# Round 1 — Core Docs Mining: Transferable Agentic Patterns
**Source vault:** `/Users/seventyleven/Desktop/researchfms/core/`
**Mined:** 06_AGENTIC_ARCHITECTURES.md, 07_LEAKED_PROMPTS.md, 08_STARTUP_AI_PIPELINES.md (grepped), 09_FRONTIER_AGENTIC_SYSTEMS.md, 12_AGENTIC_AI_DEEP.md, 13_AGENTIC_AI_ARCHITECTURE_MAP.md, 04_UNDER_THE_HOOD.md
**Date:** 2026-05-29

---

## Pattern Catalog (Ranked by Convergence Signal)

### P1 — Orchestrator-Worker Decomposition with Typed Roles
**Verdict: BORROW**
| Field | Detail |
|---|---|
| Source | `09_FRONTIER_AGENTIC_SYSTEMS.md:641-677`, `06_AGENTIC_ARCHITECTURES.md:791-833` |
| What it does | Opus-class model analyzes the query, develops search strategy, decomposes into 3-10 discrete tasks, spawns Sonnet-class workers in parallel (3-5 minimum), waits for completion, then synthesizes. A dedicated **Citation Agent** post-processes claim-to-source mappings as a final stage. |
| Why it works | Three factors explain 95% of performance variance: token usage (80%), tool-call count, model choice. Multi-agent used 15x more tokens than chat but scored 90.2% higher than single-agent Opus on internal research eval. Workers explore in isolation; the orchestrator never drowns in raw tool noise. |
| Deep-research mapping | Lead = query planner + synthesizer (extended thinking on); workers = parallel web-search + fetch agents; citation agent = post-synthesis grounding pass. Exact production blueprint. |
| Load-bearing quote | `06_AGENTIC_ARCHITECTURES.md:828` — *"Subagents store work in EXTERNAL systems and pass lightweight references → prevents information loss when context is truncated."* |

---

### P2 — Progressive Search Narrowing ("Short Broad → Long Specific")
**Verdict: BORROW**
| Field | Detail |
|---|---|
| Source | `09_FRONTIER_AGENTIC_SYSTEMS.md:657` |
| What it does | Workers start with short, high-recall queries; evaluate what's available; then issue progressively narrower follow-up queries targeting gaps. |
| Why it works | Mirrors expert human research. Avoids tunnel-vision from over-specified initial queries. Cut research time up to 90% in Anthropic's system when combined with parallel workers. |
| Deep-research mapping | Each worker sub-agent gets a research brief + gap-awareness prompt. Prompt explicitly instructs: start broad, assess coverage, then drill. |
| Convergent signal | Also present as Tavily's iterative gap-detection loop (`13_AGENTIC_AI_ARCHITECTURE_MAP.md:364-370`): define → gather → distill → decide if complete or produce follow-up queries → repeat. |

---

### P3 — Reflections-Only Context (Linear Token Growth)
**Verdict: BORROW**
| Field | Detail |
|---|---|
| Source | `08_STARTUP_AI_PIPELINES.md:2604-2620`, `13_AGENTIC_AI_ARCHITECTURE_MAP.md:370` |
| What it does | Between research iterations, only distilled reflections (compressed insights) persist in context. Raw source documents are dropped and re-injected only at final synthesis. |
| Why it works | Token cost is `n×m` instead of `n×m×(m+1)/2`. Tavily measured **66% token reduction** vs Open Deep Research with no accuracy loss. Prevents context overflow on long-horizon research. |
| Deep-research mapping | After each search wave, a cheap model distills findings into a structured reflection block. Raw HTML/docs are discarded. At synthesis, the orchestrator re-fetches the top-cited sources for citation grounding. |

---

### P4 — Pre-Assembled Evidence Injection (Citation Before Generation)
**Verdict: BORROW**
| Field | Detail |
|---|---|
| Source | `04_UNDER_THE_HOOD.md:162`, Perplexity leaked prompt `07_LEAKED_PROMPTS.md:1936-1944` |
| What it does | Citation markers, URLs, publication dates, and ranked excerpts are embedded directly into the prompt **before** the LLM generates any output. The LLM does not decide what to cite — it follows pre-assembled evidence with inline markers already mapped. |
| Why it works | Eliminates hallucination at the architecture level. *"Pre-training is like a no-notes-allowed exam; RAG is like an open-book exam."* (Srinivas, `04_UNDER_THE_HOOD.md:236`). Forces every sentence to trace to a retrieved source. |
| Deep-research mapping | Retrieval pipeline assembles a numbered evidence block before synthesis LLM call. Synthesis model instructed: cite every sentence using `[N]` format. |
| Load-bearing prompt fragment | `07_LEAKED_PROMPTS.md:1937-1940` (Perplexity Deep Research verbatim): *"You MUST cite search results used directly after each sentence it is used in. Cite using bracketed index: 'Ice is less dense than water[1][2].' Each index in its own bracket. No space between last word and citation. Cite up to three relevant sources per sentence."* |

---

### P5 — Hybrid BM25 + Dense Retrieval + Two-Stage Reranking
**Verdict: BORROW**
| Field | Detail |
|---|---|
| Source | `04_UNDER_THE_HOOD.md:144-162`, `08_STARTUP_AI_PIPELINES.md:1235-1240` |
| What it does | L1: simultaneous BM25 (lexical) + dense embedding (semantic) retrieval across 60+ candidates. L2: cross-encoder reranker narrows to top-K. Critical failsafe: if insufficient results meet threshold, discard entire result set and restart retrieval. |
| Why it works | Hybrid catches both keyword-specific and semantically-related documents. Cross-encoder reranking is 8.7pp NDCG@10 better than Cohere rerank-3.5 in the ZeroEntropy benchmark (`08_STARTUP_AI_PIPELINES.md:1357`). The failsafe gate prevents garbage answers. |
| Deep-research mapping | Use hybrid retrieval (Cohere embed + BM25) per query, two-pass reranking before context assembly. Apply the failsafe: if top-scored result < threshold, re-query with rephrased terms. |

---

### P6 — Source Trust Tiering + Freshness Filtering
**Verdict: BORROW**
| Field | Detail |
|---|---|
| Source | `08_STARTUP_AI_PIPELINES.md:1240`, `04_UNDER_THE_HOOD.md:128-144` |
| What it does | Sources are scored on a trust tier (low / medium / high / verified). For time-sensitive queries, temporal recency is a first-class filter. Perplexity's median citation age: 1.8 days vs Google's 28.6 days (16x fresher) for news/finance. |
| Why it works | Low-trust sources introduce hallucination risk even when highly ranked by BM25/dense scores. Freshness filtering prevents stale answers on fast-moving topics. |
| Deep-research mapping | Assign source tiers in retrieval config. Default `minimum_trust_tier: "medium"`. Expose a `freshness_window` parameter (e.g., 7 days for news queries). |

---

### P7 — Cross-Model Adversarial Review (Rubber Duck)
**Verdict: BORROW**
| Field | Detail |
|---|---|
| Source | `12_AGENTIC_AI_DEEP.md:769-777`, `12_AGENTIC_AI_DEEP.md:923` |
| What it does | A second model from a **different AI family** reviews orchestrator output at fixed checkpoints (post-plan, post-synthesis, pre-delivery). When orchestrator is Claude, reviewer is GPT-5.x (and vice versa). Triggers reactively when the system detects contradictions or low-confidence signals. |
| Why it works | Different model families have different failure modes and training biases. Pairing catches errors neither catches alone. GitHub measured **+4.8%** on hardest problems, closing **74.7% of the performance gap** to the best single model. Hallucination rate drops ~65% (Grok multi-agent: `12_AGENTIC_AI_DEEP.md:631`). |
| Deep-research mapping | Add a lightweight adversarial review pass after synthesis: feed the draft report + sources to a different-family model with a critique prompt. Flag unsupported claims, missing citations, internal contradictions. |

---

### P8 — Programmatic Tool Orchestration (Code as Context Compressor)
**Verdict: BORROW**
| Field | Detail |
|---|---|
| Source | `06_AGENTIC_ARCHITECTURES.md:834-848`, `06_AGENTIC_ARCHITECTURES.md:2332-2370` |
| What it does | Instead of N sequential tool calls (N inference passes, linear context growth), the model writes Python code that calls tools in a loop. Only the final `print()` output enters context — intermediate tool results are not added. |
| Why it works | Token usage dropped **37%** on complex research tasks (43,588 → 27,297 average). Eliminates 19+ inference passes when orchestrating 20+ tool calls. Internal knowledge retrieval improved from 25.6% to 28.5%. (`06_AGENTIC_ARCHITECTURES.md:2367`) |
| Deep-research mapping | For parallel multi-source fetches (e.g., fetching 8 URLs to extract claims), emit a single code-execution tool call rather than 8 sequential web-fetch calls. Only the distilled summary enters the synthesis context. |

---

### P9 — Structured Planning Recitation (todo.md Anti-Drift)
**Verdict: BORROW**
| Field | Detail |
|---|---|
| Source | `09_FRONTIER_AGENTIC_SYSTEMS.md:316`, `06_AGENTIC_ARCHITECTURES.md:2302` |
| What it does | Create and continuously update a structured plan file (todo.md or research plan) throughout the research session. Step-by-step checking pushes global objectives into the model's recent attention span. |
| Why it works | Mitigates "lost-in-the-middle" degradation — **65% of enterprise AI failures** attributed to context drift, not raw context exhaustion (`09_FRONTIER_AGENTIC_SYSTEMS.md:241`). Keeps the research brief in recent tokens even in 200K-context sessions. |
| Deep-research mapping | Orchestrator maintains a `research_plan.md` with sections, sub-questions, and status flags. Updated after each worker returns. Read at each synthesis step to ensure all sections are addressed. |
| Load-bearing quote | `06_AGENTIC_ARCHITECTURES.md:2302` — *"recites its objectives into the end of the context, pushing goals into the model's recent attention span and avoiding the 'lost-in-the-middle' problem."* |

---

### P10 — Memory No-Op Gate ("Will a Future Agent Act Better?")
**Verdict: BORROW**
| Field | Detail |
|---|---|
| Source | `06_AGENTIC_ARCHITECTURES.md:1021` |
| What it does | Before persisting any extracted insight to long-term memory, apply a single-question quality gate: *"Will a future agent plausibly act better because of what I write here?"* Only write if yes. Used in Codex CLI's 570-line memory extraction prompt with 8 parallel mini-model jobs. |
| Why it works | Prevents memory pollution with low-value observations. Maintains the signal density of the persistent memory store. Also produces `skills/<name>/` (reusable research procedures) and `rollout_summaries/` for cross-session learning. |
| Deep-research mapping | After each research run, extract high-value findings, source credibility signals, and effective query patterns. Gate each with the no-op check. Persist to `research_memory.md` and `query_skills/`. |

---

### P11 — Coordinator Mode (Pure Management Layer, No Direct Work)
**Verdict: BORROW**
| Field | Detail |
|---|---|
| Source | `06_AGENTIC_ARCHITECTURES.md:1786-1793`, `12_AGENTIC_AI_DEEP.md:442` |
| What it does | When in coordinator/orchestrator mode, the lead model's tool pool is **reduced** to coordination-only tools — no Bash, no file read/write, no web search. Its sole function: decompose, dispatch, receive summaries, synthesize. Workers do all execution. Codex CLI orchestrator prompt verbatim: *"Do not perform the actual work while they are working."* (`06_AGENTIC_ARCHITECTURES.md:1057`) |
| Why it works | Prevents the orchestrator from being distracted into doing research itself while workers are running. Enforces clean separation of responsibilities. Tool-pool restriction is a hard architectural guarantee, not a prompt suggestion. |
| Deep-research mapping | Lead model gets tools: `spawn_worker`, `wait_worker`, `read_worker_output`, `write_plan`, `synthesize`. Remove `web_search` and `fetch_url` from its tool schema entirely. |

---

### P12 — Four-Phase Coordinator Cycle with VERDICT Verification
**Verdict: NICE-TO-HAVE**
| Field | Detail |
|---|---|
| Source | `06_AGENTIC_ARCHITECTURES.md:1786-1792` |
| What it does | (1) Research — workers investigate in parallel; (2) Synthesis — coordinator crafts a spec with file/source paths and line numbers; (3) Implementation — workers execute targeted changes per spec; (4) Verification — adversarial proof, not existence checking. VERDICT system explicitly tries to disprove the answer, not just confirm it. |
| Why it works | Adversarial verification is architecturally different from "did we answer everything?" It forces the model to find counter-evidence and contradicting sources before finalizing. |
| Deep-research mapping | Add a VERDICT stage after synthesis: a separate agent is given the draft report and instructed to find sources that contradict it. Contradictions surface as revision tasks. |

---

## Prompt Fragments Worth Lifting Verbatim

**1. Orchestrator delegation rule** (`06_AGENTIC_ARCHITECTURES.md:1057`):
```
"Prefer multiple sub-agents to parallelize your work. Time is a constraint.
When you have a plan with multiple steps, process them in parallel by spawning
one agent per step. Your only role becomes to coordinate them.
Do not perform the actual work while they are working."
```

**2. Perplexity citation enforcement** (`07_LEAKED_PROMPTS.md:1937-1944`):
```xml
<citations>
- You MUST cite search results used directly after each sentence it is used in.
- Cite using bracketed index: "Ice is less dense than water[1][2]."
- Each index in its own bracket. No space between last word and citation.
- Cite up to three relevant sources per sentence.
- Never include a References section at the end. Sources displayed separately to user.
- Do not produce copyrighted material verbatim.
- If search results are empty or unhelpful, answer with existing knowledge.
</citations>
```

**3. Perplexity planning rules** (`07_LEAKED_PROMPTS.md:1976-1990`):
```xml
<planning_rules>
- Always break it down into multiple steps
- Assess the different sources and whether they are useful for any steps needed
- Create the best report that weighs all the evidence from the sources
- Remember to verbalize your plan in a way that users can follow along
- When referencing sources during planning, refer to them by index with brackets
- As a final thinking step, review planned report structure and ensure it completely answers the query
- You must keep thinking until you are prepared to write a 10,000 word report
</planning_rules>
```

**4. Sub-agent task spec discipline** (`09_FRONTIER_AGENTIC_SYSTEMS.md:655`):
```
"Short instructions like 'research the semiconductor shortage' often were vague
enough that subagents misinterpreted the task or performed the exact same
searches as other agents."
```
→ Each worker task must include: (a) specific question to answer, (b) search scope boundaries, (c) output format spec, (d) what NOT to search (to prevent duplicates with sibling workers).

**5. Parallel tool call enforcement** (`12_AGENTIC_AI_DEEP.md:529-532`):
```xml
<maximize_parallel_tool_calls>
Multiple INDEPENDENT operations MUST be parallel.
</maximize_parallel_tool_calls>
```

**6. Memory quality gate** (`06_AGENTIC_ARCHITECTURES.md:1021`):
```
No-op gate: "Will a future agent plausibly act better because of what I write here?"
```

---

## TL;DR (5 sentences)

Every top deep-research system has converged on the same core architecture: an Opus-class orchestrator that only plans and coordinates (never searches directly), spawning 3-10 typed Sonnet-class workers that fan out in parallel with narrow, progressively-narrowing search briefs. The single largest quality lever (explaining 80% of performance variance in Anthropic's own research eval) is token budget — more search = better answers, and reflections-only context propagation is the key to keeping that affordable (66% token reduction, linear not quadratic cost growth). All production systems pre-assemble evidence with citation markers before the synthesis LLM call, making hallucination prevention an architectural constraint rather than a hope. Cross-model adversarial review (a second model from a different family) is the cheapest quality multiplier — closing 74.7% of the gap to the best single model at minimal marginal cost. The five patterns that appear across three or more independent systems (orchestrator-worker, parallel progressive search, citation-before-generation, reflections-only context, and adversarial verification) are the non-negotiable foundation; the rest are tunable dials.

---

## Ranked TOP 12 Transferable Patterns

| Rank | Pattern | One-Line Why | Primary Source |
|---|---|---|---|
| 1 | Orchestrator-Worker Decomposition | +90.2% over single-agent; 3 factors explain 95% of variance | `09_FRONTIER_AGENTIC_SYSTEMS.md:641` |
| 2 | Pre-Assembled Evidence Injection | Eliminates hallucination architecturally; LLM follows evidence, doesn't invent citations | `04_UNDER_THE_HOOD.md:162` |
| 3 | Progressive Search Narrowing | Mirrors expert research; broad→narrow prevents tunnel-vision; cuts research time 90% | `09_FRONTIER_AGENTIC_SYSTEMS.md:657` |
| 4 | Reflections-Only Context | Linear token growth; 66% cost reduction; enables deep multi-wave research | `08_STARTUP_AI_PIPELINES.md:2617` |
| 5 | Hybrid BM25 + Dense + Reranking | Two-stage retrieval with failsafe gate; 8.7pp NDCG improvement vs Cohere | `04_UNDER_THE_HOOD.md:144` |
| 6 | Cross-Model Adversarial Review | +4.8% on hardest queries; closes 74.7% of perf gap; cheapest multi-agent add | `12_AGENTIC_AI_DEEP.md:771` |
| 7 | Coordinator Mode (No Direct Work) | Clean architectural separation; tool-pool restriction enforces it hard | `06_AGENTIC_ARCHITECTURES.md:1786` |
| 8 | Programmatic Tool Orchestration | 37% token reduction; collapses N inference passes to 1; stdout-only context | `06_AGENTIC_ARCHITECTURES.md:2336` |
| 9 | Source Trust Tiering + Freshness | Prevents low-quality/stale citations from entering synthesis | `08_STARTUP_AI_PIPELINES.md:1240` |
| 10 | Structured Planning Recitation | Anti-drift; keeps research brief in recent attention across 200K token sessions | `09_FRONTIER_AGENTIC_SYSTEMS.md:316` |
| 11 | Memory No-Op Gate | Prevents memory pollution; only persist what future agents can use | `06_AGENTIC_ARCHITECTURES.md:1021` |
| 12 | VERDICT Adversarial Verification | Actively tries to disprove the synthesis; surfaces contradictions before delivery | `06_AGENTIC_ARCHITECTURES.md:1791` |
