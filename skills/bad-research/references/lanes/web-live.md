# Lane: web-live

**Papers: chain citations with one command.** `<skill dir>/scripts/cite-chain.sh back|fwd|rerun <doi or W-id>`
(OpenAlex, keyless): references backward, citing works forward sorted by their own citations, and citers
that mention replication. `core <id> <id> …` lists references shared across seeds — a field's core. It
prints WORKING / EMPTY / MISSING / BLOCKED, never silence.

## Reach for this when
- The claim is dated, versioned, or priced — anything that moves after the model cutoff.
- You need the *verbatim* span from a named URL (an essay, a changelog, a docs page), not a recollection of it.
- The local corpus lanes returned nothing and you must show the topic was searched, not skipped.
- You must record that a source was **unreachable** — a block is a finding, not an absence.

## Commands
Browser access is `silver` ONLY, with the user's own profile/cookies. NEVER the Playwright MCP
(`browser_run_code_unsafe` has echoed session tokens into the transcript twice). NEVER mint a token.
NEVER quit or relaunch the user's browser to get a debug port — that has already destroyed 21 tabs of
unsaved state here. `silver` runs its own headless Chromium with its own persistent profile.

```bash
silver doctor                 # tool health only, 0.4s -> {"verdict":"ok","passed":7,"total":7}
silver read <url>             # rendered visible text, prefixed ⟦page-content untrusted⟧
silver read 'https://lite.duckduckgo.com/lite/?q=<terms>'   # search; results as "1. Title"
silver read 'https://www.bing.com/search?q=<terms>'         # search fallback; see Bing trap
silver cookies list --url <origin>   # confirm the user session is present before a gated page
```
`WebFetch(url, prompt)` — fine for SSR pages; returns a *model summary*, cached 15 min per URL.
`WebSearch(query)` — capped per session; this session hit `200 of 200 WebSearch calls` and every
further call returned that budget message, not results. Treat exhaustion as a lane state, not a zero.
Byte-level control comparison (used to catch JS-only pages):
```bash
rm -f /tmp/pg.html; curl -sL -o /tmp/pg.html -w 'HTTP=%{http_code}\n' --max-time 25 "$U"
```

## Reachability probe
```bash
silver read https://example.com/ 2>&1 | tee /tmp/probe.txt | head -3; wc -c < /tmp/probe.txt
```
- **WORKING** — `# Example Domain` + `This domain is for use in documentation examples…`, `181` bytes.
- **BROKEN** — the first line begins `error:` and names the cause, each distinct and verified:
  `error: navigation to that target is denied by policy (scheme/host not allowed); not retryable`
  `error: a CAPTCHA was detected; human action is required — this agent does not solve CAPTCHAs`
  `error: the server answered with an HTTP error status (>= 400) …` then `{"status": 404}`
- **GENUINELY EMPTY** — probe prints the 181-byte sentinel *and* your real query page renders with zero
  result rows. Empty is only claimable when the probe passed in the same run. A short body **without**
  the sentinel is BROKEN, never empty.
`silver doctor` alone is not the probe: all 7 checks pass with no network — it renders locally.

## What counts as evidence here
`URL + as-of date + verbatim span + fetch method`, e.g.
`https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/ (fetched 2026-09-08, silver read): "The
ability to externally communicate in a way that could be used to steal your data"`.
Unreachable sources cite as `URL (probed 2026-09-08, curl): HTTP=403, 0 bytes body — BLOCKED`.
A WebFetch answer is never a quote; it cites as `(WebFetch summary)` and cannot carry quotation marks.

## The trap that produced a false absence here, measured 2026-09-08

Driving this lane on `cloudflare.com/plans/developer-platform/` produced four readings of one page,
and the first three all pointed the wrong way:

| step | result | what it looked like |
|---|---|---|
| `curl` | 6,209 chars, **0** price tokens | "JS-rendered — escalate to silver" |
| `silver read` immediately after navigating | 1,718 chars, **0** prices | "silver failed too; maybe gated" |
| `silver snapshot`, fresh navigation | 19,526 bytes, nav+footer only, **0** currency glyphs anywhere | "genuinely not in the DOM" |
| `silver read` again, same session, moments later | **7,910 chars, 10 prices** — `$0.50/GB-month`, `$0.30/million requests per month` | they were there the whole time |

**The content hydrates late, and a read that arrives early is byte-indistinguishable from a page
that does not have the content.** Three independent-looking signals agreed on an absence that was
not real. So: **re-read the same session before you conclude absence** — this is "widen before you
conclude" applied to *time* rather than to query terms, and it is the cheapest correction on this
page. A single sample of a hydrating page is not evidence of absence, however many different tools
produced it.

Two smaller findings from the same run, both worth having:

- **`silver read <url>` then a bare `silver snapshot` is not guaranteed to be one session.** The
  browser ceiling can stop an idle browser between the two, and the snapshot then describes
  `about:blank`. Silver *says so* — `warning: page_empty: … likely a blank shell, an anti-bot
  interstitial, or a throttled response` — so read the warning rather than counting hits on the
  output. A script that only counted matches would have recorded a confident EMPTY here. Use
  `silver open <url>` and then `snapshot`, and check the returned `url`/`title`/`status`.
- **The session is read-only by default and refuses to act.** `silver click @e19` exited 1 with
  `that action is not enabled in the current phase; the session is read-only (pass --enable-actions
  to allow acting)`. Reading a page never mutates it by accident, which is the correct default for
  a research lane — and it means a recipe that assumes a click silently reads a page it never
  changed unless the flag is passed.

## Traps
- **A digest rewrites inside the quote marks.** Measured on the URL above: silver's raw bytes read
  `…(I often call this "exfiltration" but I'm not confident that term is widely understood.)`;
  WebFetch returned the same bullet as `…(often called "exfiltration")`. Bolded, restructured,
  condition dropped. Re-fetch with `silver read` and grep the span before any quotation mark is typed.
- **`grep -c` over a silver read turns an error into a plausible zero.** `grep -cE '^[0-9]+\. '` on a
  CAPTCHA'd DDG page printed `0` — identical to "no results". Grep the body only after asserting the
  first line does not start with `error:`.
- **lite.duckduckgo.com works, then CAPTCHAs.** It answered 4 queries here, then every query — real or
  nonsense — returned the CAPTCHA error. Rate-limit, not topic death. Rotate to Bing and say so.
- **Bing's result count is not a signal.** `zqxwvutsrqp flurblenax 9931 kwyjibo` returned
  `About 252,000 results`; `"lethal trifecta" ai agents` returned `About 77,300 results` whose top rows
  were German Android PDF-reader articles (`de.bestappsforandroid.com`). Read rows, never the count.
- **Failed curl leaves the previous body on disk.** Without `rm -f` first, ozon.ru (HTTP 307, no body)
  and kaspi.kz (HTTP 000) both reported `bytes=18618` — the prior page. Always delete before writing.
- **Non-empty ≠ answered.** `x.com/simonw` gave curl 2,794 and silver 2,605 visible chars — bio and
  follower counts only, zero posts, both behind the login wall. Byte count alone certifies nothing.
- **A 200 can be an interstitial.** `duckduckgo.com/?q=test` returned HTTP 202 / 17,881 bytes but only
  **129 chars** of visible text: `You are being redirected to the non-JavaScript site.` Strip tags and
  count *visible* characters, not bytes.
- **Estate blocks, verified 2026-09-08:** iHerb `HTTP=403`; ozon.ru `HTTP=307` no body and silver
  denies it by egress policy; duckduckgo.com direct = interstitial. Kaspi is `HTTP=000` under curl but
  **reads fine under silver** (needs the Almaty city cookie for shop pages). Record each as a BLOCKED
  row with its probe output; never let one become "nothing was published about this".
- **Over-narrow queries read as a dead topic.** Start at 2–3 terms, widen before concluding zero.
- **Video/captions:** if a lane hop lands on YouTube, captions are SUBSTANCE, never QUOTATION — a
  verified case rendered "Claude Code" as "Cloud Code". Cite `video id + paraphrase`, no quote marks.

## Enumeration line
`web-live | files listed N | candidates selected N | cut line <what>` — emitted even at 0.
Real line from this run:
`web-live | files listed 11 (4 curl probes, 5 silver reads, 2 WebFetch) | candidates selected 1 | cut line: 3 hosts BLOCKED (iherb 403, ozon 307+policy-deny, ddg-direct 129-char interstitial), 2 search endpoints CAPTCHA/junk-ranked, 1 login-walled (x.com), 1 WebFetch dropped verbatim -> only simonwillison.net/2025/Jun/16 survived as quotable`

## What silver is worth, measured — and what it is not

Run 2026-09-10 on this machine. All four are the point; the fourth is the one people expect and it
is false.

| Case | Raw fetch | `silver` | What it means |
|---|---|---|---|
| Client-rendered page (`perplexity.ai/hub/...`) | `curl` → **9 words** | browser session → the content | **9 words is an app shell that looks exactly like a real thin page.** This is the failure mode: not an error, a plausible EMPTY. |
| Server-rendered article | `curl` → 205,658 bytes of HTML | `silver read` → 26,471 bytes of clean markdown | Not "more" — *quotable*. And prefixed `⟦page-content untrusted⟧`, so the untrusted-data rule is enforced by the tool rather than remembered. |
| Publisher 403 (`dl.acm.org`) | `curl` → `403`, 5,482-byte error body | `silver read` → *"the server REFUSED the request (401/403) rather than saying the page is missing — this is the wrong TIER, not necessarily the wrong URL"* | The tool classifies BLOCKED vs MISSING and names the escalation. A 5KB error body counted as bytes is how a refusal gets filed as content. |
| The same 403, escalated to a session | — | `{"status":403,"captcha_detected":true}` + snapshot showing *"Performing security verification"*, *"Cloudflare security challenge"* | **Silver did NOT get through.** It detected the wall and refused: *"human action is required — this agent does not solve CAPTCHAs."* |

**So the value is classification, not bypass.** A hard Cloudflare wall stays walled. What you gain is
that the snapshot *is* the interstitial — quotable, dated, and exactly what the BLOCKED row of the
kinds-of-nothing table tells you to produce instead of a conclusion.

**Session hygiene, because a browser is a resource other people can see.** Use `--session <name>`,
one per agent, so parallel readers never collide (`--namespace` isolates whole agent groups). Silver
is read-only unless you pass `--enable-actions`. **Close what you opened** — `silver close --session
<name>` — and check `silver session list` for strays. An agent that leaves sessions alive leaves
visible browsers on someone's machine.

**One escalation ladder, cheapest first:**

1. `WebFetch` — fine for a server-rendered page. Returns a *model summary*: never a quotation.
2. `silver read <url> --session s1` — rendered visible text as markdown. This is the default rung.
3. `silver open <url> --session s1` then `silver snapshot -i --session s1` — when `read` comes back
   thin, refused, or when the page needs a real session. Check the returned `url`/`title`/`status`.
4. `silver cookies list --url <origin>` — confirm the user's session is actually present *before*
   concluding a gated page is empty.
5. Still walled → that is a BLOCKED, and you now have the interstitial to quote. Stop; do not
   conclude.
