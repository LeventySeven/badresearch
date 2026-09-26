<!-- AGENT OUTPUT — R1-J old vs new skill inventory. Returned by a subagent, not read by the chair unless a row says so. -->

I read both versions in full. The OLD version is the 21 step-skill files on `origin/main` plus 17 agent prompts, which live in `src/bad_research/core/hooks.py` on origin/main; I checked them against the backup copies. The NEW version is `SKILL.md`, all the references and lane files, the 3 agents, the merge plan and `frontier.py`.

The short version: NEW has no mandatory multi-round retrieval loop and fixes no query or source counts. OLD's search plan, loci, depth investigators, contradiction graph, cross-locus reconcile and pre-draft corpus critic were dropped without any recorded reason or measurement.

**Path key.** `O/<x>` = `origin/main:src/bad_research/skills/bad-research-<x>.md`, and `O/entry` = `bad-research.md`. `O/hooks` = `origin/main:src/bad_research/core/hooks.py`. `O/rc` = `…/skills/routing_constants.py`. `SKILL` = `skills/bad-research/SKILL.md`, `ref/` = `skills/bad-research/references/`, `plan` = `docs/plans/2026-09-10-merge-research-skills.md`.

## 1. Mechanism by mechanism

| # | Mechanism | OLD | NEW | Status | Measured? |
|---|---|---|---|---|---|
| a1 | Decompose and coverage matrix | Maps every verbatim query phrase to an item; cannot proceed while any `Gap?=YES` row remains (O/1-decompose:195-212) | No decomposition step. An "unfilled cell in the shape you promised" is a frontier item; `frontier-observe --promise/--close/--abandon` (SKILL:39, 81-85) | Replaced; no phrase-by-phrase audit | No |
| a2 | Search plan | 4 lenses per item (breadth, citation-chain, adversarial, period-pinned); 3–5 reformulations per sub-question; "typically 40–100 planned searches"; gap check against the matrix (O/2-width-sweep:34-89) | No plan. Queries go one at a time, each naming a frontier item (SKILL:29-32); re-express the query in each lane's vocabulary (ref/absence:33-36) | Dropped, not listed as a refusal | No |
| a3 | Fetch volume | Funnel on full: 40–100 queries, 2–4 providers, read top 60–80 (O/2-width-sweep:190-192). Legacy path: 10–12 fetchers × 8–12 URLs (:255, :294). Effort `medium`: 10–12 fetchers (O/entry:137-142) | No count. Tier: "One wide expansion … Most questions." (SKILL:146). Anthropic's 1 / 2–4 / 10+ agent bands are reported as another system's numbers, not instructed (ref/delegation:72-75) | Dropped | OLD's "reference reports average ~65 sources" has no source (O/2-width-sweep:547) |
| a4 | Source floor | Minimum 45, target 55–80; ≥3 sources per item (O/2-width-sweep:14, 542-547) | None. "Past a floor, more evidence buys confidence rather than accuracy" (SKILL:72-79) | Dropped; argued against | NEW cites an external study |
| a5 | Primary chasing | Fetcher Phase 2 is "MANDATORY": 3–8 leads, ≤8 extra primaries each (O/hooks:3073-3124) | "MUST: chase the primary"; 3–8 primaries per reader (ref/delegation:135-139). But `research-reader` "Reads ONE source" and has no WebSearch (agents/research-reader.md:3-4) | Kept in prose, weakened in the agent | OLD says "The audit shows…" with no number (O/hooks:3076) |
| a6 | Lanes | Funnel providers, academic APIs first, social Lens E (O/2-width-sweep:198-247) | 10 lane files, read when chosen. MUST report which kind of nothing an empty lane returned (SKILL:173-200). No minimum number of lanes | Expanded | External (ref/absence:37-40) |
| b1 | Contradiction graph | Pairs claims into ranked fight clusters; consensus means 3+ independent sources (O/4-loci-analysis:34-81) | Nothing is built. Contradiction MUSTs plus `close-gate` (SKILL:118-137, 289) | Replaced | No |
| b2 | Loci and budgets | 2 parallel analysts, clamped to 6 loci. Each scored on 4 dimensions (max 40). Depth budget totals 40 sources: score 30–40 gets ≤15, 20–29 gets ≤10, 10–19 gets ≤5 (O/4-loci-analysis:87-133) | ABSENT | Dropped. Only the "≥1 dialectical" quota is refused (SKILL:333-335) | No |
| b3 | Depth investigators | Up to 6 in parallel, or 2–4 sequential perspectives each handed the previous one's position, or 1 (O/5-depth-investigation:31-37, 121-125). Budget default 10 per locus, full-text reads, academic APIs first, 900 s, change direction after 3 zero-result searches (O/hooks:343, 356, 536; O/5-depth-investigation:84-90) | No such role. Frontier-chained depth is the reasoner's own sequential loop, a "do-not-fan-out tier" (SKILL:147, 271-272) | Dropped | NEW cites an external 39–70% loss for multi-agent on sequential work (ref/delegation:11-13) |
| b4 | Reconcile and orphan scan | 3–5 cross-locus tensions; read full bodies of the top 8–12 sources; 3–7 tensions total, each with a committed resolution (O/6-cross-locus-reconcile:47, 76, 100-127) | "Name TWO frontier items and ask what connects them" (SKILL:48-58) | Replaced; no scan count | No |
| b5 | Long-source analyst | Sources >5,000 words; at most 6 per query (O/2-width-sweep:551-560) | Read in capped 50-line windows (ref/corpus-scale:44-47) | Dropped | NEW cites wasted reads falling from 1 in 3 to 1 in 5 |
| c1 | Retrieval rounds | Width wave → gap wave for thin/uncovered items → Wave 3 if independent sources < 2 (2–3 fetchers) → depth fetches → corpus-critic wave (2–4 fetchers) → post-critic fetch (≤5 gaps) (O/2-width-sweep:409-474; O/8-corpus-critic:85; O/13-gap-fetch:39-49) | Stop when "nothing new arrived and nothing you promised is still open"; floor ~5 retrievals, patience 2 (SKILL:81-85; `frontier.py`:23-24, 250-254) | Replaced | NEW: functional tests only (commits ce521f9, 47115aa) |
| c2 | Memory between rounds | `reflections.md`: ≤3 bullets per source per round, append-only (O/2-width-sweep:478-531) | Read log with honest empties, plus dispositions (ref/corpus-scale:33-42) | Replaced | OLD cites Tavily's −66% |
| c3 | Fast-route loop | ≤6 steps × ≤4 queries × ≤5 results; done at 3 domains per sub-question; stall stop with patience 1; 600 s (O/fast:36-86; O/rc:10-21) | Keeps the "<2 new domains" threshold, but patience 2, floor 5, plus open cells (`frontier.py`:15, 23-24) | Extended | No |
| d1 | Worker coordination | Shared vault plus claims/loci/tensions files; batches with zero overlap; "No fetcher searches for new URLs" (O/2-width-sweep:255, 377) | Disjoint boundary per reader; the question is given verbatim, the thesis withheld. Readers return frontier candidates. Wave 2 briefs are written from wave 1 (ref/delegation:45-68, 126-133; agents/research-reader.md:35-39) | Replaced | Anecdotal (ref/delegation:50-53) |
| f1 | Adversarial retrieval | Lens C: ≥1 "against X" search per major item; "at least 5 adversarial searches total" (O/2-width-sweep:48-53, 89) | "MUST search AGAINST your emerging position … and an independent rerun" (SKILL:63-67). No count | Kept; count removed | The plan calls it the win's "ancestor" (plan:94-97); never tested separately |
| f2 | Pre-draft corpus critic | "What source would overturn this?" Re-reads 2–3 source bodies per position; 3–8 gaps; mandatory 2–4 fetchers (O/8-corpus-critic:28-106; O/hooks:3183-3238) | Implied-record frontier item; name ≥2 rivals and delete evidence that cannot separate them (SKILL:43-46, 93-111) | Replaced; no separate pass or budget | No |
| f3 | Steelman draft | Draft B written from a curated 20–50-note minority-view list (O/10-triple-draft:187-225) | Refused (SKILL:344-346); dialectic lens instead (ref/critique:53) | Dropped | Refusal cites a vendor's own number |
| g1 | Coverage checks | Steps 2.5 coverage and 2.6 redundancy; width and instruction critics | Open cells; instruction and width lenses (ref/critique:51, 54); breadth capture–recapture (ref/breadth:40-64) | Replaced | No |
| h1 | Critics | 5 in parallel, including a depth critic; ≤12/≤12/≤10 findings; assumption critic takes the top 5 claims (O/12-critics:82-89; O/hooks:659, 768, 884, 1291) | 4 lenses with no depth lens; ~10 findings each; every critic writes its own answer before reading the draft (ref/critique:44-54; agents/research-critic.md:19-30, 89) | Kept, minus the depth critic | OLD won 1 blind question on this (plan:33-37) |
| h2 | Post-critic fetch | 0–1 relevant notes in hand → fetch; ≤5 gaps, 2–3 queries each (O/13-gap-fetch:33-49) | Same 2+/0–1 rule; "Cap the re-retrieval" with no number (ref/critique:65-73) | Kept; cap now unnumbered | Same as h1 |
| h3 | Revision loop | Grader ≤3 rounds; pass = every axis ≥0.70 and mean ≥0.75; escalate an axis that repeats (O/12.5-grader:73-200). One fresh review. Synthesizer with a conflict spot-check (O/11-synthesize:45-61) | "Stop at three rounds… the bar does not rise" (ref/critique:107-122); synthesizer refused | Replaced | Grader explicitly deferred (plan:27-28) |
| i1 | Stopping | Fixed sequence: "never skip or add a step" (O/entry:425); "proceed anyway" after two waves (O/2-width-sweep:604); 3 h clock with 30 min reserved (O/entry:162-172) | "If you cannot name a frontier item, you are done" (SKILL:32); "name what this round has that the last one did not… cut it" (ref/checks:114-115) | Replaced | External replications only |

## 2. Is anything in NEW a mandatory multi-round loop?

No. SKILL:19-20 says: *"Everything below is what a good answer looks like, not a sequence to execute. What you may not skip are the refusals — marked MUST."*

**MUST items that cause retrieval:**
- *"every query after the first names a frontier item… If you cannot name a frontier item, you are done: say so and write."* (SKILL:29-32). This gates later queries and allows stopping after the first one.
- *"MUST search AGAINST your emerging position while you are still retrieving"* (SKILL:63). This forces at least one more query once a position exists; how many is not stated.
- *"MUST: chase the primary"* (ref/delegation:135). This applies only to delegated readers.

**Permitted but not MUST:**
- The ~5 floor and patience 2 (SKILL:81-85).
- The tier choice, which names "One wide expansion" as the answer for "Most questions" (SKILL:146).
- The waves under the chain veto (ref/delegation:66-68).
- The fetch after a critique finds a gap (ref/critique:67-71).

The floor is enforced in code only if the agent calls `bad frontier-observe` (`frontier.py`:250: `if self.steps < MIN_RETRIEVALS: return False`). The command block introduces it with "Run the deterministic ones on everything" (SKILL:280), which is not marked MUST.

**Typical run.** The NEW text does not set queries per round, source counts or round counts. Its stated numbers are:
- ~5 retrievals, binding only through the CLI
- patience 2
- ≤3 critique rounds
- ~10 findings per critic
- ≥2 rivals
- 3–8 primaries per reader

OLD full route, all under "never skip or add a step":
- 40–100 planned queries and 45–80 sources
- 2–3 width waves
- 1–6 loci sharing a 40-source depth budget
- a mandatory corpus-critic wave of 2–4 fetchers
- ≤5 post-critic gaps
- ≤3 grader rounds

OLD fast route: ≤6 steps × ≤4 queries.

## 3. Parallelism

**OLD forces it:**
- *"Within a step, parallelism is mandatory when there are multiple subagents"* (O/entry:422)
- *"Spawn 10–12 fetcher subagents in ONE message"* (O/2-width-sweep:294)
- 2 loci analysts (O/4-loci-analysis:87), 2 draft writers (O/10-triple-draft:245), 5 critics (O/12-critics:82)
- Depth investigators run in parallel for breadth-first queries, but *"Do NOT spawn them in parallel"* for depth-first ones (O/5-depth-investigation:33-34)

**NEW permits it and in one case forbids it:**
- *"Fan out reading, never judgment — and only when results combine by union… the frontier-chained tier is a do-not-fan-out tier"* (SKILL:268-272)
- *"Never as a MUST"* (SKILL:343)
- Readers: "Spawn several in parallel over disjoint sources" (agents/research-reader.md:3). Critics: "one per lens" (agents/research-critic.md:3). Adjudicator: "Spawn exactly one."
- The noise filters run "in that order, not in parallel" (ref/noise:25).

**What workers share.** OLD workers share a vault. NEW workers share nothing with each other; knowledge passes only through the reasoner writing the next wave's briefs.

## 4. What NEW has that OLD lacked

| Mechanism | NEW | Measured? |
|---|---|---|
| Frontier gate (a query must name something learned) | SKILL:29-32; `bad frontier-gate` | Blind test against a no-skill agent, n=2 (commit 1b22f2e) |
| Query connecting two findings; implied-record query | SKILL:43-58 | No |
| Stop computed in code, including cells still owed | `frontier.py`:237-254 | Tests only |
| Choosing how much retrieval a question needs | SKILL:139-156 | No |
| Rivals plus deleting non-diagnostic evidence | SKILL:87-116 | External source (Heuer) |
| An open disagreement blocks the close | SKILL:289; ref/checks:13 | No |
| Five kinds of empty result, plus unsampled regions | SKILL:186-200; ref/absence:62-67 | One measured loss (ref/absence:97-109) |
| Breadth: capture–recapture, singleton share, ≥half non-popularity entry points, link-walking | ref/breadth:40-91 | No outcome measurement |
| Noise filter cascade and a screening stop with a recall guarantee | ref/noise:13-98 | Top-20 → 100% recall on 5 known items |
| Chain veto; readers return frontier candidates | ref/delegation:64-68; agents/research-reader.md:35-39 | No |
| Adjudicator (ranks claims, never passes/fails) | agents/research-adjudicator.md | No |
| Quote-drift, figure-support, no-source-claim and absence gates | SKILL:290-293 | Deliberately planted defects |
| Iteration gate: each round must add information | ref/checks:114-115 | External |

## 5. The five refusals — did each also remove a depth/breadth mechanism?

1. **Disagreement quota.** Refusing only the "≥1 dialectical locus" quota does not account for the fact that the whole loci and depth-investigator machinery (b2, b3) is gone, and it has no replacement with a budget.
2. **Reader forced to commit to a position.** The depth investigator went with it. Its budgeted per-locus fetching (default 10, up to 15, 40 in total) has no replacement. The one-source `research-reader` fills a different role.
3. **Mandatory parallelism.** The 10–12-fetcher wave and the 40–100-query plan went with it. There are no replacement counts.
4. **Draft ensemble and synthesizer.** The steelman Draft B and the synthesizer's conflict spot-check went. The dialectic lens and the rivals rule partly replace them.
5. **Word floors.** This is not a retrieval mechanism, so nothing on the depth/breadth side was lost.

## 6. Git evidence

`git log origin/main..feat/research-rebuild-slice-1 -- skills src/bad_research/skills agents` lists 28 commits. The ones that matter here:

- **77fe24d (the merge).** It records: *"Twelve readers over the old system's 21 step skills returned 17 MERGE / 3 DROP / 0 KEEP"*. The per-step verdicts are not in the repo. It also records the reasons for the five refusals.
- **The plan's "Deferred" list** (plan:26-29) names the grader loop, the 2-draft ensemble and synthesizer, the plan-gate and token ceilings. It does **not** name the width sweep, search lenses, loci, depth investigators, contradiction graph, reconcile/orphan scan, corpus critic or depth critic. I found no stated reason and no measurement for any of those cuts in the plan or the commits.
- **9353c24** deleted 17 test files for the old chain "because the capability they grade is deliberately gone".

**What measurements were cited:**
- **Head-to-head (plan:33-37).** It was blind, 2 questions, and split 1-1. The OLD system's depth-question win is credited to its "5-critic fan-out". The retrieval-side depth mechanisms were never tested separately.
- **Detail outside the repo.** The per-axis breakdown lives only in `~/.claude/projects/-Users-seventyleven-Desktop/memory/badresearch-research-rebuild.md`. It adds that OLD also "found an independent replication the rebuild never surfaced". Nothing records which OLD mechanism produced it.
- **17.2× error amplification.** An external study.
- **Proportion loss** behind the word-floor refusal. It comes from NEW's own test against a no-skill agent (1b22f2e, n=2), not from a comparison with OLD.
- **Ensemble refusal.** It cites a vendor's own benchmark (DRACO), which shows the old mechanism was never measured; it is not a measurement of cutting it.

No commit after the merge records a re-run against OLD.

An uncommitted working-tree section of `DIRECTION.md` (lines 91-128) records the owner's view that the merged skill *"isn't enough for genuinely multi-step, multi-round research"*.