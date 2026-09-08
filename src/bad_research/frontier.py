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
                    "seen_domains": sorted(self.seen_domains),
                    "seen_entities": sorted(self.seen_entities),
                    "log": self.log,
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
            seen_domains=set(d.get("seen_domains", [])),
            seen_entities=set(d.get("seen_entities", [])),
            log=list(d.get("log", [])),
        )
