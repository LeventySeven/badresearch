"""The PreToolUse hook must BLOCK a WebFetch at an internal address.

Why this exists: the native-fallback path added in PR #26 retrieves URLs with the
host `WebFetch` tool, which never reaches `assert_url_safe` — the engine's only SSRF
choke point. The fetcher agent reads untrusted third-party pages AND holds an
outbound channel, so the prompt-level rule guarding that path is exactly the kind of
control a model under load skips. These tests pin the guard at the tooling layer,
where it cannot be skipped, and assert it agrees with the Python denylist.
"""

from __future__ import annotations

import json
import shutil
import subprocess

import pytest

from bad_research.core.fetcher import _host_block_reason, is_blocked_url
from bad_research.core.hooks import HOOK_SCRIPT_TEMPLATE

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")

BLOCK = 2  # PreToolUse: exit 2 blocks the tool call and shows stderr to the model


@pytest.fixture(scope="module")
def hook(tmp_path_factory) -> str:
    """The hook script exactly as `bad install` writes it."""
    path = tmp_path_factory.mktemp("hook") / "hook.js"
    path.write_text(HOOK_SCRIPT_TEMPLATE.format(hpr_path="bad"), encoding="utf-8")
    return str(path)


def run(hook: str, payload, cwd) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["node", hook],
        input=payload if isinstance(payload, str) else json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(cwd),
        timeout=30,
    )


def webfetch(url: str) -> dict:
    return {"tool_name": "WebFetch", "tool_input": {"url": url}}


# The addresses that matter. 169.254.169.254 is cloud metadata — the payload an
# injected "fetch this URL" is actually after.
BLOCKED_URLS = [
    "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
    "http://127.0.0.1:8080/admin",
    "http://localhost/",
    "http://10.0.0.5/",
    "http://172.16.0.1/",
    "http://192.168.1.1/",
    "http://[::1]:9000/",
    "http://0.0.0.0/",
    "http://[::ffff:127.0.0.1]/",  # IPv4-mapped; `new URL()` normalizes to ::ffff:7f00:1
]

# NOT in the list above, deliberately: `metadata.google.internal`. It does not resolve
# off-GCP, and BOTH implementations allow an unresolvable host through by design (see
# _host_block_reason: "let the fetch fail naturally"). On a real GCP box it resolves to
# 169.254.169.254 and both block it. Asserting otherwise here would pin an
# environment-specific result, not a property of the guard.


@pytest.mark.parametrize("url", BLOCKED_URLS)
def test_internal_targets_are_blocked(hook, tmp_path, url):
    r = run(hook, webfetch(url), tmp_path)
    assert r.returncode == BLOCK, f"{url} was NOT blocked (exit {r.returncode})"
    assert "BLOCKED by hyperresearch SSRF guard" in r.stderr


@pytest.mark.parametrize("url", BLOCKED_URLS)
def test_the_hook_agrees_with_the_python_denylist(url):
    """One denylist, two enforcement points — they must not drift apart."""
    assert is_blocked_url(url), f"{url} blocked by the hook but NOT by is_blocked_url"


# ------------------------------------------------------------------ the parity table
#
# ONE table, TWO enforcement points. Every row below is asserted against BOTH the JS
# matcher inside the hook (end to end: exit 2 = blocked) and the Python
# `_host_block_reason`, so neither can gain or lose a range without the other going
# red. Without this the hook drifted silently: it missed every IPv4-embedding IPv6
# form (NAT64 64:ff9b::/96, 6to4 2002::/16, Teredo 2001::/32, IPv4-translated
# ::ffff:0:0/96) that the Python denylist blocks, while blocking CGNAT that Python
# allowed.
#
# Literal IPs and the fixed hostnames only — no row depends on what DNS answers today.
PARITY: list[tuple[str, bool]] = [
    # --- IPv4 ---------------------------------------------------------------
    ("http://169.254.169.254/latest/meta-data/", True),   # cloud metadata
    ("http://127.0.0.1:8080/admin", True),                # 127/8   loopback
    ("http://10.0.0.5/", True),                           # 10/8    private
    ("http://172.16.0.1/", True),                         # 172.16/12 private
    ("http://172.15.0.1/", False),                        # just below it
    ("http://172.32.0.1/", False),                        # just above it
    ("http://192.168.1.1/", True),                        # 192.168/16 private
    ("http://0.0.0.0/", True),                            # 0/8     this-network
    ("http://100.64.0.1/", True),                         # 100.64/10 CGNAT
    ("http://100.63.255.255/", False),                    # just below CGNAT
    ("http://192.0.0.9/", True),                          # 192.0.0/24 IETF protocol
    ("http://198.18.0.1/", True),                         # 198.18/15 benchmarking
    ("http://203.0.113.9/", True),                        # TEST-NET-3
    ("http://224.0.0.1/", True),                          # multicast
    ("http://255.255.255.255/", True),                    # broadcast (240/4)
    ("http://8.8.8.8/", False),                           # public
    # --- IPv6 ---------------------------------------------------------------
    ("http://[::1]/", True),                              # loopback
    ("http://[::]/", True),                               # unspecified
    ("http://[::ffff:127.0.0.1]/", True),                 # IPv4-mapped loopback
    ("http://[::ffff:169.254.169.254]/", True),           # IPv4-mapped metadata
    ("http://[::ffff:8.8.8.8]/", False),                  # IPv4-mapped public
    ("http://[64:ff9b::7f00:1]/", True),                  # NAT64 -> 127.0.0.1
    ("http://[64:ff9b::a9fe:a9fe]/", True),               # NAT64 -> 169.254.169.254
    ("http://[2002:7f00:1::]/", True),                    # 6to4 -> 127.0.0.1
    ("http://[2001:0:5ef5:79fd::1]/", True),              # Teredo
    ("http://[::ffff:0:7f00:1]/", True),                  # IPv4-translated 127.0.0.1
    ("http://[::808:808]/", True),                        # IPv4-compatible (deprecated)
    ("http://[fe80::1]/", True),                          # link-local
    ("http://[fc00::1]/", True),                          # unique-local
    ("http://[fd00::1]/", True),                          # unique-local
    ("http://[fec0::1]/", True),                          # site-local (deprecated)
    ("http://[ff02::1]/", True),                          # multicast
    ("http://[2001:db8::1]/", True),                      # documentation
    ("http://[3fff::1]/", True),                          # documentation
    ("http://[2001:4860:4860::8888]/", False),            # public
    ("http://[2620:fe::fe]/", False),                     # public
    # --- names and non-hosts -------------------------------------------------
    ("http://localhost/", True),
    ("file:///etc/passwd", True),                         # no host at all
]

PARITY_IDS = [url for url, _ in PARITY]


@pytest.mark.parametrize("url,blocked", PARITY, ids=PARITY_IDS)
def test_python_denylist_matches_the_parity_table(url, blocked):
    reason = _host_block_reason(url)
    assert (reason is not None) is blocked, f"{url}: _host_block_reason -> {reason!r}"


@pytest.mark.parametrize("url,blocked", PARITY, ids=PARITY_IDS)
def test_the_hook_matches_the_parity_table(hook, tmp_path, url, blocked):
    """The hook is the enforcement point; a range it misses is a range that ships."""
    r = run(hook, webfetch(url), tmp_path)
    assert (r.returncode == BLOCK) is blocked, (
        f"{url}: hook exit {r.returncode} (expected {BLOCK if blocked else 0}) — "
        "the hook has drifted from core.fetcher._host_block_reason"
    )


def test_a_public_url_is_allowed(hook, tmp_path):
    r = run(hook, webfetch("https://example.com/article"), tmp_path)
    assert r.returncode == 0
    assert "BLOCKED" not in r.stderr


def test_an_unresolvable_host_is_allowed_through(hook, tmp_path):
    """Matches _host_block_reason: let the fetch fail naturally rather than block a
    legitimate-but-momentarily-unresolvable host."""
    r = run(hook, webfetch("https://nx-does-not-exist-9d3f1a.invalid/x"), tmp_path)
    assert r.returncode == 0


def test_a_url_with_no_host_is_blocked(hook, tmp_path):
    r = run(hook, webfetch("file:///etc/passwd"), tmp_path)
    assert r.returncode == BLOCK


def test_other_tools_are_never_blocked(hook, tmp_path):
    """The hook also matches Glob/Grep/WebSearch. Only WebFetch carries a URL."""
    for tool in ("Grep", "Glob", "WebSearch"):
        r = run(hook, {"tool_name": tool, "tool_input": {"pattern": "x"}}, tmp_path)
        assert r.returncode == 0, f"{tool} must not be blocked"


@pytest.mark.parametrize("payload", ["", "not json at all", "{}", '{"tool_name":"WebFetch"}'])
def test_malformed_input_fails_open(hook, tmp_path, payload):
    """A crashed or confused guard must never wedge a session."""
    r = run(hook, payload, tmp_path)
    assert r.returncode == 0


def test_the_block_message_tells_the_model_what_to_do(hook, tmp_path):
    r = run(hook, webfetch("http://169.254.169.254/"), tmp_path)
    assert r.returncode == BLOCK
    # Names the guarded alternative, and says not to retry — an injected redirect
    # chain is the likeliest way an agent lands here.
    assert "bad fetch" in r.stderr
    assert "do not retry" in r.stderr.lower()


def test_the_reminder_still_fires_when_a_vault_exists(hook, tmp_path):
    (tmp_path / ".hyperresearch").mkdir()
    r = run(hook, webfetch("https://example.com/"), tmp_path)
    assert r.returncode == 0
    assert "HYPERRESEARCH" in r.stderr
