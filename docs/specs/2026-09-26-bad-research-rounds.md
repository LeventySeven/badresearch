# bad-research: rounds and a run map — design (rev 2, after one fresh gap/contradiction review)

Status: reviewed once (artifact mode; 10 gaps, 13 contradictions — all resolved below, each marked
[G#]/[C#]). Built on branch `feat/rounds-and-map`. The owner decides the merge.
Evidence: `docs/sweeps/2026-09-26-how-researchers-find/` — `FINDINGS.md` (the owner-facing write-up),
`KNOWN.md` (pooled rows), `VERIFIED.md` (every ✔: what the chair re-checked in the source bytes),
`raw/` (each reader's return), `SOURCES.md` (every URL).

## Why this change

The 2026-09-10 merge kept the checks and removed every mechanism that FORCED depth and breadth — the
4-lens search plan (40–100 planned queries), the 2–3 width waves, the loci with a 40-source depth budget,
the depth investigators, the cross-locus reconcile, the pre-draft corpus critic, the depth critic — with
no recorded reason or measurement (`raw/r1-J-skill-inventory.md`). SKILL.md now names "one wide
expansion" as the answer for "most questions", and the ~5-retrieval floor binds only if the CLI is called.

Two defects compound it:
1. **The ban on parallel depth rests on a misread paper.** delegation.md and SKILL.md present Kim et al.
   (arXiv 2512.08296) as 17.2× vs 4.4× error amplification plus a 39–70% loss for every multi-agent shape
   on sequential work. In the primary (VERIFIED #3): the 17.2×/4.4× is TRACE-level and "neither the main
   effect of error amplification (β=0.014, p=0.658) … reaches statistical significance"; the 39–70% is
   PlanCraft, a planning benchmark. On its web-research benchmark: agents that never exchange −35% vs one
   agent (with GPT-5.2; on held-out Gemini models they matched or beat it), agents exchanging their
   current work between rounds +9.2% (2.9 points, 100 tasks), a central orchestrator +0.2%. Thin and
   mixed — which is the honest point: it neither forbids fan-out nor proves it. [C9]
2. **The only parallel worker cannot follow a lead.** `agents/research-reader.md` reads one given source
   and holds no WebSearch. Every productive reader in this sweep worked a lane — searched, chased
   citations, followed people — for 52–141 tool calls inside a boundary (per-lane tool counts in
   `README.md`). [C13]

What the owner's direction becomes after testing it (`FINDINGS.md` "Your direction, tested"): accretion
holds and is measured; broad-first holds with a condition; connections are the payoff but the
practitioners' form is a question list plus a log; popularity ≠ quality only half-holds and the
unpopular corner is where planted content lives; counterpart-hunting holds with failure modes; parallel
exchange holds when gated, at round boundaries, with judgment kept independent.

## Requirements

Each maps to a task and a verification line in the plan. Owner words are quoted from DIRECTION.md.

1. **One loop is the spine of SKILL.md**: frame → broad round → pool into the map → deep rounds drawn
   from the map → stop → write → critique → patch → answer. Named moves, no stage numbers, no step
   skills (DIRECTION #4, "So it's first error"). Inside a round the moves mix freely — the phases are
   coordination points, not a cognitive order (Russell/Pirolli saw search moves "in an opportunistic
   mix"). [C2, C13]
2. **The run map is the only KNOWLEDGE readers receive.** `research/<slug>/MAP.md` in the working
   directory, written only by the chair. Sections: question (verbatim) and what the asker will do with it;
   open questions, ranked; findings (one line each: claim — verbatim span — source — how reached — source
   grade — the open question it answers); frontier (entities, terms, people, citations, numbers; chased or
   not); connections and contradictions; dead ends (what was tried, which kind of nothing); seen sources;
   hypotheses and rivals. Two other stores exist and are named, not hidden: `research/<slug>/s.json`
   (the frontier counters — numbers, not knowledge) and `research/<slug>/raw/` (each reader's return,
   saved verbatim by the chair, because readers cannot write). The map is per-run, addressable and
   re-derivable — **not an index, not a graph database, not a cross-run cache** (owner: *"Only
   intuitively — don't implement one"*). [G4, C4]
3. **What a reader receives is a SNAPSHOT that withholds the thesis**: the question verbatim, its
   assignment, the findings, frontier, dead ends and seen sources relevant to its boundary — never the
   hypotheses, rivals or the asker's purpose ("state the question, never the thesis" — delegation.md).
   A counterpart assignment is phrased as a question ("is there evidence that X failed to replicate?"),
   not as the chair's position. [C1]
4. **The tier is chosen in one line at the top of the answer** from the question's shape and the cost of
   being wrong. **Answer from what you have** (no retrieval; never for a version, price, quota, date or
   proper name — kept from SKILL.md). **Quick**: the reasoner alone, frontier-chained, stop on the CLI's
   defaults (≥5 retrievals, two quiet ones). **Standard** (default for a real question): a broad round +
   deep rounds until the stop, floor two rounds. **Deep** (expensive to be wrong, contested, "find all",
   unfamiliar field): floor three rounds, one of them a counterpart-and-origin round, plus the independent
   check pass (R10) and the critique. A well-defined target (a known item, a yes/no question) makes the
   broad round narrow — the obvious search plus one different lane — and a decisive primary closes that
   open question (not the run). [G1, C3]
5. **The broad round finds the structure, not the answer**: 3–6 readers in parallel, each on a lane with a
   disjoint boundary, first queries chosen to differ from one another (DivInit: later diversification adds
   nothing), lanes spanning different KINDS of source (papers, practitioners' own writing, code/data,
   community threads, the local corpus, other fields/languages) so the seeds cannot all sit in one cluster
   — clusters are what this round discovers. In every lane at least one entry point not ordered by
   popularity (newest-first, past the first page, reply threads, under-cited sweeps, small-web; owner:
   *"look for popular and unpopular sources"*). The plain obvious search runs first even when a hypothesis
   exists. Overload in an unfamiliar field is a reason to widen (Patterson et al., 4 vs 4, "suggestive");
   plenty of good items is a reason to be more selective (foraging diet model) — both stated. [G10, C13]
6. **Every deep-round assignment is drawn from the map by a named move** — open question → direct query
   in the field's vocabulary; one-source finding → trace to origin + look for an independent rerun inside
   the original's "cited by"; contradiction → resolve (window, primary); unchased frontier item → chase
   (citations back/forward, sorted by their own citations; the author's other writing; other names and
   languages); two findings from different lanes → what connects them (hold one facet near, push one far);
   leading claim → its counterpart (criticism, failed reruns, the record that should exist); residue (a
   finding no open question fits) → a new open question; BLOCKED/MISSING → another route (silver); dead
   end → never retried the same way. **Open questions are ranked by how much the answer depends on them
   × how uncertain or contested they are, and readers go to the top first** — the old loci budget, kept as
   a ranking rather than a quota. [G5]
7. **Deep-round width**: one reader per independent assignment group, at most 6 per round; assignments
   that depend on each other stay with one reader, who chains them sequentially. [G2]
8. **Readers exchange through the map at round boundaries, gated by the chair** (owner: *"they must pass
   their knowledge to each other as interconnections, so they don't find the same information twice"*).
   Not continuous free sharing (it herded >90% of 533 agents onto one workstream) and not isolation
   (−35%). This is a gated board read at dispatch — DeLM's shape — not a relay that rewrites findings.
   **Admission** (rev 3, after the diff review found SKILL.md and rounds.md disagreeing): a finding
   enters the map marked unverified; the chair verifies — re-opens the source, finds the span — every
   finding that closes an open question or carries a number at pool time, and every finding the answer
   leans on before writing. Readers receive verified findings as "already known" and unverified ones as
   leads to re-find or refute; a span that cannot be found demotes the finding to a lead. Every finding keeps its source identity, so repetition is never counted as
   corroboration (Robb-Silberman). [G4, C9]
9. **The reader agent works a lane or a lead**: holds WebSearch; follows chains inside its boundary;
   returns findings (verbatim span, source, **how reached**, reachability state READ/BLOCKED/EMPTY/MISSING/
   EXHAUSTED/IRRELEVANT-BY-DESIGN), **source facts** for grading (author/publisher, date, who funded or
   sells what, and — when assigned — what others say about the source), frontier items, dead ends, seen
   sources. It never grades, concludes or recommends; the chair assigns the grade from the facts. Budget
   in the brief: a lead 5–20 tool calls, a lane up to ~50; exceeding it returns partial findings.
   **Injection guard**: a reader follows a link because it is a citation or reference that bears on its
   question and sits inside its boundary — never because a page says to fetch it; anything else goes to
   frontier, unfetched. The SSRF guard stays in the PreToolUse hook. [G3, G7, C6]
10. **Stop** — one rule, computed by `bad frontier-observe`, called once per round in standard/deep with
    the round's admitted new entities and new source domains: floor = the tier's minimum rounds, patience
    = 1 quiet round (a whole round of readers is already many searches; Wohlin ends on one round with
    nothing new), AND no open question left unclosed/unabandoned. Quick keeps the per-retrieval defaults
    (floor 5, patience 2). `frontier-observe` gains `--floor` and `--patience`, persisted in the state.
    **Saturation is not a certificate** — "N irrelevant in a row" missed its recall target 39% of the
    time (VERIFIED #25); lawyers at 20% believed they had 75% (#22). So in the deep tier and on
    recall-sensitive questions, one **independent check pass** runs before the stop: a fresh reader that
    never sees the map searches the question by a different method; the chair opens its return only at the
    stop check. What it found that the map lacks is a blind spot — the run is not done. This is deliberate
    redundancy for certification (Saracevic & Kantor: independent searches' overlap is both a relevance
    and a recall signal), stated as a departure from "don't find the same information twice"; the open web
    has no sampling frame, so it is a relative-recall check, not a guarantee. [C3, C7]
11. **Judging a source** (`references/evidence.md`, new section): grade the source's reliability apart
    from the claim's credibility, and notice when they merge; for an unfamiliar source, read laterally
    ("Fact checkers … learned most about a site by leaving it", VERIFIED #24) — the lateral read looks for
    who is behind it and whether the signal was manufactured (funders, coordination, throwaway accounts);
    an absence of anything written about a small source is "no track record" (Admiralty F), not a
    negative, and then the work is judged on its own terms (re-run it, check the numbers, check its
    bibliography); **never decide whether a claim is TRUE by searching its own words** (77% of headline
    queries for false news returned unreliable links in the top ten — fresh news, VERIFIED #24); searching
    its exact words to find its ORIGIN is a different move and is allowed. [G8, C11, C12]
12. **Critique gains back a depth lens** (`references/critique.md`): "which load-bearing claim rests on one
    source, a secondary account, or an origin nobody opened?" — the old 5-critic fan-out that won the
    blind depth question included a depth critic. The pre-draft corpus critic is replaced by the deep
    tier's counterpart-and-origin round; cross-locus reconcile by the connection move. [G5, C10]
13. **Kim et al. is stated correctly everywhere it appears** (delegation.md — including the 80.9% and 87%
    figures from the same paper — and SKILL.md), and the "frontier-chained tier is a do-not-fan-out tier"
    rule is replaced by: depth comes from sequential rounds; breadth from parallel readers inside a round.
    The refusal of "mandatory parallelism" becomes a refusal of readers that never exchange AND of free,
    continuous, ungated sharing. `test_the_five_refusals_are_stated_with_reasons` changes its needle from
    "17.2" to "never exchange", with the reason in the test. [G9]
14. **Simple, within the cap**: SKILL.md body ≤ 360 lines (it is at 360 today). The loop, the map, the
    moves and the stop go in; detail moves OUT to `references/rounds.md` (new: map template, reader brief,
    move catalogue, stop mechanics) and to existing references; the four pinned phrases stay. [G6]
15. **The research is kept** in the sweep folder, with the verification log.

## Shapes considered

| shape | why it lost / won |
|---|---|
| **A. Rounds + run map (chosen)** | the only shape that makes multi-round depth the default while keeping one file and no chain |
| B. Restore the 19-stage chain | its step skills did not fire (8 of 9 `Skill()` calls failed); "over-engineered" per the owner; its measured win (the critic fan-out) is kept |
| C. Current skill + an optional "deep mode" reference | keeps the spine optional; the owner's complaint is that the default run is one round |
| D. One reasoner, bigger budgets | loses breadth: 78.5% of one agent's missed key points were uncovered facets of a broad query (VERIFIED #17); independent searchers with different vocabularies are what widen recall (#22) |

**The axis:** where the loop lives (spine vs appendix) and who searches (one reasoner vs lane readers per
round, exchanging through a gated map).

**The trap on A:** the map turns into a second product — a dump of everything read, or a graph kept for
its own sake — and the chair relays findings lossily ("the centre may soften, omit, or reopen
constraints", DeLM). Guards: one line per finding with a span, never source summaries; the chair's job at
the boundary is admission and assignment, not rewriting; raw returns stay on disk for audit.

## What this design does not change

The evidence rules (extended by R11 only), the five kinds of nothing, the checks and their CLI (extended
by `--floor/--patience` only), the breadth and noise references, the lane files, the no-index rule,
silver-only browsing, and the four other refusals.
