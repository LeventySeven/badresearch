"""Saturation stop (Task 3): retrieve_until_good halts fan-out when new results
stop adding distinct domains — Perplexity's evidenced coverage stop (PD:3849-3855),
a pure new-distinct-domain-ratio counter alongside (not replacing) the 0.70/<30%
quality gate."""

from __future__ import annotations

from bad_research.web.base import WebResult
from bad_research.web.search.base import KeylessSearchConfig
from bad_research.web.search.loop import retrieve_until_good


def _result(domain: str, i: int, score: float = 0.1) -> WebResult:
    r = WebResult(url=f"https://{domain}/{i}", title=f"{domain}-{i}", content="c")
    r.metadata["score"] = score
    return r


def test_loop_stops_when_new_domains_dry_up():
    # Scores are all 0.1 (< 0.70) so the QUALITY gate never fires — only saturation
    # can stop the loop before max_rounds(5). Distinct domains per round:
    #   r1: 5 fresh          -> new_ratio 1.0  (seed)            -> continue
    #   r2: 4 seen + 1 new   -> new_ratio 0.2  (== tau, NOT < )  -> continue
    #   r3: 5 already-seen   -> new_ratio 0.0  (< tau)           -> STOP
    rounds = [
        [_result("d1", 0), _result("d2", 0), _result("d3", 0), _result("d4", 0), _result("d5", 0)],
        [_result("d2", 1), _result("d3", 1), _result("d4", 1), _result("d5", 1), _result("d6", 0)],
        [_result("d1", 2), _result("d2", 2), _result("d3", 2), _result("d4", 2), _result("d5", 2)],
    ]
    calls = {"n": 0}

    def fan_out(queries):
        i = calls["n"]
        calls["n"] += 1
        return rounds[i]

    cfg = KeylessSearchConfig(sat_tau=0.20, max_rounds=5)
    trace: dict = {}
    out = retrieve_until_good(
        "q",
        cfg=cfg,
        expand=lambda q, **kw: ["q"],
        fan_out=fan_out,
        rerank=lambda question, pool: pool,
        trace=trace,
    )
    assert trace["stopped_reason"] == "saturation"
    assert trace["rounds_run"] == 3   # stopped by saturation, not max_rounds(5)
    assert calls["n"] == 3            # exactly 3 fan-out rounds ran (no wasted 4th/5th)
    assert out == []                  # nothing cleared 0.70 → best-effort empty


def test_round1_single_domain_is_not_saturated():
    # A single-domain first round seeds `seen` (new_ratio 1.0) and must NOT be
    # mistaken for saturation — at least one full round always runs.
    cfg = KeylessSearchConfig(sat_tau=0.20, max_rounds=1)
    trace: dict = {}
    out = retrieve_until_good(
        "q",
        cfg=cfg,
        expand=lambda q, **kw: ["q"],
        fan_out=lambda qs: [_result("only", 0, score=0.9)],  # clears 0.70
        rerank=lambda question, pool: pool,
        trace=trace,
    )
    assert trace["stopped_reason"] == "quality"  # returned via quality, not saturation
    assert len(out) == 1


def test_quality_gate_wins_over_saturation_same_round():
    # When a round is BOTH saturated (all seen domains) AND clears quality, the
    # quality gate returns first (checked before saturation) — no false stop.
    cfg = KeylessSearchConfig(sat_tau=0.20, max_rounds=3)
    calls = {"n": 0}

    def fan_out(queries):
        calls["n"] += 1
        # both rounds are all d1 (saturates in r2), but r2 clears quality (2/2)
        if calls["n"] == 1:
            return [_result("d1", 0, 0.1), _result("d1", 1, 0.1)]  # 0% clear → continue
        return [_result("d1", 2, 0.9), _result("d1", 3, 0.8)]      # 100% clear → quality

    trace: dict = {}
    out = retrieve_until_good(
        "q",
        cfg=cfg,
        expand=lambda q, **kw: ["q"],
        fan_out=fan_out,
        rerank=lambda question, pool: pool,
        trace=trace,
    )
    assert trace["stopped_reason"] == "quality"
    assert trace["rounds_run"] == 2
    assert len(out) == 2


def test_default_sat_tau_is_020():
    assert KeylessSearchConfig().sat_tau == 0.20
