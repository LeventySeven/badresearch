"""Research-pipeline CLI subcommands — JSON-out bridges the skills call via Bash.

Each command is a thin wrapper over a deterministic backend seam (router /
funnel / retrieval / grounding). They emit JSON envelopes the skill prompts
parse. Heavy backends (embedder, NLI, web providers) are imported lazily inside
each function so importing this module (and registering the commands) never
pulls in optional deps — a missing backend fails only when its command runs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer

if TYPE_CHECKING:
    from bad_research.grounding.anchors import AnchorStore


# ── route (Task 2/5/12) — deterministic, $0, no heavy deps ───────────────────
def route_cmd(
    decomposition: str = typer.Option(..., "--decomposition"),
    apply: bool = typer.Option(False, "--apply"),
    interactive: bool = typer.Option(False, "--interactive"),
    wrapped: bool = typer.Option(False, "--wrapped"),
    auto: bool = typer.Option(False, "--auto"),
    fast: bool = typer.Option(False, "--fast", help="Force the fast route (override auto)."),
    full: bool = typer.Option(False, "--full", help="Force the full route (override auto)."),
    json_output: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """Classify a Step-1 decomposition into a pipeline route (fast|full).

    Also emits `query_shape` (E12, Claude Research) — the fan-out SHAPE
    (straightforward|breadth_first|depth_first), ORTHOGONAL to the route. The
    shape ADDS the investigator arrangement (single|parallel|sequential); it does
    NOT change the route decision.

    Emits `fanout` — the machine-readable coverage of that shape
    {shape, arrangement, n_subq, cap, k, deferred}. `deferred > 0` means this
    pass covers only `k` of `n_subq` sub-questions and the rest go to the gap
    waves; branch on that key rather than parsing `shape_reason` (issue #36).

    Emits `plan_gate.would_gate` (E11, Gemini collaborative_planning) — whether step
    1.6 should pause to show a plan for approval. It is a SEPARATE gate signal; it
    NEVER changes the route. The flags default OFF, so a run that does NOT pass
    `--interactive` (the eval gate, the test suite, any wrapped/`--auto` run) reports
    `would_gate: false` and flows straight through.
    """
    from bad_research.skills.router import (
        classify_query_shape,
        classify_route,
        fanout_coverage,
        plan_gate_fires,
        route_reason,
        shape_reason,
    )

    path = Path(decomposition)
    decomp = json.loads(path.read_text(encoding="utf-8"))
    route = classify_route(decomp)
    if sum([fast, full]) > 1:
        raise typer.BadParameter("--fast and --full are mutually exclusive")
    if fast:
        route, reason = "fast", "fast: forced by --fast override"
    elif full:
        route, reason = "full", "full: forced by --full override"
    else:
        reason = route_reason(decomp)
    shape = classify_query_shape(decomp)
    would_gate = plan_gate_fires(
        decomp, interactive=interactive, wrapped=wrapped, auto=auto
    )
    if apply:
        decomp["route"] = route
        decomp["query_shape"] = shape
        path.write_text(json.dumps(decomp, indent=2), encoding="utf-8")
    out = {
        "route": route,
        "reason": reason,
        "query_shape": shape,
        "shape_reason": shape_reason(decomp),
        "fanout": fanout_coverage(decomp),
        "applied": apply,
        "plan_gate": {
            "would_gate": would_gate,
            "interactive": interactive,
            "wrapped": wrapped,
            "auto": auto,
        },
    }
    typer.echo(json.dumps(out) if json_output else f"route: {route}  shape: {shape}")


# ── funnel-gather (Task 6/9/12) — the §6 scraper funnel ──────────────────────
def _build_providers(cfg: object) -> list:
    """Keyless web providers for the STANDALONE / CLI funnel path (KR-2).

    The provider order MUST lead with providers that actually return results when the
    funnel runs as a `bad funnel-gather` subprocess. `WebSearchToolProvider`
    wraps Claude Code's *host* WebSearch tool; that tool is invoked by the
    orchestrator (the running agent), NOT by a Python subprocess — its
    `search_ex` raises `NotImplementedError` here. In light mode the funnel
    slices `deps.providers[:cfg.p_providers]` with `p_providers=1`, so a
    host-tool provider sitting at index 0 would starve the whole run (the slice
    would take ONLY the provider that can't run). We therefore lead with the
    keyless HTTP providers — `DdgsProvider` (multi-engine breadth) — so the
    light-mode `[:1]` slice always picks a working lane.

    `WebSearchToolProvider` is still appended LAST so the in-agent path (where a
    `links_source` is wired) can use it, and `fan_out` skips it cleanly when it
    raises `NotImplementedError`. An optional self-host SearXNG is added when
    configured. Every provider is cost_per_search=0.0, zero key. Degrades to []
    on import error."""
    provs: list[Any] = []
    try:
        from bad_research.web.search.base import DdgsProvider, WebSearchToolProvider
    except Exception:
        return []

    # Keyless HTTP breadth lane FIRST — works in a subprocess (real httpx GETs).
    try:
        provs.append(DdgsProvider())
    except Exception:
        pass  # ddgs lib missing → fall through to the other lanes

    # Optional self-host SearXNG (keyless JSON) as an additional breadth lane.
    endpoint = getattr(cfg, "searxng_endpoint", "") or ""
    if endpoint:
        try:
            from bad_research.web.search.base import SearxngProvider

            provs.append(SearxngProvider(endpoint=endpoint))
        except Exception:
            pass

    # Host WebSearch tool adapter LAST: usable on the in-agent path (a wired
    # links_source), harmlessly skipped by fan_out's NotImplementedError guard
    # on the CLI path where the host tool is unreachable.
    try:
        provs.append(WebSearchToolProvider())
    except Exception:
        pass
    return provs


def _build_tiered_fetcher(cfg: object) -> object | None:
    """Keyless 4-rung browse fetcher (KR-4): httpx -> crawl4ai -> silver (read-only)
    -> silver (--enable-actions). No Browserbase/Browser-Use rung. The ladder reads the
    default browse engine from config; the agent-browser engines stay selectable as the
    fallback for machines without silver."""
    try:
        from bad_research.browse.ladder import BrowseEngine, TieredFetcher

        # Normalize to the Literal the ladder accepts; anything unrecognized falls back
        # to the keyless default rather than failing the run.
        configured = getattr(cfg, "browse_engine", "silver")
        engine: BrowseEngine = (
            configured if configured in ("silver", "lightpanda", "chrome") else "silver"
        )
        return TieredFetcher(engine=engine)
    except TypeError:
        # TieredFetcher() may not yet accept engine= on an older KR-4 build.
        from bad_research.browse.ladder import TieredFetcher

        return TieredFetcher()
    except Exception:
        return None


def _build_postfetch(cfg: object) -> object:
    """Post-fetch junk/login/paywall/language filter (Plan 05).

    Returns a ``reject_reason`` callable (``str`` cause to drop, ``None`` to keep) —
    the contract ``funnel/filter.py`` consumes. ``content_filter`` is a core (non-optional)
    dependency, so the import must succeed; if it ever doesn't we log LOUDLY and fall back
    to keep-everything rather than silently shipping an unfiltered corpus (the prior bare
    ``except`` swallowed a real ImportError for a full release — regression-locked by
    ``test_build_postfetch_wires_the_real_filter_not_keep_everything``)."""
    try:
        from bad_research.quality.content_filter import postfetch_reject_reason

        return postfetch_reject_reason
    except Exception as e:  # pragma: no cover - core dep, should never trigger
        import logging

        logging.getLogger("bad_research.cli.research").error(
            "post-fetch content filter unavailable (%s); corpus will NOT be junk-filtered "
            "this run — this is a wiring break, not normal degradation.", e, exc_info=True,
        )
        return lambda r: None


# Base-provider names already covered by _build_providers — never re-add them as a
# "vertical" (ddgs is in the technical route but is already an always-on base provider).
_BASE_PROVIDER_NAMES = frozenset({"ddgs", "searxng", "websearch"})


def _build_vertical_providers(query: str) -> list:
    """Intent-routed keyless scholarly providers for a query (KR-2 §3.3).

    The keyless system's academic edge: an academic/medical/technical query gets the
    matching free scholarly APIs (arXiv/OpenAlex/Crossref/Semantic Scholar/PubMed/Europe
    PMC) fanned ALONGSIDE the generic web providers, instead of silently degrading to
    DuckDuckGo scraping. `detect_intent` is the deterministic regex fallback (the host
    model normally tags intent upstream); `VERTICAL_ROUTES` maps intent → provider names.
    A general-intent query gets no verticals (empty list → funnel behaves exactly as
    before — byte-identical when unused). Each provider is built keyless via get_provider;
    a build failure is skipped, never fatal (the base web providers still carry the run).
    """
    from bad_research.web.base import get_provider
    from bad_research.web.search.route import VERTICAL_ROUTES, detect_intent

    intent = detect_intent(query)
    out: list = []
    for name in VERTICAL_ROUTES.get(intent, []):
        if name in _BASE_PROVIDER_NAMES:
            continue  # already an always-on base provider; don't double-fan it
        try:
            out.append(get_provider(name))
        except Exception:
            continue  # keyless-safe: a provider that can't build never aborts the funnel
    return out


def parse_search_plan(path: str | Path, *, k_per_query: int,
                      max_queries: int | None = None) -> list:
    """Parse the width-sweep skill's search-plan table into SearchQuery seeds.

    Step 2.1 of `bad-research-2-width-sweep.md` has the model hand-write a
    markdown table — `| Atomic item | Search query | Type | Lens | Target |` —
    typically 40-100 rows carrying the lens split (breadth / depth / adversarial /
    period-pinned), the mandated >=5 adversarial searches, and the per-item
    reformulations.

    The query column is located by HEADER NAME, never by a fixed index. Step 2.5
    tells the model to write `research/temp/gap-search-plan.md` with no column
    schema at all, so a hardcoded index 1 read the wrong column and fired the
    literal words "Lens" and "breadth" as searches. A plan with no locatable
    query column yields [] — the caller reports that rather than searching
    garbage.

    This exists because that plan was previously parsed by nobody: the CLI
    declared `--search-plan` and dropped it, so the funnel always fell back to
    `plan_queries`' generic suffix expansion and the model's planning work was
    discarded (issue #35 §4). Malformed rows are skipped rather than fatal — a
    partially-readable plan is still worth more than the fallback.
    """
    from bad_research.web.search.base import SearchQuery

    def _cells(row: str) -> list[str]:
        # Split on UNESCAPED pipes only. A query legitimately containing a pipe
        # (boolean search syntax) is written `\|` per the markdown table
        # convention; a naive split truncated "solar \| wind" to "solar \" and
        # fired that as a real search — silent query corruption.
        return [c.replace("\x00", "|").strip()
                for c in row.strip("|").replace("\\|", "\x00").split("|")]

    def _norm(cell: str) -> str:
        """Header text stripped to bare letters — `**Search query**` -> `searchquery`."""
        return "".join(ch for ch in cell.lower() if ch.isalnum())

    def _is_separator(cells: list[str]) -> bool:
        return all(set(c) <= {"-", ":", " "} and c for c in cells)

    text = Path(path).read_text(encoding="utf-8")
    rows = [_cells(ln.strip()) for ln in text.splitlines() if ln.strip().startswith("|")]

    # Locate the query column from the first row that names it.
    q_idx: int | None = None
    n_cols = 0
    for cells in rows:
        for i, cell in enumerate(cells):
            if _norm(cell) in {"searchquery", "query"}:
                q_idx, n_cols = i, len(cells)
                break
        if q_idx is not None:
            break
    if q_idx is None:
        return []  # no locatable query column — say so, don't guess a column

    out: list = []
    seen: set[str] = set()
    for cells in rows:
        if len(cells) <= q_idx or _is_separator(cells):
            continue
        # A row with MORE cells than the header means an unescaped `|` split one
        # value into several. We can only attribute that surplus to the QUERY
        # column when the query is the LAST column — otherwise the extra pipe is
        # just as likely to sit in a later column, and blindly re-joining would
        # splice that column's text onto the query ("gmv 2026 | breadth"), which
        # is the same silent corruption this handling exists to prevent. When we
        # cannot attribute it, take the query cell verbatim.
        if n_cols and len(cells) > n_cols and q_idx == n_cols - 1:
            q = " | ".join(cells[q_idx:])
        else:
            q = cells[q_idx]
        q = q.strip().strip('"').strip("'").strip()
        if not q or _norm(q) in {"searchquery", "query"} or q in seen:
            continue
        if max_queries is not None and len(out) >= max_queries:
            break
        seen.add(q)
        out.append(SearchQuery(query=q, max_results=k_per_query))
    return out


def run_funnel(query: str, *, mode: str, vault_tag: str,
               search_plan: str | None = None, max_queries: int | None = None,
               read_top_k: int | None = None, concurrency: int | None = None) -> dict:
    """Build FunnelDeps from config + run the FROZEN async gather(), then collapse
    the returned list[Chunk] into a FunnelEnvelope dict. Shared by CLI + MCP.

    `search_plan` (optional): path to the width-sweep skill's plan table. When
    given, its rows become the fan-out seeds verbatim and the deterministic
    `plan_queries` expansion is bypassed entirely — the model's lens plan is
    strictly richer than 16 generic suffixes. `max_queries` caps the plan;
    `read_top_k` overrides the mode's read budget.

    Returns {"note_ids", "top_chunks", "n_read", "n_stored", "ok", "degraded",
    "degraded_reasons", "provider_outcomes"}. The model reads top_chunks only.

    `degraded` is the honest-failure seam — True when the run could not do its
    job. Two reasons, both exit 3:

    - `no_search_provider_available` — every lane refused to run (raised).
      Unambiguous infrastructure failure.
    - `no_search_results_from_any_provider` — every lane RAN and returned zero
      hits across the whole plan (12 queries in light, up to 100 in full).

    The second is deliberately treated as degraded even though it *could* be a
    genuinely sourceless topic. We cannot tell the two apart here, because the
    keyless providers swallow transport errors into [] — so a dead network is
    indistinguishable from a clean empty SERP at this layer. The asymmetry
    decides it: a false "degraded" costs one honest "couldn't build the corpus"
    message, while a false "healthy" ships a report asserting a research gap
    that is really an outage. Zero hits across every lane and every query is
    near-impossible for a well-formed query, so the false-positive rate is low
    and the failure it prevents is the one that silently corrupts output.

    `warnings` is ORTHOGONAL to `degraded`: an `ok: True` run can still carry a
    warning that it did not do what the caller asked (e.g. a supplied search
    plan that could not be parsed, so the deterministic fallback ran instead).
    """
    import asyncio
    from dataclasses import asdict, is_dataclass

    from bad_research.config import BadResearchConfig
    from bad_research.core.vault import Vault
    from bad_research.funnel import gather
    from bad_research.funnel.orchestrator import FunnelDeps
    from bad_research.funnel.store import VaultStore

    cfg = BadResearchConfig.load()
    vault = Vault.discover()
    engine = _build_engine(cfg, vault)
    store = VaultStore(vault, tags=[vault_tag] if vault_tag else [])
    deps = FunnelDeps(
        providers=_build_providers(cfg),
        # Intent-routed scholarly verticals fire alongside the base providers (they
        # bypass the p_providers breadth cap); a general query gets an empty list.
        vertical_providers=_build_vertical_providers(query),
        fetcher=_build_tiered_fetcher(cfg),
        postfetch_filter=_build_postfetch(cfg),
        # Tag every stored note with the run's vault_tag so the corpus survey
        # (`bad search --tag <vault_tag>`) can find the run's corpus.
        vault=store,
        retrieval=engine,
    )
    norm_mode = "full" if mode == "full" else "light"
    from bad_research.funnel.config import FunnelConfig

    fcfg = FunnelConfig.for_mode(norm_mode)
    # The skill's hand-written lens plan wins over deterministic expansion when
    # present (it carries the adversarial/period-pinned lenses the suffix table
    # cannot express); plan_queries stays the fallback for programmatic callers.
    queries = None
    warnings: list[str] = []
    if search_plan:
        queries = parse_search_plan(
            search_plan,
            k_per_query=fcfg.k_per_query,
            # `or` would silently reinterpret an explicit --max-queries 0 as the
            # mode default; only an ABSENT flag falls back.
            max_queries=fcfg.m_queries if max_queries is None else max(1, max_queries),
        ) or None
        if queries is None:
            # A plan was SUPPLIED but yielded nothing parseable. Falling back to
            # the deterministic expansion without saying so would re-create the
            # exact defect this seam exists to remove: the caller believes its
            # 40-100 lens queries ran when 16 generic suffixes did. The run
            # continues (a lost plan shouldn't kill a long job) but the envelope
            # says the plan did not apply, so the orchestrator can fix and retry.
            warnings.append("search_plan_empty_or_unparseable")
    elif max_queries:
        from bad_research.funnel.fanout import plan_queries

        queries = plan_queries(query, m_queries=max_queries, k_per_query=fcfg.k_per_query)

    stats: dict = {}
    chunks = asyncio.run(gather(query, mode=norm_mode, deps=deps, queries=queries,
                                read_budget=read_top_k, stats=stats,
                                concurrency=concurrency))

    note_ids: list[str] = []
    seen: set[str] = set()
    top_chunks: list[dict] = []
    for c in chunks:
        nid = getattr(c, "note_id", None)
        if nid is not None and nid not in seen:
            seen.add(nid)
            note_ids.append(nid)
        top_chunks.append(asdict(c) if is_dataclass(c) else dict(getattr(c, "__dict__", {})))

    # Sources GATHERED = the corpus persisted to the vault this run. Stage F's
    # reranked `top_chunks` are the in-agent model-feed view; its host-model
    # reranker cannot score inside a CLI subprocess, so `note_ids` (chunk-derived)
    # can be empty even when the corpus is full. The stored note ids are the
    # load-bearing output the width-sweep corpus survey reads — surface them so a
    # standalone run honestly reports >0 sources. Union (chunk order first, then
    # any stored note the rerank dropped) keeps the model-relevant ordering.
    stored_ids = getattr(store, "stored_note_ids", [])
    for nid in stored_ids:
        if nid not in seen:
            seen.add(nid)
            note_ids.append(nid)
    # A run is DEGRADED when the machinery failed. `gather` only records a
    # reason when NO lane returned a hit — and with no hits there are no
    # candidates, no pages and no stored notes — so a non-empty corpus and a
    # degraded reason are mutually exclusive by construction. (An earlier
    # `if stored_ids: degraded_reasons = []` override was dead code that would
    # have silently erased a real infrastructure failure had that ever changed.)
    degraded_reasons: list[str] = list(stats.get("degraded_reasons") or [])
    degraded = bool(degraded_reasons)
    return {
        "note_ids": note_ids,
        "top_chunks": top_chunks,
        "n_read": len(note_ids),
        "n_stored": len(stored_ids),
        "ok": not degraded,
        "degraded": degraded,
        "degraded_reasons": degraded_reasons,
        # `warnings` is ORTHOGONAL to `degraded`: a run can succeed (ok:true)
        # while still having silently not done what the caller asked. Folding
        # these into `degraded` would either kill healthy runs or, worse, get
        # cleared the moment sources were found — hiding the very thing the
        # caller needs to know.
        "warnings": warnings,
        "provider_outcomes": stats.get("provider_outcomes", {}),
    }


def funnel_gather_cmd(
    query: str = typer.Argument(None),
    query_file: str = typer.Option(None, "--query-file"),
    search_plan: str = typer.Option(None, "--search-plan"),
    mode: str = typer.Option("light", "--mode"),
    vault_tag: str = typer.Option("", "--vault-tag"),
    max_queries: int = typer.Option(None, "--max-queries"),
    read_top_k: int = typer.Option(None, "--read-top-k"),
    concurrency: int = typer.Option(
        None, "--concurrency",
        help="Max simultaneous provider searches (1-16, default 8). The bounded "
             "answer to issue #36: an uncapped fan-out self-DoSes a keyless scraper.",
    ),
    effort: str = typer.Option(None, "--effort"),
    max_tokens: int = typer.Option(None, "--max-tokens"),
    json_output: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """Run the scraper funnel: fan-out->dedup->rank->read(rung0-3)->filter->chunk->rerank.

    --effort (minimal|low|medium|high) nudges the route + per-stage fan-out
    via skills/router.effort_overrides. --max-tokens is accepted for orchestrator-level
    compatibility but is NOT enforced here — this deterministic funnel does not meter
    tokens; the orchestrator tracks the ceiling in prose (entry skill). Defaults to the
    config's tier behaviour.
    """
    from bad_research.skills.router import effort_overrides

    if query_file:
        q = Path(query_file).read_text(encoding="utf-8")
    elif query:
        q = query
    else:
        raise typer.BadParameter("provide a query argument or --query-file")
    # An explicit --effort pins the route (the OpenAI continuum); else the
    # caller's --mode stands. This wires the previously-ignored stub flag.
    eff_mode = mode
    ov = effort_overrides(effort)
    if ov is not None:
        eff_mode = ov["route"]
    # A fan-out connection/DNS error (unreachable search-provider host), a
    # provider blowup, or any unexpected funnel failure must NOT escape as an
    # uncaught traceback: this command always speaks JSON, so an orchestrator
    # calling it needs a parseable envelope to branch on and a clean non-zero
    # exit — not a stack trace on stdout. (issue #24)
    # STDOUT IS THE MACHINE CONTRACT — keep it JSON-only.
    # crawl4ai's browse rung prints progress to stdout mid-run ("[INIT].... →
    # Crawl4AI 0.8.6", "[FETCH]... ↓ https://…"), so roughly every other real
    # invocation emitted a stream `json.loads` rejects. The skills parse this
    # envelope to branch — and now to read `degraded` — so that chatter was an
    # intermittent hard failure of the whole pipeline. Capture anything a
    # backend writes to stdout and replay it on stderr, where it stays visible
    # for debugging without corrupting the contract.
    import contextlib
    import io
    import sys

    noise = io.StringIO()
    try:
        with contextlib.redirect_stdout(noise):
            result = run_funnel(q, mode=eff_mode, vault_tag=vault_tag,
                                search_plan=search_plan, max_queries=max_queries,
                                read_top_k=read_top_k, concurrency=concurrency)
    except Exception as exc:
        if noise.getvalue():
            print(noise.getvalue(), file=sys.stderr, end="")
        typer.echo(json.dumps({
            "ok": False,
            "error": str(exc),
            "error_type": type(exc).__name__,
            "stage": "funnel-gather",
        }, default=str))
        raise typer.Exit(1) from exc
    if noise.getvalue():
        print(noise.getvalue(), file=sys.stderr, end="")
    typer.echo(json.dumps(result, default=str))
    # A degraded run must not look like success to a shell caller. The envelope
    # still prints (the orchestrator reads `degraded_reasons` to decide whether
    # to stop or retry), but the exit code makes the failure impossible to miss
    # for a plain `&&`-chained script. An honest empty result stays exit 0.
    if result.get("degraded"):
        raise typer.Exit(3)


# ── retrieve (Task 9/12) — hybrid retrieval top-chunks ───────────────────────
def _build_engine(cfg: object, vault: object) -> object:
    """Construct a keyless RetrievalEngine bound to the vault's cache dir. FTS5/BM25
    is the only mandatory index (KR-5); the LanceDB vector lane is wired only when a
    local embedder is present.

    The dense lane is opt-in via `cfg.neural_recall` (the `[local]` extra): when it
    is True, `_build_embedder` returns the bge-small bi-encoder and this constructor
    threads a `lance_dir`; when it is False (the keyless default), the embedder is
    None and retrieval is FTS-only. (The 25k-chunk auto-enable
    `NEURAL_RECALL_VAULT_THRESHOLD` is a vault-size policy not wired in this builder
    — it would belong to the index/vault layer, not the per-call engine factory.)
    """
    from bad_research.retrieval.engine import RetrievalEngine

    root = Path(getattr(vault, "root", Path.cwd()))
    base = root / ".bad-research"
    base.mkdir(parents=True, exist_ok=True)
    embedder = _build_embedder(cfg)
    reranker = _build_reranker(cfg)
    lance_dir = (base / "lance") if embedder is not None else None
    return RetrievalEngine(
        cache_db=base / "semantic_cache.db",
        reranker=reranker,
        embedder=embedder,
        lance_dir=lance_dir,
    )


def _build_embedder(cfg: object) -> object | None:
    """Keyless default: NO embedder (FTS5/BM25-only recall, KR-5). The local
    bi-encoder lane is opt-in: only when config.neural_recall is True (the [local]
    extra). Cohere is GONE."""
    if not getattr(cfg, "neural_recall", False):
        return None
    try:
        from bad_research.embed.base import get_embed_provider

        return get_embed_provider("bge-local")
    except Exception:
        return None


def _build_reranker(cfg: object) -> object:
    """Keyless default reranker = ClaudeCodeReranker (host-model LLM-rerank, KR-5).
    config.reranker selects host|local|light|zerank2|none; the factory resolves it.
    "local"/"light" → ms-marco-MiniLM ([local]); "zerank2" → the zerank-2 opt-in
    ([local], +8.7pp NDCG@10, CC-BY-NC; E14). Cohere is GONE."""
    from bad_research.retrieval.rerank import get_reranker

    return get_reranker(cfg)


def retrieve_cmd(
    query: str = typer.Argument(...),
    mode: str = typer.Option("full", "--mode"),
    top_k: int = typer.Option(20, "--top-k"),
    json_output: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """Keyless retrieval: min-max BM25 recall -> host-model rerank -> 0.70 relevance gate.
    Returns top_k Chunks. (An optional [local] dense lane adds RRF vector+BM25 fusion when
    neural_recall is enabled; the default keyless path is BM25 + rerank, no vector fuse.)"""
    from dataclasses import asdict

    from bad_research.config import BadResearchConfig
    from bad_research.core.vault import Vault

    cfg = BadResearchConfig.load()
    vault = Vault.discover()
    engine = _build_engine(cfg, vault)
    norm_mode = "full" if mode == "full" else "light"
    chunks = engine.search(query, mode=norm_mode, top_k=top_k)
    typer.echo(json.dumps([asdict(c) for c in chunks], default=str))


# ── verify-citations (Task 8/11/12) — backward grounding ─────────────────────
def _verify_report(
    report_path: str, vault_tag: str, *, effort: str | None = None,
    note_bodies_path: str | None = None,
) -> list[dict]:
    """Adapter: load report + AnchorStore + note bodies, run CitationVerifier.

    `effort` is threaded into the verifier (E4): on `effort="high"` the Tier-C
    high-stakes band is decided by the N-sample self-consistency vote rather than the
    single batched judge. None / minimal / low / medium keep the default judge."""
    import sqlite3
    from dataclasses import asdict, is_dataclass

    from bad_research.core.vault import Vault, VaultError
    from bad_research.grounding.anchors import AnchorStore
    from bad_research.grounding.verifier import CitationVerifier, default_nli

    report_md = Path(report_path).read_text(encoding="utf-8")

    # Standalone-safe (mirrors _uncited_gate): a missing vault degrades to an
    # empty in-memory store instead of crashing, and the schema is always
    # auto-initialized so a vault DB that predates the grounding tables (or a
    # fresh in-memory DB) yields "0 anchors" rather than an OperationalError
    # (no such table: claim_anchors) BEFORE the keyless degrade can run.
    note_bodies: dict[str, str]
    if note_bodies_path:
        # Standalone [N] + sources path (mirrors _uncited_gate): seed BOTH note-id and
        # 1-based ordinal anchors so numeric [N] resolves. Without this the store held
        # only note-id anchors, so an inline-[N] + `## Sources` report bound nothing and
        # returned {"results": []} (a no-op — live-run finding).
        note_bodies = json.loads(Path(note_bodies_path).read_text(encoding="utf-8"))
        store = _standalone_store_from_bodies(note_bodies)
    else:
        note_bodies = {}
        try:
            vault = Vault.discover()
            db_path = Path(vault.root) / ".bad-research" / "anchors.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(db_path))
            notes_dir = Path(vault.root) / "research" / "notes"
            if notes_dir.is_dir():
                for f in notes_dir.glob("*.md"):
                    note_bodies[f.stem] = f.read_text(encoding="utf-8")
        except VaultError:
            conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        store = AnchorStore(conn)
        # init_schema is idempotent; safe on an existing populated DB.
        store.init_schema()

    from bad_research.grounding.verifier import LineSpanJudge, nli_available

    # Keyless BY DESIGN (project directive — the host model does inference): this CLI
    # NEVER constructs an API-key'd provider and NEVER reads ANTHROPIC_API_KEY. Tier-A
    # byte-identity + the keyless Tier-B lexical/numeric-negation router (LineSpanJudge)
    # run deterministically; the verifier emits the NEUTRAL band as a
    # `needs_host_judgment` worklist the orchestrator (host model) judges inline (the
    # 11.5 / fast skills apply those dispositions by hand). When the
    # [local] cross-encoder extra is installed, that lane is used instead — still no key.
    nli = default_nli(llm=None) if nli_available() else LineSpanJudge(None)
    verifier = CitationVerifier(nli=nli, llm=None, effort=effort)
    result = verifier.verify(report_md, store, note_bodies)
    findings = getattr(result, "findings", result)
    out = []
    for f in findings:
        out.append(asdict(f) if is_dataclass(f) else dict(getattr(f, "__dict__", {})))
    return out


def verify_citations_cmd(
    report: str = typer.Option(..., "--report"),
    vault_tag: str = typer.Option(..., "--vault-tag"),
    effort: str = typer.Option(
        None, "--effort",
        help="minimal|low|medium|high; 'high' enables the E4 self-consistency vote on "
             "high-stakes (NLI-ambiguous) claims (N host samples; keyless).",
    ),
    note_bodies: str = typer.Option(
        None, "--note-bodies", "--sources",
        help="JSON {note_id: body} map. Resolves `[[note-id]]` by id AND numeric `[N]` by "
             "the N-th key (insertion order) — needed to verify an inline-`[N]` + "
             "`## Sources` report with no pre-populated vault (mirrors uncited-gate).",
    ),
    json_output: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """Run the CitationVerifier over a report. Returns per-sentence dispositions.

    `--effort high` turns on the self-consistency lane (E4): the Tier-C band is decided by
    an N-sample vote (universal self-consistency) instead of the single batched judge.
    Default effort is unchanged (no extra calls). Pass `--note-bodies`/`--sources` to bind
    numeric `[N]` citations standalone (no vault), mirroring `uncited-gate`."""
    typer.echo(json.dumps(
        {"results": _verify_report(report, vault_tag, effort=effort, note_bodies_path=note_bodies)},
        default=str,
    ))


# ── uncited-gate (Task 9/12) — deterministic ship-block, $0 ──────────────────
def _standalone_store_from_bodies(note_bodies: dict[str, str]) -> AnchorStore:
    """An in-memory AnchorStore seeded from `{note_id: body}` — the standalone
    path (no pre-populated vault, mirrors recitation-gate's --note-bodies). Each
    body becomes a verified anchor keyed by BOTH its note_id (so `[[note-id]]`
    wiki-links resolve) AND its 1-based ordinal (so numeric `[N]` resolve — `[1]`
    is the FIRST key in the JSON map's insertion order, `[2]` the second, …). The
    whole body is the quoted_support, so Tier-A byte-identity holds if the
    verifier is ever run over the same store. verified=1: the standalone gate
    treats a provided source as authoritative (its job is "is there a real
    citation", not "did Tier B pass")."""
    import sqlite3

    from bad_research.grounding.anchors import AnchorStore, ClaimAnchor

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    store = AnchorStore(conn)
    store.init_schema()
    for idx, (note_id, body) in enumerate(note_bodies.items(), start=1):
        body = body or ""
        # [[note-id]] anchor: anchor_id is the note_id itself so gate.get(note_id) hits.
        wiki = ClaimAnchor(
            note_id=note_id, char_start=0, char_end=len(body),
            claim="", quoted_support=body, verified=1, anchor_id=note_id,
        )
        store.upsert(wiki)
        # [N] anchor: anchor_id is the 1-based ordinal so gate.get("1") hits. A
        # separate row (distinct PK) pointing at the same note/body.
        numeric = ClaimAnchor(
            note_id=note_id, char_start=0, char_end=len(body),
            claim="", quoted_support=body, verified=1, anchor_id=str(idx),
        )
        store.upsert(numeric)
    return store


def _seed_anchors_from_notes_dir(store: AnchorStore, notes_dir: Path) -> int:
    """Register a verified `[[note-id]]` anchor for each research/notes/<id>.md file
    that the store does not already cover. Returns the number of anchors added.

    This is the file-based-corpus fallback for the uncited-gate (issue #18): a run
    that wrote its sources straight to disk (no funnel DB ingestion) has no
    claim_anchors rows, so a `[[note-id]]` wiki-link to a real note file would
    otherwise read as a dangling-cite. DB anchors remain authoritative — a note id
    already present in the store is left untouched; only genuinely-missing ones are
    seeded (anchor_id == the note id, the whole body as quoted_support, verified=1,
    mirroring _standalone_store_from_bodies' wiki anchor)."""
    from bad_research.grounding.anchors import ClaimAnchor

    if not notes_dir.is_dir():
        return 0
    added = 0
    for f in sorted(notes_dir.glob("*.md")):
        note_id = f.stem
        if store.get(note_id) is not None:
            continue  # DB anchor is authoritative — never overwrite a populated row.
        try:
            body = f.read_text(encoding="utf-8")
        except OSError:
            continue
        store.upsert(ClaimAnchor(
            note_id=note_id, char_start=0, char_end=len(body),
            claim="", quoted_support=body, verified=1, anchor_id=note_id,
        ))
        added += 1
    return added


def _uncited_gate(report_path: str, vault_tag: str, note_bodies_path: str | None) -> list[dict[str, Any]]:
    """Run the deterministic no-uncited-claim gate over the report.

    Standalone-safe: `--note-bodies` (a JSON `{note_id: body}` map) seeds an
    in-memory store with no vault needed; otherwise the vault's anchors.db is
    used. The schema is always auto-initialized so a missing `claim_anchors`
    table yields a clean "0 anchors" result instead of an OperationalError, and a
    missing vault degrades to an empty store rather than crashing."""
    import sqlite3

    from bad_research.grounding.anchors import AnchorStore
    from bad_research.grounding.gate import no_uncited_claim_gate

    report_md = Path(report_path).read_text(encoding="utf-8")

    # Bound in BOTH branches: the --note-bodies path has no vault to read notes
    # from, and leaving it unbound there raises UnboundLocalError downstream.
    notes_dir: Path | None = None

    if note_bodies_path:
        bodies = json.loads(Path(note_bodies_path).read_text(encoding="utf-8"))
        store: AnchorStore = _standalone_store_from_bodies(bodies)
    else:
        # Vault path; if there is no vault (standalone, no --note-bodies), fall
        # back to an empty in-memory store so the gate still runs (every factual
        # sentence reads as uncited, which is the honest answer with no sources).
        from bad_research.core.vault import Vault, VaultError

        try:
            vault = Vault.discover()
            db_path = Path(vault.root) / ".bad-research" / "anchors.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(db_path))
            notes_dir = Path(vault.research_dir) / "notes"
        except VaultError:
            conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        store = AnchorStore(conn)
        # Auto-init: a vault DB that predates the grounding tables (or a fresh
        # in-memory DB) has no claim_anchors table. init_schema is idempotent.
        store.init_schema()
        # File-based fallback (issue #18): a corpus written directly to
        # research/notes/*.md (no funnel DB ingestion) has no claim_anchors rows, so
        # every `[[note-id]]` wiki-link would read as a dangling-cite and the gate —
        # a ship-block — would fail any honest file-based run. Seed a verified anchor
        # for each note file on disk that the DB does NOT already cover, so a cite
        # whose id matches a real notes/<id>.md resolves. DB anchors stay
        # authoritative (we only fill the gaps, never overwrite a populated row).
        if notes_dir is not None:
            _seed_anchors_from_notes_dir(store, notes_dir)

    findings = list(no_uncited_claim_gate(report_md, store))

    # Bare-URL grounding. The uncited gate validates `[N]` markers, so a
    # fabricated URL inside an OTHERWISE-CITED sentence ("according to
    # https://example.com/fake-study [3]") sails through: the sentence IS cited.
    # This checks the URLs themselves against what we actually fetched. Emits
    # `minor`, so it lands in the non-blocking `warnings` channel.
    from bad_research.grounding.gate import ungrounded_url_gate

    known_urls = _known_source_urls(store, notes_dir)
    findings.extend(ungrounded_url_gate(report_md, known_urls))

    return [
        {"sentence": getattr(f, "location", ""), "reason": getattr(f, "failure_mode", "uncited"),
         "severity": getattr(f, "severity", "critical")}
        for f in findings
    ]


def _known_source_urls(store: object, notes_dir: Path | None) -> set[str]:
    """Every URL we actually grounded this run — the allowlist for prose URLs.

    Sourced from the note frontmatter on disk (the file-based path the gate
    already supports) plus any anchor the store carries. Returns an empty set
    when nothing is discoverable, which makes the URL check flag every prose
    URL — deliberately loud rather than silently vacuous.
    """
    urls: set[str] = set()
    if notes_dir is not None and Path(notes_dir).is_dir():
        from bad_research.core.note import read_note

        for path in Path(notes_dir).glob("*.md"):
            try:
                note = read_note(path, Path(notes_dir).parent)
            except Exception:
                continue
            for attr in ("source", "url"):
                val = getattr(note.meta, attr, None)
                if val:
                    urls.add(str(val))
    return urls


def uncited_gate_cmd(
    report: str = typer.Option(..., "--report"),
    vault_tag: str = typer.Option(..., "--vault-tag"),
    note_bodies: str = typer.Option(
        None, "--note-bodies", "--sources",
        help="JSON {note_id: body} map. `[[note-id]]` resolves by id; numeric `[N]` "
             "resolves to the N-th key in insertion order ([1] = first key).",
    ),
    json_output: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """Deterministic ($0) no-uncited-claim ship gate. Non-zero exit when it blocks.

    Standalone (outside Claude Code): pass `--note-bodies`/`--sources` (a JSON
    `{note_id: body}` map) to resolve `[N]`/`[[note-id]]` citations with no
    pre-populated vault — mirrors recitation-gate. Numeric `[N]` resolves
    positionally ([1] = first key in the map). With neither a vault nor
    --note-bodies, the gate auto-inits an empty store (clean "0 anchors")."""
    all_findings = _uncited_gate(report, vault_tag, note_bodies)
    # Blocking = critical + major (the exact set that blocked before this split).
    # `minor` (e.g. the phase-1 non-blocking citation-drift WARNING) is surfaced under
    # `warnings` so it is VISIBLE to the orchestrator/polish but never fails the gate.
    blocking = [f for f in all_findings if f.get("severity") != "minor"]
    warnings = [f for f in all_findings if f.get("severity") == "minor"]
    # `uncited` stays the blocking list (the skill parses it as "things that block");
    # `warnings` is additive and non-blocking.
    typer.echo(json.dumps({"uncited": blocking, "warnings": warnings}))
    if blocking:
        raise typer.Exit(1)


# ── grade-report (Stage 12.5) — in-pipeline grader, single host-model call ────
def grade_report_cmd(
    report: str = typer.Option(..., "--report"),
    corpus: str = typer.Option(..., "--corpus"),
    json_output: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """Grade a report on the 5 axes + emit patcher-shaped findings (Stage 12.5).

    --corpus is a JSON file: a list of {note_id, url, text} dicts (the
    evidence-digest the report had access to). Returns {status:"keyless-skip",
    passed:null, scores, overall, findings} — the orchestrator (host model) grades
    inline via the step-12.5 grader skill, which branches on passed==null.
    """
    # Keyless BY DESIGN (project directive — the host model does inference): grade-report
    # is an LLM-judge loop with no deterministic fallback, so it NEVER constructs an
    # API-key'd provider and NEVER reads ANTHROPIC_API_KEY. It emits the keyless-skip
    # verdict; the orchestrator grades inline via the step-12.5 grader skill (which
    # branches on passed==null and must NOT fall through to an empty-findings patcher
    # spawn), and/or the run relies on the round-1 critic-findings aggregation.
    typer.echo(json.dumps({
        "status": "keyless-skip",
        "passed": None,
        "scores": {},
        "overall": None,
        "findings": [],
        "note": (
            "Keyless run (host does inference): grade inline via the host model "
            "(step 12.5 grader skill) and/or rely on the round-1 critic-findings "
            "aggregation. No API-key'd grader runs in this CLI."
        ),
    }))


# ── recitation-gate (Stage 16) — verbatim-copy detector, $0 deterministic ─────
def recitation_gate_cmd(
    report: str = typer.Option(..., "--report"),
    note_bodies: str = typer.Option(..., "--note-bodies"),
    json_output: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """Deterministic ($0) recitation gate. --note-bodies is a JSON file mapping
    note_id -> body markdown. Flags sentences that copy a source verbatim. A
    `major` finding (NOT a ship-block — unlike uncited-gate); exit 0 always."""
    from bad_research.quality.recitation import recitation_findings

    report_md = Path(report).read_text(encoding="utf-8")
    bodies = json.loads(Path(note_bodies).read_text(encoding="utf-8"))
    findings = recitation_findings(report_md, bodies)
    typer.echo(json.dumps({
        "recitation": [
            {"failure_mode": f.failure_mode, "severity": f.severity,
             "location": f.location, "recommendation": f.recommendation}
            for f in findings
        ]
    }))


__all__ = [
    "funnel_gather_cmd",
    "grade_report_cmd",
    "recitation_gate_cmd",
    "retrieve_cmd",
    "route_cmd",
    "run_funnel",
    "uncited_gate_cmd",
    "verify_citations_cmd",
]
