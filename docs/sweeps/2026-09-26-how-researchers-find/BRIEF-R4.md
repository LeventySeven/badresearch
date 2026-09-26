# Round 4 brief — research moves of people who did great things, across fields

Read `BRIEF.md` (evidence rules, return format) and `KNOWN.md` (what is already established — do not
re-find it; extend, connect or contradict it and name the K-row) in this folder first.

## What this round is for

The owner: *"align our skill to goated researchers that done great things, truly goated … in various
fields, specifically ai, research engineering and research engineers, dev, swe, design, tech field in
general, but not only this … versatile, and do not overfit only on 1 researcher and pipelines."*

So: for your field cluster, find people with a demonstrable record of great work (what they discovered,
built, shipped, exposed or proved — say it), and extract their **research moves**: how they find the
information that matters, how they filter and verify it, how they connect it, how they hunt the
counter-evidence, how they decide they have enough — and the failure modes (anti-methods) they warn
against. In their own words, from primaries (their essays, books, talks, papers, docs they wrote).

For every move, add one line: **does it transfer to an agent researching with web search, code, APIs
and documents — and in what concrete form?** A move that only works with a lab, a body or a phone call
still counts; say what its nearest agent-reachable form is.

Prefer moves that are specific enough to act on ("read the source of the three most-imported callers
before the docs") over slogans ("be curious"). A move one person states is CONTESTED; say when two or
more people in different fields state the same move independently — that convergence is what this
round is measuring.

## Local CPU rule (the owner's)

Keep local CPU light: `timeout 60 curl` / WebFetch first; the silver browser only for a client-rendered
or walled page, one session at a time, closed right after. Never run test suites, type-checkers,
formatters or builds. No file writes except JSON/text scratch under your scratch dir.
