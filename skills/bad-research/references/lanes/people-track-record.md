# Lane: people-track-record

## Reach for this when
- The question is "who should I believe on X" and the candidate answers are opinions, not runnable checks.
- A claim is load-bearing and you need the author's *incentive at the time of writing* before you weight it.
- A pooled result looks corroborated and you have not yet collapsed it by person / company / commercial orbit.
- You are about to cite someone because they are prominent. Prominence is not track record on *this* question.

## Commands
```bash
P=~/Desktop/compound-v/references/practitioners.tsv
# Roster: 3 TAB-separated cols (x-handle, who they are, what they shipped/operate). Header is
# COMMENT LINES (#), not a header row — 45 data rows under ~37 lines of preamble as of 2026-09-08.
grep -v -e '^#' -e '^$' "$P" | awk -F'\t' '{print $1"\t"$2}'        # -> 45 rows
grep -v -e '^#' -e '^$' "$P" | grep -Ei 'harness|agent|context'     # -> 26 topic-matched rows

# Collapse by ORBIT before calling anything corroborated. Counts DISTINCT ROWS, not occurrences.
grep -v -e '^#' -e '^$' "$P" | grep -Ei 'harness|agent|context' \
 | while IFS=$'\t' read -r h who what; do
     org=$(printf '%s' "$who" | grep -owE 'Anthropic|Cursor|Cognition|Letta|Replit|LangChain|Vercel|Linear|Braintrust|Sourcegraph|Google|Browserbase|Manus|HumanLayer|MIT|Amp|HashiCorp' | head -1)
     printf '%s\t%s\n' "${org:-INDEPENDENT}" "$h"
   done | sort | awk -F'\t' '{c[$1]++; n[$1]=n[$1]" "$2} END{for(k in c) printf "%s\t%d\t%s\n",k,c[k],n[k]}' | sort -k2 -rn
# real output head: INDEPENDENT 5 | Anthropic 4 (alexalbert__ ErikSchluntz RLanceMartin trq212)
# | Replit 2 | Letta 2 | then 13 singletons. 26 candidates -> 17 orbits.

# Their own domain (the `blog` field IS the domain to scope to) + what they actually ship:
gh api users/simonw --jq '{name,company,blog,followers}'
#   -> {"blog":"https://simonwillison.net/","company":"Datasette","followers":16794,...}
gh api "users/simonw/repos?per_page=100&sort=pushed" --jq 'sort_by(-.stargazers_count)[:3]|.[]|"\(.stargazers_count)\t\(.full_name)\t\(.pushed_at)"'
#   -> 12475 simonw/llm 2026-09-08T02:01:51Z ; 11443 simonw/datasette ; 2563 simonw/shot-scraper
gh api "users/simonw/events/public?per_page=100" --jq '[.[]|select(.type=="PushEvent")]|group_by(.repo.name)|map({repo:.[0].repo.name,pushes:length})|sort_by(-.pushes)[:5]'
#   -> [{"pushes":12,"repo":"simonw/llm"},{"pushes":8,"repo":"simonw/tools"},...]
#   Stars are a resume; events are this month's shipping. Use events to separate builder from alum.

# Their WRITING (prefer this over posts — an essay is quotable, a post usually is not):
WebFetch https://borischerny.com  "List the essay titles and dates verbatim."
#   -> 17 dated essay titles, newest "Jun 19, 2024 — NPM and NodeJS should do more to make ES Modules easy to use"
WebSearch "<name> <topic>" allowed_domains:["<their blog domain from gh api>"]   # NOT verified this run — see Traps
```

## Reachability probe
```bash
P=~/Desktop/compound-v/references/practitioners.tsv
printf 'roster=%s gh=%s\n' "$(grep -c -v -e '^#' -e '^$' "$P" 2>&1)" "$(gh api users/simonw --jq .login 2>&1|head -1)"
```
- **WORKING** → `roster=45 gh=simonw` (integer ≥1 and a bare login)
- **GENUINELY EMPTY** → `roster=0 gh=simonw` — file present, every line a comment; nothing to rank, say so.
- **BROKEN** → `roster=ugrep: warning: ...: No such file or directory` (roster side), or
  `gh=gh: Not Found (HTTP 404)` / `gh=error connecting to ...` (network/auth side). All three verified 2026-09-08.

## What counts as evidence here
A person-claim needs four parts, in this order:
1. **Person + handle** — `practitioners.tsv:<line>` (e.g. `practitioners.tsv` row `simonw`).
2. **What they SHIPPED, not said** — `github.com/simonw/llm`, 12,475 stars, pushed 2026-09-08 (from `gh api`, as-of date required).
3. **The artifact you are quoting** — a URL on *their own domain* + as-of date (`https://borischerny.com`, read 2026-09-08). An essay URL, not a post.
4. **Their incentive when they wrote it** — employer/founder role at that date, from `gh api .company` or the roster's col 2. "Founder of the vendor whose product this endorses" is the finding, not a footnote.
Never cite a WebSearch digest as a quotation — it is a paraphrase (`~/.claude/.../memory/x-twitter-retrieval-paths.md`).

## Traps
- **An X handle is not a GitHub login, and a login that RESOLVES is not evidence it is the right
  account.** Measured 2026-09-08 across five roster handles: `alexalbert__` does not resolve at all
  (a clean, visible failure). The dangerous one is `GeoffreyHuntley`, which resolves — GitHub
  case-folds it to `geoffreyhuntley` — and returns **0 recent PushEvents**, which this lane's
  builder-vs-alum discriminator reads as "not shipping". It is the wrong account. Side by side:

  | login | repos | followers | blog field |
  |---|---:|---:|---|
  | `geoffreyhuntley` | 47 | **1** | `https://github.com/ghuntley/` — it points at another profile |
  | `ghuntley` | 810 | **2,870** | `https://www.ghuntley.com/` |

  A prolific practitioner would have been filed as an alum by a lane step that succeeded. **The tell
  is inside the profile you already fetched**: a follower count in single digits beside a real
  repo count, and a `blog` field pointing at another GitHub profile rather than at a site. Read
  those two fields before you read the event count, and when the handle does not resolve, say so as
  a MISSING outcome rather than scoring the person zero.
- **A zero from this lane is almost never EMPTY.** Non-resolution, the wrong account, and a genuinely
  quiet month are three different findings that all print `0`. Name which one you got.
- **`silver extract <url>` is not URL-grounded here — REPRODUCED TWICE 2026-09-08.** Asked for
  `https://x.com/bcherny` and for `https://borischerny.com`; **both** returned a snapshot headed
  `- title: "Workers & Pages Pricing | Cloudflare" [url=https://www.cloudflare.com/plans/developer-platform/]`
  — a stale tab in the persistent profile. It is also keyless, so it emits the extraction *prompt* plus that
  snapshot, never extracted JSON. **Use `silver read <url>`**, which was correctly grounded on both URLs.
- **Recruiting content is not testimony.** A lab's hiring post states what it wants applicants to *be*, so it
  reads as a track-record claim while being a demand signal. Rank ex-employees (`gh api users/<u> --jq .company`
  ≠ the org in question) and stated rejection reasons ABOVE anyone currently recruiting for the position.
- **Engagement over-selects announcements.** Measured live: the top of `silver read https://x.com/bcherny` is
  @claudeai product announcements at 261K views, not the practitioner's own reasoning. Direction of the bias
  replicated; magnitude did not (2.7x–7.8x). **Rank by nothing.** Pull outbound links, let one read decide.
- **Prominence ≠ track record on this question.** `bcherny` created Claude Code; his blog's 17 essays are all
  pre-2024 frontend/TypeScript and say nothing about agent harnesses. gh `followers` (10,914) predicted nothing.
- **Corroboration that isn't.** One practitioner supplied ~11 of 96 findings counted as three independent lanes
  (`~/Desktop/compound-v/references/corroboration.md:16`); one commercial orbit supplied
  ~18 of 59 (`:30`). A per-item check structurally cannot see this — only the chair over the pooled set can.
- **X read paths (2026-09-08):** `WebFetch https://x.com/<u>` → **HTTP 402 Payment Required** (verified).
  Anonymous `silver read https://x.com/<u>` → profile header **and timeline post text DO come back** (163 lines
  for bcherny) — this refines the older "403" note in memory; a *status* URL still walls. Never mint a token,
  never relaunch the user's browser.
- **Video/talks are SUBSTANCE, never QUOTATION** — a verified caption rendered "Claude Code" as "Cloud Code".
  Paraphrase with a video id; never quote a caption.

## Enumeration line
```
people-track-record | files listed 45 | candidates selected 26 | cut line row must name harness/agent/context work, then one voice per commercial orbit (26 -> 17; Anthropic 4 -> 1)
```
A zero selection still emits it, e.g. `people-track-record | files listed 45 | candidates selected 0 | cut line no roster row names this domain`
