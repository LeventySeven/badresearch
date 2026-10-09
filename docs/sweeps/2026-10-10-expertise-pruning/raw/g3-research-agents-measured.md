<!-- G3 research agents measured (agent output, 2026-10-10) -->

## Findings

F1. **An agent judges its own earlier search worse than it judges the same results handed to it by someone else ("inertia bias").** The IBIS benchmark holds the search results fixed and changes one thing: whether the model thinks it issued the query. When it "owns" the step, it keeps clicking into bad results instead of re-searching. On the "Should Re-search" items, GPT-4o scored 4.08% when it owned the step vs 25.31% as an observer. Gemini-2.5-Pro scored 31.43 vs 62.44, GPT-4.1 20.41 vs 59.18. Running page triage and answer validation in a fresh context raised GAIA from 56.96 to 61.82 (GPT-4o).
    who:      Zhang et al., Zhejiang Univ. + Darwinmind AI; arXiv 2608.23045. The authors' own benchmark (245 + 209 items, three annotators) and their own system.
    evidence: "models are substantially worse when they “own” the preceding search step, showing that self-authored action history can systematically distort subsequent judgment" — https://arxiv.org/abs/2608.23045 ; Table 7 and Table 4 in https://arxiv.org/pdf/2608.23045 (2026-10-10; READ-PARTIAL)
    bears on: E1 (directly), K11 (isolate judgment), K7
    limit:    These are single next-step decisions on a constructed set. In the end-to-end systems, the isolation results are "competitive", not dominant.

F2. **False evidence that arrives early is adopted LESS often than false evidence that arrives just before writing. What matters is how much research is left to challenge it.** One planted document took false-conclusion adoption from 0% to 54.7%, and more documents added under 4 points. By entry point, adoption was 40.5% when the document was there from the start, 44.2% mid-research and 85.5% just before synthesis. Its rank in the result list moved adoption by ≤6 points. Source authority and writing style mattered.
    who:      Zhu et al., BUPT + Shanghai AI Lab; arXiv 2607.20891. They tested DeerFlow and WebThinker on 3 LLMs, plus Gemini Deep Research, using 5,933 planted documents built on DeepResearch Bench tasks. They sell no system.
    evidence: "FCAR varied far more with the amount of workflow remaining after exposure than with coarse rank within a retrieved list." — https://arxiv.org/pdf/2607.20891 §4.2 (2026-10-10; READ-PARTIAL)
    bears on: E1, the owner's "knowledge improves filtering" claim (c), K14, K7
    limit:    The documents are synthetic, and adoption is scored by an LLM judge.

F3. **When later evidence contradicts an early claim, repairing the reasoning built on that claim is the part that measurably helps. Replacing the fact alone does not.** ReTree stores where each claim entered and which source it came from. On a contradiction it goes back to that point, swaps the evidence, regenerates the summaries built on it and prunes the affected branches. Pooled over 2,149 questions it beat a full-transcript ReAct agent by 13.9 points. It beat FlatUpdate — same conflict detector, but it only replaces the refuted fact — by 2.2–4.7 points on every dataset. A rolling report-style memory (the ReSum/IterResearch style) LOST attribution: 16.8% of its citations supported their claims, vs 37.7% for the full transcript and 44.5% for ReTree.
    who:      Yang et al., Shanghai Jiao Tong; arXiv 2608.10676. Their own method, with Qwen3-8B on multi-hop QA (Bamboogle, FRAMES, 2Wiki, HotpotQA), not open-ended research.
    evidence: "When newly retrieved evidence contradicts an earlier claim, ReTree traces back to the node where the claim was introduced, replaces outdated evidence, regenerates summaries, prunes affected branches, and resumes search." — https://arxiv.org/abs/2608.10676 ; Tables 1–2 (2026-10-10; READ-PARTIAL)
    bears on: E1 (going back over what was admitted early), E2, K4, the "forget between rounds" mechanism
    limit:    One 8B backbone, short-hop QA, judged by GPT-5.

F4. **Dropping old observations helps mid-strength models and hurts saturated ones.** The rule tested hides all but the 5 most recent tool outputs. The gain:
    - with a weak retriever: +6–7;
    - a strong retriever plus a mid-capacity model: +11.7;
    - Tongyi-DeepResearch: −1.1;
    - GPT-OSS-120B on live-web GAIA: −4.8.

    Why it works: attention to an observation collapses after the most recent turn, and agents reopen almost only the newest page or the very first one. Fixed queries outnumber broken ones about 3:1 for the mid model and about 1:1 for the saturated one.
    who:      Zhang, Xu et al. (UCSD, Berkeley, TAMU, UIUC; McAuley); arXiv 2606.00408. A sweep over 4B–284B backbones and 3 retrievers. They sell nothing. (Round 1 had this at abstract level only.)
    evidence: "masking implements a token-for-turn trade-off: it removes observations the model has largely stopped attending to and pages the agent rarely re-opens" — https://arxiv.org/pdf/2606.00408 Table 1, §5.3 (2026-10-10; READ-PARTIAL)
    bears on: E2 (pruning), K-mechanism "forget between rounds" (Kimi's discard-all), (b)
    limit:    The authors conclude "Future engineering should therefore pivot from aggressive heuristic pruning toward high-fidelity retrieval."

F5. **Without training, compressing the history loses to keeping all of it, and a strong model in plain ReAct beats every managed 36B variant.** Results on BrowseComp-Plus (N=150), Seed-OSS-36B:
    - full-context ReAct (327K): 0.478;
    - 32K summary agent: 0.386;
    - folding agent before RL: 0.420;
    - folding agent after the paper's RL (FoldGRPO): 0.620;
    - GPT-5 in plain 327K ReAct: 0.793.
    who:      Sun, Lu et al., ByteDance Seed (+CMU, Stanford); arXiv 2510.11967. The vendor's own method.
    evidence: "without performing RL, the context folding agent already surpasses the 32K-context ReAct and context summarization baselines, though it does not yet match the performance of the long-context ReAct agent" — https://arxiv.org/pdf/2510.11967 Table 1 (2026-10-10; READ-PARTIAL)
    bears on: (b), (d), E2
    limit:    The GPT-5 row is a reference point, not a cost-matched comparison.

F6. **Pruning the model decides on beats pruning on a fixed rule. A memory the model rewrites, though, loses facts.**
    - **Traverse:** letting the agent decide when to "seal" (compress and reset) gave 65.23 Avg@3 vs 54.95 for automatic compaction at 90% context. The first seal came at turn 67, vs turn 217 for the automatic rule. Average turns also rose from 112 to 218, so the gain is confounded with extra compute.
    - **Context Language Models:** the model edits its own context file. Untrained, it scored 59.4% on BrowseComp-Plus at 32K, 11.4% (relative) above Codex-style summarization with 21.5% fewer FLOPs (Qwen3.6-27B). The authors invoke the Bitter Lesson.
    - **AMBER (against "delete old graphs"):** RL-trained overwrite memories "delete key information required by the trajectory, as well as corrective feedback". An append-only memory beat them by 4.09 points (WebArena-Lite, Shopify).
    who:      Traverse — PKU plus an unnamed second affiliation (arXiv 2609.37082). CLM — UW, Meta Superintelligence Labs, MIT (Zettlemoyer, Koh, Lambert; arXiv 2609.37725). AMBER — NCSU + Shopify (arXiv 2610.07118). All three measure their own methods.
    evidence: "allowing the agent to decide when to compact its context yields a substantial performance gain: Active Seal improves Avg@3 by 10.28 points" — https://arxiv.org/pdf/2609.37082 Table 3; "Our findings echo The Bitter Lesson (Sutton, 2019)" — https://arxiv.org/pdf/2609.37725 §1 (2026-10-10; READ-PARTIAL)
    bears on: E2, (b)
    limit:    CLM's own safety section warns that an editable context lets self-inserted instructions persist. It cites OpenAI's report "Self-generated prompt injections in compaction summaries".

F7. **Bitter-lesson evidence: a minimal loop with a strong model and a well-tuned plain keyword retriever (BM25) is near the top.** Pi-Serini runs on a minimal harness with no sub-agents and three tools (retrieve, browse, read). With gpt-5.5 it reached 83.1% on BrowseComp-Plus with 94.7% evidence recall. In its ablations, tuning BM25 added +18.0% accuracy and searching deeper added +25.3% recall.
    A diagnosis of six agents on the same benchmark found accuracy tracks cumulative evidence recall (r = 0.99 across agents; descriptive, n = 6), not the number of searches or context used. 77.5–93.6% of search episodes added no new evidence. Correct runs found their evidence early and stopped. What marked the stronger agents was fewer redundant queries, not more searching.
    who:      Hsu, Yang, Lin (Waterloo), arXiv 2605.10848 — selling nothing. Liu, Mao, Zhu, Chua (Renmin/NUS), arXiv 2608.01913, using human relevance judgments. Practitioner: Arvind Narayanan (Princeton; X post, 154 likes / 16.9k views).
    evidence: "a well-configured lexical retriever with sufficient retrieval depth can support effective deep research when paired with more capable LLMs" — https://arxiv.org/abs/2605.10848 ; "Answer accuracy is better correlated with the quality of retrieved evidence, especially cumulative retrieval recall, than with the number of searches or the amount of context consumed." — https://arxiv.org/abs/2608.01913 ; "this kind of task-specific harness quickly got swallowed by general-purpose agents" — https://x.com/random_walker/status/2090754227907833984 (2026-10-10; READ-PARTIAL / READ-FULL for the tweet)
    bears on: (d), (e), K1 (accretion: most steps add nothing), K8 (stopping)
    limit:    BrowseComp-Plus only. Its corpus flatters retrieval (F11).

F8. **Against the pure bitter lesson: structure still adds points on top of strong models.**
    - **Question's Gambit:** a structured first retrieval move (split the question into clues, run complementary searches, rerank) took Pi-Serini with gpt-5.5 from 83.1% to 90.5%.
    - **ArcticSwarm** (Qwen3.5-27B, full 830 questions):
      - single agent: 48.4%;
      - majority vote over 20–40 single-agent runs: plateaued at 62.5–63.5%;
      - ArcticSwarm: 82.6%, at about the same token cost as 20 votes.
    - Inside ArcticSwarm, letting agents read peers' partial findings during gathering cost 3.8 points ("early consensus"). Removing the three review gates cost 6.3 points.
    - In GPT-5 runs, questions where the orchestrator never opened an "alternative/contrarian" task scored 27.4% vs 78.5% on BrowseComp. This is observational and confounded by difficulty, though the gap holds within every difficulty tier.
    who:      Gambit — Hamidi Rad et al., arXiv 2609.14412. ArcticSwarm — SNU + Snowflake AI Research, arXiv 2609.01870. Both are the authors' own systems.
    evidence: "access to peers’ partial findings cause search to converge on an early candidate before alternatives are tested" — https://arxiv.org/abs/2609.01870 , Table 3; "improving answer accuracy from 83.1% to 90.5% with gpt-5.5 over Pi-Serini" — https://arxiv.org/abs/2609.14412 (2026-10-10; READ-PARTIAL)
    bears on: (d), E1 (early commitment), K11 (DivInit, Kim; share findings, isolate judgment)
    limit:    ArcticSwarm's single-agent comparison uses a 27B model. No paper compares a frontier model's simple loop against a swarm at the same cost.

F9. **Each tier of delegation loses findings.** Results:
    - Carry-forward follows a power law with exponent δ = 0.34 (95% CI [0.30, 0.38]) on 600 traces: surface four times as many sources and only 2.3 times as many get carried forward.
    - Per-hop retention is C = 0.571 over 16,082 hops, so each extra tier costs about 45% of findings.
    - In annotated multi-agent traces, 1 brief in 16 went off-target.
    - Delegation does not respond to a filling context (odds ratio 0.969 per doubling of context); agents delegate as an opening move.
    - The paper's own conclusion is that flat is best for yield; depth instead buys a root context that is smaller and easier to keep clean.
    who:      Rong He, a single author; arXiv 2609.17464. The "production" traces were released with an earlier study and run on six public QA corpora.
    evidence: "a research agent that surfaces four times as many sources carries only 2.3 times as many forward" — https://arxiv.org/pdf/2609.17464 abstract, §4 (2026-10-10; READ-PARTIAL)
    bears on: (d), K11, E2 (what gets dropped at each handoff)
    limit:    The model is analytic, and the traces are QA, not report synthesis.

F10. **Most released agents read a page once, judged against the goal as it stood at fetch time. Agents that can re-read pages later with what they have since learned did better.**
    - **Tongyi's released inference code:** each visited page is summarized immediately against the then-current goal into rationale, evidence and summary fields. At 110×1024 tokens the agent is told to stop and answer.
    - **Fetch-then-Explore:** pages are kept in a per-question workspace and evidence is pulled from them later. It led BrowseComp (200 sampled questions) at every backbone: 44.5 vs 37.5 for fetch-time summaries (Qwen3.5-35B), and 70.5 vs 64.0 (DeepSeek-V4-Pro).
    - Agents rarely search across everything they have saved: only 1–10.5% of questions ever trigger a whole-workspace search.
    who:      Tongyi Lab code (github.com/Alibaba-NLP/DeepResearch @ f72f75d, 2026-02-27). Fetch-then-Explore — Liu et al., Renmin, Xiaohongshu, NUS; arXiv 2608.02097.
    evidence: "Visit-and-read injects a reading of the page into the message history at fetch time, fixing that reading before the agent knows which fact it will need." — https://arxiv.org/abs/2608.02097 ; inference/prompt.py:40-50 and inference/react_agent.py:186-193 in the clone (2026-10-10; READ-PARTIAL)
    bears on: E1 (evidence judged early, never re-judged), (c), K4
    limit:    WideSearch was a tie, and the gains are 5–14 points.

F11. **The benchmarks themselves are weakly validated.**
    - **BrowseComp-Plus:** its ~100K-document corpus was built per question from that question's own evidence plus mined distractors. Moving 57 of its questions onto a 553M-document pre-training web corpus (NVIDIA's ClimbMix) cut the strongest agent's evidence recall from 84.3% to 21.4%, with 63% more searches, while accuracy fell only 5 points.
    - **Long-form deep-research benchmarks:** Ai2's meta-evaluation found they are mostly validated by pairwise human preference over 3–7 systems, with human–model agreement of 50–75%. DeepResearch Bench reports 68.4% inter-annotator agreement and 71.3% judge agreement over 4 systems.
    - **LLM judges:** in the REFLECT benchmark, the best judges catch planted failures in agent traces under 55% of the time, and do worst at checking evidence.
    - **Contamination:** agents that find answers during search inflate scores by up to 4%.
    - **WANDR** (500 wide-and-deep tasks): the best of six production systems scores 0.363 soft F1.
    who:      Sharifymoghaddam … Jimmy Lin (2608.20317); Ai2 / Hwang, Feldman et al. (2603.06942); Yale + IBM (2605.19196); Wang et al. (2606.05241); Polshkov et al. (2608.14747).
    evidence: "the evidence and the distractors were both selected per query" — https://arxiv.org/abs/2608.20317 ; "pairwise preference rankings are best suited for system-level evaluation, while explicit metric-wise annotations and expert annotators are critical for reliable metric-level assessment" — https://arxiv.org/pdf/2603.06942 ; "even the best-performing models achieve overall accuracies below 55%" — https://arxiv.org/pdf/2605.19196 (2026-10-10; READ-PARTIAL, abstract-level for 2606.05241 and 2608.14747)
    bears on: (e), K14
    limit:    Nearly every number in F4–F10 is a BrowseComp(-Plus) number.

F12. **Where pruning happens matters more than how the pruned items are scored. Most iterations are stagnant.**
    - Pruning early in the pipeline saved the most, up to 73% of tokens with little loss in judged quality (DeepResearchGym, rubric judge).
    - Across many deep-research agents, most iterations "contribute little or no improvement". A retrieval-aware controller based on novelty and coverage cut 14 search calls on average, for +3% accuracy on average (up to +10%).
    - Vendor number: Anthropic reports +29% from context editing and +39% with its memory tool on an internal agentic-search set (no n given), and −84% tokens in a 100-turn search eval.
    who:      UMass + Adobe (2608.08389); Soudani, Hasibi et al. (2608.15191); Anthropic (seller, internal eval).
    evidence: "pruning effectiveness depends more on where pruning is applied than on the specific scoring rule" — https://arxiv.org/abs/2608.08389 ; "combining the memory tool with context editing improved performance by 39% over baseline" — https://www.anthropic.com/news/context-management (2026-10-10; READ-PARTIAL)
    bears on: E2, K8 (stopping)
    limit:    The quality numbers are judged by LLMs. Anthropic's are the seller's own measurement.

## Against the claims (and the owner's intuition)
- **"Delete old graphs" helps only some agents.** Masking hurts saturated models (−1.1, −4.8; F4). Untrained summarization loses to keeping everything (F5). Report-style memory cuts citation precision from 37.7% to 16.8% (F3). Overwrite memories delete corrective feedback (F6). What survives is pruning the model triggers itself, and repairing claims that were contradicted.
- **"Early judgments are worse" is not what was measured.** Planted falsehoods admitted early are adopted LESS (40.5%) than the same ones admitted late (85.5%), because the remaining research challenges them (F2). The measured defect is narrower: judgment is worse when made with no later re-check, and when made by whoever authored the step (F1).
- **"The more you know, the better you filter" fails when "what you know" is your own trajectory.** Accumulated self-authored context made agents' filtering worse, and a fresh context fixed it (F1). Agents also barely look at their middle observations (F4), so much of what has accumulated is not being used.
- **Harness vs model (C6/K11).** A minimal loop with a strong model is near state of the art (F7). Each extra tier of delegation costs about 45% of findings (F9). Narayanan reports general agents swallowed dedicated deep-research tools. The counterpoint is F8.

## Not covered by any claim
- **The first move is a design lever** (Gambit, +7.4 points; DivInit in K11). Evidence arrives early or never; the long tail of searching is waste (F7).
- **Deferred, repeatable extraction** (F10): keep the page and re-read it once you know what to look for. This is the agent form of "re-assess with later knowledge", and agents rarely use it.
- **Cross-document structure built before any query arrives:** AtlasNav, +7.47 strict accuracy with 30.22% lower query-time inference cost on BrowseComp-Plus with DeepSeek (abstract only; 2608.24764). This is the nearest thing to the owner's "graph", and it is built offline.
- **Copy inflation:** tokens copied from retrieved documents get inflated confidence. Voting on how well each answer is grounded in what that run retrieved beats confidence-weighted voting by up to +5.4 (2608.24024, abstract).

## Frontier
- CompactionRL (arXiv 2607.05378) and OpenAI's "Self-generated prompt injections in compaction summaries" (alignment.openai.com, Sept 2026): pruning as a safety surface. Cited inside 2609.37725.
- Chen et al. 2026, "Diversity collapse in multi-agent…": dense communication speeds premature convergence. Cited inside 2609.01870.
- AggAgent (2604.11753, Danqi Chen): aggregate parallel rollouts by letting an agent search across all of them, +10.3 on deep-research tasks.
- Growing Harness (2609.26760): a harness learned as code from failures cuts LLM calls 76–92%. A counterpoint for small models.
- Dossier: "Deep Research via Ledger-Driven Branching Search" (doi 10.1145/3786335.3813122), met in STORM's forward chain; 0 citations, not read.
- Also not read: REMORY (2610.11287), HyMem (2608.15703), Adaptive Consistency Graph (2609.32754), SearchSwarm (2606.09730), LongCat-DeepResearch (2609.36071; it says "further planning refinement has mixed effects").

## Lane state
- arXiv API, newest first: READ-PARTIAL. Three queries ran, then the API returned nothing (likely rate-limited); I switched to the arXiv HTML search and abstract pages, which worked.
- arXiv full texts via pdftotext: 20 papers grep-read in the sections that carry the numbers. None was read cover to cover.
- cite-chain fwd: STORM — 38 citers (WORKING, mostly off-topic). WebWeaver — 1 citer. BrowseComp-Plus — 3 citers. OpenAlex barely indexes citations from arXiv-only papers, so this lane is thin, not empty. TTD-DR was not run.
- Tongyi DeepResearch repo: READ-PARTIAL (inference/ only). The WebAgent/* subprojects (AgentFold, WebResummer, WebWeaver code) were not opened.
- X via xh.sh: 4 queries. Most hits were paper-promotion posts (one Japanese-language summary account, small hype accounts). One practitioner post was usable (Narayanan). The min_faves:20 query returned 1 post. I found no practitioner ablation reports.
- Anthropic context-management post: READ-PARTIAL. Kimi-Researcher, the SFR-DeepResearch body, AgentFold and ReSum full texts: abstract only (EXHAUSTED budget).

## Source register
- https://arxiv.org/pdf/2606.00408 — READ-PARTIAL
- https://arxiv.org/pdf/2608.23045 — READ-PARTIAL
- https://arxiv.org/pdf/2607.20891 — READ-PARTIAL
- https://arxiv.org/pdf/2608.10676 — READ-PARTIAL
- https://arxiv.org/pdf/2510.11967 — READ-PARTIAL
- https://arxiv.org/pdf/2609.37082 — READ-PARTIAL
- https://arxiv.org/pdf/2609.37725 — READ-PARTIAL
- https://arxiv.org/pdf/2610.07118 — READ-PARTIAL
- https://arxiv.org/pdf/2605.10848 — READ-PARTIAL
- https://arxiv.org/pdf/2608.01913 — READ-PARTIAL
- https://arxiv.org/pdf/2609.14412 — READ-PARTIAL
- https://arxiv.org/pdf/2609.01870 — READ-PARTIAL
- https://arxiv.org/pdf/2609.17464 — READ-PARTIAL
- https://arxiv.org/pdf/2608.02097 — READ-PARTIAL
- https://arxiv.org/pdf/2608.08389 — READ-PARTIAL
- https://arxiv.org/pdf/2603.06942 — READ-PARTIAL
- https://arxiv.org/pdf/2605.19196 — READ-PARTIAL
- https://arxiv.org/pdf/2608.20317 , 2608.15191 , 2510.15862 — READ-PARTIAL (downloaded; abstract and a few sections)
- https://arxiv.org/abs/2608.24764 , 2608.10743 , 2610.11287 , 2609.33509 , 2609.36071 , 2610.06689 , 2609.29444 , 2609.26760 , 2510.24699 , 2509.13313 , 2508.21433 , 2509.06283 , 2606.19893 , 2608.24024 , 2604.11753 , 2606.05241 , 2608.14747 — abstract only
- https://github.com/Alibaba-NLP/DeepResearch (commit f72f75d) inference/react_agent.py, prompt.py, tool_visit.py — READ-PARTIAL
- https://www.anthropic.com/news/context-management — READ-PARTIAL
- https://x.com/random_walker/status/2090754227907833984 — READ-FULL
- X search hits (LangChainJP, slash1sol, stretchcloud, rohanpaul_ai, and others on CLM and ArcticSwarm) — DIGEST-level routers only
- OpenAlex forward chains: 10.18653/v1/2024.naacl-long.347 (STORM), arXiv 2509.13312 (WebWeaver), 2508.06600 (BrowseComp-Plus) — WORKING (thin)
