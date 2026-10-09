# STATE — badresearch — rewritten 2026-10-10

## Goal
bad-research measurably improved on real questions: a held-out blind head-to-head (T1–T3, 2 judges each, opposite order) where the new skill beats c1fa0de, plus each change traced to a cold-use defect or a verified finding; merged to main.
- 2026-10-10 user: "do it as autonomous and proactive work, if needed you can partially or fully relaunch the research work, don't skimp and do not stop till the end, quality is top priority"
- 2026-10-10 user: "but you don't need hetzner for this task" — dropped D3 (Hetzner CPX) and T2 (Kamal on Hetzner); both replaced by AI-research questions in QUESTIONS.md.
- 2026-10-10 user: "everything should run locally, and remember that if needed you can relaunch that research workflow with newest direction, if that will boost quality, and add more alpha like now we do not need to skimp" — no cloud/remote sessions; extra research lanes G4 (talks/transcripts) + G5 (how top researchers use AI in their own research) added.

## Done
- questions fixed before runs: research/cold-use-2026-10-10/QUESTIONS.md (gitignored)
- doctor reports a stale install; web-live probe fixed — e11bc18; `pytest tests/test_cli/test_doctor_installed_skill.py` 3 passed
- X tool returned no followers/bio though the X lane requires them — fixed in ~/Desktop/compound-v/research/xh_norm.py (local, gitignored); verified followers=19787 for kellerjordan0
- G1 saved to sweep raw/; 9 of its spans chair-verified (VERIFIED.md)
- dev skill arms D1–D5 + gap readers G1–G3 (docs/sweeps/2026-10-10-expertise-pruning/BRIEF.md) launched

## Next
1. On each return: save via scratchpad/extract.py into research/cold-use-2026-10-10/ (answers) or the sweep raw/ (G*). Then plain arms PD1–PD5 (no skill).
2. Blind diagnostic judge per dev question; read MAPs/trajectories myself; pool defects.
3. Change the skill (each change cites its defect); recheck; held-out T1–T3 head-to-head; merge.

## Open decisions
- none

## Bounds
Stop = Goal. Escalate only on: a one-way door (push to a public remote other than our branch->main merge, spending money, deleting data). Verifier ≠ implementer: judges are fresh agents that never see the skill.

## Do not
- Run `bad install` for the owner before the improved skill is final — do it once, at the end, and say so.
- Commit research/ answers (repo is PUBLIC; answers may cite private memory).
- Read KNOWN-findings via agents only — load-bearing primaries get opened by the chair.
