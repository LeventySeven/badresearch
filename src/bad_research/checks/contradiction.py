"""Mechanical contradiction pairing -- two accounts of one fact that disagree.

**Why this exists.** When two sources disagree on a load-bearing number, that is
the most valuable thing a research run finds, and it is the thing every surveyed
memory system silently destroys: the field's canonical benchmark defines correct
handling as *overwriting the stale value*. Two accounts of the same fact that
disagree are a discrepancy in the record, not a stale value -- so this module
keeps both sides and names the gap between them.

**What counts as a disagreement.** Only a same-for-same comparison:

* the same normalized **subject** (casefold, collapsed whitespace),
* the same normalized **unit** -- $/hr against $/month is a different
  measurement, not a disagreement,
* **different sources** -- a source that restates itself inconsistently is a
  drafting problem, not a discrepancy in the record,
* and values that differ by more than `rel_tolerance` relative difference, so
  rounding ("2.490" against "2.49") is absorbed rather than reported.

A number is only ever compared against a number and prose only against prose. A
numeric value facing a non-numeric one is treated as not comparable and dropped,
for the same reason two different units are: the check would rather miss a real
discrepancy than report one that is not there.

**The guard.** The known failure mode is an agent that manufactures
contradictions to justify another search round. `MAX_OPEN_CONTRADICTIONS` caps
what comes back at the twelve widest gaps -- and the result carries `suppressed`
and `total_found`, so the cap can never be silent about what it dropped.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from itertools import combinations

# The most open discrepancies a single pass will hand back. A run that "found"
# more than a dozen live contradictions has almost always found a subject-
# normalisation bug or an agent looking for a reason to keep searching.
MAX_OPEN_CONTRADICTIONS = 12

# A bare decimal, once currency symbols, thousands separators and a trailing
# percent sign are off. Deliberately strict: anything this does not match is
# prose, and prose is compared as prose.
_NUMERIC = re.compile(r"^[+-]?\d+(?:\.\d+)?$")
_CURRENCY = "$€£¥"


@dataclass(frozen=True)
class Claim:
    """One source's account of one fact: what, how much, in what unit, from whom.

    `as_of` is the date the value was captured, and it is optional because it is
    often genuinely unavailable. Where it IS known it is load-bearing: two
    accounts of one fact carrying different dates are still a discrepancy in the
    record rather than a stale value, but a reader can only judge that if both
    dates reach them. `close_gate` enforces exactly that -- it demands the dates
    that exist and never invents a requirement for the ones that do not.
    """

    subject: str
    value: str
    unit: str
    source: str
    as_of: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "subject": self.subject,
            "value": self.value,
            "unit": self.unit,
            "source": self.source,
            "as_of": self.as_of,
        }


@dataclass(frozen=True)
class Contradiction:
    """Two claims about one fact that do not agree, and how far apart they are."""

    left: Claim
    right: Claim
    kind: str      # numeric | stance
    delta: float   # relative difference; 1.0 for a stance disagreement

    def to_dict(self) -> dict[str, object]:
        return {
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
            "kind": self.kind,
            "delta": self.delta,
        }


class ContradictionList(list[Contradiction]):
    """The contradictions that survived the cap, plus what the cap removed.

    A plain `list` so callers can compare, index and iterate it normally; the
    two extra attributes exist so `MAX_OPEN_CONTRADICTIONS` is never applied
    behind a caller's back.
    """

    def __init__(
        self, items: Iterable[Contradiction] = (), *, suppressed: int = 0
    ) -> None:
        super().__init__(items)
        self.suppressed = suppressed

    @property
    def total_found(self) -> int:
        """Contradictions found before the cap was applied."""
        return len(self) + self.suppressed


def _norm(text: str) -> str:
    """Casefold and collapse whitespace -- the one normalisation used throughout."""
    return " ".join(text.split()).casefold()


def _as_number(value: str) -> float | None:
    """`value` as a float, or None when it is prose rather than a quantity."""
    cleaned = value.strip().replace(",", "").lstrip(_CURRENCY).rstrip("%").strip()
    return float(cleaned) if _NUMERIC.match(cleaned) else None


def _compare(left: Claim, right: Claim, rel_tolerance: float) -> Contradiction | None:
    """The disagreement between two same-subject, same-unit claims, if any."""
    lhs, rhs = _as_number(left.value), _as_number(right.value)

    if lhs is not None and rhs is not None:
        scale = max(abs(lhs), abs(rhs))
        delta = 0.0 if scale == 0 else abs(lhs - rhs) / scale
        if delta > rel_tolerance:
            return Contradiction(left, right, "numeric", delta)
        return None

    if lhs is None and rhs is None:
        if _norm(left.value) != _norm(right.value):
            return Contradiction(left, right, "stance", 1.0)
        return None

    # A quantity against prose is not comparable -- same call as a unit mismatch.
    return None


def find_contradictions(
    claims: Sequence[Claim], *, rel_tolerance: float = 0.01
) -> ContradictionList:
    """Pair `claims` that describe one fact and disagree about it.

    Ranked by relative delta descending, capped at `MAX_OPEN_CONTRADICTIONS`,
    with the number dropped by the cap on `.suppressed`.
    """
    groups: dict[tuple[str, str], list[Claim]] = {}
    for claim in claims:
        groups.setdefault((_norm(claim.subject), _norm(claim.unit)), []).append(claim)

    found: list[Contradiction] = []
    for group in groups.values():
        for left, right in combinations(group, 2):
            if _norm(left.source) == _norm(right.source):
                continue
            contradiction = _compare(left, right, rel_tolerance)
            if contradiction is not None:
                found.append(contradiction)

    # Widest gap first; the rest of the key only makes ties reproducible.
    found.sort(key=lambda c: (-c.delta, _norm(c.left.subject), c.left.source, c.right.source))
    kept = found[:MAX_OPEN_CONTRADICTIONS]
    return ContradictionList(kept, suppressed=len(found) - len(kept))


__all__ = [
    "MAX_OPEN_CONTRADICTIONS",
    "Claim",
    "Contradiction",
    "ContradictionList",
    "find_contradictions",
]
