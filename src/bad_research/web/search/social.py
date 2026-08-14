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
key or account, and this adapter forwards NO credential of ours: the child gets
an explicit allow-listed environment (`_child_env`) — PATH/HOME/locale/TLS plus
the engine's own `LAST30DAYS_*` config — so an inherited ANTHROPIC_API_KEY,
GITHUB_TOKEN or AWS_* never crosses into third-party code. The keyed lanes are
the operator's own business, configured out-of-band in the engine's own config.
Absent by default: when the engine is not installed the provider does not build,
`_build_vertical_providers` skips it, and the funnel behaves exactly as it did
before.

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
    RATE_LIMITED,
    TIMEOUT,
    UNREACHABLE,
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

# Ceiling on the engine's stdout before we parse it. The JSON is derived from
# attacker-authored threads, so an unbounded read is a memory bomb handed
# straight to json.loads. A 5-source agent-profile run is tens of KB.
_MAX_STDOUT_CHARS = 8 * 1024 * 1024

# The ONLY variables that cross into the third-party engine. Everything else in
# the operator's shell — ANTHROPIC_API_KEY, GITHUB_TOKEN, AWS_* — stays our side
# of the boundary; `LAST30DAYS_*` is the engine's own config namespace and is
# forwarded wholesale so the operator's keyed lanes keep working.
_ENV_ALLOWLIST = (
    "PATH", "HOME", "LANG", "LC_ALL", "LC_CTYPE", "TMPDIR",
    "SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE",
)
_ENV_PREFIX = "LAST30DAYS_"


def _env(env: Mapping[str, str] | None) -> Mapping[str, str]:
    return os.environ if env is None else env


def _child_env(env: Mapping[str, str] | None = None) -> dict[str, str]:
    """The minimal environment the engine runs under (see module docstring)."""
    e = _env(env)
    out = {k: e[k] for k in _ENV_ALLOWLIST if e.get(k)}
    out.update({k: v for k, v in e.items() if k.startswith(_ENV_PREFIX)})
    return out


def _find_under(root: str) -> Path | None:
    """The engine script under one install root, in either documented layout."""
    base = Path(root).expanduser()
    for rel in (_SCRIPT_IN_REPO, _SCRIPT_IN_SKILL):
        candidate = base / rel
        if candidate.is_file():
            return candidate
    return None


def resolve_engine(env: Mapping[str, str] | None = None) -> Path | None:
    """The last30days script, or None when it is not installed.

    Order: explicit script → install root → the documented skill install dirs.
    Returns None rather than raising so callers can treat "not installed" as the
    ordinary case it is.

    Both env vars PIN: if `LAST30DAYS_HOME` is set and holds no engine we return
    None instead of falling through to `~/.claude/skills/last30days`. A root set
    one level too deep would otherwise silently run a DIFFERENT install than the
    operator pinned — the same reason `LAST30DAYS_SCRIPT` already refuses.
    """
    e = _env(env)

    explicit = e.get(ENV_SCRIPT, "").strip()
    if explicit:
        p = Path(explicit).expanduser()
        return p if p.is_file() else None

    home = e.get(ENV_HOME, "").strip()
    if home:
        return _find_under(home)

    for root in _INSTALL_DIRS:
        found = _find_under(root)
        if found is not None:
            return found
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


def _run_engine(argv: list[str], timeout: float, env: Mapping[str, str]) -> dict[str, Any]:
    """Run the engine and parse its JSON stdout.

    No shell: argv is a list, so the query is an argument and never a command.
    `env` is explicit — the child gets exactly what `_child_env` allowed, not the
    operator's shell. The engine streams progress on stderr and keeps stdout
    pure JSON.
    """
    proc = subprocess.run(
        argv, capture_output=True, text=True, timeout=timeout, check=False, env=dict(env),
    )
    if proc.returncode != 0:
        head = (proc.stderr or "").strip().splitlines()
        raise RuntimeError(
            f"last30days exited {proc.returncode}: {head[-1] if head else 'no stderr'}"
        )
    raw = proc.stdout or ""
    if len(raw) > _MAX_STDOUT_CHARS:
        raise ValueError(
            f"last30days emitted {len(raw)} chars of stdout, over the "
            f"{_MAX_STDOUT_CHARS} cap; refusing to parse it"
        )
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("last30days returned a non-object JSON payload")
    return payload


def _rows_from_payload(payload: dict[str, Any]) -> list[Any] | None:
    """The engine's result rows, in whichever envelope they arrived.

    TWO top-level shapes ship. The flat one is `{"results": [...]}`. The other is
    the comparison envelope — `{"comparison": true, "entities": [...],
    "reports": [{"report": {"results": [...]}}]}` — and it is reached with NO
    flags: the engine calls `apply_vs_competitor_routing` unconditionally and
    splits the topic on `\\bvs\\.?\\b|\\bversus\\b|/`, so any query containing
    "vs", "versus" or a slash ("reddit sentiment on CI/CD adoption") comes back
    in it.

    Returns None for a shape we do not recognise. That is NOT the same as zero
    rows: a payload we could not parse says nothing about what is out there, and
    the caller must report it as a failure rather than an absence (issue #39).
    """
    if payload.get("comparison"):
        reports = payload.get("reports")
        if not isinstance(reports, list):
            return None
        merged: list[Any] = []
        matched = False
        for entry in reports:
            report = entry.get("report") if isinstance(entry, dict) else None
            inner = report.get("results") if isinstance(report, dict) else None
            if isinstance(inner, list):
                matched = True
                merged.extend(inner)
        # Reports we could not read at all = drift, not an empty comparison.
        return merged if matched or not reports else None
    rows = payload.get("results")
    return rows if isinstance(rows, list) else None


# The engine's per-source states, most actionable first. Their vocabulary is
# ours (`rate_limited` → `rate-limited`), so a lane that came back empty because
# every source was throttled reports the throttle instead of a clean empty.
_SOURCE_FAILURES = (RATE_LIMITED, TIMEOUT, UNREACHABLE, ERROR)


def _source_failure(payload: dict[str, Any]) -> str | None:
    """The worst per-source failure the engine reported, or None if none did."""
    states = payload.get("source_status")
    if not isinstance(states, dict):
        return None
    seen = {
        v.strip().lower().replace("_", "-") for v in states.values() if isinstance(v, str)
    }
    return next((s for s in _SOURCE_FAILURES if s in seen), None)


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
        runner: Callable[[list[str], float, Mapping[str, str]], dict[str, Any]] | None = None,
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
        self._child_env = _child_env(env)
        self.last_status: str = OK

    def search(
        self, query: str, max_results: int = 10, recency_days: int | None = None
    ) -> list[WebResult]:
        argv = [
            self._python, str(self._script),
            "--emit=json", "--json-profile=agent", "--quick",
            f"--max-results={max_results}",
        ]
        if recency_days is not None and recency_days > 0:
            argv.append(f"--days={recency_days}")
        # The query goes LAST, behind `--`: a question that starts with a dash
        # ("--sources=all …") is a QUERY, and must never be read as engine flags.
        argv += ["--", query]
        try:
            payload = self._runner(argv, self._timeout, self._child_env)
        except subprocess.TimeoutExpired:
            # The engine is minutes-slow by nature; a timeout is the expected
            # failure, and it means "we did not search", not "nothing is there".
            self.last_status = TIMEOUT
            return []
        except (json.JSONDecodeError, ValueError, RuntimeError):
            self.last_status = ERROR
            return []
        except OSError:
            # A missing interpreter / unexecutable script is an EXEC failure.
            # classify_search_failure would call it `unreachable` — a network
            # diagnosis that sends the operator hunting for a firewall.
            self.last_status = ERROR
            return []
        except Exception as e:
            self.last_status = classify_search_failure(e)
            return []

        rows = _rows_from_payload(payload)
        if rows is None:
            # Schema drift: we hold a payload we cannot read. It is NOT evidence
            # of absence, so it must not reach the funnel as `no-results` — that
            # is the one outcome licensing "there is nothing on X" (issue #39).
            self.last_status = ERROR
            return []
        out = self._map_results(rows)
        # An empty return with every source throttled is a coverage gap, not a
        # sourceless topic; the engine's own per-source states say which.
        self.last_status = status_for(out, _source_failure(payload))
        return out

    def _map_results(self, rows: list[Any]) -> list[WebResult]:
        out: list[WebResult] = []
        for i, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                continue
            url = str(row.get("url") or "").strip()
            if not url:
                continue  # the engine documents url as possibly empty
            content = str(row.get("summary") or "").strip()
            if not content:
                continue  # ...and summary too. A row with no body is not evidence.
            engagement = row.get("engagement")
            engagement = engagement if isinstance(engagement, dict) else {}
            out.append(WebResult(
                url=url,
                title=str(row.get("title") or url),
                content=content,
                metadata={
                    "source": f"last30days:{row.get('source') or 'unknown'}",
                    "rank": i,
                    "published_date": row.get("published_at"),
                    "engagement": engagement,
                    "engagement_summary": _engagement_summary(engagement),
                    "native_score": row.get("relevance_score"),
                    # The body is the engine's, not a fetch of ours. Stage D keeps
                    # it instead of re-fetching a permalink into a login wall, and
                    # Stage E waives its one FETCH-shaped rule (the <300-char
                    # floor) for it — the rest of the junk floor still judges it.
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
