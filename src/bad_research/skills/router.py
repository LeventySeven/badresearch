"""Query router — classify the Step-1 decompose output into a pipeline mode.

Reuses the existing atomic-item analysis (no new classifier). The decision
tree (2-route consolidation; the former agentic-fast + light bands both map to
`fast` now — the split is an internal shape+effort knob, not a route):

  full  if multi-domain, contested, argumentative, time_periods, >=7 items, or a
        pipeline_tier == "full" floor
  fast  else (the bounded planner->writer loop — formerly agentic-fast/light)

[SEMANTIC-TIERING 2026-05-28] Two corrections to the post-B-5 behaviour:

  1. **`pipeline_tier == "full"` from decompose is an honoured FLOOR.** Step 1
     (bad-research-1-decompose.md) judges the SEMANTIC depth the query wants and
     writes `pipeline_tier`, with "Default is full; when uncertain, tier up". The
     router previously IGNORED that field and its docstring falsely claimed it
     "never down-routes a justified full". It now does: an explicit
     `pipeline_tier == "full"` forces `full` — mechanical heuristics may ESCALATE
     above the model's call but never DEMOTE below it. A missing / `"light"`
     pipeline_tier imposes no floor (so every fixture that omits it is unchanged).
  2. **The raised survey ceiling now requires an EXPLICIT breadth `modality`.** A
     merely lexically-inferred survey (detect_modality falling back to
     SURVEY_PHRASE_MARKERS, no explicit `modality` field) no longer buys the
     ROUTER_SURVEY_MAX_ATOMIC ceiling — it falls back to the depth-favouring deep
     ceiling ROUTER_LIGHT_MAX_ATOMIC. This kills the lexical "best X"→light demotion
     of deep single-subject queries while preserving the explicit-survey down-route.
"""
from __future__ import annotations

import re
from typing import Any, Literal

from bad_research.skills import routing_constants as R  # noqa: N812

Route = Literal["fast", "full", "ultrafast"]
QueryShape = Literal["straightforward", "breadth_first", "depth_first"]

# The 3-way Claude Research fan-out-shape taxonomy (research_lead_agent.md:12-29).
QUERY_SHAPES: tuple[QueryShape, ...] = ("straightforward", "breadth_first", "depth_first")


def _atomic_count(decomp: dict[str, Any]) -> int:
    # atomic items = sub_questions + named entities (the Step-1 taxonomy)
    return len(decomp.get("sub_questions") or []) + len(decomp.get("entities") or [])


def _sub_q_text(decomp: dict[str, Any]) -> str:
    """Lower-cased join of the sub_questions for phrase-marker matching.

    sub_questions entries are usually strings; tolerate non-strings (e.g. the
    effort test passes ``range(7)``) by string-coercing each item."""
    return " ".join(str(q) for q in (decomp.get("sub_questions") or [])).lower()


def detect_modality(decomp: dict[str, Any]) -> str:
    """Classify the query's WORK shape: a BREADTH modality (collect/compare/
    survey — coverage-driven curation) vs ``"deep"`` (analysis-driven, where
    adversarial dialectics earn their cost). B-5.

    Honours an explicit ``modality`` field from the decompose step when present
    and valid; otherwise INFERS from sub_questions phrasing. Conservative: a
    curation modality is only returned on a clear curation cue — the default is
    ``"deep"`` so the existing full-tier behaviour is preserved when no signal
    exists (protects the 7-item structured invariant)."""
    explicit = decomp.get("modality")
    if isinstance(explicit, str) and explicit in R.BREADTH_MODALITIES:
        return explicit
    if isinstance(explicit, str) and explicit == "deep":
        return "deep"

    text = _sub_q_text(decomp)
    if any(m in text for m in R.COMPARE_PHRASE_MARKERS):
        return "compare"
    if any(m in text for m in R.SURVEY_PHRASE_MARKERS):
        return "survey"
    return "deep"


def _explicit_breadth_modality(decomp: dict[str, Any]) -> bool:
    """Whether the decompose step EXPLICITLY declared a breadth modality.

    [SEMANTIC-TIERING 2026-05-28] Only an explicit `modality` field set to one of
    R.BREADTH_MODALITIES counts. A modality that detect_modality merely INFERRED
    from sub_questions phrasing (the SURVEY_PHRASE_MARKERS / COMPARE_PHRASE_MARKERS
    lexical fallback) does NOT count here — lexical "best X" phrasing cannot
    distinguish a shallow option-enumeration survey from a deep single-subject
    investigation, so it no longer earns the raised survey ceiling. This is the
    crux of the fix: the survey down-route is gated on an EXPLICIT model judgment,
    not on wording."""
    explicit = decomp.get("modality")
    return isinstance(explicit, str) and explicit in R.BREADTH_MODALITIES


def _explicit_light_tier(decomp: dict[str, Any]) -> bool:
    """Whether the decompose step EXPLICITLY declared `pipeline_tier == "light"`.

    Symmetric to `_pipeline_tier_floor_full`: where an explicit `"full"` is a FLOOR
    (never demote below it), an explicit `"light"` is the model's judgment that the
    query wants the cheap route — so a mechanical atomic-item COUNT alone must not
    override it into `full`. This is the signal the router was ignoring: a structured,
    `pipeline_tier="light"` survey with >6 atomic items (sub_questions + entities) was
    force-`full`-ed purely on count, making the cheaper tier unreachable for exactly
    the multi-entity surveys it was designed for (issue #15). The HARD full triggers
    (time_periods, argumentative, contradiction terms, multi-domain) are untouched and
    still escalate regardless — only the breadth-only count trigger is relaxed, and
    only when contestedness is below the floor. A missing pipeline_tier returns False
    (preserves the depth-favouring default for every fixture that omits the field)."""
    return decomp.get("pipeline_tier") == "light"


def _pipeline_tier_floor_full(decomp: dict[str, Any]) -> bool:
    """Whether the decompose step explicitly declared `pipeline_tier == "full"`.

    [SEMANTIC-TIERING 2026-05-28] This is the SEMANTIC depth signal the router must
    honour as a FLOOR: when the model (step 1) judged the query deep enough to want
    the full pipeline, classify_route must never demote it to fast.
    Mechanical heuristics escalate above this, never below. A missing or `"light"`
    pipeline_tier returns False (no floor) — preserving every fixture that omits it."""
    return decomp.get("pipeline_tier") == "full"


def contestedness_score(decomp: dict[str, Any]) -> float:
    """0..1 score of how source-CONTESTED the query is. >= CONTESTEDNESS_FULL_FLOOR
    means genuine tension that warrants the full adversarial path even for a
    broad query; below the floor a curation/survey query may down-route. B-5.

    Weights (routing_constants): contradiction terms are the strongest signal
    (they ARE the decompose contradiction taxonomy), argumentative format next,
    then dispute phrasing in the sub_questions. The score is the max of the
    individual signals (any single strong signal suffices), not a sum — we never
    want stacking to lower the effective bar."""
    fmt = decomp.get("response_format", "structured")
    contradiction = decomp.get("contradiction_terms") or []
    text = _sub_q_text(decomp)

    signals = [0.0]
    if contradiction:
        signals.append(R.CONTESTEDNESS_W_CONTRADICTION)
    if fmt == "argumentative":
        signals.append(R.CONTESTEDNESS_W_ARGUMENTATIVE)
    if any(m in text for m in R.DISPUTE_PHRASE_MARKERS):
        signals.append(R.CONTESTEDNESS_W_DISPUTE_PHRASE)
    return max(signals)


# time_periods entry `type`s that mark a PUBLICATION date, not a period-pinned
# primary-source window — a bare publication year must not escalate to the full tier.
_PUBLICATION_PERIOD_TYPES = frozenset(
    {"publication-year", "publication", "pub-year", "pub_year", "year"}
)
_BARE_YEAR = re.compile(r"\d{4}")


def _forces_full_period(entry: Any) -> bool:
    """True when ONE `time_periods` entry is a PERIOD-PINNED primary-source window
    (Lens D): a fiscal quarter/year, a filing, a dated event, or a multi-year range —
    the case where the report must fetch the exact filing for that period.

    A BARE single publication year ("2017", or a dict whose `type` marks it a
    publication year) is NOT period-pinned — it is merely when a source appeared, and
    must not escalate a trivial lookup to the full ~2.5h pipeline (over-escalation)."""
    if isinstance(entry, dict):
        ptype = str(entry.get("type", "")).strip().lower()
        if ptype and ptype not in _PUBLICATION_PERIOD_TYPES:
            return True  # an explicit fiscal / regulatory / event type is period-pinned
        text = str(entry.get("period", "")).strip()
    else:
        text = str(entry).strip()
    # No fiscal/event type → period-pinned iff the text is not a bare 4-digit year
    # (quarters "Q3 2024", ranges "1993-2023", months "March 2024", filings all qualify).
    return bool(text) and not _BARE_YEAR.fullmatch(text)


def _period_pinned_time_periods(decomp: dict[str, Any]) -> bool:
    """True when `time_periods` holds >=1 PERIOD-PINNED window (the Lens-D full-tier
    trigger). A list of only bare publication years does not qualify."""
    return any(_forces_full_period(e) for e in (decomp.get("time_periods") or []))


def _hard_full_triggers(decomp: dict[str, Any]) -> list[str]:
    """The full-tier triggers that are NON-NEGOTIABLE regardless of modality:
    Lens-D primaries (period-pinned time_periods), explicit argumentative format,
    contradiction terms (source tensions), and multi-domain breadth. Unchanged by
    B-5 — only the breadth-only (atomic-count) trigger gains the modality gate; and a
    bare publication year in time_periods no longer counts (over-escalation fix)."""
    fmt = decomp.get("response_format", "structured")
    contradiction = decomp.get("contradiction_terms") or []
    domains = decomp.get("domains") or []
    reasons: list[str] = []
    if _period_pinned_time_periods(decomp):
        reasons.append("period-pinned time_periods present (Lens D primaries)")
    if fmt == "argumentative":
        reasons.append("argumentative response_format (dialectics)")
    if contradiction:
        reasons.append("contradiction terms present (source tensions)")
    if len(domains) >= 3:
        reasons.append("multi-domain (>=3 domains)")
    return reasons


def _breadth_forces_full(decomp: dict[str, Any]) -> bool:
    """Whether the atomic-item COUNT escalates to full, AFTER the modality gate.

    [SEMANTIC-TIERING 2026-05-28] The raised survey ceiling (ROUTER_SURVEY_MAX_ATOMIC)
    now applies ONLY when the decompose step set an EXPLICIT breadth `modality` and
    contestedness is below the floor — a broad-but-shallow curation survey the model
    itself declared. A merely lexically-inferred breadth modality (no explicit
    `modality` field) no longer buys the raised ceiling: it falls back to the
    depth-favouring deep ceiling ROUTER_LIGHT_MAX_ATOMIC, so a deep single-subject
    "best X" query escalates to full on item count as it should. (Previously this
    gated on detect_modality, which folded in the lexical fallback — that was the
    over-demotion bug.)"""
    n = _atomic_count(decomp)
    contested = contestedness_score(decomp) >= R.CONTESTEDNESS_FULL_FLOOR
    # The raised survey ceiling applies when the decompose step EXPLICITLY signalled a
    # broad-but-shallow query — via a breadth `modality` OR an explicit
    # `pipeline_tier == "light"` — and contestedness is below the floor. Both are
    # explicit model judgments; a mere lexical "best X" inference earns neither (it
    # falls through to the depth-favouring deep ceiling). issue #15 adds the
    # pipeline_tier=="light" arm so a model-declared light survey is not force-`full`-ed
    # on atomic count alone.
    if (_explicit_breadth_modality(decomp) or _explicit_light_tier(decomp)) and not contested:
        # EXPLICITLY-declared broad-but-shallow curation: breadth alone does not
        # buy adversarial depth, so the raised survey ceiling applies.
        return n > R.ROUTER_SURVEY_MAX_ATOMIC
    return n > R.ROUTER_LIGHT_MAX_ATOMIC


def _full_triggers(decomp: dict[str, Any]) -> list[str]:
    """The reasons (if any) a query MUST route full. Empty list → not forced full."""
    reasons: list[str] = []
    if _pipeline_tier_floor_full(decomp):
        # the SEMANTIC depth floor (SEMANTIC-TIERING 2026-05-28)
        reasons.append('decompose pipeline_tier="full" (semantic depth floor)')
    reasons.extend(_hard_full_triggers(decomp))
    if _breadth_forces_full(decomp):
        n = _atomic_count(decomp)
        reasons.append(f"{n} atomic items (>{R.ROUTER_LIGHT_MAX_ATOMIC})")
    return reasons


def classify_route(decomp: dict[str, Any]) -> Route:
    fmt = decomp.get("response_format", "structured")
    contradiction = decomp.get("contradiction_terms") or []
    domains = decomp.get("domains") or []
    multi_domain = len(domains) >= 3

    # FULL: explicit pipeline_tier floor, PERIOD-PINNED time_periods, argumentative,
    # contradiction, multi-domain, or a breadth count that survives the modality gate.
    # A bare publication year in time_periods no longer forces full (over-escalation fix).
    if (_pipeline_tier_floor_full(decomp)
            or _period_pinned_time_periods(decomp) or fmt == "argumentative" or contradiction
            or multi_domain or _breadth_forces_full(decomp)):
        return "full"

    # FAST: everything else. The former agentic-fast (trivial/bounded) and light
    # (mid-band structured) bands both run the bounded planner->writer loop; the
    # split is now an internal shape+effort knob, not a route.
    return "fast"


def route_reason(decomp: dict[str, Any]) -> str:
    """A one-line, human-readable rationale for the chosen route."""
    route = classify_route(decomp)
    n = _atomic_count(decomp)
    modality = detect_modality(decomp)
    if route == "full":
        triggers = _full_triggers(decomp)
        return "full: " + ("; ".join(triggers) if triggers else "complex query")
    # FAST: call out when an EXPLICIT broad-curation signal spared a high-breadth
    # query from full (the B-5 / issue-#15 gate) so the rationale line is auditable.
    if n > R.ROUTER_LIGHT_MAX_ATOMIC:
        if _explicit_breadth_modality(decomp):
            return (f"fast: {n} atomic item(s) but explicit {modality} modality / low "
                    f"contestedness — breadth alone does not force full (B-5)")
        if _explicit_light_tier(decomp):
            return (f"fast: {n} atomic item(s) but explicit pipeline_tier=light / low "
                    f"contestedness — breadth alone does not force full (issue #15)")
    return f"fast: {n} atomic item(s), no full-tier trigger"


def plan_gate_fires(
    decomp: dict[str, Any],
    *,
    interactive: bool = False,
    wrapped: bool = False,
    auto: bool = False,
) -> bool:
    """E11 user-editable plan-gate trigger (Gemini collaborative_planning,
    STEAL_LIST #3). Decides whether step bad-research-1.6-plan-gate should emit a
    plan and pause for "approve / edit / proceed" before step 2 runs.

    **This is a SEPARATE gate step — it does NOT and MUST NOT influence
    classify_route.** It reads the same decomposition only to ask "is this a
    full-route or broad-survey run worth a human approval round-trip?"; the route
    output is untouched (it merely reads `classify_route`'s decision, never
    mutates it).

    Fires iff ALL of:
      * `interactive` — a human is at the keyboard to approve/edit. The DEFAULT is
        ``False`` so an automated caller (the eval gate, the test suite, any `-p`
        run that doesn't opt in) NEVER gates.
      * not `wrapped` and not `auto` — a wrapped run (`research/wrapper_contract.json`
        present) or an `--auto` run carries a binding GOSPEL query that must not be
        questioned (mirrors exactly how 0.5-clarify skips for wrapper/auto).
      * a FULL-ROUTE or BROAD-SURVEY run — the route is `full`, OR the atomic-item
        count exceeds `ROUTER_LIGHT_MAX_ATOMIC` (a broad survey the modality gate
        spared from full but which is still wide enough to mis-scope). A small
        bounded `fast` run is below the bar: a wrong sub-question there costs less
        than the approval round-trip.

    The interactivity flags are supplied by the orchestrator at step 1.6 (it knows
    whether the session is interactive and whether wrapper_contract.json exists);
    this keeps the predicate a pure, unit-testable function with no I/O.
    """
    if not interactive or wrapped or auto:
        return False
    route = classify_route(decomp)
    return bool(
        route == "full"
        or _atomic_count(decomp) > R.ROUTER_LIGHT_MAX_ATOMIC
    )


def _n_independent_subq(decomp: dict[str, Any]) -> int:
    """The count of independent sub-questions the breadth-first parallel fan-out
    can split across. Uses the atomic count (sub_questions + entities) — the same
    taxonomy classify_route uses, so the two stay consistent without coupling."""
    return _atomic_count(decomp)


def classify_query_shape(decomp: dict[str, Any]) -> QueryShape:
    """Classify the query's FAN-OUT SHAPE (E12, Claude Research
    research_lead_agent.md:12-29) — ORTHOGONAL to the cost tier classify_route
    decides. This determines how investigators are ARRANGED (single / parallel /
    sequential), never how many resources the run gets.

    **This function does NOT and MUST NOT influence classify_route.** It reads the
    same decompose signals (modality + contestedness + atomic count) but feeds a
    separate `query_shape` field; the route output is unchanged. (DESIGN classifier
    from STEAL_LIST #2.)

    Decision order:
      1. depth_first  — one contested topic, multiple perspectives. A genuinely
         contested query (contestedness >= floor) on a DEEP modality is depth-first
         regardless of how few atomic items it carries: "going deep" on a singular
         core question (research_lead_agent.md:13). Sequential perspectives.
      2. straightforward — focused/well-defined: <= 2 atomic items / a single
         entity, no curation breadth, not contested. One investigation.
      3. breadth_first — the default for the rest: many independent sub-questions
         / multiple entities (typically a collect/compare/survey modality).
         Parallel, importance-ordered.
    """
    n = _n_independent_subq(decomp)
    modality = detect_modality(decomp)
    contested = contestedness_score(decomp) >= R.CONTESTEDNESS_FULL_FLOOR

    # 1. depth-first: one topic, many perspectives. Contested + a deep (non-
    #    breadth) modality = "go deep" on a singular core question.
    if contested and modality not in R.BREADTH_MODALITIES:
        return "depth_first"

    # 2. straightforward: a focused, bounded single investigation.
    if (n <= R.SHAPE_STRAIGHTFORWARD_MAX_ATOMIC
            and modality not in R.BREADTH_MODALITIES
            and not contested):
        return "straightforward"

    # 3. breadth-first: independent sub-questions / multiple entities → go wide.
    #    This is the natural shape for collect/compare/survey and for any query
    #    that splits into many parallel streams.
    if modality in R.BREADTH_MODALITIES or n > R.SHAPE_STRAIGHTFORWARD_MAX_ATOMIC:
        return "breadth_first"

    # Fallback: a small, deep, uncontested query → single investigation.
    return "straightforward"


def shape_reason(decomp: dict[str, Any]) -> str:
    """A one-line rationale for the chosen query_shape (the router skill writes it
    next to the route rationale; the `bad route` CLI carries it as `shape_reason`)."""
    shape = classify_query_shape(decomp)
    n = _n_independent_subq(decomp)
    modality = detect_modality(decomp)
    if shape == "depth_first":
        return (f"depth_first: one contested topic ({modality} modality), "
                f"{R.SHAPE_DEPTH_MIN_PERSPECTIVES}-{R.SHAPE_DEPTH_MAX_PERSPECTIVES} "
                "sequential perspectives on one locus")
    if shape == "breadth_first":
        k = min(n, R.SHAPE_BREADTH_K_CAP)
        return (f"breadth_first: {n} independent sub-question(s) ({modality}), "
                f"K={k} parallel investigators, importance-ordered")
    return (f"straightforward: {n} atomic item(s), single focused investigation "
            "(1 investigator)")


def shape_fanout(decomp: dict[str, Any]) -> dict[str, Any]:
    """Resolve SHAPE_FANOUT for this decomposition: the arrangement + the concrete
    investigator count K. For breadth_first, K = min(n_independent_subq, cap)."""
    shape = classify_query_shape(decomp)
    spec = dict(R.SHAPE_FANOUT[shape])
    if shape == "breadth_first":
        spec["k"] = min(_n_independent_subq(decomp), R.SHAPE_BREADTH_K_CAP)
    spec["shape"] = shape
    return spec


def effort_overrides(effort: str | None) -> dict[str, Any] | None:
    """Translate the `--effort` dial (minimal/low/medium/high) into the
    router overrides the orchestrator applies on top of the auto-classified route.

    Returns None for an absent/invalid effort (the auto-route is left untouched).
    The returned dict pins {route, tier, fetchers_max, loci_max, extended_thinking,
    single_draft} — OpenAI's 4-level continuum expressed as a host-side config
    (dossier 16 §6.1). This is the wiring for the stub flag in cli/research.py.
    """
    if effort not in R.EFFORT_MAP:
        return None
    return dict(R.EFFORT_MAP[effort])


def degrade_order() -> tuple[str, ...]:
    """The Claude token-ceiling degrade order (dossier 16 §6.2): cut tool-call
    redundancy, then fan-out width, then model tier, then — as the TERMINAL action
    (E10 / STEAL_LIST #6c) — short_circuit_to_synthesis. NEVER the synthesis/grounding
    token budget itself (the 80%-variance core). The orchestrator walks this list when
    a run approaches its --max-tokens ceiling; the terminal step is taken when
    should_short_circuit() fires."""
    return R.DEGRADE_ORDER


def should_short_circuit(cumulative_tokens: int, ceiling: int | None) -> bool:
    """E10 / STEAL_LIST #6c — the per-step short-circuit-to-synthesis predicate
    (Perplexity "reserve budget for synthesis", PERPLEXITY_COMPUTER.md:434).

    After each retrieval/critic ROUND the orchestrator calls this with the running
    `cumulative_tokens` and the opt-in `--max-tokens` `ceiling`. It returns True when
    the budget left for the rest of the run has fallen BELOW the reserved synthesis +
    grounding budget — i.e. ``ceiling - cumulative < RESERVE_FOR_SYNTHESIS``. On True,
    the orchestrator stops stepping (skips remaining retrieval/critic stages), takes
    the terminal ``short_circuit_to_synthesis`` step of `degrade_order`, and jumps to
    step 10/11 with whatever's been gathered — shipping a smaller-corpus grounded
    report instead of dying mid-pipeline.

    Inert when there is no ceiling (the `--max-tokens` cap is opt-in; ``None``/``0`` →
    nothing to reserve → never short-circuit). The comparison is STRICT: a remaining
    budget exactly equal to the reserve is still enough, so it does not fire."""
    if not ceiling:   # None or 0 → no opt-in ceiling, never short-circuit
        return False
    return (ceiling - cumulative_tokens) < R.RESERVE_FOR_SYNTHESIS
