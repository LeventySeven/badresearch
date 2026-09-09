# Noise-discrimination sweep — STOPPED MID-RUN, SALVAGED

**Status: paused at the user's request, resumable.** The Sweep phase completed; the Verify phase was
partway through when the run was stopped. Everything the journal captured is saved here verbatim.

## Resume
```
Workflow({
  scriptPath: "/Users/seventyleven/.claude/projects/-Users-seventyleven-Desktop-badresearch/47bf30ba-3257-44d3-a6e3-5cfa643debb0/workflows/scripts/noise-discrimination-wf_49811902-352.js",
  resumeFromRunId: "wf_49811902-352"
})
```
The 8 sweep agents' prompts are unchanged, so they return from cache instantly. **The verify stage will
re-run** — deliberately: its schema was fixed (see below), which changes the agent key and invalidates
that cache. That is the intended trade; the expensive half is the sweep and it is preserved.

## What was salvaged

| | |
|---|---:|
| lanes with findings | 11 (8 named) |
| findings | 115 |
| verdicts | 274 (115 refuted) |
| corrected claims | 260 |
| negative results | 60 |
| open questions | 44 |

Raw: `raw-lanes.json`, `raw-verdicts.json`.

## The defect this run exposed, and the fix already applied

**The verdicts cannot be joined to the findings they judged.** The journal records `agentId` and a
prompt-hash `key` only; the VERDICT schema carried no identifier, and results land in *completion*
order rather than candidate order. So 274 verdicts are unattributable to the 115 findings they were
about. The `corrected_claim` texts are still readable as free-standing corrections — they just cannot
be told which finding each belongs to.

This is a trap already recorded in memory (`workflow-journal-pairing-trap`) and I walked into it anyway.
The script is now fixed: VERDICT requires `finding_index` and `claim_judged`, echoed verbatim, and the
per-finding result carries its index so a partial run stays joinable even if the workflow never reaches
its return statement.

## Lanes that completed

### The owner's own corpus tooling and its quality gates — researchfms/Transcripts (TRANSCRIPT_RULES + _transcript_tools + _quarantine + the audit workdir), compound-v scripts/references, badresearch src/bad_research checks+quality+funnel. Read only what is on disk; every number below was recomputed live rather than quoted from a doc.

11 findings · 7 negative results · 5 open questions

- **The rule that LET THE 25 FABRICATIONS IN is not a weak threshold — it is a KEY. Every source-grounding gate in _transcript_tools finds its source by r**  
  `/Users/seventyleven/Desktop/researchfms/Transcripts/_transcript_tools/verbatim_check.py:107 `if not m or m.gro`  
  accretes: No — and this is the null result in its purest form. The gate is a fixed regex over a fixed line format. Nothi

- **The rule that CAUGHT them is a distinctive-token grep in the note->source direction with `0 hits` as the reject signal — and it is entirely manual. Th**  
  `/Users/seventyleven/Desktop/researchfms/Transcripts/_queue/sweep_2026-08-04/audit_dlai.md §1 (yt-dlp `--flat-p`  
  accretes: Weakly, and only through a human editing a file afterwards. Two real, dated accretions exist: (a) the verbatim

- **The only BLOCKING depth gate is orthogonal to fabrication, and using it as a fabrication proxy is worse than useless. Recomputed from the audit's own **  
  `Parsed live from the triage table in /Users/seventyleven/Desktop/researchfms/Transcripts/_queue/sweep_2026-08-`  
  accretes: No — retention is a fixed ratio, `note_words / source_words`, floor 75% (retention_check.py; TRANSCRIPT_RULES.

- …and 8 more in `raw-lanes.json`

### 407 product teardowns at /Users/seventyleven/Desktop/researchfms/teardowns/ (flat depth-1 glob; enumerated live 2026-09-09: 423 entries, 407 .md, 16 dirs/archives excluded)

15 findings · 8 negative results · 5 open questions

- **HyperResearch demotes a rejected source instead of deleting it: a note's curation status becomes a BM25 score multiplier — evergreen ×1.5, stale ×0.7,**  
  `/Users/seventyleven/Desktop/researchfms/teardowns/HYPERRESEARCH.md:515 (search/fts.py:128-141), :649, :1254, :`  
  accretes: Yes, and this is the strongest accretion mechanism in the lane. Every curation verdict a past run reached is w

- **The only shipped fetch-time content-quality gate in the lane, looks_like_junk(), rejects on structural signals only: content <300 chars; the literal s**  
  `/Users/seventyleven/Desktop/researchfms/teardowns/HYPERRESEARCH.md:531 (web/base.py:59-118), :558 (core/fetche`  
  accretes: No — fixed rules, hand-raised once (thresholds 'raised in 0.3.0'). This is the null result for the accretion q

- **HyperResearch's rejections are pool-level, not per-item, and their output is MORE retrieval rather than a shorter list. Coverage check labels each ato**  
  `/Users/seventyleven/Desktop/researchfms/teardowns/HYPERRESEARCH.md:150 and the stage-2 block at :119-238 — 2.5`  
  accretes: Yes, within a run: the coverage matrix and the redundancy clusters are state built from what has already been 

- …and 12 more in `raw-lanes.json`

### Human evidence-synthesis methodology — systematic review screening, dual-reviewer statistics, ML-assisted screening, stopping criteria. 17 open-access primary papers pulled full-text via the Europe PMC REST API and read locally (copies at /private/tmp/claude-501/-Users-seventyleven-Desktop/47bf30ba-3257-44d3-a6e3-5cfa643debb0/scratchpad/pmc/*.txt). Silver was tried first but BMC/Springer served a Cloudflare interstitial ("A required part of this site couldn't load") on both target URLs, so I switched to the EBI REST endpoint, which returns publisher XML verbatim. WebSearch was unavailable — this session had already used 200/200 calls.

12 findings · 5 negative results · 5 open questions

- **The exchange rate for a second independent reader is measured and near-symmetric: one screener gets sensitivity 86.6% (95% CI 80.6–91.2) / specificity**  
  `Gartlehner et al. 2020, J Clin Epidemiol, DOI 10.1016/j.jclinepi.2020.01.005 — crowd-based parallel-group RCT,`  
  accretes: No — this is a fixed structural choice (n readers), not a learned filter. But it sets the ceiling the accretin

- **The shipped Cochrane RCT Classifier rejects candidates before any full-text read using a three-dataset procedure with a hard abstain rule: train (280,**  
  `Thomas et al. 2021, J Clin Epidemiol 133:140-151, PMC8168828 §3.1–3.2 and Table 2/Table 3. Local copy: scratch`  
  accretes: Partly. The threshold is fit once against a labelled calibration corpus and frozen; it does not move as a revi

- **That classifier's 5.7 points of recall come entirely from an ABSTAIN rule, not from the model: records with fewer than 400 characters of abstract or 1**  
  `Thomas et al. 2021, PMC8168828 §2.6 ('pragmatic cutoffs … 400 characters as a minimum abstract length and 15 c`  
  accretes: No — a fixed character constant. It is the null-result shape, and it is still the highest-leverage single rule

- …and 9 more in `raw-lanes.json`

### Information-retrieval / learning-to-rank literature, read live via silver (WebSearch lane EXHAUSTED at 200/200 on first call — see negative_results). All papers opened as full text (ar5iv/arxiv HTML), not abstracts; every number below was read in situ and greps were re-run against locally saved copies in /private/tmp/claude-501/-Users-seventyleven-Desktop/47bf30ba-3257-44d3-a6e3-5cfa643debb0/scratchpad/{rlt,zhan,rocketqa,multistage,beir}.txt

14 findings · 6 negative results · 6 open questions

- **The shipped mechanism for rejecting a candidate is a cheap model's own top-k list re-scored by an expensive model used ONLY as a veto, with two hard t**  
  `RocketQA, Qu et al. NAACL 2021, arXiv:2010.08191, Table 3 and Sec. 4.2.2 (read at https://ar5iv.labs.arxiv.org`  
  accretes: Yes, and it is the clearest accretion loop in the literature. STEP 3 re-mines negatives from the CURRENT retri

- **A filter trained on a FROZEN set of negatives has no performance guarantee at all — the bound collapses to MRR ~ 1/|C| — and empirically it buys top-o**  
  `Zhan et al., 'Optimizing Dense Retrieval Model Training with Hard Negatives', SIGIR 2021, arXiv:2104.08051. Wo`  
  accretes: Only if the negatives are re-mined against the CURRENT model each step. That is the paper's whole result: 'dyn

- **The cheap first stage's REJECTION CRITERION is structurally different from the expensive stage's scoring criterion, so it permanently deletes exactly **  
  `Nogueira, Yang, Cho, Lin, 'Multi-Stage Document Ranking with BERT', arXiv:1910.14424. Design rule at saved mul`  
  accretes: No — fixed constants (1000, 50), tuned once. This is the null result for stage sizing. The only adaptivity the

- …and 11 more in `raw-lanes.json`

### Reward models and learned rerankers as discriminators, read in source. Shallow clones (`--depth 1 --filter=blob:none`) at `/private/tmp/claude-501/-Users-seventyleven-Desktop/47bf30ba-3257-44d3-a6e3-5cfa643debb0/scratchpad/lane/`: RUC-NLPIR/FlashRAG@1ee5249 (2026-08-21), castorini/pyserini@b0ad282 (2026-09-08), AnswerDotAI/rerankers@5b9cbb0 (2025-12-20), huggingface/trl@e78a93b (2026-09-09), allenai/open-instruct@ebd0c8e (2026-09-03), embeddings-benchmark/mteb@df7998e (2026-09-09). Nothing installed, nothing run.

13 findings · 8 negative results · 5 open questions

- **The only filter in six repos whose threshold is DERIVED FROM ACCUMULATED EXPERIENCE rather than picked: FlashRAG's SKRJudger decides whether to retrie**  
  `FlashRAG@1ee5249 flashrag/flashrag/judger/judger.py:37-128; decision at :110-124; prior term at :116 and :121;`  
  accretes: YES — the single genuinely accretive mechanism I found. Adding labelled experience changes both the retrieved 

- **MTEB computes, on EVERY retrieval and reranking evaluation, an nAUC abstention score that measures whether a filter's own confidence signal is better **  
  `mteb@df7998e mteb/_evaluators/retrieval_metrics.py: `confidence_scores` :273-300 returns `max` (top score), `s`  
  accretes: No — fixed per-evaluation statistic. But it is the instrument that TELLS you whether an accretive filter is le

- **open-instruct logs a TYPED discard ledger every training step: not 'we dropped N' but N broken into three named causes, each meaning something operati**  
  `open-instruct@ebd0c8e open_instruct/data_loader.py:1133-1145 (attribution + log line `filtered={} (all_zero={}`  
  accretes: No — fixed rule (std == 0). The ledger is what makes the fixed rule auditable over time.

- …and 10 more in `raw-lanes.json`

### The adversary — content engineered to look like the thing you are searching for (SEO/GEO farms, paper mills, citation rings, benchmark contamination, anti-crawler generation, review fraud). Live web via silver + Crossref/OpenAlex APIs + the local teardown corpus + the badresearch repo itself.

12 findings · 7 negative results · 6 open questions

- **When the adversary can call the detector, string-overlap detection does not degrade — it goes to exactly zero. Yang et al.'s Algorithm 1 is a loop: re**  
  `arXiv:2311.04850v2 (Yang, Chiang, Zheng, Gonzalez, Stoica — UC Berkeley/LMSYS), Table 5 and Table 6, read live`  
  accretes: The DETECTOR does not accrete — 10-gram is the same rule on candidate 1 and candidate 10^9. The ADVERSARY accr

- **For 8 of 8 published membership-inference / contamination benchmarks, a classifier that never looks at the model at all beats the state-of-the-art det**  
  `arXiv:2406.16201v2, Das, Zhang & Tramèr (ETH Zurich; no detector to sell), Table 2, read live 2026-09-09 at ht`  
  accretes: The blind baseline itself is a fixed procedure, but it is the control that makes any accreting filter honest. 

- **A contamination test with a proven false-positive-rate guarantee still flagged 14 of 57 MMLU test files as contaminated in two models that predate MML**  
  `arXiv:2310.17623v2, Oren, Meister, Chatterji, Ladhak, Hashimoto (Stanford), §4.3, read live 2026-09-09 at http`  
  accretes: No — it is a fixed permutation/t-test. But the CONTROL accretes usefully: every source known to predate the ph

- …and 9 more in `raw-lanes.json`

### Filters that improve as the system accumulates knowledge — learned rejection, disposition caches, active-learning screeners, growing negative sets

16 findings · 9 negative results · 6 open questions

- **Mozilla's bugbug ships an LLM filter whose few-shot rejection examples are retrieved by vector similarity from a database of comments humans actually **  
  `bugbug@8126f25 (2026-09-08). /private/tmp/.../clones/bugbug/bugbug/tools/suggestion_filtering/agent.py:100-135`  
  accretes: Yes — this is the mechanism the lane was looking for. Every human rejection is embedded and stored; the next c

- **The same repo instruments the filter's own false-negative rate as a named metric: `false_exclusion_rate = matched_valid_excluded / matched_valid` — of**  
  `bugbug@8126f25, bugbug/tools/code_review/scorer.py:284-288 (`false_exclusion_rate`), paired with `true_exclusi`  
  accretes: The metric itself does not, but it is the instrument that makes accretion safe: it is the only thing in the sw

- **ClueBot NG does not choose a score cutoff at all — a human picks a FALSE-POSITIVE BUDGET and the threshold is computed to hit it while maximising catc**  
  `https://en.wikipedia.org/wiki/User:ClueBot_NG (read 2026-09-09, silver): "Selecting a threshold to hold false `  
  accretes: Yes, on both halves. The model is retrained from a volunteer review interface that classifies randomly-sampled

- …and 13 more in `raw-lanes.json`

### Who measures what their filter WRONGLY KILLED, and how — false-negative instrumentation for candidate filters (IR, content moderation, spam, hiring, credit/justice, medical screening, LLM pretraining-data curation, LLM safety refusal, peer review), plus an audit of what this repo does and does not measure.

16 findings · 10 negative results · 6 open questions

- **The only large study with access to a real reject pile found that the cheapest, pre-read stage killed the best items: of 1,008 manuscripts submitted t**  
  `Siler, Lee, Bero, "Measuring the effectiveness of scientific gatekeeping", PNAS 112(2), doi:10.1073/pnas.14182`  
  accretes: No — fixed human editors with no memory across submissions. That is part of the result: the un-accreting cheap

- **Planted-control preference audit of a gold set: on MS MARCO's 6,980 dev queries, 5,112 (73.24%) had the neural ranker's top passage differ from the la**  
  `Arabzadeh, Vtyurina, Yan, Clarke, "Shallow pooling for sparse labels", arXiv:2109.00062, Tables 1 and 2 (local`  
  accretes: Yes — the cleanest accreting design found. Their fix is "shallow pooling": whenever a ranker surfaces a previo

- **Per-filter ablation with a measured data cost: FineWeb tested each C4 heuristic filter individually by training identical 1.71B models on 28B tokens w**  
  `Penedo et al., "The FineWeb Datasets", arXiv:2406.17557 §3.5-3.6 (local extraction .../scratchpad/fineweb.txt `  
  accretes: Partly. Thresholds were derived by comparing >50 document statistics across a known-high-quality and known-low

- …and 13 more in `raw-lanes.json`
