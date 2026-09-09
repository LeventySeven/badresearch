"""Recall for an open set -- how many did we MISS, when nobody knows the total.

Every other gate here measures precision: is what the answer says supported. On
a "find all X" question that is the wrong axis. An answer can be perfectly
precise and miss two thirds of the population, and nothing else in this kit
would say so.

**The instrument.** Capture-recapture, the method used to count a population
that cannot be counted. Search twice by genuinely different means: if the first
pass finds `n1`, the second finds `n2`, and `m` items appear in both, then under
independence the population is about `n1*n2/m`, and coverage is what you hold
over that. It turns "I think I got most of them" into a number carrying an
assumption someone can attack -- which is the only kind of number worth having
here.

**The assumption is the whole game, and it fails in one direction.** If the two
passes share a bias -- both ranked by popularity, both seeded from one list, both
the same lane run twice -- their overlap is inflated. Inflated overlap shrinks
the estimated population, which reports HIGH coverage exactly when the obscure
tail was missed by both. That is the failure mode of a search for "the great but
unpopular ones", so this module refuses to produce an estimate for lanes it can
see are dependent rather than producing a flattering one.

**Read the singletons before the estimate.** Items found by exactly one lane are
the shape of the tail. When most of what you hold was seen by only one pass, the
population is much larger than you have sampled, whatever the point estimate says
-- and the estimate itself is least trustworthy there.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

# Lane-name fragments that mark a pass as ordered by audience size. Two of these
# agree about the head and are silent about the tail together, so their overlap
# is not evidence about the population. Kept as fragments, not exact names,
# because the caller names its own lanes.
_RANKED = ("rank", "popular", "top", "citation", "cited", "trending", "vote", "star")


@dataclass(frozen=True)
class CoverageEstimate:
    found: int
    overlap: int
    estimated_total: float | None
    coverage: float | None
    missing_estimate: float | None
    caveat: str

    def to_dict(self) -> dict[str, object]:
        return {
            "found": self.found,
            "overlap": self.overlap,
            "estimated_total": self.estimated_total,
            "coverage": self.coverage,
            "missing_estimate": self.missing_estimate,
            "caveat": self.caveat,
        }


def _dependence_caveat(lane_a: str, lane_b: str) -> str | None:
    """Why these two passes cannot be treated as independent samples, if so."""
    a, b = lane_a.strip().casefold(), lane_b.strip().casefold()
    if a == b:
        return (f"both passes are the same lane ({lane_a}) — running one lane twice measures "
                "its determinism, not the population")
    if any(t in a for t in _RANKED) and any(t in b for t in _RANKED):
        return (f"both passes are rank-ordered ({lane_a}, {lane_b}) — two popularity-ranked "
                "searches agree about the head and are silent about the tail TOGETHER, so their "
                "overlap understates the population and overstates your coverage")
    return None


def estimate_coverage(
    a: Iterable[str], b: Iterable[str], *, lane_a: str, lane_b: str
) -> CoverageEstimate:
    """Lincoln-Petersen coverage from two passes, or a refusal with its reason."""
    sa, sb = set(a), set(b)
    union, m = sa | sb, len(sa & sb)

    dep = _dependence_caveat(lane_a, lane_b)
    if dep is not None:
        return CoverageEstimate(len(union), m, None, None, None, dep)
    if m == 0:
        return CoverageEstimate(
            len(union), 0, None, None, None,
            "no overlap between the two passes — either they searched different populations, or "
            "you have sampled so little that a shared item has not appeared yet. No estimate is "
            "possible; widen one pass until the two touch.",
        )

    total = len(sa) * len(sb) / m
    total = max(total, float(len(union)))     # an estimate below what you HOLD is incoherent
    return CoverageEstimate(
        found=len(union),
        overlap=m,
        estimated_total=total,
        coverage=len(union) / total,
        missing_estimate=total - len(union),
        caveat=(
            "assumes the two passes are independent and every item was equally findable by both. "
            "Neither is ever quite true; read this as an upper bound on coverage, and check the "
            "singleton fraction before believing it."
        ),
    )


@dataclass
class CaptureRecapture:
    """Three or more passes: every pair estimates, and the SMALLEST coverage wins.

    Taking the worst pair is deliberate. Each pair's estimate is an upper bound on
    coverage (dependence between passes only ever inflates it), so the pair that
    agreed least is the one least contaminated by shared method — and its answer
    is the least flattering, which on this question is the one to act on.
    """

    lanes: dict[str, set[str]] = field(default_factory=dict)

    def add(self, lane: str, items: Iterable[str]) -> None:
        self.lanes.setdefault(lane, set()).update(items)

    @property
    def found(self) -> int:
        return len(set().union(*self.lanes.values())) if self.lanes else 0

    def singletons(self) -> list[str]:
        """Items exactly one lane found — the shape of the tail."""
        counts: dict[str, int] = {}
        for items in self.lanes.values():
            for i in items:
                counts[i] = counts.get(i, 0) + 1
        return sorted(i for i, c in counts.items() if c == 1)

    def singleton_fraction(self) -> float:
        return len(self.singletons()) / self.found if self.found else 0.0

    def best_estimate(self) -> float | None:
        """The LARGEST estimated population across independent pairs — i.e. the
        least flattering coverage. None when no pair is usable."""
        names = sorted(self.lanes)
        totals = [
            e.estimated_total
            for i, x in enumerate(names)
            for y in names[i + 1:]
            if (e := estimate_coverage(self.lanes[x], self.lanes[y], lane_a=x, lane_b=y)).estimated_total
        ]
        return max(totals) if totals else None


__all__ = ["CaptureRecapture", "CoverageEstimate", "estimate_coverage"]
