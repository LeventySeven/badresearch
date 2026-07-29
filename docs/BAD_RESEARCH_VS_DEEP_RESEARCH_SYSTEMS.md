# bad-research — everything, aligned to the deep-research field

**What this is:** the full architecture of **bad-research** (your product) set against every deep-research system reverse-engineered in `researchfms/teardowns/`: its fork parent **hyperresearch**, **Perplexity Deep Research**, **Grok DeepSearch/DeeperSearch/Heavy**, and the secondary column **OpenAI / Gemini / Claude Research**. Written 2026-07-01 from the actual source (`~/Desktop/badresearch/src`) and the teardowns, every constant cited to `path:line` (bad-research) or `TEARDOWN.md:line`.

**Core goal (the north star this doc is measured against):** bad-research is *the best research tool available as a Claude Code skill+CLI* — **install-and-go, fully keyless**, no third-party keys or subscriptions, SOTA-grounded research **right inside Claude Code** (just the host model + the `bad-research` skill + the `bad` CLI). The skill is the product; the CLI is its keyless deterministic toolbelt.

Companion docs: **`plans/2026-07-01-badresearch-sota-keyless.md`** (the implementation plan derived from §6 + §7 below — the actionable "what to build") · **`HEADLESS_BREAKAGE_AND_FIX.md`** (why it "breaks" run headless — an invocation-mode issue, not a code bug; keyless-correct usage is the skill, not the CLI).

---

## 0. The one-paragraph thesis

There are **two families** of deep-research architecture. **(A) Skill-over-disk-vault** — *hyperresearch* and *bad-research*: the Claude Code **host model IS the runtime**, the pipeline is a set of markdown "step skills" executed one at a time, all state lives on disk, and it is **keyless / zero-infra**. **(B) Hosted-loop-over-proprietary-index** — *Perplexity, Grok, OpenAI, Gemini*: a **trained/served model** runs a tool-loop over an **owned search index**, optimized for speed + coverage at scale, **keyed/proprietary**. bad-research's bet is that Family A, given a frontier **host** model + keyless search + a disciplined pipeline + **deterministic grounding gates**, reaches comparable *grounded* quality at **$0 marginal infra** — and it is the **only** system in either family with a $0 deterministic hallucination-catch layer. Its one genuine, refuted claim (that its funnel constants are "Perplexity's") is corrected in §7.

---

## 1. bad-research in one screen (the "everything" part)

**Primitive:** the research *pipeline itself* is the product, not a model call. It keeps hyperresearch's "**disk is memory, context is scratchpad**" spine (`docs/SPEC.md:25`) and replaces every paid seam (Tavily/Exa/Sonar/Firecrawl/Cohere/Browserbase/AgentQL/Browser-Use) with a keyless equivalent on **host model + local OSS + local CLIs** (`docs/INTERFACES_KEYLESS.md:9-19`).

**Keyless mechanism (the load-bearing inversion):** there is no server and no vendor key. Inference arrives through one `LLMProvider` seam; **in the skill path the Claude Code host model supplies all inference** (`llm/anthropic.py` is only the headless/calibration bridge). Web = orchestrator-invoked host **`WebSearch`** (primary) + **`ddgs`** fallback + **7 scholarly verticals** (arxiv/openalex/crossref/s2/europepmc/pubmed/wikipedia). Retrieval = **SQLite FTS5/BM25** + **host-model cross-encoder reranker** (Cohere-quality at $0), optional `[local]` bge+LanceDB dense lane. `bad doctor` proves keyless-ness (every `providers.py` row `requires_key=False`).

**Pipeline (FULL tier, `skills/bad-research.md:96`):**
```
0.5 clarify → 1 decompose → 1.5 query-router → 1.6 plan-gate → 2 width-sweep
 → 4 loci-analysis (4.0 contradiction graph) → 5 depth-investigation
 → 6 cross-locus-reconcile (6.5 orphan-tensions) → 8 corpus-critic
 → 10 triple-draft (10.0b evidence digest) → 11 synthesize → 11.5 citation-verifier
 → 12 critics(5 adversarial) → 13 gap-fetch → 12.5 grader → 14 patcher
 → 14.5 fresh-review → 15 polish → 16 readability (+uncited-gate +recitation)
```
Two shorter routes: **FAST** (bounded ReAct, `FAST_MAX_STEPS≤6`, replaces 2–14) and **ULTRAFAST** (plan → K≤6 parallel researchers → leader-only sectioned synthesis). Routing decided at **step 1.5** (`router.py::classify_route` → `fast|full`); `pipeline_tier="full"` is an honored floor `classify_route` never demotes.

**Model tiers** (`config.py:33-37`): `triage=claude-haiku-4-5` · `work=claude-sonnet-4-6` · `heavy=claude-opus-4-7`. `--cheap` demotes heavy→work; prompt-cache on by default (~10× on the stable prefix).

**The constants that ARE the product:**
- Retrieval (`retrieval/constants.py`): `ALPHA=0.7` · `RRF_K=60` · three-tier fusion `{≤3:0.75, ≤10:0.60, >10:0.40}` · `DEEP_RANK_PENALTY=0.005·(rank−10)` · source-type weights code 1.2/docs 1.0/paper 0.9/dataset 0.85 · **`RELEVANCE_GATE=0.70`** · **`RERETRIEVE_PASS_FRACTION=0.30`** · lexical cache 0.85 / cosine cache 0.92 · BM25 col weights 10/1/5/3 · neural-recall auto-on at 25 000 chunks.
- Funnel (`funnel/config.py`): full 100 queries / 4 providers / read-ceiling 80 · light 12/1/12 · dedup jaccard 0.60 · utility_max 18.
- Recitation (`quality/recitation.py`): `RECITATION_MAX_NGRAM=12` · `RECITATION_MAX_OVERLAP=0.50`.
- Grounding gate (`grounding/gate.py`): `CLAIM_QUOTE_OVERLAP_SKIP=0.8` · `SUPPORTED_FLOOR=0.70` · `PARTIAL_LOW=0.40`.

**The two things nobody else has:** (1) a **deterministic $0 grounding layer** — number/date-flip, negation-polarity-flip, and directional/antonym-flip caught mechanically, with a **blocking no-uncited-claim gate** + a **12-gram/0.50 recitation gate**; (2) a **per-claim grounding ledger as a shareable sidecar** (`bad grounding-surface`) — auditability no hosted tool exposes.

---

## 2. The one-screen comparison matrix

| Dimension | **bad-research** | hyperresearch (fork parent) | Perplexity DR | Grok DeepSearch/Heavy | OpenAI DR | Gemini DR | Claude Research |
|---|---|---|---|---|---|---|---|
| **Family** | A skill/vault, keyless | A skill/vault, keyless | B hosted loop | B hosted loop | B hosted loop | B hosted loop | B hosted loop |
| **Runtime** | CC host model | CC host model | served Sonar+ext | served grok-4.20 | served (o3 FT) | served Gemini | served Claude |
| **Pipeline** | 19-stage skill graph + fast/ultrafast | 16-stage skill graph, light/full | planner→writer ReAct | symmetric N-agent debate | single RL agent loop | plan→async executor | lead + subagents |
| **Parallelism** | staged fan-out + K≤6 ultrafast | staged fan-out (10-12/K≤6/3/4) | ≤3 queries/step (array) | agent_count 4 or 16 | none (1 agent) | async task pool | 3 (max 20) subagents |
| **Models** | haiku/sonnet/opus **tiers** | Opus write / Sonnet read (**role**) | `gpt-5.2` default + Sonar | one model × agent_count | early-o3 FT | Gemini + planner | Opus lead + Sonnet |
| **Web search** | host WebSearch + ddgs + 7 verticals | WebSearch + Exa (only key) | **own 200B-URL index** | **X firehose** + 3 web providers | Bing-class + browse | Google index | web + tools |
| **Retrieval** | FTS5/BM25 + host reranker; `[local]` dense; RRF k=60, α=0.7 | FTS5/BM25 only, no vector/rerank | BM25 ⊕ pplx-embed → rerank | RRF (collections RAG only) | n/a (live browse) | n/a | n/a |
| **Grounding** | **deterministic gates + NLI + uncited + recitation** | critics + lint (no uncited gate) | prompt-discipline only (**no verifier**) | char-span cites, no entailment | inline cites | inline cites | CitationAgent + neg-signal list |
| **Termination** | tier + degrade-order + short-circuit; fast ≤6 | tier gate + artifact exit criteria | **budget ∨ saturation ∨ satisfaction** | turns ∧ 200s ∧ tokens (**no agree metric**) | RL-learned stop | plan-bounded | lead decides |
| **Keyed?** | **keyless** | keyless (Exa optional) | fully keyed | fully keyed | fully keyed | fully keyed | fully keyed |
| **Cost/run** | host-model tokens only | $5-15 light / $60-120 full | ~$0.41/query | $0.19 (4) / $0.94 (16) | subscription | subscription | ~15× a chat |

---

## 3. Dimension-by-dimension alignment

### 3.1 Pipeline shape & the agentic loop
- **bad-research / hyperresearch** are the only two that are **not** a single tool-loop: they're a **staged skill graph** where each stage is a markdown skill loaded fresh (context-rot defense — hyperresearch's V7 single 1200-line prompt was compacted away in 100% of runs, `HYPERRESEARCH.md:23,1468`). Full-tier ≈ **30–50 subagent spawns** (`HYPERRESEARCH.md:1010`); bad-research adds 3 stages upstream lacks (0.5/1.5/1.6/11.5/14.5, +5th critic).
- **Perplexity** is a **two-system planner→writer ReAct** with a *CoT firewall*: the planner exhausts a ≤10-step budget (≤3 queries/step), then a **separate** writer sees only `(query, dedup'd evidence, prior answers)` — never the planner's raw thought (`PERPLEXITY_DEEP.md:3228-3230,3886`). "Never intermix tool calls with output text … constitutes a failure."
- **Grok** is **symmetric N-agent debate**: `agent_count∈{4,16}` spawns 1 leader + N-1 identical sub-agents; merge is **continuous `chatroom_send` function-turn injection**, not a final reduce; the leader alone emits render components; termination is turns ∧ 200 s ∧ tokens with **no agreement metric** (`GROK_HEAVY.md:1160,1850,1931`). DeepSearch/DeeperSearch/Heavy are **one model differentiated by one integer** — "marketing over a unified runtime."
- **OpenAI** is the opposite pole: **one end-to-end RL-trained agent** that *learned* browse-plan-backtrack-stop (the +RL delta is BrowseComp 51.5% vs o1 9.9%, uncloseable by prompting, `OPENAI_DEEP_RESEARCH.md:239-249`).
- **Gemini** uniquely front-loads a **user-editable plan + hard approval gate** before any browsing, then an async executor (`GEMINI_DEEP_RESEARCH.md:42,204-209`). bad-research's **step 1.6 plan-gate** is the same idea (interactive-only).
- **Claude Research** is **asymmetric lead/subagent**: an Opus lead emits N `run_blocking_subagent` blocks (default 3, max 20), each Sonnet worker in an isolated context returning only summaries; +90.2% over single-agent Opus at ~15× chat tokens (`CLAUDE_RESEARCH.md:66-72,100`). bad-research's **ultrafast route** (plan → K≤6 parallel researchers → leader synthesis) is the direct keyless analog.

**Read:** bad-research sits in Family A but has quietly imported Family-B loop ideas — Perplexity's bounded planner→writer (its FAST route), Claude's lead/subagent (its ULTRAFAST route), Gemini's plan-gate (1.6). That's the right cross-pollination.

### 3.2 Models & routing
- bad-research's **triage/work/heavy tiering** (haiku/sonnet/opus) is the most **cost-disciplined** of the field and the only one with an explicit `EFFORT_MAP` + `DEGRADE_ORDER` that cuts *tokens last*. hyperresearch routes by **role** (Opus writes/judges, Sonnet reads) with no tier gate on models. Perplexity is **caller-declarative** (`model` slug / `preset` / `models` fallback-chain up to 5) and concedes its DR *brain* to `openai/gpt-5.2` (`advanced` → `claude-opus-4.6`) — a striking admission that the value is the loop+index, not the model. Grok scales one model by `agent_count`. OpenAI is a single fine-tune.
- **The honest ceiling:** bad-research's quality is bounded by the **host frontier model's zero-shot tool-use** — which is exactly what Grok and OpenAI **RL-trained** (~50% of Grok's training budget, `GROK_HEAVY.md:2108-2109`). bad-research can't close that gap and shouldn't try; it rides whatever host model the user runs (today an Opus/Sonnet-class model with already-strong tool-use). This is the one axis where Family B has a structural edge.

### 3.3 Search & the index question
- The single biggest Family-A vs Family-B gap is the **index**. Perplexity owns a **200B-URL Vespa crawl** with **1.8-day median citation age** and **358 ms search p50** (`PERPLEXITY_DEEP.md:1596,2268,1342`); Grok owns the **X firehose** (~68M tweets/day, <1 min post→searchable). bad-research has **no owned index** — it rides host `WebSearch` + ddgs + 7 scholarly APIs. It will be **less fresh and slower** on breaking/real-time queries, and it cannot match social-signal retrieval at all. It compensates with the **scholarly verticals** (a genuine edge on academic/medical queries the hosted general-web products under-serve) and the **funnel** (breadth without context bloat: 100 queries → read-ceiling 80 → model sees only Stage-F reranked chunks).
- Retrieval recipe convergence: **Grok's collections RAG is RRF(BM25+embeddings) then a named reranker** (`GROK_HEAVY.md:1806-1820`) — *identical in shape* to bad-research's `RRF_K=60` + `α=0.7` + host reranker. Grok independently validates bad-research's retrieval design.

### 3.4 Grounding & verification — **bad-research's moat**
This is where bad-research beats **every** system in the table, and it's worth stating bluntly:
- **Perplexity DR has no post-hoc claim verifier** — grounding is *prompt-discipline* (cite-every-sentence) + rerank; "no explicit relevance-gate / claim-verifier / NLI stage is in the contract" (`PERPLEXITY_DEEP.md:79`). Its docs even warn "links in JSON may hallucinate."
- **Grok** binds char-span `InlineCitation`s and forbids fabricated IDs, but has **no entailment/uncited gate** — citation is a prompt contract, not a checker.
- **hyperresearch** has 4 adversarial critics + lint but **no per-sentence entailment/uncited gate** (`HYPERRESEARCH.md:94`).
- **Claude Research** is the closest: a prompt-embedded **source-quality negative-signal list** (worker flags caveats → lead reconciles) + a byte-identical **CitationAgent** validation gate. Notably, Anthropic shipped an `evaluate_source_quality` *tool*, found it broken, and **prompt-patched it out** — a near-exact parallel to bad-research's own recheck finding that its `authority_rank` path was a dead no-op (both teams learned "flag-don't-suppress" beats a scoring tool).
- **bad-research** is the only one with a **deterministic $0 catch layer**: `numeric_or_negation_mismatch` + `directional_antonym_mismatch` affirmatively catch flipped numbers/dates, flipped negation polarity, and antonym flips (`gate.py:280-370`); a **blocking no-uncited-claim gate** (any non-trivial factual sentence without a verified cite → `critical` → ship-block); a **12-gram/0.50 recitation gate**; and a tiered **CitationVerifier** (byte-identity → local NLI → host-judge) that *discloses* its one blind spot (pure paraphrase-contradiction is 0% keyless without `[local]` NLI). **Steal from Claude:** adopt its verbatim negative-signal list into the fetcher/critic prompts (see §6).

### 3.5 Context management
All of Family A share the same trick: **the model never holds raw pages.** bad-research keeps context flat ~5–15k tokens while sources scale 12→80 (`docs/SPEC.md:68`), reserves 40k for synthesis, and short-circuits to synthesis when `ceiling − cumulative < reserve`. Perplexity manages context inside the loop (`maybe_truncate()`, `search_context_size`) and strips `<think>` tags; Grok shares one cached prefix across all 16 agents via **RadixAttention** (prefix-cache read at $0.20/M). Convergent lesson: **the reranked-chunks-only funnel is the context-rot defense** in both families.

### 3.6 Termination
- **Perplexity** = the cleanest stated rule: **budget ∨ saturation ∨ satisfaction**, where saturation = *"stop if consecutive calls return mostly previously-seen entries"* (`PERPLEXITY_DEEP.md:3849-3855`) — **a qualitative information-saturation heuristic, NOT a numeric 0.70/0.85 gate** (this matters for §7).
- **Grok** = turns ∧ 200 s wait-budget ∧ tokens, **provably no convergence metric** (R1's "75% agreement" was debunked).
- **bad-research** = tier + `DEGRADE_ORDER` (redundancy → width → tier → short-circuit, tokens cut last) + `FAST_MAX_STEPS≤6`. **Steal:** Perplexity's saturation stop, implemented keyless as a *new-distinct-domains ratio* `new/returned < τ_sat` — this is the **evidence-based replacement** for the refuted funnel constants (§7).

---

## 4. The fork ledger — bad-research vs hyperresearch (verbatim keep/drop/add)

| Subsystem | Verdict | Detail |
|---|---|---|
| Skills-as-stages + disk state machine | **KEEP** | the core primitive (`HYPERRESEARCH.md:23`) — inherited unchanged |
| Patch-never-regenerate tool-locks | **KEEP** | `[Read,Edit]` patcher/polish, ≤500-char hunk cap, pre-stub logs (`HYPERRESEARCH.md:642`) |
| Evidence-fork / loci / tensions dialectical spine | **KEEP** | contradiction graph → 4-dim locus scoring (max 40) → committed position → reconcile |
| FTS5/BM25 vault (weights 10/1/5/3, status mults, dedup 0.6) | **KEEP** | keyless SQLite, no reason to change |
| LLM seam (host model, no key) | **KEEP** | upstream already keyless |
| **Exa neural search** | **DROP** | upstream's *only* keyed dep (`HYPERRESEARCH.md:547`) → replaced by host WebSearch + ddgs + verticals |
| Retrieval **fusion + reranker** | **ADD** | upstream is BM25-only (dead `embeddings` table); bad-research adds RRF k=60 + α=0.7 three-tier fusion + host reranker + `[local]` dense |
| **Per-sentence uncited gate + recitation gate** | **ADD** | absent upstream — bad-research's grounding moat |
| **11.5 citation-verifier + 14.5 fresh-review + 5th assumption-critic** | **ADD** | upstream has 4 critics + lint only |
| **0.5 clarify + 1.5 query-router + 1.6 plan-gate + FAST route** | **ADD** | upstream = 2 static tiers chosen at stage 1 |
| E1–E14 enhancement batch (eval gate, rails-judge, cascade-proxy, self-consistency vote, prompt-cache, …) | **ADD** | net-new, none upstream |

**Net:** bad-research = hyperresearch's skeleton + keyless search + a real retrieval engine + a grounding-verification layer + a routing/clarify layer. Every addition is defensible; the skeleton is untouched.

---

## 5. Where bad-research genuinely wins (state it plainly)
1. **Deterministic $0 grounding** — the only system in either family that mechanically catches number/negation/antonym flips and blocks uncited claims. Perplexity/Grok/hyperresearch cannot.
2. **Auditability** — `bad grounding-surface` emits a per-claim ledger (claim ↔ verbatim quote ↔ char offsets) as a shareable sidecar. No hosted DR tool exposes its grounding.
3. **Keyless / zero-infra / offline-capable** — runs on the host model + local OSS; `[local]` gives a fully offline neural lane. No index to fund, no vendor lock-in.
4. **Scholarly-first search** — 7 academic/medical verticals + primary-source discipline (period-pinned filings, "do NOT round" numbers) — hosted general-web products under-serve this.
5. **The dialectical spine** — loci/tensions/committed-positions force *argument*, not summary; the hosted products (except Claude's reconcile step) don't structurally argue.

## 6. Where bad-research is behind + the ranked steal-list
**Behind:** no owned/fresh index (Perplexity's 1.8-day median freshness, 358 ms p50); no real-time social (Grok's X firehose); no RL-trained tool-use (Grok/OpenAI's learned browse trajectory — the prompt-uncloseable gap); slower wall-clock than Grok's parallel 2–3 min.

**Steal-list (ranked, all keyless-implementable):**
1. **[P0] Claude Research's verbatim source-quality negative-signal list** → drop into the fetcher + critic prompts. It's the working mechanism Anthropic kept after deleting its scoring tool. Verbatim (`CLAUDE_RESEARCH.md:1313`): *"pay attention to indicators of potentially problematic sources — news aggregators rather than original sources, false authority, passive voice with nameless sources, general qualifiers without specifics, unconfirmed reports, marketing language, spin, speculation, cherry-picked data … flag these issues rather than presenting results as established facts."* (Your E8 already gestures at this — make it this list.)
2. **[P0] Perplexity's saturation stop** → replace the refuted funnel constants with `new_distinct_domains_i / domains_returned_i < τ_sat` (`SAT_TAU≈0.20`, calibrate on real runs). Evidence-based, cheap, model-agnostic (§7).
3. **[P1] Grok's terminal leader-render seam** → in ULTRAFAST/FAST, once synthesis starts it may **not** fan out again (Grok: "final response must never use a function call"). Prompt-only, guards synthesize-then-re-research thrash.
4. **[P1] Perplexity's ≤3-*orthogonal*-queries-per-step + dedup-guard `hash(tool,args)`** → your fast route already caps steps; add the "orthogonal not synonym" instruction + the identical-args guard.
5. **[P2] Grok's opt-in-verbosity-not-separate-modes** → you already do this (route × effort); keep resisting the urge to make "deeper" a distinct architecture — it's a budget knob.
6. **[P2] Gemini's `alpha=0.5` hybrid default** as a comparison point — your `α=0.7` leans lexical; worth an A/B on the `[local]` dense lane.
7. **REJECT — Grok's untyped emergent delegation** (work-split + conflict-reconciliation left 100% to the model over a free-text channel). For a bounded keyless run, your **typed** loci/tensions/critic layer is strictly better — keep it.

## 7. Corrections to bad-research's own docs (honesty pass)

**7.1 — The "Perplexity funnel-constant lineage" claim is refuted by your own teardown.** Multiple bad-research docs assert the `<0.70 / <30% / 0.85` funnel is *"the EXACT Perplexity DR constants / confirmed origin"* (`docs/enhancements/ENHANCEMENT_PLAN.md:43`, `docs/enhancements/DR_RUN_NOTES.md:177`, `docs/enhancements/COMPETITIVE_DR_SYSTEMS.md:218,532`). **`teardowns/PERPLEXITY_DEEP.md` `[CORRECTION 2026-05-30]` (PD:3758-3771) formally refutes all of them** — the L3-XGBoost-0.70 gate, the <30% re-retrieve, and the 0.85 entropy cutoff appear *only* in the teardown's §4 diagram, trace *only* to the third-party repo `github.com/OmidZamani/perplexity-journey` (self-labeled "reverse engineering and technical inference"), and are **contradicted-by-absence** in Perplexity's own cited article (which "names no model, no threshold, no entropy term"). Perplexity's *evidenced* coverage gate is the **qualitative saturation heuristic** in §3.6/§6, not a numeric threshold; its real default temperature is 1.0, not 0.7.

**What to do (not a code change — a relabel + optional add):**
- The **code is already honest** — `web/search/base.py:58` marks `relevance_threshold=0.70` as **CALIBRATE §7.2**, and `retrieval/constants.py` treats 0.70 as a tunable gate. **Only the enhancement docs overclaim the provenance.** Relabel those lines from *"EXACT Perplexity constants / confirmed origin"* → *"our own CALIBRATE default (originally believed Perplexity's; that attribution was refuted in PERPLEXITY_DEEP R5 2026-05-30)."*
- The `0.70` gate is a **perfectly reasonable engineering choice** — you don't have to remove it. But per §6 #2, the *evidence-based* stop is the saturation ratio; consider adding it alongside the gate and calibrating both on `bad calibrate` runs.
- Note the docs predate the 2026-05-30 correction, so this is **stale, not fabricated** — but it should be fixed so the "we copied Perplexity" story isn't repeated downstream.

**7.2 — Minor:** `docs/enhancements/COMPETITIVE_DR_SYSTEMS.md:198,532` and `DR_RUN_NOTES.md:198` carry the same refuted specifics (Perplexity "L1/L2/L3 XGBoost@0.70 … bi-encoder + DeBERTa vote"). The *shape* (recall→rerank, cross-encoder final) is INFERRED-sound; the *named models + thresholds* are the refuted speculation. Tag them INFERRED/REFUTED accordingly.

**7.3 — Accurate claims that survive (keep them):** bad-research *is* keyless (`bad doctor` proves it); its grounding gates *are* unique in the field (§4); `α=0.7 hybrid` and `RRF k=60` are independently validated by Grok's collections RAG (`GROK_HEAVY.md:1806-1820`); the planner→writer FAST route genuinely mirrors Perplexity's evidenced loop shape.

---

## 8. Sources
- **bad-research source:** `~/Desktop/badresearch/src/bad_research/**` (constants/stages cited inline) + `docs/{SPEC,HOW_IT_WORKS,INTERFACES_KEYLESS}.md`.
- **Teardowns** (`~/Desktop/researchfms/teardowns/`): `HYPERRESEARCH.md` (1,575 L), `PERPLEXITY_DEEP.md` (4,093 L, incl. R5 correction), `PERPLEXITY_COMPUTER.md`, `GROK_420.md` / `GROK_420_AGENTIC.md` / `GROK_HEAVY.md`, `OPENAI_DEEP_RESEARCH.md`, `GEMINI_DEEP_RESEARCH.md`, `CLAUDE_RESEARCH.md`.
- **Companion:** `HEADLESS_BREAKAGE_AND_FIX.md` (this dir) — why it "breaks" run headless and how to fix.
