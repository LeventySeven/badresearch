---
name: bad-research-12-critics
user-invocable: false
description: >
  Step 12 of the Bad Research pipeline (full tier) — spawns 5 adversarial critics
  in parallel against the final report, each writing a findings JSON for the
  patcher (critics never edit the draft).
---

# Step 12 — Adversarial critique (parallel critics)

**Tier gate:**
- **`full` tier** → spawn all 5 critics (the fan-out below).
- **`fast` route** → run the SLIM single-critic section
  (**Light-tier slim critic**, below) — ONE adversarial pass, no fan-out, no patcher —
  then proceed to step 15 (polish). (E3: the cheap route used to skip straight to polish
  with no adversarial pass at all; this gives it one.)

**Goal:** independent findings lists against the synthesized final report, each from a
different adversarial angle. Critics complement rather than duplicate.

---

## Light-tier slim critic (`fast` route)

On the `fast` route there is no 4-critic fan-out and no patcher
(step 14). Instead, spawn ONE slim critic — the `bad-research-light-critic` agent — that
merges the **dialectic** angle (ignored / straw-manned counter-evidence) and the
**instruction** angle (atomic items the prompt named that the draft missed, under-covered,
reordered, or reformatted) into a single adversarial pass. The full-tier fan-out below is
NOT run on these routes.

1. **Spawn the single light critic** (standard 3-piece contract):
   ```
   subagent_type: bad-research-light-critic
   prompt: |
     RESEARCH QUERY (verbatim, gospel):
     > {{paste research/query-<vault_tag>.md body}}

     QUERY FILE: research/query-<vault_tag>.md

     PIPELINE POSITION: You are the light-tier step 12 (slim single critic) of the
     Bad Research pipeline. The draft is at research/notes/final_report_<vault_tag>.md
     (the fast-route planner→writer loop). There is NO patcher on
     this route; after you return, the orchestrator applies your CRITICAL findings inline,
     then runs step 15 (polish).

     YOUR INPUTS:
     - draft_path: research/notes/final_report_<vault_tag>.md
     - decomposition_path: research/prompt-decomposition.json
     - output_path: research/critic-findings-light.json
     - vault_tag: <vault_tag>
   ```

2. **Apply findings inline (no patcher on this route).** Read
   `research/critic-findings-light.json`. Apply every `critical` finding to the report
   with a single surgical Edit each (insert a sentence / qualifier / citation, or add the
   missing atomic item) — NEVER a regeneration (the no-regenerate invariant holds on every
   route). Surface `major`/`minor` findings the budget can't absorb; do not force them.
   If a `critical` finding needs a structural restructure, handle it yourself as a hand-
   crafted Edit, exactly as step 15.3 does for polish escalations.

3. **Then proceed to step 15 (polish).** The slim critic + inline application IS the
   adversarial layer for these routes; do NOT add the full-tier fan-out below.

---

## Full-tier critics (`full` tier ONLY)

## Recover state

Read these inputs:
- `research/scaffold.md` — vault_tag
- `research/prompt-decomposition.json` — pipeline_tier, atomic items
- `research/notes/final_report_<vault_tag>.md` — merged draft from step 10
- `research/query-<vault_tag>.md` — canonical research query

---

## Procedure

1. **Spawn the critics in parallel.** In ONE message.

   **The three that always run — these are the ones that find errors:**
   - `bad-research-assumption-critic` → `research/critic-findings-assumption.json`
     (top-5 highest-stakes causal/quantitative claims decomposed into sub-assumptions;
      limit scope to 5 claims; output verified/unverified/contradicted per sub-assumption)
   - `bad-research-dialectic-critic` → `research/critic-findings-dialectic.json` (counter-evidence the draft missed or straw-manned)
   - `bad-research-instruction-critic` → `research/critic-findings-instruction.json` (atomic items from the decomposition that the draft missed, under-covered, reordered, or reformatted)

   **The fourth, conditional — coverage:**
   - `bad-research-width-critic` → `research/critic-findings-width.json` (corpus clusters the draft ignores despite evidence). **Run it only when the draft is at or under its length band.** Over the band, its findings are unusable by construction: every one of them proposes an addition, and the patcher is already cutting.
   - `bad-research-depth-critic` → `research/critic-findings-depth.json` — **fold into the width critic's prompt rather than spawning separately.** Both ask "what should the report also say"; the difference between "a topic the corpus supports that is missing" and "a passage that is thinner than the corpus allows" is not worth a second full read of the report and the vault.

   ### Why this is four and not five (2026-09-15, measured)

   On a `full` + `structured` run the five critics cost 481K tokens. Tracing every finding through to the
   patch log: **assumption, dialectic and instruction produced the findings that were applied** — a
   contradicted causal mechanism in a load-bearing argument, a licence carve-out on the recommended model
   that the report explicitly denied, two benchmark numbers compared across incompatible tasks, four
   miscited sources, and four entities the prompt named that the report had dropped. **Width and depth
   produced 22 findings of which the patcher applied six and logged five as skipped-on-length-grounds** —
   because the draft was 40% over its band and every width/depth finding asks for more words.

   The lesson is not that coverage critique is worthless. It is that **a coverage critic run against an
   over-length draft is structurally guaranteed to be wasted**, and the pipeline knew the draft was over
   length before it spawned them. Gate on that instead of paying for it.

   Two other things that run pass the same test and should be preferred over a fifth critic: the step-11.5
   citation verifier when the citation style lets it resolve, and — when it cannot — a host-model
   fact-verifier over the highest-stakes numeric and licence claims. On the measured run the fact-verifier
   cost 281K and found three miscitations and a wrong number that no critic caught, because it was the only
   agent re-reading sources against the text rather than reasoning about the text.

2. **Pass each critic** (standard 3-piece contract):
   ```
   subagent_type: bad-research-<critic-name>-critic
   prompt: |
     RESEARCH QUERY (verbatim, gospel):
     > {{paste research/query-<vault_tag>.md body}}

     QUERY FILE: research/query-<vault_tag>.md

     PIPELINE POSITION: You are step 12 (<critic-name> critic) of the
     Bad Research pipeline. Step 11 (synthesizer) produced the final report at
     research/notes/final_report_<vault_tag>.md. After you return, step 13 may run a
     gap-fetch wave, then step 14 (patcher) applies findings as Edit hunks.

     YOUR INPUTS:
     - draft_path: research/notes/final_report_<vault_tag>.md
     - output_path: research/critic-findings-<critic-name>.json
     - vault_tag: <vault_tag>
     - decomposition_path: research/prompt-decomposition.json   (instruction-critic only)
   ```

   **SOURCE-QUALITY HONOR CHECK (width + instruction critics).** The width-sweep
   fetchers and depth-investigators recorded a `source_quality_flags` array on
   each note (flag, do NOT suppress — the flags survive to here). The width and
   instruction critics MUST honor them: a source carrying any flag must NOT be
   presented in the report as established fact without its caveat. Emit a finding
   whenever such a flagged source is cited bare (as plain fact, with no hedge or
   corroborating unflagged source).
   <!-- source-quality-signals -->
   Flags to honor: `aggregator`, `false_authority`, `nameless_source`,
   `vague_qualifier`, `unconfirmed`, `marketing_spin`, `speculation`,
   `cherry_picked`. Flag, don't suppress — surface the bare citation as a finding
   for the patcher rather than dropping the source.

3. **Wait for all critics.** If one fails, you can proceed with the partial set, but log the absence to the run log — the patch pass is less robust with missing critic coverage. **Do NOT skip the instruction-critic specifically** — it's the only critic measuring prompt adherence, which is the dimension with the widest variance.

4. **Do not read the findings yourself and apply them.** The patcher (step 14) reads the findings. Your job is to hand them to the patcher — AFTER step 13 (gap-fetch) runs.

---

## Exit criterion

- All 5 critic findings JSONs exist (`research/critic-findings-<name>.json`)
- Each is valid JSON with a `findings` array

---

## Next step

Return to the entry skill (`bad-research`). Invoke step 13:

```
Skill(skill: "bad-research-13-gap-fetch")
```
