# Critique: what happens after a draft exists

Read this when you have a draft and are deciding whether it ships.

This phase is here because it is the one part of the older, five-times-larger system that
demonstrably beat this one. Blind-judged on a depth question, its adversarial pass caught the
over-claim *"No source measures the false-negative rate of a source-quality filter directly …
Nobody publishes 'we rejected N documents a human judged relevant'"* and narrowed it before
shipping. Without the pass, that sentence shipped, and the judge falsified it **in one fetch**.

The rest of this file is the four things that make the pass work rather than perform.

## 1. The critique must not see how the draft was made

**MUST NOT put the draft, the questions and their answers in one prompt.** That arrangement is
the fastest and the worst: the incorrect draft primes the model to repeat it, and the critique
comes back agreeing. Nor does it help to hand a critic the author's reasoning — a reader that
inherits the reasoning inherits the rationalisation that produced the error.

So a critic gets: the question, the draft, and its lens. Not the trail, not the notes on why a
choice was made, not your summary of what you think is weak. A brief that pre-judges the finding
("the structure is deliberate", "at most minor") poisons the lens, usually to spare the author a
fix.

Be honest about the ceiling. A fresh pass by the same model removes anchoring, not the model's
own blind spots. It is a strong filter, not an independent one.

### The pre-read prior generation

**Before opening the draft, write your own three-sentence answer to the question from memory.**
Then read the draft, and every place your a-priori answer and the draft diverge becomes a
high-priority target.

This is the keyless stand-in for a second model, and it is stronger than merely separating the
call, because it removes the priming instead of isolating it — you cannot be anchored on a draft
you have not read yet.

**Its limit, which must travel with it:** it is a head-entity instrument. On rare, recent or
version-specific facts it is checking an empty cupboard, and those are precisely the claims this
skill says never to answer from memory. So a divergence is a **targeting signal, never a
correction** — it says *go verify this one*, and nothing else. A convergence is worth nothing at
all.

## 2. Lenses, chosen so they do not overlap

Run these as separate readers. The value is in the diversity, not the count — lenses that look
for different failures beat more lenses that look for the same one.

| Lens | Asks | Why this one |
|---|---|---|
| **Instruction** | Did the answer cover every atomic thing the question named, in the order and format asked? | The only recall instrument over the prompt. `checks.md` admits recall is what nothing else here measures, and prompt adherence is the dimension with the widest variance. Do not skip this one. |
| **Assumption** | Take the top five causal or quantitative claims. Split each into its sub-assumptions. Verify each **independently**. | This operationalises the one judging arrangement with evidence behind it: a judge over *one decomposed claim with its own evidence* reaches 72% agreement and a 76% win rate at 20× less cost. A judge over a whole report does not. Cap it at five claims — past that it becomes a second draft. |
| **Dialectic** | Where does the answer ignore, hedge, or straw-man the counter-evidence? | The failure the answer cannot see from inside. |
| **Width** | What does the evidence in hand support that the answer never says? | Catches the read-and-not-used failure, which is a different failure from not-retrieved. |
| **Depth** | Which load-bearing claim rests on one source, on a secondary account, or on an origin nobody opened? | The older system's blind-judged win came from a five-critic fan-out that included a depth critic, and the merge dropped it. Citation cascades end at one source surprisingly often, and a "replication" is often the same claim cited again. Each finding here becomes a trace-to-origin or rerun fetch, not a hedge. |

An **absence claim gets its own pass**, because it is the class that shipped: run
`bad absence-gate --report <draft>`, and treat every UNSCOPED hit as an instruction-lens finding.

## 3. A gap gets a fetch, not a hedge

This is the mechanism that turns a critique into a correction, and skipping it is why critiques
usually only soften sentences. A critic can name a gap, but an author holding only the evidence
it already gathered can do exactly two things with that finding: hedge the sentence, or leave it.

The decision is cheap and mechanical:

- **Two or more relevant sources already in hand** → the author can handle it. Move on.
- **Zero or one** → this is a **fetch-worthy gap**. Go retrieve. One fetch is what it cost the
  judge to overturn the claim that shipped.
- **A gap that stays unfilled after fetching is flagged**, so the answer acknowledges the limit
  instead of writing around it.

Cap the re-retrieval. A critique that becomes a second full sweep has stopped being a critique.

**An absence claim is retested by a fresh retrieval, never by re-reading the notes you already
hold.** The notes are what produced the absence claim; consulting them again can only confirm it.

## 4. Findings go back to the author, who patches surgically

The critic never edits. The author holds the question, the context and the evidence, and decides
scope — what is in this pass, what is a separate question, what the reader actually asked for.

- **Never regenerate a section to satisfy a finding.** Grounding built at write-time from the
  retrieval you just did measured **zero** phantom references over 75 papers; reattaching
  citations to already-written prose produced them at up to **21%**. A regenerated section loses
  every binding that was verified and re-runs that risk.
- The named failure mode to watch for: **a critic proposing regeneration in patch clothing** — a
  "fix" whose hunk is the size of the section. That is an escalation, not a patch: it means the
  structure is wrong, and it goes back to you, not into the draft.
- **Verify a finding before acting on it.** A critic can be wrong about what the draft says.
  Fixing a phantom defect adds a real one. Pushing back with a reason is the value of the loop.
- **Scan a finding for scope creep.** "While you're here, handle the general case" is usually
  the over-reach that production verifiers name as their most common false rejection: inventing a
  requirement the question never carried.

### Calibrate the prose to the evidence, and keep the number off the page

When a claim survives on thin support, the hedge is the fix, not deletion:

- one source → *"one source reports …"*
- a low support score, or a span you had to stretch → *"preliminary"*, or narrow the claim to
  what the span actually supports

The raw 0.0–1.0 score belongs in the audit trail, never in the prose. A number on the page reads
as a measurement of the world; it is a measurement of your checking.

## 5. Stop at three rounds

Three fix-and-recheck cycles, and **the bar does not rise between them.** A later round re-reads
the whole draft, but a *new* objection counts only as a demonstrable defect or an unmet criterion
that was already stated — never a preference the first round saw and let pass. A critique that
finds a fresh reason every pass is an infinite loop that terminates on your patience.

Still failing at three is a signal about the draft's structure, not a reason for a fourth. Say
which is true: the question was wrong, the evidence does not support the claim, or the answer
needs rebuilding rather than patching.

**Re-asking an unchanged draft is not a new round.** "Check it again for over-claims" over the
same text re-rolls the same dice and returns a fresh set of findings, because finding something
is the only output the request rewards. Either the draft changed, or the question needs a check
with a definite answer — `bad absence-gate`, `bad verify-citations`, a grep over the promise
list — rather than another opinion.
