# Sweep: how the best researchers find the top 1% (2026-09-26)

Asked by the owner (DIRECTION.md §5): research, from scratch, how top researchers find information, filter
junk and surface the rare; test the owner's direction against the best practitioners; then make the skill
multi-round, high quality and simple.

**Read first:** `FINDINGS.md`. Then `KNOWN.md` (the pooled ledger), `VERIFIED.md` (what the chair
re-checked in the bytes), `SOURCES.md` (every URL), `raw/` (each reader's full return, agent output).
The design it produced: `docs/specs/2026-09-26-bad-research-rounds.md`.

## How it was run — the method the skill now describes, used on itself

- **Round 1, broad (10 lanes in parallel, disjoint):** X roster of lab researchers and founders; X
  query-first with low-follower accounts on purpose; researchers' own essays; the information-science
  literature; OSINT/journalism/intelligence/investing/patent/systematic-review tradecraft; 44 local
  transcripts; the local essay library and teardowns; YouTube (32 channels + off-roster talks);
  multi-agent research systems (papers and code); the old-vs-new skill inventory.
- **Pool:** the chair merged every return into `KNOWN.md`, re-checked load-bearing spans in the source
  bytes, and ran one completeness critic over the POOLED result (`raw/r1-critic.md`) — it found eight
  absent classes, one wrong row (individuals keep lists, teams keep entity graphs) and three registers
  weaker than labelled.
- **Round 2, deep (7 readers):** each received `KNOWN.md` as "already known — do not re-find" and one lead
  from its frontier: search strategy and patch-leaving; connecting findings (LBD, analogy); popularity vs
  rank; origins, cascades and replications; the data structures parallel workers share (read in source
  code); vocabulary; where agents fail vs humans.
- **Round 3, the critic's absent classes (3 readers):** source grading, integrity checks and data voids;
  scored expertise (superforecasters); stopping with recall guarantees.
- **One fresh reviewer** over the resulting design (gaps and contradictions only); all 23 items resolved in
  the spec's rev 2.

Tool calls per research lane (from the run's task notifications): R1 — 52, 90, 112, 126, 102, 141, 96,
78, 101; R2 — 129, 84, 90, 83, 88, 94, 75; R3 — 72, 92, 77. That range (52–141) is the basis for the
lane-reader budget in the design.

## Head-to-head, 2026-09-26/27 — did the redesign produce better answers?

Each question was answered by the older merged skill (9b46dab) and the rounds skill in isolated copies,
then judged blind by two judges with the answers in opposite order. Each judge wrote down what an expert
answer must cover before reading either answer, and checked at least 15 claims per answer against the
primary source.

| Question | Rounds skill | Verdict (both judges agreed) | What decided it |
|---|---|---|---|
| Transaction-mode pooling failure modes (Postgres, Supavisor) | an early build | **older skill, SLIGHT** | a runnable checklist and the asker's client-library traps; the rounds run went deeper on the pooler only |
| Does creatine improve cognition in healthy adults | 753218c | **rounds skill, SLIGHT** | traced the online claims to their sponsors, the vegetarian brain-creatine result, a recomputed p-value that misses the paper's own threshold |
| Which open-weight LLMs are competitive on agentic coding | 753218c | **rounds skill, CLEAR** | fitted the asker's own stack (harness source read at the pinned version, the issues they track), plus evaluator fallbacks, reward hacking and leakage |
| What makes Linear/Vercel/Stripe feel fast and calm | afabe04 | **rounds skill, CLEAR** | shipped values traced to file and offset and exact wherever checked; the sync and loading mechanics, not only the motion values |

Both arms were accurate on most checked claims; the few wrong ones were side points (a stale issue
premise, a misread timing), and on every question the two answers reached the same bottom line.

**How far this goes.** Four questions, one run per arm, LLM judges. The runs were not equal in cost: the
rounds skill spawned 17–23 subagents per run, and on the design question used 17 against the older
skill's 7 and took 67 minutes against 32. The older arm ran out of web-search quota on two questions
and hit the concurrent-subagent cap on one, which counts against it on the open-weight question. Two
fixes came out of the judging and are in the skill: the answer's top line names the tier and why, never
the effort; and a GitHub issue's state is a dated claim — closed is not fixed, and an open issue's
premise can be stale.
