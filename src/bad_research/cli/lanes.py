"""`bad lane-local` — grep the owner's on-disk libraries from the CLI.

Thin shell over `lanes.local_corpus.search_local`: no ranking, no rewriting,
no LLM. The enumeration line goes out first on both paths, so a run that found
nothing still reports how many files it listed and which roots it could not
reach — the difference between an honest empty and a broken lane.
"""

from __future__ import annotations

import json

import typer

from bad_research.lanes.local_corpus import search_local


def lane_local_cmd(
    query: str = typer.Argument(..., help="Substring to grep for (case-insensitive)."),
    json_out: bool = typer.Option(False, "--json", help="Emit the lane result as JSON."),
) -> None:
    """Search the local corpus (teardowns, transcripts, articles, x-guides, specs).

    Flat glob only — `*.md` at the top of each root, never recursive."""
    result = search_local(query)

    if json_out:
        typer.echo(json.dumps(result.to_dict(), ensure_ascii=False))
        return

    typer.echo(result.enumeration_line())
    for hit in result.hits:
        typer.echo(f"{hit.path}:{hit.line}: {hit.text}")


__all__ = ["lane_local_cmd"]
