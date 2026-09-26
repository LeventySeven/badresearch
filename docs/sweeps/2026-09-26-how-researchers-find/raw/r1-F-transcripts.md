<!-- AGENT OUTPUT — R1-F local transcripts. Returned by a subagent, not read by the chair unless a row says so. -->

Every `file:line` below is under `/Users/seventyleven/Desktop/researchfms/Transcripts/`. These files are notes built from auto-captions, so every row is **CAPTION-PARAPHRASE**, read 2026-09-26. "hdr" is the line where the file names the speaker. I re-grepped every cited line myself.

## Findings
F1. Systematic reviewers want every study that bears on a question, not the best few. Galen Adams says LLM search fails because it chases one ideal paper. Deep-research tools found about 15–20% of the relevant literature and leaned towards secondary reviews. Nobody has solved when to stop screening; the pattern that works is to search wide, then let two models screen the results down. She uses several databases because PubMed's own search misses papers that Embase finds.
 who: Galen Adams, Brown Center for Evidence Synthesis, former hospital librarian, 30+ evidence syntheses (hdr AI2.md:5944, :5951); nothing to sell
 evidence: "most of these LLMs want to find the perfect article. … What is needed instead is finding the breadth of the evidence" — TRANSCRIPTS_AI2.md:6037-6038; "when do you stop? … how do you know you found everything relevant?" :6069-6070; :6085, :6112, :6115, :6141
 bears on: Q1, Q2, Q3, Q6, C2, C4
 limit: for a narrative review (5–10 best sources) LLMs do fine (:5981); her deep-research figures are informal (:6109)

F2. Parallel research runs through one shared queue of ideas. Workers pull ideas and try them, and whatever works goes onto a shared branch. With untrusted workers, results arrive as commits that build on each other, and a trusted pool checks them cheaply.
 who: Andrej Karpathy on No Priors (hdr KARPATHY.md:13225)
 evidence: "there is a queue of ideas … workers that pull items … Whatever works just gets put on the feature branch" — KARPATHY.md:13531-13535; "commits can build on each other" :13693
 bears on: Q7, C6
 limit: "If you can't evaluate then you can't auto research it" (:13583); he calls the design unfinished (:13683)

F3. In a fleet of 64–128 research agents, the agents ignored each other's messages until those messages were delivered as user turns. Agent names doubled as a record of who was doing what. A separate judge decided when work was done, because agents judging themselves quit early. Harry also says to read all the code first and then run a few targeted tests, rather than guess at hypotheses.
 who: Harry (ML researcher) and Charlie (post-training startup), on a Cursor-hosted panel (hdr CURSOR.md:974)
 evidence: models "didn't really pay attention to each other enough" — CURSOR.md:1005; "read all the code first … then make a small set of targeted tests" :1070; "self-judges it cheats" :1045; :1009, :1013, :1068
 bears on: Q7, C6, Q6, C2
 limit: one fleet, nothing measured; the reading can cost ~500k tokens (:1071)

F4. Choose topics by forecasting. Ask which questions nobody is talking about yet, and chain if-then predictions to get ahead of the work everyone else will do.
 who: Will Brown, Prime Intellect, author of `verifiers` (hdr AI_AGENT_SYSTEMS.md:53854)
 evidence: "what are the questions that no one's even talking about? And this is like not an easy thing to do" — _queue/agentsys/txt/ZZg6cHltE8B.txt:208 (raw transcript); notes :54222, :54236-54237
 bears on: Q1, Q3
 limit: he calls his own bet "not a very risky" one (:54244)

F5. Majority is not truth. Training to minimise average error rewards agreeing with whatever text repeats most. Second- and third-hand rewrites survive deduplication, so go to the primary source. Low confidence in an answer should trigger more evidence-gathering.
 who: Jimmy Ba, xAI co-founder (hdr XAI.md:1368); talking his book, he calls X "the number-one news application" (:1556)
 evidence: "Majority agreement is not the same thing as physical truth." — XAI.md:1659; :1689, :1632, :1647
 bears on: C4, Q2, Q6
 limit: no formula or threshold disclosed (:1698)

F6. Citations lag and are only a rough guide. The diffusion paper was overlooked when it was published. Cho told Dinh that normalizing flows "couldn't work". Szegedy and Goodfellow's work took the impact from Biggio's earlier attack.
 who: Hugo Larochelle and Kyunghyun Cho (hdr ICML_TRANSCRIPTS.md:15713-15714); Battista Biggio (:12109)
 evidence: "Largely overlooked at publication" — ICML_TRANSCRIPTS.md:15745; :15721, :15767; "much more impact than Biggio's because they fooled models claiming superhuman performance" :12158
 bears on: C4
 limit: they still rank candidates with a citation spreadsheet (:15720)

F7. Rare knowledge sits in other communities and in older work. Biggio went back to the standard SVM textbooks, catalogued attacks that were "rediscovered over and over", and urges people to search work from before deep learning. Kambhampati says ML/NLP researchers and planning researchers don't know each other's work.
 who: Biggio; Subbarao Kambhampati, ASU (hdr :817), whose tutorial calls itself "opinionated" (:833)
 evidence: "go deeper and search for pre-deep-learning work" — ICML_TRANSCRIPTS.md:12164; :12120, :12161; "bidirectional ignorance" :830
 bears on: Q3, C3

F8. The answer to a strange result was in an old paper's appendix. Labs rarely publish the details of how they train current models after pretraining, and the best detail is in older papers. The InstructGPT appendix lists who the annotators were, and that explained why the models' opinions shifted.
 who: an unnamed CS336 lecturer who co-advises with Percy Liang (hdr STANFORD.md:21330-21334); my guess is Hashimoto, but the captions do not say
 evidence: "look at the appendix of the InstructGPT paper, which lists the annotators" — STANFORD.md:21845; :21363, :21365
 bears on: Q3
 limit: vendors now release nothing of this kind (:21368)

F9. Keep a map across many sources. Tatsu read all the LLM papers into a spreadsheet of about 19 model releases and compared what changed with what stayed the same, to work out which choices actually matter. Larochelle kept a citation spreadsheet for the same kind of comparison.
 who: Tatsu, CS336 Lecture 3 (STANFORD.md:6646; older unaudited note format); Larochelle (ICML_TRANSCRIPTS.md:15720)
 evidence: "read all the LLM papers, see what changed vs. what stayed common, infer what's really important" — STANFORD.md:6657; :6658
 bears on: Q4, C3

F10. Long one-on-one interviews, combined with inputs from elsewhere. Three inputs (a user request, social-media research, and a complaint found "by digging deeper") produced Snapchat Stories, which nobody had asked for.
 who: Evan Spiegel, Snap CEO (hdr LENNYS_PODCAST.md:13903); a founder telling the story after the fact
 evidence: "the survey model of listening is not particularly helpful; going deep with one person for an hour or two is" — LENNYS_PODCAST.md:14016; :14025, :14031
 bears on: C3, Q1

F11. An independent insight needs distance from what everyone else is saying. His test is to ask why you, of all people, would have it. He also says that what restaurants would have told him if asked directly was the wrong priority.
 who: Jason Droege, Scale AI CEO (hdr LENNYS_PODCAST.md:32554); he states Scale's financial incentive openly (:32695)
 evidence: "If your research is heavily influenced by what the world around you is saying, you will not have an independent insight." — LENNYS_PODCAST.md:32791; :32794, :32796, :32782
 bears on: Q3, C4
 limit: he says he is not "a great independent thinker" (:32801)

F12. An AI-generated hypothesis was checked against a professor's unpublished CRISPR screens, reached by cold email. The project itself began when a professor walked over after a talk. Ideas are ranked by debate and Elo scores because scientists "are not short on ideas". Debate summaries go into a memory the agents share.
 who: Vivek, DeepMind Med-PaLM lead (hdr STANFORD.md:19168); promoting Co-Scientist, and he calls the result "unvalidated" (:19789)
 evidence: "he took the hypotheses and wrote a cold email to this professor" — STANFORD.md:19784-19785; :19214, :19486, :19497, :19513
 bears on: Q3, Q2, Q7, Q1

F13. Schulman runs literature searches through GPT-5 Pro and pastes his lab notebook into models. He distrusts academic baselines and says you can't yet tell which recent ideas matter. He notes that ideas which come too early come back later; his Universe project was "a decade too early".
 who: John Schulman, OpenAI co-founder (hdr CURSOR.md:1465-1466)
 evidence: "a lot of academic papers have baselines that are nerfed in some way" — CURSOR.md:1647; :1599, :1618, :1631, :1664, :1500
 bears on: Q1, Q2, Q4, C4

F14. Casetext modelled its legal research on "the world's best lawyer". Clarify the question, write 20–50 queries, read every page of every result while taking notes, then compile. If the searches keep missing, go back and search again.
 who: Jake Heller, Casetext founder (hdr YC_ROOT_ACCESS.md:13607); sells legal AI
 evidence: "formulate 20–30 or even 50 different search queries … read every single page of every single result" — YC_ROOT_ACCESS.md:13625; :13627
 bears on: C2, C1

F15. Knowing when to stop means committing only when your confidence is well calibrated. In a game of guessing a hidden rule, models are badly overconfident, and they propose rules more complicated than the real ones.
 who: an unnamed Hugging Face presenter (hdr HUGGINGFACE.md:7521)
 evidence: "The best scientists have good calibration — they know when they know enough." — HUGGINGFACE.md:7701; :7542, :7716, :7726, :7745
 bears on: Q6, C5

F16. Retrieve many examples, not a few, so you don't anchor on one, then work out how they line up. Glassman says insight comes from "alignable differences and commonalities", a term from structure-mapping theory.
 who: Elena Glassman, Harvard HCI (hdr AI2.md:10779)
 evidence: "we retrieved many many many examples" — AI2.md:10870; :10874, :10883, :11298
 bears on: C3, C2
 limit: shown useful only within one research community (:11107)

F17. Confirm a finding by joining independent sources. Ransomware ads on underground forums were traced back to activity on Anthropic's own platform. Investigators also use infrastructure indicators shared across the security community.
 who: Anthropic Threat Intelligence (Jacob Klein, Alex; hdr ANTHROPIC.md:5603); a company comms video
 evidence: "The team traced those ads back to the activity seen on the platform" — ANTHROPIC.md:5772; :5755, :5794
 bears on: C3, C5, Q7

F18. The opposing evidence came from a reviewer, not from the author. An ablation a reviewer asked for overturned what the literature believed, and he calls it his best insight.
 who: Claas Voelcker (hdr COHERE_LABS.md:2807)
 evidence: ablation "added only during the paper's rebuttal, at a reviewer's explicit request" — COHERE_LABS.md:3102; :3107
 bears on: C5, Q3

F19. Use models to tell you where you are wrong, and turn a disagreement into a number you track over time.
 who: Jascha Sohl-Dickstein (hdr STANFORD.md:32439); publicly argues for short timelines to AGI
 evidence: "please do use them to to tell you all the ways you're wrong" — STANFORD.md:32624; :32757
 bears on: C5

## Against the claims
A1 (C2). Expertise shrinks the search, while raw intelligence widens it with about 100 parallel attempts. Knowing when to stop is a matter of judgment. Yu Su, OSU professor and CEO of NeoCognition, which sells continual learning (hdr AI_AGENT_SYSTEMS.md:16249). "Expertise compresses the search space instead." — :16352; :16351, :16341.

A2 (C6's remedy). Factory tried ten agents in parallel and got conflicts and duplicated work. They switched to one worker at a time, each leaving a written handoff with six fields. Luke Alvoeiro, a vendor (hdr AI_AGENT_SYSTEMS.md:5251). "Failure 3: they duplicate work." — :5423; :5420, :5430, :5398. Limit: tested on software builds only.

A3 (C5). Counter-evidence from admired experts was wrong: Elon gave early OpenAI a "zero% chance", and Cho said normalizing flows "couldn't work" (F6). Altman's only method was to keep going. Altman (hdr YC.md:38421): "What if he's right?" — YC.md:38705; :38700.

A4 (C1 as search). The prior work turned up only after the ideas had been rediscovered. Sanjeev Arora (hdr ICML_TRANSCRIPTS.md:3290): "While rediscovering these ideas, they found related work" — :4006; see also Biggio :12161.

## Not covered by any claim
N1. Popularity as contamination. A benchmark builder removed "the very highly cited papers" because the model will have memorized them. Unnamed Ai2 presenter (hdr AI2.md:8167). Evidence: AI2.md:8690-8691. Bears on C4, Q2.

N2. Circular reporting. Texas DPS needed tools for "avoiding circular reporting" and one shared operating picture, and teams on the ground overturned the first flood models. Capt. John Miller, speaking on Palantir's stage (hdr PALANTIR.md:9013). Evidence: :9096-9097, :9080-9081. Bears on Q7, C5; pairs with F5.

N3. Some information lives in people who hear many live reports. A mentor's value is knowing which questions interviewers are asking right now, since "the information itself is all on the internet". Anton Nazarov, who sells mentorship; Russian-language source (hdr OSOZNANNAYA_MERKANTILNOST.md:8, :25). Evidence: :1020-1021. Bears on Q3.

N4. Signs that a number was invented: round or huge figures, too many figures ending in 9 (a check used to catch tax fraud), absolute claims, and precision with no stated way of measuring it. The owner of the channel "You look like a geek", who teaches CV fabrication and admits «он сам за это не шарит» ("he himself doesn't really understand this", :752). Evidence: YOU_LOOK_LIKE_A_GEEK.md:748, :774. Bears on Q2.

N5. Stop researching when the choice doesn't matter. Ask how far apart the options really are and how hard it would be to switch later. Chip Huyen (hdr LENNYS_PODCAST.md:30932). Evidence: :30970, :30974-30976. Sherwin Wu: "most of it is noise" (:21323). Bears on Q6.

## Frontier
- Structure-mapping theory (Gentner) as a mechanism for C3 — AI2.md:11287
- Biggio & Roli, "Wild Patterns" (2018), and Nelson/Joseph/Tygar, *Adversarial Machine Learning*: maps of work rediscovered across communities — ICML_TRANSCRIPTS.md:12161-12162
- Schulman's 2020 blog post on effective research — CURSOR.md:1611
- Galen Adams' continuously updated review of AI tools for systematic reviews; the Wallace/Trikalinos pipeline figure — AI2.md:5967, :5997
- Kaggle: a rival lab re-ran a benchmark using its own API's context compaction and published better numbers — AI_AGENT_SYSTEMS.md:25368-25373
- A stopping rule for agents sharing one store: "no new findings for N cycles" — AI_AGENT_SYSTEMS.md:3128

## Lane state
- Enumerated live: 44 `*TRANSCRIPT*.md` files, 630,071 lines; I grepped the vocabulary across all 44. COURSERA had 253 hits that I left unread, because course material is not practitioners describing their own practice.
- READ-PARTIAL (hits read in context): AI2, AI_AGENT_SYSTEMS, ANTHROPIC, A16Z, COHERE_LABS, CURSOR, GOOGLE_DEEPMIND, HUGGINGFACE, ICML, KARPATHY, LENNYS_PODCAST, OPENAI, OSOZNANNAYA_MERKANTILNOST, PALANTIR, STANFORD, XAI, YC, YC_ROOT_ACCESS, YOU_LOOK_LIKE_A_GEEK.
- Grep lines only: LANGCHAIN, MICROSOFT_BUILD, DEEPLEARNINGAI, MISTRAL_COHERE_AI2.
- EMPTY (0 hits): YC_ROOT_ACCESS_PLAYBOOK, NEXT_BATCH, CLAUDE_CODE_101, APPLE_DESIGN.
- Not opened: the other 16 files (Apple ×3, AWS, Google ×2, NVIDIA, Microsoft, Vercel, Warp, LlamaCon, Meta, Claude ×2, OpenAI DevDay, DLAI courses), all vendor talks with few hits.
- Excluded for provenance: the Percy Liang section (STANFORD.md:1251-1330) carries an audit note saying about 85% of its earlier text was fabricated. The Jason Wei (STANFORD.md:2049) and Nathan Labenz (A16Z.md:385) sections are in the older unaudited format. F9's Tatsu section is in that format too.

## Source register
- /Users/seventyleven/Desktop/badresearch/docs/sweeps/2026-09-26-how-researchers-find/BRIEF.md — READ
- /Users/seventyleven/Desktop/researchfms/TRANSCRIPT_RULES.md; /Users/seventyleven/Desktop/researchfms/AGENTIC_SEARCH_SPEC.md — READ-PARTIAL
- /Users/seventyleven/Desktop/researchfms/Transcripts/ — the 19 files listed as READ-PARTIAL above — READ-PARTIAL
- /Users/seventyleven/Desktop/researchfms/Transcripts/_queue/agentsys/txt/ZZg6cHltE8B.txt — READ-PARTIAL (lines 203-225)