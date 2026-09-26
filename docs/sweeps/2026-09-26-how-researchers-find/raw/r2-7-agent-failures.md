<!-- AGENT OUTPUT — R2-7 agent failures vs humans. Returned by a subagent, not read by the chair unless a row says so. -->

## Findings

**Headline:** the largest agent failures that are measured with frequencies are fabrication (the biggest single class), coverage gaps and stopping after a failed query. Retrieval is the ceiling, not reasoning. The failures with no counterpart in KNOWN are fabrication, source-credibility judgement and implicit requirements.

**Table: agent failure class → frequency (denominator, benchmark) → human contrast → KNOWN practice that addresses it**

| # | Failure class | Frequency | Human side | Addressed by |
|---|---|---|---|---|
| A | Stops after a failed query / under-searches | Wrong answers in steps where the agent did not search: Search-R1 33.98%, R1-Searcher 63% (multi-hop QA). Qwen3-32B averages 0.92–0.94 searches per query against ~22 for gpt-5 (BrowseComp-Plus, 830 queries). Over 90% of real agent sessions have ≤10 steps (14.44M requests). WideSearch describes it but gives no frequency. | BrowseComp trainers could give up only after about two hours. WideSearch humans spent 2.33 h and read 44.10 pages per task; o3 made 13.3 searches and 5.8 page visits. | K1 (Gwern rewrites the query after every miss); K8 (stop on saturation, not on the first miss) |
| B | Loops back to earlier queries | The likeliest next states for agents are OUT, CH and DUP (an exact repeat of an earlier query); traces run up to 186 steps (ASQ). In fact-seeking sessions, repetition rises as the session goes on. | Humans abandon after 2–3 reformulations. | K8 (Kuhlthau's redundancy signal; Nanda: change approach); K11 (DeLM's FAIL notes) |
| C | Covers the obvious reading and misses the other facets | 78.5% of missing key points (100 lowest-recall queries, DeepResearchGym). Recall is below precision on every WideSearch subset. DEFT: insufficient external information acquisition is 16.30% of failures (~1,000 reports). | Mind2Web 2: every human answer was complete. | K12 broad-first (Galen Adams); K4 open-question list; K7 Berkeley Protocol keyword sets for both sides |
| D | Wrong lens or wrong vocabulary | 17.9% of missing key points are lens mismatches, plus 3.6% where a term was misread ("Indians"), same query set | — | K5 vocabulary discovery; USPTO search by function |
| E | The evidence is never retrieved | gpt-4.1 scores 93.49% when handed the right documents and 14.58% searching with BM25. Agents retrieve 16–79% of the evidence documents. | Gwern's term selection put the target at hit #2 (F2) | K1 partly; Gwern's method is new |
| F | Shallow reading (512-token previews) | A full-document tool adds +8.2 pp (35.42→43.61%) with only 1.85 calls per query. LiveResearchBench: 13 of 16 systems win under 30% on analysis depth. | — | K9 (read a few deeply), K10 (appendices) |
| G | Fabrication / claims the cited source does not support | DEFT strategic content fabrication 18.95%, the largest single mode. Mind2Web 2 hallucination: 23% of tasks for OpenAI DR, ≥50% for the others (30 tasks). DeepTRACE: citation accuracy 40–80%, unsupported statements up to 97.5% (2,727 samples). ChatGPT DR: 2 of 13 selected papers did not exist. | Mind2Web 2 humans: zero hallucinated URLs. | **None in KNOWN** (nearest: Berkeley Protocol provenance log) |
| H | One-sided answers, no cross-checking, anchoring | One-sided on debate queries: GPT-5 (DR) 54.7%, YouChat (DR) 63.1%, Copilot (DR) 94.8%. DEFT verification-mechanism failure 8.72%. | — | K7 |
| I | Noisy results override correct knowledge; confidence rises | DeepSeek-R1 drops 22.4→11.0% with search on SealQA and 23.2→7.6% on BrowseComp-ZH. o4-mini falls 6.3→4.5% as reasoning effort rises. Calibration error: GPT-4o 69→82% with browsing; DR 91%. | SealQA humans 38.8% against o3-high 28.0% (50 questions). | K7 Heuer (more information raises confidence, not accuracy); predict before reading |
| J | Misses implicit requirements | Implicit criteria fail ~45–49% of the time, explicit ~24–27% (3 DR systems). DEFT failure to understand requirements 10.55%. | — | K3 partly; otherwise none |
| K | Collects but does not connect | Synthesis criteria fail ~25–29%. Coverage is lost past >3,000 retrieved pages when nothing tracks them. | — | K4 (re-read log), K5 |
| L | Ignores source-credibility cues | Search-R1 stays at 78–80% correct at every trust level (synthetic documents). Anthropic's SEO-farm observation was seen by testers and never measured. | — | **No source-quality practice in KNOWN** |
| M | Concentrates on a few popular outlets | OpenAI models: the top 20 outlets are 67.3% of news citations, Gini 0.83 (366k citations) | — | K6: agents do not sample unpopular sources either |
| N | Cannot be complete at scale | WideSearch best table-level success 5.1%. Item F1 reaches ~80 at 128 tries, yet table success stays under 20%. | One human alone: 20%. Several annotators cross-validating: "near 100%". | K11 (Cochrane's two independent screeners) |
| O | Low recall on "find all" literature searches | AI tools missed a median 91% of included studies. Elicit sensitivity 37.9% against 93.5% for the original searches. ChatGPT DR 47.8% (11/23) using the same Boolean terms. | Librarian searches 87–98% | K2, K3; extends Galen Adams's 15–20% |

**F1. Formal recall audits confirm Galen Adams, and agents also find what librarians miss (row O).** This extends K12 and connects K10 and K2.
- who: Lau/Golder et al. (academic reviewers, nothing to sell); Clark, Barton & Albarqouni 2025, *Research Synthesis Methods*; Bencze et al. 2025 (Semmelweis).
- evidence: "the sensitivity of Elicit was poor, averaging 37.9% (25.5% - 69.2%) compared to 93.5% (87.2% - 98.0%) in the original reviews" and "all four RCTs found by Elicit alone were not indexed in either MEDLINE or Embase" — https://www.medrxiv.org/content/10.1101/2025.06.17.25329772v1.full (2026-09-26; READ-PARTIAL).
- evidence: "When used for (1) searching GenAI missed 68% to 96% (median = 91%) of studies" — https://pmc.ncbi.nlm.nih.gov/articles/PMC12527500/ (via NCBI efetch; READ-PARTIAL).
- evidence: "ChatGPT had high specificity (98%) and low sensitivity (47.8%)… Two cited articles by the AI software were nonexistent" — https://pmc.ncbi.nlm.nih.gov/articles/PMC12537162/ (READ-PARTIAL).
- bears on: Q3, Q6, C2.
- limit: Clark's median comes from 2023-era chat tools. The published Wiley version of the Elicit study gives 39.5% and 94.5% (DIGEST-ONLY).

**F2. Human against agent on one hard-to-find item: the skilled searcher and the agent both hit it; a capable non-specialist gave up.** This extends K1 and K5.
- who: Gwern (independent researcher, nothing to sell).
- method: "the 'red light' has the ring of truth: it is a concrete, logical, memorable detail, which would hardly ever show up in unrelated research"; "I would try removing 'price', 'power saving', & 'electricity' in that order."
- outcome: McKenzie "gave up after 30 minutes; it seems likely he picked the wrong key terms… not hitting the crucial intersection like I & DR did" — https://r.jina.ai/https://gwern.net/search-case-studies (READ-PARTIAL).
- bears on: Q1, Q3, C1.
- limit: one case.

**F3. On inverted multi-constraint questions, agents beat the humans who wrote them.** This contradicts an assumption that humans lead everywhere.
- evidence: trainers "Human gave up after two hours 888 / 1,255 (70.8%)"; Deep Research scored 51.5%. On tasks where DR always failed, once given the answer, "In most cases, the model succeeded" in finding supporting evidence — https://arxiv.org/pdf/2504.12516 (READ-PARTIAL).
- who: OpenAI (sells DR). The paper's footnote says DR "is trained on data that specifically teach the model to be good at BrowsingComp tasks."
- bears on: Q6.
- limit: the trainers were "not competition-level internet browsers."

**F4. Humans and agents fail in complementary ways.** Humans are complete but careless; agents are careful but incomplete and fabricate.
- evidence: "all human answers fully fulfill task requirements without omission, and without hallucinations of webpage URLs"; criteria violation is "the most common error type for humans"; "OpenAI Deep Research… reaches a hallucination rate of 23%. Other systems… at least 50%" — https://arxiv.org/pdf/2506.21506 (READ-PARTIAL; OSU, academic).
- bears on: Q5, Q6.
- limit: 30-task subset.

**F5. Stopping versus looping (rows A and B).**
- "They tend to abandon the search after an initial failed attempt and proceed to answer based on incomplete information or their internal knowledge" — https://arxiv.org/pdf/2508.07999 (ByteDance Seed, which sells Doubao).
- "high DUP probability indicates that agents often regress to previous queries, likely when trapped in long loops"; humans abandon "typically after 2 or 3 query reformulations" — https://arxiv.org/pdf/2602.17518 (academic).
- bears on: Q6, K8.
- limit: the two sources use different agents; small open models under-search while large ones loop.

**F6. Coverage misses are dominated by facets and lenses, which is a vocabulary problem (rows C and D).**
- evidence: "Multi-facet coverage gaps account for 78.5% of missing key-points"; domain misinterpretations are cases where "ambiguous terminology leads the system to research the wrong topic entirely" — https://arxiv.org/pdf/2505.19253 App. G (CMU; READ-PARTIAL).
- bears on: C2, K5.
- limit: one system (GPTResearcher), and only its worst 100 queries.

**F7. One-sidedness is measured, and it maps onto K7.**
- evidence: "still one-sided for a majority of debate queries (e.g., GPT-5(DR) 54.7%; YouChat(DR) 63.1%; Copilot(DR) 94.8%)" — https://arxiv.org/pdf/2509.04499 (Salesforce/Microsoft Research).
- ASearcher, one GAIA case: "even when the agent finds information that directly links to the correct answer, it is still misguided by previous incorrect conclusions" — https://arxiv.org/pdf/2508.07976.
- bears on: C5.

**F8. Heuer's warning is confirmed in agents (row I).** This connects K7 (Heuer) with the benchmarks.
- evidence: "access to web tools may increase the model's confidence in incorrect answers" — 2504.12516.
- evidence: "longer chains of thought can amplify spurious or irrelevant information" — https://arxiv.org/pdf/2506.01062 (Virginia Tech).
- bears on: C1, C5.
- limit: SealQA questions are adversarially built to return noisy results.

**F9. Source-credibility cues are ignored; source quality and grounding are separate problems (rows L and M).**
- evidence: open agents "rely heavily on the information provided in their context, even when sources have clear surface cues of low credibility" — https://arxiv.org/pdf/2607.13920 (Orange Research).
- evidence: news citations "concentrate heavily among a small number of outlets… though low-credibility sources are rarely cited" — https://arxiv.org/pdf/2507.05301 (Northeastern).
- bears on: C4, K6.

## Against the claims

- **C1 as agents practise it.** "search behaviours are likely governed by the agent capacity and learned behaviours rather than by retrieval quality" (2602.17518). Against that, CTAR: "54% of newly introduced query terms appear in the accumulated evidence context" (https://arxiv.org/pdf/2601.17617). So accretion is partial, and it compounds errors when the evidence is noisy (F8, ASearcher).
- **C6.** Single-agent web systems are the most consistent: "the absence of inter-agent handoffs reduces the risk of logical drift". Multi-agent systems lose coverage past 3,000 retrieved pages (https://arxiv.org/pdf/2510.14240; Salesforce/UW). Separately, WideSearch's multi-agent setup beats single agents by only +0.6 pp for o3.
- **C4 nuance.** In Google AI Overviews, source quality and claim fidelity "are largely independent (r ≈ 0.045)". Sources taken from beyond the first results page "are not lower quality" (https://arxiv.org/pdf/2605.14021).

## Not covered by any claim

- **Finding is harder than verifying.** Verification is cheap once a candidate exists: best-of-N sampling adds 15–25% (2504.12516).
- **The human-preference signal rewards irrelevant citations.** "correctly attributed citations… (β = 0.285)… irrelevant citations (β = 0.273)" — https://arxiv.org/pdf/2506.05334.
- **Budget dominates.** Anthropic: "token usage by itself explains 80% of the variance" on BrowseComp — ~/Desktop/guidesfm/research/articles/how-we-built-our-multi-agent-research-system.md:27. Its early agents were "scouring the web endlessly for nonexistent sources" (:43).
- **Fabrication follows poor retrieval.** DEFT's "Evidentiary Rigor cluster connects poor retrieval… to 'confident fabrications'" (https://arxiv.org/pdf/2512.01948; OPPO, which builds these agents).

## Frontier

- Venkit et al., "Search Engines in an AI Era" (https://arxiv.org/pdf/2410.22349) — an expert usability study of generative search. Not read.
- "Cited but Not Verified" (https://arxiv.org/pdf/2605.06635) and PaperAsk (https://arxiv.org/pdf/2510.22242) — paper-search reliability. Not read.
- "Search-Time Contamination" (https://arxiv.org/pdf/2606.05241) — agents find benchmark answers online.
- Amani et al. (https://arxiv.org/pdf/2609.19244) — ChatGPT, Claude, Grok and DeepSeek search behaviour from real user logs. Not read.
- Search Wisely (https://arxiv.org/pdf/2505.17281) — over-search and under-search rates. Read partially; used in row A.
- ResearcherBench (https://arxiv.org/pdf/2507.16280) — OpenAI DR ranks best on the rubric but has only 0.34 groundedness.

## Lane state

- BrowseComp, BrowseComp-Plus, WideSearch, Mind2Web 2, DeepResearchGym, FINDER/DEFT, DeepTRACE, SealQA, ResearchRubrics, LiveResearchBench, BrowseComp-ZH, ASearcher, DeepStress, the two search-log papers, news citing, AI Overviews, Search Arena — READ-PARTIAL. I read the error-analysis and results sections via pdftotext.
- DeepResearch Bench — READ-PARTIAL; it has leaderboard numbers but no failure taxonomy.
- GAIA — READ-PARTIAL; no error analysis. Humans 92% against GPT-4 with plugins 15%.
- Elicit study, Wiley published version — BLOCKED (Cloudflare). Its numbers are DIGEST-ONLY.
- Eye 2026 letter (PMC12764829) — BLOCKED (embargoed to 2027).
- PubMed web pages — BLOCKED (reCAPTCHA); I used NCBI eutils instead.
- Measured source-quality selection in deep-research agents (as opposed to search engines) — EMPTY after two searches. Only DeepStress uses synthetic documents.

## Source register

- https://arxiv.org/pdf/2504.12516 — READ-PARTIAL
- https://arxiv.org/pdf/2508.06600 — READ-PARTIAL
- https://arxiv.org/pdf/2508.07999 — READ-PARTIAL
- https://arxiv.org/pdf/2506.21506 — READ-PARTIAL
- https://arxiv.org/pdf/2506.11763 — READ-PARTIAL
- https://arxiv.org/pdf/2511.07685 — READ-PARTIAL
- https://arxiv.org/pdf/2507.16280 — READ-PARTIAL
- https://arxiv.org/pdf/2505.19253 — READ-PARTIAL
- https://arxiv.org/pdf/2510.14240 — READ-PARTIAL
- https://arxiv.org/pdf/2512.01948 — READ-PARTIAL
- https://arxiv.org/pdf/2509.04499 — READ-PARTIAL
- https://arxiv.org/pdf/2506.01062 — READ-PARTIAL
- https://arxiv.org/pdf/2504.19314 — READ-PARTIAL
- https://arxiv.org/pdf/2311.12983 — READ-PARTIAL
- https://arxiv.org/pdf/2505.17281 — READ-PARTIAL
- https://arxiv.org/pdf/2508.07976 — READ-PARTIAL
- https://arxiv.org/pdf/2607.13920 — READ-PARTIAL
- https://arxiv.org/pdf/2602.17518 — READ-PARTIAL
- https://arxiv.org/pdf/2601.17617 — READ-PARTIAL
- https://arxiv.org/pdf/2609.19244 — abstract only
- https://arxiv.org/pdf/2507.05301 — READ-PARTIAL
- https://arxiv.org/pdf/2605.14021 — READ-PARTIAL
- https://arxiv.org/pdf/2506.05334 — READ-PARTIAL
- https://arxiv.org/pdf/2510.22242 — downloaded, not read
- https://r.jina.ai/https://gwern.net/search-case-studies — READ-PARTIAL (PriceLight section)
- https://www.medrxiv.org/content/10.1101/2025.06.17.25329772v1.full — READ-PARTIAL
- https://onlinelibrary.wiley.com/doi/full/10.1002/cesm.70050 — BLOCKED
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12527500/ — READ-PARTIAL
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12537162/ — READ-PARTIAL
- https://pubmed.ncbi.nlm.nih.gov/41315732/ — BLOCKED (embargo)
- ~/Desktop/guidesfm/research/articles/how-we-built-our-multi-agent-research-system.md:27,43,93 — READ-PARTIAL

All fetched 2026-09-26. Text extracts are in `/private/tmp/claude-501/-Users-seventyleven-Desktop/fcd46374-4e61-45da-ae77-538c40287f4b/scratchpad/r27/`.