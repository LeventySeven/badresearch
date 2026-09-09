"""`bad discriminate` — screen candidates with what the run has learned, and check it did not over-learn."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from bad_research.checks.discriminate import Decision, Discriminator


def _lines(p: Path) -> list[str]:
    return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")]


def discriminate_cmd(
    decisions: Path = typer.Option(..., "--decisions", help="JSON list of {item,verdict,because} the run already made."),
    candidates: Path = typer.Option(..., "--candidates", help="One candidate per line."),
    canaries: Path = typer.Option(None, "--canaries", help="Known-good items that MUST survive. One per line."),
    json_out: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """Screen candidates using reject-signals learned from prior decisions. Exit 1 if a canary dies.

    The filter is a function of the run's own history, so it sharpens as the run
    learns -- and the canaries are what stop it sharpening into something that
    deletes the best source. With no canaries the verdict is UNMEASURED, never
    safe: an unwatched filter and a good one must not print the same way.
    """
    raw = json.loads(decisions.read_text(encoding="utf-8"))
    rows = raw["decisions"] if isinstance(raw, dict) else raw
    d = Discriminator(canaries=set(_lines(canaries)) if canaries else set())
    for r in rows:
        d.record(Decision(r["item"], r["verdict"], r.get("because", "")))

    report = d.screen(_lines(candidates))
    signals = d.reject_signals()

    if json_out:
        typer.echo(json.dumps({**report.to_dict(), "learned_signals": signals}, indent=2))
    else:
        typer.echo(f"discriminate | {len(rows)} prior decisions -> {len(signals)} learned reject-signals")
        if signals:
            top = sorted(signals.items(), key=lambda kv: -kv[1])[:6]
            typer.echo("  learned: " + ", ".join(f"{t!r} x{n}" for t, n in top))
        typer.echo(f"  considered {report.considered} | kept {len(report.kept)} | cut {len(report.rejected)}")
        for c in report.rejected[:8]:
            typer.echo(f"    CUT  {c.item[:58]:58s} <- {c.because}")
        if report.canaries_killed:
            typer.echo(f"\n  CANARY DEAD ({len(report.canaries_killed)}):")
            for c in report.canaries_killed:
                typer.echo(f"    {c.item[:58]:58s} <- {c.because}")
        if report.canaries_untested:
            typer.echo(f"\n  CANARIES THAT TESTED NOTHING ({len(report.canaries_untested)}): "
                       "no shared vocabulary with this pool")
            for c in report.canaries_untested:
                typer.echo(f"    {c[:70]}")
        typer.echo(f"\n  {report.caveat}")

    if report.safe is False:
        raise typer.Exit(code=1)
