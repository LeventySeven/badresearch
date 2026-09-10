# Noise — telling the real thing from what looks like it

Finding is the easy half. Five mechanical sweeps in this project returned 110/58/52/29/20 hits and
collapsed to **31/0/0/0/0** on reading. The finding rate was fine; the garbage rate was the problem,
and every gate in this kit measures whether what you *wrote* is supported — none scores whether a
candidate is real before you pay to read it.

And the filter should get better as the run learns. That is not a slogan: it is measurable, and the
mechanisms below are the ones that survived adversarial verification.

## Two halves, because a run starts with no decisions to learn from

**Cold start — a cheap structural signal.** Order the pool by something free before reading any of it.
Measured on this corpus: 407 teardowns, 5 known to carry researcher names, ranked by author/arXiv
marker count. Top 5 → 60% recall; top 10 → 80%; **top 20 → 100%**, and 313 of 407 score zero and are
free to exclude. A 20× cut in reading cost. `rank_by_signal`. The signal is question-specific — author
markers stand in for researchers and for nothing else — so a different question needs a different
signal and inherits none of that measurement.

**Then accrete.** A reject-signal is a token recurring across *rejected* items and absent from every
accepted one. Two decisions buy nothing; fifteen bought five real signals. `bad discriminate`. The
exclusion is the load-bearing half: a token present in even one accepted item is about the subject
matter, and learning it is how a filter starts deleting the good ones.

**Run them in that order, not in parallel.** A fixed rule costs nothing and never improves; a learned
one costs decisions and compounds — so the accreting layer should never spend a decision on something
already obviously junk. `bad cascade` composes them: the shipped web prefilter first (`seo_farm_score`,
`domain_tier`, `is_blocklisted` — measured here at 2 signals on a content farm, 0 on arXiv, which it
tiers `reference`), then the learned filter on survivors only. Two things it must report and does:
every cut names **which layer** made it, because a regex's *reject* and a run's *reject* are different
claims; and an item carrying no URL — a person, a filename, a transcript heading — is counted as
`web-prefilter-skipped`, never as a pass, because the web layer returns `seo=0 / tier=blog` on all of
them and a layer that cannot see an item must not be recorded as having cleared it. The canary verdict
is taken over the **whole cascade**: this was wrong first, reading only the second layer, so a canary
the regex killed came back as *tested nothing* and the report printed clean.

## The three rules that keep a filter honest

**Abstain rather than reject when you do not have enough to judge.** This is where the recall actually
comes from. A shipped clinical screening classifier's **5.7 points of recall came entirely from an
abstain rule**, not from the model: records below a minimum title/abstract length are never classified
and always pass through. Without it the pipeline silently deleted **3,600** real included studies; with
it, **224**. A short item matches few tokens, so a token filter is least reliable exactly where it
looks most confident. `min_evidence_chars`.

**Plant canaries IN the pool.** Known-good items, screened alongside everything else. If the rules kill
one, the filter has over-learned and the run is told which rule did it. Reproduced here: eight
decisions over a directory that mixed researchers with ops taught a filter that `allen` and
`institute` mean garbage, and it killed five named researchers. A canary held in a separate list is a
note-to-self — it must be *screened*, or it tested nothing and the verdict is `None`, never safe.

**Your known-good set is itself suspect.** On a standard benchmark, crowd assessors preferred a neural
ranker's top passage over the *official gold label* **58%** of the time. So "it does not match the
known-good exemplar" is a weak reason to delete something, and more than half the deletions in that
study were of the better item. Canaries bound the filter; they do not certify the label.

## What breaks a filter that looked fine

**A threshold is only meaningful against the negative distribution it was calibrated on.** Change only
the negatives at test time and calibration degrades sharply — nothing about the model changed. So
reject-signals learned on one pool do not transfer to another, and carrying them across is the quiet
version of this failure.

**Popularity and venue invert as quality proxies.** Of 18 deep-learning recommendation papers from top
venues, only **7 were reproducible, and 6 of those were beaten by simple baselines**. Nobody asked
which unfashionable method would have won — that absence is the finding. Rank-ordered sources measure
audience size twice and quality never.

**Learned adaptive cutoffs do not beat a constant.** Across 8 truncation methods, 3 retrievers and 2
re-rankers, per-query learned truncation failed to beat a hardcoded top-k — and the word *recall*
appears zero times in a paper entirely about what to discard before the expensive stage. Do not build
the adaptive version; pick a constant and measure what it cost.

## Almost nobody measures what their filter killed

Across 16 screening-methodology papers, **exactly one** goes downstream from "we missed X%" to "did the
answer change". And the cost is **bimodal, not proportional** — it concentrates in one bad screener
rather than spreading across a miss rate, which means an *average* recall figure hides the case that
matters. Precision is visible (bad things that got through); a filter's false negatives leave no trace
at all unless you plant one.

## Stopping a screen with a guarantee instead of a feeling

Screen in ranked order, then draw a **random** sample of the unseen remainder. If it turns up almost
nothing relevant, reject the hypothesis that you missed your recall target. `bad screening-stop`
(`can_stop`), exact hypergeometric, no dependency. Reported in the source literature at reliable recall
for ~17% work reduction.

It accretes in the strict sense — the same clean sample, three points in one run:

| found | unseen | may miss | p | stop |
|---:|---:|---:|---:|---|
| 5 | 400 | 0 | 0.7250 | no |
| 40 | 250 | 2 | 0.1740 | no |
| 95 | 200 | 5 | **0.0076** | **yes** |

The criterion never changed; only what the run knows did. And the guarantee is not cheap: measured
here, **80 of 200 — 40% of the remainder — must be sampled** to license a 95%-recall stop. The sample
must be RANDOM; taken in rank order it measures the ranker, not the pool, and the guarantee evaporates
without a word.
