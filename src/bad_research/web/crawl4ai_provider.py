"""Crawl4AI web provider — free, open-source, local headless browser, returns clean markdown.

Supports authenticated crawling via crawl4ai browser profiles:
  1. Run `crwl profiles` to create a profile and log in
  2. Set `profile = "profile-name"` in .hyperresearch/config.toml
  3. All fetches now use your authenticated session (cookies, localStorage, etc.)
"""

from __future__ import annotations

import asyncio
import os
import pathlib
import sys
from datetime import UTC, datetime
from typing import Any

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

from bad_research.web.base import WebResult

# Fix Windows encoding before crawl4ai's managed browser tries to log Unicode
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("PYTHONUTF8", "1")
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            try:
                _stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def persist_screenshot(
    conn: Any,
    note_id: str,
    screenshot_bytes: bytes | None,
    assets_dir: pathlib.Path,
    *,
    url: str | None = None,
) -> dict[str, Any] | None:
    """Persist a crawl4ai/Playwright screenshot to disk + the `assets` table.

    The render rung (`_fetch_async` / `_fetch_visible`) already captures PNG bytes
    on `WebResult.screenshot`, but until now NOTHING wrote them anywhere — the host
    model (natively multimodal) could never Read the page as it actually rendered.
    This is the real persistence path: write `research/assets/<note_id>/<sha>.png`
    and INSERT one `type='screenshot'` row, returning a manifest dict (or None when
    there is no screenshot). Failures are swallowed — a missing screenshot never
    aborts a note save.
    """
    if not screenshot_bytes:
        return None
    import hashlib

    from bad_research.core.db import insert_asset

    try:
        assets_dir = pathlib.Path(assets_dir)
        assets_dir.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(screenshot_bytes).hexdigest()[:16]
        filename = f"screenshot-{digest}.png"
        dest = assets_dir / filename
        dest.write_bytes(screenshot_bytes)
        rel = f"research/assets/{note_id}/{filename}"
        insert_asset(
            conn,
            note_id=note_id,
            filename=rel,
            type="screenshot",
            url=url,
            content_type="image/png",
            size_bytes=len(screenshot_bytes),
        )
        return {"path": rel, "type": "screenshot", "bytes": len(screenshot_bytes)}
    except Exception:
        return None


def _is_pdf_url(url: str) -> bool:
    """Check if URL likely points to a PDF."""
    from urllib.parse import urlparse

    parsed = urlparse(url.lower())
    path = parsed.path
    # Direct .pdf links
    if path.endswith(".pdf"):
        return True
    # Common academic PDF patterns
    if "/pdf/" in path or "/pdfs/" in path:
        return True
    # arXiv PDF links
    return "arxiv.org" in parsed.netloc and ("/pdf/" in path or "/abs/" in path)


def _looks_like_binary(text: str) -> bool:
    """Check if extracted 'content' is actually binary garbage from a PDF."""
    if not text:
        return False
    sample = text[:2000]
    # PDF internal structure markers — dead giveaway
    pdf_markers = ("endstream", "endobj", "/Filter", "/FlateDecode", "stream\nx", "%PDF-")
    if any(m in sample for m in pdf_markers):
        return True
    # High ratio of actual binary/control chars - do NOT flag ord(c) > 127, as that would
    # falsely reject valid CJK, Arabic, Cyrillic, and other non-ASCII text.
    # Only flag: true control chars (< 0x20, excluding normal whitespace), the Unicode
    # replacement character (U+FFFD from bad decoding), and C1 controls (0x80-0x9F).
    def _is_garbage(c: str) -> bool:
        o = ord(c)
        return (o < 0x20 and c not in '\t\n\r\f\v') or c == '\ufffd' or (0x80 <= o <= 0x9F)
    garbage = sum(1 for c in sample if _is_garbage(c))
    return garbage > len(sample) * 0.05


def _fetch_pdf(url: str) -> WebResult | None:
    """Download a PDF and extract text using pymupdf. Returns None if extraction fails."""
    try:
        import pymupdf
    except ImportError:
        return None

    import httpx

    from bad_research.core.fetcher import safe_redirect_get

    try:
        # Convert arXiv abs links to PDF links
        if "arxiv.org/abs/" in url:
            url = url.replace("/abs/", "/pdf/")
            if not url.endswith(".pdf"):
                url += ".pdf"

        # follow_redirects=False + manual SSRF-checked hop-following: a PDF URL that
        # 302s to an internal host (e.g. 169.254.169.254 metadata) is refused.
        # verify=False kept for academic PDF hosts with stale certs; redirect hops
        # are SSRF-checked via safe_redirect_get.
        with httpx.Client(follow_redirects=False, timeout=30, verify=False) as client:
            resp = safe_redirect_get(client, url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
        if resp.status_code != 200:
            return None

        content_type = resp.headers.get("content-type", "")
        if "pdf" not in content_type and not url.lower().endswith(".pdf"):
            return None  # Not actually a PDF

        pdf_bytes = resp.content
        if len(pdf_bytes) < 100:
            return None

        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

        # Extract text from all pages
        pages = []
        for page in doc:
            text = page.get_text("text")
            if text.strip():
                pages.append(text)

        doc.close()

        if not pages:
            return None

        # Build markdown from extracted text
        full_text = "\n\n---\n\n".join(pages)
        title = ""
        # Try to get title from first page (first non-empty line)
        for line in pages[0].split("\n"):
            line = line.strip()
            if len(line) > 10:
                title = line
                break

        return WebResult(
            url=url,
            title=title or f"PDF: {url.split('/')[-1]}",
            content=full_text,
            fetched_at=datetime.now(UTC),
            metadata={"content_type": "application/pdf", "pages": len(pages)},
            raw_bytes=pdf_bytes,
            raw_content_type="application/pdf",
        )

    except Exception as e:
        import logging
        logging.getLogger("hyperresearch.pdf").warning(f"PDF extraction failed for {url}: {e}")
        return None


class Crawl4AIProvider:
    name = "crawl4ai"

    def __init__(
        self,
        headless: bool = True,
        user_data_dir: str | None = None,
        profile: str | None = None,
        cookies: list[dict] | None = None,
        magic: bool = False,
        # SECURE BY DEFAULT. This used to default False, so the only caller that
        # got the guard was the one that remembered to ask (fetch_clean.py); the
        # general factory in web/base.py built the provider unguarded, and on
        # that path Chromium followed redirects and loaded subresources with no
        # route handler at all. A security control that is off unless requested
        # is a footgun — the entry URL was checked, then the browser was free to
        # be redirected anywhere, including link-local metadata endpoints.
        ssrf_guard: bool = True,
    ):
        # Resolve profile name to path (crawl4ai stores profiles in ~/.crawl4ai/profiles/)
        data_dir = user_data_dir
        if profile and not data_dir:
            data_dir = str(pathlib.Path.home() / ".crawl4ai" / "profiles" / profile)

        self._data_dir = data_dir
        self._headless = headless
        self._cookies = cookies
        # SSRF guard for the render rung: install a Playwright route handler that aborts
        # any browser request (nav/redirect/sub-resource) to a blocked private/metadata
        # host. Chromium ignores the Python httpx denylist, so this is the only choke
        # point for browser-driven SSRF (dossier 12 §1.3 + INTERFACES_KEYLESS §4.1).
        self._ssrf_guard = ssrf_guard

        browser_kwargs: dict = {"headless": headless}
        if data_dir:
            browser_kwargs["use_managed_browser"] = True
            browser_kwargs["user_data_dir"] = data_dir
        if cookies:
            browser_kwargs["cookies"] = cookies

        self._browser_config = BrowserConfig(**browser_kwargs)

        # Smart wait: 2s initial + poll until content stabilizes (10s ceiling)
        self._wait_js = (
            "js:() => new Promise(r => {"
            "  setTimeout(() => {"
            "    let last = document.body.innerText.length;"
            "    let stable = 0;"
            "    let checks = 0;"
            "    const interval = setInterval(() => {"
            "      const now = document.body.innerText.length;"
            "      if (now === last) { stable++; } else { stable = 0; }"
            "      if (stable >= 2 || checks > 16) { clearInterval(interval); r(true); }"
            "      last = now; checks++;"
            "    }, 500);"
            "  }, 2000);"
            "})"
        )
        # Use PruningContentFilter to populate fit_markdown (strips nav/footer chrome)
        self._md_generator = DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(),
        )
        self._run_config = CrawlerRunConfig(
            magic=magic,
            simulate_user=True,
            screenshot=True,
            page_timeout=30000,
            wait_for=self._wait_js,
            markdown_generator=self._md_generator,
        )

    def fetch(self, url: str) -> WebResult:
        # PDF detection: fetch directly with httpx, extract text with pymupdf
        if _is_pdf_url(url):
            result = _fetch_pdf(url)
            if result is not None:
                return result
            # Fallback to browser if PDF fetch failed (might be a landing page, not actual PDF)

        # When visible + profile: use Playwright directly (crawl4ai managed browser ignores headless=False)
        if not self._headless and self._data_dir:
            return asyncio.run(self._fetch_visible(url))

        result = asyncio.run(self._fetch_async(url))

        # Post-fetch PDF detection: if the browser got binary garbage (PDF served
        # inline without proper content-type handling), re-fetch as a direct PDF download.
        if result.content and _looks_like_binary(result.content):
            pdf_result = _fetch_pdf(url)
            if pdf_result is not None:
                return pdf_result

        return result

    async def _fetch_visible(self, url: str) -> WebResult:
        """Fetch using Playwright directly with a visible browser window.

        crawl4ai's managed browser always forces headless. For sites like LinkedIn
        that detect headless mode and kill sessions, we need a truly visible browser.
        """
        from playwright.async_api import async_playwright

        async with async_playwright() as pw:
            context = await pw.chromium.launch_persistent_context(
                user_data_dir=self._data_dir,
                headless=False,
                viewport={"width": 1280, "height": 900},
                ignore_https_errors=True,
            )
            page = context.pages[0] if context.pages else await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Smart wait — same logic as crawl4ai config
            await page.evaluate("""() => new Promise(r => {
                setTimeout(() => {
                    let last = document.body.innerText.length;
                    let stable = 0;
                    let checks = 0;
                    const interval = setInterval(() => {
                        const now = document.body.innerText.length;
                        if (now === last) { stable++; } else { stable = 0; }
                        if (stable >= 2 || checks > 16) { clearInterval(interval); r(true); }
                        last = now; checks++;
                    }, 500);
                }, 2000);
            })""")

            html = await page.content()
            title = await page.title()
            screenshot_bytes = await page.screenshot(type="png")
            final_url = page.url

            await context.close()

        # Convert HTML to markdown using crawl4ai's markdown generator
        # Prefer fit_markdown (main content, no nav/footer chrome) over raw_markdown.
        md_result = self._md_generator.generate_markdown(html, base_url=final_url)
        content = ""
        if md_result and hasattr(md_result, "fit_markdown"):
            content = md_result.fit_markdown or md_result.raw_markdown or ""
        elif md_result and hasattr(md_result, "raw_markdown"):
            content = md_result.raw_markdown or ""
        elif isinstance(md_result, str):
            content = md_result

        return WebResult(
            url=final_url,
            title=title,
            content=content,
            raw_html=html,
            fetched_at=datetime.now(UTC),
            metadata={"title": title},
            screenshot=screenshot_bytes,
        )

    def _build_ssrf_strategy(self) -> Any:
        """Build an AsyncPlaywrightCrawlerStrategy with the SSRF route hook registered.

        The hook (`fetch_clean._ssrf_on_context_created`) runs `context.route("**/*",
        ...)` on `on_page_context_created`, so every request in the browser context is
        intercepted and aborted if it resolves to a blocked host. One denylist, shared
        with `assert_url_safe` via `core/fetcher.is_blocked_url` (DRY).
        """
        from crawl4ai.async_crawler_strategy import (  # type: ignore[import-untyped]
            AsyncPlaywrightCrawlerStrategy,
        )

        from bad_research.web.content.fetch_clean import _ssrf_on_context_created

        strat = AsyncPlaywrightCrawlerStrategy(browser_config=self._browser_config)
        strat.set_hook("on_page_context_created", _ssrf_on_context_created)
        return strat

    def _make_crawler(self) -> AsyncWebCrawler:
        """AsyncWebCrawler, with the SSRF-gated strategy wired in when ssrf_guard=True."""
        if self._ssrf_guard:
            return AsyncWebCrawler(
                crawler_strategy=self._build_ssrf_strategy(),
                config=self._browser_config,
            )
        return AsyncWebCrawler(config=self._browser_config)

    async def _fetch_async(self, url: str) -> WebResult:
        async with self._make_crawler() as crawler:
            result = await crawler.arun(url=url, config=self._run_config)
            metadata = result.metadata or {}

            # result.markdown is a MarkdownGenerationResult with .raw_markdown,
            # .fit_markdown, .markdown_with_citations, etc.
            # Prefer fit_markdown (main content, no nav/footer chrome) over raw_markdown.
            md = result.markdown
            if md and hasattr(md, "fit_markdown"):
                content = md.fit_markdown or md.raw_markdown or ""
            elif md and hasattr(md, "raw_markdown"):
                content = md.raw_markdown or ""
            elif isinstance(md, str):
                content = md
            else:
                content = ""

            # Extract media (images) — crawl4ai returns dict with 'images' key
            media_raw = result.media or {}
            media = media_raw.get("images", []) if isinstance(media_raw, dict) else []

            # Extract links — crawl4ai returns dict with 'internal'/'external' keys
            links_raw = result.links or {}
            links = []
            if isinstance(links_raw, dict):
                for link in links_raw.get("internal", []):
                    links.append({**link, "type": "internal"})
                for link in links_raw.get("external", []):
                    links.append({**link, "type": "external"})

            # Decode screenshot from base64 if present
            screenshot_bytes = None
            if result.screenshot:
                import base64

                try:
                    screenshot_bytes = base64.b64decode(result.screenshot)
                except Exception:
                    pass

            return WebResult(
                url=result.url or url,
                title=metadata.get("title", ""),
                content=content,
                raw_html=result.html,
                fetched_at=datetime.now(UTC),
                metadata=metadata,
                media=media,
                links=links,
                screenshot=screenshot_bytes,
            )

    def fetch_many(self, urls: list[str]) -> list[WebResult]:
        """Fetch multiple URLs concurrently using crawl4ai's arun_many."""
        return asyncio.run(self._fetch_many_async(urls))

    async def _fetch_many_async(self, urls: list[str]) -> list[WebResult]:
        # Split: PDFs go direct, rest go through browser
        pdf_urls = [u for u in urls if _is_pdf_url(u)]
        html_urls = [u for u in urls if not _is_pdf_url(u)]

        web_results = []

        # Fetch PDFs directly (no browser needed)
        for url in pdf_urls:
            pdf_result = _fetch_pdf(url)
            if pdf_result is not None:
                web_results.append(pdf_result)

        # Fetch HTML pages with browser
        if html_urls:
            async with self._make_crawler() as crawler:
                results = await crawler.arun_many(urls=html_urls, config=self._run_config)
                for cr, url in zip(results, html_urls, strict=False):
                    if not cr.success:
                        continue
                    metadata = cr.metadata or {}
                    md = cr.markdown
                    if md and hasattr(md, "fit_markdown"):
                        content = md.fit_markdown or md.raw_markdown or ""
                    elif md and hasattr(md, "raw_markdown"):
                        content = md.raw_markdown or ""
                    elif isinstance(md, str):
                        content = md
                    else:
                        content = ""

                    # Post-fetch binary check — browser may have fetched a PDF inline
                    if content and _looks_like_binary(content):
                        pdf_result = _fetch_pdf(url)
                        if pdf_result is not None:
                            web_results.append(pdf_result)
                            continue

                    media_raw = cr.media or {}
                    media = media_raw.get("images", []) if isinstance(media_raw, dict) else []

                    screenshot_bytes = None
                    if cr.screenshot:
                        import base64

                        try:
                            screenshot_bytes = base64.b64decode(cr.screenshot)
                        except Exception:
                            pass

                    web_results.append(WebResult(
                        url=cr.url or url,
                        title=metadata.get("title", ""),
                        content=content,
                        raw_html=cr.html,
                        fetched_at=datetime.now(UTC),
                        metadata=metadata,
                        media=media,
                        screenshot=screenshot_bytes,
                    ))
        return web_results

    def search(self, query: str, max_results: int = 5) -> list[WebResult]:
        raise NotImplementedError(
            "crawl4ai does not support web search. "
            "Use your agent's built-in search, then pipe URLs into 'hyperresearch fetch'."
        )


