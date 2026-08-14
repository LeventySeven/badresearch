"""Frozen routing + bound constants for the Bad Research pipeline.

Every value cites INTERFACES.md / dossier 05 (DR-loops). DO NOT re-derive."""
from __future__ import annotations

# ---- Fast-route loop constants (keyless deep-research replica) ----
# Evidence-anchored: see researchfms/teardowns/DEEP_RESEARCH_FAST_MODE_RE.md PART 2.2, each
# value cited to a cloned DR repo (open_deep_research / gpt-researcher / dzhng / smolagents /
# local-deep-research). The 8-10 min budget sits at the LOW end of the open-clone range.
FAST_MAX_STEPS            = 6      # hard step cap (open_deep_research supervisor=6; Perplexity caps 10)
FAST_MAX_QUERIES_PER_STEP = 4      # parallel queries fanned out per step (dzhng breadth=4)
FAST_MAX_RESULTS_PER_QUERY = 5     # SERP results per query (dzhng + gpt-researcher agree)
FAST_MIN_NEW_DOMAINS      = 2      # < this many NEW distinct domains in a step => diminishing returns
FAST_STALL_PATIENCE       = 1      # consecutive low-novelty steps tolerated before stopping
FAST_MIN_SOURCES_PER_SUBQ = 3      # distinct domains to mark a sub-question "green" (coverage gate)
FAST_MAX_SUBQUESTIONS     = 3      # sub-questions the decomposer emits in fast mode
FAST_CONTENT_TRIM_CHARS   = 25000  # per-page content cap before it enters context
FAST_TEMPERATURE          = 0.4    # planner/extractor temperature
FAST_RESERVE_SYNTH_FRAC   = 0.25   # fraction of budget reserved for the writer (distinct from
                                   # the token-valued RESERVE_FOR_SYNTHESIS below — do NOT merge)
FAST_TIMEOUT_S            = 600    # wall-clock safety net (belt-and-suspenders on the step cap)

# Breadth-shape parallel sub-researcher fan-out cap for the fast loop. The fast
# route owns the breadth branch (K parallel researchers in breadth mode), so this
# is the single middle-tier fan-out lever — the former `ultrafast` route (fast's
# breadth branch with the caps turned up) was folded away 2026-07-06.
FAST_SUBRESEARCHER_K = 3

# Parallel subagent fan-out (Claude depth-1) — INTERFACES / CLR §CE.5,§CE.10
SUBAGENT_FANOUT_DEFAULT = 3
SUBAGENT_FANOUT_MAX = 20

# The loci / depth-investigator fan-out cap — the SINGLE SOURCE OF TRUTH for
# "how many parallel depth investigators can one full-route pass run". Steps 4
# and 5 enforce it (bad-research-4-loci-analysis.md, bad-research-5-depth-
# investigation.md) and EFFORT_MAP's top rung pins it as `loci_max`.
#
# It is deliberately NOT SUBAGENT_FANOUT_MAX (20). 20 is the generic Claude
# subagent ceiling — what the host will spawn at all. 6 is what a depth pass can
# usefully investigate: each locus costs a full source budget and an
# INVESTIGATOR_TIMEOUT_S window, and the ~80-read synthesis ceiling
# (READ_TOP_K_CEILING / SPEC §"the ~80-read ceiling is load-bearing") binds long
# before 20 loci do. Anything past the cap is DEFERRED to the gap waves, and the
# router now says so out loud (router.fanout_coverage / shape_reason) instead of
# truncating in silence — issue #36 item 5.
LOCI_MAX = 6

# Clarifier (OpenAI default-proceed) — DR-loops §1 / ODR §5
CLARIFY_MAX_QUESTIONS = 3

# Funnel + retrieval — INTERFACES
READ_TOP_K_CEILING = 80
RELEVANCE_GATE = 0.70

# Router heuristic boundaries — DR-loops §9.2 (the verbatim decision tree)
ROUTER_LIGHT_MAX_ATOMIC = 6


# ── B-5 modality factor (2026-05-27 post-benchmark) ──────────────────────────
# Benchmark bug: q1 ("best tech stack") up-routed to `full` purely because the
# decomposition carried 17 atomic items, then ran the contradiction-graph / loci
# / depth machinery on what is a SURVEY — ~2x the cost on a broad-but-shallow
# curation query. The fix: factor query MODALITY + CONTESTEDNESS alongside the
# atomic-item count so breadth ALONE no longer forces `full`. The genuine
# full-tier triggers (time_periods, argumentative format, contradiction terms,
# multi-domain) are untouched and still escalate regardless of modality.

# Broad-curation modalities. A query whose work is collecting / comparing /
# surveying options does not benefit from adversarial dialectics — it benefits
# from coverage. These modalities can absorb the breadth-only full trigger when
# contestedness is low (mirrors decompose's `light`+`structured` survey class,
# bad-research-1-decompose §7 response_format table).
BREADTH_MODALITIES = ("collect", "compare", "survey")

# Phrasing markers that signal a curation/survey intent (used by detect_modality
# when the decompose step did not set an explicit `modality` field). Kept lower-
# case; matched against the joined sub_questions text. Conservative on purpose —
# only escalate-defeating when a clear curation cue is present.
#
# [SEMANTIC-TIERING 2026-05-28] A LEXICALLY-inferred breadth modality (matched
# here, with no explicit `modality` field on the decomp) NO LONGER buys the raised
# survey ceiling. Lexical "best/top/what-are-the" phrasing can't tell "best tech
# *stack*" (enumerate ~17 independent options → shallow/wide) from "best tRPC
# *patterns*" (investigate ~8 facets of ONE subject → deep). detect_modality still
# returns a modality for shape/other uses, but the survey-ceiling down-route now
# gates on `_explicit_breadth_modality` (router.py) — an EXPLICIT `modality` field.
SURVEY_PHRASE_MARKERS = (
    "best ", "top ", "list of", "list the", "overview of", "landscape",
    "options for", "alternatives to", "which ", "what are the",
)
COMPARE_PHRASE_MARKERS = ("compare ", " vs ", " vs. ", "versus ", "difference between")

# Contestedness signal weights (0..1 score). A query clears CONTESTEDNESS_FULL_FLOOR
# when it carries genuine source-tension signals; below the floor, a broad-curation
# query is allowed to down-route. Contradiction terms are the strongest signal
# (they ARE the decompose contradiction taxonomy), so a single one clears the floor.
CONTESTEDNESS_W_CONTRADICTION = 0.60   # any contradiction_terms entry
CONTESTEDNESS_W_ARGUMENTATIVE = 0.50   # response_format == "argumentative"
CONTESTEDNESS_W_DISPUTE_PHRASE = 0.40  # dispute phrasing in sub_questions
CONTESTEDNESS_FULL_FLOOR = 0.50        # >= floor → genuinely contested → keep full

# Dispute phrasing markers (the contested-topic cues from decompose §7 "full" row).
DISPUTE_PHRASE_MARKERS = (
    "disputed", "controversial", "debate", "evaluate whether", "is it true",
    "should ", "trade-off", "tradeoff", "pros and cons", "for or against",
)

# A broad-curation survey may carry MORE atomic items in `light` before it is
# forced `full` by breadth — the whole point of B-5 (17 items of "best X" is a
# survey, not a thesis). This raised ceiling applies ONLY when modality is a
# BREADTH_MODALITY and contestedness is below the floor; the deep-modality path
# keeps ROUTER_LIGHT_MAX_ATOMIC unchanged.
ROUTER_SURVEY_MAX_ATOMIC = 40


# ── E12 query-SHAPE classifier (2026-05-27) ──────────────────────────────────
# Claude Research classifies the query SHAPE before searching (verbatim
# research_lead_agent.md:12-29): the subagent count AND the delegation pattern
# (sequential vs parallel) are downstream of this 3-way classification, not of a
# raw token budget. Shape is ORTHOGONAL to the cost tier: tier = how many
# resources (light/full), shape = how they're arranged.
#
#   - depth_first   : one topic, multiple perspectives → SEQUENTIAL subagents
#                     (each reads the prior's committed position). "What really
#                     caused the 2008 financial crisis?"
#   - breadth_first : independent sub-questions → PARALLEL subagents, importance-
#                     ordered, K=min(n_independent_subq, cap). "Compare the
#                     economic systems of three Nordic countries."
#   - straightforward : focused/well-defined → a SINGLE subagent. "What is the
#                     current population of Tokyo?"
#
# CRITICAL: query_shape is a NEW field that ADDS the fan-out shape. It MUST NOT
# change classify_route's fast/full decision (the golden corpus's
# decompose-component checks assert that route). The classifier reuses the
# existing modality + contestedness signals; it never feeds back into the route.

# How many atomic items count as a "straightforward" single-investigation query.
SHAPE_STRAIGHTFORWARD_MAX_ATOMIC = 2

# The parallel breadth-first fan-out cap. The effective K is
# min(n_independent_subq, this cap).
#
# This K IS the depth-investigator count, so it must equal LOCI_MAX — the cap
# steps 4 and 5 actually enforce. It used to mirror SUBAGENT_FANOUT_MAX (20),
# which made `bad route` promise a 25-sub-question survey "K=20 parallel
# investigators" when 6 would run: 3.3x over-reported width, 19 sub-questions
# dropped, nothing recording it (issue #36 item 5). The cap is unchanged in
# effect — only the reported number was ever wrong — and what falls outside it
# is now reported as DEFERRED rather than silently truncated.
SHAPE_BREADTH_K_CAP = LOCI_MAX  # 6

# Depth-first deploys 2-4 SEQUENTIAL perspectives on one locus.
SHAPE_DEPTH_MIN_PERSPECTIVES = 2
SHAPE_DEPTH_MAX_PERSPECTIVES = 4

# The fan-out arrangement per shape. `k` is the literal count when fixed;
# `arrangement` is single | parallel | sequential. The breadth-first K is
# computed at dispatch time as min(n_independent_subq, k_cap).
SHAPE_FANOUT: dict[str, dict[str, object]] = {
    "straightforward": {"arrangement": "single", "k": 1},
    "breadth_first": {"arrangement": "parallel", "k_cap": SHAPE_BREADTH_K_CAP,
                      "importance_ordered": True},
    "depth_first": {"arrangement": "sequential",
                    "min_k": SHAPE_DEPTH_MIN_PERSPECTIVES,
                    "max_k": SHAPE_DEPTH_MAX_PERSPECTIVES},
}


# ── E11 user-editable plan-gate (Gemini collaborative_planning; STEAL_LIST #3) ─
# Gemini emits a structured plan → the user approves/edits → execute, so an
# ambiguous/broad query doesn't research the wrong sub-questions. The gate
# (step bad-research-1.6-plan-gate) fires ONLY when the run is INTERACTIVE and not
# `--auto`/wrapped and it is a FULL-ROUTE or BROAD-SURVEY run — route == full OR
# atomic items > ROUTER_LIGHT_MAX_ATOMIC. A non-interactive / wrapped / `--auto` /
# test run NEVER gates (mirrors how 0.5-clarify skips for `--auto`/wrapped) so the
# eval gate + the whole test suite flow straight through. A small bounded `fast`
# run is below the bar — a wrong sub-question there costs less than the approval
# round-trip.


# ── KR-6 loop levers (dossier 16; INTERFACES_KEYLESS §8 frozen table) ─────────

# Grader loop — judge -> patch -> re-judge, capped (patch-not-regenerate => 3 is
# enough; NOT Claude's 20 which assumes full regeneration). dossier 16 §4.1.
MAX_GRADER_REVISIONS = 3

# Per-subagent runtime caps (Claude CE.5), keyless host guards. dossier 16 §3.2.
FETCHER_TOOLCALL_CAP = {"light": 10, "full": 20}  # tool calls per fetcher
FETCHER_TIMEOUT_S = 300       # soft-fail, return partial findings
INVESTIGATOR_TIMEOUT_S = 900  # depth stage scaled (Grok 200s x cost)
SUBAGENT_SOURCE_KILL = 100    # hard stop on sources touched (Claude)

# Reasoning-effort continuum — OpenAI's 4-level dial (dossier 16 §6.1) mapped onto
# the existing route + per-stage fan-out levers. Wiring the stub --effort flag
# (research.py) into a real config the router consumes.
#
# There is deliberately NO `tier` (model) column. It used to name a model tier per
# effort level, but nothing ever applied it: every step skill pins its own subagent
# tier (`tier: "work"` in the spawn contract), the orchestrator cannot re-tier itself,
# and the map's own "default" value was not even a member of the model-tier vocabulary
# (config.model_tiers = triage/work/heavy) — so it could not have been honoured as
# written. The live model-cost lever is `config.cheap` (heavy→work, llm/anthropic.py).
EFFORT_LEVELS = ("minimal", "low", "medium", "high")
EFFORT_MAP = {
    "minimal": {"route": "fast", "fetchers_max": 4,  "loci_max": 0,
                "extended_thinking": False, "single_draft": True},
    "low":     {"route": "fast", "fetchers_max": 8,  "loci_max": 0,
                "extended_thinking": False, "single_draft": True},
    "medium":  {"route": "full", "fetchers_max": 12, "loci_max": 4,
                "extended_thinking": True,  "single_draft": False},
    "high":    {"route": "full", "fetchers_max": 12, "loci_max": LOCI_MAX,
                "extended_thinking": True,  "single_draft": False},
}

# Token-ceiling degrade order (Claude §12: cut tokens LAST). dossier 16 §6.2.
# Each step names what the orchestrator drops first when approaching --max-tokens.
# The terminal step is the E10 / STEAL_LIST #6c per-step short-circuit (Perplexity):
# when even fan-out + model-tier cuts leave less than RESERVE_FOR_SYNTHESIS, stop
# stepping and go straight to synthesis with whatever's gathered. The synthesis +
# grounding TOKEN budget itself is STILL never a degrade step (the 80%-variance core);
# short_circuit_to_synthesis PROTECTS that budget by reserving it, it does not cut it.
DEGRADE_ORDER = (
    "tool-call-redundancy",         # 1. skip the redundancy-audit sub-step
    "fan-out-width",                # 2. fewer fetchers / fewer loci
    "model-tier",                   # 3. heavy -> light on non-critical stages
    "short_circuit_to_synthesis",   # 4. TERMINAL: stop retrieval/critic, jump to synthesis
    # NEVER cut synthesis/grounding token budget — the 80%-variance core.
)

# E10 / STEAL_LIST #6c — the token budget the run RESERVES for synthesis + the
# grounding/citation pass so a retrieval-heavy run never burns the whole ceiling
# on fetching and dies mid-pipeline. Covers the ≤10K-token distilled synthesis
# context (Chroma ceiling, bad-research-11-synthesize §11.4b) + the multi-draft
# synthesis OUTPUT + the grounding/uncited-gate/citation-verifier pass. When the
# remaining budget (ceiling - cumulative) drops below this, the orchestrator walks
# DEGRADE_ORDER to its terminal `short_circuit_to_synthesis` step. Perplexity-style
# "reserve budget for synthesis" (PERPLEXITY_COMPUTER.md:434).
RESERVE_FOR_SYNTHESIS = 40_000  # tokens; ~10K synth context + draft output + grounding

# ── The RUN-LEVEL wall-clock deadline for the `full` route ────────────────────
# The SECOND, independent trigger for the SAME terminal `short_circuit_to_synthesis`
# step above — not a new degrade step. The token trigger is opt-in (`--max-tokens`)
# AND needs a cumulative token count no phase actually accounts for, so on a default
# full run the terminal step was unreachable: a long run died mid-pipeline (losing
# every in-flight agent) instead of degrading to a shipped, grounded, smaller-corpus
# report. The full route's ONLY other deadline is per-wave (FETCHER_TIMEOUT_S), which
# bounds one fetcher wave and says nothing about the run.
#
# Wall-clock is the right denominator precisely because it is OBSERVABLE and the model
# cannot fake it — the same discipline the fast loop applies to its stop rule ("loop
# counters, not model claims — the stop is auditable even if the model lies",
# bad-research-fast.md). A model-written token estimate has neither property.
#
# The net must not fire inside the route's OWN advertised band. The entry skill
# announces "Route: full (~1.5-2.5 h)", i.e. up to 9000 s is a healthy run — and the
# predicate fires a whole RESERVE_FOR_SYNTHESIS_S EARLY, because "compose now" has to
# leave room to actually compose. So the deadline is the top of the band PLUS that
# reserve: 9000 + 1800 = 10800 s. The trigger point is then exactly 9000 s = 2.5 h —
# the first moment a run has provably outlived its own worst-case estimate — and the
# whole job is bounded at 3 h. Setting this to 9000 instead would have fired at
# 7200 s = 2.0 h, in the middle of the advertised band, degrading healthy runs.
# This is the full-route twin of FAST_TIMEOUT_S (600 s on a <10-min target) — a
# safety net over the structural caps, never a replacement for them.
FULL_TIMEOUT_S = 10800  # seconds; run-level wall-clock net for `full` (3 h)

# Wall-clock twin of RESERVE_FOR_SYNTHESIS: the slice of the deadline held back for
# the stages the short-circuit jumps TO (10 drafts → 11 synthesis → 11.5 grounding →
# 15/16 gate). Deliberately larger than one INVESTIGATOR_TIMEOUT_S (900 s) because
# that seam is several stages, not one subagent. "Compose now" fires while this much
# time is still LEFT, so synthesis still fits inside the deadline — reserving it after
# the deadline passes would reserve nothing.
RESERVE_FOR_SYNTHESIS_S = 1800  # seconds; ~30 min of drafting + synthesis + grounding
