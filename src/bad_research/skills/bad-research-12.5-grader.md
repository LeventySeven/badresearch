---
name: bad-research-12.5-grader
user-invocable: false
description: >
  Step 12.5 of the Bad Research pipeline (full tier only) — the in-pipeline
  grader loop (judge → patch → re-judge, ≤3 rounds) that scores the report on 5
  quality axes and feeds failing-axis defects to the patcher (runs AFTER step 13
  despite its number).
---

# Step 12.5 — Grader loop (judge → patch → re-judge)

**Tier gate:** FULL tier ONLY. SKIP entirely for the `fast` route —
its quality contract is the forward binding + the deterministic uncited gate; a
grader loop on a small bounded fast query is the overkill we explicitly reject.
Run only when the route in `research/prompt-decomposition.json` is `full`.

**Goal:** raise the report's quality on the four non-citation axes (factual,
completeness, source_quality, efficiency) by feeding the judge's defect findings
to the patcher and re-grading, capped at 3 rounds. Patch, never regenerate.

---

## Recover state

Read these inputs:
- `research/scaffold.md` — vault_tag, route
- `research/prompt-decomposition.json` — confirm `route == "full"`; read
  `required_section_headings` + atomic items (the judge maps completeness misses
  to these)
- `research/notes/final_report_<vault_tag>.md` — the report (already citation-
  verified at 11.5, critic-patched once at 12/14)
- `research/temp/evidence-digest.md` — the corpus the report had access to
- `research/query-<vault_tag>.md` — canonical research query

If `route != "full"`, write nothing and return to the entry skill immediately —
this step does not run.

---

## Step 12.5.1 — Build the corpus JSON for the judge

**Round 1 shortcut (C-4):** if `research/critic-findings-*.json` files exist
(i.e., step 12 ran), SKIP the full corpus JSON build for **round 1**. Instead,
**aggregate** the critic findings: read all `research/critic-findings-*.json`
files, collect their `findings` arrays into a single list, and ask the judge to
score the five axes against those findings rather than independently re-scanning
the corpus. This drops round-1 cost from a full Opus-tier corpus scan to a cheap
verdict-aggregation — the 5 critics in step 12 already did the corpus read, so
round 1 is just a verdict over their findings, not a fresh scan.

**For rounds 2 and 3 only:** run the full corpus JSON build specified below,
because the first patch may introduce new issues that are NOT in the original
critic findings, so the later rounds need a full corpus scan to catch them.

The grader needs the evidence as a JSON list of `{note_id, url, text}`. Convert
the evidence-digest into that shape (one entry per cited note):

```bash
PYTHONIOENCODING=utf-8 bad search "" --tag <vault_tag> --json \
  | python -c "
import sys, json
d = json.load(sys.stdin)
rows = [{'note_id': r.get('id',''), 'url': r.get('url',''), 'text': (r.get('body') or r.get('snippet') or '')[:1200]}
        for r in d.get('data',{}).get('results',[])]
open('research/temp/grader-corpus.json','w').write(json.dumps(rows))
print(f'corpus rows: {len(rows)}')
"
```

---

## Step 12.5.2 — The grader loop (host-run, cap = MAX_GRADER_REVISIONS = 3)

`MAX_GRADER_REVISIONS = 3` (NOT Claude's 20 — we PATCH not REGENERATE, so each
round is a small surgical Edit and convergence is far faster). The loop is:

```
revisions = 0
while revisions < MAX_GRADER_REVISIONS:   # 3
    if revisions == 0 and glob("research/critic-findings-*.json"):
        # Round 1 (C-4): aggregate existing critic findings — no fresh corpus scan.
        # Collect every findings entry from steps 12a–12d, then ask the judge to
        # score the 5 axes against that aggregate, not by re-reading the corpus.
        aggregate_findings = [f for path in glob("research/critic-findings-*.json")
                              for f in json.load(open(path)).get("findings", [])]
        verdict = grade_from_findings(aggregate_findings)   # fast verdict-aggregation path
    else:
        # Rounds 2-3: full corpus scan (patches may add NEW issues not in critic findings).
        verdict = bad grade-report --report research/notes/final_report_<vault_tag>.md \
                    --corpus research/temp/grader-corpus.json --json
    #   -> {passed, scores{5 axes}, overall, findings:[{failure_mode,severity,location,recommendation}]}
    #   KEYLESS run -> {"status":"keyless-skip","passed":null,"scores":{},"overall":null,"findings":[]}
    if verdict.get("status") == "keyless-skip" or verdict.get("passed") is None:
        # KEYLESS NULL BRANCH (see Step 12.5.2b). The CLI grader could not run
        # (no host key). Do NOT fall through to the `false` patcher spawn with an
        # empty findings list — that would burn a round patching nothing. Instead:
        # YOU (the orchestrator host model) GRADE INLINE against the evidence-digest
        # — you ARE the judge model — and either emit real findings to patch, or,
        # if you judge the report already passing, cleanly exit the loop.
        handle_keyless_skip()   # see Step 12.5.2b; break out of the loop after
        break
    if verdict.passed:  break             # every axis >= 0.70 AND mean >= 0.75
    # write the failing-axis findings as a patcher-shaped findings file:
    write verdict.findings -> research/critic-findings-grader.json  (shape: {"findings":[...]})
    # run the patcher (step 14) over the grader findings (surgical Edits only):
    Skill(skill: "bad-research-14-patcher")   # the patcher reads critic-findings-grader.json too
    revisions += 1
# PASS or cap reached -> proceed
```

This is prose procedure for the orchestrator LLM, not literal Python. The
**round-1 judge prompt** for the aggregate path is: *"These are the critic
findings from steps 12a–12d. Score the report on the 5 quality axes (factual,
completeness, source_quality, efficiency, readability). You are aggregating
those findings into a verdict, NOT independently scanning the corpus."* Round 2
and round 3 fall through to the full `bad grade-report` corpus scan as before.

Concretely, each round:

1. Run the grader.
   - **Round 1 (revisions == 0) — aggregate, do not rescan:** if
     `research/critic-findings-*.json` exist, collect every entry from their
     `findings` arrays into one aggregate list and have the judge score the 5
     axes against that aggregate (the verdict-aggregation fast path). Write the
     verdict to `research/temp/grade-round-1.json` in the same
     `{passed, scores, overall, findings}` shape the full grader emits.
   - **Rounds 2–3 (revisions >= 1) — full corpus scan:** run the full grader
     over the rebuilt corpus JSON, because the prior patch may have introduced
     new issues the critic findings never saw:
   ```bash
   bad grade-report --report research/notes/final_report_<vault_tag>.md \
       --corpus research/temp/grader-corpus.json --json > research/temp/grade-round-<N>.json
   ```
2. Parse `passed`.
   - **`status == "keyless-skip"` or `passed is null`:** the CLI grader could not
     run (keyless box, no host key). Go to **Step 12.5.2b** — do NOT treat this as
     `false` and do NOT spawn the patcher with an empty findings list. Record the
     keyless verdict in `research/temp/orchestrator-notes.md` and break the loop.
   - **`passed == true`:** the loop is done — record it in
     `research/temp/orchestrator-notes.md` and proceed to "Exit criterion."
   - **`passed == false`:** continue to step 3 (extract findings, patch, re-judge).
3. If `false`, extract the `findings` array and write the grader findings file:
   ```bash
   python -c "
   import json, pathlib
   v = json.loads(pathlib.Path('research/temp/grade-round-<N>.json').read_text())
   pathlib.Path('research/critic-findings-grader.json').write_text(
       json.dumps({'findings': v.get('findings', [])}))
   print('grader findings:', len(v.get('findings', [])))
   "
   ```
3.5. **Accumulate the `grader_history` failure ledger (round N ≥ 2).** Before
   re-spawning the patcher on round 2 or 3, fold every PRIOR round's verdict into
   a `grader_history` block on `research/critic-findings-grader.json`. This is the
   memory the patcher reads to avoid re-applying a fix that already failed. It
   **composes with the C-4 round-1 aggregate path**: the `findings_applied` count
   tallies findings from BOTH sources — the round-1 critic-findings aggregate
   (`critic-findings-*.json`) and the rounds-2–3 full-corpus scans — while
   `still_failing` per axis is independent of how the findings were sourced, so
   the accumulation is purely additive and never conflicts with the round-1
   aggregation in Step 12.5.1.
   ```bash
   python -c "
   import json, pathlib
   prev_rounds = sorted(pathlib.Path('research/temp').glob('grade-round-*.json'))
   history = []
   for p in prev_rounds[:-1]:   # all rounds EXCEPT the current one
       v = json.loads(p.read_text())
       scores = v.get('scores', {})
       history.append({
           'round': int(p.stem.split('-')[-1]),
           'failed_axes': [ax for ax, sc in scores.items() if float(sc) < 0.70],
           'findings_applied': len(v.get('findings', [])),  # counts round-1 aggregate + rounds-2-3 scan findings
           'still_failing': not bool(v.get('passed')),
           'escalate_if_repeated': [ax for ax, sc in scores.items() if float(sc) < 0.70],
       })
   if len(history) >= 1:
       cur = json.loads(pathlib.Path('research/critic-findings-grader.json').read_text())
       cur['grader_history'] = history
       pathlib.Path('research/critic-findings-grader.json').write_text(json.dumps(cur))
       print('grader_history injected, rounds:', len(history))
   "
   ```
4. Re-judge after patching: re-run the patcher (`Skill(skill: "bad-research-14-patcher")`).
   The patcher already globs `research/critic-findings-*.json`, so it picks up
   `critic-findings-grader.json` automatically and applies the grader's surgical
   Edits; the next loop iteration re-judges (re-grades) the patched report.

   **NOTE (round ≥ 2 escalation) — inject this clause into the patcher spawn on
   round 2 and round 3:** `critic-findings-grader.json` now carries a
   `grader_history` block. The patcher must read it BEFORE applying findings. If
   `grader_history` shows an axis is **still failing** after a prior round already
   patched it at the sentence level, **escalate** that axis: do NOT repeat the
   same surgical sentence-insertion — round N-1 tried that and it failed, so
   escalate to a structural change (add a new sub-section, or restructure the
   coverage / section addition for that axis) instead. Do NOT apply the same fix
   twice. State the escalation explicitly: "round N-1 tried <X> and failed;
   escalating to <structural Y>."
5. Increment the round counter in your TodoWrite note and loop.

**Track the loop counter in `research/temp/orchestrator-notes.md`** (it survives
compaction): write a line `grader-loop round <N>: passed=<bool> overall=<x>` each
round. The cap of 3 is the cost ceiling — never run a 4th round.

**Never emit bare text while the patcher Task is in flight** — append to
`research/temp/orchestrator-notes.md` instead.

---

## Step 12.5.2b — Keyless-skip branch (`bad grade-report` returned `passed: null`)

On a keyless box (no host provider key wired into the CLI), `bad grade-report`
cannot run its LLM-judge loop, so it emits the benign keyless-skip verdict:

```json
{"status": "keyless-skip", "passed": null, "scores": {}, "overall": null, "findings": []}
```

This is **NOT** a `false` verdict. A `false` verdict means "the grader judged the
report and it failed an axis" — it carries real `findings` for the patcher. A
keyless-skip carries `findings: []` and `passed: null`, meaning "the grader never
ran." Treating it as `false` would spawn the patcher (step 14) with an empty
findings list — a wasted round that patches nothing. Do not do that.

**You (the orchestrator) ARE the host judge model.** When you get a keyless-skip,
pick exactly ONE of these two and record which in `research/temp/orchestrator-notes.md`:

1. **Grade inline (preferred when you have the evidence-digest in context).** Read
   `research/temp/evidence-digest.md` and the report, then score the report
   yourself on the 5 axes (factual, completeness, source_quality, efficiency,
   readability) — you are the same class of model `grade-report` would have called.
   - If, by your own judgment, every axis ≥ 0.70 and the mean ≥ 0.75: the report
     PASSES. Write `research/temp/grade-round-<N>.json` with
     `{"passed": true, "scores": {...your scores...}, "overall": <mean>, "findings": []}`
     and break the loop.
   - If you find real defects: write those as `findings` in the same shape
     (`{failure_mode, severity, location, recommendation}`) to
     `research/temp/grade-round-<N>.json` with `"passed": false`, then proceed to
     step 3 (write `critic-findings-grader.json`, spawn the patcher, re-judge). Your
     inline re-judge on the next round is again the host-model grade, not the CLI.
2. **Cleanly skip the grader loop** (if you cannot grade inline — e.g. the
   evidence-digest is unavailable). Record `grader-loop: keyless-skip, host-grade
   unavailable, loop skipped` in the notes and break the loop. The report still
   ships; the deterministic uncited gate at step 16 remains the hard ship-block.

In **both** cases you then write `research/grader-log.json` in Step 12.5.3 with
the keyless status recorded, and proceed to step 14.5. **Never** fall through to
the `false`-path patcher spawn with an empty findings list.

---

## Step 12.5.3 — Convergence note

When the loop exits (PASS, cap reached, or keyless-skip), write
`research/grader-log.json`. Always write this file — even on the keyless "cleanly
skip" sub-case where no `grade-round-<N>.json` was produced — so the integrity
gate (entry skill + step 15.4) finds it:

```bash
python -c "
import json, pathlib
rounds = sorted(pathlib.Path('research/temp').glob('grade-round-*.json'))
log = {'rounds': len(rounds), 'final_passed': False, 'overall': None, 'status': 'graded'}
if rounds:
    v = json.loads(rounds[-1].read_text())
    log['final_passed'] = bool(v.get('passed'))
    log['overall'] = v.get('overall')
    if v.get('status') == 'keyless-skip':
        log['status'] = 'keyless-skip'   # host graded inline or loop cleanly skipped
elif <keyless-skip-with-no-inline-grade>:   # Step 12.5.2b sub-case 2
    log['status'] = 'keyless-skip'
pathlib.Path('research/grader-log.json').write_text(json.dumps(log))
print(log)
"
```

If the cap was reached without a PASS, that is acceptable — the report still ships
(the deterministic uncited gate at step 16 is the hard ship-block, not the grader).
Record the non-PASS (or `keyless-skip`) in the log for the audit trail; do NOT
loop a 4th time.

---

## Exit criterion

- `research/grader-log.json` exists with `rounds` set and `final_passed` recorded.
- The grader loop ran ≤ MAX_GRADER_REVISIONS (3) rounds.
- `research/notes/final_report_<vault_tag>.md` reflects any grader-driven patches.
- For a `fast` route: this step was skipped (no `grader-log.json`).

---

## Next step

Return to the entry skill (`bad-research`). The patcher's final convergence (step
14) is complete; invoke step 14.5:

```
Skill(skill: "bad-research-fresh-review")
```
