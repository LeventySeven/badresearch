"""S2-3 / S2-5: the frontier gate needs a production caller, and the run must log
which frontier item each query hit.

Until this existed, `gate_query` was reachable only from its own unit tests — the
owner's central thesis ("a researcher's second question is one he could not have
asked first") was implemented as a pure function nothing called. A rule nothing
calls is a rule that does not run.

The gate refuses a query that names no frontier item. That refusal has to be
enforced by something that executes: prose is worth ~7% on a post-trained model,
and the measured failure this guards against is an agent "repeatedly searching for
similar keywords despite retrieving relevant objects" — continuing after the answer
was already in hand.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from bad_research.frontier import FrontierState

BAD = str(Path(__file__).resolve().parents[2] / ".venv" / "bin" / "bad")


@pytest.fixture
def state_file(tmp_path: Path) -> Path:
    p = tmp_path / "frontier.json"
    FrontierState(items={"GB200 NVL72", "$0.66", "Adaptive-RAG"}).save(p)
    return p


def test_state_round_trips(tmp_path: Path):
    p = tmp_path / "s.json"
    FrontierState(items={"H200"}, seen_domains={"a.com"}).save(p)
    back = FrontierState.load(p)
    assert back.items == {"H200"}
    assert back.seen_domains == {"a.com"}


def test_first_query_is_allowed_and_logged(tmp_path: Path):
    p = tmp_path / "s.json"
    FrontierState(items=set()).save(p)
    st = FrontierState.load(p)
    allowed, named = st.gate_and_log("anything at all")
    assert allowed is True and named == []
    assert st.log[-1]["first"] is True


def test_a_query_naming_a_frontier_item_is_allowed_and_names_which(state_file: Path):
    st = FrontierState.load(state_file)
    st.gate_and_log("seed")                      # burn the first-query exemption
    allowed, named = st.gate_and_log("GB200 NVL72 power draw")
    assert allowed is True and named == ["GB200 NVL72"]
    assert st.log[-1]["named"] == ["GB200 NVL72"], "the run log must say WHICH item was hit"


def test_a_rephrase_is_refused(state_file: Path):
    st = FrontierState.load(state_file)
    st.gate_and_log("seed")
    allowed, named = st.gate_and_log("what is the price of an H100")
    assert allowed is False and named == []
    assert st.log[-1]["allowed"] is False


def test_cli_exits_nonzero_on_a_refused_query(state_file: Path):
    subprocess.run([BAD, "frontier-gate", "--state", str(state_file), "--query", "seed"], check=False)
    r = subprocess.run(
        [BAD, "frontier-gate", "--state", str(state_file), "--query", "unrelated rephrase", "--json"],
        capture_output=True, text=True, check=False,
    )
    assert r.returncode == 1, f"a re-phrase must be refused; got {r.returncode}\n{r.stdout}{r.stderr}"
    assert json.loads(r.stdout)["allowed"] is False


def test_cli_exits_zero_and_reports_the_item_when_the_query_names_one(state_file: Path):
    subprocess.run([BAD, "frontier-gate", "--state", str(state_file), "--query", "seed"], check=False)
    r = subprocess.run(
        [BAD, "frontier-gate", "--state", str(state_file), "--query", "Adaptive-RAG oracle router", "--json"],
        capture_output=True, text=True, check=False,
    )
    assert r.returncode == 0, f"{r.stdout}{r.stderr}"
    out = json.loads(r.stdout)
    assert out["allowed"] is True and out["named"] == ["Adaptive-RAG"]


def test_gate_query_has_a_production_caller():
    """The row's literal claim: something in src/ that is not a test calls it."""
    import subprocess as sp

    root = Path(__file__).resolve().parents[2] / "src"
    hits = sp.run(
        ["grep", "-rn", "gate_query", str(root)], capture_output=True, text=True, check=False
    ).stdout.splitlines()
    callers = [h for h in hits if "def gate_query" not in h and "__pycache__" not in h]
    assert callers, "gate_query is defined but called from nowhere in src/ — it does not run"
    assert sys.modules  # keep the import used
