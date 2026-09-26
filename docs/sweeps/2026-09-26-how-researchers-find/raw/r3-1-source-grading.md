<!-- AGENT OUTPUT — R3-1 source grading, integrity, data voids. Returned by a subagent, not read by the chair unless a row says so. -->

## Findings

F1. **Lateral reading.** Fact-checkers leave an unfamiliar page within about 30 seconds and look the source up somewhere else, usually Wikipedia first. They also practise "click restraint": they scan the whole results page before choosing a result. **Extends K9**, whose filters are all read-first; this one reads *about* the source instead of reading the source. It also **qualifies K10**: a historian who went straight to the primary court brief never found who paid for the case.
    who: Wineburg (Stanford) and McGrew. They develop curricula, so they are grading their own method.
    evidence: "Fact checkers, in short, learned most about a site by leaving it." On the American College of Pediatricians task, checkers scored 2/2, historians 0.7 and students 0.16. Checkers left the landing page after a mean of 32 s; historians took 88 s and students 100 s. On minimumwage.com, checkers took 51 s to find the funder EPI, historians 3 min 40 s and students 5 min 18 s. All 10 checkers traced EPI to Berman & Co.; 6 historians and 40% of students did. 7 of 10 historians took the page's reference list as proof of legitimacy. — https://stacks.stanford.edu/file/druid:yk133ht8603/Wineburg%20McGrew_Lateral%20Reading%20and%20the%20Nature%20of%20Expertise.pdf (2026-09-26; READ-FULL)
    bears on: Q2, Q5; C4
    limit: 10 people per expert group; the authors write "Small sample sizes exaggerate differences". On the Vergara task students were fastest (1:42 against the checkers' 2:08) but scored lower (2.3 against 3.6). When one historian searched the organisation's name, she got "an entire page of results issued by the very organization she was trying to investigate". So lateral reading fails when the source controls its own search results.

F2. **Lateral reading can be taught, and confidence does not track it.** **Extends K14**: agents ignore credibility cues, and untrained humans do too.
    who: Breakstone, Wineburg et al. (Stanford); Brodsky, Caulfield et al.
    evidence: "At pretest, only 3 of 87 students engaged in lateral reading … At posttest, 67 of 87 did so" (four one-hour modules) — https://misinforeview.hks.harvard.edu/article/lateral-reading-college-students-learn-to-critically-evaluate-internet-sources-in-an-online-course/ (READ-PARTIAL; 62 citations, 19,612 views). Brodsky 2021 (n=221): confidence "was only weakly associated with lateral reading" — doi 10.1177/23328584211038937, Crossref abstract (READ-PARTIAL). In a national sample of 3,446 high-school students, "96% never learned about the organization's ties to the fossil fuel industry" — doi 10.3102/0013189x211017495 (abstract). A district field study (271 treated vs 228 controls) found significant growth — https://eric.ed.gov/?id=EJ1372738 (abstract only, no effect size seen).
    bears on: Q2
    limit: these are the designers' own evaluations, on tasks with a known answer.

F3. **SIFT grades the claim apart from whoever carried it to you.** The four moves are Stop, Investigate the source, Find better coverage and Trace. "Find better coverage" means dropping the carrier and going to the best source on the claim itself. **Connects K9 with K7's "collapse the cascade."**
    who: Mike Caulfield (then WSU Vancouver, co-author of *Verified*). He sells a book and curricula, and now builds LLM prompts.
    evidence: "your best strategy may be to ignore the source that reached you, and look for trusted reporting or analysis on the claim"; "Taking sixty seconds to figure out where media is from before reading" — https://hapgood.us/2019/06/19/sift-the-four-moves/ (READ-FULL; 474 comments)
    bears on: Q2, Q5; C5
    limit: it assumes better coverage exists. F6 and F7 show where it does not.

F4. **Admiralty/NATO grading scores the source (A–F) and the information (1–6) separately. In practice people merge the two scales.** The doctrine explicitly protects the unknown source and the new fact. **Extends K6**: it is the only filter found that formally refuses to downgrade a source just because it has no history.
    who: US Army FM 2-22.3, Appendix B. Kelly, Budescu, Dhami and Mandel (Defence R&D Canada) tested how people apply it.
    evidence: "An 'F' rating does not necessarily mean that the source cannot be trusted, but that there is no reporting history". A "1" needs confirmation "by other independent sources" — https://r.jina.ai/https://irp.fas.org/doddir/army/fm2-22-3.pdf (READ-PARTIAL, Appendix B). In practice people "most often assign codes that fall along the diagonal such that source reliability and information credibility align perfectly" (Baker 1968, as cited). "trustworthiness ratings depended more on source reliability than on information credibility". The 74 analysts performed like the 175 non-experts — https://www.cambridge.org/core/services/aop-cambridge-core/content/view/E67548E8010A47345C3439D45D9EC6B3/S1930297525100077a.pdf/… (READ-PARTIAL: intro and discussion)
    bears on: Q2; C4
    limit: the stimuli had no raw intelligence attached. Samet (1975), where participants did see content, found credibility weighted more heavily. Baker (1968) and Miron (1978) are cited second-hand.

F5. **The funder is its own axis, and method-quality tools miss it.** **Connects F4 to K9's post-read filters.**
    who: Lundh et al., Cochrane MR000033 (2017), 75 papers. One author has been an expert witness against a drug maker (their COI statement).
    evidence: industry-sponsored studies had favourable efficacy results more often (RR 1.27) and favourable conclusions more often (RR 1.34). They were also *more* often low risk of bias from blinding (RR 1.25). "Our analyses suggest the existence of an industry bias that cannot be explained by standard 'Risk of bias' assessments." — PMID 28207928, efetch abstract (READ-PARTIAL)
    bears on: Q2
    limit: the review rates its own evidence low to moderate.

F6. **Searching to check a false claim made people believe it more, because the search landed in a data void.** **Contradicts the naive form of C5. Connects K14** (SealQA: search lowers accuracy and raises confidence) **with K5**: searching in the claim's own words is the vocabulary trap run backwards.
    who: Aslett, Sanderson, Godel, Persily, Nagler, Bonneau, Tucker (NYU), *Nature* 2024. Nothing to sell.
    evidence: being encouraged to search raised the chance of rating a false article true by 0.057, "a 19% increase" (n=2,275). "A total of 77% of search queries that used the headline or URL of a false/misleading article as a search query return at least one unreliable news link among the top ten results", against 21% for other queries — https://www.nature.com/articles/s41586-023-06883-y (READ-PARTIAL)
    bears on: Q2, Q5; C4, C5
    limit: reliability was judged by NewsGuard scores; articles were fresh (a breaking-news void); the analysts were not blinded.

F7. **Data voids: where nobody searches, whoever prepared content in advance wins. The practitioner's counter is to predict which sources should appear.** **Extends K7** (predict the record that should exist), applied here to the results page. **Extends K5 in reverse**: the planted term is by definition not the field's own vocabulary.
    who: Golebiewski (Microsoft Bing) and boyd (Data & Society, Microsoft Research). Their employer runs a search engine. Caulfield wrote the counter-procedure.
    evidence: "Data voids are difficult to detect. Generally speaking, data voids are not a liability until something happens that results in an increase of searches on a term." The report names five types: breaking news, strategic new terms, outdated terms, fragmented concepts, problematic queries. Manipulators want people to "encounter the web of information that they have produced … before those data voids are cleaned up." No measurements: the examples are "intentionally, fairly innocuous" — https://datasociety.net/wp-content/uploads/2019/11/Data-Voids-2.0-Final.pdf (READ-FULL). Caulfield: "Kalergi, of course, is historically real. But he is also a historical figure of little note and no current influence. As such, there isn't much writing on him, except … by those who have put him at the center"; people who form expectations of what should appear "are more likely to reanalyze search terms when those expectations are violated" — https://hapgood.us/2019/04/12/data-voids-and-the-google-this-ploy-kalergi-plan/ (READ-FULL)
    bears on: Q2, Q3; C4
    limit: the procedure needs a searcher who already knows what a good results page looks like, which is expertise the searcher may not have.

F8. **Wikipedia's rule for telling fringe from notable is independence from the claim's own sourcing ecosystem.** It says outright that it will not correct for neglect. **Limits K15** (Swanson's neglect markers).
    who: the Wikipedia community guideline WP:FRINGE (revision of 2026-06-25).
    evidence: use "reliable sources that are outside the sourcing ecosystem of the fringe theory itself". "Care should be taken not to mislead the reader by implying that, because the claim is actively disputed by only a few, it is otherwise supported." Its cost: "not a forum for presenting new ideas, for countering any systemic bias in institutions such as academia, or for otherwise promoting ideas which have failed to merit attention elsewhere" — https://en.wikipedia.org/w/index.php?title=Wikipedia:Fringe_theories&action=raw (READ-FULL, raw wikitext)
    bears on: Q2; C4
    limit: the same rule shuts out Smalheiser's "penumbra".

F9. **Fake popularity is caught through the behaviour of the people giving the signal, not by judging the thing they promote.** **Extends K16** (curators manufacture popularity) **and updates KNOWN's fake-stars row**: v2 of the paper reports six million suspected fake stars, not 4.5 million.
    who: He, Kästner, Vasilescu et al. (CMU, ICSE '26). **Co-author Burckhardt works at Socket Inc, which sells alerts built on this detector.** Also Keller, Schoch, Stier and Yang; Schoch et al. (*Sci Rep* 2022).
    evidence: fake-star accounts "must be either newly-registered throw-away accounts or have been synchronously starring repositories in short time windows". The detector caught "688 (81.23%) of the 847 repositories and 11,903 (75.95%) of the 15,672 involved GitHub accounts" in one confirmed malware campaign. 90.42% of flagged repositories were later deleted, against a 5.03% baseline. Fake stars help "in the short term (i.e., less than two months) and become a liability in the long term" — https://arxiv.org/pdf/2412.13459 (READ-PARTIAL). On astroturfing: "Using bot detection to study astroturfing betrays a fundamental conceptual mismatch: … not all astroturfing accounts are bots" — https://pure.manchester.ac.uk/ws/files/128397468/Astroturfing_Kelleretal_2019.pdf (READ-PARTIAL). "On average, 74% of the involved accounts in each campaign engaged in … co-tweeting and co-retweeting". In the US case, "more than 80 per cent" of campaign accounts were detected with "around 1 per cent" false positives — https://www.nature.com/articles/s41598-022-08404-9 (READ-PARTIAL)
    bears on: Q2; C4
    limit: validation may be circular: "Twitter might have used similar techniques for detecting astroturfers in the first place." The star cutoffs (50) are heuristics.

F10. **Mechanical checks on summary statistics have measured hit rates. They catch far less than checks on raw data.** **Extends K10** (raw data is where rare information lives) **and K16** (Bik connects fraud across papers).
    who: Brown and Heathers (GRIM, SPRITE; no funding); van der Zee, Anaya and Brown; Carlisle (anaesthetist and *Anaesthesia* editor).
    evidence: GRIM could be applied to 71 of 260 articles. Of those, "around half (N = 36; 50.7%) appeared to contain at least one reported mean inconsistent". Datasets came back for 9 of 21 requested, and all 9 had errors — https://r.jina.ai/https://peerj.com/preprints/2064/ (READ-PARTIAL). Four Wansink papers had "approximately 150 inconsistencies … from the reported statistics alone" — doi 10.7287/peerj.preprints.2748v1. Carlisle 2017 (5,087 RCTs): at a 1-in-10,000 threshold his test flagged 8 of 72 retracted trials (11%) and 82 of 5,015 unretracted ones (1.6%). Grouping trials by author exposed Boldt, Fujii and Reuben, plus 21 more authors — PMID 28580651. Carlisle 2021 on submissions: with individual patient data 67 of 153 (44%) were false; without it, 6 of 373 (2%) — PMID 33040331 (both READ-PARTIAL)
    bears on: Q2, Q3
    limit: honest error and stratified allocation also produce flags. The Kharasch & Houle critique (PMID 28825936) was BLOCKED.

F11. **Paper-mill detection works by snowballing on words that deviate from the field's vocabulary. The venue's impact factor rose while its integrity fell.** **Extends K1** (accretion used as a detector), **K5** (vocabulary deviation as a red flag) **and K6** (impact factor).
    who: Cabanac, Labbé and Magazinov (2021).
    evidence: tortured phrases were found "at first by chance and then by snowballing with already identified terms". "Out of 404 papers accepted in less then 30 days after submission, 394 papers (97.5%) have authors with affiliations in (mainland) China." "Its Journal Impact Factor increased from 0.471 to 1.161 over 2015–2019, that is a 146% increase" — https://arxiv.org/pdf/2107.06751 (READ-PARTIAL)
    bears on: Q2; C4
    limit: "Without any definitive proof"; the paper is a call for investigation.

F12. **Retraction status has to be checked by a tool, because citers almost never mention it.** **Extends K6** (citing ≠ reading).
    evidence: "among the 13,252 postretraction citation contexts, only 722 (5.4%) citation contexts acknowledged the retraction" — Crossref abstract of doi 10.1162/qss_a_00155 (the publisher page was BLOCKED). Zotero's automatic check "covers about 3/4 of Retraction Watch data" (items with a DOI or PMID) — https://www.zotero.org/blog/retracted-item-notifications/ (READ-FULL, undated page)
    bears on: Q2

## Against the claims

- **C4, "sample the unpopular on purpose."** The low-traffic corner is exactly where adversaries prepare content (F6, F7), and fake popularity is aimed at low-signal items (F9). The standard defence, independence from the claim's own sourcing ecosystem (F8), also excludes the genuinely neglected, and says so. **No source I reached gives a *measured* procedure for telling a neglected-but-real source from a planted one.** Three discriminators are documented:
  - (a) independent sources outside the ecosystem (F8, and F1's "who is behind this");
  - (b) coordination or throwaway-account signatures among the people producing the signal (F9);
  - (c) predicting which kinds of source ought to appear, and noticing when they do not (F7).
  Swanson's markers (K15) worked inside MEDLINE, which is peer-review-gated. F10 and F11 show that gate is itself manufactured at measurable rates (44% false in Carlisle's submissions that came with individual patient data).
- **C5.** Hunting counter-evidence by web search raised belief in false claims (F6). A claim with few rebuttals is not thereby supported (F8).
- **C1 / K10.** In credibility judgement, depth hurt. Historians who read closely or went to the primary document lost to checkers who "read less" (F1). SIFT's "Stop" move exists to cut off rabbit-hole accretion (F3).

## Not covered by any claim

- **Two axes, then watch them merge.** The source and the claim are graded separately: Admiralty, SIFT's "find better coverage", Lundh's funder axis. Measured humans, analysts included, collapse the two onto the diagonal (F4).
- **The results page as an instrument.** Click restraint (the "information neighborhood") and predicting what should appear: what a results page contains is itself evidence (F1, F7).
- **Judge the people giving the signal, not the thing signalled** (F9).
- **Obtain raw data before trusting a summary-level check** (F10: 44% against 2%).

## Frontier

- Caulfield's "Deep Background" prompt (March 2025): SIFT encoded as an LLM prompt that "searches for conflicting sources … and produces structured reports with … source assessments". The practitioner has already ported the method to agents — https://checkplease.neocities.org/
- Icard's 3×3 grid (honesty of source × truth of content), and Mandel & Irwin's proposal to crowdsource information evaluation — Kelly et al., §7.
- SourceWatch, the fact-checkers' lateral destination for front groups; Daniels (2009) "cloaked websites" — Wineburg & McGrew.
- Tripodi (2018) "Searching for Alternative Facts": fragmented vocabularies as a data-void type — cited in the Data Voids report.
- Socket's supply-chain alerts on repositories with fake stars: 283 of 2 million customer software bills of materials flagged — fake-stars paper §5.3.
- NewsGuard used as the quality oracle in Aslett. It is itself a graded source list.

## Lane state

- Wineburg & McGrew (Stanford PDF): READ-FULL. The *Verified* book: not reached (paywalled). "Check, Please!" course: MISSING; only the projects page resolved.
- SIFT post and Kalergi post: READ-FULL. The first Kalergi URL was 404; the correct one was found by search.
- FM 2-22.3: irp.fas.org and fas.org returned 202 with an empty body; marines.mil returned 403; r.jina.ai worked. AJP-2.1 was not reached directly; its table was seen via Kelly et al.
- Irwin & Mandel 2019 (paywalled; ResearchGate): not fetched.
- GRIM and SPRITE: PeerJ returned 403 to curl; r.jina.ai worked.
- Carlisle 2017 and 2021, Lundh 2017: NCBI eutils abstracts. Kharasch & Houle: BLOCKED.
- Cabanac et al. and He et al. on arXiv: READ-PARTIAL. The fake-stars paper is now v2 (ICSE '26).
- Hsiao & Schneider: publisher returned 403, r.jina.ai returned nothing, Semantic Scholar returned 429; the Crossref abstract worked.
- Keller (Manchester PDF) and Schoch (Nature): READ-PARTIAL.
- A search for a critique of lateral reading's dependence on consensus: EMPTY, nothing citable found.

## Source register

- https://stacks.stanford.edu/file/druid:yk133ht8603/Wineburg%20McGrew_Lateral%20Reading%20and%20the%20Nature%20of%20Expertise.pdf — READ-FULL
- https://hapgood.us/2019/06/19/sift-the-four-moves/ — READ-FULL
- https://hapgood.us/2019/04/12/data-voids-and-the-google-this-ploy-kalergi-plan/ — READ-FULL
- https://checkplease.neocities.org/ — READ-PARTIAL
- https://misinforeview.hks.harvard.edu/article/lateral-reading-college-students-learn-to-critically-evaluate-internet-sources-in-an-online-course/ — READ-PARTIAL
- https://eric.ed.gov/?id=EJ1372738 — READ-PARTIAL (abstract)
- Crossref: 10.1177/23328584211038937, 10.3102/0013189x211017495, 10.1162/qss_a_00155, 10.7287/peerj.preprints.2748v1 — abstracts
- https://datasociety.net/wp-content/uploads/2019/11/Data-Voids-2.0-Final.pdf — READ-FULL
- https://www.nature.com/articles/s41586-023-06883-y — READ-PARTIAL
- https://r.jina.ai/https://irp.fas.org/doddir/army/fm2-22-3.pdf — READ-PARTIAL
- Kelly et al., JDM 2025 (Cambridge PDF, above) — READ-PARTIAL
- https://en.wikipedia.org/w/index.php?title=Wikipedia:Fringe_theories&action=raw — READ-FULL
- https://arxiv.org/pdf/2412.13459 — READ-PARTIAL
- https://pure.manchester.ac.uk/ws/files/128397468/Astroturfing_Kelleretal_2019.pdf — READ-PARTIAL
- https://www.nature.com/articles/s41598-022-08404-9 — READ-PARTIAL
- https://r.jina.ai/https://peerj.com/preprints/2064/ and …/26968/ — READ-PARTIAL
- PubMed 28580651, 33040331, 28207928, 28825936 — abstracts / BLOCKED
- https://arxiv.org/pdf/2107.06751 — READ-PARTIAL
- https://www.zotero.org/blog/retracted-item-notifications/ — READ-FULL

Raw text of everything above is saved in /private/tmp/claude-501/-Users-seventyleven-Desktop/fcd46374-4e61-45da-ae77-538c40287f4b/scratchpad/r3/ (e.g. wmc.txt, dvc.txt, mandelc.txt, fsc.txt, klc.txt, tcc.txt).