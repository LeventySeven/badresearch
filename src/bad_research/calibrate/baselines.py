"""Calibration baselines — run the same query through a comparison system.

Key-gated (SPEC §14): a baseline that needs a key it doesn't have is silently
dropped by the harness, never a crash. No keyless baseline currently ships;
`available_baselines()` returns an empty list under the keyless architecture.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class BaselineUnavailable(RuntimeError):
    """Raised when a baseline is invoked without its key/dependency."""


@dataclass
class BaselineResult:
    name: str
    report: str
    corpus: list[dict[str, object]]  # the evidence that baseline used, for fair judging


class Baseline(Protocol):
    name: str

    def available(self) -> bool: ...
    def run(self, query: str) -> BaselineResult: ...


def available_baselines() -> list[Baseline]:
    """Every baseline whose dependency is present (keyless only).

    The keyed deep-research APIs (Perplexity/Grok) are REMOVED in the keyless
    re-architecture — they need third-party keys, which the keyless rule forbids.
    No keyless baseline currently ships: the keyless calibration plan
    (docs/plans/2026-05-27-bad-research-KR-7-calibration-plan.md) measures the
    keyless pipeline against keyless references instead.
    """
    candidates: list[Baseline] = []
    return [b for b in candidates if b.available()]


__all__ = [
    "Baseline",
    "BaselineResult",
    "BaselineUnavailable",
    "available_baselines",
]
