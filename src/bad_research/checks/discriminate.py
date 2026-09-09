"""A filter that learns from the run's own decisions, and a canary that catches it overreaching.

**Why this exists.** Everything else in this kit accretes *entities* -- what you
now know that you did not know before. Nothing accretes a model of what the
GARBAGE looks like. So every reader begins its screening cold, from a
definition, with no memory of what the last cut established. The owner's thesis
is that the more context you hold the better you can both find and filter; this
is the filter half, made executable.

**How it accretes.** A reject-signal is a token that recurs across REJECTED
items and appears in NO accepted item. Two decisions buy almost nothing; twenty
buy a real filter. The screen is therefore a function of the run's own history,
and it sharpens as the history grows -- which is the claim, stated so it can be
tested rather than believed.

**The half nobody ships: the canary.** Known-good items are planted in the pool.
If the current rules would kill one, the filter has become too aggressive and
the run is told WHICH RULE did it, before the cut ships. This is the cheapest
available detector for the error that is otherwise invisible -- precision is
easy to see (bad things that got through) while a filter's false negatives leave
no trace at all. The measured cost of not having it, from this project: a reader
screening a staff directory cut 156 rows and named three well-known researchers
among the casualties, in its own words "my false-negative, not their false
positive." Nothing was watching.

**And with no canaries the verdict is `None`, never `True`.** A filter nobody is
measuring is an unmeasured filter, not a safe one, and the two must never print
the same way -- the same rule that governs a check that never ran.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

# A token must explain at least this many rejections before it is a rule. One
# rejection is an anecdote; the whole point is that the filter earns its edges.
MIN_SUPPORT = 2

# Words too common to discriminate anything. Deliberately short: every entry is
# a word the filter can no longer learn from, and this list is the easiest place
# to blind it by accident.
_STOP = frozenset({
    "the", "and", "for", "with", "from", "that", "this", "have", "has", "was",
    "are", "not", "but", "all", "any", "who", "his", "her", "its", "their",
    "a", "an", "of", "in", "on", "at", "to", "is", "as", "by", "or",
})
_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9+.#-]{2,}")


@dataclass(frozen=True)
class Decision:
    """One screening call the run already made, and why."""

    item: str
    verdict: str          # accept | reject
    because: str

    def __post_init__(self) -> None:
        if self.verdict not in ("accept", "reject"):
            raise ValueError(f"verdict must be accept or reject, got {self.verdict!r}")
        if not self.because.strip():
            raise ValueError("a decision without a reason teaches the filter nothing")


@dataclass(frozen=True)
class Cut:
    """One item the filter removed, and the rule that removed it."""

    item: str
    because: str


@dataclass(frozen=True)
class ScreenReport:
    considered: int
    kept: tuple[Cut, ...]
    rejected: tuple[Cut, ...]
    abstained: tuple[Cut, ...]
    canaries_killed: tuple[Cut, ...]
    canaries_untested: tuple[str, ...]
    safe: bool | None
    caveat: str

    def to_dict(self) -> dict[str, object]:
        return {
            "considered": self.considered,
            "kept": [c.item for c in self.kept],
            "rejected": [{"item": c.item, "because": c.because} for c in self.rejected],
            "abstained": [{"item": c.item, "because": c.because} for c in self.abstained],
            "canaries_killed": [{"item": c.item, "because": c.because} for c in self.canaries_killed],
            "canaries_untested": list(self.canaries_untested),
            "safe": self.safe,
            "caveat": self.caveat,
        }


def _tokens(text: str) -> set[str]:
    return {t.casefold() for t in _TOKEN.findall(text)} - _STOP


@dataclass
class Discriminator:
    """Screens candidates using rules derived from the decisions already made."""

    decisions: list[Decision] = field(default_factory=list)
    canaries: set[str] = field(default_factory=set)
    # Never classify an item you do not have enough of -- pass it through instead.
    # From the sweep: a shipped clinical screening classifier's 5.7 points of
    # recall came ENTIRELY from an abstain rule of exactly this shape, not from
    # the model. Without it the pipeline silently deleted 3,600 real included
    # studies; with it, 224. A short item matches few tokens, so a token-based
    # filter is least reliable exactly where it looks most confident. Defaults to
    # 0 (off) so switching it on is a deliberate choice, not a surprise.
    min_evidence_chars: int = 0

    def record(self, d: Decision) -> None:
        self.decisions.append(d)

    def reject_signals(self) -> dict[str, int]:
        """Tokens that recur in rejected items and appear in NO accepted one.

        The exclusion is the important half. A token present in even one
        accepted item is not evidence of garbage -- it is evidence the token is
        about the subject matter, and learning it as a rule is exactly how a
        filter starts deleting the good ones.
        """
        accepted: set[str] = set()
        counts: dict[str, int] = {}
        for d in self.decisions:
            if d.verdict == "accept":
                accepted |= _tokens(d.item)
        for d in self.decisions:
            if d.verdict != "reject":
                continue
            for t in _tokens(d.item) - accepted:
                counts[t] = counts.get(t, 0) + 1
        return {t: n for t, n in counts.items() if n >= MIN_SUPPORT}

    def _why_rejected(self, item: str, signals: dict[str, int]) -> str | None:
        hit = sorted(_tokens(item) & signals.keys(), key=lambda t: (-signals[t], t))
        if not hit:
            return None
        return (f"matched learned reject-signal {hit[0]!r} "
                f"(explains {signals[hit[0]]} prior rejections)")

    def screen(self, candidates: Iterable[str]) -> ScreenReport:
        """Apply what the run has learned -- and check it has not learned too much."""
        signals = self.reject_signals()
        kept: list[Cut] = []
        rejected: list[Cut] = []
        abstained: list[Cut] = []
        considered = 0
        for c in candidates:
            considered += 1
            if self.min_evidence_chars and len(c.strip()) < self.min_evidence_chars:
                abstained.append(Cut(c, f"ABSTAIN — too little to judge on "
                                        f"({len(c.strip())} < {self.min_evidence_chars} chars); "
                                        "passed through rather than cut"))
                continue
            why = self._why_rejected(c, signals)
            (rejected if why else kept).append(Cut(c, why or "no reject-signal matched"))

        killed = tuple(
            Cut(c, why) for c in sorted(self.canaries)
            if (why := self._why_rejected(c, signals))
        )

        # A canary is only evidence if it was actually SCREENED. "Plant known-good
        # items in the pool" has to mean literally in the pool: a canary held in a
        # separate list is a note-to-self, not an instrument, because nothing
        # guarantees it is even the same shape as what the filter is judging.
        #
        # Found by driving this tool, after two weaker heuristics failed. A canary
        # written "Tim Dettmers | QLoRA, bitsandbytes" reported SURVIVED while the
        # filter cut "Tim Dettmers | Allen Institute for AI" from the candidates —
        # same person, different form, and no rule learned from that pool could
        # ever have touched the canary. Proximity heuristics could not separate the
        # two, because the person's own NAME supplies the shared vocabulary. So the
        # rule is the strict one: screened, or it tested nothing.
        screened = {c.item for c in [*kept, *rejected, *abstained]}
        untested = tuple(c for c in sorted(self.canaries) if c not in screened)

        if not self.canaries:
            safe, caveat = None, (
                "UNMEASURED — no canaries were planted, so this filter's false-negative rate is "
                "unknown. That is not the same as low. Plant known-good items in the pool."
            )
        elif len(untested) == len(self.canaries):
            safe, caveat = None, (
                f"UNMEASURED — none of the {len(self.canaries)} canaries was in the candidate pool, "
                "so none was screened and none could have been killed. Their survival is not "
                "evidence. Put the canaries INTO the pool, in the form the candidates take."
            )
        elif killed:
            safe, caveat = False, (
                f"UNSAFE — the current rules would kill {len(killed)} known-good item(s). The filter "
                "has over-learned; drop the named signal or add accepted examples that carry it."
            )
        else:
            live = len(self.canaries) - len(untested)
            safe, caveat = True, (
                f"{live} of {len(self.canaries)} canaries were screened by this pool and survived"
                + (f"; {len(untested)} were not in the pool and tested nothing. " if untested else ". ")
                + "That bounds the false-negative rate only for garbage resembling those items."
            )
        return ScreenReport(considered, tuple(kept), tuple(rejected), tuple(abstained),
                            killed, untested, safe, caveat)


@dataclass(frozen=True)
class SignalRank:
    """A pool ordered by a cheap structural signal, with its recall if measurable."""

    ranked: tuple[tuple[str, int], ...]
    zero: tuple[str, ...]
    scored: int
    recall_at_k: float | None
    missed_at_k: tuple[str, ...]
    caveat: str

    def to_dict(self) -> dict[str, object]:
        return {
            "scored": self.scored,
            "ranked": [{"item": n, "score": s} for n, s in self.ranked],
            "zero": list(self.zero),
            "recall_at_k": self.recall_at_k,
            "missed_at_k": list(self.missed_at_k),
            "caveat": self.caveat,
        }


def rank_by_signal(
    pool: Mapping[str, str],
    signal: str,
    *,
    known_good: set[str] | None = None,
    top_k: int | None = None,
) -> SignalRank:
    """Order a pool by how often a cheap structural signal fires, before reading any of it.

    Reject-signals have to be learned from decisions, and at the start of a run
    there are none -- so this is the cold-start half. It is the cascade shape:
    a free filter first, the expensive read last.

    Measured on this corpus: 407 product teardowns, 5 of them known to carry
    researcher names. Counting author/arXiv markers costs nothing, gives **313
    files a score of zero**, and puts all five known-good files in the **top 20**
    -- a 20x cut in reading cost at full recall on the known set.

    Two honest limits, both structural. The signal is question-specific: author
    markers stand in for researchers and stand in for nothing else, so a
    different question needs a different signal and inherits none of this
    measurement. And `recall_at_k` is agreement with whoever supplied
    `known_good`, not with truth -- which is why it is `None` rather than 1.0
    when nobody supplied any.
    """
    pat = re.compile(signal, re.M)
    scores = sorted(((n, len(pat.findall(t))) for n, t in pool.items()),
                    key=lambda kv: (-kv[1], kv[0]))
    zero = tuple(n for n, s in scores if s == 0)

    recall: float | None = None
    missed: tuple[str, ...] = ()
    if known_good:
        k = top_k if top_k is not None else len(scores)
        top = {n for n, _ in scores[:k]}
        found = known_good & top
        recall = len(found) / len(known_good)
        missed = tuple(sorted(known_good - top))
        caveat = (f"recall {recall:.0%} at k={k} against {len(known_good)} planted item(s) — "
                  "that is agreement with whoever planted them, not with truth")
    else:
        caveat = ("UNMEASURED — no known-good items were planted, so this ranking's recall is "
                  "unknown. Rank order is not evidence of coverage.")

    return SignalRank(tuple(scores), zero, len(scores), recall, missed, caveat)


__all__ = ["MIN_SUPPORT", "Cut", "Decision", "Discriminator", "ScreenReport", "SignalRank",
           "rank_by_signal"]
