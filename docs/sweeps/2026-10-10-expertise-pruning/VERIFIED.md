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
| G2-F8 | Kostopoulou RCT: alternatives shown BEFORE information gathering raised diagnostic accuracy (OR 1.31, 95% CI 1.03–1.66, P=0.027; +6% absolute); shown after a preliminary diagnosis did not (OR 1.10, 0.88–1.37) | bjgp.org/content/bjgp/65/630/e49.full.pdf | ✔ verbatim |
| G2-P1 | Rudolph et al.: only the "adaptive" residents resolved the airway problem (0/0/0/7 across modes) | proceedings.systemdynamics.org/2012/proceed/papers/P1523.pdf | ✔ table row |
| G2-F5 | Jonas et al. 2001: sequential presentation strengthens preference for supporting information | — | ✗ not re-fetched (guessed mirror URL returned HTML) — agent-read only |
| G4-F4 | Sholto Douglas: "Funnily enough, I read much less widely now that my day is occupied by working on things." | dwarkesh.com/p/sholto-douglas-trenton-bricken (the reader's saved fetch, grepped by the chair) | ✔ verbatim |
| G4-F5 | Trenton Bricken: "If it works well, it's probably not being published." | same | ✔ verbatim |
| G5-F12 | Kapoor et al. shadow evaluations: agents "dropped their most ambitious hypotheses within the first fifteen hours … and never changed course afterwards"; both runs ended with over half the budget unspent (n=2) | X API, status 2082877458924065269 (15,625 followers) | ✔ verbatim |
| G5-F1 | Tao: AI literature search suits cases where the user can "independently verify the output" | mathstodon API, status 115385025625117726 | ✔ verbatim |
| G3-F2b | MisKnow-Agent: "Pre- and post-research defenses reduce FCAR but do not eliminate adoption" (verification prompting before; a search-enabled claim-by-claim refiner after) | arXiv 2607.20891 PDF text (abstract + §3 defenses) | ✔ verbatim |
| G3-F10b | Fetch-then-Explore limits: gains on BrowseComp at every backbone; WideSearch a tie; only 1–10.5% of questions ever trigger a whole-workspace search | arXiv 2608.02097 — agent-read (raw/g3 F10) | not re-checked; the skill states the BrowseComp scope and the tie |
| R-D1 | "+15% from optimized Cline rules" charted on the 150 training tasks; repo holds a held-out 0.313 for the optimized GPT-4.1 ruleset with no matching no-rules baseline | raw/devrun-d2-arize-origin.md (a dev-run reader, agent output) | not re-checked by the chair — agent-read |
| R-AIE | 1,268 titles, 35 picked, 15/35 walled at -P4, 1 recovered serially, 12/14 recovered from ai.engineer pages, 22/35 outside a 400 window | raw/devrun-aie-transcript-lane.md (the chair's own run) | ✔ measured |
| R-OPT | Claimed 1.4–2× optimizer speedups shrink against well-tuned baselines and with scale, to 1.1× at 1.2B | export.arxiv.org abstract of 2509.02046 | ✔ verbatim |
