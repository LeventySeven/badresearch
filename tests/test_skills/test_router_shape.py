"""E12 — Query-shape classifier (Claude Research, steal-list #2).

Claude Research classifies query SHAPE before searching (verbatim
`research_lead_agent.md:12-29`): **depth-first** (one topic, multiple
perspectives → subagents SEQUENTIAL), **breadth-first** (independent sub-questions
→ PARALLEL, importance-ordered), **straightforward** (1 subagent). Shape is
ORTHOGONAL to tier: the router already classifies cost-tier + modality +
contestedness; it had NO fan-out-shape. `query_shape` is a NEW field that ADDS the
fan-out shape — it must NOT change the existing ROUTE decision.

These tests cover the `classify_query_shape` classifier in `router.py`, the
`SHAPE_FANOUT` map in `routing_constants.py`, and — critically — that
`classify_route`'s route output is UNCHANGED for every existing router test
fixture (E12 must not shift any golden-corpus decompose-component check).
"""

from __future__ import annotations

from pathlib import Path

from bad_research.skills import routing_constants as R  # noqa: N812
from bad_research.skills.router import (
    QUERY_SHAPES,
    classify_query_shape,
    classify_route,
    fanout_coverage,
    shape_reason,
)

SKILLS_DIR = Path(__file__).resolve().parents[2] / "src" / "bad_research" / "skills"


def _decomp(**kw):
    base = dict(sub_questions=["q1"], entities=[], time_periods=[],
                response_format="structured", contradiction_terms=[], domains=["tech"])
    base.update(kw)
    return base


# ── constants ─────────────────────────────────────────────────────────────────

def test_shape_constants_present():
    assert QUERY_SHAPES == ("straightforward", "breadth_first", "depth_first")
    # SHAPE_FANOUT maps every shape to a fan-out arrangement
    assert set(R.SHAPE_FANOUT) == set(QUERY_SHAPES)
    # straightforward = exactly 1 investigator
    assert R.SHAPE_FANOUT["straightforward"]["k"] == 1
    assert R.SHAPE_FANOUT["straightforward"]["arrangement"] == "single"
    # breadth_first = parallel, importance-ordered, K=min(n_subq, cap)
    assert R.SHAPE_FANOUT["breadth_first"]["arrangement"] == "parallel"
    assert R.SHAPE_FANOUT["depth_first"]["arrangement"] == "sequential"
    # depth-first runs 2-4 sequential perspectives on one locus
    assert R.SHAPE_FANOUT["depth_first"]["min_k"] == 2
    assert R.SHAPE_FANOUT["depth_first"]["max_k"] == 4
    # the breadth-first parallel fan-out cap
    assert R.SHAPE_FANOUT["breadth_first"]["k_cap"] >= 1


# ── classifier: the three distinct shapes ──────────────────────────────────────

def test_single_entity_factual_is_straightforward():
    # "What is the current population of Tokyo?" — one entity, 1-2 atomic items
    d = _decomp(sub_questions=["what is the current population of Tokyo"],
                entities=["Tokyo"], response_format="short", domains=["geo"])
    assert classify_query_shape(d) == "straightforward"


def test_two_atomic_single_entity_is_straightforward():
    d = _decomp(sub_questions=["what is the tax deadline this year"],
                entities=[], response_format="short")
    assert classify_query_shape(d) == "straightforward"


def test_multi_entity_survey_is_breadth_first():
    # "Compare the economic systems of three Nordic countries" — independent subqs
    d = _decomp(
        sub_questions=[f"economic system of country {i}" for i in range(6)],
        entities=["Norway", "Sweden", "Denmark"],
        response_format="structured", modality="compare", domains=["econ"],
    )
    assert classify_query_shape(d) == "breadth_first"


def test_many_independent_subquestions_is_breadth_first():
    # "net worths + names of all fortune 500 CEOs" — splits into parallel streams
    d = _decomp(
        sub_questions=[f"who runs company {i}" for i in range(12)],
        entities=[f"co{i}" for i in range(5)],
        response_format="structured", modality="collect", domains=["finance"],
    )
    assert classify_query_shape(d) == "breadth_first"


def test_contested_thesis_is_depth_first():
    # "What really caused the 2008 financial crisis?" — one topic, many perspectives
    d = _decomp(
        sub_questions=["what caused the 2008 financial crisis"],
        entities=["2008 financial crisis"],
        response_format="argumentative", contradiction_terms=["versus"],
        modality="deep", domains=["econ"],
    )
    assert classify_query_shape(d) == "depth_first"


def test_synthesize_high_contestedness_is_depth_first():
    d = _decomp(
        sub_questions=["does remote work raise productivity"],
        response_format="argumentative", contradiction_terms=["disputed"],
        modality="deep", domains=["econ"],
    )
    assert classify_query_shape(d) == "depth_first"


def test_three_shapes_are_distinct():
    factual = _decomp(sub_questions=["population of Tokyo"], entities=["Tokyo"],
                      response_format="short", domains=["geo"])
    survey = _decomp(sub_questions=[f"metric {i}" for i in range(8)],
                     entities=["a", "b", "c"], response_format="structured",
                     modality="compare", domains=["tech"])
    thesis = _decomp(sub_questions=["evaluate whether X caused Y"],
                     response_format="argumentative",
                     contradiction_terms=["disputed"], modality="deep")
    shapes = {classify_query_shape(factual),
              classify_query_shape(survey),
              classify_query_shape(thesis)}
    assert shapes == {"straightforward", "breadth_first", "depth_first"}


def test_shape_always_in_enum():
    for d in [_decomp(), _decomp(response_format="short", sub_questions=["q"]),
              _decomp(sub_questions=[f"q{i}" for i in range(20)])]:
        assert classify_query_shape(d) in QUERY_SHAPES


def test_shape_reason_is_nonempty_string():
    r = shape_reason(_decomp())
    assert isinstance(r, str) and r != ""
    # the reason names the chosen shape
    assert classify_query_shape(_decomp()) in shape_reason(_decomp())


# ── issue #36: the breadth cap must equal the cap the pipeline enforces ────────
# The breadth-first K IS the depth-investigator count. SHAPE_BREADTH_K_CAP used
# to alias SUBAGENT_FANOUT_MAX (20) while steps 4 and 5 spawn at most 6, so
# `bad route` promised a 25-sub-question survey "K=20 parallel investigators"
# and 19 sub-questions were dropped with nothing recording it.

def _wide_survey(n=25):
    """A breadth-first decomposition far wider than the loci cap."""
    return _decomp(sub_questions=[f"option {i}" for i in range(n)], entities=[],
                   response_format="structured", modality="collect",
                   domains=["tech"])


def test_breadth_k_cap_matches_the_loci_cap_the_skills_enforce():
    assert R.LOCI_MAX == 6
    assert R.SHAPE_BREADTH_K_CAP == R.LOCI_MAX
    assert R.SHAPE_FANOUT["breadth_first"]["k_cap"] == R.LOCI_MAX
    # LOCI_MAX is its OWN constant, not an alias of the generic subagent ceiling
    assert R.SHAPE_BREADTH_K_CAP != R.SUBAGENT_FANOUT_MAX
    # and the top effort rung reads from the same source of truth
    assert R.EFFORT_MAP["high"]["loci_max"] == R.LOCI_MAX


def test_shape_reason_reports_deferred_subquestions():
    d = _wide_survey(25)
    assert classify_query_shape(d) == "breadth_first"
    r = shape_reason(d)
    # the K it reports is the K that will actually run
    assert f"K={R.LOCI_MAX} " in r
    assert "K=20" not in r
    # and it says out loud what this pass does NOT cover
    assert f"covers {R.LOCI_MAX} of 25" in r
    assert f"{25 - R.LOCI_MAX} deferred" in r


def test_shape_reason_omits_the_deferred_clause_when_nothing_is_dropped():
    d = _wide_survey(4)
    assert classify_query_shape(d) == "breadth_first"
    r = shape_reason(d)
    assert "K=4 " in r
    assert "deferred" not in r


def test_fanout_coverage_is_machine_readable():
    cov = fanout_coverage(_wide_survey(25))
    assert cov == {"shape": "breadth_first", "arrangement": "parallel",
                   "n_subq": 25, "cap": R.LOCI_MAX, "k": R.LOCI_MAX,
                   "deferred": 25 - R.LOCI_MAX}


def test_fanout_coverage_defers_nothing_for_non_breadth_shapes():
    # depth-first: 2-4 sequential perspectives on the ONE locus — k is chosen at
    # dispatch, and nothing is dropped because there is only one locus.
    deep = _decomp(sub_questions=["what caused the 2008 financial crisis"],
                   entities=["2008 financial crisis"],
                   response_format="argumentative",
                   contradiction_terms=["versus"], modality="deep",
                   domains=["econ"])
    cov = fanout_coverage(deep)
    assert cov["shape"] == "depth_first" and cov["k"] is None
    assert cov["deferred"] == 0

    single = _decomp(sub_questions=["what is the population of Tokyo"],
                     entities=["Tokyo"], response_format="short", domains=["geo"])
    cov = fanout_coverage(single)
    assert cov["shape"] == "straightforward" and cov["k"] == 1
    assert cov["deferred"] == 0


def test_skill_bodies_agree_with_the_loci_cap_constant():
    """The skills state the cap in prose; prose and constant must not drift.

    They previously drifted in the other direction (constant 20, prose 6). Both
    files now name LOCI_MAX and quote its current value — if LOCI_MAX changes
    and the prose does not, this fails.
    """
    for name in ("bad-research-4-loci-analysis.md",
                 "bad-research-5-depth-investigation.md"):
        body = (SKILLS_DIR / name).read_text()
        assert "LOCI_MAX" in body, name
        assert str(R.LOCI_MAX) in body, name
        # no bare "capped at <old number>" left behind
        assert f"capped at {R.SUBAGENT_FANOUT_MAX}" not in body, name


# ── CRITICAL: query_shape must NOT change classify_route's output ──────────────
# Re-run every existing test_router.py fixture through classify_route and assert
# the route is what it always was. The shape field ADDS fan-out arrangement; it
# must never shift the agentic-fast/light/full decision the golden corpus asserts.

def test_route_unchanged_trivial_single_domain():
    d = _decomp(sub_questions=["what is the capital of France"], response_format="short")
    assert classify_route(d) == "fast"
    # adding shape classification on the same decomp does not move the route
    _ = classify_query_shape(d)
    assert classify_route(d) == "fast"


def test_route_unchanged_structured_midsize():
    d = _decomp(sub_questions=["q1", "q2", "q3", "q4"], response_format="structured")
    assert classify_route(d) == "fast"
    _ = classify_query_shape(d)
    assert classify_route(d) == "fast"


def test_route_unchanged_contested_full():
    d = _decomp(sub_questions=[f"q{i}" for i in range(8)],
                response_format="argumentative", contradiction_terms=["versus"])
    assert classify_route(d) == "full"
    _ = classify_query_shape(d)
    assert classify_route(d) == "full"


def test_route_unchanged_multi_domain_full():
    d = _decomp(sub_questions=["q1", "q2"], response_format="structured",
                domains=["bio", "finance", "law"])
    assert classify_route(d) == "full"
    _ = classify_query_shape(d)
    assert classify_route(d) == "full"


def test_route_unchanged_time_periods_full():
    d = _decomp(sub_questions=["q1"], response_format="short",
                time_periods=[{"period": "Q3 2024"}])
    assert classify_route(d) == "full"
    _ = classify_query_shape(d)
    assert classify_route(d) == "full"


def test_bare_publication_year_time_period_does_not_force_full():
    # Over-escalation fix: a bare publication year (a paper's year) in time_periods
    # must NOT escalate a trivial lookup to the full ~2.5h pipeline. No other full
    # trigger is present, so the route must be fast.
    d = _decomp(sub_questions=["when was the transformer paper published"],
                response_format="short", domains=["ai"], time_periods=["2017"])
    assert classify_route(d) == "fast"
    # the dict form explicitly typed as a publication year is likewise exempt
    d2 = _decomp(sub_questions=["q1"], response_format="short", domains=["ai"],
                 time_periods=[{"period": "2017", "type": "publication-year"}])
    assert classify_route(d2) == "fast"


def test_period_pinned_time_periods_still_force_full():
    # Fiscal/regulatory/event windows and multi-year ranges remain HARD full triggers
    # (Lens-D period-pinned primaries) — only a bare publication year is exempted.
    for tp in (
        [{"period": "Q3 2024", "type": "fiscal-quarter"}],
        [{"period": "Q3 2024"}],   # untyped quarter (test_route_unchanged parity)
        ["1993-2023"],             # multi-year range (golden 06_recency_temporal parity)
        [{"period": "FY 2023", "type": "fiscal-year"}],
        [{"period": "March 2024", "type": "event-anchored"}],
    ):
        d = _decomp(sub_questions=["q1"], response_format="short", domains=["fin"],
                    time_periods=tp)
        assert classify_route(d) == "full", tp


def test_route_unchanged_broad_survey_light():
    # the B-5 modality down-route must still hold with shape classification present
    d = _decomp(
        sub_questions=[f"best tech for use-case {i}" for i in range(17)],
        entities=[], response_format="structured",
        contradiction_terms=[], domains=["tech"], modality="survey",
    )
    assert classify_route(d) == "fast"
    _ = classify_query_shape(d)
    assert classify_route(d) == "fast"


# ── skill-prose: the three shapes + their fan-out arrangement ──────────────────

def test_decompose_skill_emits_query_shape_with_verbatim_labels():
    body = (SKILLS_DIR / "bad-research-1-decompose.md").read_text()
    low = body.lower()
    assert "query_shape" in body
    # the three verbatim Claude labels
    for label in ("depth-first", "breadth-first", "straightforward"):
        assert label in low
    # the verbatim Claude examples (research_lead_agent.md:12-29)
    assert "2008 financial crisis" in body  # depth-first example
    assert "nordic" in low  # breadth-first example
    assert "tokyo" in low  # straightforward example


def test_router_skill_classifies_shape_orthogonal_to_route():
    body = (SKILLS_DIR / "bad-research-query-router.md").read_text()
    low = body.lower()
    assert "query_shape" in body
    # orthogonal to the route — must say so, must not change the route
    assert "orthogonal" in low or "does not change the route" in low \
        or "not change the route" in low or "adds" in low
    # the three shapes named
    for label in ("depth_first", "breadth_first", "straightforward"):
        assert label in body


def test_loci_skill_branches_fanout_by_shape():
    body = (SKILLS_DIR / "bad-research-4-loci-analysis.md").read_text()
    low = body.lower()
    assert "query_shape" in body
    assert "breadth_first" in body and "depth_first" in body
    # breadth → parallel, importance-ordered; depth → sequential
    assert "parallel" in low and "sequential" in low
    assert "importance" in low


def test_depth_skill_branches_sequential_vs_parallel_by_shape():
    body = (SKILLS_DIR / "bad-research-5-depth-investigation.md").read_text()
    low = body.lower()
    assert "query_shape" in body
    assert "depth_first" in body and "breadth_first" in body
    # depth-first runs 2-4 sequential perspectives, each reads the prior's position
    assert "sequential" in low
    assert "prior" in low or "previous" in low or "preceding" in low
    # straightforward → single investigator
    assert "straightforward" in body
    assert "single" in low
