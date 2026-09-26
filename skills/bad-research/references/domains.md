# Domains — where the alpha lives, field by field

Read this at **Frame**, for every domain your facets touch. A lane file says *how* to reach a kind of
source; this says *which* sources carry the truth in a given field, where its criticism is kept, who
writes outside the formal channels, and what you can run yourself. The same five questions work
everywhere; the answers differ by field, and a run that asks them in the wrong field's terms reads the
marketing layer and misses the record.

The five questions, for any field:

1. **Where is the truth written first?** Almost never the summary. Usually an artifact: code at a
   version, a registry, a filing, a trial protocol, the rendered product, the appendix.
2. **Where is the criticism kept?** Every field has a place its disagreements live — issue trackers,
   reviews, replications, short reports, dissents — and it is rarely where the claim is.
3. **Who writes outside the formal channel?** Maintainers, reviewers, practitioners in reply threads,
   people after they left the company. Reach them through what they wrote.
4. **What can you run yourself?** A repro, a re-run, a measurement of the live thing. A number you
   measured outranks every number you read (`references/lanes/live-instrument.md`).
5. **What does popularity get wrong here?** Each field has its own ranking trap.

---

## Software, infrastructure, databases

- **Truth first: the source at a pinned version**, then its changelog, then its docs. In a blind test
  on a Postgres-pooler question, the facts both answers rested on came from reading the pooler's code at a
  release tag, and the vendor's own docs said the opposite of the code ("same as PgBouncer"); what then
  decided between the answers was coverage of the asker's own client libraries and a runnable inventory
  query. Docs lag code; when they disagree, the code runs. `references/lanes/artifact-re.md`,
  `references/lanes/delta-vs-pinned-ref.md`.
- **Criticism: the project's own issue tracker and PRs** — reproductions, maintainer comments ("a known
  footgun"), reverted commits, fixes merged to main but in no tag yet. An issue's state and premise are
  claims as of its date: closed is not fixed until you find the fix commit, and an open issue can
  describe code that has since changed — read the code at the current release before repeating either
  (a blind judge caught "no parser exists" from an open issue when the release already shipped one).
  Mailing lists for the database itself (a leaked planner setting that turned a 20-second query into
  two hours surfaced only on pgsql-general).
- **Outside the channel:** maintainers' blogs and talks; engineering writing from teams that operate it
  at scale (AWS Builders' Library and the rest of `~/Desktop/compound-v/references/publications.tsv`).
- **Run it:** a minimal repro against the exact version — a number you measured outranks every number
  you read. Read a project's own tests for what it claims to support, but check whether a skipped test is
  skipped in every mode before treating it as evidence about one.
- **Popularity trap:** tutorials and accepted answers. On Stack Overflow, 58.4% of obsolete answers were
  already obsolete when posted and only 20.5% are ever updated — read the comments and the non-accepted
  answers, and date everything.
- **The asker's stack is a facet.** The client libraries they use carry their own defaults (a migration
  tool that takes session locks, a job queue whose notifier needs a session) — read those packages too.
- **Rosters:** `~/Desktop/compound-v/references/exemplars.tsv` (real codebases, pinned),
  `talks.tsv`, `publications.tsv`; `bash ~/Desktop/compound-v/scripts/alpha.sh "<topic>"` sweeps talks,
  arXiv, exemplar repos, engineering blogs and practitioners in one command and returns pointers.

## AI and ML research, research engineering

- **Truth first: the paper's body, appendix, ablations and limitations**, then the code at a commit.
  "The appendix is where the bodies are buried"; one lab's key result sat in appendix A.6. The newest
  work is often in code before any paper ("TODO(noam): write a paper"), or inside labs.
- **Criticism: re-runs, reimplementations, ablations, and later work that challenges it.** Researchers
  who re-ran evals found some improve and some get worse; a 738-follower researcher re-ran a big-lab
  benchmark, found a code bug and six wrong labels in twenty, and the paper was withdrawn — five peer
  reviews had missed it. Check the baselines ("a lot of academic papers have baselines that are nerfed"),
  and whether the boring explanation was tested.
- **Outside the channel:** researchers on X — Latest and reply threads, not Top
  (`references/lanes/x-live.md`); long interviews (`references/lanes/practitioner-video.md`); the local
  transcripts (`ICML_TRANSCRIPTS.md` alone lists ~3,000 researcher names) and the x-guides lane, the
  strongest local material for agents, evals and harnesses (`references/lanes/local-corpus.md`).
- **Rare places:** non-English labs (read their papers and posts in the original, translated),
  pre-deep-learning literature (attacks "rediscovered over and over"), overlooked early papers (the
  2017 Baidu scaling paper).
- **Run it:** re-run the eval or the ablation at matched budget before you believe a delta.
- **Popularity trap:** paper curators. Being posted by a top curator went with 2–3× the citations of a
  control group; one curator's bio reads "dm for promo". Benchmarks leak into training data and into
  search results — exclude the answer key's domains.

## Design — product UI, interaction, visual

- **Truth first: the live, rendered product, measured** — drive it with `silver`, ask elements what they
  *computed* (`getComputedStyle`, `getBoundingClientRect`), composition before tokens. Counting a site's
  stylesheet measures its codebase: the "house easing" counted 122 times in one company's CSS did not
  appear once on the rendered page. A check that greps CSS text cannot see a cascade, a shorthand or a
  keyword.
- **The process record:** a design team's commit history states the decision behind each rule and what
  was tried first — clone with full history and read it in windows.
- **Outside the channel:** designers' own writing and threads (the x-guides lane holds exactly three
  design threads; route the rest through `~/Desktop/guidesfm/GUIDES_DESIGN_ENGINEERING.md` and
  `GUIDES_APPLE_HIG.md`), and the platform's own engineering sessions (WWDC in `channels.tsv`).
- **Criticism and judgment:** an untrained eye is a trustworthy defect detector and a broken chooser.
  An agent can verify that a claim about a design is true; it cannot certify that a design is good —
  that needs a credentialed eye or a blind comparison, and the answer should say which it had.
- **Popularity trap:** showcase sites rank what photographs well, not what ships well.

## Science, health, any empirical literature

- **Truth first: the registered protocol and the primary paper's methods and results**, the supplement,
  individual-level data where it exists; systematic reviews as maps, then their primaries.
- **Criticism: replications, retractions, funding, and the unpublished.** Failed replications are cited
  by a small minority of later citers (under 3–12% in most audits; one rose from 13% to 41%), so search
  the original's "cited by" for them — `bash scripts/cite-chain.sh rerun <doi>`.
  Only 5.4% of citations made after a retraction mention it — check status at the source.
  Industry-sponsored trials reach favourable conclusions more often (RR 1.34) while scoring *better* on
  standard risk-of-bias tools. Published trials show larger effects than unpublished ones (≈15%).
  Mechanical checks catch what reading does not (an impossible mean for its n).
- **Build the claim's citation network yourself.** In one audited claim, supportive papers received 94%
  of citations and the six refuting papers 6% — following reviews never reaches the refutations; list
  the primary-data papers.
- **Vocabulary:** harvest search terms from the index terms of records you already know are relevant,
  and hold some back to test recall (seed-derived searches reached 97% sensitivity vs 75% for
  hand-built ones); a drug has a code, a generic and a brand name, and registries use different ones.
- **Stop:** recall matters here — run the independent check pass (`references/rounds.md`).
  `references/lanes/evidence-synthesis.md` is this field's professional method.
- **Popularity trap:** a confident claim repeated widely usually traces to one origin; trace it.

## Companies, markets, startups

- **Truth first: filings for the exact period** — the SEC EDGAR filing index for that 10-Q/10-K, the
  Companies House filing history and the accounts made up to that date — dated press releases, and the
  product and its pricing as of a date (`references/lanes/terms-and-pricing.md`,
  `references/lanes/artifact-re.md`). Not the most recent filing, and not commentary on it.
- **Criticism:** short-seller reports (they talk their book — use them for the records they found, not
  the conclusion), filings compared across jurisdictions, customer threads, former employees writing
  after they left. Rank testimony by what the author had to sell: ex-employees > work described in
  passing > current insiders > recruiting content, which is cut.
- **Rare places:** whole registries downloaded and read (one investigation catalogued an entire
  offshore registry); open records "the competition usually isn't doing this work" on.
- **Outside the channel:** founders and operators in long interviews — the local transcripts and the
  407 product teardowns (`references/lanes/local-corpus.md`).
- **Popularity trap:** a vendor's number about itself is marketing, whatever its domain tier.

## Law, policy, terms

- **Truth first: the text as of a date** — the statute, the regulation, the court filing, the terms
  page at a version — never a summary of it. What changed since a date: `references/lanes/delta-vs-pinned-ref.md`.
- **Criticism:** the opposing brief, the dissent, the enforcement action.

## People — who is good at X, including the ones nobody ranks

- **Judge by the work and the track record, never by reach.** Among experts predicting trial outcomes,
  h-index and accuracy correlated at r = 0.00; in Tetlock's expert study, fame went with overconfidence
  (r = 0.33). Forecasting skill is found by keeping score. Experts trust small accounts on the
  work ("I have no idea who this person is (small account), but this thread is exactly correct").
- **Find the unranked:** walk links from a seed — co-authors, acknowledgements, "who do you read",
  reply threads — and ask authors which of their own papers the field missed.
  `references/lanes/people-track-record.md`, `references/breadth.md`.

---

## Across every field

- **Search by what a thing does, not what it is called** (patent examiners: "a tea mixer and a
  concrete mixer … the mixing art"), and find the field's own name before concluding absence.
- **Rare information sits in the same few places in every field**: appendices and supplements, code and
  data, registries and filings, the unpublished and the old, other languages, and people's own writing
  outside the formal channel.
- **Criticism lives somewhere other than the claim.** Name that place for the field before the counterpart
  round, and send a reader there.
