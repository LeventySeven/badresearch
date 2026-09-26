# How the best researchers find the top 1% — and whether our direction holds

2026-09-26. Built from 19 reader lanes over X (famous and small accounts), researchers' own essays, the
empirical information-science literature, OSINT/journalism/intelligence/investing/patent/systematic-
review tradecraft, 44 local transcripts, the local essay library, YouTube, multi-agent research systems
(papers and source code), and the old-vs-new skill. Every load-bearing number below was re-checked by
the chair against the source bytes (✔). Evidence rows with spans: `KNOWN.md`; every lane's full return:
`raw/`; every URL: `SOURCES.md`.

---

## The short answer

1. **Research compounds, and that is measured.** Asking questions one at a time from what you just
   read reached 99.83 unique sources vs 39.56 for the same number of questions asked all at once (STORM ✔).
   Each find changes the query (Bates' berrypicking ✔).
2. **The highest-yield move is following links, not searching.** In an audit of a large review, the
   planned database search found 30% of the sources; chasing references of references found 51%;
   people found 24% (Greenhalgh & Peacock ✔). Citation tracking found a useful paper every 15 minutes;
   databases, every 40.
3. **The best keep a list of open questions, not a graph.** Hamming's scientists carry "between 10 and
   20 important problems" and match every new idea against them ✔; connections come from re-reading a
   running log (Schulman ✔, Nanda, Darwin, Gwern ✔). Teams on name-dense material (ICIJ, OCCRP) do keep
   entity graphs.
4. **The wall between communities is vocabulary.** Two people name the same thing alike under 20% of
   the time (Furnas 1987 ✔); experienced searchers working the same question retrieved only 17% of their
   items in common on average (39 searchers, 40 questions), and an item retrieved by 5 or more of 9
   searches was over six times as likely to be relevant as one retrieved once (Saracevic & Kantor ✔).
5. **Popular is not good — but popular among experts is a usable router.** Higher-ranked pages are "more
   optimized, more monetized … lower text quality" (Bevendorff ✔); citation-ranked search buries grey
   literature around pages 35–80; 54% of citations had little or no influence on the citer ✔.
   Researcher readership tracks peer-judged quality; public attention barely does.
6. **Counter-evidence is found by predicting what should exist**, and failed replications hide inside
   the original's "cited by" list, because under 3–12% of later citers mention them. **Never check a
   claim by searching its own words**: 77% of such queries for false articles returned unreliable links
   in the top ten ✔.
7. **"Nothing new is turning up" is not a stop.** It missed its recall target 39% of the time ✔;
   lawyers who believed they had 75% of the documents had 20% ✔. The reliable stop hides a few
   known-relevant items from the searcher and waits until the search finds them on its own ✔.
8. **Parallel workers help when they exchange, at round boundaries, through a gate.** Agents that
   never exchange lost 35% to a single agent on a web-research benchmark ✔ (with GPT-5.2; on held-out
   Gemini models they matched or beat it — the evidence here is thin); a dead end shared in one line
   stops others rediscovering it; when OpenAI's agents shared freely on a board of their own making, one
   move spread to over 90% of the 533 active agents (they joined a cheating attack) and duplicate effort
   persisted until some agents began assigning lanes ✔;
   sharing without the source's identity created false corroboration in the Iraq WMD case ✔.
   Judgment (verification, rival hypotheses) stays independent.

9. **More information is the smallest lever; discipline is the largest.** In a model of forecasting
   accuracy, removing noise would cut the control group's error about 50%, removing bias about 25%, and
   more information the remaining 25% ✔; superforecasters "owe their success more to superior skills at
   tamping down measurement error, than to unusually incisive readings of the news" ✔. Tagging a forecast "hunt for the right information" bought no measurable
   accuracy; starting from a base rate did ✔. Skill is found by keeping score: among experts predicting
   trial outcomes, h-index vs accuracy was r = 0.00 ✔, and in Tetlock's expert study fame went with
   overconfidence (r = 0.33) ✔.

## Your direction, tested

| your claim | verdict | what to keep / what to correct |
|---|---|---|
| **Accretion** — each find drives the next search | **Holds, measured** | STORM's 2.5×; Bates; patent examiners call their search "interactive and iterative". Correction: accretion *finds*, it does not *certify* — the same searchers who accrete overestimate their recall (20% believed to be 75%). |
| **Broad first, then deep** | **Holds, with a condition** | Right for unfamiliar fields, complex evidence and "find all". Domain experts search MORE broadly, not less (White, Dumais & Teevan, 500k users ✔). The measured failure is narrowing too early: 10 intelligence analysts working an unfamiliar topic under a deadline "only used narrowing tactics and no widening tactics" and all missed key documents ✔ (4 vs 4 comparison; the authors call it "suggestive"). Search-skilled users with a well-defined target go direct, and some researchers go hypothesis-first (Karnofsky: "Read the 1-3 most prominent pieces on each side, then go" ✔) — and even then, do the plain obvious search first (Dan Russell: experts' assumptions are what slow them). The broad pass's real job is to find the *structure*: the open questions, the field's words, the clusters. |
| **Interconnections, like a graph** | **Holds as the payoff; a graph is not what they keep** | Tao on the Erdős problems AI solved: "combining this one obscure technique … with some other result in the literature" ✔. Swanson linked fish oil to Raynaud's through two literatures that never cited each other; a trial followed. Individuals keep a list of open questions + a log; teams on entity-dense leaks keep graphs. The connecting query that works holds one facet near and pushes one far (near purpose + far mechanism: 46% good ideas vs 30% for text similarity). Caveat: this literature's own evaluation is thin ("built on sand" — Moreau 2023). |
| **Popularity ≠ quality; sample popular AND unpopular** | **Half holds** | Public rank and likes are weak, gamed and lagging; novel work is under-cited for 3 years. Swanson *did* hunt the under-cited on purpose ("the absence of citations … plausible markers for neglect" ✔); promoting untested items into a ranking raised quality ~60% ✔ (measured as votes on a joke site). But no study shows an investigator reaches a better answer by sampling the unpopular, and low-traffic corners are exactly where planted content wins (data voids; fake GitHub stars; paper mills). So: sample both ends, and make an unpopular source pass a lateral check before it carries weight. On X, the sharpest methods in our harvest came from <50k-follower accounts and from reply threads (one non-blind harvest). |
| **Hunt the counterpart to be sure** | **Holds, with a failure mode** | Heuer: "Ask what evidence is not being seen but would be expected" (the predict-the-record move itself rests on Heuer plus one Bellingcat case — thinner than the rest). Greenberg's citation network: supportive papers got 94% of citations, the refuting six got 6% ✔ — so list the primaries, don't follow reviews. Failure modes: searching to check a false claim raised belief in it by 19% (Aslett ✔); structured hypothesis tables (ACH) did not beat a control group, while making independent judgments coherent and then pooling them cut error 61% ✔; hunting only against unwelcome results entrenches error (Feynman on Millikan). |
| **Parallel agents must pass knowledge as interconnections** | **Holds, when gated and at round boundaries** | See point 8 above. The unit that should cross: one line per finding with its verbatim span and source, the dead ends ("Negative results prevent others from wasting time on the same dead ends" — Karpathy's agenthub ✔), the sources already seen, and the open questions. Admit a finding only after checking its span is really in the source (DeLM: skipping that cost 60.1→55.2 ✔). The human randomized evidence points the same way: forecasting teams that shared information but each entered their own number, pooled by an algorithm, beat independent forecasters and forecasters who only saw the crowd's numbers ✔. |

## The method, as the best actually run it

**Frame.** Write the question as asked and what the asker will do with it (the richest statement of
the need gave 32% recall vs 18% for the typed words — Saracevic & Kantor). Start the open-questions list.

**Broad pass — find the structure.** Skim wide, read few deeply (Nielsen, Carlini, Ng: 15–20 papers
for a basic grasp, 50–100 for a very good one). Do the plain obvious search first. Seed from more than
one cluster — a chain never reaches a cluster its seeds did not touch (Wohlin). Make the first queries
different from each other; later diversification adds nothing (DivInit). Learn the field's own words
from overviews and from the index terms of the first good documents (IQWiG's seed-term method: 97%
sensitivity vs 75% for a conceptual search). Widen when overloaded.

**Follow the chains.** References backward, "cited by" forward, and sort the citing papers by their
own citations to surface the pivotal ones (Tao ✔); shared citations and repeated authors mark the core
(Keshav ✔). The author's other writing; the people they cite, thank and argue with. The same thing
under other names and in other languages (code, generic and brand names; kriging = Gaussian process).

**Connect.** Take two findings from different places and ask what links them. Keep a residue list: a
finding that fits no open question is the signal the structure must change (Russell, Stefik, Pirolli &
Card). Look in the penumbra of a field, not only its core (Smalheiser ✔).

**Hunt the counterpart.** Predict the record that should exist if the leading claim were true, and look
for it. Search the original's "cited by" for replications (`experiment OR randomized OR blind` — Gwern).
Trace a repeated claim to its origin: citation cascades end at one source surprisingly often ("it only
goes back to Edgar Snow" — Sarah Paine ✔), and "corroboration" is often repetition (Robb-Silberman ✔).

**Filter.** Before reading: the one-sentence "what is new here" (Carlini). For an unfamiliar source,
leave it and read about it ("Fact checkers … learned most about a site by leaving it" ✔). Grade the
source apart from the claim — and notice when you merge them (analysts measurably do). Who paid, what
are they selling (industry-sponsored trials: favourable conclusions RR 1.34, invisible to risk-of-bias
tools). Mechanical checks on numbers (GRIM flagged at least one impossible mean in 51% of applicable
psychology papers). Re-run or reimplement when you can (the Apple ICLR benchmark withdrawn after a
738-follower researcher re-ran it).

**Stop.** Two quiet rounds AND every open question closed or abandoned with a reason AND one last
search in different words or a different lane. For "find all" or "is there any evidence": hide a few
known-relevant items from the searchers and stop only when they re-find them. A yes/no question may
stop on one decisive primary.

**Teams.** Split the space by boundaries (Anthropic's early failure: "performed the exact same searches
as other agents"). Exchange at round boundaries, not continuously. Pass one-line findings with their
source identity, dead ends, and seen sources; gate admission on a span check. Keep verification and
rival hypotheses independent.

## Where rare information lives

Appendices, ablations and limitations sections ("the appendix is where the bodies are buried" ✔);
code and repositories before papers ("TODO(noam): write a paper"); old work, theses, pre-deep-learning
literature; whole registries and raw data (Hindenburg downloaded the entire Mauritius registry); grey
literature (published trials show 15% larger effects than unpublished ones); other languages (Paine's
30-second bibliography check); records the competition ignores; people's heads — reached, for an agent,
through what they wrote outside papers (blogs, threads, talks, issue trackers, reply threads).

## What was wrong before

- **The earlier research** studied AI research engines, eval traps and our own skill. It never asked
  how the best human researchers find, filter and connect information.
- **The merged skill** removed every mechanism that forced depth and breadth (the 4-lens search plan,
  the width waves, the loci with a 40-source depth budget, the depth investigators, the pre-draft critic)
  with no recorded reason or measurement. Its default is "one wide expansion".
- **Its ban on parallel depth rests on a misread paper**: the 17.2×/4.4× figures are trace-level and not
  significant after controls (p = 0.658), and the "39–70% loss" is a planning benchmark.
- **Its only parallel worker could not search** — it read one given source, so it could never follow a lead.

## What nobody has measured (honest gaps)

- Whether an investigator who deliberately samples unpopular sources reaches a better answer.
- A tested way to tell a neglected-but-real source from a planted one (three documented discriminators:
  independence from the claim's own sourcing ecosystem, coordination signatures among whoever produced
  the signal, and predicting which sources should appear).
- Whether sharing findings between parallel agents helps research *synthesis* (all numbers are
  find-a-fact benchmarks, GAIA, SWE-bench; the one human case is ICIJ).
- Bias from adaptive searching itself (only outcome-switching in reviews is measured).
- Whether saturation of *concepts* (not documents) is a reliable stop.
