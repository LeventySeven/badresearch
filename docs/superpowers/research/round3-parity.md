# Round 3 — Parity Verification (2026-05-29)

Verified against live source in `/src/bad_research/skills/` and `/src/bad_research/funnel/`. Not docs.

## Results table

| # | Pattern | Status | Proof (file:line) |
|---|---------|--------|-------------------|
| 1 | **6-axis URL utility scorer** (Authority, Novelty, Stance-diversity, Coverage, Redundancy, Freshness; ≥3 URLs per atomic item before low-utility extras) | **HAVE** | `funnel/rank.py:48–87` — `utility_score()` scores all 6 dims, 0–3 each, max 18. Hard constraint documented at `bad-research-2-width-sweep.md:155` ("every atomic item must have ≥3 candidate URLs before low-utility URLs from well-covered items are included"). |
| 2 | **Evidence-redundancy audit** — >60% `quoted_support` overlap → `derivative-of` tag, discounted from coverage count | **HAVE** | `bad-research-2-width-sweep.md:288–305` — Step 2.6 is "Evidence redundancy audit"; line 296 states ">60% of their `quoted_support` passages are likely derivative"; line 300 tags with `derivative-of`; line 302 writes `redundancy-audit.md`. |
| 3 | **Wikipedia-as-source-hub rule** — fetch refs/citations, never cite Wikipedia | **HAVE** | `bad-research-2-width-sweep.md:136` — "Wikipedia SOURCE HUB rule: … Wikipedia itself is NEVER cited in the final report." Exact instruction, no softening. |
| 4 | **Period-pinned primary-source preflight** — flags missing time-period filings as `priority: critical` before drafting | **HAVE** | `bad-research-8-corpus-critic.md:29–55` — "Pre-flight: period-pinned primary-source coverage check" runs BEFORE the corpus-critic subagent; missing filings are added as `"priority": "critical"` gaps of `"type": "period-pinned-primary"`. Also seeded in Lens D of Step 2.1 at `bad-research-2-width-sweep.md:55–62`. |
| 5 | **Query expansion / multi-phrasing** — 3–5 alternative phrasings per sub-query before retrieval | **PARTIAL** | Programmatic fallback exists in `funnel/fanout.py:37–63` — `_LENS_SUFFIXES` expands one query into up to 6 lens variants. However, no skill instruction explicitly tells the agent to generate 3–5 human-written alternative phrasings *per sub-question* before retrieval. The width-sweep search plan (Step 2.1) generates multiple searches per atomic item across 3 lenses, but that is lens-based, not per-query synonym/paraphrase expansion. `web/search/loop.py:45` reformulates on low recall but only after a failed round. GAP: explicit "generate N alternative phrasings of this sub-question before searching" instruction is absent from the skill prompts. |
| 6 | **Strategic direction-switching** — explicit instruction to state "switching to a different hypothesis/direction" when a search line shows no progress | **GAP** | Grepped all 17 skill .md files and all Python for "switch", "pivot", "no progress", "dead end", "hypothesis", "abandon", "stall". Nothing found. `web/search/loop.py` auto-reformulates on low rerank scores but does so silently — no instruction for the agent to *explicitly announce* the switch. `bad-research-8-corpus-critic.md:14` mentions direction but in the context of overturning a thesis, not search-line switching. |

---

## Genuine gaps worth fixing

### GAP 5 — Query expansion / multi-phrasing (PARTIAL → prompt-only fix)

**Where:** Add to `bad-research-2-width-sweep.md` Step 2.1, inside the "Generate searches from three lenses" block, as a new bullet under step 2:

> **Query reformulation (per atomic item):** For any sub-question where initial lens-A searches return fewer than 3 candidate URLs, generate 2–3 synonym/paraphrase variants before giving up. Example: "China fintech regulation" → "Chinese financial technology oversight", "PRC fintech compliance rules". This costs one extra line in the search plan and prevents single-phrasing recall failures.

No Python changes needed. The funnel's `plan_queries` already has suffix expansion; this closes the explicit-skill-instruction gap.

---

### GAP 6 — Strategic direction-switching (GAP → prompt-only fix)

**Where:** Add to `bad-research-5-depth-investigation.md` (depth investigators) and/or `bad-research-2-width-sweep.md` Step 2.2 legacy / Step 2.5 gap section:

> **Search-line pivot rule:** If 3 consecutive searches on the same sub-question return 0 relevant results, STOP that line and explicitly state: *"Switching direction: [previous approach] is not surfacing sources. Trying [new approach/hypothesis]."* Do not silently iterate on a dead query. The pivot announcement is written to `research/temp/orchestrator-notes.md` so the lead can track what was tried.

Again, prompt-only. No Python needed.

---

## Confirmed HAVE (no action needed)

Patterns 1, 2, 3, 4 are fully implemented. Do not add these to any "gap" backlog — the planning docs that listed them as gaps were stale.
