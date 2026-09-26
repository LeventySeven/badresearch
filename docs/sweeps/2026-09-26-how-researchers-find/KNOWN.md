# KNOWN — the pooled ledger after round 1 (read this before you search)

This is what the sweep already holds. **Do not re-find it.** Build on it: your job in round 2 is to
extend, connect, or break what is here. Pooled and culled by the chair from 10 round-1 lanes
(two X lanes pending at the time of writing). A row marked ✔ was re-verified by the chair
against the raw source bytes; unmarked rows are agent-read with verbatim spans on file in `raw/`.

The chair's verification record — what was checked, where, and what matched — is `VERIFIED.md`.

Registers: **DEFAULT** = 3+ independent sources across 2+ lanes · **CONDITIONAL** = strong sources
disagree; the axis is named · **CONTESTED** = one strong source.

---

## K1. Accretion is real and measured — DEFAULT
Each find changes the next query. Bates 1989 "berrypicking" ✔ ("Each new piece of information they
encounter gives them new ideas and directions to follow and, consequently, a new conception of the
query" — pages.gseis.ucla.edu/faculty/bates/berrypicking.html). EPO examiners: search is "interactive
and iterative" (epo.org guidelines B-IV 2.2). **STORM ablation ✔: at an EQUAL number of questions,
asking them one at a time conditioned on what was read collected 99.83 unique references vs 39.56
when generated all at once** (arXiv 2402.14207 Table 5). TTD-DR (Google): next query generated from
the current draft. Gwern: rewrite the query after every miss. Bellingcat Skripal: a pivot chain
(assumption → ask ex-officers → academy yearbooks → three-fact combined query → leaked databases).

## K2. Citation chaining is the highest-yield discovery move on complex, poorly-indexed questions — CONDITIONAL (axis: how well the field is indexed)
Greenhalgh & Peacock 2005 ✔ (495 sources): protocol database+hand search found 30%, snowballing
51%, personal knowledge/contacts 24%; citation tracking ≈1 useful paper / 15 min vs databases 1 / 40
min (pmc PMC1283190). Wohlin 2014 ✔: alternate backward/forward rounds; "Once no new papers are found
… the loop is ended"; then contact active authors; **seeds must span independent clusters or the
chain never reaches them**. Tao ✔: iterate back/forward, "sort the citing papers by the number of
citations that they themselves have". Keshav ✔: "find shared citations and repeated author names".
Bates: 69% of faculty relied on footnote chasing ✔. Limit: Horsley (Cochrane) — reference checking
adds 2.5%–42.7% depending on how good the database search was; chains stay inside one community
(Evans 2008: link-following may narrow toward prevailing opinion — contested by Larivière).
**Critic correction:** the yield numbers are ONE audit of one policy review; in well-indexed trial
literature four databases suffice (Bramer 98.3%; Royle & Milne: 26 more databases added 2.4%).
X lane (R1-B): Pacheco-Vega (FLACSO, 69k) stops at "concept saturation … the same citations repeated"
and spots gaps by what reference lists leave OUT; Allen (Aarhus) snowballs back from one review, then
forward via "cited by", then runs a deliberate sweep for under-cited authors; Jolicoeur-Martineau
subscribes to the citations of a few seed papers instead of scanning arXiv.

## K3. People are a primary channel for rare information — DEFAULT
24% of Greenhalgh's sources; Tenopir & King: people as the channel ran 17.7 / 15.3 / 11.3 / 13.0 /
18.5% across the survey years (browsing stayed the largest channel, 33.9% in 2005). Hamming's lunch table; Tao learns a field by befriending someone in it ("what's known, and
what's not known") ✔; Nakkiran: the big-picture goals are "almost never written in papers";
Karpathy: knowledge "spread across a shared understanding of the community"; Cochrane: write to trial
authors with your list so far; Fisher's scuttlebutt; Meho & Tibbo "networking". For an agent the
reachable form of a person is what they WROTE outside papers: blogs, threads, talks, issues, code,
acknowledgements, "people I read" pages (chair's inference, not a sourced claim). X lane: Petrov (Stanford)
asks authors which of their own papers the field missed ("I always find new gems this way"); Douglas
FRAeS downloads everything by "someone who DOES know" and emails the authors of the 2–3 closest papers.

## K4. The "map" practitioners keep is a written list of OPEN QUESTIONS plus a running log — DEFAULT for individuals
**Critic correction:** individuals keep lists and logs; TEAMS working entity-dense material keep entity
graphs — ICIJ's chapter "Using Graphs to Find Hidden Gems Together" (Neo4j/Linkurious), OCCRP/Radu's i2
link analysis ("If the same address is encountered on page 564 as it is on page 3, I2 will find this
connection"), Tatsu's 19-release comparison spreadsheet, Luhmann's linked slip box. Hamming ✔: "between 10 and 20 important problems … when they see a new
idea come up … 'Well that bears on this problem.'" Feynman's twelve problems (via Rota); Collison's
public questions page; Matuschak writes question prompts before he knows the answer and splits them
as understanding grows. Connections are found by RE-READING a log: Schulman's weekly journal review ✔,
Nanda's highlights doc, Darwin's 30–40 portfolios, Gwern's "Huh, another example of that" notes ✔,
Hunter's chronological master file ("connections between different data points … will become
evident"), Luhmann's slip box ("combinatorial possibilities which were never planned").

## K5. The payoff is connections ACROSS communities, and the barrier is vocabulary — DEFAULT
Swanson's A–B–C (fish oil ↔ Raynaud's, two literatures "had never before been cited together";
trial followed). Tao on AI-solved Erdős problems ✔: "combining this one obscure technique that not
many people know about with some other result in the literature." Uzzi 2013: hits = conventional
base + an intrusion of atypical combinations (9.11 vs 5 per 100). Shi & Evans 2023: most surprising
cross-field moves 3.5× likelier to be hits. Ke 2015: sleeping beauties are woken mostly by other
fields. Carlini: model stealing ↔ differential cryptanalysis. Biggio: attacks "rediscovered over and
over" across communities. **Vocabulary is the wall**: Gwern reads overviews "until you finally
recognize the skeleton of what you want under a completely different … name"; Muehlhauser "took me
months to discover that professionals call this the psychology of adjustment"; USPTO: search by the
FUNCTION ("a tea mixer and a concrete mixer … the mixing art"), not the name. Counter: Foster,
Rzhetsky & Evans 2015 — 85.8% of statements repeat known relationships; new links are rare and the
reward does not cover the risk.

## K6. Popularity — CONDITIONAL (axis: whose popularity, and how new the work is)
Against trusting it: citing ≠ reading (copied misprints imply ~20% of citers read the original);
Teplitskiy 2022 ✔: 54% of citations had little or no influence; novel papers are under-cited for 3
years and land in lower-IF journals (Wang et al.); sleeping beauties; Paine ✔: a citation cascade
"only goes back to Edgar Snow"; Carlini's most-cited paper is cited for its clear writing; Luu: a
"classic" cited 7,449 times rests on n=1 per group; Nanda: fads peak and fade; Collison: "Status lags
by a generation or more"; Gwern: the Baidu 2017 scaling paper was ignored. For it: experts use
popularity AMONG EXPERTS as a routing signal (Tao sorts citing papers by citations; review articles
rank high because widely cited; Scott Alexander: consensus is the best tool we have); Teplitskiy:
famous papers are 2–3× likelier to be truly influential and read more closely; MusicLab: "The best
songs rarely did poorly". **Nobody in round 1 describes sampling unpopular sources on purpose**
except Gwern checking every low-ranked hit for a known target, Million Short (removes the top
domains), and Hindenburg/Hunter going to records "the competition ignores".

## K7. Counter-evidence is hunted by predicting what SHOULD exist — DEFAULT
Heuer/Tradecraft Primer: "Ask what evidence is not being seen but would be expected for a given
hypothesis to be true"; evidence consistent with all hypotheses has no diagnostic value. Darwin's
golden rule: write down every contrary fact "without fail and at once". ACFE: "to prove that a fraud
has occurred, the fraud examiner must seek to prove that fraud has not occurred". Berkeley Protocol:
build keywords for incriminating AND exonerating information, in all relevant languages. Gwern:
reverse citations + `experiment OR randomized OR blind` to find replications; the trigger is noticing
an implausible number. Hunter: a false hypothesis "means there may be a better story". (K7 register: the named mechanism —
predict the record that SHOULD exist — rests on Heuer/Primer + one Bellingcat case: CONTESTED, not DEFAULT.) Counter:
admired experts' counter-evidence was wrong (Elon's "zero%" on OpenAI; Cho on normalizing flows);
Feynman's Millikan: hunting only against unwelcome results entrenches error; Heuer: past a minimum,
more information raises confidence, not accuracy.

## K8. The stop is novelty saturation, sometimes estimated — CONDITIONAL (weaker than it looks)
**Critic corrections:** Perplexity's "previously-seen entries" rule is scoped to memory_search, not web
search; Husain/Shankar's ~20 traces sits behind a floor of "at least 100 to start"; EPO adds a SECOND stop —
end once documents "clearly demonstrate" the answer; Nanda's time-box is for experiments (2 h / 5 h / 2
days). Saturation judges itself: a search that cannot reach a cluster saturates without it.
Wohlin: a round with no new papers ends the loop. Cochrane: stop when new terms yield nothing new —
and only re-finding the known key papers "might be a sign that the strategy is biased towards known
studies"; capture–recapture and relative recall. Kuhlthau: "decreasing relevance and increasing
redundancy". Perplexity/LangChain: consecutive calls return mostly previously-seen entries. EPO:
stop once the probability of more is "very low in comparison to the work involved". Husain/Shankar:
~20 traces with no new category. Nanda: 5 hours without learning → change approach. Counter: no stop
rule anywhere reads "I have looked for counter-evidence enough."

## K9. Skim wide, read few deeply, discard hard — DEFAULT
Nielsen (skim a great deal, pick a dozen a year to read deeply); Carlini (the pre-read test: "what's
the new thing that makes it useful … answerable in a sentence"); Nanda's barbell; Ng (skim ~10% of
each paper on a list, drop duds, read seminal ones fully, add from their citations; 15–20 papers =
basic grasp, 50–100 = very good); Cowen (starts ~10 books per 1 finished); Raschka ("95% … not that
important"). Post-read filters: did they test the boring explanation (Nanda); baselines "nerfed"
(Schulman); each paper section written for its incentive (Ng); a 30-second bibliography check for
sources in the languages of the countries discussed (Paine ✔).

## K10. Where rare information lives — DEFAULT
Appendices, ablations, limitations ("the appendix is where the bodies are buried" ✔; InstructGPT's
annotator appendix); old work and theses (Schulman; Biggio: search pre-deep-learning work; Hamming's
unreduced data); raw data and whole registries (Hindenburg downloaded the entire Mauritius registry;
Karpathy found duplicates in data; Carlini found an attack by studying LAION); unpublished/grey
literature (published trials show 15% larger effects than grey ones); non-English sources (Paine;
Berkeley Protocol); open records (Hunter: "the competition usually isn't doing this work. Instead, they're begging someone to
tell them a secret"); people's heads (K3). Counter
(Cochrane/Hartling): in well-indexed trial literature, non-English and unpublished studies "rarely had
any impact on the results" — rare sources pay when evidence is thin, complex, or interested.

## K11. Parallel workers — CONDITIONAL (axis: share FINDINGS, isolate JUDGMENT)
Sharing helps research when it is structured and checked: Kim et al. ✔ (arXiv 2512.08296) on the
web-research benchmark BrowseComp-Plus — agents that never communicate −35% vs a single agent;
decentralized agents exchanging views +9.2%; centralized +0.2%. **The skill's current citation of
this paper is wrong**: 17.2× vs 4.4× is TRACE-level amplification and "neither the main effect of
error amplification (β=0.014, p=0.658) … reaches statistical significance"; the "all multi-agent
shapes lost 39–70%" row is PlanCraft (planning), not research. Magentic-One: without its
facts/guesses ledger performance drops 31%. DeLM: a shared verified context of FACT/FAIL notes — a
dead end in one fork stops others rediscovering it; admitting unverified notes cost 60.1→55.2. Argus:
a shared URL-deduped evidence graph with support/contradict edges +5.2 over flat text. STORM's
parallel threads share nothing and merge by URL at the end. Anthropic removes duplication by
boundaries in the brief ("performed the exact same searches as other agents" was the early failure).
DivInit: diversify the FIRST queries; later diversification adds nothing. Karpathy: one shared queue
of ideas, workers pull, what works lands on a shared branch. ICIJ: findings and query tips posted to
topic groups as the work happens. Noam Brown ✔: children that cannot talk "is very inefficient".
Cursor fleet: agents ignored each other's messages unless delivered as user turns.
**Critic caveats:** Kim's out-of-sample check — "Independent MAS degradation validates only for GPT-5.2 but
not for Gemini models"; all sharing numbers are find-a-fact/GAIA/SWE/LongBench benchmarks, none scores
research synthesis; the only human evidence is ICIJ.
Isolation is right for JUDGMENT: Cognition's reviewer works best sharing no context; Team A/Team B;
Cochrane requires two independent screeners but "not necessary (or even desirable)" to run searches
in parallel; DeLM's coupled baseline lost diversity (pass@k); Kim: optimal redundancy R≈0.41.

## K12. Broad-first vs hypothesis-first — CONDITIONAL (axis: how well-defined the target is, and
how much the searcher already knows)
Broad first: Greenhalgh browsed before the protocol; Muehlhauser (reviews → granular); Kuhlthau
(explore → focus); Ng; Anthropic ("start wide, then narrow"); Galen Adams (LLMs "want to find the
perfect article… What is needed instead is finding the breadth"). Hypothesis/narrow first: Karnofsky
✔ ("Read the 1-3 most prominent pieces on each side, then go"; a bold premature claim, then the
sub-question most likely to flip it); Hunter's story-based inquiry (a ≤3-sentence hypothesis
decomposed into terms that generate questions); Hamming ("refuse to look at any answers until you've
thought the problem through"); Carlini (build the attack, then read); Heuer (the mental model matters
as much as the number of pieces); EPO narrow-first; Hölscher & Strube (only "double experts" go
straight to known sources and they solve most). Both then iterate.

## K13. X lane (R1-B) — popularity measured on its own sample — CONTESTED (one harvest, non-blind)
1,523 posts / 1,246 authors from ~70 method queries. The 44 sharpest concrete methods: 19 from <5k
followers, 23 from 5k–50k, 2 from 50k–500k, 0 from >500k (keep rates 4.3% / 4.4% / 0.8% / 0%). On 8
paired queries X's **Top** tab returned authors with median 19,128 followers vs 3,865 in **Latest**;
<5k authors were 27% of Top vs 54% of Latest. 7 A-tier posts came only from REPLY threads, 5 of them by
<5k-follower authors. The paired Top-tab hype template ("Holy shit… [Stanford/MIT] paper"): median 103k
followers. Caveat: the judge saw follower counts. Worked case: Lei Yang (738 followers) ran an Apple
ICLR benchmark, found a code bug and 6/20 wrong labels, and the paper was withdrawn — "because it was a
paper from Big Tech, I subconsciously trusted the integrity". Counter: Kuran — 82% of humanities
articles get zero citations and "most of these are mediocre".

## Round-1 critic: classes ABSENT from K1–K13 (being filled in round 3)
Lateral reading / grading the source apart from the claim (Wineburg & McGrew 2019; Admiralty code);
mechanical integrity tests (GRIM, Carlisle, retraction status, funder); data voids and manufactured
signal — the strongest case AGAINST sampling the unpopular (Golebiewski & boyd 2019); scored expertise
(superforecasters, base rates); stopping on a recall estimate (TAR/eDiscovery; statistical stopping
in screening); committing the search plan in advance as a brake on accretion drift (PRISMA-S; garden
of forking paths); monitoring as a standing channel (living reviews).

## Mechanisms none of the claims named (carry them)
- **Vocabulary discovery** (K5): find the field's own name for the thing before concluding absence.
- **Absence as a lead**: Bellingcat noticed a notable figure systematically missing from photos.
- **Collapse the cascade to its origin**: circular reporting (Texas DPS), Edgar Snow, copied
  misprints; Tradecraft: "multiple sources … not a substitute for having good information".
- **Periphery inward**: ACFE interviews from the periphery; Fisher goes to management last; Hunter:
  get people to confirm what you already know rather than volunteer.
- **Log how each find was reached** (Berkeley Protocol); keep excerpts = "a personalized search
  engine" (Gwern).
- **Predict before reading** (Nanda, Olah) — calibrates the filter.
- **Deliberate randomness** (Cowen randomizes his second search; Tao: search gives exactly what you
  want and "you don't get the accidental things"; 5 of Greenhalgh's sources came by chance).
- **Forget between rounds**: Magentic-One wipes worker context after each replan, keeping only the
  ledger; Kimi's discard-all 60.6→74.9 on BrowseComp; WebResearcher rebuilds each round from a report.
- **Publish to be corrected** (Karnofsky, Higgins, Weng asking readers for missing papers).

## Where the owner's claims stand after round 1
- C1 accretion — SUPPORTED, measured (K1, K2).
- C2 broad-first — CONDITIONAL (K12): right for unfamiliar fields, complex evidence and "find all";
  experts with a well-defined target go narrow or hypothesis-first. Both iterate.
- C3 connections — SUPPORTED as the payoff (K5), with the practitioners' form being a written list of
  open questions + a re-read log (K4), not a graph.
- C4 popularity ≠ quality — CONDITIONAL (K6, K13): public popularity and citation counts are weak and
  lagging, especially for novel work; expert-community popularity is a usable router. On X, the
  sharpest methods came from <50k-follower authors and from reply threads (one non-blind harvest).
  Deliberate unpopular sampling is attested only as Allen's under-cited sweep, Petrov's "missed papers"
  call and Gwern's known-item checks — and data voids are its named risk.
- C5 counterpart hunting — SUPPORTED (K7), with the failure mode that it can entrench error when
  aimed only at unwelcome results.
- C6 pass findings between parallel workers — SUPPORTED on find-a-fact benchmarks when the sharing is
  structured and verified and passes through a validating centre (K11); not yet measured on research
  synthesis; JUDGMENT stays isolated.

---

## Round 2 — rows added so far (✔ = chair re-verified in the raw bytes)

**K14. How agents measurably fail at finding things (R2-7).** Agents "abandon the search after an
initial failed attempt and proceed to answer based on incomplete information or their internal
knowledge" ✔ (WideSearch, arXiv 2508.07999); humans spent 2.33 h and 44 pages per WideSearch task vs o3's
13.3 searches / 5.8 page visits. "Multi-facet coverage gaps account for 78.5% of missing key-points" ✔
(DeepResearchGym, arXiv 2505.19253 — one system's 100 worst queries); lens/terminology mismatch 17.9%.
Fabrication is the largest single failure class (DEFT 18.95%; Mind2Web 2 hallucination ≥23% of tasks;
humans 0 hallucinated URLs). One-sided answers on debate queries 54.7–94.8% (arXiv 2509.04499). Search can
LOWER accuracy while raising confidence (SealQA; Heuer confirmed in agents). Agents ignore
source-credibility cues (arXiv 2607.13920). Literature-search recall of AI tools: median 91% of included
studies missed (Clark 2025); Elicit 37.9% vs original searches 93.5%. Humans and agents fail in
complementary ways: humans complete but careless, agents careful but incomplete and fabricating.

**K15. The connecting move, operationally (R2-2).** Swanson's one-node search (from C, harvest shared
title terms B, rank candidate A by how many B-literatures contain them) gave way to two-node search
(researcher supplies A and C; rank B) because researchers are "drowning in a sea of existing potential
hypotheses" ✔ (Smalheiser 2017, PMC5771422). Field testers faced hundreds–thousands of B-terms; a
frequency filter removed ~¾ with few interesting ones lost. **Swanson DID sample the unpopular on
purpose** ✔: disease×substance pairs with ≤5 shared articles, keeping articles cited ≤5 times — "The
absence of citations … together with the scarcity of other works that investigate the same problem,
are plausible markers for neglect" (PMC3097086). Smalheiser: the "penumbra" of a field — marginal,
new, or not-credible-yet work — as a source of new knowledge ✔; also "gaps" (topics expected to
co-occur that never do) and "negative consensus" claims made without evidence. The analogy query that
works holds one facet NEAR and pushes another FAR (Hope et al. 2017: near purpose + far mechanism 46%
good vs 30% text-similarity); schema from SEVERAL examples, searchers kept apart from the original
problem (Kittur 2019). People retrieve by surface similarity and judge by relational structure (Gentner
1993). LLM idea generation saturates (4,000 seeds → 200 non-duplicates, even with previous titles in the
prompt — Si et al. 2024), and AI ideas lose novelty once executed (Si 2025). Automated novelty checks
fail open ("If no clear matches are found, it assigns novel=True"); presuming prior art exists and
hunting it found 24%; "retrieving relevant papers, not determining similarity, is the bottleneck".
Counter: LBD's evidence base is "built on sand" (Moreau 2023), evaluated on the same few discoveries.

**K16. X roster (R1-A).** Karpathy files research outputs back into an LLM-kept wiki so "my own
explorations and queries always 'add up'" ✔ and runs lint passes to find connections worth a new article
(~100 articles scale). Newest knowledge sits in code and inside labs ("TODO(noam): write a paper").
Curators manufacture popularity: being tweeted by top paper-curators gave median citation counts 2–3×
the control (Weissburg et al., ICML 2024); one curator's bio reads "dm for promo". Small accounts are
trusted on track record and on the work itself (Dettmers on Alistarh, 1.8k followers; Achiam: "I have no
idea who this person is (small account), but this thread is exactly correct"). Counter-search built into
reading: "when they look up a paper they should explicitly look for later work that challenges it"
(Narayanan). Re-run/ablate before trusting (Chollet, Friedman, Dettmers, Albert Gu). Red-flag rules that
end reading early (Beyer, Tri Dao, Graham). Fraud found by connecting ACROSS papers (Bik: one blot spot in
400 papers). Counter to C4: Yi Tay — an important paper "will somehow 'intrusively' appear in my face on
twitter anyway" (works for insiders; F5 shows it can be bought). Counter to C2: Sasha Rush — "Pick depth
over breadth. If you do depth well, you get breadth for free."

**K17. Scored expertise — what forecasters with a measured track record do (R3-2).** Skill is found by
keeping score, not by fame: among experts predicting trial outcomes, h-index vs accuracy r = 0.00 ✔;
in Tetlock's expert study, fame correlated with OVERCONFIDENCE r = .33 ✔ (both via the Atanasov &
Himmelstein 2023 review). Information is the smallest lever: "Eliminating noise would reduce the
Brier score of the control group by roughly 50%; eliminating bias, by roughly 25%; and increasing information would deliver
the remaining 25%" ✔ (Satopää et al., BIN). The CHAMPS KNOW training RCT: of ten principles only
comparison classes (base rates) were associated with better performance ✔; "hunt for the right
information" bought nothing measurable (Chang et al. 2016). Frequent SMALL updates beat rare large ones
(Atanasov 2020: update size r = .49). Superforecasters ran a standing news feed per question (255 stories
clicked vs 55). Teams — the RCT behind "share findings, isolate judgment": members "could share
information, including their forecasts (but there was no systematic display of team members'
predictions)" ✔, each entered their own forecast, an algorithm aggregated; teams > crowd-belief >
independent (Mellers 2014). Counter: months of exchanging arguments changed few minds (XPT). What
people SAY they do correlates with what they measurably do at r = .29 (Karvetski) — a caveat on every
self-described practice in this ledger.
