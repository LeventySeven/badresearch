"""`bad coverage` — how much of the population did the run actually find?

Every other gate here is scoped to what the answer already contains. On a
"find all X" question that is the wrong axis: an answer can be perfectly precise
and miss most of the population, and nothing else would say so. This is the only
command in the kit that measures RECALL, and it does it the one honest way
available for a set nobody can count — capture-recapture over passes that do not
share a method.
"""

from __future__ import annotations

import json
from pathlib import Path

import typer

from bad_research.checks.coverage import CaptureRecapture, estimate_coverage


def _load(path: Path) -> set[str]:
    """One item per line, or a JSON list. Blank lines and `#` comments ignored."""
    text = path.read_text(encoding="utf-8").strip()
    if text.startswith("["):
        return {str(x).strip() for x in json.loads(text) if str(x).strip()}
    return {
        ln.split("|")[0].strip()
        for ln in text.splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")
    }


def coverage_cmd(
    pass_: list[str] = typer.Option(
        ..., "--pass", help="lane=path, repeatable. The lane NAME matters: two rank-ordered "
                            "lanes are refused as dependent."
    ),
    json_out: bool = typer.Option(False, "--json", "-j", help="Emit as JSON."),
) -> None:
    """Estimate what fraction of the population the run found. Exit 1 if it cannot estimate."""
    cr = CaptureRecapture()
    for spec in pass_:
        lane, _, p = spec.partition("=")
        if not p:
            raise typer.BadParameter(f"expected lane=path, got {spec!r}")
        cr.add(lane.strip(), _load(Path(p)))

    names = sorted(cr.lanes)
    pairs = [
        (x, y, estimate_coverage(cr.lanes[x], cr.lanes[y], lane_a=x, lane_b=y))
        for i, x in enumerate(names) for y in names[i + 1:]
    ]
    total = cr.best_estimate()
    payload = {
        "found": cr.found,
        "lanes": {k: len(v) for k, v in cr.lanes.items()},
        "estimated_total": total,
        "coverage": (cr.found / total) if total else None,
        "singleton_fraction": cr.singleton_fraction(),
        "pairs": [{"a": a, "b": b, **e.to_dict()} for a, b, e in pairs],
    }

    if json_out:
        typer.echo(json.dumps(payload, indent=2))
    else:
        typer.echo(f"coverage | held {cr.found} across {len(cr.lanes)} passes "
                   f"({', '.join(f'{k} {len(v)}' for k, v in sorted(cr.lanes.items()))})")
        for a, b, e in pairs:
            if e.estimated_total:
                typer.echo(f"  {a} x {b}: overlap {e.overlap} -> population ~{e.estimated_total:.0f}, "
                           f"coverage {e.coverage:.0%}")
            else:
                typer.echo(f"  {a} x {b}: NO ESTIMATE — {e.caveat.split(' — ')[0]}")
        if total:
            typer.echo(f"\n  least-flattering population ~{total:.0f} "
                       f"-> coverage ~{cr.found / total:.0%}, ~{total - cr.found:.0f} still unfound")
        typer.echo(f"  singletons: {cr.singleton_fraction():.0%} of what you hold was seen by ONE pass"
                   + ("  <-- the tail is undersampled; trust the estimate less"
                      if cr.singleton_fraction() > 0.5 else ""))
        if not total:
            typer.echo("\nREFUSE | no independent pair — coverage is unmeasured, not high")

    if not total:
        raise typer.Exit(code=1)
