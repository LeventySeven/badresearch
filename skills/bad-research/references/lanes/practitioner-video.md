# Lane: practitioner-video

## Reach for this when
- The question is about *how a practitioner actually built or broke something* — harness design, eval practice, context engineering, what a team unshipped — and you want a named engineer at length, not a blog summary.
- A term is young enough that essays lag conference talks (measured: 32 core-tier titles on context/eval/harness, most from 2025-26 conference tracks).
- You need to know whether a topic is *discussed at all* by serious builders — a title dump is a cheap prevalence signal.
- Do NOT reach here for a quotable line. This lane cannot produce quotations (see Traps).

## Commands
All run from `~/Desktop/compound-v`. Registry: `references/channels.tsv` — 32 rows, verified 2026-09-08: core 9, platform 14, podcast 3, research 6.

```bash
bash scripts/yt.sh channels                       # print the 32-row registry with tier + what it's good for
bash scripts/yt.sh verify aiDotEngineer           # -> "@aiDotEngineer -> AI Engineer"  (handle-collision guard, ~9s)
bash scripts/yt.sh titles AndrejKarpathy 5        # newest N titles || url, from ONE channel (~1s)
bash scripts/yt.sh sweep "<ERE>" <limit> <TIER>   # THE MAIN CALL — dump titles from every channel in TIER, grep locally
bash scripts/yt.sh csearch <handle> "<q>" 20      # YouTube's in-channel matcher — under-collects, see Traps
bash scripts/yt.sh tracks <url>                   # which caption tracks exist
bash scripts/yt.sh transcript <url>               # ~3.2k words for a 15-min talk, with a PROVENANCE header
```

Real tier-scoped sweep (9 core channels, 1307 titles, **20.5s wall**):
```
$ bash scripts/yt.sh sweep "context (engineering|window|rot)|eval(s|uation)?|harness" 200 core
# sweeping /.../i over the newest 200 titles of each core-tier channel
AI Engineer || Codex, Behind the Harness — Dominik Kundel, OpenAI || https://www.youtube.com/watch?v=shRR1e2HXMk
AI Engineer || Your Agent Didn't Fail. Your Harness Did. — Vinoth Govindarajan, OpenAI || .../watch?v=BInpv7lGp1o
YC Root Access || Advanced Context Engineering for Agents || https://www.youtube.com/watch?v=IS_y40zY-hc
InfoQ || The Engineering of AI Agents: Context, Harnessing, and Autonomy || .../watch?v=_R83pFpUWyM
#   (0) Cursor
#   (0) Andrej Karpathy
# 32 titles matched.
```
Measured wall time per tier at the default limit 400: **core 31s · platform 69s · podcast 11s · research 29s** (~139s for all 32, sequential).

## Reachability probe
```bash
cd ~/Desktop/compound-v && bash scripts/yt.sh sweep "agent" 40 podcast; echo "EXIT=$?"
```
Three distinguishable outcomes (all three produced on 2026-09-08):

| | signal |
|---|---|
| **WORKING** | `EXIT=0`, matched `Channel \|\| Title \|\| url` rows, footer `# N titles matched.` with N>0, **no stderr banner**. |
| **GENUINELY EMPTY** | `EXIT=0`, only `#   (0) <Channel>` lines, footer `# 0 titles matched.`, **no stderr banner**. Verified with the nonsense regex `zzznotarealtoken` over the podcast tier: 3 `(0)` lines, exit 0, 3.9s. |
| **BROKEN** | `EXIT=3` plus `TOOL FAILURE, NOT AN EMPTY RESULT: yt-dlp failed on ALL 3 channels.` A *partial* break prints to stderr `# NOTE: N of M channels FAILED (not empty).` — those `(0)` lines are unmeasured. |

Probe cost ~11s. For a single video, the same three-way split appears on `transcript`:
- `FETCH_FAILED_BUT_TRACKS_EXIST` + `EXIT=2` → **THROTTLE, not absence.** Sleep 30-60s and retry. Never record as caption-free.
- `VIDEO_UNREADABLE` + `EXIT=2` → listing itself failed (deleted/private/gated). Verified on a bogus id.
- `NO_SUBTITLES_AVAILABLE` + `EXIT=1` → the only outcome that *can* be an absence, and the wrapper
  infers it the weak way: `--list-subs` exited 0 and matched no `^[a-z]{2}` row. A throttled listing
  that returns a caption-free player response exits 0 and matches none either, so that inference
  cannot separate them. **There is a positive signal available and it is not being used.** Read from
  the source, then confirmed live:
  - `yt_dlp/YoutubeDL.py:4076-4077` @ 2026.8.19 — when the table is empty the listing prints
    `<video id> has no <name>` and returns *without* a header. So a genuinely caption-free video
    says so in words; it does not fall silent. Grep for `has no subtitles` / `has no automatic
    captions` and you have EMPTY as an assertion instead of an inference.
  - `YoutubeDL.py:3054-3058` renders **two** sections — automatic captions (only when the key is
    present) then subtitles — each headed `[info] Available <name> for <id>:`. Measured on
    `1IdzkRVmWAA`: header for automatic captions at stdout line 5, and `1IdzkRVmWAA has no
    subtitles` at line 189. Auto-captioned, manually uncaptioned, fully readable.
  - **The trap: `--quiet` deletes the evidence.** `YoutubeDL.py:667` sets
    `screen = sys.stderr if quiet else stdout`, and `to_screen` returns early under quiet without
    verbose (`:1007`). Measured: a `--quiet --list-subs` run gave 183 stdout lines, 0 stderr lines
    and **zero** occurrences of `has no`. Run the listing WITHOUT `--quiet` or you have thrown away
    the only thing that could have told you the difference.
- **Even confirmed, it bounds the captions and not the talk.** "This video has no caption track" is
  not "this speaker's claim is unattested" — the talk still exists, and the claim may sit in a blog
  post, a repo, or a slide deck. Record the video as unreadable in THIS lane and put the question
  back on the frontier; do not let a caption gap become a finding of absence.
- **The section header is not the signal — the rows are.** `--list-subs` prints two sections, and
  auto-only videos print none of the manual one. Measured 2026-09-08 on `1IdzkRVmWAA`: exit 0, **160**
  track rows, 2 of them English (`en`, `en-orig`), **zero** occurrences of `Available subtitles`, one
  of `automatic captions`. Grepping for the manual header would file that readable talk as caption-free;
  the wrapper's row regex is section-blind on purpose and correctly routes it to `EXIT=2` instead.

## What counts as evidence here
**channel name + exact talk title + video id + PARAPHRASE.** Never a quoted string.
> Per *Advanced Context Engineering for Agents* (YC Root Access, `IS_y40zY-hc`), the speaker traces the term to a "12-factor agents" manifesto published before the June 2025 tweets that popularised it — paraphrased from YouTube captions, not quoted.

Title and video id are verifiable and stable; caption wording is not. A URL alone is not a citation here — a reader must be able to see which talk without loading it.

## Traps
- **CAPTIONS ARE SUBSTANCE, NEVER QUOTATION.** In the single transcript pulled above, the same product name appears three ways in one talk: `Claude Code`, `Cloud Code`, `cloud code`; and "12-factor" renders as `12actor`. YouTube's *manual* subtitle section is often ASR-derived, so provenance metadata cannot license a quote. To quote, confirm against audio or an independent text source and say you did.
- **`sweep` beats `mine`/`csearch` on recall — measured.** `csearch ycrootaccess "context engineering" 20` returned 7 rows, 4 of them off-topic (Greptile, Recall.ai, relational DBs), and **missed** *How to Give AI Agents Enough Context to Be Useful* (`1egwM88T3C0`). The local title dump found all 4 "context" titles. YouTube's matcher is fuzzy and TITLE-ONLY and silently under-collects; a talk never listed cannot be judged.
- **A no-tier sweep can truncate and look like an empty lane.** This happened: a 900s all-tier sweep returned rows from only the LAST 8 channels, with the entire core tier missing and **no error emitted**. The loop is sequential in registry file order, which interleaves tiers (row 1 core, row 3 platform...), so any cut drops a mid-file slice silently. **Fix: always pass the 4th arg.** Four scoped sweeps cost 139s total and each one is separately verifiable.
- **The regex matches substrings, and the false positives are invisible.** `eval` matched `Keras Recommenders ... ranking and **retrieval**`; `harness` matched `**Harness**ing Collective Agent Intelligence`. Read every matched title before selecting; do not pass a sweep's row count off as a topic count.
- **yt-dlp bot-walls under parallelism** — 43% failures measured at 8-way on 512 videos. Run transcripts sequentially with a pause between them. Those failures are throttling, not dead videos.
- **A handle is not a name.** `@Anthropic` is a Super Mario Maker channel (the lab is `@anthropic-ai`); `@claudeai` is dead, `@claude` is live. `yt.sh verify <handle>` before trusting any handle not already in the registry.
- **Tier is a prior, not a filter.** `@claude` and `@OpenAI` are marked platform because their feeds are marketing — but 13 and 15 corpus transcripts respectively came from them. Sweep them by name; do not browse them.

## Enumeration line
```
practitioner-video | files listed 1307 | candidates selected 28 | cut line: 4 of 32 regex matches dropped as substring false-positives ("retrieval"->eval, "Harnessing"->harness) or vendor console tutorials; 1 transcribed
```
A tier that selects nothing still emits a line — this is the real one from the `zzznotarealtoken` control:
```
practitioner-video | files listed 120 | candidates selected 0 | cut line: 0 titles matched across 3 podcast-tier channels; exit 0 and no TOOL FAILURE banner, so this is a genuine empty, not a broken lane
```
