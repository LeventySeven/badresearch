# Plan — research rebuild, slice 1: the loop spine

**Goal.** Repair the grounding binding that makes every citation check fail, then land the frontier
gate and stop counters the new loop turns on. Riskiest first: T1 changes shipped semantics, T2 is
pure and cannot break anything. Spec: `docs/specs/2026-09-08-research-rebuild.md` (R1, R3, R9).
Slice 2 (`...-slice-2.md`) adds the local-corpus lane, the no-source-claim check and the skill file.

**Done =** `./.venv/bin/python -m pytest -q` green with the 80% gate still met, AND
`./.venv/bin/bad verify-citations` no longer returns every row `unsupported` on the preserved fixture
(see Manual below).

**Approach.** One dataclass field, one call-site correction, one new stdlib-only module. No new
dependencies. Failing test first in both tasks; the first test is a planted defect that reproduces a
measured production failure.

**Global constraints — every task honours these:**
- Python ≥3.11, stdlib only for new modules. No new third-party dependency.
- Repo style: `from __future__ import annotations`, type hints; Typer registration per `cli/__init__.py:42`.
- Coverage gate is 80% repo-wide. Run per-task tests with `--no-cov`; run the full suite without it.
- **A check that can only pass is not a check** — each check ships a planted-defect fixture proving red.
- Never edit a test to make it pass. If a test fails, the code under test is the suspect.
- **Precedence when two pull against each other:** correctness of a check beats its coverage. A narrow
  check that is never wrong ships; a broad one that fires on valid input does not.

**Divergence rule.** T1 is the load-bearing risk: separating `anchor_id` from the gate's lookup may
break `gate.get()` call sites. If it does not resolve in **3 attempts**, STOP and report — do not
improvise a third representation.

Deferred: all 8 source lanes; the 4 output contracts; the reader/adjudicator/quote-verifier agent
definitions; reranking and retrieval-kind routing; the new `SKILL.md`; deleting the 19-stage
orchestration, `graph/`, the `--codex` translator and the polish/readability stages; plugin packaging.
**Do not build these here, and do not re-open the spec's settled decisions R11 (no graph), R13 (no
`Skill()` indirection) or R18 (no modes, extra critics or templates).**

**Research fold-in (verified 2026-09-08):**
- `grounding/anchors.py:20-21` — `ClaimAnchor`'s own docstring states the invariant:
  *"anchor_id == quote_sha(quoted_support)"*. `cli/research.py` violates it.
- `grounding/verifier.py:161` — `tier_a_byte_identity` returns False unless
  `quote_sha(anchor.quoted_support) == anchor.anchor_id`.
- **The defect:** `cli/research.py:881-883` builds the numeric anchor with `anchor_id=str(idx)` (the
  1-based citation ordinal) and `quoted_support=body`. A SHA can never equal `"2"`, so Tier A fails for
  every row. Measured live: **111/111 `unsupported`, score `0.0`, `needs_host_judgment: False`** — and
  the skill's prescribed DROP-CITE-below-0.35 disposition would have stripped all 111 *correct*
  citations. `research.py:879-881`'s comment shows why the ordinal is there: `gate.get("1")`.
  **Two consumers, one field, incompatible contracts.**
- `anchors.py:14` `quote_sha(str) -> str`; `:143` `build_from_claims` has **zero production callers**.

---

## User Review Required

- **T1 changes the semantics of a shipped field** (`ClaimAnchor.anchor_id`) that two consumers read
  differently. It is a behaviour change on the grounding path, not a refactor. Review the diff before
  slice 2 begins.
- No migration, no deleted public API, no prod-config change.

---

### Task 1: Separate the gate's lookup key from the Tier-A quote SHA

**Files:**
- [MODIFY] `src/bad_research/grounding/anchors.py:20-63`
- [MODIFY] `src/bad_research/cli/research.py:873-890`
- [TEST]   `tests/test_grounding/test_anchor_binding.py`

- [ ] Write the failing test — **this is the planted defect; it reproduces the measured 111/111 failure**:
      ```python
      from bad_research.grounding.anchors import ClaimAnchor, quote_sha
      from bad_research.grounding.verifier import tier_a_byte_identity

      BODY = "DeepSeek-V4-Flash costs $0.66 per million output tokens off-peak."

      def test_numeric_marker_anchor_passes_tier_a_and_stays_findable():
          span = "$0.66 per million output tokens"
          start = BODY.index(span)
          a = ClaimAnchor(note_id="n1", claim="", quoted_support=span,
                          char_start=start, char_end=start + len(span),
                          verified=1, anchor_id=quote_sha(span), lookup_key="2")
          assert tier_a_byte_identity(a, BODY) is True   # SHA matches the span
          assert a.lookup_key == "2"                     # gate still finds it by ordinal

      def test_lookup_key_defaults_to_anchor_id_when_unset():
          a = ClaimAnchor(note_id="n1", claim="", quoted_support="x", char_start=0,
                          char_end=1, verified=1, anchor_id=quote_sha("x"))
          assert a.lookup_key == a.anchor_id
      ```
- [ ] Run `./.venv/bin/python -m pytest tests/test_grounding/test_anchor_binding.py -q --no-cov` → expect FAIL (`unexpected keyword argument 'lookup_key'`)
- [ ] In `anchors.py`, add to `ClaimAnchor` (verified `@dataclass` at `:19` is **not** frozen, so
      plain assignment is correct):
      ```python
      lookup_key: str = ""

      def __post_init__(self) -> None:
          # The gate addresses an anchor by citation marker ("2") or note id; Tier A
          # compares anchor_id against quote_sha(quoted_support). Different facts —
          # sharing one field made Tier A unsatisfiable for every numeric marker.
          if not self.lookup_key:
              self.lookup_key = self.anchor_id
      ```
- [ ] In `cli/research.py:874-877` set `anchor_id=quote_sha(body)`, `lookup_key=note_id`.
      In `:881-883` set `anchor_id=quote_sha(body)`, `lookup_key=str(idx)`.
- [ ] Repoint every gate lookup: `grep -rn "gate.get(\|\.get(note_id)\|\.get(str(" src/bad_research/`
      — each must read `lookup_key`.
- [ ] Run `./.venv/bin/python -m pytest tests/test_grounding tests/test_cli -q --no-cov` → expect PASS
- [ ] Commit: `git commit -am "fix(grounding): separate the gate lookup key from the Tier-A quote SHA"`

### Task 2: The frontier gate and stop counters

**Files:**
- [NEW]  `src/bad_research/frontier.py`
- [TEST] `tests/test_frontier/test_gate.py`

- [ ] Write the failing tests:
      ```python
      from bad_research.frontier import Frontier, gate_query, StopCounters

      def test_query_naming_no_frontier_item_is_refused():
          ok, named = gate_query("what is the price of an H100", Frontier(items={"H200", "MoE"}))
          assert ok is False and named == []

      def test_query_naming_a_frontier_item_passes_and_reports_which():
          ok, named = gate_query("H200 memory bandwidth", Frontier(items={"H200", "MoE"}))
          assert ok is True and named == ["H200"]

      def test_first_query_is_always_allowed():
          assert gate_query("anything", Frontier(items=set()), first=True)[0] is True

      def test_counters_are_computed_not_reported():
          c = StopCounters()
          c.observe(domains={"a.com"}, entities={"X"})
          assert c.should_stop() is False           # step 1 never stops
          c.observe(domains={"a.com"}, entities=set())
          assert c.should_stop() is True            # 0 new domains, 0 new entities
      ```
- [ ] Run `./.venv/bin/python -m pytest tests/test_frontier -q --no-cov` → expect FAIL (module missing)
- [ ] Implement `src/bad_research/frontier.py`:
      ```python
      from __future__ import annotations
      import re
      from dataclasses import dataclass, field

      MIN_NEW_DOMAINS = 2   # MIN_SOURCES_PER_SUBQ / RESERVE_FOR_SYNTHESIS land with the lane (slice 2)

      @dataclass
      class Frontier:
          """Entities/quantities learned from a read and not yet explored (spec R1)."""
          items: set[str] = field(default_factory=set)

          def add(self, new: set[str]) -> None:
              self.items |= {t for t in new if t}

          def close(self, item: str) -> None:
              self.items.discard(item)

      def _norm_tokens(text: str) -> set[str]:
          """Casefolded tokens with trailing punctuation stripped.

          `$0.66` yields `0.66` on both sides so a quantity matches itself, and a
          trailing period no longer welds itself onto the token before it.
          """
          raw = re.findall(r"[A-Za-z0-9][\w.\-]*", text)
          return {t.casefold().rstrip(".-") for t in raw} - {""}

      def gate_query(query: str, frontier: Frontier, first: bool = False) -> tuple[bool, list[str]]:
          """Refuse a query naming no frontier item. The first query is exempt (spec R1).

          An item is NAMED when every one of its tokens appears in the query, so a
          multi-token item ("GB200 NVL72") and a quantity ("$0.66") both match —
          three of R1's five item types are multi-token by construction, and an
          equality test against single tokens could never name any of them.
          """
          if first:
              return True, []
          qt = _norm_tokens(query)
          named = sorted(
              i for i in frontier.items
              if (it := _norm_tokens(i)) and it <= qt   # `and it` — an item with no
          )                                            # tokens must not match everything
          return bool(named), named

      @dataclass
      class StopCounters:
          """Computed by the harness BEFORE the prompt is built, never self-reported (spec R3)."""
          seen_domains: set[str] = field(default_factory=set)
          seen_entities: set[str] = field(default_factory=set)
          steps: int = 0
          last_new_domains: int = 0
          last_new_entities: int = 0

          def observe(self, domains: set[str], entities: set[str]) -> None:
              self.last_new_domains = len(domains - self.seen_domains)
              self.last_new_entities = len(entities - self.seen_entities)
              self.seen_domains |= domains
              self.seen_entities |= entities
              self.steps += 1

          def should_stop(self) -> bool:
              if self.steps < 2:
                  return False
              return self.last_new_domains < MIN_NEW_DOMAINS and self.last_new_entities == 0
      ```
- [ ] Run `./.venv/bin/python -m pytest tests/test_frontier -q --no-cov` → expect PASS
- [ ] Commit: `git commit -am "feat(frontier): entity-frontier gate and harness-computed stop counters"`

---

## Where R2 lands (recorded because this plan did not say)

Spec **R2** — an unreconciled contradiction is a first-class frontier item and the run may not close
while one is open — is **not implemented here and is not in the Deferred list**, which was a gap in
this plan rather than a decision. It lands in **slice 2**, with the producer that fills
`Frontier.items`: R2 is unenforceable until something populates the frontier and something owns "the
run closes", and `gate_query` has zero production callers today. Recording it so the omission is a
stated scope boundary rather than a silent one.

## Carried into slice 2 — accepted review findings, deferred with a reason

These came out of recheck rather than the pre-declared Deferred list above. They are real, accepted,
and out of scope for this slice; they become tasks in slice 2 rather than notes in a conversation.

1. **Two DDLs for one table.** `grounding/anchors.py:77` (`CLAIM_ANCHORS_DDL`, updated here) and
   `retrieval/anchors.py:23` (`PROVENANCE_DDL`, not updated) both create `claim_anchors`.
   `core/db.py:175-176` runs `create_provenance_tables` on every vault open, so a vault's
   `hyperresearch.db` gets the pre-migration shape and nothing migrates it — the grounding CLI uses a
   different file (`<root>/.bad-research/anchors.db`), which is why no current path breaks. Reproduced:
   `create_provenance_tables(c)` then `AnchorStore(c).get("x")` raises
   `OperationalError: no such column: lookup_key` — loud, not silent, but a crash where the old code
   worked. **Not fixed here because** `tests/test_retrieval/test_anchors.py:29` asserts
   `pk == ["anchor_id"]`, and editing a test to make this change pass is forbidden by this plan.
   Slice-2 task: point `PROVENANCE_DDL` at `CLAIM_ANCHORS_DDL` (one table, one DDL) and update that
   test — legitimate then, because the task will explicitly be about the schema.

2. **Tier-A byte-identity is vacuous on the `--note-bodies` standalone path.** `cli/research.py:878-891`
   seeds every anchor with `quoted_support = the whole note body` and `char_start=0/char_end=len(body)`,
   so `tier_a_byte_identity` reduces to `body == body`. Verified directly: it returns True for a body
   that supports nothing at all. **This is pre-existing, not introduced here** — before the fix Tier A
   always returned False on this path, so the diff moved it from always-fail to always-pass; neither is
   a check. The measured consequence in the re-run is that the real work falls to Tier B: 3 `supported`,
   **108 of 111 `needs_host_judgment: true`**. Spec R9 counts byte-identity as an *executing* check, so
   until this is fixed "citation grounding is repaired" must not be read as "byte-identity now protects
   the standalone path." Slice-2 task: bind standalone anchors to the located span from the claims JSON
   rather than the whole body, and add a planted-defect fixture proving Tier A goes red on a
   paraphrase.

## Verification Plan

**Automated** — a fresh session runs these; each pass condition stated:
- `./.venv/bin/python -m pytest tests/test_frontier tests/test_grounding -q --no-cov` → exit 0 *(R1, R3)*
- `./.venv/bin/python -m pytest -q` → exit 0, coverage ≥ the 89.29% baseline captured at setup
- `./.venv/bin/ruff check src` → exit 0 *(src is clean at baseline; `tests/` carries **18 pre-existing**
  errors — 6×F401, 3×RUF003, 3×N812, 2×N806, RUF059, RUF001, N802, E741 — none in `src/`. The criterion
  is `src` clean plus **no new** entries against the captured baseline at
  `scratchpad/ruff-baseline.txt`; it is NOT "fix the 18", which is out of scope for this slice.)*
- `./.venv/bin/bad doctor -j` → exit 0, `ok: true` *(the CLI still imports and runs)*
- `./.venv/bin/python -c "from bad_research.frontier import gate_query, Frontier; import sys; sys.exit(0 if gate_query('h100 price', Frontier(items={'H200'}))[0] is False else 1)"` → **exit 0** *(the gate actually refuses a re-phrase — R1's observable behaviour, not just its unit test)*

**Negative constraints — must hold alongside the greens:** no assertion weakened, no expected output
hardcoded, no test edited to make it pass, the 80% coverage gate not lowered, and no third
representation of a claim's identity introduced.

**Manual** — needs a human:
- Re-run `./.venv/bin/bad verify-citations` against the preserved fast-arm report at
  `/private/tmp/claude-501/-Users-seventyleven-Desktop/47bf30ba-3257-44d3-a6e3-5cfa643debb0/scratchpad/armtest/fast/`
  and confirm it no longer returns 111/111 `unsupported` at score `0.0`. This is the whole point of T1
  and no unit test can assert it against real fetched notes.
- Eyeball the T1 diff for any call site that reads `anchor_id` where it now means the SHA.
