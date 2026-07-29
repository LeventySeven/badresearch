"""pyproject.toml: pure-keyless base + the keyless extras (INTERFACES_KEYLESS §7)."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]  # .../badresearch/
PYPROJECT = ROOT / "pyproject.toml"


@pytest.fixture(scope="module")
def pp() -> dict:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


def _names(dep_list: list[str]) -> set[str]:
    out = set()
    for d in dep_list:
        name = d.split(";")[0].strip()
        for sep in (">=", "==", "~=", "<", ">", "[", " "):
            name = name.split(sep)[0]
        out.add(name.strip().lower())
    return out


# ── metadata + entry points ──────────────────────────────────────────────────
def test_project_name_and_python(pp):
    assert pp["project"]["name"] == "bad-research"
    assert pp["project"]["requires-python"] == ">=3.11,<3.14"


def test_entry_points(pp):
    scripts = pp["project"]["scripts"]
    assert scripts["bad"] == "bad_research.cli:app"
    assert scripts["badr"] == "bad_research.cli:app"


def test_wheel_packages(pp):
    pkgs = pp["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"]
    assert pkgs == ["src/bad_research"]


# ── pure-keyless base ────────────────────────────────────────────────────────
# The removed keyed/heavy stack MUST NOT be in the base install.
FORBIDDEN_IN_BASE = {
    "cohere", "tavily-python", "exa-py", "firecrawl-py", "browserbase",
    "browser-use", "agentql", "stagehand", "playwright", "torch",
    "sentence-transformers", "lancedb", "pyarrow", "flagembedding",
}


def test_base_is_pure_keyless(pp):
    base = _names(pp["project"]["dependencies"])
    leaked = base & {n.lower() for n in FORBIDDEN_IN_BASE}
    assert not leaked, f"non-keyless deps leaked into base: {leaked}"


def test_base_carries_keyless_essentials(pp):
    base = _names(pp["project"]["dependencies"])
    # anthropic stays core (the calibration/headless bridge); the keyless content stack.
    # (rank-bm25 + snowballstemmer were dropped once fetch_clean's highlights path — their
    # only consumer — was amputated; retrieval ranks via SQLite FTS5's native bm25().)
    assert {
        "anthropic", "httpx", "crawl4ai", "ddgs", "pymupdf", "trafilatura",
        "beautifulsoup4", "feedparser", "typer", "rich", "pydantic",
    } <= base, f"missing keyless essentials; have {sorted(base)}"


def test_base_has_no_torch_lancedb_playwright(pp):
    base = pp["project"]["dependencies"]
    assert all(
        "torch" not in d and "lancedb" not in d and "playwright" not in d for d in base
    )


# ── extras: the keyless shape ────────────────────────────────────────────────
def test_search_and_grounding_extras_gone(pp):
    extras = pp["project"]["optional-dependencies"]
    assert "search" not in extras, "the keyed [search] extra must be deleted"
    assert "grounding" not in extras, "[grounding] folds into [local] (sentence-transformers)"


def test_keyless_extras_exist(pp):
    extras = pp["project"]["optional-dependencies"]
    for group in ("browse", "local", "mcp", "all", "dev"):
        assert group in extras, f"missing extras group: {group}"


def test_browse_extra_is_playwright_only(pp):
    browse = _names(pp["project"]["optional-dependencies"]["browse"])
    assert browse == {"playwright"}, f"[browse] should be playwright-only; got {browse}"


def test_local_extra_holds_the_neural_stack(pp):
    local = _names(pp["project"]["optional-dependencies"]["local"])
    assert {"torch", "sentence-transformers", "lancedb", "pyarrow"} <= local


def test_all_composes_keyless_extras(pp):
    all_dep = pp["project"]["optional-dependencies"]["all"]
    assert any("bad-research[" in d for d in all_dep)
    joined = " ".join(all_dep)
    assert "browse" in joined and "local" in joined and "mcp" in joined
