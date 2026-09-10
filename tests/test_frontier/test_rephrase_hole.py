"""Naming a frontier item is necessary and was being treated as sufficient.

Measured by an unbiased Reckon: repeat your first query verbatim, append one frontier
token, and the gate allows it — naming entities that were frontier items only because
the model had typed them into `--entities` itself. The gate was checking the model's
output against the model's output.

SKILL.md always stated the conjunction: "A query names a frontier item AND is one
sentence saying what evidence you want." Only the first half executed.
"""
from __future__ import annotations

from bad_research.frontier import FrontierState, is_rephrase_of

Q1 = "Is Postgres faster than MySQL for OLTP"


def _run() -> FrontierState:
    st = FrontierState()
    st.gate_and_log(Q1)                       # first query is exempt
    st.observe_round({"a.com"}, {"Postgres", "MySQL", "pgbench"})
    return st


def test_a_repeat_with_a_token_bolted_on_is_refused():
    allowed, named = _run().gate_and_log(Q1 + " workloads")
    assert not allowed and named == []


def test_a_genuinely_new_question_still_passes():
    """The gate must not become a rubber refusal — that is the opposite failure."""
    allowed, named = _run().gate_and_log("what pgbench scale factor did they use")
    assert allowed and "pgbench" in named


def test_the_log_records_which_query_it_was_a_rephrase_of():
    """A refusal you cannot audit is indistinguishable from a broken gate."""
    st = _run()
    st.gate_and_log(Q1 + " workloads")
    assert st.log[-1].get("rephrase_of") == Q1


def test_a_short_prior_query_cannot_swallow_everything():
    """Containment on a 2-word prior would refuse most legitimate follow-ups."""
    st = FrontierState()
    st.gate_and_log("Postgres OLTP")
    st.observe_round({"a.com"}, {"pgbench"})
    allowed, _ = st.gate_and_log("what pgbench numbers did the Postgres OLTP run report")
    assert allowed, "a 2-word prior must not make every later query a rephrase"


def test_containment_is_contiguous_not_bag_of_words():
    """Sharing words is not repeating a question."""
    assert not is_rephrase_of("why is MySQL slower than Postgres on writes",
                              "Is Postgres faster than MySQL for OLTP")
