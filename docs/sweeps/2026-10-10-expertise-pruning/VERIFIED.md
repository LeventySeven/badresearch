# VERIFIED — what the chair re-checked in the source bytes (round 5, 2026-10-10)

Everything else in `raw/` is agent output: verbatim spans on file, not re-checked.

| row | claim (as used) | checked against | result |
|---|---|---|---|
| G1-F1 | Keller Jordan: without connections he did not know specific highly cited papers didn't reproduce | X API, status 2085461892257190396 (19,787 followers) | ✔ verbatim (curly apostrophes in original) |
| G1-F3 | Jordan: a paper's mistake → "***nothing happens***"; a speedrun's is found "automatically in the next record" | X API, status 1890181363850178639 | ✔ |
| G1-A2 | Karpathy: "I delete a note only rarely … never lost, they just don't deserve the top of mind"; old ideas "suddenly relevant in a new light" | X API, status 1902503836067229803 | ✔ |
| G1-A1 | Schulman: switching too often "is a more common failure mode than not switching enough" | guidesfm/research/articles/an-opinionated-guide-to-ml-research.md:112 | ✔ |
| G1-N2 | Perez: junior researchers see others' work as closer to theirs than it is | tips-for-empirical-alignment-research.md:102 | ✔ |
| G1-F7 | Perez: reading has "low value of information relative to running your own experiments" | same file :89 | ✔ |
| G1-F7 | Nanda: "The goal is not to read every paper before you touch research…" | how-to-become-a-mechanistic-interpretability-researcher.md:74 | ✔ |
| G1-N3 | Nanda: believe false things briefly, falsify fast; mass on "something I haven't thought of yet" | research-process-key-mindsets.md:43-49 | ✔ |
| G1-F9 | Jason Wei gave up medical-image AI for NLP (sunk cost) | practicing-ai-research.md:23 | ✔ |
| G1-F2 | Hyung Won Chung: 2020 intuition becomes a 2023 bias; "less to unlearn" | X API search `from:hwchung27 "less to unlearn"` | ✗ not re-found (search returned 0 rows) — agent-read only |
| G3-F2 | Planted false evidence: adoption 40.5% at cold start, 44.2% mid-research, 85.5% just before synthesis; "varied far more with the amount of workflow remaining after exposure than with coarse rank" | arXiv 2607.20891 PDF text | ✔ all three numbers and the sentence |
| G3-F1 | Inertia bias: models "substantially worse when they 'own' the preceding search step"; fix = context isolation at page triage and final-answer validation | arXiv 2608.23045 abstract (export.arxiv.org) | ✔ abstract; the per-model table numbers (4.08 vs 25.31 etc.) NOT re-found in the pdftotext output — agent-read only |
| G3-F10 | Fetch-then-Explore: visit-and-read fixes "a reading of the page … before the agent knows which fact it will need"; 44.5 (ours) row present | arXiv 2608.02097 PDF text | ✔ sentence; 44.5 present in table |
| G3-F3 | ReTree traces a contradicted claim back to where it entered, replaces evidence, regenerates summaries, prunes affected branches; FlatUpdate is a mechanism-matched control | arXiv 2608.10676 PDF text | ✔ sentence and control definition; the +2.2–4.7 margin not re-checked |
