---
name: bad-research-1.6-plan-gate
user-invocable: false
description: >
  Step 1.6 of the Bad Research pipeline — a user-editable plan-gate (Gemini
  collaborative_planning). On an interactive + full-route-or-broad-survey run it
  emits the research plan (numbered sub-questions + per-sub-q source strategy +
  chosen route + a rough scope summary) and pauses for "approve / edit / proceed";
  on edit it patches research/prompt-decomposition.json before step 2. SKIPPED on
  every non-interactive / `--auto` / wrapped run, so automated runs flow straight
  through.
---

# Step 1.6 — Plan-gate (user-editable, interactive full-route-or-broad-survey runs only)

**Tier gate:** Runs AFTER step 1.5 (route) and BEFORE step 2, **only** when the run
is **interactive** AND **not** `--auto`/wrapped AND a **full-route or broad-survey**
run — i.e. the deterministic predicate `router.py::plan_gate_fires` returns true. SKIP
entirely (proceed straight to step 2) when ANY of these holds:

- the run is **non-interactive** (a `-p` / automated / eval-gate / test run — the
  default; no human is present to approve),
- `research/wrapper_contract.json` exists (a **wrapped** run — the query is binding
  GOSPEL, not to be questioned; mirrors exactly how 0.5-clarify skips), or
- the run is `--auto`, or
- the run is a **small bounded run** (route `fast` within
  `ROUTER_LIGHT_MAX_ATOMIC` atomic items).

**This gate is a SEPARATE step. It NEVER changes the route.** It does not re-run
`classify_route`, never edits the `route`/`query_shape` fields, and never blocks an
automated run. Its only effects are (a) to PAUSE for approval and (b), on edit, to
patch the sub-question list the downstream steps research.

**Goal:** prevent the dominant failure mode on an ambiguous/broad query —
running a full-route fan-out on the wrong sub-questions. One quick human
confirmation of the plan before the deep fan-out begins.

## Recover state

Read:
- `research/prompt-decomposition.json` — `sub_questions`, `entities`,
  `response_format`, the `route` + `query_shape` written by step 1.5
- `research/scaffold.md` — vault_tag, modality, `## Route rationale`
- `research/query-<vault_tag>.md` — canonical research query (GOSPEL)
- whether `research/wrapper_contract.json` exists (→ wrapped → SKIP)

## Procedure

1. **Decide whether to gate (deterministic — never eyeball it).** Run the router
   CLI with the run's interactivity context. The orchestrator knows whether the
   session is interactive (a human is present) and whether this is `--auto`/wrapped:
   ```bash
   bad route --decomposition research/prompt-decomposition.json \
     --interactive            # ONLY when a human is at the keyboard; OMIT on -p/automated runs
     [--wrapped] [--auto]     # pass if wrapper_contract.json exists / --auto is set
     --json
   ```
   Read `plan_gate.would_gate` from the JSON.
   - `would_gate == false` → **SKIP this step.** Proceed straight to step 2.
   - `would_gate == true` → continue to step 2 below (show the plan + pause).

   `would_gate` is `false` for every non-interactive run (no `--interactive`),
   every wrapped run, every `--auto` run, and every small bounded `fast` run — so
   the eval gate, the test suite, and any `-p` pipeline run pass through here with
   NO pause.

2. **Emit the plan.** Surface a compact, human-readable plan to the user:
   - **Numbered sub-questions** — the `sub_questions` (+ `entities`) from the
     decomposition, in research order.
   - **Per-sub-question source strategy** — for each, one line naming the source
     class the fetchers will chase (primary docs / papers / vendor sites / news /
     code) and the search angle. Derive this from the modality + the sub-question
     phrasing; keep it to a phrase, not a paragraph.
   - **Chosen route + shape** — the `route` (fast / full) and
     `query_shape` (straightforward / breadth_first / depth_first) with the
     one-line `reason` / `shape_reason` from the router CLI.
   - **Scope note** — one line on the depth of the chosen route (fast = quick,
     bounded, single-pass; full = deep, contested, adversarially-audited), adjusted
     by any `--effort` override. Describe SCOPE, not cost or calendar time.

   The plan describes WHAT will be researched and how deep, never a price or a
   schedule. If you ever sketch effort, assume an agentic-coding world — think
   hours-to-days, never weeks or months — and omit calendar estimates unless the
   query explicitly asks.

3. **Pause for: approve / edit / proceed.** Present exactly these three options:
   - **approve / proceed** → continue to step 2 unchanged.
   - **edit** → collect the user's edits to the sub-question set (add / drop /
     reword / reorder), then **patch `research/prompt-decomposition.json`**: rewrite
     the `sub_questions` (and `entities` if the user changed the entity set) to the
     approved list, preserving every other field — **except
     `required_section_headings`, which you must re-derive (or explicitly re-confirm
     with the user) in the SAME patch.** That array is DERIVED from the sub-questions
     (step 1, `bad-research-1-decompose` §3: "generate headings from the sub-questions
     you extracted"), and step 12's instruction critic then enforces it element-wise
     against the draft as a `"severity": "critical"` structural-mirror finding. Carry
     it over unchanged and you hand the drafter a STALE heading contract for
     sub-questions nobody is researching any more — then fail the drafter against it.
     Apply step 1's own population rule (one ordered H2 per approved sub-question,
     declarative phrasing) and **never leave the array empty**; re-show the new
     headings with the patched plan. **Do NOT touch `route` or
     `query_shape`** — an edit changes WHAT is researched, not the route/depth. If the
     edited set materially changes breadth, you MAY re-run step 1.5 (`bad route
     --apply`) to re-derive the route from the new sub-questions — but only as an
     explicit re-route, never as a side effect of this gate.

   Reuse the 0.5-clarify question-asking machinery to surface the plan and collect
   the response (the same interactive prompt/collect loop). After one edit round,
   re-show the patched plan once, then proceed.

4. **Record the disposition** in `research/scaffold.md` under a `## Plan gate`
   subsection: `approved` | `edited` (+ a one-line summary of the edits) | `skipped
   (non-interactive | wrapped | auto | small-bounded)`. This is the audit trail.

## Exit criterion

- On a gated run: the user has chosen approve/edit/proceed; if edited, the
  `sub_questions` in `research/prompt-decomposition.json` reflect the approved set,
  `required_section_headings` covers exactly those sub-questions (no stale heading
  contract), and `route`/`query_shape` are unchanged by the edit itself.
- On a skipped run (`would_gate == false`): no pause occurred, the decomposition is
  untouched, and `research/scaffold.md` records `## Plan gate: skipped (...)`.
- The `route` classification is identical to what step 1.5 wrote (this gate never
  re-classifies the route).

## Next step

Return to the entry skill (`bad-research`). Continue per the route (the plan-gate can
fire on a `fast` broad-survey — `router.py::plan_gate_fires` allows atomic > 6 — so it
MUST route `fast` back to the bounded loop, never into the full width-sweep):
- **fast** → `Skill(skill: "bad-research-fast")`
- **full** → `Skill(skill: "bad-research-2-width-sweep")`
