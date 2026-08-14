"""The social vertical: engine resolution, JSON mapping, and honest failure.

No network and no subprocess — the engine call is injected, exactly as the HTTP
verticals inject an httpx client.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

from bad_research.web.base import SearchQuery
from bad_research.web.search import social
from bad_research.web.search.social import (
    ENV_HOME,
    ENV_PYTHON,
    ENV_SCRIPT,
    ENV_TIMEOUT,
    Last30DaysProvider,
    _child_env,
    _run_engine,
    resolve_engine,
)
from bad_research.web.search.status import ERROR, NO_RESULTS, OK, RATE_LIMITED, TIMEOUT

PAYLOAD = {
    "schema_version": "1.2",
    "query": "claude code skills",
    "results": [
        {
            "title": "Anthropic cut 80% of Claude Code's system prompt",
            "source": "reddit",
            "url": "https://www.reddit.com/r/ClaudeAI/comments/1v5mhhl/",
            "published_at": "2026-07-24",
            "summary": "r/ClaudeAI on what still belongs in CLAUDE.md.",
            "engagement": {"score": 1485, "num_comments": 85},
            "relevance_score": 0.91,
        },
        {
            "title": "Auto mode is now the default in Claude Code",
            "source": "hackernews",
            "url": "https://claude.com/blog/auto-mode-default-in-claude-code",
            "summary": "290 points, 313 comments.",
            "engagement": {"points": 290},
            "relevance_score": 0.74,
        },
    ],
}


def _fake_runner(payload, seen=None):
    def run(argv, timeout, env):
        if seen is not None:
            seen.append((argv, timeout, env))
        return payload
    return run


# ── resolution ────────────────────────────────────────────────────────────


def test_resolve_prefers_explicit_script(tmp_path):
    script = tmp_path / "last30days.py"
    script.write_text("")
    assert resolve_engine({ENV_SCRIPT: str(script)}) == script


def test_resolve_explicit_script_that_does_not_exist_is_none(tmp_path):
    assert resolve_engine({ENV_SCRIPT: str(tmp_path / "nope.py")}) is None


def test_resolve_finds_the_repo_layout_under_home(tmp_path):
    script = tmp_path / "skills" / "last30days" / "scripts" / "last30days.py"
    script.parent.mkdir(parents=True)
    script.write_text("")
    assert resolve_engine({ENV_HOME: str(tmp_path)}) == script


def test_resolve_finds_the_installed_skill_layout_under_home(tmp_path):
    script = tmp_path / "scripts" / "last30days.py"
    script.parent.mkdir(parents=True)
    script.write_text("")
    assert resolve_engine({ENV_HOME: str(tmp_path)}) == script


def test_resolve_returns_none_when_not_installed(tmp_path):
    # HOME points somewhere real but empty, and the documented install dirs are
    # checked by absolute path — an uninstalled engine must resolve to None, not raise.
    assert resolve_engine({ENV_HOME: str(tmp_path)}) is None


def test_provider_refuses_to_build_without_an_engine(tmp_path):
    with pytest.raises(FileNotFoundError, match="last30days"):
        Last30DaysProvider(env={ENV_HOME: str(tmp_path)})


# ── mapping ───────────────────────────────────────────────────────────────


def test_maps_results_onto_webresults_with_engagement(tmp_path):
    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=_fake_runner(PAYLOAD), env={})
    rows = p.search("claude code skills")

    assert [r.url for r in rows] == [
        "https://www.reddit.com/r/ClaudeAI/comments/1v5mhhl/",
        "https://claude.com/blog/auto-mode-default-in-claude-code",
    ]
    first = rows[0]
    assert first.title.startswith("Anthropic cut 80%")
    assert first.content == "r/ClaudeAI on what still belongs in CLAUDE.md."
    assert first.metadata["source"] == "last30days:reddit"
    assert first.metadata["rank"] == 1
    assert first.metadata["published_date"] == "2026-07-24"
    assert first.metadata["engagement"] == {"score": 1485, "num_comments": 85}
    assert first.metadata["native_score"] == 0.91
    assert p.last_status == OK


def test_every_result_is_stamped_prefetched(tmp_path):
    # The read stage keys the no-refetch path off this flag; losing it silently
    # sends every social permalink through an anonymous fetch into a login wall.
    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=_fake_runner(PAYLOAD), env={})
    assert all(r.metadata["prefetched"] is True for r in p.search("q"))


def test_engagement_summary_is_stable_and_counts_only_integers(tmp_path):
    payload = {"results": [{
        "title": "t", "url": "https://e.example/1", "summary": "s",
        "engagement": {"score": 1485, "num_comments": 85, "ratio": 0.97, "pinned": True},
    }]}
    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=_fake_runner(payload), env={})
    summary = p.search("q")[0].metadata["engagement_summary"]
    assert summary == "85 num comments · 1,485 score"   # sorted by key, thousands-grouped
    assert "ratio" not in summary and "pinned" not in summary


def test_rows_without_a_url_are_dropped(tmp_path):
    payload = {"results": [
        {"title": "no link", "url": "", "summary": "x"},
        {"title": "linked", "url": "https://e.example/2", "summary": "y"},
        "not-an-object",
    ]}
    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=_fake_runner(payload), env={})
    assert [r.url for r in p.search("q")] == ["https://e.example/2"]


def test_search_ex_threads_recency_and_max_results(tmp_path):
    seen: list = []
    p = Last30DaysProvider(
        script=tmp_path / "l30d.py", runner=_fake_runner(PAYLOAD, seen),
        env={ENV_PYTHON: "/usr/bin/python3.12"},
    )
    p.search_ex(SearchQuery(query="what do users say about X", max_results=7, recency_days=14))

    argv, _timeout, _env = seen[0]
    assert argv[0] == "/usr/bin/python3.12"
    # the query is an argv item, never a shell string — and it goes LAST, after `--`
    assert argv[-2:] == ["--", "what do users say about X"]
    assert "--emit=json" in argv and "--json-profile=agent" in argv
    assert "--quick" in argv
    assert "--max-results=7" in argv
    assert "--days=14" in argv


def test_no_recency_means_no_days_flag(tmp_path):
    seen: list = []
    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=_fake_runner(PAYLOAD, seen), env={})
    p.search("q")
    argv, _timeout, _env = seen[0]
    assert not any(a.startswith("--days=") for a in argv)


# ── failure is observable, never a silent absence (issue #39 contract) ─────


def test_empty_results_report_no_results_not_ok(tmp_path):
    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=_fake_runner({"results": []}), env={})
    assert p.search("q") == []
    assert p.last_status == NO_RESULTS


def test_timeout_reports_timeout(tmp_path):
    def boom(argv, timeout, env):
        raise subprocess.TimeoutExpired(cmd=argv, timeout=timeout)

    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=boom, env={})
    assert p.search("q") == []
    assert p.last_status == TIMEOUT


def test_nonzero_exit_reports_error(tmp_path):
    def boom(argv, timeout, env):
        raise RuntimeError("last30days exited 2: bad flag")

    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=boom, env={})
    assert p.search("q") == []
    assert p.last_status == ERROR


def test_unparseable_stdout_reports_error(tmp_path):
    def boom(argv, timeout, env):
        raise json.JSONDecodeError("nope", "", 0)

    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=boom, env={})
    assert p.search("q") == []
    assert p.last_status == ERROR


def test_timeout_env_override_is_honoured(tmp_path):
    seen: list = []
    p = Last30DaysProvider(
        script=tmp_path / "l30d.py", runner=_fake_runner(PAYLOAD, seen),
        env={ENV_TIMEOUT: "45"},
    )
    p.search("q")
    assert seen[0][1] == 45.0


def test_bad_timeout_env_falls_back_to_the_default(tmp_path):
    seen: list = []
    p = Last30DaysProvider(
        script=tmp_path / "l30d.py", runner=_fake_runner(PAYLOAD, seen),
        env={ENV_TIMEOUT: "not-a-number"},
    )
    p.search("q")
    assert seen[0][1] == 300.0


# ── the comparison envelope: a `vs` or `/` query is not an empty topic ─────
#
# The engine calls apply_vs_competitor_routing unconditionally and splits the
# topic on `\bvs\.?\b|\bversus\b|/`, so ANY query containing "vs", "versus" or a
# slash comes back in a SECOND top-level shape that has no `results` key at all.
# Reading only `payload["results"]` turned that into results=[] -> "no-results",
# the one outcome that licenses "there is nothing on X" (issue #39).

COMPARISON_PAYLOAD = {
    "comparison": True,
    "entities": ["jenkins", "github actions"],
    "reports": [
        {"entity": "jenkins", "report": {"results": [
            {"title": "Jenkins is still fine", "source": "reddit", "summary": "r/devops says",
             "url": "https://www.reddit.com/r/devops/comments/1/"},
        ]}},
        {"entity": "github actions", "report": {"results": [
            {"title": "Actions billing surprise", "source": "hackernews", "summary": "313 comments",
             "url": "https://news.ycombinator.com/item?id=2"},
        ]}},
    ],
}


def test_comparison_envelope_rows_are_flattened_not_read_as_an_absence(tmp_path):
    p = Last30DaysProvider(script=tmp_path / "l30d.py",
                           runner=_fake_runner(COMPARISON_PAYLOAD), env={})
    rows = p.search("reddit sentiment on CI/CD adoption")
    assert [r.url for r in rows] == [
        "https://www.reddit.com/r/devops/comments/1/",
        "https://news.ycombinator.com/item?id=2",
    ]
    assert p.last_status == OK
    assert all(r.metadata["prefetched"] is True for r in rows)


def test_an_unrecognised_envelope_is_an_error_never_no_results(tmp_path):
    # An unparsed payload must never license an absence claim: `error` is a
    # coverage gap, `no-results` is a licence to say "there is nothing on X".
    p = Last30DaysProvider(script=tmp_path / "l30d.py",
                           runner=_fake_runner({"schema_version": "9.0", "items": []}), env={})
    assert p.search("q") == []
    assert p.last_status == ERROR


def test_a_comparison_whose_reports_drifted_is_an_error_too(tmp_path):
    payload = {"comparison": True, "entities": ["a", "b"],
               "reports": [{"entity": "a", "findings": []}]}   # no `report.results`
    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=_fake_runner(payload), env={})
    assert p.search("a vs b") == []
    assert p.last_status == ERROR


# ── a body-less row is not evidence ───────────────────────────────────────


def test_rows_without_a_summary_are_dropped(tmp_path):
    # The engine documents `summary` as possibly empty. An empty body is exempt
    # from the funnel's content-hash collapse and lands as a zero-byte note.
    payload = {"results": [
        {"title": "no body", "url": "https://e.example/1", "summary": None},
        {"title": "blank body", "url": "https://e.example/2", "summary": "   "},
        {"title": "real", "url": "https://e.example/3", "summary": "u/x: it broke"},
    ]}
    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=_fake_runner(payload), env={})
    assert [r.url for r in p.search("q")] == ["https://e.example/3"]


# ── per-source failure states ─────────────────────────────────────────────


def test_every_source_rate_limited_is_not_reported_as_no_results(tmp_path):
    payload = {"results": [], "source_status": {"reddit": "rate_limited", "hackernews": "timeout"}}
    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=_fake_runner(payload), env={})
    assert p.search("q") == []
    assert p.last_status == RATE_LIMITED      # most actionable failure wins


def test_source_status_is_ignored_when_the_lane_returned_hits(tmp_path):
    payload = dict(PAYLOAD, source_status={"reddit": "ok", "youtube": "error"})
    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=_fake_runner(payload), env={})
    assert p.search("q")
    assert p.last_status == OK


def test_all_sources_clean_and_empty_is_still_no_results(tmp_path):
    payload = {"results": [], "source_status": {"reddit": "ok", "hackernews": "ok"}}
    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=_fake_runner(payload), env={})
    assert p.search("q") == []
    assert p.last_status == NO_RESULTS


def test_a_missing_interpreter_is_an_error_not_a_network_diagnosis(tmp_path):
    # OSError -> classify_search_failure says UNREACHABLE (DNS/connect). An exec
    # failure is not a network outage; calling it one sends the operator hunting
    # for a firewall that is not there.
    def boom(argv, timeout, env):
        raise FileNotFoundError(2, "No such file or directory: 'python3'")

    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=boom, env={})
    assert p.search("q") == []
    assert p.last_status == ERROR


# ── argv + env boundary ───────────────────────────────────────────────────


def test_a_query_that_starts_with_a_dash_is_not_parsed_as_flags(tmp_path):
    seen: list = []
    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=_fake_runner(PAYLOAD, seen), env={})
    p.search("--sources=all reddit sentiment")
    argv, _timeout, _env = seen[0]
    assert argv[-2:] == ["--", "--sources=all reddit sentiment"]


def test_the_engine_gets_a_minimal_env_not_the_operators_shell(tmp_path):
    # REAL subprocess, real env boundary: the child dumps what it was handed.
    script = tmp_path / "dump_env.py"
    script.write_text("import json, os\nprint(json.dumps(dict(os.environ)))\n")
    parent = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": str(tmp_path),
        ENV_PYTHON: sys.executable,
        "LAST30DAYS_REDDIT_CLIENT_ID": "the engine's own config",
        "ANTHROPIC_API_KEY": "sk-ant-must-not-cross",
        "GITHUB_TOKEN": "ghp-must-not-cross",
        "AWS_SECRET_ACCESS_KEY": "aws-must-not-cross",
        "OPENAI_API_KEY": "sk-must-not-cross",
    }
    child = _run_engine([sys.executable, str(script)], 60.0, _child_env(parent))

    for secret in ("ANTHROPIC_API_KEY", "GITHUB_TOKEN", "AWS_SECRET_ACCESS_KEY", "OPENAI_API_KEY"):
        assert secret not in child
    # nothing else of OURS crossed either (the OS adds its own LC_CTYPE etc.)
    assert set(child) & set(parent) == {"PATH", "HOME", ENV_PYTHON, "LAST30DAYS_REDDIT_CLIENT_ID"}


def test_the_provider_hands_that_same_minimal_env_to_the_runner(tmp_path):
    seen: list = []
    p = Last30DaysProvider(
        script=tmp_path / "l30d.py", runner=_fake_runner(PAYLOAD, seen),
        env={"PATH": "/usr/bin", "ANTHROPIC_API_KEY": "sk-ant-must-not-cross"},
    )
    p.search("q")
    assert seen[0][2] == {"PATH": "/usr/bin"}


def test_an_oversized_stdout_is_refused_before_json_parsing(tmp_path, monkeypatch):
    # stdout is derived from attacker-authored threads; an unbounded read is a
    # memory bomb the funnel would happily hand to json.loads.
    monkeypatch.setattr(social, "_MAX_STDOUT_CHARS", 512)
    script = tmp_path / "flood.py"
    script.write_text('print("[" + "0," * 5000 + "0]")\n')
    with pytest.raises(ValueError, match="stdout"):
        _run_engine([sys.executable, str(script)], 60.0, _child_env({"PATH": os.environ["PATH"]}))


# ── LAST30DAYS_HOME pins the install; it never falls through ──────────────


def test_home_that_does_not_contain_the_engine_refuses_to_fall_through(tmp_path, monkeypatch):
    # Set one level too deep, HOME silently resolved to whatever was installed in
    # ~/.claude/skills — a DIFFERENT engine than the operator pinned.
    installed = tmp_path / "installed" / "scripts" / "last30days.py"
    installed.parent.mkdir(parents=True)
    installed.write_text("")
    monkeypatch.setattr(social, "_INSTALL_DIRS", (str(tmp_path / "installed"),))

    assert resolve_engine({}) == installed                       # the install dir still works
    assert resolve_engine({ENV_HOME: str(tmp_path / "empty")}) is None   # the pin refuses
