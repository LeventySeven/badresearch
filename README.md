<p align="center">
  <img src="assets/banner.png" alt="BAD — michael jackson bad" width="520">
</p>

<h1 align="center">Bad Research</h1>

<p align="center"><em>michael jackson bad</em></p>

<p align="center">
  <a href="https://pypi.org/project/bad-research/"><img src="https://img.shields.io/pypi/v/bad-research.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/bad-research/"><img src="https://img.shields.io/pypi/pyversions/bad-research.svg" alt="Python versions"></a>
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT">
</p>

A **keyless** research skill for Claude Code, plus the gates that make its rules
execute. Zero API keys: the host model supplies all inference. Optional local CLIs
and a `[local]` neural extra are enhancements, never requirements. Originally a
fork of [hyperresearch](https://github.com/jordan-gibbs/hyperresearch); the
research skill itself was rebuilt from scratch in 2026-09.

**What it actually is now.** One skill (`skills/bad-research/SKILL.md`) that runs research in
**rounds**: a broad round of parallel readers finds the shape of the question, and each later round is
built from what the earlier ones found. The readers exchange what they found through one per-run map
(`research/<slug>/MAP.md`: open questions, one-line findings with verbatim spans, the frontier, dead
ends, sources already seen), so nothing is found twice; the reasoner holds the map and all judgment.
Ten lane recipes read on demand, three agents (a reader that works a lane or a lead, a critic, an
adjudicator), and the `bad` subcommands that exit non-zero when a rule is broken.

The one mechanism is the **frontier**: every query after the first must NAME
something a previous read produced, and a query that names nothing is a re-phrase
and is refused by `bad frontier-gate`. The stop signal is computed in code before
the next round is built — from what arrived *and* what the answer still owes —
because a model that wants to keep searching is not a witness to its own
diminishing returns. An open disagreement between sources blocks the finish, and
ranking one side does not license dropping the other.

Why those and not something else: of eleven open-source research engines read in
source, exactly one generates its next question from evidence it retrieved and did
not use; none of them has contradiction handling in code; and a draft whose every
sentence is false but carries a resolving citation passes a presence-based gate
clean. How the best researchers, investigators and forecasters actually find and filter information —
the evidence the rounds are built on — is in
[`docs/sweeps/2026-09-26-how-researchers-find/FINDINGS.md`](docs/sweeps/2026-09-26-how-researchers-find/FINDINGS.md);
the other design notes and measurements are in [`docs/sweeps/`](docs/sweeps/) and the skill's `references/`.

## Install

Bad Research is a small CLI that registers itself as a Claude Code skill. No API keys. Requires Python 3.11–3.13.

```bash
# Install the CLI (pipx or uv — either works)
pipx install bad-research
uv tool install bad-research

# Register the /bad-research skill into ~/.claude
bad install

# Verify
bad doctor
```

`bad install` writes the skill to `~/.claude/skills/bad-research/` and its agents to
`~/.claude/agents/`. For a project-local install instead of global, run
`bad install --project` inside the project. `bad doctor` shows what's wired (host model,
keyless search/browse, the optional external CLIs it can drive, the `[local]` neural stack).

## Use it in Claude Code

After `bad install`, open Claude Code in any project and either:

- **Invoke it directly** — type the slash command with your question:
  ```
  /bad-research Is open-source AI more dangerous than closed-source for national security?
  ```
- **Let Claude trigger it** — just ask a research-shaped question (*"write me a cited report
  comparing vector databases"*, *"literature review on GLP-1 drugs"*) and Claude loads the
  skill automatically.

It scales to the question, and says which tier it chose in the first line of the answer:

- **Answer from what you have** — stable knowledge, cheap to be wrong. Never for a version, price,
  quota, date or proper name.
- **Quick** — one reasoner chaining queries from what it read; minutes.
- **Standard** (the default for a real question) — a broad round of 3–6 parallel readers on different
  kinds of source, then deep rounds built from the map until a round brings nothing new and every open
  question is closed.
- **Deep** — expensive to be wrong, contested, "find all", or an unfamiliar field: at least three rounds,
  a round spent on counter-evidence and origins, an independent check pass that never sees the map, and
  a multi-lens critique before the answer.

Ask for a tier in plain words ("quick answer", "go deep on this"). The run's map and each reader's raw
return land under `./research/<slug>/`, so a long run is auditable after the fact.

**Why there is no unbounded mode.** Two measured limits: a keyless, scraped search backend soft-blocks
past a handful of concurrent requests and returns an empty list indistinguishable from "no sources", so
an uncapped fan-out reports its own traffic as a research gap; and past a floor, more sources buy
confidence rather than accuracy. The rounds stop on a computed signal instead (`bad frontier-observe`).

> Want the latest unreleased build? Install from source: `pipx install git+https://github.com/LeventySeven/badresearch.git`

### Updating

Already installed? Upgrade the CLI **and** re-register the skill so both are current:

```bash
# From PyPI (pipx or uv — whichever you installed with)
pipx upgrade bad-research      # or: uv tool upgrade bad-research
bad install                    # refresh the /bad-research skill + agents in ~/.claude

# ...or track the latest source
pipx install --force git+https://github.com/LeventySeven/badresearch.git
bad install
```

`bad install` is idempotent — re-run it any time after upgrading the CLI to pull the newest
skill + agents.
Confirm with `bad --version`.

## What it does

A tier-adaptive pipeline turns a question into an audited, fully-cited report, and
every fetched source lands in a persistent, searchable vault that compounds across
sessions. Keyless by design:

- **Search** — the host `WebSearch` tool + DuckDuckGo + 7 scholarly APIs, fused and reranked by the host model.
- **Content** — a native fetch-and-clean pipeline (readability → markdown → optional LLM clean), SSRF-guarded.
- **Browse** — an agentic observe → act → extract loop driven by a local, keyless headless browser.
- **Retrieve** — SQLite FTS5/BM25 by default (no model required), with an optional local neural lane.
- **Ground** — every factual sentence must carry a source citation, and a deterministic ship-gate **blocks** any uncited claim. Fabricated quotes are caught for free by a byte-identity check; the harder paraphrase-faithfulness cases are judged by the host model (an optional `[local]` cross-encoder upgrades this to NLI).

## Reporting engine bugs

An engine/CLI defect — a missing or broken subcommand, a crash, a slim-build capability
gap — belongs in **this repo's** issue tracker, not in whatever downstream project
happened to be driving the run. File a fresh issue here with the build version and the
exact failing command; don't rely on a cross-org `gh issue transfer` to relocate it from
a downstream repo (transfers across organizations are unreliable and lose the report).
Keep the bug where the fix lives. This is guidance for **people**: the research agent
itself only surfaces the defect in its final report, and never files anything on its own.

## How it works & where the patterns came from

Bad Research takes hyperresearch as its base and enhances each stage with patterns
drawn from the best deep-research systems — Perplexity, Gemini, Firecrawl, Stagehand,
AgentQL, and others — reimplemented to run **keyless** on the host model. The full
write-up, stage by stage with provenance, is in
[**docs/HOW_IT_WORKS.md**](docs/HOW_IT_WORKS.md).

MIT licensed.
