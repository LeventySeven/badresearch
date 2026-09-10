# Merge `bad-research` and `research` into one skill

**Goal.** One skill, named `bad-research`, that carries the old system's measured advantage
(an adversarial pass over a finished draft, and adversarial coverage on the retrieval side)
on the new system's architecture (compact spine, on-demand references, checks that execute).

**Done =** `.venv/bin/python -m pytest -q` green, `bash skills/bad-research/scripts/lane-probes.sh`
runs, `bad absence-gate --help` resolves, and a cold reader can follow SKILL.md to a critique
pass without reading any other file first.

**Approach.** The new skill's `skills/research/` is the base; it is renamed, not rewritten.
Three additions and five explicit refusals. Nothing is carried as a numbered step.

## Global constraints

- **No step numbering, no route table, no "invariants" list.** A renumbered invariants section
  is how the two refuted invariants come back. Refusals are stated as prose, by name.
- **Wire the check, do not describe it.** Where a capability already ships as a tested CLI
  command, the skill names the command. Prose is worth ~7%; a non-zero exit is worth what it says.
- **No SQLite vault, no tag minting, no capability probe, no archive-run** in the skill path.
- **Browser access is `silver` only, with the user's own cookies.** Never Playwright MCP.
- **Do not shave to hit a line count.** `DIRECTION.md`: *"simpler is a means, never the goal.
  Do not trade capability for line count."* Where the two pull against each other, capability wins
  and the cap moves, with the reason written into the test.

**Deferred:** a `filings` lane file (the rule goes in `evidence.md`; a lane file waits until
someone has driven it); a second-model critique (keyless stand-in only); re-implementing the
grader loop; the 2-draft ensemble and the synthesizer; the readability recommender; the
plan-gate; per-run token ceilings and degrade ladders.

## Research fold-in (what decided each task)

A blind head-to-head over two questions split 1-1. The old system won the depth question on
adversarial self-correction: its 5-critic fan-out caught the over-claim *"No source measures the
false-negative rate of a source-quality filter directly"* that the new skill shipped and a judge
falsified in one fetch. The new system won the breadth question on fabrication rate (0 wrong
attributions vs 2) and on a completeness claim a judge re-derived end to end, at 8.5x the speed.

A pooled critique over 12 readers of the old skill found three things no reader could:
1. Every reader labelled the externalized run store "ceremony" while carrying a dozen
   instructions that operate on it. The condition is real and the new skill already concedes it
   (*"earning its keep only once evidence sits outside the window"*) then says nothing about it.
2. 1,431 of the old system's lines were post-draft revision; the pool reduced it to ~40 lines of
   advice with no owner, no order and no stop. That phase is where the head-to-head win lived.
3. Four already-tested commands were about to be rewritten as prose: `absence-gate`,
   `verify-citations`, `grounding-surface`, `grounding-recall`.

## User Review Required

Task 7 moves installed artifacts out of `~/.claude/` — the old entry skill, 21 project step
skills, and 17 `bad-research-*` agents. **They are MOVED to a timestamped backup directory,
never deleted**, so the action is reversible. No file outside `~/.claude/skills/`,
`~/.claude/agents/` and this repo is touched.

---

### Task 1: Rename the skill, keep history

- [ ] `git mv skills/research skills/bad-research`
- [ ] Update `SKILL` path in `tests/test_skills/test_research_skill_shape.py`
- [ ] Update the frontmatter `name:` to `bad-research`
- [ ] Grep the repo for `skills/research` and fix every hit
- [ ] Run `pytest tests/test_skills -q` → expect PASS

### Task 2: `references/critique.md` — the post-draft phase (NEW)

The phase that earned the win, with the owner, the order and the stop the pool omitted.

- [ ] Write the file. It must carry:
      - **Fresh context, not one prompt.** `checks.md` already measures the alternative:
        putting the draft, the questions and their answers in one prompt is *"the fastest and
        the worst, because the incorrect draft primes the model to repeat it."* The 12-critics
        reader proposed exactly that arrangement; it is refused here by name.
      - **The pre-read prior generation.** Before opening the draft, the reviewer writes its
        own 3-sentence answer from memory; every divergence becomes a high-priority target.
        Keyless stand-in for a second model — it removes the priming rather than separating the
        call. Carry its stated limit: it is a targeting signal on head entities, worthless on
        rare/recent/version-specific facts, and never a correction.
      - **Lenses, chosen not to duplicate.** Instruction (did the draft answer every atomic item
        the prompt named — the only recall instrument over the prompt, and `checks.md` admits
        recall is what nothing else here measures); assumption (top-5 causal/quantitative claims
        decomposed into sub-assumptions, each verified independently); dialectic; width.
      - **Findings go back to the author, who patches surgically.** The critic never edits.
        Named failure mode: *"a critic proposed regeneration in patch clothing."*
      - **A gap gets a fetch, not a hedge.** 2+ relevant sources in hand → the author can handle
        it; 0-1 → re-retrieve. This is the mechanism that turns a critique into a correction, and
        it is the exact shape of the loss: a judge falsified the claim in ONE fetch.
      - **A gap that stays unfilled is flagged, not written around.**
      - **Stop at 3 rounds.** Still failing is a signal about the draft's structure, not a reason
        for round 4. The bar does not rise between rounds.
- [ ] Add a pointer to it from SKILL.md
- [ ] `grep -c "" skills/bad-research/references/critique.md` → expect ≤ 120

### Task 3: Adversarial coverage on the RETRIEVAL side

The ancestor of the win, and the cheaper half: contrarian queries put counter-evidence into the
corpus before a draft exists, where a correction costs nothing.

- [ ] In SKILL.md's frontier section, add the adversarial-search floor: for each load-bearing
      position, search *against* it — "criticism of X", "limitations of X", "why X doesn't work".
- [ ] Add the mirror conclusion the new skill has no form of: **a failed adversarial search is a
      reportable finding that RAISES confidence.** State it in those terms.
- [ ] Add the replication hunt as a named frontier move: go look for an *independent rerun* of a
      load-bearing result. This is the capability the head-to-head credits the old system with.
- [ ] Add to `references/absence.md`: a chart or text-layerless PDF is a sixth kind of nothing —
      transcribe the plotted numbers off the saved image; never eyeball a number you did not read.

### Task 4: Wire the four orphaned executing checks

- [ ] Add to SKILL.md's command block: `bad absence-gate --report r.md`
- [ ] Add to `references/checks.md`: `bad verify-citations` (the only pass asserting a span
      SUPPORTS its sentence rather than that it exists), `bad grounding-surface` (per-claim
      ledger), `bad grounding-recall` (the mutation harness — `checks.md` currently says
      *"Break it on purpose and watch it go red"* while the harness that does that is unreferenced)
- [ ] Carry the MUST/SHOULD/EXEMPT triage: MUST verify load-bearing facts and anything that moves
      since cutoff (numbers, dates, prices, versions, "current/latest"); EXEMPT common knowledge
      and pure synthesis.
- [ ] Carry the hedge ladder as prose-with-a-source: one source → "one source reports…"; low
      verify score → "preliminary…". Keep the raw score off the page.
- [ ] Verify each named command resolves: `test_every_named_command_resolves` already asserts this

### Task 5: `references/corpus-scale.md` — the condition the skill concedes and abandons (NEW)

- [ ] Write it. The rule stands (no embeddings, no findings cache, no summary of summaries — a
      production findings-cache measured 0 hits in 133 attempts), and this file says what to do
      once evidence sits outside the window, which is the condition the rule itself names:
      dispositions over a target you re-scan, a read-log, capped reads. Not an index.
- [ ] State the boundary: what makes a store legitimate here is that it is re-derivable and
      addressable, never that it is searchable.

### Task 6: Fold the earned merges; refuse the refuted ones

- [ ] `evidence.md`: period-pinned primary filings — a transcript narrates rounded numbers where
      the filing has line items, and *"a Q1 2025 10-Q does NOT satisfy 'Q3 2024'"*.
- [ ] `evidence.md`: the source-quality flags, ONCE (six readers proposed this into four files
      under three mechanisms): aggregator, false authority, nameless source, vague qualifier,
      unconfirmed, marketing spin, speculation-as-finding, cherry-picked. Flag, don't suppress.
      A flagged source may not be cited bare as established fact.
- [ ] `references/lanes/community.md` (NEW, ≤45 lines): for reception/adoption/lived-experience
      questions the thread is primary and the article about it is derivative. Add the lane row.
- [ ] `delegation.md`: promote to MUST — every delegated reader gets the question VERBATIM; and
      chase 3-8 primary sources through citation chains (Wikipedia as source hub, never cited).
- [ ] Add a short **"What this skill refuses"** section to SKILL.md naming the five refuted
      invariants as refusals, with their reasons — a quota on disagreements (against "do not
      manufacture them"), a delegated reader that must commit to a position (against
      `research-reader.md`'s measured "never concludes"), mandatory parallelism (against 17.2x
      error amplification), a mandatory draft ensemble (fanning out judgment as a MUST), and
      word floors (against the blind-judged proportion result).

### Task 7: Install one skill; back up the old system

- [ ] `mkdir -p ~/.claude/_backup-bad-research-<UTC>` and MOVE into it:
      `~/.claude/skills/bad-research`, `~/.claude/skills/research`,
      `~/.claude/agents/bad-research-*.md` (17 files), `.claude/skills/bad-research-*` (21 dirs)
- [ ] Install the merged skill to `~/.claude/skills/bad-research/`
- [ ] Confirm the listing shows exactly one research skill: `ls ~/.claude/skills | grep research`
- [ ] Confirm agents: `ls ~/.claude/agents | grep -c research` → expect 3

### Task 8: Verify by cold use, not by audit

- [ ] Dispatch ONE fresh-context reader that has never seen this session: give it the merged skill
      and a question, and have it report where the skill was unfollowable — not whether it is good.
      Cold use finds what an audit cannot; ten audit rounds missed what one cold run found.
- [ ] Fix what it names; do not fix what it merely disliked.

---

## Verification Plan

**Automated** — each command with the result that counts as pass:

```bash
.venv/bin/python -m pytest -q --no-cov -p no:warnings          # no F in the output
.venv/bin/python -m pytest tests/test_skills -q --no-cov       # shape guards green
.venv/bin/python -m bad_research absence-gate --help           # exit 0
.venv/bin/python -m bad_research verify-citations --help       # exit 0
.venv/bin/python -m bad_research grounding-surface --help      # exit 0
.venv/bin/python -m bad_research grounding-recall --help       # exit 0
bash skills/bad-research/scripts/lane-probes.sh                # exit 0, prints per-lane state
grep -rn "step [0-9]\|Skill(skill:" skills/bad-research/       # expect ZERO hits — no chain
ls ~/.claude/skills | grep -c "^research$\|^bad-research$"     # expect 1
```

Tests may not be weakened to pass: no assertion relaxed, no expected value edited to match
output. A failing test indicts the change, not the test — the one exception is a test whose
own fixture is provably wrong, which is fixed with the reason written into it.

**Manual** — what no command asserts:
- Read SKILL.md end to end as someone who has never seen it. Does the critique phase have an
  owner, an order and a stop, without opening another file?
- Confirm the five refusals are stated as refusals with reasons, not as a numbered list.
