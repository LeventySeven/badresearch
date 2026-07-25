"""Provider registry (keyless) + external-CLI detection.

Pure and network-free: `bad doctor` and `bad calibrate` use this to report the
keyless capability surface. Every provider is KEYLESS (host model + local OSS +
self-host) — `requires_key` is False on every row, so `active` reduces to
`import_present` for everything that runs IN-PROCESS.

The exception is `_HOST_BRIDGE_PROVIDERS` (`websearch`, `anthropic-host`):
adapters over a Claude-host tool that a `bad …` subprocess has no wire to. They
carry no import to check, so `import_present` is vacuously True — equating that
with "active" made `doctor` promise capability the engine could not deliver
(issue #35 §2). They remain keyless; they are simply reported honestly as
unreachable from here.

The external CLIs the skill drives (agent-browser/lightpanda/yt-dlp/git) are
detected via `shutil.which` (no subprocess execution).
"""

from __future__ import annotations

import importlib.util
import os
import shutil
from dataclasses import dataclass


@dataclass(frozen=True)
class Provider:
    name: str
    env_var: str | None  # always None in the keyless world (host supplies inference)
    import_name: str | None  # the module that must import for the capability to work
    extra: str  # which `pip install bad-research[<extra>]` ships it ("(base)" = no extra)
    capability: str  # "llm" | "search" | "browse" | "embed" | "rerank" | "nli"


# The keyless registry (INTERFACES_KEYLESS §3.5). NO keyed provider rows.
PROVIDERS: tuple[Provider, ...] = (
    Provider("anthropic-host", None, None, "(base)", "llm"),       # host supplies inference; no key
    Provider("websearch", None, None, "(base)", "search"),         # host WebSearch tool
    Provider("ddgs", None, "ddgs", "(base)", "search"),            # keyless multi-engine lib
    Provider("searxng", None, None, "(base)", "search"),           # self-host, no key
    Provider("crawl4ai", None, "crawl4ai", "(base)", "browse"),    # local JS render
    Provider("agent-browser", None, None, "browse", "browse"),     # local CLI (CDP)
    Provider("arxiv", None, None, "(base)", "search"),             # keyless vertical (httpx)
    Provider("openalex", None, None, "(base)", "search"),
    Provider("crossref", None, None, "(base)", "search"),
    Provider("europepmc", None, None, "(base)", "search"),
    Provider("pubmed", None, None, "(base)", "search"),
    Provider("wikipedia", None, None, "(base)", "search"),
    Provider("bge-local", None, "sentence_transformers", "local", "embed"),
    Provider("ms-marco-local", None, "sentence_transformers", "local", "rerank"),
    Provider("nli-deberta", None, "sentence_transformers", "local", "nli"),
)


# External keyless CLI tools the skill drives (INTERFACES_KEYLESS §7.1). These are
# NOT pip deps — installed out-of-band. `bad doctor` reports presence + this hint.
# SearXNG is intentionally ABSENT (silent/opt-in, INTERFACES_KEYLESS §9).
EXTERNAL_CLIS: dict[str, str] = {
    "agent-browser": "agent-browser install   # pulls Chrome-for-Testing, no account",
    "lightpanda": "curl -L github.com/lightpanda-io/browser/releases/latest -o lightpanda  # keyless JS engine",
    "yt-dlp": "pipx install yt-dlp      # caption-track puller (YouTube/video tier)",
    "git": "(install git via your OS package manager)",
}


@dataclass
class ProviderStatus:
    name: str
    capability: str
    extra: str
    requires_key: bool
    key_present: bool
    import_present: bool
    active: bool


# Providers that are adapters over a HOST tool bridge (Claude Code's WebSearch
# tool, host model inference). They have no client library to import, so
# `_import_ok` returns True vacuously — but a `bad …` subprocess has no bridge
# wired, so they can never return a result there. `doctor` is itself always a
# subprocess, so reporting them "active" was a capability claim the engine could
# not honour; the plugin bootstrap reads doctor to decide whether it can run at
# all (issue #35 §2). Import-resolves != can-return-a-result.
_HOST_BRIDGE_PROVIDERS = frozenset({"websearch", "anthropic-host"})


def _import_ok(import_name: str | None) -> bool:
    if not import_name:
        return True  # host tool / self-host / pure-httpx vertical — no client lib needed
    try:
        return importlib.util.find_spec(import_name) is not None
    except (ImportError, ValueError):
        return False


def _host_bridge_live(name: str) -> bool:
    """Can this host-bridge provider actually produce a result from here?

    `anthropic-host` becomes genuinely usable when a key is exported (the LLM
    client then calls the API directly instead of the absent host bridge).
    `websearch` has no such escape hatch: the CLI's `_build_providers` never
    wires a `links_source`, so it raises NotImplementedError in every
    subprocess invocation.
    """
    if name == "anthropic-host":
        return bool(os.environ.get("ANTHROPIC_API_KEY"))
    return False


def provider_status() -> list[ProviderStatus]:
    """Status for every registered provider. No network, no config-file read.

    Keyless: `requires_key` is False everywhere, so `active == import_present`.
    """
    out: list[ProviderStatus] = []
    for p in PROVIDERS:
        requires_key = bool(p.env_var)  # always False in the keyless registry
        key_present = (not requires_key) or bool(os.environ.get(p.env_var or ""))
        import_present = _import_ok(p.import_name)
        active = key_present and import_present
        if p.name in _HOST_BRIDGE_PROVIDERS:
            active = active and _host_bridge_live(p.name)
        out.append(
            ProviderStatus(
                name=p.name,
                capability=p.capability,
                extra=p.extra,
                requires_key=requires_key,
                key_present=key_present,
                import_present=import_present,
                active=active,
            )
        )
    return out


def active_providers() -> list[ProviderStatus]:
    """Only the providers that can actually run right now (keyless: import resolves)."""
    return [s for s in provider_status() if s.active]


def external_cli_status() -> list[dict[str, object]]:
    """Detect the external keyless CLIs the skill drives (shutil.which; no subprocess).

    Returns one row per CLI: {name: str, present: bool, hint: str}. SearXNG is silent
    — never reported here (INTERFACES_KEYLESS §9).
    """
    return [
        {"name": name, "present": shutil.which(name) is not None, "hint": hint}
        for name, hint in EXTERNAL_CLIS.items()
    ]


__all__ = [
    "EXTERNAL_CLIS",
    "PROVIDERS",
    "Provider",
    "ProviderStatus",
    "active_providers",
    "external_cli_status",
    "provider_status",
]
