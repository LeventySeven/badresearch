# Lane: terms-and-pricing

## Reach for this when
- The answer is a **clause**: an AUP/ToS restriction, a data-residency or NDA-binary constraint, a "you must buy X to do Y" gate.
- The answer is a **rate**: egress $/GB, per-plan €/mo, token pricing, a provider-restriction map.
- Someone is about to restate a vendor blog or a comparison table as if it were measured.
- A number already in a doc needs re-checking — terms move, and the URL does not.

## Commands
```bash
# 1. Reachability + shape (see probe below). Run this first, always.
/tmp/tp.sh "https://vercel.com/docs/pricing"     # code=200 chars=19447 money=40 datemarks=1

# 2. Plain fetch when the probe says the body is there. Strip tags, keep lines.
curl -sL --compressed -m 30 -A "Mozilla/5.0" URL -o /tmp/p.html
python3 -c 'import re,sys;h=open("/tmp/p.html",encoding="utf-8",errors="ignore").read();h=re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>"," ",h);print("\n".join(l.strip() for l in re.sub(r"(?s)<[^>]+>","\n",h).split("\n") if l.strip()))' > /tmp/p.txt
# anthropic.com/legal/aup -> 18907 chars incl. "Effective / September 15, 2025 / Previous Version"
# vercel.com/docs/pricing -> $0.05 $0.0812 $0.40 $0.64 ... + "Last updated September 3, 2026"

# 3. silver when the probe says money=0 on a pricing page (JS-rendered). NEVER Playwright MCP.
silver open "https://www.cloudflare.com/plans/developer-platform/"; silver read
# curl: 6209 chars, 0 price tokens.  silver: 7996 chars, 10 real figures ($0.50 $5 $0.30 $0.02 ...)
silver open "https://www.cloudflare.com/service-specific-terms-application-services/"; silver read
# curl: 381 lines of nav, clause ABSENT. silver: 23073 chars incl. the full CDN-video clause.

# 4. silver read dropped the number? escalate to the a11y tree, not to memory.
silver snapshot | LC_ALL=C grep -n -A3 'starting from'
#   - StaticText "starting from"   /   - generic "€ 5 ."   /   - StaticText "99"  -> €5.99 max/mo
#   (hetzner.com/cloud/: `silver read` renders "starting from ___ max/mo." with NO digits)

# 5. As-of anchoring + edit history for any clause you will quote.
curl -s -m 60 "http://web.archive.org/cdx/search/cdx?url=anthropic.com/legal/aup&fl=timestamp,digest&collapse=digest" | wc -l   # 728
curl -s --compressed -m 60 "https://web.archive.org/web/20240221160247id_/https://www.anthropic.com/legal/aup" -o /tmp/old.html
# same URL: 2024 snapshot says "Effective September 15, 2023" (101 text lines);
#           2026-09-08 snapshot says "Effective September 15, 2025" (279 text lines).
```

## Reachability probe
```bash
cat > /tmp/tp.sh <<'EOF'
curl -sL --compressed -m 25 -A "Mozilla/5.0" -w '\n@@%{http_code}\n' "$1" | python3 -c '
import re,sys;raw=sys.stdin.read();m=re.search(r"@@(\d+)\s*$",raw);code=m.group(1) if m else "?"
h=re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>"," ",raw[:m.start()] if m else raw)
t=re.sub(r"\s+"," ",re.sub(r"(?s)<[^>]+>"," ",h)).strip()
print("code=%s chars=%d money=%d datemarks=%d"%(code,len(t),len(re.findall(r"[€$£]\s?\d",t)),len(re.findall(r"(?i)last updated|effective|version dated",t))))'
EOF
chmod +x /tmp/tp.sh
```
- **BROKEN** — `code=403 chars=16 money=0 datemarks=0` (iherb bot-wall), or `code=502 chars=0`. Rule: `code!=200` **or** `chars<500`. Stop; do not quote.
- **WORKING** — `code=200 chars=19447 money=40 datemarks=1` (vercel docs pricing): body present, anchors present. Quote from it.
- **NOT-YET-KNOWN (the trap case)** — `code=200 chars=6209 money=0 datemarks=0` (cloudflare plans). Body reached, anchor missing. This is **not** empty: silver got 10 prices off that same URL. Escalate to command 3.
- **GENUINELY EMPTY** — only after silver on the loaded page also returns 0 anchors and the page title matches the topic. e.g. `code=200 chars=18907 money=0 datemarks=1` on anthropic.com/legal/aup is correct: an AUP has clauses and an effective date, and legitimately no prices.

## What counts as evidence here
Four fields or it is not evidence: **verbatim clause (or figure)** + **section/heading label** + **URL** + **as-of date**.
- `"Unless you are an Enterprise customer, Cloudflare offers specific Paid Services (e.g., the Developer Platform, Images, and Stream) that you must use in order to serve video and other large files via the CDN." — heading "Content Delivery Network (Free, Pro, or Business)", https://www.cloudflare.com/service-specific-terms-application-services/, page's own "Last updated: June 02, 2026", read 2026-09-08.`
- As-of date = the page's OWN dateline when it has one ("Effective September 15, 2025", "Last updated: September 3, 2026"), plus the date you read it. Both.
- Where a doc has no numbers (Cloudflare's does not), cite the **heading**. Never invent `§2.8`.
- A rate cites the plan name too: `€5.99 max/mo, "Shared vCPU / Regular Performance", hetzner.com/cloud/, read 2026-09-08 (a11y snapshot; digits split "€ 5 ." + "99")`.

## The fifth field: what would flip this

A clause and a rate are the two things in a research answer with a **known expiry**. Every other
finding is wrong or right; these are right *until the vendor edits a page*, and the URL does not
change when they do. So a terms/pricing finding ships a fifth field beyond the four above — one line
naming what would overturn it and how a reader re-checks in under a minute:

```
flip-check: re-run the probe; if the page's own dateline is later than the as-of below, this row is stale.
  "Effective September 15, 2025" — Anthropic Usage Policy, anthropic.com/legal/aup, read 2026-09-08
  (18,907 chars / 279 text lines; a "Previous Version" link is present, so edits are dated and diffable)
```

Two reasons this is not ceremony. **It survives the answer.** The reader who acts on your number is
often reading months later, and a bare "as of 2026-09-08" tells them the finding is old without
telling them how to fix it. **And it forces you to look for the dateline**, which is the field agents
skip — a page with no dateline at all is a materially weaker citation, and writing this row is where
you find that out rather than discovering it after the number is load-bearing.

Where a page carries no dateline of its own, say so in the row and substitute the Wayback digest
count (command 5): "no vendor dateline; 728 distinct snapshots, latest digest read 2026-09-08."

Re-verified 2026-09-08 by re-running this lane against its own citations: the Anthropic AUP is
unchanged (same dateline, same 18,907 chars / 279 lines) and Vercel's pricing still reads "Last
updated September 3, 2026" with Image transformations at $0.05 / $0.0812. UNCHANGED, checked rather
than assumed — which is the only way that sentence is worth anything.

## Traps
- **JS-rendered tables.** Plain fetch returns marketing copy with zero numbers, and an empty fetch is byte-identical in shape to a fabricated quote. Measured here: cloudflare plans curl=6209 chars/0 prices vs silver=7996/10 prices; cf terms curl=nav-only vs silver=23073 chars with the clause. (Prior measured case: curl 15 chars vs silver 9,921 on one URL.)
- **`silver read` drops nested price nodes.** hetzner.com/cloud/ renders "starting from ___ max/mo." because the integer sits in a `generic` and the decimals in a child `StaticText`; the markdown flattener loses them. `silver snapshot` recovers `€ 5 .` + `99`. A blank where a price belongs is a *retrieval failure*, never a free plan.
- **WebFetch trims the condition off a clause.** Asked for the CDN-video clause verbatim, WebFetch returned it starting at "Cloudflare offers specific Paid Services…" and silently dropped the preceding **"Unless you are an Enterprise customer,"** — the exact qualifier that decides whether the clause binds you. Use WebFetch to locate, silver/curl text to quote.
- **In-place edits at a stable URL.** anthropic.com/legal/aup served "Effective September 15, 2023" in 2024 and "Effective September 15, 2025" today, same URL, plus a "Previous Version" link. A clause claim with no as-of date is unsound by construction.
- **Digest churn ≠ clause change.** That URL has 748 Wayback captures and 728 distinct adjacent digests — build hashes and nonces move every capture. Diff extracted TEXT between two snapshots; never conclude "changed" from digests.
- **Wayback `id_` replays the raw gzip.** Without `--compressed` you get binary; the tag-stripper then yields plausible-looking noise and greps return nothing. Always `--compressed` on `id_` URLs.
- **CDX truncates silently.** One run of the same collapse query returned 14 rows ending March 2025; the retry returned 728 ending today. Re-run and compare the row count before trusting a version history.
- **Promotional and legacy rates.** Vendor pricing pages carry parallel "Legacy Metrics" / introductory tiers whose expiry is not printed beside the number. Capture the tier label with the figure, or the figure is unquotable.
- **Interested sources.** A vendor blog, its docs, and its comparison page are one actor. Count distinct **actors**, not distinct URLs, before writing "widely reported".
- **WebSearch budget dies quietly.** This session hit 200/200; the tool returned a prose notice, not an error — indistinguishable from "no results" if you skim. Check for the budget sentence before recording a null.
- **No video in this lane.** If a rate ever comes from a talk or demo, captions are substance, never quotation (a verified case rendered "Claude Code" as "Cloud Code").

## Enumeration line
`terms-and-pricing | files listed 7 | candidates selected 5 | cut line HTTP!=200 or chars<500 (cut: iherb 403/16 chars, httpstat 502/0 chars)`
A run that selects nothing still emits it, e.g. `terms-and-pricing | files listed 3 | candidates selected 0 | cut line probe money=0 and silver also 0 — page has no rate card`.
