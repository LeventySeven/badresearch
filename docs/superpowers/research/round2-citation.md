# Round 2 — Citation Grounding Design Fragment
## Line-anchored, support-checked, keyless citations — kills G1 / G4 / G5

**Scope:** P1 + P2 from SYNTHESIS.md. Targets G1 (gate false-positives from
formatting artifacts), G4 (citation-exists check but not citation-SUPPORTS check),
G5 (ungrounded draft → gate-block loop). All machinery runs inside Claude Code:
no new paid APIs, no hosted cross-encoders beyond what is already optional.

---

## 1. The current grounding chain (what we are changing)

The live machinery in order:

| Step | File | Current behaviour |
|------|------|------------------|
| 9 (evidence digest) | `bad-research-9-evidence-digest.md:45-60` | Emits `quoted_support` + `source_note_id` per claim — char offsets but NO line numbers |
| 11.4b (evidence injection) | `bad-research-11-synthesize.md:134-179` | Re-injects raw spans by `char_start`/`char_end`; synthesizer generates `[[note-id]]` / `[N]` tokens |
| 11.5 (CitationVerifier) | `grounding/verifier.py:271-376` | Tier A: byte-identity via SHA (`char_start:char_end`); Tier B: NLI no-op on keyless path (`CitationPresentNLI`); Tier C: host batched judge only for NLI-neutral band |
| 16 (gate) | `grounding/gate.py:136-163` | `no_uncited_claim_gate`: regex split + `is_factual_claim` + `extract_citations`; checks citation EXISTS and `anchor.verified == 1` |

**The three gaps:**
- **G1** (`gate.py:65-75`): `is_formatting_line` catches bold-only headings, table rows, code fences — but the `split_sentences` regex at line 96 (`re.split(r"(?<=[.!?])\s+", line)`) can still tokenize fragments from bold-span prose inside a sentence, triggering false critical findings on non-sentences.
- **G4** (`verifier.py:31-41`): On the fully-keyless path, `CitationPresentNLI.predict` always returns `{"entailment": 1.0}` — a paraphrased claim that drifts from its quoted span is marked SUPPORTED. The gate then passes `anchor.verified == 1` even though the span doesn't support the claim.
- **G5**: Because grounding is checked POST-synthesis at step 11.5, a draft written without anchors (all citations dangling) hits the gate as a wall of critical findings, forcing a full regrounding loop. The fix is grounding BEFORE the synthesizer writes, not after.

---

## 2. Design: four-layer upgrade

### Layer 1 — Source-side: stable line anchors at fetch time

**Goal:** every stored note body has stable 1-based line numbers. A cited span
becomes `note:L42-L58`, not just `char_start=1247`.

**Mechanism (pure Python, no new dependency):**

Add `body_to_lines(body: str) -> list[tuple[int, int]]` to
`src/bad_research/grounding/extract.py`. It returns a list of `(char_start,
char_end)` for each line (0-indexed line → char span). Computed once at
write-note time, stored in a new SQLite column.

**Schema addition** (`src/bad_research/core/db.py` — one migration, SCHEMA_VERSION bump):
```sql
ALTER TABLE note_content ADD COLUMN body_lines TEXT;  -- JSON: [[char_start, char_end], ...]
```
Populated by `note.py:write_note` (two lines: compute + store). Existing notes
get it on next auto-sync (populate lazily on first read of a note that lacks it).

**New helper** in `grounding/extract.py`:
```python
def char_span_to_line_range(body_lines, char_start, char_end) -> tuple[int, int]:
    """Given char offsets, return 1-based (line_start, line_end). O(n) scan."""
```

**New MCP tool** in `mcp/server.py` (analogous to OpenAI `web.find` — the
`note find` regex span extractor):
```python
@server.tool()
def note_find(note_id: str, pattern: str, context_lines: int = 3) -> str:
    """Regex grep within a stored note body. Returns matching line ranges
    (line_start, line_end, matched_text, char_start, char_end). Cheap —
    no LLM. Analogous to OpenAI web.find."""
```

This lets a synthesizer or verifier agent say: `note_find("source-note-12",
"12.4%")` and receive `{"line_start": 42, "line_end": 44, "text": "...12.4%..."}`.

**Citation token format** — the canonical anchor becomes:
```
[[note-id:L42-L58]]
```
This is a backward-compatible extension of the existing `[[wikilink]]` grammar.
`render.py:extract_citations` already parses `[[([^\]|]+)(?:\|[^\]]*)?]]` — the
new token is just a note-id with a colon-suffix. A one-line regex extension
extracts the `note_id` and `(L42, L58)` from the same group.

The `claim_anchors` table gains two integer columns (`line_start`, `line_end`)
and the `anchor_id` computation remains `quote_sha(quoted_support)` — unchanged,
so the byte-identity Tier A is untouched.

**No change to `anchors.py:ClaimAnchor`** struct beyond adding the two nullable
fields. `build_from_claims` populates them by calling
`char_span_to_line_range` after `extract_spans` returns.

---

### Layer 2 — Synthesis-side: line-anchored citation emission

**Goal:** the synthesizer emits `[[note-id:L42-L58]]` tokens, not bare
`[[note-id]]`, so every citation carries its line range at write time.

**Change in `bad-research-11-synthesize.md` step 11.4b** (the synthesis-evidence
injection block, lines 134-179): the `bad retrieve` output already returns
`char_start` / `char_end` per chunk. The orchestrator converts these to
`(line_start, line_end)` using `char_span_to_line_range` and writes them into
`research/temp/synthesis-evidence.md` alongside `quoted_support`.

**Change in step 11.6 synthesizer spawn instructions** (lines 240-255): replace
the current citation rendering rule with:

> Every factual sentence citation MUST use the line-anchored form
> `[[note-id:Lstart-Lend]]`. The `Lstart-Lend` values come directly from the
> chunk's `(line_start, line_end)` in synthesis-evidence.md. Do NOT invent line
> numbers — copy them from the evidence file.

If `citation_style == "inline"`, the anchor is rendered `[N:Lstart-Lend]` in the
text and the Sources section lists `[N] Title. URL (L<start>-L<end>)`.

The synthesis-evidence.md format gains one field per chunk:
```markdown
- chunk: "Vietnam reached 64%..."
  note_id: source-note-19
  char_start: 1247
  char_end: 1402
  line_start: 42          # NEW
  line_end: 44            # NEW
  quoted_support: "..."
```

This is the **P2 pre-assembled evidence injection fix for G5**: the synthesizer
writes the citation including its line range in pass 1, while the evidence is in
front of it. No post-hoc regrounding pass needed.

---

### Layer 3 — Verify-side: support-check with line-span judge (kills G4)

**Current keyless gap** (`verifier.py:31-41`): `CitationPresentNLI` marks every
cited sentence SUPPORTED as long as Tier A passes — it does not check whether the
cited span actually supports the claim.

**Replacement: `LineSpanJudge`** (new class in `grounding/verifier.py`, ~20 lines):

```python
class LineSpanJudge:
    """Keyless support-check: reads the cited line span and the report sentence,
    asks a batched Haiku/triage-tier judge whether the span supports the claim.
    Replaces CitationPresentNLI on the keyless path. Costs ~1 triage token batch
    per 20 claims — ~$0.00 on the Claude Code host. No new API key."""

    def predict(self, premise: str, hypothesis: str) -> dict[str, float]:
        # premise = quoted_support (the line span text).
        # hypothesis = report sentence (claim, citation tokens stripped).
        # Routes near-verbatim pairs (overlap >= CLAIM_QUOTE_OVERLAP_SKIP) to
        # ENTAILMENT without a judge call (existing HostJudgeNLI behaviour).
        # For genuine paraphrases: returns NEUTRAL to queue for batched Tier-C.
        # IDENTICAL interface to HostJudgeNLI — zero caller change.
```

The **key addition** is that the Tier-C batched judge (`tier_c_judge` in
`verifier.py:164-185`) now receives the **line span text** as the `quote` field
— not just `anchor.quoted_support` as an opaque string, but the *specific lines*
`L42-L58` re-read from the note body via `note_find`. This is the critical
entailment signal: the judge sees what lines 42-58 say and whether the claim
follows from exactly those lines.

**Change to `CitationVerifier.verify`** (`verifier.py:293-376`):
- After Tier A byte-identity passes, extract `(line_start, line_end)` from the
  anchor.
- Re-read the span: `line_text = body_lines[line_start-1:line_end]` joined.
- Tier B premise = `line_text` (the specific lines), not the full
  `quoted_support`. Tier C queue gets `(hypothesis, line_text)`.

This is the **G4 fix**: verification now checks `line span entails claim`, not
`citation exists and SHA matches`.

**G1 fix**: the `is_factual_claim` heuristic in `gate.py:110-133` is unchanged —
the formatting-artifact false-positives it still misses are now rendered harmless
because:
1. Line-anchored citations are present on every grounded sentence from the
   synthesizer (G5 fix means the draft arrives already grounded).
2. The verifier checks support on the line span, so a sentence that correctly
   carries `[[note-id:L42-L58]]` gets `verified=1` regardless of formatting.
3. The only sentences the gate can block are those that `is_factual_claim` scores
   TRUE but carry no citation — and because the synthesizer emits citation tokens
   inline with grounding instructions, formatting-artifact false-positives
   (bold-span sub-sentence fragments that the splitter tokenizes) now almost
   always either carry the parent sentence's citation or are correctly classified
   as `_is_formatting_line`.

As a belt-and-suspenders guard: bump `split_sentences` in `gate.py:78-107` to
skip lines that are entirely within a `**...**` span (add `_BOLD_SPAN_ONLY` to
`_is_formatting_line`) — a 3-line change. This closes the residual G1 path.

---

### Layer 4 — Gate-side: operate on support verdicts, not existence

**Current** (`gate.py:148-158`): gate checks `anchor.verified != 1` and emits
`unverified-cite` (major). The critical/major split was designed for the era when
`verified=1` only meant byte-identity passed.

**Revised logic**: with `LineSpanJudge` in the verifier path, `verified=1` now
means the line span supports the claim. The gate needs no structural change — just
a documentation update to `Finding.failure_mode` strings and one tightening:

- `unverified-cite` stays major (not critical) for `partial` verdicts (the patcher
  hedges them).
- Promote `unsupported` and `contradicted` dispositions written into
  `citation-verify-actions.json` to CRITICAL from the gate's perspective — these
  block ship. Currently `unverified-cite` is major; the gate's
  `gate_blocks_ship` at line 161 only blocks on `critical`. Add a check:
  ```python
  if anchor.verify_score is not None and anchor.verify_score < PARTIAL_LOW:
      severity = "critical"   # span explicitly does not support the claim
  ```
  This is a 3-line addition to `gate.py:148-158`.

The **G5 loop** is broken structurally: because the synthesizer writes citations
inline (Layer 2), the gate arrives at a draft that is already grounded. The
grading loop (`grader/patcher` at step 12-14) handles `partial` and
`unsupported` verdicts as targeted edit hunks, not wholesale regrounding.

---

## 3. Minimal diff surface

### Files that change

| File | Change type | Size |
|------|-------------|------|
| `src/bad_research/grounding/extract.py` | Add `body_to_lines`, `char_span_to_line_range` | +30 lines |
| `src/bad_research/core/db.py` | Add `body_lines TEXT` column + SCHEMA_VERSION bump | +5 lines |
| `src/bad_research/core/note.py` | Populate `body_lines` on `write_note` | +8 lines |
| `src/bad_research/grounding/anchors.py` | Add `line_start`, `line_end` fields to `ClaimAnchor` + DDL | +10 lines |
| `src/bad_research/grounding/verifier.py` | Add `LineSpanJudge`; update `CitationVerifier.verify` to pass line span to Tier B/C | +30 lines |
| `src/bad_research/grounding/gate.py` | Bump `unsupported`/`contradicted` verdicts to critical; add `_BOLD_SPAN_ONLY` guard | +12 lines |
| `src/bad_research/grounding/render.py` | Extend `extract_citations` regex to parse `[[note-id:L42-L58]]` | +10 lines |
| `src/bad_research/mcp/server.py` | Add `note_find` tool | +35 lines |
| `src/bad_research/retrieval/anchors.py` | Add `line_start`, `line_end` to DDL | +4 lines |
| `skills/bad-research-11-synthesize.md` | Update step 11.4b evidence format + step 11.6 citation token format | prose change |
| `skills/bad-research-11.5-citation-verifier.md` | Update procedure to note `LineSpanJudge` is now the keyless Tier-B | prose change |

### Files that do NOT change

Everything else: the 22-stage pipeline orchestration, the triple-draft ensemble
(step 10), critics (step 12), patcher (step 14), polish (step 15), quality/
consistency.py (E4 self-consistency), the router, the fetcher, the retrieval
engine. The `CitationPresentNLI` no-op class stays in the file as a
last-resort fallback but is no longer the default on the keyless path.

---

## 4. The three most important mechanism decisions

**Decision 1 — `[[note-id:L42-L58]]` as the citation token format.**
Rationale: backward-compatible with the existing `[[wikilink]]` grammar (one
regex extension in `render.py`); carries line provenance in the token itself so
a reader, verifier, or post-processor can re-read the span without a DB lookup;
mirrors OpenAI's `【turn3search4†L42-L58】` but uses our existing wikilink
namespace. Alternative considered: a separate `line_span` JSON sidecar. Rejected:
sidecar requires two-file lookup everywhere the token appears; the colon-suffix
keeps provenance inline.

**Decision 2 — `LineSpanJudge` as the keyless Tier-B replacement, not a new
entailment model.**
Rationale: the existing `HostJudgeNLI` in `verifier.py:44-81` already routes
near-verbatim pairs to a lexical accept and genuine paraphrases to the batched
Tier-C judge. `LineSpanJudge` is the same class extended with the line-span
re-read. No new model download, no new API key, no torch. The batched Tier-C judge
(`JUDGE_SYSTEM` at `verifier.py:123-136`) already asks exactly the right question:
"does the QUOTE support the CLAIM?" — now the QUOTE is the specific line range,
not the full `quoted_support` string stored at fetch time. This closes G4 with
~30 lines of new code.

**Decision 3 — Forward binding (G5 fix) lives in the synthesizer instruction, not
a new pipeline stage.**
Rationale: adding a "regrounding pass" stage between synthesis and criticism
repeats the existing CitationVerifier machinery and balloons the pipeline. The
simpler fix is instruction-level: the synthesizer spawn template
(`bad-research-11-synthesize.md:240-255`) already says "cite as you write, in
pass 1." The one change is requiring the line-anchored `[[note-id:L42-L58]]` form
and providing `(line_start, line_end)` in `synthesis-evidence.md`. The synthesizer
copies line numbers from the evidence file — no invention possible. The gate then
arrives at an already-grounded draft, and the G5 block-and-regrind loop never
triggers.

---

## 5. Open questions (not blocking, for Round 3)

- **Citation coalescing** (`render.py:coalesce_citations:65-130`): the coalescer
  groups consecutive sentences sharing the same source set. With line-anchored
  tokens two sentences citing the same note at different line ranges produce
  distinct tokens (`[[n:L1-L5]]` vs `[[n:L8-L12]]`) — the coalescer will NOT
  merge them, which is correct. Confirm this by inspection; no code change needed.
- **`inline` citation style** (`[N]` numeric): the Sources section format
  `[N] Title. URL` should gain `(L<start>-L<end>)` after the URL for parity.
  Trivial prose change in synthesizer spawn template.
- **Backward compat with old bare `[[note-id]]` anchors**: existing notes in the
  vault that were cited without line ranges still have `anchor.line_start = NULL`.
  The gate's `anchor.verified != 1` check is unaffected (byte-identity still
  works). The `LineSpanJudge` falls back to full `quoted_support` when
  `line_start` is NULL — same behavior as today.

---

*Written: 2026-05-29. Evidence from `round1-competitors-A.md:164,176-219` (OpenAI
line-level grounding), `SYNTHESIS.md:34-42` (G1/G4/G5), `grounding/verifier.py`,
`grounding/gate.py`, `grounding/anchors.py`, `grounding/extract.py`,
`bad-research-11-synthesize.md:134-255`, `bad-research-11.5-citation-verifier.md:46-55`.*
