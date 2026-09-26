<!-- AGENT OUTPUT — R2-3 popularity vs rank. Returned by a subagent, not read by the chair unless a row says so. -->

## Findings

F1. **A search engine's ranking can put worse pages on top when the pages are optimised for it.** Over one year, Google, Bing and DuckDuckGo were tracked on 7,392 product-review queries. Pages ranked higher had more affiliate links (r = −.99), were more repetitive, and were less readable. A plain BM25 engine over ClueWeb22 (ChatNoir) returned far fewer affiliate pages: 18% of its results, against 29–42% on the commercial engines and a 2.35% base rate across the whole web.
    who:      Bevendorff, Wiegmann, Potthast, Stein. Academic IR group (Leipzig/Weimar), ECIR 2024. Nothing to sell.
    evidence: "at the population level, we can conclude that higher-ranked pages are on average more optimized, more monetized with affiliate marketing, and they show signs of lower text quality." — https://downloads.webis.de/publications/papers/bevendorff_2024a.pdf §6 (2026-09-26; READ-FULL)
    bears on: Q2, C4. **Extends K6**: public rank is not only lagging, it is gamed by others.
    limit:    Product reviews only. Averages across the population "cannot predict the rank of individual pages". Google's ranker updates helped, but only for a short time.

F2. **In health search, optimised pages were rated less expert.** A user study (N=61, laypeople and experts) rated non-optimised health pages as more expert, and the two groups did not differ.
    who:      Schultheiß, Häußler, Lewandowski. HAW Hamburg, CHIIR 2022.
    evidence: "The subjects rated the expertise of non-optimized web pages as higher than the expertise of optimized pages" — https://arxiv.org/pdf/2301.10105 (2026-09-26; READ-PARTIAL)
    bears on: Q2, C4. Extends K6 and connects it to K10.
    limit:    Small N. It measures perceived expertise, not verified accuracy.

F3. **Luu finds unpopular pages by walking the link graph.** When Google will not return a page he remembers, he searches for a page that links to it and follows the links by hand, using archive.org for dead ones. In his six-query test, Marginalia (a one-person engine for the small, non-commercial web) had the lowest scam rate of the search engines.
    who:      Dan Luu. Engineer, Patreon-funded.
    evidence: "I have to remember some text in a page that links to the page … and then manually navigate the link graph to get to the page." Also, hearsay from people who build rankers: engagement signals "only drive users to the best results when users are sophisticated enough to know what the best results are" — https://danluu.com/seo-spam/ (2026-09-26; READ-FULL)
    bears on: Q1, Q3, C4. **Connects K2 (citation chasing) with K6**: on the web, link-chasing reaches pages the ranking will not show.
    limit:    Six naive queries and one rater. Marginalia returned "no results" or wrong results on three of the six.

F4. **Ranking by citations pushes grey literature deep into the results.** Across 1,364,757 articles, citation count was Google Scholar's heaviest ranking factor. 16.7% of rank-1 results had more than 1,000 citations, though such papers are 0.8% of the total. In seven systematic-review case studies, grey literature (reports and papers outside commercial journals) was most concentrated at page 80 ±15 for full-text searches and page 35 ±25 for title searches. It did not make up most of a page until pages 20–30. Common practice screens only the first 50–100 results.
    who:      Beel & Gipp (RCIS 2009). Haddaway et al. (PLOS ONE 2015, environmental evidence synthesis).
    evidence: "more suitable for searching standard literature than for gems or articles by authors advancing a view different from the mainstream" — https://isg.beel.org/pubs/Google%20Scholar's%20Ranking%20Algorithm%20-%20The%20Impact%20of%20Citation%20Counts%20--%20preprint.pdf ; "should revise the current common practice of searching the first 50–100 results (5–10 pages) in favour of a more extensive search" — https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0138237 (2026-09-26; READ-PARTIAL both)
    bears on: Q3, Q6, C4. **Connects K6 with K10**: the rare material K10 lists sits exactly where citation-weighted ranking puts it, far past the top 10.
    limit:    Scholar's 2009 ranking weights may have changed. Scholar shows at most 1,000 records. Haddaway also found that a general Scholar search missed all of the grey literature that one case study had found by searching organisations' own websites.

F5. **The best-scoring AI answer engine cited the fewest sources that Google ranks.** Only 15.99% of GPT-5's cited sources appeared in Google's first five pages of results (roughly the top 50), and GPT-5 had the highest source-quality score (89.08). Tavily had the most overlap with Google (55.45%) and scored lowest (78.27).
    who:      Jin, Liu, Li, Malik, Zhang. UCSD and **GenseeAI Inc.**, whose own product is in the comparison and ranks third. That is an incentive to note.
    evidence: "good sources are mostly not in the one-shot, keywordbased searches" — https://arxiv.org/pdf/2602.16942 §5.2, Table 8 (2026-09-26; READ-PARTIAL)
    bears on: Q2, Q3. Adds to the KNOWN note that tools return the top 10 or 30.
    limit:    100 queries, scored by an LLM. It is a correlation across 11 systems.

F6. **Promoting a few untested items into the ranking raised quality.** In a live study, 962 volunteers used a joke site for 45 days. Placing new pages just below rank 20 raised the share of "funny" votes by about 60% over ranking purely by popularity. From simulation, the authors recommend 10% randomisation starting at rank 1 or 2, aimed only at pages nobody has seen yet. The same group (via Cho & Roy, not opened) reports that popularity ranking delays wide awareness of a high-quality page by "a factor of over 60".
    who:      Pandey, Roy, Olston, Cho, Chakrabarti. CMU/UCLA, VLDB 2005.
    evidence: "The ratio achieved using rank promotion was approximately 60% larger than that obtained using strict ranking by popularity." — https://arxiv.org/pdf/cs/0503011 §1.3 (2026-09-26; READ-PARTIAL)
    bears on: C4. **Partly fills the K6 gap.** This is measured deliberate sampling of the unpopular.
    limit:    It measures quality averaged over a community's clicks, not the answer of one investigation. The "quality" was funniness.

F7. **Hacker News has sampled overlooked posts on purpose since 2014.** Moderators hand-pick old submissions that got no attention, and software places one at random on the lower front page. The list is public at /pool. This is F6's design run by people.
    who:      Daniel Gackle (dang), HN moderator. HN is owned by YC.
    evidence: "These get put into a hopper from which software randomly picks one every so often and lobs it randomly onto the lower part of the front page." — https://news.ycombinator.com/item?id=26998308 (via hn.algolia.com API; 2026-09-26; READ-FULL)
    bears on: Q1, Q3, C4. Connects F6 and F8.
    limit:    No hit rate has been published.

F8. **Among retracted and false material, attention runs higher.** Compared with matched articles from the same journal issue, retracted articles were 1.2–7.4 times more likely to get more Altmetric attention, even after adjusting for attention after the retraction. On Twitter from 2006 to 2017, false news spread "significantly farther, faster, deeper, and more broadly than the truth", and false news was "more novel".
    who:      Serghiou, Marton, Ioannidis (Stanford METRICS). Vosoughi, Roy, Aral (MIT, Science 2018).
    evidence: see above — https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0248625 ; https://pubmed.ncbi.nlm.nih.gov/29590045/ (abstract only) (2026-09-26; READ-PARTIAL)
    bears on: Q2, C4. **Extends K6** (likes over-select announcements) with measured cases where attention goes up as reliability goes down.
    limit:    News and retractions, not everyday research sources.

F9. **Who engages matters: researcher readership tracks expert-judged quality, broad attention barely does.** Across 67,030+ articles peer-scored in REF2021, the UK's national research assessment, Mendeley reader counts (researchers saving a paper) were the best altmetric, "close to Scopus citations". Tweeter counts came next, with an average correlation of about 0.18. The same measure on 2008 papers (REF2014) averaged 0.06. On F1000Prime, a post-publication expert review service, tweets formed a separate dimension from citations and readership and related to quality less than either.
    who:      Thelwall et al. (Wolverhampton; they build altmetric methods). Bornmann & Haunschild (Max Planck).
    evidence: "Mendeley is close to Scopus citations in power as a research quality indicator, and Tweeters is clearly the best of the social web indicators" — https://arxiv.org/pdf/2212.07811 ; "citation-based metrics and readership counts are significantly more related to quality, than tweets" — https://arxiv.org/pdf/1711.07291 (2026-09-26; READ-PARTIAL)
    bears on: Q2, C4. **Connects K6's "expert popularity is a usable router"** to a measurement: popularity among researchers tracks peer judgement; public attention barely does.
    limit:    These are aggregate correlations, strongest in health and physical sciences and weakest in arts and humanities.

F10. **Engagement ranking picks posts readers say they do not want.** In a pre-registered audit (N=806, February 2023), Twitter's engagement ranking was compared with a reverse-chronological feed of accounts followed. Users preferred the engagement feed's tweets only slightly overall and were less likely to prefer the political tweets it chose.
    who:      Milli, Carroll, Wang, Pandey, Zhao, Dragan (Cornell Tech/Berkeley). PNAS Nexus 2025.
    evidence: "users do not prefer the political tweets selected by the algorithm" — https://arxiv.org/pdf/2305.16941 (2026-09-26; READ-PARTIAL)
    bears on: Q1, Q2, C4. A feed that is not ordered by popularity (who you follow, newest first) is a working entry point.
    limit:    It measures stated preference, not research value.

F11. **For an LLM, searching pays most on unpopular entities and can hurt on popular ones.** Retrieval "helps significantly" for long-tail entities (popularity measured by Wikipedia page views). For popular entities it can hurt large models, because "the retrieved context can be misleading". Scaling models mainly improves recall of popular facts.
    who:      Mallen, Asai, Zhong, Das, Khashabi, Hajishirzi (UW/AI2). ACL 2023.
    evidence: "LMs struggle with less popular factual knowledge, and that retrieval augmentation helps significantly in these cases" — https://arxiv.org/pdf/2212.10511 (2026-09-26; READ-PARTIAL)
    bears on: Q3, Q6. Adds the WHEN to K6: search effort pays in the tail.
    limit:    Single-hop factual QA only.

## Against the claims

A1. **Among posts that got seen, popularity tracked quality well (against C4).** "Quality" was estimated as the vote rate an article would get with bias-free exposure. Its Spearman correlation with score was .80 on Hacker News and .54 on r/worldnews; MusicLab was .57. But only 1,500 of 5,000 HN submissions ever reached the top ranking, and the rest were excluded.
    who:      Greg Stoddard (Northwestern), 2015.
    evidence: "we must interpret that as only being among a set of articles that received at least a reasonable amount of attention … Its likely there are a number of high quality articles that were discarded" — https://arxiv.org/pdf/1501.07860 §7 (2026-09-26; READ-FULL)
    bears on: C4. Limit: the unseen tail was never measured, which is exactly the part F7 samples.

A2. **Search engines send traffic toward less popular sites (against the rich-get-richer assumption).** Measured on 28,164 sites, traffic grew slower than in-degree (the number of links pointing in). The mechanism is that specific queries return small result sets, inside which low-PageRank pages rank at the top.
    who:      Fortunato, Flammini, Menczer, Vespignani (Indiana). WWW 2006, arXiv version of the PNAS paper.
    evidence: "directing more traffic toward less popular sites, even in comparison to what would be expected from users randomly surfing the Web" — https://arxiv.org/pdf/cs/0511005 (2026-09-26; READ-PARTIAL)
    bears on: C4. **Connects K5 and K6**: a specific query in the field's own terms is how a top-10-limited tool reaches the tail.
    limit:    2006 web, Alexa traffic data.

A3. **Scholarly citation spread out rather than narrowed (against Evans in K2).** Citations to journals outside each field's top 10 rose from 27% of all citations in 1995 to 47% in 2013. The number of top-1,000 papers published in those journals went from 149 to 245.
    who:      Acharya, Verstak et al. **Google Scholar staff**, who credit their own search tool. That is an incentive to note.
    evidence: "the percentage of citations to articles in non-elite journals went from 27% of all citations in 1995 to 47% in 2013" — https://arxiv.org/pdf/1410.2217 (2026-09-26; READ-PARTIAL)
    bears on: K2's limit and K6. Limit: it shows no cause.

## Not covered by any claim

N1. **Weight an answer by how much more popular it is than people predicted, not by raw popularity.** Majority voting loses specialised minority knowledge. Picking the "surprisingly popular" answer cut errors by 21.3% against majority vote across 490 items, and by 35.8% across the 290 items where confidence was also measured.
    who:      Prelec, Seung, McCoy (MIT/Princeton). Nature 2017.
    evidence: "biased for shallow, lowest common denominator information, at the expense of novel or specialized knowledge that is not widely shared" — https://marketing.wharton.upenn.edu/wp-content/uploads/2017/08/11-02-2017-McCoy-John-PAPER.pdf (2026-09-26; READ-PARTIAL)
    bears on: C4, C5.

N2. **Low-attention sources can pay because few people have used them yet, not because they are better.** Holding firm size fixed, momentum strategies worked "particularly well among stocks which have low analyst coverage". The authors read this as firm-specific, especially negative, information "diffuses only gradually". This connects to the practice in K6/K10 of going to records "the competition ignores".
    who:      Hong, Lim, Stein. NBER w6553, 1998.
    evidence: https://www.nber.org/system/files/working_papers/w6553/w6553.pdf p.3. The PDF is a scan; I read the page as a rendered image (2026-09-26; READ-PARTIAL).

N3. **Engines "against popularity" use proxies other than obscurity, and none measure the result.**
    - Marginalia prefers text-heavy, old-looking sites (a "Lindy-effect" age proxy) and warns: "If you are looking for facts you can trust, this is almost certainly the wrong tool. If you are looking for serendipity, you're on the right track." — https://www.marginalia.nu/marginalia-search/about/ (READ-FULL)
    - Kagi Small Web has 41,200 feeds (counted live). Its rules ban ads and undisclosed affiliate links, admit only single-author personal blogs, and cap YouTube channels at "fewer than 100,000 subscribers", which is a popularity cap. Kagi is a paid search vendor. — https://github.com/kagisearch/smallweb (READ-FULL)
    - **Exa is not anti-popularity.** Its founder: "if everyone is sharing some Paul Graham essay … our model is more likely to predict it … high canonicity". Its advantage is matching different wordings of a request, not reaching unpopular pages. — https://www.latent.space/p/exa (published podcast transcript, which may be machine-generated; READ-PARTIAL)

**Stated plainly:** I found **no study where an investigator who deliberately sampled low-ranked or unpopular sources got a better answer** than one who did not.
- The measured evidence is at other levels: a ranking system serving a community (F6), crowd aggregation (N1), where rare material sits in results (F4, F5), and when searching pays for a model (F11).
- I also found **no measured study showing that low-engagement posts by credible authors carry more signal**. F9 and F10 are the nearest.

## Frontier
- Rank drives clicks regardless of relevance. When the top two results were swapped, users still clicked position 1: 15 vs 1 compared with 7 vs 10, p = .003 (Joachims et al. TOIS 2007, https://www.cs.cornell.edu/people/tj/publications/joachims_etal_07a.pdf). This is the search-engine version of MusicLab.
- Kammerer & Gerjets: grouping results into objective, subjective and commercial columns instead of a ranked list led users to pick objective sources more often (https://doi.org/10.1080/0144929x.2011.599040; DIGEST-ONLY).
- Stack Overflow: 58.4% of obsolete answers were probably obsolete when first posted, and only 20.5% are ever updated. The authors advise reading comments and non-accepted answers (https://arxiv.org/pdf/1903.12282).
- Salganik & Watts 2008 "Leading the herd astray" (popularity inverted), Branch et al. RCT on Twitter promotion and citations, Peng et al. PNAS 2022 on attention to retracted papers: not opened.

## Lane state
- Bevendorff, Luu, Fortunato, Pandey, Stoddard, Milli, Thelwall, Bornmann F1000, Serghiou, SourceBench, Haddaway, Beel, Prelec, Mallen, Acharya, Schultheiß, Marginalia, Kagi, HN pool: READ (full or partial).
- Hong–Lim–Stein: READ-PARTIAL (scanned; rendered to image).
- Cho & Roy 2004 (oak.cs.ucla.edu): MISSING (HTTP 000). Pandey used as the router.
- VLDB Pandey PDF: BLOCKED (403). Used arXiv instead.
- Million Short: BLOCKED (Cloudflare).
- Vosoughi full text: BLOCKED (science.org bot wall, jina too). Read the PubMed abstract.
- Health rank-vs-quality: EMPTY for a large study that correlates position with quality. Daraz 2019 (PMC6712138) READ and silent on rank. Kitchens 2014: DIGEST-ONLY via a UF news release.
- Exa blog: MISSING (404).
- Bornmann 2015 meta-analysis (arXiv 1407.8010): downloaded, not read. Its pooled r = 0.003 for Twitter is DIGEST-ONLY.

## Source register
- https://danluu.com/seo-spam/ — READ
- https://downloads.webis.de/publications/papers/bevendorff_2024a.pdf — READ
- https://arxiv.org/pdf/cs/0511005 — READ-PARTIAL
- https://arxiv.org/pdf/cs/0503011 — READ-PARTIAL
- https://www.vldb.org/conf/2005/papers/p781-pandey.pdf — BLOCKED
- http://oak.cs.ucla.edu/~cho/papers/cho-bias.pdf — MISSING
- https://isg.beel.org/pubs/Google%20Scholar's%20Ranking%20Algorithm%20-%20The%20Impact%20of%20Citation%20Counts%20--%20preprint.pdf — READ-PARTIAL
- https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0138237 — READ-PARTIAL
- https://arxiv.org/pdf/2602.16942 — READ-PARTIAL
- https://arxiv.org/pdf/2305.16941 — READ-PARTIAL
- https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0248625 — READ-PARTIAL
- https://pubmed.ncbi.nlm.nih.gov/29590045/ — READ (abstract)
- https://arxiv.org/pdf/2212.07811 — READ-PARTIAL
- https://arxiv.org/pdf/1711.07291 — READ-PARTIAL
- https://arxiv.org/pdf/1407.8010 — downloaded, not read
- https://arxiv.org/pdf/1501.07860 — READ
- https://marketing.wharton.upenn.edu/wp-content/uploads/2017/08/11-02-2017-McCoy-John-PAPER.pdf — READ-PARTIAL
- https://arxiv.org/pdf/2212.10511 — READ-PARTIAL
- https://arxiv.org/pdf/1410.2217 — READ-PARTIAL
- https://arxiv.org/pdf/2301.10105 — READ-PARTIAL
- https://www.nber.org/system/files/working_papers/w6553/w6553.pdf — READ-PARTIAL
- https://www.cs.cornell.edu/people/tj/publications/joachims_etal_07a.pdf — READ-PARTIAL
- https://arxiv.org/pdf/1903.12282 — READ-PARTIAL
- https://pmc.ncbi.nlm.nih.gov/articles/PMC6712138/ — READ (EMPTY on rank)
- https://archive.news.ufl.edu/articles/2014/04/consumer-be-aware-quality-of-health-related-internet-searches-varies.html — READ (router)
- https://about.marginalia-search.com/ ; https://www.marginalia.nu/marginalia-search/about/ — READ
- https://github.com/kagisearch/smallweb ; https://blog.kagi.com/small-web — READ
- https://www.latent.space/p/exa — READ-PARTIAL
- https://news.ycombinator.com/item?id=26998308 — READ
- https://millionshort.com/about — BLOCKED
- https://doi.org/10.1080/0144929x.2011.599040 — DIGEST-ONLY

All fetched 2026-09-26. Scratch copies are in /private/tmp/claude-501/-Users-seventyleven-Desktop/fcd46374-4e61-45da-ae77-538c40287f4b/scratchpad/r23/.