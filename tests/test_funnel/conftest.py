"""Fakes for the funnel tests — mock every cross-plan seam (Plan 02/03/04/05).

We do NOT import real providers/retrieval/LLM; the funnel composes them behind
seams, and here we substitute deterministic fakes so funnel *logic* is isolated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

import pytest

# ---- WebResult (Plan 03 / hyperresearch web/base.py shape) ----------------
# We mirror the real WebResult fields the funnel touches. The real class lives
# in bad_research.web.base (forked from hyperresearch). For isolation we define
# a structurally identical stand-in; the funnel only uses .url/.title/.content
# and .looks_like_junk()/.looks_like_login_wall().


@dataclass
class FakeWebResult:
    url: str
    title: str = ""
    content: str = ""
    fetched_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict = field(default_factory=dict)
    links: list[dict] = field(default_factory=list)
    # SERP-time signals the rank stage uses (set by FakeProvider.search_ex):
    serp_rank: int = 0          # 1-based rank within this provider's list
    serp_provider: str = ""

    @property
    def domain(self) -> str:
        from urllib.parse import urlparse

        return urlparse(self.url).netloc

    def looks_like_login_wall(self, original_url: str) -> bool:
        return "login" in (self.title or "").lower()

    def looks_like_junk(self, *, min_chars: int = 300) -> str | None:
        if len((self.content or "").strip()) < min_chars:
            return "Empty or near-empty content"
        return None


# ---- SearchQuery (Plan 03 dataclass, INTERFACES.md) -----------------------
@dataclass
class FakeSearchQuery:
    query: str
    intent: Literal["keyword", "neural", "deep"] = "keyword"
    recency_days: int | None = None
    include_domains: list[str] | None = None
    exclude_domains: list[str] | None = None
    max_results: int = 10


# ---- Chunk (Plan 02 dataclass, INTERFACES.md) -----------------------------
@dataclass
class FakeChunk:
    chunk_id: str
    note_id: str
    text: str
    char_start: int
    char_end: int
    score: float
    source_id: str


# ---- WebSearchProvider fake (Plan 03 Protocol) ----------------------------
class FakeProvider:
    """Each provider returns a deterministic, distinct URL list so we can prove
    the union/merge and the parallelism. `calls` records concurrency evidence.
    """

    def __init__(self, name: str, *, latency: float = 0.0,
                 url_template: str = "https://{name}.example/{q}/{i}"):
        self.name = name
        self.capabilities = {"keyword"}
        self.cost_per_search = 0.005
        self.p50_ms = 300
        self._latency = latency
        self._url_template = url_template
        self.calls: list[str] = []        # queries this provider received

    def fetch(self, url: str) -> FakeWebResult:  # not used by the funnel directly
        return FakeWebResult(url=url, title=url, content="x" * 400)

    async def search_ex(self, q) -> list[FakeWebResult]:  # async in the funnel
        import asyncio

        self.calls.append(q.query)
        if self._latency:
            await asyncio.sleep(self._latency)
        out = []
        for i in range(q.max_results):
            url = self._url_template.format(name=self.name, q=q.query.replace(" ", "_"), i=i)
            out.append(FakeWebResult(url=url, title=f"{self.name} {q.query} {i}",
                                     content="body " * 100,
                                     serp_rank=i + 1, serp_provider=self.name))
        return out


# ---- fetch_tiered fake (Plan 04) ------------------------------------------
class FakeFetcher:
    """Records which URLs were read so the ≤80 ceiling can be asserted."""

    def __init__(self, *, junk_urls: set[str] | None = None,
                 hub_links: dict[str, list[str]] | None = None):
        self.read_urls: list[str] = []
        self._junk = junk_urls or set()
        self._hub_links = hub_links or {}

    async def fetch_tiered(self, url: str, *, tier_max: int = 1,
                           instruction=None, schema=None) -> FakeWebResult:
        self.read_urls.append(url)
        if url in self._junk:
            return FakeWebResult(url=url, title="login", content="too short")
        links = [{"href": h, "text": "next"} for h in self._hub_links.get(url, [])]
        return FakeWebResult(url=url, title=f"page {url}", content="real content " * 80,
                             links=links)


# ---- postfetch_filter fake (Plan 05) --------------------------------------
def fake_postfetch_filter(result):
    """Plan 05 contract: returns reason str if junk, None if it passes."""
    return result.looks_like_junk()


# ---- vault / store fake ----------------------------------------------------
class FakeVault:
    """Captures stored notes so we can assert raw text lives on 'disk', not in
    the returned Chunks."""

    def __init__(self):
        self.notes: dict[str, str] = {}   # note_id -> body (the raw page text)
        self._counter = 0

    def store_note(self, *, title: str, body: str, url: str, provider: str) -> str:
        self._counter += 1
        note_id = f"note-{self._counter}"
        self.notes[note_id] = body
        return note_id


# ---- RetrievalEngine fake (Plan 02) ---------------------------------------
class FakeRetrievalEngine:
    """Indexes notes, then 'search' returns Chunks whose text is a short
    excerpt (NOT the full body) with a score; honors top_k and the 0.70 gate."""

    def __init__(self):
        self.indexed: list[tuple[str, str]] = []  # (note_id, body)

    def index(self, notes) -> None:
        # Mirror the REAL RetrievalEngine.index contract: an Iterable[Note]. We
        # read the same fields chunk_note reads (note.meta.id + note.body) so a
        # tuple-vs-Note seam mismatch surfaces here exactly as it would in prod.
        for note in notes:
            self.indexed.append((note.meta.id, note.body))

    def search(self, query: str, *, mode: str, top_k: int) -> list:
        chunks = []
        for rank, (note_id, body) in enumerate(self.indexed):
            score = max(0.0, 0.95 - rank * 0.05)   # descending, deterministic
            if score < 0.70:
                continue
            excerpt = body[:60]                     # a CHUNK, never the full body
            chunks.append(FakeChunk(
                chunk_id=f"{note_id}#0", note_id=note_id, text=excerpt,
                char_start=0, char_end=len(excerpt), score=score, source_id=note_id))
        return chunks[:top_k]


# ---- fixtures --------------------------------------------------------------
@pytest.fixture
def providers():
    return [FakeProvider("sonar"), FakeProvider("exa"), FakeProvider("searxng")]


@pytest.fixture
def fetcher():
    return FakeFetcher()


@pytest.fixture
def vault():
    return FakeVault()


@pytest.fixture
def retrieval():
    return FakeRetrievalEngine()
