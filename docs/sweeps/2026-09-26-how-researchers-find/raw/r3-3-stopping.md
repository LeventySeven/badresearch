<!-- AGENT OUTPUT — R3-3 stopping with recall guarantees. Returned by a subagent, not read by the chair unless a row says so. -->

## Findings

**F1. People who search iteratively do not know their own recall. Extends and contradicts K8 (self-judged saturation).**
- **Who:** Blair & Maron 1985, CACM. 668 citations on OpenAlex. I reached this only through Cormack & Grossman 2016 (see F3), because the primary was BLOCKED.
- **Evidence:** "teams of lawyers and paralegals, using iterative Boolean searches, believed they had achieved 75% recall, when in fact they had achieved 20%." Source: web.archive.org/web/20160821003944id_/http://plg.uwaterloo.ca/~gvcormac/reliability/cormackgrossman16.pdf (2026-09-26; ROUTER, READ-FULL)
- **Bears on:** Q6, C1.
- **Limit:** One 1985 study of Boolean search over a legal collection.

**F2. The "N irrelevant in a row" stop, which is novelty saturation made formal, misses its recall target about 4 times in 10. A random-sample hypothesis test does not. Contradicts K8.**
- **Who:** Callaghan & Müller-Hansen (MCC Berlin), Systematic Reviews 9:273, 2020. 116 citations. Academic, no product to sell.
- **Evidence:** "Although the mean work saved for IH50 is 41%, the target is missed in 39% of cases."
- **Why it fails:** "where ML has performed well … a low proportion of relevant documents in those not yet checked is indicative of lower recall." A good searcher runs dry sooner, and a dry run is exactly what fools this rule.
- **The procedure:** pause the adaptive search. Draw random documents from the unseen remainder. Stop once you can state "We reject the null hypothesis that we achieve a recall of less than 95% with a significance level of 5%."
- **Measured result:** the test reached 95% recall in more than 95% of runs. The random-sample version missed 3.29% of the time and saved 15% of the work; the ranked version missed 0.95% and saved 17%. A baseline-rate estimate missed 39.67%.
- **Source:** https://systematicreviewsjournal.biomedcentral.com/articles/10.1186/s13643-020-01521-4 (2026-09-26; READ-FULL)
- **Bears on:** Q6.
- **Limit:** When relevant items are rare the test gets expensive. In one dataset (47 relevant in 5,999) the searcher had 95% recall early but could not prove it until much later. The authors did not correct formally for repeated testing.

**F3. Certify the stop with a target set the searcher never sees. This lets accretion steer freely. Connects K1 and K8.**
- **Who:** Cormack (U. Waterloo) & Grossman (then at Wachtell Lipton), SIGIR 2016. 99 citations. They built continuous active learning (CAL), the method under test.
- **The target method:** draw random documents until 10 relevant ones are found. Then search without knowing which they are, and stop when all 10 have turned up. The paper proves at least 70% recall with 95% reliability. The extra review costs about 10|C|/R documents, roughly 1,000 at 1% prevalence (|C| = collection size, R = number of relevant documents).
- **The eDiscovery acceptance test it compares against:** a 75% recall estimate at ±5% and 95% confidence needs about 385 random relevant documents, 38.5 times the target method's overhead.
- **Evidence:** "if the underlying method uses a human in the loop to formulate queries or to influence the selection of documents in any way, that human must be isolated from any knowledge of T." They call this an "information barrier".
- **The knee method:** a formal saturation stop. Stop when the slope ratio is at least 6 (before vs after the bend in the recall curve), after at least 1,000 documents. The threshold rises to 150 when few relevant documents have been found. It was reliable across 555 topics and 4.5M documents. The budget variant was added because low R breaks saturation.
- **Source:** same PDF as F1 (2026-09-26; READ-FULL)
- **Bears on:** Q6, C1, C5.
- **Limit:** The knee and budget methods are tuned to one CAL baseline. The test collections are convenience samples.

**F4. Courts certify a stop two ways: a blind stratified sample, plus a judgment on whether what was missed is new. Extends K8.**
- **Who:** In re Broiler Chicken (N.D. Ill.), order of 2018-01-03 signed by Special Master Maura Grossman and Magistrate Judge Gilbert. Rio Tinto v. Vale (S.D.N.Y. 2015, Judge Peck).
- **The Broiler Chicken procedure:** a 3,000-document validation sample is drawn from the produced set, the human-rejected set and the machine-excluded set. An expert codes it blind, "with no indication of the Subcollection".
- **Evidence (Broiler Chicken):** "a recall estimate on the order of 70% to 80% is consistent with, but not the sole indicator of, an adequate (i.e., high-quality) review"; what also matters is "the novelty and materiality (or conversely, the duplicative or marginal nature)" of the missed documents. Source: https://storage.courtlistener.com/recap/gov.uscourts.ilnd.330954/gov.uscourts.ilnd.330954.586.0_1.pdf (2026-09-26; READ-FULL, validation section and Appendix A)
- **Evidence (Rio Tinto):** the protocol's control set "is not used to train the set, it is only for validation"; and "it is inappropriate to hold TAR to a higher standard than keywords or manual review." Source: https://www.courtlistener.com/opinion/8788861/rio-tinto-plc-v-vale-sa/ (2026-09-26; READ-PARTIAL)
- **What this adds to K8:** novelty is judged on the *discard pile*, not on the stream of new results.
- **Bears on:** Q6, Q2.
- **Limit:** Both are negotiated between adversaries. Manual review is held to no validated standard at all (compare F1).

**F5. Capture–recapture has the same blind spot as saturation. Extends K8 (both its capture–recapture row and the critic's correction).**
- **Who:** Webster & Kemp (UK Atomic Energy Authority), American Statistician 2013. 12 citations.
- **Evidence:** "This will fail if there is a sub-population that is much more difficult to find, for which case both searchers will appear to have found the majority of items and will over-estimate the accuracy of their search." Source: https://arxiv.org/pdf/1205.1150 (2026-09-26; READ-PARTIAL). They also show that the widely used Chapman and Lincoln-Petersen estimates are "often too small".
- **Second source:** Poorolajal et al. estimated 87.2% completeness from three sources, and warn that "sufficiently high overlapping information is required". Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC3082794/ (2026-09-26; READ-PARTIAL)
- **Bears on:** Q6.
- **Limit:** Two searches that share a blind spot certify each other.
- **Popularity note:** the sharpest statement of this limit has 12 citations.

**F6. Practitioners' consensus stop combines saturation with floors, a second searcher and held-out key papers. Extends K8 and connects K2 (seeds must span clusters).**
- **Who:** Boetje & van de Schoot (Utrecht, ASReview team), Systematic Reviews 2024, peer-reviewed by 26 experts. 131 citations. The authors maintain the free tool they recommend.
- **The rule:** stop only when all four hold: every key paper found, at least twice the estimated number of relevant records screened, at least 10% of the dataset screened, and 50 irrelevant records in a row. Then switch to a different model to re-rank what is left. Then an independent screener checks the excluded records.
- **Evidence:** key papers "might not be the best set to use as prior knowledge … as they could be biased by the method used to identify them", and experts tend toward "citing papers from their colleagues". Key papers are therefore used only to validate, never to seed. Also: "a direct comparison with existing stopping heuristics has not been presented".
- **Source:** https://systematicreviewsjournal.biomedcentral.com/articles/10.1186/s13643-024-02502-7 (2026-09-26; READ-PARTIAL)
- **Bears on:** Q6, Q5.
- **Limit:** The recall of this rule has not been measured.

**F7. The review world's brake on accretion is disclosure and peer review, not a frozen plan. Extends the critic's absent class.**
- **Who:** Rethlefsen et al., PRISMA-S, 2021. 3,400 citations.
- **What PRISMA-S does:** it is a *reporting* standard. It accepts "targeted, iterative hand searching", personal files, and related-articles tools that cannot be reproduced.
- **Evidence:** "it is still important to declare that the method was used, even if it may not be fully replicable." Other requirements: report the strategy "exactly as run", peer review with PRESS, give dates, and state any cap on web results set in advance. Source: https://systematicreviewsjournal.biomedcentral.com/articles/10.1186/s13643-020-01542-z (2026-09-26; READ-PARTIAL, Items 1–16)
- **Measured drift, search:** in 22 nursing protocol-review pairs registered on PROSPERO, the protocol register, all 22 showed differences in "Search strategy", and only 3% of all differences were explained. Source: https://www.biorxiv.org/content/10.1101/2020.04.14.040865.full.pdf (2026-09-26; READ-PARTIAL; preprint, n=22)
- **Measured bias, outcomes:** in Cochrane reviews, "Outcomes that were promoted in the review were more likely to be significant than if there was no discrepancy (relative risk 1.66 …)". Changes were made after seeing trial results in 8 of 28. Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0009810 (2026-09-26; READ-PARTIAL)
- **Bears on:** C1, Q6.
- **Limit:** I found no study that measures bias from adaptive *searching* itself (EMPTY, see Lane state).

**F8. The mechanism is data-dependent choice without any fishing. The remedy from the people who named it is two phases, not preregistration. Connects K1 and K7.**
- **Who:** Gelman (Columbia) & Loken, 2013. Also Nosek's replication, which they cite.
- **Evidence:** "Our most important hypotheses could never have been formulated ahead of time." Their remedy is "two experiments, the first being exploratory but still theory-based, and the second being purely confirmatory with its own preregistered protocol."
- **The cited case:** Nosek's replication "had over 99% power. Nonetheless … p-value of .59."
- **Source:** http://www.stat.columbia.edu/~gelman/research/unpublished/p_hacking.pdf (2026-09-26; READ-PARTIAL)
- **Bears on:** C1, C5.
- **Limit:** Written about analysis, not literature search. The mapping to search is my inference; it has the same shape as F3's walled-off target set.

**F9. Reviewers reconcile iteration and discipline by review type. The qualitative saturation rule is the same heuristic F2 measured. Connects K8 and K12.**
- **Who:** Booth (Sheffield), Systematic Reviews 2016, a structured review of 131 papers. 590 citations.
- **The split:** reviews that aggregate evidence pre-specify and search exhaustively. Theory-building reviews iterate, treating "the question as a compass rather than an anchor".
- **Their stop:** O'Connell & Downe stopped "when two articles identified late in the search process did not add anything new". One reviewer: "if the next twenty papers don't offer anything new, what's the likelihood of the 21st".
- **Practice lags the method:** 81% of meta-ethnographies still search exhaustively.
- **Source:** https://systematicreviewsjournal.biomedcentral.com/articles/10.1186/s13643-016-0249-x (2026-09-26; READ-PARTIAL)
- **Bears on:** Q6, C2.
- **Limit:** F2's 39% miss rate is for *studies*. Whether saturation of *concepts* is reliable has never been measured.

**F10. Monitoring as a standing channel has entry rules, a monthly cadence and exit rules. It replaces the stop. Extends K8 (EPO's "clearly demonstrate" stop).**
- **Who:** Cochrane's 2019 guidance on living systematic reviews. Elliott et al. 2014 (616 citations). Shojania et al. 2007 (856 citations).
- **Cochrane's rules:** monthly searches of core databases. A review enters "living mode" only if all three hold: priority, uncertainty, emerging evidence. It leaves when any one fails, for example "a reasonable level of certainty has been reached". Continuation is reassessed yearly.
- **Evidence (Cochrane):** "updated … when relevant new information … that is likely to impact the conclusions of the LSR is identified or on a pre-specified fixed schedule (e.g. every 4 months)." Source: https://community.cochrane.org/sites/default/files/uploads/inline-files/Transform/201912_LSR_Revised_Guidance.pdf (2026-09-26; READ-PARTIAL)
- **Elliott's publishing rule, three tiers:**
  - no new studies: update the date only;
  - negligible change: editorial check only;
  - a changed conclusion: rapid peer review.
- **Elliott's warning:** "an inflated rate of false-positive findings is likely if statistical tests are repeated naively". Monitoring has its own forking paths. Source: https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1001603 (2026-09-26; READ-FULL)
- **How fast a stop goes stale (Shojania):** "In 7%, a signal had already occurred at the time of publication". The share reached 15% at 1 year and 23% at 2 years, with a median of 5.5 years. Cardiovascular and heterogeneous topics went stale faster. Source: https://pubmed.ncbi.nlm.nih.gov/17638714/ (2026-09-26; abstract only)
- **PRISMA-S Item 12:** email alerts count as an update method, for example "Ovid Auto Alerts … weekly"; the last search should be under 6 months before publication.
- **Bears on:** Q6, Q1.
- **Limit:** Built for fast-moving trial fields. It needs a standing team.

**F11. An individual's monitoring setup: keyword alerts, category lists and a weekly pick. Extends K9 and K2 (Jolicoeur-Martineau's citation subscriptions).**
- **Who:** Sebastian Raschka, arXiv cs.LG moderator 2018–21. He sells books and a newsletter.
- **Evidence:** "the problem is not finding interesting papers but how to avoid getting distracted"; "I have Google Scholar keyword alerts". He read the titles of 100–300 uploads a day, several times a week.
- **Source:** https://sebastianraschka.com/blog/2023/keeping-up-with-ai.html (2026-09-26; READ-FULL)
- **Bears on:** Q1, Q6.
- **Limit:** His stop is a matter of priority. He does not claim coverage.

## Against the claims

**A1. Against the fear that accretion drifts (C1's cost, as the critic framed it), in a closed collection.**
- **Who:** Cormack & Grossman, SIGIR 2015. 37 citations. They are the method's authors.
- **Evidence:** "continuous active learning … efficiently achieves high recall for each facet of the topic", which answers the concern of "excluding identifiable categories of relevant information." Rio Tinto, citing their 2014 paper: under CAL "the contents of the seed set is much less significant."
- **Source:** http://web.archive.org/web/2016id_/http://plg.uwaterloo.ca/~gvcormac/facet/ (2026-09-26; abstract only)
- **Limit:** A fixed, closed corpus. The open web is not closed.

**A2. Against C1 as sufficient.** F1 shows iterative searchers at 20% believing they were at 75%. F2 shows a saturation stop missing its target 39% of the time. Accretion finds; it does not certify.

## Not covered by any claim

- **An information barrier as the certification device:** a sample the searcher cannot see (F3, F4, F6).
- **Stop cost scales inversely with prevalence** (F2, F3). When the answer is rare, every certifiable stop gets expensive.
- **Judge novelty in the discard pile, not the stream** (F4).
- **Repeated updating inflates false positives** (F10).

## Frontier

- Lewis, Yang & Frieder, "Certifying One-Phase Technology-Assisted Reviews" and "Heuristic stopping rules for TAR" (2021). Not read.
- Bagdouri et al.: the control set is "sequential sampling", which yields a biased recall estimate (cited in the Cormack & Grossman PDF).
- Shemilt 2014 baseline inclusion rate; Howard et al. SWIFT-Active Screener (recall estimate uses proprietary software and is not reproducible, per Callaghan).
- Booth 2010, "How much searching is enough?" (IJTAHC 26:431). Not read.
- Silagy 2002 (43 of 47 Cochrane reviews had major changes). DIGEST-ONLY.
- Blair 1996, "STAIRS redux".
- Taguchi loss functions as a replacement for a fixed recall "goal-post".
- TREC Total Recall "call your shot" protocol.

## Lane state

- Blair & Maron primary (dl.acm.org; silver hit a CAPTCHA/403): BLOCKED. Used through Cormack & Grossman.
- Cormack & Grossman 2016: the live page 404s. Reached through a Wayback copy of the authors' PDF. READ-FULL.
- jclinepi.com (Elliott 2017, LSR part 1): BLOCKED (Cloudflare). Replaced by the Cochrane 2019 guidance.
- Measured bias from adaptive search vs protocol search: EMPTY. One targeted query found only studies of outcome switching (Kirkham) and PROSPERO drift (nursing, n=22).
- Local corpus (guidesfm articles and x-guides, researchfms transcripts), searched for alert/RSS/scholar-alert practices: EMPTY. Only site RSS links and product demos.
- BMC direct fetch returned a JS challenge; r.jina.ai worked.

## Source register

- systematicreviewsjournal.biomedcentral.com/articles/10.1186/s13643-020-01521-4 — READ-FULL
- web.archive.org/web/20160821003944id_/http://plg.uwaterloo.ca/~gvcormac/reliability/cormackgrossman16.pdf — READ-FULL
- cormack.uwaterloo.ca/PAPERSx.html — READ (router)
- storage.courtlistener.com/recap/gov.uscourts.ilnd.330954/gov.uscourts.ilnd.330954.586.0_1.pdf — READ-PARTIAL
- ediscoverytoday.com/wp-content/uploads/2025/06/Validation-Protocol-in-In-re-Broiler-Chicken-Antitrust-Litigation.pdf — READ (secondary, unused)
- courtlistener.com/opinion/8788861/rio-tinto-plc-v-vale-sa/ — READ-PARTIAL
- systematicreviewsjournal.biomedcentral.com/articles/10.1186/s13643-020-01542-z — READ-PARTIAL
- stat.columbia.edu/~gelman/research/unpublished/p_hacking.pdf — READ-PARTIAL
- journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1001603 — READ-FULL
- community.cochrane.org/…/201912_LSR_Revised_Guidance.pdf — READ-PARTIAL
- jclinepi.com/article/S0895-4356(17)30636-4/fulltext — BLOCKED
- journals.plos.org/plosone/article?id=10.1371/journal.pone.0009810 — READ-PARTIAL
- systematicreviewsjournal.biomedcentral.com/articles/10.1186/s13643-016-0249-x — READ-PARTIAL
- systematicreviewsjournal.biomedcentral.com/articles/10.1186/s13643-024-02502-7 — READ-PARTIAL
- pmc.ncbi.nlm.nih.gov/articles/PMC3082794/ — READ-PARTIAL
- arxiv.org/pdf/1205.1150 — READ-PARTIAL
- biorxiv.org/content/10.1101/2020.04.14.040865.full.pdf — READ-PARTIAL
- pubmed.ncbi.nlm.nih.gov/17638714/ ; /16848895/ — abstracts
- arxiv.org/abs/1504.06868 ; web.archive.org/…/~gvcormac/facet/ — abstracts
- sebastianraschka.com/blog/2023/keeping-up-with-ai.html — READ-FULL
- dl.acm.org/doi/10.1145/3166.3197 — BLOCKED