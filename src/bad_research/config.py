"""Bad Research top-level configuration.

Distinct from hyperresearch's per-vault `core/config.py:VaultConfig` (kept verbatim
in the fork). This holds the cross-cutting knobs: provider keys (read lazily from
env), the model-tier map, budget caps, and thresholds. Precedence: env > TOML > default.

Default TOML location: ~/.config/bad-research/config.toml (XDG user config).
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


def default_config_path() -> Path:
    """The user-side config file location (~/.config/bad-research/config.toml)."""
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "bad-research" / "config.toml"


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes", "on")


@dataclass
class BadResearchConfig:
    vault_root: Path = field(default_factory=lambda: Path.home() / ".bad-research")
    model_tiers: dict[str, str] = field(
        default_factory=lambda: {
            "triage": "claude-haiku-4-5",
            "work": "claude-sonnet-4-6",
            "heavy": "claude-opus-4-7",
        }
    )
    cheap: bool = False                    # demote heavy->work (llm/anthropic.py)
    # E7 — append-only prompt-cache discipline (headless AnthropicProvider only).
    # When True (default) the provider stamps a cache_control breakpoint on the
    # STABLE system-prompt prefix so repeated headless calls hit the Anthropic
    # prompt cache (>80% hit / 5-10x cost, Genspark; DEEPLEARNINGAI.md A4). Set
    # False to disable (SDKs/models without prompt caching degrade gracefully).
    prompt_cache: bool = True
    # ── Keyless knobs (KR-1; dossier 13/15/16) ──────────────────────────────
    # host-model LLM-rerank default; "local"/"light" = ms-marco-MiniLM ([local]),
    # "zerank2" = ZeroEntropy zerank-2 opt-in ([local], +8.7pp NDCG@10, CC-BY-NC; E14)
    reranker: Literal["host", "local", "light", "zerank2", "none"] = "host"
    neural_recall: bool = False                            # opt-in local bi-encoder lane ([local])
    searxng_endpoint: str = "http://localhost:8080"        # self-host T1; no key
    # rung-2.5/3 backend: "silver" (default — DNS-resolved entry gate + read-only unless
    # `--enable-actions`; it does NOT gate intermediate redirect hops, see browse/ladder.py)
    # or the two agent-browser engines kept as a fallback for machines without silver.
    browse_engine: Literal["silver", "lightpanda", "chrome"] = "silver"
    effort: Literal["minimal", "low", "medium", "high"] = "medium"  # KR-6 effort continuum
    # NOTE: `max_tokens` / `budget_usd` used to live here. Both were parsed from TOML
    # + env and read by NOTHING — this package has no token or cost meter, and the
    # run-level ceiling the orchestrator honours is the `--max-tokens` value it tracks
    # in prose (entry skill), never a config field. They were removed rather than
    # faked: a dial that silently does nothing is worse than no dial. A config or env
    # that still carries them loads fine (unknown keys are ignored).
    # Retrieval knobs (Plan 02; default to the frozen constants). The engine
    # reads these (not the constants module directly) so config overrides apply.
    retrieval_alpha: float = 0.7
    relevance_gate: float = 0.70
    semantic_cache_threshold: float = 0.92
    top_k_retrieve: int = 30
    # provider keys read from env / ~/.config/bad-research/config.toml at call sites

    @classmethod
    def load(cls, config_path: Path | None = None) -> BadResearchConfig:
        """Build a config with precedence env > TOML > dataclass default."""
        if config_path is None:
            config_path = default_config_path()

        cfg = cls()

        # --- TOML layer (overrides defaults) ---
        if config_path.exists():
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
            section = data.get("bad-research", {})
            if "vault_root" in section:
                cfg.vault_root = Path(section["vault_root"])
            if "model_tiers" in section:
                cfg.model_tiers = dict(section["model_tiers"])
            if "reranker" in section:
                cfg.reranker = section["reranker"]
            if "neural_recall" in section:
                cfg.neural_recall = bool(section["neural_recall"])
            if "searxng_endpoint" in section:
                cfg.searxng_endpoint = str(section["searxng_endpoint"])
            if "browse_engine" in section:
                cfg.browse_engine = section["browse_engine"]
            if "effort" in section:
                cfg.effort = section["effort"]
            if "cheap" in section:
                cfg.cheap = bool(section["cheap"])
            if "prompt_cache" in section:
                cfg.prompt_cache = bool(section["prompt_cache"])

        # --- env layer (overrides TOML) ---
        if (v := os.environ.get("BAD_RESEARCH_VAULT_ROOT")) is not None:
            cfg.vault_root = Path(v)
        if (v := os.environ.get("BAD_RESEARCH_RERANKER")) is not None:
            cfg.reranker = v  # type: ignore[assignment]
        if (v := os.environ.get("BAD_RESEARCH_NEURAL_RECALL")) is not None:
            cfg.neural_recall = _parse_bool(v)
        if (v := os.environ.get("BAD_RESEARCH_SEARXNG_ENDPOINT")) is not None:
            cfg.searxng_endpoint = v
        if (v := os.environ.get("BAD_RESEARCH_BROWSE_ENGINE")) is not None:
            cfg.browse_engine = v  # type: ignore[assignment]  # the one-line rollback switch
        if (v := os.environ.get("BAD_RESEARCH_EFFORT")) is not None:
            cfg.effort = v  # type: ignore[assignment]
        if (v := os.environ.get("BAD_RESEARCH_CHEAP")) is not None:
            cfg.cheap = _parse_bool(v)
        if (v := os.environ.get("BAD_RESEARCH_PROMPT_CACHE")) is not None:
            cfg.prompt_cache = _parse_bool(v)

        return cfg
