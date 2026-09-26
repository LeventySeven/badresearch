# Delegation — the fan-out contract

Read this when you fan out. `references/rounds.md` defines the brief and the rounds; this file is the
evidence behind them — what fan-out costs, when it inverts, and why a brief carries what it carries.

## The number that decides the shape — and how it was misread here

A controlled sweep of 180 configurations (Kim et al., arXiv 2512.08296; 4 agentic benchmarks, 3 model
families) is the best measurement of multi-agent topology there is. This file used to cite it as
"17.2× vs 4.4× error amplification, and on strictly sequential work all four multi-agent shapes lost by
39–70%", and to conclude that frontier-chained research is a do-not-fan-out tier. Read in the primary,
none of that holds for research:

| what the paper measured | what it actually says |
|---|---|
| 17.2× (independent) vs 4.4× (centralized) | **trace-level** amplification; "neither the main effect of error amplification (β=0.014, p=0.658) … reaches statistical significance" once other coordination metrics are controlled |
| −39% to −70% for every multi-agent shape | **PlanCraft** — "sequential constraint satisfaction (planning)", not multi-hop research |
| its web-research benchmark (BrowseComp-Plus) | independent agents that never exchange **−35%** vs one agent; decentralized agents exchanging their current answers between rounds, debate-style, **+9.2%** (0.347 vs 0.318, about 3 points on 100 tasks — the released code first passed a 300-character digest, later full answers); a central orchestrator **+0.2%**. In its own words: decentralized coordination "benefits tasks requiring parallel exploration of high-entropy search spaces" |
| its out-of-sample check | the independent-agent loss held on GPT-5.2 and **not** on held-out Gemini models (+11.1%, +5.9%) |

Two more figures from the same paper that this file quoted: a within-domain predictor picks the best
topology for 87% of held-out configurations, and centralized agents gained +80.8% on a finance task.
Anthropic measured a separate effect on BrowseComp — unintended-solution rate 0.24% single-agent vs 0.87%
multi-agent, **3.7×** — and named the mechanism as *sampling*: more parallel searchers per round raise
the chance one hits leaked material.

**So the shape is: depth from sequential rounds, breadth from parallel readers inside a round, and an
exchange at every boundary.** Readers that never exchange are the losing shape; ungated sharing is
the other one — Anthropic's early agents were "distracting each other with excessive updates", and on a
board of their own making one move spread to over 90% of 533 active agents while duplicate effort
persisted until some began assigning lanes (METR's investigation of an OpenAI agent incident). What crosses is
gated: one line per finding with its span and its source, the dead ends, the sources already seen —
read by every reader at dispatch, admitted by the reasoner (`rounds.md`). The evidence is thin and
mixed: it neither forbids fan-out nor supports a hub — the hub arm, this skill's shape, gained +0.2%.
The support for the shape comes from outside this paper, and each piece has a caveat: a shared verified
board with shared failures beat isolated attempts on code and long-document tasks (DeLM — not research
tasks); a graph written only by a navigator over blind searchers beat flat text by 5.2 points at the
synthesis step (Argus — a vendor, RL-trained); and forecasting teams that shared information while each
member gave their own number, pooled by an algorithm, beat independents in a randomized trial (Mellers
2014 — forecasting, and what it supports is pooled independent judgment, not one judge).

## The union test — the discriminator, sharper than "reading, never judgment"

Two published, funded positions disagree about fan-out, and the discriminator sits in their own
examples rather than in either argument.

- Anthropic's win case is *"all board members of the companies in the IT S&P 500"* — results combine
  by **union**, so one reader's implicit decisions cannot conflict with another's.
- Cognition's loss case requires the parts to be **mutually consistent**: two subagents each did their
  subtask correctly and produced a Flappy Bird with a Super Mario background. Their rule — *rule out
  by default any architecture that does not share full traces, because actions carry implicit
  decisions and conflicting decisions carry bad results.*
  **Weigh it as what it is.** Read in full, that essay contains no benchmark, no eval and no number;
  it is expert testimony from a production team, and it is widely cited as though it were data. Take
  the mechanism and the worked failure; do not put it on the same shelf as the 180-configuration sweep
  above. The two agree here, which is why the discriminator survives — but one of them measured.

**Fan out when the results combine by union. Do not when they must be mutually consistent.**

## What a brief must carry

Beyond the objective and the lane, four things:

- **A boundary — what this reader must NOT read.** Written per reader so you can check the boundaries
  are disjoint before a token is spent. Without one, readers duplicate work and leave gaps; with one,
  overlapping returned sources are a visible defect rather than an invisible cost.
- **The question and the lane — never the conclusion you expect.** Measured on a methodology shipped
  to ~10,000 engineers and then partly retracted: users who pasted "here is what I'm building" into
  the research step **got opinions back instead of facts**. The fix is structural, not a prompt line —
  one context generates the questions, a fresh context with no knowledge of the goal does the reading.
  Keep the implied-record move (SKILL.md's fifth frontier item) as the *reasoner's* move, run against
  readers who were never told the thesis.
- **A slot for what it could not close** — findings, verbatim spans, a reachability outcome, *and* the
  questions its read opened. That last slot is the only way a fan-out feeds the frontier instead of
  flattening it into a single round.
- **The specific thing that would count as wrong here.** A reader without the domain context to
  recognise a defect reports the source as clean. Measured: asked to open-code a trace, an LLM said it
  looked fine; the trace contained a hallucinated offer the company does not make, which the human
  caught because he knew the business.

## The chain veto

**Could you have written this brief before the previous read returned?** If yes for every reader, you
bought width and called it depth, however many ran. The fix is waves: wave 2's briefs are written from
wave 1's open questions. Anything else is one round of depth wearing a fan-out's cost.

## What it costs

Agents use roughly **4× the tokens of chat; multi-agent roughly 15×**. Three factors explain 95% of
BrowseComp variance and **token usage alone explains 80%**. Effort bands that shipped with those
numbers: simple fact-finding = 1 agent, 3–10 tool calls; direct comparison = 2–4 subagents, 10–15 calls
each; complex = 10+. Default 3, hard max 20 — *more subagents = more overhead*.

Note the honest gap: the same source's headline "outperformed single-agent by 90.2%" is an internal
eval with no task count, no denominator and no rubric. It is not citable as a measurement, and the
BrowseComp decomposition is the half that survives.

## Reader budgets, and how the ceiling is enforced

A shipped research subagent carries three levels, not one: a **floor** — a minimum of five distinct
tool calls; a **soft stop** at ~15 calls / ~100 sources; and a **hard kill at 20**, where exceeding the
limit terminates the subagent. A ceiling enforced by killing the reader is a design choice: it makes
partial findings the failure mode instead of an unbounded run. Those numbers fit a **lead** (5–20
calls). A **lane** — a reader that searches a whole kind of source and follows its chains — needs more:
the lanes of the sweep behind `rounds.md` ran 52–141 tool calls each. Give a lane up to ~50 and let it
return partial findings past that.

Related and worth copying: retries are free. A turn counter that is not incremented after an empty
model turn or a denied action spends budget only on productive iterations.

## Where the reducer is, and what it returns

Ablation over model combinations put roughly **three quarters of the lift in synthesis and one quarter
in diversity** — measured by **OpenRouter, announcing its own Fusion product**, on Perplexity's DRACO
benchmark: 100 deep-research tasks across 10 domains. Carry the seller's own scope limit, which is the
half a reader needs and the half a launch thread buries: *"we have only evaluated one deep research
benchmark so far, which did not include long-horizon tasks."* One vendor, one benchmark, no
long-horizon coverage. The 3/4–1/4 split is the shape to reason from, not a constant to plan against.

(This paragraph carried no attribution at all until a sweep traced it, along with the rubric-contamination
finding below and its twin in `checks.md`, to that single unnamed launch thread — three paragraphs, two
files, one seller. That is precisely what *count distinct actors, not distinct URLs* exists to stop, and
it had happened inside the document that states the rule.)

The reducer is where the value sits, and it should return a **typed structure** —
consensus points, contradictions, partial coverage, unique insights, blind spots — which the writer
then works from. A contradiction that is reduced into prose is a contradiction that got averaged away.

## The one judgment that must NOT stay with the reasoner

SKILL.md keeps judgment with the one reasoner holding the thread. There is a single carve-out:
**verification of your own emerging answer goes to a fresh context.** Self-preferential bias is
measured, and it is strongest *exactly when a model is asked to judge its own output against a
rubric*. A refuter (argue this claim is false) is a distinct role from a critic (check this claim is
supported); the refuter is the one worth buying.

## The contamination that invalidates the whole exercise

Once a panel had web search, models began **surfacing the benchmark's own rubric online**; the authors
had to exclude those domains and re-run everything before publishing. Any eval of a research skill run
with the web lane open can retrieve its own answer key. Exclude the domains hosting your fixtures, and
say that you did.

# Two things a brief must carry

**MUST: the question goes to every reader VERBATIM.** Not your paraphrase, not the sub-question as
you have come to think of it three rounds in. Where readers are covering one population, the
population definition is identical across every brief, word for word — otherwise the union you
compute at the end is over sets that were never the same set, and the coverage number it produces
is meaningless.

This composes with the rule above rather than contradicting it: give the **question** verbatim,
withhold the **thesis**. A reader told what you are building returns opinions instead of facts.

**MUST: chase the primary, do not stop at the commentary.** A reader that returns the article
about the paper has returned a source about a source. Follow the citation chain to the thing being
cited — three to eight primaries per reader is the working floor on a real question. The concrete
form: **an encyclopedia page is a source hub, never a citation.** Read it to find what to read,
then cite what it pointed at.
