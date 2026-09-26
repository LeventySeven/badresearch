# Rounds — the map, the brief, the moves, the stop

Read this when you run a standard or deep question. SKILL.md holds the loop; this holds what you need
at each boundary of it. Everything here was drawn from how the best researchers, investigators and
multi-agent systems actually work — the evidence is `docs/sweeps/2026-09-26-how-researchers-find/`
in the repo (`FINDINGS.md` first).

## The map

One file per run: `research/<slug>/MAP.md` in the working directory. Only you write it. It is the one
thing readers receive, so it holds knowledge and nothing else — no summaries of sources, no prose.

```markdown
# <slug> — map
Question (verbatim): …
What the asker will do with it: …                       ← never shown to readers
Tier: standard | deep — because …

## Open questions (ranked: how much the answer depends on it × how uncertain or contested)
- Q1 … [open | closed by F3,F7 | abandoned: <reason>]

## Findings  (one line each; the span is verbatim)
- F1 [Q1] <claim> — "<span>" — <URL + fetch date | path:line> — reached by <query | link from F? | lane>
       — source: <author/publisher, date, who pays / what they sell> — grade: <see evidence.md>

## Frontier  (named in a source, not yet chased)
- <entity | term | person | paper | number> — seen in F? — [unchased | assigned R2 | chased: F?/dead end]

## Connections and contradictions
- F2 ↔ F9: <what links them, or how they disagree; window/primary diagnosis>

## Dead ends  (so no reader repeats them)
- <query or route> in <lane> — <EMPTY | BLOCKED | MISSING | EXHAUSTED | IRRELEVANT-BY-DESIGN> — <what was tried>

## Seen sources
- <URL/path>, …

## Hypotheses and rivals                                   ← never shown to readers
```

Two other stores exist and are named, not hidden: `research/<slug>/s.json` (the stop counters —
numbers, not knowledge) and `research/<slug>/raw/` (each reader's return, saved verbatim by you,
because readers cannot write files). Nothing here is an index, a graph database or a cache across runs:
it is addressable, re-derivable, and deleted or archived with the run. Individuals keep a list of open
questions and a log; that is this file. (Teams working a name-dense leak keep entity graphs — ICIJ,
OCCRP. If a question is that shape, the Frontier and Connections sections are where it shows.)

## The brief — what a reader gets

A reader gets a **snapshot**, never the map itself:

- the question, **verbatim**
- its assignment: a lane (broad round) or one to three leads (deep round), with a boundary — what it
  must NOT read, so boundaries can be checked for overlap before a token is spent
- the findings, frontier items, dead ends and seen sources that touch its boundary, headed *"already
  known — do not re-find; extend, connect or break it"*
- its budget: a lead 5–20 tool calls, a lane up to ~50. Past it, return what you have.

It never gets the hypotheses, the rivals, or what the asker will do with the answer. Readers told what
you are building return opinions instead of facts. A counterpart assignment is phrased as a question —
*"is there evidence that X failed to replicate, or that its origin is weaker than its citers claim?"* —
not as your position.

**What comes back** (`agents/research-reader.md` enforces it): findings with verbatim spans, the
source, and how each was reached; the reachability state of every source tried; source facts for
grading (who wrote it, when, who pays or what they sell — and, when assigned, what others say about the
source); frontier items as exact strings; dead ends; seen sources. No grade, no conclusion. You grade.

## The broad round — find the structure

Its job is the representation, not the answer: which open questions exist, what the field calls things,
which clusters of work there are. Everything later is filling that in, and a finding no open question
fits (residue) is the signal the structure is wrong — add the question.

- **3–6 readers in parallel, each on a lane of a different KIND** — papers; practitioners' own writing
  (essays, threads, talks); code, data and registries; community threads and replies; the local corpus;
  another field or language. Different kinds, because seeds that all sit in one cluster never reach the
  others, and you cannot pick clusters you have not found yet.
- **Make the first queries different from one another.** Diversity at the first move is what counts;
  diversifying later turns measured as adding nothing.
- **In every lane, one entry point that is not ordered by popularity** — newest-first instead of top,
  past the first page, reply threads, an under-cited sweep, the field's penumbra rather than its core.
  On X, the Top tab returned authors with a median 19,128 followers; Latest, 3,865; the sharpest methods
  in one harvest came from under 50k-follower accounts and from replies.
- **The plain, obvious search first**, even with a hypothesis in hand. Expert assumptions are what make
  expert searches slow.
- **Widen when an unfamiliar field overloads you**; be more selective when good sources are plentiful.
  Analysts who only narrowed under a deadline all missed key documents.
- **A well-defined target** (a known item, a yes/no): the broad round is the obvious search plus one
  different lane, and a decisive primary closes that question.

## The deep rounds — every assignment is a named move drawn from the map

| the map shows | the move |
|---|---|
| an open question | a direct query in the field's own vocabulary (learn it from overviews and the index terms of the first good documents) |
| a finding with one source | trace it to its origin; look for an independent rerun inside the original's "cited by" (`experiment OR replication OR randomized`) — failed reruns are cited by a small minority of later citers, so they will not come to you |
| a contradiction | resolve it: the window each covers, and which one read the primary |
| an unchased frontier item | chase it: references back, citing papers forward (sort them by their own citations to surface the pivotal ones), the author's other writing, the same thing under another name or language |
| two findings from different lanes | ask what connects them — hold one facet near and push one far; most pairs connect to nothing, which costs one query |
| the leading claim | its counterpart: criticism, failed reruns, and the record that would have to exist if it were true |
| residue | a new open question |
| a BLOCKED or MISSING lane | another route (`silver`, an archive, a mirror) — never a verdict |
| a dead end | never retried the same way |

**Rank open questions by how much the answer depends on them × how uncertain or contested they are,
and send readers to the top first.** One reader per independent group of assignments, at most six per
round; assignments that depend on each other stay with one reader, who chains them in order.

**Between rounds you pool:** save each return to `raw/`, admit findings into the map (one line, span,
source, how reached), grade sources from the facts, add frontier items, record dead ends, update the
seen list, rank the open questions again, and call the counter once:

```bash
bad frontier-observe --state research/<slug>/s.json --floor <2|3> --patience 1 \
  --domains <new source domains this round> --entities <new frontier items admitted> \
  [--promise Q1,Q2 | --close Q3 | --abandon "Q4=reason"]
```

**Admission.** Before a finding carries weight in the answer, re-open its source and find the span —
a fetch and a grep. A span you cannot find demotes the finding to a lead. Every finding keeps its source
identity, because when several readers report "the same" fact from sources that all rest on one origin,
that is repetition, not corroboration — the Iraq WMD commission's fix was exactly "distinguish
corroboration from repetition".

## The stop

`frontier-observe` computes it: the floor (standard 2 rounds, deep 3), then one quiet round — no new
source domains beyond noise and no new frontier item — with every open question closed or abandoned with
a reason. Before you accept it, one last search in a different vocabulary or a different lane.

**Saturation is not a certificate.** A stop on "nothing new is turning up" missed its recall target 39%
of the time in systematic-review screening, and lawyers who searched iteratively believed they had 75%
of the relevant documents when they had 20%. A good search runs dry early; running dry is exactly what
fools the rule.

So in the deep tier, and on any question whose answer is a set or an absence ("find all", "is there any
evidence that"), run **one independent check pass** before stopping: a fresh reader, given only the
question, that never sees the map and searches by a different method (another kind of lane, another
vocabulary). Open its return only at the stop check. What it found that the map lacks is a blind spot —
the run is not done; chase it. This is deliberate redundancy, the one place readers may re-find things,
and it is there because independent searches that overlap are both a relevance signal and a recall
check. The open web has no sampling frame, so it is a relative-recall check, not a guarantee — say so.

## What this replaced, and why

The earlier skill ran one reasoner with optional fan-out and forbade parallel depth on the strength of
"17.2× error amplification". That figure is trace-level and not significant after controls, and the
"39–70% loss" beside it is a planning benchmark. On the same paper's web-research benchmark, readers
that never exchanged lost 35% to one agent (with one model family; not with another), and readers that
exchanged their work between rounds gained a little. The shape here — parallel inside a round,
exchange through a gated map at the boundary, judgment kept with you — is the one the stronger evidence
points to: a shared verified board read at dispatch, with dead ends shared too, beat isolated attempts
on code and long-document tasks, and forecasting teams that shared information but each gave their own
number, pooled, beat both independents and crowd-watchers in a randomized trial. Free, continuous
sharing is refused: it herded over 90% of 533 active agents onto one workstream.
