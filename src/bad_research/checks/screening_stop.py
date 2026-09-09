"""When may you stop screening a ranked pool -- with a recall guarantee attached.

`coverage.py` estimates how large the population is. That is the wrong question
during a screening run. What you need is *have I now seen enough of the relevant
items to stop reading*, and you need it with a confidence level rather than a
feeling that the hits have dried up.

Evidence synthesis solved this, and the mechanism transfers directly. Screen in
ranked order; periodically draw a **random** sample from the not-yet-screened
remainder. If that sample turns up (almost) nothing relevant, the remainder is
depleted, and you can reject the hypothesis that you have missed your recall
target. Verified from the primary source (Callaghan & Muller-Hansen 2020,
*Systematic Reviews* 9:273): *"flexible statistical stopping criteria, which
offer real work reductions on the basis of rejecting a hypothesis of having
missed a given recall target with a given level of confidence"*, reported to
"achieve a reliable level of recall, while still providing work reductions of on
average 17%."

**It accretes, in exactly the sense that matters.** The criterion is recomputed
every round from everything screened so far, and its power grows with the
screened set: early in a run no sample can license a stop, and later a single
clean one is enough. The filter genuinely gets better because you know more --
the owner's thesis, with the arithmetic attached.

**The arithmetic needs no dependency.** Under H0 the remainder still holds at
least `K` relevant items; the chance of drawing this few in a random sample of
`n` is an exact hypergeometric tail from `math.comb`.

**The assumption that carries everything: the sample must be RANDOM.** A sample
taken in rank order measures the ranker, not the pool, and the guarantee
evaporates without a word of warning -- which is why it is repeated in the
output rather than left in a docstring.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb


@dataclass(frozen=True)
class StopVerdict:
    stop: bool
    p_value: float
    max_missable: int
    why: str
    caveat: str

    def to_dict(self) -> dict[str, object]:
        return {
            "stop": self.stop,
            "p_value": self.p_value,
            "max_missable": self.max_missable,
            "why": self.why,
            "caveat": self.caveat,
        }


def _hypergeom_at_most(k: int, pool: int, relevant: int, draw: int) -> float:
    """P(X <= k) drawing `draw` from `pool` of which `relevant` are relevant.

    Exact, stdlib only -- no scipy. Named in words rather than the textbook
    N/K/n so the call sites read as what they mean.
    """
    if relevant <= 0:
        return 1.0
    total = comb(pool, draw)
    if total == 0:
        return 1.0
    acc = 0
    for i in range(0, min(k, relevant, draw) + 1):
        if draw - i > pool - relevant:
            continue
        acc += comb(relevant, i) * comb(pool - relevant, draw - i)
    return acc / total


def can_stop(
    found_relevant: int,
    unseen: int,
    sample_n: int,
    sample_relevant: int,
    *,
    target_recall: float = 0.95,
    alpha: float = 0.05,
) -> StopVerdict:
    """May the run stop, at `target_recall` with confidence `1 - alpha`?

    `found_relevant` is what screening has turned up so far; `unseen` is the size
    of the remainder; `sample_n`/`sample_relevant` describe a RANDOM sample drawn
    from that remainder.
    """
    if sample_n > unseen:
        raise ValueError(f"sample_n={sample_n} exceeds the unseen remainder ({unseen})")
    if not 0 < target_recall < 1:
        raise ValueError("target_recall must be strictly between 0 and 1")

    caveat = (
        "Valid only if the sample was drawn AT RANDOM from the remainder. A sample taken in rank "
        "order measures the ranker, not the pool, and this guarantee silently evaporates."
    )

    if unseen == 0:
        return StopVerdict(True, 0.0, 0, "nothing left to screen — the pool is exhausted", caveat)

    # To hold recall at the target given what is already found, the remainder may
    # hide at most this many relevant items.
    max_missable = int(found_relevant * (1 - target_recall) / target_recall)

    # H0: the remainder hides MORE than that, i.e. at least max_missable + 1.
    k_null = max_missable + 1
    p = _hypergeom_at_most(sample_relevant, unseen, min(k_null, unseen), sample_n)

    if p < alpha:
        why = (f"a random sample of {sample_n} from the {unseen} unseen found {sample_relevant} "
               f"relevant; under H0 (>{max_missable} still hiding) that has p={p:.4f} < {alpha}. "
               f"Reject H0 — recall >= {target_recall:.0%} at {1 - alpha:.0%} confidence.")
        return StopVerdict(True, p, max_missable, why, caveat)

    why = (f"not enough evidence to stop: p={p:.4f} >= {alpha}. With {found_relevant} found, the "
           f"remainder may hide up to {max_missable} and still meet {target_recall:.0%} recall — "
           f"a sample of {sample_n} finding {sample_relevant} does not rule out more than that. "
           "Screen further or draw a larger random sample; the criterion sharpens as you do.")
    return StopVerdict(False, p, max_missable, why, caveat)


__all__ = ["StopVerdict", "can_stop"]
