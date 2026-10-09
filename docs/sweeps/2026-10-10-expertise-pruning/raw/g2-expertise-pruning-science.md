<!-- G2 expertise during search + pruning (agent output, 2026-10-10) -->

## Findings

**E1: does judgment get better as a search goes on?**

F1. Judging gets sharper as the searcher's picture of the task gets clearer. In longitudinal studies of students writing research proposals, the ability to tell relevant from irrelevant improved as the task took shape. Early on, students accepted references that matched what they expected to find. By the end they were more critical.
- who: Vakkari & Hakala (Tampere). 11 students, IR searches at the start, middle and end of a term. Serola & Vakkari: 22 psychology undergraduates searched at the start and end of a seminar. Academics, nothing to sell.
- evidence: "The more structured the task in the process, the more able the person is to distinguish between relevant and other sources. The relevance criteria of documents changed more than the criteria of references" — doi.org/10.1108/EUM0000000007127, abstract via api.openalex.org (2026-10-10; READ-PARTIAL, abstract only; full text BLOCKED). Also: "the students tended to accept references according to their expectations… At the end of the task, students became more proficient at recognizing the utility and topicality of references. They also became more critical" — doi.org/10.1002/asi.20113, via OpenAlex (READ-PARTIAL).
- bears on: E1 yes, C1, K1, K12
- limit: Small samples (11 and 22) of students, not experts. Nobody went back to re-judge the documents they had admitted early.

F2. The same expert, re-judging later, disagrees with himself. The work is caught by a blind re-review, not by trusting the first pass. A state archivist classified 401,960 emails. He then re-reviewed blind a stratified sample of 2,798, after wash-out periods of two years and then two months, and disagreed with himself on 901. A third blind review settled those cases. Measured against it, his original manual pass reached recall 0.89–0.98 and precision 0.75–0.91.
- who: Cormack & Grossman (Waterloo), SIGIR 2017. The authors build technology-assisted review (TAR) methods, so the paper argues for their own approach.
- evidence: "Roger re-reviewed blind a stratified sample of 2,798 documents (the 'Roger II' assessments). As the ultimate arbiter of truth, Roger reviewed blind, for a third time, all 901 cases of disagreement between Roger I and Roger II" — static.aminer.org/pdf/20170130/pdfs/sigir/ixea6i3mgbz9ms0ugkwtuposjchxq8rn.pdf (2026-10-10; READ-FULL)
- bears on: E1 (going back to re-assess), K8, K11 (judgment checked independently)
- limit: The sample was stratified, so 901/2,798 is not a population error rate. The final arbiter was the same person.

F3. Against "later is better": judgments drift and stick over time. Across TREC collections, assessors judged 15–24% of duplicate document pairs inconsistently. The inconsistent pairs were judged further apart in time (wt10g: 457 vs 207 documents between them; gov2: 213 vs 131; p<0.01). A similar document seen shortly before acted as a reminder and kept the judgments consistent. Assessors also showed inertia: on gov2, a "relevant" label followed a relevant one 42% of the time against a 20% base rate.
- who: Scholer, Turpin & Sanderson (RMIT/Melbourne), SIGIR 2011.
- evidence: "assessors were not always clear on the criteria used to judge a document and that such criteria were either forgotten, or alternatively that an assessor's view of what constituted relevance shifted over time" — marksanderson.org/files/papers/sigir2011-scholer.pdf (2026-10-10; READ-FULL)
- bears on: E1 against, K8, K14
- limit: Paid assessors, not researchers. The authors infer time from qrels order.

F4. The first documents set the bar for everything after them, in people and in LLMs.
- Threshold priming: participants who first saw only non-relevant documents later gave significantly higher relevance scores.
- Hedging: in Eisenberg & Barry, documents shown first in high-to-low order were underrated.
- Fatigue: Huang & Wang found no order effect at 75 documents, which the authors guessed was exhaustion.
- LLMs: GPT-3.5, GPT-4 and LLaMa2 showed the same priming.
- Ordering by priority makes assessors favour "popular" documents.
- who: Scholer, Kelly et al., SIGIR 2013. Chen, Liu, Sakai et al., arXiv 2409.16022. Sakai, Tao & Zeng, arXiv 2211.00981, from a dataset of 259,000 labels.
- evidence: "participants exposed to only non-relevant documents in the prologue assigned significantly higher average relevance scores to prologue and epilogue documents" — doi.org/10.1145/2484028.2484090 via OpenAlex (READ-PARTIAL). "LLMs tend to give lower scores to later documents if earlier ones have high relevance, and vice versa, regardless of the combination and model used" — arxiv.org/pdf/2409.16022 (READ-FULL). "The PRI strategy tends to make the assessor favour 'popular' documents" — arxiv.org/pdf/2211.00981 (READ-FULL). All 2026-10-10. Eisenberg & Barry and Huang & Wang are reached only through Sakai's summary (ROUTER).
- bears on: E1, C4, K6, K13. Ordering by priority brings the popularity bias into relevance judgments.
- limit: Sakai found that the agreement difference between random and priority ordering is "probably of no practical significance".

F5. Seeing evidence one piece at a time strengthens confirmation bias, and searching is sequential by nature. After a preliminary decision, people seeing information one item at a time picked a supporting-minus-conflicting margin of M = 2.33. People shown everything at once picked M = 0.78. The cause was presentation one at a time, not processing one at a time, and it worked through heightened commitment.
- who: Jonas, Schulz-Hardt, Frey & Thelen, JPSP 2001 (cited 676 times per the PDF's cover page).
- evidence: "an even stronger preference for supporting information arises if information is presented and processed sequentially instead of simultaneously" — moodle2.units.it/…/Jonas et al., 2001….pdf (2026-10-10; READ-FULL)
- bears on: E1, C1 (the cost of accretion), C5, K7
- limit: Lab decisions involving students.

F6. Prior belief steers what searchers click. They update a little, and they never got better as more came in. Pre-search belief correlated with the stance of the clicked caption at r = 0.8112. Beliefs changed in 66.7% of tasks, but 66.9% of those changes were ≤20 points. Evidence in the top half of a page produced an update 78.57% of the time, against 56.49% in the bottom half. In White's 2013 log study, about half of the answers searchers settled on were wrong. Lau & Coiera tested 227 students: anchoring (p<0.001) and order effects (p=0.026) were present. A de-biasing interface removed the order effect but did not significantly improve accuracy (p=0.23).
- who: White & Horvitz (Microsoft Research), TOIS 2015, with Cochrane reviews as ground truth. Lau & Coiera, JAMIA 2009.
- evidence: "a strong correlation between pre-search beliefs and the rating of the clicked caption (r = 0.8112, p < 0.001)" — erichorvitz.com/Belief_dynamics_retrieval.pdf (READ-FULL). "With use of the order debiasing interface, the initial order effect was no longer present (p = 0.34) but there was no significant improvement in decision accuracy (p = 0.23)" — Europe PMC PMC2605604 (READ-PARTIAL). Both 2026-10-10.
- bears on: E1, C5, K7, K14
- limit: Health yes/no questions answered by laypeople.

F7. Heuer, from the perception experiments: whoever starts early on fuzzy evidence is worse placed than someone who arrives late. He recommends "a fresh look at all the evidence" and rethinking from scratch, but admits there is no evidence that works. The 1973 Arab-Israeli War post-mortem blamed "incremental analysis".
- who: Richards Heuer, CIA, *Psychology of Intelligence Analysis*, drawing on Bruner & Potter 1964.
- evidence: "an analyst who starts observing a potential problem situation at an early and unclear stage is at a disadvantage as compared with others, such as policymakers, whose [first] exposure may come at a later stage" — and on rethinking from scratch: "[There] is no experimental evidence to show that this is possible or that it will work" — cia.gov/resources/csi/static/Pyschology-of-Intelligence-Analysis.pdf, lines ~1300–1320 and ~6520. The PDF text drops the "fi"/"Th" ligatures, so bracketed words are restored (2026-10-10; READ-FULL).
- bears on: E1, E2, K7
- limit: The finding comes from perception studies and is extrapolated to analysts.

F8. Prompting alternatives at the start helped; the same prompt after a leading hypothesis had formed did not. In an RCT with 297 GPs and 9 cases, a list of diagnoses shown before gathering information raised accuracy (OR 1.31, +6% absolute). The same list shown after a preliminary diagnosis did not (OR 1.10, n.s.), even though GPs could still change their answer. Related findings:
- Information distortion: physicians reinterpreted neutral cues to fit an early "steer", and 56% stayed committed after contrary cues. Physicians with more than 10 years in practice distorted less (1.04 vs 1.78).
- Psychiatrists who searched in a confirmatory way gave a wrong diagnosis 70% of the time, against 27% for those who searched disconfirmingly.
- who: Kostopoulou et al., BJGP 2015 and MDM 2012. Mendel et al., Psychological Medicine 2011.
- evidence: "Early support significantly improved diagnostic accuracy over control (odds ratio [OR] 1.31…), while late support did not (OR 1.10…)" — bjgp.org/content/bjgp/65/630/e49.full.pdf (READ-FULL). "Physicians with over 10 years in practice distorted less than their less experienced counterparts" — doi.org/10.1177/0272989x12447241 via OpenAlex (READ-PARTIAL). "Psychiatrists conducting a confirmatory search made a wrong diagnosis in 70% of the cases compared to 27% or 47%" — cambridge.org Psychological Medicine abstract page (READ-PARTIAL). All 2026-10-10.
- bears on: E1 (timing matters), E2, C2, C5, K7, K12, K17
- limit: Simulated cases.

F9. Experts judge sources better and question inconsistent evidence more, but they still mostly keep their first frame.
- Generalist evaluators "fall back on surface features such as keyword matching" on queries that need expertise.
- When feedback conflicted with their frame, expert designers looked for more information in 26.32% of events, against 6.11% for novices. But experts (56.7%) and novices (70.6%) mostly kept the original frame anyway.
- Most of 62 Dutch military analysts showed no confirmation bias.
- who: Kinney, Huffman & Zhai, CIKM 2008. Foong, Gergle & Gerber (Northwestern), 2017, n=21. Dhami et al., Cognitive Research 2024.
- evidence: "experts were more likely than novices to question the inconsistency, seeking critical information to expand their understanding of the design goals" — collablab.northwestern.edu/pubs/2017_Foong-Gergle-Gerber_Sensemaking-of-Feedback_PACMHCI-Final.pdf (READ-FULL). "the majority of 62 Dutch military analysts did not suffer from confirmation bias" — doi.org/10.1186/s41235-024-00560-y via OpenAlex (READ-PARTIAL). Both 2026-10-10.
- bears on: E1 (expertise helps the owner's filtering claim), K9, K17

F10. Searching more lowers precision but improves the final work. In 41 medical students' essays, effort spent expanding MeSH terms and exploring documents between sessions lowered precision but raised essay scores.
- who: Vakkari & Huuskonen, JASIST 2012.
- evidence: "effort in assessing and exploring documents in the result list between the sessions degraded precision, but led to better task outcome" — doi.org/10.1002/asi.21683 via OpenAlex (2026-10-10; READ-PARTIAL; Wiley full text BLOCKED)
- bears on: E1, C1, K1

**E2: pruning**

P1. Pruning too early and too late both failed, and both were measured. In a simulated operating-room crisis with 39 anesthesiology residents:

| Mode | Residents | Diagnoses considered | Treatment steps per diagnosis | Resolved the airway problem |
|---|---|---|---|---|
| Fixated (pruned alternatives too early) | 11 (28%) | 3.8 | 2.0 | 0 |
| Vagabonds (never committed to test any) | 17 (44%) | 6.1 | 1.5 | 0 |
| Adaptive | 9 (23%) | 5.0 | 3.6 | 7 |

Two more residents (5%) stalled.

The adaptive residents held several hypotheses and acted on each one long enough to test it.
- who: Rudolph, Morrison & Carroll (Harvard/MIT/Boston College). This is their own conference deck; the paper is AMR 2009.
- evidence: Table "Problem Solving Modes in Source Data": "Subjects who resolved the airway problem 0 0 0 7 … ChiSq(3) = 28.4***"; their model labels: "Fixating … Overconfident in proposed diagnosis" and "Diagnostic Vagabonding … Cautious to take action" — proceedings.systemdynamics.org/2012/proceed/papers/P1523.pdf (2026-10-10; READ-FULL)
- bears on: E2, K8, K12

P2. Pruning alternatives too early was the single most common cognitive cause of diagnostic error, and missing knowledge was rare. In 100 internal-medicine error cases, cognitive factors contributed in 74%.
- who: Graber, Franklin & Gordon, Arch Intern Med 2005 (cited 1,550 times).
- evidence: "Premature closure, ie, the failure to continue considering reasonable alternatives after an initial diagnosis was reached, was the single most common cause… Faulty or inadequate knowledge was uncommon." — doi.org/10.1001/archinte.165.13.1493 via OpenAlex (2026-10-10; READ-PARTIAL)
- bears on: E2, C5, K17 ("information is the smallest lever")

P3. Working scientists discard anomalies or act on them depending on timing and centrality. In four lab meetings there were 70 findings: 22 expected, 18 unexpected, 30 exploratory. 8 of 10 inconsistent unexpected findings led to new hypotheses, and the group interacted 176 times over unexpected findings against 23 over expected ones. Anomalies that came early and touched only an auxiliary hypothesis were ignored. Late anomalies were attended to either way.
- who: Kevin Dunbar (McGill), from in-vivo recordings of molecular-biology labs.
- evidence: "when the unexpected finding occurs early and it is not a core hypothesis, the scientists ignore it… When the unexpected finding occurs late in the research project the scientist will attend to it regardless" — chunk.cc.gatech.edu/AY2013/cs7601_spring/papers/Dunbar.pdf (2026-10-10; READ-FULL)
- bears on: E1, E2, C3, C6 (group reasoning), K11
- limit: The timing analysis is described as "recently… conducting"; no counts are given for it.

P4. When people persist with a failing course, the driver is how strongly they held the initial belief, not personal involvement. Escalation came from "improper use of initial positive beliefs in the face of negative new information"; involvement in the original decision "is not a necessary condition". The authors' explanation implies that a new decision-maker who inherits the old belief would not prune either; that is my inference, not tested in the paper.
- who: Biyalogorsky, Boulding & Staelin, J Marketing 2006.
- evidence: doi.org/10.1509/jmkg.70.2.108 via OpenAlex (2026-10-10; READ-PARTIAL)
- bears on: E2, K11 (hand judgment to someone else)

P5. Abandoning a whole frame has a measured cost: the pivot penalty. Across about 26M papers and 1.72M patents:
- The lowest-pivot papers were high-impact 7.4% of the time; the highest-pivot papers 2.2% (base rate 5%).
- After a forced prune, the retraction of a paper they had built on, 164,988 researchers pivoted 2.5% more and lost 0.4% in hit rate. Heavier users of the retracted paper pivoted 3.7% more and lost 0.7%.
- who: Hill, Yin, Stein, Wang, Wang & Jones, Nature 2025.
- evidence: "The lowest-pivot work had high impact 7.4% of the time… whereas the highest-pivot work had high impact only 2.2% of the time" — kellogg.northwestern.edu/faculty/jones-ben/htm/The Pivot Penalty in Research.pdf (2026-10-10; READ-FULL)
- bears on: E2 against "delete old graphs" freely, C3, K5
- limit: The study measures where researchers moved, not why. Impact is measured by citations.

P6. Fields drop a frame when its holder leaves. After a star life scientist's premature death, outsiders' articles flowed into the field, drew on "a different scientific corpus" and were "disproportionately likely to be highly cited".
- who: Azoulay, Fons-Rosen & Graff Zivin, AER 2019.
- evidence: "outsiders appear reluctant to challenge leadership within a field when the star is alive" — doi.org/10.1257/aer.20161574 via OpenAlex (2026-10-10; READ-PARTIAL)
- bears on: E2, C4, K6

P7. Literatures fail to prune retracted work, and higher-quality reviewers prune more. Of 324 citations to retracted papers in 286 pharmacy evidence syntheses, only 20.4% noted the retraction. High-quality syntheses were more likely to cite them negatively.
- who: Systematic Reviews 2023.
- evidence: "high-quality evidence syntheses were more associated with negative citation of retracted publications" — doi.org/10.1186/s13643-023-02316-z, Europe PMC abstract (2026-10-10; READ-PARTIAL)
- bears on: E2, E1 (quality tracks pruning), K6

## Against the claims

- Accretion has costs. Judgments drift and stick as a search goes on (F3). Taking evidence in sequence amplifies confirmation bias (F5). Starting early on fuzzy evidence is a handicap (F7). This bears on C1 and the owner's "the more you know, the easier".
- More information raised confidence, not accuracy. In Oskamp's 1965 study, psychologists did no better than undergraduates, and after the fourth part of the case "more than 90 percent of Oskamp's subjects were overconfident" — web.csulb.edu/~cwallis/382/certainty/chapter19.html (Plous textbook, ROUTER; primary not reached). Tsai, Klayman & Hastie 2008: "their confidence increases more than their accuracy" — ideas.repec.org/a/eee/jobhdp/v107y2008i2p97-105.html (READ-PARTIAL). This is K7's Heuer point, now with primaries.
- Expertise does not cure frame lock. Expert chess players said they were looking for a better solution while their eyes stayed on features of the one they had already found (Bilalić et al., doi 10.1016/j.cognition.2008.05.005, Europe PMC abstract, READ-PARTIAL). Experienced analysts still showed confirmation bias, and the structured hypothesis method (ACH) reduced it only in participants without analysis experience (Lehner et al. 2008, doi 10.1109/TSMCA.2008.918634, READ-PARTIAL).
- Moving far from one's base is penalised (P5), which tempers "delete old graphs".
- Late correction does not take (F8). Re-assessing at the end is weaker than widening at the start.

## Not covered by any claim

- **Calibrate before judging instead of re-judging after.** Cochrane: "pilot test the eligibility criteria on a sample of reports (say six to eight articles…)" — training.cochrane.org/handbook/current/chapter-04 (READ-FULL). Scholer 2013: expose assessors to "multiple relevance levels early". Kostopoulou: show the alternatives first.
- **Re-adjudicate a blind sample of your own early labels** (F2). This is quality control by disagreement, not re-reading everything.
- **Reminder documents keep judgments consistent.** Seeing a near-duplicate shortly before keeps the criterion stable (F3; p = 0.008).
- **Review the evidence as a whole, not the day's take.** Heuer and the 1973 post-mortem; Jonas: showing everything at once halves the bias.
- **Commit-and-test is the pruning rule that worked** (P1). Neither "keep everything open" nor "settle early" did.

## Frontier

- Hogarth & Einhorn 1992 belief-adjustment model (cited 1,633 times). Order effects depend on response mode and series length. Abstract not retrieved.
- Contrast bias rather than confirmation bias in daily impression updating, BJSO (doi 10.1111/bjso.70123). A new challenge to anchoring.
- Klein et al. 2007 data/frame chapter, with a "garden path" study: not reached.
- Pontis & Blandford 2016, an empirical test of data/frame with researchers (UCL PDF, BLOCKED).
- Chinn & Brewer 1993 taxonomy of responses to anomalous data.
- Tolcott, Marvin & Lehner 1989, analysts' first hypotheses persisting: not reached.
- Wang & Soergel 1998 / Wang & White 1999: selection criteria recur at the reading and citing stages, plus 14 new ones (terpconnect.umd.edu/~whitemd/study_2_abs.html).
- Kangasrääsiö et al. 2016, a timeline UI that flags past relevance feedback likely to need revision (arXiv 1603.02609; simulation and small user study).
- Eickhoff et al. 2014 and Gadiraju et al. 2018 on knowledge gain within a session (abstracts only).
- Human overharvesting in patch foraging (Constantino & Daw 2015): no overstay claim found in the abstract; full text not reached.

## Lane state

- Vakkari line (journal.fi, trepo.tuni.fi): BLOCKED (Anubis and "Access Denied", also via silver). Abstracts READ through OpenAlex.
- Wiley full texts (asi.21683): BLOCKED (Cloudflare 403, also via silver).
- MITRE 04_0985 report and publication page: BLOCKED (Akamai 403, also via silver). Lehner 2008 abstract READ.
- Tsai 2008 on SSRN: BLOCKED. IDEAS abstract READ.
- Kuhlthau 1991: MISSING at unc.edu (404); Rutgers mirror returned HTML. Already in K8/K12, so not pursued.
- Brand-Gruwel 2005 (OU repository PDF): returned HTML, BLOCKED.
- Trickett, Trafton & Schunn (Pitt LRDC): BLOCKED.
- Pontis & Blandford (UCL): BLOCKED.
- Europe PMC full text for Azoulay and Constantino: EMPTY (150-byte response).
- Screening order and fatigue effects inside systematic reviews: EMPTY after two searches. No study measured whether screening accuracy rises or falls across the screening sequence, and no study was found on re-screening early records after criteria change. This is a gap.
- Oskamp 1965 primary: not reached; reached only through the Plous ROUTER.

## Source register (all fetched 2026-10-10)

- proceedings.systemdynamics.org/2012/proceed/papers/P1523.pdf — READ
- arxiv.org/pdf/2211.00981 — READ
- arxiv.org/pdf/2409.16022 — READ
- arxiv.org/pdf/1603.02609 — READ
- moodle2.units.it/…/Jonas et al., 2001….pdf — READ
- cambridge.org Mendel 2011 abstract page — READ-PARTIAL
- terpconnect.umd.edu/~whitemd/study_2_abs.html — READ
- bjgp.org/content/bjgp/65/630/e49.full.pdf — READ
- static.aminer.org/…/ixea6i3mgbz9ms0ugkwtuposjchxq8rn.pdf (Roger & Me) — READ
- marksanderson.org/files/papers/sigir2011-scholer.pdf — READ
- collablab.northwestern.edu/…Foong…pdf — READ
- chunk.cc.gatech.edu/AY2013/cs7601_spring/papers/Dunbar.pdf — READ
- erichorvitz.com/Belief_dynamics_retrieval.pdf — READ
- kellogg.northwestern.edu/…/The Pivot Penalty in Research.pdf — READ
- cia.gov/resources/csi/static/Pyschology-of-Intelligence-Analysis.pdf — READ
- training.cochrane.org/handbook/current/chapter-04 — READ
- training.cochrane.org/handbook/current/chapter-03 — READ-PARTIAL
- web.csulb.edu/~cwallis/382/certainty/chapter19.html — READ (ROUTER)
- ideas.repec.org/a/eee/jobhdp/v107y2008i2p97-105.html — READ-PARTIAL
- api.openalex.org abstracts by DOI or search (Vakkari & Hakala 2000; Vakkari 2001; Pennanen & Vakkari 2003; Serola & Vakkari 2004; Vakkari & Huuskonen 2012; Kostopoulou 2012; Graber 2005; Lehner 2008; Kinney 2008; Scholer 2013; Scholer 2011; Bailey 2008; Gadiraju 2018; White 2013; Eickhoff 2014; White & Horvitz 2015; Biyalogorsky 2006; Azoulay 2019; Dhami 2024; Wang 2020) — READ-PARTIAL
- ebi.ac.uk/europepmc abstracts (Lau & Coiera 2009; Gartlehner 2020; Hanegraaf 2024; Bilalić 2008; contrast-bias 2026; retracted-citations 2023; Constantino & Daw 2015) — READ-PARTIAL
- journal.fi; trepo.tuni.fi; onlinelibrary.wiley.com; mitre.org; papers.ssrn.com; discovery-pp.ucl.ac.uk; ils.unc.edu; tefkos.rutgers-sci.domains; research.ou.nl; lrdc.pitt.edu; link.springer.com (Constantino) — BLOCKED or MISSING
