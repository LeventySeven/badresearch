<!-- G1 AI research engineers (agent output, 2026-10-10) -->

## Findings

F1. **Knowing which papers are noise came from Keller Jordan's network, not from reading more.** Before he had connections, he took highly cited optimizer claims at face value, tested them, and found they did not even beat the default baseline. Connected researchers already knew which highly cited papers did not reproduce.
    who: Keller Jordan — creator of the Muon optimizer and the modded-NanoGPT speedrun, now at a big lab (19.8k followers). He promotes his own speedrun benchmark.
    evidence: "When I didn't have connections, I didn't realize that everyone who was connected already knew that overclaiming was rampant, and even knew that specific highly cited papers didn't reproduce." — https://x.com/kellerjordan0/status/2085461892257190396 (2026-10-10; READ-FULL). Also: "if you select for the papers that seem most exciting, then those ones will be majority overclaims" — /status/2084728635592970339
    bears on: E1, Q2, C4; K6, K13, K3
    limit: his field is optimizers, which is especially prone to untuned baselines. Stella Biderman (EleutherAI, 19k) agreed the claim holds for field leaders in general, not only big labs (/status/2084887446408356309).

F2. **Against the owner's intuition: experience can make filtering worse, because old intuitions go stale.** Hyung Won Chung says intuitions from earlier model generations become biases. Newcomers have less to unlearn, and accumulated knowledge breeds ego.
    who: Hyung Won Chung — OpenAI research scientist (FLAN, T5X), 39k followers.
    evidence: "an intuition cultivated in 2020 might become a counter-productive bias by 2023. This I think is one of the rare advantages of the new comers to the field: less to unlearn." — https://x.com/hwchung27/status/1676407216986009600. In a reply: "As people accumulate knowledge, it becomes easier to develop ego, to reuse higher-level concepts instead of deriving them from scratch, and to confuse axioms as objective truth." — /status/1676467842097766405 (2026-10-10; READ-FULL)
    bears on: E1, E2; K17 (fame went with overconfidence)
    limit: he scopes it to fields with no strong theory. His pruning heuristics: "if an architecture is designed for a specific task, that doesn't live long" and "is this really necessary?" (/status/1800687751786029518).

F3. **For optimizer claims, a shared, continually tuned baseline replaces trusting papers, and it supersedes stale results automatically.** Jordan judges a result real only if it improves a public speedrun record. Each record retires the baseline before it.
    who: Keller Jordan (as F1).
    evidence: "The reason papers alone can't provide strong evidence is because if they contain a mistake (like an untuned hyperparameter), ***nothing happens***." — /status/1890181363850178639. "I only trust speedruns." — /status/1890178773586489716. Correcting a senior researcher: "You're using an obsolete Muon baseline. The current Muon baseline is 3325 steps, not 3375" — /status/2064634271319691690 (2026-10-10; READ-FULL)
    bears on: E3, E2, Q5; extends K11 (shared verified state)
    limit: covers one benchmark at one scale. He says it "is not intended to be the final measure of optimizer quality across all domains" (/status/2049193527440187494).

F4. **Measured: published gains shrink or vanish once the baseline is tuned, tested at scale, run over enough seeds, or tried on more than one model family.** Most of this work comes from small-audience researchers.
    who:
    - Kaiyue Wen (2,781 followers; >4,000 models trained).
    - Andreas Hochlehnert (**254 followers**; first author of "A Sober Look", COLM 2025).
    - Rulin Shao (6,630; first author of "Spurious Rewards").
    - Davis Blalock (15.2k; meta-analysis of 81 pruning papers).
    - Konstantin Mishchenko (8.7k): "I couldn't get better results than with a tuned baseline" — https://x.com/konstmish/status/2051257013158457732
    evidence:
    - Wen: "Tuning JUST the LR in the commonly used AdamW baseline gives 2x speedup on 130M models." — https://x.com/wen_kaiyue/status/1963633870546636959. The abstract says the speedup "decreases with model size to only 1.1x for 1.2B" — arxiv.org/abs/2509.02046.
    - Hochlehnert: "most reinforcement learning (RL) approaches yield only modest improvements--far below prior claims" — arxiv.org/abs/2504.07086. Elsewhere he gives "10 seeds are a reasonable minimum" (/status/1930908595446554746).
    - Shao: random rewards gave Qwen2.5-Math-7B "21.4 percentage points … nearly matching the 29.1-point gain from ground-truth rewards" — arxiv.org/abs/2506.10947.
    - Blalock: "hard to compare pruning techniques to one another or determine how much progress the field has made over the past three decades" — arxiv.org/abs/2003.03033.
    (all fetched 2026-10-10; READ-PARTIAL — abstracts and threads)
    bears on: E3, Q2, Q5, C4; K9 (Schulman's "nerfed" baselines), K13
    limit: the evidence comes from optimizers, RL for reasoning and pruning, where untuned baselines are common. Hochlehnert's pipeline also *confirmed* one claim: "were able to verify its outstanding performance" (/status/1990874602470265030).

F5. **After a debunk, the field turns it into a routine check: a procedure is updated, not just one belief.**
    who: Rulin Shao; Arthur Conmy (Google DeepMind, interpretability).
    evidence: in the DR Tulu revision, "We added more ablations including … spurious rewards sanity check" — https://x.com/RulinShao/status/2058998802716176623. On Olmo 3: "Comparable to Qwen while no Spurious Rewards effect" — /status/1991600604934967630. Conmy: "always try strong baselines on any new project and only get excited when…" — alignmentforum.org/posts/4uXCAJNuPKtKBsi28 (comments) (2026-10-10; READ-PARTIAL)
    bears on: E2, E1; not in any K row (the cross-paper form of K7)
    limit: two instances.

F6. **When paper and code disagree, the information that decides it is in the code, the appendix, an undocumented flag, or the author's reply — not in the paper's body.**
    who:
    - Alex Nichol (unixpickle, OpenAI; 12k followers), on a paper "everybody was raving about".
    - Its author, Aayush Karan (2.9k).
    - Keller Jordan, on Shampoo.
    evidence:
    - Nichol: "the code doesn't match the paper" — https://x.com/unixpickle/status/2107251102282584525. The author answered that the "appendix has a brief discussion" (/status/2107318691952030051). Nichol then: "I didn't see mention of post-filtering in the paper" (/status/2107456819186786374).
    - Jordan: the Shampoo result depended on an "undocumented flag … contained within the 12,000-line DistributedShampoo codebase" — /status/2064761560732713360.
    (2026-10-10; READ-FULL)
    bears on: E3, Q3; extends K10 (appendices, code) and K13 (reply threads)
    limit: Nichol reads with an LLM ("I (and chat)"). Joshua Achiam warns the other way too: "don't overfit to paper details" and "Don't overfit to existing implementations either" — ~/Desktop/guidesfm/research/articles/spinning-up-as-a-deep-rl-researcher.md:80-82.

F7. **To get up to speed, they build or run something first and read as gaps appear. Reading has low value of information compared with their own experiments.** They do not grow a reading graph before acting.
    who: Neel Nanda (Google DeepMind; recruits MATS scholars); Ethan Perez (Anthropic); John Schulman; Joshua Achiam (OpenAI).
    evidence:
    - Nanda: "The goal is not to read every paper before you touch research. When doing research you'll notice gaps and go back to learn more." — how-to-become-a-mechanistic-interpretability-researcher.md:74. Also "a common mistake among academic types is to spend months reading" (:90). He recommends "breadth over depth. Skim things" plus at least one paper read fully (:171-181).
    - Perez: reading is "Generally not very important — low value of information relative to running your own experiments", and "Talking with people can often be superior" — tips-for-empirical-alignment-research.md:89, 112.
    - Schulman: split early time "about evenly between textbooks and papers"; in theses read the intro and outlook; reimplement "where the desired level of performance is known" — an-opinionated-guide-to-ml-research.md:122-128.
    - Achiam: "write the shortest correct implementation of each" — spinning-up-as-a-deep-rl-researcher.md:67.
    (2026-10-10; READ-FULL)
    bears on: E1, E3, C1, C2; K9, K12
    limit: written for empirical ML, where experiments are cheap. All of these authors mentor or recruit.

F8. **Nanda's team dropped sparse autoencoder (SAE) research on an aggregate of failures, not one result — and did not delete the tool.** The trigger was that expected positive results never showed up.
    who: Google DeepMind's interpretability team (Smith, Rajamanoharan, Conmy, Shah, Nanda). The post was curated, and habryka called it "well-calibrated about the extent of the update".
    evidence:
    - "we are deprioritising fundamental SAE research for the moment … though SAEs will remain a tool in our toolkit".
    - Nanda: "if SAEs are awesome, it really should not be this hard to find good use cases".
    - They also admit asymmetric effort: they retrained SAEs "after getting results we thought were disappointing".
    — alignmentforum.org/posts/4uXCAJNuPKtKBsi28 (2026-10-10; READ-PARTIAL)
    Later partial reinstatement: "I've resolved this positively: 2 papers convincingly show sparse autoencoders beating baselines" — https://x.com/NeelNanda5/status/1945616578038652943. And: "SAEs never went away" (/status/1945665189971448107).
    bears on: E2, Q5, Q6; K7, K8
    limit: Sam Marks (Anthropic) disputes what should be pruned. He argues good baselines should lower confidence in "interp as a whole", not SAEs in particular (same page). So *what* to prune is itself contested.

F9. **Whole frames get dropped too, on lack of traction or on one decisive event.**
    who: Jason Wei (OpenAI, then Meta); François Chollet (742k); Mengdi "prime_cai" Cai (2.2k).
    evidence:
    - Wei: "when I realized that I wasn't gaining much traction doing medical image AI research, I gave that up completely and started doing NLP." — practicing-ai-research.md (local; READ-FULL).
    - Chollet: "This was the moment I changed my mind, in December 2024, following the o3 test-time compute breakthrough" — https://x.com/fchollet/status/2085416724266983682.
    - Cai: "The moment that completely changed my mind was when Objaverse was out" (from 3D priors to data-driven methods) — /status/2023591229741822330.
    (2026-10-10)
    bears on: E2
    limit: only one-sided, after-the-fact accounts. K17 found self-report correlates with what people measurably do at only r = .29.

## Against the claims (and against the owner's "graph that grows, then prune old graphs")

A1. **Pruning too early is the more common failure in Schulman's experience, and abandoned ideas come back.**
    who: John Schulman (OpenAI co-founder; now at Thinking Machines).
    evidence: "switching problems too frequently (and giving up on promising ideas) is a more common failure mode than not switching enough" — an-opinionated-guide-to-ml-research.md:112 (READ-FULL). In an interview (summary file, paraphrase), he called OpenAI's Universe project "a deeply correct idea, but … maybe even a decade too early", and said he would "expect value functions to make a comeback" — ~/Desktop/researchfms/Transcripts/TRANSCRIPTS_CURSOR.md:1521-1525, 1582 (CAPTION-PARAPHRASE).
    Nanda: "beware switching costs" — research-process-key-mindsets.md:71. Achiam: "If it doesn't work, assume there's a bug" before dropping an idea — spinning-up-as-a-deep-rl-researcher.md:86.
    bears on: E2, C1; K8
    limit: describes projects, not sources.

A2. **The best keep old material and demote it; they almost never delete it.**
    who: Andrej Karpathy (4.3M followers); Lilian Weng (ex-OpenAI VP of Research & Safety).
    evidence:
    - Karpathy: "I delete a note only rarely. Notes that repeatedly don't deserve attention will naturally continue to sink. They are never lost" and "sometimes an idea from a while ago is suddenly relevant in a new light." — https://x.com/karpathy/status/1902503836067229803 (READ-FULL).
    - Weng: "I update my old posts periodically. Everytime I would add an one-line update message" — lilianweng.github.io/faq/. Her Transformer post v2 "is a superset of the old version" (lilianweng.github.io/posts/2023-01-27-the-transformer-family-v2/). Corrections are logged in place: "[Updated on 2019-07-18: Correct the mistake…]" (lilianweng.github.io/posts/2018-06-24-attention/) (2026-10-10; READ-PARTIAL).
    bears on: E2, C3; K4
    limit: these are personal notes and surveys; F3 shows superseded *baselines* are retired outright.

A3. **On reading versus experiments, what changes their beliefs is experiments and people, not more reading.** The 2026 version is starker: "PSA: Most biglab people now read almost zero papers" — https://x.com/kellerjordan0/status/2084721463089902074. Lucas Beyer (Meta, ex-OpenAI and Google; 154k): "you should never trust a paper, just take it as inspiration to run your own experiments!" — /status/2083073218433233293. Counter in the replies: "Many people in academia also read close to zero papers" (gavinrbrown1, 1.3k). Bears on C1 and E1; extends K16.

## Not covered by any claim

N1. **Going back to an early dismissal.** Beyer: "I've held a skeptical opinion of DiffTransformer after skimming it, but after some recent interaction thought that's unfair and I'd give it a proper read." — https://x.com/giffmana/status/1873869654252544079 (READ-PARTIAL: thread head only; his verdict not captured). On a buggy result: "I still like that it put a new idea in my toolbox" (/status/1681218546246860800). He drops the number but keeps the idea. Bears on E1 and E2.

N2. **Novices misjudge relevance early.** Ethan Perez: "You're almost never actually scooped: Junior researchers (including/especially my past self) tend to look at work that other people have done and see it as closer to what they're actually doing." — tips-for-empirical-alignment-research.md:102. This is direct practitioner evidence that early relevance judgments are coarser. Arthur Douillard (Google DeepMind, DiLoCo; 9.4k): "Something I didn't fully realize during my PhD but now see … So many research papers proposing new archi/losses/optimizers would get crushed by a well-tuned baseline." — https://x.com/Ar_Douillard/status/1788502672904990929. Bears on E1.

N3. **Cheap early belief plus fast falsification.** Nanda: "It's not too bad if you end up believing false things for a bit, the key thing is to move fast and reflexively try to falsify any beliefs you form", and "most of your probability mass should normally be on 'something I haven't thought of yet'" — research-process-key-mindsets.md:43-49. Bears on E1 and K7.

N4. **Category-level priors.** Davis Blalock: "I always assume papers introducing new Adam-like optimizers are just some mix of grad student descent, subtly messing up the baselines, unfair hparam tuning" — https://x.com/davisblalock/status/1561976219075166210. He adds that results tables cannot be pooled: "different papers often get different results for what's nominally the same setup" — /status/1577735206097735680. He keeps a "big list of discouraging ML meta-analyses". Bears on Q2 and K6.

N5. **Study what is driving the field's change, not the latest papers.** Chung: "Instead of spending all our energy catching up with the latest development, we should study the change itself. First step is to identify and understand the dominant driving force" — https://x.com/hwchung27/status/1800676312916656592. Bears on E1 and Q1.

N6. **Notice confusion; think instead of running when iteration is slow.** Matthew Rahtz, who reproduced a deep RL paper solo in 8 months (vs 3 planned) for about $850 of compute. He spent "several days just thinking, not starting any runs", and kept a log. He missed a bug "for several months by ignoring a small but mysterious decay in frames per second". Before each run he asks "How surprised would I be if this run failed?" — http://amid.fish/reproducing-deep-rl (2026-10-10; READ-PARTIAL). Bears on E3.

N7. **Removing structure is under-published.** CS25 talk notes (local summary, paraphrase): the community is good at adding structure because it gets papers, and bad at removing it — ~/Desktop/researchfms/Transcripts/TRANSCRIPTS_STANFORD.md:2140-2145 (CAPTION-PARAPHRASE; this file carries provenance flags elsewhere). Bears on E2.

## Frontier
- Semenov et al., "Benchmarking Optimizers for LLM Pretraining" (arXiv 2509.01440). Wen attributes their disagreeing rankings to batch size — a case of two careful studies conflicting (/status/1963633888678547923).
- The modded-NanoGPT Optimization Benchmark repo, with numbered results #1–#37: a public record of baselines being superseded.
- GDM's "pragmatic interpretability" pivot post (/status/1995490212567560628) and Nanda's video "What happened with sparse autoencoders?" (/status/1988950392911327623) — a retrospective on a pruning decision.
- Kantamneni et al. (linear probes vs SAEs) and Sam Marks's two-type update analysis (on the AF post).
- Hochlehnert, "Solving Spatial Supersensing Without Spatial Supersensing" (/status/1993006581135688024): a debunk of a benchmark's own method.
- Wang & Dravid's follow-up explaining Spurious Rewards from the data side (/status/2107512953285349658).
- "The efficiency misnomer" (Dehghani, Tay, Beyer et al.): parameter count is a misleading axis (/status/1453260385868468225).

## Lane state
- X `search`+`top` over 8 generic method queries (reimplement, tuned baseline, get up to speed, changed my mind, read the code, OpenReview, abandoned direction, don't trust until) — READ. Mostly noise and hype; 3 queries returned ≤2 hits. Tuned-baseline and "don't trust" queries yielded Wen, Douillard, Mishchenko.
- X handle queries: hwchung27, giffmana, kellerjordan0, _sholtodouglas, natolambert, NeelNanda5, karpathy, davisblalock, AHochlehnert, wen_kaiyue, RulinShao — READ. Sholto and Lambert gave nothing on method (EMPTY for E1–E3).
- X reply threads: Keller PSA, Chung "human unlearning", Beyer DiffTransformer, unixpickle — READ. For DiffTransformer the reply endpoint returned replies, not the self-thread, so it is READ-PARTIAL.
- X: "I used to believe", "I was wrong about", code≠paper, new-field queries — READ. Mostly off-topic; Chollet and unixpickle kept.
- X: OpenReview and reading-group/Discord queries — EMPTY (noise only).
- X user `matthewrahtz` — MISSING (0 tweets returned).
- Alignment Forum SAE post — READ-PARTIAL (curl, regex extraction).
- arXiv abstracts 2509.02046, 2506.10947, 2504.07086, 2003.03033 — READ-PARTIAL (abstract only).
- amid.fish (Rahtz) — READ-PARTIAL. Lilian Weng FAQ and two posts — READ-PARTIAL.
- Local essays — READ-FULL: Achiam, Jason Wei "Practicing AI Research", Nanda key-mindsets section, Perez reading and mindset sections. READ-PARTIAL (grep): Karpathy "Recipe", Nanda "How to become", Schulman guide.
- Local transcripts: heading index over all 46 `*TRANSCRIPT*.md`. Read CURSOR.md:1465-1620 (Schulman) and STANFORD.md:2120-2190 (Chung) — READ-PARTIAL. No Sholto talk on disk.
- YouTube and silver — not used (X and essays were enough).

## Source register
- https://x.com/kellerjordan0/status/{2085461892257190396, 2084728635592970339, 2084721463089902074, 1890181363850178639, 1890178773586489716, 2064634271319691690, 2064761560732713360, 2049193527440187494} — READ-FULL
- https://x.com/hwchung27/status/{1676407216986009600, 1676467842097766405, 1800676312916656592, 1800687751786029518} — READ-FULL
- https://x.com/wen_kaiyue/status/{1963633867140526319, 1963633870546636959, 1963633888678547923} — READ-FULL
- https://x.com/ahochlehnert/status/{1930908595446554746, 1990874602470265030, 1993006581135688024} — READ-FULL
- https://x.com/RulinShao/status/{2058998802716176623, 1991600604934967630, 2107512953285349658} — READ-FULL
- https://x.com/konstmish/status/2051257013158457732; https://x.com/Ar_Douillard/status/1788502672904990929 — READ-FULL
- https://x.com/unixpickle/status/{2107251102282584525, 2107456819186786374}; https://x.com/aakaran31/status/2107318691952030051 — READ-FULL
- https://x.com/giffmana/status/{1873869654252544079, 2083073218433233293, 1681218546246860800} — READ-PARTIAL
- https://x.com/NeelNanda5/status/{1904988240542834724, 1945616578038652943, 1945665189971448107, 1995490212567560628} — READ-FULL
- https://x.com/karpathy/status/1902503836067229803; https://x.com/fchollet/status/2085416724266983682; https://x.com/prime_cai/status/2023591229741822330 — READ-FULL
- https://x.com/davisblalock/status/{1561976219075166210, 1577735206097735680} — READ-FULL
- https://x.com/BlancheMinerva/status/2084887446408356309; https://x.com/gavinrbrown1/status/2085363267115917583 — READ-FULL
- https://www.alignmentforum.org/posts/4uXCAJNuPKtKBsi28/negative-results-for-saes-on-downstream-tasks — READ-PARTIAL
- https://arxiv.org/abs/2509.02046 ; /2506.10947 ; /2504.07086 ; /2003.03033 — READ-PARTIAL
- http://amid.fish/reproducing-deep-rl — READ-PARTIAL
- https://lilianweng.github.io/faq/ ; /posts/2018-06-24-attention/ ; /posts/2021-07-11-diffusion-models/ ; /posts/2023-01-27-the-transformer-family-v2/ — READ-PARTIAL
- ~/Desktop/guidesfm/research/articles/{spinning-up-as-a-deep-rl-researcher, practicing-ai-research, tips-for-empirical-alignment-research, research-process-key-mindsets, how-to-become-a-mechanistic-interpretability-researcher, an-opinionated-guide-to-ml-research, a-recipe-for-training-neural-networks, favourite-mech-interp-papers}.md — READ-FULL or READ-PARTIAL as noted above
- ~/Desktop/researchfms/Transcripts/TRANSCRIPTS_CURSOR.md:1465-1620; TRANSCRIPTS_STANFORD.md:2120-2190 — READ-PARTIAL (summaries, paraphrase)

All fetched 2026-10-10.
