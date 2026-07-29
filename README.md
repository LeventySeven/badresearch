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

A **keyless** deep-research agent that runs as a Claude Code skill — a
fork-and-enhance of [hyperresearch](https://github.com/jordan-gibbs/hyperresearch).
It searches wide, filters garbage, grounds every claim to a source, and needs
**zero API keys**: the Claude Code host model supplies all inference, exactly like
hyperresearch. Optional local CLIs and a `[local]` neural extra are enhancements,
never requirements.

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

`bad install` writes the entry skill to `~/.claude/skills/bad-research/`; the per-step
skills install lazily on first use. For a project-local install instead of global, run
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

It scales to the question: a simple lookup gets a fast cited answer in minutes; a broad or
contested one runs the full adversarially-reviewed pipeline (~1.5–2.5 h). The final report
and every fetched source land in a vault under `./research/` that compounds across sessions.

### Pick the depth (it auto-scales, or force it)

By default the skill **auto-routes** — a simple, bounded question takes the **fast** route
(a quick cited answer, minutes); a broad or contested one takes the **full**
adversarially-reviewed pipeline (~1.5–2.5 h). You can steer it:

- **Want a thorough report without the multi-hour wait?** The **fast** route is the sweet
  spot — its breadth branch fans out K parallel researchers over a wide multi-source browse,
  then writes a sectioned, fully-cited answer in minutes. Force it with `bad route --apply
  --fast` if the auto-router picked `full` and you want the quicker take. If you're just
  trying Bad Research out, start here.
- **Dial the effort** with `--effort minimal|low|medium|high` to nudge the route and per-step
  fan-out (`minimal`/`low` bias toward fast; `medium`/`high` toward full).

On an interactive run the skill announces the chosen route and its rough ETA before it
commits to a long job (and for `full` it shows the editable plan first), so you're never
surprised by a 2-hour job you didn't want. The route is decided from the step-1
decomposition and shown by that up-front in-skill route announcement — so you see which
route a query takes before any long work starts.

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
entry skill + agents (the per-step skills refresh lazily on the next `/bad-research` run).
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

## How it works & where the patterns came from

Bad Research takes hyperresearch as its base and enhances each stage with patterns
drawn from the best deep-research systems — Perplexity, Gemini, Firecrawl, Stagehand,
AgentQL, and others — reimplemented to run **keyless** on the host model. The full
write-up, stage by stage with provenance, is in
[**docs/HOW_IT_WORKS.md**](docs/HOW_IT_WORKS.md).

MIT licensed.
