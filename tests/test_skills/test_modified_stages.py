import pytest

from tests.test_skills.validate import validate_skill

STAGES = [
    "bad-research-2-width-sweep.md",
    "bad-research-5-depth-investigation.md",
    "bad-research-10-triple-draft.md",
    "bad-research-11-synthesize.md",
    "bad-research-13-gap-fetch.md",
    "bad-research-16-readability-audit.md",
]

# A-1: the generation-time grounding mandate marker. The drafter prompts carry an
# unambiguous "cite as you write — [N] before the terminal period" instruction so
# the downstream uncited-gate runs as a cheap VERIFIER (0-few blocks) rather than a
# heavy block-and-patch rewriter. Asserting the literal anchor keeps the frozen
# wording from silently drifting back to "draft now, ground later".
_GEN_GROUNDING_ANCHOR = "GENERATION-TIME GROUNDING"


def test_all_modified_stages_valid(skills_dir, known_skills):
    for s in STAGES:
        p = skills_dir / s
        assert p.exists(), s
        assert validate_skill(p, known_skills) == [], s


def test_width_sweep_calls_funnel(skills_dir):
    body = (skills_dir / "bad-research-2-width-sweep.md").read_text()
    assert "bad funnel-gather" in body
    assert "top_chunks" in body or "top-chunks" in body


def test_depth_uses_tiered_browse(skills_dir):
    body = (skills_dir / "bad-research-5-depth-investigation.md").read_text()
    assert "--tier-max" in body


def test_synthesize_renders_grounded_citations(skills_dir):
    body = (skills_dir / "bad-research-11-synthesize.md").read_text()
    assert "claim_anchors" in body or "grounded" in body.lower()
    assert "bad retrieve" in body  # synthesizer reads retrieval top-chunks


def test_gap_fetch_uses_tiered_browse(skills_dir):
    body = (skills_dir / "bad-research-13-gap-fetch.md").read_text()
    assert "--tier-max" in body


def test_step16_has_uncited_gate(skills_dir):
    body = (skills_dir / "bad-research-16-readability-audit.md").read_text()
    assert "bad uncited-gate" in body
    assert "ship-block" in body.lower() or "ship block" in body.lower()


def test_patcher_consumes_grader_findings_and_hedges(skills_dir):
    body = (skills_dir / "bad-research-14-patcher.md").read_text()
    assert "critic-findings-grader.json" in body
    # the confidence-band hedge rule (dossier 16 §7)
    assert "confidence_band" in body
    assert "hedge" in body.lower()


def test_step16_has_recitation_gate(skills_dir):
    body = (skills_dir / "bad-research-16-readability-audit.md").read_text()
    assert "bad recitation-gate" in body
    # it's a major finding, NOT a ship-block (unlike uncited)
    assert "not a ship-block" in body.lower() or "does not block ship" in body.lower()


# ── A-1: generation-time grounding (cite-as-you-write) in the drafter prompts ──

def test_step10_mandates_per_sentence_inline_cite_from_first_draft(skills_dir):
    body = (skills_dir / "bad-research-10-triple-draft.md").read_text()
    assert _GEN_GROUNDING_ANCHOR in body
    low = body.lower()
    # Unambiguous: a [N]/[[note-id]] citation before EVERY factual sentence's
    # terminal period, in the FIRST draft (not deferred to a later grounding pass).
    assert "before" in low and "terminal period" in low
    assert "first draft" in low or "as you write" in low
    assert "every factual sentence" in low


def test_step11_synthesizer_spawn_mandates_inline_cite_as_you_write(skills_dir):
    body = (skills_dir / "bad-research-11-synthesize.md").read_text()
    assert _GEN_GROUNDING_ANCHOR in body
    low = body.lower()
    assert "before" in low and "terminal period" in low
    assert "every factual sentence" in low
    # the gate's role becomes a cheap verifier, not a rewriter
    assert "verifier" in low


def test_gen_grounding_preserves_patch_not_regenerate(skills_dir):
    # The cite-as-you-write change must NOT weaken the patch-not-regenerate invariant.
    body = (skills_dir / "bad-research-11-synthesize.md").read_text()
    assert "patch-not-regenerate" in body or "patch not regenerate" in body.lower() \
        or "do not re-synthesize" in body.lower()


# ── B-8: citation coalescing in step 16 (readability, provenance-preserving) ──

def test_step16_mandates_citation_coalescing(skills_dir):
    body = (skills_dir / "bad-research-16-readability-audit.md").read_text()
    low = body.lower()
    # invokes the deterministic helper (not a hand-edit)
    assert "coalesce_citations" in body
    # the rule: collapse CONSECUTIVE sentences sharing the SAME source set
    assert "coalesc" in low
    assert "consecutive" in low
    assert "same source" in low or "identical source" in low or "same set" in low


def test_step16_coalescing_preserves_provenance_and_never_drops_source(skills_dir):
    body = (skills_dir / "bad-research-16-readability-audit.md").read_text()
    low = body.lower()
    # provenance preserved — explicitly forbids dropping any source
    assert "never drop a source" in low or "never drop" in low or "no source" in low \
        or "no provenance lost" in low
    assert "provenance" in low
    # a DISTINCT source must NOT be merged — keeps its own cite, breaks the run
    assert "distinct source" in low
    assert "never merge" in low or "never merges" in low or "not merge" in low \
        or "breaks the run" in low


def test_step16_coalescing_runs_after_both_gates(skills_dir):
    # must run AFTER uncited + recitation gates (gates validate per-sentence cites
    # first; coalescing only collapses the visual repetition afterwards)
    body = (skills_dir / "bad-research-16-readability-audit.md").read_text()
    low = body.lower()
    assert "after" in low and ("both gate" in low or "gates pass" in low
                               or "after the uncited" in low
                               or "after both gate" in low)


# ── E5: distilled-reflection memory (Tavily) — skill-prose discipline ──────────
# The reflections artifact + the read-from-reflections discipline must live in the
# skill prose: width-sweep distills each kept source to ≤3 claim bullets + note_id
# into research/temp/reflections.md and DROPS the raw body from working context;
# the re-retrieve / next-round planning reads reflections.md + open_gaps, NOT the
# raw corpus; synthesis re-injects raw bodies ONLY for the cited note_ids ("re-
# inject raw only at the end") so the verbatim quoted_support spans survive for the
# uncited-/recitation-gate. Asserting the literal anchors freezes the wording.
_REFLECTIONS_ARTIFACT = "research/temp/reflections.md"


def test_width_sweep_distills_to_reflections_and_drops_raw_body(skills_dir):
    body = (skills_dir / "bad-research-2-width-sweep.md").read_text()
    low = body.lower()
    assert _REFLECTIONS_ARTIFACT in body
    # ≤3 distilled claim bullets + note_id, sourced from claims-*.json (not raw text)
    assert "claims-" in body  # the distilled-claims source
    assert "distill" in low
    assert "note_id" in low or "note id" in low
    # the raw body is DROPPED from working context (it stays on disk in the vault)
    assert "drop" in low and ("raw body" in low or "raw note" in low or "raw page" in low)
    # the re-retrieve / next-round planning reads reflections + open_gaps, NOT corpus
    assert "open_gaps" in low or "open gaps" in low
    assert "not" in low and ("raw corpus" in low or "re-read" in low or "reread" in low)


def test_width_sweep_token_growth_is_linear(skills_dir):
    # the whole point: linear (n·m) inter-round growth, not quadratic
    low = (skills_dir / "bad-research-2-width-sweep.md").read_text().lower()
    assert "linear" in low


# ── Draft ensemble reduced 3→2 (strongest-thesis + steelman-contrarian); the
# synthesizer is the reconciler, so a 3rd reconciling draft is no longer spawned.
# The skill filename `bad-research-10-triple-draft` stays as a LEGACY IDENTIFIER. ──


def test_step10_spawns_two_draft_orchestrators_not_three(skills_dir):
    body = (skills_dir / "bad-research-10-triple-draft.md").read_text()
    low = body.lower()
    # spawns TWO draft sub-orchestrators
    assert "spawn 2" in low, "step 10 must spawn 2 draft sub-orchestrators"
    assert "spawn 3" not in low, "step 10 must not spawn 3 draft sub-orchestrators"
    # the dropped third angle has no bold "Draft C" assignment label
    assert "**draft c" not in low, "no third draft angle assignment"
    # produced artifacts are draft-a/b only (no draft-c on disk)
    assert "draft-c" not in low, "no draft-c artifact/id"
    assert "draft-c.md" not in body and "draft-c-source-list" not in body
    # the legacy-filename note must be present (the name: frontmatter is unchanged)
    assert "legacy identifier" in low, "must note the filename is a legacy identifier"


def test_step10_frontmatter_name_unchanged_legacy_identifier(skills_dir):
    """The behavior dropped to 2 drafts, but the skill `name:` frontmatter stays
    `bad-research-10-triple-draft` (a legacy identifier) to avoid churning the
    step-skill roster / hooks / installers."""
    body = (skills_dir / "bad-research-10-triple-draft.md").read_text()
    assert "name: bad-research-10-triple-draft" in body


def test_step11_synthesizer_reads_two_drafts_not_three(skills_dir):
    body = (skills_dir / "bad-research-11-synthesize.md").read_text()
    low = body.lower()
    assert "draft-c" not in low, "synthesizer must not read a third draft"
    # draft_paths handed to the synthesizer are draft-a + draft-b only
    assert "draft-a.md, research/temp/draft-b.md]" in body
    assert "draft-c.md]" not in body


def test_entry_skill_invariant10_spawns_two_orchestrators(skills_dir):
    body = (skills_dir / "bad-research.md").read_text()
    # invariant #10: MUST spawn 2 draft-orchestrators (not 3)
    assert "spawn 2 `bad-research-draft-orchestrator`" in body
    assert "spawn 3 `bad-research-draft-orchestrator`" not in body


def test_draft_and_synthesizer_agent_constants_reference_two_drafts():
    from bad_research.core import hooks

    for const in (hooks.DRAFT_ORCHESTRATOR_AGENT, hooks.SYNTHESIZER_AGENT):
        low = const.lower()
        assert "draft-c" not in low, "agent constants must not reference a third draft"
        assert "from all three drafts" not in low
        assert "one of three" not in low


def test_triple_draft_plans_from_reflections_reinjects_raw_for_cited(skills_dir):
    body = (skills_dir / "bad-research-10-triple-draft.md").read_text()
    low = body.lower()
    assert _REFLECTIONS_ARTIFACT in body
    # drafter plans from reflections, then re-injects raw note bodies ONLY for the
    # note_ids it will cite ("re-inject raw only at the end")
    assert "re-inject" in low or "reinject" in low or "re-injects" in low
    assert "cited" in low or "cite" in low
    # spans must survive for the grounding gates
    assert "quoted_support" in body or "span" in low


def test_synthesize_caps_distilled_context_and_reinjects_spans(skills_dir):
    body = (skills_dir / "bad-research-11-synthesize.md").read_text()
    low = body.lower()
    assert _REFLECTIONS_ARTIFACT in body
    # ≤10K distilled-synthesis-context ceiling (Chroma context-rot)
    assert "10k" in low or "10,000" in low or "10000" in low
    # re-inject raw spans only at the end, for the cited note_ids — preserves the
    # verbatim quoted_support the uncited-/recitation-gate / anchors.py need
    assert "re-inject" in low or "reinject" in low or "re-injects" in low
    assert "quoted_support" in body or "span" in low


# ── C-1: merge step 3 (contradiction-graph) into step 4 as a Step 4.0 preamble ──


def test_step3_merged_into_step4_preamble(skills_dir):
    """After C-1: step 3 content lives as Step 4.0 inside bad-research-4-loci-analysis.md."""
    # step 3 must no longer exist as a standalone skill file
    assert not (skills_dir / "bad-research-3-contradiction-graph.md").exists(), \
        "bad-research-3-contradiction-graph.md must be removed after C-1 merge"
    # step 4 must contain the contradiction-graph procedure as a preamble
    body = (skills_dir / "bad-research-4-loci-analysis.md").read_text()
    assert "Step 4.0" in body, "loci-analysis must have a Step 4.0 preamble section"
    assert "contradiction-graph.json" in body
    assert "consensus-claims.json" in body
    assert "claim-pairing" in body.lower() or "pair contradiction" in body.lower()


def test_step3_removed_from_hooks_roster(skills_dir):
    from bad_research.core.hooks import _BAD_RESEARCH_STEP_SKILLS
    assert "bad-research-3-contradiction-graph" not in _BAD_RESEARCH_STEP_SKILLS
    assert "bad-research-4-loci-analysis" in _BAD_RESEARCH_STEP_SKILLS


# ── C-2: merge step 7 (source-tensions) into step 6 as a Step 6.5 orphan scan ──


def test_step7_merged_into_step6_subsection(skills_dir):
    """After C-2: step 7 content lives as Step 6.5 inside bad-research-6-cross-locus-reconcile.md."""
    assert not (skills_dir / "bad-research-7-source-tensions.md").exists(), \
        "bad-research-7-source-tensions.md must be removed after C-2 merge"
    body = (skills_dir / "bad-research-6-cross-locus-reconcile.md").read_text()
    assert "Step 6.5" in body, "reconcile skill must contain a Step 6.5 orphan-scan subsection"
    assert "tensions.md" in body, "merged output artifact must be tensions.md"
    assert "orphan" in body.lower(), "orphan tension scan procedure must be present"
    # old separate artifacts must no longer be the exit criterion
    assert "source-tensions.json" not in body or "tensions.md" in body


def test_step7_removed_from_hooks_roster(skills_dir):
    from bad_research.core.hooks import _BAD_RESEARCH_STEP_SKILLS
    assert "bad-research-7-source-tensions" not in _BAD_RESEARCH_STEP_SKILLS
    assert "bad-research-6-cross-locus-reconcile" in _BAD_RESEARCH_STEP_SKILLS


def test_step10_reads_tensions_md_not_source_tensions_json(skills_dir):
    body = (skills_dir / "bad-research-10-triple-draft.md").read_text()
    assert "tensions.md" in body, "step 10 must read the merged tensions.md artifact"


# ── C-3: cut step 9 (evidence-digest); build inline in step 10.0b Part 2 ──


def test_step9_merged_inline_into_step10(skills_dir):
    """After C-3: step 9 no longer exists; evidence-digest procedure is in step 10.0b."""
    assert not (skills_dir / "bad-research-9-evidence-digest.md").exists(), \
        "bad-research-9-evidence-digest.md must be removed after C-3 merge"
    body = (skills_dir / "bad-research-10-triple-draft.md").read_text()
    assert "evidence-digest.md" in body, "step 10 must build evidence-digest.md inline"
    assert "10.0b" in body or "Step 10.0b" in body, "inline digest build must be Step 10.0b"
    # the 80-120 claim cap and quoted_support discipline must survive
    assert "80" in body and "120" in body
    assert "quoted_support" in body


def test_step9_removed_from_hooks_roster(skills_dir):
    from bad_research.core.hooks import _BAD_RESEARCH_STEP_SKILLS
    assert "bad-research-9-evidence-digest" not in _BAD_RESEARCH_STEP_SKILLS
    assert "bad-research-10-triple-draft" in _BAD_RESEARCH_STEP_SKILLS


def test_step12_5_grader_still_reads_evidence_digest(skills_dir):
    body = (skills_dir / "bad-research-12.5-grader.md").read_text()
    assert "evidence-digest.md" in body, "grader must still reference evidence-digest.md artifact"


# ── C-4: grader round 1 aggregates critic-findings-*.json (no fresh full scan) ──


def test_grader_round1_aggregates_critic_findings(skills_dir):
    """After C-4: grader round 1 scores from critic-findings-*.json, not a fresh corpus scan."""
    body = (skills_dir / "bad-research-12.5-grader.md").read_text()
    low = body.lower()
    # round 1 uses existing critic findings
    assert "round 1" in low or "round-1" in low or "first round" in low
    assert "critic-findings" in body, "round 1 must reference critic-findings-*.json"
    assert "aggregate" in low or "aggregat" in low, "round 1 must aggregate, not rescan"
    # rounds 2-3 remain full scans
    assert "round 2" in low or "round-2" in low or "second round" in low
    assert "full" in low and ("scan" in low or "corpus" in low), \
        "rounds 2-3 must still perform full corpus scan"
    # convergence loop and floor preserved
    assert "0.70" in body or "0.7" in body
    assert "MAX_GRADER_REVISIONS" in body or "3" in body
    assert "grader-log.json" in body


# ── D-2: step-1 decompose delegated to a work-tier subagent ──


def test_decompose_delegates_to_work_tier(skills_dir):
    """D-2: Step 1 must instruct the orchestrator to spawn a work-tier subagent for
    the JSON extraction, not run it inline at Opus cost."""
    body = (skills_dir / "bad-research-1-decompose.md").read_text()
    # The spawn instruction must explicitly reference work tier or Sonnet
    assert (
        'tier="work"' in body or "tier: work" in body or "work-tier subagent" in body.lower()
    ), "bad-research-1-decompose.md must instruct orchestrator to delegate to a work-tier subagent"
    # The delegation must name the output artifact to read back
    assert "prompt-decomposition.json" in body  # already present; guard against accidental removal


# ── D-3: step-6.5 orphan tension scan delegated to a work-tier subagent ──


def test_reconcile_step65_delegates_tension_scan_to_work_tier(skills_dir):
    """D-3: Step 6.5 (orphan tension scan, post-C-2 merge) must instruct the orchestrator
    to delegate the tensions extraction to a work-tier subagent (reference: C-2, D spec §5)."""
    body = (skills_dir / "bad-research-6-cross-locus-reconcile.md").read_text()
    assert "Step 6.5" in body, (
        "Step 6.5 must exist (C-2 must land before D-3)"
    )
    # Work-tier delegation instruction must be present inside or immediately after the 6.5
    # section. Anchor on the section HEADING ("## Step 6.5"), not the frontmatter mention —
    # post-C-2 the description block names "Step 6.5" first, ~4.7K chars before the section.
    assert "## Step 6.5" in body, "Step 6.5 must be a real section heading, not just a mention"
    step65_idx = body.index("## Step 6.5")
    after_65 = body[step65_idx : step65_idx + 1200]
    assert (
        'tier="work"' in after_65 or "tier: work" in after_65 or "work-tier" in after_65.lower()
    ), "Step 6.5 must delegate the tension scan to a work-tier subagent"
    # tensions.md artifact must still be named (not silently dropped)
    assert "tensions.md" in body


# B-2: the patcher skill consumes the 5th assumption critic's findings.
def test_patcher_skill_findings_paths_includes_assumption(skills_dir):
    body = (skills_dir / "bad-research-14-patcher.md").read_text()
    assert "critic-findings-assumption.json" in body


# ── Re-audit 2026-06: polish step-15.4 integrity gate must match the entry skill ──
# The full-tier gate must require all FIVE critic findings (incl. assumption) AND
# the grader-log — not just the original four critics.


def test_polish_integrity_gate_includes_assumption_and_grader(skills_dir):
    body = (skills_dir / "bad-research-15-polish.md").read_text()
    # the full-tier integrity gate (step 15.4) loops over the required artifacts
    for required in (
        "critic-findings-dialectic.json",
        "critic-findings-depth.json",
        "critic-findings-width.json",
        "critic-findings-instruction.json",
        "critic-findings-assumption.json",  # the 5th critic — was OMITTED
        "grader-log.json",                  # the grader convergence log — was OMITTED
        "patch-log.json",
        "polish-log.json",
    ):
        assert required in body, f"polish integrity gate must require {required}"
    # the stale "four critic findings" prose must be gone
    assert "all four critic" not in body.lower(), \
        "polish gate prose must not say 'all four critic' — the full tier has five"


def test_polish_gate_matches_entry_skill_gate(skills_dir):
    """The polish step-15.4 gate and the entry skill's final integrity gate must
    require the same full-tier artifact set (assumption + grader included)."""
    polish = (skills_dir / "bad-research-15-polish.md").read_text()
    entry = (skills_dir / "bad-research.md").read_text()
    for required in ("critic-findings-assumption.json", "grader-log.json"):
        assert required in entry, f"entry-skill gate must require {required}"
        assert required in polish, f"polish gate must require {required} to match entry"


# ── Re-audit 2026-06: grader skill handles the keyless-skip / passed:null verdict ──
# `bad grade-report` returns {"status":"keyless-skip","passed":null} on a keyless
# box. The grader loop must NOT treat that as `false` and spawn the patcher with
# empty findings — it must branch explicitly (host grades inline, or clean skip).


def test_grader_skill_handles_keyless_null_verdict(skills_dir):
    body = (skills_dir / "bad-research-12.5-grader.md").read_text()
    low = body.lower()
    assert "keyless-skip" in body, "grader must reference the keyless-skip verdict"
    # an explicit null/keyless branch, distinct from passed==false
    assert "passed is none" in low or "passed: null" in low or "passed == null" in low \
        or "passed:null" in low, "grader must branch on passed==null explicitly"
    # must say grade inline (host is the model) and must NOT fall through to the
    # empty-findings patcher spawn
    assert "inline" in low, "keyless branch must grade inline via the host model"
    assert "empty findings" in low or "empty findings list" in low, \
        "grader must explicitly forbid the empty-findings false-path patcher spawn"


# ── Re-audit 2026-06: needs_host_judgment worklist has a consumer in the 3 grounders ──
# `bad verify-citations` emits keyless neutral-band findings with
# needs_host_judgment:true. The grounding-disposition steps must instruct the host
# model to RE-JUDGE those pairs, not ride the bare 0.5 default.


@pytest.mark.parametrize(
    "skill_file",
    [
        "bad-research-11.5-citation-verifier.md",
        "bad-research-fast.md",
    ],
)
def test_grounding_skills_consume_needs_host_judgment(skills_dir, skill_file):
    body = (skills_dir / skill_file).read_text()
    assert "needs_host_judgment" in body, (
        f"{skill_file} must reference the needs_host_judgment worklist field"
    )
    low = body.lower()
    assert "re-judge" in low or "rejudge" in low or "judge that" in low, (
        f"{skill_file} must instruct the host to re-judge needs_host_judgment findings"
    )


# ── B-5: query expansion (width-sweep) + direction-switch pivot (depth) ──


def test_width_sweep_query_expansion_instruction(skills_dir):
    body = (skills_dir / "bad-research-2-width-sweep.md").read_text()
    low = body.lower()
    # explicit per-sub-question paraphrase/synonym instruction
    assert "synonym/paraphrase" in low or "paraphrase alternative" in low
    # minimum count: 3-5 alternatives generated per sub-question
    assert "3–5" in body or "3-5" in body  # noqa: RUF001 (en dash matches skill prose)
    # the reformulation rows are tagged in the search-plan table Type column
    assert "reformulation" in low
    # scoped to Step 2.1 (multi-perspective search planning)
    assert "step 2.1" in low or "2.1" in body


def test_depth_investigation_direction_switch_rule(skills_dir):
    body = (skills_dir / "bad-research-5-depth-investigation.md").read_text()
    low = body.lower()
    # explicit pivot/direction-switch instruction
    assert "pivot" in low or "switch" in low or "switching direction" in low
    # triggered by consecutive failed searches
    assert "consecutive" in low or "3 consecutive" in body or "three consecutive" in low
    # the pivot must be announced explicitly (written to notes)
    assert "switching direction" in low or "pivot" in low
    assert "orchestrator-notes" in body or "orchestrator_notes" in body or "orchestrator-notes.md" in body
