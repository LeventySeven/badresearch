"""An open contradiction blocks the close -- computed, not self-reported.

`contradiction.py` gives a run a way to NOTICE that two sources disagree.
Noticing is worth nothing by itself. The measured failure is not that agents
miss a discrepancy, it is what they do next: they average it away, or take the
newer number and move on. The field's canonical memory benchmark defines
correct handling of a conflicting fact as *overwriting the stale value*, so a
system trained toward that benchmark is trained to destroy the single most
valuable thing a research run finds. This module is the counterweight -- the
disagreement gets to stop the run.

**Load-bearing is a fact about two strings.** A contradiction blocks the close
if and only if its subject appears in the answer being shipped. Nothing here
asks a model whether a disagreement "matters", because a model that wants to
finish is not a reliable witness to that, and a model that wants another round
is not either. Computing it also removes the incentive to manufacture: a
contradiction about a subject the draft never discusses cannot hold the close
open, whatever its delta, so inventing one buys no extra round.

**Closing one is an act with a record.** Two dispositions are legal and neither
is a default. `ranked` says which side you believe and why. `unresolved` says
the record genuinely disagrees and you could not settle it -- a real answer, not
a failure, and the honest one more often than agents behave as though. What is
not legal is silence, or a reason field with nothing in it.

**The known limit, stated rather than papered over.** "Load-bearing" is a
substring test on the subject, so an answer that paraphrases the subject --
"H100 hourly rate" where the claim said "H100 on-demand" -- files a real
disagreement as cosmetic and the gate goes quiet. Fuzzy subject matching would
close that hole and open a worse one, blocking closes over pairs that are not
about the same thing at all; a check that cries wolf gets switched off. So the
gate is a floor, not a proof: it catches the disagreement you already named
consistently, and it never certifies that none was missed.

**A disposition is not a licence to drop a side.** Even a ranked contradiction
must reach the reader carrying both values, both sources, and both capture dates
where those dates are known. Without that clause "I resolved it" and "I deleted
the inconvenient number" produce identical output.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from bad_research.checks.contradiction import Claim, Contradiction

# `ranked` and `unresolved` are the only two ways to close. There is deliberately
# no `dismissed`: a contradiction the answer does not touch is already cosmetic
# and never reaches this decision, so a third disposition could only ever be used
# to wave away one that does.
DISPOSITIONS = ("ranked", "unresolved")

# Formatting tolerance only -- "2.490" and "2.49" are the same number. This is
# NOT the tolerance that decides whether two claims disagree; that one lives in
# `find_contradictions` and is the caller's to set.
_FORMAT_TOLERANCE = 1e-9

_NUMBER_IN_TEXT = re.compile(r"(?<![\w.])[+-]?\d[\d,]*(?:\.\d+)?(?![\w])")


@dataclass(frozen=True)
class Disposition:
    """How the run closed one contradiction, and why."""

    contradiction_id: str
    kind: str          # ranked | unresolved
    because: str

    def to_dict(self) -> dict[str, str]:
        return {
            "contradiction_id": self.contradiction_id,
            "kind": self.kind,
            "because": self.because,
        }


@dataclass(frozen=True)
class Blocker:
    """One reason a specific contradiction is still holding the close open."""

    contradiction_id: str
    subject: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {
            "contradiction_id": self.contradiction_id,
            "subject": self.subject,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class CloseReport:
    """Whether the answer may ship, and every reason it may not."""

    blockers: tuple[Blocker, ...]
    load_bearing: tuple[str, ...]
    cosmetic: tuple[str, ...]

    @property
    def can_close(self) -> bool:
        return not self.blockers

    def to_dict(self) -> dict[str, object]:
        return {
            "can_close": self.can_close,
            "blockers": [b.to_dict() for b in self.blockers],
            "load_bearing": list(self.load_bearing),
            "cosmetic": list(self.cosmetic),
        }


def _norm(text: str) -> str:
    return " ".join(text.split()).casefold()


def contradiction_id(c: Contradiction) -> str:
    """A stable id for one disagreement, symmetric in the pair.

    Symmetric because the two sides arrive in whatever order the claim list
    happened to be in, and a disposition written during one step has to still
    match on the next. An id that flipped with the argument order would silently
    reopen every contradiction the run had already closed.
    """
    sides = sorted(
        f"{_norm(x.subject)}|{_norm(x.unit)}|{_norm(x.value)}|{_norm(x.source)}"
        for x in (c.left, c.right)
    )
    return hashlib.sha256("\x1e".join(sides).encode("utf-8")).hexdigest()[:16]


def _as_number(value: str) -> float | None:
    cleaned = value.strip().replace(",", "").lstrip("$€£¥").rstrip("%").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def _value_present(value: str, answer: str) -> bool:
    """Is this claim's value visible in the answer?

    A number is matched as a NUMBER, not as a substring: `$2.49/hr`, `2.490` and
    `2.49` are the same value to a reader, and a substring test would also match
    the `2.49` inside `12.49`, which is a different rate entirely. Prose is
    matched as normalised text.
    """
    target = _as_number(value)
    if target is None:
        return _norm(value) in _norm(answer)
    for token in _NUMBER_IN_TEXT.findall(answer):
        found = _as_number(token)
        if found is not None and abs(found - target) <= _FORMAT_TOLERANCE * max(1.0, abs(target)):
            return True
    return False


def _side_blockers(cid: str, subject: str, side: Claim, answer: str) -> list[Blocker]:
    """Everything this side of the disagreement owes the reader."""
    out: list[Blocker] = []
    if not _value_present(side.value, answer):
        out.append(Blocker(cid, subject, (
            f"the answer drops the value {side.value} ({side.unit}) from {side.source} -- "
            "ranking a side does not license deleting the one you ruled against"
        )))
    if _norm(side.source) not in _norm(answer):
        out.append(Blocker(cid, subject,
                           f"the answer does not name the source {side.source}"))
    if side.as_of and _norm(side.as_of) not in _norm(answer):
        out.append(Blocker(cid, subject, (
            f"the answer drops the as-of date {side.as_of} for {side.source} -- "
            "without both dates a reader cannot tell a discrepancy from a stale value"
        )))
    return out


def evaluate_close(
    contradictions: Sequence[Contradiction],
    answer: str,
    dispositions: Iterable[Disposition] = (),
) -> CloseReport:
    """Decide whether `answer` may ship while these contradictions are on the table.

    A contradiction is load-bearing when its subject appears in `answer`. Each
    load-bearing one needs a disposition carrying a real reason, and both of its
    sides have to survive into the answer with provenance and dating.
    """
    by_id = {d.contradiction_id: d for d in dispositions}
    blockers: list[Blocker] = []
    load_bearing: list[str] = []
    cosmetic: list[str] = []

    for c in contradictions:
        cid = contradiction_id(c)
        subject = c.left.subject
        if _norm(subject) not in _norm(answer):
            cosmetic.append(cid)
            continue
        load_bearing.append(cid)

        d = by_id.get(cid)
        if d is None:
            blockers.append(Blocker(cid, subject, (
                f"no disposition recorded for the disagreement about {subject!r} "
                f"({c.left.source} says {c.left.value}, {c.right.source} says "
                f"{c.right.value}) -- rank it or record it unresolved"
            )))
            continue
        if d.kind not in DISPOSITIONS:
            blockers.append(Blocker(cid, subject,
                                    f"unknown disposition {d.kind!r}; expected one of {DISPOSITIONS}"))
            continue
        if not d.because.strip():
            blockers.append(Blocker(cid, subject, (
                f"the {d.kind} disposition carries no reason -- "
                '"sources differ" with no verdict and no reason is not an answer'
            )))

        blockers += _side_blockers(cid, subject, c.left, answer)
        blockers += _side_blockers(cid, subject, c.right, answer)

    return CloseReport(tuple(blockers), tuple(load_bearing), tuple(cosmetic))


__all__ = [
    "DISPOSITIONS",
    "Blocker",
    "CloseReport",
    "Disposition",
    "contradiction_id",
    "evaluate_close",
]
