"""A run that works in ROUNDS sets its own floor and patience, and they persist.

The per-retrieval defaults (floor 5, patience 2) are right for one reasoner chaining
queries. A round-based run observes once per round -- several readers, pooled -- where a
floor of 5 rounds is far past what a real question needs and one quiet round is already
the saturation signal (Wohlin ends a snowballing loop on the first round with nothing new).
Without a persisted rule the skill would state one stop and the code would compute another,
which is the exact defect a Reckon found here once already: a rule the skill states and the
code it names does not enforce is worse than an unstated one.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from bad_research.frontier import MIN_RETRIEVALS, QUIET_PATIENCE, FrontierState

BAD = str(Path(__file__).resolve().parents[2] / ".venv" / "bin" / "bad")


def _observe(p: Path, *args: str) -> dict:
    r = subprocess.run([BAD, "frontier-observe", "--state", str(p), *args, "--json"],
                       capture_output=True, text=True, check=False)
    assert r.returncode == 0, r.stdout + r.stderr
    return json.loads(r.stdout)


def test_defaults_are_unchanged_for_a_single_reasoner():
    st = FrontierState()
    assert (st.min_steps, st.patience) == (MIN_RETRIEVALS, QUIET_PATIENCE)


def test_a_standard_run_stops_after_its_floor_and_one_quiet_round(tmp_path: Path):
    p = tmp_path / "s.json"
    out = _observe(p, "--floor", "2", "--patience", "1",
                   "--domains", "a.com,b.com,c.com", "--entities", "Wohlin,snowballing")
    assert out["should_stop"] is False, "the broad round can never be the stop"
    out = _observe(p, "--domains", "a.com", "--entities", "")   # round 2: nothing new
    assert out["floor"] == 2 and out["patience"] == 1, "the rule must persist without re-passing it"
    assert out["should_stop"] is True


def test_an_open_question_still_holds_a_round_run_open(tmp_path: Path):
    p = tmp_path / "s.json"
    _observe(p, "--floor", "2", "--patience", "1", "--promise", "q1",
             "--domains", "a.com,b.com", "--entities", "X")
    out = _observe(p, "--domains", "a.com")
    assert out["should_stop"] is False and out["residual"] == ["q1"]


def test_the_floor_is_not_satisfied_by_quiet_rounds_alone(tmp_path: Path):
    p = tmp_path / "s.json"
    _observe(p, "--floor", "3", "--patience", "1", "--domains", "a.com,b.com", "--entities", "X")
    out = _observe(p, "--domains", "a.com")                     # quiet, but only round 2 of 3
    assert out["should_stop"] is False
    out = _observe(p, "--domains", "a.com")                     # round 3, still quiet
    assert out["should_stop"] is True


def test_the_rule_survives_save_and_load(tmp_path: Path):
    p = tmp_path / "s.json"
    st = FrontierState()
    st.set_rule(floor=3, patience=1)
    st.save(p)
    back = FrontierState.load(p)
    assert (back.min_steps, back.patience) == (3, 1)


@pytest.mark.parametrize("flag", ["--floor", "--patience"])
@pytest.mark.parametrize("value", ["0", "-1"])
def test_a_rule_that_could_stop_before_reading_is_refused(tmp_path: Path, flag: str, value: str):
    """A floor or patience below 1 is a stop that can fire before anything was read.

    Zero is refused too, not silently ignored: a first version defaulted the option to 0
    and read 0 as "not given", so an explicit `--floor 0` exited clean with the default
    kept -- the caller believed it had set a rule that never took effect.
    """
    p = tmp_path / "s.json"
    r = subprocess.run([BAD, "frontier-observe", "--state", str(p), flag, value, "--domains", "a.com"],
                       capture_output=True, text=True, check=False)
    assert r.returncode == 2, r.stdout + r.stderr
    assert not p.exists(), "a refused rule must not write state"
    with pytest.raises(ValueError):
        FrontierState().set_rule(**{flag.strip("-"): int(value)})


def test_a_state_file_from_before_the_rule_loads_with_the_defaults(tmp_path: Path):
    """Runs started before --floor/--patience existed must keep the per-retrieval rule."""
    p = tmp_path / "old.json"
    p.write_text(json.dumps({"items": [], "steps": 3, "quiet_streak": 1}), encoding="utf-8")
    st = FrontierState.load(p)
    assert (st.min_steps, st.patience) == (MIN_RETRIEVALS, QUIET_PATIENCE)


def test_abandonments_ride_on_the_rounds_one_observe(tmp_path: Path):
    """A bookkeeping call must not be counted as a round.

    With patience 1, a second observe made only to abandon a question came back
    should_stop=true — a round that never happened, counted as the quiet round. The fix
    is that every abandonment travels on the round's single call.
    """
    p = tmp_path / "s.json"
    _observe(p, "--floor", "2", "--patience", "1", "--promise", "Q1,Q2,Q3",
             "--domains", "a.com,b.com", "--entities", "X")
    out = _observe(p, "--domains", "c.com,d.com", "--entities", "Y", "--close", "Q1",
                   "--abandon", "Q2=no primary exists", "--abandon", "Q3=out of scope")
    assert out["step"] == 2 and out["residual"] == []
    assert set(out["abandoned"]) == {"Q2", "Q3"}
