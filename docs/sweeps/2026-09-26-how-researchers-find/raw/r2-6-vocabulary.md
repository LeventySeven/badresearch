<!-- AGENT OUTPUT — R2-6 vocabulary mismatch. Returned by a subagent, not read by the chair unless a row says so. -->

## Findings

**F1. People name the same thing differently almost every time. The fix is many aliases gathered from many people, not synonyms one person thinks up.** Extends K5 by measuring the wall.
- who: Furnas, Landauer, Gomez & Dumais, Bell Communications Research (Bellcore), CACM 1987. Cited 1,739 times (Semantic Scholar) / 1,513 (OpenAlex). Nothing to sell.
- evidence: "In every case two people favored the same term with probability <0.20." / "three armchair aliases are no better than a single optimally chosen term." / "The recipe texts contain roughly 80 percent of the keywords selected by users"
  - web.archive.org/web/20240221075657id_/https://dl.acm.org/doi/pdf/10.1145/32206.32212 (2026-09-26; READ-FULL, OCR)
- more from the paper:
  - If one person names an item, other untrained people fail to reach it 80–90% of the time.
  - Expert cooks' keywords "fared no better than average".
  - Even fifteen aliases satisfy only about 60–80% of attempts (the OCR is garbled at this number).
  - Indexing the full text was about as good as harvesting aliases from experts.
  - Their adaptive index works like this: users try their own words and "usually fail"; when they finally find the item, the words that failed get attached to it.
- bears on: Q1, Q3, C1
- limit: tested on command names and recipe or object keywords, not scholarly literature.

**F2. Experienced searchers working the same question pick different words and find almost entirely different documents. Documents that several independent searches all find are much more likely to be relevant.** Connects K5 with K11 and K6.
- who: Saracevic (Rutgers) & Kantor, JASIS 1988. NSF-funded. 39 searchers, 72% of whom used DIALOG weekly.
- evidence: "Only 2.5% of variation of overlap in retrieved items is explained by overlap in search terms." / "an item retrieved 5 or more times (out of 9 searches) was over six times as likely to be relevant as an item retrieved once"
  - web.archive.org/web/20230629130736id_/https://tefkos.comminfo.rutgers.edu/JASIS1988part3.pdf (2026-09-26; READ-PARTIAL: conclusions and overlap sections)
- more from the paper:
  - Search terms overlapped 27% on average; retrieved items overlapped 17%. In 59% of pairs the item overlap was 0–5%.
  - Where the search words came from mattered:

    | Source of search words | Recall |
    |---|---|
    | The user's taped problem statement | 32% |
    | Written question plus a thesaurus | 25% |
    | Words from the written question only | 18% |

  - Searches using fewer terms had 28% better odds of relevance.
- bears on: Q2, Q7, C6, C4
- limit: 1980s DIALOG, 40 questions. The authors call the convergence result "one of the most important findings of the study."

**F3. Each document found gave the next name for the same thing, and the trail never ended. The searchers believed they had found most of it when they had found a fifth.** Extends K1 and contradicts K8's novelty stop when you stay inside one vocabulary.
- who: Blair & Maron, CACM 1985. A litigation database of 350,000 pages. Cited 668 times (OpenAlex).
- evidence: "STAIRS could be used to retrieve only 20 percent of the relevant documents, whereas the lawyers using the system believed they were retrieving a much higher percentage (Le., over 75 percent)." / "there is no reason to believe that we had reached the end of the trail; we simply ran out of time."
  - web.archive.org/web/20260602005443id_/https://dl.acm.org/doi/pdf/10.1145/3166.3197 (2026-09-26; READ-FULL)
- the name chain: "trap correction" → "wire warp" → "shunt correction system" → the inventor's name, Coxwell → "Roman circle method" → "air truck". This took 40 hours.
- other misses:
  - Three key terms later grew to 26 more; four grew to 44 more.
  - People involved in the accident euphemised it ("unfortunate situation") depending on their culpability.
  - Some relevant documents never used the abstract term at all ("nonexpendable components"); they only listed the parts.
- The mechanism: searchers see precision (79%), not recall. The lawyers recognised relevant documents almost perfectly but could not recall what they had missed.
- bears on: Q3, Q6, C1, C5
- limit: one full-text legal database from 1985.

**F4. The measured way to find the field's words is to mine records you already know are relevant, hold some of them back, and stop when the held-back ones are all found.** Extends K5 (procedure) and K8 (a stop test).
- who: Hausner, Waffenschmidt et al., IQWiG, the German statutory health technology assessment institute. This is their own method, so they have an incentive.
- the procedure (Hausner et al. 2012):
  - Split the known-relevant records 2/3 for development and 1/3 for validation.
  - Keep terms that appear in at least 20% of the development records and in at most 2% of a random sample of the database.
  - Build the search, then check that it finds the held-out records.
- evidence:
  - "Terms that are present in at least 20% of the references in the development set are selected" — https://pmc.ncbi.nlm.nih.gov/articles/PMC3351720/
  - "The objective approach yielded a weighted mean sensitivity and precision of 97% and 5%. The corresponding values for the conceptual approach were 75% and 4%." — https://pubmed.ncbi.nlm.nih.gov/27256930/ (prospective, 5 reviews)
  - 96% sensitivity over 13 Cochrane searches, shown non-inferior to Cochrane's usual approach — PMID 25464826 (2026-09-26; abstracts READ-FULL, 2012 paper READ-FULL)
- They say the usual approach makes it "difficult, and might even be impossible, to tell when the strategy is completed."
- bears on: Q1, Q6, C1
- limit: contradicted by F-A3 below. It also needs known-relevant seed records to start.

**F5. Searching from similar records (PubMed "similar articles") is common and adds recall that a Boolean search misses.** Extends K2: a text-similarity link alongside citation links.
- who: Lin & Wilbur (NLM, who built the feature); Waffenschmidt et al. 2013 (IQWiG); Sampson et al. 2016.
- evidence:
  - "roughly a fifth of all non-trivial user sessions contain at least one invocation of related article search" — https://pmc.ncbi.nlm.nih.gov/articles/PMC2212667/
  - "The first 20 RelCits plus SSBS achieved high completeness and reliability (sensitivity: 98.1%, range: 80-100%)" (RelCits = related citations; SSBS = a simple Boolean search) — PMID 23419611
  - Recall: Boolean clinical query 0.69, related articles 0.66, both together 0.91 — PMID 26976054 (2026-09-26; READ-FULL abstracts)
- Cochrane's Technical Supplement says this route works "independent of the searcher's expertise."
- bears on: Q1, C1
- limit: related articles showed "least stability over time". Tested on MEDLINE drug and trial reviews.

**F6. Swapping in a related word helps when your last query already found something. It mostly fails when you had nothing.** Connects K1 and K5; matches F1's point that aliases should come from what you have found.
- who: Huang & Efthimiadis, University of Washington, CIKM 2009. AOL logs: 36M queries, 3.4M reformulations. Cited 281 times.
- evidence: "Word substitution reformulations were more likely to result in a Skip than a Click when the initial action was Skip, but result in Click 3× as often as Skip when the initial action is a Click." — https://jeffhuang.com/papers/Reformulation_CIKM09.pdf (2026-09-26; READ-FULL)
- Word substitution gave the largest rank gain of any reformulation (+4.04). About 28% of queries are reformulations.
- bears on: Q4, C1
- limit: general web users; clicks stand in for success.

**F7. A typical query word is missing from 30–50% of the relevant documents. Expanding only the two words most likely to be missing gets most of the gain.** Extends K5.
- who: Le Zhao, CMU PhD thesis 2012 (advisor Jamie Callan).
- evidence: "on average a query term mismatches (fails to appear in) 40% to 50% of the documents relevant to the query." / "Expanding only the two query terms with the highest likelihood of mismatch achieves most of the benefit of CNF expansion, saving 33% of user effort"
  - https://www.lti.cs.cmu.edu/people/alumni/alumni-thesis/zhao-le-thesis.pdf (2026-09-26; READ-PARTIAL)
- Full synonym expansion beat the keyword baseline by 50–300%.
- Words likely to be missing are the ones that are not central to the topic, have many synonyms, or are more abstract than the documents.
- In the RIA workshop failure analysis, mismatch caused 27% of failures.
- bears on: Q3
- limit: the thesis gives the rate variously as 30–40%, 30–50% and 40–50%. Measured on TREC collections.

**F8. One thing, three names: code, generic and brand. Each source uses its own.** Connects K5 with K10: registries need their own vocabulary.
- who: Knelangen et al. 2018 (IQWiG); Gwern (independent researcher).
- evidence:
  - "The main reason for study nondetection was the sole use of the drug code in the registry entries." Searching by generic name found 94% of trials in ClinicalTrials.gov, 71% in the EU register and 60% in WHO ICTRP — PMID 29132833
  - "The key turned out to be to use the trademark name instead" (ritonavir → Norvir) — https://gwern.net/search-case-studies (2026-09-26; READ-FULL)
- bears on: Q3
- limit: drugs are an easy case because their names are enumerable.

**F9. There are concrete ways to learn a field's term.** Extends K5 beyond Gwern's "skeleton" line.
- who: Gwern; Bertsekas (MIT, 2018); Tibshirani (Stanford course glossary); Rasmussen & Williams (*Gaussian Processes for Machine Learning*, 2006).
- evidence:
  - Gwern: "If you're using the wrong term, period, nothing will help you". He points to "Rosetta stones", documents that translate one field's terms into another's (Baez & Stay 2009; Bertsekas 2018; Metz et al. 2018).
  - Gwern's "Add Jargon" move: add the method words the target paper must use ("odds", "logistic regression").
  - Gwern: Wikipedia is "a good place to look for key terminology", and Google Scholar's related/cited-by lists help when "still figuring out the right jargon."
  - Gwern: the plain query `official name for Lisp's "data and code" thing` returns "homoiconicity".
  - Bertsekas: "(h) Action (or state-action) value = Q-factor of a state-control pair." — arXiv 1804.04577 §1.2
  - Rasmussen & Williams: "Gaussian process prediction is also well known in the geostatistics field … where it is known as kriging" — gaussianprocess.org/gpml/chapters/RW2.pdf §2.8
  - Tibshirani's glossary pairs ML and statistics terms, e.g. weights = parameters, learning = fitting.
- bears on: Q1, Q3
- limit: see A4.

**F10. What it costs when nobody crosses the wall.** Extends K5, contradicts relying on K2 chaining across communities, and touches K6.
- evidence:
  - Tai 1994 describes the method as "dividing the area under the curve … into small segments (rectangles and triangles)". A published reply was titled "Tai's formula is the trapezoidal rule." The paper has been cited 508 times (OpenAlex, 2026-09-26). — PMIDs 8137688, 7677819 (letter text BLOCKED)
  - Kulikowski (KU Leuven, arXiv 2609.07595, 2026-09): "the retrieval variants learn from the citation graph, which cannot reach independently re-invented twins that never cite each other." Describing each paper's mechanism with field and method names removed "lifts cross-domain retrieval average precision over the abstract from 0.222 to 0.513". Four scientific embedders all scored below a plain keyword baseline (abstract + TF-IDF).
- bears on: Q3, C3, C4
- limit: Kulikowski is a preprint with 109 papers across 18 method families. Tai is one case.

## Against the claims

**A1. More words or more reformulation does not predict success; reading more documents does.** Against a naive reading of C1 and K5.
- evidence:
  - Vakkari, Pennanen & Serola 2003 (22 psychology students): "Although the students' vocabulary of the topic grew … There was no correlation between the terms and tactics used and the total number of useful references found." — sciencedirect.com/science/article/pii/S0306457302000316 (abstract READ)
  - Bailey 2008 (UNC master's paper, n=57): high performers used fewer search terms (10.9 vs 19.7) and opened more documents (59 vs 32). — ils.unc.edu/MSpapers/3349.pdf
  - F2: fewer search terms gave 28% better relevance odds.
- limit: novices and small samples.

**A2. Vocabulary an LLM generates is precise but has low recall, and partly invented.**
- evidence: "55% and over of the MeSH terms generated by ChatGPT are actually not in the MeSH vocabulary". Output also varied a lot across runs. — arXiv 2302.03495 (Wang, Scells, Zuccon & Koopman, early 2023)
- For balance: Query2doc (LLM-written pseudo-documents) raised BM25 by 3–15% (arXiv 2303.07678); HyDE (arXiv 2212.10496) grounds a generated document in the real corpus.
- limit: a 2023 model.

**A3. Text mining was faster but less sensitive than a librarian's usual practice.** Contradicts F4.
- evidence: Paynter et al. 2021 (AHRQ): text-mining tools 84.9% vs usual practice 92% sensitivity, 5 h vs 12 h. On complex topics the tools found citations usual practice missed. — PMID 33753230, 33755394
- Hausner et al. disputed this in a 2022 letter (PMID 35644323), which I did not read.
- Status: CONDITIONAL. The axis is whether the method is IQWiG's full test-set procedure or ad-hoc tool use.

**A4. A translation document did not stop fields reinventing the same maths.**
- evidence: Stephenson & Macomber (independent researchers, preprint): Sornette's 2004 cross-field synthesis existed, "yet domain-specific literatures continued developing largely in parallel afterward." — arXiv 2601.22389
- Status: CONTESTED (one weak source).

## Not covered by any claim

- **Found by several independent searches is a relevance signal (F2).** This is popularity among independent searchers, an axis K6 lacks.
- **Hold out part of the known-relevant set and stop when all of it is found (F4).** This makes Cochrane's "only known papers" warning testable.
- **Attach the words that failed to the thing you finally found (F1).** Gwern does the same by adding keywords to his clippings.
- **Start from the richest statement of the need, not the words of the question (F2):** 32% vs 18% recall.
- **Recall is invisible to the searcher (F3).** Confidence follows precision.

## Frontier
- Markey & Atherton 1978 ERIC manual (origin of "pearl growing"); Hawkins & Wagers 1982; Booth 2008; Schlosser 2006 "comprehensive pearl growing". Seen only in a search digest.
- Gomez, Lochbaum & Landauer 1990: full text vs harvested aliases (cited in Furnas and Bates).
- Lilley 1954 (62 subject headings per book; the most common got 29%); Leonard 1977 on how consistently indexers index; the Getty study of humanities search terms (via Bates 1998).
- The jingle-jangle fallacy (same construct under different names in psychology); Bikard's "idea twins"; Matt Clancy's "How common is independent discovery?"; Ogburn & Thomas 1922.
- Tools: IQWiG searchbuildR, litsearchr, Yale MeSH Analyzer, PubReMiner, MeSH on Demand, LitSuggest, Medline Ranker, Kreutz & Schenkel 2022 (review of seed-based retrieval).

## Lane state
- Furnas via ACM: BLOCKED (Cloudflare; silver also got a CAPTCHA). Read from the Wayback copy.
- Saracevic's Rutgers site: BLOCKED (anti-robot page). Read from the Wayback copy.
- Tai letters (diabetesjournals.org): BLOCKED.
- Cochrane Handbook ch. 4 and its Technical Supplement PDF (v6.5): READ.
- Jansen/Spink reformulation papers: reached only through Huang's citations (37% of Dogpile queries are reformulations).
- Vakkari 2003: abstract only. Bailey: READ.
- Cowen's "Second Law" on Marginal Revolution: it is used as a tag on oddly specific papers, not as a method. EMPTY for procedure.
- Merton / Ogburn and Stigler's-law counts: not reached (budget).

## Source register (all fetched 2026-09-26)
- dl.acm.org/doi/pdf/10.1145/32206.32212 — BLOCKED; Wayback id_ copy READ-FULL
- dl.acm.org/doi/pdf/10.1145/3166.3197 — Wayback READ-FULL
- tefkos.comminfo.rutgers.edu/JASIS1988part3.pdf — BLOCKED; Wayback READ-PARTIAL
- pages.gseis.ucla.edu/faculty/bates/articles/indexdlib.html — READ-PARTIAL
- pages.gseis.ucla.edu/faculty/bates/articles/Information%20Search%20Tactics.html — READ-PARTIAL (the TRACE tactic: take new terms from what the search has already found)
- training.cochrane.org/handbook/current/chapter-04 — READ-PARTIAL
- training.cochrane.org/…/chapter04-tech-supplonlinepdfv65270924 — READ-PARTIAL (§3.2)
- pmc.ncbi.nlm.nih.gov/articles/PMC3351720/ — READ-FULL
- pmc.ncbi.nlm.nih.gov/articles/PMC2212667/ — READ-PARTIAL
- PubMed abstracts 27256930, 25464826, 23419611, 29132833, 26976054, 33753230, 33755394, 17971238, 8137688, 7677819, 40475881 — READ
- jeffhuang.com/papers/Reformulation_CIKM09.pdf — READ-FULL
- lti.cs.cmu.edu/…/zhao-le-thesis.pdf — READ-PARTIAL
- gwern.net/search, gwern.net/search-case-studies (via r.jina.ai) — READ-FULL
- arxiv.org/pdf/1804.04577 — READ-PARTIAL
- gaussianprocess.org/gpml/chapters/RW2.pdf — READ-PARTIAL
- web.archive.org/web/20140903084841id_/http://statweb.stanford.edu/~tibs/stat315a/glossary.pdf — READ-FULL
- arxiv.org/pdf/2609.07595, arxiv.org/pdf/2601.22389 — READ-PARTIAL
- arxiv 2302.03495 — READ-PARTIAL; 2303.07678, 2212.10496 — abstracts
- ils.unc.edu/MSpapers/3349.pdf — READ-PARTIAL
- sciencedirect S0306457302000316 (via r.jina.ai) — abstract
- doi.org/10.2337/diacare.17.10.1225a and doi.org/10.2337/diacare.17.10.1224 — BLOCKED
- marginalrevolution.com search for "Cowen's Second Law" — READ (EMPTY)