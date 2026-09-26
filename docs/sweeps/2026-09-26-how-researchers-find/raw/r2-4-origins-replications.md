<!-- AGENT OUTPUT — R2-4 origins, cascades, replications. Returned by a subagent, not read by the chair unless a row says so. -->

## Findings

F1. **Bossavit checks each reference in a stacked citation against seven failure modes.** The reference may not be empirical, may support only a weaker claim, may only cite other research, may be a book-length "needle in a haystack", may be hard to obtain, or may come from one side of a dispute. Extends the cascade-origin row.
    who: Laurent Bossavit. Developer for 20 years, head of Institut Agile, former Agile Alliance board member. He sells the book, and he debunks claims his own Agile camp relies on (the defect-cost argument for TDD).
    evidence: "the papers support weaker versions of the claim • the papers don't support the claim directly, but only cite research that does" — http://samples.leanpub.com/leprechauns-sample.pdf ch.1 (2026-09-26; READ-PARTIAL, free sample)
    bears on: Q2, Q5, C5
    limit: his worked cases come from a field he calls "pseudo-scientific".

F2. **The disqualifier is often in a footnote of the origin, and derivative papers turn an assumption into "research".** Bossavit bought Boehm's 1981 book and found on p.311 that the Cone of Uncertainty ranges "have been determined subjectively". Laranjeira 1990 called the same section "empirically validated", and McConnell later cited Laranjeira as research that "suggests" the claim. Extends K10 (appendices) and the cascade row.
    evidence: "that paper "suggests" nothing of the kind; it quite straightforwardly assumes it" — same PDF, ch.2 (READ-PARTIAL)
    limit: it cost him years: "for a number of years, I finally broke down and ordered my own copy."

F3. **Re-citations get counted as replications.** This links the cascade row to K7: a "rerun" you find may be the same claim cited again.
    evidence: "A further generation counts these indirect citations as if they were themselves original research: the claim now looks very strong, as it appears to be backed by multiple replications." — https://modelviewculture.com/pieces/the-making-of-myths (READ-FULL)
    bears on: Q5, C5, K7

F4. **Provenance tools:**
    - **Citations by year, filtered by date, plus who cited first.** Royce's 1970 "waterfall" paper "remained almost totally unknown until 1987". Nearly every early citer was "an author at TRW", and the 1987 spike came from Boehm republishing it (sample ch.7).
    - **Check that the cited body exists and what it was.** For the "IBM Systems Sciences Institute", Bossavit used Scholar searches on affiliated names, obituaries, Google Books ads and a postal address.
    extends: K2 (citation chasing used for provenance, not discovery)
    evidence: "the Institute was a corporate training program, not a research body … the original project data, if any exist, are not more recent than 1981 … could be as old as 1967" — https://gist.github.com/Morendil/ebfa32d10528af04e2ccb8995e3cb4a7 (READ-FULL)

F5. **Gwern's test for a legend.** Collect every version, order them newest to oldest, and look at where the chain ends and how much the details vary. The tank story's chain always stops at Dreyfus 1992. Its likely seed is a question Fredkin asked in a 1960s Q&A, which lost its question mark in retelling.
    who: Gwern Branwen, independent writer; nothing to sell. His first attempts failed "for over more than half a decade".
    evidence: "Typically for a real story, one will find at least one or two hints of a penultimate citation and then a final definitive citation to some very difficult-to-obtain or obscure work" — https://gwern.net/tank (READ-FULL via r.jina.ai); also "Almost every aspect of the tank story which could vary does vary."
    bears on: Q5, K7, cascade row

F6. **What triggers suspicion is a mismatch in style, and the last step is a scan of the original page.** The "Walpole" quote sounded wrong for someone who died in 1797. The trail went Wikiquote → Internet Archive (not found) → HathiTrust p.342. The real quote ends "as well", which changes its meaning.
    evidence: "misattributed to the wrong person 2 centuries prior, to the wrong book, and quoted wrongly, in a way which changed the meaning substantially" — https://gwern.net/leprechaun (READ-FULL)

F7. **How often the source fails to support the claim built on it:**
    - Meta-analysis of 28 medical studies: total quotation errors 25.4%, major 11.9% (https://doi.org/10.7717/peerj.1364, Jergas & Baethge 2015, 89 cites).
    - Recalculated per quotation: 14.5%. Of those, 64.8% are major (the source fails to support, is unrelated, or contradicts), and improper indirect citation runs at 10.4% (https://doi.org/10.1371/journal.pone.0184727, Mogull 2017).
    evidence: "the referenced source either fails to substantiate, is unrelated to, or contradicts the assertion" — Mogull abstract (OpenAlex, 2026-09-26; READ-PARTIAL)
    bears on: Q2, K6
    limit: medicine only.

F8. **Greenberg builds a network for one claim and finds the counter-evidence that citations never reach.**
    - Method: take every paper stating the claim. Label each paper primary data, review, model or other. Label each citation supportive, neutral, critical or diversion. A second investigator re-checked 17% of papers.
    - Results: 8 papers (7 from one group) carried 97% of citation traffic. In one sub-claim, 24% of citations were "dead-end" (the cited paper says nothing on the point).
    - This connects K2's limit (chains stay inside one community) with K7: the six refuting papers existed, and following citations from reviews would never reach them. You have to list every primary-data paper.
    who: Steven Greenberg, associate professor of neurology at Harvard/BWH, working in the field he audits. The paper has 505 citations.
    evidence: "The supportive papers received 94% of the 214 citations to these primary data, whereas the six papers containing data that weakened or refuted the claim received only 6%" — Europe PMC full text PMC2714656 (READ-FULL)

F9. **Citing papers do not tell you a paper was retracted.**
    - 13,252 post-retraction citation contexts in PubMed Central: 722 (5.4%) mention the retraction, and "retraction did not change the way the retracted papers were cited" — Hsiao & Schneider 2021, https://api.semanticscholar.org/graph/v1/paper/DOI:10.1162/qss_a_00155 (abstract only; READ-PARTIAL).
    - 238 post-retraction citations across fields: "198 (83%) were positive, 28 neutral (12%) and only 12 (5%) negative" — Bar-Ilan & Halevi 2017, https://pmc.ncbi.nlm.nih.gov/articles/PMC5629243/ (READ-FULL). Halevi was at Elsevier and the data are ScienceDirect.
    extends: K6
    bears on: Q2, Q5
    limit: the article's status has to be checked at the source itself.

F10. **Other citers almost never mention a failed rerun, but the rerun cites the original.** That explains why Gwern's move in K7 works: search inside the original's "cited by" list for the replication.
    - Of articles citing 98 originals, fewer than 3% cited the replication attempt. A failed replication cut citations by only 5–9%, not significantly different from zero — von Hippel 2022, https://doi.org/10.1177/17456916211072525 (24 cites).
    - Ego depletion: the share of citing articles that also cited the replication went from 20% to 18%. Facial feedback: 13% to 41%. Favourable citations went from 79% to 77% — Hardwicke 2021, https://pure.uva.nl/ws/files/72827566/25152459211040837.pdf (READ-FULL, 39 cites).
    - "Only 12% of postreplication citations of nonreplicable findings acknowledge the replication failure", and nonreplicable papers are cited more — Serra-Garcia & Gneezy 2021, https://doi.org/10.1126/sciadv.abd1705 (184 cites).
    connects: K7 ↔ K6. The most useful sources here are the least cited.

F11. **How often an independent rerun exists at all:**
    - Psychology: "replication" appears in 1.6% of papers in 100 top journals since 1900. Only 68% of those are real replications, so the rate is 1.07%. That 68% is the measured precision of a "replicat*" filter. Replications were "significantly less likely to be successful when there was no overlap in authorship", so independent reruns are the ones that count (Makel 2012, 788 cites; abstract only).
    - Economics: "from 1974 to 2014 0.10% of publications in the Top 50 economics journals were replications" (Mueller-Langer 2019).
    - Tools: FLoRA (FORRT's replication database; FReD in the brief is its data/R-package side) holds 2,982 original–replication pairs, and its Zotero plugin tags DOIs already in your library "Has Replication".
    evidence: "Self-identify as a replication (e.g., "replication of Author (Year)") before reporting results — replication must be an aim, not just a result" — https://forrt.org/flora-zotero/ (READ-FULL)
    limit: because of that inclusion rule, conceptual reruns published under other names are missed (the K5 vocabulary wall).

F12. **In the Curveball case, the "corroboration" fell apart one source at a time.**
    - Three other sources gave one report each. The second recanted. The INC source was judged a fabricator in May 2002 yet stayed in the October 2002 estimate. The fourth "was not the direct source".
    - Corroboration was also misread: it "merely established that Curveball had been to the location, not that he had any knowledge of BW activities".
    - The fixes: new CIA source descriptions (September 2004), because "it is important to distinguish corroboration from repetition". Recommendation 10 requires citations in finished products. ICD 206 requires that a citation "should reference the most original source that presents the relevant information".
    who: the Robb-Silberman presidential commission, 2005. Its political incentive was to place blame on the intelligence agencies.
    evidence: "there is currently no way to determine from the face of the CIA report whether a series of reports represents one source reporting similar information several times or several different sources independently" — https://www.govinfo.gov/content/pkg/GPO-WMD/pdf/GPO-WMD.pdf pp.177–78 (READ-PARTIAL, grep); ICD 206 p.3 at https://www.dni.gov/files/documents/ICD/ICD-206.pdf (read from rendered page images, pp.2–4)
    extends: cascade row, K7

F13. **The adversarial collaboration protocol is Table 1 of the paper, not an appendix.**
    - Each side names the results that would change its mind, and the arbiter records these predictions.
    - A replication both sides agree on goes into the first study.
    - Both sides accept in advance that the first study will be inconclusive, and each gets one follow-up study.
    - The arbiter controls the data and can publish with only one side.
    evidence: "The participant should seek to identify results that would change their mind, at least to some extent … These predictions should be recorded by the arbiter" — https://pure.mpg.de/rest/items/item_2102238/component/file_2102237/content (READ-FULL)
    who: Kahneman and Hertwig as the two parties, Mellers as arbiter.
    limit: "We did not think the experiments would resolve all the issues, nor did this miracle occur." The most striking finding was one "none of us had anticipated".

## Against the claims

A1. **Sharing findings without their sources creates false corroboration (against C6 and K11).**
    evidence: "When several services unknowingly rely on the same sources and then share the intelligence production from those sources, the result can be false corroboration of the reporting." — WMD report p.178. The same page calls the result "groupthink" on an international scale.
    limit: the report blames sharing that left out source identity, not sharing as such.

A2. **Finding the counter-evidence does not make people sure (against C5 as a mechanism for belief change).**
    - About half of the articles that cited both the original and the replication, and still cited the original favourably, explicitly defended the original (Hardwicke Table 4: 31 of 60).
    - Bossavit: listeners "still believed … even though they agreed with me that the data was totally unconvincing".
    - Harzing: her 1995 debunk "didn't quite have the impact I had hoped (academics kept making the same unjustified assertions)". Her 2002 follow-up was desk-rejected by more than a dozen journals — https://harzing.com/blog/2016/04/are-referencing-errors-undermining-our-scholarship-and-credibility (READ-FULL).

A3. **The "~20% of citers read the original" figure in K6 is weaker than stated.**
    - It is an upper bound from one paper (4,300 citations; 196 misprints, 45 distinct, one repeated 78 times).
    - Across 12 papers the estimate ranges from 12% to 58%, and the weighted estimate is 0.33.
    - The authors concede that copying a citation is not proof of not reading it: "albeit this can not be rigorously proved".
    - 16 of the 88 misprints the ISI database flagged were correct in the original articles (https://arxiv.org/pdf/cond-mat/0401529, READ-FULL).
    - Liang, Zhong & Rousseau 2014 (16,622 errors in citations to Laemmli 1970) found a third route: authors copying from their own earlier paper (abstract).
    - Broadus 1983 found 23% of citers copied Wilson's error but saw "considerable doubt" that this meant fraud (quoted via gwern.net/leprechaun; primary not reached).
    - Gwern notes that reference managers now hide this signal entirely.

A4. **Most misquotation happens when citing directly, not through chains.**
    evidence: "Indirect references accounted for less than one sixth of all quotation problems." — Jergas & Baethge abstract
    So collapsing a cascade is not the main fix; reading the cited source is (connects to K9).

## Not covered by any claim

N1. **Check whether the claim can be true or false before tracing it** (Bossavit): 10x and defect-cost claims are "too vague to be either 'true' or 'false.'" — Model View Culture essay.
N2. **Tag each citation with how it was verified.** Quote Investigator (Garson O'Toole, Yale CS PhD, 4.2M visitors a year, ad-supported) marks each citation "verified with hardcopy", ProQuest or Newspapers_com, and keeps more than 4,000 investigations open, treating each attribution as "iteratively improved over time" with no stop rule (extends K8). Source: https://quoteinvestigator.com/about/ (READ-FULL).
N3. **Date the loop.** Wikipedia counts a case as citogenesis only when media that copied an article is then cited back into that article, and it uses the insertion edit's diff to date the origin — https://en.wikipedia.org/w/index.php?title=Wikipedia:List_of_citogenesis_incidents&action=raw (READ-PARTIAL).
N4. **Record mind-change conditions with a third party before the rerun** (F13).

## Frontier
- scite.ai "contrasting" citation classes: a vendor tool for finding citers who disagree. Not read.
- PubPeer, the Retraction Watch Database, and Zotero retraction alerts: reachable ways to check a paper's status. Not read.
- Tatsioni et al. 2007 on how long contradicted claims persist in medicine (cited in Hardwicke).
- Camerer and Dreber prediction markets: "experts predict well which papers will be replicated" (Serra-Garcia abstract). This could decide which claims are worth hunting reruns for.
- Todd Little 2006, IEEE Software: the counter-data to the Cone of Uncertainty (Bossavit ch.2).
- Hoerman & Nowicke 1995; Pavlovic et al. 2020; Cobb et al. 2023; Stang et al. 2018 (Newcastle-Ottawa miscitation). All listed on gwern.net/leprechaun.
- Sutton 2010 and Dagg 2015: the spinach "myth-bust" was itself a myth. The debunk needs tracing too (gwern.net/leprechaun).
- Hillel Wayne's separate check of the "100x" defect-cost claim (router: The Register, 2021).
- ICD 203 analytic standards; the Senate Intelligence Committee's 2004 Iraq report.

## Lane state
- Bossavit's book: READ-PARTIAL (the free sample holds the preface and chapters 1, 2 and 7; chapter 9, "A Leprechaun hunting tutorial", is paid).
- Gwern leprechaun and tank essays: READ-FULL via r.jina.ai.
- Simkin & Roychowdhury 2002 and 2004: READ-FULL. Liang et al.: abstract. Broadus: MISSING (gwern.net PDF fetch failed).
- Hsiao & Schneider: BLOCKED at MIT Press (Cloudflare); abstract via the Semantic Scholar API.
- Rekdal 2014 and the Makel full text: BLOCKED at Sage; abstracts via OpenAlex.
- Semantic Scholar search: EXHAUSTED (rate-limited, HTTP 429). Switched to OpenAlex.
- ICD 206: the PDF is image-only. Pages 2–4 were rendered and read; the rest is unread.
- Curate Science: READ-PARTIAL. The front page asks for funding, and no replication tracker appears there.
- Many Labs as a finding tool: not reached. Only Hardwicke's case studies (which include Many Labs) were covered.

## Source register
- http://samples.leanpub.com/leprechauns-sample.pdf — READ-PARTIAL
- https://leanpub.com/leprechauns — READ (table of contents)
- https://modelviewculture.com/pieces/the-making-of-myths — READ-FULL
- https://gist.github.com/Morendil/ebfa32d10528af04e2ccb8995e3cb4a7 — READ-FULL
- https://gwern.net/leprechaun — READ-FULL
- https://gwern.net/tank — READ-FULL
- https://arxiv.org/pdf/cond-mat/0212043 — READ-FULL
- https://arxiv.org/pdf/cond-mat/0401529 — READ-FULL
- https://ideas.repec.org/a/spr/scient/v101y2014i3d10.1007_s11192-014-1275-x.html — READ-PARTIAL
- https://direct.mit.edu/qss/article/2/4/1144/107356 — BLOCKED; S2 API abstract READ-PARTIAL
- https://pmc.ncbi.nlm.nih.gov/articles/PMC5629243/ — READ-FULL
- https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2714656/fullTextXML — READ-FULL
- https://pure.uva.nl/ws/files/72827566/25152459211040837.pdf — READ-FULL
- https://doi.org/10.1177/17456916211072525; 10.1126/sciadv.abd1705; 10.1177/1745691612460688; 10.7717/peerj.1364; 10.1371/journal.pone.0184727; 10.1016/j.respol.2018.07.019; 10.1002/job.125; 10.1177/0306312714535679 — abstracts via OpenAlex/S2, READ-PARTIAL
- https://harzing.com/download/failurerates.pdf — READ-PARTIAL
- https://harzing.com/blog/2016/04/are-referencing-errors-undermining-our-scholarship-and-credibility — READ-FULL
- https://forrt.org/replication-hub/, /flora-zotero/, /flora-replication-atlas/ — READ-FULL
- https://curatescience.org — READ-PARTIAL
- https://www.govinfo.gov/content/pkg/GPO-WMD/pdf/GPO-WMD.pdf — READ-PARTIAL
- https://www.dni.gov/files/documents/ICD/ICD-206.pdf — READ-PARTIAL (page images)
- https://pure.mpg.de/rest/items/item_2102238/component/file_2102237/content — READ-FULL
- https://quoteinvestigator.com/about/ — READ-FULL
- https://en.wikipedia.org/wiki/Wikipedia:List_of_citogenesis_incidents — READ-PARTIAL
- https://journals.sagepub.com/doi/full/10.1177/0306312714535679 — BLOCKED