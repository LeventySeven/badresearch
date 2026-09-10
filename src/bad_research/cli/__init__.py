"""Bad Research CLI — the `bad`/`badr` Typer app.

The single-file `cli.py` was promoted to a package so the research-pipeline
subcommands (`cli/research.py`) and the asset-saver (`cli/fetch.py`, imported
lazily by `core/fetcher.py`) live alongside the app without circular imports.
"""

from __future__ import annotations

import typer

from bad_research import __version__


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"bad-research v{__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="bad",
    help="michael jackson bad — deep-research agent.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-V", callback=_version_callback, is_eager=True,
        help="Show version",
    ),
) -> None:
    pass


# ── install command (Task 13) ────────────────────────────────────────────────
from bad_research.cli.install import install as _install_cmd

app.command("install")(_install_cmd)

# ── research-pipeline subcommands (Task 12) ──────────────────────────────────
from bad_research.cli.research import (
    funnel_gather_cmd,
    grade_report_cmd,
    recitation_gate_cmd,
    retrieve_cmd,
    route_cmd,
    uncited_gate_cmd,
    verify_citations_cmd,
)

app.command("route")(route_cmd)
app.command("funnel-gather")(funnel_gather_cmd)
app.command("retrieve")(retrieve_cmd)
app.command("verify-citations")(verify_citations_cmd)
app.command("uncited-gate")(uncited_gate_cmd)
app.command("grade-report")(grade_report_cmd)
app.command("recitation-gate")(recitation_gate_cmd)

# ── doctor + calibrate commands (Plan 09) ────────────────────────────────────
from bad_research.cli.calibrate import calibrate as _calibrate_cmd
from bad_research.cli.doctor import doctor as _doctor_cmd

app.command("doctor")(_doctor_cmd)
app.command("calibrate")(_calibrate_cmd)

# ── head-to-head benchmark (honesty-audit row 11) ────────────────────────────
from bad_research.cli.headtohead import headtohead as _headtohead_cmd

app.command("headtohead")(_headtohead_cmd)

# ── vault lifecycle + corpus inspection (wire-missing-cli-commands) ───────────
from bad_research.cli.vault_cmds import (
    archive_run_cmd,
    fetch_cmd,
    init_cmd,
    lint_cmd,
    note_app,
    search_cmd,
    vault_tag_cmd,
)

app.command("init")(init_cmd)
app.command("vault-tag")(vault_tag_cmd)
app.command("archive-run")(archive_run_cmd)
app.command("search")(search_cmd)
app.command("fetch")(fetch_cmd)
app.command("lint")(lint_cmd)
app.add_typer(note_app, name="note")

# ── assets subcommand (host-vision multimodal path) ──────────────────────────
from bad_research.cli.assets import assets_app

app.add_typer(assets_app, name="assets")

# ── export + grounding sidecars (Road-to-9 levers #7/#8/#9) ───────────────────
from bad_research.cli.export import export_cmd as _export_cmd
from bad_research.cli.grounding_surface import (
    grounding_recall_cmd as _grounding_recall_cmd,
)
from bad_research.cli.grounding_surface import (
    grounding_surface_cmd as _grounding_surface_cmd,
)

app.command("export")(_export_cmd)
app.command("grounding-surface")(_grounding_surface_cmd)
app.command("grounding-recall")(_grounding_recall_cmd)

# ── local-corpus lane (research rebuild, slice 1) ─────────────────────────────
from bad_research.cli.lanes import lane_local_cmd as _lane_local_cmd

app.command("lane-local")(_lane_local_cmd)

from bad_research.cli.frontier_cmds import frontier_gate_cmd, frontier_observe_cmd

app.command("frontier-gate")(frontier_gate_cmd)
app.command("frontier-observe")(frontier_observe_cmd)

from bad_research.cli.close_gate_cmds import close_gate_cmd

app.command("close-gate")(close_gate_cmd)

# ── deterministic report checks (research rebuild, slice 1) ───────────────────
from bad_research.cli.checks import no_source_claim_gate_cmd as _no_source_claim_cmd
from bad_research.cli.checks import quote_drift_gate_cmd as _quote_drift_cmd

app.command("no-source-claim-gate")(_no_source_claim_cmd)
app.command("quote-drift-gate")(_quote_drift_cmd)

from bad_research.cli.checks import figure_support_gate_cmd as _figure_support_cmd

app.command("figure-support-gate")(_figure_support_cmd)

from bad_research.cli.checks import absence_gate_cmd as _absence_cmd

app.command("absence-gate")(_absence_cmd)

from bad_research.cli.coverage_cmds import coverage_cmd as _coverage_cmd

app.command("coverage")(_coverage_cmd)

from bad_research.cli.discriminate_cmds import discriminate_cmd as _discriminate_cmd

app.command("discriminate")(_discriminate_cmd)

from bad_research.cli.discriminate_cmds import screening_stop_cmd as _screening_stop_cmd

app.command("screening-stop")(_screening_stop_cmd)

from bad_research.cli.discriminate_cmds import cascade_cmd as _cascade_cmd

app.command("cascade")(_cascade_cmd)

__all__ = ["app"]
