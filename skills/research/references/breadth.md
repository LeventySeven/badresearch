# Breadth — "find all X", which is a different job from "is this true"

Everything else in this skill is built for depth: one claim, chased until it holds or breaks. A
question shaped *find all the articles, podcasts and videos by the great AI researchers, including the
obscure ones* inverts every part of that, and the machinery quietly fails in ways the depth checks
cannot see.

## What changes

| | depth question | breadth question |
|---|---|---|
| the unit of an answer | a claim | a **set** |
| the metric | precision — is what I said supported | **recall** — is what belongs here here |
| the stop | the frontier is empty | you cannot exhaust it; you can only **estimate coverage** |
| the failure | a wrong number, loudly wrong | a **missing row, silently absent** |
| what a check sees | every gate here | **none of them** |

Every gate in this kit is scoped to what the answer already contains — `uncited-gate` asks whether the
sentences you wrote carry markers, `figure-support-gate` whether the figures you cited are in their
notes. A breadth answer can pass all of them at 100% and hold a third of the population. Nothing in the
depth path will ever say so, and the run will feel finished, because *feeling finished* is what the
frontier's emptiness is measuring.

## Name the frame before you search

**"All" is unfalsifiable until you say all of what.** Write the population definition first, in one
paragraph, with its inclusions and — harder and more useful — its exclusions. Then every later
judgement is a consistent application rather than a fresh opinion, and someone can disagree with the
frame instead of with your taste.

Give every reader the *identical* definition, verbatim. Two readers applying two definitions produce
two populations, and their overlap then measures nothing at all.

**Over-include at the edge.** Mark a doubtful item `[borderline]` and keep it. A consistent
over-inclusion is visible and reversible; a silent omission is neither, and it is the failure this
whole regime is about.

## Estimate coverage; do not assert it

You cannot count what you did not find. You *can* estimate it, the way a population of fish is
estimated — search twice by genuinely different means and look at the overlap. If pass one finds `n1`,
pass two finds `n2`, and `m` appear in both, the population is about `n1·n2/m`. `bad coverage
--pass lane=file --pass lane=file` computes it and refuses when it cannot.

**The independence assumption is the whole method, and it fails in one direction.** Two passes that
share a bias — both ranked by popularity, both seeded from the same list, the same lane run twice —
overlap more than chance. Inflated overlap shrinks the estimated population, which reports *high
coverage exactly when the obscure tail was missed by both*. That is precisely the failure mode for a
search that was asked to find the unpopular ones, so the command refuses those pairs rather than
returning a flattering number.

**Read the singleton fraction before the estimate.** Items found by exactly one pass are the shape of
the tail. When most of what you hold was seen once, the population is much larger than you sampled,
whatever the point estimate says — and the estimate is least reliable exactly there.

Three good passes for a person-shaped population, and they are different *methods*, not different
queries:

- **a curated local library** — rank-blind, already filtered by someone's judgement, blind to anyone
  nobody has written down yet
- **live search** — wide and current, and ordered by audience size, which is the bias to fight
- **link-walking** — start from a small seed and follow co-authors, acknowledgements, blogrolls,
  citations, co-speakers. This is the pass that reaches people no ranking surfaces and no library
  indexed, and it is the one most often skipped

## Fight the ranking on purpose

*"Even the most unpopular but still great"* is a requirement, not a flourish, and every default in
every tool works against it. Search engines order by audience. Citation APIs order by citation count.
Both are measuring the same thing twice, and neither is measuring quality.

So spend at least half the effort on entry points that are **not** ordered by popularity: lab
team-and-alumni pages, conference accepted-paper lists, workshop programmes, course staff pages,
newsletter archives, acknowledgement sections, and the "people I read" links on personal sites. Say in
the report which entry points you used — that sentence is the difference between a search that fought
the ranking and one that inherited it.

## Dedup is a real step, not bookkeeping

One person is `A. Karpathy`, `Andrej Karpathy`, `@karpathy` and `karpathy`. Merged wrongly you
understate the population; merged too little you inflate your own coverage. Normalise before you
compare passes, keep the surface forms, and note that an entity-merge is the classic place a corpus
silently loses a source link — when two records merge, one parent's provenance is the thing that gets
dropped.

## What "done" looks like here

Not an empty frontier. A breadth run is done when it can state, in one line: **what frame it searched,
how many it holds, its estimated coverage with the pair that produced it, its singleton fraction, and
which method it did not run.** A run that cannot say those five things has not finished — it has
stopped.

And the last of the five is the one that is always available and usually omitted. A method you did not
run is not a method that came back empty.
