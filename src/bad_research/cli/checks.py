"""`bad no-source-claim-gate` — block a report that claims an absence its own corpus fills.

Thin shell over `checks.no_source_claim`: no ranking, no rewriting, no LLM. The
enumeration line goes out first on both paths, so a run that found nothing still
reports how many notes it read and how many absence claims it examined — the
difference between an honest clean and a gate that never looked.

Exit 1 when there are findings, 0 when clean, 2 when the inputs could not be
read (an unreadable input must never be mistaken for a pass).
"""

from __future__ import annotations

import json
from pathlib import Path

import typer

from bad_research.checks.figure_support import check_figure_support
from bad_research.checks.no_source_claim import (
    count_absence_claims,
    find_unfounded_absence_claims,
)
from bad_research.checks.quote_drift import check_quote_drift

# Note bodies on disk. Flat glob, text only — a directory of notes is a
# directory of notes, not a tree to recurse into.
_NOTE_SUFFIXES = ("*.md", "*.txt")

# The keys a JSON note record may use for its id and its body, in preference
# order. Matches the `{note_id, url, text}` corpus shape `grade-report` takes.
_ID_KEYS = ("note_id", "id", "slug")
_BODY_KEYS = ("text", "body", "content", "summary")


def _fail(message: str) -> typer.Exit:
    typer.echo(message)
    return typer.Exit(2)


def _load_notes(path: Path) -> dict[str, str]:
    """Read `{note_id: body}` from a JSON file or a directory of note files."""
    if path.is_dir():
        notes: dict[str, str] = {}
        for pattern in _NOTE_SUFFIXES:
            for file in sorted(path.glob(pattern)):
                notes[file.stem] = file.read_text(encoding="utf-8", errors="replace")
        return notes

    if not path.is_file():
        raise _fail(f"no-source-claim: notes path not found: {path}")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise _fail(f"no-source-claim: could not parse notes JSON {path}: {exc}")

    if isinstance(payload, dict):
        return {str(k): str(v) for k, v in payload.items()}
    if isinstance(payload, list):
        records: dict[str, str] = {}
        for i, item in enumerate(payload):
            if not isinstance(item, dict):
                raise _fail(f"no-source-claim: notes list item {i} is not an object")
            note_id = next((str(item[k]) for k in _ID_KEYS if k in item), f"note-{i}")
            body = next((str(item[k]) for k in _BODY_KEYS if k in item), "")
            records[note_id] = body
        return records
    raise _fail(
        f"no-source-claim: notes JSON must be an object or a list of objects, "
        f"got {type(payload).__name__}"
    )


def no_source_claim_gate_cmd(
    report: str = typer.Option(..., "--report", help="Path to the report markdown."),
    notes: str = typer.Option(
        ...,
        "--notes",
        help="JSON {note_id: body} map, a JSON list of note records, or a "
             "directory of .md/.txt note files.",
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="Emit JSON."),
) -> None:
    """Flag absence claims ("no source was found for X") the corpus contradicts.

    Fires only when two or more content words from the claim's subject co-occur
    in one note body — one shared word is coincidence, not coverage."""
    report_path = Path(report)
    if not report_path.is_file():
        raise _fail(f"no-source-claim: report not found: {report_path}")
    body = report_path.read_text(encoding="utf-8", errors="replace")

    note_bodies = _load_notes(Path(notes))
    examined = count_absence_claims(body)
    findings = find_unfounded_absence_claims(body, note_bodies)

    if json_output:
        typer.echo(json.dumps({
            "check": "no-source-claim",
            "notes_scanned": len(note_bodies),
            "absence_claims_examined": examined,
            "findings": [f.to_dict() for f in findings],
        }, ensure_ascii=False))
    else:
        typer.echo(
            f"no-source-claim | notes scanned {len(note_bodies)} | "
            f"absence claims examined {examined} | findings {len(findings)}"
        )
        for f in findings:
            typer.echo(
                f"{f.note_id} | claimed missing: {f.subject} | "
                f"present in note: {', '.join(f.matched_words)}"
            )

    if findings:
        raise typer.Exit(1)


__all__ = ["no_source_claim_gate_cmd"]


def quote_drift_gate_cmd(
    report: Path = typer.Option(..., "--report", help="The report about to ship."),
    note_bodies: Path = typer.Option(
        ..., "--note-bodies", "--sources", help="JSON {note_id: body} map, in source order."
    ),
    json_out: bool = typer.Option(False, "--json", "-j", help="Emit findings as JSON."),
) -> None:
    """Verify every attributed quotation against the note it cites. Exit 1 on any drift.

    Quotation marks assert that a source contains exactly these bytes. That is
    checkable for nothing, and it is the one claim in a research report that does
    not need a judge -- which is why it, and not a 55-60 BAcc semantic verdict,
    is what gets to close a ship decision.
    """
    bodies = json.loads(note_bodies.read_text(encoding="utf-8"))
    result = check_quote_drift(report.read_text(encoding="utf-8"), bodies, list(bodies))

    if json_out:
        typer.echo(json.dumps(result.to_dict(), indent=2))
    else:
        counts: dict[str, int] = {}
        for f in result.findings:
            counts[f.outcome] = counts.get(f.outcome, 0) + 1
        typer.echo(
            "quote-drift | attributed quotations checked "
            f"{len(result.findings)} | "
            + (" ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "none found")
        )
        for f in result.findings:
            if f.outcome == "MATCHED":
                continue
            where = f" (the words are in {f.found_in})" if f.found_in else ""
            typer.echo(f"  - {f.outcome}{where}: [{f.marker}] -> {f.cited_note} :: {f.quoted[:90]!r}")
        typer.echo("PASS | every attributed quotation is byte-identical to its note"
                   if result.ok else "REFUSE | a quotation does not match the source it cites")

    if not result.ok:
        raise typer.Exit(code=1)


def figure_support_gate_cmd(
    report: Path = typer.Option(..., "--report", help="The report about to ship."),
    note_bodies: Path = typer.Option(..., "--note-bodies", "--sources", help="JSON {note_id: body}, in source order."),
    json_out: bool = typer.Option(False, "--json", "-j", help="Emit findings as JSON."),
) -> None:
    """Every cited sentence's NUMBERS must appear in the note it cites. Exit 1 on any that do not.

    Closes the numeric half of the cite-everything hole. A draft whose every
    sentence is false but carries a resolving marker passes `uncited-gate`
    clean; most fabricated research claims fabricate a quantity, and that half
    is a fact about two strings. Reports its own blind spot: `unchecked` counts
    cited sentences carrying no number, which this gate cannot see.
    """
    bodies = json.loads(note_bodies.read_text(encoding="utf-8"))
    result = check_figure_support(report.read_text(encoding="utf-8"), bodies, list(bodies))

    if json_out:
        typer.echo(json.dumps(result.to_dict(), indent=2))
    else:
        typer.echo(
            f"figure-support | figures checked {result.checked} "
            f"| cited sentences with no figure (UNCHECKABLE here) {result.unchecked} "
            f"| findings {len(result.findings)}"
        )
        for f in result.findings:
            typer.echo(f"  - {f.outcome}: {f.quantity} cited to {f.cited_note} :: {f.sentence[:80]!r}")
        typer.echo("PASS | every cited figure appears in the note it cites"
                   if result.ok else "REFUSE | a cited figure does not appear in its source")
    if not result.ok:
        raise typer.Exit(code=1)


def absence_gate_cmd(
    report: Path = typer.Option(..., "--report", help="Path to the report markdown."),
    json_out: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """List the report's absence claims, flagging the ones that name no search scope.

    An absence claim is the one sentence class no other gate can reach: `quote-drift`
    needs a quotation, `figure-support` needs a figure, `no-source-claim` needs a claim
    that has a source to be missing. An absence cites nothing by construction and its
    "source" is the whole world.

    This is a TRIAGE LIST, not a verdict. It cannot tell you an absence is false --
    only finding the thing can. What it can tell you is which of your absence claims
    are stated in a form nobody could falsify, which is the form that shipped a claim
    a blind judge overturned in one fetch.

    Exit 1 when any absence claim names no search scope.
    """
    from bad_research.checks.absence_claim import find_absence_claims

    r = find_absence_claims(report.read_text(encoding="utf-8"))
    if json_out:
        typer.echo(json.dumps(r.to_dict(), indent=2))
    else:
        typer.echo(f"absence-gate | {len(r.claims)} absence claim(s) | "
                   f"{len(r.unscoped)} name no search scope")
        for c in r.claims:
            mark = "UNSCOPED" if not c.scoped else f"scoped [{c.scope}]"
            typer.echo(f"  {mark:30s} L{c.line}: {c.sentence[:76]}")
        typer.echo(f"\n  {r.caveat}")
    if not r.ok:
        raise typer.Exit(code=1)
