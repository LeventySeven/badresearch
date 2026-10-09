<!-- G5 how researchers use AI in research (agent output, 2026-10-10) -->

## Findings

F1. **Tao hands literature search to AI only in a narrow niche: a field that is hard to search but where checking an answer is easy.** When the problem has a standard name and a dense citation graph, he says ordinary forward and backward citation searches are enough. AI pays when the literature is scattered, has no shared name, or sits in obscure journals. It pays because an expert can quickly confirm a paper the tool surfaces. The tool's output is used only to find human-written sources. It never goes into the work itself.
- who: Terence Tao (UCLA, Fields Medal; 27.1k Mastodon followers). His own team builds an AI harness, and he has co-authored with DeepMind.
- evidence:
  - "This ability to independently verify the output of a literature search tool makes it a suitable use case for AI (assuming that the user has enough expertise to perform such a verification)" — https://mathstodon.xyz/@tao/115385025625117726
  - "the (potentially unreliable) output of such AI tools is only used to locate more reliable human-generated resources, rather than being directly incorporated into the final product" — https://mathstodon.xyz/@tao/115135610687969581
  - (2026-10-10; READ-FULL via the Mastodon API)
- bears on: E1, E3, Q1, C1; K2 (it adds the condition "how dense is the citation graph"), K5
- limit: assumes expert verifiers. He also says "the success rate of the AI output does not need to be 100%".

F2. **The Erdős AI ledger: AI literature search mostly finds that "open" problems were already solved. AI "solutions" to open problems often turn out to be in the literature already.** The 2(a) table has 84 literature-search entries:
- 40 found a full solution already in print;
- 42 found partial results;
- 4 are flagged red (wrong claims, a confused problem, "literature proof not found").

Of the 86 entries where AI worked with no significant human input (sections 1(a) and 1(b)), 25 had comparable literature turn up after the AI "solved" the problem. My counts from the wiki's raw markdown (commit c8ad430, data frozen 2026-06-30). Tao's explanation is that the problems easiest for AI are also the ones most likely to have been quietly solved already.
- who: the community wiki linked from erdosproblems.com. It is "decidedly unaffiliated with any AI company". The counts are mine.
- evidence:
  - "Absence of past progress may reflect obscurity rather than difficulty" — github.com/teorth/erdosproblems/wiki/Disclaimers-and-caveats
  - "that category is also precisely the category of nominally open problems that are most likely to have been solved in the literature" — https://mathstodon.xyz/@tao/115788262274999408
  - (2026-10-10; READ-FULL)
- bears on: Q3, C4; K6 (sleeping beauties), K10, K15 (fail-open novelty checks)
- limit: the wiki's own disclaimer 3 says negative results are under-reported.

F3. **What the searcher has learned changes which AI search succeeds. A second search, run after the answer's form was known, found what the first missed.** On Erdős #1026:
- The first deep-research pass failed. An "old-fashioned" Google Scholar search found Tidor–Wang–Yang 2016.
- After AlphaEvolve's numbers suggested a precise conjecture, a collaborator's second deep-research search found Baek–Koizumi–Ueoro, which proved it.
- A 1980 conjecture by Steele was located later the same way.
- who: Tao's blog.
- evidence: "AI deep research tools have successfully located such prior literature in the past, but in this case they did not succeed, and a more 'old-fashioned' Google Scholar job turned up some relevant references" — https://terrytao.wordpress.com/2025/12/08/the-story-of-erdos-problem-126/ (2026-10-10; READ-PARTIAL)
- bears on: **E1 (for: more knowledge, sharper query)**, C1; K1, K12
- limit: a single case.

F4. **One hallucination made an expert discount a correct pointer in the same answer. The fix was to read the primary source himself.** Gemini Deep Research correctly found Alaoglu–Erdős 1944, but also claimed n=17 was a counterexample, which was false. Tao therefore at first gave the true part little weight. Reading pages 466–467 himself confirmed it.
- evidence: "Based on this latter failure, I did not initially give much credence to the initial statement; but later, after reading the Alaoglu-Erdos paper carefully, I did find…" — https://mathstodon.xyz/@tao/115329949423342204 (READ-FULL)
- He also notes that a fast, accurate search can hurt: "research is sometimes 'non-monotone'… getting accurate answers quickly can, paradoxically, lead to *less* understanding" (/115329950370116948).
- bears on: E1 (early judgments are contaminated by one error), K7, K14
- limit: anecdote.

F5. **Recall against an expert gold standard depends on who measured it and how deep they looked.**

| Study (seller?) | Gold standard, n | Result |
|---|---|---|
| Arthroplasty Today 2026, orthopaedic surgeons (some consult for device makers; no AI vendor) | 5 published systematic reviews; AI searches run 3× | Fellows 85.2% recall (268 h screening 9,101 articles). ChatGPT-5 Deep Research 47.5%; Agent Mode 40.9% (12–14 min per search). The AI also found eligible studies the humans missed. |
| SMU Libraries, Aaron Tay (librarian; subscriber, not seller) | Included-study lists of published systematic reviews | Undermind found "~30–80%" of target papers after ~8 minutes. |
| ReportBench, ByteDance (does not sell these products) | 100 arXiv survey papers, ~153 references each | Recall: OpenAI Deep Research 0.033, Gemini Deep Research 0.036. ~10 vs 32 references per report. |
| Elicit, vendor | 994 Cochrane reviews; review title as the only query | 95.0% recall. In its own robustness check, recall rose with depth: 79.06% at top-500, 89.77% at top-10,000. |

- evidence:
  - "identifying 47.5% and 40.9% of gold standard articles" — https://pmc.ncbi.nlm.nih.gov/articles/PMC13194160/
  - "Undermind retrieves only ~30–80% of those target papers" — https://aarontay.substack.com/p/are-ai-tools-killing-review-articles (2026-02-12)
  - "Using only the review title as the query, Elicit finds 95.0% of included studies" — https://elicit.com/blog/evaluating-elicit-slr (2026-05-06)
  - ReportBench Table 1 — https://arxiv.org/pdf/2508.15804
  - (all 2026-10-10; READ-PARTIAL)
- bears on: Q6, C2; extends K14 row O (an independent study put Elicit at 37.9%)
- limit: Elicit's number counts excluded-studies tables as relevant and depends on retrieval depth. Arthroplasty n=5. ReportBench measures references, not included studies.

F6. **Judging a candidate set is a different job from finding it. On judging, an LLM pipeline beat graduate reviewers.** otto-SR, results:
- screening sensitivity 96.7% vs 81.7% for human reviewers;
- extraction accuracy 93.1% vs 79.7%;
- on 12 Cochrane reviews (146,276 citations), it found 114 eligible studies vs 64 for the original authors;
- it changed statistical significance in 3 meta-analyses.

Counterpoint on screening: Tay found Undermind "drops too many papers because title/abstract is lacking a concept", where a human would answer "maybe" (x.com/aarontay/status/1803021853335970262).
- who: Cao et al., University of Toronto (medRxiv v4, 2026-05-04); the tool is not public. Tay: 7.4k followers.
- evidence: "otto-SR: 96.7% sensitivity, 97.9% specificity; human: 81.7% sensitivity, 98.1% specificity" — https://api.medrxiv.org/details/medrxiv/10.1101/2025.06.13.25329541 (READ-PARTIAL, abstract)
- bears on: K14 ("humans complete but careless" holds for screening), K11 (independent screeners)
- limit: a preprint. The reference standard is the original reviews' decisions.

F7. **Fabricated references persist and get past peer review. A mechanical check is cheap.**
- **Rao, Wong & Callison-Burch** (no vendor): 3–13% of citation URLs from 10 models and agents were hallucinated (53,090 DRBench URLs; 168,021 ExpertQA URLs). Deep-research agents hallucinate at higher rates. A liveness tool brought non-resolving URLs below 1%.
- **Russinovich et al.** (RefChecker, open source): "roughly one in twenty NeurIPS and USENIX Security papers" in 2025 contains at least two likely hallucinated references, at about $0.04 per paper to audit.
- **Ansari**: 100 fabricated citations in 53 accepted NeurIPS 2025 papers. "every hallucination (100%) exhibited compound failure modes".
- evidence: "3--13\% of citation URLs are hallucinated -- they have no record in the Wayback Machine" — arxiv.org/abs/2604.03173; arxiv.org/abs/2607.00738; arxiv.org/abs/2602.05930 (2026-10-10; abstracts)
- Practitioner case: John Lam (5.4k): his PhD advisor and faculty, shown a Deep Research report on his thesis area, "were (rightfully) disappointed… after seeing some hallucinated references" — x.com/john_lam/status/1886827830945923359. Karpathy: "A few times I caught it hallucinating URLs that don't exist" — x.com/karpathy/status/1891720635363254772.
- bears on: K14, K16
- limit: this contradicts Mollick's claim (401k followers, unmeasured) that the Deep Research button ended fake citations (x.com/emollick/status/1928271628447662367).

F8. **Practitioners see source selection and popularity bias as the bigger failure, more than fabrication.**
- **Narayanan** (Princeton; 132k): "the main factuality problem is not hallucination, but source selection — the sources it relies on might sometimes be outdated, incomplete*, or not the highest quality" — x.com/random_walker/status/1890063232762867847.
- **Algaba et al.**: across 274,951 references GPT-4o generated for 10,000 papers, "LLMs systematically reinforce the Matthew effect in citations by consistently favoring highly cited papers" (arxiv.org/abs/2504.02767). This is parametric recall, not live search.
- **Haddaway**, quoted by Tay: AI "tends towards aggregation, missing important minority subdomains".
- **Minseok Choi** (KAIST postdoc, **72 followers**) did the opposite on purpose. He built a corpus of only accepted papers, with citation counts attached. His reason: "when you're just getting into a new area, you don't even know which papers are seminal. you need citation counts to tell signal from noise" (x.com/minseok__choi/status/2041811252658532572).
- bears on: C4, E1; K6 (newcomers use popularity as a filter, experts route by it), K13, K14 row M

F9. **Queries that require a leap across vocabularies are where these tools fail most. A librarian reverses the tool's role to find the words.** Tay collected failed Undermind queries from disappointed users over 1.5 years. They were broad, cross-disciplinary, and "connecting subdomains that don't share vocabulary". The tools stay "close to established terminology". His workaround is to run a semantic search, read the top 50 hits, and harvest the keywords his Boolean search missed.
- evidence: "They're designed to reproduce consensus" — aarontay.substack.com (as F5); "semantic search results provides a idea of what keywords are used" — x.com/aarontay/status/1753059234458018132 (READ-FULL)
- bears on: K5 (the vocabulary wall), C3, Q1

F10. **What practitioners delegate and what they keep.**
- **Litt** (Toronto mathematician, 64k):
  - "it's primary use for me so far is still literature search, not, like, one-shotting results" (x.com/littmath/status/2090110750383566851).
  - Proving lemmas in algebraic geometry is "basically useless": hours for "a lemma that takes me ~5 minutes".
  - Even on lit review, "strong incoming graduate students are arguably better" (/2084426043788784033).
  - He did hand a model the job of scanning his own published papers for errors. Of about 400 comments, "Only about 2-3% were wrong", 5 were serious, and it missed one error he already knew about (/2092644620177940934, /2092644634648256921).
- **Karpathy**: "Usually pass 1 is manual, then pass 2 'explain/summarize', pass 3 Q&A" (x.com/karpathy/status/1990577951671509438; 13k likes).
- **Andreas Karch** (UT Austin physicist, **2.6k**): "I tell students to do literature search with AI, but make sure to read the actual papers" (x.com/karch_andreas/status/2087186148154089642).
- **John Wu** (astrophysics, **1.9k**): "90% of the work is simply 'specifying the question'… 9% … 'contextualizing to literature'" (x.com/jwuphysics/status/2013082686252851376).
- **The erdosproblems policy**: the existence of relevant sources must be "carefully checked and verified by the user themselves without the assistance of AI" (Tao #1026 post).
- bears on: E1, E3, Q2

F11. **Handing over the learning itself measurably weakens the expertise that does the filtering.** In a randomized trial of developers learning a new library, AI assistance cut quiz scores by 17% (d = 0.738, p = 0.010, n = 52) with no significant speed gain. Three of the six interaction patterns preserved learning.
- Tay's practitioner version: "If we offload that struggle too early, we may get more polished text and fewer well-formed thinkers."
- Tao (2026-09): answers and insight "have become _negatively correlated_" when AI runs "unguided by any human expert" — https://mathstodon.xyz/@tao/117208618508728654
- who: Shen & Tamkin, Anthropic (the vendor, publishing against its own interest); arxiv.org/abs/2601.20245 (READ-PARTIAL)
- bears on: **E1 (the filter grows only if you do the work)**, C1
- limit: coding, not literature.

F12. **Agents doing open-ended research prune too early and rate their own work too kindly.** In "shadow evaluations" (Kapoor, Narayanan et al.; n = 2 unpublished papers, six days each), the original authors rejected both AI papers. The agents also:
- dropped their most ambitious hypotheses within the first 15 hours, never to return;
- graded their own poor papers only "weak rejects";
- ended with more than half the budget unspent.

Related vendor number: Kosmos (Edison, sells it) was 82.1% accurate on literature-review statements but 57.9% on synthesis statements (102 statements, 3 reports). Its authors attribute the synthesis errors to conflating "statistically significant results with scientifically valuable ones" (arxiv.org/pdf/2511.02824).
- evidence: "The agents dropped their most ambitious hypotheses within the first fifteen hours of carrying out the experiment and never changed course afterwards." — x.com/sayashk/status/2082877458924065269 (READ-FULL)
- bears on: **E2 (pruning too early, measured in agents)**; matches A1 in the g1 lane (Schulman)
- limit: the reviews were non-blind.

## Against the claims

- **Against C1/E1 as "more is better", from Tao on #367 and his MathOverflow problem.** A reliable early literature hit would have marked the problem "solved" and stopped deeper work: "I would not have tried the more technically challenging initial approach" (/115329950370116948). Accretion can end inquiry too soon.
- **Against heavy AI use where people already exchange findings (K11/K3).** "a well-run crowdsourced project has less need of AI assistance than an individual, because it is already 'superintelligent' through the human network interactions" (/115325229364313459).
- **Against "deep-research harness beats simple."** In the First Proof refereeing, Tao's UCLA harness was only "slightly better than the out-of-the-box frontier model, but at much higher compute costs" and showed "general failure to cite appropriate relevant literature" (/116727977488589991). Narayanan: general agents "swallowed" Deep Research tools (as in the g3 lane). The report format itself works against thinking: "The text it insists on producing… creates negative value for me by biasing my thinking" (x.com/random_walker/status/1947701358074679481).

## Not covered by any claim

- **Report searches that found nothing.** Tao proposes logging failed literature searches so others stop repeating them; the wiki records misses such as "literature proof not found" (/115385029462648630). His "Of the 36 problems… 24 (66%)" is a hypothetical template, not data.
- **Have a third party formalize the statement.** "it is best if the *statement* of the result is formalized by a human or a third party rather than by the AI doing the proof" (wiki, What-to-do page). This is the claim-level form of keeping judgment independent (K11).
- **Delegate only where errors are cheap and visible.** Narayanan: "(1) the user is in the loop, (2) errors are relatively easy to spot and (3) aren't a deal-breaker if not spotted" (x.com/random_walker/status/1870218641448546470).
- **Red flags for the AI's own output.** A proof that is "suspiciously short, is suspiciously elementary, proves significantly more than the problem asks" may be solving a misstated problem (wiki).

## Frontier
- First Proof report (1stproof.org/assets/docs/report.pdf): expert-refereed benchmark of four harnesses. Not read.
- Leiden Declaration (leidendeclaration.ai), cited by the wiki.
- urlhealth (Rao) and RefChecker (github.com/markrussinovich/refchecker): mechanical citation gates.
- "Refine", the commercial error-finder Litt used; Litt's problem-list site.
- Galli et al. 2024: descriptive vs reflexive reviews.
- Neal Haddaway on evidence maps.
- Dean Giustini 2025, independent review of Undermind (JCHLA). Not read.
- Undermind's vendor benchmark (23 queries) and the JMIR 2026 review (Gemini/Perplexity Deep Research ~47–50% fabricated references): DIGEST-ONLY.
- "Zhao et al.: 146,932 hallucinated citations in 2025 preprints": seen only through a promotional tweet, unverified.
- DeepMind's AI Co-Mathematician: literature search counted as one component; 19% → 48% on FrontierMath T4, per a digest.

## Lane state
- Mathstodon API, @tao: READ (1,074 posts, 2025-05 to 2026-10, grepped).
- Erdős AI wiki: READ-FULL (git clone of the wiki repo).
- Tao #1026 blog post: READ-PARTIAL.
- X searches: 17 queries, Latest and Top. Mostly influencer and tool-promotion noise. Kept: Litt, Narayanan, Kapoor, Karpathy, Tay, Karch, Choi, Wu, Lam. Thread and conversation reads for Litt (×5), Tay, Choi, Kapoor: READ.
- Aaron Tay Substack: READ-FULL. Elicit evaluation blog: READ-PARTIAL.
- PMC13194160 via efetch, ReportBench PDF, Kosmos PDF, Shen & Tamkin PDF: READ-PARTIAL.
- arXiv abstracts (2604.03173, 2607.00738, 2602.05930, 2504.02767, 2411.14199, 2409.13740): abstract only. OpenScholar and PaperQA2 were not used as findings; they are 2024 and the authors' own systems.
- otto-SR: medRxiv API abstract.
- Scott Aaronson "QMA Singularity": READ-PARTIAL, EMPTY for literature search.
- Gowers on X: EMPTY on this topic.
- Silver was not needed; no pages were blocked.

## Source register
- https://mathstodon.xyz/@tao/{115385022005130505, 115385025625117726, 115385028019354838, 115385029462648630, 115788262274999408, 115329949423342204, 115329950370116948, 115325229364313459, 115135610687969581, 115416211466664814, 116727977488589991, 117208618508728654} — READ-FULL
- github.com/teorth/erdosproblems/wiki (all 8 pages, commit c8ad430) — READ-FULL
- https://terrytao.wordpress.com/2025/12/08/the-story-of-erdos-problem-126/ — READ-PARTIAL
- https://pmc.ncbi.nlm.nih.gov/articles/PMC13194160/ — READ-PARTIAL
- https://elicit.com/blog/evaluating-elicit-slr — READ-PARTIAL
- https://aarontay.substack.com/p/are-ai-tools-killing-review-articles — READ-FULL
- https://arxiv.org/pdf/2508.15804 ; /2511.02824 ; /2601.20245 — READ-PARTIAL
- arxiv.org/abs/{2604.03173, 2607.00738, 2602.05930, 2504.02767, 2405.15739, 2411.14199, 2409.13740} — abstract only
- https://api.medrxiv.org/details/medrxiv/10.1101/2025.06.13.25329541 — abstract only
- x.com/littmath/status/{2090110750383566851, 2084426043788784033, 1980985527466946762…1980985538296582594, 2054352925212684512, 2092644610833006825…2092644636263059840} — READ-FULL
- x.com/random_walker/status/{1890063232762867847, 1947701358074679481, 1870218641448546470, 1890025279495503876} — READ-FULL
- x.com/sayashk/status/2082877458924065269 — READ-FULL
- x.com/karpathy/status/{1990577951671509438, 1891720635363254772} — READ-FULL
- x.com/aarontay/status/{1908372855718633601, 1908376442041442462, 1803021853335970262, 1753059234458018132} — READ-FULL
- x.com/karch_andreas/status/2087186148154089642 ; x.com/minseok__choi/status/2041811250989117901 (thread) ; x.com/jwuphysics/status/2013082686252851376 ; x.com/john_lam/status/1886827830945923359 ; x.com/emollick/status/1928271628447662367 — READ-FULL
- https://scottaaronson.blog/?p=9183 — READ-PARTIAL (EMPTY)
- WebSearch digests (Undermind benchmark, JMIR 2026, Consensus consistency, GPTZero) — DIGEST-ONLY, routers only

All fetched 2026-10-10.
