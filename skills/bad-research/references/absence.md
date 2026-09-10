# Absence — the five kinds of nothing, and what each licenses

SKILL.md carries the table. This is what stands behind it: how to widen before you conclude, what an
EMPTY has to state to count, and the two shapes that beat every check in the file.

## Widen first, and say what you could have detected

One literal phrase returning zero is not evidence. Try the term the field uses, the abbreviation, the
author's name, the adjacent concept. A cold run credited that single rule with stopping a false "not in
corpus" after one zero-hit grep.

Then the part that is usually skipped. **A failed query rules out an instantiation, not an approach** —
one phrasing is a vanishing fraction of the ways a thing can be said, and *"I tried and it wasn't
there"* is the most over-claimed sentence in research. Prune the conceptual branch only with an
argument for why the branch is empty; feeling that it will not work is explicitly not ruling out.

Medicine names the same gap and has a discipline for it: **state in advance what size of finding you
could have detected.** A trial whose interval excludes the minimum important difference is genuinely
negative; one whose interval includes it is underpowered and says nothing — and both look like "no
significant difference". Without the equivalent declaration, a real zero and an unreachable one are
indistinguishable, and what you have is a widened MISSING.

## Query construction, from people who do this professionally

Four rules from an information specialist, each with its evidence:

- **Leave out the facet whose vocabulary you cannot enumerate.** Clinical search frames a question as
  population / intervention / comparison / outcome and then routinely omits the *outcome* term from the
  string, because it is too easy to miss one of the words that would express it. Fewest concepts wins;
  a manageable result set is still in the thousands.
- **Use exclusion to price a term, never to ship one.** Add a candidate term, see it added 50 records,
  then exclude everything else to read exactly those 50 and judge whether the term earned its place.
- **Re-express the query in each lane's own vocabulary.** The most common defect found in *published*
  search strategies is a string pasted across databases without adapting to that database's controlled
  vocabulary, truncation symbols and syntax. A query reused verbatim across lanes is the field's named
  number-one error.
- **Multiple lanes is an empirical claim, not a ritual** — and it held: across five topic areas and
  four databases, every one of the four contributed unique records in every one of the five areas.
  Hand-searching separately identified relevant trials at 92–100% accuracy where database search was
  less sensitive.

And the reason to run a load-bearing query at least two ways: a study of a search engine found that
**misspelling one letter of a query term returned the opposite claim**, and the study underpinning the
flipped answer had its comparison group reversed relative to what the output asserted.

## The two shapes that beat every check

**IRRELEVANT-BY-DESIGN.** Anti-bot systems now answer a detected crawler instead of blocking it.
Cloudflare's own description of Labyrinth is explicit that it will *not* generate inaccurate content —
*"the content we generate is real and related to scientific facts, just not relevant or proprietary to
the site being crawled"* (blog.cloudflare.com/ai-labyrinth/, read 2026-09-09). So the span is genuine,
the quotation is verbatim, byte-identity holds, and the support verdict passes. It fails **only**
relevance. The check is therefore not about the text: confirm the page is about the site you fetched it
from. A related instance of the same shape — a page whose content depends on who asked, returning
different prices by device or proxy — means "I fetched it" and "this is what it says" are different
claims for any commercially interesting URL.

*(Recorded because it is the honest provenance: this row was first written here from a competitor's
account, which said the content was fabricated. It is not. Read the primary before repeating a claim
about somebody's product — especially one that agrees with you.)*

**UNSAMPLED.** The lane is healthy, the query is right, the zero is real, and the conclusion is still
wrong, because the region where the thing would have appeared was never in the sample. A deployed agent
asked to justify its opening hours ran the analysis, found it had made no sales outside them, and
concluded they were optimal — having never once been open outside them. Before reading an absence as
evidence, ask whether you ever sampled where the thing would be. A lane you did not drive is not a lane
that came back empty, and *not driven* is a legitimate thing to write down.

## What the enumeration line is for

Every lane emits `lane | files listed N | candidates selected N | cut line <what>` — including a lane
that selected zero. The cut line is the part that matters: it says what you decided not to read and
why, which is the only thing that distinguishes a narrow search from an absent one. `bad lane-local`
prints it for the corpus lane; `scripts/lane-probes.sh` makes every lane state its own reachability so
that none of them can return silence.

# A figure is not an empty lane

A chart, or a PDF with no text layer, comes back with no matchable text — and every string search
you run on it returns nothing. That is not EMPTY. The lane is healthy, the artifact is there, and
the number you want is in it.

**Resolve the image and read the values off it** (`references/evidence.md`, *Read the figure*).
Filing it as EMPTY is the worst available outcome, because EMPTY is the one state that licenses
"not in corpus" — so a picture of the answer gets reported as the answer's absence.

# Before you write an absence claim, run the gate

```bash
bad absence-gate --report <draft>.md
```

It lists every absence claim in the draft and flags the ones that name no **search scope**. That
distinction is the whole rule, and it is worth stating twice: **the qualifier must bound where you
LOOKED, not what you were looking FOR.**

Measured, on this skill's own output. This shipped and a blind judge overturned it in one fetch:

> No source measures the false-negative rate of a source-quality filter directly. … Nobody
> publishes "we rejected N documents a human judged relevant."

A comparison run got the *same fact* right, and the only difference was scope:

> … and no published work **in this corpus** has sampled and read at comparable scale what a
> production **pretraining** quality classifier threw away.

Note what does not rescue the first one: its subject was already extremely narrow — a
*direction-split false-negative rate of a source-quality filter* — and it was still false of the
field. **Narrowing the subject is what makes a false absence claim sound careful.**

The gate is a triage list, not a verdict. It cannot tell you an absence is false; only finding the
thing can. It tells you which of your absence claims are stated in a form nobody could falsify.
