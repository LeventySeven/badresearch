"""KR-6 — CLI surface for the grader + recitation gate, and the keyless rewire."""
from __future__ import annotations

import inspect
import json
from pathlib import Path

from typer.testing import CliRunner

import bad_research.cli.research as RESEARCH  # noqa: N812 (used pervasively as RESEARCH.*)
from bad_research.cli import app

runner = CliRunner()


def test_recitation_gate_clean_report_exits_zero(tmp_path: Path):
    report = tmp_path / "r.md"
    report.write_text("# Q\n\nA short paraphrase of the finding here [1].\n", encoding="utf-8")
    notes = tmp_path / "notes.json"
    notes.write_text(json.dumps({"n1": "Entirely different wording about the topic at hand."}),
                     encoding="utf-8")
    res = runner.invoke(app, ["recitation-gate", "--report", str(report),
                              "--note-bodies", str(notes), "--json"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["recitation"] == []


def test_recitation_gate_flags_verbatim_copy(tmp_path: Path):
    src = ("Transformers replace recurrence with self attention allowing the model to "
           "weigh every token against every other token in parallel during training.")
    report = tmp_path / "r.md"
    report.write_text(f"# Q\n\n{src} [1].\n", encoding="utf-8")
    notes = tmp_path / "notes.json"
    notes.write_text(json.dumps({"n1": src}), encoding="utf-8")
    res = runner.invoke(app, ["recitation-gate", "--report", str(report),
                              "--note-bodies", str(notes), "--json"])
    # recitation is a MAJOR finding, not a ship-block: exit 0, but flagged.
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert len(out["recitation"]) == 1
    assert out["recitation"][0]["failure_mode"] == "recitation"


# ── the keyless rewire (Task 7) ──────────────────────────────────────────────


def test_grounding_cli_never_constructs_a_provider(monkeypatch, tmp_path):
    """Project directive — verify-citations + grade-report are ALWAYS keyless: they
    must NEVER construct an API-key'd LLM provider, even with ANTHROPIC_API_KEY set.
    Poison get_llm_provider so any attempt raises; both commands must still succeed."""
    def _boom(*a, **k):
        raise AssertionError("get_llm_provider must NOT be called on the keyless grounding path")

    monkeypatch.setattr("bad_research.llm.base.get_llm_provider", _boom)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-should-be-ignored")

    report = tmp_path / "rep.md"
    report.write_text("# Q\n\nVietnam exported 7 million tonnes in 2023 [[v]].\n", encoding="utf-8")
    corpus = tmp_path / "corpus.json"
    corpus.write_text(
        json.dumps([{"note_id": "v", "url": "", "text": "Vietnam exported 7 million tonnes in 2023."}]),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    v = runner.invoke(app, ["verify-citations", "--report", str(report), "--vault-tag", "t", "--json"])
    assert v.exit_code == 0, v.stdout

    g = runner.invoke(app, ["grade-report", "--report", str(report), "--corpus", str(corpus), "--json"])
    assert g.exit_code == 0, g.stdout
    out = json.loads(g.stdout)
    assert out["status"] == "keyless-skip"
    assert out["passed"] is None


def test_build_providers_returns_keyless_providers():
    cfg = type("C", (), {"searxng_endpoint": "", "effort": "medium"})()
    provs = RESEARCH._build_providers(cfg)
    names = {getattr(p, "name", "") for p in provs}
    # the keyless default: the host WebSearch tool adapter + the ddgs lib.
    assert "websearch" in names
    assert "ddgs" in names
    # every provider is keyless: cost_per_search 0.0, no api key attr set true
    for p in provs:
        assert getattr(p, "cost_per_search", 0.0) == 0.0


def test_build_reranker_default_is_claude_code():
    cfg = type("C", (), {"reranker": "host"})()
    r = RESEARCH._build_reranker(cfg)
    assert type(r).__name__ == "ClaudeCodeReranker"


def test_build_embedder_is_none_by_default():
    cfg = type("C", (), {"reranker": "host", "neural_recall": False})()
    assert RESEARCH._build_embedder(cfg) is None


def test_build_tiered_fetcher_uses_agent_browser_ladder():
    cfg = type("C", (), {"browse_engine": "lightpanda"})()
    f = RESEARCH._build_tiered_fetcher(cfg)
    # the keyless 4-rung TieredFetcher (no Browserbase/Browser-Use rungs).
    assert f is not None
    assert hasattr(f, "fetch_tiered")


def test_no_removed_provider_imports_in_research_module():
    # the rewired module must not pull in any paid-provider seam, even lazily.
    src = inspect.getsource(RESEARCH)
    banned = ["cohere", "tavily", "exa_provider", "firecrawl", "sonar_provider",
              "browse_browserbase", "browse_browseruse", "extract_agentql",
              "extract_stagehand", "cascade", 'get_provider("builtin")',
              'get_embed_provider("cohere"']
    for token in banned:
        assert token not in src, f"removed-provider reference survives: {token}"


def test_funnel_gather_cmd_has_max_tokens_and_effort():
    # C-5: the --reasoning-effort alias is removed; --effort is the single canonical
    # CLI flag. The Python parameter is named `effort` to match.
    sig = inspect.signature(RESEARCH.funnel_gather_cmd)
    assert "effort" in sig.parameters
    assert "max_tokens" in sig.parameters
    # the removed alias must not survive as a CLI option string anywhere
    from typer.testing import CliRunner

    from bad_research.cli import app
    r = CliRunner().invoke(app, ["funnel-gather", "--help"])
    assert "--effort" in r.stdout
    assert "--reasoning-effort" not in r.stdout


# ── the crown-jewel integration test — REAL builders, mocked host LLM ─────────
#
# This test exercises the ACTUAL _build_* functions (not stand-ins) and assembles
# them into a real FunnelDeps + a real run_query end-to-end, so a wrong builder
# wiring FAILS here. Prior Plan-08 caught broken builder imports that seam-
# monkeypatching had hidden — to defeat that, we (a) assert each real builder's
# concrete type, and (b) drive the funnel `gather` directly (which does NOT
# swallow exceptions like pipeline._gather does) so a broken builder surfaces as
# an empty corpus / wrong behaviour rather than a silently-degraded pass.

import json as _json
from dataclasses import dataclass

from bad_research.llm.base import LLMResponse
from bad_research.web.base import WebResult


@dataclass
class _Cfg:
    """A minimal keyless config matching what the builders read."""

    searxng_endpoint: str = ""
    neural_recall: bool = False
    reranker: str = "host"
    browse_engine: str = "lightpanda"
    effort: str = "medium"


class _MockHostLLM:
    """The host model behind the LLMProvider seam — scripted, keyless, no network.
    Returns a synthesis report for the synthesizer and a rerank score array for
    ClaudeCodeReranker, distinguished by the system message."""

    name = "mock-host"

    def __init__(self) -> None:
        self.synth_calls = 0
        self.rerank_calls = 0

    def complete(self, messages, *, tier, tools=None, cache=False,
                 max_tokens=4096, temperature=0.1) -> LLMResponse:
        sys = str(next((m.content for m in messages if m.role == "system"), "")).lower()
        is_rerank = "relevance scorer" in sys or "reranker" in sys
        if is_rerank:
            # ClaudeCodeReranker's frozen prompt — return a per-doc score array (the
            # §5.3 JSON shape the shared parser reads). One score per candidate.
            self.rerank_calls += 1
            user = str(next((m.content for m in messages if m.role == "user"), ""))
            n = sum(1 for ln in user.splitlines() if ln.strip().startswith("["))
            items = [{"i": i, "s": 0.95} for i in range(max(1, n))]
            return LLMResponse(text=_json.dumps(items), usage={}, model="mock")
        self.synth_calls += 1
        return LLMResponse(
            text="# Mocked Report\n\nThe host-model synthesis ran [1].\n",
            usage={"input_tokens": 10, "output_tokens": 20}, model="mock")


def test_real_builders_assemble_keyless_concrete_types():
    """A wiring break (a builder that imports a non-existent class, swallowed to
    None/wrong-type) is caught right here, before any seam-mocking can hide it."""
    cfg = _Cfg()
    provs = RESEARCH._build_providers(cfg)
    assert {type(p).__name__ for p in provs} == {"WebSearchToolProvider", "DdgsProvider"}
    fetcher = RESEARCH._build_tiered_fetcher(cfg)
    assert type(fetcher).__name__ == "TieredFetcher"        # NOT None (the prior bug)
    assert hasattr(fetcher, "fetch_tiered")
    assert getattr(fetcher, "engine", None) == "lightpanda"  # config threaded through
    assert type(RESEARCH._build_reranker(cfg)).__name__ == "ClaudeCodeReranker"
    assert RESEARCH._build_embedder(cfg) is None             # FTS-only default


async def test_real_builder_funnel_path_produces_corpus(monkeypatch):
    """Assemble FunnelDeps from the REAL builders (providers + fetcher + reranker)
    and run the real funnel `gather` A→F. We inject content at the lowest seam (the
    host Links array + the module-level fetch_tiered) so the REAL provider/fetcher
    objects are exercised — a broken builder yields an empty corpus and FAILS."""
    from bad_research.funnel.orchestrator import FunnelDeps, gather
    from tests.test_funnel.conftest import FakeRetrievalEngine, FakeVault

    cfg = _Cfg()
    provs = RESEARCH._build_providers(cfg)
    # The keyless-correct cascade LEADS with DdgsProvider (the working HTTP lane);
    # in light mode the funnel's `[:1]` slice picks it. Feed it canned results (no
    # network) so the REAL provider object is exercised. The host WebSearchToolProvider
    # cannot run in this (subprocess) context — it raises NotImplementedError and
    # fan_out skips it — so it must NOT be the active provider.
    ddgs = next(p for p in provs if type(p).__name__ == "DdgsProvider")
    monkeypatch.setattr(ddgs, "search", lambda *a, **k: [
        WebResult(url="https://a.example/doc", title="Doc A", content="a"),
        WebResult(url="https://b.example/doc", title="Doc B", content="b"),
    ])
    assert provs[0] is ddgs, "keyless HTTP lane must lead the cascade"

    fetcher = RESEARCH._build_tiered_fetcher(cfg)  # REAL TieredFetcher
    # Patch the module-level fetch_tiered the REAL wrapper delegates to → canned content.
    def _fake_fetch_tiered(url, *, tier_max, instruction=None, schema=None,
                           replay_key=None, variables=None, **kw):
        return WebResult(url=url, title=f"page {url}",
                         content="grounded research content " * 40,
                         metadata={"source": "test"})
    monkeypatch.setattr("bad_research.browse.ladder.fetch_tiered", _fake_fetch_tiered)

    deps = FunnelDeps(
        providers=provs,
        fetcher=fetcher,
        postfetch_filter=lambda r: r.looks_like_junk(),
        vault=FakeVault(),
        retrieval=FakeRetrievalEngine(),
    )
    chunks = await gather("impact of AI on research", mode="light", deps=deps)
    # The REAL providers + REAL fetcher produced a corpus the funnel chunked.
    assert chunks, "real builder funnel path produced an empty corpus — wiring break"
    assert all(getattr(c, "note_id", None) for c in chunks)


def test_real_build_engine_reranks_through_host_llm(monkeypatch, tmp_path):
    """Exercise the REAL _build_engine → REAL _build_reranker (ClaudeCodeReranker)
    against the REAL RetrievalEngine on real Notes, with the host LLM mocked. This
    is the fourth builder: a broken reranker wiring (wrong class / a Cohere import)
    would surface as a non-ClaudeCodeReranker engine.reranker or a crash here.

    We index real Notes (the engine's true input contract) and search; the rerank
    runs the frozen prompt through the mocked host model (rerank_calls > 0)."""
    from bad_research.models.note import Note, NoteMeta

    mock_llm = _MockHostLLM()
    monkeypatch.setattr("bad_research.llm.base.get_llm_provider",
                        lambda *a, **k: mock_llm)

    cfg = _Cfg()
    vault = type("V", (), {"root": tmp_path})()
    engine = RESEARCH._build_engine(cfg, vault)          # REAL engine via REAL builders
    assert type(engine.reranker).__name__ == "ClaudeCodeReranker"  # the KR-5 default
    assert engine.embedder is None                       # FTS-only keyless default

    def _note(nid, body):
        return Note(meta=NoteMeta(title=nid, id=nid, source=f"https://ex.com/{nid}",
                                  status="evergreen"),
                    body=body, path=f"research/{nid}.md")
    # Graded term-frequency over the query terms (all docs recalled) so the min-max-
    # normed BM25 proxy spans E6's bands: the top doc is auto-kept by the cascade and
    # the weakest auto-dropped, but the MIDDLE docs land in the UNCERTAIN band and MUST
    # hit the host-model reranker seam — which is exactly what this test verifies (a
    # wrong-class / Cohere wiring would crash here, post-E6 it must still be reached).
    engine.index([
        _note("a", "# A\n\n" + "research synthesis grounding " * 12 + "\n"),
        _note("m1", "# M1\n\n" + "research synthesis grounding " * 7 + ("pad " * 30) + "\n"),
        _note("m2", "# M2\n\n" + "research synthesis grounding " * 4 + ("pad " * 60) + "\n"),
        _note("z", "# Z\n\n" + "research synthesis grounding " * 1 + ("pad " * 120) + "\n"),
    ])
    hits = engine.search("research synthesis grounding", mode="light", top_k=4)
    assert hits, "real FTS+host-rerank engine returned no hits on a matching query"
    assert mock_llm.rerank_calls >= 1, "the host-model reranker seam was never called"


def test_run_query_end_to_end_degrades_gracefully_on_real_builders(monkeypatch, tmp_path):
    """The full headless pipeline.run_query on the REAL builders + a mocked host
    LLM, NO keys, NO network. The four real builders assemble and run end-to-end
    without crashing; run_query returns a RunResult and the synthesizer reaches the
    host-model seam (a key-claiming builder would crash the import here)."""
    from bad_research import pipeline
    from bad_research.config import BadResearchConfig

    mock_llm = _MockHostLLM()
    monkeypatch.setattr("bad_research.llm.base.get_llm_provider",
                        lambda *a, **k: mock_llm)

    # Force a corpus into the synthesizer THROUGH the real run_query stage graph by
    # supplying a faithful _retrieve result (real engine builder + real Notes), so
    # synthesis runs on the real builders' output via the host-model seam.
    from bad_research.models.note import Note, NoteMeta

    def _seeded_retrieve(query, mode, cfg, cm):
        vault = type("V", (), {"root": tmp_path})()
        engine = RESEARCH._build_engine(cfg, vault)  # REAL builders (engine+reranker)
        engine.index([Note(meta=NoteMeta(title="a", id="a",
                                         source="https://ex.com/a", status="evergreen"),
                           body="# A\n\nresearch synthesis grounding keyless pipeline content\n",
                           path="research/a.md")])
        from dataclasses import asdict
        return [asdict(c) for c in engine.search(query, mode="light", top_k=5)]

    monkeypatch.setattr(pipeline, "_retrieve", _seeded_retrieve)
    monkeypatch.chdir(tmp_path)

    result = pipeline.run_query("research synthesis grounding", BadResearchConfig())
    assert result is not None
    # The seeded corpus reached synthesis via the host-model seam → mocked report.
    assert mock_llm.synth_calls >= 1, "synthesis never reached the host-model seam"
    assert "host-model synthesis ran" in result.report
    assert result.corpus, "run_query produced an empty corpus on the real builders"


# ── the crown jewel — the REAL funnel→engine seam, NO mocks on deps.retrieval ──
#
# Every prior funnel/pipeline test mocked deps.retrieval (a FakeRetrievalEngine
# whose .index() happily accepts (note_id, body) tuples) or sidestepped the funnel
# with a seeded _retrieve. So the funnel→RetrievalEngine input-shape seam — Stage E
# emitting what Stage F's RetrievalEngine.index(Iterable[Note]) actually consumes —
# was never exercised. These tests drive the WHOLE chain with the REAL engine, so a
# wrong type at the seam surfaces as an empty corpus / AttributeError, not a pass.


def _real_engine_on_tmp_vault(tmp_path):
    """A REAL keyless RetrievalEngine (FTS-only, embedder=None) on a tmp vault,
    with the host-model reranker mocked at construction (no key, no network)."""
    from bad_research.retrieval.engine import RetrievalEngine
    from bad_research.retrieval.rerank import ClaudeCodeReranker

    base = tmp_path / ".bad-research"
    base.mkdir(parents=True, exist_ok=True)
    reranker = ClaudeCodeReranker(llm=_MockHostLLM())  # REAL reranker, mocked host
    return RetrievalEngine(cache_db=base / "semantic_cache.db",
                           reranker=reranker, embedder=None)


def _wire_real_funnel_deps(monkeypatch, tmp_path):
    """Assemble a FunnelDeps where EVERY seam that touches the funnel→engine path
    is REAL: real providers (host Links injected), real TieredFetcher (module-level
    fetch_tiered patched to canned content), a REAL VaultStore on a tmp vault, and
    a REAL RetrievalEngine. The ONLY fakes are network edges (no key/no net)."""
    from bad_research.core.vault import Vault
    from bad_research.funnel.orchestrator import FunnelDeps
    from bad_research.funnel.store import VaultStore
    from bad_research.web.base import WebResult

    cfg = _Cfg()
    provs = RESEARCH._build_providers(cfg)
    # Keyless-correct cascade: DdgsProvider (the working HTTP lane) leads, so the
    # light-mode `[:1]` slice picks it. Inject canned results (no network). The host
    # WebSearchToolProvider can't run here (NotImplementedError; fan_out skips it).
    ddgs = next(p for p in provs if type(p).__name__ == "DdgsProvider")
    monkeypatch.setattr(ddgs, "search", lambda *a, **k: [
        WebResult(url="https://a.example/transformers",
                  title="Attention Is All You Need", content="a"),
        WebResult(url="https://b.example/rag",
                  title="Retrieval Augmented Generation", content="b"),
    ])
    assert provs[0] is ddgs, "keyless HTTP lane must lead the cascade"

    fetcher = RESEARCH._build_tiered_fetcher(cfg)

    def _fake_fetch_tiered(url, *, tier_max, instruction=None, schema=None,
                           replay_key=None, variables=None, **kw):
        # Real, indexable prose with a heading so the prose chunker produces chunks.
        return WebResult(
            url=url, title=f"page {url}",
            content=("# Findings\n\nTransformers replace recurrence with self "
                     "attention so the model weighs every token against every other "
                     "token in parallel during training and inference. " * 8),
            metadata={"source": "test"})
    monkeypatch.setattr("bad_research.browse.ladder.fetch_tiered", _fake_fetch_tiered)

    # A REAL vault on disk (idempotent: reuse if a prior call already init'd it).
    vault = Vault(tmp_path) if (tmp_path / ".hyperresearch").is_dir() else Vault.init(tmp_path)
    real_engine = _real_engine_on_tmp_vault(tmp_path)
    return FunnelDeps(
        providers=provs,
        fetcher=fetcher,
        postfetch_filter=lambda r: r.looks_like_junk(),
        vault=VaultStore(vault),                    # REAL vault adapter (persists to disk)
        retrieval=real_engine,                      # REAL engine — NO mock
    ), vault, real_engine


async def test_real_funnel_into_real_engine_produces_nonempty_corpus(monkeypatch, tmp_path):
    """THE BUG GUARD: run the REAL funnel A→F into the REAL RetrievalEngine. The
    seam (Stage E → Stage F index) must hand `index` real Notes; if it hands tuples
    the engine raises AttributeError → gather can't return chunks → empty corpus.
    A non-empty corpus here proves the seam carries the right type."""
    from bad_research.funnel.orchestrator import gather

    deps, vault, _engine = _wire_real_funnel_deps(monkeypatch, tmp_path)
    # Query terms all appear in the canned body (transformers/attention/token), so
    # the FTS AND-match recalls the chunk; the bug we guard is the SEAM (tuple vs
    # Note), not FTS tokenization — a poorly-matched query is a separate concern.
    chunks = await gather("transformers attention token", mode="light", deps=deps)

    assert chunks, ("real funnel → real engine produced an EMPTY corpus — the "
                    "Stage E→F seam handed the wrong type to RetrievalEngine.index")
    assert all(getattr(c, "note_id", None) for c in chunks)
    # The reranker ran over the indexed chunks (host-model seam reached, no key).
    assert all(getattr(c, "score", 0.0) > 0.0 for c in chunks)
    # Vault persistence intact: survivors were written to disk as real note files.
    note_files = list((vault.root / "research" / "notes").glob("*.md"))
    assert note_files, "survivors were not persisted to the vault (Stage E broke)"


async def test_real_funnel_engine_search_returns_ranked_chunks(monkeypatch, tmp_path):
    """After the real funnel indexes the real engine, a direct engine.search over
    the same vault returns ranked chunks (the ClaudeCodeReranker scored them via the
    mocked host LLM). Proves the indexed corpus is queryable end-to-end, no key."""
    from bad_research.funnel.orchestrator import gather

    deps, _vault, engine = _wire_real_funnel_deps(monkeypatch, tmp_path)
    await gather("transformers attention token", mode="light", deps=deps)
    hits = engine.search("self attention tokens parallel", mode="light", top_k=5)
    assert hits, "the real engine returned no hits after the real funnel indexed it"
    assert all(h.score > 0.0 for h in hits)


def test_run_query_nonempty_corpus_on_real_funnel(monkeypatch, tmp_path):
    """pipeline.run_query end-to-end on the REAL funnel + a mocked host LLM, NO keys.
    The corpus that reaches synthesis is NON-EMPTY (the bug = empty) and the report
    is NOT the 'no evidence gathered' template — real chunks reached the synthesizer."""
    from bad_research import pipeline
    from bad_research.cli import research as research_mod
    from bad_research.config import BadResearchConfig
    from bad_research.core.vault import Vault

    mock_llm = _MockHostLLM()
    monkeypatch.setattr("bad_research.llm.base.get_llm_provider",
                        lambda *a, **k: mock_llm)

    # Build a real vault on disk and make run_funnel use REAL deps (real engine).
    Vault.init(tmp_path)
    monkeypatch.chdir(tmp_path)

    deps_box: dict = {}

    def _wired_run_funnel(query, *, mode, vault_tag, raw=False, **kw):
        import asyncio
        from dataclasses import asdict, is_dataclass

        from bad_research.funnel.orchestrator import gather

        deps, _vault, _engine = _wire_real_funnel_deps(monkeypatch, tmp_path)
        deps_box["deps"] = deps
        chunks = asyncio.run(gather(query, mode=("full" if mode == "full" else "light"),
                                    deps=deps))
        top_chunks = [asdict(c) if is_dataclass(c) else dict(getattr(c, "__dict__", {}))
                      for c in chunks]
        return {"note_ids": [], "top_chunks": top_chunks, "n_read": len(top_chunks)}

    monkeypatch.setattr(research_mod, "run_funnel", _wired_run_funnel)
    # Force _gather to use the real (wired) funnel and _retrieve to NOT override it.
    monkeypatch.setattr(pipeline, "_retrieve", lambda *a, **k: [])

    result = pipeline.run_query("transformers attention token", BadResearchConfig())
    assert result.corpus, "run_query produced an EMPTY corpus on the real funnel chain"
    assert "No evidence was gathered" not in result.report, \
        "synthesis emitted the no-evidence template — real chunks never reached it"
    assert mock_llm.synth_calls >= 1, "synthesis never reached the host-model seam"
