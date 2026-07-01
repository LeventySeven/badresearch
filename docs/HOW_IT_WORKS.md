# How Bad Research was built — and where the patterns came from

Bad Research is a **fork-and-enhance of [hyperresearch](https://github.com/jordan-gibbs/hyperresearch)**.
Hyperresearch gave us the foundation: a tier-adaptive, ~16-stage research pipeline
driven as a Claude Code skill, with a persistent markdown + SQLite vault that
compounds knowledge across sessions. We kept that whole spine and enhanced each
stage with the best pattern we could find for it — the approaches that the leading
deep-research and web-agent systems are known for — and reimplemented every one of
them to run **keyless**, on the Claude Code host model, with no third-party API key.

This document is the honest tour: each stage, the pattern it borrows, and who
pioneered that pattern. Nothing here needs an API key; where a pattern was
originally a paid product, we adopted the *idea* and rebuilt it on the host model
and open tooling.

---

## How you run it — two keyless entrypoints

Bad Research is a **Claude Code skill**, and that is how you use it — keyless, with a
model driving the pipeline:

1. **Interactive.** Type `/bad-research <your query>` in a Claude Code session.
2. **From a subagent.** A Claude Code **Task** subagent invokes the `bad-research`
   skill programmatically.

Both are keyless: the *host model* (your Claude Code session, or the subagent's model)
is what reads sources, reranks, drafts, critiques, and grounds every claim. No
third-party API key is ever required.

**The boundary — what the `bad` CLI is (and isn't).** The `bad` CLI is a set of
**deterministic helpers only** — the funnel, retrieval/rerank, grounding gates, and
vault ops. It never calls a model on its own. There is exactly ONE key-requiring
path: the headless `run_query` synthesis that `bad calibrate` bridges to — the
**off-mission calibration/benchmark harness**, not how you run research. Run it
without a key and it degrades to an honest, stitched, best-effort report led by a
banner that points you back to the keyless skill; it never crashes and never
fabricates.

**Why there is no "host-model provider" for the CLI.** A model-less subprocess cannot
call the host model. The `bad` CLI runs *outside* the Claude Code session, so it has
no channel to the model driving that session — this is an architectural truth, not a
missing feature. There is no `HostModelProvider`, and one cannot be added from a plain
subprocess. The keyless answer is to run research *through the skill*, where a model
is already in the loop.

---

## The build approach

1. **Start from hyperresearch.** Its pipeline, vault, skill packaging, and grounding
   gate are the base. We did not rewrite what already worked.
2. **Enhance stage by stage.** For each stage — search, content, browse, retrieval,
   reranking, grounding, the control loop — we took the strongest known pattern and
   wired it in behind a clean seam.
3. **Keyless by design.** Every enhancement is implemented on the host model (via a
   single `LLMProvider` seam) plus open-source libraries and optional local CLIs.
   No vendor key is ever required to install or run; `bad doctor` proves it.
4. **Built with reviews.** Each stage was implemented and then independently
   reviewed for correctness, security (e.g. SSRF), and faithfulness to the pattern
   before it landed.

---

## The stages and their provenance

### Search — wide recall, then a relevance-gated loop
*Pattern from: Perplexity.* Perplexity's deep search popularised the loop of
casting a wide net across many sources and then **re-querying until the results are
actually good enough** rather than answering from the first page. We implement that
as a "retrieve-until-good" loop: a relevance gate (default 0.70) and a minimum
pass-fraction (0.30) decide whether to expand and search again, up to a small round
cap. Recall comes from the host `WebSearch` tool + DuckDuckGo (`ddgs`), with an
optional self-hosted SearXNG if you have one.

### Scholarly verticals — go to the primary sources
*Pattern from: the open scholarly ecosystem.* For research-grade questions, general
web search isn't enough, so we route to the primary academic APIs directly —
**arXiv, OpenAlex, Crossref, Semantic Scholar, Europe PMC, PubMed, and Wikipedia**.
All are free and keyless; an intent classifier sends a query to the right ones
(medical → PubMed/Europe PMC, academic → OpenAlex/arXiv, etc.).

### Rank fusion — merge many ranked lists fairly
*Pattern from: Reciprocal Rank Fusion (a standard IR technique, used by systems like
Exa).* When several sources each return their own ranked list, we combine them with
**RRF (k = 60)** so no single source dominates and consensus results rise to the top.

### Reranking — a cross-encoder pass for precision
*Pattern from: Cohere Rerank.* Cohere popularised dropping a cross-encoder reranker
in front of the final results to sharply improve precision. We adopt the pattern but
keep it **keyless**: the **host model itself** scores each candidate against the
query with one frozen rubric prompt. It's a frontier cross-encoder you already have —
≥ rerank-API quality at zero dollars. (An optional `[local]` extra adds an offline
`ms-marco-MiniLM` cross-encoder for users who want it.)

### Content extraction — clean signal out of messy HTML
*Pattern from: Firecrawl.* Firecrawl is known for turning arbitrary pages into clean,
model-ready markdown by stripping boilerplate (nav, ads, cookie banners) before
conversion. We rebuilt that natively: a readability/pruning pass strips chrome,
HTML→markdown conversion preserves citations and structure, PDFs go through a PDF
text extractor, and a final optional LLM-clean pass tidies what's left — all with a
strict anti-prompt-injection preamble so page content is always treated as data.
Every fetch is **SSRF-guarded** (private-IP/metadata-endpoint denylist, re-validated
on each redirect).

### Agentic browse — observe, act, extract
*Pattern from: Stagehand / Browserbase.* The modern web-agent pattern is a loop of
**observe** the page's accessibility tree → **act** (click/type/navigate) → **extract**
structured data, with the model choosing actions against stable element references.
We use Stagehand's well-known observe/act/extract prompts as the loop's brain — but
instead of a paid cloud browser, we drive **[vercel's `agent-browser`](https://github.com/vercel-labs/agent-browser)**,
a local, keyless headless-Chrome CLI (with `lightpanda` as a fast optional engine).
The model only ever acts on element references that exist in the live page snapshot,
so it can't be steered onto a hallucinated element.

### Element querying — ask the page in a query language
*Pattern from: AgentQL.* AgentQL's idea is a small declarative query language for
locating page elements by role/intent rather than brittle CSS selectors. We ported a
parser for that query style so the browse layer can resolve elements the same way —
again, purely local, no service.

### Retrieval — hybrid lexical + (optional) semantic
*Pattern from: Perplexity-style hybrid retrieval.* The robust pattern is to blend
keyword and semantic recall rather than rely on either alone. Our **default is
keyless and model-free**: SQLite **FTS5/BM25** lexical recall, three-tier rank
fusion, and a lexical semantic cache (0.85 overlap) — fast, deterministic, and it
runs anywhere. If you install the `[local]` extra, a dense vector lane (a local
`bge` embedder + **LanceDB** ANN, the pattern LanceDB is built for) is used
automatically on large corpora, fused with BM25 via RRF.

### Grounding — cite or don't say it
*Pattern from: Gemini's grounding & recitation guarantees.* Gemini is known for
binding generated claims back to retrieved evidence and guarding against verbatim
recitation. Every factual sentence must carry a source citation, and a deterministic
ship-gate **blocks** any uncited claim. Fabricated quotes are caught for free by a
byte-identity check; the harder paraphrase-faithfulness cases are judged by the host
model (an optional `[local]` cross-encoder upgrades this to NLI).

Being honest about what the *keyless* layer decides on its own versus what it defers:
the deterministic guards **affirmatively catch** the mechanical contradictions — a
flipped number/date, a flipped negation, and a flipped directional/antonym term (and
an unsupported appended fact, whose new number trips the same numeric check). A pure
**paraphrase-contradiction** that keeps the numbers, negation, and direction intact is
*not* decided keyless — it carries no deterministic signal, so the verifier escalates
it to the host-model judge (or, with no host wired, emits a `needs_host_judgment`
worklist the host model resolves inline). That escalation is a deferral, not a catch.
A reproducible harness measures exactly this: `bad grounding-recall` mutates
known-grounded claims and reports a **100% keyless affirmative catch-rate on the
number / negation / antonym / unsupported-append bands and an explicitly-disclosed 0%
on the paraphrase-contradiction band** (which is escalated to the host judge), so the
published figure is a per-mutation rate, never a "we catch everything" absolute. A
recitation gate flags any sentence that copies a source too closely (a 12-word verbatim
run or >50% overlap) — with a carve-out only for genuine, attributed direct quotes. The
per-claim grounding ledger (verdict, confidence band, score, deciding tier) is itself
surfaceable as a shareable sidecar via `bad grounding-surface` — a per-claim
auditability surface no hosted deep-research tool exposes.

### Reasoning-effort dial — spend compute where it matters
*Pattern from: OpenAI's reasoning-effort control.* We expose a `--reasoning-effort`
continuum (minimal → low → medium → high) that maps to route, model tier, fetch
budget, and a token ceiling, with a defined degrade order so the system spends more
only when the question warrants it.

### Confidence-band hedging — say how sure it is
*Pattern from: calibrated-uncertainty practice in research assistants.* The final
report's claims carry a confidence band derived from grounding scores, so
low-confidence statements are hedged rather than asserted flatly.

---

## What's keyless vs. optional

| Capability | Default (keyless, no setup) | Optional enhancement |
|---|---|---|
| Inference | Claude Code host model | — |
| Web search | host `WebSearch` + DuckDuckGo + 7 scholarly APIs | self-hosted SearXNG |
| Reranking | host-model cross-encoder | `[local]` `ms-marco-MiniLM` |
| Retrieval | SQLite FTS5/BM25 | `[local]` `bge` + LanceDB dense lane |
| Content render | native httpx + readability | `crawl4ai` JS render (bundled) |
| Browse | — | `agent-browser` / `lightpanda` CLIs |
| Media transcripts | — | `yt-dlp` CLI |

Everything in the left column works the moment you `pip install bad-research`. The
right column is detected at runtime (`bad doctor` shows the status) and degrades
gracefully when absent — it never blocks a run.

---

*Built on the shoulders of [hyperresearch](https://github.com/jordan-gibbs/hyperresearch),
with patterns from Perplexity, Gemini, Cohere, Firecrawl, Stagehand/Browserbase,
AgentQL, LanceDB, and the open scholarly web — all reimplemented keyless.*
