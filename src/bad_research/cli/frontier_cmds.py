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


def frontier_observe_cmd(
    state: Path = typer.Option(..., "--state", help="Path to the run's frontier JSON."),
    domains: str = typer.Option("", "--domains", help="Comma-separated domains this round returned."),
    entities: str = typer.Option("", "--entities", help="Comma-separated entities this round produced."),
    promise: str = typer.Option("", "--promise", help="Comma-separated cells the answer OWES (set once, up front)."),
    close: str = typer.Option("", "--close", help="Comma-separated promised cells this round filled."),
    abandon: list[str] = typer.Option(
        [], "--abandon",
        help="cell=reason — give up on a promised cell, with a reason. Repeatable, so a round's "
             "abandonments ride on the round's one observe instead of costing a phantom round.",
    ),
    floor: int | None = typer.Option(None, "--floor", help="Minimum observes before a stop (default 5 per retrieval; a round-based run sets its tier's minimum rounds). Persisted."),
    patience: int | None = typer.Option(None, "--patience", help="Consecutive quiet observes that signal saturation (default 2 per retrieval; 1 per round). Persisted."),
    json_out: bool = typer.Option(False, "--json", help="Emit the counters as JSON."),
) -> None:
    """Record what a retrieval round brought back and compute the stop signal.

    The signal is COMPUTED here, before the next prompt is built, so it is auditable
    from the run's own counters rather than taken from the model's account of its own
    diminishing returns. Every stopping rule surveyed for this rebuild was either
    absent, a constant someone picked, or a convergence check that could never fire.
    """
    st = FrontierState.load(state)
    try:
        st.set_rule(floor=floor, patience=patience)
    except ValueError as e:  # 0 or negative: a stop that could fire before anything was read
        typer.echo(str(e), err=True)
        raise typer.Exit(code=2) from None
    st.open_cells |= {x.strip() for x in promise.split(",") if x.strip()}
    for c in (x.strip() for x in close.split(",") if x.strip()):
        st.close_cell(c)
    for a in abandon:
        if a.strip():
            cell, _, why = a.partition("=")
            st.abandon_cell(cell.strip(), why.strip())
    d = {x.strip() for x in domains.split(",") if x.strip()}
    e = {x.strip() for x in entities.split(",") if x.strip()}
    st.observe_round(d, e)
    st.save(state)

    payload = {
        "step": st.steps,
        "new_domains": st.last_new_domains,
        "new_entities": st.last_new_entities,
        "should_stop": st.should_stop(),
        "seen_domains": len(st.seen_domains),
        "residual": st.residual(),
        "abandoned": st.abandoned,
        "floor": st.min_steps,
        "patience": st.patience,
    }
    if json_out:
        typer.echo(_json.dumps(payload))
    else:
        if payload["should_stop"]:
            verdict = "STOP — nothing new arrived and nothing is owed"
        elif st.open_cells:
            verdict = f"continue — still owed: {', '.join(st.residual())}"
        else:
            verdict = "continue"
        typer.echo(
            f"step {st.steps} | +{st.last_new_domains} domains "
            f"+{st.last_new_entities} entities | open cells {len(st.open_cells)} | {verdict}"
        )
