# Round 5 — does knowing more make you filter better, and should old branches be deleted?

2026-10-10. Five readers: AI research engineers in their own words (X, essays), the empirical
literature on judgment during a search and on pruning, measured research-agent results since June,
long-form talks and the local transcripts, and how top researchers use AI tools in their own research.
✔ = re-checked by the chair against the source bytes (`VERIFIED.md`); everything else is agent-read with
the verbatim span on file in `raw/`. This extends `../2026-09-26-how-researchers-find/FINDINGS.md`.

---

## The owner's intuition, tested

> "the more information you get, the easier it is to find exactly the information you need… the more you
> know in a field, the easier it is to tell which information is genuinely high quality… Over time you
> can even delete some old graphs."

| claim | verdict | what the evidence says |
|---|---|---|
| **Knowing more makes the next search better** | **Holds** | A second literature search run after the answer's precise form was known found the paper that proved it; the first, broad pass had missed it (Tao, Erdős #1026). Students judged relevance better as their task took shape (Vakkari, small samples). |
| **Knowing more makes you filter better** | **Holds only with feedback — otherwise it reverses** | Researchers describe filtering as trained by completed feedback loops, not by reading volume (Schulman, Nanda, Millidge). Knowledge without feedback goes stale: a 2020 intuition becomes a 2023 bias (Chung); a 40-year networking expert was wrong when the requirements changed (Vahdat); Karpathy's own hand-tuned baseline still hid misses an overnight search found. Connected researchers know which highly cited papers do not reproduce; outsiders do not (Keller Jordan ✔). |
| **…and early judgments are worse than later ones** | **Half holds** | Novices see others' work as closer to theirs than it is (Perez ✔). But judgments also *drift* during a session (TREC assessors judged 15–24% of duplicate pairs inconsistently, more so the further apart in time), and the first documents set the bar for the rest — in people and in LLMs. Agents judge the outcome of their *own* earlier search worse than the same outcome handed to them by someone else ("inertia bias" ✔). |
| **The danger is early evidence** | **Wrong way round** | A planted false document reached the final report 40.5% of the time when it arrived at the start, 44.2% mid-research, and **85.5% when it arrived just before synthesis** ✔ — "varied far more with the amount of workflow remaining after exposure" than with its rank. Prompting the agent to verify, and a claim-by-claim verifier after the report, both reduced this and neither removed it ✔. Evidence admitted late has no research left to challenge it. |
| **Delete old graphs** | **Demote, don't delete — and repair what rested on a refuted claim** | Karpathy deletes a note "only rarely… They are never lost" ✔; Weng updates old posts in place. Dropping old context helps mid-strength agents and *hurts* strong ones; summarising history loses to keeping it; overwrite memories delete corrective feedback, append-only beat them. What worked: when a claim is contradicted, trace it to where it entered and redo what was built on it ✔ (flat replacement of the fact alone was the weaker control). |
| **Prune hypotheses as you learn** | **Too-early pruning is the measured failure** | Switching too often "is a more common failure mode than not switching enough" (Schulman ✔). Premature closure is the most common cognitive cause of diagnostic error. In a simulated crisis only residents who held several hypotheses *and tested each long enough* resolved it — fixating and vagabonding both scored 0 of 28 ✔. Research agents "dropped their most ambitious hypotheses within the first fifteen hours… and never changed course", with over half their budget unspent ✔ (n=2). |
| **Alternatives help** | **Only before the evidence comes in** | In an RCT of 297 GPs, a list of alternatives shown before gathering information raised accuracy (OR 1.31, P=0.027); the same list shown after a preliminary diagnosis did not (OR 1.10, n.s.) ✔. |

## What this changes in practice

1. **Name the rivals before the first search, not after the broad round.** The broad round is then
   assigned so that each rival's predicted record is reachable.
2. **Late evidence gets its own challenge.** Anything admitted in the last round — or fetched by the
   critique to fill a gap — that the answer leans on gets a lateral check and an independent source
   before it can carry weight. The critique pass is exactly the "just before synthesis" moment.
3. **A refuted finding repairs what rests on it.** Findings carry what they rest on; a demoted finding
   reopens its dependants and the provisional answer.
4. **Demote, never delete.** The map is append-only; a superseded finding stays, marked with what
   superseded it.
5. **A debunk becomes a check.** When a run finds a field-specific failure (an untuned baseline, a
   spurious reward, a sponsor), every admitted finding of that kind is re-screened against it — the
   working form of "the more you know, the better you filter" (Jordan ✔, Shao, Conmy).
6. **Re-read what you already fetched, with what you now know.** Pages read at fetch time are read
   against the question as it stood then ✔; a new open question first searches the pages already
   saved.
7. **A rival dies only to a finding that bore on it** — never for want of attention.
8. **Search where the run thinks it is settled** — one counterpart assignment goes against the premise
   nobody questioned, not only against the leading claim.

## What AI researchers actually do (new in this round)

- **Run it, don't read it.** "most biglab people now read almost zero papers" (Jordan); reading has
  "low value of information relative to running your own experiments" (Perez ✔); trust only a shared,
  continually tuned baseline — a paper's mistake changes nothing, a speedrun's is found automatically
  in the next record (Jordan ✔). Published gains shrink against tuned baselines and with scale (claimed 1.4–2× optimizer speedups fell
  to 1.1× at 1.2B — abstract ✔; tuning only AdamW's learning rate was worth 2× at 130M); random rewards
  nearly matched real ones on one model family.
- **The deciding information is in the code, the appendix, an undocumented flag, or the author's
  reply** — not the paper body (Nichol; Jordan on a 12,000-line codebase).
- **The best work is unpublished** ("If it works well, it's probably not being published" — Bricken ✔);
  insiders read less widely as they work more (Douglas ✔).
- **AI tools are used to locate human-written sources, never as the source** (Tao ✔), and only where the
  user can verify what comes back. Measured recall of deep-research tools against expert reviews ranges
  from 3% (references of surveys) to ~48% (systematic reviews) independently, 95% vendor-reported.
  Narayanan ranks source selection above hallucination as the factuality problem, and LLMs measurably
  favour highly cited papers when they recall citations (Algaba et al.) — while fabricated citation URLs
  still run at 3–13% across models and agents (Rao et al., abstract).

## Honest gaps

- No study measures an agent re-grading its own early-admitted sources and getting a better answer.
  The nearest are fresh-context isolation (inertia bias) and repair-on-contradiction (ReTree), both on
  QA benchmarks, both the authors' own systems.
- Most agent numbers are BrowseComp(-Plus), whose corpus flatters retrieval; long-form research
  benchmarks are validated against 3–7 systems with 50–75% human–model agreement.
- Nobody found a study of screening order or fatigue inside systematic reviews, or of re-screening early
  records after criteria change.
