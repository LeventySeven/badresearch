<!-- AGENT OUTPUT — R2-2 connecting (LBD, analogy). Returned by a subagent, not read by the chair unless a row says so. -->

I read all of the lane's primary sources I could reach. Swanson's own 2011 paper, the Arrowsmith field study and Moreau's 2023 critique change how K5 and K6 should be read.

## Findings

**F1.** Swanson's "one-node" search, which starts from one literature and hunts for an unknown second one, turned into a "two-node" search. In the two-node search the researcher supplies both A and C, and the system ranks the B-terms (title words the two literatures share). The original one-node steps: start from problem literature C; take its title B-terms; run searches that build B-literatures; rank candidate A-terms by how many B-literatures contain them. The switch happened because researchers already had more hypotheses than they could use.
- **who:** Neil Smalheiser, UIC psychiatry. He worked with Swanson and maintains Arrowsmith. It is his own free tool; no commercial interest.
- **evidence:** "most investigators are already drowning in a sea of existing potential hypotheses and findings, and their goal is not to find still more hypotheses, but rather to decide which of the existing ones is most promising to pursue" — https://pmc.ncbi.nlm.nih.gov/articles/PMC5771422/ (2026-09-26; READ-FULL)
- **bears on:** Q4, C3. Extends K5. Connects K5 to K4: the connecting query gets its A and C from the researcher's own list of open questions.
- **limit:** He calls ranking by B-term count "relatively crude and nonrobust". The shared-term relevance score (pR) is ~0.07 for random pairs of literatures and 0.4–0.5 for closely related ones.

**F2.** The combinatorial explosion was real, and it was tamed with blunt filters. Field testers (2001–06) got "hundreds to a few thousand B-terms displayed in alphabetical order", which was "excessively long for most field testers to scan". Two filters fixed it:
- A filter keeping only terms that appear in more than one paper "removed about ¾ of B-terms, yet users judged informally that very few 'interesting' terms were lost".
- A semantic-category filter was popular because "users knew what type of terms they were looking for ahead of time".
- **who:** Smalheiser, Torvik et al., UIC. Neuroscientist field testers used the tool in their own lab work.
- **evidence:** https://pmc.ncbi.nlm.nih.gov/articles/PMC1559644/ (via Europe PMC XML; READ-FULL)
- **bears on:** Q2, Q4. Extends K5 and K9.
- **limit:** "Informally". The filter throws away exactly the rare, low-frequency terms that F4 argues for.

**F3.** Swanson searched for **unpopular work on purpose**, using low citation counts as the selection criterion. His "resurrection" procedure: take disease × substance pairs whose shared literature is ≤5 articles, and keep only articles cited ≤5 times before a cutoff date. In a pilot of 846 random pairs, 789 had no shared articles, 57 had some, 36 were small enough, and 14 articles (9 pairs) qualified as neglected. Vosgerau's 1973 German paper was cited twice in 15 years, then 14 times in 1988–98. Of the 57 articles that cited the neglected papers, 55 also cited Swanson 1988.
- **who:** Don Swanson. This was his last paper, published unfinished.
- **evidence:** "The absence of citations to an article over an extended period immediately following its publication, together with the scarcity of other works that investigate the same problem, are plausible markers for neglect." — https://pmc.ncbi.nlm.nih.gov/articles/PMC3097086/ (READ-FULL)
- **bears on:** Q3, C4. **Contradicts K6's line "Nobody in round 1 describes sampling unpopular sources on purpose"**. Connects K6 with K10 (non-English).
- **limit:** A pilot, "incomplete". The follow-up after 1988 was never run.

**F4.** Core versus periphery ("penumbra") is a live disagreement about the connecting query. Swanson filtered B-terms down to the frequent ones (the cores of each field). Kostoff, Petrič and Workman argue that "low-frequency terms which reside in the penumbra of one or both fields may sometimes be more promising". Other moves Smalheiser names:
- **Gaps:** two topics expected to co-occur in ≥10 articles that co-occur in none.
- **"Negative consensus":** claims that something does not occur, stated without citing any evidence. He treats these as research targets.
- **who / evidence:** Smalheiser 2017, PMC5771422 (READ-FULL)
- **bears on:** Q3, C4. Makes K6 CONDITIONAL on this axis; connects to F2.

**F5.** The analogy query that works holds one facet near and pushes another facet far. Hope et al. retrieved products with a near purpose and a far mechanism. Share of ideas judged good:

| Inspirations shown | Good at ≥2 of 5 judges | Good at ≥3 of 5 judges |
|---|---|---|
| Near purpose, far mechanism | 46% | 38% |
| Random products | 37% | 22% |
| Text similarity (TF-IDF) | 30% | 21% |

Precision on the top 1% of retrieved pairs: 0.739 with mechanism vectors vs 0.63 with TF-IDF.
- **who:** Hope, Chan, Kittur, Shahaf (Hebrew U/CMU). Academic, KDD 2017.
- **evidence:** "a non-negligible portion of the pairs labeled as positive were either superficial matches or near analogies" — https://arxiv.org/pdf/1706.05585 (READ-PARTIAL)
- **bears on:** Q4, C3. Extends K5 and the "deliberate randomness" mechanism: random inspirations did as well as or better than similarity-ranked ones.
- **limit:** Only 9 seeds appeared in all three conditions. Product redesign, not science. Judges agreed only moderately (κ=0.51).

**F6.** Kittur et al. split the work of analogy across people:
- Build the abstract schema by comparing several examples. Crowds "generated high-quality schemas when they were asked to identify the common principles behind multiple related products but could not do as well when trying to generate a schema for a single product."
- Keep the people who write the schema apart from the people who search, to avoid fixation.
- Concrete constraints searched in abstract domains worked best.
- Results: about twice as many ideas rated good; a mechanical-engineering expert got twice as many valuable papers as from a machine-learning baseline.
- **evidence:** https://pmc.ncbi.nlm.nih.gov/articles/PMC6369801/ (READ-FULL)
- **bears on:** Q4, Q7, C3, C6. Extends K11's "isolate judgment" row: here what is isolated is the searcher from the original problem. Connects K12.
- **limit:** A perspective paper that summarises its own studies. The authors also ran "several unsuccessful" configurations that are not reported.

**F7.** People retrieve by surface similarity and judge soundness by relational structure. That is why connections across fields are missed even when the relevant material is on hand.
- **who:** Gentner, Rattermann & Forbus, Northwestern, 1993. 692 citations on Semantic Scholar.
- **evidence:** "subjective soundness was highly related to the degree of common relational structure, while retrievability was chiefly related to the degree of surface similarity" — https://pubmed.ncbi.nlm.nih.gov/8243045/ (abstract only; full text closed).
- Bridger participant P18 describes the same failure at the recognition step: "I wouldn't know enough to recognize it as interesting." — https://arxiv.org/pdf/2108.05669 (READ-PARTIAL; 20 CS researchers)
- **bears on:** C3. This is the mechanism under K5's vocabulary wall. It adds a second barrier: recognising a link, not only retrieving it.

**F8.** LLM idea generation runs out of new ideas. Si et al. generated 4,000 seed ideas per topic; only 200 were non-duplicates. This happened even though they "append the titles of all previously generated ideas to the prompt to explicitly ask the LLM to avoid repetitions". Other results:
- Novelty: AI ideas 5.64 vs human ideas 4.84.
- The best LLM judge agreed with human reviewers 53.3% of the time; human reviewers agreed with each other 56.1% (chance is 50%).
- Only 17 of the 49 ideas a human expert picked overlapped with the agent's own top picks.
- **who:** Si, Yang, Hashimoto (Stanford); 79 blind reviewers.
- **evidence:** https://arxiv.org/pdf/2409.04109 (READ-PARTIAL)
- **bears on:** Q6, Q7, C6. Extends K8: generation saturation can be measured. Qualifies K11: putting a "seen" list in the prompt did not prevent duplicates.

**F9.** Automated novelty checks fail open. The AI Scientist queries Semantic Scholar; "If no clear matches are found, it assigns novel=True". It "classified all 10 generated ideas and both seed ideas as novel", including micro-batching for SGD (Beel, Kan & Baumgart, https://arxiv.org/pdf/2502.14297; READ-PARTIAL).

Gupta & Pruthi gave 13 experts a different instruction: presume the idea is plagiarised and find the source ("Let me find the original paper to prove this point"). The experts flagged 24% of 50 documents, and the source papers' authors confirmed the matches. Automated detectors scored:

| Detector | Accuracy |
|---|---|
| Claude, given the true source paper | 88.8% |
| Claude with Semantic Scholar search | 51.3% |
| Turnitin, OpenScholar | 0% |

- **evidence:** "retrieving relevant papers, not determining similarity, is the bottleneck." — https://arxiv.org/pdf/2502.16487 (READ-PARTIAL)
- **bears on:** Q5, C5. Extends K7: a novelty check is a hunt for the counterpart. Connects K7 with K5, since the vocabulary wall is what defeats it.
- **limit:** The authors note that presuming plagiarism can introduce confirmation bias; author verification is their control.

**F10.** Co-STORM's moderator asks new questions using material that was retrieved but never used. It ranks those passages by closeness to the topic times distance from the query that fetched them.
- With every simulated participant an expert, the discussion "tends to consist mostly of utterances with intent FURTHER DETAILS, leading to repetition and niche discussions."
- Removing the moderator cut novelty from 3.05 to 2.89 and unique URLs from 6.04 to 5.67. It hurt more than cutting the number of experts.
- **Appendix B is not an ablation of the mind map.** It measures where new information gets placed in the map: top-level placement accuracy is 39.39% for Co-STORM's method, 24.24% for embeddings alone, and 3.03% for the LLM alone.
- The automatic Novelty score correlates with human ratings at only r=0.32, not significant.
- **evidence:** https://arxiv.org/pdf/2408.15232 (READ-PARTIAL)
- **bears on:** C1, C6. Extends K11. The mind-map row in round 1's notes can be closed as "no discovery ablation exists".

## Against the claims

**A1 (C3, K5).** The LBD evidence base is small and self-referential. Moreau: "the field is built on sand due to a lack of appropriate evaluation method". Evaluation has relied on "the same small set of discoveries as benchmark for the past three decades". Time-sliced evaluation (checking later papers for predicted links) counts co-occurrences, and "very few co-occurences represent a true discovery". Kostoff (2007) showed three published LBD "discoveries" were not discoveries. Moreau also questions whether Swanson's personal motivation drove his picks (he had both conditions).
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9945845/ (READ-FULL)
- Router only: Thilakaratne 2019 reports Arrowsmith failing to recover Swanson's own Somatomedin-C–arginine link (https://pmc.ncbi.nlm.nih.gov/articles/PMC7924697/).
- Smalheiser adds that his own verified discoveries used no algorithm (PMC5771422).

**A2 (C3, C5).** Combinations that look novel lose value once someone executes them. Si, Hashimoto & Yang ran an execution study: 43 experts each spent 100+ hours executing an idea. AI ideas lost 1.049, 1.760 and 1.879 points (1–10 scale) on novelty, excitement and effectiveness. Human ideas moved −0.010, +0.078 and −0.052. After execution the ranking flipped, e.g. excitement 3.90 (AI) vs 4.48 (human), though this is not significant at N=43.
- https://arxiv.org/pdf/2506.20803 (READ-PARTIAL)
- SciMON: the ground-truth idea from the real paper beat the generated one in 85% of comparisons. Its novelty-boosting produced "superficial recombinations of common concepts" (https://arxiv.org/pdf/2305.14259; READ-PARTIAL).

**A3 (C1, K1).** Arrowsmith field testers rejected iterative querying. "none of the field testers ever followed the recommended scenario"; "nor did they tend to modify and re-enter queries". They also wanted links "even if they were well known in the literature already" (PMC1559644).

## Not covered by any claim

**N1. One named query shape recurs in four systems:** keep one facet near and push another far.
- Near purpose, far mechanism (F5).
- Similar task, dissimilar method (Bridger). Caveat: when rating papers alone, the similarity baseline (SPECTER) was marginally preferred.
- On-topic but far from the query that fetched it (F10).
- The RATIO benchmark types these moves as ADDRESS, BROADEN and SPECIFY. Off-the-shelf retrievers find the right ADDRESS passage in the top 10 only 15–20% of the time, "limited gains over BM25"; tuned retrievers reach 40%. https://arxiv.org/pdf/2608.27394 (READ-PARTIAL)

**N2. Grounding in the literature lowers duplication and raises hit rate.** Theorizer (AI2, 2026), under a novelty-focused prompt: 61% of predictions from literature-grounded theories were supported by later papers vs 34% from the model's memory alone; recall was 16% vs 4%. Memory-only theories "quickly saturate to generating only duplicates". Cost: about 7× more. https://arxiv.org/pdf/2601.16282 (READ-PARTIAL)

**N3. Screening in small batches beats large ones.** MOOSE-Chem found 86.9% of the ground-truth inspirations inside the top 4% of a 3,000-paper pool. Windows of 15 beat windows of 60 (83.7% at 4% selected vs 71.6% at 5%). But:
- LLM ranking of the resulting hypotheses was nearly flat (average rank ratio 0.489 for perfect matches vs 0.503 for non-matches).
- Experts gave a full match to 0 of 51 top hypotheses.
- The pool was "3000 most cited chemistry papers published in Nature", which bears on K6, and the ground-truth inspirations are papers the authors cited, so there is a hindsight effect. https://arxiv.org/pdf/2410.07076 (READ-PARTIAL)

## Frontier
- **Hassabis's "Einstein test":** train a model with a 1901 knowledge cutoff and see if it finds special relativity; he also names analogical reasoning as the missing piece. It is time-sliced evaluation scaled up. `TRANSCRIPTS_YC.md:12591,12598-12601` (CAPTION-PARAPHRASE)
- **CHIMERA** (Sternlicht & Hope, ACL 2026), a knowledge base of idea recombinations; **MUSE** (Sweed et al., EMNLP 2025); **Obliq-bench** (Tchuindjo, Shah, Khattab 2026). All seen in RATIO's references.
- **TCA-SIR**, https://arxiv.org/pdf/2607.28498: retrieves transferable principles tailored to the target problem; reports +10 points hit rate over MOOSE-Chem.
- **HypoArena**, https://arxiv.org/pdf/2607.15766: a benchmark for proposing hypotheses from incomplete evidence.
- **SKiM-GPT** (PMC12829140): co-occurrence search proposes A–B–C links and an LLM grades them against abstracts; agreement with human experts QWK=0.84 on 14 hypotheses.
- **Peng, Bonifield & Smalheiser 2017** ("Gaps"); **Smalheiser & Gomes 2014** ("negative consensus"); **Sybrandt 2018 MOLIERE** (https://arxiv.org/pdf/1802.03793), which reports a lab-confirmed HAND–DDX3 link.
- **Elena Glassman**, structure-mapping tools for reading many abstracts side by side — `TRANSCRIPTS_AI2.md:11282-11310`.

## Lane state
- Smalheiser 2017, Arrowsmith 2006, Swanson 2011, Moreau 2023, Kittur 2019 — READ-FULL.
- Hope 2017, Si 2024, Si 2025, SciMON, Co-STORM, Gupta & Pruthi, Beel, MOOSE-Chem, Theorizer, RATIO, Bridger, Kang 2022 (only 3 participants, qualitative), Thilakaratne, SKiM-GPT — READ-PARTIAL (pdftotext plus targeted sections).
- Gentner 1993, Torvik 2007 — abstract only; full text closed / BLOCKED on OUP.
- Henry & McInnes 2017, Yetisgen-Yildiz & Pratt 2009 — BLOCKED (ScienceDirect captcha via both curl and r.jina.ai); abstracts READ.
- Gick & Holyoak 1980 — BLOCKED (Deep Blue behind Cloudflare). Swanson 1990 PMC XML — MISSING (500 error).
- Local corpus: guidesfm articles and x-guides — EMPTY for Swanson/analogy/LBD. Transcripts — 1 relevant hit (Hassabis).

## Source register (all fetched 2026-09-26)
- PMC5771422, PMC1559644, PMC3097086, PMC9945845, PMC6369801, PMC7924697, PMC12829140 — READ
- arxiv.org/pdf/ 1706.05585, 2409.04109, 2506.20803, 2305.14259, 2408.15232, 2502.16487, 2502.14297, 2410.07076, 2601.16282, 2607.15766, 2607.28498, 2608.27394, 2108.05669, 2206.01328, 1802.03793 — READ-PARTIAL
- pubmed 8243045, 28838802, 19124086, 17463015 — abstracts READ
- sciencedirect S1532046417301909, S1532046408001482; academic.oup.com btm161; hdl.handle.net/2027.42/23210 — BLOCKED
- `~/Desktop/researchfms/Transcripts/TRANSCRIPTS_YC.md:12568-12612`, `TRANSCRIPTS_AI2.md:10900-11330` — READ-PARTIAL