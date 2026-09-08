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
