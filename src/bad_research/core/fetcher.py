"""Core fetch logic — reusable by CLI and MCP server."""

from __future__ import annotations

import hashlib
import ipaddress
import socket
from urllib.parse import urlparse

from bad_research.browse import fetch_tiered  # Tier 0->3 ladder hook


class SSRFError(ValueError):
    """Raised when a URL resolves to a private/loopback/metadata address.

    The funnel + browse layers fetch attacker-influenceable URLs (search-result
    links + chained-crawl hrefs). Without this guard a malicious page could point
    the fetcher at `http://169.254.169.254/` (cloud metadata) or an internal
    service. We refuse any URL whose host resolves into a blocked range.
    """


# Hostnames refused outright (no DNS resolution needed).
_BLOCKED_HOSTNAMES = frozenset({"localhost", "ip6-localhost", "ip6-loopback"})


# Ranges `ipaddress` calls neither private nor reserved, but that an egress guard must
# still refuse. Blocking them is also what the PreToolUse hook has always done, and the
# two are pinned to each other by tests/test_core/test_pretooluse_ssrf_guard.py.
_EXTRA_BLOCKED_NETWORKS = (
    ipaddress.ip_network("100.64.0.0/10"),  # CGNAT — someone else's internal network
    ipaddress.ip_network("192.0.0.0/24"),   # IETF protocol block (192.0.0.9/.10 anycast)
    ipaddress.ip_network("fec0::/10"),      # site-local: deprecated, still internal
)


def _is_blocked_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """True if `ip` is loopback / private / link-local / metadata / reserved.

    Covers 127.0.0.0/8, 10/8, 172.16/12, 192.168/16, 169.254.0.0/16 (cloud
    metadata at 169.254.169.254), ::1, and IPv4-mapped IPv6 forms of all of them,
    plus `_EXTRA_BLOCKED_NETWORKS`.
    """
    # Unwrap IPv4-mapped IPv6 (e.g. ::ffff:127.0.0.1) so the v4 rules apply.
    mapped = getattr(ip, "ipv4_mapped", None)
    if mapped is not None:
        ip = mapped
    return (
        ip.is_loopback
        or ip.is_private
        or ip.is_link_local      # 169.254.0.0/16 incl. cloud metadata
        or ip.is_reserved
        or ip.is_unspecified
        or ip.is_multicast
        or any(ip in net for net in _EXTRA_BLOCKED_NETWORKS)  # mismatched family: False
    )


def _host_block_reason(url: str) -> str | None:
    """Return a human-readable reason string if `url`'s host is blocked, else None.

    This is the single source of truth for the SSRF denylist. Both `assert_url_safe`
    (raises) and `is_blocked_url` (boolean) are thin wrappers over it, and the
    crawl4ai render-rung route handler reuses `is_blocked_url` — one denylist, one
    decision function (DRY).

    Resolves the hostname (all A/AAAA records) and blocks if ANY resolved address
    falls in a blocked range — closing the DNS-rebinding-ish gap where a name resolves
    to both a public and an internal IP. Literal IPs are checked directly.
    Non-resolvable hosts are allowed through (the fetch will fail normally) so we never
    block legitimate-but-momentarily-unresolvable hosts.
    """
    host = (urlparse(url).hostname or "").strip().rstrip(".").lower()
    if not host:
        return f"refusing URL with no host: {url!r}"
    if host in _BLOCKED_HOSTNAMES:
        return f"refusing loopback host {host!r}"

    # Literal IP in the URL — check directly, no DNS.
    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
    if literal is not None:
        if _is_blocked_ip(literal):
            return f"refusing private/loopback/metadata IP {host!r}"
        return None

    # Hostname — resolve and check every returned address.
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return None  # unresolvable: let the downstream fetch fail naturally
    for info in infos:
        addr = info[4][0]
        # strip IPv6 zone id if present (fe80::1%eth0)
        addr = addr.split("%", 1)[0]
        try:
            ip = ipaddress.ip_address(addr)
        except ValueError:
            continue
        if _is_blocked_ip(ip):
            return f"host {host!r} resolves to blocked address {addr}"
    return None


def is_blocked_url(url: str) -> bool:
    """True if `url` targets a private/loopback/link-local/metadata/reserved address.

    The boolean form of the shared SSRF predicate (see `_host_block_reason`). Used by
    the crawl4ai render-rung Playwright route handler to `route.abort()` any request
    (main-frame nav, redirect, or sub-resource) that resolves to a blocked host —
    reusing the SAME denylist as `assert_url_safe` so there is exactly one source of
    truth. A URL with no host (e.g. `file:///`) is treated as blocked.
    """
    return _host_block_reason(url) is not None


def assert_url_safe(url: str) -> None:
    """Raise SSRFError if `url` targets a private/loopback/metadata address.

    Thin wrapper over the shared `_host_block_reason` denylist (DRY) — the same
    predicate `is_blocked_url` and the render route handler use.
    """
    reason = _host_block_reason(url)
    if reason is not None:
        raise SSRFError(reason)


_MAX_REDIRECT_HOPS = 5


def safe_redirect_get(
    client,
    url: str,
    *,
    headers: dict | None = None,
    max_hops: int = _MAX_REDIRECT_HOPS,
):
    """GET `url` with `client`, following redirects MANUALLY and re-validating each
    hop with `assert_url_safe` BEFORE the request is sent.

    `assert_url_safe(url)` only checks the *input* URL once. When a fetch provider
    uses `httpx.Client(follow_redirects=True)`, a public URL that 302-redirects to
    `http://169.254.169.254/` (cloud metadata) or another internal host is followed
    with no further check — an SSRF bypass. This helper closes that gap: it requires
    the caller's client to have redirect-following DISABLED, then walks the redirect
    chain itself, calling `assert_url_safe` on every `Location` target.

    The supplied `client` MUST be constructed with `follow_redirects=False`. Returns
    the final non-redirect `httpx.Response`. Raises `SSRFError` if any hop targets a
    blocked address, or `RuntimeError` if the redirect chain exceeds `max_hops`.
    """
    from urllib.parse import urljoin

    current = url
    for _ in range(max_hops + 1):
        assert_url_safe(current)
        resp = client.get(current, headers=headers)
        # httpx exposes is_redirect for 3xx with a Location header.
        if not getattr(resp, "is_redirect", False):
            return resp
        location = resp.headers.get("location") or resp.headers.get("Location")
        if not location:
            return resp
        # Resolve relative redirects against the current URL before re-validating.
        current = urljoin(current, location)
    raise RuntimeError(f"too many redirects (> {max_hops}) starting from {url!r}")


def fetch_and_save(
    vault,
    url: str,
    tags: list[str] | None = None,
    title: str | None = None,
    parent: str | None = None,
    provider_name: str | None = None,
    save_assets: bool = False,
    visible: bool = False,
    *,
    tier_max: int | None = None,
    instruction: str | None = None,
    schema: dict | str | None = None,
) -> dict:
    """Fetch a URL and save as a research note. Returns result dict.

    With none of `tier_max`/`instruction`/`schema` set (the default), behaviour is
    byte-for-byte unchanged: a single `prov.fetch(url)` via the configured provider.
    Setting any of them routes the fetch through the Tier 0->3 escalation ladder
    (`browse.fetch_tiered`), which may climb to JS-render / typed-extract / agentic browse.

    Raises:
        ValueError: If URL is already fetched.
        RuntimeError: If fetch fails.
    """
    from bad_research.web.base import get_provider

    # SSRF guard — refuse private/loopback/cloud-metadata targets before any
    # network call. URLs here are attacker-influenceable (search results +
    # chained-crawl links), so this is the choke point.
    assert_url_safe(url)

    tags = tags or []
    conn = vault.db

    # Check if URL already fetched
    existing = conn.execute("SELECT note_id FROM sources WHERE url = ?", (url,)).fetchone()
    if existing:
        raise ValueError(f"URL already fetched as note '{existing['note_id']}'")

    # Auto-visible for sites that kill headless sessions on first contact
    if not visible and vault.config.web_profile:
        from urllib.parse import urlparse as _urlparse

        domain = _urlparse(url).netloc.lower()
        _auth_aggressive = (
            "linkedin.com", "twitter.com", "x.com", "facebook.com",
            "instagram.com", "tiktok.com",
        )
        if any(d in domain for d in _auth_aggressive):
            visible = True

    # Fetch content — opt-in ladder when any tier arg is set, else the unchanged default path.
    use_ladder = tier_max is not None or instruction is not None or schema is not None
    if use_ladder:
        result = fetch_tiered(
            url,
            tier_max=tier_max if tier_max is not None else 3,
            instruction=instruction,
            schema=schema,
        )
        # The ladder already chose a provider; record a synthetic name.
        prov_name = result.metadata.get("fetch_provider") \
            or ("browse" if instruction else "tiered")

        class _ProvShim:
            name = prov_name
        prov = _ProvShim()
    else:
        prov = get_provider(
            provider_name or vault.config.web_provider,
            profile=vault.config.web_profile,
            magic=vault.config.web_magic,
            headless=not visible,
        )
        result = prov.fetch(url)

    # Detect login redirects — abort instead of saving junk
    if result.looks_like_login_wall(url):
        raise RuntimeError(
            f"Redirected to login page ({result.title}). "
            "Your browser profile session may have expired. "
            "Create a crawl4ai login profile (`crwl profiles`) and set it in .hyperresearch/config.toml."
        )

    # Detect junk pages — captcha, error pages, binary garbage, empty content
    junk_reason = result.looks_like_junk()
    if junk_reason:
        raise RuntimeError(f"Skipped junk content: {junk_reason}")

    # Write note + sync + record source (stubbable seam for tests)
    note_title = title or result.title or urlparse(url).path.split("/")[-1] or "Untitled"
    domain = result.domain

    note_id = _persist_note(
        vault, url, result, prov, tags, note_title, parent, save_assets
    )
    raw_file_path = result.metadata.get("raw_file")
    note_rel_path = result.metadata.get("_note_path", f"research/notes/{note_id}.md")

    # Save assets if requested
    saved_assets: list[dict] = []
    if save_assets:
        from bad_research.cli.fetch import _save_assets

        assets_dir = vault.root / "research" / "assets" / note_id
        saved_assets = _save_assets(conn, result, note_id, assets_dir)

    return {
        "note_id": note_id,
        "title": note_title,
        "url": url,
        "domain": domain,
        "provider": prov.name,
        "path": note_rel_path,
        "word_count": len(result.content.split()),
        "assets": saved_assets,
        "raw_file": raw_file_path,
    }


def _persist_note(vault, url, result, prov, tags, note_title, parent, save_assets):
    """Write the note, persist raw-file / extracted frontmatter, sync, and record source.

    Returns the ``note_id`` string. Any saved raw-file path is stashed on
    ``result.metadata["raw_file"]`` so the caller can surface it without a tuple return
    (keeps the stub seam a simple ``-> str``). Isolated from ``fetch_and_save`` so tests can
    stub it without dragging in the full sync machinery. The logic here is identical to
    the pre-ladder inline body of ``fetch_and_save`` (plus the new ``extracted`` block).
    """
    from bad_research.core.note import write_note
    from bad_research.core.sync import compute_sync_plan, execute_sync

    conn = vault.db
    domain = result.domain

    extra_meta = {
        "source": url,
        "source_domain": domain,
        "fetched_at": result.fetched_at.isoformat(),
        "fetch_provider": prov.name,
    }
    if result.metadata.get("author"):
        extra_meta["author"] = result.metadata["author"]

    note_path = write_note(
        vault.notes_dir,
        title=note_title,
        body=result.content,
        tags=tags,
        status="draft",
        source=url,
        parent=parent,
        extra_frontmatter=extra_meta,
    )

    # Save raw file (PDF, etc.) if present
    raw_file_path = None
    if result.raw_bytes and result.raw_content_type:
        ext_map = {
            "application/pdf": ".pdf",
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/gif": ".gif",
            "image/webp": ".webp",
        }
        ext = ext_map.get(result.raw_content_type, "")
        if ext:
            raw_dir = vault.root / "research" / "raw"
            raw_dir.mkdir(parents=True, exist_ok=True)
            raw_filename = note_path.stem + ext
            raw_file = raw_dir / raw_filename
            raw_file.write_bytes(result.raw_bytes)
            raw_file_path = f"raw/{raw_filename}"

    # Note: tagging and summarization is the agent's job, not an automatic process.

    # Add raw_file reference to frontmatter AFTER enrich (enrich rewrites frontmatter)
    if raw_file_path:
        note_text = note_path.read_text(encoding="utf-8")
        if note_text.startswith("---") and "raw_file:" not in note_text:
            end = note_text.find("---", 3)
            if end != -1:
                note_text = (
                    note_text[:end]
                    + f"raw_file: {raw_file_path}\n"
                    + note_text[end:]
                )
                note_path.write_text(note_text, encoding="utf-8")

    # Persist any typed-extraction dict from the Tier-2 ladder rung into frontmatter.
    extracted = result.metadata.get("extracted")
    if extracted:
        note_text = note_path.read_text(encoding="utf-8")
        if note_text.startswith("---") and "extracted:" not in note_text:
            import json as _json
            end = note_text.find("---", 3)
            if end != -1:
                note_text = (
                    note_text[:end]
                    + "extracted: " + _json.dumps(extracted, ensure_ascii=False) + "\n"
                    + note_text[end:]
                )
                note_path.write_text(note_text, encoding="utf-8")

    # Sync
    note_id = note_path.stem
    plan = compute_sync_plan(vault)
    if plan.to_add or plan.to_update:
        execute_sync(vault, plan)

    # Record source
    content_hash = hashlib.sha256(result.content.encode("utf-8")).hexdigest()[:16]
    conn.execute(
        """INSERT INTO sources (url, note_id, domain, fetched_at, provider, content_hash)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (url, note_id, domain, result.fetched_at.isoformat(), prov.name, content_hash),
    )
    conn.commit()

    if raw_file_path:
        result.metadata["raw_file"] = raw_file_path
    # Preserve the original exact relative path (str(note_path.relative_to(vault.root))).
    result.metadata["_note_path"] = str(note_path.relative_to(vault.root))
    return note_id
