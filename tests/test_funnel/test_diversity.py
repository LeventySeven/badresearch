"""Stage C.5 — pool diversity guards (issue #40).

The guards only RE-ORDER; `diversify_pool`'s limit is the single cut. These
tests pin that contract, because Stage D reads `ranked[:read_top_k]` — a
candidate's POSITION is what buys it a read.
"""

from __future__ import annotations

from bad_research.funnel.dedup import Candidate
from bad_research.funnel.diversity import cap_per_domain, diversify_pool
from tests.test_funnel.conftest import FakeWebResult


def _c(url, *, providers=("sonar",), rank=1):
    r = FakeWebResult(url=url, title=url, content="body " * 80,
                      serp_rank=rank, serp_provider=providers[0])
    return Candidate(canonical_url=url, result=r,
                     provider_ranks={p: rank for p in providers})


def _urls(cands):
    return [c.url for c in cands]


# ---- cap_per_domain --------------------------------------------------------

def test_cap_per_domain_keeps_at_most_n_from_one_netloc_in_the_head():
    ranked = [_c(f"https://loud.example/{i}") for i in range(5)]
    ranked += [_c("https://other.example/a"), _c("https://third.example/a")]
    out = cap_per_domain(ranked, max_per_domain=3)
    head = out[: len(out) - 2]          # the two demoted loud.example pages
    assert sum(1 for u in _urls(head) if "loud.example" in u) == 3


def test_cap_per_domain_demotes_rather_than_drops():
    # A topic that genuinely lives on ONE host must still fill the pool.
    ranked = [_c(f"https://loud.example/{i}") for i in range(10)]
    out = cap_per_domain(ranked, max_per_domain=3)
    assert len(out) == 10
    assert set(_urls(out)) == set(_urls(ranked))


def test_cap_per_domain_preserves_rank_order_within_head_and_tail():
    ranked = [_c("https://loud.example/1"), _c("https://other.example/a"),
              _c("https://loud.example/2"), _c("https://loud.example/3"),
              _c("https://loud.example/4"), _c("https://loud.example/5")]
    out = cap_per_domain(ranked, max_per_domain=3)
    assert _urls(out) == [
        "https://loud.example/1", "https://other.example/a",
        "https://loud.example/2", "https://loud.example/3",
        # demoted, still in rank order
        "https://loud.example/4", "https://loud.example/5",
    ]


def test_cap_per_domain_exempts_authority_domains():
    # The scholarly verticals all live on ONE host and deliberately bypass the
    # provider cap; capping them at 3 would gut the lane.
    ranked = [_c(f"https://arxiv.org/abs/{i}") for i in range(6)]
    ranked += [_c(f"https://sec.gov/f/{i}") for i in range(4)]
    ranked += [_c(f"https://blog.example/{i}") for i in range(4)]
    out = cap_per_domain(ranked, max_per_domain=3)
    head = out[: len(out) - 1]           # exactly one blog page is demoted
    assert sum(1 for u in _urls(head) if "arxiv.org" in u) == 6
    assert sum(1 for u in _urls(head) if "sec.gov" in u) == 4
    assert sum(1 for u in _urls(head) if "blog.example" in u) == 3


def test_cap_per_domain_disabled_is_identity():
    ranked = [_c(f"https://loud.example/{i}") for i in range(5)]
    assert cap_per_domain(ranked, max_per_domain=0) == ranked


# ---- diversify_pool --------------------------------------------------------

def test_diversify_pool_reserves_head_slots_for_a_low_volume_provider():
    # 30 mainstream hits out-rank a small vertical lane's 4 hits. Without the
    # reservation the vertical is cut entirely by a limit of 10.
    ranked = [_c(f"https://news.example/{i}", providers=("sonar",)) for i in range(30)]
    ranked += [_c(f"https://arxiv.org/abs/{i}", providers=("arxiv",)) for i in range(4)]
    out = diversify_pool(ranked, limit=10, min_per_provider=2)
    assert len(out) == 10
    arxiv = [u for u in _urls(out) if "arxiv.org" in u]
    assert arxiv == ["https://arxiv.org/abs/0", "https://arxiv.org/abs/1"]


def test_diversify_pool_reserves_the_provider_best_not_an_arbitrary_one():
    ranked = [_c(f"https://news.example/{i}", providers=("sonar",)) for i in range(5)]
    ranked.insert(3, _c("https://vert.example/best", providers=("vertical",)))
    ranked.append(_c("https://vert.example/worst", providers=("vertical",)))
    out = diversify_pool(ranked, limit=3, min_per_provider=1)
    assert "https://vert.example/best" in _urls(out)
    assert "https://vert.example/worst" not in _urls(out)


def test_diversify_pool_caps_to_limit_and_keeps_rank_order_of_the_rest():
    ranked = [_c(f"https://news.example/{i}") for i in range(30)]
    out = diversify_pool(ranked, limit=5, min_per_provider=2)
    assert _urls(out) == [f"https://news.example/{i}" for i in range(5)]


def test_diversify_pool_is_a_no_op_below_the_limit():
    ranked = [_c(f"https://news.example/{i}") for i in range(4)]
    assert diversify_pool(ranked, limit=20, min_per_provider=2) == ranked


def test_diversify_pool_zero_limit_returns_empty():
    ranked = [_c("https://news.example/0")]
    assert diversify_pool(ranked, limit=0, min_per_provider=2) == []


def test_diversify_pool_reservations_never_exceed_the_limit():
    # 6 lanes x 2 reserved slots = 12 wanted, but the pool is 4.
    ranked = [_c(f"https://s{n}.example/{i}", providers=(f"p{n}",))
              for n in range(6) for i in range(3)]
    out = diversify_pool(ranked, limit=4, min_per_provider=2)
    assert len(out) == 4


def test_diversify_pool_handles_candidates_with_no_provider_stamp():
    bare = Candidate(canonical_url="https://x.example/a",
                     result=FakeWebResult(url="https://x.example/a"))
    ranked = [bare] + [_c(f"https://news.example/{i}") for i in range(5)]
    out = diversify_pool(ranked, limit=3, min_per_provider=2)
    assert len(out) == 3
