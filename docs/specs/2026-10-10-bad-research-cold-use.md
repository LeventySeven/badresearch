# bad-research — cold-use round (2026-10-10)

The owner's ask (DIRECTION.md §5, restated 2026-10-10): research should work like a growing web —
the more the run knows, the better it finds and the better it filters; old branches can be dropped.
The rounds skill (c1fa0de) already researched in rounds through a map. This round did two things the
2026-09-26 work did not: **used the skill cold on real questions against a plain session**, and
**researched the four parts of the owner's intuition the earlier sweep never tested** (expertise growing
during a search, pruning, how AI research engineers work, what research agents have measured since June).

Evidence: `docs/sweeps/2026-10-10-expertise-pruning/` (FINDINGS.md, VERIFIED.md — 19 spans re-checked
by the chair, raw/) and the dev-set results below. Answers and judge verdicts are in the gitignored
`research/cold-use-2026-10-10/` (they quote private notes; the repo is public).

## The dev set — what cold use showed

Five AI-research questions, fixed before any run. Each was answered by the rounds skill (c1fa0de, in an
isolated copy) and by a plain Claude session with a demanding prompt and no skill; two blind judges per
question, opposite answer order, each writing the expert-coverage list before reading and checking ≥15
claims per answer against the primary.

| Q | skill | plain | verdicts (2 judges) |
|---|---|---|---|
| D1 is an eval difference real or noise | 27 min, 10 subagents | 5 min, 0 | skill SLIGHT, skill SLIGHT |
| D4 did "LLM ideas more novel" hold up | 42 min, 13 | 6.5 min, 0 | skill SLIGHT, skill SLIGHT |
| D5 who does credible long-horizon agent evals | 51 min, 12 | 10 min, 1 | skill CLEAR, skill CLEAR |
| D2 do instruction files / skills help | 70 min, 15 | 8.5 min, 0 | skill CLEAR, skill CLEAR |
| D3 agentic search vs RAG (not controlled: the skill arm also got 33 AI Engineer transcripts on the owner's steer) | 72 min, 24 | 16 min, 1 | skill CLEAR, skill CLEAR |

**10 of 10 verdicts for the skill (4 SLIGHT, 6 CLEAR)** — on coverage, depth, origin-tracing and
confounds caught at source; it costs 5–8× the wall time. Judges are the same model family as the
authors and the questions were chosen by the author; a direction, not a proof. Every judged loss point was one of a few recurring defects — those are what this round fixes.

## Changes, each with what it rests on

| # | change | where | rests on |
|---|---|---|---|
| 1 | **Read what you cite** — results, tables, limitations, conclusions of every source the answer leans on; record read depth; "the paper did not compare X" is an absence claim checked in its tables | SKILL.md evidence; reader agent; rounds map | the commonest judged miss, 6 instances across D1/D2/D4/D5 (a Table 1 human row; a recommendations section; §5 of a cited post; a paper's own Finding 4 cited for its opposite) |
| 2 | **Rivals before the first search**; a rival is dropped only by a finding that bears on it | SKILL.md frame + rivals; rounds map | RCT, 297 GPs: early alternatives OR 1.31, late OR 1.10 n.s. ✔; agents dropped their most ambitious hypotheses within 15 h and never returned ✔; fixating and vagabonding residents 0 of 28 resolved ✔ |
| 3 | **Late evidence gets its own challenge** (last round, critique gap-fetches) | SKILL.md stop; critique.md | planted false doc adopted 40.5% at start vs 85.5% before synthesis; verification prompting reduced, did not remove ✔ |
| 4 | **A debunk becomes a check**; **a refuted finding repairs what rests on it**; map append-only (superseded, never deleted) | SKILL.md pool; rounds map | Jordan: a paper's mistake changes nothing, a shared baseline's is found next record ✔; repair-on-contradiction beat flat replacement (ReTree, mechanism ✔); Karpathy deletes a note "only rarely" ✔; overwrite memories delete corrective feedback (agent-read) |
| 5 | **Keep pages; re-read them with later knowledge**; a new open question greps `pages/` first | rounds stores + brief; reader agent | fetch-time reading fixes the reading "before the agent knows which fact it will need" ✔; kept-pages agents led on BrowseComp at every backbone, tied on WideSearch (agent-read) |
| 6 | **Show the derivation; no false precision; attribute facts from the asker's notes; length tracks belief** | SKILL.md answer | judged in D1 (both judges), D4 (both), D2 critic, D5 |
| 7 | Deep-round moves: **browse the publisher of a load-bearing primary**; **open a pre-registration**; **counterpart through the same entry points**; **attack the settled premise**; domains.md: tuned baselines and train/test split | rounds move table; domains.md | D5 misses sat in posts beside the one cited (both judges); D4 headline test absent from its registration; D4 missed the one blinded study on the other side; experts' misses sit where they stopped looking (talks, agent-read); optimizer speedups 1.4–2× → 1.1× at 1.2B ✔; Arize "+15%" on the training set (raw/devrun-d2-arize-origin.md, agent-read) |
| 8 | Video lane: **all titles for the field's core channel**; serial fetch; **ai.engineer talk pages when YouTube walls captions** | lanes/practitioner-video.md | owner steer; measured (raw/devrun-aie-transcript-lane.md): 1,268 titles, 35 relevant, 22 outside a 400 window; −P4 walled 15/35, serial retries recovered 1; PO-token wall beat every client; site pages recovered 12/14 |
| 9 | Installed-skill drift reported by `bad doctor`; web-live probe matches silver's fenced output | src/…/doctor.py; scripts/lane-probes.sh | the owner's ~/.claude ran the Sep 10 skill for two weeks after the rebuild (11 files differed) |

Dropped with a measurement: a URL-liveness gate — 169 cited URLs across eight answers, 0 fabricated
(the 4 non-2xx were bot walls on real pages).

## How it is judged

A held-out set (T1–T8 in the private questions file, fixed before any change): the old skill (c1fa0de)
against this one (0c1d963), isolated copies, two blind judges per question in opposite order, one pair
running at a time so neither arm loses subagent slots. Eight questions can show only a large effect: a
two-sided sign test at p < .05 needs 8 of 8 (7 of 8 gives p = .07), and the two judges of one question
are not independent.

## Held-out results so far (paused after T3, 2026-10-10)

The owner paused the set after three questions. T4–T8 have not run.

| Q | old | new | verdicts (2 judges) |
|---|---|---|---|
| T1 RLVR: sharpening vs new abilities | 116 min, 24 subagents | not recorded, 21 | new SLIGHT, new SLIGHT |
| T2 why multi-agent systems fail | 47 min, 20 | 59 min, 22 | new SLIGHT, new SLIGHT |
| T3 retainers vs fixed price for a studio | 53 min, 17 | not comparable (8 h gap in wall clock), 14 | new SLIGHT, old SLIGHT |

**5 of 6 verdicts for the new skill, all SLIGHT.** By question that is 2 wins and 1 split — a
direction, not a result; it says nothing yet at p < .05. Where the judges separated the two:

- **Fixed by this round, and seen to work.** The old answers printed rival probabilities from pooled
  model judgments (T2: both judges called it pseudo-quantification); the new ones did not. The old T1
  answer added a "within chance" argument during its final patch that both judges found overstated —
  the late-evidence failure change 3 targets. The new answers caught more confounds at source (a base
  model already at ~99% pass@128, an 8-shot vs 0-shot prompt split, a dataset's label-join rebuild).
- **Still missed by the new skill, fixed after the arms were built (not covered by these results):**
  - a limitation sentence from a paper whose method beat RL, cited as "sampling loses to RL" (T1,
    both judges) → cite a source for the direction its own results take (8bf896d);
  - arXiv v3 cited when the journal version had changed which effect held (T2, both judges) →
    check a load-bearing preprint's latest and published versions (a90d687, de6e8fa);
  - a real quote pooled under a batch file, then linked to the author's other post (T3) → each span
    keeps its own URL (889bdf8);
  - the absence gate passed "no one has settled it" and "nobody has re-run" with 0 claims (found by a
    T1 critic) → wider record verbs, "I found no" counts as scope (98dc8ad).
- **Coverage still varies run to run.** Each side found a decisive source the other missed (T3: open
  books vs the SPI margin benchmark; T1: Guru vs the coverage-preserving objectives). Two runs of one
  skill would likely differ as much.

**Harness finding for whoever resumes.** A background subagent's own background subagents report to
the top-level session, not to it: three arms sat "waiting for readers" that had already returned. Arm
prompts from T3 on say to spawn subagents in the foreground; T1 and T2 arms were resumed by hand with
the returns saved into their work folders.

**To resume:** run T4–T8 one pair at a time from the same two commits (rebuild arms with
`git archive <sha> skills/bad-research agents | tar -x -C <arm>`), judge as above, then add the rows.
