<!-- G4 talks/transcripts (agent output, 2026-10-10) -->

## Findings

F1. **A whole expert community filtered out the key direction because of its background, and one cheap side experiment overturned years of work.** Brown saw humans think for minutes in hard spots while his bot acted in milliseconds. He tested search and found it was worth about 100,000× more scaling. He had scaled 100× in 3–4 years, and "we changed our approach completely." He gives four reasons the field missed it:
- **Culture:** game theorists wanted the whole equilibrium computed and verifiable up front.
- **Measurement:** experiments with search were hard to measure.
- **Incentive:** the annual competition capped test-time compute at 2 CPU cores.
- **Underestimation:** he would have guessed 10×.

    who: Noam Brown — OpenAI (Libratus, Pluribus, o1).
    evidence: the passage runs ≈6–14 min of https://www.youtube.com/watch?v=eaAonE58sLU (2026-10-10; CAPTION-PARAPHRASE).
    bears on: E1, E2, Q2; K6, K17, K12; against "more knowledge → better filtering"
    limit: told after the fact, and he is the one who won.

F2. **Experts stop searching where they believe things are settled, and that is where the misses sit.** Karpathy says he has trained nanochat "thousands of times" and tuned it by hand for two decades. An overnight AutoResearch loop still found weight decay he had forgotten on the value embeddings and under-tuned Adam betas. His explanation: parameters "jointly interact", so tuning one moves the others.
    who: Andrej Karpathy.
    evidence: ~/Desktop/researchfms/Transcripts/TRANSCRIPTS_KARPATHY.md:13502-13516 (No Priors, kwSVtQ7dziU; Source block present; CAPTION-PARAPHRASE).
    bears on: E1, E3; K8 (the stop), K17. Extends g1 F4 (tuned baselines) to an expert's own baseline.
    limit: there is an objective metric, so a dumb search can be checked.

F3. **Forty years of domain expertise produced the wrong call when the requirements changed.** Vahdat, Google's networking lead, argued for Ethernet in the TPU v2 interconnect from "40 years of history behind me and always been right." He says "it turned out I was wrong," and the non-Ethernet design "has stood the test of time".
    who: Amin Vahdat (Google infrastructure).
    evidence: TRANSCRIPTS_STANFORD.md:20160-20178 (CS153, VeTqsCpcDgg; Source block present; CAPTION-PARAPHRASE).
    bears on: E1, E2; against the owner's filtering claim; connects g1 F2 (Chung, "less to unlearn").

F4. **Breadth peaked while he was an outsider and shrank as he became an expert. Rare knowledge came from asking people.**
    who: Sholto Douglas (Google DeepMind, now Anthropic; an ex-McKinsey hire with no PhD).
    evidence:
    - "I was obsessively reading papers every night. Funnily enough, I read much less widely now… If you just read all the NLP work and all the computer vision work and like all the robotics work, you see all these patterns that start to emerge across subfields" — https://www.dwarkesh.com/p/sholto-douglas-trenton-bricken (01:49:41).
    - On the outsider's other advantage: "you can just go and ask all the algorithms experts and all the systems experts everything they know" (same page, ~01:46).
    (2026-10-10; READ-FULL — written transcript)
    bears on: E1, E3, C2; K3, K5, K12
    limit: being at Google gave him access to those experts.

F5. **The best information is unpublished. Without lab feedback, judging what matters ("taste") is hard.**
    who: Douglas, Trenton Bricken (Anthropic interpretability), Dwarkesh Patel.
    evidence (same page, 03:05:56–03:06:55):
    - Douglas: "Most people… refer to an internal narrative."
    - Bricken: "If it works well, it's probably not being published."
    - Patel: "now nothing worth reading is published."
    - Douglas: problem taste is "really tough unless you have the feedback signal what will work at scale."
    (READ-FULL)
    bears on: E3, Q3; K10, K16; connects g1 A3 (Keller: "biglab people read almost zero papers")
    limit: this applies to frontier-scale work. Douglas points to interpretability as "legible from the outside."

F6. **Pruning happens early and on a massive scale, but early verdicts can flip at scale.**
    who: Douglas; Jeff Dean and Noam Shazeer (Google).
    evidence:
    - Douglas: "paring that down and shot calling, under very imperfect information… things which can help at smaller scales can actually hurt at larger scales" — sholto-douglas-trenton-bricken (00:40:32–00:41:40).
    - Dean: "a 1/1000th scale problem and then vet 100,000 ideas on that" — https://www.dwarkesh.com/p/jeff-dean-and-noam-shazeer (~00:44:55).
    (READ-FULL)
    bears on: E1, E2; K8. This is the human form of g3 F2: an early verdict is safe only if later evidence can still overturn it.

F7. **Whether to drop a direction when experiments contradict it is decided top-down, because in neural-net work a contradiction is weak evidence.**
    who: Ilya Sutskever; Jeff Dean; Noam Shazeer.
    evidence:
    - Sutskever: "The top-down belief is the thing that sustains you when the experiments contradict you… How do you know if you should keep debugging or you conclude it's the wrong direction? It's the top-down." — https://www.dwarkesh.com/p/ilya-sutskever-2 (01:33:14).
    - Dean: nets are "so tolerant of noise. You can have things set up kind of wrong in a lot of ways."
    - Shazeer: a bug sometimes "makes your model better. Then you discover something new" — jeff-dean-and-noam-shazeer (01:07:04–01:07:15).
    (READ-FULL)
    bears on: E2; extends g1 A1 (Achiam: "assume there's a bug")
    limit: Sutskever's prior is aesthetic ("beauty, simplicity, elegance, correct inspiration from the brain"). By his own account it is not checkable.

F8. **Researchers describe the ability to tell good from bad as something trained by completed feedback loops, not by how much they have read.**
    who: Beren Millidge (CTO, Zyphra — lesser-known); John Schulman (Thinking Machines); Neel Nanda (Google DeepMind).
    evidence:
    - Millidge: "They've only done maybe 10-30 research projects in total. But somehow they develop taste quite quickly" — https://www.dwarkesh.com/p/john-beren-charlie (≈00:45).
    - Schulman: "a lot of what people call taste is something about behavior that works in the long run, and that people have realized works in the long run" (same page; READ-FULL).
    - Nanda gives a feedback delay per skill: coding takes minutes; conceptual understanding takes hours ("read papers… ask someone more experienced"); "was this a good project?" takes months. He says to train yourself "like you're a neural network" on lots of high-quality data. Beginners should take "unambitious projects… willing to give it up" — https://www.youtube.com/watch?v=MfMq4sVJSFc ≈1:18–1:24 (CAPTION-PARAPHRASE).
    bears on: E1; K17 (scored skill); against "more knowledge → better filtering" unless the knowledge is feedback on your own judgments
    limit: these are self-descriptions, and K17 found self-report tracks measured practice at only r = .29.

F9. **A paper's own ablation table contradicted the field's story about it, and blind tests deflated what researchers believed mid-research.**
    who: John Jumper (Google DeepMind, AlphaFold).
    evidence:
    - The field concluded "equivariance that is the answer."
    - Yet the ablation row with no invariant point attention removes all equivariance, and equivariance explains "two or three" of AlphaFold 2's ~30 GDT gain.
    - On blind assessment: "a lot of systems don't live up to what people believe over the course of their research"; "we all overfit to our ideas to the benchmark… Unless you have held out."
    — TRANSCRIPTS_YC.md:37394-37431 (2Yguz5U-Nic; Source block present; CAPTION-PARAPHRASE).
    bears on: E1 (beliefs that build up during research run high), E3; K10 (ablations), K6 (the popular narrative)
    limit: CASP-style blind tests exist in few fields.

F10. **Results that fit the evidence still need the disconfirming experiments nobody ran.** Biderman's team revisited a well-regarded grokking/universality paper. Its explanations were fully supported by its evidence, but other explanations fit equally well, and the disconfirming experiments had never been run.
    who: Stella Biderman (EleutherAI), on the ICML 2024 mech-interp panel.
    evidence: ~/Desktop/researchfms/Transcripts/ICML_TRANSCRIPTS.md:12524 (-gTkBM42uOY; URL block present; CAPTION-PARAPHRASE).
    bears on: E3, Q5; K7
    same panel, against reading more inside the field: Naomi Saphra (Kempner, Harvard) told researchers to "go mad hermit": skip arXiv for a week and read information theory or evolutionary biology, because the field is a "research monoculture" (ICML_TRANSCRIPTS.md:12560). Bears on K5 and against C1-as-reading.

F11. **Verification costs more than discovery. When reproduction works, it often goes through odd channels.**
- **Lupsasca:** GPT-5.2 Pro produced the graviton result in about 3 days, and verification took 3 weeks. His prompt told the model the appendices are "where most of the hard work goes". He relays, second-hand, that Tao found AI's creative-looking proofs "pulled facts out of some obscure reference" — https://www.youtube.com/watch?v=9d899Ram9Bs ≈48–51 min and ≈1:11 (CAPTION-PARAPHRASE).
- **Fursin:** a "three months project" to reproduce a paper became three years. Results did not match, and real-world data differed. Releasing his code drew outside fixes. He cites Collberg's audit of 600 papers: most did not share code, or the shared code was not enough to build and run — https://www.youtube.com/watch?v=7zpeIVwICa4 ≈9–22 min (CAPTION-PARAPHRASE).
- **Epoch on Chinchilla:** Epoch replicated Chinchilla's method 3 by pulling data points off the published plots with a forensic tool. The original fit had non-zero-mean residuals, and the corrected fit matched methods 1–2: "replication showed the original result was correct all along" — TRANSCRIPTS_STANFORD.md:8727-8740 (CS336 lecture 9, 6Q-ESEmDf4Q; CAPTION-PARAPHRASE).
- **O'Neill:** Kaplan's scaling-law fits used intermediate checkpoints and "didn't account for the annealing… would have been caught years earlier" — john-beren-charlie (READ-FULL).

    who: Alex Lupsasca (black-hole physicist, now OpenAI — lesser-known; OpenAI incentive); Grigori Fursin (cTuning/CK — lesser-known); Charlie O'Neill (head of model training, Baseten — lesser-known).
    bears on: E3, Q5; K10, K16

F12. **The field prunes by forgetting what cannot be reproduced. Very recent ideas cannot be judged yet.**
    who: John Schulman.
    evidence:
    - "If you publish something that can't be replicated easily, people will just forget about it… you don't just report someone's number… you also try to reimplement their method" — https://www.dwarkesh.com/p/john-schulman (~01:14; READ-FULL).
    - It is hard to measure progress in the recent past because "you sort of don't know yet which ideas are important." Internal labs draw more accurate conclusions, but "the thoroughness of experiments is usually less" — TRANSCRIPTS_CURSOR.md:1480-1706 region (29BYxvvF1iM; CAPTION-PARAPHRASE).
    bears on: E2, E3; K6, K8

F13. **Reading-group Q&A carries failed reproductions that no paper reports.** An audience member, Tonius, said he could not always reproduce V-JEPA's IntPhys pairwise results, and tied it to sinusoidal vs RoPE positional embeddings differing between sources.
    who: Cohere Labs talk by Sonia Joseph (Mila/FAIR).
    evidence: TRANSCRIPTS_COHERE_LABS.md:4166-4176 (6UKl8e8-qKE; CAPTION-PARAPHRASE)
    bears on: E3, Q3; extends g1 F6 (undocumented flags) and K13 (replies)
    limit: one exchange, and neither person is famous.

F14. **What experts let go of in fast-moving fields is beliefs about what is currently possible, and they re-test those by direct use.**
- **Brown:** observers "last looked at AI a year ago or six months ago… just try the models today."
- **Brown:** a frontier-lab researcher bet $1,000 that the Millennium Prize result would take past 2027, two weeks before it happened: "people have been continuously surprised, even inside the labs."
- **Brown:** an incident showed him "my previous mental model about the way in which optimization pressure shapes AI minds was wrong." — https://www.dwarkesh.com/p/noam-brown (00:22:02, 00:40:22, 01:01:18; READ-FULL)
- **Bricken:** "get rid of the sunk cost of your previous workflows, or expertise" — sholto-trenton-2 (02:15:35; READ-FULL).
- **Carlini:** he set aside his dislike of next-token prediction ("I did not think that this would work… But it works"), while others "get bitter… and they dismiss the entire thing as being hype" — https://www.youtube.com/watch?v=qCBfc8sfAJo ≈1:14 (CAPTION-PARAPHRASE).
- **Lupsasca:** a year earlier he thought AI was "cool for emails". Then o3 did one of his calculations in 11 minutes (9d899Ram9Bs ≈1:12).

    bears on: E2, owner's "delete old graphs". Supports deleting outdated *beliefs*. g1 A2 shows *notes* are kept.

## Against the claims

A1. **More knowledge did not mean better filtering when the regime changed or variables interacted (F1–F3, F14).** Nanda adds a case where prior expertise from another field biased him: as a former mathematician he was drawn to "complex and elegant methods," and his lesson is that such ideas "are often useless for the immediate interpretability goal." A plain linear probe beat SAEs on harmful-intent detection, which "surprised the team" — TRANSCRIPTS_GOOGLE_DEEPMIND.md:293-295, 403-404 (1DtMiRKg-cs; CAPTION-PARAPHRASE). Bears on E1, C4, K17.

A2. **Contradicting data is a weak reason to prune (F7).** This sits against fast pruning in E2. It agrees with Schulman, who says switching too often is the more common failure (g1 A1).

A3. **The "graph" does not keep growing by reading once someone is an expert (F4, F5).** Insiders read less. Their information comes from internal feedback and people. This is against C1 if accretion means reading.

A4. **Against C6 (K11): sharing between agents had to be learned and has not been measured.** Brown: early multi-agent versions were "very hard to get the agents to even talk to each other". Talking "interrupts their chain of thought", and "we haven't measured… 10,000 agents… over 2,000" (noam-brown 00:15:28; READ-FULL). This connects to g3 F8 (reading peers' partial findings cost 3.8 points).

## Not covered by any claim

N1. **Signs-of-life ladder.** Schulman: start from an intuition, "come up with a task that is designed to show signs of life… make successively more realistic versions." The inner loop tests the intuition (john-beren-charlie 00:28:06; READ-FULL).

N2. **Stage-aware checks.** Nanda splits research into explore, understand and distil. Each day or two he asks "Did I learn anything? If… no, consider changing tools." The rabbit-hole failure is thinking you found the right thing "but actually they just don't know enough about the problem." After weeks of work, red-team the hypotheses you are attached to (MfMq4sVJSFc ≈1:20–1:27; CAPTION-PARAPHRASE). Bears on E1 and E2.

N3. **Building is the check on whether you understand.** Karpathy: "If I can't build it, I don't understand it". Without building, "you just think you have the knowledge"; and no copy-paste. He also argues forgetting is a feature: being bad at memorization "forces you to only learn the generalizable components" (KARPATHY.md:11863-11872, 12163-12177; CAPTION-PARAPHRASE). This is an analogy for the owner's "prune old graphs": keep the patterns, drop the details.

N4. **Use unsupervised tools to escape your own frame.**
- Olah: "gradient descent is smarter than you".
- In OthelloGPT, a colour-absolute frame made the features look nonlinear. A player-relative frame (Nanda) found them linear.
- "SAEs mean you don't have to guess what's there."
- Olah himself dropped his earlier belief that superposition would prove too hard to get past.
(ICML_TRANSCRIPTS.md:12646-12660; CAPTION-PARAPHRASE.) Bears on E1 and E2.

N5. **Variability treated as data, not as a red flag.** Fursin maps run-to-run variance to its causes (CPU frequency, cache effects) (7zpeIVwICa4 ≈1:00).

N6. **The log becomes context.** Schulman pastes his lab notebook into an LLM for feedback, and uses GPT-5 Pro for literature searches (CURSOR.md, Schulman §"Skills"; CAPTION-PARAPHRASE). Extends K4.

## Frontier
- Epoch's Chinchilla replication (fit read off published plots) — a model case of verifying without raw data (STANFORD.md:8727).
- Collberg's 600-paper "weak reproducibility" study, and artifact-evaluation badges at PL conferences (PLDI, OOPSLA) (7zpeIVwICa4).
- Biderman's revisit of the grokking/universality paper; "Not All Features Are Linear"; "An Interpretability Illusion for BERT"; Saphra's position paper on evaluation as pentesting (ICML_TRANSCRIPTS.md:12524-12545).
- Andy Jones, "Scaling scaling laws with board games" (sholto-trenton-2).
- Nanda's research-taste blog post (cited in the 80k episode).
- Dwarkesh, "AI researchers debate how close we are to recursive self-improvement" (Schulman, Millidge, O'Neill) — more on taste and meta-learning not mined.
- Brown's Dwarkesh episode on 10,000-agent coordination — an internal practitioner account bearing on K11.

## Lane state
- Local `*TRANSCRIPT*.md` (46 files): heading index for target names, then practice-word counts across all files. Most sections are summaries with Source/URL blocks, so I treated them as paraphrase.
- Bounded reads: CURSOR 1465-1706 (READ-FULL section), KARPATHY 11493-14084 (READ-PARTIAL, grepped), ICML 12337-12686 (READ-PARTIAL: panel and Olah talk), GOOGLE_DEEPMIND 30-642 (READ-PARTIAL), YC Jumper 37260-37445 (READ-PARTIAL), STANFORD 8715-8740, 20160-20178, 2049-2110 (the Jason Wei section has only a URL and the file carries provenance flags, so it is unused), COHERE_LABS 3828-4185 (READ-PARTIAL), AI_AGENT_SYSTEMS 65200-65250 (Wolf essay; not used).
- No Dwarkesh episodes with Sholto/Trenton or Noam Brown exist locally: EMPTY.
- dwarkesh.com written transcripts: READ-FULL for sholto-douglas-trenton-bricken, sholto-trenton-2, john-schulman, noam-brown, john-beren-charlie, ilya-sutskever-2, jeff-dean-and-noam-shazeer (all grepped plus targeted reads).
- yt.sh: 9 searches; transcripts READ-FULL as captions for 7 videos (Carlini–Boneh, Tri Dao–Effron, Fursin, Lupsasca, Nanda 80k pt2, Brown Parables). Sasha Rush/Cohere fireside: BLOCKED ("FETCH_FAILED_BUT_TRACKS_EXIST", bot-wall). Search for Jason Wei talks: EMPTY (noise). Searches for Steinhardt and Beyer interviews found results; I did not fetch them (EXHAUSTED by choice).
- Tri Dao: READ-FULL, little on method beyond hardware and algorithm people "talking to each other" finding the bottleneck for FlashAttention. Not used as a finding.
- silver was not needed. No X or web search.

## Source register (all 2026-10-10)
- ~/Desktop/researchfms/Transcripts/TRANSCRIPTS_CURSOR.md:1465-1706 — READ-FULL (paraphrase)
- ~/Desktop/researchfms/Transcripts/TRANSCRIPTS_KARPATHY.md:11493-11880, 12150-12215, 13225-13700 — READ-PARTIAL
- ~/Desktop/researchfms/Transcripts/ICML_TRANSCRIPTS.md:12337-12686 — READ-PARTIAL
- ~/Desktop/researchfms/Transcripts/TRANSCRIPTS_GOOGLE_DEEPMIND.md:30-642 — READ-PARTIAL
- ~/Desktop/researchfms/Transcripts/TRANSCRIPTS_YC.md:37260-37445 — READ-PARTIAL
- ~/Desktop/researchfms/Transcripts/TRANSCRIPTS_STANFORD.md:2049-2110, 8315, 8715-8740, 19890, 20160-20178 — READ-PARTIAL
- ~/Desktop/researchfms/Transcripts/TRANSCRIPTS_COHERE_LABS.md:3828-4185 — READ-PARTIAL
- ~/Desktop/researchfms/Transcripts/TRANSCRIPTS_AI_AGENT_SYSTEMS.md:65200-65250, 68368 — READ-PARTIAL
- ~/Desktop/researchfms/Transcripts/TRANSCRIPTS_A16Z.md:9832-9846 — READ-PARTIAL (not used)
- https://www.dwarkesh.com/p/sholto-douglas-trenton-bricken — READ-FULL
- https://www.dwarkesh.com/p/sholto-trenton-2 — READ-FULL
- https://www.dwarkesh.com/p/john-schulman — READ-FULL
- https://www.dwarkesh.com/p/noam-brown — READ-FULL
- https://www.dwarkesh.com/p/john-beren-charlie — READ-FULL
- https://www.dwarkesh.com/p/ilya-sutskever-2 — READ-FULL
- https://www.dwarkesh.com/p/jeff-dean-and-noam-shazeer — READ-FULL
- https://www.youtube.com/watch?v=eaAonE58sLU — CAPTION-PARAPHRASE
- https://www.youtube.com/watch?v=qCBfc8sfAJo — CAPTION-PARAPHRASE
- https://www.youtube.com/watch?v=xlSaoP0b90A — CAPTION-PARAPHRASE (unused)
- https://www.youtube.com/watch?v=7zpeIVwICa4 — CAPTION-PARAPHRASE
- https://www.youtube.com/watch?v=9d899Ram9Bs — CAPTION-PARAPHRASE
- https://www.youtube.com/watch?v=MfMq4sVJSFc — CAPTION-PARAPHRASE
- https://www.youtube.com/watch?v=YMT81cpP6zc — BLOCKED

Caption positions are approximate, worked out from where a passage falls in the transcript, because yt.sh output carries no timestamps. Fetched copies are in /private/tmp/claude-501/-Users-seventyleven-Desktop/2748e90d-68b2-4b87-8ff4-e3a382ec991b/scratchpad/{dw,yt}/.
