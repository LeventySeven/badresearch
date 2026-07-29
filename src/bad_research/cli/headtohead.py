"""`bad headtohead` — the reproducible head-to-head benchmark (honesty-audit row 11).

Score bad-research against a commercial Deep Research tool on a SHARED query set,
with both sides BLINDED and graded by the EXISTING categorical judge, then emit a
scorecard (JSON + markdown table). Keyless and offline by default.

HONEST by construction: the competitor's report is PASTED by a human (this tool
never calls Gemini/OpenAI/Perplexity/Grok). The command measures the apparatus,
not a claimed win — the tally is whatever the real runs produced.

Two input shapes for the entrant reports:

  1. `--manifest M.json` — a per-query manifest mapping each query id to its
     entrants:
        {
          "bad_name": "bad-research-fast",
          "competitor_name": "gemini-deep-research",
          "entrants": {
            "h2h_01_causal": [
              {"name": "bad-research-fast", "report_file": "runs/bad/01.md",
               "corpus_file": "runs/bad/01_corpus.json", "cost_usd": 0.02, "latency_s": 540},
              {"name": "gemini-deep-research", "report_file": "runs/gem/01.md",
               "cost_usd": 0.0, "latency_s": 300}
            ],
            ...
          }
        }
     `report_file`/`corpus_file` are resolved relative to the manifest's dir.

  2. `--bad-report F --competitor-report F --query-id ID` — a single-query
     convenience pair (handy for a first run before a full manifest exists).

`--llm` routes scoring through the host-model LLMJudge (needs the host model);
the default is the keyless deterministic RubricJudge ($0, no network).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer

from bad_research.cli._output import console, output
from bad_research.models.output import error, success

if TYPE_CHECKING:
    from bad_research.calibrate.headtohead import Scorecard
    from bad_research.calibrate.judge import LLMJudge


def headtohead(
    query_set: str = typer.Option(
        "docs/benchmarks/queries/starter_set.json",
        "--query-set",
        "-q",
        help="Shared query set JSON [{id, query}] (default: the shipped starter set).",
    ),
    manifest: str | None = typer.Option(
        None,
        "--manifest",
        "-m",
        help="Per-query entrant manifest JSON (bad + competitor report files per query id).",
    ),
    bad_report: str | None = typer.Option(
        None, "--bad-report", help="Single-query: bad-research report file (use with --query-id)."
    ),
    competitor_report: str | None = typer.Option(
        None,
        "--competitor-report",
        help="Single-query: pasted competitor report file (use with --query-id).",
    ),
    query_id: str | None = typer.Option(
        None, "--query-id", help="Single-query: which query id the two reports answer."
    ),
    bad_name: str = typer.Option(
        "bad-research", "--bad-name", help="Display name for the bad-research entrant."
    ),
    competitor_name: str = typer.Option(
        "competitor", "--competitor-name", help="Display name for the competitor entrant."
    ),
    out: str = typer.Option(".", "--out", "-o", help="Output dir for the scorecard files."),
    no_blind: bool = typer.Option(
        False, "--no-blind", help="Skip blinding (debug only; biases the judge — not for results)."
    ),
    llm: bool = typer.Option(
        False, "--llm", help="Score via the host-model LLMJudge (needs host model; slow)."
    ),
    emit_judge_tasks: str | None = typer.Option(
        None,
        "--emit-judge-tasks",
        help="KEYLESS host-judge: write blinded judge-task files + manifest to this dir "
        "(the orchestrating Claude then judges each file). No scorecard yet.",
    ),
    verdicts: str | None = typer.Option(
        None,
        "--verdicts",
        help="KEYLESS host-judge: ingest host-written *.verdict.json from this dir "
        "(an --emit-judge-tasks dir) and emit the scorecard. No key needed.",
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output."),
) -> None:
    """Run the head-to-head: blind both sides, score with the categorical judge,
    emit a scorecard. Keyless + offline unless --llm is passed.

    Two keyless host-judge subcommands let the orchestrating Claude BE the judge
    (no API key, no provider): `--emit-judge-tasks <dir>` writes blinded task files
    + a manifest; the host judges each file by hand; `--verdicts <dir>` ingests the
    host-written `*.verdict.json` rails and emits the same scorecard."""
    from bad_research.calibrate.headtohead import (
        Entrant,
        load_query_set,
        load_verdicts,
        run_head_to_head,
    )
    from bad_research.calibrate.headtohead import (
        emit_judge_tasks as emit_judge_tasks_fn,
    )

    out_dir = Path(out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── KEYLESS host-judge ingest: build the scorecard from host-written verdicts ──
    # Self-contained: reads its own manifest (from --emit-judge-tasks), so it does
    # NOT need --manifest/--bad-report/etc. No provider, no key.
    if verdicts is not None:
        try:
            v_qset, v_entrants, host, v_bad, v_comp, v_blinded = load_verdicts(
                Path(verdicts).resolve()
            )
        except (FileNotFoundError, ValueError, KeyError, json.JSONDecodeError) as exc:
            msg = f"headtohead --verdicts error: {exc}"
            if json_output:
                output(error(msg, "BAD_INPUT"), json_mode=True)
            else:
                console.print(f"[red]Error:[/] {msg}")
            raise typer.Exit(2)
        # Reports in the manifest are ALREADY blinded; do not re-blind. The
        # scorecard's blinded flag is restored from the manifest below.
        card = run_head_to_head(
            v_qset,
            v_entrants,
            bad_name=v_bad,
            competitor_name=v_comp,
            judge=host,
            blind=False,
        )
        card.blinded = v_blinded
        card.llm_judged = True  # the host model IS the semantic judge (not the RubricJudge proxy)
        _write_and_report(card, out_dir, v_bad, v_comp, json_output)
        return

    # Resolve the query set + entrants. A bad path is a clean exit(2), not a crash.
    try:
        qset = load_query_set(query_set)
        if manifest is not None:
            man_bad, man_comp, entrants_by_qid = _load_manifest(manifest)
            # Manifest names win over the flag defaults unless the flag was set.
            if bad_name == "bad-research" and man_bad:
                bad_name = man_bad
            if competitor_name == "competitor" and man_comp:
                competitor_name = man_comp
        else:
            entrants_by_qid = _single_pair_entrants(
                bad_report=bad_report,
                competitor_report=competitor_report,
                query_id=query_id,
                bad_name=bad_name,
                competitor_name=competitor_name,
                qset=qset,
            )
    except (FileNotFoundError, ValueError, KeyError) as exc:
        msg = f"headtohead input error: {exc}"
        if json_output:
            output(error(msg, "BAD_INPUT"), json_mode=True)
        else:
            console.print(f"[red]Error:[/] {msg}")
        raise typer.Exit(2)

    # Score only the queries we actually have entrants for — you benchmark the
    # queries you ran, not the whole catalogue. This keeps a single-query smoke or
    # a partial manifest from padding the tally with phantom ties.
    scored_ids = set(entrants_by_qid)
    qset = [q for q in qset if q["id"] in scored_ids]
    if not qset:
        msg = "no query in the query set has any entrant reports — nothing to score."
        if json_output:
            output(error(msg, "NO_ENTRANTS"), json_mode=True)
        else:
            console.print(f"[red]Error:[/] {msg}")
        raise typer.Exit(2)

    entrants = {
        qid: [Entrant.from_json(e) for e in ents] for qid, ents in entrants_by_qid.items()
    }

    # ── KEYLESS host-judge emit: write blinded task files + manifest, then stop ──
    # The orchestrating Claude reads each *.task.md and writes the rails; ingest the
    # results later with `--verdicts <this dir>`. No scoring happens here.
    if emit_judge_tasks is not None:
        tasks_dir = Path(emit_judge_tasks).resolve()
        man = emit_judge_tasks_fn(
            qset,
            entrants,
            tasks_dir,
            bad_name=bad_name,
            competitor_name=competitor_name,
            blind=not no_blind,
        )
        n_tasks = len(man["tasks"])
        if json_output:
            output(success(man, count=n_tasks, vault=str(tasks_dir)), json_mode=True)
            return
        console.print(
            f"[bold]Head-to-head:[/] emitted [green]{n_tasks}[/] blinded judge task(s) "
            f"to {tasks_dir}"
        )
        console.print(
            "  Next: as the host judge, read each [cyan]*.task.md[/] and write its "
            "[cyan]<id>.verdict.json[/] rails,"
        )
        console.print(
            f"  then run [bold]bad headtohead --verdicts {tasks_dir}[/] for the scorecard. "
            "No API key needed."
        )
        return

    judge = _make_llm_judge() if llm else None

    # If --llm was requested but the host model is unavailable, fail clean.
    if llm and judge is None:
        msg = "headtohead --llm needs a host model (set ANTHROPIC_API_KEY) or drop --llm."
        if json_output:
            output(error(msg, "NO_PROVIDER"), json_mode=True)
        else:
            console.print(f"[red]Error:[/] {msg}")
        raise typer.Exit(1)

    card = run_head_to_head(
        qset,
        entrants,
        bad_name=bad_name,
        competitor_name=competitor_name,
        judge=judge,
        blind=not no_blind,
    )
    _write_and_report(card, out_dir, bad_name, competitor_name, json_output)


def _write_and_report(
    card: Scorecard, out_dir: Path, bad_name: str, competitor_name: str, json_output: bool
) -> None:
    """Write the scorecard (JSON + markdown) and print/emit the summary. Shared by
    the default/--llm scoring path and the keyless --verdicts ingest path."""
    json_path = out_dir / "headtohead-scorecard.json"
    md_path = out_dir / "headtohead-scorecard.md"
    json_path.write_text(card.to_json(), encoding="utf-8")
    md_path.write_text(card.to_markdown(), encoding="utf-8")

    if json_output:
        output(success(card.to_dict(), count=len(card.results), vault=str(out_dir)), json_mode=True)
        return

    t = card.tally
    console.print(f"[bold]Head-to-head:[/] {bad_name} vs {competitor_name}")
    console.print(f"  {card.verdict_line()}")
    console.print(
        f"  W [green]{t['win']}[/] / T [yellow]{t['tie']}[/] / L [red]{t['loss']}[/] "
        f"(bad-research POV, {len(card.results)} queries)"
    )
    console.print(f"\n[green]Wrote[/] {json_path}\n[green]Wrote[/] {md_path}")


def _read_text(base: Path, ref: str) -> str:
    """Read a report file referenced (relative to `base`) by a manifest/flag."""
    p = (base / ref) if not Path(ref).is_absolute() else Path(ref)
    if not p.exists():
        raise FileNotFoundError(f"report file not found: {p}")
    return p.read_text(encoding="utf-8")


def _read_corpus(base: Path, ref: str | None) -> list[dict[str, Any]]:
    """Read an optional corpus file (JSON list of note dicts). None/missing → []."""
    if not ref:
        return []
    p = (base / ref) if not Path(ref).is_absolute() else Path(ref)
    if not p.exists():
        raise FileNotFoundError(f"corpus file not found: {p}")
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"corpus file {p} must be a JSON list of note objects")
    return list(data)


def _load_manifest(manifest: str) -> tuple[str | None, str | None, dict[str, list[dict[str, Any]]]]:
    """Resolve a per-query entrant manifest into entrant dicts (reports inlined).
    Returns (bad_name, competitor_name, {qid: [entrant_dict, ...]})."""
    man_path = Path(manifest).resolve()
    if not man_path.exists():
        raise FileNotFoundError(f"manifest not found: {man_path}")
    data = json.loads(man_path.read_text(encoding="utf-8"))
    base = man_path.parent
    raw = data.get("entrants", {})
    if not isinstance(raw, dict):
        raise ValueError("manifest 'entrants' must be a {query_id: [entrant, ...]} object")
    by_qid: dict[str, list[dict[str, Any]]] = {}
    for qid, ents in raw.items():
        resolved: list[dict[str, Any]] = []
        for e in ents:
            report = e.get("report") or _read_text(base, e["report_file"])
            corpus = e.get("corpus") or _read_corpus(base, e.get("corpus_file"))
            resolved.append(
                {
                    "name": str(e["name"]),
                    "report": report,
                    "corpus": corpus,
                    "cost_usd": float(e.get("cost_usd", 0.0) or 0.0),
                    "latency_s": float(e.get("latency_s", 0.0) or 0.0),
                }
            )
        by_qid[str(qid)] = resolved
    return data.get("bad_name"), data.get("competitor_name"), by_qid


def _single_pair_entrants(
    *,
    bad_report: str | None,
    competitor_report: str | None,
    query_id: str | None,
    bad_name: str,
    competitor_name: str,
    qset: list[dict[str, str]],
) -> dict[str, list[dict[str, Any]]]:
    """Build a one-query entrant map from the --bad-report/--competitor-report pair."""
    if not (bad_report and competitor_report and query_id):
        raise ValueError(
            "single-query mode needs --bad-report, --competitor-report and --query-id "
            "(or pass --manifest for a full set)"
        )
    known = {q["id"] for q in qset}
    if query_id not in known:
        raise ValueError(f"--query-id {query_id!r} is not in the query set")
    cwd = Path.cwd()
    return {
        query_id: [
            {"name": bad_name, "report": _read_text(cwd, bad_report), "corpus": []},
            {"name": competitor_name, "report": _read_text(cwd, competitor_report), "corpus": []},
        ]
    }


def _make_llm_judge() -> LLMJudge | None:
    """Construct an LLMJudge for the --llm path. Returns None if no host model is
    available (the caller then fails clean instead of crashing)."""
    try:
        from bad_research.calibrate.judge import LLMJudge
        from bad_research.llm.base import get_llm_provider

        return LLMJudge(provider=get_llm_provider())
    except Exception:
        return None


__all__ = ["headtohead"]
