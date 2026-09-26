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

---

# Binding a claim to a source that supports it — the one shipped system that does

**A correction to a claim made earlier in this file's own sweep.** Reading eleven open-source research
systems in source, none bound a claim to a source that *supports* it — all bound at best claim → source
that *exists*, and two responded to a failed check by deleting the citation and keeping the sentence.
That was stated as a fact about the field. It is a fact about those eleven. A twelfth, in production
under regulatory audit, does the thing properly, and how it does it is the useful part.

**It is a separate trained extractor, not a citation the generator emits.** Framed as extractive QA:
given source document `D` of utterances and generated output `O`, for each output sentence find the
supporting span `E ⊂ U`. A RoBERTa-base hierarchical classifier, QA-pretrained (SQuAD / HotpotQA /
BioASQ plus synthesised domain QA) and finetuned on roughly **0.5M `[output-sentence,
evidence-utterances]` tuples from 6,862 real sessions**.

The numbers are the argument:

| approach | score |
|---|---:|
| BM25 similarity retrieval | HA **65** |
| the trained extractor | HA **94** |
| Llama-13B asked to extract | F **5.6** |
| GPT-3.5-turbo asked to extract | F **26.8** |

**Generative models are terrible at this task**, which is precisely why "ask the LLM for citations"
fails and why a dedicated scorer over (output sentence, source sentence) pairs is worth building. In
clinic it finds appropriate evidence **>75% of the time** and cuts review from 5 minutes to 1, with
readers scanning 3–7 source lines instead of the whole transcript.

**And it publishes the claim class it cannot bind: negative and absent assertions.** "No clubbing or
cyanosis" has no evidence span, because the true evidence is the source's *silence*. That is exactly
the shape of an absence claim — "no source was found for X" — and a shipped system says its evidence
layer is structurally blind to it. Which is why absence claims get their own checked gate here rather
than riding on the citation machinery.

**Three things to take:** an evidence-binding stage is a separate scorer, not a request to the
generator; its coverage must be reported **per claim type**, not as one number; and a system that
verifies against an **independently produced record** — one generated by a different system for a
different purpose — should calibrate the join key on measured per-field agreement first. One product
doing that reconciliation drops the amount field from its key entirely, because across 3,793 matched
pairs 77% agreed on the item and only **52%** agreed on the amount. Its honest end-to-end score is
**F1 ≈ 57.5%**, which is the realistic ceiling for external verification — not 95%.

# Two disagreement moves the contradictions section does not have

**Ask whether the disagreement is DIRECTIONAL before you rank.** In one reconstruction, two fields
disagreed on 36 of 288 records — and never randomly: the disagreement always pointed the same way,
from a specific type toward a general one. A directional disagreement is a *migration in flight*; a
random one is noise. They take different verdicts, and the direction is cheap to compute.

**Grounding granularity is a property of the endpoint, not the content.** One product ships three
citation transports off a single generator: a non-streaming path with no grounding at all, a streaming
path with claim-level grounding where the cited text is the supporting quote, and a third using a text
fragment that resolves to a highlighted sentence. An earlier round of that same teardown concluded the
product had no claim-level grounding — true only of the path it probed. **Enumerate a system's
transports before concluding it does not bind claims to evidence.**

# Which artifact counts: a narration is not the record

**When the question names a period, the primary is the filing for THAT period.** An earnings-call
transcript narrates numbers that have already been rounded — *"revenue grew about 27%"* — where
the filing carries the tabular line items. A transcript is a source about the record; the filing
is the record. Where both exist and they disagree in precision, the filing wins and the transcript
becomes evidence about how the company described it.

And the period must match: **a Q1 2025 10-Q does not satisfy a question about Q3 2024.** Different
period, different tables. This is the shape of the miss — topically right and numerically wrong —
and numerical-precision misses of exactly this kind are the largest avoidable category of factual
error, because everything about the citation looks correct.

The same holds outside finance: a press release dated to the change, a changelog entry, a filing
history, a commit — the dated artifact beats the article describing it.

# Read the figure, never eyeball it

A chart, or a PDF with no text layer, is not an EMPTY lane. **Resolve the image and transcribe the
plotted numbers verbatim as the quoted span.** If you cannot read a value off the image, that value
does not ship — you have a picture of evidence, not evidence.

**Never state a number you did not read off the saved artifact.** A number inferred from where a
bar appears to end is a fabrication with a citation attached, which is the worst shape available:
the span exists, the source is real, and the figure is invented. `figure-support-gate` checks
whether a cited figure appears in the note cited; it cannot check whether you read it or guessed it.

<!-- source-quality-signals -->
# Source-quality flags: flag, never suppress

A source can be reachable, real, on a good domain, and still not carry the weight a sentence puts
on it. Name the defect next to the citation rather than dropping the source — dropping it loses
the evidence that the claim is circulating, which is often itself the finding.

| Flag | What it means |
|---|---|
| `aggregator` | restates another source; the upstream primary is what you want |
| `false_authority` | an institution's name attached to something it did not measure |
| `nameless_source` | "experts say", "according to reports" — no actor you can count |
| `vague_qualifier` | "significantly", "most", "up to" with no denominator |
| `unconfirmed` | reported once, never independently reproduced |
| `marketing_spin` | the seller describing its own product's performance |
| `speculation` (as finding) | a future-tense prediction restated as something that happened |
| `cherry_picked` | one favourable slice of a result whose other slices are absent |

Two things this table is for. **Domain tier does not clear a flag** — a vendor's "X is the best"
listicle on a high-tier domain is still marketing spin, and a filter that scores by domain will
pass it. And **a flagged source may not be cited bare as established fact**: it travels with its
caveat, or with an unflagged source that corroborates it, or it does not carry the sentence.

*Speculation as finding* is the one that reads cleanest and is easiest to miss — a source's
"this will likely reach X by 2027" becomes "X reached" one paraphrase later, and every check here
passes on it.

# Before you read closely — three cheap filters

- **The one new thing, in a sentence.** Before a close read, say what this source adds that the map does
  not already hold. "In a good paper this is answerable in a sentence: your goal is to find that
  sentence" (Carlini). If there is none, skim it and move on.
- **Predict first.** Write the result you expect before you read it, and note the gap; a surprise is a
  frontier item, and a source that only confirms you adds confidence, not accuracy.
- **The boring explanation.** After reading, ask whether it tested the dull alternative that would
  produce the same observation. It is "one of the most common reasons" one interpretability lead
  dismisses a paper, and he estimates "at least 50% of papers are basically useless due to insufficient skepticism".

# Judging a source you do not know — leave it, and grade it apart from its claim

The flags above describe a source you have read. Most of the junk is cheaper to catch before that.

**Leave the page and read about it.** Professional fact-checkers left an unfamiliar site within about
half a minute and looked it up elsewhere; PhD historians read it closely and were fooled by its
reference list. "Fact checkers, in short, learned most about a site by leaving it." (Wineburg & McGrew,
2019; 10 per group — small.) A lateral read asks two things: **who is behind this** (funder, owner, the
front group behind a friendly name) and **was the signal manufactured** (coordination among the
accounts pushing it, throwaway accounts, synchronized stars or reviews). Industry-sponsored trials
reached favourable conclusions more often (RR 1.34) while scoring *better* on standard risk-of-bias
checks, so the funder is its own axis, invisible to a methods check.

**Grade the source and the claim on separate axes, then watch them merge.** Intelligence doctrine rates
the source's reliability apart from the information's credibility; measured analysts collapse the two
onto one scale anyway. Keep them apart in the map: *source* — known good / no track record / known bad;
*claim* — independently confirmed / single source / contradicted. **No track record is not a negative**
— the doctrine says so explicitly (Admiralty grade F: "does not necessarily mean that the source cannot
be trusted, but that there is no reporting history") — and for a small or new source it is the usual
case. Then judge the
work on its own terms: re-run it, check its numbers (a reported mean that is impossible for its n is a
mechanical flag), check what its bibliography rests on.

**Never decide whether a claim is TRUE by searching its own words.** People encouraged to search a
false article's claims came to believe them *more* (+19%); 77% of queries built from a false article's
headline or URL returned an unreliable link in the top ten, against 21% for other queries (Aslett et
al., Nature 2024 — fresh news). A phrase nobody else uses returns the ecosystem that coined it. Search
the topic in the field's own words, or find better coverage of the claim from sources that did not
carry it to you. Searching its exact words to find where it came FROM is a different move, and allowed
— then judge that origin laterally.

**The unpopular corner is where planted content wins.** A low-traffic query is a data void: whoever
prepared content for it in advance owns the results. So an obscure source must pass a lateral read
before it carries weight — and a genuinely neglected one usually does (independent sources outside its
own ecosystem mention it; its producers show no coordination), while a planted one does not. Neither
test is measured; say which you ran.

# Weight testimony against interest UP

The flag table above gives eight ways to *discount* a source and no way to *promote* one, so a
filter built from it systematically under-weights the strongest evidence class there is.

**When a source says the thing that costs it something, that is worth more than a neutral source
saying it.** The concrete shapes, all of them cheap to spot:

- **A shipped default that declines the vendor's own feature.** A vector database whose docs ship
  its index *off* by default, a search product shipping its reranker disabled, a threshold set where
  the feature stops paying — that is the vendor telling you where their own thing stops working, in
  the one place they cannot spin it.
- **A team removing a feature it built and announced.** Killing your own A/B arm is a measurement
  reported against interest.
- **A negative result somebody paid to publish** about a tool they like.
- **A study commissioned by opponents, with leading questions, that still returns the answer they
  did not want.**
- **A prompt that patches out its own tool.** A system whose own instructions tell the model to stop
  using a capability that system ships is reporting a failure nobody made it report.

The mirror is the discount you already have: a vendor's headline number about its own product is
marketing, whatever its domain tier. **The same source can be both** — a launch post's benchmark is
marketing and its buried scope caveat is testimony against interest. Take the second and flag the
first, in the same citation.

**Revealed preference beats stated preference.** What a team *does* under cost — what they shipped,
what they turned off, what they quietly reverted — outranks what they say in a post about it.

# Selection on the outcome you are studying

The record you are searching was produced by a filter, and often the filter selected on exactly the
thing you want to measure.

- **Adoption is announced; reversion is silent.** Nobody publishes a retreat. So a corpus of "teams
  who adopted X" is not a sample of teams who tried X.
- **Failed replications are rarely written up**, so the literature over-represents results that
  worked the first time.
- **Every famous example is an outlier**, which is what made it famous and what makes it a bad
  guide. Advice derived from blockbusters — including any list of "how the best teams do it" —
  inherits that selection.
- **The set of unconflicted sources can be genuinely empty**, and that emptiness is itself the
  finding, not a gap to paper over with a conflicted one.

So an **absence in a literature is weak evidence of absence in the world**, and it is precisely the
inference an EMPTY lane otherwise licenses. Say which filter produced the record before you read a
silence as a result.

# A correction this skill had to make to its own opening sentence

`SKILL.md` opened with *"Of seven open-source research engines read in source…"*. The sweep behind
it read **eleven**, and says so twice. So the thesis sentence of a document that MUSTs a denominator
beside any count carried a wrong one — which is the failure mode in its purest form, because nobody
audits the sentence they are most sure of.

Two things were wrong, not one. The number, and the scope: the finding is about eleven OSS research
engines chosen for that lane, not about the field. A twelfth, shipped in a regulated domain where
"is this supported" is a legal requirement, binds claims to supporting evidence properly — with a
separately trained extractor (BM25 HA=65 against trained HA=94; generative models asked to do the
same extraction score F=5.6 and F=26.8) — and publishes the one class it cannot bind: negative and
absent assertions, whose evidence is the source's silence.
