# Evidence — what makes a span count, and the ways it stops counting

SKILL.md states the rules. This is the reasoning and the measurements behind them, plus the failure
each one was written after. Read it when you are deciding whether something you have is citable.

## Ordering: the citation is bound when the claim is made

The commonest grounding failure is temporal rather than careless. A system that drafts the prose and
then attaches sources afterwards is asking a model to find support for something it already wrote —
and it produced phantom references at rates up to **21%**. The same audit over **75 generated papers
across 5 tasks** measured **zero** phantom references when the citation was constructed from the
retrieval call itself, so parametric memory was never a candidate source.

Two consequences worth having. A claim that outruns its evidence is **restated conservatively**, not
deleted — the third disposition, alongside "supports" and "contradicts". And of four forensic audit
checks in that system, **three were mechanical** (re-run the code and compare the score; read the code
against the stated task; cross-check every bibliography entry against live APIs); the LLM judge was
spent on the single check no mechanical procedure could settle.

## Span width, and why a whole-file citation defeats everything downstream

`FILE.md:1-2383` satisfies a `path:line` rule and defeats every check built on it: the path resolves,
the gate sees a citation, and nobody re-reads 500 lines to find the number was mis-transcribed. The
shipped rule worth copying caps a code citation at **five lines** and says *do not cite more lines than
necessary*. Bound the span to the claim and an over-wide citation becomes a visible defect rather than
a passing one.

Vendor quote discipline, for calibration — and note the two shipped systems disagree, so take the
shape and not the constant: one caps attributed words per source at **200** with verbatim runs at **25
words**; another allows **under 15 words, one quote per source, and applies the cap globally across the
whole response**. The second enforces it at the data layer rather than by instruction — search returns
an opaque encrypted handle, so the model cannot reproduce plaintext it was never shown, and fetch
refuses any URL search did not surface.

## Identity: verify the object by its properties, not its name

A retrieved artifact that *resolves* is not evidence you got the one you meant. Encoding what a human
does on finding a candidate — check its frequency, its unit, and whether its **values match your
priors** — took one production retrieval system from roughly **50% to 90%**. The skill's three lane
traps are instances of this one rule: the npm name-squat (check version list, publish date, maintainer
and unpacked size *before* reading), the GitHub login that resolves to the wrong person (single-digit
followers beside a real repo count, and a blog field pointing at another profile), and a transcript
section whose claims appear nowhere in its own source video.

## Corroboration: count actors, and say how each was reached

Collapse by person, by company and by commercial orbit before calling anything corroborated. Measured
here: one practitioner supplied eleven of ninety-six findings across three lanes that each believed
they were independent.

**And sources reached by frontier-chaining are not independent.** Each was selected *because* the last
one pointed at it, which is the structure that invalidates naive pooling — a validated hypothesis
system cannot use Fisher's combined test for exactly this reason and reaches for anytime-valid
statistics instead. You do not need the arithmetic; you need the discipline. Say how a source was
reached — an independent lane, or chained from another finding — beside any count, and never report
*N sources agree* without that split.

Two adjacent traps. **The subject may control the order of the pool**: with references, testimonials,
case studies or a vendor's reference customers, uniform positives mean the search is unfinished, not
that the record is clean — keep going until one dissents, and if none does, report the search as
incomplete. And **an earlier agent's query trail is not a source**: sites auto-generate indexed pages
from search-query slugs, returning HTTP 200 with a real title and a body that is a restatement of the
query. Agents working the same problems have read each other's trails as results. That is the one case
where "count distinct actors" fails because the actor is you, one run ago.

## Numbers: protocol, then discrimination

A number needs its resolution, window and unit — hourly sampling understated a peak by 700% on the same
data, so where sampling could hide a peak report a bound (`≥ X`) rather than a fact.

Then the half that protocol does not cover: **a correlation needs a control.** Before crediting a trend
to a cause, look at the population where the cause is absent and check whether the trend is there too.
The worked case: youth employment really is slowing, and it fails to implicate the proposed cause
because the slowdown is identical with and without degrees, and identical in exposed and unexposed
fields. A real number and no support for your story is a finding — say both halves.

## Reading a source against itself

The explanation a source gives for its result is often not the mechanism that produced it. In the
worked case, a published signature split into **three disjoint gene sets** — the genes that actually
split the test set, the genes that split the training set, and the genes the prose names to explain why
it works — with no overlap; and in the follow-up, two of the four genes carrying the finding were not
on the array used. Check the explanation against the part of the source that did the work.

Two more, cheap: **report the denominator of silence** — how many of your sources addressed the claim
at all, because the ones that did not are evidence rather than neutral. And **citation mass tracks
priority, not weight** — in one literature the answer was unequivocal after study 12, while the
most-cited paper remained the original and the largest study was cited seven times.

## Sweeps produce candidates, never verdicts

Five sweeps returning 110/58/52/29/20 hits collapsed to 31/0/0/0/0 on reading. That is **base rate, not
bad luck**: when the thing you are hunting is rare, even a 95%-accurate filter returns mostly false
positives. So re-check survivors rather than shipping them — one operator with ~100 people on the
problem keeps a holdout and re-reads it, and roughly **a third** of confirmed effects fail that
re-check. Industrially the same ratio shows up as a named triage stage between the sweep and the
report: 109 flags → 10 actionable findings.

## Two rules that need no argument

**Captions are substance, never quotation.** A talk listed under a *manual* subtitle track still
rendered "Claude Code" as "Cloud Code" throughout. Paraphrase, and say it came from a talk.

**A retrieval tool's digest is the tool's words, not the page's.** Re-check any quote against raw bytes
before it goes in quotation marks.
