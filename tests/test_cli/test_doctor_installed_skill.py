"""`bad doctor` reports whether the installed skill is the one this version would install.

The source tree moved for two weeks while ~/.claude kept an older skill, and nothing said so.
"""

from pathlib import Path

from bad_research.cli.doctor import _installed_skill_status
from bad_research.core.hooks import install_global_hooks


def test_not_installed(tmp_path: Path) -> None:
    assert _installed_skill_status(tmp_path)["status"] == "not-installed"


def test_fresh_install_is_current(tmp_path: Path) -> None:
    install_global_hooks(home=tmp_path)
    assert _installed_skill_status(tmp_path) == {"status": "current", "differs": []}


def test_edited_or_missing_file_is_stale(tmp_path: Path) -> None:
    install_global_hooks(home=tmp_path)
    skill = tmp_path / ".claude" / "skills" / "bad-research"
    (skill / "SKILL.md").write_text("an older skill\n")
    (tmp_path / ".claude" / "agents" / "research-reader.md").unlink()
    st = _installed_skill_status(tmp_path)
    assert st["status"] == "stale"
    assert "skills/bad-research/SKILL.md" in st["differs"]
    assert "agents/research-reader.md" in st["differs"]


def test_no_skill_source_is_unknown_not_current(tmp_path: Path, monkeypatch) -> None:
    install_global_hooks(home=tmp_path)
    import bad_research.cli.doctor as doctor_mod
    import bad_research.core.hooks as hooks_mod

    def no_skill_install(home=None, hpr_path="bad"):
        (home / ".claude" / "agents").mkdir(parents=True, exist_ok=True)
        return []

    monkeypatch.setattr(hooks_mod, "install_global_hooks", no_skill_install)
    assert doctor_mod._installed_skill_status(tmp_path)["status"] == "unknown"
