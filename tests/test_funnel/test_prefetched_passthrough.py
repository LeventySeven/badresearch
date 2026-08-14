"""Prefetched candidates keep the body their provider already read.

The social lane returns content-complete results (the thread, its top comments,
the transcript). Re-fetching a reddit.com or x.com permalink anonymously returns
a login wall, which Stage E drops as junk — so a re-fetch would gather the
evidence and discard it one stage later. Stage D passes those through; Stage E
does not apply its post-FETCH junk rules to them.
"""

from __future__ import annotations

from bad_research.funnel.dedup import Candidate, dedup
from bad_research.funnel.filter import filter_and_store
from bad_research.funnel.read import read_top_k
from bad_research.quality.content_filter import postfetch_reject_reason
from bad_research.web.base import WebResult
from tests.test_funnel.conftest import FakeFetcher, FakeVault, FakeWebResult, fake_postfetch_filter


def _hit(url, *, provider, rank=1, content="snippet", prefetched=False):
    """A raw fan-out hit, as one provider's SERP produced it."""
    return FakeWebResult(
        url=url, title=url, content=content, serp_provider=provider, serp_rank=rank,
        metadata={"prefetched": True} if prefetched else {},
    )


def _cand(url, *, prefetched=False, content="snippet", title=""):
    meta = {"prefetched": True} if prefetched else {}
    return Candidate(
        canonical_url=url,
        result=FakeWebResult(url=url, title=title, content=content, metadata=meta),
        provider_ranks={"last30days" if prefetched else "ddgs": 1},
    )


# ── Stage B — the merge must not throw the prefetched body away ───────────
#
# Base lanes run BEFORE the verticals (orchestrator: providers[:p] + verticals),
# so for any popular thread ddgs sees the URL first and dedup kept the FIRST-seen
# representative — the snippet. The prefetched body was dropped, Stage D fetched
# the permalink anyway, and Stage E junked the login wall.


def test_dedup_keeps_the_prefetched_body_when_a_base_lane_saw_the_url_first():
    url = "https://www.reddit.com/r/x/comments/9/"
    body = "u/someone: it broke my fine-tunes (1,485 upvotes)"
    cands = dedup([
        _hit(url, provider="ddgs", rank=3, content="Reddit - the front page…"),
        _hit(url, provider="last30days", rank=1, content=body, prefetched=True),
    ])
    assert len(cands) == 1
    assert cands[0].result.content == body
    assert cands[0].result.metadata["prefetched"] is True
    # the swap keeps every SERP signal both lanes contributed
    assert cands[0].provider_ranks == {"ddgs": 3, "last30days": 1}
    assert cands[0].provider_rank_lists == {"ddgs": [3], "last30days": [1]}


def test_dedup_does_not_swap_when_the_incumbent_is_already_prefetched():
    url = "https://news.ycombinator.com/item?id=2"
    cands = dedup([
        _hit(url, provider="last30days", rank=1, content="the thread", prefetched=True),
        _hit(url, provider="ddgs", rank=2, content="a snippet"),
    ])
    assert cands[0].result.content == "the thread"


def test_dedup_without_a_prefetched_sibling_is_unchanged():
    # First-seen still wins for ordinary hits — this path must stay byte-identical.
    url = "https://blog.example/post"
    cands = dedup([
        _hit(url, provider="ddgs", rank=1, content="first"),
        _hit(url, provider="websearch", rank=2, content="second"),
    ])
    assert cands[0].result.content == "first"


async def test_prefetched_candidate_is_not_fetched():
    ranked = [_cand("https://www.reddit.com/r/x/comments/1/", prefetched=True)]
    fetcher = FakeFetcher()
    results = await read_top_k(ranked, fetcher=fetcher, read_top_k=80, concurrency=4,
                               max_chain_depth=0, max_links_per_hub=0)
    assert fetcher.read_urls == []                       # no HTTP call at all
    assert [r.url for r in results] == ["https://www.reddit.com/r/x/comments/1/"]


async def test_prefetched_body_survives_verbatim():
    body = "u/someone: it broke my fine-tunes (1,485 upvotes)"
    ranked = [_cand("https://www.reddit.com/r/x/comments/2/", prefetched=True, content=body)]
    results = await read_top_k(ranked, fetcher=FakeFetcher(), read_top_k=80, concurrency=4,
                               max_chain_depth=0, max_links_per_hub=0)
    assert results[0].content == body


async def test_normal_candidates_are_still_fetched():
    ranked = [_cand("https://blog.example/post")]
    fetcher = FakeFetcher()
    await read_top_k(ranked, fetcher=fetcher, read_top_k=80, concurrency=4,
                     max_chain_depth=0, max_links_per_hub=0)
    assert fetcher.read_urls == ["https://blog.example/post"]


async def test_mixed_pool_reads_only_the_unfetched_half():
    ranked = [
        _cand("https://www.reddit.com/r/x/comments/3/", prefetched=True),
        _cand("https://blog.example/a"),
        _cand("https://news.ycombinator.com/item?id=1", prefetched=True),
        _cand("https://blog.example/b"),
    ]
    fetcher = FakeFetcher()
    results = await read_top_k(ranked, fetcher=fetcher, read_top_k=80, concurrency=4,
                               max_chain_depth=0, max_links_per_hub=0)
    assert sorted(fetcher.read_urls) == ["https://blog.example/a", "https://blog.example/b"]
    assert len(results) == 4                              # all four reach Stage E


async def test_prefetched_still_spends_the_read_budget():
    # The budget bounds how much content enters the corpus, not how many HTTP
    # calls we make — otherwise a social-heavy pool silently blows past the ceiling.
    ranked = [_cand(f"https://s{i}.example/p", prefetched=True) for i in range(10)]
    results = await read_top_k(ranked, fetcher=FakeFetcher(), read_top_k=4, concurrency=4,
                               max_chain_depth=0, max_links_per_hub=0)
    assert len(results) == 4


def test_stage_e_does_not_junk_filter_a_short_prefetched_body():
    # 200 chars of Reddit comment is short on purpose; the <300 rule exists to
    # catch a FAILED FETCH, and nothing was fetched here.
    short = FakeWebResult(url="https://www.reddit.com/r/x/comments/4/", title="t",
                          content="short but load-bearing", metadata={"prefetched": True})
    assert fake_postfetch_filter(short) is not None       # the filter WOULD drop it
    vault = FakeVault()
    stored = filter_and_store([short], vault=vault, postfetch_filter=fake_postfetch_filter,
                              redundancy_overlap=0.7, shingle_n=3)
    assert len(stored) == 1                               # kept anyway


# The bypass waives the LENGTH rule, not the content floor. These run the REAL
# WebResult + the REAL reject-reason filter the CLI wires in, because the point
# is which of its rules survive for a body nobody fetched.


def _real(url, title, content, *, prefetched=True):
    return WebResult(url=url, title=title, content=content,
                     metadata={"prefetched": True} if prefetched else {})


def test_stage_e_still_drops_an_empty_prefetched_body():
    # The engine documents `summary` as possibly empty; an empty body is exempt
    # from the content-hash collapse, so it used to reach the vault as a
    # zero-byte note — a citable source with nothing in it.
    empty = _real("https://www.reddit.com/r/x/comments/5/", "a thread", "")
    stored = filter_and_store([empty], vault=FakeVault(),
                              postfetch_filter=postfetch_reject_reason,
                              redundancy_overlap=0.7, shingle_n=3)
    assert stored == []


def test_stage_e_still_drops_a_prefetched_bot_wall():
    wall = _real("https://www.reddit.com/r/x/comments/6/", "Just a moment...",
                 "Checking your browser before accessing. Ray ID: 8b2. Enable "
                 "JavaScript and cookies to continue.")
    stored = filter_and_store([wall], vault=FakeVault(),
                              postfetch_filter=postfetch_reject_reason,
                              redundancy_overlap=0.7, shingle_n=3)
    assert stored == []


def test_stage_e_still_drops_prefetched_binary_garbage():
    garbage = _real("https://www.reddit.com/r/x/comments/7/", "paper.pdf",
                    "%PDF-1.4 endobj /FlateDecode endstream")
    stored = filter_and_store([garbage], vault=FakeVault(),
                              postfetch_filter=postfetch_reject_reason,
                              redundancy_overlap=0.7, shingle_n=3)
    assert stored == []


def test_stage_e_keeps_a_short_real_prefetched_body():
    # Same filter, same page shape — only the <300-char rule is waived.
    good = _real("https://www.reddit.com/r/x/comments/8/", "the thread",
                 "u/someone: it broke my fine-tunes")
    stored = filter_and_store([good], vault=FakeVault(),
                              postfetch_filter=postfetch_reject_reason,
                              redundancy_overlap=0.7, shingle_n=3)
    assert len(stored) == 1


def test_stage_e_still_junk_filters_a_short_fetched_body():
    short = FakeWebResult(url="https://blog.example/thin", title="t", content="thin")
    stored = filter_and_store([short], vault=FakeVault(), postfetch_filter=fake_postfetch_filter,
                              redundancy_overlap=0.7, shingle_n=3)
    assert stored == []


# --- the junk floor must not invert against community text -------------------
# Lowering the length floor to 1 let every remaining rule judge a body nobody
# fetched. Two of them then ate genuine evidence, both measured before the fix.

def _thread(title: str, body: str):
    from bad_research.web.base import WebResult

    return WebResult(url="https://www.reddit.com/r/x/comments/1/", title=title, content=body)


def _prefetched_reason(page):
    """Exactly what funnel/filter.py asks of a body nobody fetched."""
    return page.looks_like_junk(min_chars=1)


def test_a_non_latin_thread_is_not_binary_garbage():
    # `ord(c) > 127` counted every Cyrillic/CJK/emoji char as non-printable, so a
    # source more than 15% non-ASCII was discarded — in a research tool.
    assert _prefetched_reason(_thread("тред", "Это длинный тред про файнтюны. " * 20)) is None
    assert _prefetched_reason(_thread("スレ", "これは日本語のスレッドです。" * 40)) is None
    assert _prefetched_reason(_thread("t", "🔥 this broke my fine-tunes 😤 " * 30)) is None


def test_real_junk_still_dies_on_the_prefetched_path():
    assert _prefetched_reason(_thread("t", "")) is not None                       # empty
    assert _prefetched_reason(_thread("t", "endstream endobj %PDF- " * 20)) is not None  # pdf
    assert _prefetched_reason(_thread("t", "\x00\x01\x02\x03" * 300)) is not None  # control bytes
    assert _prefetched_reason(_thread("t", "�" * 300)) is not None            # mojibake


def test_the_fetched_path_is_completely_unchanged():
    # The non-printable fix must not weaken any rule a fetched page is judged by.
    wall = _thread("Just a moment...", "Checking your browser before accessing. Ray ID: abc. " * 10)
    err = _thread("404 Not Found", "The page you requested could not be located. " * 15)
    assert wall.looks_like_junk() == "Bot detection page: Just a moment..."
    assert err.looks_like_junk() == "Error page: 404 Not Found"
