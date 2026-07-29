from __future__ import annotations

from bad_research.funnel.orchestrator import FunnelDeps, gather
from tests.test_funnel.conftest import (
    FakeFetcher,
    FakeProvider,
    FakeRetrievalEngine,
    FakeVault,
    fake_postfetch_filter,
)


def _deps(providers=None, fetcher=None, vault=None, retrieval=None):
    return FunnelDeps(
        providers=providers or [FakeProvider("sonar"), FakeProvider("exa"),
                                FakeProvider("searxng")],
        fetcher=fetcher or FakeFetcher(),
        postfetch_filter=fake_postfetch_filter,
        vault=vault or FakeVault(),
        retrieval=retrieval or FakeRetrievalEngine(),
    )


async def test_gather_returns_only_chunks():
    deps = _deps()
    chunks = await gather("impact of AI on jobs", mode="full", deps=deps)
    assert isinstance(chunks, list)
    assert all(hasattr(c, "chunk_id") and hasattr(c, "text") and hasattr(c, "note_id")
               for c in chunks)


async def test_no_raw_page_body_leaks_into_return():
    # THE invariant: the corpus body lives on disk; the caller never sees it.
    vault = FakeVault()
    deps = _deps(vault=vault)
    chunks = await gather("topic", mode="full", deps=deps)
    # every stored note body is the full raw page; assert NO chunk text equals
    # (or contains the full of) any stored body — chunks are excerpts only.
    full_bodies = list(vault.notes.values())
    assert full_bodies, "precondition: something was stored"
    for c in chunks:
        for body in full_bodies:
            assert c.text != body, "raw page body leaked into a Chunk"
            assert len(c.text) < len(body), "Chunk text is not an excerpt"


async def test_gather_returns_note_id_pointers():
    deps = _deps()
    chunks = await gather("topic", mode="full", deps=deps)
    # every chunk points back to a note_id (the [[note-id]] pointer the model resolves)
    assert all(c.note_id for c in chunks)


async def test_read_ceiling_enforced_end_to_end():
    # Wide fan-out → many candidates → only ≤80 are ever fetched.
    fetcher = FakeFetcher()
    deps = _deps(fetcher=fetcher)
    await gather("topic with lots of sources", mode="full", deps=deps)
    assert len(fetcher.read_urls) <= 80


async def test_rank_runs_before_read():
    # Instrument: the fetcher records read order. The first URLs read must be the
    # top-ranked ones (highest RRF). We seed one clearly-authoritative URL and
    # assert it is read (i.e. survived the rank gate), while a low-utility one is
    # only read if budget remains.
    class TaggedProvider(FakeProvider):
        async def search_ex(self, q):
            from tests.test_funnel.conftest import FakeWebResult
            self.calls.append(q.query)
            # one gov authority hit at rank 1, plus filler
            out = [FakeWebResult(url="https://sec.gov/top", title="SEC filing data",
                                 content="body " * 100, serp_rank=1, serp_provider=self.name)]
            for i in range(q.max_results - 1):
                out.append(FakeWebResult(url=f"https://{self.name}.f/{q.query}/{i}",
                                         title="blog", content="body " * 100,
                                         serp_rank=i + 2, serp_provider=self.name))
            return out

    fetcher = FakeFetcher()
    deps = _deps(providers=[TaggedProvider("sonar")], fetcher=fetcher)
    await gather("financial data", mode="full", deps=deps)
    # The authority URL (surfaced by every query at rank 1, multi-RRF) is read.
    assert "https://sec.gov/top" in fetcher.read_urls


# ---- the pool cap runs AFTER the rank (issue #40) --------------------------

class _LateAuthorityProvider(FakeProvider):
    """Emits 5 distinct low-value hits per query, and the ONE authoritative hit
    only on its LAST query — i.e. last in raw fan-out order."""

    def __init__(self, name, *, n_queries):
        super().__init__(name)
        self._n_queries = n_queries
        self._seen = 0

    async def search_ex(self, q):
        from tests.test_funnel.conftest import FakeWebResult

        self.calls.append(q.query)
        self._seen += 1
        out = []
        if self._seen >= self._n_queries:
            out.append(FakeWebResult(url="https://sec.gov/top", title="SEC filing data",
                                     content="authoritative primary filing " * 40,
                                     serp_rank=1, serp_provider=self.name))
        for i in range(q.max_results):
            n = self._seen * 100 + i
            out.append(FakeWebResult(
                url=f"https://filler{n}.example/p", title="blog",
                content=f"filler {n} body " * 40,
                serp_rank=len(out) + 1, serp_provider=self.name))
        return out


async def test_pool_cap_runs_after_the_rank_not_in_fanout_order():
    # The defect: `candidates[:candidate_pool]` executed BEFORE rank_candidates,
    # so the pool was the FIRST N hits the fan-out happened to return. A
    # top-ranked source emitted by the last query was discarded unscored.
    fetcher = FakeFetcher()
    provider = _LateAuthorityProvider("sonar", n_queries=12)  # light m_queries=12
    deps = _deps(providers=[provider], fetcher=fetcher)
    stats: dict = {}
    await gather("financial data", mode="light", deps=deps, stats=stats)
    assert "https://sec.gov/top" in fetcher.read_urls
    # ...and it was ranked against the WHOLE post-gate pool, not a prefix of it.
    assert stats["n_candidates_prepool"] > stats["n_candidates"]
    assert stats["n_candidates"] == 20                 # light candidate_pool


class _FloodProvider(FakeProvider):
    """4 of every 5 hits come from ONE domain — the 'one loud source owns the
    pool' shape the diversity guard exists to break."""

    async def search_ex(self, q):
        from tests.test_funnel.conftest import FakeWebResult

        self.calls.append(q.query)
        slug = q.query.replace(" ", "_")
        out = []
        for i in range(4):
            out.append(FakeWebResult(
                url=f"https://flood.example/{slug}/{i}", title="flood",
                content=f"flood {slug} {i} body " * 40,
                serp_rank=i + 1, serp_provider=self.name))
        out.append(FakeWebResult(
            url=f"https://other-{slug}.example/p", title="report",
            content=f"other {slug} body " * 40,
            serp_rank=5, serp_provider=self.name))
        return out


async def test_one_domain_cannot_own_the_read_budget():
    fetcher = FakeFetcher()
    deps = _deps(providers=[_FloodProvider("sonar")], fetcher=fetcher)
    await gather("topic", mode="light", deps=deps)
    flood = [u for u in fetcher.read_urls if "flood.example" in u]
    assert len(flood) <= 3                       # cfg.max_per_domain
    assert len(fetcher.read_urls) > len(flood)   # the rest of the budget is spread


async def test_light_mode_smaller_pool_and_no_chain():
    fetcher = FakeFetcher(hub_links={"x": ["y"]})
    deps = _deps(fetcher=fetcher)
    chunks = await gather("simple question", mode="light", deps=deps)
    assert len(fetcher.read_urls) <= 20      # light READ_TOP_K is 12, ceiling 20-ish
    assert isinstance(chunks, list)


async def test_dedup_collapses_duplicate_providers_end_to_end():
    # All three providers return the SAME url template -> heavy URL overlap ->
    # candidate pool collapses; far fewer reads than M*P*K raw hits.
    same_tpl = "https://shared.example/{q}/{i}"
    providers = [FakeProvider(n, url_template=same_tpl) for n in ("a", "b", "c")]
    fetcher = FakeFetcher()
    deps = _deps(providers=providers, fetcher=fetcher)
    await gather("topic", mode="full", deps=deps)
    # 3 providers returned identical URLs per query -> dedup to 1 per (q,i) slot.
    # raw = M*P*K; deduped reads must be roughly M*K (a third), well under raw.
    assert len(fetcher.read_urls) <= 80


async def test_empty_corpus_returns_empty_not_error():
    # Every page is junk → nothing stored → gather returns [] (honest gap, SPEC §13).
    class AllJunk(FakeFetcher):
        async def fetch_tiered(self, url, *, tier_max=1, instruction=None, schema=None):
            from tests.test_funnel.conftest import FakeWebResult
            self.read_urls.append(url)
            return FakeWebResult(url=url, title="x", content="short")  # junk
    deps = _deps(fetcher=AllJunk())
    chunks = await gather("topic", mode="full", deps=deps)
    assert chunks == []
