"""`bad frontier-gate` — the executing form of the frontier rule.

The rule: every query after the first must NAME something learned from a prior
read. A query that names nothing is a re-phrase of the question already asked, and
re-phrasing is the measured failure mode of research loops — an agent
"repeatedly searching for similar keywords despite retrieving relevant objects",
continuing after the answer was already in hand.

This exists because a rule stated in prose is worth roughly 7% on a post-trained
model, while a rule that exits non-zero is worth what it says. The gate refuses;
the caller decides whether to widen the frontier or stop.
"""

from __future__ import annotations

import json as _json
from pathlib import Path

import typer

from bad_research.frontier import FrontierState


def frontier_gate_cmd(
    state: Path = typer.Option(..., "--state", help="Path to the run's frontier JSON (created if absent)."),
    query: str = typer.Option(..., "--query", help="The query about to be issued."),
    json_out: bool = typer.Option(False, "--json", help="Emit the decision as JSON."),
) -> None:
    """Gate one query against the run's frontier. Exit 1 when it names nothing.

    The first query of a run is exempt — there is nothing to have learned yet.
    Every decision is appended to the state file's log, so the run's accretion is
    auditable afterwards from the counters rather than from the model's own account
    of how well it did.
    """
    st = FrontierState.load(state)
    allowed, named = st.gate_and_log(query)
    st.save(state)

    payload = {
        "query": query,
        "allowed": allowed,
        "named": named,
        "first": st.log[-1]["first"],
        "frontier_size": len(st.items),
    }
    if json_out:
        typer.echo(_json.dumps(payload))
    elif allowed:
        why = "first query (exempt)" if payload["first"] else f"names {', '.join(named)}"
        typer.echo(f"allow | {why} | frontier {len(st.items)}")
    else:
        typer.echo(
            f"REFUSE | names no frontier item | frontier {len(st.items)}\n"
            "  This is a re-phrase of a question already asked. Either widen the "
            "frontier by reading something new, or stop and write."
        )

    if not allowed:
        raise typer.Exit(code=1)
