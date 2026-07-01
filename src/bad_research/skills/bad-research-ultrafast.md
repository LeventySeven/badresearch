---
name: bad-research-ultrafast
user-invocable: false
description: >
  The commercial-DR middle tier of Bad Research (ultrafast route only) — an
  autonomous plan → K parallel researchers → leader-only sectioned synthesis that
  produces a long, fully-cited report in 5–15 minutes, replacing the 16-step
  pipeline. Keyless; stacks the best pattern from Perplexity / Gemini / Grok /
  OpenAI / Claude Deep Research.
---

# Ultrafast — autonomous lead + parallel researchers (commercial-DR middle tier)

**Tier gate:** Runs ONLY for the `ultrafast` route. It is fully **autonomous** — no
clarifier (0.5) and no plan-gate (1.6) precede it; the entry skill skips both. It
does NOT run the width-sweep funnel as a fixed step; the lead spawns parallel
sub-researchers that each *call* retrieval.

**Goal:** answer a moderately broad query at commercial-Deep-Research grade in a
**5–15 minute** target — a research plan, a wide parallel multi-source browse, and
ONE long sectioned report with per-sentence citations. Deeper than `fast` (a single
shallow loop), far cheaper than `full` (no contradiction graph, loci, depth
investigation, triple-draft, 5-critic fan-out, grader loop, or fresh-review).

## Recover state

Read:
- `research/query-<vault_tag>.md` — canonical query (GOSPEL)
- `research/prompt-decomposition.json` — confirm `route == "ultrafast"`; read the
  `sub_questions` (capped at ULTRAFAST_MAX_SUBQUESTIONS = 8) and the `scope_brief`

If `route != "ultrafast"`, STOP and return to the entry skill — you were invoked by
mistake.

## The pipeline (PLAN → BROWSE → SYNTH)

You are the **lead** and the **only writer**. Maintain, across the whole run, a
per-sub-question coverage **checklist** (each sub-question → the set of distinct
supporting domains seen so far) plus cumulative `seen_domains` / `seen_urls` sets. A
sub-question is GREEN once it has ULTRAFAST_MIN_SOURCES_PER_SUBQ (4) distinct domains.

### 1. PLAN (internal — no gate; Gemini DR plan run autonomously)

The decomposition's `sub_questions` ARE the report's sections. Order them by
importance (Claude breadth-first ordering). Do NOT pause for approval — ultrafast is
autonomous. Write the ordered section plan to `research/temp/ultrafast-plan.md`.

### 2. BROWSE (wide parallel multi-source — Claude lead + parallel subagents)

Spawn `K = min(n_sub_questions, ULTRAFAST_SUBRESEARCHER_K = 6)` parallel
`bad-research-fetcher` sub-researchers, ONE per sub-question, importance-ordered.
Each is a bounded agentic browse loop (Perplexity/OpenAI pattern):
`FETCHER_TOOLCALL_CAP["ultrafast"]` (15) tool calls, ULTRAFAST_FETCHER_TIMEOUT_S
(360s) soft deadline, chasing 3–8 primary sources via citation chains.
Sub-researchers return **claims + sources JSON, never prose** (Grok leader-only
seam). Use the **seven-piece subagent spawn contract** from the entry skill —
`research_query` (verbatim) / `pipeline_position` / `inputs` / `objective` /
`output_shape` (the `claims-*.json` shape) / `tools_allowed`
(`["web_search","fetch_url","execute_python"]`) / `stop_conditions` (halt when
ULTRAFAST_MIN_SOURCES_PER_SUBQ distinct domains found OR the tool-call cap is hit OR
ULTRAFAST_FETCHER_TIMEOUT_S elapses).

Gather all waves with a per-wave deadline = ULTRAFAST_FETCHER_TIMEOUT_S; proceed with
returned results if a wave exceeds it. After the first wave, if any sub-question is
still below the green gate, spawn ONE optional gap-fill wave targeting only the weak
sub-questions (never re-spawn green ones). The whole BROWSE stage is bounded by
ULTRAFAST_TIMEOUT_S (900s wall-clock net).

Math sub-claims: the fetchers use `execute_python`, never compute in prose.

Read figures (the sub-researchers are natively multimodal): if a source's substance is
in a figure/chart/table-image, or in a scanned (text-layerless) PDF, the text layer is
empty and the fetch path has already saved the rendered pixels as a PNG asset bound to
the note. Resolve it with `bad assets list --note-id <note-id> --json`, then
`bad assets path <asset-id>`, and use the `Read` tool on that PNG to transcribe the data
into the note VERBATIM (the numbers exactly as plotted/printed), citing it as a figure.
The transcription written into the note body becomes the claim's `quoted_support`, so the
figure-derived number is grounded and verifiable like any text claim — never eyeball a
number that was not Read off the saved image. `Read` is therefore in the fetcher
`tools_allowed`.

### 3. SYNTH (leader-only terminal synthesis — Grok seam + Gemini/OpenAI report)

When BROWSE ends you become the **writer**. Reserve ULTRAFAST_RESERVE_SYNTH_FRAC
(30%) of budget for this. Three boundaries (same discipline as `fast`):

1. **Writer context boundary (Perplexity):** synthesize from `(original_query,
   dedup'd evidence, the researchers' returned claims)` only — never raw browse
   traces. Once writing starts, do NOT fan out again (Grok terminal-synthesis seam).
2. **Word governor (Claude copyright cap; OpenAI `[wordlim]`):** ≤25 words verbatim
   from any single source, ≤1 quote per source.
3. **Partial-answer-better-than-none (Perplexity):** if a wave stalled, still write
   the best grounded report from what was gathered — flag the thin sub-questions
   rather than refusing.

**Terminal synthesis seam (Grok):** Once you begin writing the synthesized answer, you must NOT issue any further search/fetch/tool calls. If you find a gap while writing, note it as a limitation — do not re-open research. The synthesis turn is terminal.

**Realism:** when the answer estimates software/technical effort, assume an
agentic-coding world — hours-to-days, never weeks or months — and omit calendar
estimates unless the query asks for one.

Write the report in ONE pass to `research/notes/final_report_<vault_tag>.md`:
- A direct lead answer, then **one section per sub-question** (importance-ordered),
  **tables over bullet lists** where the data is comparative.
- Length **1500–4000 words**, scaling with breadth.
- Per-sentence single-index `[N]` citations: each index in its own bracket
  (`[1][2]`, never `[1,2]`), ≤3 per sentence, no space before the bracket.
- No `## References` section — the `[N]` resolves to the vault note out-of-band.

## Exit criterion

- `research/notes/final_report_<vault_tag>.md` exists, 1500–4000 words, sectioned
- `research/temp/ultrafast-plan.md` has the ordered section plan
- Every non-trivial sentence carries a `[N]` resolving to a vault note (the slim
  citation-grounding pass + the step-16 `bad uncited-gate` enforce this)

## Next step

Return to the entry skill (`bad-research`). After the writer, sequence the same slim
tail as the fast route:

1. **Slim citation grounding** — `Skill(skill: "bad-research-11.5-citation-verifier")`
   (its **Slim mode (fast route)** section): backward-ground the cited sentences with
   `bad verify-citations`, applying ACCEPT/TIGHTEN/FLAG/DROP-CITE dispositions INLINE
   (Read+Edit, no patcher). **Keyless neutral band:** for any finding
   `bad verify-citations` emits with `needs_host_judgment: true` (a paraphrase the
   local NLI could not judge, parked at the 0.5 default), do NOT disposition off the
   bare 0.5 — that silently hedges a never-judged claim. You ARE the host model:
   re-judge that (claim, cited-span) pair yourself — read the cited span and the
   sentence, decide entailment, and apply the ACCEPT/TIGHTEN/FLAG/DROP-CITE
   disposition from your own judgment.
2. **Slim single critic** — `Skill(skill: "bad-research-12-critics")` (its **Light-tier
   slim critic** section): one adversarial dialectic+instruction pass, applied inline;
   no fan-out, no patcher.
3. **Polish** — `Skill(skill: "bad-research-15-polish")`.
4. Then the step-16 gate (`bad uncited-gate`).
