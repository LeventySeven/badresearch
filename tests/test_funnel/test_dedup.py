from __future__ import annotations

from bad_research.funnel.dedup import dedup
from tests.test_funnel.conftest import FakeWebResult


def _hit(url, content="real body " * 50, rank=1, provider="sonar", title=""):
    return FakeWebResult(url=url, title=title or url, content=content,
                         serp_rank=rank, serp_provider=provider)


def test_collapses_url_variants_to_one_candidate():
    hits = [
        _hit("https://a.com/p"),
        _hit("https://a.com/p/"),       # trailing slash → same
        _hit("https://www.a.com/p#x"),  # www + fragment → same
    ]
    cands = dedup(hits)
    assert len(cands) == 1


def test_collapses_tracking_param_twins_to_one_candidate():
    # Distinct BODIES so only URL-canonical collapse (tracking-param stripping)
    # can merge them — content-hash dedup cannot (bodies differ).
    hits = [
        _hit("https://a.com/p?utm_source=x", content="AAA " * 60),
        _hit("https://a.com/p?utm_source=y", content="BBB " * 60),
        _hit("https://a.com/p", content="CCC " * 60),
    ]
    cands = dedup(hits)
    assert len(cands) == 1


def test_collapses_amp_and_mobile_twins_to_one_candidate():
    hits = [
        _hit("https://a.com/story", content="AAA " * 60),
        _hit("https://amp.a.com/story", content="BBB " * 60),   # amp. subdomain
        _hit("https://m.a.com/story", content="CCC " * 60),     # m. subdomain
        _hit("https://a.com/story/amp", content="DDD " * 60),   # /amp path segment
    ]
    cands = dedup(hits)
    assert len(cands) == 1


def test_collapses_identical_content_under_different_urls():
    same = "the exact same syndicated wire story " * 20
    hits = [
        _hit("https://ap.com/story", content=same),
        _hit("https://reuters-mirror.com/story", content=same),  # mirror, diff URL
        _hit("https://other.com/unique", content="totally different text " * 20),
    ]
    cands = dedup(hits)
    # AP + mirror collapse to 1, the unique page stays → 2
    assert len(cands) == 2


def test_candidate_accumulates_all_provider_ranks():
    # Same URL surfaced by sonar@2 and exa@5 → ONE candidate, BOTH rank lists.
    hits = [
        _hit("https://a.com/p", rank=2, provider="sonar"),
        _hit("https://a.com/p", rank=5, provider="exa"),
    ]
    cands = dedup(hits)
    assert len(cands) == 1
    c = cands[0]
    assert c.provider_ranks == {"sonar": 2, "exa": 5}


def test_keeps_first_seen_webresult_as_representative():
    hits = [_hit("https://a.com/p", title="first"),
            _hit("https://a.com/p/", title="second")]
    cands = dedup(hits)
    assert cands[0].result.title == "first"


def test_empty_input_returns_empty():
    assert dedup([]) == []
