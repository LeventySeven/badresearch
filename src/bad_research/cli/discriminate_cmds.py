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


def screening_stop_cmd(
    found: int = typer.Option(..., "--found", help="Relevant items screening has turned up so far."),
    unseen: int = typer.Option(..., "--unseen", help="Size of the not-yet-screened remainder."),
    sample: int = typer.Option(..., "--sample", help="How many you drew AT RANDOM from that remainder."),
    sample_relevant: int = typer.Option(0, "--sample-relevant", help="Relevant items in that sample."),
    target_recall: float = typer.Option(0.95, "--target-recall"),
    alpha: float = typer.Option(0.05, "--alpha"),
    json_out: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """May the screen stop, at a stated recall with a stated confidence? Exit 1 if not.

    The alternative is stopping when the hits feel like they have dried up, which
    is how a breadth run ends with no error bar at all.
    """
    from bad_research.checks.screening_stop import can_stop

    v = can_stop(found, unseen, sample, sample_relevant,
                 target_recall=target_recall, alpha=alpha)
    if json_out:
        typer.echo(json.dumps(v.to_dict(), indent=2))
    else:
        typer.echo(f"screening-stop | found {found} | unseen {unseen} | "
                   f"random sample {sample} -> {sample_relevant} relevant")
        typer.echo(f"  may miss at most {v.max_missable} and still hold {target_recall:.0%} recall")
        typer.echo(f"  p = {v.p_value:.4f}   {'STOP' if v.stop else 'KEEP SCREENING'}")
        typer.echo(f"  {v.why}")
        typer.echo(f"  {v.caveat}")
    if not v.stop:
        raise typer.Exit(code=1)


def cascade_cmd(
    candidates: Path = typer.Option(..., "--candidates", help="One candidate per line."),
    decisions: Path = typer.Option(None, "--decisions", help="JSON list of {item,verdict,because} the run already made. Omit on run 1."),
    canaries: Path = typer.Option(None, "--canaries", help="Known-good items that MUST survive. One per line."),
    json_out: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """Screen in two layers: the free fixed web prefilter, then what this run learned.

    The ordering is the point. The fixed layer costs nothing and never improves;
    the learned one costs decisions and compounds, so it should never spend a
    decision on something already obviously junk. Every cut names the layer that
    made it, because a regex's `reject` and a run's `reject` are different claims.

    The layer counts carry `web-prefilter-skipped` explicitly: an item with no URL
    in it -- a person, a filename, a transcript heading -- is invisible to the web
    layer, and a layer that cannot see an item must not be recorded as having
    passed it.
    """
    from bad_research.checks.cascade import cascade_screen

    d = Discriminator(canaries=set(_lines(canaries)) if canaries else set())
    if decisions:
        raw = json.loads(decisions.read_text(encoding="utf-8"))
        for r in (raw["decisions"] if isinstance(raw, dict) else raw):
            d.record(Decision(r["item"], r["verdict"], r.get("because", "")))

    report = cascade_screen(_lines(candidates), d)

    if json_out:
        typer.echo(json.dumps({**report.to_dict(),
                               "learned_signals": d.reject_signals()}, indent=2))
    else:
        typer.echo(f"cascade | considered {report.considered} | kept {len(report.kept)} "
                   f"| cut {len(report.rejected)}")
        for layer, n in sorted(report.by_layer.items()):
            typer.echo(f"    {layer:24s} {n}")
        for c in report.rejected[:8]:
            typer.echo(f"    CUT  {c.item[:52]:52s} <- {c.because}")
        if report.canaries_killed:
            typer.echo(f"\n  CANARY DEAD ({len(report.canaries_killed)}):")
            for c in report.canaries_killed:
                typer.echo(f"    {c.item[:52]:52s} <- {c.because}")
        typer.echo(f"\n  {report.caveat}")

    if report.safe is False:
        raise typer.Exit(code=1)
