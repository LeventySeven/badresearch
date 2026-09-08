"""A quoted span is a promise that a source says exactly this. Bytes settle it.

The slice's adversarial check plants two defects. Asserting an absence the
corpus contradicts already has a gate. The other -- swapping a cited note's body
for a paraphrase supporting a different number -- had none, and every existing
check stays green through it: `recitation-gate` exits 0 by construction,
`uncited-gate` only asks whether a marker is *present*, and the semantic
verifier sits in the 55-60 balanced-accuracy band where an instrument may rank
but must not close.

So this one is decided structurally. Quotation marks are a claim about bytes,
and a claim about bytes is checkable for nothing -- which is the only kind of
check worth putting in front of a ship decision.

**Four outcomes, one of them innocent.** They are named separately because
collapsing them is the same error the four-kinds-of-nothing table exists to
prevent: MATCHED, DRIFTED (the words are real but live in a *different* note --
misattribution), ABSENT (no note contains them -- the note moved under the quote,
or the quote was never in one), and UNRESOLVED (the marker points nowhere).
Fabrication and misfiling need different fixes, so they get different words.

**What it deliberately does not flag.** A short quoted phrase is scare quotes or
a term of art, not a citation promise, so the gate ignores anything under
`MIN_QUOTED_CHARS`. A quotation carrying no marker is `uncited-gate`'s business,
not this one. Both exclusions exist because a gate that cries wolf gets switched
off, and a gate that is switched off catches nothing at all.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

# Below this a quoted string is a term of art ("agentic", "context engineering"),
# not a promise that a source contains those exact bytes.
MIN_QUOTED_CHARS = 40

# How far after a closing quote a citation marker may sit and still be read as
# attributing it. Wide enough for `." [3]` and `," per the build sheet [3]`.
_ATTRIBUTION_WINDOW = 60

_QUOTED = re.compile(rf'["“]([^"“”]{{{MIN_QUOTED_CHARS},}}?)["”]')
_MARKER = re.compile(r"\[(\d+)\]")


@dataclass(frozen=True)
class DriftFinding:
    """One quoted span, where it was said to come from, and where it actually is."""

    quoted: str
    marker: int
    cited_note: str | None
    outcome: str               # MATCHED | DRIFTED | ABSENT | UNRESOLVED
    found_in: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "quoted": self.quoted,
            "marker": self.marker,
            "cited_note": self.cited_note,
            "outcome": self.outcome,
            "found_in": self.found_in,
        }


@dataclass(frozen=True)
class DriftReport:
    findings: tuple[DriftFinding, ...] = field(default_factory=tuple)

    @property
    def ok(self) -> bool:
        return all(f.outcome == "MATCHED" for f in self.findings)

    def to_dict(self) -> dict[str, object]:
        return {"ok": self.ok, "findings": [f.to_dict() for f in self.findings]}


def _canon(text: str) -> str:
    """Strip the rendering, keep the content.

    A quote re-wrapped across lines, or typeset with a curly apostrophe, is the
    same quote -- treating either as drift would flag correct work and teach the
    reader to ignore the gate. Unicode is NFKC-folded, quote glyphs unified, and
    all whitespace collapsed. Nothing else moves: casing, digits and word choice
    are exactly what the check is here to compare.
    """
    t = unicodedata.normalize("NFKC", text)
    # The ambiguous glyphs ARE the subject here: this table is what folds a
    # typeset quote back onto the plain-ASCII one, so the linter's "did you mean
    # a hyphen" is precisely the substitution being performed.
    t = t.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',  # noqa: RUF001
                                   "–": "-", "—": "-"}))  # noqa: RUF001
    return " ".join(t.split())


def check_quote_drift(
    report: str,
    note_bodies: Mapping[str, str],
    sources: Sequence[str],
) -> DriftReport:
    """Verify every attributed quotation in `report` against the note it cites.

    `sources` is the report's ordered source list, so a `[N]` marker resolves to
    `sources[N-1]` -- the same 1-based convention `uncited-gate` uses.
    """
    canon_notes = {nid: _canon(body) for nid, body in note_bodies.items()}
    findings: list[DriftFinding] = []

    for m in _QUOTED.finditer(report):
        quoted = m.group(1).strip()
        tail = report[m.end(): m.end() + _ATTRIBUTION_WINDOW]
        marker_match = _MARKER.search(tail)
        if marker_match is None:
            continue                      # uncited-gate's problem, not this gate's

        marker = int(marker_match.group(1))
        cited = sources[marker - 1] if 1 <= marker <= len(sources) else None
        needle = _canon(quoted)

        if cited is None or cited not in canon_notes:
            findings.append(DriftFinding(quoted, marker, cited, "UNRESOLVED"))
            continue
        if needle in canon_notes[cited]:
            findings.append(DriftFinding(quoted, marker, cited, "MATCHED", cited))
            continue

        elsewhere = next((nid for nid, body in canon_notes.items() if needle in body), None)
        findings.append(DriftFinding(
            quoted, marker, cited,
            "DRIFTED" if elsewhere else "ABSENT",
            elsewhere,
        ))

    return DriftReport(tuple(findings))


__all__ = ["MIN_QUOTED_CHARS", "DriftFinding", "DriftReport", "check_quote_drift"]
