"""`bad doctor` — the keyless capability report. No network, no key checks.

Reports: the keyless-by-default banner, the keyless provider rows (host model +
keyless search/browse), the external keyless CLIs the skill drives (silver/
agent-browser/lightpanda/yt-dlp/git) with one-line install hints, and whether the optional
`[local]` neural stack is installed. SearXNG is intentionally silent — its provider
row only renders when `searxng_endpoint` is configured away from the localhost
default (opt-in, INTERFACES_KEYLESS §9).
"""

from __future__ import annotations

import importlib.util
from dataclasses import asdict
from pathlib import Path

import typer

from bad_research.cli._output import console, output
from bad_research.models.output import success
from bad_research.providers import external_cli_status, provider_status

_SEARXNG_DEFAULT_ENDPOINT = "http://localhost:8080"


def _local_installed() -> bool:
    """True iff the [local] neural stack (sentence-transformers) is importable."""
    try:
        return importlib.util.find_spec("sentence_transformers") is not None
    except (ImportError, ValueError):
        return False


def doctor(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Report the keyless capability surface: providers, external CLIs, [local]. Network-free."""
    statuses = provider_status()
    clis = external_cli_status()
    local_installed = _local_installed()

    # Vault root + model tiers from config (best-effort; defaults if config absent).
    # `searxng_configured` is True only when the user pointed at a non-default endpoint —
    # otherwise SearXNG stays silent (opt-in, never warned about).
    searxng_configured = False
    try:
        from bad_research.config import BadResearchConfig

        cfg = BadResearchConfig()
        vault_root = str(cfg.vault_root)
        model_tiers = dict(cfg.model_tiers)
        searxng_configured = (
            getattr(cfg, "searxng_endpoint", _SEARXNG_DEFAULT_ENDPOINT)
            != _SEARXNG_DEFAULT_ENDPOINT
        )
    except Exception:  # pragma: no cover - config always loads in practice
        vault_root = str(Path.home() / ".bad-research")
        model_tiers = {
            "triage": "claude-haiku-4-5",
            "work": "claude-sonnet-4-6",
            "heavy": "claude-opus-4-7",
        }

    # SearXNG is silent unless explicitly configured (INTERFACES_KEYLESS §9).
    visible = [s for s in statuses if s.name != "searxng" or searxng_configured]

    data = {
        "keyless": True,
        "vault_root": vault_root,
        "model_tiers": model_tiers,
        "providers": [asdict(s) for s in statuses],
        "external_clis": clis,
        "local_installed": local_installed,
        "active_count": sum(1 for s in statuses if s.active),
    }

    if json_output:
        output(success(data, vault=vault_root), json_mode=True)
        return

    from bad_research._banner import render_rich

    console.print(render_rich())
    console.print()
    console.print("[bold]bad doctor[/] — keyless capability surface\n")
    console.print("[green]keyless by default[/] — zero third-party API key required.")
    console.print("[dim](the skill uses the Claude Code host model; web via host tools + local OSS/CLIs)[/]\n")
    console.print(f"[dim]vault:[/] {vault_root}")
    console.print(f"[dim]models:[/] {model_tiers}\n")

    # Providers (all keyless: active == import resolves).
    console.print("[bold]providers[/] [dim](all keyless)[/]")
    for s in visible:
        if s.active:
            mark, color = "OK ", "green"
        else:
            mark, color = "off", "dim"
        note = ""
        if not s.import_present and s.extra != "(base)":
            # escape the [extra] brackets so rich doesn't parse them as markup tags
            note = rf"  [dim](pip install 'bad-research\[{s.extra}]')[/]"
        console.print(f"  [{color}]{mark}[/] {s.name:<16} [dim]{s.capability}[/]{note}")

    # External CLIs the skill drives (detected; degrade gracefully when absent).
    console.print("\n[bold]external CLIs[/] [dim](skill-driven; install out-of-band)[/]")
    for c in clis:
        if c["present"]:
            console.print(f"  [green]OK [/] {c['name']:<16} [dim]found on PATH[/]")
        else:
            console.print(f"  [yellow]--[/] {c['name']:<16} [dim]{c['hint']}[/]")

    # The optional [local] neural stack.
    if local_installed:
        console.print("\n[bold]local stack[/]  [green]installed[/] [dim](torch + sentence-transformers — neural rerank/embed/NLI available)[/]")
    else:
        console.print("\n[bold]local stack[/]  [dim]not installed (default: host-model rerank, FTS5/BM25 recall). `pip install 'bad-research\\[local]'` for offline neural.[/]")

    console.print(f"\n[bold]{data['active_count']}[/] provider(s) active. [dim]Keyless pipeline (host WebSearch + ddgs + crawl4ai + BM25 + host-model rerank) runs with zero keys.[/]")


__all__ = ["doctor"]
