"""`bad grounding-surface` — surface the ALREADY-computed per-claim grounding
ledger as a shareable markdown/JSON appendix.

The CitationVerifier (grounding/verifier.py) already computes, for every cited
sentence: a verdict (supported|partial|unsupported|contradicted), a verify_score, a
confidence_band (high|medium|low), and — on the keyless path — a needs_host_judgment
flag for the paraphrase band the orchestrator resolves inline. No hosted deep-research
tool exposes a per-claim confidence ledger; this command makes that auditability moat
clickable, as an opt-in SIDECAR.

It does NOT modify the verifier — it reuses `cli/research._verify_report` (the same
adapter `bad verify-citations` uses) and only RENDERS its findings. Keyless: same
seam as the verifier (host-model judge when wired; deterministic Tier-A/B otherwise).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer

# Render order: contradicted/unsupported first (the claims a reader most needs to
# inspect), then partial, then supported. A stable rank for the ledger table.
_VERDICT_RANK = {
    "contradicted": 0,
    "unsupported": 1,
    "partial": 2,
    "supported": 3,
}

_BAND_ICON = {"high": "high", "medium": "med", "low": "low"}


def _sentence_preview(sentence: str, *, width: int = 100) -> str:
    """A one-line, citation-stripped preview of the claim sentence for the table."""
    import re

    bare = re.sub(r"\[\[[^\]]+\]\]|\[\d+\]", "", sentence or "")
    bare = re.sub(r"\s+", " ", bare).strip()
    bare = bare.replace("|", r"\|")  # don't break the markdown table
    return bare if len(bare) <= width else bare[: width - 1].rstrip() + "…"


def render_ledger_markdown(findings: list[dict[str, Any]]) -> str:
    """Render the verifier findings as a markdown per-claim grounding ledger.

    Columns: verdict, confidence band, verify_score, whether the keyless path left
    it for host judgment, and a preview of the claim. A summary line precedes the
    table. Honest about the keyless gap: rows flagged `needs_host_judgment` are the
    paraphrase band the deterministic guards do NOT decide keyless."""
    if not findings:
        return "## Grounding ledger\n\n_No cited claims found in this report._\n"

    n = len(findings)
    counts: dict[str, int] = {}
    for f in findings:
        counts[f.get("verdict", "unsupported")] = counts.get(f.get("verdict", "unsupported"), 0) + 1
    n_host = sum(1 for f in findings if f.get("needs_host_judgment"))

    summary = (
        f"{n} cited claim(s): "
        + ", ".join(f"{counts[v]} {v}" for v in sorted(counts, key=lambda v: _VERDICT_RANK.get(v, 9)))
        + "."
    )
    if n_host:
        summary += (
            f" {n_host} claim(s) flagged `needs_host_judgment` — the keyless "
            "deterministic guards routed these paraphrase-band claims to the host "
            "model for an inline support call (they are NOT decided keyless)."
        )

    rows = sorted(
        findings,
        key=lambda f: (_VERDICT_RANK.get(f.get("verdict", "unsupported"), 9), -float(f.get("score", 0.0))),
    )
    lines = [
        "## Grounding ledger",
        "",
        summary,
        "",
        "Per-claim grounding from the CitationVerifier (Tier-A byte-identity → "
        "Tier-B lexical/NLI → Tier-C host judge). Each row is one cited sentence.",
        "",
        "| # | Verdict | Band | Score | Host-judged | Claim |",
        "|---|---------|------|-------|-------------|-------|",
    ]
    for i, f in enumerate(rows, start=1):
        verdict = f.get("verdict", "unsupported")
        band = _BAND_ICON.get(f.get("confidence_band") or "", f.get("confidence_band") or "—")
        score = float(f.get("score", 0.0))
        host = "yes" if f.get("needs_host_judgment") else "—"
        claim = _sentence_preview(f.get("sentence", ""))
        lines.append(f"| {i} | {verdict} | {band} | {score:.2f} | {host} | {claim} |")
    return "\n".join(lines) + "\n"


def grounding_surface_cmd(
    report: str = typer.Option(..., "--report", help="Path to the final report markdown."),
    vault_tag: str = typer.Option("", "--vault-tag", help="Vault tag (passed to the verifier adapter)."),
    effort: str = typer.Option(
        None, "--effort",
        help="minimal|low|medium|high; 'high' uses the verifier's self-consistency "
             "vote on the high-stakes band (keyless, N host samples).",
    ),
    note_bodies: str = typer.Option(
        None, "--note-bodies", "--sources",
        help="JSON {id: body} map — grade a report with no vault behind it.",
    ),
    out: str = typer.Option(
        None, "--out", "-o",
        help="Write the markdown ledger to this path (default: stdout / JSON).",
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="Emit the ledger as JSON."),
) -> None:
    """Render the per-claim grounding ledger (verdict, confidence band, score,
    deciding tier) for REPORT as a markdown/JSON sidecar.

    Reuses the CitationVerifier output (does not modify the verifier). On the
    keyless path the paraphrase band is flagged `needs_host_judgment` rather than
    silently rubber-stamped — the honest auditability surface.

    Standalone: pass `--note-bodies`/`--sources` (a JSON {id: body} map) to grade a
    report that has no vault behind it. The shared adapter `_verify_report` has
    accepted that argument all along and its two siblings (`verify-citations`,
    `uncited-gate`) expose it; this command did not, so on any report whose sources
    are files or URLs the ledger bound zero anchors and printed "No cited claims
    found" — a clean-looking empty that is indistinguishable from a clean report."""
    from bad_research.cli.research import _verify_report

    if not Path(report).is_file():
        raise typer.BadParameter(f"report not found: {report}")

    findings = _verify_report(report, vault_tag, effort=effort, note_bodies_path=note_bodies)

    if json_output:
        n_host = sum(1 for f in findings if f.get("needs_host_judgment"))
        typer.echo(json.dumps({
            "report": report,
            "n_claims": len(findings),
            "n_needs_host_judgment": n_host,
            "ledger": findings,
        }, default=str))
        return

    md = render_ledger_markdown(findings)
    if out:
        out_path = Path(out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        typer.echo(f"Wrote grounding ledger: {out_path} ({len(findings)} claim(s))")
    else:
        typer.echo(md)


def grounding_recall_cmd(
    fixtures: str = typer.Option(
        None, "--fixtures",
        help="JSON file: a list of {claim, quote} known-grounded pairs. Default: "
             "the built-in fixtures.",
    ),
    floor: float = typer.Option(
        None, "--floor",
        help="Regression floor on the deterministic-band catch-rate (default: the "
             "harness's REGRESSION_FLOOR). Exit non-zero if the catch-rate drops below it.",
    ),
    json_output: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """Grounding-recall harness: mutate known-grounded claims (number/negation/
    antonym/unsupported-append + the disclosed paraphrase-contradiction band) and
    print the KEYLESS deterministic guards' per-mutation catch-rate.

    HONEST by design: no LLM is consulted (a FakeLLM scripting the verdict would be
    circular), so the catch-rates measure only the deterministic layer. The
    paraphrase-contradiction band is reported as keyless-undecided BY DESIGN and is
    EXCLUDED from the regression floor. Exits non-zero if the deterministic-band
    catch-rate drops below the floor."""
    from bad_research.grounding.recall_harness import (
        REGRESSION_FLOOR,
        builtin_fixtures,
        format_report_text,
        load_fixtures,
        run_recall,
    )

    claims = load_fixtures(Path(fixtures)) if fixtures else builtin_fixtures()
    report = run_recall(claims)
    effective_floor = REGRESSION_FLOOR if floor is None else floor

    if json_output:
        payload = report.to_dict()
        payload["regression_floor"] = effective_floor
        payload["regression_pass"] = report.deterministic_catch_rate() >= effective_floor
        typer.echo(json.dumps(payload))
    else:
        typer.echo(format_report_text(report, floor=effective_floor))

    if report.deterministic_catch_rate() < effective_floor:
        raise typer.Exit(1)


__all__ = ["grounding_recall_cmd", "grounding_surface_cmd", "render_ledger_markdown"]
