<!-- AGENT OUTPUT — R1-B X query-first/unpopular. Returned by a subagent, not read by the chair unless a row says so. -->

## Findings

F1. **Go to where the people who already solved it wrote things down, then email them.** Douglas pulls NASA technical reports, then Google Scholar, then old textbooks, then YouTube. He emails the authors of the 2–3 closest papers and later sends them his own results. His stopping point is when the experts left are as unsure as he is.
- who: Calum E. Douglas FRAeS. Consulting mechanical engineer, aviation historian and author (Tempest Books). 23,400 followers; this post has 2,649 likes. Mild incentive: he sells consulting and books.
- evidence: "download all papers pertaining to someone who DOES know" … "you will eventually realise that the remaining people in the field are just as confused as you are" — https://x.com/CalumDouglas1/status/1982591934389784687 (2026-09-26; READ-FULL)
- bears on: Q1, Q3, Q5, Q6; supports C1
- limit: engineering questions that have a technical-report literature. His stop rule means "reached the edge of what anyone knows", not "enough to decide".

F2. **Stop when the same citations keep coming back; draw the citation map by hand; spot gaps by what reference lists leave out.** Pacheco-Vega saw that four water-policy papers cited nothing from the policy-implementation literature. He only noticed because he read their reference lists.
- who: Raul Pacheco-Vega, professor at FLACSO Mexico, 69,441 followers.
- evidence: "I define concept saturation as the point where I am seeing the same citations repeated on a regular basis." — http://www.raulpacheco.org/2016/06/how-to-do-a-literature-review-citation-tracing-concept-saturation-and-results-mind-mapping/ (2026-09-26; READ-FULL). Found via https://x.com/raulpacheco/status/983105747968864267
- bears on: Q4, Q6; supports C3
- limit: saturation only covers the citation network you entered. A literature that never cites your central author stays invisible.

F3. **Snowball backward, then run forward citations, then do a deliberate sweep for under-cited authors.** Allen starts from one review, reads 4–5 key references, then uses Scholar's "cited by" to bring the tree up to date. He ends with an "inclusion sweep" for early-career and under-represented authors.
- who: Micah G. Allen, professor of computational neuroscience at Aarhus, 24,258 followers.
- evidence: "look up individual papers in your tree on Google scholar. Open the papers that cite these papers and now sort the reference tree forward into the modern day" — https://x.com/micahgallen/status/1452531940041666560 ; the sweep: https://x.com/micahgallen/status/1452532125236973573 (2026-09-26; READ-FULL)
- bears on: Q1, Q4; C1 and C4 (low-cited work sampled on purpose); runs against C2 (starts deep)
- limit: everything flows from one review, so it inherits that review's framing.

F4. **Subscribe to the citations of a few important papers instead of scanning arXiv.**
- who: Alexia Jolicoeur-Martineau, principal researcher at Microsoft and 2025 ARC Prize winner, 26,159 followers. Also @fiandola (Meta research scientist, 3,785) and @jason_trost (Databricks detection engineering, 2,965), who calls it "Very high SNR".
- evidence: "I follow a few GAN papers to be able to catch most GAN papers." — https://x.com/jm_alexia/status/1242497833967771649 (2026-09-26; READ-FULL)
- bears on: Q1, Q2; runs partly against C4 (the seeds are the popular papers)
- limit: it misses work that never cites the seed papers, which is exactly the gap in F2.

F5. **Read the appendix and supplement; both the best results and the bad news are hidden there.**
- who: David W., primary-care nurse practitioner, 1,134 followers. Joe Carlsmith (Anthropic, 13,377) says Apollo's most important result was in "appendix A.6". James Thompson (psychologist, 7,244) says a paper "buried contrary findings in an appendix!" Jason Locasale (professor, ~50,000 citations, 16,289 followers) says the best work is "buried in supplementary information that no one reads."
- evidence: "Always read the appendix in studies. Nuggets of good AND bad get buried there. Reimagine 2, only 59% of patients were on CagriSema 2.4/2.4" — https://x.com/rn_flex/status/2063970766249472026 ; https://x.com/jkcarlsmith/status/1866232909558112508 ; https://x.com/JamesPsychol/status/2101591419974520874 (2026-09-26; READ-FULL)
- bears on: Q3; C5 (appendices hold the counter-evidence)
- limit: this happens because of venue page limits. Talia Ringer (33,901): "most reviewers won't read the appendix" — https://x.com/TaliaRinger/status/1696959810430816521

F6. **Run the artifact, check samples by hand, and don't trust prestige.** Yang ran an Apple benchmark and found a code bug; fixing it lowered the scores. He hand-checked 20 failures and found 6 wrong labels. He checked the paper's own examples and its five OpenReview reviews (none caught it), then posted a public comment. The paper was withdrawn.
- who: Lei Yang, ML researcher at StepFun, **738 followers** (the post has 2,454 likes and 400k views).
- evidence: "because it was a paper from Big Tech, I subconsciously trusted the integrity and quality, which prevented me from spotting the problem sooner." — https://x.com/diyerxx/status/1994042370376032701 (2026-09-26; READ-FULL)
- bears on: Q2, Q5; supports C4 and C5
- limit: needs something you can run and can check by eye. Related: Ankita Singh (ZK, ex-intern at Nethermind and OpenZeppelin, 4,202): "the paper describes the ideal. the implementation ships a subset… read the code, not just the paper" — https://x.com/annkkitaaa/status/2056630411552534878

F7. **Two passes with a question list, and past findings read in between.** Dacian reads the code once fast and logs open questions, then reads prior audit findings on similar protocols. He then does a slow second pass to answer his questions, then looks for weak spots in the test suite. Last, he works backwards from an imagined successful hack.
- who: Dacian, head of security research at Cyfrin, 6,717 followers. The claim of protecting "$100B+ TVL" is his own.
- evidence: "After the first pass is completed I use @SoloditOfficial to read previous findings from similar protocols. Then I begin the second read-through of the code where I go much slower" — https://x.com/DevDacian/status/1754129562261446679 (2026-09-26; READ-FULL)
- bears on: Q4, Q5, Q6; supports C1 and C2
- limit: works on a bounded artifact (one codebase), not an open literature.

F8. **Ask authors which of their own papers the field missed.**
- who: Dmitri Petrov, Stanford evolutionary biologist, 14,311 followers. The 20 replies came from authors with 87 to 19,513 followers. Their reasons were practical: "by publishing in a very good microbiology journal we missed our community" (@DDuneau, 331 followers); "2 citations in 7 years? (Of which one is me.)"
- evidence: "A paper they believe made a real advance but was somehow missed by the community. I always find new gems this way." — https://x.com/PetrovADmitri/status/1689316130538872832 ; https://x.com/DDuneau/status/1689648410167754752 (2026-09-26; READ-FULL)
- bears on: Q3; supports C4
- limit: self-nominated, and authors overrate their own work.

F9. **Unpublished theses and a test for old ideas.**
- who: Joseph Francis, economic historian, 11,530 followers (1,538 likes). Jim Lux, licensed PE working on space hardware, **306 followers**.
- evidence: "The PhD dissertations of people who left academia and never published anything are a goldmine." — https://x.com/joefrancis505/status/1923695028565667879 ; "Is that because it a) violates the laws of physics, or is it b) because it was uneconomic. If b), you got a shot." — https://x.com/jimlux/status/1982653400530690117 (2026-09-26; READ-FULL)
- bears on: Q3
- limit: none stated.

F10. **Following citations to the original catches errors and takes your reading away from where your peers read.**
- who: @analytichegel (3,582; credentials not checked). Nate Jones, FOIA director at the Washington Post (15,106). Phillip Johnston, embedded consultant (2,592).
- evidence: "It's astonishing how much stuff is wrong due to a combination of games of telephone and the original source being unreliable." — https://x.com/analytichegel/status/1892249342460710955 ; "I end up reading in very different directions than most of my peers (like you, I do a lot of reading-via-mining-the-references-list)" — https://x.com/mbeddedartistry/status/1146843097394925569 ; https://x.com/FOIANate/status/2090517470696087557 (2026-09-26; READ-FULL)
- bears on: Q2, Q3; supports C5
- limit: none stated.

F11. **Follow people, but filter them hard.** Haelle only lists researchers whose main field is the topic. Rosinality posts only papers he found himself, never recommended ones. n00py adds every good blog to an RSS feed until it is "near 100% signal".
- who: Tara Haelle, science journalist (22,027); Rosinality, ML engineer at Poolside (8,003); n00py, pentester (13,844). Kevin Lin (Oxford postdoc, 2,469) notes that Hugging Face Daily Papers are "usually either shared by authors who actively promote their work", so that feed rewards self-promotion.
- evidence: "I want researchers whose *PRIMARY* ressearch area is evolutionary bio of viruses or similar (ie, the pre-COVID experts)." — https://x.com/tarahaelle/status/1465160694958108674 ; https://x.com/rosinality/status/2019309099654213874 ; https://x.com/n00py1/status/1290787023653974016 ; https://x.com/KevinQHLin/status/1986219709235167706 (2026-09-26; READ-FULL)
- bears on: Q1, Q2
- limit: none stated.

F12. **Reject fast; read to answer a specific question.**
- who: David Chapman (36,825). Michael Kirchhof, Apple research scientist (1,721), gives reading "modes". Hillel Wayne (18,815) spent an hour on one paper and changed his verdict; he treats "Evidence of manual labour" as "a GREAT sign".
- evidence: "97% of academic papers have such glaring flaws that you can dismiss them after reading the title, or the abstract… Learning to ignore quickly and accurately is a critical research skill." — https://x.com/Meaningness/status/1276213439417815041 ; "'Did they scoop me?' read methods -> start of experiments" — https://x.com/mkirchhof_/status/1718170609916485902 ; https://x.com/hillelogram/status/1146841388983570432 (2026-09-26; READ-FULL)
- bears on: Q2, Q6
- limit: fast rejection by title and abstract may throw away the papers that are good but badly packaged (F8).

F13. **Search tools rank by popularity, so switch tools and use chronological order.**
- who: Alvaro Alhambra, quantum physicist at IFT UAM-CSIC (2,179). Seitaro Shinagawa, VLM researcher at SB Intuitions (10,177), quoting @iBotamon. Nico "Dutch OSINT Guy", SANS principal instructor (39,179).
- evidence: "all the great but not so cited papers that I will never find due to Google Scholar showing the most cited first." — https://x.com/AlhambraAlvaro/status/1428709009587113990. iBotamon: "質問を変えても似た文献がずっとサジェストされて Google scholarに変えると掘り出しものが出たりしますね" [my translation: one tool keeps suggesting similar papers even when you rephrase; switching to Google Scholar turns up hidden finds] — https://x.com/sei_shinagawa/status/1697949901194412358. Nico: "Don't forget to hit the 'latest' tab… by default it will point to the the 'top results'." — https://osintcurio.us/2019/08/01/muting-the-twitter-algorithm-and-using-basic-search-operators-for-better-osint-research/ (2026-09-26; READ-FULL)
- bears on: Q2, Q3; supports C4
- limit: none stated.

F14. **Non-English and non-paper sources.** Pablo copied and translated Chinese posts by hand and deliberately trained his X feed toward them. A <500-follower account found a pre-alpha game screenshot in Japanese patent filings. Douglas translated a German manuscript while researching and it became his second book.
- evidence: "I realized the chinese content was way better than the english feed. So, I started manually copying and translating their articles." — https://x.com/pblmnz/status/2043798694491988122 ; https://x.com/chriswhoisgreat/status/1451444602691592193 ; https://x.com/CalumDouglas1/status/1982927279026999801 (2026-09-26; READ-FULL)
- bears on: Q3
- limit: these are anecdotes, not a system.

F15. **C4 measurement on my own sample (not a claim about the world).**
- Harvest: 1,523 unique posts from 1,246 authors. By follower band: <5k 443 (36%), 5k–50k 517 (41%), 50k–500k 240 (19%), >500k 46 (4%).
- The sharpest concrete methods I kept (A-tier): 44 posts. <5k: 19. 5k–50k: 23. 50k–500k: 2. >500k: 0.
- Keep rate per band: 4.3%, 4.4%, 0.8% and 0%.
- Median followers of the A-tier set: 8,176; median likes: 65.5.
- The "Holy shit… [Stanford/MIT] paper" hype template, pulled from Top on the same platform: median 103,000 followers and 948 likes. Identical texts were posted by different accounts.
- On 8 paired queries, Top returned authors with median 19,128 followers against 3,865 in Latest. Share of <5k authors was 27% in Top against 54% in Latest.
- Seven A-tier posts came only from reply threads, and 5 of those 7 authors had under 5k followers. Replies to a question are where small practitioners show up.
- Caveats: I saw follower counts while judging, so the keep decisions were not blind. Narrow-phrase Top queries still returned small accounts. My queries select for people who describe their methods publicly.

## Against the claims

A1. **Citations do track low quality at the bottom (against C4).** Timur Kuran, Duke professor, 65,436 followers.
- evidence: "In the humanities, 82% of all published articles get zero citations. Most of these are mediocre pieces by mediocre scholars." — https://x.com/timurkuran/status/1958381384629710920 (2026-09-26; READ-FULL)
- Also: Adam Ozimek (92,650): "Forward citations to capture actual impact" — https://x.com/ModeledBehavior/status/2026734191577059726
- limit: this is his opinion, not measured.

A2. **Popularity is the right target when the question is what resonates (against C4).** E-commerce operator @ecommmoose (13,344).
- evidence: "Filter by the most liked videos in the past 6 months. 3. The top results will show the best angles" — https://x.com/ecommmoose/status/1894122685380059428
- Also: Stanford PhD student Martin Bucher (211 followers) prioritises papers he keeps running into: "what pops up over and over again" — https://x.com/mnbucher/status/1717763868842426869 (2026-09-26; READ-FULL)

A3. **Deep first, not broad first (against C2).** Allen (F3) and Pacheco-Vega (F2, 4–5 articles from the last 2–3 years) both start narrow. Chapman says that at PhD level "you have to be sure you know everything that is happening in your subsubsubspecialty" — https://x.com/Meaningness/status/1276268334602874881

A4. **Accretion is not always the method (against C1).** Eric Jang (143,023).
- evidence: "Read little, think a lot… Wait for those papers to become obsolete then delete them without ever reading" — https://x.com/ericjang11/status/1188006210999468032 (2026-09-26; READ-FULL)

## Not covered by any claim

N1. **Divide popularity by reach.** Look for small channels whose videos far outperform their audience size.
- who: Kyle, content strategist at Acquisition.com, **580 followers**. Also Dennis Willeboordse, e-commerce (15,984).
- evidence: "If a 750K sub channel gets a 1M view video, you can make a pretty strong guess it's cracked cold traffic." — https://x.com/KyleAM15/status/2081714972045070520 ; "Big accounts get views from being big. Small accounts only get views from the idea." — https://x.com/thedennis/status/2076021221146116290 (2026-09-26; READ-FULL)
- limit: these are content-marketing questions, not research.

N2. **Engagement as a timing signal.** Low engagement means early; heavy engagement means the idea is saturated and late.
- who: @darran0x, crypto investor (10,919). He talks his book.
- evidence: "Great ideas will get very little engagement when you're early… Alpha decays as an idea saturates the conversation." — https://x.com/darran0x/status/2054602738487775723

N3. **A thin literature can signal an important problem.**
- who: David MacIver (8,349).
- evidence: "if nobody is working on the most important problems, then the people who do work on important problems won't have many papers related to their work." — https://x.com/DRMacIver/status/1276272343183249408

N4. **Ask the author, and measure how often it works.**
- Sanjit Dhami? No: Dimitri Pages? Neither. The KCL economics professor @sanpages (2,153) emailed the authors of 5 papers for their data and got 3 replies — https://x.com/sanpages/status/1797564632615539134
- Laurence Tratt (4,269) was corrected by the authors he emailed — https://x.com/laurencetratt/status/1126194330467733506
- Graham Neubig (CMU, 47,069): "email the authors for the code" and now "ask openhands to reimplements the code" — https://x.com/gneubig/status/2026806305080656302
- Jack Morris (53,684): "Try to talk to the authors– you can learn much more from them than from a PDF." — https://x.com/jxmnop/status/1996599531358573044

N5. **A visual map of the network shows the gaps.**
- who: Riccardo Fusaroli (4,076).
- evidence: "invaluable to identify structures in the discourse about a topic and blind spots and non-talking communities" — https://x.com/fusaroli/status/1452544454078910466 (supports C3)

## Frontier
- Peter Norvig, "warning signs in experimental design" notes. Chapman pointed to them via https://x.com/DataSciFact/status/1274043325604073479
- "Six Million (Suspected) Fake Stars in GitHub" (arXiv 2412.13459). I read the abstract: fake stars promote only "less than two months" and then "become a liability". https://arxiv.org/abs/2412.13459 (router was @rohanpaul_ai)
- "Sleeping beauty" papers (term coined by van Raan in 2004). Example: Horndeski 1974 had no citations before 2008 and now has 3,000 — https://x.com/inspirehep/status/2092972894036934773
- The book *Most Underappreciated: 50 Prominent Social Psychologists Describe Their Most Unloved Work*, edited by Arkin — https://x.com/helendewitt/status/1341828255771455488
- Tools: citationchaser (github.com/nealhaddaway/citationchaser, 159 stars), Scholar Inbox, arXiv Xplorer, Solodit, the Lumen takedown database pivoted to archive.org (https://x.com/dutch_osintguy/status/1391319943589867520), NASA NTRS, Yoga OSINT pivot map (https://x.com/DailyOsint/status/1633092428142977025)
- Research-taste material: colah.github.io/notes/taste, kejunying.com/blog/research-taste, a Stanford "research taste" benchmark (https://x.com/ohmyksh/status/2089379839228915984), @ToruO_O's post on intellectual lineage (via https://x.com/GuanyaShi/status/2101161990475354616)
- Locasale's self-audit of his own citation record: "citations reflect marketing" — https://x.com/LocasaleLab/status/2087213687904010664
- Seong Joon Oh (KAIST): researchers used to skim all of arXiv and now rely on Twitter and LinkedIn to discover papers. He is building a product for this — https://x.com/coallaoh/status/1839588920402600303
- Jack Clark's arXiv "gut criteria": reported by @MattPRD, who sells a token-gated product (router only) — https://x.com/MattPRD/status/1945370732512362654
- Soviet 1970s papers as untapped "alpha": second-hand, from @teortaxesTex — https://x.com/teortaxesTex/status/1730178760354259423
- A source-grading scheme in a Centre for Information Resilience report appendix — https://x.com/QOrigins/status/1573441213835153408
- An expert-network call-diligence thread by a fund PM — https://x.com/hfreflection/status/1584886209247318019
- Phil Fisher's "scuttlebutt" method — https://x.com/iancassel/status/1150421693443260419

## Lane state
- X Top and Latest search: about 70 queries, 92 query pages. READ.
- Reply threads: 10 fetched. READ, with two exceptions. @hfreflection returned only bot replies (READ-PARTIAL). James Heathers' original post was not returned, only replies to it.
- EMPTY or noise: mailing-list query (0 rows), "how do you find" question query (0), OpenReview query (returned consumer product reviews), foreign-language query, old-ideas query (1 row), "I skip" query (4 rows). The customs-data query was killed mid-run and returned nothing.
- Aaron Tay's citation-chasing blog post: BLOCKED. The blogspot and blogger hosts reset the TLS connection, WebFetch reported "Socket is closed", and the Wayback copy has no post body.
- Budget: 102 of 160 API calls used.
- **Security note:** the twitterapi.io key appeared once in a `ps` process listing in my transcript. I did not copy or reuse it. Rotating it would be safe.

## Source register
- Raw harvest: /private/tmp/claude-501/-Users-seventyleven-Desktop/fcd46374-4e61-45da-ae77-538c40287f4b/scratchpad/raw/r1b/*.jsonl (every row: id, url, followers, likes, verbatim text). Keep list: kept.txt; call log: _calls.log. All READ.
- http://www.raulpacheco.org/2016/06/how-to-do-a-literature-review-citation-tracing-concept-saturation-and-results-mind-mapping/ — READ-FULL
- https://osintcurio.us/2019/08/01/muting-the-twitter-algorithm-and-using-basic-search-operators-for-better-osint-research/ — READ-FULL
- https://arxiv.org/abs/2412.13459 — READ-PARTIAL (abstract only)
- https://api.github.com/repos/nealhaddaway/citationchaser — READ
- https://musingsaboutlibrarianship.blogspot.com/2024/06/all-about-citation-chasing-and-tools.html — BLOCKED
- Every x.com URL cited above — READ-FULL via the xh.sh API, fetched 2026-09-26