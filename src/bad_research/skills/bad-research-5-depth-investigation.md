---
name: bad-research-5-depth-investigation
user-invocable: false
description: >
  Step 5 of the Bad Research pipeline (full tier) — spawns one depth-investigator
  per scored locus in parallel; each reads full sources and writes an interim note
  ending in a Committed Position.
---

# Step 5 — Depth investigation (parallel, K = len(loci))

**Tier gate:** SKIP entirely for `light` tier. Only `full` tier runs depth investigation.

**Goal:** produce ONE `interim-{locus}.md` note per locus with dense synthesis that the draft sub-orchestrators (step 10) will draft from. Each note ends in a **Committed Position** (a one-paragraph declarative stance on the locus — not a both-sides summary).

---

## Recover state

Read these inputs:
- `research/scaffold.md` — vault_tag
- `research/loci.json` — scored loci with source_budget per locus, plus the `"fanout"` key step 4 wrote (arrangement + ordered loci)
- `research/prompt-decomposition.json` — **`query_shape`** (decides parallel vs sequential vs single — see step 1 below)
- `research/temp/contradiction-graph.json` (written by step 4.0)
- `research/query-<vault_tag>.md` — canonical research query

---

## Procedure

0. **Branch the fan-out on `query_shape`** (the arrangement step 4 recorded in `research/loci.json`'s `"fanout"` key; Claude Research `research_lead_agent.md:12-29`). The shape is orthogonal to the tier — it decides only how the investigators are *arranged*:

   - **`breadth_first` → PARALLEL.** Spawn K investigators in ONE message (true parallel), **importance-ordered** (highest composite-score locus first), `K = min(n_loci, 6)`. Independent loci, gathered simultaneously. This is the default path (step 1 below).
   - **`depth_first` → SEQUENTIAL.** Run **2–4 perspectives on the ONE** highest-impact locus, **one at a time**: spawn perspective 1, wait for its committed position, then spawn perspective 2 with the prior perspective's committed position pasted into its prompt ("here is the position the preceding perspective committed to — extend, challenge, or steelman it"), and so on for 2–4 rounds. Going deep on a single topic from many angles, each building on the last. Do NOT spawn them in parallel — the sequential read of the prior's position is the whole point.
   - **`straightforward` → SINGLE.** Spawn exactly one investigator on the one locus that matters. No ensemble, no sequence.

   Absent a `query_shape` (older runs), use the parallel path (step 1).

1. **`breadth_first` / default — Spawn K `bad-research-depth-investigator` subagents in parallel** (ONE message, all Task calls). One per locus with `source_budget > 0`, capped at 6, **importance-ordered**.

   **Spawn template** (carries the 7-field delegation contract — the four added
   fields `objective`, `output_shape`, `tools_allowed`, `stop_conditions` appear
   as the uppercase blocks below):
   ```
   subagent_type: bad-research-depth-investigator
   prompt: |
     RESEARCH QUERY (verbatim, gospel):
     > {{paste research/query-<vault_tag>.md body}}

     QUERY FILE: research/query-<vault_tag>.md

     PIPELINE POSITION: You are step 5 (depth-investigator) of the
     Bad Research pipeline. Step 4's loci analysts produced research/loci.json;
     after you return, step 6 will reconcile your committed position against
     the other investigators' positions in research/temp/tensions.md.

     YOUR LOCUS (from research/loci.json):
     - name: "<locus name>"
     - one_line: "<one-line locus description>"
     - flavor: "dialectical" / "synthesis" / "technical"
     - source_budget: <integer from loci.json>
     - rationale: "<why this locus matters>"

     YOUR INPUTS:
     - corpus_tag: <vault_tag>
     - locus_name: <locus name>
     - source_budget: <hard cap on additional sources you can fetch>

     OBJECTIVE: investigate the assigned locus to a committed position, grounding
     every claim in primary sources.

     OUTPUT_SHAPE: an interim note ending in `## Committed position`, plus a claims
     JSON array of {claim, note_id, quoted_support, char_start, char_end}.

     TOOLS_ALLOWED: ["fetch_url", "web_search", "Read", "Write", "execute_python"]

     STOP_CONDITIONS: halt when the locus is investigated to a committed position OR
     you reach the fetcher tool-call cap (FETCHER_TOOLCALL_CAP) OR INVESTIGATOR_TIMEOUT_S
     (900s) elapses — then return your committed position with the evidence gathered so
     far. Do not keep searching for nonexistent sources. Hard kill at SUBAGENT_SOURCE_KILL (100).

     SEARCH-LINE PIVOT RULE: When a search line shows no progress — 3 consecutive
     searches on the same sub-question return 0 relevant results — STOP that line
     and explicitly state the pivot to a different hypothesis:
     "Switching direction: [previous approach] is not surfacing sources.
     Trying [new approach/hypothesis]." Write the pivot announcement to
     `research/temp/orchestrator-notes.md` so the lead can track what was tried
     and what was abandoned. Do NOT silently iterate on a dead query line.

     CRITICAL: Read the full source text of relevant vault notes (via
     `hyperresearch note show <id1> <id2> ... -j`) BEFORE writing your
     interim note. Drafting from summaries alone produces paraphrase;
     drafting from full text produces synthesis. Use your source_budget
     to fetch additional sources beyond the width corpus if needed.

     <!-- source-quality-signals -->
     SOURCE-QUALITY NEGATIVE SIGNALS (flag, do NOT silently drop or suppress):
     as you read each full source, judge it against the Anthropic worker-prompt
     list and record any that apply as a `source_quality_flags` array on the
     interim note (the lead reconciles flags downstream — flag, don't suppress):
     `aggregator` (news aggregator, not the original), `false_authority` (cites
     authority it lacks), `nameless_source` ("experts say"), `vague_qualifier`
     ("many"/"often", no specifics), `unconfirmed` (unverified rumor),
     `marketing_spin` (promotional/sales copy), `speculation` (incl. future-tense
     "could"/"may" projections stated as things that happened), `cherry_picked`
     (selective evidence, no counter-data). A flagged source is caveated or
     corroborated at synthesis, never suppressed.

     OUTPUT: Write a single interim note via the hyperresearch CLI with
     type=interim, tags = <vault_tag> + locus-<locus-name>. The note MUST
     end with a "## Committed position" section that takes a SIDE on the
     dialectical question (or a synthesis verdict for non-dialectical
     loci). Include calibration: confidence level, what evidence would
     change your mind.
   ```

   Each investigator's hard cap is `locus.source_budget`, not a flat number.

   **`depth_first` — SEQUENTIAL perspectives (one locus, 2–4 angles).** When `query_shape == depth_first`, do NOT use the parallel spawn above. Instead, on the single highest-impact locus, run 2–4 investigators one at a time:
   1. Spawn perspective 1 with the spawn template above (but `analytical perspective: "<angle 1, e.g. the economic lens>"`). Wait for it to write its interim note and return its committed position.
   2. Spawn perspective 2 with the **prior perspective's committed position pasted into the prompt**: add a `PRIOR COMMITTED POSITION` block — *"The preceding perspective committed to: <quote>. Read it, then investigate this locus from <angle 2>; extend it where the evidence agrees, challenge or steelman it where it doesn't."* Each perspective reads the prior's committed position so the sequence accumulates depth rather than repeating.
   3. Repeat for perspectives 3–4 if the locus warrants it (importance/uncertainty high). Stop at 4.
   The interim notes are distinguished by `perspective-<n>` in their tags. Step 6 reconciles the sequence's committed positions into one.

   **Hard sources (JS-heavy, login-walled, anti-bot):** when a load-bearing
   source fails a Tier-0/1 fetch (returns junk or a login wall), escalate it
   through the Tier 0→3 browse ladder instead of giving up:

   ```bash
   bad fetch "<url>" --tier-max 3 --tag <vault_tag> \
       --instruction "extract the section about <topic>" --json
   ```

   Tier 0 = HTTP, Tier 1 = crawl4ai (JS render), Tier 2 = typed extract
   (AgentQL / LLM-extract), Tier 3 = agentic browse (Browser-Use self-host).
   Escalation is gated by `looks_like_junk()` / `looks_like_login_wall()` — only
   hard pages climb the ladder; cheap pages stop at Tier 0. The SSRF guard
   refuses any private/loopback/metadata URL before the fetch runs.

2. **Each investigator writes ONE interim note** into the vault with `type: interim` and tags `<vault_tag>` + `locus-<locus-name>`. Return value is the note id.

3. **Wait for all K to complete.** Investigators can fail independently. Proceed with whichever succeeded. If >50% failed, stop and reassess loci quality with the user.

4. **Read the interim notes.** After all return, list them:
   ```bash
   bad search "" --tag <vault_tag> --type interim --json
   ```
   Then batch-read them:
   ```bash
   bad note show <id1> <id2> ... -j
   ```
   Hold the Committed Position sections in your context — they are the load-bearing input to step 6 (cross-locus reconciliation).

**INVARIANT:** Every interim note ends with a `## Committed position` section. An interim note ending with descriptive summary only is defective — flag it and re-spawn that investigator with the committed-position requirement emphasized.

---

## Exit criterion

- One interim note per locus with `source_budget > 0`, each tagged `<vault_tag>` + `locus-<locus-name>`
- Every interim note ends with `## Committed position`

If >50% of investigators failed: stop and escalate.

---

## Next step

Return to the entry skill (`bad-research`). Invoke step 6:

```
Skill(skill: "bad-research-6-cross-locus-reconcile")
```
