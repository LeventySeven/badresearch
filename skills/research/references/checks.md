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
