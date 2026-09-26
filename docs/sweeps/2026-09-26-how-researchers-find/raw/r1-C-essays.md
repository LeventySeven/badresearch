<!-- AGENT OUTPUT — R1-C researcher essays. Returned by a subagent, not read by the chair unless a row says so. -->

## Findings

F1. Searching is a loop of rewriting the query. Each failed search gets its title, metadata, date or jargon changed. When the right term is unknown, he goes back to overviews to learn what the field calls the thing, then searches again.
 who: Gwern Branwen. Independent researcher who is known for tracking down obscure fulltexts (he pays bounties for them). Reader-funded; sells no method.
 evidence: "You may need to read through overviews until you finally recognize the skeleton of what you want under a completely different (and often rather obtuse) name." — https://gwern.net/search (2026-09-26; READ-FULL via r.jina.ai)
 bears on: Q1, Q3, C1
 limit: written for finding a known item.

F2. Rare items sit in low-ranked, odd-looking or mis-cited places: foreign library sites, Internet Archive scans, journal tables of contents, papers buried inside larger PDFs. The citations themselves are often copied wrong.
 who: Gwern
 evidence: "Sometimes you have to check every hit, just in case." — https://gwern.net/search. On the Pressley 1990 case: "no wonder everyone copies the same incorrect citation." — https://gwern.net/search-case-studies (2026-09-26; READ-FULL)
 bears on: Q3, C4
 limit: the "Littlewood" case study did not render.

F3. He hunts counter-evidence through reverse citations: open "Cited by" and search within the citing papers for replications. The trigger is noticing an implausible number.
 who: Gwern
 evidence: "then you can search a query like `experiment OR randomized OR blind`". Also: "This case study demonstrates the critical skill of _noticing_ the need to search at all, and the search itself is almost trivial." — search-case-studies (2026-09-26; READ-FULL)
 bears on: Q5, C5
 limit: a quick skim; he ends "dubious", not settled.

F4. Following the citation graph is the default way to discover a field. Go back through references and forward through citing papers. Papers cited in common and authors who recur mark the core. Repeat. Finding a survey ends the search.
 who: Terence Tao (Fields Medal); S. Keshav (Waterloo CS, 2007 note); Lilian Weng (ex-OpenAI, Lil'Log)
 evidence: Tao: "I often find it illuminating to sort the citing papers by the number of citations that they themselves have, as this tends to highlight particularly pivotal papers at the top of this sorted list." — https://terrytao.wordpress.com/career-advice/dont-be-afraid-to-learn-things-outside-your-field/. Keshav: "find shared citations and repeated author names in the bibliography. These are the key papers and researchers in that area." and "If you can find such a survey, you are done." — http://ccr.sigcomm.org/online/files/p83-keshavA.pdf. Weng: "With Google scholar and recursive citation search, I get to see quite a lot of papers but still not all of them." — https://lilianweng.github.io/faq/ (2026-09-26; READ-FULL)
 bears on: Q1, Q6, C1, C4
 limit: the graph stays inside field boundaries (see N4).

F5. Go broad through review articles and edited handbooks, then go granular through researchers' own pages. Edited volumes avoid getting only one person's view.
 who: Luke Muehlhauser (autodidact; later MIRI and Open Philanthropy). LessWrong karma 250.
 evidence: "Once textbooks and review articles have given you a good overview of the key concepts and terms, open and closed problems, studies and researchers on your chosen topic, it's time to go granular." — https://www.lesswrong.com/posts/37sHjeisS9uJufi4u/scholarship-how-to-do-it-efficiently (2026-09-26; READ-FULL)
 bears on: C2 (for), Q1
 limit: in his words, a good volume "does not protect you from the entire field being mostly misguided".

F6. Skim widely, read very few deeply, and throw away hard.
 who: Michael Nielsen (quantum computing); Sebastian Raschka (arXiv ML moderator 2018–21; sells books and a newsletter); Tyler Cowen (sells books)
 evidence: Nielsen: "You are almost certainly better off reading deeply in the ten most important papers of a research field than you are skimming the top five hundred." — https://aykuterdem.github.io/resources/principles-of-effective-research.pdf (third-party mirror; michaelnielsen.org returned 404). Raschka: "I realize that 95% of the stuff I captured is not that important" — https://sebastianraschka.com/blog/2023/keeping-up-with-ai.html. Cowen: "I start ten or so books for every one I finish." — https://marginalrevolution.com/marginalrevolution/2006/12/how_to_read_fas.html (2026-09-26; READ-FULL)
 bears on: Q2, Q6
 limit: Nielsen picks about a dozen deep reads a year out of the skim.

F7. He starts from a hypothesis and builds on it. Read the one to three most prominent pieces on each side, then write a bold premature claim. List its weaknesses, dig into the subquestion most likely to flip it, and switch sides when it does. Stop when you can find no more problems, then publish.
 who: Holden Karnofsky (co-founder of GiveWell and Open Philanthropy), describing his own practice.
 evidence: "The process looks less like “Read and digest everything out there on the topic” and more like “Read the 1-3 most prominent pieces on each side, then go.”" On stopping: "I can’t easily find more problems with this, so it’s time to see whether others can" — https://www.cold-takes.com/learning-by-writing/ (2026-09-26; READ-FULL)
 bears on: Q4, Q5, Q6, C1, C5; against C2
 limit: he says he cannot predict when an investigation will be done.

F8. Darwin's "golden rule" was to write down disconfirming facts at once, because those are forgotten first. He gathered facts widely, including from practitioners and not only from books. His key connection came from reading off-topic. His map was 30–40 labelled portfolios plus an index for each book.
 who: Charles Darwin, autobiography
 evidence: "whenever a published fact, a new observation or thought came across me, which was opposed to my general results, to make a memorandum of it without fail and at once". His sources: "by printed enquiries, by conversation with skilful breeders and gardeners, and by extensive reading." He read Malthus "for amusement". — https://www.gutenberg.org/cache/epub/2010/pg2010.txt (2026-09-26; READ-PARTIAL)
 bears on: Q3, Q4, Q5, C2, C3, C5
 limit: the payoff he names is that almost no objection was raised "which I had not at least noticed and attempted to answer". That is anticipation, not certainty.

F9. Try to kill your own idea early. Order tasks by how much they teach per unit of time. Rule out whole approaches with an argument, not a feeling.
 who: Jacob Steinhardt (Berkeley). He reports going from a year of little progress to "one project every four months on average".
 evidence: "Compared to other people I know, I try harder and earlier to show that my ideas can't work to solve a problem." — https://cs.stanford.edu/~jsteinhardt/ResearchasaStochasticDecisionProcess.html (2026-09-26; READ-FULL)
 bears on: Q5, Q6, C1, C5
 limit: one failed implementation does not rule out the whole approach.

F10. Research runs as explore, then understand, then distill. Pivot when you stop learning. A running "highlights" document is where connections get spotted. Excitement about a result is a warning sign.
 who: Neel Nanda (leads mechanistic interpretability at Google DeepMind). Incentive: he recruits MATS scholars. Alignment Forum karma 37 and 23. He discloses the process post was co-written with Gemini 2.5 Pro.
 evidence: "If you've learned nothing in 2 hours, pivot to another approach." and "Excitement is evidence of bullshit: Generally, most true results are not exciting, but a fair amount of false results are." — https://www.alignmentforum.org/posts/jP9KDyMkchuv6tHwm/how-to-become-a-mechanistic-interpretability-researcher. "A key practical tip is to keep a highlights doc of particularly interesting results, this makes it easier to spot connections" — https://www.alignmentforum.org/posts/hjMy4ZxS5ogA9cTYK/how-i-think-about-my-research-process-explore-understand (2026-09-26; READ-FULL)
 bears on: Q2, Q4, Q6, C3, C4 (fads)
 limit: the exploring is of data and experiments. For the literature his advice is "breadth over depth" plus LLM summaries.

F11. He connects ideas in a daily notebook reviewed every week or two. He chooses problems by goal because a field that reads the same papers produces duplicate ideas.
 who: John Schulman (OpenAI co-founder; TRPO and PPO). Written for the OpenAI Fellows program.
 evidence: "Researchers around the world are reading the same literature, which leads them to similar ideas." Also: "Often, when I revisit my journal entries during the week in review, I’ll fill in a missing piece in a puzzle, which didn’t occur to me at the time." — http://joschu.net/blog/opinionated-guide-ml-research.html (2026-09-26; READ-FULL)
 bears on: Q4, C3, C6 (duplication across a whole field)
 limit: none stated

F12. Linked notes produce combinations nobody searched for.
 who: Niklas Luhmann, sociologist; essay read in Manfred Kuehn's translation.
 evidence: "The slip box provides combinatorial possibilities which were never planned, never preconceived, or conceived in this way." — http://luhmann.surge.sh/communicating-with-slip-boxes (2026-09-26; READ-FULL)
 bears on: Q4, C3 (for)
 limit: "The slip box needs a number of years in order to reach critical mass. Until then, it functions as a mere container…"

F13. Citation counts and fame are often decoupled from being right.
 who: Dan Luu (engineer; Patreon-funded); Feynman (Caltech 1974 address); Rota (MIT)
 evidence: Luu on Chase & Simon 1973: "a "classic" which has been cited a whopping 7449 times in the literature" that "used an absurdly small sample size of one chess player at each skill level." — https://danluu.com/dunning-kruger/. Feynman on Young's rat-maze paper: "his papers are not referred to, because he didn’t discover anything about the rats." — https://calteches.library.caltech.edu/51/2/CargoCult.htm. Rota cited irrelevant papers as an experiment and received grateful letters — https://www.ams.org/notices/199701/comm-rota.pdf (via r.jina.ai; direct request got 403) (2026-09-26; READ-FULL)
 bears on: Q2, C4 (for)
 limit: Luu: "clever, contarian" ideas are the ones that "become viral relative to their correctness."

F14. The opinion of people you respect is signal; fame is noise.
 who: Paul Graham (YC founder; incentive: the YC ecosystem); Patrick Collison (Stripe; funds Emergent Ventures and Pioneer)
 evidence: "The opinion of people you respect is signal. Fame, which is the opinion of a much larger group you might or might not respect, just adds noise." — https://paulgraham.com/greatwork.html. "Status lags by a generation or more." — https://patrickcollison.com/advice (2026-09-26; READ-FULL)
 bears on: Q2, C4
 limit: Graham says that if you cannot state precisely what the authorities miss, you are drifting toward the cranks.

F15. Rare information lives outside papers: in shared community knowledge, raw data, and dense primary sources.
 who: Andrej Karpathy (built arxiv-sanity); Nabeel Qureshi (essayist)
 evidence: "each field has knowledge that doesn’t get serialized into papers but is instead spread across a shared understanding of the community" — https://karpathy.github.io/2016/09/07/phd/. "On foreign policy, read books published by university presses -- not The Atlantic or The Economist or whatever." — https://nabeelqu.co/understanding (2026-09-26; READ-FULL; Qureshi read through silver after repeated 429s)
 bears on: Q1, Q3
 limit: getting the community knowledge requires being physically present.

## Against the claims

X1. Against C2: several start work, or think first, before reading broadly.
 who: Steven Weinberg (Nobel 1979); Hamming (Bell Labs, Turing Award); Qureshi; Andy Matuschak (independent researcher)
 evidence: Weinberg: "I did learn one big thing: that no one knows everything, and you don't have to." — https://www.nature.com/articles/426389a (READ-PARTIAL, paywall). Hamming: "get the problem reasonably clear and then refuse to look at any answers until you've thought the problem through carefully" — https://www.cs.virginia.edu/~robins/YouAndYourResearch.html. Qureshi: "Start by thinking about the question yourself before reading a bunch of stuff about it." Matuschak: "I noticed myself dodging difficult work by diving down literature rabbit holes" — https://andymatuschak.org/stillness (2026-09-26)
 bears on: C2, Q6
 limit: Darwin and Muehlhauser do the opposite. Darwin refused to write even "the briefest sketch" of his theory "to avoid prejudice", which inverts Karnofsky's write-early method.

X2. Against C4 as stated: these practitioners use popularity among experts as a guide. Citation counts, papers cited in common, prizes and consensus all steer them. What they distrust is popularity with the general public.
 who: Gwern, Muehlhauser, Nielsen, Tao, Scott Alexander
 evidence: Gwern on 667 citations: "which for an arcane economics paper like this, is a remarkably high citation (usually you’d see <100), and so we can be confident". Muehlhauser: "review articles will often be listed near the top of the results because review articles are cited widely." Nielsen: "look at what wins prizes (of all sorts)." Alexander: "Scientific consensus is the best tool we have for seeking truth." and "The correct conclusion is that Vox shouldn’t be trusted about any science more complicated than the wedge vs. inclined plane." — https://slatestarcodex.com/2017/04/17/learning-to-love-scientific-consensus/. Tao, on a twist that previous experts supposedly missed: "there is a high probability that this twist contains a serious technical flaw that the previous experts were aware of and avoided" — https://terrytao.wordpress.com/career-advice/be-sceptical-of-your-own-work/ (2026-09-26; READ-FULL)
 bears on: C4, Q2
 limit: nobody describes sampling unpopular sources on purpose. The one exception is Gwern checking low-ranked hits when chasing a known target.

X3. Against C5: hunting the other side lowers confidence, rarely converts anyone, and entrenches error when it is done only against unwelcome results.
 who: Scott Alexander; Daniel Kahneman (Nobel 2002); Feynman; Karnofsky
 evidence: Alexander: "Decrease your confidence about most things if you’re not sure that you’ve investigated every piece of evidence." — https://slatestarcodex.com/2014/12/12/beware-the-man-of-one-study/. Kahneman on the critique–reply–rejoinder format: "hardly anyone ever admits an error or acknowledges learning anything from the other." His adversarial collaborations ended in "narrowed differences of opinion", not agreement — https://bear.warrington.ufl.edu/brenner/mar7588/Papers/kahneman-collab-essay2003.pdf (mirror). Feynman on measurements after Millikan: "When they got a number that was too high above Millikan’s, they thought something must be wrong—and they would look for and find a reason why something might be wrong." (2026-09-26; READ-FULL)
 bears on: C5, Q5
 limit: Karnofsky: "Half the time, all of this work just ends up with me agreeing with conventional wisdom or “the experts” anyway".

X4. Against C6: the most productive team described never split the work at all.
 who: Kahneman (on working with Tversky); Schulman; Hamming
 evidence: Kahneman: "we avoided any explicit division of labor." and "We soon learned that joint collaboration with any third party should be avoided because we became competitive in a threesome." Schulman: "idea-driven research is most effectively carried out by “teams” of 1-2 people." Hamming: "When you get too many sound absorbers, you give out an idea and they merely say, ``Yes, yes, yes.''" (2026-09-26; READ-FULL)
 bears on: C6, Q7
 limit: Schulman says a shared goal does let a larger team attack different parts.

X5. Against "more reading means more progress" (a limit on C1).
 who: Hamming
 evidence: "there's no effect named after him because he read too much. If you read all the time what other people have done you will think the way they thought." (2026-09-26; READ-FULL)
 limit: in his words, "it is not the amount, it is the way you read that counts."

## Not covered by any claim

N1. Keep a standing list of open problems and test everything new against it. You match incoming information rather than search for it. A published list also brings in pointers from readers.
 who: Hamming; Feynman, as told by Rota; Collison
 evidence: Hamming: "They have something between 10 and 20 important problems for which they are looking for an attack. And when they see a new idea come up, one hears them say ``Well that bears on this problem.''" Rota: "Every time you hear or read a new trick or a new result, test it against each of your twelve problems to see whether it helps." Collison: "Pointers to interesting readings on these topics are always welcome, as are pointers to responses." — https://patrickcollison.com/questions (2026-09-26; READ-FULL)
 bears on: Q1, Q4

N2. Decide whom to trust by going deep on one small slice yourself. Karnofsky also visits sites, pulls raw data, checks attributions, and once found a "circular" malaria dataset.
 who: Karnofsky
 evidence: "I then look for people who seem to be reasoning well about the part(s) of X I understand, and put trust in them on other parts of X." — https://www.cold-takes.com/minimal-trust-investigations/ (2026-09-26; READ-FULL)
 bears on: Q2, Q3, Q5

N3. Train your filter on bad examples and on your own predictions.
 who: Karpathy; Chris Olah (Anthropic co-founder; a self-described "rough note"); Nanda
 evidence: Karpathy: "What you really want is to also have exposure to a large number of bad papers and one way to get this is by reviewing papers." Olah: "Pay attention when other people try ideas you’ve had. How did the results compare with your expectations?" — https://colah.github.io/notes/taste/. Nanda: "Predict methods, results, and limitations before revealing them." (2026-09-26; READ-FULL)
 bears on: Q2

N4. The main thing hiding rare information is terminology: the other field calls it something else.
 who: Muehlhauser; Gwern ("Cowen's Law", "Rosetta stones"); Rota (Riesz republished the same result for different communities)
 evidence: "It took me months to discover that professionals call this the psychology of adjustment." (2026-09-26; READ-FULL)
 bears on: Q3, C1

N5. Once something is found, make sure it stays found, and publish so readers can supply what you missed: Gwern re-hosts and fixes metadata, Weng asks readers for missing papers, Karnofsky publishes so others can find the weaknesses.
 evidence: "regularly making and keeping excerpts creates a personalized search engine, in effect." — https://gwern.net/search (2026-09-26; READ-FULL)
 bears on: Q6, Q7

N6. Triggers for where to look: messy fields and misgivings you set aside earlier.
 evidence: Weinberg: "My advice is to go for the messes — that's where the action is." Graham, on early misgivings: "When you've gotten further into the subject, come back and check if they're still there." (2026-09-26)
 bears on: Q1, Q2

## Frontier
- Million Short: a search overlay that removes the top 100 to 1M domains from results, a tool built against popularity. Gwern's external links.
- Gwern had OpenAI Deep Research find the PriceLight study that Patrick McKenzie gave up on after 30 minutes. An agent-versus-human data point. search-case-studies.
- Mellers, Hertwig & Kahneman 2001 appendix: a written protocol for adversarial collaboration. Latham, Erez & Locke 1988 did it first. Kahneman PDF.
- Rare-source lanes Gwern names: Internet Archive Scholar, ERIC, Wellcome Library, ProQuest paid scans, and Archive Team's Google Reader dump.
- Gwern's "Leprechaun hunting" and "The Neural Net Tank Urban Legend": case studies in tracing citations back.
- Dan Luu, "How bad are search results?" (https://danluu.com/seo-spam/): a measured comparison of search engines. Probably for the OSINT lane.
- Andy Matuschak, "On breadth vs. depth in learning" and "Augmenting scholarship: a proto-proposal" (Patreon; blocked).
- Karnofsky, "The Wicked Problem Experience" (next in his series). Nanda's ideation post.
- Martin Schwartz, "The importance of stupidity in scientific research" (2008), via Tao.

## Lane state
- gwern.net: BLOCKED on direct TLS (curl and silver both failed); READ-FULL through r.jina.ai.
- michaelnielsen.org: MISSING (404); read the PDF mirror instead.
- AMS Rota PDF: BLOCKED (403); read through r.jina.ai. The Williams mirror turned out to be a different Rota paper.
- nabeelqu.co: 429 on curl and jina; READ through a silver session.
- Patreon (Matuschak): BLOCKED by a bot check.
- Nature (Weinberg): READ-PARTIAL; only lessons 1–2 visible.
- Nathan Lambert, "My path into AI": EMPTY on method.
- Jason Wei: READ-FULL, but mostly about promoting work. "Advertising work on twitter is probably the highest return per amount of effort", which suggests popularity is partly produced by effort.
- Karpathy PhD guide: READ-FULL, 2 of 8 sections relevant.

## Source register (all 2026-09-26)
- https://gwern.net/search — READ-FULL (jina)
- https://gwern.net/search-case-studies — READ-FULL (jina)
- https://www.cs.virginia.edu/~robins/YouAndYourResearch.html — READ-FULL
- http://joschu.net/blog/opinionated-guide-ml-research.html — READ-FULL
- https://aykuterdem.github.io/resources/principles-of-effective-research.pdf — READ-FULL
- https://michaelnielsen.org/blog/principles-of-effective-research/ — MISSING
- https://karpathy.github.io/2016/09/07/phd/ — READ-FULL
- http://ccr.sigcomm.org/online/files/p83-keshavA.pdf — READ-FULL
- https://colah.github.io/notes/taste/ — READ-FULL
- https://www.alignmentforum.org/posts/jP9KDyMkchuv6tHwm/… , /hjMy4ZxS5ogA9cTYK/… , /Ldrss6o3tiKT6NdMm/… , /cbBwwm4jW6AZctymL/… — READ-FULL
- https://cs.stanford.edu/~jsteinhardt/ResearchasaStochasticDecisionProcess.html — READ-FULL
- https://paulgraham.com/greatwork.html — READ-PARTIAL (grep-guided)
- https://nabeelqu.co/understanding — READ-FULL (silver)
- https://www.cold-takes.com/learning-by-writing/ ; /minimal-trust-investigations/ — READ-FULL
- https://slatestarcodex.com/2014/12/12/beware-the-man-of-one-study/ — READ-FULL; /2017/04/17/learning-to-love-scientific-consensus/ — READ-PARTIAL; /2019/12/11/… — MISSING
- https://patrickcollison.com/advice ; /questions — READ-FULL / READ-PARTIAL
- https://marginalrevolution.com/marginalrevolution/2006/12/how_to_read_fas.html — READ-FULL
- https://terrytao.wordpress.com/career-advice/ plus 10 posts — READ-FULL
- https://www.ams.org/notices/199701/comm-rota.pdf — READ-FULL (jina)
- https://web.williams.edu/Mathematics/lg5/Rota.pdf — wrong paper
- https://danluu.com/dunning-kruger/ ; /look-stupid/ — READ-FULL; /programming-blogs/ — EMPTY
- https://andymatuschak.org/stillness — READ-PARTIAL; notes.andymatuschak.org Evergreen notes — READ-FULL; Patreon posts — BLOCKED
- https://sebastianraschka.com/blog/2023/keeping-up-with-ai.html — READ-FULL
- https://lilianweng.github.io/faq/ — READ-FULL
- https://www.jasonwei.net/blog/practicing-ai-research — READ-FULL
- https://www.interconnects.ai/p/my-path-into-ai — EMPTY
- https://calteches.library.caltech.edu/51/2/CargoCult.htm — READ-PARTIAL
- https://www.gutenberg.org/cache/epub/2010/pg2010.txt — READ-PARTIAL
- http://luhmann.surge.sh/communicating-with-slip-boxes — READ-FULL
- https://bear.warrington.ufl.edu/brenner/mar7588/Papers/kahneman-collab-essay2003.pdf — READ-PARTIAL
- https://www.nature.com/articles/426389a — READ-PARTIAL
- https://www.lesswrong.com/posts/37sHjeisS9uJufi4u/… — READ-FULL