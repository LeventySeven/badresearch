"""Observable provider outcomes — why a lane returned nothing (issue #39).

Every keyless provider swallows its own transport failure into `[]` so one dead
lane can never abort a fan-out. That graceful degrade is correct, and it is also
what made a rate-limit, a DNS failure and a genuinely sourceless query arrive at
the funnel looking identical — and a report then asserted "there is nothing on
X" about a topic the stack never actually searched.

The fix is not to stop swallowing; it is to leave a NOTE behind. A provider sets
`self.last_status` on its way out, `funnel/fanout.py` reads it, and the funnel
can finally tell "searched, found nothing" from "could not search".

Deliberately NOT in the vocabulary:
- `auth-failed` — every provider here is keyless by construction
  (`cli/research.py`: "Every provider is cost_per_search=0.0, zero key"), so no
  credential exists to fail.
- `schema-drift` — nothing in this package detects it; a status no code can ever
  set is a lie in the enum.
"""

from __future__ import annotations

import httpx

# The statuses a provider may report. `funnel/fanout.py` owns how they RANK;
# this module owns how a live exception MAPS onto one.
OK = "ok"
NO_RESULTS = "no-results"
RATE_LIMITED = "rate-limited"
TIMEOUT = "timeout"
UNREACHABLE = "unreachable"
ERROR = "error"


def classify_search_failure(exc: BaseException) -> str:
    """Map a provider's transport exception onto the outcome vocabulary.

    Order matters: a 429 is a rate limit even though it arrives as an
    HTTPStatusError, and `httpx.ConnectTimeout` is a `TimeoutException` before it
    is a `TransportError`. Anything unrecognized degrades to the generic
    `error` — never a false-specific diagnosis.
    """
    if isinstance(exc, httpx.HTTPStatusError):
        code = getattr(exc.response, "status_code", 0)
        if code == 429:
            return RATE_LIMITED
        return ERROR
    if isinstance(exc, httpx.TimeoutException | TimeoutError):
        return TIMEOUT
    if isinstance(exc, httpx.ConnectError | httpx.NetworkError):
        return UNREACHABLE
    if isinstance(exc, OSError):
        # socket.gaierror (DNS) and friends — the offline case that used to be
        # indistinguishable from an empty SERP.
        return UNREACHABLE
    # `ddgs` raises its OWN hierarchy (RatelimitException / TimeoutException /
    # DDGSException), and it is an optional dependency we must not import here
    # just to name a class. Fall back to the class NAME, which is stable enough
    # for a diagnostic and costs nothing when the lib is absent. A rate limit on
    # the always-on breadth lane is the single most valuable status to get right
    # — it is exactly the "we self-DoSed and called it an empty topic" case.
    name = type(exc).__name__.lower()
    if "ratelimit" in name or "toomanyrequests" in name:
        return RATE_LIMITED
    if "timeout" in name:
        return TIMEOUT
    if "connect" in name or "dns" in name or "resolve" in name:
        return UNREACHABLE
    return ERROR


def status_for(results: list, failure: str | None) -> str:
    """The status a completed `search()` should record.

    Hits always win: a lane that returned something works, whatever a sibling
    request did. A clean run with no hits is `no-results` — the ONLY outcome that
    licenses an absence claim downstream.
    """
    if results:
        return OK
    return failure or NO_RESULTS


__all__ = [
    "ERROR",
    "NO_RESULTS",
    "OK",
    "RATE_LIMITED",
    "TIMEOUT",
    "UNREACHABLE",
    "classify_search_failure",
    "status_for",
]
