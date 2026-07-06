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
    ultrafast: bool = typer.Option(
        False, "--ultrafast",
        help="Force the ultrafast route (commercial-DR middle tier; override auto).",
    ),
    json_output: bool = typer.Option(False, "--json", "-j"),
) -> None:
    """Classify a Step-1 decomposition into a pipeline route (fast|full|ultrafast).

    Also emits `query_shape` (E12, Claude Research) — the fan-out SHAPE
    (straightforward|breadth_first|depth_first), ORTHOGONAL to the route. The
    shape ADDS the investigator arrangement (single|parallel|sequential); it does
    NOT change the route decision.

    Emits `plan_gate.would_gate` (E11, Gemini collaborative_planning) — whether step
    1.6 should pause to show a plan for approval. It is a SEPARATE gate signal; it
    NEVER changes the route. The flags default OFF, so a run that does NOT pass
    `--interactive` (the eval gate, the test suite, any wrapped/`--auto` run) reports
    `would_gate: false` and flows straight through.
    """
    from bad_research.skills.router import (
        classify_query_shape,
        classify_route,
        plan_gate_fires,
        route_reason,
        shape_reason,
    )

    path = Path(decomposition)
    decomp = json.loads(path.read_text(encoding="utf-8"))
    route = classify_route(decomp)
    if sum([fast, full, ultrafast]) > 1:
        raise typer.BadParameter("--fast, --full, and --ultrafast are mutually exclusive")
    if fast:
        route, reason = "fast", "fast: forced by --fast override"
    elif full:
        route, reason = "full", "full: forced by --full override"
    elif ultrafast:
        route, reason = "ultrafast", "ultrafast: forced by --ultrafast override (commercial-DR middle tier)"
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
    """Keyless 4-rung browse fetcher (KR-4): httpx -> crawl4ai -> agent-browser
    (lightpanda) -> agent-browser (chrome). No Browserbase/Browser-Use rung.
    The ladder reads the default browse engine from config."""
    from typing import Literal

    try:
        from bad_research.browse.ladder import TieredFetcher

        # Normalize to the Literal the ladder accepts; any non-"chrome" value
        # defaults to lightpanda (the keyless rung-2.5 default, dossier 14 §12.5).
        engine: Literal["lightpanda", "chrome"] = (
            "chrome" if getattr(cfg, "browse_engine", "lightpanda") == "chrome" else "lightpanda"
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


def run_funnel(query: str, *, mode: str, vault_tag: str) -> dict:
    """Build FunnelDeps from config + run the FROZEN async gather(), then collapse
    the returned list[Chunk] into a FunnelEnvelope dict. Shared by CLI + MCP.

    Returns {"note_ids", "top_chunks", "n_read"}. The model reads top_chunks only.
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
        fetcher=_build_tiered_fetcher(cfg),
        postfetch_filter=_build_postfetch(cfg),
        # Tag every stored note with the run's vault_tag so the corpus survey
        # (`bad search --tag <vault_tag>`) can find the run's corpus.
        vault=store,
        retrieval=engine,
    )
    norm_mode = "full" if mode == "full" else "light"
    chunks = asyncio.run(gather(query, mode=norm_mode, deps=deps))

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
    return {
        "note_ids": note_ids,
        "top_chunks": top_chunks,
        "n_read": len(note_ids),
        "n_stored": len(stored_ids),
    }


def funnel_gather_cmd(
    query: str = typer.Argument(None),
    query_file: str = typer.Option(None, "--query-file"),
    search_plan: str = typer.Option(None, "--search-plan"),
    mode: str = typer.Option("light", "--mode"),
    vault_tag: str = typer.Option("", "--vault-tag"),
    max_queries: int = typer.Option(None, "--max-queries"),
    read_top_k: int = typer.Option(None, "--read-top-k"),
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
    try:
        result = run_funnel(q, mode=eff_mode, vault_tag=vault_tag)
    except Exception as exc:
        typer.echo(json.dumps({
            "ok": False,
            "error": str(exc),
            "error_type": type(exc).__name__,
            "stage": "funnel-gather",
        }, default=str))
        raise typer.Exit(1) from exc
    typer.echo(json.dumps(result, default=str))


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
    # 11.5 / fast / ultrafast skills apply those dispositions by hand). When the
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

    if note_bodies_path:
        bodies = json.loads(Path(note_bodies_path).read_text(encoding="utf-8"))
        store: AnchorStore = _standalone_store_from_bodies(bodies)
    else:
        # Vault path; if there is no vault (standalone, no --note-bodies), fall
        # back to an empty in-memory store so the gate still runs (every factual
        # sentence reads as uncited, which is the honest answer with no sources).
        from bad_research.core.vault import Vault, VaultError

        notes_dir: Path | None = None
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

    findings = no_uncited_claim_gate(report_md, store)
    return [
        {"sentence": getattr(f, "location", ""), "reason": getattr(f, "failure_mode", "uncited")}
        for f in findings
    ]


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
    uncited = _uncited_gate(report, vault_tag, note_bodies)
    typer.echo(json.dumps({"uncited": uncited}))
    if uncited:
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
