"""The no-source-claim check: an absence claim the run's own corpus contradicts.

**The defect this reproduces.** In a live run a report asserted *"No source was
found for GPU depreciation schedules... PUE, cooling overhead. This is the
largest evidentiary gap in this report"* — while a note the SAME report cited
elsewhere carried a 36-month straight-line schedule, an explicit PUE of 1.2, and
tiered ops-labour rates. The gap was in the reading, not in the corpus. A model
critic caught it. This module makes that catch a script.

**How it decides.** Two stages, both cheap and both deliberately conservative:

1. A sentence must match one of a small set of *absence phrasings* — "no source
   was found for X", "no published X", "X is not available", "I could not
   establish X", "no data on X". A sentence that never claims an absence is
   never examined, however well the corpus covers it.
2. The subject's **content words** must then co-occur, **two or more of them**,
   inside a single note body. One shared word is not evidence: "no source was
   found for the cost of tunnelling" against a note about "the cost of a coffee"
   shares *cost* and means nothing.

**Why the acronym carve-out exists.** Content words are normally longer than
three characters — that filter removes function words cheaply. Applied bare it
also removes PUE, GPU, TCO, ROI, which in this domain are the highest-signal
terms in the sentence, and it removes them from the exact defect above: drop PUE
and the reproducer is left with one shared word and goes quiet. All-caps
acronyms are therefore kept. Bare numbers are dropped in the same pass, because
a year matching a year is a coincidence, not a subject.

Matching is on whole tokens, never substrings — "PUE" must not be found inside
"Puerto".
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

# ── absence phrasings ────────────────────────────────────────────────────────
# Narrow by design. Every trigger added here widens what the check will examine,
# and the co-occurrence stage is the only thing standing between a loose trigger
# and a false positive. Prefix forms take the subject to the end of the
# sentence; the one suffix form takes it from the start.
_ABSENCE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\bno\s+sources?\s+(?:was\s+|were\s+|could\s+be\s+)?found\s+(?:for|on)\s+(?P<subject>.+)",
        re.IGNORECASE,
    ),
    re.compile(r"\bno\s+published\s+(?P<subject>.+)", re.IGNORECASE),
    re.compile(r"\bno\s+data\s+(?:on|for)\s+(?P<subject>.+)", re.IGNORECASE),
    re.compile(
        r"\bI\s+could\s+not\s+(?:establish|find|locate)\s+(?P<subject>.+)",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(?P<subject>.+?)\s+(?:is|was|are|were)\s+not\s+available\b",
        re.IGNORECASE,
    ),
)

# Sentence break: end punctuation followed by whitespace, or a blank line. A
# single newline is NOT a break — reports are hard-wrapped and splitting on it
# would cut sentences in half and hide their triggers.
_SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+|\n\s*\n")

# Whole-token alphanumerics. Hyphens and slashes split ("36-month" -> 36, month;
# "$75/hour" -> 75, hour) so both sides of the comparison tokenize alike.
_TOKEN = re.compile(r"[A-Za-z0-9]+")

# Function words, plus the handful of research-generic nouns the absence
# phrasings themselves use. Kept short on purpose: every word added here is a
# word the check can no longer see, and this list is the easiest place to
# accidentally blind it.
_STOPWORDS: frozenset[str] = frozenset({
    "about", "after", "also", "and", "any", "are", "available", "because", "been",
    "before", "being", "both", "but", "can", "could", "data", "did", "does", "done",
    "during", "each", "either", "evidence", "for", "found", "from", "further", "had",
    "has", "have", "here", "how", "however", "into", "its", "itself", "just", "least",
    "less", "like", "made", "make", "many", "may", "might", "more", "most", "much",
    "must", "neither", "never", "not", "only", "onto", "other", "others", "our",
    "over", "own", "public", "published", "same", "shall", "should", "since", "some",
    "source", "sources", "such", "than", "that", "the", "their", "them", "then",
    "there", "these", "they", "this", "those", "through", "thus", "under", "until",
    "upon", "very", "was", "were", "what", "when", "where", "which", "while", "who",
    "whom", "whose", "why", "will", "with", "within", "without", "would", "yet",
})


@dataclass(frozen=True)
class UnfoundedAbsenceClaim:
    """One absence claim, and the one note body that contradicts it."""

    subject: str
    sentence: str
    note_id: str
    matched_words: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        """JSON-ready payload for `bad no-source-claim-gate --json`."""
        return {
            "subject": self.subject,
            "sentence": self.sentence,
            "note_id": self.note_id,
            "matched_words": list(self.matched_words),
        }


def content_words(subject: str) -> list[str]:
    """The tokens of `subject` that can carry evidence, lower-cased, in order.

    Kept: words longer than three characters, and all-caps acronyms of any
    length (PUE, GPU, TCO). Dropped: stopwords, bare numbers, and everything
    short that is neither.
    """
    out: list[str] = []
    for raw in _TOKEN.findall(subject):
        low = raw.casefold()
        if low in _STOPWORDS or low in out or raw.isdigit():
            continue
        is_acronym = raw.isupper() and raw.isalpha() and len(raw) >= 2
        if len(raw) > 3 or is_acronym:
            out.append(low)
    return out


def _sentences(report: str) -> list[str]:
    """Split a report body into whitespace-collapsed sentences."""
    return [s for s in (" ".join(p.split()) for p in _SENTENCE_BREAK.split(report)) if s]


def _absence_subject(sentence: str) -> str | None:
    """The subject of `sentence`'s absence claim, or None if it makes none."""
    for pattern in _ABSENCE_PATTERNS:
        match = pattern.search(sentence)
        if match:
            return match.group("subject").strip(" \t.,;:!?\"'()[]")
    return None


def count_absence_claims(report: str) -> int:
    """How many sentences in `report` claim an absence — findings or not.

    The enumeration number. A run that reports zero findings has to say whether
    it examined one claim or none, or an empty result is indistinguishable from
    a broken check.
    """
    return sum(1 for s in _sentences(report) if _absence_subject(s) is not None)


def find_unfounded_absence_claims(
    report: str,
    notes: Mapping[str, str],
    *,
    min_shared_words: int = 2,
) -> list[UnfoundedAbsenceClaim]:
    """Absence claims in `report` that a body in `notes` contradicts.

    One finding per (claim, contradicting note) pair, in report order then note
    order. `min_shared_words` is the co-occurrence bar; below 2 the check starts
    firing on incidental overlap and should not be trusted.
    """
    tokenized = {
        note_id: set(_TOKEN.findall(body.casefold())) for note_id, body in notes.items()
    }
    findings: list[UnfoundedAbsenceClaim] = []
    for sentence in _sentences(report):
        subject = _absence_subject(sentence)
        if subject is None:
            continue
        words = content_words(subject)
        if len(words) < min_shared_words:
            continue
        for note_id, tokens in tokenized.items():
            matched = tuple(w for w in words if w in tokens)
            if len(matched) >= min_shared_words:
                findings.append(
                    UnfoundedAbsenceClaim(subject, sentence, note_id, matched)
                )
    return findings


__all__ = [
    "UnfoundedAbsenceClaim",
    "content_words",
    "count_absence_claims",
    "find_unfounded_absence_claims",
]
