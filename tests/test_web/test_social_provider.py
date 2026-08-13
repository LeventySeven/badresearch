"""The social vertical: engine resolution, JSON mapping, and honest failure.

No network and no subprocess — the engine call is injected, exactly as the HTTP
verticals inject an httpx client.
"""

from __future__ import annotations

import json
import subprocess

import pytest

from bad_research.web.base import SearchQuery
from bad_research.web.search.social import (
    ENV_HOME,
    ENV_PYTHON,
    ENV_SCRIPT,
    ENV_TIMEOUT,
    Last30DaysProvider,
    resolve_engine,
)
from bad_research.web.search.status import ERROR, NO_RESULTS, OK, TIMEOUT

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
    def run(argv, timeout):
        if seen is not None:
            seen.append((argv, timeout))
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

    argv, _timeout = seen[0]
    assert argv[0] == "/usr/bin/python3.12"
    assert argv[2] == "what do users say about X"      # the query is an argv item, never a shell string
    assert "--emit=json" in argv and "--json-profile=agent" in argv
    assert "--quick" in argv
    assert "--max-results=7" in argv
    assert "--days=14" in argv


def test_no_recency_means_no_days_flag(tmp_path):
    seen: list = []
    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=_fake_runner(PAYLOAD, seen), env={})
    p.search("q")
    argv, _ = seen[0]
    assert not any(a.startswith("--days=") for a in argv)


# ── failure is observable, never a silent absence (issue #39 contract) ─────


def test_empty_results_report_no_results_not_ok(tmp_path):
    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=_fake_runner({"results": []}), env={})
    assert p.search("q") == []
    assert p.last_status == NO_RESULTS


def test_timeout_reports_timeout(tmp_path):
    def boom(argv, timeout):
        raise subprocess.TimeoutExpired(cmd=argv, timeout=timeout)

    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=boom, env={})
    assert p.search("q") == []
    assert p.last_status == TIMEOUT


def test_nonzero_exit_reports_error(tmp_path):
    def boom(argv, timeout):
        raise RuntimeError("last30days exited 2: bad flag")

    p = Last30DaysProvider(script=tmp_path / "l30d.py", runner=boom, env={})
    assert p.search("q") == []
    assert p.last_status == ERROR


def test_unparseable_stdout_reports_error(tmp_path):
    def boom(argv, timeout):
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
