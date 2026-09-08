from __future__ import annotations

from bad_research.frontier import Frontier, StopCounters, gate_query


def test_query_naming_no_frontier_item_is_refused():
    ok, named = gate_query("what is the price of an H100", Frontier(items={"H200", "MoE"}))
    assert ok is False and named == []


def test_query_naming_a_frontier_item_passes_and_reports_which():
    ok, named = gate_query("H200 memory bandwidth", Frontier(items={"H200", "MoE"}))
    assert ok is True and named == ["H200"]


def test_first_query_is_always_allowed():
    assert gate_query("anything", Frontier(items=set()), first=True)[0] is True


def test_counters_are_computed_not_reported():
    c = StopCounters()
    c.observe(domains={"a.com"}, entities={"X"})
    assert c.should_stop() is False           # step 1 never stops
    c.observe(domains={"a.com"}, entities=set())
    assert c.should_stop() is True            # 0 new domains, 0 new entities


def test_add_drops_empty_strings_and_close_removes_an_item():
    # Written after the implementation (these two methods are not driven by the
    # gate tests above); they lock the frontier's own bookkeeping.
    f = Frontier(items={"H200"})
    f.add({"MoE", ""})
    assert f.items == {"H200", "MoE"}
    f.close("H200")
    f.close("never-there")  # closing an unknown item is a no-op, not an error
    assert f.items == {"MoE"}


def test_multi_token_item_is_named():
    ok, named = gate_query("GB200 NVL72 power draw", Frontier(items={"GB200 NVL72"}))
    assert ok is True and named == ["GB200 NVL72"]


def test_quantity_with_currency_prefix_is_named():
    assert gate_query("is it $0.66 per token", Frontier(items={"$0.66"}))[0] is True


def test_trailing_punctuation_does_not_block_a_match():
    assert gate_query("compare price of the H200.", Frontier(items={"H200"}))[0] is True


def test_item_with_no_tokens_never_matches():
    # the empty set is a subset of everything — the `and it` guard stops it naming itself
    assert gate_query("anything at all", Frontier(items={"$$$"}))[0] is False


def test_partial_multi_token_match_is_refused():
    # naming only half a multi-token item is still a re-phrase
    assert gate_query("GB200 power draw", Frontier(items={"GB200 NVL72"}))[0] is False
