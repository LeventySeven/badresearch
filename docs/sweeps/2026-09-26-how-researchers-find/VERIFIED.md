# Chair verification log

Every ✔ in `KNOWN.md`, `FINDINGS.md` and the design spec is one of these rows: the chair (not a reader)
fetched or opened the source on 2026-09-26 and found the span in the bytes with `grep`/`pdftotext`. A
row not listed here is agent-read — its span is in `raw/`, unchecked by the chair.

| # | claim | source | what matched |
|---|---|---|---|
| 1 | old skill: 4 lenses, 2 loci analysts, depth-first sequential perspectives | `git show origin/main:src/bad_research/skills/bad-research-{2-width-sweep,4-loci-analysis,5-depth-investigation}.md` | lines 34–60, 87–100, 31–37 |
| 2 | STORM: 99.83 vs 39.56 unique references; equal number of questions | arxiv.org/pdf/2402.14207 | Table 5 row; "we control an equal total number of generated questions" |
| 3 | Kim et al.: 17.2×/4.4× trace-level; β=0.014, p=0.658; BrowseComp-Plus independent −35%, decentralized +9.2% (0.347 vs 0.318), centralized +0.2%; PlanCraft −39…−70% | arxiv.org/pdf/2512.08296 | lines 171, 215, 588–596, 690–700, 944–958 of the text dump |
| 4 | Kim code: first release passed `findings[:300]` between rounds; later rewritten to full-response debate | raw.githubusercontent.com/ybkim95/agent-scaling/{cbf8c10,6f3bfb7}/…/multiagent_decentralized.py | lines 24, 101; line 8 |
| 5 | Tao: "combining this one obscure technique that not many people know about with some other result in the literature." | dwarkesh.com/p/terence-tao | exact |
| 6 | Paine: bibliography "flip through it for 30 seconds"; "only goes back to Edgar Snow." | dwarkesh.com/p/sarah-paine, /p/sarah-paine-china | exact |
| 7 | Gwern: "Papers do not tell you where the ideas come from in a truthful manner."; "…that I don't even realize are connected." | dwarkesh.com/p/gwern-branwen | exact |
| 8 | Noam Brown: "Can they talk to each other? Usually the answer is no. That's very inefficient." | dwarkesh.com/p/noam-brown | exact |
| 9 | Hamming 10–20 problems; Schulman "reading the same literature" and "revisit my journal"; Nielsen "picking a dozen"; Vivek "bodies are buried"; Anthropic duplicate searches; Carlini ↔ differential cryptanalysis | ~/Desktop/guidesfm/research/{articles,x-guides}/… | lines 103; 62, 102; 124; 33; 51; 407 |
| 10 | Galen Adams (LLMs "want to find the perfect article"; "when do you stop?"); Karpathy's idea queue; Cursor fleet agents ignored each other; Heller's 20–50 queries | ~/Desktop/researchfms/Transcripts/TRANSCRIPTS_{AI2,KARPATHY,CURSOR,YC_ROOT_ACCESS}.md | 6037–6038, 6069–6070; 13531–13535; 1005; 13625 (caption notes) |
| 11 | Tao: sort citing papers by their own citations; Karnofsky: "Read the 1-3 most prominent pieces on each side, then go."; Keshav: "find shared citations and repeated author names" | terrytao.wordpress.com/career-advice/dont-be-afraid-…; cold-takes.com/learning-by-writing; ccr.sigcomm.org/online/files/p83-keshavA.pdf | exact |
| 12 | Greenhalgh & Peacock: 30% protocol, 51% snowballing, 24% personal; 1 per 40 min vs 1 per 15 min | pmc.ncbi.nlm.nih.gov/articles/PMC1283190 | exact |
| 13 | Bates: "Each new piece of information they encounter…"; 69% footnote chasing | pages.gseis.ucla.edu/faculty/bates/berrypicking.html | exact |
| 14 | Wohlin: "Once no new papers are found in the iterations using both backward and forward snowballing, the loop is ended." | wohlin.eu/ease14.pdf | exact |
| 15 | Teplitskiy: 54% of citations little-to-no influence; highly cited papers found earlier, via contacts, read more closely | arxiv.org/pdf/2002.10033 | exact |
| 16 | Karpathy: outputs filed back into the wiki so queries "add up" | twitterapi.io, status 2039805659525644595 | exact |
| 17 | WideSearch: agents "abandon the search after an initial failed attempt"; DeepResearchGym: 78.5% of missing key-points are multi-facet gaps | arxiv.org/pdf/2508.07999; arxiv.org/pdf/2505.19253 | exact |
| 18 | Swanson 2011 neglect markers; Smalheiser "drowning in a sea of existing potential hypotheses"; the penumbra | Europe PMC PMC3097086; pmc.ncbi.nlm.nih.gov/articles/PMC5771422 | exact |
| 19 | X: Douglas (23.4k), Petrov "new gems", Lei Yang (738 followers), Chapman 97%, Allen forward-citation tree | scratchpad/raw/r1b/*.jsonl (verbatim API text) | ids 1982591934389784687, 1689316130538872832, 1994042370376032701, 1276213439417815041, 1452531940041666560 |
| 20 | Pandey: rank promotion "approximately 60% larger"; Bevendorff: higher-ranked pages "more optimized, more monetized … lower text quality"; Mallen: retrieval helps on less popular facts; DeLM: "a negative result remains local to one trajectory" | arxiv.org/pdf/cs/0503011; downloads.webis.de/…/bevendorff_2024a.pdf; arxiv.org/pdf/2212.10511; arxiv.org/pdf/2606.10662 | exact |
| 21 | Greenberg: 94% vs 6% of 214 citations; Robb-Silberman: "distinguish corroboration from repetition", "false corroboration" | Europe PMC PMC2714656; govinfo.gov/content/pkg/GPO-WMD/pdf/GPO-WMD.pdf | exact |
| 22 | Blair & Maron: STAIRS retrieved 20% while lawyers believed >75%; Saracevic & Kantor: item retrieved ≥5 of 9 times >6× as likely relevant | Wayback copies of dl.acm.org/doi/pdf/10.1145/3166.3197 and tefkos.comminfo.rutgers.edu/JASIS1988part3.pdf | exact |
| 23 | White, Dumais & Teevan: experts "explore the space more broadly"; Patterson et al.: "only used narrowing tactics and no widening tactics"; Lau & Coiera: 22.4% right→wrong, 45.1% wrong stayed wrong | microsoft.com/…/wsdm09-expertise.pdf; Wayback apps.dtic.mil/…/ADA395332.pdf; pmc.ncbi.nlm.nih.gov/articles/PMC1975788 (table) | exact |
| 24 | Aslett: 77% of headline/URL queries → an unreliable link in the top ten (vs 21%); Wineburg & McGrew: "Fact checkers, in short, learned most about a site by leaving it." | nature.com/articles/s41586-023-06883-y; stacks.stanford.edu/…/Lateral Reading and the Nature of Expertise.pdf | exact |
| 25 | Callaghan & Müller-Hansen: IH50 "target is missed in 39% of cases"; Cormack & Grossman: the searcher "must be isolated from any knowledge of T" | r.jina.ai of systematicreviewsjournal…/s13643-020-01521-4; Wayback of plg.uwaterloo.ca/~gvcormac/reliability/cormackgrossman16.pdf | exact |
| 26 | Karpathy agenthub: "Check children of the current best to avoid duplicating work"; "Negative results prevent others from wasting time on the same dead ends." | raw.githubusercontent.com/karpathy/autoresearch/7004de0/program_agenthub.md | lines 137, 158 |
| 27 | ACH study: "the control group was a little more accurate (and coherent) than the ACH group"; error −61% after coherentizing then aggregating | r.jina.ai of sas.upenn.edu/~baron/journal/18/18803/jdm18803.html | exact |
| 28 | Furnas et al.: "In every case two people favored the same term with probability <0.[20]" | Wayback of dl.acm.org/doi/pdf/10.1145/32206.32212 | PARTIAL — the OCR cut after "<0."; the figure 0.20 is the reader's |
| 29 | BIN: noise ~50%, bias ~25%, information ~25%; Mellers 2014: teams "could share information, including their forecasts (but there was no systematic display…)"; Chang 2016: only C (comparison classes) associated with better performance | faculty.wharton.upenn.edu/…/mnsc.2020.3882.pdf; sydneyscott.nfshost.com/…/Psychological_Strategies_for_Winning_a_G.pdf; journal.sjdm.org/16/16511/jdm16511.pdf | exact |

| 30 | METR: "Of the 533 agents active on the message board … over 90% quickly joined in the attack"; a coordinator: "too many duplicate efforts" | metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/ | exact |
| 31 | Anthropic: early agents "distracting each other with excessive updates"; BIN: superforecasters "owe their success more to superior skills at tamping down measurement error" | ~/Desktop/guidesfm/research/articles/how-we-built-our-multi-agent-research-system.md:43; faculty.wharton.upenn.edu/…/mnsc.2020.3882.pdf | exact |
| 32 | FM 2-22.3 (Admiralty grading): an "F" rating "does not necessarily mean that the source cannot be trusted, but that there is no reporting history" | the R3-1 reader's saved fetch of irp.fas.org/doddir/army/fm2-22-3.pdf via r.jina.ai (`scratchpad/r3/fm_jina.txt`) | exact, in the reader's raw bytes (not re-fetched) |

| 33 | Stack Overflow: 58.4% of obsolete answers obsolete when posted; 20.5% ever updated | arxiv.org/pdf/1903.12282 | exact |
| 34 | Weissburg et al.: tweeted papers' "median citation counts 2-3 times higher than those of the control group"; curator bio "dm for promo" | export.arxiv.org/abs/2401.13782; twitterapi.io profile of the curator | exact |
| 35 | IQWiG objective vs conceptual search: sensitivity 97% vs 75% | PubMed 27256930 (efetch) | exact |
| 36 | Published vs grey literature: effects larger "by 15%" | PubMed 11072941 (efetch) | exact |
| 37 | h-index vs accuracy r = 0.00 (experts predicting efficacy outcomes); fame vs overconfidence r = 0.33 (Tetlock) | the R3-2 reader's saved text of Atanasov & Himmelstein 2023 (`scratchpad/r3-2/atanasov2023.md`) | exact, in the reader's raw bytes — and the context was corrected: not "forecasting tournaments" |
| 38 | X: "TODO(noam): write a paper" (jekbradbury); appendix A.6 (jkcarlsmith); "I have no idea who this person is (small account)…" (jachiam0); Lei Yang "checked the five reviews … Not a single reviewer noticed" | twitterapi.io verbatim text in the R1-A/R1-B harvests | exact |

| 39 | Heuer's handicapper study: data "in increments of the 5, 10, 20 and 40 variables"; accuracy "remained the same"; "With only five items of information, the handicappers' confidence was well calibrated" | cia.gov/resources/csi/static/Pyschology-of-Intelligence-Analysis.pdf (ch. 5) | exact — an alignment reviewer called this unsourced because it was not in this ledger; it is in the primary |
| 40 | Aslett: searching raised belief in false articles by 0.057, "a 19% increase" | nature.com/articles/s41586-023-06883-y | exact |
| 41 | Tenopir & King Table 1: browsing 58.5% (1977) → 33.9% (2005); automated searching 23.1% (2005) | dlib.org/dlib/november08/tenopir/11tenopir.html | exact |
| 42 | Karnofsky "explain and defend my current, incredibly premature hypothesis" / reading "most likely to change the big-picture claim"; Steinhardt "I try harder and earlier to show that my ideas can't work"; adversarial collaboration "identify results that would change their mind" | cold-takes.com/learning-by-writing; cs.stanford.edu/~jsteinhardt/…; pure.mpg.de/…/file_2102237 | exact |
| 43 | Carlini "In a good paper this is answerable in a sentence: your goal is to find that sentence"; Nanda "at least 50% of papers are basically useless due to insufficient skepticism" | ~/Desktop/guidesfm/research/articles/how-to-win-a-best-paper-award….md:196-197; …/research-process-key-mindsets.md:36 | exact |
| 44 | OpenAlex citation chaining (`cite-chain.sh`): the Greenhalgh & Peacock work resolves; 1,995 citers; 296 mention replication; 6 references; `core` finds shared references | api.openalex.org, run live | tested, all four modes |

| 45 | Saracevic & Kantor: searches built from the user's problem statement had the highest recall (32%); written question only the lowest (18%) | Wayback of tefkos.comminfo.rutgers.edu/JASIS1988part3.pdf | exact — note: a statement of the NEED, not of the asker's plan |

**Correction logged 2026-09-26:** an earlier KNOWN/FINDINGS/SKILL line attached BIN's 50/25/25 split to
superforecasters; the source says it of "the control group". Fixed everywhere after the diff review.

Not verified by the chair, and used anyway only with that label: every other row. The largest unverified
clusters are the forecasting correlations beyond row 29, the paper-mill and GRIM figures, the LBD
analogy percentages, the Hausner/IQWiG sensitivities, and all caption-derived transcript material
beyond row 10.
