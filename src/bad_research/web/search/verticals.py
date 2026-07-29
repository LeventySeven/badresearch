"""The 7 keyless scholarly verticals (dossier 13 §8). Each implements the
WebProvider/search_ex surface and returns WebResult with rich metadata
{doi, year, authors, citations, oa_pdf, source, rank, native_score}. KNOWN
endpoints (probed live 2026-05-26 §8.0); DESIGNED mappings (§8.1). All keyless:
no key, no auth header — only a polite User-Agent (+ mailto for the polite pool).
"""

from __future__ import annotations

import time
import xml.etree.ElementTree as ET
from typing import Any

import httpx

from bad_research.web.base import SearchQuery, WebResult, recency_cutoff_date
from bad_research.web.search.status import (
    NO_RESULTS,
    OK,
    RATE_LIMITED,
    classify_search_failure,
    status_for,
)

_UA = "bad-research/keyless (research tool; mailto:{mailto})"
_ATOM = {"a": "http://www.w3.org/2005/Atom"}


def reconstruct_abstract(inv: dict[str, list[int]] | None) -> str:
    """OpenAlex stores abstracts as {word: [positions]} (§8.1(4)). Rebuild text."""
    if not inv:
        return ""
    pairs = [(p, w) for w, ps in inv.items() for p in ps]
    return " ".join(w for _, w in sorted(pairs))


def _client(injected: httpx.Client | None) -> httpx.Client:
    return injected if injected is not None else httpx.Client(timeout=20.0)


class ArxivProvider:
    """KNOWN endpoint export.arxiv.org/api/query (Atom). arXiv is 100% OA."""

    name = "arxiv"
    capabilities = frozenset({"academic", "oa_pdf"})
    cost_per_search = 0.0
    p50_ms = 1200

    BASE = "https://export.arxiv.org/api/query"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client
        self.last_status: str = OK

    def search(self, query: str, max_results: int = 10,
               recency_days: int | None = None) -> list[WebResult]:
        # arXiv supports a submittedDate range filter (keyless, in search_query).
        # When a recency window is set, bound submissions to [cutoff TO now].
        search_query = f"all:{query}"
        cutoff = recency_cutoff_date(recency_days)
        if cutoff is not None:
            lo = cutoff.strftime("%Y%m%d") + "0000"
            search_query = f"{search_query} AND submittedDate:[{lo} TO 99991231235959]"
        params: dict[str, str | int] = {"search_query": search_query, "start": 0,
                                         "max_results": max_results, "sortBy": "relevance"}
        try:
            resp = _client(self._client).get(self.BASE, params=params,
                                             headers={"User-Agent": _UA.format(mailto="")})
            resp.raise_for_status()
            root = ET.fromstring(resp.text)
        except Exception as e:
            # Degrade to [] as before, but record WHY so the funnel can tell a
            # broken scholarly lane from a topic with no literature (issue #39).
            self.last_status = classify_search_failure(e)
            return []
        out: list[WebResult] = []
        for i, e in enumerate(root.findall("a:entry", _ATOM), start=1):
            abs_url = (e.findtext("a:id", default="", namespaces=_ATOM) or "").strip()
            title = " ".join((e.findtext("a:title", default="", namespaces=_ATOM) or "").split())
            summary = (e.findtext("a:summary", default="", namespaces=_ATOM) or "").strip()
            published = e.findtext("a:published", default="", namespaces=_ATOM) or ""
            authors = [a.findtext("a:name", default="", namespaces=_ATOM)
                       for a in e.findall("a:author", _ATOM)]
            pdf = ""
            for link in e.findall("a:link", _ATOM):
                if link.get("title") == "pdf":
                    pdf = link.get("href", "")
            out.append(WebResult(
                url=pdf or abs_url, title=title, content=summary,
                metadata={"source": "arxiv", "rank": i, "year": published[:4] or None,
                          "authors": [a for a in authors if a], "oa_pdf": pdf or None,
                          "doi": None, "citations": None},
            ))
        self.last_status = status_for(out, None)
        return out

    def search_ex(self, q: SearchQuery) -> list[WebResult]:
        return self.search(q.query, max_results=q.max_results,
                           recency_days=q.recency_days)

    def fetch(self, url: str) -> WebResult:  # pragma: no cover - bridges to KR-3
        from bad_research.web.search.base import _fetch_clean_bridge
        return _fetch_clean_bridge(url)


class OpenAlexProvider:
    """KNOWN endpoint api.openalex.org/works. The best all-round academic source."""

    name = "openalex"
    capabilities = frozenset({"academic", "oa_pdf", "citation_graph"})
    cost_per_search = 0.0
    p50_ms = 700

    BASE = "https://api.openalex.org/works"

    def __init__(self, mailto: str = "research@bad-research.local",
                 client: httpx.Client | None = None) -> None:
        self._mailto = mailto
        self._client = client
        self.last_status: str = OK

    def search(self, query: str, max_results: int = 10,
               recency_days: int | None = None) -> list[WebResult]:
        params: dict[str, str | int] = {"search": query, "per_page": max_results, "mailto": self._mailto}
        # OpenAlex keyless date filter: filter=from_publication_date:YYYY-MM-DD.
        cutoff = recency_cutoff_date(recency_days)
        if cutoff is not None:
            params["filter"] = f"from_publication_date:{cutoff.isoformat()}"
        try:
            resp = _client(self._client).get(self.BASE, params=params,
                                             headers={"User-Agent": _UA.format(mailto=self._mailto)})
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            # Degrade to [] as before, but record WHY so the funnel can tell a
            # broken scholarly lane from a topic with no literature (issue #39).
            self.last_status = classify_search_failure(e)
            return []
        out: list[WebResult] = []
        for i, w in enumerate(data.get("results", []) or [], start=1):
            oa = (w.get("open_access") or {}).get("oa_url")
            authors = [(a.get("author") or {}).get("display_name")
                       for a in (w.get("authorships") or [])]
            out.append(WebResult(
                url=oa or w.get("doi") or w.get("id") or "",
                title=w.get("title") or "",
                content=reconstruct_abstract(w.get("abstract_inverted_index")),
                metadata={"source": "openalex", "rank": i,
                          "doi": w.get("doi"), "year": w.get("publication_year"),
                          "authors": [a for a in authors if a],
                          "citations": w.get("cited_by_count"),
                          "oa_pdf": oa, "native_score": w.get("relevance_score")},
            ))
        self.last_status = status_for(out, None)
        return out

    def search_ex(self, q: SearchQuery) -> list[WebResult]:
        return self.search(q.query, max_results=q.max_results,
                           recency_days=q.recency_days)

    def fetch(self, url: str) -> WebResult:  # pragma: no cover
        from bad_research.web.search.base import _fetch_clean_bridge
        return _fetch_clean_bridge(url)


class CrossrefProvider:
    """KNOWN endpoint api.crossref.org/works — the DOI spine (§8.3)."""

    name = "crossref"
    capabilities = frozenset({"academic", "doi_registry"})
    cost_per_search = 0.0
    p50_ms = 900

    BASE = "https://api.crossref.org/works"

    def __init__(self, mailto: str = "research@bad-research.local",
                 client: httpx.Client | None = None) -> None:
        self._mailto = mailto
        self._client = client
        self.last_status: str = OK

    def search(self, query: str, max_results: int = 10,
               recency_days: int | None = None) -> list[WebResult]:
        params: dict[str, str | int] = {"query": query, "rows": max_results, "sort": "relevance"}
        # Crossref keyless date filter: filter=from-pub-date:YYYY-MM-DD.
        cutoff = recency_cutoff_date(recency_days)
        if cutoff is not None:
            params["filter"] = f"from-pub-date:{cutoff.isoformat()}"
        try:
            resp = _client(self._client).get(self.BASE, params=params,
                                             headers={"User-Agent": _UA.format(mailto=self._mailto)})
            resp.raise_for_status()
            items = (resp.json().get("message") or {}).get("items", [])
        except Exception as e:
            # Degrade to [] as before, but record WHY so the funnel can tell a
            # broken scholarly lane from a topic with no literature (issue #39).
            self.last_status = classify_search_failure(e)
            return []
        out: list[WebResult] = []
        for i, it in enumerate(items or [], start=1):
            doi = it.get("DOI")
            title = (it.get("title") or [""])[0]
            authors = [" ".join(x for x in (a.get("given"), a.get("family")) if x).strip()
                       for a in (it.get("author") or [])]
            dp = ((it.get("issued") or {}).get("date-parts") or [[None]])[0]
            out.append(WebResult(
                url=f"https://doi.org/{doi}" if doi else (it.get("URL") or ""),
                title=title, content="",
                metadata={"source": "crossref", "rank": i, "doi": doi,
                          "year": dp[0] if dp else None,
                          "authors": [a for a in authors if a],
                          "citations": it.get("is-referenced-by-count"),
                          "native_score": it.get("score")},
            ))
        self.last_status = status_for(out, None)
        return out

    def search_ex(self, q: SearchQuery) -> list[WebResult]:
        return self.search(q.query, max_results=q.max_results,
                           recency_days=q.recency_days)

    def fetch(self, url: str) -> WebResult:  # pragma: no cover
        from bad_research.web.search.base import _fetch_clean_bridge
        return _fetch_clean_bridge(url)


class SemanticScholarProvider:
    """KNOWN endpoint api.semanticscholar.org/graph/v1 — keyless but throttled
    (§8.0: live probe returned 429). Retry-with-backoff, best-effort, seed-only."""

    name = "s2"
    capabilities = frozenset({"academic", "tldr", "oa_pdf"})
    cost_per_search = 0.0
    p50_ms = 1500

    BASE = "https://api.semanticscholar.org/graph/v1/paper/search"
    FIELDS = "title,year,authors,abstract,tldr,externalIds,citationCount,openAccessPdf"

    def __init__(self, client: httpx.Client | None = None,
                 max_retries: int = 3, backoff_base: float = 2.0) -> None:
        self._client = client
        self._max_retries = max_retries
        self._backoff = backoff_base
        self.last_status: str = OK

    def search(self, query: str, max_results: int = 10) -> list[WebResult]:
        params: dict[str, str | int] = {"query": query, "limit": max_results, "fields": self.FIELDS}
        client = _client(self._client)
        data: dict[str, Any] | None = None
        # The sharpest instance of the whole class of bug (issue #39): S2 is
        # documented as throttled ("live probe returned 429"), the retry loop
        # CONFIRMS the 429, and then the result was thrown into a bare [] that
        # the funnel read as "the scholarly literature has nothing on this".
        failure: str | None = None
        for attempt in range(self._max_retries):
            try:
                resp = client.get(self.BASE, params=params,
                                  headers={"User-Agent": _UA.format(mailto="")})
                if resp.status_code == 429:
                    failure = RATE_LIMITED
                    if attempt + 1 < self._max_retries and self._backoff > 0:
                        time.sleep(self._backoff * (attempt + 1))
                    continue
                resp.raise_for_status()
                data = resp.json()
                failure = None
                break
            except Exception as e:
                self.last_status = classify_search_failure(e)
                return []
        if data is None:
            self.last_status = failure or NO_RESULTS
            return []
        out: list[WebResult] = []
        for i, p in enumerate(data.get("data", []) or [], start=1):
            ext = p.get("externalIds") or {}
            oa = (p.get("openAccessPdf") or {}).get("url")
            tldr = (p.get("tldr") or {}).get("text")
            out.append(WebResult(
                url=oa or (f"https://doi.org/{ext.get('DOI')}" if ext.get("DOI") else ""),
                title=p.get("title") or "",
                content=p.get("abstract") or tldr or "",
                metadata={"source": "s2", "rank": i, "doi": ext.get("DOI"),
                          "year": p.get("year"),
                          "authors": [a.get("name") for a in (p.get("authors") or [])],
                          "citations": p.get("citationCount"), "oa_pdf": oa, "tldr": tldr},
            ))
        self.last_status = status_for(out, None)
        return out

    def search_ex(self, q: SearchQuery) -> list[WebResult]:
        return self.search(q.query, max_results=q.max_results)

    def fetch(self, url: str) -> WebResult:  # pragma: no cover
        from bad_research.web.search.base import _fetch_clean_bridge
        return _fetch_clean_bridge(url)


class EuropePMCProvider:
    """KNOWN endpoint ebi.ac.uk/europepmc — biomedical, one call, structured."""

    name = "europepmc"
    capabilities = frozenset({"medical", "academic"})
    cost_per_search = 0.0
    p50_ms = 1000

    BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client
        self.last_status: str = OK

    def search(self, query: str, max_results: int = 10) -> list[WebResult]:
        params: dict[str, str | int] = {"query": query, "format": "json",
                                         "pageSize": max_results, "resultType": "core"}
        try:
            resp = _client(self._client).get(self.BASE, params=params,
                                             headers={"User-Agent": _UA.format(mailto="")})
            resp.raise_for_status()
            results = ((resp.json().get("resultList") or {}).get("result") or [])
        except Exception as e:
            # Degrade to [] as before, but record WHY so the funnel can tell a
            # broken scholarly lane from a topic with no literature (issue #39).
            self.last_status = classify_search_failure(e)
            return []
        out: list[WebResult] = []
        for i, r in enumerate(results, start=1):
            doi = r.get("doi")
            url = (f"https://doi.org/{doi}" if doi
                   else f"https://europepmc.org/article/{r.get('source')}/{r.get('id')}")
            out.append(WebResult(
                url=url, title=r.get("title") or "",
                content=r.get("abstractText") or "",
                metadata={"source": "europepmc", "rank": i, "doi": doi,
                          "pmid": r.get("pmid"), "pmcid": r.get("pmcid"),
                          "year": r.get("pubYear"),
                          "oa_pdf": None if r.get("isOpenAccess") != "Y" else url},
            ))
        self.last_status = status_for(out, None)
        return out

    def search_ex(self, q: SearchQuery) -> list[WebResult]:
        return self.search(q.query, max_results=q.max_results)

    def fetch(self, url: str) -> WebResult:  # pragma: no cover
        from bad_research.web.search.base import _fetch_clean_bridge
        return _fetch_clean_bridge(url)


class PubMedProvider:
    """KNOWN endpoints eutils esearch+esummary — two-step (§8.1(5))."""

    name = "pubmed"
    capabilities = frozenset({"medical", "academic"})
    cost_per_search = 0.0
    p50_ms = 1100

    ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client
        self.last_status: str = OK

    def search(self, query: str, max_results: int = 10) -> list[WebResult]:
        client = _client(self._client)
        try:
            r1 = client.get(self.ESEARCH, params={"db": "pubmed", "term": query,
                                                   "retmode": "json", "retmax": max_results},
                            headers={"User-Agent": _UA.format(mailto="")})
            r1.raise_for_status()
            ids = (r1.json().get("esearchresult") or {}).get("idlist", [])
            if not ids:
                self.last_status = NO_RESULTS
                return []
            r2 = client.get(self.ESUMMARY, params={"db": "pubmed", "id": ",".join(ids),
                                                    "retmode": "json"},
                            headers={"User-Agent": _UA.format(mailto="")})
            r2.raise_for_status()
            result = r2.json().get("result") or {}
        except Exception as e:
            # Degrade to [] as before, but record WHY so the funnel can tell a
            # broken scholarly lane from a topic with no literature (issue #39).
            self.last_status = classify_search_failure(e)
            return []
        out: list[WebResult] = []
        for i, pmid in enumerate(ids, start=1):
            doc = result.get(pmid) or {}
            year = (doc.get("pubdate") or "")[:4] or None
            out.append(WebResult(
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                title=doc.get("title") or "", content="",
                metadata={"source": "pubmed", "rank": i, "pmid": pmid, "year": year,
                          "authors": [a.get("name") for a in (doc.get("authors") or [])],
                          "journal": doc.get("fulljournalname")},
            ))
        self.last_status = status_for(out, None)
        return out

    def search_ex(self, q: SearchQuery) -> list[WebResult]:
        return self.search(q.query, max_results=q.max_results)

    def fetch(self, url: str) -> WebResult:  # pragma: no cover
        from bad_research.web.search.base import _fetch_clean_bridge
        return _fetch_clean_bridge(url)


class WikipediaProvider:
    """KNOWN endpoints MediaWiki search + REST summary (§8.1(6)). Always-on
    grounding source (low weight in fusion). Wikidata wbsearchentities is used by
    disambiguate() for entity-linking, not as a ranked SERP."""

    name = "wikipedia"
    capabilities = frozenset({"grounding", "entity_link"})
    cost_per_search = 0.0
    p50_ms = 600

    SEARCH = "https://en.wikipedia.org/w/api.php"
    SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client
        self.last_status: str = OK

    def search(self, query: str, max_results: int = 5) -> list[WebResult]:
        client = _client(self._client)
        ua = {"User-Agent": _UA.format(mailto="")}
        try:
            r1 = client.get(self.SEARCH, params={"action": "query", "list": "search",
                                                  "srsearch": query, "format": "json",
                                                  "srlimit": max_results}, headers=ua)
            r1.raise_for_status()
            hits = (r1.json().get("query") or {}).get("search", [])
        except Exception as e:
            # Degrade to [] as before, but record WHY so the funnel can tell a
            # broken scholarly lane from a topic with no literature (issue #39).
            self.last_status = classify_search_failure(e)
            return []
        out: list[WebResult] = []
        for i, h in enumerate(hits, start=1):
            title = h.get("title", "")
            try:
                rs = client.get(self.SUMMARY + title.replace(" ", "_"), headers=ua)
                rs.raise_for_status()
                summ = rs.json()
            except Exception:
                summ = {}
            url = ((summ.get("content_urls") or {}).get("desktop") or {}).get("page") \
                or f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            out.append(WebResult(
                url=url, title=title, content=summ.get("extract") or "",
                metadata={"source": "wikipedia", "rank": i,
                          "wikibase_item": summ.get("wikibase_item")},
            ))
        self.last_status = status_for(out, None)
        return out

    def search_ex(self, q: SearchQuery) -> list[WebResult]:
        return self.search(q.query, max_results=q.max_results)

    def fetch(self, url: str) -> WebResult:  # pragma: no cover
        from bad_research.web.search.base import _fetch_clean_bridge
        return _fetch_clean_bridge(url)
