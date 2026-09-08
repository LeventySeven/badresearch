from __future__ import annotations

from bad_research.lanes.local_corpus import search_local


def test_returns_path_line_hits(tmp_path):
    d = tmp_path / "teardowns"
    d.mkdir()
    (d / "a.md").write_text("line one\ndeep research agent loop\n")
    r = search_local("deep research", roots=[d])
    assert r.selected == 1
    assert r.hits[0].line == 2 and r.hits[0].path.endswith("a.md")


def test_enumeration_line_emitted_even_at_zero(tmp_path):
    d = tmp_path / "teardowns"
    d.mkdir()
    (d / "a.md").write_text("nothing here\n")
    r = search_local("absent-term", roots=[d])
    assert r.selected == 0
    assert r.enumeration_line().startswith("local-corpus | files listed 1 |")


def test_never_recurses(tmp_path):
    d = tmp_path / "teardowns"
    (d / "vendor").mkdir(parents=True)
    (d / "vendor" / "b.md").write_text("deep research\n")
    assert search_local("deep research", roots=[d]).selected == 0


def test_missing_root_is_reported_not_silently_skipped(tmp_path):
    r = search_local("x", roots=[tmp_path / "does-not-exist"])
    assert "unreachable" in r.enumeration_line()


def test_cap_is_reported_in_the_cut_line(tmp_path):
    d = tmp_path / "teardowns"
    d.mkdir()
    (d / "a.md").write_text("hit\n" * 7)
    r = search_local("hit", roots=[d], limit=3)
    assert r.selected == 3
    assert r.cut_line == "capped at 3 of 7 matches"
    assert "cut line capped at 3 of 7 matches" in r.enumeration_line()


def test_uncapped_run_says_no_cap_applied(tmp_path):
    d = tmp_path / "teardowns"
    d.mkdir()
    (d / "a.md").write_text("hit\n")
    assert search_local("hit", roots=[d]).cut_line == "no cap applied"


def test_unreadable_file_is_counted_not_crashed_on(tmp_path):
    d = tmp_path / "teardowns"
    d.mkdir()
    (d / "good.md").write_text("deep research\n")
    (d / "bad.md").write_bytes(b"\xff\xfe deep research\n")
    r = search_local("deep research", roots=[d])
    assert r.files_listed == 2
    assert r.selected == 1
    assert "1 file(s) unreadable" in r.cut_line


def test_match_is_case_insensitive(tmp_path):
    d = tmp_path / "teardowns"
    d.mkdir()
    (d / "a.md").write_text("Multi-Agent Pipeline\n")
    assert search_local("multi-agent", roots=[d]).selected == 1


def test_non_markdown_and_subdirectory_names_are_not_read(tmp_path):
    d = tmp_path / "teardowns"
    d.mkdir()
    (d / "a.txt").write_text("deep research\n")
    (d / "sub.md").mkdir()
    r = search_local("deep research", roots=[d])
    assert r.files_listed == 0 and r.selected == 0


def test_default_roots_are_used_when_none_given(tmp_path, monkeypatch):
    from bad_research.lanes import local_corpus

    d = tmp_path / "teardowns"
    d.mkdir()
    (d / "a.md").write_text("deep research\n")
    monkeypatch.setattr(local_corpus, "DEFAULT_ROOTS", (d, tmp_path / "gone"))
    r = search_local("deep research")
    assert r.selected == 1
    assert r.unreachable_roots == [str(tmp_path / "gone")]
