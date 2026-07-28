"""SilverProvider — keyless agentic browse on the local `silver` CLI.

silver (agent-silver) drives a LOCAL headless Chromium through Playwright and never
calls a model or any provider — no API key, ever. Like agent-browser it hands back an
accessibility tree with stable `@eN` refs and executes ref-grounded actions, so it drops
into the same rung-2.5/3 seat with the same grounding contract. Claude Code (the host
model) remains the brain; this module is only the driver.

Why it is the default browse provider (see docs/HOW_IT_WORKS.md):
  * **Redirect-gated fetch.** `silver read <url>` re-checks EVERY redirect hop, which
    closes the SSRF hole agent-browser leaves open (ladder._do_browse can only validate
    the entry URL and the final landed URL — an intermediate hop through an internal
    host is invisible to it).
  * **Read-only by default.** Actor verbs are not even dispatchable without
    `--enable-actions`. The research path (open → snapshot → read) never passes it, so a
    hostile page cannot talk the driver into clicking or typing.
  * **Clean body text.** `read` returns landmark-skipped Markdown rather than the raw
    a11y tree, so a stored note carries prose instead of widget scaffolding.
  * **Egress allowlist.** `--allowedDomains` is tighten-only, so the browse rung can be
    fenced to the domain being researched.

silver is an EXTERNAL CLI (`npm i -g agent-silver`), NOT a pip dep. `is_available()`
gates construction so the ladder degrades to agent-browser/crawl4ai/httpx without it.
"""

from __future__ import annotations

import inspect
import json
import os
import re
import shutil
import subprocess
from collections.abc import Callable
from typing import Any

from bad_research.browse.agent_browser import (
    CLI_TIMEOUT_S,
    BrowseStep,
    Snapshot,
    normalize_ref,
)
from bad_research.web.base import WebResult

# ---- frozen constants ----
SILVER_PROGRAM = "silver"
DEFAULT_MAX_STEPS = 12
DEFAULT_NAMESPACE = "bad-research"   # keeps our sessions off the user's `default`
READY_TIMEOUT_MS = 25_000            # matches agent-browser's WAIT_TIMEOUT_MS

# A subprocess runner: (argv, *, timeout, env, stdin) -> (returncode, stdout, stderr).
Runner = Callable[..., tuple[int, str, str]]

# silver fences page-derived text; the markers are for the reader, not the corpus.
_FENCE_OPEN = "⟦page-content untrusted⟧"
_FENCE_CLOSE = "⟦/page-content⟧"

# `* link "Andrej Karpathy blog" [ref=e2]` / `- heading "medium.com" [level=1, ref=e1]`
_NODE_RE = re.compile(
    r"^\s*[-*]\s+(?P<role>[A-Za-z][\w-]*)(?:\s+\"(?P<name>[^\"]*)\")?[^\[]*\[(?P<attrs>[^\]]*)\]"
)
_REF_RE = re.compile(r"\bref=(?P<ref>e\d+)\b")
# the snapshot header line: `- title: "A Recipe…" [url=https://…]`
_HEADER_RE = re.compile(r"^\s*[-*]\s+title:\s+\"(?P<title>[^\"]*)\"\s+\[url=(?P<url>[^\]]+)\]")


def _default_runner(argv: list[str], *, timeout: float | None = None,
                    env: dict[str, str] | None = None,
                    stdin: str | None = None) -> tuple[int, str, str]:
    """The production runner: subprocess.run. Never raises on a non-zero exit — silver
    exits 1 on `success:false` and the caller reads the envelope instead."""
    proc = subprocess.run(
        argv, capture_output=True, text=True, timeout=timeout,
        env=env, input=stdin,
    )
    return (proc.returncode, proc.stdout or "", proc.stderr or "")


def is_available(program: str = SILVER_PROGRAM) -> bool:
    """True iff the silver CLI is on PATH (detect-and-degrade contract)."""
    return shutil.which(program) is not None


def _runner_accepts_stdin(runner: Runner) -> bool:
    try:
        sig = inspect.signature(runner)
    except (TypeError, ValueError):
        return False
    return "stdin" in sig.parameters or any(
        p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
    )


def default_session(pid: int | None = None) -> str:
    """One silver session per OS process. Parallel fetchers are separate processes, so
    they never contend on the same session lock; a single process reuses one browser."""
    return f"br-{os.getpid() if pid is None else pid}"


class _SilverCLI:
    """Builds + runs silver command argv. The runner is injectable so tests assert the
    constructed argv and feed canned stdout (NO real subprocess in tests).

    silver takes its flags AFTER the verb, so the argv is
    `[program, verb, *args, *flags, --json]`.
    """

    def __init__(
        self,
        *,
        runner: Runner | None = None,
        session: str | None = None,
        namespace: str = DEFAULT_NAMESPACE,
        enable_actions: bool = False,
        allowed_domains: str | None = None,
        program: str = SILVER_PROGRAM,
        timeout_s: float = CLI_TIMEOUT_S,
    ) -> None:
        self._runner = runner or _default_runner
        self.session = session or default_session()
        self.namespace = namespace
        self.enable_actions = enable_actions
        self.allowed_domains = allowed_domains
        self.program = program
        self.timeout_s = timeout_s

    # ---- trailing flags (order is stable, asserted by tests) ----
    def _flags(self) -> list[str]:
        argv = ["--session", self.session]
        if self.namespace:
            argv += ["--namespace", self.namespace]
        if self.allowed_domains:
            argv += ["--allowedDomains", self.allowed_domains]
        if self.enable_actions:
            argv.append("--enable-actions")
        argv.append("--json")
        return argv

    def _run(self, *args: str, stdin: str | None = None) -> str:
        argv = [self.program, *args, *self._flags()]
        if _runner_accepts_stdin(self._runner):
            _rc, out, _err = self._runner(argv, timeout=self.timeout_s, env=None, stdin=stdin)
        else:
            _rc, out, _err = self._runner(argv, timeout=self.timeout_s, env=None)
        return out

    # ---- lifecycle / nav ----
    def open(self, url: str) -> str:
        return self._run("open", url)

    def close(self) -> str:
        return self._run("close")

    # ---- perception ----
    def snapshot(self, *, interactive: bool = True) -> str:
        return self._run("snapshot", "-i") if interactive else self._run("snapshot")

    def read(self) -> str:
        """Plain-text body of the live page (innerText), landmark-skipped."""
        return self._run("read")

    def get_text(self, ref: str) -> str:
        return self._run("get", "text", ref)

    def eval_js(self, js: str) -> str:
        """In-page JS. An actor verb: without --enable-actions silver refuses it with
        `not_permitted` rather than running it."""
        return self._run("eval", js)

    # ---- interaction (each needs --enable-actions) ----
    def click(self, ref: str) -> str:
        return self._run("click", ref)

    def fill(self, ref: str, value: str) -> str:
        return self._run("fill", ref, value)

    def type_text(self, ref: str, value: str) -> str:
        return self._run("type", ref, value)

    def keyboard_press(self, key: str) -> str:
        """Raw key press on the focused element. A BrowseStep('press') carries the KEY in
        `target` (agent-browser parity), not a ref, so the ref-scoped `press @ref <key>`
        form does not apply."""
        return self._run("keyboard", "press", key)

    def select(self, ref: str, *values: str) -> str:
        return self._run("select", ref, *values)

    # ---- wait ----
    def wait_ready(self) -> str:
        """Dual-quiet page-ready (DOM-quiet + network-quiet). More robust than
        `--load networkidle` on SPAs where networkidle never fires."""
        return self._run("wait", "--ready")

    def wait_text(self, text: str) -> str:
        return self._run("wait", "--text", text)

    def wait_url(self, pattern: str) -> str:
        return self._run("wait", "--url", pattern)

    # ---- auth ----
    def state_save(self, path: str) -> str:
        return self._run("state", "save", path)

    def state_load(self, path: str) -> str:
        return self._run("state", "load", path)

    def cookies_set_curl(self, curl_file: str) -> str:
        return self._run("cookies", "set", "--curl", curl_file)


# ============================================================ envelope + snapshot
def envelope_data(stdout: str) -> Any:
    """Unwrap silver's `{success, data, error}` envelope. Returns None on a failed or
    malformed envelope — never raises, so the loop/ladder can degrade."""
    try:
        payload = json.loads(stdout)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(payload, dict) or not payload.get("success"):
        return None
    return payload.get("data")


def strip_fence(text: str) -> str:
    """Drop silver's untrusted-content fence markers. The fence is a boundary signal for
    the reading model, not part of the page, and it must not reach a stored note."""
    return text.replace(_FENCE_OPEN, "").replace(_FENCE_CLOSE, "").strip()


def parse_snapshot(stdout: str) -> Snapshot:
    """Parse `snapshot -i --json` stdout into the shared Snapshot (same grounding object
    agent-browser produces, so `has_ref`/`is_empty` behave identically).

    silver's snapshot `data` is the tree TEXT — refs are inline `[ref=eN]` markers rather
    than a separate map — so the refs dict is rebuilt from the tree.
    """
    data = envelope_data(stdout)
    if not isinstance(data, str):
        return Snapshot()
    text = strip_fence(data)
    refs: dict[str, dict[str, Any]] = {}
    title = ""
    url = ""
    for line in text.splitlines():
        header = _HEADER_RE.match(line)
        if header:
            title = header.group("title").strip()
            url = header.group("url").strip()
            continue
        node = _NODE_RE.match(line)
        if not node:
            continue
        ref_m = _REF_RE.search(node.group("attrs"))
        if not ref_m:
            continue
        refs[normalize_ref(ref_m.group("ref"))] = {
            "role": node.group("role"),
            "name": (node.group("name") or "").strip(),
        }
    return Snapshot(text=text, refs=refs, title=title, url=url)


# kinds that change the page → re-snapshot afterward
_PAGE_CHANGING = {"click", "press", "select"}


class SilverProvider:
    """Keyless agentic browse on the local silver CLI. Claude Code is the brain: it
    supplies `steps`; this driver executes them and re-perceives.

    Interface-compatible with AgentBrowserProvider so the ladder can hold either.
    """

    name = "silver"

    def __init__(
        self,
        *,
        runner: Runner | None = None,
        program: str = SILVER_PROGRAM,
        namespace: str = DEFAULT_NAMESPACE,
        session: str | None = None,
        allowed_domains: str | None = None,
    ) -> None:
        self._runner = runner
        self.program = program
        self.namespace = namespace
        self.session = session
        self.allowed_domains = allowed_domains

    def _cli(self, *, enable_actions: bool = False) -> _SilverCLI:
        return _SilverCLI(
            runner=self._runner,
            program=self.program,
            namespace=self.namespace,
            session=self.session,
            allowed_domains=self.allowed_domains,
            enable_actions=enable_actions,
        )

    def snapshot(self, *, interactive: bool = True) -> Snapshot:
        return parse_snapshot(self._cli().snapshot(interactive=interactive))

    def browse(
        self,
        url: str,
        instruction: str,
        *,
        max_steps: int = DEFAULT_MAX_STEPS,
        variables: dict[str, Any] | None = None,
        replay_key: str | None = None,
        steps: list[BrowseStep] | None = None,
        state: str | None = None,
        headers: str | None = None,
    ) -> WebResult:
        """Open the page, perceive it, run any host-supplied steps, return the body.

        With no steps this is the 'observe' case and the whole call runs WITHOUT
        `--enable-actions`: silver refuses actor verbs outright, so the research path
        cannot be steered into acting by page content.
        """
        if not is_available(self.program):
            return WebResult(url=url, title="", content="",
                             metadata={"unavailable": True, "provider": self.name})

        acting = bool(steps)
        cli = self._cli(enable_actions=acting)

        if state:
            cli.state_load(state)

        opened = envelope_data(cli.open(url))
        cli.wait_ready()
        snap = parse_snapshot(cli.snapshot(interactive=True))

        executed = 0
        for step in (steps or []):
            if executed >= max_steps:
                break
            # ---- grounding: a @eN target must exist in the current snapshot refs ----
            if step.target.startswith("@") and not snap.has_ref(step.target):
                continue  # ungrounded ref → skip, never guess
            self._dispatch(cli, step)
            executed += 1
            if step.kind in _PAGE_CHANGING:
                cli.wait_ready()
                snap = parse_snapshot(cli.snapshot(interactive=True))  # re-perceive

        # ---- body text beats the a11y tree for a stored note; tree is the fallback ----
        body = envelope_data(cli.read())
        content = strip_fence(body) if isinstance(body, str) else ""
        if not content:
            content = snap.text

        landed = snap.url or (opened.get("url") if isinstance(opened, dict) else "") or url
        title = snap.title or (opened.get("title") if isinstance(opened, dict) else "") or ""

        cli.close()
        return WebResult(
            url=landed,
            title=title,
            content=content,
            metadata={
                "engine": "silver",
                "provider": self.name,
                "refs": list(snap.refs.keys()),
                "steps_executed": executed,
                "replay_key": replay_key,
            },
        )

    @staticmethod
    def _dispatch(cli: _SilverCLI, step: BrowseStep) -> None:
        k = step.kind
        if k == "click":
            cli.click(step.target)
        elif k == "fill":
            cli.fill(step.target, step.value)
        elif k == "type":
            cli.type_text(step.target, step.value)
        elif k == "press":
            cli.keyboard_press(step.target)
        elif k == "select":
            cli.select(step.target, step.value)
        elif k == "eval":
            cli.eval_js(step.value)
        elif k == "wait_text":
            cli.wait_text(step.target)
        elif k == "wait_url":
            cli.wait_url(step.target)
        # unknown kind → no-op (graceful)

    def save_state(self, path: str) -> None:
        """Persist cookies + storage to a Playwright StorageState JSON."""
        self._cli().state_save(path)

    def cookies_set_curl(self, curl_file: str) -> None:
        """Replay a Copy-as-cURL dump's cookies (the no-automation auth path). The model
        never sees the password — only the resulting cookies."""
        self._cli().cookies_set_curl(curl_file)
