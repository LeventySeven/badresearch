# STATE — badresearch — rewritten 2026-10-10

## Goal
bad-research measurably improved on real questions: a held-out blind head-to-head (T1–T3, 2 judges each, opposite order) where the new skill beats c1fa0de, plus each change traced to a cold-use defect or a verified finding; merged to main.
- 2026-10-10 user: "do it as autonomous and proactive work, if needed you can partially or fully relaunch the research work, don't skimp and do not stop till the end, quality is top priority"
- 2026-10-10 user: "but you don't need hetzner for this task" — dropped D3 (Hetzner CPX) and T2 (Kamal on Hetzner); both replaced by AI-research questions in QUESTIONS.md.
- 2026-10-10 user: "everything should run locally, and remember that if needed you can relaunch that research workflow with newest direction, if that will boost quality, and add more alpha like now we do not need to skimp" — no cloud/remote sessions; extra research lanes G4 (talks/transcripts) + G5 (how top researchers use AI in their own research) added.
- 2026-10-10 user (on the agentic-search run): "for this one you can use top source channels from gathering context skill, like all relevant videos(there're a lot of them on this field) SPECIFICALLY ai engineer channel, find every useful/relevant video, transcribe via yt dlp and use it for this agent's work" — 35 AIE talks picked from 1,268 titles; transcripts handed to D3 (Q3 is therefore no longer a controlled skill-vs-plain pair).
- 2026-10-10 user: "after you finish everything commit push everything to main" — authorizes the final merge of run/cold-use-2026-10 into main and `git push origin main`.
- 2026-10-10 user: "proceed till the end autonomosly, no need to stop or ask me anything… top priority is quality of skill and research, till the end, no stopping"

- 2026-10-10 owner: "do that right now and stop that work for now, we will proceed sooner" — "that" = the wrap-up (spec results, memory, bad install + doctor, merge to main, push); held-out runs paused after T3 (T4 arms stopped mid-run).

## Done
- held-out T1: new SLIGHT, new SLIGHT (judges in research/cold-use-2026-10-10/judges/t1-*); T2 answers saved, judges running; T3 pair running
- absence-gate verbs widened 98dc8ad; cite-the-headline-direction rule 8bf896d (both AFTER the held-out arm snapshot — untested by held-out)
- questions fixed before runs: research/cold-use-2026-10-10/QUESTIONS.md (gitignored)
- doctor reports a stale install; web-live probe fixed — e11bc18; `pytest tests/test_cli/test_doctor_installed_skill.py` 3 passed
- X tool returned no followers/bio though the X lane requires them — fixed in ~/Desktop/compound-v/research/xh_norm.py (local, gitignored); verified followers=19787 for kellerjordan0
- G1 saved to sweep raw/; 9 of its spans chair-verified (VERIFIED.md)
- dev results: skill beat plain 10/10 judges (D1 S,S; D2 C,C; D3 C,C uncontrolled; D4 S,S; D5 C,C) at 5–8x wall time — 7a676de
- skill changes: 012e2e2, review fixes e670e44, recheck fixes cb67f6a (two reviews, all findings closed); pytest 1769 passed
- round-5 sweep G1–G5 committed d8a37e0; skill batch 1 (9 changes, docs/specs/2026-10-10-bad-research-cold-use.md) — `pytest` 1768 passed
- dev skill arms D1–D5 + gap readers G1–G3 (docs/sweeps/2026-10-10-expertise-pruning/BRIEF.md) launched

## Next
1. Resume held-out T4–T8 (questions in research/cold-use-2026-10-10/QUESTIONS.md): old c1fa0de vs new 0c1d963; rebuild arms with `git archive <sha> skills/bad-research agents | tar -x -C <arm>` (scratchpad arms are session-local); arm prompt = spec "How it is judged" + FOREGROUND subagents; one pair at a time; 2 blind judges each (opposite order), tools (blind.py, extract.py, judge-template.txt, questions.json) are in research/cold-use-2026-10-10/tools/; blind.py strips Tier/RUN NOTE/paths but NOT a prose tier sentence — strip that by hand.
2. Add rows to docs/specs/2026-10-10-bad-research-cold-use.md "Held-out results so far"; then delete this file in the final commit.

## Open decisions
- none

## Bounds
Stop = Goal. Escalate only on: a one-way door (push to a public remote other than our branch->main merge, spending money, deleting data). Verifier ≠ implementer: judges are fresh agents that never see the skill.

## Do not
- Run `bad install` for the owner before the improved skill is final — do it once, at the end, and say so.
- Commit research/ answers (repo is PUBLIC; answers may cite private memory).
- Read KNOWN-findings via agents only — load-bearing primaries get opened by the chair.
- Take a held-out arm's last message as its answer without checking it: T1O ended its turn with "round 3 running" while its readers lived on; their results come to the chair. Save them into the arm's work/ and SendMessage the arm to continue. T3+ arm prompts carry the harness note in SETUP: run subagents in the FOREGROUND (several per message), never end the turn to wait for background ones.
