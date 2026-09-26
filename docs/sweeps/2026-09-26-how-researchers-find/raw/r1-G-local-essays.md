<!-- AGENT OUTPUT — R1-G local essay library. Returned by a subagent, not read by the chair unless a row says so. -->

## Findings
Paths: A = `/Users/seventyleven/Desktop/guidesfm/research/articles/`, X = `/Users/seventyleven/Desktop/guidesfm/research/x-guides/`, T = `/Users/seventyleven/Desktop/researchfms/teardowns/`. I opened every file myself on 2026-09-26. All are READ-FULL unless marked. The teardowns were written by agents in the user's own reverse-engineering pipeline; they quote vendor prompts and papers, and they carry the teardown's own KNOWN or INFERRED label.

**F1. Skim a lot, and deep-read a small, fixed number.**
- who: Michael Nielsen (theoretical physicist, nothing to sell). Backed by Nicholas Carlini (Anthropic, ex-Google Brain, best-paper winner), Neel Nanda (Google DeepMind; recruits for his MATS stream) and Ethan Perez (Anthropic).
- evidence: "quickly skimming a great deal of work… (b) based on that skimming, picking a dozen or so papers each year to read deeply" — A/principles-of-effective-research.md:124. Carlini: "a few each month---I do actually read the full paper top-to-bottom" — A/how-to-win-a-best-paper-award-doing-research-that-matters.md:208-209. Nanda calls it a "barbell strategy" — A/how-to-become-a-mechanistic-interpretability-researcher.md:181. Perez's stop point is "Title+Abstract, Figure 1… Usually stop there" — A/tips-for-empirical-alignment-research.md:96.
- bears on: Q1, Q2, Q6; C2 FOR
- limit: this filters the stream already arriving. It does not reach anything outside that stream.

**F2. The filter before reading asks for one sentence: what is new here?**
- who: Carlini
- evidence: "(1) is this paper useful, and if so, (2) what's the new thing that makes it useful. In a good paper this is answerable in a sentence: your goal is to find that sentence." — A/how-to-win…:194-197
- bears on: Q2

**F3. Chase citations in both directions: backward through related work, forward to the follow-ups that correct famous papers.**
- who: Joshua Achiam (OpenAI; the essay ends with a jobs link) and Nanda
- evidence: "Use the related work section and citations to find closely-related papers and do a deep dive" — A/spinning-up-as-a-deep-rl-researcher.md:70. Nanda: "an exciting paper, that gets a lot of attention yet has some subtle flaws, and follow-up work identifies and clarifies these" — A/favourite-mech-interp-papers.md:146
- bears on: Q1, Q5; C1 FOR, C5 FOR, C4 FOR (attention ≠ correctness)
- limit: backward chasing stays inside one citation community.

**F4. People come before documents. The unwritten "big picture" is only available by asking.**
- who: Richard Hamming (30 years at Bell Labs, Hamming codes, nothing to sell), Perez, and Preetum Nakkiran as quoted by Chris Olah
- evidence: "I talk to people and ask questions when I think they can answer me and give me clues that I do not know about. I go out and look!" — A/you-and-your-research.md:201. Perez: "Talking with people can often be superior though" — A/tips…:112, and "Twitter + what people share on Slack + what your collaborators/colleagues send you is a pretty good 80/20" — :94. Nakkiran: "'big picture' research goals. This is almost never written in papers" — A/research-taste-exercises.md:136
- bears on: Q1, Q3
- limit: people get filtered too. Hamming drops "sound absorbers" (:199).

**F5. A standing list of 10–20 open problems is the device that makes connections.**
- who: Hamming, and Paul Graham (his essays double as YC marketing)
- evidence: "between 10 and 20 important problems for which they are looking for an attack. And when they see a new idea come up, one hears them say 'Well that bears on this problem.'" — A/you-and-your-research.md:103. Graham: "noticing that two unanswered questions are the same" — A/how-to-do-great-work.md:289
- bears on: Q4; C3 FOR. New input is matched against open questions, not against other findings.
- limit: the list lives in the person's head; neither author describes an external format.

**F6. Connections pay most when they cross fields.**
- who: Carlini and Nielsen
- evidence: "Model stealing existed in the machine learning community since 2016; I found a connection to differential cryptanalysis that resulted in a series of papers" — A/how-to-win…:406-408. Nielsen: "virtually none of the researchers in either field will systematically learn the other field in any sort of depth. The few who do… spectacular results" — A/principles…:120
- bears on: Q4; C3 FOR
- limit: it needs real depth in both fields first.

**F7. Connections come from reviewing a written log.**
- who: John Schulman (OpenAI co-founder; the guide was written for the OpenAI Fellows program) and Nanda
- evidence: "when I revisit my journal entries during the week in review, I'll fill in a missing piece in a puzzle, which didn't occur to me at the time" — A/an-opinionated-guide-to-ml-research.md:102. Nanda: "keep a highlights doc of particularly interesting results, this makes it easier to spot connections" — A/how-i-think-about-my-research-process-explore-understand-dis.md:75. See also the "things I believe to be true" doc and the idle-curiosity doc (A/how-to-become…:396, :587).
- bears on: Q4; C1 FOR, C3 FOR
- limit: every example is a personal, time-ordered log. No one keeps a map or graph.

**F8. Contradicting evidence is written down on purpose, and the unknown hypothesis is assumed to be the likeliest.**
- who: Hamming (reporting Darwin) and Nanda
- evidence: Darwin "found it necessary to write down every piece of evidence which appeared to contradict his beliefs because otherwise they would disappear from his mind" — A/you-and-your-research.md:87. Nanda: "most of your probability mass should normally be on 'something I haven't thought of yet'" — A/research-process-key-mindsets.md:44, and "Excitement is evidence of bullshit" — A/how-to-become…:575
- bears on: Q5; C5 FOR
- limit: Nanda: "It is also an issue if you are too skeptical" (:49).

**F9. The filter after reading: drop papers that never tested the boring explanation.**
- who: Nanda
- evidence: "I see a simple and boring explanation for the author's observations, and they didn't test for it… at least 50% of papers are basically useless" — A/research-process-key-mindsets.md:35-36
- bears on: Q2, Q5
- limit: 50% is his own uncounted estimate.

**F10. Popularity lags and misleads.**
- who: Nanda (who counts his own sparse-autoencoder work as a fad), Patrick Collison (Stripe CEO; the page plugs Pioneer and Emergent Ventures), Gwern (independent writer) and Vivek (MATS/Anthropic researcher on X; follower count not recorded)
- evidence: "very popular for a year or so, make some progress and find many limitations, and then the field moves on" — A/how-to-become…:415. Collison: "Status lags by a generation or more." — A/advice.md:23. Gwern: GPT-3 was released "to remarkably little interest from researchers" — A/the-scaling-hypothesis.md:35. Vivek: "subfields saturate… usually right after they peak on twitter" — X/vivek-how-to-be-good-at-research.md:65
- bears on: Q2; C4 FOR
- limit: Olah warns "beware survivorship bias" about contrarian success stories (A/research-taste-exercises.md:139).

**F11. Counts (citations, paper volume, reach) track promotion and readability, not correctness.**
- who: Carlini, Keller Jordan (OpenAI; creator of the Muon optimizer, promoting his own benchmark) and Jason Wei (OpenAI, speaking as a producer)
- evidence: "cited so frequently… is that we did a far better job writing down what a membership inference attack is… even though our exact method no longer really matters" — A/how-to-win…:755-758. Jordan: "hundreds of optimizer papers… the SOTA has only improved a few times… almost all optimizer papers are fake" — X/keller-jordan-optimizer-benchmark.md:15. Wei: "Advertising work on twitter is probably the highest return per amount of effort" — A/practicing-ai-research.md:37. Robin Sloan, quoted by Andy Matuschak: "you only notice the people who are speaking nonstop" — A/work-with-the-garage-door-up.md:36
- bears on: Q2; C4 FOR

**F12. Rare information sits in appendices, ablations, theses, old work and raw data.**
- who: Achiam, Vivek, Schulman, Andrej Karpathy (independent educator), Carlini and Hamming
- evidence: Achiam: "scour that paper, especially the ablation analyses and supplementary material" — A/spinning-up…:50. Vivek: "the appendix is where the bodies are buried" — X/vivek…:33. Schulman: "older theses also often contain valuable gems of insight" — A/an-opinionated…:126. Karpathy: "One time I discovered that the data contained duplicate examples" — A/a-recipe-for-training-neural-networks.md:51. Carlini found an attack because he "came across the LAION-5b dataset, wanted to study it, and noticed an attack" — A/how-to-win…:469-470. Hamming's Berkeley story: "if we had reduced that data we would have found fission" — A/you-and-your-research.md:103
- bears on: Q3

**F13. Rare information also sits in people's heads and in taboo topics.**
- who: Chris Olah and Shan Carter; Peter Thiel through Blake Masters' class notes (secondary source, and Thiel is an investor talking his book)
- evidence: "some individuals have a much more developed version of an idea than is publicly shared" — A/research-debt.md:75. Thiel: "What is explicitly forbidden? What is implicitly off-limits or taboo?" — A/peter-thiel-s-cs183-class-11-secrets.md:131
- bears on: Q3

**F14. The stop rules people actually write down are novelty saturation or a time box.**
- who: Nanda; Hamel Husain and Shreya Shankar (they sell an evals course); Perplexity's and LangChain's prompts, quoted in the teardowns
- evidence: Nanda: "more than five hours without learning something new… try a different approach" — A/how-to-become…:544. Husain and Shankar: "if ~20 traces don't turn up a new category, you can stop (but review at least 100 to start)" — A/llm-evals-faq.md:222. Perplexity: "Stop if consecutive calls return mostly previously-seen entries." — T/PERPLEXITY_DEEP.md:3852-3853. LangChain's open_deep_research: "Your last 2 searches returned similar information" — T/DEEP_RESEARCH_FAST_MODE_RE.md:238
- bears on: Q6
- limit: no stop rule anywhere reads "I have looked for counter-evidence enough."

**F15. Anthropic's research system avoids duplicate work by dividing tasks up front, not by having workers share findings.**
- who: Anthropic engineering (a vendor describing its own product)
- evidence: "one subagent explored the 2021 automotive chip crisis while 2 others duplicated work investigating current 2025 supply chains" — A/how-we-built-our-multi-agent-research-system.md:51. The lead prompt: "Avoid overlap between subagents — every subagent should have distinct, clearly separate tasks" — T/CLAUDE_RESEARCH.md:1229. The blog says "subagents can't coordinate" (A/…:115). The teardown did find an SDK message bus, but it is "directed point-to-point… not a shared global scratchpad" (T/CLAUDE_RESEARCH.md:942).
- bears on: Q7; C6 partly FOR. Duplication is real; the cure is task boundaries.
- limit: depth-first queries run subagents "in sequence… to fill gaps" (T/CLAUDE_RESEARCH.md:1195-1199).

**F16. Google's AI co-scientist uses shared state that both deduplicates and steers workers.**
- who: Google's co-scientist paper (Gottweis et al.; vendor), read through the teardown; the paper reports wet-lab-validated results
- evidence: the Proximity agent enables "clustering of similar ideas, de-duplication, and efficient exploration of the hypothesis landscape" — T/AI_CO_SCIENTIST.md:148. Meta-review feedback is "simply appended to their prompts in the next iteration" (:171). Generation is pushed into "under-explored regions" (:106), and a persistent "context memory" holds it all (:211).
- bears on: Q4, Q7; C1 FOR, C3 FOR, C6 FOR

**F17. Hyperresearch has a shared vault with check-before-fetch, and lets disagreement decide where to go deep.**
- who: Jordan Gibbs (open-source package; star count not recorded), read through the teardown's file:line citations
- evidence: a PreToolUse hook reminds "the agent to check the research base first" — T/HYPERRESEARCH.md:625. Search planning uses "4-lens search planning (A breadth / B citation-chain depth / C adversarial-contrarian / D period-pinned primary sources)" (:1483). The depth budget comes from "importance + uncertainty + disagreement + decision_impact" (:1487).
- bears on: Q4, Q5, Q7; C2, C3, C5 and C6 all FOR
- limit: no measured benefit is reported.

**F18. Deep-research products go broad, then read deeply, then follow up on what the reading turned up.**
- evidence: OpenAI Deep Research issues "follow-up queries triggered by something noticed in the deep-read phase ('X said it depends on Y, but I haven't researched Y yet')" — T/OPENAI_DEEP_RESEARCH.md:509 (the teardown reconstructs this from screenshots, so INFERRED). Anthropic: "Start wide, then narrow down" — A/how-we-built…:65
- bears on: C1 FOR, C2 FOR

## Against the claims

**X1. Think or build first, read second (against C2).**
- who: Hamming and Carlini
- evidence: Hamming: "refuse to look at any answers until you've thought the problem through" — A/you-and-your-research.md:209. Carlini: "(1) develop my own attack, and then (2) read what everyone else was doing" — A/how-to-win…:277-278, and "Once you've seen ten papers use Approach X, you implicitly assume Approach X is the right way" (:266-267)
- limit: Carlini also says to read "as much of the literature as you possibly can" (:180) and warns against re-inventing (:282).

**X2. The accretion comes from experiments, not reading (against a reading-based C1 and C2).**
- who: Perez and Nanda
- evidence: reading is "Generally not very important — low value of information relative to running your own experiments" — A/tips…:89. Nanda: "Do not just read papers" — A/how-to-become…:90

**X3. Duplication is welcomed as a signal (against C6's premise that it is waste).**
- who: Perez and Olah
- evidence: "It's a win if you are scooped… often the best way to get signal on what you're working on" — A/tips…:106. Olah's Exercise 2: "Pay attention when other people try ideas you've had" — A/research-taste-exercises.md:48

**X4. For verification and diversity, isolation beats sharing (against C6).**
- who: Cognition (vendor), Thariq Shihipar (Anthropic), OpenRouter (vendor), and Husain and Shankar
- evidence: Cognition: "work best when the coding and review agents do not share any context beforehand" — A/multi-agents-what-s-actually-working.md:48. Thariq: "generate hypotheses from disjoint evidence… face a panel of verifiers and refuters" — X/thariq-a-harness-for-every-task.md:155. OpenRouter, whose panel members never exchange findings: "three quarters of the lift… comes from synthesis, and one quarter from diversity" — X/openrouter-fusion-compound-models.md:25. Husain and Shankar: "label a shared set of traces independently to surface differences" — A/llm-evals-faq.md:486

**X5. Some avoid parallel work entirely.**
- evidence: Cognition: "just use a single-threaded linear agent" — A/don-t-build-multi-agents.md:68. OpenAI Deep Research is "single-threaded… no fan-out" — T/OPENAI_DEEP_RESEARCH.md:522. Husain and Shankar prefer "a single domain expert as a 'benevolent dictator'" — A/llm-evals-faq.md:448

**X6. Some use popularity as the quality signal (against C4).**
- who: Will Bryk, Exa CEO (vendor, via the teardown's quote of his podcast appearances); Glean docs (vendor); Schulman
- evidence: Bryk: "trained to predict links that people share, and people often — no one shares SEO blog posts" — T/EXA.md:107. Glean ranks on "recency, authority, popularity, and link structure" — T/GLEAN.md:216. Schulman watches "which ideas become widely used" — A/an-opinionated…:130
- limit: this is sharing and uptake, not search rank. Anthropic's testers found agents picked "SEO-optimized content farms over authoritative but less highly-ranked sources" — A/how-we-built…:93

**X7. One-shot intuition instead of step-by-step accretion (against C1).**
- who: Jason Wei
- evidence: a "yolo run directly implements an ambitious new model without extensively de-risking individual components" — X/jason-wei-yolo-runs.md:17
- limit: this is about experiments, not information-finding.

## Not covered by any claim

- **N1. The goal you bring is what makes your questions rare.** Schulman: "Researchers around the world are reading the same literature, which leads them to similar ideas" — A/an-opinionated…:62. Vivek: "shared reading lists produce shared ideas" — X/vivek…:27
- **N2. Confusion is the signal.** Nielsen, following Steven Weinberg: "a field that is a mess is really an opportunity" — A/principles…:180. Carlini: "areas where, when I read the work, I want to scream" — A/how-to-win…:362-363
- **N3. Trust incentives over claims.** Jordan: "It is hard to trust claims in 2025. What's easier to trust is incentives." — X/keller-jordan…:27
- **N4. Predict before reading.** Nanda: "Predict methods, results, and limitations before revealing them" — A/cultivating-research-taste.md:95
- **N5. Order work by information gained per unit time, neither broad-first nor deep-first.** Jacob Steinhardt — A/research-as-a-stochastic-decision-process.md:45. Carlini: "start with the sub-problem most likely to fail" — A/how-to-win…:585-586
- **N6. Ask for your unknown unknowns before starting.** Thariq's "blindspot pass" — X/thariq-finding-your-unknowns.md:59
- **N7. Writing up exposes the holes.** "people didn't really understand their project until they wrote it up" — A/how-i-think…:107

## Frontier
- Weinberg's "identify the messes" (A/principles…:178), Thurston's account of killing a field with research debt (A/research-debt.md:139), and Gowers' "theory-builders vs problem-solvers" (A/how-to-win…:370-372) — each is an original worth fetching.
- "Theoretical saturation" from qualitative research, the source of the stop rule in F14 (A/llm-evals-faq.md:222).
- Baidu's early scaling paper, Hestness et al. 2017, which Gwern says was overlooked — a candidate for non-English or out-of-lane labs that do not get read (A/the-scaling-hypothesis.md:218).
- Hiring labs' "requests for research" (X/sholto-break-into-frontier.md:13) and recruiters' filters: "insightful questions on the JAX GitHub" (X/noam-brown-land-a-research-job.md:23). These are recruiting posts, so they rank low as testimony.
- The Claude managed-agents thread message bus (T/CLAUDE_RESEARCH.md:935-942).
- Manus's merge rule, "Final length must exceed sum of drafts" (T/MANUS.md:372).
- Keller Jordan's bounty-as-filter (X/keller-jordan…:27).
- ROUTER-ONLY: Carmack asking Sutskever for a reading list. The folklore "30" came from a post with 877K views and matches neither Carmack's figure nor the list. Primary is the Dallas Innovates interview, 2023-02-02, which I did not fetch (/Users/seventyleven/Desktop/guidesfm/GUIDES_30PAPERS.md:15-28).

## Lane state
- articles/ (190 .md, enumerated live): READ-FULL for the research-method essays and the multi-agent pieces. The rest were routed by grepping the manifest and bodies; the business, design and growth essays are EMPTY for this question.
- ahead-of-ai-magazine-sebastianraschka-com.md: EMPTY — it is a homepage stub with no text.
- x-guides/ (67 threads, grepped): READ-FULL on the 11 threads listed in the register. The rest were grepped and are EMPTY on topic (Olah's "Magnifica Humanitas" and Scott Belsky's thread were opened and have nothing).
- GUIDES_*.md (4): used only to route. GUIDES_30PAPERS is a router, not a source.
- BAD_GUIDE.md (both copies) and sections/ai-research-taste.md: grepped. They are routers only and led back to sources already read.
- teardowns (417 files, flat glob): READ-PARTIAL on the relevant sections of 11 files. PARALLEL_CODE, DEEPWIKI and TAVILY_R3 were checked and are EMPTY for Q7.
- Verso: README and research/THESIS_VERIFICATION.md read. Its stance is that spawned sub-agents isolate context ("child's tokens stay in the child", README.md:207) and that verification uses one fact-finder plus one adversarial skeptic per claim (THESIS_VERIFICATION.md:5). Both are the user's own agent-built material, so they are not practitioner testimony.
- Not in the brief and not read: researchfms top-level specs, transcripts.

## Source register (all local, read 2026-09-26)
- A/you-and-your-research.md — READ
- A/an-opinionated-guide-to-ml-research.md — READ
- A/principles-of-effective-research.md — READ
- A/how-i-think-about-my-research-process-explore-understand-dis.md — READ
- A/research-process-key-mindsets.md — READ
- A/cultivating-research-taste.md — READ
- A/how-to-become-a-mechanistic-interpretability-researcher.md — READ-PARTIAL
- A/favourite-mech-interp-papers.md — READ-PARTIAL
- A/how-to-win-a-best-paper-award-doing-research-that-matters.md — READ-PARTIAL (lines 1–590, 736–770, 1100–1251)
- A/practicing-ai-research.md — READ
- A/spinning-up-as-a-deep-rl-researcher.md — READ-PARTIAL
- A/research-taste-exercises.md — READ
- A/research-debt.md — READ-PARTIAL
- A/research-as-a-stochastic-decision-process.md — READ-PARTIAL
- A/tips-for-empirical-alignment-research.md — READ-PARTIAL
- A/tips-and-code-for-empirical-research-workflows.md — READ-PARTIAL
- A/how-to-do-great-work.md — READ-PARTIAL
- A/how-to-think-for-yourself.md — READ-PARTIAL
- A/peter-thiel-s-cs183-class-11-secrets.md — READ-PARTIAL
- A/advice.md — READ
- A/how-we-built-our-multi-agent-research-system.md — READ
- A/don-t-build-multi-agents.md — READ
- A/multi-agents-what-s-actually-working.md — READ
- A/goodbye-rag-how-hebbia-solved-information-retrieval-for-llms.md — READ (vendor, EMPTY for the claims apart from its document-by-question "Matrix" as shared answer space, :122)
- A/work-with-the-garage-door-up.md — READ
- A/things-i-learned-at-openai.md — READ (EMPTY)
- A/the-scaling-hypothesis.md — READ-PARTIAL
- A/2025-the-year-in-llms.md — READ-PARTIAL (EMPTY)
- A/ahead-of-ai-magazine-sebastianraschka-com.md — EMPTY
- A/llm-evals-faq.md — READ-PARTIAL
- A/a-recipe-for-training-neural-networks.md — READ-PARTIAL
- A/write-five-then-synthesize-good-engineering-strategy-is-bori.md — READ-PARTIAL
- X/vivek-how-to-be-good-at-research.md — READ
- X/vivek-getting-into-frontier-ai-labs.md — READ-PARTIAL
- X/noam-brown-land-a-research-job.md — READ
- X/sholto-break-into-frontier.md — READ
- X/thariq-finding-your-unknowns.md — READ
- X/thariq-a-harness-for-every-task.md — READ-PARTIAL
- X/openrouter-fusion-compound-models.md — READ
- X/keller-jordan-optimizer-benchmark.md — READ
- X/jason-wei-yolo-runs.md — READ
- X/mlpowered-debug-models-by-reading-the-highest-lo.md — READ
- X/scott-belsky-seeing-the-matrix.md — READ (EMPTY)
- X/ch402-chris-olah-x-long-form-article-may-2026-ti.md — READ-PARTIAL (EMPTY)
- /Users/seventyleven/Desktop/guidesfm/GUIDES_30PAPERS.md — READ-PARTIAL (router)
- /Users/seventyleven/Desktop/guidesfm/BAD_GUIDE.md — grepped (router)
- /Users/seventyleven/Desktop/BAD_GUIDE.md — grepped (router)
- /Users/seventyleven/Desktop/guidesfm/research/sections/ai-research-taste.md — READ-PARTIAL (router)
- T/CLAUDE_RESEARCH.md — READ-PARTIAL
- T/OPENAI_DEEP_RESEARCH.md — READ-PARTIAL
- T/GEMINI_DEEP_RESEARCH.md — READ-PARTIAL (single 1M-token context holds every step's findings, :500-531)
- T/AI_CO_SCIENTIST.md — READ-PARTIAL
- T/HYPERRESEARCH.md — READ-PARTIAL
- T/PERPLEXITY_DEEP.md — READ-PARTIAL
- T/DEEP_RESEARCH_FAST_MODE_RE.md — READ-PARTIAL
- T/EXA.md — READ-PARTIAL
- T/GLEAN.md — READ-PARTIAL
- T/NOTEBOOKLM.md — grepped (EMPTY)
- T/MANUS.md — grepped
- /Users/seventyleven/Desktop/Verso/README.md — READ-PARTIAL
- /Users/seventyleven/Desktop/Verso/research/THESIS_VERIFICATION.md — READ-PARTIAL