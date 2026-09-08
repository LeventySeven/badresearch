# Super-Skill Synthesis — Round 1 → Round 2 Plan

Goal: make `bad-research` (HYPERRESEARCH V8) measurably better than Perplexity DR, OpenAI DR,
Gemini DR, Grok DR, Claude/Anthropic DR, Nia Oracle, and HyperResearch — while keeping a
**simple operator surface** ("deep core, simple surface"). No overkill: simplest + most efficient
design that preserves our adversarial edge.

Round-1 evidence files (all cited):
- `round1-current-state.md` — what V8 already does + known gaps
- `round1-competitors-A.md` — Perplexity / OpenAI / Gemini DR
- `round1-competitors-B.md` — Grok / Claude / Nia / HyperResearch
- `round1-core-docs.md` — convergent patterns from leaked-prompt + architecture corpus
- `round1-borrowable.md` — broad teardown sweep (24 non-DR agentic products)
- `round1-hyperresearch.md` — HyperResearch sibling diff + transcript principles

---

## 1. Current state of V8 (baseline)

22-stage tier-adaptive pipeline (light/full), keyless, compaction-resistant (multi-skill chain),
disk-recoverable. Already has: 10–12 parallel fetchers + 4-lens search planning
(breadth/depth/adversarial/period-pinned); contradiction graph; 2 loci analysts w/ dynamic source
budgets; K depth investigators; triple-draft ensemble → fresh synthesizer; 4-critic parallel
fan-out; grader loop (judge→patch→re-judge ≤3); fresh-context cold reviewer; byte-identity + NLI
citation verification; 2 deterministic ship gates (uncited, recitation). Entry: `/bad-research
<q>` + `--effort/--max-tokens/--auto`; ≤3 clarifying Qs + plan-gate.

**We are already architecturally ahead** of every named competitor on adversarial verification,
parallel depth, and contradiction handling. The win is in (a) closing our own known gaps, (b)
absorbing a short list of genuinely-missing mechanisms, and (c) SIMPLIFYING.

### Known gaps (our own plans/eval)
- G1. Gate false positives from formatting artifacts (57/31/57 blocks) — `IMPROVE.md:11-24` (fix A-2)
- G2. Standalone `uncited-gate` crash outside Claude Code — `IMPROVE.md:26-36` (A-3)
- G3. **No golden-set eval corpus** (only 8 stubs; no per-step regression) — `ENHANCEMENT_PLAN.md:27-28` (E1, P0)
- G4. NLI entailment not in default ship path (checks citation EXISTS, not SUPPORTS) — `IMPROVE.md:48-57` (A-4)
- G5. Ungrounded draft → iterative gate-block loop (q2 stall) — `IMPROVE.md:60-72` (A-1)
- G6. Grader uses 0–1 float scores (Arize anti-pattern) — `ENHANCEMENT_PLAN.md:29-30` (E2)
- G7. **`ClaudeCodeReranker` is a STUB** (NotImplementedError; identity fallback) — `KR-1-removal.md:103-107`
- G8. URL→content cache absent (re-hits network for same URL) — `ENHANCEMENT_PLAN.md:75-77`

---

## 2. Consolidated steal-list (deduped, mapped, verdicted)

Legend: **STEAL** = clear win we lack; **UPGRADE** = we have a weaker version; **HAVE** = already
covered; **SKIP** = infeasible (keyless/Claude-Code-only) or not worth complexity.

| # | Pattern | Source(s) | Maps to | Verdict |
|---|---------|-----------|---------|---------|
| P1 | **Line-level citation grounding** `【ref†L42-L58】` + `web.find` regex span extraction | OpenAI DR; Perplexity inline | citation-verifier 11.5, grounding, gates → kills G1/G4 | **STEAL (highest leverage)** |
| P2 | **Pre-assembled evidence injection** (citation markers BEFORE synthesis = architectural anti-hallucination) | core-docs 04; convergent | synthesizer 11, draft 10 → fixes G5 | **STEAL** |
| P3 | **Keyless hybrid retrieval + rerank** (BM25+dense+RRF, LLM two-pass URL rerank, failsafe restart) | Firecrawl, Exa/Tavily/Glean, Perplexity 3-level | reranker stub → fixes G7 | **STEAL** (must be keyless) |
| P4 | **Reflections-only context** (drop raw sources between iters, re-inject at synthesis; ~66% token cut) | core-docs 08; Tavily | orchestration, depth investigators | **UPGRADE (efficiency)** |
| P5 | **Dual-ledger re-plan on stall** (facts+plan ledger, structured "what failed + revised plan") | Magentic-One | grader loop 12.5 → fixes G5 loop | **UPGRADE** |
| P6 | **Debate-then-judge / Elo tournament for contested loci** (instances revise after seeing peers) | Grok Heavy, AI Co-Scientist | loci 4 / depth 5 / reconcile 6 | **UPGRADE (selective)** |
| P7 | **Multi-mode critic + assumption decomposition + meta-review** (decontextualize each claim; recurring-failure feedback to patcher) | AI Co-Scientist | critics 12 → patcher 14 | **UPGRADE** |
| P8 | **Golden-set eval + LLM-judge w/ integer rubric (not 0–1 float) + DSPy-style offline prompt opt** | DRACO, Anthropic eval, Genspark, DSPy | calibration → fixes G3/G6 | **STEAL (P0 keystone)** |
| P9 | **6-axis URL utility scorer + evidence-redundancy audit + Wikipedia-as-hub** | HyperResearch sibling | width-sweep 2 | **UPGRADE (verify parity)** |
| P10 | **Strategic direction-switch + query expansion (multi-phrasing)** | Perplexity | search planning | **UPGRADE (cheap prompt win)** |
| P11 | **Two-stage host/worker split** (cheap clarify → expensive execute) | OpenAI | clarify 0.5 / router 1.5 | **HAVE (verify)** |
| P12 | **User-editable plan gate** | Gemini | plan-gate 1.6 | **HAVE** |
| P13 | **Prompt-injection / BrowseSafe classifier** on fetched content | Perplexity | fetchers/browse | **NICE-TO-HAVE (security)** |
| P14 | **Cross-model adversarial review** (different model family reviews draft) | core-docs 12 | critics | **SKIP? (keyless → likely infeasible; assess in R2)** |
| P15 | **Programmatic tool orchestration** (model writes code to batch tools; stdout-only) | core-docs 06 | orchestration | **ASSESS (may not fit subagent model)** |
| P16 | **External memory / cross-session compounding vault** | Anthropic, Manus | vault | **HAVE** |

### Transcript principles (design north-stars)
- The **verifier** is the binding constraint on research-agent quality (A16Z). → our edge; double down.
- **Context-assembly pipeline is the moat**, not the model. → invest in retrieval/grounding (P3/P2).
- Inline **per-sentence citations** build the most trust (Perplexity). → P1.
- Without **new external grounding**, outputs converge to a stationary distribution. → keep fetching NEW (anti-redundancy P9).
- **Mixture-of-models** reduces hallucination. → relevant to P14 feasibility.
- Agents **don't ask for clarification** when uncertain (specification gaming). → our 0.5 clarifier is a differentiator; keep sharp.

---

## 3. The SIMPLIFY mandate (user-critical)

User stressed: "as simple as it can be… no overkill, no workarounds, simplest + most efficient in
every way." We have 22 stages across ~24 skill files and FOUR distinct adversarial passes
(4-critic fan-out, grader loop, corpus-critic, fresh-review). Round 2 must include a
**consolidation audit**: which stages are genuinely load-bearing, what overlaps, what can merge
without losing the adversarial edge, and how to keep the surface one-command-simple. Simplification
is a first-class deliverable, not an afterthought.

---

## 4. Round 2 — targeted deep-dives (launch in parallel)

Each agent reads the relevant Round-1 file(s) AND our actual implementation, and returns an
*implementable design fragment* (not just more notes).

- **R2-1 Citation grounding** (P1+P2): extract OpenAI line-level + `web.find` mechanics + Perplexity
  inline; design a keyless line-anchored grounding upgrade that kills gate false-positives (G1) and
  puts support-checking/NLI in the default path (G4/G5). Read our 11.5 + grounding + gate code.
- **R2-2 Retrieval/rerank** (P3+P9+G7/G8): design a keyless hybrid retrieval + reranker to fill the
  stub; URL utility scorer + redundancy audit + content cache. Read funnel/retrieval/browse + the stub.
- **R2-3 Efficiency/orchestration** (P4+P15+economics): reflections-only context, token-budget-as-
  quality-lever, asymmetric tiering, batch pipelining (vs Anthropic synchronous-batch limit). Read
  pipeline orchestration. Output: token cuts without depth loss.
- **R2-4 Verification + eval harness** (P5+P6+P7+P8+P14): dual-ledger re-plan, debate/Elo for
  contested loci, multi-mode critic, golden-set + integer-rubric judge + offline prompt opt; assess
  cross-model feasibility under keyless. Read critics/grader/calibration.
- **R2-5 SIMPLIFY/consolidation map**: read ALL ~24 skill files in full + router; produce stage
  dependency graph, overlap analysis among the 4 adversarial passes, and a minimal-but-equivalent
  pipeline + simplest operator surface. The "no overkill" deliverable.

Round 3 (if needed): reconcile R2 fragments into a single coherent upgrade spec + sequencing.
