---
name: bad-research-6-cross-locus-reconcile
user-invocable: false
description: >
  Step 6 of the Bad Research pipeline (full tier) — reconciles the depth
  investigators' committed positions into cross-locus tensions, then (Step 6.5)
  scans the source bodies for orphan tensions, writing both into a single richer
  research/temp/tensions.md (named tensions with engagement guidance + per-tension
  schema for the draft).
---

# Step 6 — Cross-locus reconciliation + orphan tension scan

**Tier gate:** SKIP entirely for `light` tier (no loci = no tensions). Only `full` tier runs this step.

**Goal:** before drafting, reconcile the committed positions from all depth investigators AND surface the orphan tensions hiding in the source bodies. Produce `research/temp/tensions.md` — a single richer document combining (a) 3–5 cross-locus tensions where the loci conflict or complicate each other, and (b) the orphan tensions that slipped past loci analysis (Step 6.5). This merges the former step 6 (`comparisons.md`) and step 7 (`source-tensions.json`) into one artifact.

**Why this step exists:** the depth investigators each committed to a position on their own locus. Some of those positions disagree, some reinforce each other, some partially complicate each other. The draft must engage those cross-locus dynamics explicitly — not summarize each locus in isolation. Writing `tensions.md` forces you to see the loci in cross-section before opening the draft. The richest disagreements, though, often live in the width corpus itself and were never elevated as loci — Step 6.5 catches those.

**This step is always-on for full tier.** Even single-locus runs produce `tensions.md` — with that locus's committed position as the lone argumentative anchor the draft must engage. The discipline of writing it down BEFORE drafting is the same.

---

## Recover state

Read these inputs:
- `research/scaffold.md` — vault_tag
- `research/loci.json` — scored loci
- `research/temp/contradiction-graph.json` (built in Step 4.0, if it exists) — high-relevance fight clusters that were NOT promoted to loci are prime orphan-tension candidates for Step 6.5
- All interim notes: `bad search "" --tag <vault_tag> --type interim --json` then `bad note show <id1> <id2> ... -j`

You need the `## Committed position` section from every interim note in your context.

---

## Procedure

1. **Lay out all committed positions.** For each interim note, read its `## Committed position` section. Write them down side-by-side in a scratch list (you can use `research/temp/orchestrator-notes.md` as scratch).

2. **Hunt for tensions.** Ask of every pair of positions:
   - Do they agree on the facts but disagree on what the facts mean?
   - Do they cite different evidence and reach opposite conclusions?
   - Does one locus's position assume something another locus's evidence complicates?
   - Is one locus's position a special case of another's general claim?
   - Do they converge on a conclusion but via different mechanisms (worth noting — convergence from independent paths is itself a finding)?

3. **Pick the 3–5 strongest cross-locus dynamics.** Reject weak ones (loci that are simply orthogonal, or that restate each other). You want cross-locus relationships that a good final draft should actually wrestle with.

4. **Write the cross-locus tensions into `research/temp/tensions.md`** (you'll append the orphan tensions from Step 6.5 to this same file):

   ```markdown
   # Tensions (cross-locus + orphan)

   ## Tension 1: <short name for the dynamic>

   - **Locus A** ([[interim-A]]) commits: <one-line committed position>
   - **Locus B** ([[interim-B]]) commits: <one-line committed position>
   - **The cross-locus dynamic:** <2–3 sentences naming exactly how they relate — conflict? convergence? complication? special case? Name the load-bearing disagreement or agreement.>
   - **How the draft should engage this:** <one sentence. Example: "Section on X must acknowledge that Y from Locus B undercuts the simple reading of Locus A" or "The recommendation should privilege Locus B's position because its evidence base is stronger.">

   ## Tension 2: ...
   ```

5. **Calibration synthesis.** For each tension, note the investigators' confidence levels and "what would change this position" conditions from their calibrated committed positions. When two investigators disagree but one is "high confidence" and the other is "low confidence," the draft should weight accordingly. When both name the same "what would change my mind" condition, that's a genuine open question to flag explicitly.

6. **This document is the argumentative spine of the draft.** Every tension you name here must become a visible argumentative beat in the final report — a paragraph or section that engages the disagreement explicitly, not a one-line gesture. If you write `tensions.md` with 4 tensions and the draft only visibly engages 1, the insight score suffers.

---

## Step 6.5 — Orphan tension scan

**Goal:** extract explicit expert disagreements from the source bodies themselves — including **orphan tensions** that slipped past loci analysis — and merge them into `research/temp/tensions.md`. This is the single highest-leverage move for the insight dimension (it was the former step 7).

**Why this subsection exists:** the cross-locus tensions above capture places where the depth investigators disagree. But the richest disagreements often live in the width corpus itself: Source A says X, Source B says Y, and neither the loci analysts nor the depth investigators elevated this as a locus because it cut across multiple topics. These "orphan tensions" are invisible to locus-driven analysis but are exactly what distinguishes an expert synthesis from a competent survey.

**After writing the cross-locus tensions above, scan the top 8–12 source bodies for orphan tensions (tensions that slipped past loci analysis). Merge findings into `research/temp/tensions.md`, combining: (a) cross-locus tensions from the reconciliation above, (b) orphan tensions from this scan.**

### Delegation

The orchestrator delegates this orphan tension scan to a **work-tier subagent** — structured
extraction of expert disagreements from source bodies into the per-tension schema is
deterministic-format work requiring no frontier reasoning. This follows the same spawn pattern as
the step-1 decompose and step-5 depth investigators. Spawn:

```
Task(
  prompt: "Execute Step 6.5 of bad-research-6-cross-locus-reconcile: read all interim notes and the
           top 8–12 source bodies for vault_tag=<vault_tag> (plus research/temp/contradiction-graph.json
           if it exists), extract orphan source tensions, and APPEND them to research/temp/tensions.md
           following the per-tension schema in the step (side_a, side_b, resolution, origin,
           decision_relevance). Do NOT overwrite the cross-locus tensions already in the file. Then stop.",
  tier: "work",
  tools_allowed: [Read, Write, Bash],
  stop_conditions: "research/temp/tensions.md contains the merged cross-locus + orphan tensions (3–7 total)"
)
```

Read `research/temp/tensions.md` back into orchestrator context before proceeding to step 8.

First survey the vault for the 15–20 highest-quality non-deprecated sources: `bad search "" --tag <vault_tag> -j`.

1. **Re-read the cross-locus tensions you just wrote.** Each is already a candidate tension. Extract: the two positions, the strongest evidence for each, your preliminary reading of which side has the better case.

2. **Scan the width corpus for orphan tensions.** For the 15–20 highest-quality non-deprecated sources, then **read the full body** of the top 8–12 sources most likely to contain disagreements — use `bad note show <id1> <id2> ... -j` in batches. **Tensions hide in nuance that summaries flatten:** a source's "however" clause, a footnote caveat, a methodological critique buried in a discussion section. You cannot extract tensions you haven't read. Look for:
   - Sources that explicitly disagree with each other (different conclusions from similar evidence)
   - Sources that use competing theoretical frameworks to explain the same phenomenon
   - Sources where one side cites data the other side ignores
   - Government/institutional positions that conflict with academic findings
   - Industry claims that contradict independent research
   - Historical consensus that recent evidence challenges

3. **If `research/temp/contradiction-graph.json` exists** (built in Step 4.0), read it. Any high-relevance fight cluster that was NOT promoted to a locus is a prime orphan-tension candidate. It was important enough for the contradiction graph but wasn't investigated in depth — these deserve standalone treatment in the draft.

4. **Select 3–7 tensions total.** Combine the cross-locus tensions above with the orphan tensions. Rank by:
   - **Decision relevance:** does resolving this tension change the report's recommendation?
   - **Evidence quality:** are both sides grounded in real evidence (not just opinion)?
   - **Reader value:** would an expert reader find this tension illuminating?

   Drop tensions that are: trivially resolved (one side is clearly wrong), definitional (the disagreement is about word meaning, not substance), or orthogonal to the research query.

5. **For each tension, pre-commit to a resolution.** Do NOT leave tensions open. For each:
   - Name it in 5–10 words (e.g., "NHTSA's 'no defect' vs. NTSB's 'design failure'")
   - State Side A's strongest case with evidence (quote or cite specific sources)
   - State Side B's strongest case with evidence
   - Commit to a reading: which side has the better evidence, or is there a synthesis? Name the load-bearing reason.

6. **Append each tension's full schema to `research/temp/tensions.md` as an inline JSON block** (the former `source-tensions.json` schema, preserved in full — every tension retains `side_a`, `side_b`, `resolution`, `origin`, `decision_relevance`):

   ````markdown
   ## Tension N: <short descriptive name>

   - **The dynamic / how the draft should engage this:** <one sentence>

   ```json
   {
     "name": "short descriptive name",
     "side_a": {
       "position": "one-sentence claim",
       "evidence": "strongest evidence with source note ids",
       "proponents": ["source-note-id-1", "source-note-id-2"]
     },
     "side_b": {
       "position": "one-sentence claim",
       "evidence": "strongest evidence with source note ids",
       "proponents": ["source-note-id-3"]
     },
     "resolution": "one-paragraph committed reading with load-bearing reason",
     "origin": "cross-locus|contradiction-graph|orphan-scan",
     "decision_relevance": "high|medium"
   }
   ```
   ````

   `origin: "cross-locus"` marks the tensions from the reconciliation above; `origin: "orphan-scan"` / `"contradiction-graph"` mark the ones surfaced here. `tensions.md` therefore holds BOTH the readable per-tension prose AND the structured schema per tension — step 10 reads it as the expert-disagreements source and turns every tension into a dedicated subsection in the final report.

---

## Exit criterion

- `research/temp/tensions.md` exists with 3–7 tensions (cross-locus + orphan)
- Each tension includes: locus/source references, a dynamic description + engagement guidance, and the full per-tension schema (`side_a`, `side_b`, `resolution`, `origin`, `decision_relevance`) with both sides' proponents and a committed resolution
- (single-locus runs: at minimum 1 distilled cross-locus position + any orphan tensions found)

---

## Next step

Return to the entry skill (`bad-research`). Invoke step 8:

```
Skill(skill: "bad-research-8-corpus-critic")
```
