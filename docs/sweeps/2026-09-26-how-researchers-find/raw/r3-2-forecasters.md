<!-- AGENT OUTPUT — R3-2 superforecasters. Returned by a subagent, not read by the chair unless a row says so. -->

## Findings

F1. **Forecasting skill is found by keeping score. Résumés and fame don't find it.** Extends **K6**: fame and h-index predict nothing, and fame goes with overconfidence.
- **who:** Atanasov (Pytho LLC, a forecasting vendor, so an incentive) and Himmelstein (Fordham). Their 2023 review covers 40+ skill measures across the GJP/ACE and HFC tournaments.
- **evidence:** "Experts can be identified by reviewing resumes, while skilled forecasters are those who demonstrate strong performance in settings where accuracy is rigorously tracked". h-index vs accuracy "(r = 0.00)". Tetlock's fame measure "correlated with overconfidence (r = 0.33)". Self-rated expertise was "completely uncorrelated". The famous fox–hedgehog result "did not replicate", and Epstein's *Range* repeated it ("We have notified Epstein"). — r.jina.ai/https://gwern.net/doc/statistics/prediction/2023-atanasov.pdf (2026-09-26; READ-FULL)
- **bears on:** Q2, C4
- **limit:** mostly geopolitics. Skill measured in one season predicts the next at only r≈.45.

F2. **Superforecasters read far more news, from a standing search feed set up for each question.** This fills the critic's absent class "monitoring as a standing channel", with numbers. Connects **K1** and **K8**: there is no stop, only continuous updating.
- **who:** Mellers, Tetlock et al., 2015, GJP (the IARPA tournament winner)
- **evidence:** "the GJP website provided a news reader that used Google search queries with keywords to help forecasters collect articles from reputable and relevant sources". Superforecasters clicked 255 stories, against 55 and 58 for the comparison groups.
  - News links shared: 91.6 vs 9.2 in Year 2, 181.9 vs 28.6 in Year 3.
  - Forecasts per question: 5.64 vs 2.15 vs 1.79 in Year 2.
  - Update frequency was "the strongest single behavioral predictor of accuracy". Articles checked vs accuracy: r = −.18.
  - https://stanford.edu/~knutson/jdm/mellers15.pdf, Table 2 and p.277 (2026-09-26; READ-FULL)
- **bears on:** Q1, Q4, Q6, C1
- **limit:** correlational. Superforecasters were also more than 1 SD higher in fluid intelligence.

F3. **Heuer, checked against the forecasting literature: mostly confirmed, with qualifications.** Information is the smallest lever. Extends **K7** (the Heuer line) and **K14** (SealQA).
- **who:** Satopää, Salikhov, Tetlock, Mellers (BIN model, *Management Science* 2021); Mellers 2015
- **evidence:**
  - "superforecasters owe their success more to superior skills at tamping down measurement error, than to unusually incisive readings of the news … Discipline may matter more than creativity here."
  - "Eliminating noise would reduce the Brier score of the control group by roughly 50%; eliminating bias, by roughly 25%; and increasing information would deliver the remaining 25%."
  - — https://faculty.wharton.upenn.edu/wp-content/uploads/2022/03/mnsc.2020.3882.pdf (2026-09-26; READ-FULL)
  - Mellers 2015, Fig. 2, on forecasts made in the first 24 hours and within 4 minutes: "Even when forecasts were made quickly without research, Supers were more accurate."
- **qualification:** elite and regular teams show "Information differences are not large" 60 days out. Superforecasters gain information only as resolution nears. Their extra confidence then shows up as a late over-extreme "bias bump", which the authors put down to competition incentives.
- **related, via a router only:** EPJ: "We reach the point of diminishing marginal predictive returns for knowledge disconcertingly quickly". Quoted in https://infoproc.blogspot.com/2005/12/expert-predictions.html, not the book (2026-09-26; READ-FULL of the router).
- **bears on:** Q6, C1
- **limit:** a model decomposition. The authors concede the noise term may absorb misfit.

F4. **Accretion happens, but each step should be small.** Frequency and step size are separate skills, and step size predicts accuracy better. Qualifies **K1** and **C1**.
- **who:** Atanasov, Witkowski, Ungar, Mellers, Tetlock (*OBHDP* 2020). Abstract posted by Atanasov himself.
- **evidence:** "the most accurate forecasters make frequent, small updates, while low-skill forecasters are prone to make infrequent, large revisions or to confirm their initial judgments … high-frequency updaters … access more information … Small-increment updaters … obtain their advantage from superior accuracy in their initial forecasts."
  - Correlation with accuracy: update size r = .49 in-sample and .45 out-of-sample; update frequency r = −.32.
  - Atanasov in the comments: "effort is probably a more important limiting factor on update frequency".
  - https://statmodeling.stat.columbia.edu/2021/01/31/small-steps-to-accuracy-incremental-updaters-are-better-forecasters/ (2026-09-26; READ-FULL); the size and frequency correlations are from the gwern chapter.
- **bears on:** C1, Q4
- **limit:** geopolitical questions only.

F5. **The "broad pass" is a reference class taken before any news, not a literature survey.** Explicitly hunting for information bought no measurable accuracy. Adds a third option to **K12** and bears on **C2**.
- **who:** Chang, Chen, Mellers, Tetlock (*JDM* 2016), testing CHAMPS KNOW, the GJP training module, in an RCT
- **evidence:**
  - Under an hour of training improved Brier scores by 6–11%.
  - Of the ten principles, "C [comparison classes] was associated with better performance, whereas P and O were associated with worse performance."
  - "Hunt for the right information" was the most-cited principle (n = 2,992) with a mean standardized Brier of 0.38. That is no better than explanations citing no principle (0.37). Comparison classes scored 0.17; "Other perspectives should inform forecasts" scored 0.63, i.e. worse.
  - — http://journal.sjdm.org/16/16511/jdm16511.pdf, Tables 3 and 5 (2026-09-26; READ-FULL)
- **replicated:** Karvetski et al. 2022: comparison-class use measured in forecasters' written rationales r = .32 with accuracy, the largest effect. "Other linguistic variables, such as sources, quotes … did not generalize well across studies." — https://faculty.wharton.upenn.edu/wp-content/uploads/2022/03/SSRN-id3779404.pdf (2026-09-26; READ-FULL)
- **practitioner:** Eli Lifland (#1 on INFER's all-time leaderboard; 9.8k followers): "calibration training and 'always start with the base rate / reference class' gets a large fraction of the gains". — https://www.foxy-scout.com/retro/ (2026-09-26; READ-FULL)
- **bears on:** C2, Q1, Q2
- **limit:** principles were self-tagged. The P (post-mortem) result is confounded, since post-mortems follow misses.

F6. **When no reference class exists, they build one. The class chosen is the step that gets fought over.** Extends **K5** and **K10**.
- **who:** Nuño Sempere (Samotsvety; 5.3k followers); Misha Yagudin, Eli Lifland (Samotsvety); Daniel Kokotajlo
- **evidence:**
  - Sempere: "I asked my friend group for their relationship timelines. This allows me to construct a baserate for the reference class of {…}" — https://x.com/NunoSempere/status/1912134291187720252 (62 likes)
  - Sempere, same habit on observation bias: "Significant streetlight effect in H5N1; US doesn't have the majority of human cases … just the majority of observed cases" — https://x.com/NunoSempere/status/1871317832165707811
  - On the Samotsvety nuclear-risk forecast, Lifland: "~.1%/yr then have adjusted up by a factor of 10".
  - Kokotajlo challenged the class: "not an average month".
  - Yagudin replied with a bound on the update: "So to be 100x of the default rate, one should have put less than 1% on events in Ukraine unfolding as they are now."
  - — https://forum.effectivealtruism.org/posts/KRFXjCqqfGQAYirm5/samotsvety-nuclear-risk-forecasts-march-2022 (2026-09-26; READ-FULL)
- **bears on:** Q3, Q5
- **limit:** the Samotsvety members sell forecasts (Sentinel, askaforecaster), so there is an incentive.

F7. **The randomized human evidence behind "share findings, keep judgment separate".** Extends **K11**, where the critic noted "the only human evidence is ICIJ".
- **who:** Mellers et al., *Psych Science* 2014 (RCT); Horowitz et al., *JOP* 2019
- **evidence (design):**
  - Accuracy ranked teams > "crowd-belief" forecasters (who saw only the distribution of others' numbers) > independent forecasters.
  - Team members "could share information, including their forecasts (but there was no systematic display of team members' predictions)". Each member entered their own forecast, and an algorithm did the aggregating.
  - Comments vs accuracy: r = −.19 and −.22.
  - — https://sydneyscott.nfshost.com/pubs/Psychological_Strategies_for_Winning_a_G.pdf (2026-09-26; READ-FULL)
- **evidence (superteams):**
  - Superforecasters asked more questions and got replies to 23% of them, vs 4% for top-team individuals. Their forecasts converged over a question's life while other groups' diverged.
  - The authors assert this came "at little or no risk of groupthink or premature closure". That is a claim, not a test.
- **evidence (decentralization):**
  - In top teams "the most prolific responder typically gives 3-6 times as many explanations as the average member". In about half of other teams' questions that ratio was "8 or more times".
  - Teamwork topics × analysis topics predicted accuracy only in top teams. A typical message: "Following teammates … after reading [name] links".
  - — r.jina.ai/https://dtingley.scholars.harvard.edu/sites/g/files/omnuum8551/files/dtingley/files/teamwork.pdf (2026-09-26; READ-FULL)
- **BIN on teaming:** mostly noise reduction. Teaming "allows forecasters to harness the information" at short horizons.
- **bears on:** Q7, C6
- **limit:** the tasks are forecasts, not research synthesis.

F8. **Samotsvety's group protocol.** Adds guardrails to **K11**.
- They aggregate with a trimmed geometric mean of odds, dropping the highest and lowest forecast.
- They compute a separate aggregate for members outside their own community: "To reduce concerns of in-group bias to some extent, I calculated a separate aggregate for those who weren't highly-engaged EAs".
- They discussed "the report section by section over the course of a few weekly meetings".
- They solicited a hostile domain-expert review ("a foil").
- A superforecaster, David Manheim, asked about "independent elicitation before discussion". The post doesn't say whether Samotsvety does it.
- — https://forum.effectivealtruism.org/posts/EG9xDM8YRz4JN4wMN/samotsvety-s-ai-risk-forecasts (2026-09-26; READ-FULL)
- **bears on:** Q7, C6
- **limit:** self-report by the group.

F9. **The stop is set by triage and marginal value, not by novelty running out.** Extends **K8**.
- **evidence:**
  - The CHAMPS "S" principle was revised to "Select the right level of effort to devote to each question" (Chang 2016).
  - Tetlock's first commandment: skip "clocklike" and "cloud-like" questions. — https://goodjudgment.com/philip-tetlocks-10-commandments-of-superforecasting/ (vendor page: it sells workshops)
  - Dan Schwarz (FutureSearch CEO, a vendor; ex-Metaculus): the "'dirty secret' of forecasting tournaments - the winners are those that spend the most time. The best strategy is to spend your marginal hour getting into the right ballpark, or doing a quick-and-dirty update". Also: "elite forecasters make far fewer big mistakes". — https://forum.nunosempere.com/posts/qMP7LcCBFBEtuA3kL/the-rationale-shaped-hole-at-the-heart-of-forecasting (2026-09-26; READ-FULL)
- **conditional on setting:**
  - Among independent GJP forecasters, attempting more questions correlated with *worse* accuracy (r = .25). Superforecasters attempted about 40% more.
  - Deliberation time correlated with accuracy (r = −.30) (Atanasov & Himmelstein).
- **bears on:** Q6

F10. **Counter-evidence is committed to in advance.** Extends **K7**.
- Commandment 5: "Each side should list, in advance, the signs that would nudge them toward the other." (vendor page)
- Rationales that hold clashing views ("dialectical complexity") correlate with accuracy at r = .28 (Karvetski).
- Lifland's own post-mortem on a missed AI benchmark forecast: "I anchored on this claim, not seriously considering the likelihood that it was just flat out wrong" (foxy-scout retro).
- **bears on:** C5, Q5

## Against the claims

A1. **Against C5 and C6: months of exchanging arguments did not produce agreement.**
- **who:** Forecasting Research Institute, Existential-Risk Persuasion Tournament (XPT)
- **evidence:** "Few minds were changed during the XPT, even among the most active participants, and despite monetary incentives for persuading others." Also: "why did rational forecasters … not converge after months of debate and the exchange of millions of words". — https://forum.effectivealtruism.org/posts/un42vaZgyX7ch2kaj/announcing-forecasting-existential-risks-evidence-from-a (2026-09-26; READ-FULL)
- **limit:** questions about 2100 that can't be scored. Participants blamed the async format and effort falling off.

A2. **Against C4: being close to the skilled crowd's consensus is itself a sign of skill.**
- **evidence:** proxy scores, based on distance from the consensus of independent first estimates, were the strongest predictor of skill short of accuracy itself: "forecasters whose independent initial estimates were both relatively close to the consensus … and were relatively extreme … tended to be most accurate" (Atanasov & Himmelstein).
- **limit, stated by the authors:** "limited in their utility in spotting accurate forecasters with unique views".
- **practitioner:** Peter Wildeford (37k followers): "I didn't think much about the median forecast but I also didn't end up deviating much from it." — https://x.com/peterwildeford/status/2015833360287805927
- **the edge comes from choosing where the crowd is wrong:** Lifland "selected questions based on the community seeming very wrong, after having received tips from other forecasters" (foxy-scout retro).

A3. **Against "more searching = better" (the flip side of C1):** tagging a forecast with "Hunt for the right information" gained nothing (F5), and superforecasters won within 4 minutes (F3).

A4. **Against C2's justified breadth:** Wildeford's "Second Law - 'The best forecast is usually not the most justifiable forecast.'" — https://x.com/peterwildeford/status/1546199733802336258 (34 likes)

## Not covered by any claim

N1. **What people say they do differs from what they measurably do.** This is a caveat on the sweep's own ranking of self-described practice.
- Karvetski: "The two comparison class variables, self-assessed and model assessed, were correlated by only r(1,048) = .29." Self-assessed use predicted accuracy at r = .15; text-measured use at r = .33.
- Atanasov: "seek ways to assess forecaster tendencies through their behaviors, and rely less on their self-reports."

N2. **Keeping errors small beats finding more signal (BIN):** "Discipline may matter more than creativity."

N3. **Granularity:** superforecasters used 57 distinct probability values vs 29–30 for the others. Rounding to the nearest 10% cost accuracy only for superforecasters (Mellers 2015).

N4. **Auditing a source's track record, including what it deleted.** Sempere on a public earthquake predictor: "he sprays predictions but later deletes the ones that don't work out" — https://x.com/NunoSempere/status/1865028984745963888

## Frontier
- Intersubjective or proxy scoring rules (Witkowski 2017; Himmelstein 2023b): scoring researchers before ground truth exists (Atanasov chapter).
- Arb, "Comparing top forecasters and domain experts" (EA Forum), cited in Lifland's retro.
- Zong et al. 2020: text of GJ Open rationales (past focus good, future focus bad).
- Metaculus "Forecast Fridays": recorded live forecasting sessions by top forecasters, including Wildeford (Schwarz post; x.com/peterwildeford/status/1653546376171495428).
- Joseph & Atanasov 2019: optional training, d = 0.42, argued causal.
- Augenblick & Rabin 2021: a measure of over- or under-reaction in forecast paths.
- Karger, Atanasov & Tetlock, "Improving Judgments of Existential Risk" (FHI 2022).

## Lane state
- Mellers 2015, Mellers 2014, Chang 2016, BIN, Karvetski, Horowitz, Atanasov & Himmelstein 2023 — READ-FULL.
- Atanasov 2020 full paper — BLOCKED (ResearchGate and ACM returned HTML walls). Read via the EC'20 poster (READ-FULL) and the author-posted abstract.
- *Superforecasting* book — MISSING. The Bard excerpt's hostname didn't resolve and archive.org is borrow-only. "Dragonfly eye" and "foxes … seek out information not from one source but many" are available only via Pollock's notes, as a router. Not used as evidence.
- Tetlock Edge 2012 — READ; EMPTY on information gathering.
- Wildeford's NYC-election retro (tumblr) — BLOCKED (429).
- X harvester: 10 calls. The Lifland, Wildeford and Sempere timelines yielded the above. Generic "how I forecast" queries were swamped by finance and weather accounts (EMPTY for this lane).
- Local corpus (guidesfm, researchfms transcripts) — EMPTY: 3 passing mentions only.

## Source register
- https://stanford.edu/~knutson/jdm/mellers15.pdf — READ-FULL
- https://sydneyscott.nfshost.com/pubs/Psychological_Strategies_for_Winning_a_G.pdf — READ-FULL
- http://journal.sjdm.org/16/16511/jdm16511.pdf — READ-FULL
- https://faculty.wharton.upenn.edu/wp-content/uploads/2022/03/mnsc.2020.3882.pdf — READ-FULL
- https://faculty.wharton.upenn.edu/wp-content/uploads/2022/03/SSRN-id3779404.pdf — READ-FULL
- https://dtingley.scholars.harvard.edu/sites/g/files/omnuum8551/files/dtingley/files/teamwork.pdf (via r.jina.ai) — READ-FULL; scholar.harvard.edu copy — BLOCKED
- https://gwern.net/doc/statistics/prediction/2023-atanasov.pdf (via r.jina.ai; direct TLS failed) — READ-FULL
- https://www.sigecom.org/ec20/posters/slides-450.pdf — READ-FULL
- https://statmodeling.stat.columbia.edu/2021/01/31/small-steps-to-accuracy-incremental-updaters-are-better-forecasters/ — READ-FULL
- ResearchGate and dl.acm.org Atanasov PDFs — BLOCKED
- https://goodjudgment.com/philip-tetlocks-10-commandments-of-superforecasting/ — READ-FULL
- https://goodjudgment.com/superforecaster/ — EMPTY
- https://rufuspollock.com/post/tetlock-gardner-2015-superforecasting-the-art-and-science-of-prediction/ — READ-PARTIAL (router)
- https://infoproc.blogspot.com/2005/12/expert-predictions.html — READ-FULL (router)
- https://www.edge.org/conversation/philip_tetlock-how-to-win-at-forecasting — READ, EMPTY
- https://forum.effectivealtruism.org/posts/KRFXjCqqfGQAYirm5/samotsvety-nuclear-risk-forecasts-march-2022 — READ-FULL
- https://forum.effectivealtruism.org/posts/EG9xDM8YRz4JN4wMN/samotsvety-s-ai-risk-forecasts — READ-FULL
- https://www.foxy-scout.com/retro/ — READ-FULL
- https://forum.nunosempere.com/posts/qMP7LcCBFBEtuA3kL/the-rationale-shaped-hole-at-the-heart-of-forecasting — READ-PARTIAL
- https://forum.effectivealtruism.org/posts/un42vaZgyX7ch2kaj/announcing-forecasting-existential-risks-evidence-from-a — READ-FULL
- https://peterhurford.tumblr.com/post/658521880125489152/successful-forecasting-retrospective-2021-nyc — BLOCKED
- http://faculty.bard.edu/hhaggard/teaching/sci127Sp20/notes/TetlockGardnerSuperforecasting1.pdf — MISSING
- X (twitterapi.io): x.com/NunoSempere/status/1912134291187720252, /1865028984745963888, /1871317832165707811; x.com/peterwildeford/status/1546199733802336258, /2015833360287805927, /1653546376171495428; x.com/eli_lifland/status/1489697386490474500; x.com/SamotsvetyF/status/1571323532508008448 — READ

All fetches 2026-09-26. Working copies are in `/private/tmp/claude-501/-Users-seventyleven-Desktop/fcd46374-4e61-45da-ae77-538c40287f4b/scratchpad/r3-2/`.