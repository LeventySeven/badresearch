"""S2-4: the stop decision must be COMPUTED by the harness, not self-reported.

Every published stopping rule this project surveyed is either absent, a constant a
human picked, or unreachable — FLARE ships `max_iteration: int = 10000,  # TODO:
too high?`, and cognee's convergence check dedupes by object identity so it can
never fire. The one thing they share is that nothing measures whether the loop is
still learning.

So the counters have to run BEFORE the prompt is built and be visible in the run
log, because the alternative is asking the model whether it is done — and the
measured failure is precisely a model that keeps going after the answer is in hand.
A model that wants to keep searching is not a reliable witness to diminishing returns.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from bad_research.frontier import FrontierState

BAD = str(Path(__file__).resolve().parents[2] / ".venv" / "bin" / "bad")


def test_observing_a_round_records_the_deltas(tmp_path: Path):
    st = FrontierState()
    st.observe_round(domains={"a.com", "b.com"}, entities={"H200"})
    assert st.last_new_domains == 2 and st.last_new_entities == 1
    assert st.should_stop() is False, "step 1 must never stop"


def test_a_round_that_adds_nothing_new_says_stop(tmp_path: Path):
    st = FrontierState()
    st.observe_round(domains={"a.com", "b.com"}, entities={"H200"})
    st.observe_round(domains={"a.com"}, entities={"H200"})
    assert st.last_new_domains == 0 and st.last_new_entities == 0
    assert st.should_stop() is True


def test_a_round_still_finding_new_domains_keeps_going(tmp_path: Path):
    st = FrontierState()
    st.observe_round(domains={"a.com"}, entities=set())
    st.observe_round(domains={"b.com", "c.com"}, entities=set())
    assert st.should_stop() is False


def test_the_counters_survive_a_save_load_round_trip(tmp_path: Path):
    p = tmp_path / "s.json"
    st = FrontierState()
    st.observe_round(domains={"a.com"}, entities={"X"})
    st.save(p)
    back = FrontierState.load(p)
    assert back.steps == 1 and back.seen_domains == {"a.com"}
    assert back.rounds and back.rounds[-1]["new_domains"] == 1


def test_the_cli_reports_the_computed_stop_signal(tmp_path: Path):
    p = tmp_path / "s.json"
    FrontierState().save(p)
    r = subprocess.run(
        [BAD, "frontier-observe", "--state", str(p),
         "--domains", "a.com,b.com", "--entities", "H200", "--json"],
        capture_output=True, text=True, check=False,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    out = json.loads(r.stdout)
    assert out["new_domains"] == 2 and out["should_stop"] is False

    r2 = subprocess.run(
        [BAD, "frontier-observe", "--state", str(p),
         "--domains", "a.com", "--entities", "H200", "--json"],
        capture_output=True, text=True, check=False,
    )
    out2 = json.loads(r2.stdout)
    assert out2["new_domains"] == 0 and out2["new_entities"] == 0
    assert out2["should_stop"] is True, "a round adding nothing new must say stop"


def test_stop_counters_has_a_production_caller():
    root = Path(__file__).resolve().parents[2] / "src"
    hits = subprocess.run(["grep", "-rn", "StopCounters", str(root)],
                          capture_output=True, text=True, check=False).stdout.splitlines()
    callers = [h for h in hits if "class StopCounters" not in h and "__pycache__" not in h]
    assert callers, "StopCounters is defined but called from nowhere in src/ — it does not run"
