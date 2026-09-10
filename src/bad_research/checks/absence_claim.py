"""`bad absence-gate` — refuse an absence claim that says nothing about where you looked.

An absence claim is the highest-risk sentence a research report contains. Every other
claim can be checked against the source it cites; an absence cites nothing by
construction, so nothing downstream can catch it. `quote-drift` needs a quotation,
`figure-support` needs a figure, `no-source-claim` needs a claim with no source — an
absence has no quotation, no figure, and its "source" is the whole world.

**Measured, on this project's own output.** A blind judge falsified this sentence in a
single fetch:

    No source measures the false-negative rate of a source-quality filter directly.
    ... Nobody publishes "we rejected N documents a human judged relevant."

Thomas et al. (SIGIR 2024) publish exactly that, split by direction: 68% agreement when
the judge says "not relevant" against 94% when it says "relevant". The claim was true of
one lane and asserted of the field.

The comparison run got the same fact right, and the difference is only scope:

    ...and no published work IN THIS CORPUS has sampled and read at comparable scale
    what a production *pretraining* quality classifier threw away.

So the rule this module enforces: **an absence claim must say where you looked.** It is
not enough to narrow the SUBJECT — "the false-negative rate of a source-quality filter"
is a narrow subject and the claim was still false. The qualifier has to bound the
SEARCH: this corpus, this lane, the sources you actually read, your own reach, or a
count of what you examined. Narrowing what you were looking for makes a false claim
sound careful; narrowing where you looked makes it true.

This gate cannot tell you an absence is real — nothing can, short of finding the thing.
It only refuses the form in which an absence is unfalsifiable, which is the form that
shipped.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Assertions about the WORLD's RECORD. The object has to be bibliographic, or the verb
# has to be one of publishing/measuring/reporting — otherwise the pattern eats rhetoric.
#
# Measured while building this: a first version keyed on a bare `there is no` and flagged
# "Without this dataset there is no neural retrieval era" and "Without this there is no
# TREC, no MS MARCO, no BEIR" — emphasis, not a claim about the literature. It also
# flagged `nobody has labelled which passage`, which describes a training setup. A gate
# whose flags are mostly rhetoric does not get read, and an unread gate is worse than
# none, because it still reports a number.
_BIB = (r"(?:source|sources|paper|papers|study|studies|published|publication|publications"
        r"|literature|measurement|measurements|dataset|datasets|benchmark|benchmarks"
        r"|work|works)")  # not author/authors: "as though they had no authors" is rhetoric
_BIBVERB = (r"(?:publish(?:es|ed)?|measures|measured|measure|report(?:s|ed)?"
            r"|quantif(?:y|ies|ied)|sampled|studied|rerun|replicated|split)")

_ABSENCE = re.compile(
    r"""(?ix)
    \b(?:
        no \s+ """ + _BIB + r""" \b
      | no \s+ (?:one|body) \s+ (?:has \s+)? """ + _BIBVERB + r"""
      | nobody \s+ (?:has \s+)? """ + _BIBVERB + r"""
      | (?:has|have) \s+ never \s+ been \s+ (?:\w+ \s+)? """ + _BIBVERB + r"""
      | never \s+ """ + _BIBVERB + r""" \s+ (?:at|by|in|anywhere)
      | there \s+ (?:is|are|exists) \s+ no \s+ (?:\w+ \s+)? """ + _BIB + r"""
      | (?:does|do) \s+ not \s+ exist \s+ in \s+ the \s+ literature
      | the \s+ literature \s+ (?:has|contains|offers) \s+ no \b
      | none \s+ of \s+ the \s+ literature
    )
    """,
)

# Qualifiers that bound the SEARCH. A subject qualifier does not appear here on
# purpose: "of a source-quality filter" narrows what was sought and rescues nothing.
_SCOPE = re.compile(
    r"""(?ix)
    \b(?:
        in \s+ (?:this|the) \s+ (?:corpus|vault|lane|sample|pool|set|collection|survey|review)
      | in \s+ the \s+ \w[\w-]* \s+ lane
      | (?:i|we) \s+ (?:could \s+ not|did \s+ not|was \s+ not \s+ able|were \s+ not \s+ able|
                        failed \s+ to|have \s+ not) \s+ (?:find|reach|locate|see|obtain)
      | (?:i|we) \s+ (?:reached|read|examined|screened|searched|surveyed|checked)
      | (?:of|among|within) \s+ the \s+ \d[\d,]* \s+ \w+
      | of \s+ the \s+ (?:sources|papers|works|studies|files|notes) \s+ (?:i|we) \s+
      | in \s+ what \s+ (?:i|we) \s+ (?:read|reached|found|searched)
      | as \s+ far \s+ as \s+ (?:i|we) \s+ (?:could|can|know|reached)
      | \b(?:EMPTY|BLOCKED|MISSING|EXHAUSTED|IRRELEVANT-BY-DESIGN)\b
      | (?:i|we) \s+ (?:reached|could \s+ reach)
      | no \s+ (?:source|sources|paper|papers|work|study) \s+ (?:i|we) \s+
    )
    """,
)

_SENTENCE = re.compile(r"(?:[^.!?\n]|(?<=\d)[.](?=\d))+[.!?]?")
_MARKUP = re.compile(r"\*{1,2}|`|\[\[[^\]]*\]\]|\[\d+\]")
_QUOTED = re.compile(r"[\u201c\"][^\u201d\"]{0,600}[\u201d\"]")


@dataclass(frozen=True)
class AbsenceClaim:
    sentence: str
    line: int
    scoped: bool
    scope: str


@dataclass(frozen=True)
class AbsenceReport:
    claims: tuple[AbsenceClaim, ...]
    caveat: str

    @property
    def unscoped(self) -> tuple[AbsenceClaim, ...]:
        return tuple(c for c in self.claims if not c.scoped)

    @property
    def ok(self) -> bool:
        return not self.unscoped

    def to_dict(self) -> dict[str, object]:
        return {
            "found": len(self.claims),
            "scoped": len(self.claims) - len(self.unscoped),
            "unscoped": [{"line": c.line, "sentence": c.sentence} for c in self.unscoped],
            "ok": self.ok,
            "caveat": self.caveat,
        }


def _in_code_block(lines: list[str]) -> list[bool]:
    """A fenced block is quoted material, not the report's own assertion."""
    out, fenced = [], False
    for ln in lines:
        if ln.lstrip().startswith("```"):
            fenced = not fenced
            out.append(True)
            continue
        out.append(fenced)
    return out


def find_absence_claims(report: str) -> AbsenceReport:
    lines = report.splitlines()
    fenced = _in_code_block(lines)
    claims: list[AbsenceClaim] = []

    for i, raw in enumerate(lines, start=1):
        if fenced[i - 1]:
            continue
        # A blockquote is somebody else's sentence.
        if raw.lstrip().startswith(">"):
            continue
        text = _MARKUP.sub("", raw)
        # blank out quotations so a source's own absence claim is not scored as ours
        text = _QUOTED.sub(lambda m: " " * len(m.group(0)), text)
        for m in _SENTENCE.finditer(text):
            s = m.group(0).strip()
            if not s or not _ABSENCE.search(s):
                continue
            sc = _SCOPE.search(s)
            claims.append(AbsenceClaim(s, i, bool(sc), sc.group(0).strip() if sc else ""))

    n_un = sum(1 for c in claims if not c.scoped)
    if not claims:
        caveat = (
            "No absence claim found. That is a clean result only if the report makes none — "
            "a report that asserts absence in a form this gate does not match is unchecked, "
            "not clear."
        )
    elif n_un:
        caveat = (
            f"{n_un} of {len(claims)} absence claim(s) name no search scope. Each asserts "
            "something about the world's whole record while citing nothing, so nothing "
            "downstream can falsify it. Bound the SEARCH (this corpus, this lane, what you "
            "reached) — narrowing the subject does not help, and was the exact form that "
            "shipped a claim a judge falsified in one fetch."
        )
    else:
        caveat = (
            f"All {len(claims)} absence claim(s) name a search scope. That makes each one "
            "falsifiable; it does not make any of them true. This gate checks form, never "
            "fact — only finding the thing can do that."
        )
    return AbsenceReport(tuple(claims), caveat)


__all__ = ["AbsenceClaim", "AbsenceReport", "find_absence_claims"]
