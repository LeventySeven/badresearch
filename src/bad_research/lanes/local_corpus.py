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

    def enumeration_line(self) -> str:
        """The one line this lane always emits, hits or no hits."""
        line = (
            f"local-corpus | files listed {self.files_listed} | "
            f"candidates selected {self.selected} | cut line {self.cut_line}"
        )
        if self.unreachable_roots:
            line += f" | unreachable: {', '.join(self.unreachable_roots)}"
        return line

    def to_dict(self) -> dict[str, object]:
        """JSON-ready payload for `bad lane-local --json`."""
        return {
            "lane": "local-corpus",
            "files_listed": self.files_listed,
            "selected": self.selected,
            "cut_line": self.cut_line,
            "unreachable_roots": list(self.unreachable_roots),
            "hits": [{"path": h.path, "line": h.line, "text": h.text} for h in self.hits],
        }


def _list_flat_markdown(root: Path) -> list[Path]:
    """Every `*.md` directly inside `root`, sorted. Deliberately NOT recursive."""
    return sorted(p for p in root.glob("*.md") if p.is_file())


def search_local(
    query: str,
    roots: list[Path] | None = None,
    *,
    limit: int = 40,
) -> LaneResult:
    """Case-insensitively grep `query` across the flat `*.md` of each root.

    Returns every matching line as a `Hit`, capped at `limit` — with the cap,
    the file count, and any unreachable root recorded on the result so the
    caller can tell "found nothing" apart from "could not look".
    """
    search_roots = list(DEFAULT_ROOTS) if roots is None else list(roots)
    needle = query.lower()

    result = LaneResult()
    matches: list[Hit] = []
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
            for lineno, line in enumerate(text.splitlines(), start=1):
                if needle in line.lower():
                    matches.append(Hit(path=str(path), line=lineno, text=line.strip()))

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
