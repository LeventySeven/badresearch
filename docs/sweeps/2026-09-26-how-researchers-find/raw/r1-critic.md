<!-- AGENT OUTPUT — Completeness critic over pooled round 1. Returned by a subagent, not read by the chair unless a row says so. -->

Round 1 misses whole classes of mechanism. Most of its non-✔ quotes hold, but three stop-rule rows (K8) lost their conditions, one quote is really a paraphrase, and three registers are weaker than their labels once the sources are grouped by who supplied them. Everything below was checked against the source bytes today; nothing was written to disk.

## 1. Missing classes

1. **Judging a source by leaving it, and grading the source separately from the claim.** Every filter in K9 works by reading the source itself (Carlini's one-sentence test, Nanda's boring-explanation test, Paine's bibliography check). The one measured contest between expert evaluators found professional fact-checkers beat PhD historians because they left the page at once to see what others say about the publisher. Intelligence formalises the split with Admiralty grading (source reliability rated apart from claim credibility). The pool has zero hits for "lateral", "fact-check" or "Admiralty". Open: Wineburg & McGrew, *Lateral Reading and the Nature of Expertise*, Teachers College Record 121(11), 2019, doi:10.1177/016146811912101102.

2. **Mechanical tests on the artifact itself.** Research-integrity sleuths filter junk without needing taste: the GRIM test (is a reported mean possible for that n?), Carlisle's baseline test across 5,087 RCTs, retraction status, and who funded the study. The pool has zero hits for GRIM, retract, funder or sponsor. Keller Jordan's "trust incentives" (raw G N3) was dropped when pooling. Open: Brown & Heathers, *The GRIM Test*, SPPS 2017 (doi:10.1177/1948550616673876); Lundh et al., *Industry sponsorship and research outcome*, Cochrane MR000033, 2017.

3. **Manufactured signal and data voids.** K6, K10 and C4 treat rare places as where value hides, never as where manipulation hides. Low-competition queries are exactly where SEO farms, astroturf and paper mills plant content. Anthropic's own finding that agents picked "SEO-optimized content farms" (raw G X6) never reached KNOWN. This is the strongest case against "sample the unpopular on purpose", and it is absent. Open: Golebiewski & boyd, *Data Voids*, Data & Society 2019 (datasociety.net/research-library/data-voids/).

4. **Expertise that is scored, not famous.** The ledger picks "the best" by fame (Fields, Nobel, lab founders, a podcast episode with 5.21M views), which is the signal K6 calls lagging. Forecasting tournaments pick the best by measured accuracy and describe what those people do: start from a base rate (reference class), update in small steps, keep score. Hölscher & Strube is the only row in the pool that measures how well people search. Open: Mellers et al., *Identifying and Cultivating Superforecasters…*, Perspectives on Psychological Science 10(3), 2015.

5. **Stopping on a recall estimate.** K8 names capture–recapture only in passing. The profession that stops on a statistical guarantee is legal eDiscovery, using technology-assisted review (TAR), and systematic-review screening that copied it; it has zero hits in the pool. The skill already ships "a screening stop with a recall guarantee" (J inventory) with no practitioner source under it. Open: Cormack & Grossman, *Engineering Quality and Reliability in Technology-Assisted Review*, SIGIR 2016; Callaghan & Müller-Hansen, *Statistical stopping criteria for automated screening in systematic reviews*, Systematic Reviews 9:273 (2020, open access).

6. **Building queries as engineering, then testing them on known items.** K5 names the vocabulary wall but not the librarians' fix:
   - pin down the real question before searching;
   - take search terms from a seed set of papers already known to be relevant;
   - measure recall on a separate held-out set of known papers.

   Open: Hausner et al., *Routine development of objectively derived search strategies*, Systematic Reviews 1:19 (2012); Taylor, *Question-Negotiation and Information Seeking in Libraries*, C&RL 29(3), 1968.

7. **Committing to the search plan in advance, as a brake on accretion.** C1 is scored SUPPORTED with no cost attached. Fields that care most about bias fix the search before looking and report any deviations, because letting each find steer the next query drifts the search toward what the searcher already believes. Cochrane's "biased towards known studies" warning is the only trace of this in the ledger. Open: Rethlefsen et al., *PRISMA-S*, Systematic Reviews 10:39 (2021); Gelman & Loken, *The garden of forking paths* (stat.columbia.edu/~gelman/research/unpublished/p_hacking.pdf).

8. **Monitoring.** Every K row treats research as a one-off hunt. Tenopir's table, which K3 already cites, shows browsing was still the largest channel in 2005 (33.9%), and Ellis's "monitoring" (raw D F7) did not survive pooling. Open: Elliott et al., *Living systematic reviews…*, PLoS Med 11(2):e1001603 (2014).

Two more were lost in pooling: Pirolli & Card's information foraging (raw D frontier, blocked there, absent from KNOWN), and the Tradecraft Primer's Key Assumptions Check, which sits in a source a lane read in full.

## 2. Spot-checks on unmarked rows

1. **K8, Perplexity: "Stop if consecutive calls return mostly previously-seen entries"** (T/PERPLEXITY_DEEP.md:3852) — **WRONG in scope.** The rule is for `memory_search`, a lookup over the user's memory store. The teardown itself says "It is stated for memory_search" and then extends it to web search on its own.
2. **K6:78, Hunter's records "the competition ignores"** — **PARAPHRASED but shown as a quote.** The manual says: "the competition usually isn't doing this work. Instead, they're begging someone to tell them a secret."
3. **K3, Tenopir "~18% via people (1977 and 2005)"** — **HOLDS at the endpoints only.** The full series is 17.7 / 15.3 / 11.3 / 13.0 / 18.5, so "stable" comes from picking the endpoints. The same table shows browsing at 33.9%, the largest channel.
4. **K8, Nanda "5 hours without learning → change approach"** (A/how-to-become…:544) — **HOLDS, but incomplete.** The same post also says "learned nothing in 2 hours, pivot" (:362) and "two days → pivot" (:545); two lanes each quoted a different number. It is a time-box on experiments, not a rule for when to stop searching.
5. **K8, EPO B-IV 2.6** — **HOLDS verbatim**, but the next sentence gives a second stop: end once documents "clearly demonstrate" lack of novelty. That stop-on-a-decisive-document rule is omitted.
6. **K8, Husain/Shankar "~20 traces with no new category"** — **HOLDS**, but the same sentence ends "(but review at least 100 to start)". The floor that comes before saturation was dropped.

These also HOLD against today's fetch, with the condition KNOWN drops noted where there is one:

| Row | What holds | Condition KNOWN drops |
|---|---|---|
| Magentic-One | 31% drop without ledgers | measured on GAIA validation |
| DeLM | 60.1 → 55.2 without verification | LongBench-v2 Multi-Doc QA, not web research |
| DivInit | diversifying later turns adds nothing | Qwen3-8B only |
| Kimi | Discard-all 60.6 → 74.9 | — |
| Tradecraft Primer | "Ask what evidence is not being seen…" | — |
| Uzzi | 9.11 / 5.33 / 2.05 per 100 | — |
| Simkin | ~20% of citers read the original | a model estimate |
| Hölscher & Strube | 3.2 of 5 tasks | — |
| Hunter | master-file quote; "better story" | — |
| Carlini, Anthropic | one-sentence test; duplicate searches | — |

**Kim et al., a ✔ row:** the bytes hold, but the paper's own out-of-sample check says "Independent MAS degradation validates only for GPT-5.2 but not for Gemini models". Its decentralised-beats-centralised result replicates Partial / ✓ / ✗ across the three held-out models. K11 leans on this paper and drops that caveat.

## 3. Distinct actors behind the rows

- **Anthropic:** its product blog and cookbook are one actor (K11, K12). Carlini (Anthropic) appears in K5, K6, K9, K10, K11 and K12; Olah, and Nakkiran quoted through Olah, carry K3 and predict-before-reading. That is 7 of 12 K sections, in a sweep run by Claude to build a Claude skill. K12 counts Anthropic's own product prompt as a practitioner.
- **Dwarkesh:** one interviewer's guest list supplies five ✔ rows (Tao ×2, Gwern, Paine ×2) plus Noam Brown. The ✔ checks the bytes, not how the guests were chosen.
- **Gwern:** 7 mentions across 6 sections, from two essays and one interview. Those essays are about finding a known item (raw C F1 limit), and that condition is dropped in K1, K5, K6 and K7.
- **Hunter's manual** (whose authors sell training in it): 6 sections. **Cochrane ch. 4:** K2, K3, K8, K10, K11. **Greenhalgh & Peacock:** K2, K3, K12 and the mechanisms list — one audit of one review. **Heuer and the Primer** are one actor. **The Evans lab** supplies both the support for K5 and the counter to it. **Hamming** is one talk counted in three lanes.

**Registers that are weaker than their labels:**

- **K7 (DEFAULT):** the named mechanism, predicting what record *should* exist, rests on Heuer/Primer plus one Bellingcat case. Darwin, ACFE and Gwern support seeking contrary evidence, not that mechanism. By the ledger's own definition the mechanism is CONTESTED.
- **K8 (DEFAULT):** the practitioner support is only Wohlin (one replication of about 10 papers), Cochrane ("little formal evaluation") and Kuhlthau (students). The rest are the mis-scoped memory rule, a fast-mode budget cap, a trace-review rule, an experiment time-box and a cost rule. Saturation also judges itself: a search that cannot reach a cluster saturates without it.
- **K2 (DEFAULT, "highest yield"):** the yield figures come from one audit. The well-indexed-field evidence in the same row (Horsley, Bramer, Royle & Milne) points the other way. It should be CONDITIONAL, with the axis being how well indexed the field is.
- **K5 (DEFAULT):** Uzzi, Shi & Evans, Ke and Wang all define a "hit" by citation count, the metric K6 says does not track quality. Either K6 weakens, or K5 is left with Swanson's three wins (failures not counted) and anecdotes.
- **K4 (DEFAULT), "Nobody on record keeps a graph": WRONG inside the pool.** The ICIJ chapter lane E read in full has a section "Using Graphs to Find Hidden Gems Together", where Neo4j and Linkurious played "a key role during the research and reporting phase". Radu's i2 link analysis, Tatsu's 19-release spreadsheet and Luhmann's linked slip box point the same way. Individual researchers keep lists and logs; teams working through entity-dense material keep entity graphs.
- **K11 (CONDITIONAL), "share findings" side:** the numbers come from BrowseComp-type find-a-fact benchmarks, GAIA, SWE-bench and LongBench-v2; none scores research synthesis. The only human evidence is ICIJ. C6's "SUPPORTED for research-shaped tasks" overstates this.
- **K1, "measured":** STORM measured unique references collected, not whether answers were correct.

## 4. What a research skill can obey and check, versus exhortation

**Obeyable and checkable** (a check can read it from the log or compute it):
- Alternate backward and forward citation rounds; end on a round with zero new included items. Seeds must come from at least two clusters with no citation link between them.
- Sort citing papers by their own citation counts (Tao); count co-cited papers and repeat authors (Keshav).
- Every query after the first names the finding it was conditioned on.
- Stop after N rounds with fewer than k new items. If only already-known key papers keep coming back, flag the strategy as biased (Cochrane's own warning); measure relative recall on a held-out set of known papers.
- For each hypothesis, write the record that should exist if it were true, search for it, and log found or not. Drop evidence that fits every hypothesis.
- Search for both sides, and in the languages of the places involved.
- Keep a contrary-evidence list from the first contrary find; if it is empty, say so.
- Per source: a one-sentence "what is new"; a bibliography-language check; the boring explanation and whether it was tested.
- Absence claims list the field terms tried. Claims with several sources trace each back to its origin and count origins, not sources. Log the path to each find.
- Record a prediction before opening a source.
- Parallel workers: disjoint briefs (measured by URL overlap), diverse first queries, shared notes admitted only with a verbatim span that matches the source, failed attempts shared.
- From the absences above: a lateral check on unknown publishers, retraction and funder fields, GRIM on reported means, and a recall estimate at the stop.

**Exhortation dressed as mechanism:**
- "People are a primary channel" (K3). The sentence about its "reachable form" for an agent is the chair's own inference, with no source.
- "Connections across communities" (K5) is a goal. Swanson's shared-B-term search is the part that can be computed.
- "Read deeply" (K9). Ng's 15–20 / 50–100 paper counts can be obeyed but were never tested as stopping points.
- "Re-read the log" (K4): a check can confirm it happened, not that it produced anything.
- Popularity among experts as a router (K6) stays vague until "which experts" is defined.
- "Excitement is evidence of bullshit", "go for the messes", "know when you know enough", "publish to be corrected", "train your filter on bad papers".
- Heuer's point that more information raises confidence but not accuracy. Its obeyable form: never raise stated confidence because the source count went up.
- K12's broad-first versus hypothesis-first debate. The obeyable form is Karnofsky's: read 1–3 pieces per side, write the claim, and name the sub-question most likely to flip it before round 2.