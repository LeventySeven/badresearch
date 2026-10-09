# STATE — badresearch — rewritten 2026-10-10

## Goal
bad-research measurably improved on real questions: a held-out blind head-to-head (T1–T3, 2 judges each, opposite order) where the new skill beats c1fa0de, plus each change traced to a cold-use defect or a verified finding; merged to main.
- 2026-10-10 user: "do it as autonomous and proactive work, if needed you can partially or fully relaunch the research work, don't skimp and do not stop till the end, quality is top priority"
- 2026-10-10 user: "but you don't need hetzner for this task" — dropped D3 (Hetzner CPX) and T2 (Kamal on Hetzner); both replaced by AI-research questions in QUESTIONS.md.
- 2026-10-10 user: "everything should run locally, and remember that if needed you can relaunch that research workflow with newest direction, if that will boost quality, and add more alpha like now we do not need to skimp" — no cloud/remote sessions; extra research lanes G4 (talks/transcripts) + G5 (how top researchers use AI in their own research) added.
- 2026-10-10 user (on the agentic-search run): "for this one you can use top source channels from gathering context skill, like all relevant videos(there're a lot of them on this field) SPECIFICALLY ai engineer channel, find every useful/relevant video, transcribe via yt dlp and use it for this agent's work" — 35 AIE talks picked from 1,268 titles; transcripts handed to D3 (Q3 is therefore no longer a controlled skill-vs-plain pair).
- 2026-10-10 user: "proceed till the end autonomosly, no need to stop or ask me anything… top priority is quality of skill and research, till the end, no stopping"

## Done
- questions fixed before runs: research/cold-use-2026-10-10/QUESTIONS.md (gitignored)
- doctor reports a stale install; web-live probe fixed — e11bc18; `pytest tests/test_cli/test_doctor_installed_skill.py` 3 passed
- X tool returned no followers/bio though the X lane requires them — fixed in ~/Desktop/compound-v/research/xh_norm.py (local, gitignored); verified followers=19787 for kellerjordan0
- G1 saved to sweep raw/; 9 of its spans chair-verified (VERIFIED.md)
- dev results: skill beat plain 6/6 judges (D1 S,S; D4 S,S; D5 C,C) at 5–8x wall time; D2/D3 pending
- round-5 sweep G1–G5 committed d8a37e0; skill batch 1 (9 changes, docs/specs/2026-10-10-bad-research-cold-use.md) — `pytest` 1768 passed
- dev skill arms D1–D5 + gap readers G1–G3 (docs/sweeps/2026-10-10-expertise-pruning/BRIEF.md) launched

## Next
1. Judge D2 and D3 vs PD2/PD3 (blind, 2 each); fold any new defect into the skill.
2. Independent recheck of the whole skill diff (compound-v:code-reviewer, artifact mode); fix; then held-out T1–T8 old (c1fa0de) vs new, ≤2 arms at once.
3. Change the skill (each change cites its defect); recheck; held-out T1–T3 head-to-head; merge.

## Open decisions
- none

## Bounds
Stop = Goal. Escalate only on: a one-way door (push to a public remote other than our branch->main merge, spending money, deleting data). Verifier ≠ implementer: judges are fresh agents that never see the skill.

## Do not
- Run `bad install` for the owner before the improved skill is final — do it once, at the end, and say so.
- Commit research/ answers (repo is PUBLIC; answers may cite private memory).
- Read KNOWN-findings via agents only — load-bearing primaries get opened by the chair.
