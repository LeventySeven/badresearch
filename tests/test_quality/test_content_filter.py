"""Tests for Stage-2 post-fetch content filtering (dossier 07 §2)."""

from __future__ import annotations

from datetime import UTC, datetime

from bad_research.quality.content_filter import (
    looks_like_paywall,
    postfetch_filter,
    postfetch_reject_reason,
)
from bad_research.web.base import WebResult


def _wr(content: str, *, url="https://news.example/article", title="Article") -> WebResult:
    return WebResult(url=url, title=title, content=content,
                     fetched_at=datetime(2026, 5, 26, tzinfo=UTC))


_GOOD_BODY = (
    "This is a substantive article about distributed systems. " * 60
)  # well over 1500 chars, no junk markers


def test_looks_like_paywall_detects_metered():
    short = "To continue reading, subscribe to read the full article. " * 3
    assert looks_like_paywall(_wr(short))


def test_looks_like_paywall_ignores_full_article():
    assert not looks_like_paywall(_wr(_GOOD_BODY))


def test_postfetch_filter_keeps_good_article():
    r = postfetch_filter(_wr(_GOOD_BODY))
    assert r is not None
    assert r.content  # passthrough


def test_postfetch_filter_drops_login_wall():
    wall = _wr("Please sign in to your account to view this page.",
               url="https://app.example/login", title="Sign in")
    assert postfetch_filter(wall) is None


def test_postfetch_filter_drops_junk_empty():
    assert postfetch_filter(_wr("tiny")) is None  # < 300 chars -> looks_like_junk


def test_postfetch_filter_drops_paywall():
    short = "Subscribers only. Unlock this article. " * 3
    assert postfetch_filter(_wr(short)) is None


def test_postfetch_reject_reason_keeps_good_article():
    # None == keep (the contract funnel/filter.py:38 relies on: `is None` -> keep).
    assert postfetch_reject_reason(_wr(_GOOD_BODY)) is None


def test_postfetch_reject_reason_names_the_drop_cause():
    wall = _wr("Please sign in to your account to view this page.",
               url="https://app.example/login", title="Sign in")
    assert postfetch_reject_reason(wall) == "login_wall"
    assert postfetch_reject_reason(_wr("tiny")) == "junk"
    # >300 chars (clears the junk floor) but <1500 with a paywall marker -> paywall.
    paywall = "To continue reading, subscribe to read the full article. " * 8
    assert postfetch_reject_reason(_wr(paywall)) == "paywall"


def test_build_postfetch_wires_the_real_filter_not_keep_everything():
    # Regression lock for the silent bug: cli._build_postfetch imported a
    # nonexistent symbol, a bare except swallowed the ImportError, and the funnel
    # kept EVERY page. The callable it returns must actually reject junk.
    from bad_research.cli.research import _build_postfetch

    reject = _build_postfetch(object())
    assert reject(_wr("tiny")) is not None          # junk -> a reason (dropped)
    assert reject(_wr(_GOOD_BODY)) is None           # good  -> None (kept)


def test_postfetch_filter_language_gate_drops_off_language():
    # German body, query_lang='en', no translation requested -> drop
    de = ("Dies ist ein langer deutscher Artikel ueber verteilte Systeme und "
          "Datenbanken und Netzwerke und Programmierung. " * 30)
    assert postfetch_filter(_wr(de), query_lang="en") is None


def test_postfetch_filter_language_gate_off_when_no_query_lang():
    de = ("Dies ist ein langer deutscher Artikel ueber verteilte Systeme. " * 40)
    # query_lang=None disables the gate (default) -> kept
    assert postfetch_filter(_wr(de)) is not None
