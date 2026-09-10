"""The seam: what `frontier-observe` records must be nameable by `frontier-gate`.

Every unit test here passed while this was broken, because each half was tested
alone — `observe_round` against `seen_entities`, `gate_query` against a hand-built
`Frontier`. Nothing drove one into the other, so `items` was never written and the
frontier stayed empty for the life of a run.

A cold user found it in two commands. The failure mode is the dangerous kind: the
gate still REFUSED, so it looked like a working guard. A gate that refuses everything
and a gate that refuses correctly produce the same exit code.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from bad_research.frontier import FrontierState


def test_an_observed_entity_becomes_nameable(tmp_path):
    st = FrontierState()
    # Spend the first-query exemption first: the gate lets query #1 through naming
    # nothing, because there is nothing to have learned yet. A first version of this
    # test asserted on that exempt call and read `named == []` as the bug it was
    # hunting — the code was right and the test was standing one call too early.
    st.gate_and_log("what is Adaptive-RAG")
    st.observe_round({"arxiv.org"}, {"Adaptive-RAG", "HotpotQA"})
    allowed, named = st.gate_and_log("how does Adaptive-RAG do on HotpotQA")
    assert allowed, "an entity this run just recorded must satisfy the gate"
    assert set(named) >= {"Adaptive-RAG"}


def test_the_gate_still_refuses_a_rephrase(tmp_path):
    """The fix must not turn the gate into a rubber stamp."""
    st = FrontierState()
    st.observe_round({"arxiv.org"}, {"Adaptive-RAG", "HotpotQA"})
    st.gate_and_log("first")
    allowed, named = st.gate_and_log("tell me more about retrieval augmented generation")
    assert not allowed and not named


def _run(state: Path, *args):
    return subprocess.run([sys.executable, "-m", "bad_research", *args, "--state", str(state)],
                          capture_output=True, text=True)


def test_end_to_end_through_the_two_commands(tmp_path):
    """Driven the way a user drives it — the path no unit test covered."""
    s = tmp_path / "s.json"
    r = _run(s, "frontier-gate", "--query", "what is Adaptive-RAG", "--json")
    assert r.returncode == 0 and json.loads(r.stdout)["first"] is True

    r = _run(s, "frontier-observe", "--domains", "arxiv.org",
             "--entities", "Adaptive-RAG,HotpotQA", "--json")
    assert r.returncode == 0, r.stderr

    r = _run(s, "frontier-gate", "--query", "Adaptive-RAG on HotpotQA", "--json")
    assert r.returncode == 0, (
        "the second query named two entities the previous command recorded and was "
        f"still refused: {r.stdout}{r.stderr}"
    )
    assert json.loads(r.stdout)["frontier_size"] >= 2
