<!-- AGENT OUTPUT — R1-I multi-agent research mechanics. Returned by a subagent, not read by the chair unless a row says so. -->

## Findings

F1. Anthropic's Research system prevents duplicate work by giving each subagent a tight brief, not by letting workers share findings. Subagents run synchronously and report only to the lead. The lead saves its plan to Memory, puts the results together, and decides whether to spawn more subagents.
    who:      Hadfield, Zhang et al. (Anthropic, who build and sell Claude Research)
    evidence: "subagents misinterpreted the task or performed the exact same searches as other agents" / early agents were "distracting each other with excessive updates" — https://www.anthropic.com/engineering/multi-agent-research-system (2026-09-26; READ-FULL; local copy guidesfm/research/articles/how-we-built-our-multi-agent-research-system.md:43,51)
    bears on: Q7, C6, C2 ("start wide, then narrow down", :65-67)
    limit:    No duplication rate is reported. The 90.2% gain over a single agent is on an internal eval. The post also says the synchronous design means "subagents can't coordinate" (:115).

F2. In Anthropic's open-source lead prompt, overlap is removed at decomposition time by drawing boundaries. Findings flow back only to the lead, which updates the plan from them. The subagent prompt runs an OODA loop over "what has been learned so far" and stops at diminishing returns.
    who:      Anthropic cookbook; the last commit touching the file is 66ab04a (2025-07-29)
    evidence: "Avoid overlap between subagents - every subagent should have distinct, clearly separate tasks, to avoid replicating work unnecessarily" — github.com/anthropics/anthropic-cookbook patterns/agents/prompts/research_lead_agent.md:105 (see also :41 "boundaries … to prevent overlap", :66 "Update the search plan … based on findings"); research_subagent.md:10,45 (2026-09-26; READ-FULL)
    bears on: Q7, C6, C1, Q6
    limit:    This is a prompt, not a measurement.

F3. Cognition first said to share full traces or not to go multi-agent. Its April 2026 revision allows read-only helpers and manager/child setups but still lists sibling-to-sibling discovery transfer as unsolved.
    who:      Walden Yan (Cognition, which sells Devin)
    evidence: "Cross-agent communication, a sub-agent writing messages back to its manager to be passed to other agents in the agent team, doesn't happen by default" / "How does a child agent surface a discovery that should change its siblings' work?" — https://cognition.ai/blog/multi-agents-working (local guidesfm/.../multi-agents-what-s-actually-working.md:90,98); 2025 principle "Share context, and share full agent traces" — don-t-build-multi-agents.md:55 (read 2026-09-26; READ-FULL)
    bears on: Q7, C6
    limit:    No numbers are given on sharing. Cognition's own reviewer works best when agents share no context (see Against).

F4. Kim et al. confirm 17.2× and 4.4×, but these are trace-level error amplification, meaning extra work estimated from token analysis. Task-level amplification is only 1.1–1.3. After controls, error amplification does not significantly predict success. On web browsing (BrowseComp-Plus), agents that never talk did worse than one agent (-35%), while peer exchange through debate gained +9.2%.
    who:      Yubin Kim, Xin Liu, Daniel McDuff et al. (Google Research, DeepMind, MIT), arXiv 2512.08296v3
    evidence: "Independent systems amplify trace-level errors 17.2× through unchecked error propagation … Centralized coordination, however, contains this to 4.4×" — https://arxiv.org/pdf/2512.08296 (2026-09-26; READ-PARTIAL, §1, §4, Table 5, App. E)
    bears on: C6, Q7
    limit:    Conditions were 3 agents at a matched ~4,800 reasoning tokens per trial, with max 10 iterations for a single agent. The regression gives error amplification β=0.014, p=0.658. On held-out Gemini models, the no-communication setup matched or beat a single agent (+11.1%, +5.9%). The paper defines redundancy two different ways: as cosine similarity of agent outputs (p.13) and as the share of subtasks done by more than one agent (p.18).

F5. MAST, a taxonomy built from 1,642 traces, finds that pure information-passing failures are rare. Withholding and ignored input are small next to step repetition (15.7%) and reasoning-action mismatch (13.2%). The authors locate the cause in agents failing to model what other agents need to know, not in the message format.
    who:      Cemri, Pan, Yang et al. (UC Berkeley), arXiv 2503.13657v3
    evidence: "withholding crucial information (FM-2.4, 0.85%), ignoring other agents' input (FM-2.5, 1.90%)" — https://arxiv.org/pdf/2503.13657 (2026-09-26; READ-PARTIAL)
    bears on: Q7, C6
    limit:    The traces are coding, math and GAIA tasks, not research. Step repetition is defined as repeated steps in general, not duplicated work between agents.

F6. STORM's ablation is the clearest test of whether each find should drive the next question. Asking questions one at a time, each conditioned on the answers so far, collected 99.83 unique references. Generating the same number of questions all at once collected 39.56. In the code, the parallel persona conversations share nothing while they run; results are merged by URL only at the end.
    who:      Shao, Jiang, Lam et al. (Stanford OVAL), arXiv 2402.14207v2; repo stanford-oval/storm (31.5k★) @fb951af
    evidence: "'STORM w/o Conversation' gives much worse results, indicating reading relevant information is crucial to generating effective questions" — https://arxiv.org/pdf/2402.14207 (Table 3, Table 5); code knowledge_curation.py:59-62,327-342 (each thread keeps its own `dlg_history`), storm_dataclass.py:66-79 (merge by URL) (2026-09-26; READ-PARTIAL)
    bears on: C1, Q4, C6
    limit:    Measured on outline recall and reference counts, not on correctness. Uses GPT-3.5/4 and Wikipedia-style topics.

F7. In Co-STORM, the moderator writes the next question from information that was retrieved but not yet used. It favours material that is on-topic but unlike the query that found it. The code goes further than the paper: it also pushes away from anything already in the shared knowledge base, so that base serves as a "seen" set that steers the next search away from what is already known.
    who:      Jiang, Shao et al. (Stanford), arXiv 2408.15232v2
    evidence: "This reranking function prioritizes information that does not directly answer the original question but is relevant to the topic t." — https://arxiv.org/pdf/2408.15232 §3.5. In the code, the score is `(1-max_query_sim)^0.5 * (1-cited_snippets_sim)^0.5 * claim_gate` — co_storm_agents.py:190-246 @fb951af (2026-09-26; READ-PARTIAL + code)
    bears on: C1, C3, Q3, Q7
    limit:    Removing the moderator hurt more than removing experts (Depth 3.77→3.41, Novelty 3.05→2.89) under LLM judges with simulated users. The human study had 20 participants. The code formula differs from the paper's.

F8. Magentic-One's orchestrator keeps a task ledger of verified facts, facts to look up, facts to derive and educated guesses. That ledger is the only thing carried across replans: every worker's context is wiped each time the plan changes.
    who:      Fourney, Bansal et al. (Microsoft Research AI Frontiers), arXiv 2411.04468v1
    evidence: "we force all agents to clear their contexts and reset their states after each plan update" / "without the full ledgers, performance drops by 31%" — https://arxiv.org/pdf/2411.04468 (2026-09-26; READ-PARTIAL)
    bears on: Q7, C6, Q4
    limit:    The ablation is on GAIA validation. Its automated error codes include "ineffective-team-communication", with the example "Two agents simultaneously accessed order histories … resulting in duplicated efforts"; no frequency is given for it.

F9. Google's co-scientist shares by broadcast: meta-review critiques are appended to every agent's prompt. A Proximity agent groups similar hypotheses to remove duplicates.
    who:      Gottweis, Weng, Natarajan et al. (Google), arXiv 2502.18864v2 (now titled "Accelerating scientific discovery with Co-Scientist")
    evidence: "The Meta-review agent generates feedback applicable to all agents, which is simply appended to their prompts in the next iteration" — https://arxiv.org/pdf/2502.18864 (2026-09-26; READ-PARTIAL)
    bears on: Q7, C6
    limit:    Meta-review raised review AUC from 0.521 to 0.597 on the authors' own dataset and from 0.629 to 0.634 on GPQA. The duplicate removal itself is backed only by a correlation between proximity and quality differences; there is no ablation.

F10. DeLM uses a queue plus a shared verified context. Each worker writes back short tagged notes (FACT / FAIL / PATCH_SUMMARY), so one agent's dead end becomes a constraint for the others. Checking a note against its evidence before admitting it is the part that matters most.
    who:      Yuzhen Mao, Azalia Mirhoseini (Stanford), arXiv 2606.10662v1
    evidence: "In isolated forks, a negative result remains local to one trajectory, so other attempts may spend their own budget rediscovering the same failure." / "Removing verification causes the largest drop, from 60.1% to 55.2%" — https://arxiv.org/pdf/2606.10662 (2026-09-26; READ-PARTIAL)
    bears on: C6, Q7, Q5
    limit:    Measured on SWE-bench (+9.3pt Avg@1 with Gemini-3-Flash; much less with Opus 4.6) and LongBench-v2. Its value for research workflows is only claimed as future work.

F11. Argus keeps one shared evidence graph. Evidence nodes are deduplicated by URL, and edges mark whether evidence supports or contradicts a claim. With the searchers' output held fixed, giving the navigator this structure instead of flat text added 5.2 points.
    who:      Zhen Zhang, Xinyu Wang et al. (MiroMind AI, a vendor), arXiv 2605.16217v3
    evidence: "Evidence nodes are deduplicated at the source-URL level, preventing any single page from inflating the support count of a claim" — https://arxiv.org/pdf/2605.16217 §2.2, Table 3 (text only 69.3 → bare graph 72.0 → full graph 74.5, BrowseComp, 8 searchers) (2026-09-26; READ-PARTIAL)
    bears on: C3, C6, Q5
    limit:    The claim that parallel rollouts "duplicate rather than complete" is asserted, not measured. The navigator is trained with RL.

F12. DivInit measures duplication between parallel search threads. Threads that start with similar first queries retrieve overlapping documents and fail together ("anchor collapse"). Choosing diverse first queries fixes it; diversifying later turns adds nothing.
    who:      Murali, Coelho, Xiong et al. (CMU, Lisbon, NOVA), arXiv 2606.17209v1
    evidence: "extending it to turns 1 through N for N ∈ {1, ..., 8} yields no gain on the open-web benchmarks" — https://arxiv.org/pdf/2606.17209 (2026-09-26; READ-PARTIAL)
    bears on: C6, C2, Q7
    limit:    Gains of 5–7 points on multi-hop QA are reported as pass@k. Not tested outside search.

F13. WebResearcher's parallel "Research-Synthesis" mode has no sharing at all between workers. Each researcher compresses its own work into an evolving report between rounds, and one synthesiser reads only the final reports.
    who:      Tongyi Lab (Alibaba), arXiv 2509.13309v2 (repo Alibaba-NLP/DeepResearch, 20.0k★)
    evidence: "multiple Research Agents concurrently solve the target problem following the IterResearch method, with each agent deriving a final report and the predicted answer" — https://arxiv.org/pdf/2509.13309 (2026-09-26; READ-PARTIAL)
    bears on: C6 (against), Q4
    limit:    Scaling from n=1 to 8 helped and flattened after 8, with cost growing linearly. The round-by-round report beats a single accumulating context (HLE 28.8 vs 25.4).

F14. Google's TTD-DR writes a draft first, from the model's own knowledge. Each next search query is generated from the current draft, and each answer is used to revise the draft.
    who:      Google Cloud AI Research, arXiv 2507.16075v1
    evidence: "we feed the current draft report into Stage 2a of the backbone DR workflow to inform the generation of the next search query" — https://arxiv.org/pdf/2507.16075 (2026-09-26; READ-PARTIAL)
    bears on: C1, Q4
    limit:    Adding draft-driven search on top of self-evolution raised the win rate against OpenAI DR from 60.9 to 69.1 (LongForm) and 59.8 to 74.5 (DeepConsult). It is judged by LLM raters, applied cumulatively, and in a single agent.

F15. WebWeaver alternates searching with rewriting an outline that cites into a memory bank. Its evidence is supporting but weak.
    who:      Tongyi Lab, arXiv 2509.13312v3
    evidence: "the outline undergoes more than two optimization cycles on average" — https://arxiv.org/pdf/2509.13312 (2026-09-26; READ-PARTIAL)
    bears on: C1
    limit:    The per-round ablation uses only samples that reached three rounds ("We collect the samples with three-round outline optimization"), which is a selection effect. There is no head-to-head with a static outline at equal budget.

F16. Anthropic's 16-agent C-compiler team avoided duplication with lock files for claiming tasks. When all agents still converged on one bug, the fix was to split the problem using an outside oracle, not to have agents talk more.
    who:      Nicholas Carlini (Anthropic)
    evidence: "Every agent would hit the same bug, fix that bug, and then overwrite each other's changes. Having 16 agents running didn't help because each was stuck solving the same task." — https://www.anthropic.com/engineering/building-c-compiler (2026-09-26; READ-PARTIAL)
    bears on: C6, Q7
    limit:    This is coding with a test oracle. Agents also kept "a running doc of failed approaches".

F17. Kimi K2.5's Agent Swarm keeps subagents' contexts isolated; only their outputs reach the orchestrator. On BrowseComp, simply discarding old context did most of the work.
    who:      Kimi Team (Moonshot), arXiv 2602.02276v2
    evidence: "On BrowseComp, K2.5 achieves 60.6% without context management techniques, 74.9% with Discard-all" (Swarm reaches 78.4%) — https://arxiv.org/pdf/2602.02276 (2026-09-26; READ-PARTIAL)
    bears on: Q7, "forgetting" practice
    limit:    Vendor numbers. The orchestrator is trained with RL, including a reward that pushes it to spawn subagents at all.

F18. Two blackboard systems, in which agents coordinate through a shared board, show modest measured gains.
    who:      Salemi, Palangi et al. (UMass and Google Cloud), arXiv 2510.01285v2; Han and Zhang (CAS), arXiv 2507.01701v1
    evidence: "performance declines on three datasets if the cleaner agent is asked to mark the redundant messages rather than directly remove them" — https://arxiv.org/pdf/2507.01701 (2026-09-26; READ-PARTIAL)
    bears on: C6, Q7
    limit:    In Salemi et al., requests are broadcast but helpers answer only the main agent. The gain is 13–57% relative, from low bases (for example 5.03%→7.90%). In Han and Zhang, deleting redundant messages instead of flagging them gains less than 1.6 points on math and reasoning tasks, not search. Removing their control unit cost 3–4.5× more tokens at similar accuracy.

F19. Gemini Deep Research keeps shared state between its planner and task models, but mainly so a failed step does not restart the whole task. At each step the planner grounds on "all information gathered so far" to find gaps and contradictions.
    evidence: "a novel asynchronous task manager that maintains a shared state between the planner and task models, allowing for graceful error recovery" — https://gemini.google/overview/deep-research/ (2026-09-26; READ-PARTIAL)
    bears on: Q7, C1
    limit:    No numbers are published.

## Against the claims

- **C6: working independently can be the design, not a defect.** WebResearcher (F13) and Kimi (F17) isolate their workers and still gain. On held-out Gemini models, Kim et al.'s no-communication setup matched or beat a single agent (F4). Kim et al. also find redundancy helps slightly as agent count grows (β=0.024, p=0.034) and that "optimal redundancy occurs at R ≈ 0.41", with R>0.50 hurting (r=−0.136).
- **C6: sharing has measured costs.**
  - Anthropic's early agents were "distracting each other with excessive updates" (F1).
  - In DeLM, AOrchestra-Parallel (a baseline that couples threads through a central agent) improved single-attempt accuracy but lowered pass@2/4. The authors read this as reduced exploration diversity.
  - Admitting unverified findings to shared memory lowered accuracy from 60.1% to 55.2% (F10).
- **C6: duplication is usually removed by partitioning, not by passing findings.** The methods are briefs with boundaries (F2), lock files plus an oracle split (F16), one-time diversification of the first query (F12), and URL-level merging after the fact (F6, F11).
- **Clean context beats shared context for checking work.** Cognition: "we found this technique to work best when the coding and review agents do not share any context beforehand." — multi-agents-what-s-actually-working.md:48
- **C2: the pattern varies.** DivInit makes the breadth decision once, at the first move, and nothing after it matters. TTD-DR goes deep first: it drafts from memory, then searches to correct the draft.

## Not covered by any claim

- **Deliberate forgetting between rounds:**
  - Magentic-One wipes worker contexts (F8), and WebResearcher and Tongyi rebuild each round from the report alone.
  - Kimi's Discard-all took BrowseComp from 60.6% to 74.9% (F17).
  - MiroThinker keeps only the most recent tool outputs and reports this "does not lead to degradation in performance" — https://arxiv.org/pdf/2511.11793 (2026-09-26; READ-PARTIAL).
- **Checking a finding before it enters shared memory,** so an unsupported claim cannot spread to other workers (DeLM, F10).
- **Sharing failures and negative results:** DeLM's FAIL notes and Carlini's running "failed approaches" doc (F10, F16).
- **Guesses kept as marked guesses:** Magentic-One's ledger stores "educated guesses" separately from verified facts (F8).
- **Steering toward retrieved-but-unused material** to reach unknown unknowns (F7).

## Frontier

- Masking stale observations (arXiv 2606.00408). The benefit of dropping old observations follows an inverted U depending on model strength; it collapses for saturated models. https://arxiv.org/abs/2606.00408
- Kimi's "serial collapse": an orchestrator left alone falls back to acting as a single agent and needs a reward to use parallelism (arXiv 2602.02276 §PARL).
- Salesforce EDR (arXiv 2510.17797) shares a todo.md between agents and a human and makes decomposition "duplicate-aware". No ablation found.
- W&D (arXiv 2602.07359) scales parallel tool calls inside one agent instead of multiple agents.
- MultiSearch (arXiv 2605.13534); AggAgent (Lee et al. 2026, cited in DivInit); AOrchestra (Ruan et al. 2026).
- PatchBoard (arXiv 2605.29313) and Agent Team Work Zone (arXiv 2607.22917) — not read.
- WideSearch (arXiv 2508.07999v2): divide-and-conquer multi-agent beats single agent, but the best multi-agent success rate is 5.1%.
- Co-STORM's mind-map ablation is in its Appendix B — not read.
- Teardowns of research products on disk belong to the local-library lane.

## Lane state

- Anthropic multi-agent research post: READ-FULL (live page plus local copy). Cookbook prompts: READ-FULL.
- Cognition, both posts: READ-FULL (local copies, fetched 2026-06-13).
- Kim et al.; MAST; STORM; Co-STORM; Magentic-One; co-scientist; both blackboard papers; WebWeaver; WebResearcher; Tongyi; DeLM; Argus; DivInit; TTD-DR; Kimi K2.5; MiroThinker; WideSearch: READ-PARTIAL (PDF grep plus targeted sections).
- STORM code: READ-PARTIAL at commit fb951af.
- OpenAI "Introducing deep research": BLOCKED (403 via WebFetch, curl and silver). System card PDF: READ-PARTIAL, single agent: "pivoting as needed in reaction to information it encounters".
- Perplexity Deep Research blog: BLOCKED (Cloudflare, curl and silver).
- Gemini Deep Research overview page: READ-PARTIAL.
- Kimi-Researcher blog: not opened; DIGEST-ONLY.

## Source register

- https://www.anthropic.com/engineering/multi-agent-research-system — READ-FULL
- /Users/seventyleven/Desktop/guidesfm/research/articles/how-we-built-our-multi-agent-research-system.md — READ-FULL
- https://github.com/anthropics/anthropic-cookbook/blob/main/patterns/agents/prompts/research_lead_agent.md , research_subagent.md — READ-FULL
- /Users/seventyleven/Desktop/guidesfm/research/articles/don-t-build-multi-agents.md , multi-agents-what-s-actually-working.md — READ-FULL
- https://www.anthropic.com/engineering/building-c-compiler — READ-PARTIAL
- https://arxiv.org/pdf/2512.08296 , 2503.13657 , 2402.14207 , 2408.15232 , 2411.04468 , 2502.18864 , 2510.01285 , 2507.01701 , 2509.13312 , 2509.13309 , 2510.24701 , 2606.10662 , 2605.16217 , 2606.17209 , 2507.16075 , 2602.02276 , 2511.11793 , 2508.07999 , 2510.17797 , 2605.13534 — READ-PARTIAL
- https://github.com/stanford-oval/storm @fb951af7744dab086e34962e9bc6fe878e145f83 — READ-PARTIAL
- https://cdn.openai.com/deep-research-system-card.pdf — READ-PARTIAL
- https://openai.com/index/introducing-deep-research/ — BLOCKED
- https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research — BLOCKED
- https://gemini.google/overview/deep-research/ — READ-PARTIAL
- https://arxiv.org/abs/2606.00408 , 2602.07359 — abstract only
- https://moonshotai.github.io/Kimi-Researcher/ — DIGEST-ONLY