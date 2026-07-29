"""Executable keyless-invariant guard (Task 1) — the check that keeps bad-research
install-and-go and fully keyless.

Two machine-checkable invariants must always hold:

1. **No keyed provider in base deps.** No keyed search/browse provider may enter
   the base ``project.dependencies``; the keyed extras live only in
   ``optional-dependencies``. ``anthropic`` is deliberately NOT in the keyed set —
   it is the base *headless/calibration* bridge, which invariant 2 fences off the
   skill path.
2. **Skill path is bridge-free.** Every module reachable on the SKILL path (the
   keyless research flow) must never import the key bridge (``llm.anthropic``) or
   read ``ANTHROPIC_API_KEY``. The Claude Code host model supplies all skill-path
   inference; the bridge exists only for the off-mission ``calibrate`` /
   headless-``run_query`` path.

Run as a gate (exit 0 == clean)::

    python -m bad_research.tests.keyless_invariant

The same functions back ``tests/keyless_invariant_test.py`` so there is ONE
source of truth for both the CI test and the runnable gate.
"""

from __future__ import annotations

import importlib
import pathlib
import tomllib

# Keyed search/browse providers that must stay OUT of base deps. NOT `anthropic`:
# that is the base calibration bridge, fenced off the skill path by invariant 2.
# Both underscore and hyphen spellings are listed so a `browser-use`/`exa-py`
# PyPI name can't slip through a `browser_use`-only match.
KEYED_PROVIDERS: frozenset[str] = frozenset(
    {
        "tavily",
        "exa",
        "exa_py",
        "exa-py",
        "cohere",
        "firecrawl",
        "browserbase",
        "agentql",
        "browser_use",
        "browser-use",
    }
)

# Every module the keyless skill path can reach. None may reference the key bridge.
SKILL_PATH_MODULES: tuple[str, ...] = (
    "bad_research.pipeline",
    "bad_research.funnel.orchestrator",
    "bad_research.retrieval.engine",
    "bad_research.web.search.base",
    "bad_research.grounding.verifier",
    "bad_research.skills.router",
)

# Literal tokens forbidden in any skill-path module source.
FORBIDDEN_ON_SKILL_PATH: tuple[str, ...] = ("llm.anthropic", "ANTHROPIC_API_KEY")


def _find_pyproject() -> pathlib.Path:
    """Locate ``pyproject.toml``: cwd first (dev / CI run from the repo root),
    else resolved from this module's src-tree location
    (``.../src/bad_research/tests/keyless_invariant.py`` → ``parents[3]``)."""
    cwd = pathlib.Path("pyproject.toml")
    if cwd.is_file():
        return cwd
    return pathlib.Path(__file__).resolve().parents[3] / "pyproject.toml"


def base_dependencies() -> list[str]:
    """The base (always-installed) ``project.dependencies`` list from pyproject."""
    pp = tomllib.loads(_find_pyproject().read_text(encoding="utf-8"))
    return list(pp["project"]["dependencies"])


def keyed_base_deps() -> list[str]:
    """Base dependencies that name a keyed provider ( ``[]`` == clean )."""
    return [
        dep
        for dep in base_dependencies()
        if any(keyed in dep.lower() for keyed in KEYED_PROVIDERS)
    ]


def skill_path_bridge_imports() -> list[str]:
    """Skill-path modules whose source references the key bridge ( ``[]`` == clean )."""
    offenders: list[str] = []
    for mod_name in SKILL_PATH_MODULES:
        mod = importlib.import_module(mod_name)
        if mod.__file__ is None:  # namespace package — no source to scan
            continue
        src = pathlib.Path(mod.__file__).read_text(encoding="utf-8")
        if any(token in src for token in FORBIDDEN_ON_SKILL_PATH):
            offenders.append(mod_name)
    return offenders


def check() -> list[str]:
    """Run both invariants; return human-readable violations ( ``[]`` == clean )."""
    problems: list[str] = []
    keyed = keyed_base_deps()
    if keyed:
        problems.append(f"KEYED provider(s) in base dependencies: {keyed}")
    bridged = skill_path_bridge_imports()
    if bridged:
        problems.append(
            "skill-path module(s) import the key bridge "
            f"({' / '.join(FORBIDDEN_ON_SKILL_PATH)}): {bridged}"
        )
    return problems


def main() -> int:  # pragma: no cover - exercised via the CLI/Done signal, not pytest
    problems = check()
    if problems:
        print("KEYLESS INVARIANT VIOLATED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("keyless invariant OK: no keyed base dep; skill path is bridge-free.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
