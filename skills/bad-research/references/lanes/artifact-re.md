# Lane: artifact-re

## Reach for this when
- The question is "how does <product> actually work" and the answer must be reimplementable, not summarized.
- A vendor blog / docs page states a behavior and you need the constant, schema, or code path behind it.
- You need a claim about a dependency's real behavior at a pinned version (defaults moved, an option is a no-op).
- Anything the owner would file as a teardown. Blogs are step 6 of 6 here, never step 1.

## Commands
Order is mandatory (`~/.claude/skills/re-source-first/SKILL.md`): package → clone → bundle → probe → infra → blogs.

**1. Package, zero-execution path** (fetch+extract never runs vendor code):
```bash
npm view left-pad dist.tarball version     # -> https://registry.npmjs.org/left-pad/-/left-pad-1.3.0.tgz ; 1.3.0
T=$(npm view chalk@5.3.0 dist.tarball); curl -sSL "$T" -o p.tgz; tar -xzf p.tgz   # -> package/{package.json,source,readme.md,license}
npm pack left-pad --pack-destination .     # same tarball, prints "npm notice total files: 10"
# (npm pack on a LOCAL dir runs prepack/prepare; on a registry spec it only fetches — unverified here, prefer the curl line)
python3 -m pip download six -d ./py --no-deps --only-binary=:all:   # -> Saved ./py/six-1.17.0-py2.py3-none-any.whl
unzip -o -q ./py/*.whl -d ./py-unpacked     # -> six.py + six-1.17.0.dist-info/{METADATA,RECORD,WHEEL}
```
Then read, and cite lines: `grep -n "function leftPad" left-pad/index.js` → `22:function leftPad (str, len, ch) {`

**2. Sparse clone** (4.0s, 2.4M .git for a 376MB repo):
```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/vercel/ai.git ai-sparse
cd ai-sparse && git sparse-checkout set packages/ai/src/generate-text   # -> 89 .ts (56 non-test)
grep -rn "maxOutputTokens" packages/ai/src/generate-text/*.ts | head
# -> packages/ai/src/generate-text/generate-text.ts:675:    maxOutputTokens: callSettings.maxOutputTokens,
gh api repos/vercel/ai --jq '{full_name,default_branch,pushed_at,size}'   # pin what you cloned
gh api repos/vercel/ai/releases --jq '.[0].tag_name'                      # -> @ai-sdk/openai@4.0.60
```

**3. Production bundle**:
```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
curl -sSLA "$UA" https://linear.app/ -o page.html -w "http=%{http_code} bytes=%{size_download}\n"  # http=200 bytes=1267263
grep -oE 'src="[^"]+\.js[^"]*"' page.html | sed 's/src="//;s/"//' | sort -u        # 4 chunks
grep -ohE 'https://static\.linear\.app/[^"]+\.js' chunks/*.js page.html | sort -u  # 488 chunks (the real graph)
npx --yes js-beautify chunks/index-C2XfvN2U.js -o chunks/index.pretty.js   # 2 lines -> 10298 lines
```
If the page is JS-rendered and curl returns a shell, use `silver` with the user's own cookies. Never Playwright MCP, never mint a token, never quit the user's browser.

**4. Malformed-POST schema mining** (only for gaps source could not cover):
```bash
curl -sS -X POST https://api.linear.app/graphql -H 'content-type: application/json' -d '{"bad":"field"}' -i
# HTTP/2 400 ... {"errors":[{"message":"GraphQL operations must contain a non-empty `query` or a `persistedQuery` extension.",
#   "extensions":{"http":{"status":400},"code":"INVALID_INPUT","type":"invalid input","userError":true}}]}
```
The reveal is *persisted queries are supported and the error taxonomy is `code`+`type`+`userError`* — not "the endpoint exists".

## Reachability probe
```bash
npm view <pkg> dist.tarball version
```
- **WORKING** → `dist.tarball = 'https://registry.npmjs.org/left-pad/-/left-pad-1.3.0.tgz'` + `version = '1.3.0'`.
- **GENUINELY EMPTY** → `npm error code E404` / `404 Not Found - GET https://registry.npmjs.org/<pkg> - Not found`. The registry answered; that name has no package. Exit code is still 0 through a pipe — read the text, not `$?`.
- **BROKEN** → `npm error code ENOTFOUND` / `ECONNREFUSED` / `ETIMEDOUT`, `npm error syscall getaddrinfo`, `network request to ... failed`. No registry answer at all.
For the clone half, `gh api repos/<o>/<r> --jq .pushed_at`: a JSON date is WORKING, `HTTP 404` is EMPTY, `Bad credentials`/`could not resolve host` is BROKEN.

## What counts as evidence here
- **Package/clone:** `path:line` inside the fetched artifact, plus the exact version or commit it came from (`left-pad/index.js:22` @ 1.3.0; `packages/ai/src/generate-text/generate-text.ts:675` @ pushed_at 2026-09-07).
- **Bundle:** `chunks/<file>.pretty.js:<line>` plus the chunk's hashed filename (the hash IS the version) and the as-of date — chunk names rotate on every deploy.
- **Probe:** the full request line + response status + verbatim body, with a UTC timestamp. A probe with no body pasted is not evidence.
- Never cite a blog for a mechanism a file can show. If only the blog has it, mark it INFERRED.

## Traps
- **Order inversion.** Starting at curl/OpenAPI/DNS produces a 40k-line endpoint catalogue, not a teardown — this is the documented NIA failure (43,627 lines, <10% load-bearing). If a section's claim is "this endpoint exists", it is Tier-2 fingerprinting; cut it.
- **Tier-3 garbage is banned from the body** (`re-quality-gate`): funding rounds, investor lists, customer logos, employee counts, competitive-landscape tables, award lists, CSS palettes, TechCrunch prose. None of it answers "what hidden logic lies behind this surface".
- **Name-squat / version identity.** Verify *before* reading: `npm view composio --json` → single version `1.0.0`, published `2023-03-06`, maintainer `flashcodex`, description "UI Components for the web", 2 files / 352 bytes unpacked. That is a squat, not the vendor. The vendor ships `composio-core` (0.5.39) and `@composio/core` (0.18.1); `@composio/cli` is E404. Always check version list, publish date, maintainer, and unpacked size first.
- **Third-party code execution.** `npm install`, and `pip download` on an sdist, run vendor-authored install/build scripts as you. The commands above avoid that (`npm view`+`curl`+`tar`, `npm pack`, `--only-binary=:all:`); if you must install, use `npm install --ignore-scripts` and do it in a container/VM, in a throwaway dir, with no credentials in env. This lane needs a sandbox — say so rather than assuming one.
- **The page's `src=` tags are not the bundle.** Linear's HTML lists 4 chunks; the chunk graph inside those 4 lists 488. Grepping only the page-level chunks silently misses ~99% of the code.
- **Minified bundles are one line.** `grep -n` on an unbeautified chunk returns "line 1" and dumps 285KB. Beautify first, then cite.
- **Video/captions**: if a step reaches a conference talk, captions are SUBSTANCE ONLY, never quotation — a verified case rendered "Claude Code" as "Cloud Code". Cite as video id + timestamp + paraphrase.

## Enumeration line
`artifact-re | files listed N | candidates selected N | cut line <what>`

Real, from the runs above:
```
artifact-re | files listed 488 | candidates selected 4 | cut line non-entry chunks (vendor/UI-component chunks; kept the 4 the document loads)
artifact-re | files listed 89 | candidates selected 56 | cut line *.test.ts and __snapshots__ (behavior lives in the impl files)
artifact-re | files listed 1 | candidates selected 0 | cut line composio@1.0.0 is a 2023 name-squat, not the vendor's CLI — wrong artifact, nothing read
```
A lane selecting 0 still emits the line.
