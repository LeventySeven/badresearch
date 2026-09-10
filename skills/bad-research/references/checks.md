# Checks — what each one buys, and what beats it

SKILL.md names the commands. This is what they are worth, in what order, and where each one has
already been beaten. Read it when a check comes back clean and you are deciding what that licenses.

## The gates, and their exact scope

| command | what it actually asserts | what it does NOT assert |
|---|---|---|
| `lane-local` | the lane was enumerated and reported its own zeros | that the topic is absent |
| `frontier-gate` | this query names something a prior read produced | that the query can discriminate between live answers |
| `frontier-observe` | the last round's new-domain / new-entity deltas, computed in code | that the answer is complete |
| `close-gate` | every load-bearing disagreement is disposed, both sides surviving | that you found the disagreements |
| `quote-drift-gate` | every attributed quotation is byte-identical to its note | anything about a claim carrying no quotation |
| `figure-support-gate` | every cited figure appears in the note cited | the prose half — it reports that count as `unchecked` |
| `uncited-gate` | every factual sentence carries a marker | **that the marker's target supports it** |
| `recitation-gate` | you paraphrased rather than copied | how much paraphrase is too much |

## The three rules that decide how to read a result

**A check never run and a check that passed must never look the same in your report.** Say "did not
apply" when it did not apply. `uncited-gate` and `recitation-gate` assume a vault with `[N]` markers
resolved against note bodies; an answer citing `path:line` directly does not have that shape.

**A degenerate answer that passes is a defect in the check, not a clean bill.** Measured here: a draft
whose every sentence was false but carried a marker resolving to a real, on-topic note returned
`{"uncited": [], "warnings": []}` — clean — while the same claims with markers stripped produced four
criticals. `uncited-gate` measures presence. That is why `figure-support-gate` exists, and why it
reports its own blind spot instead of reporting clean about it.

**A citation pass that cannot edit turns a fabrication into an UNCITED sentence, not a bad citation.**
The shipped one keeps content byte-identical and only adds markers, validated by string comparison with
no whitespace normalisation. So an unsupported claim survives into the final report wearing no citation
at all — which reframes `uncited-gate` from hygiene into the primary hallucination detector, provided
something downstream can act on what it flags.

## The judge, and the unit that decides whether to trust it

On long-form groundedness every published judge lands between **55 and 60** balanced accuracy where 50
is chance. An instrument that weak may rank what a human looks at first; it may never certify.

**But the ceiling is a property of the unit, not of judging.** Decompose a report into self-contained
atomic facts, give each its own retrieval loop, and a shipped system reached **72% agreement with human
annotators and a 76% win rate on the cases where they disagreed, at 20× lower cost.** So: no judge over
a whole report; a judge over one decomposed claim with its own evidence is defensible. Allocate
accordingly — of four audit checks in one shipped system, **three were mechanical** and the judge was
used for exactly the one no mechanical procedure could settle.

## What nothing here measures

**Recall.** `uncited-gate`, `quote-drift-gate` and `figure-support-gate` all measure precision — of the
claims you made, how many are supported. None asks whether the claims that *should* be in the answer
are in it. The constraint list you wrote before retrieving is the only recall instrument in this skill:
an answer can be 100% precise and still fail every constraint it promised to satisfy.

**Trajectory.** Every gate reads the finished artifact. None scores the run — what fraction of sources
opened carried a claim that shipped, whether the loop repeated itself, whether exploration was too much
or too little. Four independent groups now evaluate the path rather than only the answer, and a
fixed-rubric judge structurally cannot see a loop failure because the trajectory differs every run.
That is exactly why `frontier-gate` executes rather than advising.

## The contamination that voids an eval

Once a system has web search, it can retrieve the answer key for the thing being measured. One team
found their panel surfacing the benchmark's own rubric online and had to exclude those domains and
re-run everything. Any eval of this skill run with the web lane open inherits that risk: exclude the
domains hosting your fixtures, and say that you did.

---

# Verification: the four controls that decide whether a loop is adding or subtracting

These come from replications that *inverted* published results. Every one is a property of the
experiment, not of the output, so no groundedness judge and no contradiction handler can detect them.

## 1. An oracle stop is not a stopping rule

Reported self-correction gains — roughly +70% relative on GSM8K, +50% on CommonsenseQA — were produced
by a loop that halted **using the ground-truth label**: if the current answer is already right, stop.
Remove the label and accuracy *falls* after self-correction on all three benchmarks; one 7B model went
from 62% with plain prompting to **36.5%** after two rounds. The mechanism: about three quarters of
answers are left unchanged, and among the ones that change, **correct→incorrect flips outnumber
incorrect→correct**.

So a stopping rule has three categories, not two — computed, a picked constant, and **oracle-dependent**
(it reads something the deployed system will not have). The third is the dangerous one because it is
unimplementable, so anyone copying the published number inherits a gain that cannot exist in production.

**The cheap diagnostic:** log correct→incorrect and incorrect→correct per round. If the first exceeds
the second, the loop is subtracting and no amount of tuning the prompt will fix it.

## 2. Two controls that make an iteration gain evaporate

- **Equal response budget.** Multi-agent debate beat standard prompting by 5–6 points after two rounds
  — and did *not* beat plain self-consistency at the same nine generated responses. Inspecting the
  outputs, the agents were not debating; the procedure was an expensive way to reach sample consistency.
- **Initial-prompt strength.** In the headline self-refine task, the requirement that the output contain
  all input concepts was **absent from the initial prompt and present only in the feedback prompt**. Put
  it in the initial prompt and the single pass already beats the self-corrected number — after which
  applying the feedback prompt *degrades* it.

**So the baseline for any "iterating helps" claim is n samples aggregated the cheapest way at the same
call count, with a first-pass prompt containing every instruction that appears anywhere in the loop.**
Without both, the number is measuring the handicap you gave the baseline.

## 3. The precondition, stated as a mechanism

A second pass is just another input sequence containing the first prompt, the first response, and the
feedback. So it can only help when the feedback carries **information the first prompt did not** —
clearer instructions, a tool or environment result, external evidence, or a set of principles too large
to fit up front. It cannot help when the bottleneck is capability: a model that could not solve the
problem cannot verify the solution either.

**Gate every iteration on it:** name what this round has that the last one did not. If the answer is
"nothing, it re-reads its own output", the round is predicted net-negative — cut it, don't tune it.

## 4. Verification works when it cannot see the draft

This is what reconciles the above with the fact that verification loops *do* sometimes work. The
variants differ only in context isolation: putting the draft, the verification questions and their
answers in one prompt is the **fastest and the worst**, because the incorrect draft primes the model to
repeat it. Answering the verification questions in *separate calls* beats it.

And the question's form matters as much as its context: **open-form beats binary.** "Where was X born?"
recovers the right answer where "Was X born in Boston?" gets a confirming "yes" — a yes/no question
smuggles the claim back in. A templated "is this true?" also underperforms model-generated open questions.

**So specify a verification step by its context, not its prompt: fresh context, open-form question, the
claim not restated.** Any `check this claim: <claim>` call is the binary form, and it is the weak one.
This is also why the adjudicator holds `Read` and nothing else, and why it never sees the run that
produced the artifact.

## Two limits worth knowing before you trust any of this

**Self-verification is a head-entity instrument.** On biography generation stratified by entity
frequency, decomposed self-verification beat a retrieval-backed system on *frequent* entities and lost
on rare ones. It interrogates parametric knowledge, so on the tail it is checking an empty cupboard —
route rare claims to retrieval. It also *removes* unsupported facts rather than correcting them: it buys
precision and never recall, and a verification loop silently deleting correct-but-rare facts looks
exactly like one that improved.

**More samples stop helping and then hurt.** Accuracy from verifier-ranked sampling rises to roughly 400
completions and then *falls* — with more candidates there are more near-identical pairs where one is
right, and the ranker's precision on those drops; the output is the argmax of the verifier, not
coverage. Majority voting turns over far earlier, around 50. (Second-hand and caption-derived, so treat
the numbers as shape.) The consequence is not: measure your own turnover per selector, and report
coverage *and* post-selection accuracy — a rising coverage curve beside a falling selected-answer curve
is the signature, and reporting only the first is how it gets missed.

## Ingestion is not additive — and it has two distinct failure shapes

Putting a new source in front of a system that already holds a prior belief costs something. Measured
across two open models with `preservation + distortion + loss = 1`, the best update method preserved
only about **86%** of existing correct knowledge while acquiring ~72% of the new, and **no method
achieved all objectives at once**. Roughly one prior-correct claim in seven stopped being correct.

The two failures are not equivalent and a system measuring only accuracy sees them as one event:
**distortion** turns a correct answer into a confident wrong one; **loss** turns it into an abstention.
Keep a regression set of previously-correct claims and re-check it after ingesting a major source —
"did adding this break something I already knew" is currently nobody's metric.

---

# Assert that the stop FIRED, not that the run ended

A shipped product built a genuinely computed stop — a stateful predicate re-evaluated after every
page, holding the set of things still wanted, returning true only when that set empties. Exactly the
right shape. And in one of its two instantiations it is **dead**: the removal call casefolds the key
while the set was populated un-casefolded, so it never matches, the miss is swallowed by a
`suppress(KeyError)`, the predicate never fires, and stopping silently degrades to a full scan bounded
only by a 30-second timeout.

Nothing fails. The run terminates, the results look fine, and the computed stop has quietly become a
wall clock. **A timeout backstop makes a broken stop predicate indistinguishable from a working one** —
which is the same shape as a check that can only pass.

So a saturation or frontier stop needs a test asserting the predicate went from *continue* to *stop*
for the right reason, not a test that the loop exited. (Checked here: `should_stop()` is asserted
across the False→True transition in two test files, and there is no timeout backstop that could mask
it.)

# Track residual failures as a vector, not a score

The most complete accretion mechanism found in the corpus keeps, per archived attempt, an
**instance-level outcome vector** — which specific cases passed and failed — rather than a scalar
score. That is what makes *"target what the last attempt specifically failed at"* computable at all;
with a single number you can rank attempts but you cannot ask what any of them left uncovered.
Selection then draws two candidates deliberately: one for highest complementary coverage, one aimed at
the parent's residual failures.

It also writes down, and **persists**, a label per direction — effective / saturated / underexplored —
which survives into the next round's prompt instead of being re-derived. A frontier that records which
lanes are exhausted is doing the same job.

The honest limit, stated by its own teardown: the *direction* is computed, but the tempo is not — the
review cadence and the exploration rate are still constants a human picked. So this extends "stopping
is usually a picked constant" rather than refuting it.

**For a research run:** carry which sub-questions remain unanswered, not just how many new entities
arrived. A round that added three entities and closed no promised cell has not advanced, and a scalar
counter cannot tell you that.

# A judge that emits the score first will defend it

The model is autoregressive, so a rubric that asks for a number and then an explanation gets an
explanation *of the number*, not a reason for it. A practitioner demonstrated his own judge doing
exactly that — arguing for a score it had already committed to, on output he considered worthless —
and fixed it by eliciting pros, cons and reasons first and letting the score fall out last. A shipped
loop-detector in a coding harness makes the same choice in its schema: `{analysis, confidence}`, in
that order, so the reasoning is generated before the number.

Two live failures from the same session, worth having as calibration: an image judge returned **5/5 for
images on a deck containing no images**, and after a model upgrade every rubric score moved into the
4.2–4.8 band, which its author read as evidence the rubric was measuring nothing. An unanchored rubric
has nothing to attach to — no example of what a 0 or a 5 looks like.

**And judge–human agreement is measurable, so measure it rather than assuming.** One shipped tool makes
it the headline number: hand-label a set, then iterate the judge prompt against an alignment score. A
live run went 72% → **56%** (the author's own prompt edit made it worse) → 78% → 89% after changing the
judge model. He named his own overfitting out loud — adding literal words he knew the judge tripped on
— which is the failure a rising alignment score cannot distinguish from a better judge. An independent
team names the taxonomy: data drift, **judge drift** (hill-climbing one judge means overfitting to it),
and small-eval-set drift (the prompt starts to mirror those examples). Their mitigation is
human-annotated goldens kept specifically to detect judge drift.

# Three shipped checks this file used to describe instead of naming

Each of these executes. Naming the command instead of restating its rule is not a stylistic
preference here — this file's own argument is that prose is worth roughly 7% on a post-trained
model while a non-zero exit is worth what it says.

**`bad verify-citations --report r.md --sources n.json`** — the only pass that asks whether a
cited span **supports** its sentence, rather than whether the span exists. That gap is real and
this file already documents it in the other direction: `uncited-gate` measures citation
*presence*; `quote-drift-gate` only reaches text already inside quotation marks;
`figure-support-gate` covers numerals and self-reports the prose half as `unchecked`. Nothing else
here runs an entailment check.

It escalates cheapest-first, which is what makes per-sentence checking affordable at all: a
zero-cost byte-identity re-find, then entailment, then a re-fetch only for a claim that comes back
contradicted *and* is load-bearing.

**Which sentences earn the check:**

| | |
|---|---|
| **MUST** | the load-bearing facts, and anything that moves since your cutoff — numbers, dates, prices, versions, quotas, "current", "latest" |
| **SHOULD** | other statements a source could settle |
| **EXEMPT** | common knowledge, and your own synthesis (a conclusion is not a citation target) |

Do not let a `needs_host_judgment` result ride on its 0.5 default. That silently hedges a
paraphrase nothing actually judged, and a default is not a verdict.

**`bad grounding-surface --report r.md --note-bodies n.json`** — the per-claim ledger: verdict,
score and confidence band for every cited sentence, ordered worst-first. It is the audit surface,
not a gate; it tells a reader which claims to inspect. Pass `--note-bodies`/`--sources` when there
is no vault behind the run, which is the normal case here — without it the ledger binds nothing
and prints "No cited claims found", an empty that reads exactly like a clean bill.

**`bad grounding-recall`** — the mutation harness. This file says *"break it on purpose and watch
it go red"*; this is the command that does it, over the keyless guards, and reports their measured
catch-rate. A guard whose catch-rate you have never measured is a guard with an unknown
false-negative rate, which is not the same as a low one.

**`bad absence-gate --report r.md`** — every absence claim in the draft, flagged where it names no
search scope. Built from a measured loss; `references/absence.md` carries the sentence and the
comparison.

# Hedging is a check output, not a writing style

When a claim survives on thin support, calibrate the prose to what the check returned: one source
→ *"one source reports…"*; a low support score, or a span you had to stretch → *"preliminary"*, or
narrow the sentence to what the span actually supports.

**Keep the raw 0.0–1.0 score off the page.** It belongs in the audit trail. A number in the prose
reads as a measurement of the world, when it is a measurement of your checking.

# Two bounds on every judge in this file

**A model given your definition will often quietly use its own, and its confidence carries no signal
about which one it used.** Measured across 8 datasets and 3 model families: how familiar a model is
with a *label's definition* predicts its accuracy (r ≈ 0.4) where memorisation of the data does not,
and a full rescue battery — supplying the aligned definition, few-shot examples, prompt optimisation,
multi-turn self-correction — recovers only about **35%** of the gap. The sharp part: models apply
aligned and misaligned definitions with *the same confidence*, so nothing in the output tells you
which happened.

What follows for this kit: a judge, screen or gate that turns on a **word** — "relevant", "supported",
"high-quality", "load-bearing" — is running on the model's definition of that word, not yours, and it
will not tell you. Prefer a criterion that is mechanically checkable (does this span contain this
figure) over one that is nameable (is this source good). Where the word is unavoidable, define it by
example in the prompt and treat the result as a triage order rather than a verdict.

**The sampling-turnover figure above needs its condition.** That accuracy from verifier-ranked
sampling turns over near 400 samples, and majority vote near 50, is a property of *the selector* —
a verifier-ranked argmax degrades because ranking error accumulates faster than candidate quality
improves. It is not a general ceiling on test-time compute: on agentic long-horizon work the plateau
is reported as very far out and sometimes not observed at all within practical budgets, and for
stronger models it is pushed further or disappears. So do not carry the turnover number into an
agentic loop. It bounds a ranked-sampling selector, and only that.


# The files you have to write yourself, and the exit codes

**Nothing generates these.** A gate that names an input no command produces is a gate nobody runs.

| file | shape |
|---|---|
| `n.json` | `{"<id>": "<the body text you actually read>"}` — what a quote or figure is checked against |
| `c.json` | a list of `{subject, value, unit, source, as_of}`, one entry per side of a disagreement |
| `d.json` | a list of `{contradiction_id, kind, reason}`; `kind` is `ranked` or `unresolved`. `[]` is legal and means "none disposed yet" |

**Exit codes, because two of them lie.** These gates exit **0** when clean and **1** when they block,
so a caller reading `$?` treats any non-zero as a refusal. But a missing required option exits **2**
and a missing script exits **127** — both then read as *a gate that fired and blocked you*, when the
truth is *the gate never ran*. That is the exact confusion this skill's own rule forbids: a check
never run and a check that passed must never look the same. Test for 2 and 127 explicitly.

Measured: driven cold from a scratch directory, the skill's command block returned exit 2 from
`uncited-gate` and `recitation-gate` and 127 from `lane-probes.sh`, and every one of those would have
been reported as a passing gate by a caller that only asked "was it non-zero?".

**And run them from a directory you control.** A stale `inspect.py` sitting in `/tmp` shadows the
stdlib module and every command dies on import — which surfaces as a traceback that looks like a gate
failure. Verified during this run: five gates "exited 1" from `/tmp` and all five were that crash.
