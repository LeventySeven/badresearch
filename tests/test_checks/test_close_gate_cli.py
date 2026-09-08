"""S3-4: the gate has to be a command a person can run, not a function in a library.

A rule that only unit tests call is a rule that does not run. This drives the
same path a user drives: raw claims in, a verdict and an exit code out.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

BAD = str(Path(__file__).resolve().parents[2] / ".venv" / "bin" / "bad")

CLAIMS = [
    {"subject": "H100 on-demand", "value": "2.49", "unit": "$/hr",
     "source": "vendor-a.com/pricing", "as_of": "2026-08-01"},
    {"subject": "H100 on-demand", "value": "3.35", "unit": "$/hr",
     "source": "vendor-b.com/pricing", "as_of": "2026-09-02"},
]

BOTH_SIDES = (
    "The H100 on-demand rate is not one number: vendor-a.com/pricing lists "
    "$2.49/hr as of 2026-08-01 and vendor-b.com/pricing lists $3.35/hr as of "
    "2026-09-02. I rank the later capture higher."
)


@pytest.fixture
def run(tmp_path: Path):
    (tmp_path / "claims.json").write_text(json.dumps(CLAIMS))

    def _run(answer: str, dispositions: list[dict] | None = None):
        (tmp_path / "answer.md").write_text(answer)
        argv = [BAD, "close-gate", "--claims", str(tmp_path / "claims.json"),
                "--answer", str(tmp_path / "answer.md"), "--json"]
        if dispositions is not None:
            (tmp_path / "d.json").write_text(json.dumps(dispositions))
            argv += ["--dispositions", str(tmp_path / "d.json")]
        p = subprocess.run(argv, capture_output=True, text=True, check=False)
        return p.returncode, json.loads(p.stdout)

    return _run


def test_exits_nonzero_while_the_disagreement_is_undisposed(run):
    rc, out = run(BOTH_SIDES)
    assert rc == 1
    assert out["can_close"] is False and out["found"] == 1
    assert len(out["load_bearing"]) == 1


def test_exits_zero_once_disposed_with_both_sides_intact(run):
    rc, out = run(BOTH_SIDES)
    cid = out["blockers"][0]["contradiction_id"]
    rc, out = run(BOTH_SIDES, [{"contradiction_id": cid, "kind": "ranked",
                                "because": "later capture"}])
    assert rc == 0, out["blockers"]
    assert out["can_close"] is True


def test_a_draft_that_never_raises_the_subject_cannot_be_held_open(run):
    """Anti-manufacture, at the CLI: a cosmetic conflict blocks nothing."""
    rc, out = run("This answer is about storage egress, not GPUs.")
    assert rc == 0
    assert out["cosmetic"] and not out["blockers"]
