---
name: bad-research-14-patcher
user-invocable: false
description: >
  Step 14 of the Bad Research pipeline (full tier) — spawns the Read+Edit-locked
  patcher to apply critic, grader, and verifier findings as surgical Edit hunks
  (patch, never regenerate). Produces research/patch-log.json and edits the final report in place.
---

# Step 14 — Patch pass

**Tier gate:** SKIP entirely for `light` tier (no critics = no findings to patch). For `full`: run as documented.

**Goal:** apply critic findings to the draft as surgical Edit hunks (targeted Edit diffs that change only the affected spans — no regeneration of whole sections). Zero regeneration.

---

## Recover state

Read these inputs:
- `research/scaffold.md` — vault_tag
- `research/notes/final_report_<vault_tag>.md` — the synthesized final report from step 11
- All `research/critic-findings-*.json` files — 5 critic findings files on full tier (count may vary by tier)
- `research/temp/evidence-digest.md` — patcher's primary citation source
- `research/query-<vault_tag>.md` — canonical research query

---

## Step 14.0 — Skip gate (optional)

Before spawning the patcher, check whether `research/skip-patcher.txt` exists. If it does, the invoker has requested that step 14 be bypassed. In that case, skip to "Skip path" below.

**Skip path:** Record a minimal log:

```bash
python -c "
import json, pathlib
files = ['research/critic-findings-dialectic.json','research/critic-findings-depth.json','research/critic-findings-width.json','research/critic-findings-instruction.json','research/critic-findings-assumption.json']
total = sum(len(json.loads(pathlib.Path(f).read_text()).get('findings',[])) for f in files if pathlib.Path(f).exists())
pathlib.Path('research/patch-log.json').write_text(json.dumps({'total_findings': total, 'applied': [], 'skipped': [{'reason': 'patcher-skipped-by-invoker'}], 'conflicts': [], 'orchestrator_escalated': []}))
"
```

Then proceed to step 15. Most runs should not use this gate.

---

## Step 14.1 — Pre-create the patch log stub

The patcher is tool-locked to `[Read, Edit]` — it cannot Write. Edit can only modify files that already exist. So you (the orchestrator) MUST write the canonical stub first, which the patcher will then Edit to populate:

```bash
echo '{"total_findings": 0, "applied": [], "skipped": [], "conflicts": [], "orchestrator_escalated": []}' > research/patch-log.json
```

The schema above is canonical. The patcher's only job on this file is to Edit the existing keys — `total_findings` becomes an integer, the four arrays get populated. **The patcher MUST NOT invent alternate schemas** — downstream tooling assumes the canonical shape.

If you skip this step the patcher will silently have nowhere to write its log, will inline the log in its response instead, and you may mis-capture or drop the data entirely.

---

## Step 14.2 — Spawn the patcher

Spawn ONCE.

**Spawn template:**
```
subagent_type: bad-research-patcher
prompt: |
  RESEARCH QUERY (verbatim, gospel):
  > {{paste research/query-<vault_tag>.md body}}

  QUERY FILE: research/query-<vault_tag>.md

  PIPELINE POSITION: You are step 14 (patcher) of the Bad Research
  pipeline. Step 12 produced critic findings; step 13 filled vault gaps.
  After you return, step 15 (polish auditor) does the final hygiene pass.
  You are TOOL-LOCKED to [Read, Edit] — you cannot Write.

  YOUR INPUTS:
  - draft_path: research/notes/final_report_<vault_tag>.md
  - findings_paths: [
      research/critic-findings-dialectic.json,    (full tier only)
      research/critic-findings-depth.json,        (full tier only)
      research/critic-findings-width.json,
      research/critic-findings-instruction.json,
      research/critic-findings-assumption.json,   (full tier only; B-1 assumption critic)
      research/critic-findings-grader.json        (full tier only; Step 12.5 grader loop, if present)
    ]
  - patch_log_path: research/patch-log.json   (already stubbed)
  - evidence_digest_path: research/temp/evidence-digest.md
```

The patcher's job:
- Apply each finding's patch as an Edit on the draft file
- Populate the pre-stubbed patch log via Edit on `research/patch-log.json`
- Each Edit hunk stays surgical: change as little as possible while addressing the issue
- Reject findings that don't serve the research_query (the patcher checks every finding against the canonical query)
- Escalate findings that require structural restructure (rather than applying them as oversized patches)

---

## Step 14.2b — Confidence-band hedging

The step 11.5 citation verifier wrote a `confidence_band` (high / medium / low)
per cited sentence into `research/temp/citation-verify-actions.json`, derived from
`verify_score` × the fetcher's self-reported confidence × the independent-source
count (`research/temp/consensus-claims.json`). The patcher MUST add a band-
appropriate hedge to any **medium / low** claim the synthesizer asserted too
confidently — WITHOUT changing the citation or the number:

| `confidence_band` | prose treatment |
|---|---|
| `high` (fetcher=high AND verify_score≥0.70 AND n_sources≥2) | assert plainly, no hedge |
| `medium` (verify_score 0.40–0.70 OR n_sources==1) | "the evidence suggests…" / "one source reports…" |
| `low` (verify_score<0.40 OR fetcher=low) | "preliminary…" / "a single commentary claims…" |

Keep the raw 0.0–1.0 score OFF the page (it lives on `claim_anchors.verify_score`
for the CLI/audit only). The prose carries only the hedge word. This is a patcher
finding like any other — a surgical Edit that prepends the hedge frame; if the
sentence is already hedged at the right band, no edit.

The patcher spawn prompt (Step 14.2) must instruct the subagent: *"For any cited
sentence whose `confidence_band` in citation-verify-actions.json is `medium` or
`low` and which is asserted without a hedge, add the band-appropriate hedge frame
via a surgical Edit. Do not change the citation or any number."*

---

## Step 14.3 — Read the patch log

Check the patch log when the patcher returns:

- **Did the patcher apply all `critical` findings?** If any critical was SKIPPED, that's a pipeline blocker — resolve it yourself before step 15. Options:
  - (a) reject the finding as invalid after re-reading the draft
  - (b) escalate to the user
  - (c) hand-craft an Edit to address it (you have Write/Edit access; the lock applies only to the patcher subagent)

- **Did any findings CONFLICT?** Look at the conflict log. If two critics disagreed and the patcher picked one, consider whether the discarded one was actually more important.

- **Did the patcher log a "patch too large" skip?** That means a critic proposed regeneration in patch clothing. If the finding was critical, re-spawn the critic with a tighter suggestion, or address it yourself with multiple small hunks.

- **Is the patch log still the empty stub?** If yes, the patcher failed to log — its Task result will contain the real log inline. Read the Task result, parse out the JSON, and write it to `research/patch-log.json` yourself via Bash so downstream lint rules see it.

---

## Step 14.4 — Handle orchestrator-escalated findings (structural restructures)

The patcher populates `orchestrator_escalated` with findings where `requires_orchestrator_restructure: true` — most commonly, structural-mirror-check findings from the instruction critic (wrong H2 order / missing required heading / extra H2). The patcher's tool-lock cannot safely move / rename H2 sections, so YOU handle them here, before step 15:

For each entry:
1. Read the `issue` field to understand which H2 in the draft needs to move, be added, or be renamed.
2. Apply the restructure via hand-written Edit calls on `research/notes/final_report_<vault_tag>.md`. You have Write and Edit access — the tool lock applies only to the patcher and polish auditor subagents.
3. Preserve the body content within each H2 section — you are moving / renaming / inserting headings, not regenerating prose. If a new heading is added and its body needs fresh content, write a short evidence-grounded paragraph for it.
4. Log changes in `research/orchestrator-restructure-log.md` (plain markdown, one bullet per change). Nothing reads this file programmatically — no lint rule and no later step opens it. It is the audit trail for edits you made by hand outside the patcher's tool-lock, and it is what the exit criterion below checks you against.
5. Never regenerate a whole section or the whole draft. The "patch not regenerate" invariant still binds you — broader tools but not broader license.

---

## Constraints

- **Do not apply revisions yourself in step 14.2.** You MUST spawn the patcher subagent. Do NOT call Edit directly on `research/notes/final_report_<vault_tag>.md` — the patcher has the tool-lock invariants (surgical-edit discipline, conflict resolution, integrate-don't-caveat rule) baked into its prompt. Bypassing it defeats the entire adversarial-review architecture. If the patcher returns empty, re-spawn it once — don't fall back to doing the work yourself unless step 14.4 escalations require it.

- **Do not re-spawn the patcher on the same findings** unless you've modified the findings. The patcher's second run on identical input is a waste.

---

## Exit criterion

- `research/patch-log.json` exists with `total_findings` set and at least one of `applied` / `skipped` / `conflicts` populated
- All critical findings either applied or resolved by orchestrator
- All `orchestrator_escalated` findings handled (with `research/orchestrator-restructure-log.md` if any structural restructures were applied)
- `research/notes/final_report_<vault_tag>.md` has been edited (or no edits needed if findings were trivial)

---

## Next step

Return to the entry skill (`bad-research`). Invoke step 15:

```
Skill(skill: "bad-research-15-polish")
```
