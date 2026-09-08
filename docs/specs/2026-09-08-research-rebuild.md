# Spec — the research skill rebuild

Status: **approved 2026-09-08** (owner approved the shape; this is the design of record).
Supersedes: the 19-stage / 21-skill pipeline. `DIRECTION.md` outranks this file.

---

## 0. The one-paragraph statement

One skill, one loop, zero stages. A reasoner routes, then iterates under an **entity-frontier gate**
— every query after the first must name something learned from a prior read — with stop counters
computed by the harness rather than self-reported by the model. Readers fan out and return findings
plus verbatim spans, never reasoning. One adjudicator with one rubric. Grounding is enforced by
scripts with exit codes, not by prose. **Versatility lives in `references/lanes/*.md` — access
recipes read at the moment of use — never in modes, stages or registered sub-skills.** What grows is
source reach and executing checks. What shrinks is process scaffolding.

---

## 1. Requirements

Each is numbered so `compound-v:writing-plans` can map it to a task and to a verification line.
Hard constraints from `DIRECTION.md` are quoted **in the owner's own words**.

### Goals

**R1.** A query after the first MUST name a frontier item — an entity, quantity, contract cell,
unreconciled contradiction, or unprobed reachability failure that came from a prior read. A query
naming none is a re-phrase and MUST be refused **by a script, not by advice**.
*Owner: "a researcher finds one thing, and after he finds one thing he got more info in context to
find another thing, and he connects these two things."*

**R2.** An unreconciled contradiction between two sources on one claim is a **first-class frontier
item**, and the run MUST NOT close while one is open (subject to R14's cap).
*Owner: "knowing a lot of things in your research also makes you find counterparts of your research.
So when you know a lot of things, you can research counterparts of it to be 100% sure."*

**R3.** Stop counters (new-distinct-domains, new-distinct-entities per step) MUST be computed in code
BEFORE the prompt is built and merely shown to the planner. The model MUST NOT self-report
diminishing returns. `MIN_NEW_DOMAINS=2`, `MIN_SOURCES_PER_SUBQ=3`, `RESERVE_FOR_SYNTHESIS=0.25`.
"Unchanged" and "unreachable" are legitimate terminal states.

**R4.** ONE reasoner owns all judgment and writes the deliverable in one pass. Readers receive
`{source, question}` and return `{findings, verbatim spans, reachability outcome}` — never reasoning,
never a recommendation. Fan-out MUST be file/entity-disjoint, and reader count scales by **reading
volume**, not by research kind.

**R5.** ONE adjudicator with ONE rubric reads **only the artifact** — no trajectory, no search
history, no drafting rationale. Isolation is enforced by the harness (tool allowlist), not by the
prompt.

**R6.** Eight source lanes MUST be reachable, each as one `references/lanes/<lane>.md` recipe:
`local-corpus`, `artifact-re`, `practitioner-video`, `terms-and-pricing`, `live-instrument`,
`delta-vs-pinned-ref`, `people-track-record`, `web-live`. A lane is a FILE, never a registered skill.

**R7.** Every lane MUST emit an enumeration line — `lane | files listed | candidates selected | cut
line` — and a lane selecting 0 MUST be visibly reported, never silently absent.

**R8.** The deliverable's shape MUST be declared BEFORE retrieval and diffed **mechanically** at
ship. Contracts: `answer`, `matrix`, `verdict-table`, `decision-memo`. Each is a terminal predicate,
not a template.

**R9.** Six to eight grounding checks MUST execute as scripts with exit codes: byte-identity quote
check, recitation cap, uncited gate, contract diff, **no-source-claim check** (assert every "no
source was found for X" against the note store), and reachability-outcome presence.

**R10.** Retrieval-kind routing (navigational | semantic | metadata | author-shaped) and reranking
before the reasoner reads MUST be **coded**, below the reasoner, not prompted.

### Constraints (hard — quoted)

**R11.** *"graphs are only similarity/intuintion"* and *"graphs will be overkill for research."*
NO knowledge graph, entity store, triple store or embeddings index over the local corpus. The
existing `src/bad_research/graph/` fossil (a 34-byte `__init__.py`) is deleted, not filled in.

**R12.** *"don't skimp — no need to maybe enhance the skill if it's bad… Because quality is a
priority."* Simpler is a means, never the goal. **No capability may be removed to reduce line count.**

**R13.** *"step-by-step skills — they're not working, and coding agents have to read them manually
and not invoke it. So it's first error."* The `Skill()` step-indirection is deleted. Procedures are
bundled reference files read with `Read`, which has no registry and cannot race.

**R14.** No unbounded loop. The contradiction queue (R2) MUST be capped, or the agent manufactures
conflicts to keep searching.

**R15.** Browser access is `silver` only, with the user's own cookies. **Never** the Playwright MCP,
never mint a token, never quit or relaunch the user's browser. (Global CLAUDE.md; the leak class has
fired twice.)

**R16.** Always-on description budget ≤ ~500 chars for the whole skill. Measured live 2026-09-08:
109 personal skills already cost **40,139 chars (~10,034 tokens)**, and the listing is shortened when
it overflows — a dropped description reads as a skill that does not work.

**R17.** Never draft under a JSON schema. Structure applied to *reasoning* costs accuracy
(GSM8K free-text → JSON-with-schema: Claude-3-Haiku 86.5 → 23.4); structure applied to a *finished*
answer is free. Serialize afterwards as a separate transcription pass.

### Out of scope (explicitly)

**R18.** No per-kind research modes behind a router. No additional critics beyond R5. No polish or
readability stage. No per-kind report templates or domain rubrics. No blocking plan card at t=0 and
no mid-run clarifying questions (one cheap default-proceed shape confirmation at the boundary only).
No new scholarly APIs. No maintenance of the `--codex` translator.

**R19.** The teardown output shape stays its own skill (`re-source-first` / `re-quality-gate`). Its
acceptance rule — *"if you cannot state in one sentence what hidden server-side logic a section
reveals, the section is padding"* — is not expressible as a heading template, and that rule is the
entire value of the shape.

---

## 2. Why this shape — the evidence that decided it

Only the load-bearing items. Full provenance in the session's recon and mine artifacts.

| Decision | Evidence |
|---|---|
| Retrieval reach over process | BrowseComp-Plus: same agent, same loop, retriever swapped — gpt-4.1 **14.58% → 93.49%**; gpt-5 55.90 → 70.12 while search calls **drop** 23.23 → 21.74. Better reach raises accuracy AND cuts calls; every process expansion does the opposite. |
| Frontier gate, not naive iteration | Press et al. ~40% compositionality gap says chaining is necessary; 70.5% measured over-search and a verified **−42% fact-check degradation** from 2→150 tool calls say naive iteration is destructive. The gate separates the two. |
| Contradiction as a frontier item | DRNOISE: one seeded plausible-but-false document causes **66–88 point** accuracy drops. Named failure "verification inertia"; authors note *"generic verification prompts reduce but do not close this gap"* — so it cannot be prose. |
| Harness-computed stop | No published stopping rule has a measurement behind it. FLARE ships `max_iteration: int = 10000,  # TODO: too high?`; cognee's convergence check dedupes by `id(t)` so it can never fire. |
| One reasoner | ZS Associates built one agent per analytical step and killed it: *"it's not the LLM which failed, it's the way how we split the work"* — locally correct, globally incoherent. Warp and Cognition independently. |
| One adjudicator, not eight | Anthropic on this exact output type: a single LLM judge with one rubric *"proved most consistent for free-form outputs vs. many small judges."* Live run: 8 critic agents produced findings across only 3 angles. |
| Keep an adjudicator at all | Measured live: the critic caught a genuinely false claim — the draft asserted no source existed for depreciation/PUE/ops-labour while its own cited note contained all three. That catch becomes R9's script. |
| Checks execute, prose does not | Prompt scaffolding recovers ~73% of a **base** model's gap and **~7%** of a post-trained one's. Converting a source doc into a structured version measured **−8.4 to −27.4pp**. |
| Reranking | OpenScholar ablation: removing reranking drops citation F1 **47.9 → 28.2** — the largest single component, bigger than training (−5.6) or attribution (−3.9). |
| Shape as contract | DeepResearch Bench RACE: shipped agents spread **13.13 points** on Instruction-Following but only **2.97** on Readability. Polish is saturated; "did you produce the thing asked for" is where systems differ. |
| Contracts must be mechanical | AstaBench's **Faker** — fabricates the report, does no research — scores **39.2** on E2E-Bench for $0.026, beating ReAct/o3 (34.9) and ReAct/gpt-5 (30.0). Report-shaped output passes judges; only an executing check catches fabrication. |
| No graph | Karpicke & Blunt (*Science* 2011): concept mapping lost to plain retrieval practice, **M=0.45 vs 0.67** at one week, **d=1.50**, and lost even when the final test was building a concept map; 75% of subjects predicted the opposite. Shipped systems agree: graphiti defaults to no BFS, cognee's `neighborhood_depth` defaults to `None`, mem0 has no graph module. |
| No index over the corpus | A production findings-cache measured **0 hits in 133 attempts**; build cost projected at 25–92M tokens; both corpus roots grow most days. `grep -n` is correct at this size and current for free. |
| No per-kind specialist workflows | AstaBench: Asta v0 (routing to eight science specialists) scores 53.0 at **$3.40**/problem vs plain ReAct/gpt-5 44.0 at **$0.31**, and *loses* Code & Execution 47.6 to 55.0. Ai2: *"there may be diminishing value in application-specific workflows."* |
| Reference files, not sub-skills | Anthropic's own contract: bundled files are **level three**, read on demand; *"when the SKILL.md file becomes unwieldy, split its content into separate files and reference them."* |

### Measured on this system (2026-09-08) — the baseline being replaced

- **Step skills never fire: 8 of 9 `Skill()` calls returned `Unknown skill`** in a live run; only the
  entry skill resolved. Root cause chain: (a) `bad init` injected a CLAUDE.md block naming
  `/hyperresearch` and sixteen `hyperresearch-*` skills that have never existed — shipped into five
  real projects, two of which had no CLAUDE.md until it created one; (b) step skills are deliberately
  not installed globally to save listing budget; (c) the mid-session install loses a resolver race,
  and the entry skill converts one lost race into a permanent whole-run fallback.
  **Resolver rule, established by experiment:** the name set is captured at context start and
  refreshed at turn boundaries — main session same-turn fails, next-turn succeeds, and a subagent
  spawned *after* the write succeeds immediately.
- **`bad verify-citations` is broken and destructive**: 111/111 cited sentences returned
  `unsupported`, score exactly `0.0`, `needs_host_judgment: False`. The cited figures are verbatim in
  the cited notes (`0.66` ×5, `1,414.90` ×1, `87,072` ×2). It binds on `anchor_id: '2'` — the citation
  marker number — not on a resolved note plus span, so there is no premise to check. Its prescribed
  DROP-CITE-below-0.35 disposition would have stripped **all 111 correct citations**.
- **19% of the fetched corpus is junk and is never excluded**: 31 of 165 notes carry
  `status: deprecated` (404 pages, cookie banners). Zero notes ever get `deprecated: true`, so 31 carry
  a self-contradicting frontmatter. Nothing excludes them; `BM25_STATUS_MULT` only down-ranks ×0.3.
  Five skill files instruct the model **in prose** to "filter to non-deprecated notes".
- **Source reach is inverted against apparatus**: plain Claude+WebSearch cited **36 distinct URLs in
  ~14 minutes**; the fast pipeline cited **24 in 42 minutes**; the full 19-stage route fetched
  **192 sources and produced no report**, dying on a session rate limit at step 8 of 19 after ~2 hours.
- **Polish/readability cost ~19 minutes and added zero citations** (24 unique refs before and after),
  while the headline number moved 51% with no new evidence behind it.
- **Instruction surface before the first source is read: ~108,000 tokens** across 38 files.

**Methodological caveats on the above, stated because they bound the claims.** The blind-judge sweep
(3 lenses, plain session ahead on all three) compared **plain-final against fast-interim** — I
snapshotted the fast report while its run was still going. The fast arm was also forced onto the fast
route when its own router had correctly classified the question as `full`. Neither caveat touches the
firing measurement, the broken citation gate, the junk-note finding, or the full route's failure to
finish, all of which are independent.

---

## 3. Architecture

### 3.1 Always-on core

`SKILL.md` — target **≤250 lines**, description **~500 chars**. Deliberately under the ~5,000-token
per-skill compaction head. Contents, in order:

1. **Route** — three sentences, not a component: *answer-from-context | one wide expansion |
   frontier-chained*. Declared in the output header so the user can see and correct it. A silent
   classifier is rejected: Adaptive-RAG's oracle router reaches 51.20 EM at **1.59 steps** against
   always-multi-step's 44.60 at 5.53, but its shipped classifier is only **54.52%** accurate — so the
   route is re-decided continuously by the frontier gate rather than predicted once.
2. **The frontier gate** (R1, R2) with its four item types.
3. **Stop counters** (R3).
4. **Reader contract** (R4).
5. **Adjudicator contract** (R5).
6. **The checks** (R9) — named, with the command that runs each.

Everything else is a pointer.

### 3.2 What varies — `references/lanes/*.md`

Pay-per-use, **zero always-on cost**, read at the moment of use. Each is a recipe: when to reach for
it, exact commands, known traps, its reachability probe, and what counts as evidence.

| lane | carries |
|---|---|
| `local-corpus` | grep-first over 407 teardowns, ~190 essays (route via `_manifest.json`), ~100 x-guides, ~41 transcripts. Flat glob on teardowns, never `-r`. No index, ever. |
| `artifact-re` | the mandatory order: install package → sparse clone → read bundles → malformed-POST schema probe → fingerprint → blogs **last**. Evidence = `file:line` or a probe trace. Needs a sandbox story. |
| `practitioner-video` | `channels.tsv` (the only copy is `compound-v/references/channels.tsv`) + `yt.sh`. Traps: in-channel search is title-only so a zero means nothing; handle collisions are silent; **captions are substance, never quotation**; low concurrency (43% bot-wall at 8-way). |
| `terms-and-pricing` | verbatim clause + section number + URL + as-of date. Output carries a "what would flip this" row. |
| `live-instrument` | state the protocol (resolution, window, unit, control); report a **bound**, not a fact. Hourly sampling understated peak CPU by 700% on identical data. |
| `delta-vs-pinned-ref` | two pinned refs; **version-identity check first** (npm `composio@1.0.0` was a 2023 name-squat); UNCHANGED rows are reportable. |
| `people-track-record` | rank by incentive, not prominence; recruiting content is not testimony. |
| `web-live` | `silver` only, user's cookies (R15). The probe outcome — status, interstitial text, byte count — becomes **a row in the report**, because an empty fetch is indistinguishable from a fabricated quote (curl got 15 chars where silver got 9,921 on the same URL). |

### 3.3 What varies — `references/contracts/*.md`

Terminal predicates, not templates (R8):

- **answer** — every claim bound to a quoted span that byte-matches a retrieved source.
- **matrix** — rows × columns fixed before retrieval, each cell a retrieval obligation; no empty cell
  ships unlabelled.
- **verdict-table** — one row per claim graded TRUE / MOSTLY_TRUE / MISLEADING / FALSE, counter-evidence
  attached; DECLINE is legitimate.
- **decision-memo** — contains a named option, a quoted number, and a stated re-evaluation trigger
  (three presence checks).

### 3.4 The four seams

1. **Lane seam** — reasoner → reads `references/lanes/<lane>.md` → runs a shell command. Keeps
   versatility off the shared description budget (R16).
2. **Reader seam** — `{source, question}` in; `{findings, spans, reachability}` out (R4).
3. **Check seam** — every check is a script with an exit code, **proven against a planted defect
   before it counts**. *"A check that can only pass is not a check"* — a coverage checker in this repo
   shipped at 11% coverage while printing clean.
4. **Contract seam** — shape declared before retrieval, structural diff at ship (R8).

### 3.5 Retrieval plumbing (coded, below the reasoner)

Retrieval-kind routing, reranking before the reasoner reads, and full-text acquisition as an explicit
step. Ai2's note on why this layer is coded rather than delegated: *"more efficient… and more reliable
than a more dynamic process that grants more autonomy to the LLM."*

### 3.6 Substrate

Author as one `SKILL.md` + `references/` + a platform-neutral CLI — the portable core the Agent Skills
standard covers. Install to `~/.agents/skills` **or** `~/.claude/skills`, never both (opencode scans
both at equal priority, last-write-wins). Ship host-specific pieces (hooks, agents, bin) as a Claude
Code plugin — **for capability, not for budget protection**: plugin membership does not protect a
description.

---

## 4. Size — a reallocation, not a shrink

| | before (measured) | after (target) |
|---|---|---|
| skills | 21 | **1** |
| always-on description | 5,861 chars (5,363 of them — **91%** — belonging to 20 `user-invocable: false` step skills) | **~500 chars** |
| entry SKILL.md | 411 lines / 36,983 chars | **~250 lines** |
| stages | 19 | **0** (a loop with a gate) |
| agent definitions | 17 (8 of them critics) / 3,142 lines | **3** (reader, adjudicator, quote-verifier) |
| prose total | 7,771 lines | **~1,800 lines** |
| **source lanes reachable** | **0** | **8** |
| **checks that execute** | **~0** | **6–8** |

Cut cleanly from the CLI: stage orchestration, the `graph/` fossil, the 2,390-line `--codex`
translator, polish/readability. Kept: retrieval plumbing, the vault, the funnel, the deterministic
grounding primitives. Added: reranking, full-text acquisition, retrieval-kind routing, the
local-corpus lane.

**Nothing the agent can do today is removed. Six kinds of source it cannot currently reach are added.**

---

## 5. How it gets tested

- Every check in R9 ships with a **planted-defect fixture** and is proven to go red before it counts.
- **R1 is verified by replay**: a fixed query set run with (a) classify-once routing and (b)
  re-decide-per-read frontier routing, comparing steps-to-answer against answer quality. Fixtures
  already exist unused at `researchfms/skills_research/cv_test/` and `cv_test2/`.
- **The baseline is the three-arm run** in this session's scratchpad: plain / fast / full. The rebuild
  must beat plain-session on the accretion lens, blind-judged, on a report allowed to finish.
- `bad doctor` must report every registered lane, and a lane returning zero must say so (R7).

## 6. Open — carried forward, not resolved

- **Five real queries and the triggering run** are still missing from `DIRECTION.md`. The two
  preserved runs are both web-doc lookups, so the corpus may be scoped to the wrong kind of research.
- **What "overcomplicated" costs** has never been priced: tokens, wall-clock, cognitive load, or bad
  reports.
- **The full route has never produced a report**, so its stages' contribution remains unmeasured. The
  rebuild does not depend on that measurement, but no claim about what those stages *would* have
  produced may be made.
