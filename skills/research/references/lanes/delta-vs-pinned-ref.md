# Lane: delta-vs-pinned-ref

## Reach for this when
- The question is "what changed since X" — a prior teardown round (COMPOSIO R4→R5, TAVILY R2→R3, NIA_R4), a pinned version, or a dated page snapshot.
- A claim in an existing doc was true at some ref and you must confirm it still holds.
- You need to date a behaviour: which version introduced it, and when it shipped.
- A vendor announced something and you need the shipped diff, not the announcement.

## Commands
All run 2026-09-08 against `ComposioHQ/composio` / `@composio/core`.

**0. Identity first — never diff two things you have not proven are the same artifact.**
```
npm view composio repository description        # -> description='UI Components for the web', NO repository field = squat
npm view @composio/core repository description  # -> url: https://github.com/ComposioHQ/composio.git, directory: ts/packages/core
curl -s https://pypi.org/pypi/composio/json | python3 -c 'import json,sys;i=json.load(sys.stdin)["info"];print(i["name"],i["version"],i.get("home_page"))'
```
A package whose `repository` is absent and whose description does not match the vendor is a different artifact. Stop.

**1. Version timeline (what refs exist, and when).**
```
npm view @composio/core versions --json | tail -8     # -> ... "0.18.0","0.18.1","1.0.0-beta.0"
npm view @composio/core time --json | tail -12        # -> "0.18.1": "2026-09-04T19:06:35.074Z"
```

**2. Diff two published packages without a clone.**
```
npm pack @composio/core@0.18.0 --silent; npm pack @composio/core@0.18.1 --silent
mkdir -p a b && tar xzf composio-core-0.18.0.tgz -C a && tar xzf composio-core-0.18.1.tgz -C b
diff -u a/package/package.json b/package/package.json      # the highest-signal file: exports, deps, engines
```
Real hunk returned: `+ "./utils/ssrf-guard": { "workerd": {...}, "node": {...} }` — a new public export in 0.18.1.

**3. Diff two git refs without a clone (cheapest source diff).**
```
gh api repos/ComposioHQ/composio/compare/v0.7.0...v0.7.1 --jq '{status:.status,ahead:.ahead_by,files:(.files|length)}'
  -> {"ahead":9,"files":15,"status":"ahead"}
gh api repos/.../compare/v0.7.0...v0.7.1 --jq '.files[] | "\(.status)\t\(.additions)+/\(.deletions)-\t\(.filename)"'
gh api repos/.../compare/v0.7.0...v0.7.1 --jq '.files[] | select(.filename=="python/composio/client/__init__.py") | .patch'
  -> -    if auth_mode not in AUTH_SCHEMES:
     +    if auth_mode not in AUTH_SCHEME_WITH_INITIATE:
```

**4. Sparse blobless clone when you need repeated/pathspec diffs (15M .git, not 1.5G).**
```
git clone --filter=blob:none --no-checkout https://github.com/ComposioHQ/composio.git sparse
cd sparse && git sparse-checkout set --cone python/composio/client && git checkout main
git fetch --tags --quiet origin          # ALWAYS, before any comparison
git diff --stat v0.7.0 v0.7.1 -- python/composio/client
  -> __init__.py | 6 +++---   collections.py | 21 ++++++++++++-------   2 files changed, 17 insertions(+), 10 deletions(-)
```

**5. Page-snapshot delta.** Browser is `silver` only, user's cookies; never Playwright MCP, never relaunch their browser.
```
silver read https://docs.composio.dev/docs/welcome > snap-2026-09-08.md
diff -u snap-<old-date>.md snap-2026-09-08.md   # exit 0 = unchanged; two reads 8s apart were byte-identical (127 lines each)
```

## Reachability probe
```
git diff --quiet <REF_A> <REF_B> -- <path>; echo $?
```
- **WORKING, CHANGED** → `1`. There is a delta; go read it with `git diff <A> <B> -- <path>`.
- **WORKING, GENUINELY EMPTY (unchanged)** → `0`. This is a **reportable result**, not a failed run. Write "UNCHANGED between A and B as of <date>" and stop. Do not go searching for a change that is not there.
- **BROKEN** → `128` with `fatal: bad revision 'v99.9.9'` — a ref does not exist locally (stale clone, or wrong tag name). `git fetch --tags origin` and retry; if it still fails, the ref is wrong.

Network equivalents, same three-way: `gh api .../compare/A...B` → `"status":"identical","files":0` is EMPTY-unchanged; exit `1` + `{"message":"Not Found","status":"404"}` is BROKEN. `npm view <pkg> versions` → exit `1` + `npm error code E404` is BROKEN (or a wrong package name).

## What counts as evidence here
`<artifact-id> <REF_A> → <REF_B>, compared <YYYY-MM-DD>` + the diff hunk or `--stat` line, and for source, `path:line` at the newer ref.
Example: `@composio/core 0.18.0 → 0.18.1, compared 2026-09-08 — package.json gains export "./utils/ssrf-guard" (workerd/edge-light/node conditions)`.
An UNCHANGED result cites the same two refs plus the probe exit code. Refs must be immutable: a tag or sha or exact version, never `main`/`latest`/`HEAD`.

## Traps
- **Name-squat / wrong artifact.** `npm composio@1.0.0` is a 2023 squat ("UI Components for the web", one hello-world file); the vendor's CLI is `@composio/cli`, `"private": true`, 0 npm versions, shipped only as GitHub-Release binaries. Diffing it would have produced pure noise. Mechanism: npm names are first-come, unrelated to the repo. Always read `repository` + `description` before diffing. See `~/Desktop/researchfms/teardowns/COMPOSIO_R5_SDK_DELTA.md:46`.
- **A moved line number is not a change, and a changed file is not a changed behaviour.** Measured
  2026-09-08 on `yt-dlp` 2025.9.26 → 2026.8.19: `YoutubeDL.py` grew 4442 → 4556 lines across **28
  hunks**, so any file-level verdict says CHANGED. Extract the functions the question actually rests
  on and the answer inverts — `__list_table` and `to_screen` byte-identical, `render_subtitles_table`
  differing only by `strict=True` added to a `zip()`. The line carrying the behaviour is identical
  and sits at `:648` in one ref and `:667` in the other. So diff the SPAN, never the file, and pin
  every citation as `path:line @ version` — a bare `path:line` rots on the next release even when
  nothing it describes has moved.
- **Stale clone diffs against the wrong base silently.** A tag fetched last month still resolves; git does not warn that the remote moved or that the tag was re-pointed. `git fetch --tags origin` before every comparison, or use `gh api compare` which always reads the remote.
- **Version sort is not string sort.** `sorted(releases)` on PyPI put `2.0.0b0` last while `info.version` was `0.21.1`. Read `info.version` for latest; never take the last element of a lexicographic sort.
- **Three-way version split.** Dist version, in-code `__version__`, and `pyproject.toml` can disagree (composio dist 0.13.1 / `__version__` "1.0.0-rc2" / pyproject 0.14.0). Pin the one you actually diffed and say which.
- **`diff -rq` on `dist/` is all noise.** Bundlers content-hash filenames, so every chunk shows as "Only in a/" vs "Only in b/" (`CustomTool-BKhHv2hJ` vs `CustomTool-VRfWzMix`). Diff `package.json`, `CHANGELOG.md`, and named entry files — not the chunk directory.
- **Piping the probe eats the exit code.** `git diff --quiet A B | head; echo $?` printed `0` for a genuine 404. Never pipe a command whose `$?` you are reading.
- **Raw HTML page diffs are noise.** Build ids, CSRF nonces and timestamps change on every load. Use `silver read` (markdown) not `get html`, and keep the dated snapshot file as the baseline.
- **Video changelogs:** captions are SUBSTANCE, never QUOTATION (a verified case rendered "Claude Code" as "Cloud Code"). Cite a video delta as video-id + paraphrase, and confirm the change in the diff before it is a finding.

## Enumeration line
`delta-vs-pinned-ref | files listed 15 | candidates selected 12 | cut line dropped docs/*.mdx and mint.json — prose, no behaviour change`
(real run: `gh api repos/ComposioHQ/composio/compare/v0.7.0...v0.7.1`, 2026-09-08.)
A zero-selection run still emits it: `delta-vs-pinned-ref | files listed 0 | candidates selected 0 | cut line UNCHANGED between v0.7.1 and v0.7.1 (git diff --quiet exit 0) — reportable, not a miss`
