"""Every check command must actually RUN its --json path.

`--help` does not execute a command body, so a NameError inside one is invisible to a
smoke test that only asks for help. This exact defect shipped twice in one file:
`_json.dumps` where the module imports `json`, in a command whose `--help` was green
both times. The second occurrence was written the same day the first was recorded.

So this test invokes each command for real, with inputs it constructs, and asserts the
process did not crash. A non-zero exit is fine — several of these gates are SUPPOSED to
refuse. A traceback is not.
"""
from __future__ import annotations

import json
import subprocess
import sys

import pytest

REPORT = """# R

The gate refuses a query naming no frontier item (`src/bad_research/frontier.py:52`).

No source measures the false-negative rate of a source-quality filter directly.
"""


def _run(tmp_path, *args):
    report = tmp_path / "r.md"
    report.write_text(REPORT, encoding="utf-8")
    notes = tmp_path / "n.json"
    notes.write_text(json.dumps({"src-1": "a body that says something"}), encoding="utf-8")
    argv = [sys.executable, "-m", "bad_research", *args]
    argv = [a.replace("{report}", str(report)).replace("{notes}", str(notes)) for a in argv]
    return subprocess.run(argv, capture_output=True, text=True)


@pytest.mark.parametrize("args", [
    ("absence-gate", "--report", "{report}", "--json"),
    ("no-source-claim-gate", "--report", "{report}", "--notes", "{notes}", "--json"),
    ("quote-drift-gate", "--report", "{report}", "--note-bodies", "{notes}", "--json"),
    ("figure-support-gate", "--report", "{report}", "--note-bodies", "{notes}", "--json"),
    ("grounding-surface", "--report", "{report}", "--note-bodies", "{notes}", "--json"),
    ("uncited-gate", "--report", "{report}", "--vault-tag", "t", "--json"),
])
def test_json_path_executes_without_crashing(tmp_path, args):
    r = _run(tmp_path, *args)
    assert "Traceback" not in r.stderr, f"{args[0]} crashed:\n{r.stderr[-800:]}"
    assert "NameError" not in r.stderr, f"{args[0]} has an undefined name:\n{r.stderr[-400:]}"
    # exit 2 means the ARGUMENTS were wrong, i.e. the command block that names it is not
    # runnable as written -- which is indistinguishable from "the gate blocked" to a
    # caller reading $?.
    assert r.returncode != 2, f"{args[0]} rejected its own documented arguments: {r.stderr[-400:]}"
