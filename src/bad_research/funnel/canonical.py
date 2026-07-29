"""canonicalize_url — Firecrawl-style URL normalization for dedup (dossier 10
§3.1, FC §28.5). Collapses cosmetic variants so `a.com/p` and `a.com/p/`,
`www.a.com/p`, and `a.com/p#x` all dedup to one candidate.
"""

from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

_DEFAULT_PORTS = {"http": "80", "https": "443"}
_INDEX_RE = re.compile(r"/index\.(html?|php|aspx?|jsp|cgi)$", re.IGNORECASE)

# Tracking-param twins collapse: strip known analytics/click-id params so
# `?utm_source=x`, `?utm_source=y`, and the bare URL all dedup to one candidate.
# These carry NO page semantics; every other param is kept (the funnel treats
# ordinary query params — ?id=5, ?page=2 — as meaningful, dossier 10 §3.1).
_TRACKING_PARAMS = frozenset({"fbclid", "gclid", "mc_cid", "mc_eid", "igshid"})
_TRACKING_PREFIXES = ("utm_",)
# Host-prefix twins: amp./m. (AMP + mobile) and old. (legacy UI, e.g.
# old.reddit.com) all serve the SAME page as the bare host, so they must collapse
# onto one canonical candidate. An /amp path segment is the same page too.
_HOST_PREFIXES = ("amp.", "m.", "old.")
_AMP_PATH_RE = re.compile(r"/amp(/|$)", re.IGNORECASE)


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url.strip())

    scheme = parts.scheme.lower() or "https"

    host = parts.hostname or ""
    host = host.lower()
    if host.startswith("www."):
        host = host[4:]
    # strip a leading amp./m./old. subdomain (they share one canonical host).
    # The remainder must still look like a host (contain a dot) — otherwise
    # `m.com` / `old.com`, which are ordinary registrable domains, would be
    # mangled into the bare TLD `com` and collide with every other `*.com`.
    for sub in _HOST_PREFIXES:
        if host.startswith(sub) and "." in host[len(sub):]:
            host = host[len(sub):]
            break

    # Drop default port; keep non-default ports.
    netloc = host
    if parts.port is not None and str(parts.port) != _DEFAULT_PORTS.get(scheme):
        netloc = f"{host}:{parts.port}"

    path = parts.path
    # collapse an /amp path segment (…/amp or /amp/…) to the canonical page
    path = _AMP_PATH_RE.sub("/", path)
    # strip index.* files
    path = _INDEX_RE.sub("", path)
    # strip a single trailing slash (but keep root "/")
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]

    # Drop tracking params (utm_*/fbclid/gclid/…); keep every semantic param.
    kept = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
            if k not in _TRACKING_PARAMS
            and not any(k.startswith(pre) for pre in _TRACKING_PREFIXES)]
    query = urlencode(kept)

    # drop fragment; preserve semantic query
    return urlunsplit((scheme, netloc, path, query, ""))
