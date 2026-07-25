---
name: bad-research-2-width-sweep
user-invocable: false
description: >
  Step 2 of the Bad Research pipeline — multi-perspective search planning
  (breadth / depth / adversarial lenses) plus parallel fetcher waves that build a
  curated, coverage-checked source corpus in the vault.
---

# Step 2 — Width sweep

**Tier gate:** Runs for ALL tiers. For `light` tier: skip academic APIs, target 12–20 sources, limit to 2–3 fetcher batches. For `full`: run the full procedure below.

**Goal:** achieve comprehensive topical coverage — every atomic item from the decomposition must have at least 3 supporting sources by the end of this step. Target 40–80 curated sources for `full` tier.

---

## Recover state

Read these inputs:
- `research/scaffold.md` — vault_tag (in Run config), modality
- `research/prompt-decomposition.json` — atomic items, sub_questions, entities, pipeline_tier
- `research/temp/coverage-matrix.md` — verbatim query phrases mapped to atomic items
- `research/query-<vault_tag>.md` — canonical research query (GOSPEL)

---

## Step 2.1 — Multi-perspective search planning

Before spawning any fetchers, produce a **search plan** that maps the decomposition to concrete searches from **three independent perspectives**. This is the single highest-leverage step for comprehensiveness — an ad-hoc search finds 40 sources on the same 3 sub-topics; a multi-perspective planned search distributes sources across all atomic items from angles a single researcher would miss.

1. **Read the decomposition.** Extract every `sub_question` and every `entity` with its `required_fields`.

2. **Generate searches from three lenses.** For EACH atomic item, generate searches from all three perspectives:

   **Lens A — Breadth coverage (systematic):**
   - One search for the core factual content of that item
   - One search for recent developments / state-of-the-art (last 2 years)
   - One search for each named entity or sub-concept within the item
   - Goal: no atomic item left uncovered. Cast wide.

   **Lens B — Citation-chain depth (academic/canonical):**
   - Academic API queries (Semantic Scholar, arXiv, OpenAlex, PubMed) for each item with research literature
   - Searches targeting canonical/seminal works, foundational papers, authoritative reports
   - Searches for the upstream sources that derivative commentary cites ("original study", "primary data", "foundational paper")
   - Goal: find the load-bearing sources that secondary commentary is built on.

   **Lens C — Adversarial/contrarian (dialectical):**
   - "criticism of X", "limitations of X", "problems with X", "why X doesn't work" for each item
   - Searches for competing frameworks, alternative explanations, dissenting experts
   - Searches for failure cases, negative results, counter-examples
   - At least one "X is wrong" or "against X" search per major atomic item
   - Goal: ensure the corpus includes the strongest case AGAINST the emerging consensus.

   **Lens D — Period-pinned primary sources (MANDATORY when `time_periods` is non-empty in the decomposition):**
   - For EVERY entry in `prompt-decomposition.json -> time_periods`, generate at least one search that targets the **primary filing for that exact period** — not the most recent filing, not narrative commentary, not earnings-call summaries.
   - **SEC EDGAR (US public companies):** target the filing index for the named period. Example queries: `site:sec.gov 10-Q "period ended September 30, 2024" <company>` or `site:sec.gov/cgi-bin/browse-edgar <CIK> 10-Q dateb=20241231`. Open the EDGAR filing-history page directly when CIK is known.
   - **Companies House (UK):** target the filing-history view, NOT the search index. Example: `site:find-and-update.company-information.service.gov.uk <company> filing-history`. Then fetch the specific accounts PDF made up to the named period.
   - **Earnings releases / press releases:** target the dated press release for that period, not coverage of it. Example: `<company> "third quarter 2024" results press release`.
   - **Government / central-bank releases, regulatory disclosures, statutory accounts:** target the publication for the exact reporting period.
   - **Earnings-call transcripts are insufficient on their own.** Transcripts narrate already-rounded numbers ("revenue grew about 27%"); rubrics demand the tabular line items from the filing itself. If the prompt names a fiscal period, the search plan MUST include a query for the filing PDF, not just the transcript.
   - Goal: every period in `time_periods` has at least one search that, if successful, fetches the filing's tabular data — not a paraphrase of it.

   **Query reformulation (per atomic item, Step 2.1):** For EACH sub-question, before searching, generate **3–5 synonym/paraphrase alternative phrasings** of the query (and any time a sub-question's initial Lens-A searches return fewer than 3 candidate URLs, generate them then if not already done). Example: "China fintech regulation" → "Chinese financial technology oversight", "PRC fintech compliance rules", "digital finance regulation China", "online lending rules Beijing". Write the alternatives directly into the search-plan table with `reformulation` in the Type column. This closes single-phrasing recall failures: one phrasing can miss sources another phrasing surfaces. The funnel's `_LENS_SUFFIXES` handles programmatic expansion — this adds the human-paraphrase layer on top.

3. **Write the combined search plan to `research/temp/search-plan.md`** — a table with a `Lens` column:
   ```markdown
   | Atomic item | Search query | Type | Lens | Target |
   |---|---|---|---|---|
   | Sub-Q1 | "China financial industry growth trends 2025" | web | breadth | factual |
   | Sub-Q1 | "China financial sector structural risks" | web | adversarial | contrarian |
   | Sub-Q1 | "financial repression China scholarly analysis" | academic | depth | canonical |
   | Entity: PE | "China private equity returns academic study" | academic | depth | canonical |
   ```

   Plan typically has **40–100 planned searches** for a `full` query.

4. **Search gap check.** Cross-check the search plan against `research/temp/coverage-matrix.md`. For every row in the coverage matrix, verify at least one search in the plan targets that query phrase's atomic item. Re-read the verbatim query and check: is there any significant topic, entity, or category in the query that has ZERO rows in the search plan?

   Common failure modes this catches:
   - Decomposition correctly listed "rugged tablets" but search plan has no queries for tablet manufacturers, enterprise mobility, or field-service devices
   - Query mentions "Southeast Asia" but all regional searches target only "North America" and "Japan/Korea"
   - Query says "SaaS applications" but every search is about "payment terminals"

   If gaps exist: add the missing searches to the plan NOW, before proceeding. Do NOT proceed to fetching with known search gaps — a missing search now becomes a missing section in step 10.

5. **Execute searches from ALL three lenses.** Do not shortcut by running only Lens A. The adversarial and depth lenses produce qualitatively different URLs that breadth searching misses.

6. **Minimum adversarial coverage:** at least **5 adversarial searches total**. The dialectic critic will punish one-sided coverage.

---

## Step 2.2 — Run the scraper funnel (PREFERRED)

The width-sweep no longer hand-dispatches fetcher batches. It hands the search
plan to the deterministic six-stage funnel (fan-out → dedup → rank → read
Tier 0→3 → filter junk → chunk+store → rerank). The model reads ONLY the
funnel's `top_chunks` — never raw pages. This is the "disk is memory, context
is scratchpad" invariant: sources scale (45→80) while context stays flat.

```bash
bad funnel-gather --query-file research/query-<vault_tag>.md \
    --search-plan research/temp/search-plan.md \
    --mode <light|full> --vault-tag <vault_tag> \
    --effort <minimal|low|medium|high> --json
```

Returns `FunnelEnvelope` JSON:
`{note_ids, top_chunks, n_read, n_stored, ok, degraded, degraded_reasons, warnings, provider_outcomes}`.
- `note_ids` — sources written to the vault this run.
- `top_chunks` — the reranked chunks (≤ TOP_CHUNKS for the mode) the model may
  read. Read these; do NOT re-read full pages.
- `n_read` ≤ 80 (the load-bearing read ceiling — the funnel enforces it
  internally; reading past it degrades synthesis).

**CHECK `degraded` BEFORE READING ANYTHING ELSE.** The envelope distinguishes a
run that found nothing from a run that *could not search*:

| Envelope | Meaning | What you do |
|---|---|---|
| `ok:true, degraded:false`, `note_ids` non-empty | normal | proceed to Step 2.5 |
| `ok:false, degraded:true` (exit 3), reason `no_search_provider_available` | every search lane refused to run | **STOP. Do NOT gap-fetch, do NOT draft.** |
| `ok:false, degraded:true` (exit 3), reason `no_search_results_from_any_provider` | every lane ran and returned zero hits across the entire plan | **STOP.** Almost always an outage, not an empty topic — see below |

There is deliberately **no** "ran fine, found nothing" success row. Zero hits
across every lane and every query (12 in light, up to 100 in full) is
near-impossible for a well-formed query, and the keyless providers swallow
transport errors into empty results — so this layer cannot tell a dead network
from a sourceless topic. It is reported as degraded on purpose: a false alarm
costs one honest message, whereas proceeding would ship a report asserting a
research gap that is really an outage.

When `degraded` is true, report the `degraded_reasons` and `provider_outcomes`
to the user, say plainly that the corpus could not be built, and stop.

**Also check `warnings` even when `ok:true`.** It is orthogonal to `degraded`: a
run can succeed while not doing what you asked. `search_plan_empty_or_unparseable`
means your plan did not apply and the generic fallback expansion ran instead —
the corpus is NOT plan-driven, so regenerate the plan table and re-run rather
than treating the coverage as if your lenses had fired.

When `degraded` is true, a gap-fetch retry hits the same dead providers and
returns empty again, and the run then reports a *content* gap that is really an
*infrastructure* failure — a fabricated research finding. Instead: report the
`degraded_reasons` and `provider_outcomes` to the user, say plainly that the
corpus could not be built and why, and stop. A thin corpus is recoverable; a
report that claims "no sources exist" when the search stack was down is not.

**Fan-out constants are indexed by mode** (the funnel applies them internally
via its `FunnelConfig`): `light` = 12–20 queries / 1–2 providers / read top
12–20; `full` = 40–100 queries / 2–4 providers / read top 60–80.

After the funnel returns, jump to **Step 2.5** (coverage check) — the funnel
already executed the search/fetch/dedup/filter/store waves that the legacy
hand-dispatch steps 2.2(legacy)–2.4 describe.

---

## Step 2.2 (legacy) — Execute searches and build URL queue

> Kept as a fallback for runs where the funnel CLI is unavailable. Prefer the
> `bad funnel-gather` path above; this hand-dispatch procedure is the same
> work done manually.


1. **Academic APIs first.** For topics with a research literature, hit Semantic Scholar / arXiv / OpenAlex / PubMed BEFORE web search. Academic APIs return citation-ranked canonical papers.

2. **Web searches from the plan.** Execute ALL planned searches across all three lenses. Aim for **80–120 candidate URLs** before deduplication for `full` tier.

3. **Build and deduplicate the master URL queue.** Remove exact-URL duplicates. Remove obvious junk domains. The deduplicated queue should have **60–100 URLs** for `full` tier.

   **Wikipedia SOURCE HUB rule:** Include Wikipedia URLs in the queue — they're valuable for discovery — but treat them as SOURCE HUBS, not as citable sources. When a fetcher processes a Wikipedia article, it extracts the references/citations Wikipedia links to. Those primary sources go into Wave 2 (or the same wave if capacity permits). Wikipedia itself is NEVER cited in the final report.

4. **Partition the queue into non-overlapping batches.** Split the master queue into **10–12 batches** of **8–12 URLs each**. Each batch goes to exactly ONE fetcher. **Zero overlap.**

---

## Step 2.3 (legacy) — Hand utility scoring and selection

> **FALLBACK ONLY — do NOT run this on the preferred path.** This hand-scored
> table is consumed by the legacy hand-dispatch fetcher waves (Step 2.4) and is
> live ONLY when `bad funnel-gather` (Step 2.2) is unavailable or was skipped.
> On the preferred funnel path the funnel does its OWN deterministic rank →
> read Tier 0→3 → filter junk → chunk+store → rerank and returns `top_chunks`;
> it never reads this eyeball table, so producing it there is wasted work.
> **If you ran Step 2.2 (`bad funnel-gather`), SKIP straight to Step 2.5.**
>
> **Gate:** run ONLY when the funnel CLI is unavailable/skipped AND tier is
> `full` (always skip for `light`).

When the funnel is unavailable, score each candidate URL by hand on six
dimensions (0–3 each, max composite 18) before batching:

1. **Authority (0–3):** Primary data / government / academic (3) > institutional report (2) > quality journalism (1) > blog (0)
2. **Novelty (0–3):** Unique domain or perspective (3) > partially overlapping (1) > redundant (0)
3. **Stance diversity (0–3):** Adversarial / contrarian (3) > mixed-stance (2) > neutral (1) > same-stance majority (0)
4. **Coverage (0–3):** Targets uncovered atomic item (3) > thin item (2) > adequate item (1) > well-covered (0)
5. **Redundancy (0–3):** Likely novel content (3) > possibly overlapping (1) > almost certainly a rewrite (0)
6. **Freshness (0–3):** For temporal topics: last 12 months (3), 1–3 years (2), 3–5 years (1), older (0). For foundational topics: canonical/seminal (3), recent derivative (1).

**Selection rule:** Rank by composite utility score. Select the top N URLs (where N = batch capacity × batch count). Hard constraint: every atomic item must have ≥3 candidate URLs before low-utility URLs from well-covered items are included. (On the preferred path the funnel's internal rank/rerank supersedes this hand ranking.)

Write to `research/temp/scored-urls.md`.

---

## Step 2.4 (legacy) — Parallel fetcher waves

> **FALLBACK ONLY.** Consumes the Step 2.3 hand-scored batches. Run ONLY when
> `bad funnel-gather` (Step 2.2) is unavailable/skipped. If you ran the funnel,
> it already executed these fetcher/dedup/filter/store waves — SKIP to Step 2.5.

**Wave 1 (main wave):** Spawn **10–12 fetcher subagents in ONE message** — true parallel execution. Each fetcher gets its own non-overlapping batch.

**Subagent type:** `bad-research-fetcher`

**Spawn template (the 7-field delegation contract — see entry-skill spawn contract).**
The four added contract fields — `objective`, `output_shape`, `tools_allowed`,
`stop_conditions` — appear in every fetcher prompt as the uppercase blocks below:
```
subagent_type: bad-research-fetcher
prompt: |
  RESEARCH QUERY (verbatim, gospel):
  > {{paste contents of research/query-<vault_tag>.md}}

  QUERY FILE: research/query-<vault_tag>.md

  PIPELINE POSITION: You are step 2 (width-sweep fetcher) of the
  Bad Research pipeline. The orchestrator partitioned the URL queue into
  non-overlapping batches; you fetch ONLY the URLs in your batch. After you
  return, the orchestrator runs a coverage check (step 2.5) and may dispatch wave 2.

  INPUTS:
  - vault_tag: <vault_tag>
  - urls: [<batch URLs, exactly as assigned>]
  - batch_id: <number>

  OBJECTIVE: fetch and ground every URL in your batch into vault notes tagged
  <vault_tag>, chasing 3–8 primary sources via citation chains.

  <!-- source-quality-signals -->
  SOURCE-QUALITY NEGATIVE SIGNALS (down-weight or FLAG, do NOT suppress):
  As you read each source, judge it against this list (Anthropic worker-prompt
  discipline — the things a regex/domain check CANNOT see). FLAG the source; do NOT
  silently drop it (the lead reconciles flags downstream — flag, don't suppress):
  - news aggregators rather than original sources       -> flag `aggregator`
  - false authority (cites authority it lacks / misattributes)  -> `false_authority`
  - passive voice with nameless sources ("experts say", "it is reported")  -> `nameless_source`
  - general qualifiers without specifics ("many", "often", "significant")  -> `vague_qualifier`
  - unconfirmed reports (rumor not yet verified)        -> flag `unconfirmed`
  - marketing language / spin language (promotional, sales copy)  -> `marketing_spin`
  - speculation presented as finding, incl. future-tense predictions ("could", "may", projections) stated as things that happened  -> flag `speculation`
  - cherry-picked data (selective evidence, no counter-data)  -> `cherry_picked`
  A source with NONE of these gets no flags (it is unchanged). A primary filing or
  peer-reviewed paper is almost never flagged; a vendor "X is the best" listicle on a
  good domain SHOULD be flagged `marketing_spin` even though its domain tier is high.

  READ FIGURES (you are natively multimodal): if a source's substance is in a
  figure/chart/table-image, or in a scanned (text-layerless) PDF, the text layer is
  empty and the fetch path has already saved the rendered pixels as a PNG asset bound
  to the note. Resolve it with `bad assets list --note-id <note-id> --json`, then
  `bad assets path <asset-id>`, and use the `Read` tool on that PNG to transcribe the
  data into the note VERBATIM (the numbers exactly as plotted/printed), citing it as a
  figure. The transcription you write into the note body becomes the claim's
  `quoted_support`, so the figure-derived number is grounded and verifiable like any
  text claim — NEVER eyeball a number you did not Read off the saved image.

  OUTPUT_SHAPE: for each note, emit the claims JSON the binding consumes —
  a JSON array of {claim, note_id, quoted_support, char_start, char_end,
  source_quality_flags}. `source_quality_flags` is a (possibly empty) JSON array of
  the flag strings above — e.g. [] for a clean primary, ["marketing_spin"] for a
  vendor spin page. This field is ADDITIVE: downstream consumers (the anchor binding,
  the uncited-gate) ignore unknown/extra fields. The flags are reconciled at SYNTHESIS:
  the drafter/synthesizer down-weights and caveats any flagged source (a flagged claim
  must be corroborated by an unflagged source or explicitly hedged, and is never the
  lead) — flag, don't suppress. There is NO deterministic penalty; this is the
  worker-flags / lead-reconciles discipline, applied in prose at draft+synthesis time.

  TOOLS_ALLOWED: ["fetch_url", "web_search", "execute_python", "Read"]

  STOP_CONDITIONS: halt when every assigned URL is fetched OR you reach the
  fetcher tool-call cap (FETCHER_TOOLCALL_CAP: 10 light / 20 full tool calls)
  OR FETCHER_TIMEOUT_S (300s) elapses — then return what you have. Do NOT keep
  searching for nonexistent sources. Hard kill at SUBAGENT_SOURCE_KILL (100 sources).
```

**Orchestrator-side wave deadline.** The host cannot interrupt a fetcher mid-loop.
So between waves, check elapsed wall-clock: if a fetcher wave exceeds
FETCHER_TIMEOUT_S (300s), proceed to step 2.5 with the results that returned —
do not block on a slow fetcher.

**CRITICAL: no token waste.** Each fetcher gets ONLY its batch. No fetcher searches for new URLs or duplicates another fetcher's work. If a fetcher finishes early, it's done.

**CRITICAL: never emit bare text while waiting.** In `-p` mode, a text-only response triggers `end_turn`.

**Use wait time to think.** While subagents are working, write evolving thoughts to `research/temp/orchestrator-notes.md`:
- What patterns are emerging from sources?
- What tensions or contradictions do you expect?
- What's the strongest thesis forming? What could overturn it?
- How will atomic items map to sections?
- What's the narrative arc?

Append a few lines with `Edit` or `Write` every 30-60 seconds. Productive thinking time AND keeps the turn alive.

**Vault count check** — once every 60 seconds max:
```bash
PYTHONIOENCODING=utf-8 bad search "" --tag <vault_tag> --json | python -c "import sys,json; d=json.load(sys.stdin); print(f'Notes in vault: {len(d.get(\"data\",{}).get(\"results\",[]))}')"
```

The wave is done when the vault note count is ≥80% of total URLs queued.

---

## Step 2.5 — Coverage check (MANDATORY)

After the funnel (Step 2.2) returns its `FunnelEnvelope`, run the coverage check
before proceeding. The funnel returns reranked chunks, NOT a coverage map, so
the orchestrator computes coverage by mapping the returned `note_ids` → atomic
items (same well/adequate/thin/uncovered logic as before):

1. **List fetched sources:** use the funnel envelope's `note_ids` (or
   `bad search "" --tag <vault_tag> --json`) — count substantive (non-deprecated) notes.

2. **Map sources → atomic items.** For each atomic item in the decomposition, identify which fetched sources serve it. Mark each item as:
   - **Well-covered** (4+ relevant sources)
   - **Adequate** (2–3 sources)
   - **Thin** (1 source)
   - **Uncovered** (0 sources)

3. **Gap fetch — a second, smaller funnel call for gaps.** For every `thin` or
   `uncovered` item, fire one more, gap-targeted `funnel-gather` (do NOT
   hand-dispatch fetchers):
   ```bash
   bad funnel-gather --query-file research/query-<vault_tag>.md \
       --search-plan research/temp/gap-search-plan.md \
       --mode <light|full> --vault-tag <vault_tag> --json
   ```
   This wave is smaller (a gap-targeted query plan) but surgically targeted at
   the thin/uncovered items.

4. **Write coverage report** to `research/temp/coverage-gaps.md`:
   - List every atomic item with its coverage status and source count
   - Any item still at 0 sources after Wave 2 is a genuine gap — flag it prominently

**Do NOT skip the coverage check.** Comprehensiveness scores directly with how many atomic items have multi-source coverage.

---

## Step 2.6 — Evidence redundancy audit

**Tier gate:** SKIP for `light`. Run for `full`.

**Goal:** detect when N sources are really 1 source in N outfits.

1. **Collect all claims.** Read `research/temp/claims-<note-id>.json` for every non-deprecated note tagged `<vault_tag>`. If no claim files exist, skip this step.

2. **Cluster by content overlap.** Sources sharing >60% of their `quoted_support` passages are likely derivative.

3. **Cluster by citation ancestry.** Use `suggested-by` links in the vault graph.

4. **For each cluster, identify the canonical upstream source.** Tag derivative sources with `derivative-of`. Do NOT deprecate them — discount them in coverage counting.

5. **Write `research/temp/redundancy-audit.md`** — clusters, adjusted coverage counts, atomic items dropping below 2 → flag for Wave 3.

6. **Wave 3 fetch (conditional).** If any atomic item's independent source count drops below 2, run targeted searches for INDEPENDENT sources. Spawn 2-3 fetchers.

---

## Step 2.7 — Distill each round into reflections (distilled-reflection memory)

**Why this step exists:** between rounds the loop must carry only **distilled
reflections**, never the raw source corpus. Re-reading every fetched note body on
each re-retrieve round makes inter-round token growth *quadratic*
(`n·m·(m+1)/2`); carrying a compact distilled memory keeps it **linear** (`n·m`) —
a ~−66% token win (Tavily). The raw bodies stay on disk in the vault, retrievable
by `note_id`; they are NOT re-injected until synthesis (step 10/11), and even then
only for the `note_id`s a section will cite. On the legacy hand-dispatched fetcher path
the distilled memory is `research/temp/claims-<note-id>.json` of shape
`{claim, note_id, quoted_support, char_start, char_end}` (claims already separated from
the raw body); on the **preferred `funnel-gather` path there are no per-note claims files** —
the funnel's reranked `top_chunks` ARE the distilled, separated-from-raw-body memory that
plays the same role. Either way, the raw bodies are not re-injected until synthesis.

After each fetch wave (the funnel return in Step 2.2, and again after each gap
fetch in Step 2.5), **distill, then drop the raw body from working context**:

1. **Distill each kept source to ≤3 claim bullets + its `note_id`.** Read the
   source's `research/temp/claims-<note-id>.json` (the distilled claims — NOT the
   raw note body). Pick the ≤3 most load-bearing claim bullets for the current
   sub-question. The bullets are distilled claims, never raw prose.

2. **Append one record per round / sub-question to `research/temp/reflections.md`**
   (append-only — never overwrite a prior round's record; that is what keeps
   growth linear). Each record:
   ```markdown
   ### Round <n> — <sub_question>

   **Key findings (distilled):**
   - <≤3 distilled claim bullets, each traceable to a claims-*.json claim>

   **Open gaps:**
   - <atomic items still thin/uncovered, contradictions still unresolved>

   **Cited notes (vault):** <note_id>, <note_id>, …
   <!-- reflection {"round": <n>, "sub_question": "...", "key_findings": [...], "open_gaps": [...], "cited_note_ids": [...]} -->
   ```
   The deterministic helper `retrieval/reflections.py` (`ReflectionLog.append`)
   writes this block; the trailing HTML comment is the machine-parseable payload.

3. **DROP the raw note body from working context.** Once a source is distilled to
   its reflection bullets, do NOT keep its raw body (or the funnel's full
   `top_chunks` text) in context. The raw body stays on disk in the vault, keyed
   by `note_id` — that is the "disk is memory, context is scratchpad" invariant.

4. **The re-retrieve decision + next-round query planning read
   `research/temp/reflections.md` + its `open_gaps` — NOT the raw corpus.** When
   deciding whether to fire another gap fetch (Step 2.5) and what to search for,
   read the reflections artifact and the aggregated `open_gaps`; do NOT re-read
   the raw note bodies. Re-reading the corpus each round is the quadratic-growth
   anti-pattern this step exists to prevent. If `reflections.md` grows past the
   ≤10K-token synthesis ceiling, compact it (`ReflectionLog.compact` drops the
   oldest records, keeping the most-recent live gaps).

**Grounding is preserved:** dropping the raw body from *context* does not drop the
verbatim `quoted_support` spans — those live in `claims-*.json` + the vault note,
and synthesis (step 10/11) re-injects them for the cited `note_id`s so the
`uncited-gate` / `recitation-gate` / `anchors.py` still verify byte-for-byte.

---

## Source count targets

| Tier | Minimum sources | Target sources | Fetchers per wave | Waves |
|------|----------------|---------------|-------------------|-------|
| `light` | 10 | 15–25 | 3–5 | 1–2 |
| `full` | 45 | 55–80 | 8–12 | 2–3 |

Substantive (non-deprecated) note counts. Quality over quantity — reference reports average ~65 sources. Beyond ~80, each additional source yields diminishing returns while degrading summarizer quality.

---

## Long-source delegation (any time during step 2)

When a single long source (>5000 words) is load-bearing, delegate end-to-end analysis to `bad-research-source-analyst` (Sonnet, 1M context):

Trigger conditions (ALL three must hold):
1. **Length:** source's `word_count` (visible on `bad note show <id> -j`) exceeds ~5000 words
2. **Relevance:** source is relevant to the research_query
3. **No existing analysis:** no `type: source-analysis` note already exists for this source

**Cap: at most 6 source-analysts per query.**

Spawn template:
```
subagent_type: bad-research-source-analyst
prompt: |
  RESEARCH QUERY (verbatim, gospel):
  > {{paste research/query-<vault_tag>.md body}}

  QUERY FILE: research/query-<vault_tag>.md

  PIPELINE POSITION: You are a leaf subagent for deep end-to-end analysis
  of ONE long source. Your digest feeds downstream Bad Research steps. You
  do NOT spawn other subagents.

  SOURCE-QUALITY NEGATIVE SIGNALS (down-weight or FLAG, do NOT suppress):
  Judge this long source against the Anthropic negative-signal list — flag, don't
  suppress (the lead reconciles): news aggregators rather than original sources
  (`aggregator`), false authority (`false_authority`), passive voice with nameless
  sources (`nameless_source`), general qualifiers without specifics
  (`vague_qualifier`), unconfirmed reports (`unconfirmed`), marketing/spin language
  (`marketing_spin`), speculation presented as finding (`speculation`), cherry-picked
  data (`cherry_picked`). Record any that apply as `source_quality_flags: [...]` (empty
  if none) in your digest header so the synthesizer can reconcile it at draft time —
  a flagged source is down-weighted and caveated (corroborated by an unflagged source
  or explicitly hedged, never the lead), so a spin page on a high-authority domain is
  still demoted in the report. Flag, don't suppress; there is no deterministic penalty.

  YOUR INPUTS:
  - source_note_id: <vault note id of the long source>
  - output_path: research/temp/source-analysis-<source_note_id>.md
  - vault_tag: <vault_tag>
```

---

## Exit criterion

- Minimum source count met (per tier table)
- Coverage check shows no `uncovered` atomic items (thin is acceptable)
- `research/temp/coverage-gaps.md` written
- `research/temp/reflections.md` written — one distilled record per round, raw bodies dropped from context
- (For std/full): `research/temp/redundancy-audit.md` written if any claim files existed

If you fall short after two waves, proceed anyway but ensure `coverage-gaps.md` lists what's missing so the drafter handles it.

---

## Next step

Return to the entry skill (`bad-research`). Tier-based routing:

- **light tier:** Skip directly to step 10 — invoke `Skill(skill: "bad-research-10-triple-draft")` (light tier writes a single draft, not the ensemble)
- **full tier:** Invoke `Skill(skill: "bad-research-4-loci-analysis")` (its Step 4.0 preamble builds the contradiction graph before loci analysis)
