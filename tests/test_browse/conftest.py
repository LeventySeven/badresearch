"""Shared fixtures for the browse-ladder tests. Mocks everything external."""

from __future__ import annotations

from typing import Any

import pytest

from bad_research.web.base import WebResult


def make_result(content: str, *, url: str = "https://example.test/page",
                title: str = "Example") -> WebResult:
    return WebResult(url=url, title=title, content=content)


@pytest.fixture
def good_result() -> WebResult:
    # Long, clean content — passes looks_like_junk (>= 300 chars, no bot/error signals).
    body = ("This is a substantial article about a real topic. " * 20)
    return make_result(body, title="A Real Article")


@pytest.fixture
def empty_result() -> WebResult:
    # < 300 chars -> looks_like_junk == "Empty or near-empty content" -> escalate 0->1.
    return make_result("tiny", title="Stub")


@pytest.fixture
def bot_result() -> WebResult:
    # Cloudflare interstitial -> looks_like_junk == "Bot detection page: ..." -> escalate to 3b.
    return make_result("Just a moment... Checking your browser. Ray ID: abc123. " * 10,
                       title="Just a moment...")


@pytest.fixture
def login_result() -> WebResult:
    # Short + login signals + /login path -> looks_like_login_wall == True -> escalate to 3.
    return make_result("Please sign in to continue. Create account.",
                       url="https://example.test/login", title="Sign in")


class FakeLLM:
    """A stand-in LLMProvider: returns a canned text per call. Records calls."""

    name = "fake"

    def __init__(self, replies: list[str]) -> None:
        self._replies = list(replies)
        self.calls: list[dict[str, Any]] = []

    def complete(self, messages, *, tier="triage", tools=None, cache=False,
                 max_tokens=4096, temperature=0.1):
        self.calls.append({"messages": messages, "tier": tier, "temperature": temperature})
        from bad_research.llm.base import LLMResponse

        text = self._replies.pop(0) if self._replies else "{}"
        return LLMResponse(text=text, tool_calls=[], usage={}, model="fake")


@pytest.fixture
def fake_llm() -> Any:
    return FakeLLM


import json as _json

# A canonical agent-browser `snapshot -i --json` stdout (dossier 14 §10B / README.md:911-913).
SNAPSHOT_JSON = _json.dumps({
    "success": True,
    "data": {
        "snapshot": (
            "Page: Example - Log in\n"
            "URL: https://example.com/login\n\n"
            "@e1 [heading] \"Log in\"\n"
            "@e2 [form]\n"
            "  @e3 [input type=\"email\"] placeholder=\"Email\"\n"
            "  @e4 [input type=\"password\"] placeholder=\"Password\"\n"
            "  @e5 [button type=\"submit\"] \"Continue\"\n"
            "  @e6 [link] \"Forgot password?\""
        ),
        "refs": {
            "e1": {"role": "heading", "name": "Log in"},
            "e2": {"role": "form", "name": ""},
            "e3": {"role": "textbox", "name": "Email"},
            "e4": {"role": "textbox", "name": "Password"},
            "e5": {"role": "button", "name": "Continue"},
            "e6": {"role": "link", "name": "Forgot password?"},
        },
    },
})

# An empty/near-empty snapshot (lightpanda failed to hydrate → triggers chrome fallback).
EMPTY_SNAPSHOT_JSON = _json.dumps({
    "success": True,
    "data": {"snapshot": "Page: Loading…\nURL: https://spa.example/\n", "refs": {}},
})

# ---- silver envelopes: `{success, data, error}` with `data` a fenced TREE STRING ----
SILVER_FENCE_OPEN = "⟦page-content untrusted⟧"
SILVER_FENCE_CLOSE = "⟦/page-content⟧"

SILVER_SNAPSHOT_JSON = _json.dumps({
    "success": True,
    "data": (
        f"{SILVER_FENCE_OPEN}\n"
        '- title: "Example - Log in" [url=https://example.com/login]\n'
        '* heading "Log in" [level=1, ref=e1]\n'
        "* form [ref=e2]\n"
        '* textbox "Email" [ref=e3]\n'
        '* textbox "Password" [ref=e4]\n'
        '* button "Continue" [ref=e5]\n'
        '* link "Forgot password?" [ref=e6]\n'
        f"{SILVER_FENCE_CLOSE}"
    ),
    "error": None,
})

SILVER_EMPTY_SNAPSHOT_JSON = _json.dumps({
    "success": True,
    "data": f"{SILVER_FENCE_OPEN}\n- title: \"Loading…\" [url=https://spa.example/]\n{SILVER_FENCE_CLOSE}",
    "error": None,
})

SILVER_OPEN_JSON = _json.dumps({
    "success": True,
    "data": {"url": "https://example.com/login", "title": "Example - Log in",
             "page_changed": False},
    "error": None,
})

SILVER_READ_JSON = _json.dumps({
    "success": True,
    "data": f"{SILVER_FENCE_OPEN}\nLog in\n\nEnter your email and password to continue.\n"
            f"{SILVER_FENCE_CLOSE}",
    "error": None,
})

SILVER_OK_JSON = _json.dumps({"success": True, "data": None, "error": None})


class FakeRunner:
    """Stand-in for subprocess.run. Records every argv it is asked to run and returns
    canned (returncode, stdout, stderr) tuples in order. If `route` is given it maps a
    matched command word -> stdout (so a multi-step loop can return different stdout per
    command). Never spawns a real process."""

    def __init__(self, replies=None, route=None, returncode=0):
        self.calls: list[list[str]] = []
        self._replies = list(replies or [])
        self._route = dict(route or {})
        self._returncode = returncode
        self.stdin: str | None = None

    def __call__(self, argv, *, timeout=None, env=None, stdin=None):
        self.calls.append(list(argv))
        if stdin is not None:
            self.stdin = stdin
        # route by the command word (argv[1] after the `agent-browser` program name).
        # the global flags (--engine X, --session Y, ...) precede the command word, so
        # find the first argv element that is not a flag and not a flag's value.
        cmd = _first_command_word(argv)
        if cmd in self._route:
            out = self._route[cmd]
        elif self._replies:
            out = self._replies.pop(0)
        else:
            out = ""
        return (self._returncode, out, "")

    def argvs(self) -> list[list[str]]:
        return self.calls

    def last(self) -> list[str]:
        return self.calls[-1]


# global flags that take a value (so the value is skipped when finding the command word)
_GLOBAL_VALUE_FLAGS = {"--engine", "--session", "--state", "--headers"}


def _first_command_word(argv: list[str]) -> str:
    """Return the agent-browser subcommand word (skipping the program name + global flags)."""
    i = 1  # skip the program name (argv[0])
    while i < len(argv):
        tok = argv[i]
        if tok in _GLOBAL_VALUE_FLAGS:
            i += 2  # skip the flag and its value
            continue
        if tok.startswith("--"):
            i += 1  # bare flag
            continue
        return tok
    return ""
