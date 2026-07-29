"""Regression lock for the slim-CLI capability probe + its native-fetch fallback.

Three defects this pins, all found in review of the slim-CLI resilience change:

1. The probe keyed the degrade decision on `bad sources`, a subcommand that has
   NEVER existed in this Typer app. It therefore recorded `sources: false` on
   every install, and the "any missing capability => file-based path" rule then
   forced EVERY run — full CLI included — onto the degraded native path. The
   decision is now gated on `fetch` alone.

2. The native fallback fetches with the host `WebFetch` tool, which does NOT go
   through `core.fetcher.assert_url_safe` — the engine's single SSRF choke point
   (`cli/vault_cmds.fetch_cmd` calls it before the first byte). The fetcher agent
   is the #1 lethal-trifecta node and its Phase 2 URLs come out of untrusted page
   text, so the fallback prompt must restate the guarantee it is bypassing:
   refuse private/loopback/link-local/metadata hosts and re-check every redirect
   hop. These assertions pin that text into the prompt.

3. `Write` truncates; `core.note.write_note` disambiguates with `-2`, `-3`, ….
   The fallback must carry the collision rule or a title clash silently repoints
   every existing `[[wiki-link]]` at the wrong body.
"""

from __future__ import annotations

import re

from bad_research.cli import app
from bad_research.cli.vault_cmds import _SCRATCH_NAMES
from bad_research.core import hooks


def _fetcher_prompt() -> str:
    return hooks.RESEARCHER_AGENT.format(hpr_path="bad")


def _capability_section(text: str) -> str:
    """The fetcher agent's `## Capability detection` section body."""
    start = text.index("## Capability detection")
    end = text.index("\n## ", start + 1)
    return text[start:end]


# ── 1. no phantom `sources` capability ────────────────────────────────────────

def test_sources_is_not_a_real_cli_command():
    """The premise of the fix: `bad sources` does not exist and never did."""
    names = {c.name or (c.callback.__name__ if c.callback else "")
             for c in app.registered_commands}
    names |= {g.name for g in app.registered_groups}
    assert "sources" not in names


def test_probe_does_not_reference_the_phantom_sources_command(skills_dir):
    entry = (skills_dir / "bad-research.md").read_text(encoding="utf-8")
    assert "bad sources" not in entry
    assert '"sources"' not in entry
    assert "sources_ok" not in entry
    assert "bad sources" not in _fetcher_prompt()


def test_degrade_decision_is_gated_on_fetch_alone(skills_dir):
    entry = (skills_dir / "bad-research.md").read_text(encoding="utf-8")
    # The entry skill must state the positive rule: fetch true -> CLI path.
    assert "`fetch: true`" in entry and "`fetch: false`" in entry
    assert "gated on `fetch` ALONE" in entry
    # assets / note_new / note_update must NOT be path switches on their own.
    assert "None of them force the fallback path on their own." in entry
    # The fetcher agent says the same thing.
    cap = _capability_section(_fetcher_prompt())
    assert "`fetch` is the ONLY capability that decides this branch" in cap


def test_probe_lines_are_all_guarded_against_set_e(skills_dir):
    """Every probe in the block must swallow its own non-zero exit.

    The block exists because `set -e` aborts on a missing subcommand; an
    unguarded `bad doctor -j` (or a bare `cat` of a missing caps file) defeats
    the whole point on exactly the slim build it is meant to detect.
    """
    entry = (skills_dir / "bad-research.md").read_text(encoding="utf-8")
    block = entry[entry.index("Detect the surface up front"):]
    block = block[: block.index("```", block.index("```bash") + 7)]
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("bad "):
            continue
        assert ">/dev/null 2>&1 &&" in line and "||" in line, \
            f"unguarded probe line aborts under `set -e`: {line!r}"

    cap = _capability_section(_fetcher_prompt())
    cat_line = next(ln for ln in cap.splitlines() if ln.startswith("cat research/cli-caps.json"))
    assert cat_line.rstrip().endswith("|| true"), \
        "a missing cli-caps.json makes `cat` exit 1 and kills the probe under `set -e`"


# ── 2. the SSRF guarantee the native fallback bypasses ────────────────────────

def test_native_fallback_restates_the_ssrf_guard():
    """`WebFetch` skips `assert_url_safe`; the prompt must carry the rules itself."""
    cap = _capability_section(_fetcher_prompt())
    low = cap.lower()
    assert "ssrf" in low, "fallback does not mention the guard it is bypassing"
    assert "assert_url_safe" in cap, "fallback does not name the choke point it replaces"
    # every range core.fetcher._is_blocked_ip blocks must be spelled out
    for cidr in ("127.0.0.0/8", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
                 "169.254.0.0/16", "::1"):
        assert cidr in cap, f"fallback SSRF rule is missing {cidr}"
    # cloud metadata, IPv4-mapped forms, and loopback-by-name
    assert "169.254.169.254" in cap
    assert "::ffff:" in cap, "IPv4-mapped v6 forms are a documented bypass"
    assert "localhost" in low
    # hostname resolution, not just literal IPs (the DNS-rebinding-ish gap)
    assert "resolves into" in low or "resolves to" in low
    # redirects — safe_redirect_get re-validates every hop, so must the prompt
    assert "redirect" in low
    assert "REFUSE" in cap or "refuse" in low


def test_native_fallback_refuses_non_http_schemes():
    cap = _capability_section(_fetcher_prompt())
    assert "file:" in cap and "gopher:" in cap


def test_degrade_is_announced_not_silent():
    """A report produced without the egress guard must be identifiable."""
    cap = _capability_section(_fetcher_prompt())
    assert "DEGRADED" in cap


def test_cli_path_still_runs_assert_url_safe_before_the_first_byte():
    """The guarantee the prompt is restating is real on the CLI path."""
    import inspect

    from bad_research.cli import vault_cmds

    src = inspect.getsource(vault_cmds._normalize_fetch_result)
    body = src[src.index('"""', src.index('"""') + 3) + 3:]  # drop the docstring
    assert "assert_url_safe(url)" in body
    # ...and it precedes the network call on BOTH branches of that function.
    guard_at = body.index("assert_url_safe(url)")
    assert guard_at < body.index("fetch_tiered(")
    assert guard_at < body.index("fetch_clean(")


# ── 3. note-collision handling in the fallback write ──────────────────────────

def test_native_fallback_carries_the_note_collision_rule():
    cap = _capability_section(_fetcher_prompt())
    assert "-2.md" in cap, "fallback must disambiguate like core.note.write_note"
    low = cap.lower()
    assert "collision" in low
    assert "dedup hit" in low, "same-source rewrite must be skipped, not clobbered"


def test_engine_writer_really_disambiguates(tmp_path):
    """Pins the behavior the prompt is told to mirror."""
    import inspect

    from bad_research.core import note

    src = inspect.getsource(note)
    assert "while file_path.exists()" in src


# ── interim-note fallback must land in research/notes/, not research/temp/ ─────

def test_interim_note_fallback_targets_the_indexed_directory():
    body = hooks.DEPTH_INVESTIGATOR_AGENT.format(hpr_path="bad")
    start = body.index("**Slim-build fallback (`note new` absent):**")
    section = body[start:start + 900]
    assert "research/notes/interim-report-" in section
    # `bad search` only globs research/notes/*.md, so the note itself may not be
    # parked in research/temp/ (which `bad archive-run` also sweeps away).
    assert "interim artifacts may also live under `research/temp/`" not in section
    assert "only globs" in section or "must land in `research/notes/`" in section


def test_search_only_indexes_the_notes_dir():
    """The reason the parenthetical above was wrong."""
    import inspect

    from bad_research.cli import vault_cmds

    src = inspect.getsource(vault_cmds.search_cmd)
    assert 'notes_dir.glob("*.md")' in src
    assert "temp" not in re.sub(r"#.*", "", src).split("notes_dir.glob")[0][-400:]


# ── the caps file is per-run scratch, like every other run artifact ───────────

def test_cli_caps_json_is_archived_between_runs():
    """A stale {"fetch": false} must not pin the next run to the degraded path."""
    assert "cli-caps.json" in _SCRATCH_NAMES
