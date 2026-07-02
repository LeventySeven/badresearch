---
name: bad-research-10-triple-draft
user-invocable: false
description: >
  Step 10 of the Bad Research pipeline — for full tier, builds the evidence digest
  inline (Step 10.0b Part 2, formerly step 9) then spawns 3 parallel
  draft-orchestrators that each write one angle-specific draft from that evidence
  digest plus a per-angle curated note list (step 11 synthesizes them); for light
  tier, writes a single final draft directly. Produces
  research/temp/draft-{a,b,c}.md (full) or the final report (light).
---

# Step 10 — Triple-draft ensemble (curated lists, parallel writers)

**⚠ CRITICAL ANTI-PATTERN: Writing a single draft for `full` tier is a PIPELINE VIOLATION.** **If you find yourself about to write `research/notes/final_report_<vault_tag>.md` directly without spawning 3 `bad-research-draft-orchestrator` subagents, STOP. Re-read this skill. Spawn the sub-orchestrators.** (Light tier is the ONE exception — see "Light tier" section below.)

**Tier gate:** Runs for ALL tiers. For `light` tier: write a single draft directly to `research/notes/final_report_<vault_tag>.md` and skip ahead to step 15 (polish). For `full`: run the triple-draft ensemble below — step 11 (synthesizer) will turn the 3 drafts into the final report.

**Goal:** produce THREE independent angle-specific drafts (`draft-{a,b,c}.md`) — each an *angle-specific draft*, i.e. a full draft written from one assigned analytical stance (e.g. strongest-thesis vs. steelman-contrarian vs. synthesis). Step 11 (synthesizer subagent) consumes all three and writes the final report.

---

## Recover state

Read these inputs:
- `research/scaffold.md` — vault_tag, modality, wrapper requirements
- `research/prompt-decomposition.json` — atomic items, required_section_headings, response_format, citation_style, pipeline_tier
- `research/temp/reflections.md` — the distilled short-term memory (≤3 claim bullets + `cited_note_ids` per round). **PLAN from this, not the raw corpus** — see Step 10.0b
- `research/temp/claims-*.json` (full tier) — per-note distilled claims; Step 10.0b Part 2 below BUILDS `research/temp/evidence-digest.md` (the PRIMARY EVIDENCE LAYER) from these, inline. Absent for light.
- `research/temp/tensions.md` (full tier) — cross-locus + orphan expert disagreements (the merged step-6 artifact; replaces the former `comparisons.md` + `source-tensions.json`)
- `research/temp/coverage-gaps.md` (if exists) — items with weak source coverage
- Survey vault: `bad search "" --tag <vault_tag> -j` for the evidence landscape
- Modality calibration (from the scaffold's `modality` field):
  - **collect** — enumerative coverage, per-entity sections with named fields
  - **synthesize** — defended thesis with evidence chains, interpretive density
  - **compare** — proportionate per-entity depth + a committed recommendation
  - **forecast** — predictive claims grounded in past + present, explicit time horizon

---

## Step 10.0 — Read response_format and citation_style

Read `response_format` and `citation_style` from `research/prompt-decomposition.json`. These control the draft shape:

| Format | Target length | Character |
|--------|-------------|-----------|
| `"short"` | 500–2000 words / 1500–6000 chars (CJK) | Direct answer, compact |
| `"structured"` | 2000–5000 words / 6000–15000 chars (CJK) | Scannable, breadth-first |
| `"argumentative"` | 5000–10000 words / 20000–25000 chars (CJK) | Dense thesis-driven |

**Length discipline:** Target the MIDDLE of the range. Under-length loses on comprehensiveness; over-length dilutes good content.

---

## Step 10.0b — Plan from reflections, re-inject raw only at the end (distilled-reflection memory)

**Plan from the distilled memory, batch-read raw bodies only for what you'll
cite.** This is Tavily's "re-inject raw only at the end": the mid-pipeline carried
only distilled reflections (linear token growth); the drafter pays the raw-body
cost ONCE, at draft time, and only for the `note_id`s it will actually cite.

1. **Plan the draft from `research/temp/reflections.md`** — the ≤3-claim-bullet
   distilled records per round, the `open_gaps`, and the `cited_note_ids`. Decide
   the angle, the section beats, and which claims anchor which section *from the
   distilled reflections*, NOT by re-reading the whole raw corpus. The reflections
   are the short-term memory; trust them.

2. **Then batch-read the raw note bodies ONLY for the `note_id`s you will cite.**
   From the reflections' `cited_note_ids` (and the curated `must_read_note_ids`
   list in Step 10.2), read the raw bodies for just those notes
   (`bad note show <id1> <id2> ... -j`) so you have the verbatim text in front of
   you as you write. Do NOT batch-read notes you don't intend to cite — that
   re-introduces the quadratic-context cost the reflections discipline removed.

3. **Spans survive for grounding.** Re-injecting the raw body for a cited note
   gives you its verbatim `quoted_support` span — keep the exact wording when you
   ground a claim so the downstream `uncited-gate` / `recitation-gate` /
   `anchors.py` verify byte-for-byte. A claim whose supporting span you cannot
   re-locate in the re-injected raw body is dropped or hedged, never fabricated.

**Light tier:** light has no `evidence-digest.md` (it skips Part 2 below); it still
plans from `reflections.md` (written in step 2) and re-injects raw bodies only for
the `cited_note_ids` it will cite (the 8–15 notes it opens — see the Light tier
section below).

---

## Step 10.0b — Part 2: Build evidence digest (inline)

**Full tier only.** Build `research/temp/evidence-digest.md` here, inline, BEFORE
spawning the draft-orchestrators. This replaces the former step 9 invocation — the
evidence digest is now assembled at the top of step 10 rather than as its own stage.
(Skip this Part for `light` tier — light has no evidence digest and writes a single
draft directly per the Light tier section below.)

The digest is the top load-bearing claims + verbatim quotes from the claims JSONs,
assembled into a single file the drafter reads as primary evidence —
higher-fidelity than fetcher summaries. The per-angle source-list curation
(Step 10.2) and each draft-orchestrator both reference it.

`# NOTE (Workstream A): when A lands, carry line_start/line_end per chunk here (converted from char_start/char_end via char_span_to_line_range).`

1. **Read all claims files** from `research/temp/claims-*.json` for every non-deprecated note tagged with the vault tag. If no claim files exist (e.g., fetchers didn't produce them), skip building the digest (the drafter falls back to the curated `must_read_note_ids` raw bodies).

2. **Filter and rank.** Keep claims where `confidence` is `"high"` OR `evidence_type` is `"empirical"` or `"statistical"`. From the remainder, prefer claims with non-empty `numbers` arrays and non-empty `quoted_support`. Cap at **80–120 claims total** for `full` tier.

3. **Group by atomic item.** Match each surviving claim to the atomic item it is most relevant to based on **topic overlap** — do not rely on exact field matching. A claim about "United Health Group regulatory exposure" serves the atomic item "UNH risk factors" even though no field matches exactly. Use the claim's `entities`, `stance_target`, `scope_conditions`, and `claim` text holistically to judge relevance. When uncertain, include the claim under the most relevant item rather than dropping it to Ungrouped. Claims that genuinely don't map to any atomic item go into an "Ungrouped" section at the end.

4. **Include consensus and contested claims.**
   - If `research/temp/consensus-claims.json` exists, include its claims marked as `[consensus]`.
   - If `research/temp/contradiction-graph.json` exists, include the top 3–5 contested claim pairs with both sides' `quoted_support` passages.

5. **Write `research/temp/evidence-digest.md` now (before spawning draft-orchestrators). This replaces the former step 9 invocation.** Format: one H3 per atomic item, bullet list of claims. Each bullet includes:
   - The `claim` text
   - The `quoted_support` verbatim passage (block-quoted) — keep it byte-for-byte so the cited spans survive for the downstream grounding gates
   - The `source_note_id`

   Keep it scannable — this is an evidence index, not a narrative. Target at least 30 claims for `full` tier; if fewer claims exist in total, include all of them.

   Example:
   ```markdown
   ### Atomic item: Market growth in Southeast Asia

   - Annual growth rate of 12.4% in 2024 (empirical)
     > "Southeast Asian e-commerce GMV grew from $89B to $100B between 2023 and 2024, a 12.4% YoY expansion."
     [source-note-12]

   - Vietnam led by penetration rate (statistical)
     > "Vietnam reached 64% e-commerce penetration in 2024, the highest in SEA, surpassing Singapore (61%)."
     [source-note-19]
   ```

---

## GENERATION-TIME GROUNDING — cite as you write (applies to ALL drafts, ALL tiers)

**Ground every factual sentence in the FIRST draft. Do not draft ungrounded prose and "add citations later".** A *factual sentence* is any sentence carrying a number, a named entity, a comparative/superlative, or a causal/temporal claim. Every such sentence MUST end with its citation token placed **before the terminal period** — `… grew 12.4% in 2024 [[note-id]].` (wikilink style) or `… grew 12.4% in 2024 [3].` (inline style). One marker minimum; stack `[[a]][[b]]` when two sources back the same claim.

- **Why:** the downstream `bad uncited-gate` (step 16) is a deterministic ship-block on any uncited factual sentence. If you cite as you write, that gate runs as a cheap **verifier** that finds 0–few blocks. If you defer grounding, the gate becomes a heavy block-and-patch rewriter that re-touches dozens of sentences over many iterations — the ~2× cost the benchmark exposed. Cite-as-you-write moves the cost from a late rewrite to the cheapest possible moment: when the sentence is being written and the source is already in front of you.
- **What does NOT need a citation:** the executive-summary topic sentence, pure transitions/framing ("This section examines…"), hedge-frame openers ("In general,…"), and questions. These are non-factual by the gate's own classifier, so leave them clean — don't bolt on a decorative cite.
- **Anchoring rule:** every `[[note-id]]`/`[N]` you emit MUST point at a source you actually read (light tier: a note you opened; full tier: a note on your `must_read_note_ids`). A claim you cannot ground to a real source is NOT written — drop it or hedge it, never fabricate a marker. The CitationVerifier checks every cite byte-for-byte afterward; fabricated cites are caught and dropped.
- **`citation_style: "none"` exemption:** when the deliverable's `citation_style` is `"none"`, emit NO citation markers — the marker requirement above does not apply, and the uncited-gate is not a ship-block for a no-citation deliverable. The grounding *discipline* still holds at the sourcing level (only write claims you *could* cite to a real note), but the rendered draft carries no tokens.

---

## SOURCE-QUALITY RECONCILIATION — down-weight flagged sources (applies to ALL drafts, ALL tiers)

**This is where the fetcher's `source_quality_flags` are actually reconciled** (the worker FLAGS, the lead RECONCILES — Anthropic's worker-prompt discipline; there is NO deterministic penalty in the funnel/rank code). When the per-source claims you read carry a non-empty `source_quality_flags` array in their `claims-<note-id>.json` (e.g. `["marketing_spin"]`, `["nameless_source"]`, `["cherry_picked"]`), reconcile it in the prose you write — **flag, don't suppress**:

- **Never lead with a flagged-source claim.** A claim drawn from a flagged source is not the topic sentence of a section and is never the sole basis for a headline finding.
- **Corroborate or hedge.** A flagged source's claim is only stated plainly if an *unflagged* source corroborates it (cite both, `[[flagged]][[unflagged]]`). If no unflagged source corroborates it, it is explicitly hedged ("one vendor account claims…", "an unconfirmed report suggests…") — the hedge names the weakness the flag identifies (spin / nameless source / unconfirmed / cherry-picked).
- **A flag down-weights, it does not delete.** The flagged source can still appear — a marketing-spin page on a high-authority domain is demoted to a hedged, corroborated, or supporting mention, never a load-bearing un-caveated claim. This is the report-level analogue of "demote, never drop."
- **An unflagged source is unchanged** (empty `source_quality_flags`) — write its claims exactly as the grounding rule above dictates.

You see the `source_quality_flags` on each claim because step 10.0b re-injects the raw bodies + `claims-*.json` for the `note_id`s you cite; honor the flags as you ground.

---

## Light tier ONLY: single-draft path

If `pipeline_tier == "light"`: SKIP step 10.1 — 10.3 below and follow this section instead.

**Light tier writes a single draft directly to `research/notes/final_report_<vault_tag>.md`.** No subagents, no triple-draft ensemble, no synthesizer.

1. **Read the vault directly.** Light tier has no `evidence-digest.md` (step 9 was skipped). Survey the vault: `bad search "" --tag <vault_tag> -j` and pick the 8–15 most relevant non-deprecated notes. Read each one (`bad note show <id1> <id2> ... -j`) before writing.

2. **Honor the structural contract.**
   - Use the literal H2 headings from `required_section_headings` in `research/prompt-decomposition.json`, in order.
   - Hit the length target from step 10.0's table for the chosen `response_format` (light typically pairs with `short` or `structured`).
   - Apply the modality calibration from the recover-state list above.

3. **Citations.** Apply the **GENERATION-TIME GROUNDING** rule above: every factual sentence ends with its citation token *before* the terminal period, written in the first pass. Three styles:
   - `"wikilink"` (default for non-wrapped runs): every citation is a `[[<source-note-id>]]` marker pointing at the source note in the vault. No separate `## Sources` section. Each wikilink resolves to its source note's frontmatter (title + URL). This is the navigable-vault format.
   - `"inline"` (benchmark + public deliverables): numbered `[N]` citations + a `## Sources` section listing each cited note as `[N] Title. URL` (read each cited note's YAML frontmatter for title + URL).
   - `"none"`: no citation markers anywhere, no Sources section.

4. **Hygiene.** No YAML frontmatter on the final report. No pipeline vocabulary in prose ("hyperresearch", "evidence digest", "comparisons.md", "tensions.md", "committed reading", etc.). When `citation_style == "wikilink"`, `[[<source-note-id>]]` markers ARE the citation system and must be preserved — only strip wikilinks that point at workspace artifacts (interim-*, scaffold, comparisons, tensions). Step 15 (polish) is a backstop, not a license to leak.

5. **Exit and route.** Once `research/notes/final_report_<vault_tag>.md` is written, return to the entry skill and invoke `Skill(skill: "bad-research-12-critics")` for the **light-tier slim single critic** (E3 — one adversarial dialectic+instruction pass, applied inline; no fan-out, no patcher), THEN `Skill(skill: "bad-research-15-polish")`. Light tier skips steps 11 + 13–14 entirely (it runs the slim step-12 critic, not the full 4-critic fan-out + patcher).

---

## Step 10.1 — Define 3 analytical angles (full tier)

Based on the evidence, tensions, and query, assign each sub-orchestrator a distinct angle. The angles should produce genuinely different drafts — not three versions of the same argument.

**For topics with clear tensions/disagreements:**
- **Draft A — Strongest-thesis:** take the position best supported by evidence and argue it forcefully.
- **Draft B — Steelman-contrarian:** take the strongest counter-position seriously. Defend the MINORITY view.
- **Draft C — Synthesis-reconciler:** argue that both sides capture part of the truth. Focus on BOUNDARY CONDITIONS — when does each side's argument hold?

**For topics without clear tensions (surveys, comparisons, collections):**
- **Draft A — Breadth-optimized:** widest possible coverage of all atomic items.
- **Draft B — Depth-optimized:** deeper treatment of the 3-4 most important atomic items.
- **Draft C — Practitioner-optimized:** organized around actionable recommendations.

Write the 3 angle assignments to `research/temp/draft-angles.md` (for the run log). Each angle: 2-3 sentences describing the analytical direction.

---

## Step 10.2 — Curate per-angle source lists

**Critical step.** Each draft sub-orchestrator does NOT decide what to read. YOU pick the 20-50 most relevant vault notes for each angle and pass them as `must_read_note_ids`. This eliminates wasted vault-survey loops in the sub-orchestrators and forces real differentiation by giving each draft a different evidence base.

1. **List all substantive vault notes:**
   ```bash
   bad search "" --tag <vault_tag> --json
   ```
   Filter to non-deprecated notes. You should have 50-100 candidates.

2. **For each draft (A, B, C), pick 20-50 angle-specific notes.** Use these signals:
   - **Source-analysis notes** (`type: source-analysis`): high-value, full digests of long sources. Include relevant ones in EVERY draft's list — these are gold.
   - **Interim notes** (`type: interim`, full tier only): include all of them in EVERY draft's list — these have the committed positions.
   - **For Draft A (strongest-thesis or breadth):** prefer sources that support the dominant evidence direction. Include any source the evidence digest cites for high-confidence claims.
   - **For Draft B (steelman-contrarian or depth):** prefer minority-view or methodological-critique sources. Pull from `research/temp/tensions.md` proponents on the contested side (each tension's per-tension schema lists `side_a`/`side_b` proponents). If `contradiction-graph.json` exists, include the lower-quality-evidence side's sources to force the steelman to engage them.
   - **For Draft C (synthesis or practitioner):** prefer sources with boundary conditions, comparative analyses, or applied case studies. Pull from sources the evidence digest groups under multiple atomic items (cross-cutting sources).

3. **Source overlap is fine.** Drafts can share source IDs — interim notes and key source-analyses should appear in all three lists. Differentiation comes from the angle-specific extras (the 5-15 sources unique to each draft's list).

4. **Cap each list at 50, minimum 20.** For `argumentative` format, lean toward 35-50. For `structured`, lean toward 25-40. For `short`, lean toward 20-30.

5. **Write each list to disk** so the spawn template can reference it:
   - `research/temp/draft-a-source-list.md`
   - `research/temp/draft-b-source-list.md`
   - `research/temp/draft-c-source-list.md`

   Format:
   ```markdown
   # Draft A — must_read_note_ids (n=37)
   Angle: <2-3 sentence angle assignment>

   - <note-id-1>: <one-line summary or title>
   - <note-id-2>: <one-line summary or title>
   ...
   ```

---

## Step 10.3 — Spawn 3 draft sub-orchestrators in parallel

**Spawn 3 `bad-research-draft-orchestrator` subagents in ONE message.** This is true parallel execution. Each gets a different `draft_id`, `analytical_angle`, and (CRUCIALLY) a different `must_read_note_ids` array.

**Spawn template:**
```
subagent_type: bad-research-draft-orchestrator
prompt: |
  RESEARCH QUERY (verbatim, gospel):
  > {{paste research/query-<vault_tag>.md body}}

  QUERY FILE: research/query-<vault_tag>.md

  PIPELINE POSITION: You are one of 3 parallel step 10 sub-orchestrators
  in the Bad Research pipeline. After you and the other two return, the
  main orchestrator runs step 11 (synthesizer subagent) which reads all
  3 drafts and writes the final report. Your draft is an INPUT to that
  synthesis, not the final output.

  YOUR INPUTS:
  - query_file_path: research/query-<vault_tag>.md
  - vault_tag: <vault_tag>
  - draft_id: "a" (or "b" or "c")
  - output_path: research/temp/draft-a.md (or draft-b.md or draft-c.md)
  - analytical_angle: "<the 2-3 sentence angle assignment>"
  - must_read_note_ids: [<paste the IDs from research/temp/draft-<x>-source-list.md, e.g. 30-50 IDs>]
  - decomposition_path: research/prompt-decomposition.json
  - evidence_digest_path: research/temp/evidence-digest.md
  - tensions_path: research/temp/tensions.md
  - response_format: "<short|structured|argumentative>"
  - citation_style: "<wikilink|inline|none>"
  - modality: "<collect|synthesize|compare|forecast>"

  Read every note on must_read_note_ids before writing. Do NOT survey
  the vault — your reading list is curated. Do NOT fetch new sources.
  Write your draft from your assigned angle, citing your curated sources.

  GENERATION-TIME GROUNDING (non-negotiable): cite as you write. Every
  factual sentence — anything with a number, named entity, comparative/
  superlative, or causal/temporal claim — MUST end with its citation
  token BEFORE the terminal period (`… grew 12.4% in 2024 [[note-id]].`).
  Do NOT write an ungrounded draft to be cited later. Every marker points
  at a note on your must_read_note_ids; a claim you cannot ground is
  dropped or hedged, never given a fabricated marker. Non-factual
  sentences (transitions, framing, hedge-frame openers, questions) stay
  uncited. This makes the step-16 uncited-gate a cheap verifier, not a
  rewriter.
```

**CRITICAL: never emit bare text while the 3 sub-orchestrators are running.** They will take 5-15 minutes each. Use this time to think — append notes to `research/temp/orchestrator-notes.md` about the synthesis you'll plan in step 11: what's the strongest thesis emerging across angles? Which atomic items will be contentious? What argumentative beats must the final draft commit to? One vault count check per minute max. Write your thoughts, don't just poll.

---

## Step 10.4 — Validate that all 3 drafts came back

When all 3 sub-orchestrators return:

1. **Confirm all 3 draft files exist:**
   - `research/temp/draft-a.md`
   - `research/temp/draft-b.md`
   - `research/temp/draft-c.md`

2. **Read each sub-orchestrator's report-back.** Each should report:
   - Path to the draft
   - Core thesis
   - How many notes from `must_read_note_ids` it actually read
   - Strongest argumentative beat
   - Word/character count

3. **If a draft is missing or trivially short** (under 1000 chars for argumentative, 500 for structured), re-spawn that single sub-orchestrator with the same inputs. Do not proceed to step 11 with fewer than 3 drafts.

4. **Do NOT synthesize the drafts in this step.** Step 11 (the synthesizer subagent) does that. Your only job here is to ensure 3 valid drafts exist.

---

## Exit criterion

**Light tier:**
- `research/notes/final_report_<vault_tag>.md` exists, hits the length target from step 10.0, follows `required_section_headings`, and respects `citation_style`.

**Standard / full tier:**
- All three drafts exist at `research/temp/draft-{a,b,c}.md`
- Each draft has non-trivial length (1000+ chars argumentative, 500+ structured)
- Sub-orchestrator report-backs are captured (you can paraphrase them in `research/temp/orchestrator-notes.md` for the synthesis plan you'll write in step 11)

---

## Next step

Return to the entry skill (`bad-research`). Tier-based routing:

- **light tier:** You already wrote `research/notes/final_report_<vault_tag>.md` directly. Skip step 11 (synthesis) and steps 13–14 (no gap-fetch, no patcher), but DO run the light-tier slim critic — invoke `Skill(skill: "bad-research-12-critics")` (its **Light-tier slim critic** section: one adversarial dialectic+instruction pass, findings applied inline), THEN `Skill(skill: "bad-research-15-polish")`. (E3: the light route used to skip straight to polish with no adversarial pass.)
- **full tier:** Invoke `Skill(skill: "bad-research-11-synthesize")`.
