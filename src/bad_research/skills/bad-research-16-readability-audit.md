---
name: bad-research-16-readability-audit
user-invocable: false
description: >
  Step 16 (final) of the Bad Research pipeline — a readability recommender
  writes JSON formatting suggestions and the orchestrator selectively applies
  them via Edit, then runs the uncited + recitation ship-gates (blocking quality
  checks before delivery).
---

# Step 16 — Readability audit & selective apply (FINAL STEP)

**Tier gate:** Runs for ALL tiers. Every report gets a readability audit, regardless of tier — readability is the dimension where small structural changes (paragraph rhythm, list/table conversions, bold injection) yield outsized scoring gains.

**Goal:** improve the report's visual structure, paragraph rhythm, and scannability without changing substantive content. The recommender writes a JSON list of suggested changes; YOU (the orchestrator) decide which to apply.

**Why split recommender + orchestrator-applied:** an Edit-based reformatter sometimes makes changes that hurt the argument — converting a flowing paragraph to a bullet list when the prose was load-bearing, or merging paragraphs that addressed distinct sub-topics. By having the recommender produce JSON suggestions and the orchestrator decide what to apply, we get the recommender's pattern-matching speed plus your judgment about which changes serve the research_query.

---

## Recover state

Read these inputs:
- `research/scaffold.md` — vault_tag
- `research/notes/final_report_<vault_tag>.md` — the polished final report from step 15

---

## Step 16.1 — Spawn the readability recommender

Spawn ONE `bad-research-readability-recommender` subagent. Single spawn, runs once.

**Spawn template:**
```
subagent_type: bad-research-readability-recommender
prompt: |
  RESEARCH QUERY (verbatim, gospel):
  > {{paste research/query-<vault_tag>.md body}}

  QUERY FILE: research/query-<vault_tag>.md

  PIPELINE POSITION: You are step 16 of the Bad Research pipeline —
  the final analytical pass. The final report at
  research/notes/final_report_<vault_tag>.md has been drafted (step 10),
  synthesized (step 11), critiqued (step 12), gap-filled (step 13),
  patched (step 14), and polish-audited (step 15). Your job: write
  JSON recommendations for paragraph rhythm, list/table conversions,
  and other structural readability improvements. You are tool-locked
  to [Read, Write] — you cannot Edit the report. The orchestrator
  reads your recommendations and decides which to apply.

  YOUR INPUTS:
  - draft_path: research/notes/final_report_<vault_tag>.md
  - recommendations_path: research/readability-recommendations.json

  Write recommendations as a JSON array per the schema in your agent
  prompt. Cap at 50 recommendations, prioritized by impact.
```

---

## Step 16.2 — Read the recommendations

When the recommender returns:

1. **Read `research/readability-recommendations.json`.**

2. **Read the recommender's report-back.** It tells you:
   - Total count of recommendations
   - Breakdown by category (merge-paragraphs, break-paragraph, make-list, make-table, bold-keyterms, split-sentence, remove-hr, add-whitespace)
   - Highest-severity issue
   - Expected net char delta if all applied

---

## Step 16.3 — Decide which to apply

You are not obligated to apply every recommendation. Use these heuristics:

**Apply confidently:**
- All `merge-paragraphs` recommendations where adjacent paragraphs are clearly the same sub-topic (rationale field confirms this)
- All `break-paragraph` recommendations on paragraphs > 800 CJK / 1500 EN chars
- All `remove-hr` recommendations (horizontal rules don't belong in research reports)
- All `add-whitespace` recommendations (zero risk)
- `make-table` recommendations when the prose-comparison passage cited 3+ entities × 2+ dimensions and the recommender's suggested table preserves all comparison points

**Apply with judgment:**
- `make-list` recommendations: confirm the prose was actually enumerative (3+ items in sequence) and not load-bearing argumentative prose. If the rationale says "items appear sequentially in flowing prose," that's NOT a list candidate — skip it.
- `bold-keyterms` recommendations: confirm the term is genuinely a key term, not just any noun. Bold load-bearing concepts and statistics; don't over-bold.

**Apply skeptically (often skip):**
- `split-sentence` recommendations on argumentative prose where sentence length serves emphasis or rhythm
- Recommendations that touch the opening thesis paragraph (load-bearing — keep as written)
- Recommendations that change tables that already exist

**Always skip:**
- Any recommendation whose `current` field doesn't match the actual draft (the recommender mis-anchored — log and ignore)
- Recommendations that would change H2 heading text
- Recommendations that delete substantive content (the recommender shouldn't, but verify)

---

## Step 16.4 — Apply chosen recommendations via Edit

For each recommendation you decide to apply:

1. Use the Edit tool on `research/notes/final_report_<vault_tag>.md`
2. `old_string` = the recommendation's `current` field (exactly as the recommender wrote it)
3. `new_string` = the recommendation's `recommended` field

**For non-ASCII text (CJK / Arabic / Cyrillic):** the recommender copied `current` verbatim from Read output. Trust that. Don't retype.

**Order of application:**
1. `remove-hr` first (smallest changes, cleanest baseline)
2. `merge-paragraphs` and `break-paragraph` (paragraph-level changes)
3. `make-list` and `make-table` (structural conversions)
4. `bold-keyterms` (within paragraphs that survived the merges/breaks)
5. `split-sentence` (within finalized paragraphs)
6. `add-whitespace` (final cleanup)

If an Edit fails because `old_string` doesn't match (recommender mis-anchored), skip that recommendation and continue with the rest.

---

## Step 16.5 — Log decisions

Write `research/readability-decisions.json` with the orchestrator's decisions:

```json
{
  "total_recommendations": <int>,
  "applied": [<list of recommendation IDs you applied>],
  "skipped": [
    {"id": "rec-N", "reason": "<one sentence>"}
  ],
  "edit_failures": [
    {"id": "rec-N", "reason": "old_string did not match the draft"}
  ],
  "net_char_delta_actual": <int — measure the actual delta>
}
```

This is the audit trail. If a future review finds a readability problem we should have fixed, this log shows whether we considered it and skipped, or never saw the recommendation.

---

## Step 16.6 — No-uncited-claim hard gate (deterministic ship-block)

After readability edits, run the deterministic ($0) grounding gate. It is a
**ship-block** for ALL routes (fast / full): the report does
NOT ship if any non-trivial factual claim lacks a verifiable citation resolving
to a `claim_anchors` row.

```bash
bad uncited-gate --report research/notes/final_report_<vault_tag>.md \
    --vault-tag <vault_tag> --json
```

- Output `{"uncited": []}` (exit 0) → PASS, ship.
- Output `{"uncited": [{"sentence": "...", "reason": "..."}]}` (exit 1) → BLOCK.
  For each uncited non-trivial claim, either (a) add a citation via a surgical
  Edit if a supporting note exists, (b) run one targeted `bad fetch
  --tier-max 3` to ground it, or (c) soften the claim to a non-assertion.
  Re-run the gate until `uncited == []`.

This is deterministic, so it is a hard pass/fail — never "good enough." The
non-zero exit code surfaces the block to the orchestrator.

### Step 16.6b — Citation-drift warnings (non-blocking, but ACT on them)

The gate's JSON also carries a `warnings` array (severity `minor`) alongside `uncited`:

```json
{"uncited": [], "warnings": [{"sentence": "...", "reason": "citation-drift", "severity": "minor"}]}
```

A `citation-drift` warning means the cited note shares almost none of the claim's content
words — the cite probably points at the WRONG source (a real note, but not the one that
supports the claim). This does **not** block ship (that stays deterministic on `uncited`),
but do not ship it silently: for each drift warning, either **(a) repoint** the cite to the
note that actually supports the sentence (check the vault via `bad search`), or **(b) hedge**
the claim to what the cited note does support, or **(c)** if the note genuinely supports it
and the low overlap is a heavy paraphrase, leave it. Fixing drift here is the cheap,
non-blocking half of "bind, not count" — the claim ends up bound to a source that *supports*
it, not merely to a source that *exists*.

---

## Step 16.7 — Recitation overlap gate (major finding, NOT a ship-block)

After the uncited gate passes, run the deterministic ($0) recitation gate. It
flags any report sentence that reproduces a cited note's body too closely (a
verbatim run > 12 words, or > 50% of the sentence lifted contiguously) — Gemini's
RECITATION *output* guarantee without its decoder machinery. Unlike the uncited
gate, recitation is a **major** finding, **not a ship-block** (copying is a
quality/legal smell, not a correctness failure) — so it never blocks ship.

First build the note-bodies JSON (note_id → body) the gate needs:

```bash
PYTHONIOENCODING=utf-8 bad search "" --tag <vault_tag> --json \
  | python -c "
import sys, json
d = json.load(sys.stdin)
bodies = {r.get('id',''): (r.get('body') or '') for r in d.get('data',{}).get('results',[])}
open('research/temp/recitation-bodies.json','w').write(json.dumps(bodies))
"
bad recitation-gate --report research/notes/final_report_<vault_tag>.md \
    --note-bodies research/temp/recitation-bodies.json --json
```

- Output `{"recitation": []}` → no verbatim copying; done.
- Output `{"recitation": [{"location": "...", "recommendation": "..."}]}` → for each
  flagged sentence, apply a surgical Edit that paraphrases the copied span while
  keeping the `[N]` citation. A sentence whose verbatim run sits inside an explicit
  `"…"` quotation adjacent to a citation is already exempt (the gate does not flag
  it). Re-run the gate after paraphrasing to confirm the flag cleared. The gate
  does not block ship — but a clean report has zero recitation findings.

---

## Step 16.8 — Citation coalescing (final visual pass, AFTER both gates pass)

**Run this LAST — only after `bad uncited-gate` returned `{"uncited": []}` and the recitation gate is clean.** The gates validate per-sentence provenance *before* any cites are visually grouped; this pass only collapses the visual repetition.

**Why:** paragraph-level citations read far better than per-sentence ones. A run of consecutive sentences that all cite the same source-set renders as dense `[1][2][3]` ... `[1][2][3]` ... `[1][2][3]` — one repeated group per sentence. Collapsing a run of CONSECUTIVE sentences that share the SAME source-set into ONE trailing group cite reads better without losing any provenance.

**This is a DETERMINISTIC, $0 pass — use the helper, do not hand-edit cites.** Run `bad_research.grounding.render.coalesce_citations` over the report body:

```bash
PYTHONIOENCODING=utf-8 python -c "
import sys
from bad_research.grounding.render import coalesce_citations
p = 'research/notes/final_report_<vault_tag>.md'
src = open(p, encoding='utf-8').read()
open(p, 'w', encoding='utf-8').write(coalesce_citations(src))
"
```

**The coalescing rule (exactly what the helper does — and what you MUST NOT override by hand):**
- **Coalesce ONLY consecutive sentences that cite the IDENTICAL source SET.** `{1,2,3}` then `{1,2,3}` then `{1,2,3}` → the prose of all three sentences, then ONE `[1] [2] [3]` group cite at the end of the run. Order-independent: `{1,2}` and `{2,1}` are the same set and coalesce.
- **A sentence citing a DISTINCT source NEVER merges.** It keeps its own cite and BREAKS the run. `…{1,2}. A separate audit disagreed [9]. …{1,2}.` → the `[9]` sentence stays exactly as written, and the two `{1,2}` sentences on either side are NOT joined across it.
- **NEVER drop a source.** The union of cited sources is byte-identical before and after coalescing — every claim stays traceable to its sources; only the visual repetition is removed, never the provenance. (Sanity-check: the multiset of distinct source tokens from `extract_citations` over the whole report is unchanged.)
- **Uncited (background/transition) sentences pass through unchanged** and also break a run.

**Do NOT** re-run the uncited gate after coalescing (it checks per-sentence cites and would false-positive on the now-grouped sentences — provenance was already validated in 16.6 before grouping). If you must re-verify, verify the source-token SET is unchanged, not per-sentence presence.

---

## Exit criterion

- `research/readability-recommendations.json` exists
- `research/readability-decisions.json` exists with at least one entry in `applied` or all `skipped`
- `research/notes/final_report_<vault_tag>.md` reflects the applied recommendations
- The final report's structure (H2 list, executive summary, conclusion) is unchanged from step 15's output (this step does not restructure)
- `bad uncited-gate` returned `{"uncited": []}` (exit 0) — the ship-block passed
- `bad recitation-gate` was run; any flagged sentences were paraphrased (recitation is a major finding, not a ship-block)
- Citation coalescing (16.8) ran AFTER both gates; the report's distinct-source set is unchanged (no provenance lost — only consecutive same-set repetition collapsed)

---

## Pipeline complete

Return to the entry skill (`bad-research`). Mark all todos complete. Tell the user the final report path.

You're done.
