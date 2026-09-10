"""`bad close-gate` -- the executing form of "an open disagreement blocks the finish".

The rule states itself in one line and is worth about nothing that way: prose on
a post-trained model buys single-digit compliance, and the behaviour it asks for
(keep the number that makes your answer messier) is the one the model has the
least appetite for. So the rule exits non-zero instead.

One command takes a run from raw claims to a verdict: pair the claims, decide
which disagreements the draft actually touches, and refuse the close while any
of those is unrecorded or has quietly lost a side.
"""

from __future__ import annotations

import json as _json
from pathlib import Path

import typer

from bad_research.checks.close_gate import Disposition, evaluate_close
from bad_research.checks.contradiction import Claim, find_contradictions


def _load_claims(path: Path) -> list[Claim]:
    raw = _json.loads(path.read_text(encoding="utf-8"))
    rows = raw["claims"] if isinstance(raw, dict) else raw
    return [
        Claim(
            subject=r["subject"],
            value=str(r["value"]),
            unit=r.get("unit", ""),
            source=r["source"],
            as_of=r.get("as_of"),
        )
        for r in rows
    ]


def _load_dispositions(path: Path | None) -> list[Disposition]:
    if path is None:
        return []
    raw = _json.loads(path.read_text(encoding="utf-8"))
    # `{}` is a legal way to say "no dispositions yet" and used to raise KeyError,
    # which reads as a broken command rather than an empty input. Found cold.
    rows = raw.get("dispositions", []) if isinstance(raw, dict) else raw
    return [
        Disposition(
            contradiction_id=r["contradiction_id"],
            kind=r["kind"],
            because=r.get("because", ""),
        )
        for r in rows
    ]


def close_gate_cmd(
    claims: Path = typer.Option(..., "--claims", help="JSON list of {subject,value,unit,source,as_of}."),
    answer: Path = typer.Option(..., "--answer", help="The draft answer about to ship."),
    dispositions: Path = typer.Option(
        None, "--dispositions", help="JSON list of {contradiction_id,kind,because}."
    ),
    rel_tolerance: float = typer.Option(
        0.01, "--rel-tolerance", help="Relative gap below which two numbers agree."
    ),
    json_out: bool = typer.Option(False, "--json", help="Emit the report as JSON."),
) -> None:
    """Refuse the close while a load-bearing disagreement is open. Exit 1 when blocked."""
    body = answer.read_text(encoding="utf-8")
    found = find_contradictions(_load_claims(claims), rel_tolerance=rel_tolerance)
    report = evaluate_close(found, body, _load_dispositions(dispositions))

    payload = report.to_dict()
    payload["found"] = len(found)
    payload["suppressed_by_cap"] = found.suppressed

    if json_out:
        typer.echo(_json.dumps(payload, indent=2))
    else:
        typer.echo(
            f"contradictions found {len(found)} "
            f"| load-bearing {len(report.load_bearing)} "
            f"| cosmetic {len(report.cosmetic)} "
            f"| suppressed by cap {found.suppressed}"
        )
        if report.can_close:
            typer.echo("ALLOW | every load-bearing disagreement is disposed and both sides survive")
        else:
            typer.echo(f"REFUSE | {len(report.blockers)} blocker(s):")
            for b in report.blockers:
                typer.echo(f"  - [{b.contradiction_id}] {b.reason}")

    if not report.can_close:
        raise typer.Exit(code=1)
