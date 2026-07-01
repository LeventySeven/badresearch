---
name: bad-research-fast
user-invocable: false
description: >
  The bounded-ReAct fast mode of Bad Research (fast route only) — a
  step-bounded (FAST_MAX_STEPS ≤ 6) shape-aware planner→writer loop that
  produces a fast, cheap, per-sentence-cited answer, replacing the 16-step
  pipeline.
---

# Fast — shape-aware bounded ReAct

**Tier gate:** Runs ONLY for the `fast` route. It does NOT run the
width-sweep funnel (`bad funnel-gather`) as a fixed step; it does a bounded
loop that *calls* the funnel / retrieval per iteration. No clarifier, no
decompose-time fan-out — fast by design.

**Goal:** answer a bounded query quickly (a < 10 minute target) with grounded
per-sentence citations. Terminate via the auditable XSTOP-1 4-clause stop rule
(below) — whichever clause fires first.

## Recover state

Read:
- `research/query-<vault_tag>.md` — canonical query (GOSPEL)
- `research/prompt-decomposition.json` — confirm `route == "fast"`

If `route != "fast"`, STOP and return to the entry skill — you were
invoked by mistake.

## The loop (shape-aware, planner → writer split)

Read `query_shape` from `research/prompt-decomposition.json` and the one-paragraph
`scope_brief` (your framing). Then run by shape:

- **straightforward** → ONE bounded ReAct loop, ≤3 steps.
- **depth_first** → ONE bounded ReAct loop, up to `FAST_MAX_STEPS` (6) steps,
  reflect-then-narrow (each step deepens the prior).
- **breadth_first** → spawn K = min(n_independent_subq, `FAST_SUBRESEARCHER_K` = 3)
  parallel `bad-research-fetcher` sub-researchers, ONE per sub-question, each a
  bounded fetch loop (`FETCHER_TOOLCALL_CAP["light"]`, `FETCHER_TIMEOUT_S`). You are
  the LEADER and the ONLY writer (sub-researchers return claims+sources, never prose).
  Use the seven-piece subagent spawn contract from the entry skill. Gather all waves
  (per-wave deadline = `FETCHER_TIMEOUT_S`) before writing.

You are the **planner** (system A). Maintain, across the whole run, a per-sub-question
coverage **checklist** (each sub-question → the set of distinct supporting domains seen
so far) plus cumulative `seen_domains` / `seen_urls` sets. A sub-question is GREEN once
it has `FAST_MIN_SOURCES_PER_SUBQ` (3) distinct domains.

The single-loop body (straightforward/depth), persisting `(thought, action, observation)`
to `research/temp/react-trace.md`:

```
step=0; stalled=0; deadline=now+600                      # FAST_TIMEOUT_S (wall-clock safety net)
next_queries = sub_questions[:FAST_MAX_QUERIES_PER_STEP]  # step-0 queries = the sub-questions
while step < 6 and next_queries and now < deadline:      # (1) hard cap = FAST_MAX_STEPS
    step += 1
    before = (len(seen_domains), len(seen_urls))
    ACT: fan out <=4 queries (FAST_MAX_QUERIES_PER_STEP), <=5 results each (FAST_MAX_RESULTS_PER_QUERY):
        bad funnel-gather "<q>" --mode light --vault-tag <tag> --max-queries 4 --read-top-k 12 --json
        for each NEW url: seen_domains.add(domain); add that domain to the checklist entry of the sub-q this query served
    OBSERVE: bad retrieve "<original verbatim query>" --mode light --top-k 12 --json
    new_domains, new_urls = deltas vs `before`           # loop counters, ZERO model calls
    if all sub-qs have >= FAST_MIN_SOURCES_PER_SUBQ (3) distinct domains: break          # (2) coverage complete
    if new_domains < FAST_MIN_NEW_DOMAINS (2) and new_urls < FAST_MIN_NEW_DOMAINS:
        stalled += 1
        if stalled >= FAST_STALL_PATIENCE (1): break                                     # (3) diminishing returns
    else: stalled = 0
    decision = REFLECT(...)                               # the reflect/stop JSON below (one model call)
    if decision.research_complete or decision.coverage_complete or decision.can_answer_confidently: break   # (4) model-declared
    next_queries = decision.next_queries[:FAST_MAX_QUERIES_PER_STEP]   # target WEAKEST sub-qs; never repeat/paraphrase a past query
# reserve FAST_RESERVE_SYNTH_FRAC (25%) of budget for the writer; a partial answer beats no answer
```

**Orthogonal queries per step:** The queries a step fans out (≤ `FAST_MAX_QUERIES_PER_STEP`) must be ORTHOGONAL sub-questions — distinct facets, never synonyms/rephrasings of one query. Spend the budget on coverage, not restatement (Perplexity's orthogonal-facets discipline, PD:3846).

**Math queries:** use `execute_python` in ACT, never compute in prose. The domain/URL deltas are
loop counters, not model claims — the stop is auditable even if the model lies about diminishing returns.

**Read figures (you are natively multimodal):** if a source's substance is in a
figure/chart/table-image, or in a scanned (text-layerless) PDF, the text layer is empty
and the fetch path has already saved the rendered pixels as a PNG asset bound to the
note. Resolve it with `bad assets list --note-id <note-id> --json`, then
`bad assets path <asset-id>`, and use the `Read` tool on that PNG to transcribe the data
into the note VERBATIM (the numbers exactly as plotted/printed), citing it as a figure.
The transcription you write into the note body becomes the claim's `quoted_support`, so
the figure-derived number is grounded and verifiable like any text claim — never eyeball
a number you did not Read off the saved image.

### Reflect/stop prompt (emit once per step — returns ONE JSON object)

After each retrieval step the planner emits this prompt and acts on the returned JSON
without a second model call. The harness computes the `new_distinct_domains` /
`new_distinct_urls` deltas + the coverage checklist BEFORE the prompt is built (zero
extra model calls) and merely *shows* them — so the stop decision stays auditable from
the loop's own counters even if the model lies about `diminishing_returns`.

```text
SYSTEM:
You are the planner for a fast web-research loop. After each batch of search results you must (a)
record what you learned, (b) assess coverage against the sub-question checklist, (c) decide whether
to stop or issue the next batch of queries. Be decisive: this is a SPEED-optimized loop, not an
exhaustive one. Bias toward stopping. Return ONLY valid JSON, no prose, no markdown fences.

USER:
Original question: {original_query}
Today: {today}

Sub-question coverage checklist (each item: sub-question -> distinct supporting domains so far):
{checklist_json}

New sources retrieved THIS step:
- new distinct domains this step: {new_domains_this_step}
- new distinct URLs this step: {new_urls_this_step}
- cumulative distinct domains: {cumulative_domains}

Newly retrieved content (trimmed to FAST_CONTENT_TRIM_CHARS):
{step_findings}

Decide, following these HARD LIMITS:
- STOP if every sub-question already has FAST_MIN_SOURCES_PER_SUBQ+ distinct supporting domains.
- STOP if this step added fewer than FAST_MIN_NEW_DOMAINS new distinct domains AND fewer than
  FAST_MIN_NEW_DOMAINS new distinct URLs (the frontier has saturated — more searching will repeat).
- STOP if you can already answer the original question comprehensively and confidently.
- Otherwise CONTINUE and propose up to FAST_MAX_QUERIES_PER_STEP NEW search queries that target the
  WEAKEST (fewest-source) sub-questions. Each query must be unique and not a paraphrase of any past
  query. Do NOT propose queries for sub-questions that are already green.

Return ONLY this JSON:
{
  "learnings": ["<concise, entity- and number-dense fact extracted from the new sources>", ...],
  "checklist_update": {"<sub-question>": <count of distinct domains now supporting it>, ...},
  "coverage_complete": <true|false>,
  "diminishing_returns": <true|false>,
  "can_answer_confidently": <true|false>,
  "research_complete": <true|false>,        // true => stop now (the keyless ResearchComplete signal)
  "next_queries": ["<query>", ...]          // [] if research_complete is true
}
```

The loop treats `research_complete == true` OR `coverage_complete == true` OR
`diminishing_returns == true` (for `FAST_STALL_PATIENCE` steps) OR the structural cap as the
stop trigger.

## Write (the writer split — system B)

When the loop ends, you become the **writer**. Three boundary lifts the R5 deltas confirmed:

1. **Writer context boundary (Perplexity §R5.2):** the writer receives ONLY
   `(original_query, dedup'd evidence, prior learnings)` — never the planner's raw
   `react-trace.md`. Once the writer starts, the loop does NOT fan out again
   (Grok terminal-synthesis seam, `GROK_HEAVY.md:598`).
2. **Word governor (Claude copyright cap; OpenAI `[wordlim 200]`):** ≤25 words verbatim
   from any single source, ≤1 quote per source.
3. **Partial-answer-better-than-none (Perplexity §R5.4):** if the loop stopped early
   (cap / stall), still write the best grounded answer from what was gathered — flag the
   thin sub-questions rather than refusing.

**Terminal synthesis seam (Grok `GROK_HEAVY.md:598`):** Once you begin writing the synthesized answer, you must NOT issue any further search/fetch/tool calls. If you find a gap while writing, note it as a limitation — do not re-open research. The synthesis turn is terminal.

**Realism:** when the answer estimates software or technical effort, assume an
agentic-coding world — think hours-to-days, never weeks or months — be realistic,
and omit calendar estimates unless the query explicitly asks for one.

Write the answer in ONE pass:
- Direct answer first; length scales with shape — 500–2000 words (straightforward/depth);
  longer for `breadth_first` runs (one section per sub-question), tables not bullet lists.
- Per-sentence single-index `[N]` citations: each index in its own bracket
  (`[1][2]`, never `[1,2]`), ≤3 per sentence, no space before the bracket.
- No `## References` section in the prose — the `[N]` resolves to the vault
  note out-of-band (the CLI/host renders the source list).
- Write to `research/notes/final_report_<vault_tag>.md`.

## Exit criterion

- `research/notes/final_report_<vault_tag>.md` exists, length-appropriate for the shape
- `research/temp/react-trace.md` has the full (thought, action, observation) trace
- Every non-trivial sentence carries a `[N]` resolving to a vault note (the slim
  citation-grounding pass + the step-16.6 `bad uncited-gate` enforce this)

## Next step

Return to the entry skill (`bad-research`). After the writer, sequence:

1. **Slim citation grounding** — invoke `Skill(skill: "bad-research-11.5-citation-verifier")`
   (its **Slim mode (fast route)** section): backward-ground the cited sentences with
   `bad verify-citations`, applying ACCEPT/TIGHTEN/FLAG/DROP-CITE dispositions INLINE (Read+Edit,
   no patcher). This sits upstream of the step-16.6 `bad uncited-gate` ship-block.
   **Keyless neutral band:** for any finding `bad verify-citations` emits with
   `needs_host_judgment: true` (a paraphrase the local NLI could not judge, parked at
   the 0.5 default), do NOT disposition off the bare 0.5 — that silently hedges a
   claim that was never judged. You ARE the host model: re-judge that (claim,
   cited-span) pair yourself — read the cited span and the sentence, decide
   entailment, and apply the ACCEPT/TIGHTEN/FLAG/DROP-CITE disposition from your own
   judgment.
2. **Slim single critic** — `Skill(skill: "bad-research-12-critics")` (its **Light-tier slim
   critic** section): one adversarial dialectic+instruction pass, findings applied inline; no
   fan-out, no patcher.
3. **Polish** — `Skill(skill: "bad-research-15-polish")`.
4. Then the step-16 gate (`bad uncited-gate`).
