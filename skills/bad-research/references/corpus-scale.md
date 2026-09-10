# When the evidence stops fitting in the window

Read this when a run has gathered more than you can hold — dozens of sources, a long transcript,
a corpus you are sweeping rather than sampling.

The main skill says: **do not build an index over any of this** — no embeddings, no findings
cache, no summary of summaries. That rule is right and it stays. A production findings-cache
measured **zero hits in 133 attempts**; the corpora grow most days, so a stored summary is stale
by construction; and `grep -n` over a few hundred markdown files is the correct retrieval at that
size and is current by definition.

But the rule carries a condition, and the condition is the whole reason this file exists: a
memory layer measured **zero capability gain and pure cost while the material fits in context**,
earning its keep only once evidence sits *outside* the window. Stating the rule and never saying
what happens when its condition lapses is how a run past that point improvises — which in
practice means re-fetching what it already read, or answering from whatever survived compaction.

## The distinction that decides it

**A store is legitimate here when it is re-derivable and addressable. It is not legitimate when
it is searchable in place of the source.**

- *Addressable* — you can name the thing and go back to it: a path, a URL plus a fetch date, an
  id you wrote down. Reopening costs one read.
- *Re-derivable* — if the store vanished, re-running the same reads would rebuild it. Nothing in
  it is knowledge that exists only there.

An index fails both. It answers *from itself* rather than pointing at a source, and its embedding
of a page you can no longer re-derive is a summary you will end up citing.

## What to keep, and what it is for

**A read log — what you opened, and what it produced.** One row per source: what you read, what
came out of it, and **an honest empty when nothing did**. The empty row is the valuable one: it
is what stops the next round re-reading a source hoping. Mark delegated reading as delegated —
what a reader returned is not what you read.

**Dispositions over a target you re-scan** — *rejected, and why, in the reason's own terms.* This
is explicitly permitted by the main rule and it is the cheapest thing here: on a pool you sweep
more than once, a disposition means the second sweep does not re-decide what the first one
settled. Keep the reason, not the verdict alone — a bare "rejected" cannot be reviewed, and it
cannot be reversed when the question shifts.

**Caps on how much of a file you read.** This is where the cheap half of an index's benefit
actually lives, and it needs no index. Grep buys recall and pays in precision: about **one file
read in three was wasted**, and reading a **50-line window** around the hit rather than the whole
file cut that to one in five.

**The open promises.** The cells the answer owes and has not filled. This is the half of the stop
rule that a long run forgets first, because new arrivals feel like progress while a promised cell
sits open. `bad frontier-observe --promise/--close/--abandon` holds these outside your context on
purpose, which is the point: the counter is computed before the next prompt is built, not
recalled.

## What NOT to keep

- **A summary of a source, in place of the source.** The next reader cites the summary. A pooled
  summary of a summary is not evidence and it systematically loses the thing worth having.
- **A findings memo across runs.** Measured dead, and it makes a stale claim look like a
  retrieved one.
- **Anything you cannot re-derive.** If losing the file would lose a fact, the fact was never
  grounded.

## Two failures specific to working past the window

**Your own notes contradict each other and nothing will tell you.** Options you were weighing get
written down as things that happened — one memory system logged its user visiting two countries
on overlapping dates, from a conversation that was *deciding between* them. Two of your own rows
that cannot both be true is a frontier item, not bookkeeping.

**Enumerate live, every run.** A count written in a document is stale the moment the corpus
grows, and these grow most days: one corpus went from ~395 items to 407 *inside a single
session*. Never work from a number a file states — including a number this skill states. `ls` and
`grep` it now.
