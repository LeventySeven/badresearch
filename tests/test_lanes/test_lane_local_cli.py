from __future__ import annotations

import json

from typer.testing import CliRunner

from bad_research.cli import app
from bad_research.lanes import local_corpus

runner = CliRunner()


def _corpus(tmp_path, monkeypatch, body: str = "line one\ndeep research agent loop\n"):
    d = tmp_path / "teardowns"
    d.mkdir()
    (d / "a.md").write_text(body)
    monkeypatch.setattr(local_corpus, "DEFAULT_ROOTS", (d, tmp_path / "gone"))
    return d


def test_json_payload_shape(tmp_path, monkeypatch):
    d = _corpus(tmp_path, monkeypatch)
    res = runner.invoke(app, ["lane-local", "deep research", "--json"])
    assert res.exit_code == 0, res.stdout
    out = json.loads(res.stdout)
    assert out["lane"] == "local-corpus"
    assert out["files_listed"] == 1
    assert out["selected"] == 1
    assert out["cut_line"] == "no cap applied"
    assert out["unreachable_roots"] == [str(tmp_path / "gone")]
    assert out["hits"] == [
        {"path": str(d / "a.md"), "line": 2, "text": "deep research agent loop"}
    ]


def test_human_output_leads_with_the_enumeration_line(tmp_path, monkeypatch):
    d = _corpus(tmp_path, monkeypatch)
    res = runner.invoke(app, ["lane-local", "deep research"])
    assert res.exit_code == 0, res.stdout
    lines = res.stdout.strip().splitlines()
    assert lines[0].startswith("local-corpus | files listed 1 | candidates selected 1 |")
    assert lines[1] == f"{d / 'a.md'}:2: deep research agent loop"


def test_zero_hits_still_prints_the_enumeration_line(tmp_path, monkeypatch):
    _corpus(tmp_path, monkeypatch)
    res = runner.invoke(app, ["lane-local", "zzz-no-such-term-zzz"])
    assert res.exit_code == 0, res.stdout
    assert res.stdout.strip().splitlines()[0].startswith(
        "local-corpus | files listed 1 | candidates selected 0 |"
    )
