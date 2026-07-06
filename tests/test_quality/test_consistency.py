"""E4 — Self-consistency vote on high-stakes claims (ENHANCEMENT_PLAN E4, P1).

Denny Zhou: self-consistency lifts accuracy 58→75% by sampling N answers and
selecting the most cross-supported one (universal self-consistency for open-ended).
DISTINCT from the draft ensemble (which MERGES 2 angle drafts; this VOTES).

The high-effort lane only: for `effort=high` (or an explicitly contested claim),
sample N host-model judgments on a high-stakes (claim, quote) pair and apply
universal self-consistency — the host model picks the most cross-supported verdict.
Keyless (host model via the LLMProvider seam, N calls — costs tokens, no key). The
default (non-high) effort path is UNCHANGED: no extra calls.
"""

from __future__ import annotations

from bad_research.grounding.verifier import VerifyVerdict
from bad_research.llm.base import LLMMessage, LLMResponse
from bad_research.quality.consistency import (
    SELF_CONSISTENCY_N,
    consistency_enabled,
    self_consistency_vote,
)


class ScriptedLLM:
    """Host-model double: pops a scripted response text per `complete` call and
    records every call (so a test can assert N samples were drawn)."""

    name = "scripted"

    def __init__(self, script: list[str]) -> None:
        self.script = list(script)
        self.calls: list[dict] = []

    def complete(
        self,
        messages: list[LLMMessage],
        *,
        tier: str,
        tools: list[dict] | None = None,
        cache: bool = False,
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> LLMResponse:
        self.calls.append({"tier": tier, "temperature": temperature})
        text = self.script.pop(0) if self.script else "{}"
        return LLMResponse(text=text, model="scripted")


def _sample(verdict: str, score: float) -> str:
    import json

    return json.dumps({"verdict": verdict, "score": score})


# ── The gate: only effort=high enables the lane ──────────────────────────────


def test_consistency_disabled_by_default_effort():
    for eff in (None, "minimal", "low", "medium"):
        assert consistency_enabled(eff) is False


def test_consistency_enabled_only_on_high_effort():
    assert consistency_enabled("high") is True


def test_default_n_is_at_least_three():
    # Denny Zhou samples N>=3; majority needs an odd-ish N to break ties.
    assert SELF_CONSISTENCY_N >= 3


# ── The vote: N samples, majority/most-supported wins ────────────────────────


def test_two_of_three_supported_is_accepted():
    # 2/3 samples say supported, 1/3 says unsupported -> the majority (supported) wins.
    llm = ScriptedLLM([
        _sample("supported", 0.9),
        _sample("supported", 0.85),
        _sample("unsupported", 0.2),
    ])
    verdict, _score, votes = self_consistency_vote(
        "SEA GMV grew 12.4%.", "a 12.4% YoY expansion", llm, n=3
    )
    assert verdict is VerifyVerdict.SUPPORTED
    # exactly N host-model samples were drawn (this is the keyless token cost)
    assert len(llm.calls) == 3
    assert votes[VerifyVerdict.SUPPORTED] == 2


def test_one_of_three_supported_is_outvoted_rejected():
    # A single dissenting "supported" sample is OUTVOTED by 2 unsupported -> rejected.
    llm = ScriptedLLM([
        _sample("supported", 0.95),
        _sample("unsupported", 0.3),
        _sample("unsupported", 0.25),
    ])
    verdict, _score, votes = self_consistency_vote(
        "Vietnam led at 64%.", "Vietnam was mentioned in passing", llm, n=3
    )
    assert verdict is not VerifyVerdict.SUPPORTED
    assert votes[VerifyVerdict.SUPPORTED] == 1
    assert len(llm.calls) == 3


def test_unanimous_supported_accepted():
    llm = ScriptedLLM([_sample("supported", 0.9)] * 3)
    verdict, _score, votes = self_consistency_vote("c", "q", llm, n=3)
    assert verdict is VerifyVerdict.SUPPORTED
    assert votes[VerifyVerdict.SUPPORTED] == 3


def test_samples_drawn_at_nonzero_temperature():
    # Self-consistency REQUIRES diverse samples → temperature must be > 0 (a single
    # deterministic sample is not a vote). This is the core of the technique.
    llm = ScriptedLLM([_sample("supported", 0.9)] * 3)
    self_consistency_vote("c", "q", llm, n=3)
    assert all(call["temperature"] > 0.0 for call in llm.calls)


def test_robust_to_unparseable_sample():
    # A garbage sample doesn't crash the vote; it counts as a non-supporting verdict.
    llm = ScriptedLLM([
        _sample("supported", 0.9),
        "not json at all",
        _sample("supported", 0.8),
    ])
    verdict, _score, _votes = self_consistency_vote("c", "q", llm, n=3)
    # 2 supported still carries the majority despite one unparseable sample.
    assert verdict is VerifyVerdict.SUPPORTED
    assert len(llm.calls) == 3
