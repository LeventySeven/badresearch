# Round 2 — Verification + Eval Harness Design

**Agent:** R2-4 (P5+P6+P7+P8+P14)  
**Date:** 2026-05-29  
**Primary mandate:** verify every claimed gap against `src/` before designing anything.

---

## Item 1 — Eval Harness (G3/G6)

### Verified current state

**G3 (no golden-set corpus):** CLOSED. The corpus exists and is substantial.

- `src/bad_research/calibrate/golden/` — 8 fixture files (01–08), covering causal, comparison,
  multi-domain, contested/argumentative, definitional, temporal, breadth-list, numeric-precise
  query shapes. `golden.py:75-88` implements `load_golden_corpus()` with drop-in extensibility.
- `golden-eval-report.json` (repo root) records a live run: pass_rate=1.0, total=8,
  all three component axes (decompose/retrieval/synthesis) at 1.0.
- `tests/test_calibrate/test_golden.py` has a full regression gate suite including a
  deliberate-break test (`test_gate_fails_on_a_deliberately_broken_case`) and a
  zero-keys invariant test.

**G6 (0–1 float scores / Arize anti-pattern):** CLOSED. Integer/categorical rails are in production.

- `calibrate/judge.py:34-49` — `JudgeRail(StrEnum)` with values `pass | borderline | fail`.
  The docstring at line 1 explicitly cites the Arize fix ("E2 — CATEGORICAL RAILS, not numeric
  scores"). No float axis scores exist in the current judge path.
- `calibrate/constants.py:19-21` — `JUDGE_RAILS = ("pass", "borderline", "fail")` and
  `RAIL_CREDIT = {"pass": 1.0, "borderline": 0.5, "fail": 0.0}` — the float only surfaces as
  a reporting aggregate, never as a raw model output.
- `quality/grader.py:36-57` — `GraderVerdict` wraps `JudgeVerdict` and inherits categorical rails.

**Verdict: G3 and G6 are both HAVE. No implementation needed.**

### Remaining real gap in this area

The `RubricJudge` (keyless, used by default in `evaluate_corpus`) grades grounding overlap by
content-word intersection (`golden.py:159-165`), not entailment. Its `factual` rail passes if a
well-cited report uses the corpus's vocabulary even if it contradicts the source meaning
(`golden.py:126-130` — the scope caveat is documented verbatim). The `LLMJudge` path exists but
requires the host model.

**Gap (real, medium):** The 8-fixture golden set has no case designed to catch
cited-but-contradicting synthesis — a report that correctly cites a source but inverts its
finding passes the keyless judge with a clean `factual: pass`. This is a structural blind spot
in the regression gate.

**Design (SIMPLE):** Add two targeted golden fixtures that the `RubricJudge` cannot distinguish
from good reports, reserved for `LLMJudge`-gated CI runs:

```
09_cited_contradiction.json — report cites src correctly but inverts the causal direction.
10_over_hedged_completeness.json — completeness axis: answer technically present but buried in
                                    a hedge so deep it fails intent (tests axes_floor enforcement).
```

Wire a new `bad gate --llm` flag (uses `LLMJudge` over the full corpus; slow, key-required, only
on release branches) alongside the existing keyless gate. The two new fixtures MUST be excluded
from the keyless path (mark them `"requires_llm": true`). This extends the gate without
regressing the keyless invariant.

**Tag: SIMPLE**

### DSPy MIPROv2 prompt optimization

Borrowable.md P15 suggests using DSPy MIPROv2 to auto-optimize critic/judge prompts against
the eval set. With 8 fixtures and a keyless judge this is **SKIP-as-overkill**: MIPROv2 needs
~35 eval examples per trial and a differentiable score signal, neither of which we have at
8 fixtures with a categorical judge. Revisit at ~50 fixtures with the LLMJudge path enabled.

**Tag: SKIP-as-overkill (preconditions not met)**

---

## Item 2 — Grader Loop Re-Plan (G5 stall — Magentic-One dual-ledger / P8)

### Verified current state

`src/bad_research/skills/bad-research-12.5-grader.md` documents the loop (`12.5.2`):

```
while revisions < 3:
    verdict = grade()
    if verdict.passed: break
    write verdict.findings -> critic-findings-grader.json
    Skill("bad-research-14-patcher")   # patcher reads the findings
    revisions += 1
```

The grader emits `findings` (patcher-shaped `{failure_mode, severity, location, recommendation}`)
via `quality/grader.py:60-82` (`_parse_findings`). On reject it hands a findings list to the
patcher and re-grades the patched output. This is a patch loop, not a re-plan.

**What is MISSING vs. Magentic-One P8:** Magentic-One's `PLAN_UPDATE_PROMPT` explicitly asks
"what went wrong, what prior mistakes to avoid" and emits a *revised plan* before re-executing.
Our grader loop on round 2+ sends the same instruction context as round 1 — there is no
mechanism to say "the completeness axis failed twice because the Africa sub-question is
structurally missing; the patcher must add a new section, not just a sentence." The patcher is
told WHAT to fix but not THAT IT ALREADY TRIED AND FAILED.

**Real gap:** no failure-history injection across grader rounds. Round 2 patches the same report
with no knowledge of what round 1 patched or why it still failed. Convergence probability drops
on deep structural misses (missing sections, wrong ordering) where a surgical edit in round 1
was insufficient and round 2 should escalate to a structural rewrite directive.

**Design (SIMPLE — two-line addition to the grader skill prompt):**

In `bad-research-12.5-grader.md` Step 12.5.2, before invoking the patcher on round N ≥ 2,
inject a failure ledger into `critic-findings-grader.json`:

```json
{
  "grader_history": [
    {"round": 1, "failed_axes": ["completeness"], "findings_applied": 2,
     "still_failing": true, "escalate_if_repeated": ["completeness"]}
  ],
  "findings": [...]
}
```

Add one sentence to the patcher's spawn prompt when `grader_history` is present:

> "The grader already ran N round(s). Axes still failing after patching: [list]. If the
> previous patch was a sentence-level insertion and the axis still fails, escalate to a
> structural section addition. Do NOT repeat the same surgical fix."

No new code module required — the grader skill orchestration already controls the loop and
already writes the findings file. This adds one `python -c` snippet per round to accumulate
the history and one conditional sentence in the patcher spawn prompt.

**Tag: SIMPLE**

---

## Item 3 — Multi-Mode Critic + Assumption Decomposition + Meta-Review (P4/P7/P13)

### Verified current state

`src/bad_research/skills/bad-research-12-critics.md` spawns four parallel critics:

- `bad-research-dialectic-critic` — counter-evidence the draft missed or straw-manned
- `bad-research-depth-critic` — shallow spots vs. interim notes
- `bad-research-width-critic` — corpus clusters the draft ignores
- `bad-research-instruction-critic` — structural adherence to decomposition

**What we HAVE:**  
- Four independent angles (genuine fan-out, not duplicates).  
- The `dialectic-critic` covers the adversarial / counter-evidence mode.  
- `bad-research-fresh-review.md` (step 14.5) is a fresh-context cold-read — closest analogue
  to the AI Co-Scientist "initial review with no tools" mode.

**What is MISSING vs. AI Co-Scientist P4/P7/P13:**

1. **Assumption decomposition critic (P4):** None of the four critics decontextualizes a claim
   into sub-assumptions and rates each independently. The dialectic critic attacks the *overall
   direction* of the report; it does not decompose "X causes Y because A, B, and C" into three
   separate assumption checks. This is the Co-Scientist deep-verification mode.

2. **Meta-review (P13):** No mechanism feeds recurring cross-run or cross-critic failure
   patterns to the patcher. The four findings files are read once by the patcher and discarded.
   If the dialectic critic flags "missing counter-evidence" on 4 of 5 runs, that signal is never
   accumulated to sharpen future critic prompts or patcher directives.

**Design:**

**Assumption critic (SIMPLE — new critic variant, no architecture change):**  
Add a fifth critic spawned in parallel with the existing four: `bad-research-assumption-critic`.
Its sole job: for each load-bearing causal or quantitative claim in the report (identified by
scanning for "because", "causes", "leads to", "increases by", "is due to"), split it into
constituent sub-assumptions, then independently verify each against the corpus. Format: one
`finding` per assumption that cannot be verified from the fetched notes. Limit scope to the 5
highest-stakes claims (by section heading importance from decomposition). This is a prompt-only
addition to the critic fan-out in `bad-research-12-critics.md` Step 12 item 1.

Output path: `research/critic-findings-assumption.json` — the patcher already globs
`critic-findings-*.json`, so it is auto-consumed with no patcher change.

**Meta-review (MEDIUM — requires a cross-run accumulation store):**  
True meta-review requires a persistent pattern store across runs (AI Co-Scientist paper: "the
meta-review ensures 100% of future reviews address recurring BBB issues"). For a keyless
Claude-Code-native tool with no background process, the minimal version is:

1. After each full-tier run completes, append a structured critic-failure summary to
   `research/vault-meta-review.json` (one entry per run):
   ```json
   {"run": "<vault_tag>", "query_domain": "...", "repeated_critic_flags": ["missing counter-evidence", "overclaim on mechanism"]}
   ```
2. At step 12 spawn time, if `research/vault-meta-review.json` exists and has ≥3 entries
   matching the current query domain, prepend the top-3 most-frequent flags to every critic's
   system prompt: "Prior runs in this domain consistently flagged: [list]. Look hard for these."

This is cross-run, not cross-session (the vault is per-research-directory). It accumulates over
repeated use of the same vault and sharpens critics without fine-tuning.

**Tag: assumption critic = SIMPLE; meta-review = MEDIUM**

---

## Item 4 — Debate-then-Judge / Elo for Contested Loci (P6/P11)

### Verified current state

Steps 3–6 form a full contradiction-resolution pipeline:

- **Step 3** (`bad-research-3-contradiction-graph.md`): clusters opposing claims into ranked
  "fight" clusters with `side_a / side_b / evidence_quality_delta / scope_overlap /
  decision_relevance`. Already emits structured bi-polar positions.
- **Step 4** (`bad-research-4-loci-analysis.md`): scores loci on importance, uncertainty,
  disagreement, decision_impact — disputed loci get more depth-investigation budget.
- **Step 5** depth investigators commit to a position with explicit confidence and "what would
  change my position" conditions.
- **Step 6** (`bad-research-6-cross-locus-reconcile.md`): lays committed positions side by
  side, identifies 3–5 cross-locus tensions, and writes engagement guidance for the draft.

**Assessment vs. Grok Heavy P14 / AI Co-Scientist P11:**

Grok Heavy's debate ensemble spawns N independent instances that see each other's answers and
may revise before a judge synthesizes. Our architecture already achieves structural equivalents:
the triple-draft ensemble (step 10) uses differentiated angles (strongest-thesis, steelman-
contrarian, synthesis-reconciler), and the depth investigators write from differentiated source
lists on the same locus. The reconcile step (step 6) is the "judge" pass.

The one gap is **locus-level Elo / pairwise ranking** for cases where two depth investigators
commit to genuinely opposite positions at comparable confidence. Our step 6 reads both positions
and asks the orchestrator to adjudicate, but the adjudication is prose-driven, not structured
as a formal debate with an explicit winner declaration and win-rate tracking.

**Recommendation: SKIP-as-overkill.**  
Rationale: adding a formal Elo tournament on top of the existing contradiction graph →
loci → depth-investigation → reconcile pipeline would add one more LLM pass at a point where
the report has not yet been drafted. The contradiction graph already ranks fights by
`decision_relevance` and the depth investigators already write from differentiated angles.
The remaining gap (no explicit win-rate) is not a quality bottleneck — the reconcile step's
prose adjudication is structurally equivalent and already guided by the evidence_quality_delta
field. Reserve for a future round if empirical calibration shows unresolved loci reaching the
draft with unreconciled positions.

**Tag: SKIP-as-overkill**

---

## Item 5 — Cross-Model Adversarial Review Feasibility (P14)

### Verified current state

`bad-research-fresh-review.md` (step 14.5) runs a fresh-context Opus reviewer with no
pipeline history — the closest structural proxy to a different-model reviewer: cold context,
no dispatch history, read-locked to [Read].

### Feasibility verdict: INFEASIBLE under keyless / Claude-Code-native constraint

**Why:** Cross-model adversarial review requires either (a) a different model-family API key
(OpenAI, Gemini, xAI — all keyless-prohibited) or (b) routing within Anthropic's model family
(Haiku/Sonnet/Opus). The "mixture-of-models reduces hallucination" principle (SYNTHESIS.md
transcript line) requires genuine model diversity at the weights level — running Sonnet after
Opus reviewing the same report is not architecturally distinct from two Opus passes because
both models share Anthropic's RLHF distribution and will share systematic biases on the same
claim types.

**Best in-family proxy (already partially implemented):** 

The three adversarial differentiators we already deploy constitute the achievable in-family
maximum:

1. **Fresh-context isolation** (step 14.5): fresh-context Opus with no pipeline history catches
   whole-report drift the in-context critics miss. This is the dominant benefit of the
   "different reviewer" pattern — context independence, not weight independence.

2. **Explicit persona differentiation in the triple-draft ensemble** (step 10): Draft B
   (steelman-contrarian) and the dialectic critic are explicitly prompted to attack the
   strongest-thesis position. This is a weaker but genuine form of adversarial diversity.

3. **Assumption critic (designed above, Item 3)**: decontextualizing claims and checking
   sub-assumptions independently is the within-model equivalent of asking a specialist
   reviewer rather than a generalist.

**Additional proxy worth adding (SIMPLE):**  
In the fresh-review spawn prompt (step 14.5), add one explicit instruction:

> "Before reading the report, generate your own 3-sentence direct answer to the research query
> from memory alone. Then read the report and flag any claim where your a-priori position and
> the report's position diverge — these are the highest-priority verification targets."

This forces the fresh reviewer to construct a prior before seeing the draft, approximating
the "new model instance with independent priors" behavior without requiring a second model
family. Zero new code, one additional sentence in the spawn prompt.

**Verdict: SKIP cross-model (keyless; infeasible). Best proxy = fresh-context isolation
(already HAVE) + assumption critic (Item 3) + prior-generation prompt addition (SIMPLE).**

---

## Summary Table

| Item | G/P ref | Verified state | Gap (if real) | Design | Tag |
|---|---|---|---|---|---|
| 1a. Golden-set corpus | G3 | HAVE (8 fixtures, full harness) | Cited-but-contradicting blind spot | 2 LLM-gated fixtures + `bad gate --llm` flag | SIMPLE |
| 1b. Categorical rails | G6 | HAVE (`JudgeRail` StrEnum, E2 closed) | — | — | HAVE |
| 1c. DSPy prompt opt | P15 | Preconditions unmet | — | — | SKIP-as-overkill |
| 2. Grader re-plan | G5/P8 | Patch loop only, no failure history | No escalation signal across rounds | Failure ledger in findings JSON + patcher escalation clause | SIMPLE |
| 3a. Assumption decomp critic | P4/P7 | Not present | No sub-assumption verification | 5th parallel critic (`bad-research-assumption-critic`) | SIMPLE |
| 3b. Meta-review | P13 | Not present | No cross-run critic-failure accumulation | `vault-meta-review.json` + domain-matched preamble injection | MEDIUM |
| 4. Debate/Elo contested loci | P6/P11 | Covered by steps 3–6 | Win-rate not tracked (non-bottleneck) | — | SKIP-as-overkill |
| 5. Cross-model adversarial | P14 | INFEASIBLE keyless | — | Prior-generation sentence in fresh-review prompt | SKIP (infeasible) + SIMPLE proxy |

---

## Highest-Leverage Single Upgrade

**Item 3a — assumption decomposition critic.**

Rationale: the existing four critics all operate on the draft's *conclusions and structure*;
none decompose individual load-bearing claims into sub-assumptions and verify each independently.
This is the one verification mode that is (a) genuinely absent, (b) directly addresses the most
common failure mode in deep research (a claim that is cited and well-structured but rests on an
unverified causal link), and (c) implementable as a prompt-only addition to the existing
critic fan-out with zero architectural change. The patcher already auto-consumes any
`critic-findings-*.json` file, so the integration cost is one new skill file and one new
entry in the step-12 spawn list.

The grader re-plan (Item 2) is a close second — it addresses the G5 stall that the SYNTHESIS.md
explicitly flags as a known open issue, and it too is a two-artifact change (findings file
schema + one spawn-prompt sentence).

---

## Cross-Model Feasibility Verdict

**INFEASIBLE** under the keyless/Claude-Code-native constraint. A different-model-family
reviewer requires a non-Anthropic API key. Within Anthropic's family, weight-level diversity
does not exist between Haiku/Sonnet/Opus (shared RLHF distribution). The best achievable proxy
is context-isolation + explicit prior-generation in the fresh reviewer prompt (already partially
HAVE; addition costs one sentence in `bad-research-fresh-review.md`).

---

## File Artifacts Required

1. **New skill:** `src/bad_research/skills/bad-research-assumption-critic.md` (Item 3a)  
2. **Modified skill:** `src/bad_research/skills/bad-research-12-critics.md` — add assumption critic to fan-out list (Item 3a)  
3. **Modified skill:** `src/bad_research/skills/bad-research-12.5-grader.md` — failure ledger injection in loop Step 12.5.2 (Item 2)  
4. **Modified skill:** `src/bad_research/skills/bad-research-fresh-review.md` — prior-generation sentence in spawn prompt (Item 5 proxy)  
5. **2 new golden fixtures:** `src/bad_research/calibrate/golden/09_cited_contradiction.json`, `10_over_hedged_completeness.json` — marked `"requires_llm": true` (Item 1a)  
6. **CLI addition:** `bad gate --llm` flag routing to `LLMJudge` over full corpus (Item 1a, MEDIUM effort within the existing calibrate framework)
