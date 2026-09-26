<!-- AGENT OUTPUT — R2-1 foraging and search strategy. Returned by a subagent, not read by the chair unless a row says so. -->

## Findings

F1. **The patch-leaving rule, and two tests of it.** The marginal value theorem says: stay in a source while its marginal yield is above the average yield of the whole environment, then leave. Pirolli & Card tested this on 8 users of the Scatter/Gather clustering interface. Across 2,929 cluster decisions, users picked a cluster when its profitability was above their current rate of gain and skipped it when below (χ²(1)=50.65). Hills, Jones & Todd ran the same test on memory search (animal-naming, n≈141). People whose leaving times sat furthest from the MVT optimum recalled fewer items: B=−5.35 items per second of deviation, p<.001.
- who: Pirolli & Card, Xerox PARC, funded by ONR (OpenAlex cites 1,290). Hills (Warwick), Jones and Todd (Indiana).
- evidence: "a forager should remain in a patch so long as the slope of gi (i.e., the marginal value of gi) is greater than the average rate of gain R for the environment" — Wayback copy of PARC UIR-1999-05-Pirolli-Report-InfoForaging.pdf, lines 1084–86 (2026-09-26; READ-FULL). "Greater deviation from the optimal departure time led to fewer items produced" — home.cs.colorado.edu/~mozer/Teaching/syllabi/TopicsInCognitiveScience/2012HillsetalPsychRev2012.pdf (READ-FULL)
- bears on: Q6, C1. **Extends K8.** K8's stops all mean "nothing new arrived". MVT instead leaves when a source falls below the *average rate elsewhere*, so the threshold depends on how rich the alternatives are.
- limit: Only 8 Scatter/Gather users. Hills measured memory, not documents.

F2. **People leave when the *promise* of a source drops, before its yield does.** In think-aloud web protocols, scent (judges' rating of the chance that a page's links lead to the answer) was high on entering a site. Users switched to another site or a search engine when scent fell.
- who: Card, Pirolli et al., PARC (CHI 2001; OpenAlex 167).
- evidence: "initially the information scent at a site is high, and when that information scent becomes low, users switch to another site or search engine" — Wayback copy of PARC UIR-2000-13-Card-CHI2001-WWWProtocols.pdf (READ-FULL)
- bears on: Q6, Q1. **Extends K8** with a stop signal that comes before the results do.
- limit: Only 9 leaving sequences, rated on an ordinal scale.

F3. **Which leaving heuristic, under which condition.** Stephens & Krebs list four patch-leaving rules: time, item count, giving-up time and rate. A count rule fails when some patches are empty. A giving-up-time rule works well when patches vary a lot. Payne et al. ran three experiments. Their people used none of these rules alone. What fit was Green's rule (patience that grows with each find) plus a chance of switching right after finishing a subgoal.
- who: Payne, Duggan & Neth, Bath/Manchester (JEP: General 2007).
- evidence: "if some patches contain no prey items at all, then the number-of-items rule could be disastrous" / "they did not use a simple giving-up time threshold" — purehost.bath.ac.uk/ws/files/444452/Payne,_Duggan_&_Neth,_07.pdf (READ-FULL)
- bears on: Q6. **Extends K8** (Nanda's "5 hours without learning" is a giving-up-time rule) and **connects to K2** (Wohlin's "no new papers" round rule).
- limit: Word-generation tasks, not document search.

F4. **When access gets cheaper, the model says be more selective, and a lab test shows cost changes breadth.**
- The diet model: whether you read a low-value type of source depends only on how common *better* sources are, not on how much junk arrives.
- Russell et al. drew the practical corollary: when a technology speeds delivery of both good and bad items, exclude more of the bad.
- Azzopardi, Kelly & Brennan tested cost directly (n=36). With costlier queries, people issued fewer queries, went deeper into each result list, and saved more relevant documents.
- who: Pirolli & Card. Russell, Stefik, Pirolli & Card (PARC; OpenAlex 727). Azzopardi (Glasgow) and Kelly (UNC).
- evidence: "increases in the prevalence of higher-profitability items … make it optimal to be more selective" — Pirolli & Card report, lines 1396–98. "exclude more low-quality periodicals, rather than processing all newly available periodicals" — markstefik.com/wp-content/uploads/2014/04/1993-Cost-Structure-of-Sensemaking1.pdf (READ-FULL). Azzopardi — dcs.gla.ac.uk/~leif/papers/azzopardi2013economics.pdf (READ-FULL)
- bears on: Q2, Q4. **Connects K9 and K10.** "Discard hard" is optimal when good sources are plentiful. Widening to rare sources pays when they are scarce, which matches Cochrane's condition that rare sources matter when evidence is thin.
- limit: The diet result is a model prediction, not tested on people. The cost study used 36 undergraduates.

F5. **The missing condition for K12: does the searcher already have a representation (a schema to sort findings into)?** Sensemaking alternates between searching for a representation and filling it in (coverage). Items that do not fit (the "residue") force the representation to change. Experts on repeated tasks mostly just fill in.
- who: Russell et al. (1993). Pirolli & Card 2005, a cognitive task analysis of intelligence analysts funded by ARDA.
- evidence: "In the case of experts and repeated tasks, the representation may not be problematic and most activity would concern the coverage loop" — andymatuschak.org/files/papers/Pirolli, Card - 2005 - …pdf (READ-FULL). "The representational shift loop is guided by the discovery of residue" (Russell 1993, READ-FULL; the scan's OCR is rough)
- bears on: Q4, C1, C2. **Extends K12** with a mechanism: broad pass means searching for a representation, narrow pass means filling one in. **Connects K4 and K7**: residue is the operational form of Hamming's "bears on this problem" and Darwin's contrary facts.
- limit: Built from case studies and task analysis. Top-down and bottom-up moves were seen "in an opportunistic mix", not in phases.

F6. **Novices go broad by default; experienced searchers pick a strategy per task.** Novices started with very general queries and narrowed using the engine's own suggestions, with no plan. Experienced searchers typed specific terms for fact-finding. Task type changed the strategy of experienced searchers more than of novices.
- who: Navarro-Prieto, Scaife & Rogers, Sussex (1999), 23 students.
- evidence: "novice participants typically started with very general queries, for instance "Psychology" or "Diseases", and gradually narrowed down the search, adding the words suggested from the search engines" — web.archive.org/web/2005id_/http://zing.ncsl.nist.gov/hfweb/proceedings/navarro-prieto/ (READ-FULL; the live host is dead)
- bears on: C2. **Extends K12**: broad-first with no plan is what novices do, not an expert practice.
- limit: Small observational study. The paper's own labels for "top-down" and "bottom-up" contradict each other.

F7. **Narrowing too early is the measured failure.** 10 professional intelligence analysts worked outside their expertise, on a deadline, over a large database. All of them only narrowed and never widened, and all missed some of the 9 best ("high-profit") documents. The 4 who relied on high-profit documents spent 78 vs 32 minutes, read 22 vs 7 documents, and kept larger working result sets (204 vs 107 hits). They made fewer inaccurate statements in their briefings.
- who: Patterson, Roth & Woods, Ohio State (Air Force-funded).
- evidence: "Essentially, all of the participants only used narrowing tactics and no widening tactics" — web.archive.org copy of apps.dtic.mil/sti/pdfs/ADA395332.pdf (READ-FULL)
- bears on: Q6, C2. **Extends K12 and K8**: in the stated condition (unfamiliar field, deadline, overload), stopping early and narrowing early are the error.
- limit: 4 vs 4 analysts; the authors say the statistics are only "suggestive".

F8. **Experts widen their intake and reject faster.**
- who: Pirolli & Card 2005.
- evidence: "Expert analysts often set their filters for information lower (thereby accepting more irrelevant information) because they want to make sure that they don't miss something that is relevant" (same PDF)
- bears on: Q2. **Connects K9 and K12**: an expert's breadth is cheap because their rejection is fast.
- limit: Task-analysis claim; no numbers.

F9. **Stopping on a plausible answer is the most common error, and it is worst when you know least.** Good searchers do "one more search". Expertise shows in knowing when to give up or switch strategy.
- who: Dan Russell, Google search-quality researcher. He also sells a book (*The Joy of Search*) and teaches search courses.
- evidence: "people often don't know enough about a topic to estimate whether or not something is a realistic answer and they stop searching too soon" — searchresearch1.blogspot.com/2010/02/strategies-of-thought-when-do-you.html via r.jina.ai (READ-FULL). "good searchers do is one more search" — theinformed.life/2023/05/21/episode-114-dan-russell/ (READ-FULL transcript)
- bears on: Q6. **Extends K8**: the domain-knowledge axis from K12 also sets how reliable a stop is.
- limit: Practitioner observation; he gives no counts here.

F10. **Which stopping rule people use depends on how structured the task is.** Browne et al. ran 115 people on three web tasks. A 2017 conceptual replication found the same rules for structured tasks, but possibly different ones for poorly structured tasks.
- who: Browne, Pitts & Wetherbe (MIS Quarterly 2007). Gerhart & Windsor (AIS Transactions on Replication Research 2017).
- evidence: "Poorly structured tasks potentially involve the use of different stopping rules than previously determined" — aisel.aisnet.org/trr/vol3/iss1/2/ (abstract READ; body BLOCKED)
- bears on: Q6. **Extends K8.**
- limit: I could reach only the abstracts.

F11. **Skimming keeps the main ideas and loses the inferences.** Readers given time for half of each text skimmed by leaving a paragraph when its rate of new information dropped below a threshold. Skimming helped only when the pages were easy to navigate.
- who: Duggan & Payne, Bath (JEP: Applied 2009).
- evidence: "skimming improved memory for important ideas from a text but did not improve memory of less important details or of inferences made from information within the text" — web.archive.org copy of time.com/wp-content/uploads/2015/05/duggan_payne_jepa_2009.pdf (READ-FULL)
- bears on: Q2, C3. **Limits K9 and connects it to K5**: the connections K5 says are the payoff are exactly what skimming does not keep.
- limit: Lab texts under time pressure.

## Against the claims

A1. **Domain experts search broader, not narrower.** A 3-month log study of more than 500,000 users across medicine, finance, law and computer science:
- Experts used domain vocabulary in 37% of queries vs 26% for non-experts.
- Experts' sessions were longer, branched more, and visited more unique domains in all four fields.
- Search-skilled users (the 20% who used query operators) showed the opposite: more directed trails and much fewer queries per session (d=1.98). They also clicked further down the result list (d=.67) and were more successful.
- who: White, Dumais & Teevan (MSR, WSDM 2009; OpenAlex 311). White & Morris (MSR, SIGIR 2007).
- evidence: "experts exhibiting more branchiness and visiting more unique domains in all cases … experts have developed strategies to explore the space more broadly than non-experts" — microsoft.com/en-us/research/wp-content/uploads/2016/02/wsdm09-expertise.pdf (READ-FULL). whitesigir2007b.pdf (READ-FULL)
- bears on: C2. **Contradicts K12's "experts go narrow".** Domain expertise and search expertise push breadth in opposite directions.
- limit: Experts were identified by visits to specialist sites (PubMed, SEC, Westlaw, ACM). Success is measured by proxies.

A2. **An expert's hypothesis can slow the search down.** 94 reported solve times for one challenge were split roughly half under and half over 5 minutes. Russell says the slow ones often made wrong assumptions, "Paradoxically, this often happens to people who are experts in the field."
- evidence: "Even (especially!) if you're an expert in a field, do the simple, dumb, obvious search first" — searchresearch1.blogspot.com/2011/12/how-long-does-it-take-to-find-answer.html (READ via search page)
- bears on: C2. **Contradicts K12's hypothesis-first practice** (Carlini, Karnofsky) as a default for search.
- limit: Self-reported times from a biased sample.

A3. **Searching with a prior answer anchors, and search can make right answers wrong.** 75 clinicians answered 400 questions before and after searching. Of those right beforehand, 22.4% were wrong afterwards. Of those wrong beforehand, 45.1% stayed wrong (χ²=19.63). In students (n=227) the figures were 5.7% and 37.8%.
- who: Lau & Coiera, UNSW (JAMIA 2007).
- evidence: Table 3 — pmc.ncbi.nlm.nih.gov/articles/PMC1975788/ (READ-FULL)
- bears on: Q5. **Contradicts K12 hypothesis-first and connects to K7.**

A4. **Structured hypothesis testing (Heuer's ACH method) did not improve accuracy; aggregation did.** 50 UK analysts took part.
- evidence: "the control group was a little more accurate (and coherent) than the ACH group" … judgment error "decreased by 61% after first coherentizing … and then aggregating" — sas.upenn.edu/~baron/journal/18/18803/jdm18803.html (READ-FULL)
- bears on: Q5, Q7. **Limits K7** (Heuer's method) and **connects to K11**: independent judgments that are statistically pooled beat a structured method.

A5. **Stopping when results stop being new performed worst at the result-list level.** In simulations over two TREC collections, checked against real user data:
- "Stop after N non-relevant results, especially N in a row" was best and closest to what users did.
- Difference-based rules (stop when a snippet is too similar to what was already seen) were consistently poor.
- The MVT rate rule scored significantly lower than a fixed depth.
- who: Maxwell, Azzopardi, Järvelin & Keskustalo (CIKM 2015).
- evidence: "difference-based stopping strategies SS4 and SS5 consistently performed poorly" — strathprints.strath.ac.uk/75627/1/Maxwell_etal_CIKM_2015_…pdf (READ-FULL)
- bears on: Q6. **Contradicts K8 at the query level.** K8's novelty rule (Wohlin, Cochrane) is a session- and corpus-level rule, so these do not directly collide.

## Not covered by any claim

N1. **Switching strategy, meaning asking a person, is the expert's move when stuck.** Evidence: "One of the hallmarks of a truly expert searcher is one who knows when to stop their current search strategy and switch to another strategy" — searchresearch1.blogspot.com/2012/01/search-strategies-what-are-they.html. **Connects K3 to K8.**

N2. **Extracting data costs more than finding it.** Extraction and encoding took "over 75% of the total time" (Russell 1993), so faster retrieval alone "may help very little".

N3. **People tend to stay in a patch too long** (reward-foraging task, t(20)=−4.87) — Constantino & Daw 2015, pmc.ncbi.nlm.nih.gov/articles/PMC4624618/ (READ). Not an information task.

## Frontier
- Fu & Gray 2006, "Suboptimal tradeoffs in information seeking" (Cognitive Psychology): measured under-exploration. Seen in the SNIF-ACT references.
- Fu & Pirolli 2007 SNIF-ACT 2.0: Bayesian satisficing leave rule, validated on 74 subjects. Only a 1-page abstract was reachable (escholarship.org).
- Maxwell PhD 2019, theses.gla.ac.uk/41132: stopping models.
- Bhavnani's Strategy Hubs, Tabatabai & Shore 2005, Jenkins et al. 2003 (domain novices browse breadth-first), Duggan & Payne 2008, Vakkari 2001/2003: follow-ups to Hölscher & Strube. DIGEST or router only.
- Wu & Kelly 2014 and Prabha et al. 2007 on stopping; Zach 2005, cited via Maxwell: people stopped when satisfied while believing more existed.
- Hames: time-minimizer vs resource-maximizer response to cheaper search (Pirolli & Card 1999).
- Aula, Khan & Guan 2010 (Google): after a couple of failed searches, users switch to question queries or operators, or "completely changed their approach" — research.google/blog/frowns-sighs-… (READ).
- arXiv 2601.12544, "Information Farming: From Berry Picking to Berry Growing" (2026).

## Lane state
- Pirolli & Card 1999: READ-FULL via the Wayback copy of a PARC preprint. Round 1's BLOCKED is resolved. ACM, APA, ResearchGate and Wiley all hit Cloudflare in both curl and silver.
- Pirolli 2005 (Cognitive Science) and the 2007 book: BLOCKED (Wiley captcha; no open copy).
- Marchionini 2006: BLOCKED (ACM and ResearchGate captchas).
- Browne 2007 body: BLOCKED (AISeL captcha); abstract READ.
- Zach 2005, Vakkari 2001: BLOCKED; routers only.
- DTIC: live site under maintenance or 403; the Wayback copy worked.
- searchresearch1.blogspot.com: TLS fails from this network; r.jina.ai worked.
- Local corpus (guidesfm articles and x-guides, GUIDES_*, researchfms transcripts and teardowns): EMPTY. The only hits were passing mentions in a marketing essay and a course transcript.

## Source register (all fetched 2026-09-26)
- web.archive.org/web/2005id_/http://www2.parc.com/istl/projects/uir/pubs/items/UIR-1999-05-Pirolli-Report-InfoForaging.pdf — READ-FULL
- web.archive.org/web/2006id_/http://www2.parc.com/istl/projects/uir/pubs/items/UIR-2000-13-Card-CHI2001-WWWProtocols.pdf — READ-FULL
- markstefik.com/wp-content/uploads/2014/04/1993-Cost-Structure-of-Sensemaking1.pdf — READ-FULL
- andymatuschak.org/files/papers/Pirolli, Card - 2005 - The sensemaking process….pdf — READ-FULL
- home.cs.colorado.edu/~mozer/…/2012HillsetalPsychRev2012.pdf — READ-FULL
- purehost.bath.ac.uk/ws/files/444452/Payne,_Duggan_&_Neth,_07.pdf — READ-FULL
- strathprints.strath.ac.uk/75627/1/Maxwell_etal_CIKM_2015_….pdf — READ-FULL
- dcs.gla.ac.uk/~leif/papers/azzopardi2013economics.pdf — READ-FULL
- microsoft.com/en-us/research/wp-content/uploads/2016/02/wsdm09-expertise.pdf — READ-FULL
- microsoft.com/en-us/research/wp-content/uploads/2016/02/whitesigir2007b.pdf — READ-FULL
- web.archive.org/web/2005id_/http://zing.ncsl.nist.gov/hfweb/proceedings/navarro-prieto/ — READ-FULL
- web.archive.org/web/2022id_/https://apps.dtic.mil/sti/pdfs/ADA395332.pdf — READ-FULL
- web.archive.org/web/2020id_/https://time.com/wp-content/uploads/2015/05/duggan_payne_jepa_2009.pdf — READ-FULL
- pmc.ncbi.nlm.nih.gov/articles/PMC1975788/ — READ-FULL
- pmc.ncbi.nlm.nih.gov/articles/PMC4624618/ — READ-PARTIAL
- sas.upenn.edu/~baron/journal/18/18803/jdm18803.html — READ-FULL
- searchresearch1.blogspot.com: 2010/02, 2011/12, 2012/01, 2026/09 posts (via r.jina.ai) — READ
- theinformed.life/2023/05/21/episode-114-dan-russell/ — READ-FULL
- hci.stanford.edu/seminar/abstracts/07-08/080118-russell.html — READ (abstract)
- research.google/blog/frowns-sighs-and-advanced-queries-… — READ
- aisel.aisnet.org/misq/vol31/iss1/7/ and aisel.aisnet.org/trr/vol3/iss1/2/ — abstracts READ; PDFs BLOCKED
- escholarship.org/…/qt8jz4g3g1… (SNIF-ACT) — READ (1 page)
- eric.ed.gov/?id=EJ625205 — abstract READ
- dl.acm.org (5 DOIs), onlinelibrary.wiley.com (10.1207/s15516709cog0000_20), ResearchGate (Marchionini), emerald.com (Vakkari), apps.dtic.mil (live) — BLOCKED