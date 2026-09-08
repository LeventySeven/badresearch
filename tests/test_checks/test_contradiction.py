"""Mechanical contradiction pairing.

Two accounts of the same fact that disagree are a discrepancy in the record,
not a stale value to overwrite -- and a disagreement on a load-bearing number
is the most valuable thing a research run finds.
"""

from __future__ import annotations

import json
from pathlib import Path

from bad_research.checks.contradiction import (
    MAX_OPEN_CONTRADICTIONS,
    Claim,
    find_contradictions,
)


# ── the five behaviours the pairing exists for ───────────────────────────────
def test_same_subject_different_number_is_a_contradiction():
    a = Claim(subject="h200 rental", value="2.49", unit="usd/hr", source="s1")
    b = Claim(subject="h200 rental", value="6.31", unit="usd/hr", source="s2")
    c = find_contradictions([a, b])
    assert len(c) == 1 and {c[0].left.source, c[0].right.source} == {"s1", "s2"}


def test_same_number_is_not_a_contradiction():
    a = Claim(subject="h200 rental", value="2.49", unit="usd/hr", source="s1")
    b = Claim(subject="h200 rental", value="2.49", unit="usd/hr", source="s2")
    assert find_contradictions([a, b]) == []


def test_different_units_are_not_compared():
    # $/hr vs $/month is not a disagreement, it is a different measurement
    a = Claim(subject="h200 rental", value="2.49", unit="usd/hr", source="s1")
    b = Claim(subject="h200 rental", value="1800", unit="usd/month", source="s2")
    assert find_contradictions([a, b]) == []


def test_same_source_does_not_contradict_itself():
    a = Claim(subject="x", value="1", unit="u", source="s1")
    b = Claim(subject="x", value="2", unit="u", source="s1")
    assert find_contradictions([a, b]) == []


def test_tolerance_absorbs_rounding():
    a = Claim(subject="x", value="2.490", unit="u", source="s1")
    b = Claim(subject="x", value="2.49", unit="u", source="s2")
    assert find_contradictions([a, b]) == []


# ── what a finding carries ───────────────────────────────────────────────────
def test_numeric_finding_carries_kind_and_relative_delta():
    a = Claim(subject="h200 rental", value="2.00", unit="usd/hr", source="s1")
    b = Claim(subject="h200 rental", value="4.00", unit="usd/hr", source="s2")
    c = find_contradictions([a, b])[0]
    assert c.kind == "numeric"
    assert c.delta == 0.5  # |2-4| / max(|2|,|4|)
    assert c.to_dict()["kind"] == "numeric"
    assert c.to_dict()["left"]["source"] == "s1"


def test_tolerance_is_configurable():
    a = Claim(subject="x", value="100", unit="u", source="s1")
    b = Claim(subject="x", value="105", unit="u", source="s2")
    assert find_contradictions([a, b]) != []              # 4.8% > 1% default
    assert find_contradictions([a, b], rel_tolerance=0.10) == []


# ── normalisation ────────────────────────────────────────────────────────────
def test_subject_and_unit_normalise_by_casefold_and_whitespace():
    a = Claim(subject="H200  Rental", value="2.49", unit="USD/hr", source="s1")
    b = Claim(subject="h200 rental", value="6.31", unit="usd/hr", source="s2")
    assert len(find_contradictions([a, b])) == 1


def test_currency_and_thousands_separators_parse_as_numbers():
    a = Claim(subject="fleet", value="$1,800.00", unit="usd", source="s1")
    b = Claim(subject="fleet", value="1800", unit="usd", source="s2")
    assert find_contradictions([a, b]) == []


def test_two_zeroes_do_not_divide_by_zero():
    a = Claim(subject="x", value="0", unit="u", source="s1")
    b = Claim(subject="x", value="0.0", unit="u", source="s2")
    assert find_contradictions([a, b]) == []


# ── non-numeric values ───────────────────────────────────────────────────────
def test_non_numeric_disagreement_is_a_stance_contradiction():
    a = Claim(subject="export licence", value="required", unit="", source="s1")
    b = Claim(subject="export licence", value="not required", unit="", source="s2")
    c = find_contradictions([a, b])
    assert len(c) == 1 and c[0].kind == "stance" and c[0].delta == 1.0


def test_stance_values_that_differ_only_in_case_agree():
    a = Claim(subject="export licence", value="Required", unit="", source="s1")
    b = Claim(subject="export licence", value="required ", unit="", source="s2")
    assert find_contradictions([a, b]) == []


# ── the manufactured-contradiction guard ─────────────────────────────────────
def _spread(n: int) -> list[Claim]:
    """n disagreeing pairs, each on its own subject, with increasing delta."""
    out: list[Claim] = []
    for i in range(n):
        out.append(Claim(subject=f"s{i}", value="100", unit="u", source="a"))
        # +5% per step: every pair clears the 1% default tolerance outright, so
        # the cap is what trims the list, not the tolerance.
        out.append(Claim(subject=f"s{i}", value=str(100 + 5 * (i + 1)), unit="u", source="b"))
    return out


def test_the_cap_is_enforced_and_ranked_by_delta_descending():
    got = find_contradictions(_spread(MAX_OPEN_CONTRADICTIONS + 5))
    assert MAX_OPEN_CONTRADICTIONS == 12
    assert len(got) == MAX_OPEN_CONTRADICTIONS
    assert [c.delta for c in got] == sorted((c.delta for c in got), reverse=True)


def test_the_cap_is_never_silent():
    got = find_contradictions(_spread(MAX_OPEN_CONTRADICTIONS + 5))
    assert got.suppressed == 5
    assert got.total_found == MAX_OPEN_CONTRADICTIONS + 5


def test_an_uncapped_result_reports_zero_suppressed():
    a = Claim(subject="x", value="1", unit="u", source="s1")
    b = Claim(subject="x", value="2", unit="u", source="s2")
    got = find_contradictions([a, b])
    assert got.suppressed == 0 and got.total_found == 1
    assert find_contradictions([]).suppressed == 0


# ── pairing hygiene ──────────────────────────────────────────────────────────
def test_three_sources_produce_every_disagreeing_pair():
    claims = [
        Claim(subject="x", value="1", unit="u", source="s1"),
        Claim(subject="x", value="2", unit="u", source="s2"),
        Claim(subject="x", value="3", unit="u", source="s3"),
    ]
    assert len(find_contradictions(claims)) == 3


def test_ordering_is_deterministic_across_equal_deltas():
    claims = [
        Claim(subject="b", value="1", unit="u", source="s1"),
        Claim(subject="b", value="2", unit="u", source="s2"),
        Claim(subject="a", value="1", unit="u", source="s1"),
        Claim(subject="a", value="2", unit="u", source="s2"),
    ]
    first = [(c.left.subject, c.left.source) for c in find_contradictions(claims)]
    second = [(c.left.subject, c.left.source) for c in find_contradictions(claims)]
    assert first == second == [("a", "s1"), ("b", "s1")]


def test_a_lone_claim_contradicts_nothing():
    assert find_contradictions([Claim(subject="x", value="1", unit="u", source="s1")]) == []


# ── the planted-defect fixture (a check that can only pass is not a check) ────
def _load(name: str) -> list[Claim]:
    path = Path(__file__).parent / "fixtures" / name / "claims.json"
    return [Claim(**record) for record in json.loads(path.read_text())]


def test_planted_fixture_surfaces_both_disagreements():
    got = find_contradictions(_load("planted"))
    assert [c.kind for c in got] == ["stance", "numeric"]
    assert {c.left.source for c in got} == {"vendor-faq", "broker-listing"}
    assert got.suppressed == 0


def test_clean_fixture_is_silent():
    # rounding, a currency symbol and a genuinely different unit -- no disagreement
    assert find_contradictions(_load("clean")) == []


def test_a_quantity_is_never_compared_against_prose():
    # not comparable, for the same reason two different units are not
    a = Claim(subject="x", value="2.49", unit="u", source="s1")
    b = Claim(subject="x", value="roughly two fifty", unit="u", source="s2")
    assert find_contradictions([a, b]) == []
