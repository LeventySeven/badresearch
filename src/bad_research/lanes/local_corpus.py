"""The local-corpus lane — a flat glob over the owner's on-disk libraries.

Grepping this repo's `src/` for `guidesfm|researchfms|teardown` used to return
only comments: 407 teardowns, ~43 transcripts, ~190 articles and ~67 x-guides
sat on disk, invisible to the research engine, while a plain web agent could
never reach any of them. This module is the reach.

Two decisions are load-bearing and are pinned by tests:

**Flat glob, never `rglob`.** `~/Desktop/researchfms/teardowns/` holds ~36k
files once you descend into its subdirectories — vendored source cloned during
teardowns. Recursion ranks that vendored code above the 407 breakdowns the
lane exists to find, so the lane lists `*.md` at the top of each root and stops
there.

**A zero still emits the enumeration line.** A lane that returns nothing and
says nothing is indistinguishable from a lane that is broken — which is the
exact failure this project exists to stop. `LaneResult.enumeration_line()`
always renders how many files were listed, how many candidates survived, where
the cut fell, and which roots could not be reached.
"""

from __future__ import annotations

import re

from dataclasses import dataclass, field
from pathlib import Path

# The owner's libraries, in the order a reader should meet them. Only roots that
# actually exist are searched; the rest are named in `unreachable_roots` rather
# than silently dropped — a missing library must look different from an empty one.
DEFAULT_ROOTS: tuple[Path, ...] = (
    Path.home() / "Desktop" / "researchfms" / "teardowns",
    Path.home() / "Desktop" / "researchfms" / "Transcripts",
    Path.home() / "Desktop" / "guidesfm" / "research" / "articles",
    Path.home() / "Desktop" / "guidesfm" / "research" / "x-guides",
    # Top level: the operating specs (AGENTIC_SEARCH_SPEC, TRANSCRIPT_RULES, …).
    Path.home() / "Desktop" / "researchfms",
)


@dataclass(frozen=True)
class Hit:
    """One matching line: the file it came from, its 1-based line number, its text."""

    path: str
    line: int
    text: str


@dataclass
class LaneResult:
    """What one lane run saw — including what it did NOT return, and why."""

    files_listed: int = 0
    selected: int = 0
    cut_line: str = "no cap applied"
    hits: list[Hit] = field(default_factory=list)
    unreachable_roots: list[str] = field(default_factory=list)
    # How the query was matched, and what each of its terms found on its own. A zero
    # that cannot be attributed to a term is the false-EMPTY this whole lane exists to
    # prevent; these two fields are what make it attributable.
    matched_by: str = "phrase"
    terms: list[str] = field(default_factory=list)
    per_term_files: dict = field(default_factory=dict)

    def enumeration_line(self) -> str:
        """The one line this lane always emits, hits or no hits."""
        line = (
            f"local-corpus | files listed {self.files_listed} | "
            f"candidates selected {self.selected} | cut line {self.cut_line}"
        )
        line += f" | matched by {self.matched_by}"
        if self.unreachable_roots:
            line += f" | unreachable: {', '.join(self.unreachable_roots)}"
        if self.selected == 0 and self.per_term_files:
            dead = [t for t, n in self.per_term_files.items() if not n]
            live = {t: n for t, n in self.per_term_files.items() if n}
            line += (
                f" | ZERO IS ATTRIBUTABLE: absent terms {dead or 'none'}; "
                f"terms present in files {live or 'none'}"
            )
        return line

    def to_dict(self) -> dict[str, object]:
        """JSON-ready payload for `bad lane-local --json`."""
        return {
            "lane": "local-corpus",
            "files_listed": self.files_listed,
            "selected": self.selected,
            "cut_line": self.cut_line,
            "unreachable_roots": list(self.unreachable_roots),
            "matched_by": self.matched_by,
            "terms": list(self.terms),
            "per_term_files": dict(self.per_term_files),
            "hits": [{"path": h.path, "line": h.line, "text": h.text} for h in self.hits],
        }


def _list_flat_markdown(root: Path) -> list[Path]:
    """Every `*.md` directly inside `root`, sorted. Deliberately NOT recursive."""
    return sorted(p for p in root.glob("*.md") if p.is_file())


# Stopwords that would match every line in the corpus and so cannot narrow anything.
_STOP = frozenset("""a an and are as at be by do does for from how i if in into is it its
me my not of on or our so than that the their them then there these they this to was we
what when where which who why will with would you your can could should about over under
""".split())


def _terms(query: str) -> list[str]:
    """Content words, longest first — the ones that can actually select a line."""
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9._+-]*", query.lower())
    seen, out = set(), []
    for w in words:
        if len(w) < 3 or w in _STOP or w in seen:
            continue
        seen.add(w)
        out.append(w)
    return sorted(out, key=len, reverse=True)


def search_local(
    query: str,
    roots: list[Path] | None = None,
    *,
    limit: int = 40,
) -> LaneResult:
    """Search the flat `*.md` of each root for `query`, cheapest match first.

    **A literal substring is not a search.** This used to lower-case the whole query
    and ask whether it appeared inside a single line. That works for `rerank` and is
    incapable of ever matching a question: driven cold with the natural-language form
    this project's own skill documents, it returned `selected: 0` over a corpus holding
    **1,408 matching lines across 87 files** — and reported `unreachable_roots: []`
    beside it, so the output was indistinguishable from a healthy lane that is genuinely
    empty. That is precisely the false-EMPTY the lane was written to prevent, produced
    by the lane itself.

    So the match runs as a ladder, and the result says which rung answered:

    * ``phrase``    — the query appears verbatim in a line. Unchanged behaviour, and
                      still first, so a substring query costs exactly what it did.
    * ``all-terms`` — a line carrying every content word of the query.
    * ``any-term``  — a line carrying at least one, ranked by how many it carries, so
                      the densest lines come back first rather than the earliest.

    And **a zero is attributable or it is not reportable**: `per_term_files` records how
    many files each individual term appears in, so "nothing found" resolves into "these
    words are absent from the corpus" (a real EMPTY) or "the words are here but never
    together" (not an EMPTY at all). Reporting an unattributable zero is what licenses a
    reader to conclude "not in corpus", which is the one conclusion this lane must never
    manufacture.
    """
    search_roots = list(DEFAULT_ROOTS) if roots is None else list(roots)
    phrase = query.lower().strip()
    terms = _terms(query)

    result = LaneResult(terms=terms)
    per_term_files: dict[str, int] = {t: 0 for t in terms}
    phrase_hits: list[Hit] = []
    all_hits: list[tuple[int, Hit]] = []
    any_hits: list[tuple[int, Hit]] = []
    unreadable = 0

    for root in search_roots:
        if not root.is_dir():
            result.unreachable_roots.append(str(root))
            continue
        for path in _list_flat_markdown(root):
            result.files_listed += 1
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                unreadable += 1
                continue
            lowered = text.lower()
            for t in terms:
                if t in lowered:
                    per_term_files[t] += 1
            for lineno, line in enumerate(text.splitlines(), start=1):
                low = line.lower()
                hit = Hit(path=str(path), line=lineno, text=line.strip())
                if phrase and phrase in low:
                    phrase_hits.append(hit)
                if terms:
                    n = sum(1 for t in terms if t in low)
                    if n == len(terms):
                        all_hits.append((n, hit))
                    if n:
                        any_hits.append((n, hit))

    if phrase_hits:
        matches, result.matched_by = phrase_hits, "phrase"
    elif all_hits:
        matches, result.matched_by = [h for _, h in all_hits], "all-terms"
    elif any_hits:
        any_hits.sort(key=lambda p: -p[0])
        matches, result.matched_by = [h for _, h in any_hits], "any-term"
    else:
        matches, result.matched_by = [], "no-match"

    result.per_term_files = per_term_files
    total = len(matches)
    result.hits = matches[:limit] if limit >= 0 else []
    result.selected = len(result.hits)
    result.cut_line = (
        f"capped at {limit} of {total} matches" if total > result.selected else "no cap applied"
    )
    if unreadable:
        result.cut_line += f"; {unreadable} file(s) unreadable"
    return result

__all__ = ["DEFAULT_ROOTS", "Hit", "LaneResult", "search_local"]
