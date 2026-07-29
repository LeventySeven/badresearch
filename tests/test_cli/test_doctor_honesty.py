"""`doctor` must not claim capability the engine cannot deliver.

Three defects from issue #35 (§2, §6): the active count was summed over the
UNFILTERED provider list so an unconfigured SearXNG was counted while being
hidden from the printed rows; `vault_root` reported the global default even when
`bad init .` had created a vault in CWD; and the host-bridge providers were
reported active in a subprocess where they structurally cannot run.

Grounded: Hermes gates "active" behind a real behavioural probe and carries an
explicit opt-out for providers whose probe lies (HERMES_DEEP_PROVIDERS.md:130,
885). Import-resolves is not the same claim as can-return-a-result.
"""
from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from bad_research.cli import app

runner = CliRunner()


def _doctor(args=None) -> dict:
    res = runner.invoke(app, ["doctor", "-j", *(args or [])])
    assert res.exit_code == 0, res.stdout
    return json.loads(res.stdout)["data"]


def test_active_count_matches_the_listed_providers():
    """The number printed must count the rows actually shown — not hidden ones."""
    data = _doctor()
    listed_active = sum(1 for p in data["providers"] if p["active"])
    assert data["active_count"] == listed_active, (
        "active_count is summed over a different list than `providers` — an "
        "unconfigured searxng is counted but never shown"
    )


def test_unconfigured_searxng_is_not_listed():
    """SearXNG is silent unless configured (INTERFACES_KEYLESS §9)."""
    data = _doctor()
    names = [p["name"] for p in data["providers"]]
    assert "searxng" not in names


def test_host_bridge_providers_are_not_claimed_active_headlessly():
    """`websearch`/`anthropic-host` need a host tool bridge that a subprocess lacks.

    Reporting them active makes `doctor` useless as a capability probe: the
    plugin bootstrap reads it to decide whether the engine can run at all.
    """
    data = _doctor()
    by_name = {p["name"]: p for p in data["providers"]}
    for host_only in ("websearch", "anthropic-host"):
        if host_only in by_name:
            assert by_name[host_only]["active"] is False, (
                f"{host_only} cannot return a result in a subprocess but doctor "
                f"reports it active"
            )


def test_doctor_reports_a_headless_capable_summary():
    """A single field the bootstrap can branch on."""
    data = _doctor()
    assert "headless_capable" in data
    assert isinstance(data["headless_capable"], bool)
    # ddgs is a real keyless HTTP lane and works in a subprocess.
    assert data["headless_capable"] is True


def test_vault_root_reports_the_effective_vault(tmp_path: Path, monkeypatch):
    """`bad init .` makes a vault in CWD; doctor must report THAT one."""
    monkeypatch.chdir(tmp_path)
    init = runner.invoke(app, ["init", ".", "--json"])
    assert init.exit_code == 0, init.stdout
    data = _doctor()
    assert Path(data["vault_root"]).resolve() == tmp_path.resolve(), (
        "doctor reports the global default vault while the effective vault is CWD"
    )
