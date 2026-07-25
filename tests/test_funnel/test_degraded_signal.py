"""A run that found nothing must say WHY.

`gather` returned [] identically for "this topic genuinely has no sources" and
"every search provider was unavailable" — exit 0, empty stderr, empty vault.
An orchestrator cannot branch on that, so it proceeds to write a report claiming
a research gap that is really a broken provider (issue #35 §5).

Grounded in the convergent contract across the reference corpus: Verso's dispatch
envelope is always `{data, error, ok}` (PRD_v1.md:171); Perplexity's MCP schema
keeps `error` populated distinct from an empty `output`; HYPERRESEARCH carries a
machine-readable `NO_SEARCH` error_code. Emptiness is data; failure is a
different shape.
"""
from __future__ import annotations

import asyncio

from bad_research.funnel.orchestrator import FunnelDeps, gather


class _DeadProvider:
    """A provider that cannot run here — the headless host-tool adapter case."""

    name = "websearch"

    async def search_ex(self, q):
        raise NotImplementedError("host WebSearch tool is not reachable in a subprocess")


class _EmptyProvider:
    """A provider that returned no hits WITHOUT raising.

    This is the shape a dead network actually takes: the keyless providers
    swallow transport failures internally (`DdgsProvider.search_ex` ends
    `except Exception: return []`), so an offline run is indistinguishable
    here from a clean empty SERP. Caught by a live proxy-blocked prod run
    after the first cut of this instrumentation called it healthy.
    """

    name = "ddgs"

    async def search_ex(self, q):
        return []


class _WorkingProvider:
    """A provider that actually returns a hit."""

    name = "ddgs"

    async def search_ex(self, q):
        from bad_research.web.search.base import WebResult

        return [WebResult(url="https://example.org/a", title="a", content="body text")]


def _deps(providers):
    return FunnelDeps(providers=providers, fetcher=None, postfetch_filter=None,
                      vault=None, retrieval=None, vertical_providers=[])


def test_all_providers_unavailable_is_reported_as_degraded():
    stats: dict = {}
    asyncio.run(gather("topic", mode="light", deps=_deps([_DeadProvider()]), stats=stats))
    assert stats["degraded"] is True
    assert "no_search_provider_available" in stats["degraded_reasons"]


def test_every_lane_returning_zero_hits_is_flagged_degraded():
    """A silently-offline stack must not report itself healthy.

    Regression for the bug a proxy-blocked prod run exposed: providers swallow
    their own transport errors into [], so "did not raise" is NOT success.
    """
    stats: dict = {}
    asyncio.run(gather("topic", mode="light", deps=_deps([_EmptyProvider()]), stats=stats))
    assert stats["provider_outcomes"] == {"ddgs": "empty"}
    assert stats["degraded"] is True
    assert "no_search_results_from_any_provider" in stats["degraded_reasons"]


def test_a_lane_returning_hits_is_not_degraded():
    """One lane with real hits carries the run — the documented failover."""
    stats: dict = {}
    asyncio.run(gather("topic", mode="light",
                       deps=_deps([_WorkingProvider(), _DeadProvider()]), stats=stats))
    assert stats["provider_outcomes"]["ddgs"] == "ok"
    assert stats["degraded"] is False
    assert stats["degraded_reasons"] == []


def test_all_dead_and_all_empty_are_distinguishable_reasons():
    """Two different failures deserve two different, actionable reasons."""
    dead: dict = {}
    asyncio.run(gather("t", mode="light", deps=_deps([_DeadProvider()]), stats=dead))
    empty: dict = {}
    asyncio.run(gather("t", mode="light", deps=_deps([_EmptyProvider()]), stats=empty))
    assert dead["degraded_reasons"] == ["no_search_provider_available"]
    assert empty["degraded_reasons"] == ["no_search_results_from_any_provider"]


def test_best_outcome_per_provider_wins_across_queries():
    """One query returning hits proves the lane works, whatever siblings did."""
    class _Flaky:
        name = "flaky"
        calls = 0

        async def search_ex(self, q):
            from bad_research.web.search.base import WebResult

            _Flaky.calls += 1
            if _Flaky.calls == 1:
                raise RuntimeError("transient")
            return [WebResult(url="https://example.org/b", title="b", content="body text")]

    stats: dict = {}
    asyncio.run(gather("topic", mode="light", deps=_deps([_Flaky()]), stats=stats))
    assert stats["provider_outcomes"]["flaky"] == "ok"
    assert stats["degraded"] is False


def test_stats_is_optional_and_gather_is_unchanged_without_it():
    """Opt-in instrumentation: omitting `stats` must not alter behaviour."""
    out = asyncio.run(gather("topic", mode="light", deps=_deps([_EmptyProvider()])))
    assert out == []


def test_no_providers_at_all_is_degraded():
    stats: dict = {}
    asyncio.run(gather("topic", mode="light", deps=_deps([]), stats=stats))
    assert stats["degraded"] is True
    assert "no_search_provider_available" in stats["degraded_reasons"]


# ── the envelope the orchestrator actually reads ─────────────────────────────
def test_funnel_envelope_carries_ok_and_degraded_keys(monkeypatch, tmp_path):
    """run_funnel's dict is the orchestrator's branch point — it must be typed."""
    import bad_research.cli.research as RESEARCH  # noqa: N812

    monkeypatch.chdir(tmp_path)
    from bad_research.cli.vault_cmds import init_cmd  # noqa: F401  (ensures vault module loads)

    envelope_keys = {"note_ids", "top_chunks", "n_read", "n_stored", "ok",
                     "degraded", "degraded_reasons"}
    src = RESEARCH.run_funnel.__doc__ or ""
    assert "degraded" in src, "run_funnel must document the degraded contract"
    # structural check on the literal returned by run_funnel
    import inspect
    body = inspect.getsource(RESEARCH.run_funnel)
    for key in envelope_keys:
        assert f'"{key}"' in body, f"envelope is missing {key}"


def test_degraded_run_exits_nonzero_so_a_shell_caller_can_branch(monkeypatch, tmp_path):
    """A degraded empty run must not look like success to a script."""
    from typer.testing import CliRunner

    import bad_research.cli.research as RESEARCH  # noqa: N812
    from bad_research.cli import app

    def _fake_run_funnel(q, *, mode, vault_tag, search_plan=None, max_queries=None,
                         read_top_k=None, concurrency=None):
        return {"note_ids": [], "top_chunks": [], "n_read": 0, "n_stored": 0,
                "ok": False, "degraded": True,
                "degraded_reasons": ["no_search_provider_available"]}

    monkeypatch.setattr(RESEARCH, "run_funnel", _fake_run_funnel)
    res = CliRunner().invoke(app, ["funnel-gather", "t", "--mode", "light", "--json"])
    assert res.exit_code != 0, "a degraded empty run must not exit 0"
    assert "no_search_provider_available" in res.stdout


def test_genuinely_empty_run_still_exits_zero(monkeypatch, tmp_path):
    """Honest emptiness is success — only degradation is an error."""
    from typer.testing import CliRunner

    import bad_research.cli.research as RESEARCH  # noqa: N812
    from bad_research.cli import app

    def _fake_run_funnel(q, *, mode, vault_tag, search_plan=None, max_queries=None,
                         read_top_k=None, concurrency=None):
        return {"note_ids": [], "top_chunks": [], "n_read": 0, "n_stored": 0,
                "ok": True, "degraded": False, "degraded_reasons": []}

    monkeypatch.setattr(RESEARCH, "run_funnel", _fake_run_funnel)
    res = CliRunner().invoke(app, ["funnel-gather", "t", "--mode", "light", "--json"])
    assert res.exit_code == 0
