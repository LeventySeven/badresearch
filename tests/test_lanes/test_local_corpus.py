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


# ── the false-EMPTY a cold run manufactured ────────────────────────────────────

def test_a_natural_language_query_is_not_a_false_empty(tmp_path):
    """A question must not report zero over a corpus that plainly matches it.

    Driven cold with the natural-language form the skill's own command block shows,
    this lane returned `selected: 0` over a corpus holding 1,408 matching lines in 87
    files — beside `unreachable_roots: []`, so the output was indistinguishable from a
    healthy lane that is genuinely empty. That is the exact false-EMPTY the lane exists
    to prevent, produced by the lane itself, and EMPTY is the one state that licenses
    "not in corpus".
    """
    (tmp_path / "a.md").write_text(
        "Reranking improved answer quality by 11% on this benchmark.\n"
        "The retriever alone was weaker.\n", encoding="utf-8")
    r = search_local("does reranking improve answer quality", roots=[tmp_path])
    assert r.selected > 0, r.enumeration_line()
    assert r.matched_by in {"all-terms", "any-term"}


def test_a_substring_query_still_matches_as_a_phrase(tmp_path):
    """The cheap rung stays first, so the old behaviour costs exactly what it did."""
    (tmp_path / "a.md").write_text("we rerank with a cross-encoder\n", encoding="utf-8")
    r = search_local("rerank", roots=[tmp_path])
    assert r.selected == 1 and r.matched_by == "phrase"


def test_a_real_zero_names_which_terms_were_absent(tmp_path):
    """An unattributable zero is not reportable — it is what licenses 'not in corpus'."""
    (tmp_path / "a.md").write_text("reranking and retrieval\n", encoding="utf-8")
    r = search_local("zorblax quixotrone", roots=[tmp_path])
    assert r.selected == 0 and r.matched_by == "no-match"
    assert r.per_term_files == {"quixotrone": 0, "zorblax": 0}
    assert "ZERO IS ATTRIBUTABLE" in r.enumeration_line()


def test_present_but_never_together_is_not_an_empty(tmp_path):
    """The distinction the attribution buys: absent words vs words never co-occurring."""
    (tmp_path / "a.md").write_text("reranking is discussed here\nquixotrone lives alone\n",
                                   encoding="utf-8")
    r = search_local("reranking quixotrone", roots=[tmp_path])
    # both terms exist in the file, so this is NOT an empty corpus result
    assert r.per_term_files["reranking"] == 1
    assert r.per_term_files["quixotrone"] == 1
    assert r.selected > 0 and r.matched_by == "any-term"


def test_stopwords_alone_do_not_select_the_whole_corpus(tmp_path):
    """"does the it" must not become a query that matches every line."""
    (tmp_path / "a.md").write_text("the quick brown fox does it\n", encoding="utf-8")
    r = search_local("does the it", roots=[tmp_path])
    assert r.terms == [], f"stopwords survived as terms: {r.terms}"
