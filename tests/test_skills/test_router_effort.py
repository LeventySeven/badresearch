"""KR-6 — routing_constants loop caps + the effort continuum."""
from __future__ import annotations

from bad_research.skills import routing_constants as R


def test_grader_and_cap_constants_present_and_frozen():
    # dossier 16 §3.2 / §4.1 / INTERFACES_KEYLESS §8 frozen table
    assert R.MAX_GRADER_REVISIONS == 3
    assert R.FETCHER_TOOLCALL_CAP == {"light": 10, "full": 20}
    assert R.FETCHER_TIMEOUT_S == 300
    assert R.INVESTIGATOR_TIMEOUT_S == 900
    assert R.SUBAGENT_SOURCE_KILL == 100


def test_fast_loop_constants_present_and_anchored():
    assert R.FAST_MAX_STEPS == 6                 # open_deep_research supervisor cap; Perplexity hard-caps 10
    assert R.FAST_MAX_QUERIES_PER_STEP == 4      # dzhng breadth default
    assert R.FAST_MAX_RESULTS_PER_QUERY == 5     # dzhng + gpt-researcher agree
    assert R.FAST_MIN_NEW_DOMAINS == 2           # "last 2 searches returned similar info" -> novelty floor
    assert R.FAST_STALL_PATIENCE == 1            # fast mode stops after the first stalled step
    assert R.FAST_MIN_SOURCES_PER_SUBQ == 3      # open_deep_research "3+ relevant sources"
    assert R.FAST_MAX_SUBQUESTIONS == 3          # three clones converge on 3
    assert R.FAST_SUBRESEARCHER_K == 3           # breadth fan-out cap
    assert R.FAST_TIMEOUT_S == 600               # wall-clock safety net (8-10 min budget)
    assert R.FAST_RESERVE_SYNTH_FRAC == 0.25     # reserve 25% of budget for the writer
    assert R.FAST_CONTENT_TRIM_CHARS == 25000    # dzhng + gpt-researcher agree
    assert R.FAST_TEMPERATURE == 0.4             # gpt-researcher planner/extractor temp


def test_effort_levels_are_the_openai_four():
    assert R.EFFORT_LEVELS == ("minimal", "low", "medium", "high")
    # every level maps to a route + a fetcher fan-out cap (dossier 16 §6.1)
    for lvl in R.EFFORT_LEVELS:
        assert lvl in R.EFFORT_MAP
        row = R.EFFORT_MAP[lvl]
        assert row["route"] in ("fast", "full")
        assert isinstance(row["fetchers_max"], int)
        assert isinstance(row["loci_max"], int)
        # No `tier` key: it was a computed dial NOTHING consumed, and its "default"
        # value was not even a member of the model-tier vocabulary
        # (config.model_tiers = triage/work/heavy), so it could never have been
        # applied. Shipping a dial that does nothing is worse than not shipping it.
        assert "tier" not in row


def test_effort_monotonic_fanout():
    # minimal <= low <= medium <= high on fetcher width (the cost knob)
    widths = [R.EFFORT_MAP[l]["fetchers_max"] for l in R.EFFORT_LEVELS]
    assert widths == sorted(widths)


from bad_research.skills.router import classify_route, degrade_order, effort_overrides


def test_effort_overrides_minimal_forces_fast_single_draft():
    ov = effort_overrides("minimal")
    assert ov["route"] == "fast"
    assert ov["fetchers_max"] == 4
    assert ov["single_draft"] is True


def test_effort_overrides_high_forces_full_max_width():
    ov = effort_overrides("high")
    assert ov["route"] == "full"
    assert ov["fetchers_max"] == 12
    assert ov["loci_max"] == 6
    assert "tier" not in ov   # the unconsumed model-tier dial is gone


def test_effort_overrides_unknown_returns_none():
    # an absent/invalid --effort leaves the auto-route untouched
    assert effort_overrides(None) is None
    assert effort_overrides("turbo") is None


def test_effort_can_downgrade_full_to_light():
    # auto-classify would say full (7 atomic items), but --effort minimal pins light
    decomp = {"sub_questions": list(range(7)), "entities": [], "domains": ["x"],
              "response_format": "structured"}
    assert classify_route(decomp) == "full"
    ov = effort_overrides("minimal")
    assert ov["route"] == "fast"  # the override is the user's explicit floor/ceiling


def test_degrade_order_is_tokens_last():
    order = degrade_order()
    assert order[0] == "tool-call-redundancy"
    # fan-out width then model tier are cut before the terminal short-circuit.
    assert order[1] == "fan-out-width"
    assert order[2] == "model-tier"
    # E10 terminal action is LAST — when even those cuts leave too little budget,
    # short-circuit straight to synthesis with whatever's gathered (Perplexity).
    assert order[-1] == "short_circuit_to_synthesis"
    # the synthesis/grounding TOKEN budget itself is still never a degrade step.
    assert "grounding-tokens" not in order
    assert "synthesis-tokens" not in order


# ── E10 (STEAL_LIST #6c): per-step short-circuit-to-synthesis predicate ────────
from bad_research.skills.router import should_short_circuit


def test_reserve_for_synthesis_constant_present():
    # the reserved per-run budget that synthesis + grounding must never be starved of
    assert isinstance(R.RESERVE_FOR_SYNTHESIS, int)
    assert R.RESERVE_FOR_SYNTHESIS > 0


def test_short_circuit_fires_when_remaining_below_reserve():
    # ceiling - cumulative < RESERVE → stop stepping, go straight to synthesis.
    ceiling = 100_000
    cumulative = ceiling - (R.RESERVE_FOR_SYNTHESIS - 1)   # 1 token short of the reserve
    assert should_short_circuit(cumulative, ceiling) is True


def test_short_circuit_does_not_fire_with_ample_budget():
    ceiling = 100_000
    cumulative = ceiling - (R.RESERVE_FOR_SYNTHESIS + 50_000)   # plenty left
    assert should_short_circuit(cumulative, ceiling) is False


def test_short_circuit_at_exact_reserve_boundary_does_not_fire():
    # remaining == RESERVE is exactly enough — only a STRICT shortfall short-circuits.
    ceiling = 100_000
    cumulative = ceiling - R.RESERVE_FOR_SYNTHESIS
    assert should_short_circuit(cumulative, ceiling) is False


def test_short_circuit_inert_when_no_ceiling():
    # the --max-tokens ceiling is opt-in; with no ceiling there is nothing to reserve.
    assert should_short_circuit(999_999, None) is False
    assert should_short_circuit(999_999, 0) is False


# ── The RUN-LEVEL wall-clock deadline — the SECOND, independent trigger for the
#    same terminal short_circuit_to_synthesis step, and the only one reachable on a
#    default `full` run (the token twin above is opt-in AND needs a cumulative token
#    count no phase accounts for). ──────────────────────────────────────────────
from bad_research.skills.router import should_short_circuit_wallclock


def test_full_timeout_and_wallclock_reserve_constants_present():
    # The full route's run-level net — the twin of FAST_TIMEOUT_S (600s on a <10-min
    # target). The net must not fire inside the route's own advertised band: the
    # full run never trips it; it fires only on the long tail.
    assert R.FULL_TIMEOUT_S == 10800
    # The TRIGGER point — not the deadline — is what must clear the advertised top
    # of 2.5 h (9000 s), because "compose now" fires a full reserve early.
    assert R.FULL_TIMEOUT_S - R.RESERVE_FOR_SYNTHESIS_S == 9000
    assert R.FULL_TIMEOUT_S > R.FAST_TIMEOUT_S
    # the wall-clock twin of RESERVE_FOR_SYNTHESIS — it must fit inside the deadline
    assert 0 < R.RESERVE_FOR_SYNTHESIS_S < R.FULL_TIMEOUT_S
    # and reserve more than ONE depth-investigator window: the synthesis seam the
    # short-circuit jumps to is several stages (10 -> 11 -> 11.5 -> 15/16), not one subagent.
    assert R.RESERVE_FOR_SYNTHESIS_S > R.INVESTIGATOR_TIMEOUT_S


def test_wallclock_short_circuit_needs_no_opt_in():
    """The whole point: the terminal degrade step must be REACHABLE on a default full
    run. The token twin is inert without `--max-tokens`; the wall-clock trigger has a
    default deadline and needs no flag and no token accounting."""
    assert should_short_circuit(999_999, None) is False              # token twin: inert
    assert should_short_circuit_wallclock(R.FULL_TIMEOUT_S) is True  # wall-clock: fires


def test_wallclock_fires_when_remaining_below_reserve():
    elapsed = R.FULL_TIMEOUT_S - R.RESERVE_FOR_SYNTHESIS_S + 1   # 1s short of the reserve
    assert should_short_circuit_wallclock(elapsed) is True


def test_wallclock_does_not_fire_early_in_the_run():
    assert should_short_circuit_wallclock(60) is False


def test_wallclock_at_exact_reserve_boundary_does_not_fire():
    # remaining == the reserve is exactly enough — STRICT shortfall only, mirroring
    # should_short_circuit's boundary.
    assert should_short_circuit_wallclock(
        R.FULL_TIMEOUT_S - R.RESERVE_FOR_SYNTHESIS_S) is False


def test_wallclock_honours_an_explicit_deadline():
    assert should_short_circuit_wallclock(
        100, deadline_s=R.RESERVE_FOR_SYNTHESIS_S + 200) is False
    assert should_short_circuit_wallclock(
        100, deadline_s=R.RESERVE_FOR_SYNTHESIS_S + 50) is True


def test_wallclock_explicit_zero_deadline_opts_out():
    # An explicit 0/negative deadline is the deliberate "no wall-clock net" opt-out.
    # `None` means "use the default deadline", NOT "no deadline" — that asymmetry
    # with the token predicate IS the fix.
    assert should_short_circuit_wallclock(999_999, deadline_s=0) is False
    assert should_short_circuit_wallclock(999_999, deadline_s=-1) is False
    assert should_short_circuit_wallclock(999_999, deadline_s=None) is True


def test_wallclock_adds_no_new_degrade_step():
    # Two independent triggers, ONE already-sanctioned terminal step — the wall-clock
    # net must not grow DEGRADE_ORDER.
    order = degrade_order()
    assert order[-1] == "short_circuit_to_synthesis"
    assert len(order) == 4


def test_fetcher_toolcall_cap_is_two_route_light_and_full():
    # The `ultrafast` route was folded away 2026-07-06; the fetcher tool-call cap is
    # now a 2-key dial — light (the fast route) and full — with no middle tier.
    assert set(R.FETCHER_TOOLCALL_CAP) == {"light", "full"}
    assert R.FETCHER_TOOLCALL_CAP["light"] < R.FETCHER_TOOLCALL_CAP["full"]
    # the ULTRAFAST_* loop constants are gone with the route
    assert not hasattr(R, "ULTRAFAST_SUBRESEARCHER_K")
    assert not hasattr(R, "ULTRAFAST_TIMEOUT_S")
