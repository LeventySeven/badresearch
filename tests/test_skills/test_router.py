from bad_research.skills import routing_constants as R  # noqa: N812
from bad_research.skills.router import classify_route, route_reason


def _decomp(**kw):
    base = dict(sub_questions=["q1"], entities=[], time_periods=[],
                response_format="short", contradiction_terms=[], domains=["tech"])
    base.update(kw)
    return base


def test_constants_match_interfaces():
    # Fast-route loop bounds now live under FAST_* (see test_router_effort.py for
    # the full evidence-anchored set); the old agentic-fast loop names were retired.
    assert R.SUBAGENT_FANOUT_DEFAULT == 3 and R.SUBAGENT_FANOUT_MAX == 20
    assert R.CLARIFY_MAX_QUESTIONS == 3
    assert R.READ_TOP_K_CEILING == 80
    assert R.ROUTER_LIGHT_MAX_ATOMIC == 6


def test_trivial_single_domain_routes_fast():
    d = _decomp(sub_questions=["what is the capital of France"], response_format="short")
    assert classify_route(d) == "fast"


def test_two_atomic_no_tension_routes_fast():
    d = _decomp(sub_questions=["q1", "q2"], response_format="short")
    assert classify_route(d) == "fast"


def test_structured_midsize_routes_fast():
    d = _decomp(sub_questions=["q1", "q2", "q3", "q4"], response_format="structured")
    assert classify_route(d) == "fast"


def test_time_periods_force_full():
    d = _decomp(sub_questions=["q1"], response_format="short",
                time_periods=[{"period": "Q3 2024"}])
    assert classify_route(d) == "full"


def test_contested_argumentative_routes_full():
    d = _decomp(sub_questions=[f"q{i}" for i in range(8)],
                response_format="argumentative", contradiction_terms=["versus"])
    assert classify_route(d) == "full"


def test_multi_domain_routes_full():
    d = _decomp(sub_questions=["q1", "q2"], response_format="structured",
                domains=["bio", "finance", "law"])
    assert classify_route(d) == "full"


def test_short_with_three_atomic_routes_fast():
    # 3 atomic items, short format, single domain → not full → fast
    d = _decomp(sub_questions=["q1", "q2", "q3"], response_format="short")
    assert classify_route(d) == "fast"


def test_entities_count_toward_atomic():
    # 2 sub_questions + 1 entity = 3 atomic → fast
    d = _decomp(sub_questions=["q1", "q2"], entities=["X"], response_format="short")
    assert classify_route(d) == "fast"


def test_route_reason_is_nonempty_string():
    assert isinstance(route_reason(_decomp()), str)
    assert route_reason(_decomp()) != ""


def test_route_reason_mentions_full_trigger():
    d = _decomp(time_periods=[{"period": "Q3 2024"}])
    assert "time_period" in route_reason(d).lower() or "full" in route_reason(d).lower()


def test_classify_route_only_emits_fast_or_full():
    # The pipeline is a clean 2-route system (fast / full) since the `ultrafast`
    # route was folded away 2026-07-06 — classify_route must only ever emit those two.
    from typing import get_args

    from bad_research.skills.router import Route

    assert set(get_args(Route)) == {"fast", "full"}
    cases = [
        _decomp(sub_questions=["what is the capital of France"], response_format="short"),
        _decomp(sub_questions=["q1", "q2", "q3"], domains=["a", "b", "c"],
                response_format="argumentative", contradiction_terms=["x"]),
    ]
    for d in cases:
        assert classify_route(d) in ("fast", "full")
