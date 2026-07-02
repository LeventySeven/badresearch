# Why bad-research "breaks" headless / as a backend — root cause + fix

**Status:** diagnosed 2026-07-01, reproduced with literal errors, nothing mutated. Written for you to fix.

**TL;DR (the one-sentence root cause):** bad-research's **"keyless" property only holds when the Claude Code *host model* drives the skill** — the host model *is* the inference engine and calls the `bad` CLI for deterministic machinery. There is **no Python code path where the running CLI/pipeline calls "the host model"**; the only concrete `LLMProvider` is `AnthropicProvider`, which **hard-requires `ANTHROPIC_API_KEY`**. So when bad-research is run **headless** — a Workflow subagent shelling out, a plain `bad` invocation, `import bad_research`, or "use it as a search/research backend" — the deterministic stages run but the terminal LLM step fails. **This is an invocation-mode / architectural-boundary issue, not a code defect.** It is *not* "the search backend is broken" (that memory note was a symptom read, not the cause — see §4).

---

## 1. Symptom (what was observed / recorded)

The project memory carried: *"bad-research search backend broken in this sandbox, use Workflow + WebSearch instead."* That note was written from a **Claude Code session (researchfms/Verso)** that tried to use bad-research **programmatically as a research/search backend** for another task. It "didn't work," and the pragmatic workaround (use the harness's own `WebSearch`/`Workflow`) was adopted. The note names the *search* as broken; the actual boundary is broader and elsewhere.

## 2. What actually works vs. fails headless (reproduced 2026-07-01, venv Python 3.12.13)

`bad doctor` reports **all 12 providers OK** — but `doctor` only checks the *capability surface* (module imports / CLI on PATH), never runtime behavior, so it is green while the pipeline can't complete headless. Reproductions:

| Path | Result headless | Evidence |
|---|---|---|
| `ddgs` search lib directly | ✅ returns results | `DDGS().text(...)` → 3 rows, network fine |
| `bad funnel-gather <q>` (ddgs + BM25 funnel) | ❌ **`VaultError: No hyperresearch vault found`** | `core/vault.py:156` — needs a `research/` vault cwd, *not* a search failure |
| `bad calibrate <q>` (headless LLM judge) | ❌ **`ANTHROPIC_API_KEY is not set. Export it or use --offline`** | `cli/calibrate.py` → `llm/anthropic.py:49-51` |
| `pipeline.run_query` route + gather + retrieve | ✅ deterministic, $0, keyless | `pipeline.py:247-261` (docstring: "$0 model cost") |
| `pipeline.run_query` → `_synthesize` (the report) | ❌ needs inference | `pipeline.py:198-212` `get_llm_provider()` → `AnthropicProvider` → key |
| **no `bad research` command exists at all** | — | full CLI surface = `funnel-gather / retrieve / calibrate / init / search / fetch / grounding-* / uncited-gate / recitation-gate / route / verify-citations / …` — **research is the skill, not a command** |

## 3. Root cause, three layers (deepest first)

**Layer A — the real blocker: keyless inference requires a host-model driver that only exists in the interactive skill flow.**
- `bad-research` is a **Claude Code skill** (installed at `~/.claude/skills/bad-research/SKILL.md`). The *intelligence* — decompose, query-gen, rerank, draft, critics, synthesize — is performed by the **Claude Code host model executing the skill markdown**, which calls `bad` CLI subcommands only for deterministic ops (vault, FTS, funnel-gather, grounding gates).
- The Python LLM seam has exactly **one** concrete provider: `AnthropicProvider` (`llm/anthropic.py:31`), and `get_llm_provider()`/`load_provider()` default to it (`llm/base.py:48-52`). Its constructor: `key = api_key or os.environ.get("ANTHROPIC_API_KEY"); if not key: raise RuntimeError(...)` (`llm/anthropic.py:48-51`).
- **There is no `HostModelProvider`** — nothing lets the *running Python process* call back into the host session's model. So "keyless" is true **only** when the host model is the caller (skill flow), and **false** for any headless caller, which must supply a key.
- Consequence: headless `run_query` completes route + gather + retrieve (all `$0`, `pipeline.py:247-261`) and then `_synthesize` (`pipeline.py:182-212`) calls `get_llm_provider()` → `AnthropicProvider` → **`RuntimeError` without a key**. In this sandbox (keyless by design, no key exported) that is the exact failure.

**Layer B — the primary search lane is a host-tool adapter, not a self-contained searcher.**
- `WebSearchToolProvider` (`web/search/base.py:69`) is *"an adapter over the Claude Code host WebSearch tool… invoked by the ORCHESTRATOR (Claude Code), NOT by this Python layer"*; its `search_ex` raises `NotImplementedError` in a subprocess. `BuiltinProvider.search()` also `raise NotImplementedError` (`web/builtin.py:66`).
- The CLI funnel deliberately **leads with `DdgsProvider`** and appends the host adapter **last** ("harmlessly skipped by `fan_out`'s `NotImplementedError` guard", `cli/research.py:96-144`). So headless search *does* run — via **ddgs + the 7 scholarly verticals** — it just lacks the host-WebSearch quality lane. Search is **degraded, not broken.**

**Layer C — vault cwd requirement (a red herring that looks like a search break).**
- `funnel-gather` and every vault op need an initialized `research/` vault; run from an arbitrary dir they raise `VaultError` (`core/vault.py:156`) **before any search happens** — which is easy to misread as "search is broken."

## 4. Why the memory note said "search backend broken → use Workflow + WebSearch"
It was a **symptom read from the wrong invocation mode.** Trying to call bad-research as a headless backend hits Layer C first (`VaultError`, looks like search), Layer B (no host-WebSearch lane), and Layer A (synthesize needs a key). The note-taker correctly concluded "don't fight it, use the harness's own WebSearch" — a fine *workaround*, but the *cause* is that **bad-research is a host-model-driven interactive skill, not a callable headless research backend.** Run the right way, it is keyless and works.

## 5. The fix (aligned to the core goal: keyless, install-and-go, SOTA *inside Claude Code*)

**It's not broken — run it the one intended way.** bad-research is a **keyless Claude Code skill**; research runs when a **model drives the skill**. There are exactly **two legitimate keyless entrypoints**, and both are on-mission:
1. **Interactive:** `/bad-research <query>` in a Claude Code session. Installed, keyless, SOTA. *This is the product.*
2. **Subagent:** a Claude Code **Task subagent** invokes the `/bad-research` entry skill. Still a model driving the skill → still keyless. **This is the keyless-correct way to use bad-research "as a backend"** from a Workflow / another agent — delegate to a subagent that runs the skill; do **not** shell the CLI expecting a report.

**Why there is no keyless *subprocess* path (architectural truth, not a gap to fix):** a `python -m bad_research` subprocess has **no channel to the session model** — it cannot call the host model. Keyless inference *only* exists when a Claude model reads the skill and performs the LLM steps (calling the CLI for deterministic ops). So the `bad` CLI is, by design, **deterministic helpers only** (`funnel-gather`, `retrieve`, `fetch`, grounding gates) — it is not, and cannot be, a keyless headless report generator. **Do NOT add a "HostModelProvider" that calls the host model from Python — it is impossible in this architecture** (an earlier draft of this doc floated it; that was wrong).

**The ONE key-requiring path is off-mission.** `pipeline.run_query`'s terminal `_synthesize` and `bad calibrate` use the `AnthropicProvider` bridge (needs `ANTHROPIC_API_KEY`) — that exists **only** for offline calibration/benchmarking, never for using the product. Setting a key to "make research work headless" means you've deliberately stepped off the keyless path. The real fix (Task 6 of `docs/plans/2026-07-01-badresearch-sota-keyless.md`) is to make that path's error message point back to the skill, so nobody mistakes the calibration bridge for "bad-research needs a key."

**Operational:** run vault/funnel ops from an initialized vault (`bad init <dir>` or a `research/` dir) to avoid the `VaultError` that masquerades as a search failure (Layer C).

## 6. What is NOT the problem (so you don't chase it)
- **Not the sandbox network** — `ddgs` returns live results here.
- **Not Python 3.14 / pyexpat** — the venv is **3.12.13**; the 3.14/pyexpat issue is the *system* Python, unrelated to this.
- **Not a missing dependency** — `bad doctor` is all-green; every provider imports.
- **Not the ddgs/vertical search code** — it works headless once a vault exists.
- The single `*_API_KEY` read is the **opt-in headless/calibration bridge** (`llm/anthropic.py`), never read on the skill path.

---

### Evidence index (all `file:line` in `src/bad_research/`, verified 2026-07-01)
- `llm/anthropic.py:31,48-51` — the only provider; hard key requirement.
- `llm/base.py:48-54` — `load_provider` defaults to Anthropic; registry = `{anthropic}` only.
- `pipeline.py:228-268` — `run_query` stages; 247-261 deterministic `$0`; **182-212 `_synthesize` → `get_llm_provider()` → key**.
- `web/search/base.py:69-75` — `WebSearchToolProvider` is a host-tool adapter; `web/builtin.py:66` — `search()` NotImplemented.
- `cli/research.py:96-144` — funnel leads with ddgs, host adapter appended last & skipped headless.
- `core/vault.py:156` — `VaultError` when no vault in cwd.
- Reproduced errors: `bad calibrate` → *"ANTHROPIC_API_KEY is not set"*; `bad funnel-gather` (no vault) → *"No hyperresearch vault found"*; `ddgs` direct → 3 live results.
