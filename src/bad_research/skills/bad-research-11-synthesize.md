---
name: bad-research-11-synthesize
user-invocable: false
description: >
  Step 11 of the Bad Research pipeline (full tier) — plans and outlines the
  synthesis, then spawns one Read+Write-locked synthesizer that merges the 2
  drafts into the final report (research/notes/final_report_<vault_tag>.md).
---

# Step 11 — Synthesize the final report

**Tier gate:** SKIP entirely for `light` tier — light tier wrote `research/notes/final_report_<vault_tag>.md` directly in step 10 and proceeds straight to step 15 (polish). For `full`: run as documented below.

**Goal:** turn the 2 angle-specific drafts from step 10 into ONE integrated final report at `research/notes/final_report_<vault_tag>.md`. The orchestrator preps the strategic brief; the synthesizer subagent writes the report in two passes (rough integrated draft, then voice/redundancy/length cleanup). The synthesizer IS the reconciler — it merges the strongest-thesis and steelman-contrarian drafts and commits per-tension.

**Why split orchestrator + synthesizer:** the orchestrator has been running for 30+ minutes and 200K+ tokens of context. Writing a coherent 5000-10000 word report at this point is the highest cognitive load step in the pipeline, and orchestrator context is full of stale subagent dispatch logic. The synthesizer is a fresh Opus session with `[Read, Write]` tool-lock, focused exclusively on producing the final report. This is the same architectural move that made the patcher and polish-auditor reliable.

---

## Recover state

Read these inputs:
- `research/scaffold.md` — vault_tag
- `research/prompt-decomposition.json` — atomic items, required_section_headings, response_format, citation_style
- `research/temp/reflections.md` — the distilled short-term memory (≤3 claim bullets + `cited_note_ids` per round). **The synthesizer plans from this; cap the distilled context at ≤10K tokens — see Step 11.4b**
- `research/temp/draft-a.md`, `research/temp/draft-b.md` — the 2 angle-specific drafts from step 10
- `research/temp/tensions.md` (full tier) — cross-locus + orphan expert disagreements (the merged step-6 artifact; replaces the former `comparisons.md` + `source-tensions.json`)
- `research/temp/evidence-digest.md` — load-bearing claims with verbatim quotes
- `research/query-<vault_tag>.md` — canonical research query (GOSPEL)

---

## Step 11.1 — Read both drafts in full

1. **Read each draft in full** from `research/temp/draft-{a,b}.md`. Don't skim — actually read. Hold them in context.

2. **Re-read each sub-orchestrator's report-back** (from your own task results in step 10). Note each draft's:
   - Core thesis
   - How many notes from `must_read_note_ids` it actually read
   - Strongest argumentative beat
   - Word/character count

---

## Step 11.2 — Spot-check factual conflicts (orchestrator only)

The synthesizer is tool-locked to `[Read, Write]` — it cannot run Bash to query the vault. So YOU resolve factual conflicts here, before spawning it.

For each substantive contradiction between drafts:
1. Identify the cited source IDs on both sides
2. `bad note show <id1> <id2> -j` to read the actual source bodies
3. Decide which side is correct. Write the verdict to `research/temp/synthesis-conflicts.md`:
   ```markdown
   ## Conflict 1: <one-line description>
   - Draft A says: <claim with citation>
   - Draft B says: <opposing claim with citation>
   - Source check: <what the source actually says, verbatim where possible>
   - **Verdict:** <which side, with reason>
   ```

If there are no substantive conflicts, write a one-line file: "No factual conflicts found across drafts."

---

## Step 11.3 — Write the synthesis plan

Write `research/temp/synthesis-plan.md`. This is your strategic brief for the synthesizer:

```markdown
# Synthesis plan

## Core thesis (1-2 sentences)
<the final report's central argument>

## The 3-7 strongest argumentative beats
1. **<short name>** — sourced from Draft <A/B>. <one sentence on the beat and why it's load-bearing>
2. ...

## Section structure
<list required_section_headings if present, OR the inferred H2 structure>

## Per-section commitments
### Section 1: <heading>
- Evidence to pull from: Draft A's <topic>, Draft B's <topic>
- Argumentative beat: <which committed position to argue here>
- Cross-locus tension to engage (if any): <name from tensions.md>

### Section 2: ...

## Where drafts disagreed
- **<Disagreement 1>:** Draft A says X; Draft B says Y. **Commit to <side>** because <reason>. The other side gets explicit engagement, not equal hedging.
- ...

## Length target
- response_format: <short|structured|argumentative>
- Pass 1 target: <middle of pass-1 range>
- Pass 2 final target: <middle of pass-2 range>
```

---

## Step 11.4 — Write the synthesis outline

Write `research/temp/synthesis-outline.md`. This is the per-section contract — 1-2 sentences per H2 naming what evidence and argument lives there:

```markdown
# Synthesis outline

## Executive summary
<1-2 sentences: the direct answer to the research_query, with top-line numbers if applicable>

## I. <First H2 from required_section_headings or plan>
<1-2 sentences: what this section establishes, which evidence anchors it, what argumentative beat lives here>

## II. <Second H2>
<1-2 sentences>

...

## Conclusion / Opinionated synthesis
<1-2 sentences: the committed reading, the strongest forward-looking implication>

## Sources
<only emitted when citation_style == "inline" — N numbered entries, deduplicated. For "wikilink" style (default), the wiki-link markers in the body are self-resolving and no separate Sources section is needed.>
```

The outline is short (50-200 words total). It's the structural anchor that prevents pass-1 sections from rambling.

---

## Step 11.4b — Pull grounded evidence for the synthesizer (≤10K distilled + targeted raw spans)

**Plan from the distilled reflections; re-inject raw spans only for what gets
cited (Tavily "re-inject raw only at the end" + Chroma ≤10K-token ceiling).** The
mid-pipeline carried only distilled reflections; the synthesizer pays the raw-span
cost once, at the end, and only for the cited `note_id`s.

1. **Plan the synthesis from `research/temp/reflections.md`** — its distilled ≤3
   claim bullets per round and its `cited_note_ids`. **Cap the distilled
   synthesis context at ≤10K tokens** (the Chroma context-rot ceiling — context
   past ~10K degrades synthesis quality). If `reflections.md` exceeds the ceiling,
   compact it first (`retrieval/reflections.py::ReflectionLog.compact` drops the
   oldest records, keeping the most-recent live findings/gaps).

2. **Then re-inject raw spans ONLY for the `note_id`s the synthesizer will
   cite.** For each planned section, pull the top-ranked grounded chunks — the
   verbatim spans — for the relevant cited notes so the synthesizer cites against
   `claim_anchors`, not its own recall:

   ```bash
   bad retrieve "<section topic / sub-question>" --mode full --top-k 20 --json
   ```

   For each returned chunk, the `note_id` + `char_start`/`char_end` are the
   citation anchor; its `quoted_support` is the verbatim span. Compute
   `(line_start, line_end)` from `char_start`/`char_end` using
   `char_span_to_line_range` (available via `bad_research.grounding.extract`).
   Write the section→chunks map to `research/temp/synthesis-evidence.md` — each
   chunk carries its line span so the synthesizer can emit a line-anchored cite:

   ```yaml
   - chunk: "Vietnam reached 64%..."
     note_id: source-note-19
     char_start: 1247
     char_end: 1402
     line_start: 42          # 1-based line in the note body
     line_end: 44            # 1-based line in the note body
     quoted_support: "..."
   ```

   Pass its path to the synthesizer. The total context handed to the synthesizer
   is the ≤10K-token distilled plan **plus** these targeted raw spans — not the
   whole corpus.

   **Carry each cited note's `source_quality_flags` into `synthesis-evidence.md`.**
   When you pull the spans for a note, read its `claims-<note-id>.json` and copy any
   non-empty `source_quality_flags` array (e.g. `["marketing_spin"]`) next to the
   chunk in the section→chunks map. The synthesizer reconciles these flags in prose
   (worker flags, lead reconciles — there is NO deterministic penalty); it needs to
   see the flag to down-weight/caveat the source.

3. **Spans preserved for grounding.** Re-injecting the verbatim `quoted_support`
   spans for the cited notes is exactly what keeps the `uncited-gate` /
   `recitation-gate` / `anchors.py` lane able to verify each cite byte-for-byte —
   the distilled-reflection discipline never weakens grounding, it just defers the
   raw re-injection to this final step.

**Grounded citation rendering** (added to the synthesizer's spawn instructions):
- Every `[[note-id]]` / `[N]` the synthesizer emits MUST correspond to a chunk
  in `synthesis-evidence.md` whose `quoted_support` is in the `claim_anchors`
  table. A claim with no locatable anchor is NOT written (forward binding).
- The CitationVerifier (step 11.5) will check every cite byte-for-byte after —
  fabricated cites are caught and dropped, so emit only anchored ones.

---

## Step 11.5 — VERIFICATION GATE

Before spawning the synthesizer, verify these files exist with non-trivial content:
- `research/temp/synthesis-plan.md` — must include the core thesis and at least one per-section commitment
- `research/temp/synthesis-outline.md` — must include one outline entry per H2 in the planned structure
- `research/temp/synthesis-conflicts.md` — exists (may say "no conflicts found")
- `research/temp/draft-{a,b}.md` — both exist

If any are missing or trivial, fix them before proceeding. The synthesizer cannot do strategic planning — it can only execute the plan. Skipping plan/outline produces a thin synthesizer output that doesn't beat the original drafts.

---

## Step 11.6 — Spawn the synthesizer

Spawn ONE `bad-research-synthesizer` subagent. Single spawn, runs once.

**Spawn template:**
```
subagent_type: bad-research-synthesizer
prompt: |
  RESEARCH QUERY (verbatim, gospel):
  > {{paste research/query-<vault_tag>.md body}}

  QUERY FILE: research/query-<vault_tag>.md

  PIPELINE POSITION: You are step 11 of the Bad Research pipeline.
  Step 10 produced 2 angle-specific drafts. The orchestrator wrote a
  synthesis plan and outline. You read everything and write the final
  report in TWO passes (pass 1 = rough integrated draft, pass 2 = voice/
  redundancy/length cleanup). You are tool-locked to [Read, Write] — you
  cannot Bash, cannot spawn subagents. After you return, step 12 (4
  critics) reads your final report.

  YOUR INPUTS:
  - query_file_path: research/query-<vault_tag>.md
  - draft_paths: [research/temp/draft-a.md, research/temp/draft-b.md]
  - synthesis_plan_path: research/temp/synthesis-plan.md
  - synthesis_outline_path: research/temp/synthesis-outline.md
  - synthesis_conflicts_path: research/temp/synthesis-conflicts.md
  - synthesis_evidence_path: research/temp/synthesis-evidence.md
  - decomposition_path: research/prompt-decomposition.json
  - tensions_path: research/temp/tensions.md
  - evidence_digest_path: research/temp/evidence-digest.md
  - pass1_output_path: research/temp/synthesis-pass1.md
  - final_output_path: research/notes/final_report_<vault_tag>.md
  - response_format: "<short|structured|argumentative>"
  - citation_style: "<wikilink|inline|none>"

  Read everything. Write pass 1 to pass1_output_path. Then audit pass 1
  for redundancy, voice consistency, weak sections, and length, and
  write the cleaned pass 2 to final_output_path. Do not paste paragraphs
  from the input drafts — synthesize them in your own voice.

  REALISM: when a section estimates software or technical effort/timeline,
  assume an agentic-coding world — think hours-to-days, never weeks or
  months — be realistic, and omit calendar estimates unless the query
  explicitly asks for one.

  GENERATION-TIME GROUNDING (non-negotiable): cite as you write, in
  pass 1. Every factual sentence — anything with a number, named entity,
  comparative/superlative, or causal/temporal claim — MUST end with its
  citation token BEFORE the terminal period. Use the LINE-ANCHORED form:
  `… grew 12.4% in 2024 [[note-id:Lstart-Lend]].` where `Lstart-Lend` comes
  directly from the chunk's `(line_start, line_end)` in synthesis-evidence.md.
  Do NOT invent line numbers — copy them verbatim from the evidence file. If
  citation_style == "inline", render `[N:Lstart-Lend]` and add `(L<start>-L<end>)`
  after the URL in the Sources section. Do NOT write an
  ungrounded integrated draft and add citations in pass 2 — ground it the
  first time, while the source chunk in synthesis-evidence.md is in front
  of you. Every marker corresponds to a chunk in synthesis-evidence.md
  whose quoted_support is in claim_anchors; a claim with no locatable
  anchor is NOT written. Non-factual sentences (the executive-summary
  topic sentence, transitions, framing, hedge-frame openers, questions)
  stay uncited — do not bolt on decorative cites. This keeps the
  step-16 `bad uncited-gate` a cheap VERIFIER over a clean draft (0–few
  blocks) instead of a heavy block-and-patch rewriter — the ~2× cost the
  benchmark exposed when drafts were grounded after the fact.
  EXEMPTION: when citation_style == "none", emit NO markers (the
  rule above doesn't apply, and the uncited-gate is not a ship-block) —
  the discipline survives only as sourcing: write claims you *could*
  cite, but render no tokens.

  SOURCE-QUALITY RECONCILIATION (non-negotiable): synthesis-evidence.md
  carries each cited note's source_quality_flags (the fetcher's per-source
  epistemic judgment — marketing_spin / nameless_source / unconfirmed /
  cherry_picked / etc.). This is where those flags are RECONCILED (the
  worker flags, the lead reconciles — there is NO deterministic penalty
  upstream). When a chunk's source carries any flag: NEVER lead with its
  claim; state it plainly ONLY if an unflagged source corroborates it
  (cite both); otherwise HEDGE it explicitly, naming the weakness the flag
  identifies ("one vendor account claims…", "an unconfirmed report
  suggests…"). A flag down-weights and caveats — it does not delete (a
  spin page on a high-authority domain becomes a hedged/supporting mention,
  never a load-bearing un-caveated claim). An unflagged source (empty
  flags) is written exactly as the grounding rule dictates. Flag, don't
  suppress.

  **Citation rendering:**
  - If citation_style == "wikilink" (default): every citation is a
    `[[note-id]]` marker pointing at the source note in the vault. No
    separate `## Sources` section. The wiki-link IS the citation —
    readers click through to the source note's frontmatter for title +
    URL. Do NOT add numbered references.
  - If citation_style == "inline": every citation is a `[N]` marker,
    AND the report ends with a `## Sources` section listing each cited
    source as `[N] Title. URL` (read each cited note's YAML frontmatter
    for title + URL).
  - If citation_style == "none": no citation markers anywhere, no
    Sources section.
```

**CRITICAL: never emit bare text while the synthesizer is running.** It will take 5-15 minutes (two passes). Use the wait time to think — append notes to `research/temp/orchestrator-notes.md` about what you'll watch for in step 12 (the critics) based on the synthesis plan you just wrote.

---

## Step 11.7 — Validate the synthesizer output

When the synthesizer returns:

1. **Confirm both files exist:**
   - `research/temp/synthesis-pass1.md` (pass 1, rough integrated)
   - `research/notes/final_report_<vault_tag>.md` (pass 2, final)

2. **Read the synthesizer's report-back.** It tells you:
   - Word/character count
   - Pass 1 vs pass 2 length delta (should be NEGATIVE — pass 2 cuts)
   - Top redundancies cut
   - Top voice fixes
   - Sections flagged as still weak

3. **Sanity checks on the final report:**
   - Length is in the target range for `response_format` (not 3x)
   - Has all H2s from `required_section_headings`
   - Citations match `citation_style`: `[[note-id]]` markers for `"wikilink"` (no Sources section); `[N]` markers + a `## Sources` section for `"inline"`; no markers for `"none"`
   - No YAML frontmatter, no scaffold leaks, no pipeline vocabulary

If pass 2 is longer than pass 1 (positive delta), something went wrong — pass 2 is supposed to cut. Investigate before proceeding.

If a sanity check fails, hand-craft an Edit on `research/notes/final_report_<vault_tag>.md` yourself to fix it. Do NOT re-spawn the synthesizer — that's regeneration, which violates the patch-not-regenerate invariant once we have a final draft.

---

## Write-once after synthesis

After this step, the final report is only modified by Edit hunks from the patcher (step 14) and polish auditor (step 15). Do NOT re-write or re-synthesize.

---

## Exit criterion

- `research/notes/final_report_<vault_tag>.md` exists, length in target range
- `research/temp/synthesis-pass1.md` exists (debugging artifact)
- All H2s from `required_section_headings` present
- Citations match `citation_style` (wikilink → `[[note-id]]` no Sources section; inline → `[N]` + Sources section; none → no markers)
- No YAML frontmatter, no pipeline vocabulary, no scaffold leaks

---

## Next step

Return to the entry skill (`bad-research`). Invoke step 12:

```
Skill(skill: "bad-research-12-critics")
```
