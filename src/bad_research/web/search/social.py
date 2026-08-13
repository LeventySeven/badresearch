"""The social vertical — community evidence, ranked by what people engaged with.

The seven scholarly verticals cover what was *published*. Nothing covered what
was *said*: the Reddit thread with 1,485 upvotes, the HN argument with 313
comments, the YouTube transcript nobody transcribed into an article. For a
question about reception, adoption, or lived experience, that evidence is the
primary source and a blog post about it is the derivative.

`last30days` (github.com/mvanhorn/last30days-skill, MIT) is an external engine
that searches Reddit, Hacker News, YouTube transcripts, GitHub and Polymarket —
plus X, TikTok and Instagram when the operator has configured them — and ranks
by native engagement. This module is the adapter and nothing more: one
subprocess call, its `--emit=json` agent profile (schema 1.x) mapped onto
WebResult.

Keyless, like every provider in this package. The engine's default lanes need no
key or account, and this adapter neither reads nor forwards a credential; the
keyed lanes are the operator's own business, configured out-of-band in the
engine's own config. Absent by default: when the engine is not installed the
provider does not build, `_build_vertical_providers` skips it, and the funnel
behaves exactly as it did before.

Two properties make it unlike the HTTP verticals:

1. **Its results arrive content-complete.** The engine already read the thread
   and the transcript; the body is in hand at SERP time. Each result is stamped
   `metadata["prefetched"] = True`, which tells the funnel's read stage to keep
   that body instead of re-fetching the URL. Re-fetching a reddit.com or x.com
   permalink returns a login wall, which Stage E then drops as junk — the
   evidence would be gathered and thrown away one stage later.
2. **It is slow.** A keyless run takes minutes, not the ~1s an HTTP vertical
   takes, because it is really a dozen searches behind one command. The route
   table fans verticals across at most two seed queries, `--quick` selects the
   engine's low-latency profile, and the whole call is bounded by a timeout —
   past which the lane reports `timeout` and the run continues without it.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from bad_research.web.base import SearchQuery, WebResult
from bad_research.web.search.status import (
    ERROR,
    OK,
    TIMEOUT,
    classify_search_failure,
    status_for,
)

# Explicit path to the engine script; wins over every other lookup.
ENV_SCRIPT = "LAST30DAYS_SCRIPT"
# The engine's install root — either its repo checkout or the installed skill dir.
ENV_HOME = "LAST30DAYS_HOME"
# Interpreter override; the engine needs Python 3.12+, which is not necessarily ours.
ENV_PYTHON = "LAST30DAYS_PYTHON"
ENV_TIMEOUT = "LAST30DAYS_TIMEOUT_SECONDS"

_SCRIPT_IN_REPO = Path("skills/last30days/scripts/last30days.py")
_SCRIPT_IN_SKILL = Path("scripts/last30days.py")

# The two install layouts the engine's own README documents. Deliberately NOT a
# recursive search: a path-discovery loop is how you end up running a stale copy.
_INSTALL_DIRS = ("~/.claude/skills/last30days", "~/.agents/skills/last30days")

_DEFAULT_TIMEOUT_S = 300.0


def _env(env: Mapping[str, str] | None) -> Mapping[str, str]:
    return os.environ if env is None else env


def resolve_engine(env: Mapping[str, str] | None = None) -> Path | None:
    """The last30days script, or None when it is not installed.

    Order: explicit script → install root (either layout) → the documented skill
    install dirs. Returns None rather than raising so callers can treat "not
    installed" as the ordinary case it is.
    """
    e = _env(env)

    explicit = e.get(ENV_SCRIPT, "").strip()
    if explicit:
        p = Path(explicit).expanduser()
        return p if p.is_file() else None

    roots = [e.get(ENV_HOME, "").strip(), *_INSTALL_DIRS]
    for root in roots:
        if not root:
            continue
        base = Path(root).expanduser()
        for rel in (_SCRIPT_IN_REPO, _SCRIPT_IN_SKILL):
            candidate = base / rel
            if candidate.is_file():
                return candidate
    return None


def _interpreter(env: Mapping[str, str] | None = None) -> str:
    """A Python the engine can run under. It requires 3.12+; we allow 3.11."""
    override = _env(env).get(ENV_PYTHON, "").strip()
    if override:
        return override
    if sys.version_info >= (3, 12):
        return sys.executable
    return "python3"


def _timeout_s(env: Mapping[str, str] | None = None) -> float:
    raw = _env(env).get(ENV_TIMEOUT, "").strip()
    if not raw:
        return _DEFAULT_TIMEOUT_S
    try:
        parsed = float(raw)
    except ValueError:
        return _DEFAULT_TIMEOUT_S
    return parsed if parsed > 0 else _DEFAULT_TIMEOUT_S


def _run_engine(argv: list[str], timeout: float) -> dict[str, Any]:
    """Run the engine and parse its JSON stdout.

    No shell: argv is a list, so the query is an argument and never a command.
    The engine streams progress on stderr and keeps stdout pure JSON.
    """
    proc = subprocess.run(
        argv, capture_output=True, text=True, timeout=timeout, check=False,
    )
    if proc.returncode != 0:
        head = (proc.stderr or "").strip().splitlines()
        raise RuntimeError(
            f"last30days exited {proc.returncode}: {head[-1] if head else 'no stderr'}"
        )
    payload = json.loads(proc.stdout)
    if not isinstance(payload, dict):
        raise ValueError("last30days returned a non-object JSON payload")
    return payload


def _engagement_summary(engagement: dict[str, Any]) -> str:
    """`{"score": 1485, "num_comments": 85}` → `85 comments · 1,485 score`.

    Ordered by key so the line is stable across runs, and only integer-ish
    counters are shown — the engine's counter names differ per source and we do
    not pretend to know which one is the headline.
    """
    parts = [
        f"{v:,} {k.replace('_', ' ')}"
        for k, v in sorted(engagement.items())
        if isinstance(v, int) and not isinstance(v, bool)
    ]
    return " · ".join(parts)


class Last30DaysProvider:
    """The social lane. Keyless, prefetched, subprocess-backed."""

    name = "last30days"
    capabilities = frozenset({"social", "engagement", "community"})
    cost_per_search = 0.0
    p50_ms = 210_000  # measured: 209s for a keyless 5-source run. Minutes, not ms.

    def __init__(
        self,
        script: Path | str | None = None,
        runner: Callable[[list[str], float], dict[str, Any]] | None = None,
        env: Mapping[str, str] | None = None,
    ) -> None:
        resolved = Path(script) if script is not None else resolve_engine(env)
        if resolved is None:
            raise FileNotFoundError(
                "last30days engine not found. Install it "
                "(github.com/mvanhorn/last30days-skill) or set "
                f"{ENV_SCRIPT} to its last30days.py."
            )
        self._script = resolved
        self._runner = runner if runner is not None else _run_engine
        self._python = _interpreter(env)
        self._timeout = _timeout_s(env)
        self.last_status: str = OK

    def search(
        self, query: str, max_results: int = 10, recency_days: int | None = None
    ) -> list[WebResult]:
        argv = [
            self._python, str(self._script), query,
            "--emit=json", "--json-profile=agent", "--quick",
            f"--max-results={max_results}",
        ]
        if recency_days is not None and recency_days > 0:
            argv.append(f"--days={recency_days}")
        try:
            payload = self._runner(argv, self._timeout)
        except subprocess.TimeoutExpired:
            # The engine is minutes-slow by nature; a timeout is the expected
            # failure, and it means "we did not search", not "nothing is there".
            self.last_status = TIMEOUT
            return []
        except (json.JSONDecodeError, ValueError, RuntimeError):
            self.last_status = ERROR
            return []
        except Exception as e:
            self.last_status = classify_search_failure(e)
            return []

        out = self._map_results(payload)
        self.last_status = status_for(out, None)
        return out

    def _map_results(self, payload: dict[str, Any]) -> list[WebResult]:
        rows = payload.get("results")
        if not isinstance(rows, list):
            return []
        out: list[WebResult] = []
        for i, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                continue
            url = str(row.get("url") or "").strip()
            if not url:
                continue  # the engine documents url as possibly empty
            engagement = row.get("engagement")
            engagement = engagement if isinstance(engagement, dict) else {}
            out.append(WebResult(
                url=url,
                title=str(row.get("title") or url),
                content=str(row.get("summary") or ""),
                metadata={
                    "source": f"last30days:{row.get('source') or 'unknown'}",
                    "rank": i,
                    "published_date": row.get("published_at"),
                    "engagement": engagement,
                    "engagement_summary": _engagement_summary(engagement),
                    "native_score": row.get("relevance_score"),
                    # The body is the engine's, not a fetch of ours. Stage D keeps
                    # it instead of re-fetching a permalink into a login wall, and
                    # Stage E's post-FETCH junk rules do not apply to it.
                    "prefetched": True,
                },
            ))
        return out

    def search_ex(self, q: SearchQuery) -> list[WebResult]:
        return self.search(q.query, max_results=q.max_results, recency_days=q.recency_days)

    def fetch(self, url: str) -> WebResult:  # pragma: no cover - parity with verticals
        from bad_research.web.search.base import _fetch_clean_bridge

        return _fetch_clean_bridge(url)


__all__ = ["Last30DaysProvider", "resolve_engine"]
