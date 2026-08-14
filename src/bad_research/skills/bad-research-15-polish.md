---
name: bad-research-15-polish
user-invocable: false
description: >
  Step 15 of the Bad Research pipeline — spawns the Read+Edit-locked
  polish-auditor for the hygiene + filler pass (strips pipeline-reference leaks,
  frontmatter, scaffold sections, filler) before the step 16 readability audit.
---

# Step 15 — Polish audit

**Tier gate:** Runs for ALL tiers. Every report gets a polish pass regardless of tier.

**Goal:** final hygiene + readability pass. Tool-locked to `[Read, Edit]`.

---

## Recover state

Read these inputs:
- `research/notes/final_report_<vault_tag>.md` — the patched draft from step 14 (or single-pass draft for light tier)
- `research/query-<vault_tag>.md` — canonical research query

---

## Step 15.1 — Pre-create the polish log stub

The polish auditor has `[Read, Edit]` only and cannot create a new file (same tool-lock rule as the step 14 patcher). Stub it first:

```bash
echo '{"applied": [], "escalations": []}' > research/polish-log.json
```

---

## Step 15.2 — Spawn the polish auditor

Spawn ONCE.

**Spawn template:**
```
subagent_type: bad-research-polish-auditor
prompt: |
  RESEARCH QUERY (verbatim, gospel):
  > {{paste research/query-<vault_tag>.md body}}

  QUERY FILE: research/query-<vault_tag>.md

  PIPELINE POSITION: You are step 15 (polish auditor) of the
  Bad Research pipeline — the hygiene pass. Step 14 (patcher) applied
  critic findings as Edit hunks. After you return, the orchestrator
  runs step 16 (readability audit) and the final integrity gate, then
  ships. You are TOOL-LOCKED to [Read, Edit].

  YOUR INPUTS:
  - draft_path: research/notes/final_report_<vault_tag>.md
  - polish_log_path: research/polish-log.json   (already stubbed)
```

The polish auditor strips:
- **Pipeline reference leaks**: `[I\d+]` references, `[[interim-*]]` wiki-links pointing at workspace artifacts (NOT source notes), references to scaffold/comparisons/synthesis-plan files in prose. **Citation wiki-links** of the form `[[<source-note-id>]]` (where the target is a real source note in the vault, not an interim/scaffold workspace file) are PRESERVED when `citation_style == "wikilink"` — they are the citation system, not a leak. Strip wikilinks only when `citation_style` is `"inline"` or `"none"`.
- Hygiene leaks (YAML frontmatter, scaffold sections, prompt echoes)
- Filler phrases ("It is worth noting", "Importantly", etc.)
- Redundant sentences / paragraphs that restate prior content

**Do NOT reformat structure here** (run-on/paragraph splitting, list/table conversion,
paragraph rhythm). That is step 16's job, and step 16 owns it on purpose: it uses the
judgment-safe *recommend-then-apply* mechanism (the recommender proposes, the orchestrator
decides), because a direct-Edit reformatter "sometimes makes changes that hurt the argument —
converting a flowing paragraph to a bullet list when the prose was load-bearing." Splitting a
run-on here via blind Edit is exactly that hazard, and doing it in both steps is duplicate work.
Polish is hygiene + filler + redundancy (a NEGATIVE net-char cut); structural readability is
step 16.

---

## Step 15.3 — Handle escalations

The polish auditor ESCALATES structural mismatches (wrong format for the prompt, missing required sections, etc.) rather than fabricating content to fix them. Read the escalations in the polish log.

If the escalation names a structural issue (e.g., "user asked for a ranked list; draft is unranked prose"), you have one shot to fix it — craft the restructure yourself with hand-written Edits, then ship.

**Sanity-check net length.** Polish should have NEGATIVE net char delta. If the polish log shows positive net chars added, something went wrong — polish is for cutting, not expanding.

**Do not apply polish edits yourself in step 15.2.** The polish auditor's tool lock is the mechanism. Calling Edit directly bypasses the hygiene-check and filler-detection logic baked into the auditor's prompt. If the auditor returned empty, re-spawn it; don't do the work yourself unless step 15.3 escalations require it.

---

## Step 15.4 — Final integrity gate

Before declaring the run complete, verify every expected pipeline artifact exists. **The required set depends on the tier:**

- **light tier:** only `research/polish-log.json` is required (steps 12–14 are skipped, so no critic findings or patch log).
- **full tier:** require all five critic findings (incl. assumption) + grader-log + patch-log + polish-log:

```bash
for f in research/critic-findings-dialectic.json \
         research/critic-findings-depth.json \
         research/critic-findings-width.json \
         research/critic-findings-instruction.json \
         research/critic-findings-assumption.json \
         research/grader-log.json \
         research/patch-log.json \
         research/polish-log.json; do
  test -f "$f" || echo "MISSING: $f"
done
```

If any artifact is missing, the responsible step failed silently. Re-spawn the responsible agent ONCE with the missing output path as its explicit required output. If it fails a second time, write a minimal stub (`{"findings":[]}` for critic files, canonical empty-log schema for patch-log.json / polish-log.json) and log the failure in the run log before proceeding.

---

## Step 15.5 — Lint gate

Run the deterministic lint rules (or `bad lint --json` for all four at once):

```bash
bad lint --rule wrapper-report --json
bad lint --rule locus-coverage --json
bad lint --rule scaffold-prompt --json
bad lint --rule patch-surgery --json
```

Each rule checks the **presence and shape of one artifact** — none of them reads the
report's prose. Only `error` severity blocks (`bad lint` exits 1); `warning` / `info`
are reported and do not gate. What each rule actually asserts, and what to do:

- `wrapper-report`: at least one `research/notes/final_report_*.md` exists (**error** if
  none — step 11 or the fast writer never landed its file), and each one contains at
  least one citation marker: `[[note-id]]` wikilink, `[^…]`, `[Source …]`, or `[N]`
  (**warning** if a report has none — the polish auditor most likely stripped the
  citation style; re-spawn it with the citation-preservation rule flagged). It does
  NOT detect scaffold leakage — that is the polish auditor's own hygiene pass.
- `locus-coverage`: `research/loci.json` is valid JSON (**error** if not) and a final
  report exists to check against (**error** if none); then every locus `id` must appear
  as a case-insensitive substring somewhere in the report body (**warning** per missing
  locus — a depth investigator's locus never made it into the draft; note it in the run
  log rather than re-running). An absent `loci.json` is `info`, not a failure — the
  light tier has no step 4.
- `scaffold-prompt`: `research/scaffold.md` exists (**error** if not) and contains a
  markdown **heading** matching `#+ User Prompt` followed by non-empty content
  (**error** if the heading is missing or its section is empty). It never opens the
  query file, so it cannot tell you the two disagree — it only checks the heading is
  there and not empty. Fix by writing the canonical
  `## User Prompt (VERBATIM — gospel)` heading with the verbatim query under it.
- `patch-surgery`: `research/patch-log.json` parses as JSON (**error** if not) and
  carries at least one canonical key (`total_findings` / `applied` / `skipped` /
  `conflicts` / `orchestrator_escalated`; legacy `hunks` / `patches` also accepted)
  (**warning** if not — step 14 logged an off-schema shape; re-read the patcher's Task
  result and rewrite the log). It measures no churn and never compares drafts. An
  absent log is `info` — expected on the light tier, which has no step 14.

---

## Step 15.6 — Ship

The final report lives at `research/notes/final_report_<vault_tag>.md`. The wrapper's required save path (if any) is a separate copy — handle per the wrapper contract.

---

## Exit criterion

- `research/polish-log.json` populated
- Final integrity gate passed (or stub-filled with documented failure)
- Lint gate passed
- `research/notes/final_report_<vault_tag>.md` is the final, shippable artifact

---

---

## Next step

Return to the entry skill (`bad-research`). Invoke step 16:

```
Skill(skill: "bad-research-16-readability-audit")
```

Step 16 is the final step — readability audit + selective apply. Runs for ALL tiers.
