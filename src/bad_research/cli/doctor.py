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
from bad_research.providers import (
    _HOST_BRIDGE_PROVIDERS,
    external_cli_status,
    provider_status,
)

_SEARXNG_DEFAULT_ENDPOINT = "http://localhost:8080"


def _installed_skill_status(home: Path | None = None) -> dict:
    """Is the installed /bad-research skill what `bad install` would write today?

    The source tree moved for two weeks while ~/.claude kept the older skill: every
    `/bad-research` ran a version nobody was editing, and nothing said so. The reference
    is built by the real installer into a temp home, so this check cannot drift from it.
    """
    import tempfile

    from bad_research.core.hooks import install_global_hooks

    home = home or Path.home()
    installed = home / ".claude"
    if not (installed / "skills" / "bad-research" / "SKILL.md").is_file():
        return {"status": "not-installed", "differs": []}
    with tempfile.TemporaryDirectory() as tmp:
        ref = Path(tmp)
        install_global_hooks(home=ref)
        rels = [
            p.relative_to(ref / ".claude")
            for p in sorted((ref / ".claude" / "skills" / "bad-research").rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts
        ] + [
            p.relative_to(ref / ".claude")
            for p in sorted((ref / ".claude" / "agents").glob("research-*.md"))
        ]
        differs = [
            str(r) for r in rels
            if not (installed / r).is_file()
            or (installed / r).read_bytes() != (ref / ".claude" / r).read_bytes()
        ]
    return {"status": "stale" if differs else "current", "differs": differs}


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
        # Report the EFFECTIVE vault, not the global default. `bad init .`
        # creates a vault in CWD and every other command resolves it via
        # Vault.discover(); doctor printing the global path sent users looking
        # for their corpus in the wrong directory (issue #35 §6).
        try:
            from bad_research.core.vault import Vault

            vault_root = str(Vault.discover().root)
        except Exception:
            pass  # no discoverable vault here — the config default is correct
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

    # `providers` and `active_count` MUST be derived from the same list, or the
    # printed count describes rows the caller cannot see (an unconfigured
    # searxng was counted but hidden — issue #35 §2).
    # `headless_capable` is the single field the plugin bootstrap branches on:
    # is there a GENERAL web-search lane that works in a subprocess?
    #
    # Deliberately NOT "any active search provider": the scholarly verticals
    # (arxiv/openalex/crossref/…) carry no import to check, so `import_present`
    # — and therefore `active` — is vacuously True for all six no matter what
    # is installed. Deriving the flag from them made it a constant True that
    # could never report incapacity, which is the exact false-capability class
    # this field exists to eliminate. The verticals are also intent-routed:
    # they only fire for academic/medical queries and cannot carry a general
    # one. So the flag tracks the general lanes — `ddgs` (a real import) and a
    # configured self-host SearXNG.
    # ddgs ONLY. searxng carries no import_name either, so its `active` is
    # vacuously True — including it reproduced the exact vacuity this field
    # exists to avoid: a configured-but-dead endpoint would report capable,
    # while a genuinely running SearXNG left on the default endpoint would not.
    _general = {"ddgs"}
    headless_capable = any(
        s.active and s.capability == "search" and s.name in _general for s in visible
    )
    data = {
        "keyless": True,
        "vault_root": vault_root,
        "model_tiers": model_tiers,
        "providers": [asdict(s) for s in visible],
        "external_clis": clis,
        "local_installed": local_installed,
        "active_count": sum(1 for s in visible if s.active),
        "headless_capable": headless_capable,
        "installed_skill": _installed_skill_status(),
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
        elif s.name in _HOST_BRIDGE_PROVIDERS and not s.active:
            # Without this, a host-bridge row renders as an unexplained `off`
            # and a user running `bad doctor` from inside Claude Code — where
            # the bridge genuinely works — concludes the install is broken.
            note = "  [dim](host-only: works in-agent, not in a CLI subprocess)[/]"
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

    lane = ("ddgs + crawl4ai + BM25" if headless_capable
            else "[yellow]no general web-search lane available here[/]")
    sk = data["installed_skill"]
    if sk["status"] == "stale":
        console.print(
            f"\n[bold red]installed skill is STALE[/] — {len(sk['differs'])} file(s) differ from "
            "this version (e.g. " + ", ".join(sk["differs"][:3]) + "). "
            "`/bad-research` is running an older skill. Run `bad install`."
        )
    elif sk["status"] == "not-installed":
        console.print("\n[yellow]skill not installed[/] in ~/.claude — run `bad install`.")
    else:
        console.print("\n[green]installed skill matches this version[/]")
    console.print(f"\n[bold]{data['active_count']}[/] provider(s) active here. "
                  f"[dim]Keyless pipeline ({lane}) runs with zero keys; host WebSearch + "
                  f"host-model rerank additionally light up in-agent.[/]")
    console.print("[dim]run research: `/bad-research <query>` in Claude Code, or invoke the skill from a subagent — keyless. The `bad` CLI is deterministic helpers only.[/]")


__all__ = ["doctor"]
