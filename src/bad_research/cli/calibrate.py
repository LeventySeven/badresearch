"""`bad calibrate <query>` — OFFLINE calibration harness (SPEC §14; keyless).

Runs a query through bad-research, judges it on the categorical (E2) rubric, and
writes calibration-report.{json,md}. Calibration, NOT a per-run gate (SPEC §10).

`--offline` forces a deterministic stub runner + StubJudge so the command runs
with ZERO keys and ZERO network — this is the tested path.

`--gate` (E1) runs the STORED golden corpus (`calibrate/golden/`) through the
categorical judge + the per-component split (decompose / retrieval / synthesis)
and EXITS NON-ZERO when the corpus pass-rate drops below `--floor` or below a
`--baseline` — the regression gate every later enhancement runs against. It is
keyless (the deterministic RubricJudge) and ignores QUERY.

The live path drives the KEYLESS `pipeline.run_query` (host WebSearch + ddgs +
crawl4ai + FTS5/BM25 + host-model LLM-rerank — no third-party key) and a single
strong-model LLMJudge. It still reads ANTHROPIC_API_KEY for the HEADLESS model
calls (the only path that needs it; the skill path uses the Claude Code host
model and needs no key). The only baseline is the keyless `hyperresearch` one —
the keyed deep-research baselines (Perplexity/Grok) were removed.
"""

from __future__ import annotations

from pathlib import Path

import typer

from bad_research.cli._output import console, output
from bad_research.models.output import success


def calibrate(
    query: str | None = typer.Argument(
        None, help="The research query to calibrate on (omit with --gate)."
    ),
    out: str = typer.Option(".", "--out", "-o", help="Output dir for the calibration report."),
    offline: bool = typer.Option(
        False,
        "--offline",
        help="Use a deterministic stub runner + stub judge (no keys, no network).",
    ),
    gate: bool = typer.Option(
        False,
        "--gate",
        help="Run the golden corpus through the regression gate; exit non-zero on regression.",
    ),
    llm: bool = typer.Option(
        False,
        "--llm",
        help="Use LLMJudge over the full corpus (requires host model; slow).",
    ),
    golden_dir: str | None = typer.Option(
        None, "--golden-dir", help="Override the golden-corpus dir (default: the shipped seed set)."
    ),
    floor: float | None = typer.Option(
        None, "--floor", help="Gate pass-rate floor (default: GATE_FLOOR)."
    ),
    baseline: float | None = typer.Option(
        None, "--baseline", help="Gate also fails if the pass-rate regresses below this baseline."
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output."),
) -> None:
    """Score bad-research on QUERY (offline categorical judge), or run the
    golden-corpus regression gate with --gate."""
    out_dir = Path(out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if gate:
        _run_gate(
            out_dir,
            golden_dir=golden_dir,
            floor=floor,
            baseline=baseline,
            json_output=json_output,
            llm=llm,
        )
        return

    if query is None:
        msg = "calibrate needs a QUERY (or pass --gate to run the golden corpus gate)."
        if json_output:
            from bad_research.models.output import error

            output(error(msg, "NO_QUERY"), json_mode=True)
        else:
            console.print(f"[red]Error:[/] {msg}")
        raise typer.Exit(2)

    from bad_research.calibrate import (
        CostMeter,
        StubJudge,
        available_baselines,
        run_calibration,
    )
    from bad_research.calibrate.constants import JUDGE_AXES
    from bad_research.calibrate.harness import BadRunOutput

    if offline:
        # Deterministic, key-free path: a stub runner + stub judge.
        def _stub_runner(q: str) -> BadRunOutput:
            meter = CostMeter()
            meter.record(
                stage="synthesize",
                tier="heavy",
                input_tokens=8000,
                output_tokens=4000,
                citation_tokens=200,
                search_queries=15,
            )
            return BadRunOutput(
                report=f"# {q}\n\nA grounded claim [1].\n",
                corpus=[{"note_id": "n1", "url": "https://example.edu", "text": "evidence"}],
                cost=meter,
            )

        judge = StubJudge(rails={a: "pass" for a in JUDGE_AXES})
        report = run_calibration(query, runner=_stub_runner, baselines=[], judge=judge)
    else:
        # Live path: real runner + LLM judge + key-gated baselines.
        from bad_research.calibrate.judge import LLMJudge
        from bad_research.calibrate.runner import default_runner

        try:
            from bad_research.llm.base import get_llm_provider

            provider = get_llm_provider()
        except Exception as exc:
            msg = (
                "RESEARCH runs KEYLESS via the skill — run `/bad-research <query>` in "
                "a Claude Code session (or invoke the bad-research skill from a Task "
                "subagent); no API key needed. `bad calibrate` is the off-mission "
                "calibration/benchmark bridge and is the one path that needs a model "
                "key: set ANTHROPIC_API_KEY, or use --offline for the deterministic "
                f"key-free path. ({exc})"
            )
            if json_output:
                from bad_research.models.output import error

                output(error(msg, "NO_PROVIDER"), json_mode=True)
            else:
                console.print(f"[red]Error:[/] {msg}")
            raise typer.Exit(1)

        report = run_calibration(
            query,
            runner=default_runner(config=None),
            baselines=available_baselines(),
            judge=LLMJudge(provider=provider),
        )

    json_path = out_dir / "calibration-report.json"
    md_path = out_dir / "calibration-report.md"
    json_path.write_text(report.to_json(), encoding="utf-8")
    md_path.write_text(report.to_markdown(), encoding="utf-8")

    if json_output:
        output(success(report.to_dict(), vault=str(out_dir)), json_mode=True)
        return

    v = report.bad.verdict
    console.print(f"[bold]Calibration:[/] {query}")
    console.print(
        f"  bad-research pass-rate: [bold]{v.pass_rate:.3f}[/] "
        f"({'[green]PASS[/]' if v.passed else '[red]FAIL[/]'})  "
        f"cost ${report.bad.cost_usd:.4f}"
    )
    for b in report.baselines:
        console.print(f"  {b.name}: {b.verdict.pass_rate:.3f}  (Δ {report.delta_vs(b.name):+.3f})")
    console.print(f"\n[green]Wrote[/] {json_path}\n[green]Wrote[/] {md_path}")


def _run_gate(
    out_dir: Path,
    *,
    golden_dir: str | None,
    floor: float | None,
    baseline: float | None,
    json_output: bool,
    llm: bool = False,
) -> None:
    """E1 — the golden-corpus regression gate. Default: keyless deterministic
    RubricJudge ($0, no host model). With --llm (E1-1) it routes the full corpus
    (including the `requires_llm` fixtures) through the host-model LLMJudge.
    Exits non-zero iff the corpus pass-rate < floor (or < baseline)."""
    import json as _json

    from bad_research.calibrate.golden import (
        GATE_FLOOR,
        evaluate_corpus,
        load_golden_corpus,
    )

    use_floor = GATE_FLOOR if floor is None else floor
    cases = load_golden_corpus(golden_dir)
    # E1-1: --llm routes to the host-model LLMJudge; the default stays keyless
    # (judge=None -> evaluate_corpus uses the deterministic RubricJudge).
    judge = _make_llm_judge() if llm else None
    report = evaluate_corpus(cases, judge=judge)
    ok = report.gate_ok(floor=use_floor, baseline=baseline)

    rep_path = out_dir / "golden-eval-report.json"
    rep_path.write_text(_json.dumps(report.to_dict(), indent=2), encoding="utf-8")

    if json_output:
        payload = report.to_dict()
        payload["gate_ok"] = ok
        payload["floor"] = use_floor
        envelope = success(payload, count=report.total, vault=str(out_dir))
        output(envelope, json_mode=True)
    else:
        verb = "[green]PASS[/]" if ok else "[red]FAIL[/]"
        console.print(
            f"[bold]Golden gate:[/] pass-rate [bold]{report.pass_rate:.3f}[/] "
            f"over {report.total} cases (floor {use_floor:.2f}) {verb}"
        )
        for name, rate in report.components.items():
            console.print(f"  {name}: {rate:.3f}")
        for c in report.cases:
            if not c.passed:
                console.print(f"  [red]regression[/] {c.id}: {c.verdict.rails.as_str_dict()}")
        console.print(f"\n[green]Wrote[/] {rep_path}")

    if not ok:
        raise typer.Exit(1)


def _make_llm_judge():
    """Construct an LLMJudge for the --llm gate path (E1-1).
    Requires the host model (ANTHROPIC_API_KEY or the Claude Code host)."""
    from bad_research.calibrate.judge import LLMJudge
    from bad_research.llm.base import get_llm_provider

    return LLMJudge(provider=get_llm_provider())


__all__ = ["calibrate"]
