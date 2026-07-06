# Bad Research — Full-System Audit & Enhancement Roadmap

**Date:** 2026-07-06 · **Method:** 15 parallel evidence-carrying audit agents (13 disjoint
code slices + a Verso/philosophy yardstick + an adversarial competitive cross-cut), each
reading raw source and returning findings with `file:line` + verbatim quotes. Every
load-bearing claim re-verified at the source. Branch: `enhance/audit-remediation`.

**Two guardrails govern every recommendation:** (1) **no overkill** — machinery must earn
the quality it buys; (2) **keyless is sacred** — nothing may add an API-key dependency to
the skill path.

---

## Part 1 — What Bad Research *is* (essence, goals, core rules, core functions)

**Essence.** A keyless deep-research agent that runs *as a Claude Code skill*. The host
Claude model supplies **all** inference; the `bad` CLI is deterministic $0 helpers the skill
shells out to. It searches wide, filters garbage, grounds every claim to a source, and
writes one report into a SQLite-backed markdown **vault** that compounds across sessions.
Fork-and-enhance of hyperresearch.

**Core rules (the invariants that define it).**
- **Keyless.** Host model = inference; no keyed providers on the skill path (enforced by
  `tests/keyless_invariant.py`).
- **Grounded.** Every factual claim binds to a source; a deterministic *uncited-claim
  ship-gate* blocks delivery on any uncited claim, on every route.
- **Patch, never regenerate after synthesis.** Once the report exists, the only edits are
  surgical hunks from tool-locked (`Read+Edit`) patcher/polish agents.
- **Compaction-resistant chain.** Each pipeline step is its own skill file loaded *fresh*
  at the moment it runs, and reads its inputs from disk — a long run can't silently
  collapse when an early step's procedure is evicted from context.

**Core functions (the shape).**
- **Pipeline brain:** an entry orchestrator skill sequences ~19 step-skills
  (`0.5→1→1.5→1.6→2→4→5→6→8→10→11→11.5→12→13→12.5→14→14.5→15→16`) across **3 routes**
  (`fast` bounded-ReAct / `ultrafast` plan→K researchers→synth / `full` deep adversarial).
- **Engine (Python):** `web` (keyless search + content fetch) → `funnel` (source selection)
  → `retrieval` (FTS5/BM25 + optional neural rerank) → `grounding` (citation gate + verifier)
  → `quality` (garbage/injection/recitation filters); plus `core` (vault/db/notes/installer),
  `browse` (fetch-escalation ladder), `embed` (`[local]`), `calibrate` (dev eval bridge).

**The steelman — genuinely best-in-class-*keyless*; defend these, do not cut.**
1. Deterministic, non-bypassable uncited-claim ship-gate.
2. $0 byte-identity quote check that kills fabricated quotes with no LLM call.
3. Patch-never-regenerate with tool-locked agents — *no frontier DR system does this
   mechanically*.
4. Keyless $0 marginal cost + a persistent, auditable, markdown-is-truth vault.
5. Compaction-resistant multi-skill chain (resume from the highest-numbered artifact).
6. Separate-corpus adversarial critics (keep the *mechanism*).

---

## Part 2 — The yardstick

**Verso (reference philosophy):** "the boring core done right"; "we don't force the graph";
every capability **additive — byte-identical when unused**; "not a router/planner cult";
evals are the wedge. → *Machinery you rarely use must not tax the common path, and the
common path must run the good version, not the weak twin.*

**SOTA proportionality (competitive cross-cut).** OpenAI Deep Research = a **single** agent.
Perplexity = **2-stage**, ≤10 steps. Gemini = plan → executor → synthesizer. Anthropic
(the heaviest) = orchestrator + 3–5 research workers + **one** CitationAgent + **one**
bounded grader (≤3), and **no** critic fan-out. **Bad Research runs 2–3× the stages and
4–6× the wall-clock of the heaviest SOTA system, and is the only one running a draft
*ensemble* + a *fan-out* of critics + a grader loop + a fresh-review.** The corpus's own
evidence: the +90.2% multi-agent uplift came from **tokens + task-clarity, not the
architecture**; "scaffolding > model" measures *design*, not *pass count*. More adversarial
passes ≠ more of what actually moved the benchmark. Tellingly, the project's own README
calls the lighter `ultrafast` route "the sweet spot."

---

## Part 3 — The verdict

### The dominant meta-finding
**Bad Research carries ~2 implementations of each subsystem; on the live keyless path the
*weaker* twin runs while the more rigorous one is dead (test-only) — and the docs describe
the dead one.** This is simultaneously the biggest *overkill/bullshit* (dead code + lying
docstrings) and the biggest *underkill* (the good version isn't wired). It is the exact
inverse of Verso's "additive, byte-identical when unused": here it is "duplicated, and the
common path silently uses the weaker copy." Instances (all verified):

| Subsystem | Live (weaker) | Dead-but-rigorous twin | Consequence |
|---|---|---|---|
| Source select | `funnel/` (weak canonical, no pre-fetch garbage reject) | `quality/prefilter` (canonical_url, seo_farm_score, is_blocklisted), `quality/dedup` (MinHash) | SEO farms/AMP twins consume the 80-read budget |
| Web search | ddgs/searxng/websearch only | `web/search/verticals` (7 free scholarly APIs) + `route`/`loop`/`rank` | Academic queries silently fall back to web-scraping; docs still advertise verticals |
| Content | `browse/ladder` | `fetch_clean.py` `llm_clean`/`highlights` (no-ops); `sources.py` 6 extractors (0 callers) | 813-line 2nd stack; docstring claims a monkeypatch that never ships |
| Retrieval | min-max BM25 → host rerank → gate | phantom `hybrid_fuse`/`ALPHA` (alpha=0.7); `reflections.py` (test-only) | Headline docstring "vector+BM25 fuse (alpha=0.7)" is **false** |
| Grounding | whole-body anchors stamped `verified=1` | `build_from_claims` (located-span, drop-hallucinated; 0 runtime callers) | Deterministic gate degrades to "does a cited note *file* exist" — not relevance-binding |
| Interfaces | CLI | MCP server (14 tools, no launcher) + serve HTTP (588 lines, no `bad serve`) | ~1,100 lines dead, already stale, coverage-exempt |
| Eval | in-pipeline grader (self-grade keyless) | `calibrate/` (~1,300 lines) ships to every `pipx` user, undocumented | Package + `bad --help` bloat |

### Correctness / security / reliability (not "overkill" — real defects)
- **[BUG]** `cli/research.py:174` imports non-existent `postfetch_reject_reason`; a bare
  `except` degrades the junk/login/paywall/language filter to **keep every page**.
- **[SECURITY — lethal trifecta]** `quality/injection.py` (`wrap_untrusted`/`INJECTION_PREAMBLE`)
  has **zero live callers**. Tool-armed subagents read raw fetched web bodies via `note show`
  with no injection preamble. (SSRF *is* well-guarded; injection is not.)
- **[RELIABILITY]** `core/db.py` sets WAL but no `PRAGMA busy_timeout`; `BEGIN IMMEDIATE` under
  the pipeline's own 10–12× parallel fetch waves → spurious `database is locked`, no retry.
- **[RELIABILITY]** `migrations.py` v7/v8 do a non-atomic `DROP notes; RENAME` (crash =
  no `notes` table, no backup).

### Overkill (machinery > quality it buys)
Triple-draft ensemble (3 Opus drafts + a merge — no SOTA does this); four stacked adversarial
passes (11.5 + 5 critics + grader-loop + fresh-review — the grader is ~90% redundant on the
keyless default where it becomes the author grading itself); five pre-draft disagreement stages;
`ultrafast` as a third route that's really `fast`'s breadth branch with the caps turned up;
the ~150-line legacy fallback in width-sweep; a 4-level `--effort` "dial" only one field of
which is read; the token-ceiling degrade prose asking an LLM to self-count tokens; the E6
rerank cascade optimizing a single already-batched call; the dense/LanceDB lane that never
fires at ≤80-note corpus size.

### Bullshit (dead code + claims the code doesn't honor)
`shape_fanout`, `ROUTER_AGENTIC_MAX_ATOMIC`, the `max_tokens` param, the phantom `hybrid_fuse`
fuser + its lying docstrings, `linker.py`, `templates.py`, `browse/cache.py`, `aql.py`,
`extract_llm.py`, `HyperresearchBaseline` (always raises), `recall_harness.py` in `src/`;
leaked scaffold (`# NOTE (Workstream A)`, stale `hyperresearch`/`{hpr_path}` CLI names,
"former step N" changelog archaeology, `hyperresearch` branding in the vault index);
grader's 4-vs-5-axes self-contradiction; the plan-gate exit table's dead `light` route.
**The biggest single piece:** the "verifiably better than every major DR product" claim,
asserted with **zero** real competitor runs (empty `research/runs/`, an 8-stub golden set
self-graded to `pass_rate:1.0`, a single-query head-to-head won on a citation-presence proxy).

### Underkill (genuinely behind, quality suffers)
**#1 and the root cause of the overkill:** no distilled-reflections / inter-round memory →
raw sources carried between rounds → quadratic token growth → *that's why* it needs 19 heavy
stages to fit context (Tavily's distilled reflections = −66% tokens). Also: no real eval set
(eval-first is the corpus's #1 meta-lesson); keyless faithfulness can't reach the ship-block
band for the hardest error (0.5 ≥ 0.40 threshold); `bad search` (the most-called command)
uses a substring scorer, not the FTS engine; the source-quality-flag pass lives only on the
dead legacy path.

---

## Part 4 — Enhancement roadmap (tiered by risk × value)

### Tier 0 — correctness / security / reliability
1. ✅ **DONE** — Fix the `postfetch_reject_reason` import → the real post-fetch content filter runs again.
2. ✅ **DONE (defense-in-depth layer)** — untrusted-content policy added to the universal
   subagent **spawn contract** (covers every body-reading subagent + the Codex port) and
   **baked into the fetcher's system prompt** (guaranteed at the #1 lethal-trifecta node);
   both regression-locked. The *authoritative* control is the existing deterministic SSRF
   egress allowlist (`core/fetcher.is_blocked_url`) + the host's Bash-permission gating —
   this adds the model-side warning that was absent. The 3 `INJECTION_PREAMBLE` strings were
   **left as-is on purpose**: they are purpose-fit variants (reranker=scoring,
   fetch_clean=cleaning, injection.py=extraction), not divergent copies — forcing one
   would degrade context-fit. *Deeper structural follow-ups (tracked): bake the warning into
   every body-reading agent constant (not just the fetcher); optionally fence `bad note show`
   body output with `wrap_untrusted` at the CLI layer; minimize per-agent tool grants.*
3. ✅ **DONE** — `PRAGMA busy_timeout=5000` (SQLite now blocks-and-retries the lock; the
   explicit Python-level retry around `execute_sync` remains a cheap follow-up).
4. **TODO** — Wrap the v7/v8 migration rebuilds in a single transaction (low probability,
   high blast radius).

### Tier 1 — dead-code & honesty (implement now; safe; net deletion; tests green)
Cut `shape_fanout`, `ROUTER_AGENTIC_MAX_ATOMIC` (+ its test assertion), the `max_tokens`
param, the phantom `hybrid_fuse`/`ALPHA`/`alpha` fuser (+ fix the two lying retrieval
docstrings), `linker.py`, `templates.py`, `browse/cache.py`, `HyperresearchBaseline`; move
`recall_harness.py` → `tests/`; delete `serve/server.py` (relocate the one live
`render_markdown`); fix leaked scaffold (`# NOTE (Workstream A)`, `hyperresearch`/`{hpr_path}`
CLI names, "former step N" lines, the vault-index branding); fix the grader 4-vs-5-axes
contradiction and the plan-gate `light`/`fast` exit routing. Gate `aql.py`/`extract_llm.py`
behind a real `--schema` entrypoint or cut them.

### Tier 2 — reconcile the parallel implementations (high value; medium risk; staged, tested)
- ✅ **DONE — Funnel → quality/prefilter.** New Stage B.6 `prefetch_garbage_gate` in
  `gather()` rejects blocklisted domains + SEO-farm listicles (primary/docs/reference tiers
  exempt) BEFORE the pool cap, so garbage never spends one of the ≤80 reads; `canonicalize_url`
  now strips utm_*/fbclid/gclid/AMP twins so they dedup to one candidate. This turns the dead
  `is_blocklisted`/`seo_farm_score`/`canonical` logic live. TDD (18 new/extended tests), full
  suite green. ✅ **Follow-up DONE** — the now-redundant dead twins were cut: `quality/dedup.py`,
  `quality/rank.py` (`authority_rank`), `quality/relevance.py` (`score_and_filter`), and the dead
  `prefetch_filter`/`passes_engagement_floor` inside the now-live `prefilter.py`; plus the dead
  588-line `serve/server.py` HTTP server (kept the live `renderer.py`). Net −1,135 lines.
  *(Still deferred as a product decision, not cleanup: the `mcp/server.py` face — a shipped `[mcp]`
  extra.)*
- **Wire the scholarly verticals** into fan-out (the keyless system's actual academic
  differentiator) — or delete them and stop advertising them in `doctor`/`decompose`.
- **Collapse the content stacks** — route `bad fetch` through the browse ladder; amputate
  `fetch_clean`'s dead `llm_clean`/`highlights` tails; wire or cut `sources.py`.
- **Make grounding bind, not count** — wire `build_from_claims` (a `bad bind-anchors` step
  over `claims-*.json`), stop stamping `verified=1` on whole-body seeds, let an unverified
  cite block ship. Fixes the gap between the "bound to a source" promise and the code.
- **Fix the `claims-*.json` seam** — the funnel must emit per-note claims, or the
  contradiction-graph/loci chain must stop depending on an artifact the default path lacks.

### Tier 3 — right-size the pipeline (highest value; changes research behaviour → needs an explicit product call)
These change what Bad Research *is*, so they are recommendations, not unilateral edits:
- **Add distilled-reflections / inter-round memory** (the #1 underkill; unlocks cutting the
  stage count without losing rigor).
- **Gut the grader loop on the keyless default** (it becomes the author grading itself);
  keep only the deterministic step-16 gates as the floor + one guaranteed critic-apply pass.
- **Cut Draft C → 2 drafts** (thesis + steelman) into the reconciling synthesizer; add a
  divergence gate so the ensemble can't silently degrade to expensive triplication.
- **Merge polish (15) into readability-audit (16)** — they duplicate paragraph/run-on surgery.
- **Collapse `ultrafast` into a `fast` effort rung**, or gate it behind a behavioral eval
  proving it beats `fast`-breadth. Two honest routes.
- **Move `calibrate/` behind a `[dev]`/`[eval]` extra** (extract the shared rubric first).
- **Build a real eval set** and run genuine competitor comparisons before making any
  "better than SOTA" claim.

**Net effect if executed:** a leaner, faster, cheaper pipeline whose common path runs the
*rigorous* version of every subsystem, whose grounding actually binds claims to relevant
sources, whose security holds at the untrusted-input boundary, and whose docs describe the
code that runs — with the keyless, grounded, patch-locked, compounding spine fully intact.
