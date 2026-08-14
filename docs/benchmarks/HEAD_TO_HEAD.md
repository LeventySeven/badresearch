# Head-to-Head Benchmark Protocol

**Status:** apparatus, not a result. This document + the `bad headtohead` command
define a *reproducible* way to measure bad-research against a commercial Deep
Research tool. As of this writing **no run has been executed**, so there is **no
claimed win on any axis**. This closes the apparatus half of honesty-audit row 11
("Run ONE real head-to-head vs a commercial DR tool on 8-12 shared queries,
blind/LLM-judged"). The remaining half — actually running the competitor and
pasting its reports — needs a human, because this tool cannot call Gemini /
OpenAI / Perplexity / Grok.

## What this measures, honestly

- It scores **two pasted reports per query** (bad-research's own output and a
  competitor's output) with the **same categorical judge** the calibration
  harness uses (`src/bad_research/calibrate/judge.py`), after **blinding** both so
  the judge cannot tell which tool produced which text.
- It tallies per-query **win / tie / loss** from bad-research's point of view and
  emits a scorecard (JSON + a markdown table) with a per-axis breakdown and
  cost / wall-clock columns.

### What it does NOT do (read before quoting any number)

- **It does not run the competitor.** A human runs Gemini / OpenAI / Perplexity /
  Grok Deep Research manually and pastes the report as a file. The harness is the
  scorer + tally, not the runner.
- **The default judge is not a quality oracle.** Keyless-by-default scoring uses
  the deterministic `RubricJudge`, which is a *grounding-overlap + citation-presence
  proxy*, **not semantic entailment** (its own docstring says so:
  `src/bad_research/calibrate/golden.py:130-145`). It will happily pass a
  well-cited report that *contradicts* its sources, and it will score a competitor
  report with no machine-readable corpus as `source_quality: fail`. For a verdict
  that reflects content quality you must run with `--llm` (the host-model
  `LLMJudge`), which needs the host model.
- **cost_usd / latency_s are operator-supplied metadata.** They are recorded on
  the scorecard for the cost/wall-clock columns; they do **not** feed the
  categorical verdict.

So: a tally out of this harness is *whatever the real runs produced under a named
judge*, with the judge's limits stated on every artifact. It is not, by itself,
evidence that bad-research is "better." Cite the `disclaimer` field that ships in
the scorecard alongside any number.

## The shared query set

`docs/benchmarks/queries/starter_set.json` ships **12 queries spanning the eight
golden-taxonomy modalities** (mirrors `src/bad_research/calibrate/golden/`):

| modality      | query ids                              |
|---------------|----------------------------------------|
| causal        | `h2h_01_causal`, `h2h_09_causal_policy`|
| comparison    | `h2h_02_comparison`, `h2h_10_comparison_tech` |
| multi-domain  | `h2h_03_multidomain`                   |
| contested     | `h2h_04_contested`, `h2h_11_contested_health` |
| definitional  | `h2h_05_definitional`                  |
| recency       | `h2h_06_recency`, `h2h_12_recency_numeric` |
| breadth-list  | `h2h_07_breadth_list`                  |
| numeric       | `h2h_08_numeric`                       |

Each item is `{id, modality, query}`. The harness only requires `id` + `query`;
`modality` is documentation. Extend or replace the set by passing
`--query-set PATH`. Use the **same** set for both sides — that is the whole point
of "shared."

## The run procedure (manual where it must be)

For each query in the set:

1. **bad-research side (automatable).** Run bad-research on the query. Run it once
   per route you want to benchmark — the competitive middle tier and the full
   pipeline are both fair entrants, recorded separately:
   Invoke `/bad-research <query>` and **pin the route** at step 1.5 rather than
   letting the heuristic pick, so every query is benchmarked at the same depth:
   - `fast`: `bad route --decomposition research/prompt-decomposition.json --fast
     --apply --json` — the bounded-ReAct middle tier (`bad-research-fast`).
     Save the final report to a file.
   - `full`: same command with `--full`. The full pipeline. Save the report to a file.

   These are the only two routes (`bad route --help`). The former third route,
   `ultrafast`, was folded into `fast` on 2026-07-06 — there is no `--ultrafast`
   flag and no `bad-research-ultrafast` skill.
   Record the wall-clock seconds and (from `bad calibrate`'s cost meter, or your
   own timing) the USD cost for each.
2. **competitor side (MANUAL — needs a human).** Open the commercial Deep Research
   product (Gemini Deep Research / OpenAI Deep Research / Perplexity Pro /
   Grok DeepSearch), paste the **identical** query, let it finish, and **copy its
   full report into a file**. Note the wall-clock time and, if the product exposes
   it, the cost (most are flat-subscription, so record `0.0` and rely on the
   latency + quality columns). The harness cannot do this step — it has no access
   to those products.
3. **Optionally capture a competitor corpus.** The keyless `RubricJudge` scores
   `source_quality` from a machine-readable corpus. A pasted competitor report
   usually has none, so it scores `fail` on that axis under the keyless judge —
   honest but unflattering to the competitor. To score `source_quality` fairly,
   either (a) hand-build a small corpus JSON of the competitor's cited sources
   (`[{"note_id","url","text"}, ...]`) and reference it via `corpus_file`, or
   (b) run the whole benchmark with `--llm` so the host-model judge reads the
   report's inline citations directly. State which you did.

Then score everything in one shot (see "Running the harness").

## Blinding

Before any report reaches the judge it is passed through `blind_report`
(`src/bad_research/calibrate/headtohead.py`), which strips known
tool-identifying markers (case-insensitive, longest-match-first) and replaces them
with a neutral `[tool]` token, and removes leading `Produced by …` / `Source: …`
attribution lines. The marker list (`TOOL_MARKERS`) covers the bad-research family
(`bad-research`, `hyperresearch`, `michael jackson bad`, …) and the commercial
tools (`gemini`, `openai`/`chatgpt`, `perplexity`, `grok`, `claude`, `anthropic`,
…). Blinding is **lexical and best-effort**: it removes the markers we know about,
not a guarantee that no stylistic tell survives. You can extend it per-run by
adding markers in code, and you can verify a report is clean with
`markers_present(report)` (empty list = blind). Blinding is **on by default**;
`--no-blind` exists only for debugging and must not be used for reported results.

## Scoring rubric (reuses the judge's axes)

Each blinded report is scored on the **five existing judge axes** — identical to
the calibration harness, no new rubric invented:

| axis            | what it asks                                                        |
|-----------------|---------------------------------------------------------------------|
| `factual`       | are claims accurate and grounded in the available evidence?         |
| `citation`      | does every non-trivial claim carry a supportable citation?          |
| `completeness`  | does the report cover the question's sub-parts?                     |
| `source_quality`| are the cited sources authoritative and on-topic?                   |
| `efficiency`    | concise — no padding, no redundancy, right length?                  |

Each axis gets a categorical rail in `{pass, borderline, fail}` (rail credit
`pass=1.0`, `borderline=0.5`, `fail=0.0`). A report's **pass-rate** is the mean
rail-credit; it `PASS`es iff no axis is `fail` **and** pass-rate ≥ 0.75
(`PASS_RATE_THRESHOLD`). This is exactly `JudgeVerdict.from_rails`, unchanged.

Beyond the categorical axes the scorecard records two **operator-supplied**
columns per entrant per query, which do not feed the verdict:

- **cost** (USD) — bad-research's metered cost; the competitor's is usually `0.0`
  (flat subscription).
- **wall-clock** (seconds) — end-to-end latency for that query.

## Win / tie / loss tally rule

Per query, from **bad-research's point of view**, comparing pass-rates:

- **win**  iff bad-research's pass-rate **>** the competitor's;
- **loss** iff bad-research's pass-rate **<** the competitor's;
- **tie**  iff the pass-rates are **equal** (ties are never rounded into a win),
  *and* any query missing one side's report is counted a **tie**, never a silent
  win.

The aggregate verdict line is honest about direction: it only says
"bad-research leads" when wins **>** losses; an equal or trailing tally reads as a
tie or a competitor lead. Cost and wall-clock are reported alongside but are **not**
part of the W/T/L decision — they are a separate, explicit axis of comparison so a
"slower but more grounded" or "faster but thinner" trade-off is visible rather than
collapsed into one number.

## Running the harness

Keyless, offline default (deterministic `RubricJudge`):

```bash
# Single-query smoke (one bad report vs one pasted competitor report):
bad headtohead \
  --query-id h2h_02_comparison \
  --bad-report runs/bad/02_fast.md \
  --competitor-report runs/gemini/02.md \
  --bad-name bad-research-fast \
  --competitor-name gemini-deep-research \
  --out runs/scorecards/

# Full set via a manifest (preferred):
bad headtohead --manifest runs/manifest.json --out runs/scorecards/

# Content-quality scoring through the host model (needs the host model):
bad headtohead --manifest runs/manifest.json --llm --out runs/scorecards/
```

The manifest maps each query id to its entrants (report files resolved relative to
the manifest's directory):

```json
{
  "bad_name": "bad-research-fast",
  "competitor_name": "gemini-deep-research",
  "entrants": {
    "h2h_02_comparison": [
      {"name": "bad-research-fast", "report_file": "bad/02.md",
       "corpus_file": "bad/02_corpus.json", "cost_usd": 0.018, "latency_s": 530},
      {"name": "gemini-deep-research", "report_file": "gemini/02.md",
       "cost_usd": 0.0, "latency_s": 295}
    ]
  }
}
```

Outputs: `headtohead-scorecard.json` (machine-readable, with the `disclaimer`
field) and `headtohead-scorecard.md` (the per-query table + aggregate tally + the
per-axis mean rail-credit breakdown).

## What still needs a human

1. Run each query through the chosen commercial Deep Research product and paste
   its report into a file. *(The harness cannot reach those products.)*
2. Run each query through bad-research (`fast` and/or `full`), saving the
   report and recording cost + wall-clock.
3. Optionally hand-build a competitor corpus JSON (or run `--llm`) so
   `source_quality` is scored fairly rather than failing for lack of a corpus.
4. Assemble the manifest and run `bad headtohead`. Publish the scorecard **with**
   its `disclaimer`, naming the competitor, the date, the routes, and the judge
   used. Do not headline the tally without that context.
