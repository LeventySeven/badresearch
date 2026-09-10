# Lane: local-corpus

Owner-only libraries on disk. No web agent can reach these.

## Reach for this when
- You want what a company/product actually *built*, not what it announced (`teardowns/`, 407 files).
- The question is about agent/eval/harness design — this corpus beats the live web on it.
- A live-web lane returned a digest, a paraphrase, or a 402/403 and you need verbatim primary text.
- Before any X/Twitter or WebSearch call: check `x-guides/` — same material, on disk, free.

## Commands
```sh
R=~/Desktop; T=$R/researchfms/Transcripts/TRANSCRIPTS_AI_AGENT_SYSTEMS.md
# 1. Teardowns — FLAT GLOB ONLY (see Traps). Returns matching breakdown filenames.
grep -l "retrieval" $R/researchfms/teardowns/*.md      # -> 182 files
grep -n "<term>" $R/researchfms/teardowns/ABRIDGE.md   # -> path:line for citation
# 2. Transcripts — heading index FIRST, never cat (68,481 lines in that one file).
grep -nE '^#{1,2} ' $T                                 # -> 296 index lines
awk 'NR>6884 && /^## /{print NR": "$0; exit}' $T       # -> 7138 = end of your section
sed -n '6884,6960p' $T                                 # read <=1500 lines at a time
# 3. Articles — slugs NOT guessable; route via manifest, then open the .md.
grep -i "multi-agent" $R/guidesfm/research/articles/_manifest.json   # -> don-t-build-multi-agents
python3 -c "import json;[print(e['slug'],'|',e['title'],'|',e['author']) for e in json.load(open('$R/guidesfm/research/articles/_manifest.json')) if 'agent' in e['title'].lower()]"
# 4. X-guides — grep the DIRECTORY, not the manifest (it indexes 28 of 67).
grep -ril "subagent" $R/guidesfm/research/x-guides/*.md
# 5. Operating specs, already grounded — read before re-deriving retrieval rules
ls $R/researchfms/*.md   # AGENTIC_SEARCH_SPEC.md, TRANSCRIPT_RULES.md, INDEX_AND_PARTITION_DECISIONS.md
```

**Worked example — answerable only here.** "What did ZS Associates conclude about multi-agent
research pipelines?" `grep -rln "ZS Associates" $R/researchfms/Transcripts $R/guidesfm/research`
-> `TRANSCRIPTS_AI_AGENT_SYSTEMS.md:6884`. They killed a four-specialists-plus-orchestrator pipeline
whose output was "locally correct, globally incoherent" (`:6949`) — every agent derived a correct
fact, none owned the end-to-end picture (`:6947`) — and rebuilt it as a deterministic statistical
pre-stage plus one context-owning agent (`:6886`, `:6998`). Cause: context lost at each handoff.

## Reachability probe
```sh
R=~/Desktop
echo "teardowns   $(find $R/researchfms/teardowns -maxdepth 1 -name '*.md' | wc -l)"
echo "transcripts $(find $R/researchfms/Transcripts -maxdepth 1 -name '*TRANSCRIPT*.md' | wc -l)"   # *TRANSCRIPT* not TRANSCRIPTS_* — see the trap below
echo "articles    $(find $R/guidesfm/research/articles -maxdepth 1 -name '*.md' | wc -l)"
echo "x-guides    $(find $R/guidesfm/research/x-guides -maxdepth 1 -name '*.md' | wc -l)"
```
- **WORKING** — four non-zero counts, e.g. `teardowns 407 / transcripts 41 / articles 190 / x-guides 67`
  (real output, 2026-09-08). Counts drift up most days; that is health, not error.
- **BROKEN** — a row prints `0` *and* stderr names the path:
  `bfs: error: ~/Desktop/NOPE: No such file or directory.` Root moved/unmounted.
  Report the lane as DOWN, never as "no sources found".
- **GENUINELY EMPTY** — all four rows non-zero, and your topic grep returns `0`
  (verified: `grep -l "quantum tunnelling" teardowns/*.md` -> `0` against a healthy 407). Only this
  state licenses "the corpus does not cover it".

## What counts as evidence here
`absolute/path.md:LINE` from `grep -n` or `sed -n`, plus the quoted sentence. Nothing else.
- Transcript sections carry a `**Source:**` line with a YouTube id — cite the id (`u6jJcIFDLE4`) as
  provenance, but the quote is to the transcript `path:line`.
- Articles: cite the `.md` path:line, and take `url` + `author` from `_manifest.json` for attribution.
- A manifest entry is a ROUTE, never a citation. Never quote `_manifest.json` or a `GUIDES_*.md` map.

## Traps
- **`TRANSCRIPTS_*.md` is a PREFIX glob and the directory does not only use that prefix.** Measured
  2026-09-09: it matches 41 files and silently drops `ICML_TRANSCRIPTS.md` — 23,000 lines, 761
  `**Authors:**` rows, ~3,074 distinct researcher names, i.e. **more names than the other 41 files
  hold combined**. It also drops `ICML_2026_NEXT_SESSION.md`. Use `*TRANSCRIPT*.md`. A glob that
  returns a plausible number is the worst kind of wrong: 41 looked right, matched the count written in
  the corpus map, and was missing the largest source in the lane. Anchor on the distinctive substring,
  not on the prefix somebody happened to use first.
- **`-r` in `teardowns/` is forbidden.** The folder holds 36,870 files, only 407 of which are the
  flat breakdowns. Measured: `grep -l "retrieval" *.md` -> 182 breakdowns; `grep -rl "retrieval" .`
  -> 368, of which **135 are vendored source** (`x-algorithm/phoenix/run_retrieval.py`,
  `home-mixer/*.rs`). `--include='*.md'` does NOT fix it — 23 hits still come from `_scratch/`,
  `_archive/`, `*_parts/`. Use the flat glob; use `-maxdepth 1` if you need `find`.
- **Article slugs are unguessable, sometimes truncated mid-word** — Sean Goedecke's is
  `if-you-are-good-at-code-review-you-will-be-good-at-using-ai-` (trailing dash). A guessed
  `building-multi-agent-research-system.md` -> `No such file or directory`. Always route via manifest.
- **`_completeness_manifest.json` indexes 28 of 67 x-guides.** All five top "subagent" hits
  (`addy-osmani-loop-engineering`, `boris-cherny-how-i-use-claude-code`, …) are absent from it.
  Manifest-only routing silently loses ~58% of the lane.
- **Never `cat` a transcript.** H1–H2 gives 296 index lines; H1–H3 on the same file gives 5,324 and
  blows the window. Index at `^#{1,2} `, then `sed -n` ranges of <=1500 lines.
- **Transcripts are auto-captions: SUBSTANCE, never QUOTATION.** The corpus flags this itself —
  `TRANSCRIPTS_AI_AGENT_SYSTEMS.md:6889` records that "Cloud Code" throughout is Claude Code and a
  speaker's name renders as "Sufiyan" for "Subbiah". 37 of 41 transcripts carry `auto-caption` notes.
  Paraphrase caption content and cite the line; never present it as a verbatim quote.
- **Never build an index/embeddings/findings-cache here.** A production findings-cache measured 0
  hits in 133 attempts, and both roots grow most days. `grep -n` is correct retrieval at this size.
- **Never quote a stored count, including the ones above.** The corpus map says x-guides is "~100";
  live enumeration says 67. Re-run the probe every session.
- **zsh does not word-split unquoted vars.** A `for p in "a b c"; set -- $p` loop silently emitted
  four blank rows here. Write lane loops as explicit lines.

## Enumeration line
`local-corpus | files listed N | candidates selected N | cut line <what>` — real, from the ZS run:
`local-corpus | files listed 41 | candidates selected 1 | cut line grep "ZS Associates" across Transcripts+guidesfm; only TRANSCRIPTS_AI_AGENT_SYSTEMS.md matched (teardowns/*.md flat grep: 0)`
A zero-selection run still emits it:
`local-corpus | files listed 407 | candidates selected 0 | cut line probe healthy (407 files), topic grep returned 0 — genuinely absent, not unreachable`
