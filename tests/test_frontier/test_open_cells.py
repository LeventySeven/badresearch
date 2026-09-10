"""The stop signal must see what the answer still OWES, not only what arrived.

`frontier-observe` counts new domains and new entities — two scalars. A round can
add three entities and close none of the cells the answer promised to fill, and
both counters go up while the answer has not advanced. The skill has named this
from the start (an unfilled cell in the shape you promised is frontier item #2);
only the instrument was blind to it.

The corpus supplies the shape. The most complete accretion mechanism found keeps
a per-instance OUTCOME VECTOR — which specific cases passed and failed — rather
than a scalar score, precisely because "target what the last attempt failed at"
is not computable from a number. Selection then aims one candidate at the
parent's residual failures.

So: a run stops when nothing new arrived AND nothing is still owed. Either alone
is a half-signal, and the scalar half is the one that reads as progress.
"""
from __future__ import annotations

from bad_research.frontier import MIN_RETRIEVALS, FrontierState


def test_a_round_that_adds_entities_but_closes_no_promised_cell_does_not_stop():
    st = FrontierState(open_cells={"price", "latency", "licence"})
    st.observe_round({"a.com"}, {"H200"})
    st.observe_round(set(), set())          # scalar-quiet round
    assert st.should_stop() is False, (
        "scalars went quiet but three promised cells are still open — that is not done"
    )


def test_stopping_needs_both_halves():
    st = FrontierState(open_cells={"price"})
    st.observe_round({"a.com"}, {"H200"})
    st.close_cell("price")
    st.observe_round(set(), set())
    _past_the_floor(st)
    st.observe_round(domains=set(), entities=set())   # quiet 1 — noise
    st.observe_round(domains=set(), entities=set())   # quiet 2 — the signal
    assert st.should_stop() is True, "nothing new arrived and nothing is owed"


def test_open_cells_alone_do_not_hold_a_run_open_forever():
    """A cell nothing can fill must not become an infinite loop. It is reportable
    as unestablished — the skill's own 'what I could not establish' section — so
    the run may stop once it is explicitly abandoned with a reason."""
    st = FrontierState(open_cells={"vendor's internal margin"})
    st.observe_round({"a.com"}, {"H200"})
    st.abandon_cell("vendor's internal margin", "not published anywhere; asked and refused")
    st.observe_round(set(), set())
    _past_the_floor(st)
    st.observe_round(domains=set(), entities=set())   # quiet 1 — noise
    st.observe_round(domains=set(), entities=set())   # quiet 2 — the signal
    assert st.should_stop() is True
    assert st.abandoned["vendor's internal margin"].startswith("not published")


def test_the_residual_is_reportable_not_just_countable():
    """A scalar says how many remain; the answer needs to say WHICH."""
    st = FrontierState(open_cells={"price", "latency"})
    st.close_cell("price")
    assert st.residual() == ["latency"]


def test_closing_a_cell_that_was_never_promised_is_refused():
    """Otherwise a run can empty its own obligations by inventing closures."""
    st = FrontierState(open_cells={"price"})
    try:
        st.close_cell("something nobody asked for")
    except KeyError as e:
        assert "never promised" in str(e)
    else:
        raise AssertionError("closing an unpromised cell must be refused")


def test_state_round_trips_with_cells(tmp_path):
    p = tmp_path / "s.json"
    st = FrontierState(open_cells={"price", "latency"})
    st.close_cell("price"); st.abandon_cell("latency", "vendor refused")
    st.save(p)
    back = FrontierState.load(p)
    assert back.residual() == [] and back.abandoned == {"latency": "vendor refused"}
    assert back.closed_cells == {"price"}


# The floor and the patience, added after the code and the prose were found to disagree
#
# These tests were written against the CODE, which stopped after two rounds and one quiet
# one. `SKILL.md` has always said something stricter: "a run answered on fewer than ~5
# distinct retrievals was answered from what you had, and one quiet round is noise where
# two consecutive is the signal." A Reckon drove the two CLI commands and got STOP at two
# retrievals, so the rule the reader was given was not the rule the counter enforced.
#
# The spec wins: the skill is the artifact the owner specified, the code is its
# implementation. So these now assert the documented behaviour, and the helper below
# spends the floor explicitly rather than hiding it.


def _past_the_floor(st):
    """Advance the run past MIN_RETRIEVALS with productive rounds, then return it."""
    for i in range(MIN_RETRIEVALS):
        st.observe_round(domains={f"d{i}.com"}, entities={f"E{i}"})
    return st
