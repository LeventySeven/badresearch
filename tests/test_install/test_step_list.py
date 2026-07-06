from bad_research.core.hooks import _BAD_RESEARCH_STEP_SKILLS


def test_step_list_has_new_stages():
    s = set(_BAD_RESEARCH_STEP_SKILLS)
    assert "bad-research-0.5-clarify" in s
    assert "bad-research-query-router" in s
    assert "bad-research-fast" in s
    assert "bad-research-11.5-citation-verifier" in s
    assert "bad-research-fresh-review" in s
    # the original 16 kept (renamed)
    assert "bad-research-1-decompose" in s
    assert "bad-research-16-readability-audit" in s
    # ordering: clarify before decompose, router after decompose
    assert _BAD_RESEARCH_STEP_SKILLS.index("bad-research-0.5-clarify") < \
        _BAD_RESEARCH_STEP_SKILLS.index("bad-research-1-decompose")
    assert _BAD_RESEARCH_STEP_SKILLS.index("bad-research-1-decompose") < \
        _BAD_RESEARCH_STEP_SKILLS.index("bad-research-query-router")


def test_step_list_has_20_entries():
    # 16 kept + 5 prior new + 1 E11 plan-gate = 22, MINUS the 3 Workstream-C
    # stage merges (C-1 step 3→4, C-2 step 7→6, C-3 step 9→10) = 19, PLUS
    # bad-research-12.5-grader (audit 2026-06-01: it was invoked by the entry skill
    # but missing from the roster) = 20. (The `ultrafast` route skill was folded
    # away 2026-07-06 — its breadth need now lands on the `fast` route.)
    assert len(_BAD_RESEARCH_STEP_SKILLS) == 20
    assert len(set(_BAD_RESEARCH_STEP_SKILLS)) == 20  # no dupes
    assert "bad-research-1.6-plan-gate" in _BAD_RESEARCH_STEP_SKILLS
    assert "bad-research-ultrafast" not in _BAD_RESEARCH_STEP_SKILLS
    assert "bad-research-12.5-grader" in _BAD_RESEARCH_STEP_SKILLS
    # the 3 merged-away stages are gone from the roster
    assert "bad-research-3-contradiction-graph" not in _BAD_RESEARCH_STEP_SKILLS
    assert "bad-research-7-source-tensions" not in _BAD_RESEARCH_STEP_SKILLS
    assert "bad-research-9-evidence-digest" not in _BAD_RESEARCH_STEP_SKILLS
