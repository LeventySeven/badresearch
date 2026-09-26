<!-- AGENT OUTPUT — R1-A X roster. Returned by a subagent, not read by the chair unless a row says so. -->

## Findings

F1. Karpathy compounds his research by filing every answer back into a wiki that an LLM maintains. It also runs "lint" passes over that wiki to find connections worth a new article.
    who: Andrej Karpathy (ex-OpenAI, ex-Tesla AI; 4.22M followers). Sells nothing here.
    evidence: "Often, I end up "filing" the outputs back into the wiki to enhance it for further queries. So my own explorations and queries always "add up" in the knowledge base." — https://x.com/karpathy/status/2039805659525644595 (2026-09-26; READ-FULL)
    bears on: Q4, C1, C3
    limit: tested at "~100 articles and ~400K words". He says this small scale is why he did not need RAG.

F2. Nanda splits research into Explore (gain surface area, "prioritise for information gain"), then Understand, then Distill (red-team the result). He keeps a highlights doc so that connections become visible.
    who: Neel Nanda (mech-interp lead, Google DeepMind; 47k). He recruits MATS scholars, and the post was co-written with Gemini 2.5 Pro.
    evidence: "A key practical tip is to keep a highlights doc of particularly interesting results, this makes it easier to spot connections" / "Your north star is to gain evidence for and against these hypotheses" — https://www.alignmentforum.org/s/5GT3yoYM9gRmMEKqL/p/hjMy4ZxS5ogA9cTYK (2026-09-26; READ-FULL)
    bears on: Q4, Q5, Q6 (his check: "am I getting enough information per unit time?"), C1, C3, C5
    limit: he scopes it himself: "most useful for mechanistic interpretability researchers". A reply from Hadfield-Menell says the method is missing a "map" of related work.

F3. Before trusting a paper, researchers re-run it, reimplement it or ablate it, and that is where the real mechanism turns up.
    who: François Chollet (ARC Prize co-founder, so he has a stake in ARC; 734k). Nat Friedman (investor; 483k) asked the crowd "What am I missing?" and then re-ran the evals from the papers it recommended.
    evidence: "2. The outer refinement loop (barely mentioned in the paper) is the main driver of performance." — https://x.com/fchollet/status/1956442449922138336 ; "When we re-ran the evals from some of the cited experiments, we saw some improve, and some get worse" — https://x.com/natfriedman/status/1791462511889559615 (2026-09-26; READ-FULL)
    bears on: Q3, Q5, C5
    limit: costs compute. Also seen: Dettmers ("implement stuff and then see they cheated", /status/1624469056299610112) and Albert Gu, who traced wrong Mamba results to bad initialisations in popular implementations (/status/2026770917997818201).

F4. The newest knowledge sits in code and inside labs, not in papers.
    who: James Bradbury (Anthropic compute, ex-Google JAX; 17.5k). Stephen Roller (Thinking Machines; 6.1k followers).
    evidence: "AdaFactor, quietly added three weeks ago to the Tensor2Tensor repository along with a note reading "TODO(noam): write a paper."" — https://x.com/jekbradbury/status/962121602421829632 ; "yeah we call it flabberblanung internally. we’ve been using it as our default for about 8 months. here’s the code." — https://x.com/stephenroller/status/1784792629189738897 (2026-09-26; READ-FULL)
    bears on: Q3, Q7
    limit: you need a view into the repo or the lab. Jason Wei adds that inside labs the handoff is now "slack posts, stale documentation, code, and training runs… way worse information density, longevity, and discoverability" (/status/1858587929809219626).

F5. Popularity is produced by a few curators, and it raises citation counts measurably.
    who: Stella Biderman (EleutherAI; 19k), pointing to Weissburg et al. (ICML 2024). One of the curators, @_akhaliq (528k), has "dm for promo" in his bio.
    evidence: "Being tweeted about by @arankomatsuzaki is more selective than any ML venue" — https://x.com/BlancheMinerva/status/1750777835529072648 ; "median citation counts 2-3 times higher than those of the control group" — https://arxiv.org/abs/2401.13782 (2026-09-26; READ-FULL / abstract only)
    bears on: C4, Q2
    limit: the paper measures citations, not quality.

F6. Citation counts miss in both directions: important work goes uncited, and flawed work collects thousands of citations.
    who: François Fleuret (FAIR/Geneva; 55k), Eric Jang (143k), Andrew Gelman's blog (48.8k).
    evidence: "So FlashAttention is used now *everywhere*, and the paper is cited only 50 times?" — https://x.com/francoisfleuret/status/1658391811319103488 ; "cited more than 6,000 times… It’s fatally flawed" — https://x.com/StatModeling/status/2014345097043714076 ; Grokking "<5 citations" — https://x.com/ericjang11/status/1480633788505812992 (2026-09-26; READ-FULL)
    bears on: C4
    limit: citations lag. Gelman's underlying post was BLOCKED.

F7. Sources with small followings get trusted on track record or on the work itself, not on reach.
    who: Tim Dettmers (48k) on Dan Alistarh (1,792 followers). Joshua Achiam (35k) on an unnamed small account. Arvind Narayanan (131k) on Igor Brigadir (5.3k). Jacob Steinhardt on Nuño Sempere (5.3k): "strong forecasting track record".
    evidence: "I do not get why Dan's group does not get more attention: best quantization methods, best quantization kernels" — https://x.com/Tim_Dettmers/status/1967552946172027057 ; "I have no idea who this person is (small account), but this thread is exactly correct" — https://x.com/jachiam0/status/2095764746155032859 ; "Many viral threads by growth hackers / influencers… All of them were BS. Read this instead from actual experts" — https://x.com/random_walker/status/1643683157856903169 (2026-09-26; READ-FULL)
    bears on: C4, Q2
    limit: none stated.

F8. Some researchers build the counter-search into reading itself: every lookup triggers a search for later work that challenges it.
    who: Arvind Narayanan (Princeton CITP; sells *AI Snake Oil*). Andy Matuschak (tools-for-thought researcher; 63k).
    evidence: "when they look up a paper they should explicitly look for later work that challenges it." — https://x.com/random_walker/status/2093359668806512793 ; "orange highlight on a claim -> prints a skeptical fact-check" — https://x.com/andy_matuschak/status/2099987276550041633 (2026-09-26; READ-FULL)
    bears on: C5, Q5
    limit: Narayanan's is a proposal, backed by his own rough estimate that 80% of the literature is wrong. Matuschak's is a prototype.

F9. Some researchers search specifically against their own position, and stop when that search comes back empty.
    who: Nathan Lambert (ex-Ai2 Olmo co-lead; paid newsletter; 102k). He argues for open models and searched for evidence they are falling behind. Stella Biderman: "If LLMs are that dangerous I would stop making them, so I've been looking into the evidence."
    evidence: "I spent a long time looking for evidence of or arguments supporting open models falling behind, but it's not there at all today." — https://x.com/natolambert/status/2046299148883046450 (2026-09-26; READ-FULL)
    bears on: C5, Q6
    limit: an empty search is only as good as how it was scoped.

F10. Olah calibrates taste by checking predictions (watch how ideas you had turn out when others try them) and by steelmanning rival research schools.
    who: Chris Olah (Anthropic, Distill; 159k).
    evidence: "Are there adjacent research “schools”… If so, try to articulate the strongest version of their view, and why you agree or disagree." — http://colah.github.io/notes/taste/ (2026-09-26; READ-FULL)
    bears on: C5, Q2
    limit: he labels it a "rough note".

F11. Several people use red-flag rules that end reading before the paper does.
    who: Lucas Beyer (Meta, ex-OpenAI/DeepMind; 153k), Tri Dao (Princeton/Together; 45k), Arvind Narayanan. Paul Graham: "patent-pending… I stop reading." hardmaru gives a fixed skim order: abstract, intro first and last paragraphs, conclusion, figures.
    evidence: "never, ever write "we use the same learning rate across all methods for fair comparison" I read this as "do not trust any of our conclusions" and then i move on." — https://x.com/giffmana/status/2017283232736100742 ; "way too fast: ~1800 TFLOPS of FP32 on H100, 30x the theoretical max!" — https://x.com/tri_dao/status/1892610951662153945 ; "you’re less impressed when you read it the second time" — https://x.com/random_walker/status/2029898822327890231 (2026-09-26; READ-FULL)
    bears on: Q2, Q6
    limit: Beyer admits the pull of his own bias: "it confirms most of my intuitions, so it's self serving for me to like it" (/status/1998536238408565003).

F12. Fraud turns up by connecting across many papers: one artefact repeated across 400 papers.
    who: Elisabeth Bik (science-integrity consultant; 144k). Tips arrive by anonymous email.
    evidence: "the spot is on the exact same position in dozens of blots within the same paper but also among those 400 papers." — https://x.com/MicrobiomDigest/status/1232854318061015042 (2026-09-26; READ-FULL, thread)
    bears on: C3, Q2, Q3
    limit: it rests on "we have scanned 1000s of papers" of experience.

F13. Where trials are never run, some go to forums for knowledge that exists nowhere else.
    who: Patrick Collison (Stripe CEO, Arc co-founder; 1.78M). Nabeel Qureshi (ex-Palantir; 38k): "google "X reddit"".
    evidence: "Reddit provides a kind of emergent intelligence that sits between that which any single physician can marshal and the full rigor of clinical trials." — https://x.com/patrickc/status/1967346630539333662 (2026-09-26; READ-FULL)
    bears on: Q3, C1 ("compounding knowledge")
    limit: he calls it "pretty unstructured"; the evidence is self-reported.

## Against the claims

A1. Depth first, not breadth first (against C2).
    who: Sasha Rush (85k). Neel Nanda, same post as F2.
    evidence: "Pick depth over breadth. If you do depth well, you get breadth for free." — https://x.com/srush_nlp/status/1276514523726389250 ; "Building deep knowledge of a literature takes time, and is easier once you have some hands-on experience." — AF post above (2026-09-26; READ-FULL)
    bears on: C2, Q4
    limit: advice to learners. Jason Wei goes further: inspect the data before reading at all, to gain what "we could not have gotten from reading research papers" (/status/1708921475829481683).

A2. Popularity used as the filter, and it works for them (against C4).
    who: Yi Tay (Google DeepMind, Gemini Deep Think; 60k). Chollet: adoption is "a much better feedback signal than publication ever could".
    evidence: "If there's a paper important enough to read, it will somehow "intrusively" appear in my face on twitter anyway." — https://x.com/YiTayML/status/1645613573081829376 ; https://x.com/fchollet/status/1467023443010928640 (2026-09-26; READ-FULL)
    bears on: C4
    limit: this works for insiders whose feeds are made of peers. F5 shows the same mechanism can be bought.

A3. Discovery by chance, not by accretion (against C1).
    who: Paul Graham (5.3M). Narayanan's "150 open tabs" post, the most-liked post in the harvest at 172k likes.
    evidence: "Books I come across in used bookshops, or randomly pick off a shelf in my house, or have recommended to me by someone I trust" — https://x.com/paulg/status/1610087893271302145 ; "a tab that's been open since 2019 with a paper that has a solution to the exact research problem" — https://x.com/random_walker/status/1531406325787160577 (2026-09-26; READ-FULL)
    bears on: C1, Q1

A4. Connecting findings can overfit (a limit on C3).
    who: Zachary Lipton (CMU/Abridge), reporting Sanjeev Arora's talk. This is a secondary report.
    evidence: "Drawing connections between (in fact) unrelated facts" — https://x.com/zacharylipton/status/1098989274438033414 (2026-09-26; READ-FULL)
    bears on: C3

A5. Shared memory between parallel agents is reported, but its benefit is not measured (limit on C6).
    who: NVIDIA's Agora paper, which I found through Elvis Saravia (@omarsar0), who sells courses.
    evidence: "Measuring the effect on discovery per unit of compute requires a matched comparison." — https://arxiv.org/abs/2609.18094 (2026-09-26; READ-FULL / abstract only)
    bears on: C6, Q7
    limit: the same run reports 165 reproductions with no failures, so sharing did enable verification.

## Not covered by any claim

N1. Predict, then check, to calibrate filters. Jason Wei: "Having a track record holds you to be accountable for intuitions and helps you remember when you were wrong." — https://x.com/_jasonwei/status/1783565962891178420. Nuño Sempere bet on stock tips from X: "people don't know what they're talking about… selective reporting of wins is rampant" — https://x.com/NunoSempere/status/2032802263215845378 (5.3k followers). (Q2, Q5; READ-FULL)

N2. Finding people through the questions they ask or through solo follow-up papers. Noam Brown (OpenAI; 175k): "put a solo paper on arxiv that followed up on my work. I was impressed, so I invited him to work with me." — https://x.com/polynoamial/status/1774860796142538936. Michael Nielsen asks "Who do you read/watch _everything_ by?" (/status/1084540193518931968). (Q1; READ-FULL)

N3. Daily writing as the accumulator instead of a knowledge store. Matuschak on Tyler Cowen and Matt Levine: "Nothing quite accumulates for either of them… They're doing the whole thing over again every day." — https://www.dwarkesh.com/p/andy-matuschak (Q4; READ-PARTIAL). This contradicts the idea that compounding requires a kept map.

N4. Testing claims on data that cannot be in the index. Patrick McKenzie (patio11) used "three writing samples… which I do not believe to be on the public Internet" — https://x.com/patio11/status/2046705423802155037 (Q5; READ-FULL)

N5. Feed hygiene. Karpathy's return to RSS: "a lot less slop intended to provoke" (/status/2018043254986703167). McKenzie on the algorithmic side of X: "That product hates you" (/status/1809963674821431684). Nat Friedman switched to Lists (/status/1307412289620865026). (Q1, C4)

N6. Stopping by accepting incompleteness. Sebastian Raschka: "The world goes on even if you don't read everything." — https://x.com/rasbt/status/1584514519526961152. Casey Handmer: "80% of the citations link back to stuff I wrote" — https://x.com/CJHandmer/status/1889576483632365613. When the search returns your own work, you are at the frontier. (Q6)

## Frontier
- Agora, Git as shared memory for research agents (C6/Q7): https://arxiv.org/abs/2609.18094
- Neel Nanda's posts on research mindsets and research taste: https://www.alignmentforum.org/s/5GT3yoYM9gRmMEKqL
- Keshav, "How to Read a Paper" (via hardmaru): http://blizzard.cs.uwaterloo.ca/keshav/home/Papers/data/07/paper-reading.pdf
- Adler and Van Doren's active-reading rules, and Matuschak reading a textbook at "15 minutes a page": dwarkesh.com/p/andy-matuschak
- Hamming, "You and Your Research", and Nielsen, "Principles of Effective Research" (via Olah's note)
- Vicki Boykis, "How I (try to) keep up" and her anti-hype LLM reading list: https://gist.github.com/veekaybee/be375ab33085102f9027853128dc5f0e
- Gelman, "Refuted papers continue to be cited more than their failed replications" (BLOCKED) and "Scientific citations as an overwhelmed communication channel" (2026-09-17)
- fantasticanachronism, "Studies that replicate are cited at the same rate…" (via Paul Graham): https://fantasticanachronism.com/2020/09/11/whats-wrong-with-social-science-and-how-to-fix-it/
- PubPeer, a venue for distributed counter-evidence (Bik)
- Nihar Shah interviewed the authors of low-quality submissions (via Gautam Kamath): https://x.com/thegautamkamath/status/2100322947479036045
- CORE-Bench and CRUX reproducibility evals (Sayash Kapoor)
- Karpathy's list of 92 RSS feeds from HN: https://gist.github.com/emschwartz/e6d2bf860ccc367fe37ff953ba6de66b
- LessWrong, "The best textbooks on every subject" (Karpathy)
- Long-COVID patient-reported outcomes study, 3,900 respondents (Collison)

## Lane state
- Roster "top" queries: 65 handles, one call each. Harvested: 42 lab/ML researchers and 20 founders/skeptics.
- gwern, jamesheathers: EMPTY. Both the query and the `user` endpoint return 0 rows; the account may be deleted, protected or renamed.
- sholtodouglas: WRONG-HANDLE. It returned a different person ("Douglas Cole", 61 followers). A wrong handle can return a stranger's feed, not only nothing. Re-run as _sholtodouglas.
- Added 15, all pointed to by the harvest: _sholtodouglas, seb_ruder, 1a3orn, NunoSempere, dlwh, DAlistarh, vqctran, stephenroller, LauraDeming, IgorBrigadir, jekbradbury, CJHandmer. sebkrier, EricSteinb, nelsonfliu: EMPTY. caseyhandmer: MISSING (the real handle is CJHandmer).
- Themed OR queries over 20 handles silently returned 0. The query appears to be too long; splitting into groups of 10 fixed it. Treat these zeros as a tool failure, not as EMPTY.
- Gelman blog: BLOCKED (Cloudflare).
- About 134 of 160 API calls used.

## Source register
- Raw harvests (JSONL, one file per handle and query, all 2026-09-26): /private/tmp/claude-501/-Users-seventyleven-Desktop/fcd46374-4e61-45da-ae77-538c40287f4b/scratchpad/raw/r1a/ — READ
- Every x.com status URL cited above — READ-FULL (verbatim text from the API)
- http://colah.github.io/notes/taste/ — READ-FULL
- https://www.alignmentforum.org/s/5GT3yoYM9gRmMEKqL/p/hjMy4ZxS5ogA9cTYK — READ-FULL
- https://arxiv.org/abs/2401.13782 — READ-FULL (abstract)
- https://arxiv.org/abs/2609.18094 — READ-FULL (abstract)
- https://www.dwarkesh.com/p/andy-matuschak — READ-PARTIAL
- https://statmodeling.stat.columbia.edu/2024/03/10/refuted-papers-continue-to-be-cited-more-than-their-failed-replications-can-a-new-search-engine-be-built-that-will-fix-this-problem/ — BLOCKED
- Threads rebuilt: 1916095332133527844, 1230794470855069697, 957763229454774272 — READ