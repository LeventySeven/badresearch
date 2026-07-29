"""The width-sweep search plan must actually reach the funnel.

`bad-research-2-width-sweep.md` builds a 40-100 row, lens-diverse search plan and
passes it via `--search-plan`; the skill prose promises it "hands the search plan
to the deterministic six-stage funnel". `gather()` was built to accept it
(`queries=`). The CLI never wired it, so every run silently fell back to
`plan_queries` — 6 generic suffix expansions — regardless of mode. (issue #35 §4)
"""
from __future__ import annotations

import inspect
from pathlib import Path

import bad_research.cli.research as RESEARCH  # noqa: N812
from bad_research.funnel.config import FunnelConfig
from bad_research.funnel.fanout import plan_queries


# ── the parser ───────────────────────────────────────────────────────────────
def test_parse_search_plan_extracts_queries_from_the_skill_table(tmp_path: Path):
    """The skill writes a markdown table; column 2 holds the query."""
    plan = tmp_path / "search-plan.md"
    plan.write_text(
        "| Atomic item | Search query | Type | Lens | Target |\n"
        "|---|---|---|---|---|\n"
        '| Sub-Q1 | "China financial industry growth trends 2025" | web | breadth | factual |\n'
        '| Sub-Q1 | "China financial sector structural risks" | web | adversarial | contrarian |\n'
        '| Entity: PE | "China private equity returns academic study" | academic | depth | canonical |\n',
        encoding="utf-8",
    )
    queries = RESEARCH.parse_search_plan(plan, k_per_query=10)
    texts = [q.query for q in queries]
    assert texts == [
        "China financial industry growth trends 2025",
        "China financial sector structural risks",
        "China private equity returns academic study",
    ]
    assert all(q.max_results == 10 for q in queries)


def test_parse_search_plan_ignores_header_separator_and_prose(tmp_path: Path):
    """Only real data rows count — no header, no `|---|`, no surrounding prose."""
    plan = tmp_path / "search-plan.md"
    plan.write_text(
        "# Search plan\n\nSome prose that is not a table.\n\n"
        "| Atomic item | Search query | Type | Lens | Target |\n"
        "|---|---|---|---|---|\n"
        "| Sub-Q1 | solar panel efficiency 2026 | web | breadth | factual |\n"
        "\nTrailing prose.\n",
        encoding="utf-8",
    )
    queries = RESEARCH.parse_search_plan(plan, k_per_query=5)
    assert [q.query for q in queries] == ["solar panel efficiency 2026"]


def test_parse_search_plan_respects_max_queries_cap(tmp_path: Path):
    rows = "\n".join(f"| S{i} | query number {i} | web | breadth | factual |" for i in range(50))
    plan = tmp_path / "search-plan.md"
    plan.write_text(
        "| Atomic item | Search query | Type | Lens | Target |\n|---|---|---|---|---|\n" + rows,
        encoding="utf-8",
    )
    queries = RESEARCH.parse_search_plan(plan, k_per_query=5, max_queries=12)
    assert len(queries) == 12


def test_parse_search_plan_dedups_repeated_queries(tmp_path: Path):
    plan = tmp_path / "search-plan.md"
    plan.write_text(
        "| Atomic item | Search query | Type | Lens | Target |\n|---|---|---|---|---|\n"
        "| S1 | same query text | web | breadth | factual |\n"
        "| S2 | same query text | web | adversarial | contrarian |\n",
        encoding="utf-8",
    )
    assert len(RESEARCH.parse_search_plan(plan, k_per_query=5)) == 1


# ── the threading seam ───────────────────────────────────────────────────────
def test_run_funnel_accepts_the_plan_flags():
    """run_funnel must be able to carry what the CLI parses."""
    params = inspect.signature(RESEARCH.run_funnel).parameters
    assert "search_plan" in params
    assert "max_queries" in params
    assert "read_top_k" in params


def test_funnel_gather_cmd_passes_search_plan_through(monkeypatch, tmp_path: Path):
    """The CLI must hand the parsed plan to run_funnel — not drop it."""
    from typer.testing import CliRunner

    from bad_research.cli import app

    plan = tmp_path / "search-plan.md"
    plan.write_text(
        "| Atomic item | Search query | Type | Lens | Target |\n|---|---|---|---|---|\n"
        "| S1 | grounded query alpha | web | breadth | factual |\n",
        encoding="utf-8",
    )

    seen: dict = {}

    def _fake_run_funnel(q, *, mode, vault_tag, search_plan=None, max_queries=None,
                         read_top_k=None, concurrency=None, raw=False):
        seen["search_plan"] = search_plan
        seen["max_queries"] = max_queries
        return {"note_ids": [], "top_chunks": [], "n_read": 0}

    monkeypatch.setattr(RESEARCH, "run_funnel", _fake_run_funnel)
    res = CliRunner().invoke(app, [
        "funnel-gather", "topic", "--mode", "light", "--vault-tag", "t",
        "--search-plan", str(plan), "--max-queries", "7", "--json",
    ])
    assert res.exit_code == 0, res.stdout
    assert seen["search_plan"] == str(plan)
    assert seen["max_queries"] == 7


def test_supplied_but_unparseable_plan_is_reported_not_silently_dropped(tmp_path: Path):
    """Falling back silently would re-create the exact bug this seam removes.

    The caller believes its 40-100 lens queries ran; without a warning it has no
    way to learn that 16 generic suffixes ran instead.
    """
    plan = tmp_path / "search-plan.md"
    plan.write_text("# Search plan\n\nThe model forgot to emit the table.\n", encoding="utf-8")
    queries = RESEARCH.parse_search_plan(plan, k_per_query=5)
    assert queries == []
    body = inspect.getsource(RESEARCH.run_funnel)
    assert "search_plan_empty_or_unparseable" in body, (
        "an unparseable supplied plan must surface a warning, not vanish"
    )
    assert '"warnings"' in body


def test_missing_plan_file_fails_loudly(tmp_path: Path):
    """A path that isn't there is a caller bug — surface it, don't paper over it."""
    import pytest

    with pytest.raises(FileNotFoundError):
        RESEARCH.parse_search_plan(tmp_path / "nope.md", k_per_query=5)


def test_query_column_is_located_by_header_not_by_index(tmp_path: Path):
    """Step 2.5's gap-search-plan has no fixed schema — index 1 read the wrong column.

    With a hardcoded index this returned ['Lens', 'breadth'] and the funnel
    searched the literal word "breadth".
    """
    plan = tmp_path / "gap-search-plan.md"
    plan.write_text(
        "| Search query | Lens |\n|---|---|\n| solar efficiency 2026 | breadth |\n",
        encoding="utf-8",
    )
    assert [q.query for q in RESEARCH.parse_search_plan(plan, k_per_query=5)] == [
        "solar efficiency 2026"
    ]


def test_bolded_header_is_not_fired_as_a_query(tmp_path: Path):
    """Model-written markdown bolds headers constantly."""
    plan = tmp_path / "search-plan.md"
    plan.write_text(
        "| Atomic item | **Search query** | Type |\n|---|---|---|\n"
        "| S1 | real query one | web |\n",
        encoding="utf-8",
    )
    assert [q.query for q in RESEARCH.parse_search_plan(plan, k_per_query=5)] == [
        "real query one"
    ]


def test_plan_with_no_locatable_query_column_yields_nothing(tmp_path: Path):
    """Better to report "unparseable" than to guess a column and search garbage."""
    plan = tmp_path / "search-plan.md"
    plan.write_text("| Foo | Bar |\n|---|---|\n| a | b |\n", encoding="utf-8")
    assert RESEARCH.parse_search_plan(plan, k_per_query=5) == []


def test_unescaped_pipe_is_rejoined_when_the_query_is_the_last_column(tmp_path: Path):
    """Only then can the surplus be attributed to the query."""
    plan = tmp_path / "search-plan.md"
    plan.write_text(
        "| A | Search query |\n|---|---|\n"
        "| S1 | solar | wind capacity |\n",
        encoding="utf-8",
    )
    assert [q.query for q in RESEARCH.parse_search_plan(plan, k_per_query=5)] == [
        "solar | wind capacity"
    ]


def test_a_stray_pipe_in_a_later_column_never_splices_onto_the_query(tmp_path: Path):
    """The surplus is unattributable here — guessing corrupts the query.

    With the query at index 1 of 5 and a stray pipe in Target, a blind rejoin
    fired "southeast asia GMV | breadth" as a real search: the same silent
    corruption the escaped-pipe handling exists to prevent.
    """
    plan = tmp_path / "search-plan.md"
    plan.write_text(
        "| Atomic item | Search query | Type | Lens | Target |\n|---|---|---|---|---|\n"
        "| S1 | southeast asia GMV | web | breadth | factual | extra |\n",
        encoding="utf-8",
    )
    assert [q.query for q in RESEARCH.parse_search_plan(plan, k_per_query=5)] == [
        "southeast asia GMV"
    ]


def test_max_queries_zero_is_not_reinterpreted(tmp_path: Path):
    """The cap must be checked BEFORE appending, and 0 must mean 0."""
    plan = tmp_path / "search-plan.md"
    plan.write_text(
        "| A | Search query | T |\n|---|---|---|\n| S1 | q1 | web |\n| S2 | q2 | web |\n",
        encoding="utf-8",
    )
    assert RESEARCH.parse_search_plan(plan, k_per_query=5, max_queries=0) == []


def test_parse_search_plan_handles_an_escaped_pipe_in_the_query(tmp_path: Path):
    r"""A boolean query containing `\|` must survive the column split.

    A naive split on every `|` truncated `solar \| wind efficiency` to
    `solar \` and fired THAT as a real search — silent query corruption.
    """
    plan = tmp_path / "search-plan.md"
    plan.write_text(
        "| Atomic item | Search query | Type | Lens | Target |\n|---|---|---|---|---|\n"
        "| S1 | solar \\| wind efficiency | web | breadth | factual |\n",
        encoding="utf-8",
    )
    out = RESEARCH.parse_search_plan(plan, k_per_query=5)
    assert [q.query for q in out] == ["solar | wind efficiency"]


def test_gather_uses_supplied_queries_over_deterministic_expansion(tmp_path: Path):
    """End-to-end at the orchestrator seam: a supplied plan wins over plan_queries."""
    import asyncio

    from bad_research.funnel.orchestrator import FunnelDeps, gather
    from bad_research.web.search.base import SearchQuery

    fired: list[str] = []

    class _RecordingProvider:
        name = "recorder"

        async def search_ex(self, q):
            fired.append(q.query)
            return []

    deps = FunnelDeps(
        providers=[_RecordingProvider()], fetcher=None, postfetch_filter=None,
        vault=None, retrieval=None, vertical_providers=[],
    )
    planned = [SearchQuery(query="hand written lens query", max_results=5)]
    asyncio.run(gather("raw topic", mode="light", deps=deps, queries=planned))

    assert fired == ["hand written lens query"], (
        "gather must fire the supplied plan verbatim, not the suffix expansion"
    )


# ── the breadth collapse ─────────────────────────────────────────────────────
def test_deterministic_fallback_is_not_starved_in_full_mode():
    """full mode configures m_queries=100; the fallback must not collapse to 6.

    A `full` run with no supplied plan previously produced exactly 6 queries — a
    94% breadth loss against its own configured budget.
    """
    cfg = FunnelConfig.for_mode("full")
    produced = plan_queries("China fintech regulation 2025",
                            m_queries=cfg.m_queries, k_per_query=cfg.k_per_query)
    assert len(produced) > 6, (
        f"full mode budgets {cfg.m_queries} queries but the fallback produced "
        f"{len(produced)} — the suffix table starves it"
    )


def test_plan_queries_keeps_verbatim_query_first():
    """Regression guard: the bare query must remain seed #1 whatever else changes."""
    out = plan_queries("solar panel efficiency", m_queries=20, k_per_query=5)
    assert out[0].query == "solar panel efficiency"


def test_plan_queries_never_exceeds_its_cap():
    assert len(plan_queries("x", m_queries=3, k_per_query=5)) == 3


def test_plan_queries_emits_no_duplicates():
    out = plan_queries("quantum error correction", m_queries=40, k_per_query=5)
    assert len({q.query for q in out}) == len(out)
