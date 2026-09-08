"""The numeric half of the cite-everything hole, closed without a judge.

**The attack this answers, measured on this repo's own checks.** Grab Bench
validates its scorer against shortcut baselines -- empty output, schema-only,
cite-all-evidence -- under one rule: if a shortcut baseline can pass, the
benchmark is not ready. Run here, that rule fails at once. A draft whose every
sentence is false but carries a marker resolving to a real, on-topic note comes
back `{"uncited": [], "warnings": []}` from `uncited-gate`, and
`quote-drift-gate` reports PASS because nothing is in quotation marks. Stapling
`[1]` to every sentence beats the entire set.

**Why this gate is not a judge.** Entailment in general needs one, and a judge on
long-form groundedness lands between 55 and 60 balanced accuracy where 50 is
chance -- an instrument that may rank but must never close. The numeric half
needs no judge at all. A fabricated research claim usually fabricates a
quantity, and "the note this sentence cites contains no number matching the one
in the sentence" is a fact about two strings, settled for nothing.

**It is deliberately partial and says so.** `unchecked` counts cited sentences
carrying no quantity -- the prose claims this gate structurally cannot see. A
partial check that reports its own coverage is useful; the same check silent
about its blind spot is how "clean" gets read as "supported", which is the exact
defect it was built to catch.

**What it refuses to flag,** because a gate that cries wolf gets switched off: a
bare year (2026), an ordinal reference (Section 3, Figure 2), and any sentence
with no citation marker at all -- that last one is `uncited-gate`'s failure and
two checks must not both claim it.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

# Formatting tolerance only: 1.20 and 1.2 are one number, and so are $75 and 75.
_REL_TOL = 1e-9

# A quantity worth checking. Deliberately excludes a bare 4-digit year and any
# number introduced by a structural word, which are references, not claims.
_QUANTITY = re.compile(r"(?<![\w.])\$?\d[\d,]*(?:\.\d+)?%?(?![\w])")
_YEAR = re.compile(r"^(?:19|20)\d{2}$")
_STRUCTURAL_LEAD = re.compile(
    r"(?:section|figure|fig|table|chapter|part|step|footnote|note|item|page|"
    r"appendix|version|v|paragraph)\s*$",
    re.I,
)
_MARKER = re.compile(r"\[(\d+)\]")
# A sentence boundary is a terminator NOT sitting between two digits -- otherwise
# "a PUE of 2.9" splits into "a PUE of 2" and "9", the quantity is destroyed, and
# the gate silently checks numbers that were never in the text. Caught by the
# planted-defect test failing on the exact attack it was written to catch.
_SENTENCE = re.compile(r"(?:[^.!?\n]|(?<=\d)[.](?=\d))+[.!?]?")


@dataclass(frozen=True)
class FigureFinding:
    sentence: str
    quantity: str
    marker: int
    cited_note: str | None
    outcome: str          # UNSUPPORTED | UNRESOLVED

    def to_dict(self) -> dict[str, object]:
        return {
            "sentence": self.sentence,
            "quantity": self.quantity,
            "marker": self.marker,
            "cited_note": self.cited_note,
            "outcome": self.outcome,
        }


@dataclass(frozen=True)
class FigureReport:
    findings: tuple[FigureFinding, ...] = ()
    checked: int = 0
    unchecked: int = 0

    @property
    def ok(self) -> bool:
        return not self.findings

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "checked": self.checked,
            "unchecked": self.unchecked,
            "findings": [f.to_dict() for f in self.findings],
        }


def _as_number(token: str) -> float | None:
    cleaned = token.strip().lstrip("$").rstrip("%").replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _claim_quantities(sentence: str) -> list[str]:
    """Quantities in `sentence` that assert something, not ones that point at something."""
    out: list[str] = []
    for m in _QUANTITY.finditer(sentence):
        raw = m.group(0)
        bare = raw.strip("$%").replace(",", "")
        if _YEAR.match(bare):
            continue                                   # a date, not a claim
        if _STRUCTURAL_LEAD.search(sentence[: m.start()]):
            continue                                   # "Section 3" is a reference
        out.append(raw)
    return out


def check_figure_support(
    report: str,
    note_bodies: Mapping[str, str],
    sources: Sequence[str],
) -> FigureReport:
    """Every cited sentence's numbers must appear in the note it cites.

    `sources` is the report's ordered source list, so `[N]` resolves to
    `sources[N-1]` -- the same 1-based convention `uncited-gate` uses.
    """
    note_numbers = {
        nid: {n for n in (_as_number(t) for t in _QUANTITY.findall(body)) if n is not None}
        for nid, body in note_bodies.items()
    }
    findings: list[FigureFinding] = []
    checked = unchecked = 0

    for raw in _SENTENCE.findall(report):
        sentence = raw.strip()
        if not sentence:
            continue
        marker_match = _MARKER.search(sentence)
        if marker_match is None:
            continue                          # uncited-gate's business, not this gate's

        marker = int(marker_match.group(1))
        body = _MARKER.sub("", sentence)
        quantities = _claim_quantities(body)
        if not quantities:
            unchecked += 1                    # a prose claim: counted, never called clean
            continue

        cited = sources[marker - 1] if 1 <= marker <= len(sources) else None
        if cited is None or cited not in note_numbers:
            findings.append(FigureFinding(sentence, quantities[0], marker, cited, "UNRESOLVED"))
            continue

        available = note_numbers[cited]
        for q in quantities:
            target = _as_number(q)
            if target is None:
                continue
            checked += 1
            if not any(abs(n - target) <= _REL_TOL * max(1.0, abs(target)) for n in available):
                findings.append(
                    FigureFinding(sentence, q, marker, cited, "UNSUPPORTED")
                )

    return FigureReport(tuple(findings), checked, unchecked)


__all__ = ["FigureFinding", "FigureReport", "check_figure_support"]
