"""The entity frontier and the harness-computed stop counters.

Pure stdlib, no I/O: the research loop's next query must name something the loop
actually learned, and the decision to stop is COMPUTED from what came back rather
than self-reported by the model that wants to keep going.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

MIN_NEW_DOMAINS = 2   # MIN_SOURCES_PER_SUBQ / RESERVE_FOR_SYNTHESIS land with the lane (slice 2)


@dataclass
class Frontier:
    """Entities/quantities learned from a read and not yet explored."""

    items: set[str] = field(default_factory=set)

    def add(self, new: set[str]) -> None:
        self.items |= {t for t in new if t}

    def close(self, item: str) -> None:
        self.items.discard(item)


def _norm_tokens(text: str) -> set[str]:
    """Casefolded tokens with trailing punctuation stripped.

    `$0.66` yields `0.66` on both sides so a quantity matches itself, and a
    trailing period no longer welds itself onto the token before it.
    """
    raw = re.findall(r"[A-Za-z0-9][\w.\-]*", text)
    return {t.casefold().rstrip(".-") for t in raw} - {""}


def gate_query(query: str, frontier: Frontier, first: bool = False) -> tuple[bool, list[str]]:
    """Refuse a query naming no frontier item. The first query is exempt (spec R1).

    An item is NAMED when every one of its tokens appears in the query, so a
    multi-token item ("GB200 NVL72") and a quantity ("$0.66") both match — three
    of R1's five item types are multi-token by construction, and an equality test
    against single tokens could never name any of them.
    """
    if first:
        return True, []
    qt = _norm_tokens(query)
    named = sorted(
        i for i in frontier.items
        if (it := _norm_tokens(i)) and it <= qt   # `and it` — an item with no
    )                                            # tokens must not match everything
    return bool(named), named


@dataclass
class StopCounters:
    """Computed by the harness BEFORE the prompt is built, never self-reported."""

    seen_domains: set[str] = field(default_factory=set)
    seen_entities: set[str] = field(default_factory=set)
    steps: int = 0
    last_new_domains: int = 0
    last_new_entities: int = 0

    def observe(self, domains: set[str], entities: set[str]) -> None:
        self.last_new_domains = len(domains - self.seen_domains)
        self.last_new_entities = len(entities - self.seen_entities)
        self.seen_domains |= domains
        self.seen_entities |= entities
        self.steps += 1

    def should_stop(self) -> bool:
        if self.steps < 2:
            return False
        return self.last_new_domains < MIN_NEW_DOMAINS and self.last_new_entities == 0


@dataclass
class FrontierState:
    """Durable frontier + the run log that makes the gate auditable.

    This is what gives `gate_query` a production caller. Without one the rule is a
    pure function nothing invokes, which is the same as not having the rule: prose
    on a post-trained model is worth ~7%, and the failure it guards against is
    measured — an agent "repeatedly searching for similar keywords despite
    retrieving relevant objects", continuing after the answer was already in hand.

    The log records, per query, whether it was allowed and WHICH item it named.
    That is the artifact the end-to-end check reads: a run whose post-first queries
    name nothing learned from a read has not accreted, whatever else it produced.
    """

    items: set[str] = field(default_factory=set)
    seen_domains: set[str] = field(default_factory=set)
    seen_entities: set[str] = field(default_factory=set)
    log: list[dict[str, object]] = field(default_factory=list)
    rounds: list[dict[str, object]] = field(default_factory=list)
    steps: int = 0
    last_new_domains: int = 0
    last_new_entities: int = 0
    # What the answer OWES. The scalar counters above say what arrived; these say
    # what is still promised. A round can add three entities and close no cell,
    # and both counters rise while the answer has not advanced -- which is why the
    # strongest accretion mechanism in the corpus keeps a per-instance outcome
    # VECTOR rather than a score: "target what the last attempt failed at" is not
    # computable from a number.
    open_cells: set[str] = field(default_factory=set)
    closed_cells: set[str] = field(default_factory=set)
    abandoned: dict[str, str] = field(default_factory=dict)

    def close_cell(self, cell: str) -> None:
        """Mark a promised cell filled. Refuses one that was never promised.

        Without the refusal a run can empty its own obligations by inventing
        closures, which is the same move as editing the check that grades you.
        """
        if cell not in self.open_cells:
            raise KeyError(f"{cell!r} was never promised — cannot close a cell nobody asked for")
        self.open_cells.discard(cell)
        self.closed_cells.add(cell)

    def abandon_cell(self, cell: str, because: str) -> None:
        """Give up on a cell, with a reason, so it stops holding the run open.

        A cell nothing can fill must not become an infinite loop. Abandoning it is
        a legal outcome -- it is what the answer's "what I could not establish"
        section is for -- but it costs a stated reason, so an abandonment and a
        quiet drop never look the same.
        """
        if cell not in self.open_cells:
            raise KeyError(f"{cell!r} was never promised — cannot abandon a cell nobody asked for")
        if not because.strip():
            raise ValueError("abandoning a promised cell requires a reason")
        self.open_cells.discard(cell)
        self.abandoned[cell] = because

    def residual(self) -> list[str]:
        """WHICH cells are still owed -- a scalar count cannot be acted on."""
        return sorted(self.open_cells)

    def observe_round(self, domains: set[str], entities: set[str]) -> None:
        """Record what a retrieval round actually brought back, in code.

        This runs BEFORE the next prompt is built, so the stop signal is auditable
        from the run's own counters even if the model would rather keep going. Every
        surveyed system either has no stopping rule, a constant a human picked, or a
        convergence check that cannot fire; the common failure is asking the model
        whether it is done, and a model that wants to keep searching is not a
        reliable witness to diminishing returns.
        """
        c = StopCounters(
            seen_domains=set(self.seen_domains),
            seen_entities=set(self.seen_entities),
            steps=self.steps,
        )
        c.observe(domains, entities)
        self.seen_domains, self.seen_entities = c.seen_domains, c.seen_entities
        self.steps = c.steps
        self.last_new_domains, self.last_new_entities = c.last_new_domains, c.last_new_entities
        self.rounds.append({
            "step": self.steps,
            "new_domains": self.last_new_domains,
            "new_entities": self.last_new_entities,
            "should_stop": self.should_stop(),
        })

    def should_stop(self) -> bool:
        """True when nothing new arrived AND nothing is still owed.

        Both halves are required. The scalar half alone reads as progress: a round
        that added three entities and closed none of the promised cells moves both
        counters while the answer stands still. The cell half alone would hold a
        run open forever on a cell nothing can fill -- which is why `abandon_cell`
        exists and takes a reason.
        """
        if self.steps < 2:
            return False
        quiet = self.last_new_domains < MIN_NEW_DOMAINS and self.last_new_entities == 0
        return quiet and not self.open_cells

    @property
    def frontier(self) -> Frontier:
        return Frontier(items=set(self.items))

    def gate_and_log(self, query: str) -> tuple[bool, list[str]]:
        """Gate one query and append the decision to the run log."""
        first = not self.log
        allowed, named = gate_query(query, self.frontier, first=first)
        self.log.append(
            {"query": query, "first": first, "allowed": allowed, "named": named}
        )
        return allowed, named

    def save(self, path: Path) -> None:
        path.write_text(
            json.dumps(
                {
                    "items": sorted(self.items),
                    "open_cells": sorted(self.open_cells),
                    "closed_cells": sorted(self.closed_cells),
                    "abandoned": dict(self.abandoned),
                    "seen_domains": sorted(self.seen_domains),
                    "seen_entities": sorted(self.seen_entities),
                    "log": self.log,
                    "rounds": self.rounds,
                    "steps": self.steps,
                    "last_new_domains": self.last_new_domains,
                    "last_new_entities": self.last_new_entities,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Path) -> FrontierState:
        if not path.exists():
            return cls()
        d = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            items=set(d.get("items", [])),
            open_cells=set(d.get("open_cells", [])),
            closed_cells=set(d.get("closed_cells", [])),
            abandoned=dict(d.get("abandoned", {})),
            seen_domains=set(d.get("seen_domains", [])),
            seen_entities=set(d.get("seen_entities", [])),
            log=list(d.get("log", [])),
            rounds=list(d.get("rounds", [])),
            steps=int(d.get("steps", 0)),
            last_new_domains=int(d.get("last_new_domains", 0)),
            last_new_entities=int(d.get("last_new_entities", 0)),
        )


# Words that are frequent enough that emitting them as frontier items would make the
# gate nameable by almost any query — the opposite of what it is for. Cue
# diagnosticity (how uniquely a cue selects one item) is what predicts retrieval, so
# a producer that emits common words grows the frontier and weakens the gate at once.
_STOP = {
    "the", "this", "that", "these", "those", "with", "from", "into", "over", "under",
    "when", "where", "which", "while", "there", "their", "here", "than", "then",
    "have", "has", "had", "was", "were", "been", "being", "are", "is", "and", "but",
    "for", "not", "all", "any", "each", "more", "most", "some", "such", "only",
    "also", "does", "did", "done", "will", "would", "could", "should", "about",
    "result", "results", "thing", "things", "work", "works", "well", "very", "much",
    "one", "two", "three", "first", "second", "same", "other", "another", "both",
}

# Capitalised only because they start a sentence — never the head of an entity.
_LEADING_NOISE = {
    "on", "in", "at", "by", "for", "the", "a", "an", "and", "but", "or", "if",
    "when", "while", "with", "from", "to", "of", "as", "so", "then", "this",
    "that", "these", "those", "it", "its", "we", "our", "they", "their", "here",
    "there", "both", "each", "every", "no", "not", "only", "also", "however",
}

# A capitalised or alphanumeric token that carries a specific referent: a model name
# (GB200, H200), a method (Adaptive-RAG), an acronym (EM, NAACL), a versioned id.
# The en-dash branch is deliberate: real corpus text hyphenates method names
# with an en dash, and dropping that branch would silently miss those entities.
_ENTITY = re.compile(r"\b(?:[A-Z][A-Za-z0-9]*(?:[-–][A-Za-z0-9]+)+|[A-Z]{2,}[0-9]*|[A-Z][a-z]+[0-9]+|[A-Za-z]+[0-9]{2,}(?:[A-Za-z0-9]*)?)\b")  # noqa: RUF001
# A figure the question did not contain — but ONLY one carrying a referent: money,
# a percentage, an arXiv id, or a number bound to a unit. A bare decimal is NOT a
# frontier item. Measured: the first version matched any decimal and produced 348
# items from 40k chars of one teardown, most of them raw floats like
# "0.069180676288051". A frontier that large is nameable by accident, which
# disables the gate quietly — the failure mode this producer's own docstring warns
# about. Under-emitting costs a hop; over-emitting costs the check.
_QUANTITY = re.compile(
    r"\b(?:arXiv:?\s?)?\d{4}\.\d{4,5}\b"                       # arXiv id
    r"|\$\d[\d,]*(?:\.\d+)?"                                     # money
    r"|\b\d[\d,]*(?:\.\d+)?\s?%"                                # percentage
    r"|\b\d[\d,]*(?:\.\d+)?\s?(?:EM|F1|BAcc|GB|TB|MB|kW|hr|ms)\b"  # number + word unit
    # No trailing \b for the symbol units: \b after a multiplication sign or "/"
    # requires a word character next, so "3.8x" and "22,282 tok/s" never matched. Caught
    # by testing whether the branch fires rather than by reading the pattern.
    r"|\b\d[\d,]*(?:\.\d+)?\s?(?:tok/s|×|x(?![A-Za-z]))"  # noqa: RUF001
)
# Two or three capitalised/alphanumeric tokens in a row — a multi-word entity.
_MULTI = re.compile(r"\b(?:[A-Z][A-Za-z0-9]*|[A-Z]{2,}[0-9]*)(?:\s+(?:[A-Z][A-Za-z0-9]*|[A-Z]{2,}[0-9]*)){1,2}\b")


def extract_frontier_items(body: str, question: str) -> set[str]:
    """Entities and quantities present in `body` and absent from `question`.

    This is the producer the gate depends on. Without it the frontier stays empty,
    every query after the first names nothing, and the loop stalls rather than
    accreting — the rule has to be survivable as well as strict.

    Deliberately narrow. It emits things with a specific referent (a model name, a
    method, an arXiv id, a figure) and refuses common words, because every item added
    is another way for a lazy query to satisfy the gate. Under-emitting costs a hop;
    over-emitting silently disables the check.
    """
    known = {t.casefold().rstrip(".-,;:") for t in re.findall(r"[A-Za-z0-9][\w.\-]*", question)}
    out: set[str] = set()

    for pat in (_MULTI, _ENTITY, _QUANTITY):
        # A quantity already earned its place by carrying a referent (money, a
        # percentage, an arXiv id, a unit), so the common-word guard below must not
        # be applied to it. Measured: that guard silently ate "3.8x" and
        # "22,282 tok/s", because both tokenize to pieces of three characters or
        # fewer and the guard drops an item whose every token is that short. The
        # guard is right for prose and wrong for figures.
        is_quantity = pat is _QUANTITY
        for raw in pat.findall(body):
            item = raw.strip().rstrip(".,;:)")
            # A sentence-initial function word gets capitalised by grammar, not by
            # being a name: "On Natural Questions" is one entity plus a preposition.
            # Leaving it in makes the cue less diagnostic and the item harder to name.
            parts = item.split()
            while len(parts) > 1 and parts[0].casefold() in _LEADING_NOISE:
                parts = parts[1:]
            item = " ".join(parts)
            if not item:
                continue
            toks = {t.casefold().rstrip(".-") for t in re.findall(r"[A-Za-z0-9][\w.\-]*", item)}
            if not toks or toks <= known:
                continue                      # nothing new in it
            if not is_quantity and all(t in _STOP or len(t) <= 3 for t in toks):
                continue                      # no diagnostic token
            # Must be nameable by the gate that consumes it, or it is dead weight.
            if not _norm_tokens(item):
                continue
            out.add(item)

    # Prefer the longer form when one item's tokens contain another's ("GB200 NVL72"
    # over "GB200"): the longer cue is the more diagnostic one.
    redundant = {
        a for a in out for b in out
        if a != b and _norm_tokens(a) < _norm_tokens(b)
    }
    return out - redundant
