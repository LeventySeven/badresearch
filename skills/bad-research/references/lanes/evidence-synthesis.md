# Lane: the professions that do this for a living

**Use this lane whenever the question is about METHOD** — how much to search, when to stop, how to
weigh a source, how to report what you did not find.

## Why this lane exists

The other nine lanes all route to where AI people publish. That is one industry, roughly twenty
years old, and it shows: a sweep of six lanes over ~190 essays, 67 practitioner threads, 42 talk
transcripts and 407 product teardowns reported **"nobody publishes a measured stopping rule for
reading"** — four lanes, four independent zeros. The sixth lane left the AI industry and came back
with a fifty-year professionalised literature on exactly that question.

**Four lanes agreeing on an empty is not evidence that the world is empty.** It is evidence they
share a boundary. That is the trap this lane is here to close, and it is the same mistake the main
skill warns about in the small — *a lane you did not drive is not a lane that came back empty* —
occurring at the scale of a whole corpus.

## Where to look

| Field | What it owns | Reach it at |
|---|---|---|
| **Systematic review** | how much to search, when to stop, how to report the search | Cochrane Handbook ch. 4; PRISMA; PRESS |
| **Evidence grading** | separating *how good is the evidence* from *how strongly should you act* | GRADE |
| **Intelligence analysis** | competing hypotheses, diagnosticity, deception, calibration | Heuer, *Psychology of Intelligence Analysis* (CIA, free PDF) |
| **Information science** | what a question is, before it reaches you | Taylor 1968 on question negotiation |
| **Metascience** | forking paths, analyst variability, publication bias | Gelman & Loken; Silberzahn et al. 2018 |

## What this lane supplies that the AI lanes do not

**Peer-review the search BEFORE you run it.** Verified verbatim in the Cochrane Handbook §4.2.2:
*"It is strongly recommended, however, that all search strategies should be peer reviewed, before
being run, by a suitably qualified and experienced medical/healthcare librarian or information
specialist."* The review covers not just syntax but whether the strategy interpreted the question
the way the question meant. Cheap here: read your own query back and ask what it would miss.

**A stopping discipline exists and is published.** Cochrane ch. 4 carries a section titled *"When to
stop searching"* (§4.4.11) — its existence alone refutes the four-lane empty above.

> **Verification state, and it matters:** I confirmed §4.4.11 exists from the handbook's own table of
> contents. Its *text* did not render in the fetch, so the mechanism below reached me second-hand and
> is **UNVERIFIED against the primary**. Reported here rather than dropped, because the pointer is
> useful and a reader can finish the job — but do not quote it as Cochrane's words.

The mechanism as reported: validate a search by what a **different method** surfaces that you did not
already have. The inverse reading is the sharp half — if a supplementary method (citation chasing,
hand-searching) yields many records the main search missed, that **indicts the main search** rather
than complimenting the supplement.

**And the trap in the obvious version of that test.** Tuning a query until it recovers your known key
papers fits it to *their* vocabulary. Recovering them is necessary and is not sufficient; a strategy
that finds *only* them is a strategy shaped by them. The passing signal is finding, by a genuinely
different route, something you did not know was there.

*(Note how this cuts against `noise.md`'s canaries, which say to plant known-good items and check the
filter does not kill them. They act on different objects — a filter versus a query — and the canary
rule stays right. But do not carry canary logic across to query-tuning, or you inherit exactly this
bias.)*

**Confidence in the evidence and strength of the recommendation are separate judgements.** GRADE
keeps them on two axes on purpose, and both crossings are real: a high-quality trial can support a
weak recommendation, and observational evidence alone can support a strong one. Collapsing them is
how a well-sourced answer becomes a bad decision. A purely factual answer with nothing to act on has
only one axis and needs only one.

**A question arrives already compressed.** Taylor's four forms: what the asker actually needs, what
they consciously want, how they formalise it, and what they finally say — degraded at each step to
fit what they believe the system can do. The main skill's *recover the question* rule comes from here.

**One question, many analysts, many answers.** 29 teams given one dataset and one question produced
odds ratios from 0.89 to 2.93, using 21 unique covariate combinations, and *peer ratings of analysis
quality did not account for the variability.* This is the strongest available bound on what any
single critique pass can certify — including this skill's.

## Orbit warning

These professions sell things too. Cochrane sells training and its imprimatur; GRADE's methodology
is free but is hosted and taught commercially; PRESS sits inside a professional-association
ecosystem. The methods are decades-tested and used by WHO, NICE and Cochrane reviews, which is real
corroboration — but "an established profession endorses it" is a different warrant from "it was
measured", and the two must not be blurred just because the field is older than machine learning.

## Reaching these sources: expect walls, and classify them

This lane's sources sit behind academic publishers, and a sweep of it hit **403 on PRESS, on the BMJ
GRADE paper, and on the Sage copy of Silberzahn** — plus one mirror that was a **hijacked academic
domain serving gambling SEO at HTTP 200 under the correct filename**, which is the
IRRELEVANT-BY-DESIGN row of the kinds-of-nothing table arriving in the wild. A 200 is not a fetch.

So drive this lane through `silver` and let it classify (`references/lanes/web-live.md` has the
ladder). Measured on `dl.acm.org`: a raw fetch gives a bare 403, `silver read` says *"the server
REFUSED the request … this is the wrong TIER, not necessarily the wrong URL"*, and a browser session
returns `captcha_detected: true` with the Cloudflare interstitial rendered. **Silver does not get
through a hard wall.** What it gives you is the difference between *"this paper does not support the
claim"* and *"I could not read this paper"* — which in a methods lane is the whole answer.

Where a publisher wall holds, the open routes are usually: the handbook's own free web edition, an
author's copy, the free CIA/agency PDF, or the guideline body's own site. Say which one you read,
because they are not always the same text.
