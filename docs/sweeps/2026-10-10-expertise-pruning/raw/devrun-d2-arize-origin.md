<!-- Reader return from the D2 dev run (rounds skill c1fa0de), 2026-10-10 — agent output. Provenance for the Arize "+15%" training-set finding cited in references/domains.md. -->

ASSIGNMENT: leads 1–5 (the Arize origin, 2609.23270v2, mdarena, replication of 2602.11988, measurements outside Python)   BUDGET USED: about 36 tool calls

ENTRY POINTS: Popularity-ordered: WebSearch top results (Arize; a general query about non-Python evaluations). Not popularity-ordered: arXiv API sorted newest first over abs terms for AGENTS.md, CLAUDE.md, "context files" and "cursor rules" (37 entries); the full Semantic Scholar citer list of 2602.11988 sorted by date (29 citers, several with 0 citations); the Arize prompt-learning repo tree and raw ruleset files read through `gh api`; the mdarena source read through `gh api`.

FINDINGS

**Lead 1: origin of the Arize "15%" claim**
- [Q-origin] The resource page states the claim with an "early testing" caveat and names GPT-4.1: "Based on early testing , using prompt learning it's possible to improve Cline's accuracy by over 15% on SWE-Bench without retraining or fine tuning an LLM, changing any tools, or modifying the architecture — bringing GPT-4.1's performance on SWE-Bench Lite to near state-of-the-art levels (matching Claude Sonnet 4-5) purely through ruleset optimization." (https://arize.com/resources/cline-rules/, fetched 2026-10-10, curl). Reached by WebSearch.
- [Q-origin] The blog gives a different range: "Keep reading to see how we improved Cline's accuracy by 10-15%, just by optimizing Cline rules ." Its protocol: "We split SWE-bench Lite into a 50/50 train–test split with 150 examples each". Feedback came from "We used GPT-5 to compare cline_patch with patch (ground truth patch) from SWE bench, asking it to tell us WHY cline_patch was right/wrong". Test phase: "we boot up Cline servers on the 150 test examples, testing out the optimized ruleset, and generating an accuracy metric (% of test examples where Cline's patch passed all unit tests)." The result is stated only in prose and two images: "Through ruleset optimization alone, Prompt Learning was able to close much of that gap, bringing GPT-4.1's performance close to Sonnet-level accuracy" (https://arize.com/blog/optimizing-coding-agent-rules-claude-md-agents-md-clinerules-cursor-rules-for-improved-accuracy/, fetched 2026-10-10, curl). Reached by WebSearch.
- [Q-origin] **Both result images in the blog are titled "Cline Act Mode: SWE-bench Train"**, which means they show the 150 training examples the rules were optimized on. Each shows 5 experiments, "repetitions 1", "run count 150". I read the values from the images myself, so they are not quotes:
  - gpt-4-1-prompt-learning-boost-coding-accuracy.png: Train 1 to Train 5 correctness 0.18, 0.20, 0.34, 0.33, 0.34 (dated 10/10/2025).
  - claude-sonnet-results-coding-agent.png: 0.30, 0.28, 0.32, 0.36, 0.36.
  - No test-set chart appears in the post. GPT-4.1 going from 0.18 to 0.34 on the training set is +16pp.
  - Images: https://arize.com/wp-content/uploads/2025/10/{gpt-4-1-prompt-learning-boost-coding-accuracy,claude-sonnet-results-coding-agent}.png, fetched 2026-10-10. Reached by following the img src in the blog HTML.
- [Q-origin] Repo files carry test numbers. `coding_agent_rules_optimization/cline/act_mode/act_rulesets/gpt4-1_optimized_ruleset` begins "train_accuracy: 0.34 / test_accuracy: 0.3133333333 / optimized ruleset_2:". `.../act_rulesets/ruleset_0.txt` reads "train_accuracy: 0.4 / test_accuracy: 0.4 / optimized ruleset_0: / No rules" and does not say which model produced it. I found no file holding a GPT-4.1 no-rules test baseline (github.com/Arize-ai/prompt-learning, gh api, fetched 2026-10-10). That file was last touched by commit 2026-03-30 "fix organization".
- [Q-origin] Loop order in the cookbook. Each loop runs Cline on train and test with the current `ruleset`, computes `test_acc = sum(test_df["pass_or_fail"] == "pass") / len(test_df)`, then calls the optimizer with `model_choice="gpt-5.5"` and writes `f.write(f"train_accuracy: {train_acc} \n")`. The guide says "Each loop after loop 1 edits and optimizes the previous iteration's ruleset." Its Results section: "Here's an example of one run, where we just ran 2 loops and saw a huge boost in training accuracy." The repo's `cline/act_mode/main.py` has `model_choice="gpt-5",` and `TRAIN_SIZE = 1` / `TEST_SIZE = 1`, which differs from the docs (https://arize.com/docs/ax/cookbooks/prompt-learning/optimizing-coding-agent-prompts-for-execution.md, fetched 2026-10-10, curl; main.py via gh api).
- [Q-origin, residue] The repo also has a Claude Code (Sonnet 4.5) arm. Test-accuracy headers:
  - `ruleset_0.txt`: train 0.58 / test 0.40
  - `ruleset_1.txt`: train 0.6133 / test 0.45185
  - `ruleset_2.txt`: "train_accuracy: 0.5933333333333334 / test_accuracy: 0.0"
  - django rulesets 0–3, test 0.6087, 0.7174, 0.6957, 0.6739, while train rises from 0.647 to 0.779
  - Path: `claude_code/act_rulesets/claude-sonnet-4-5-20250929/`, gh api.

**Lead 2: arXiv 2609.23270v2**
- [Q-counterpart] It is one-shot generation, not an agent: "Generation was single-turn, one stateless call per prompt, with no tools, no retrieval, and no multi-turn interaction." The arms: "Arm B (frame) is the 267-word filled frame, a blank line, and the same task text, sent as a single user message. No system message was used in either arm." (https://arxiv.org/html/2609.23270v2, fetched 2026-10-10)
- [Q-counterpart] What the frame contains: "four labeled sections, Role, Context, Task, and Constraints". Its context rules include "monetary amounts use decimal.Decimal or integer cents", timezone-aware UTC, parameterized SQL, secrets from environment variables, plus seven constraints. The paper: "The frame states constraints, not procedures." The frame comes from the author's own book: ref [6] "S. Dhuri, Delta: Closing the Specification Gap . Acuity Press, 2026."
- [Q-counterpart] The outcome is a defect count, not task success: "The nine checkers measure named defect classes, not correctness or security in general. They were designed by the same author who designed the frame". Also: "It does not show that code generated with the frame is correct".
- [Q-counterpart] Table IV, n = 50 pairs per model. Columns are bare findings / frame findings / mean Δ [CI] / Holm p.

  | Model | Bare | Frame | Mean Δ [95% CI] | Holm p |
  |---|---|---|---|---|
  | claude-sonnet-5 | 40 | 6 | 0.68 [0.38, 1.02] | 4e-5 |
  | deepseek-v4-pro | 22 | 2 | 0.40 [0.24, 0.58] | 4e-5 |
  | gemini-3.1-pro-preview | 44 | 9 | 0.70 [0.38, 1.08] | 4e-5 |
  | qwen3.8-27b | 30 | 2 | 0.56 [0.36, 0.76] | 1e-5 |
  | gpt-5.6-sol | 12 | 4 | 0.16 [0.04, 0.28] | 0.021 |

  Pooled: "the frame arm carried 23 findings against 148 in the bare arm". Ties: "150 of 250 pairs tied". Bandit: "53 versus 11 in aggregate".
- [Q-counterpart] Limits stated by the paper:
  - "One run per arm means we did not measure within-model variance."
  - "neither a length-matched neutral preamble nor a reason-first arm was run"
  - "Results may differ for agentic multi-turn generation, other languages, and other domains."
  - Temperature: "Two vendor endpoints do not accept the parameter for the model families used, and it was omitted for them".
  - The v2 abstract note "marks the length-matched and reason-first arms as planned for the follow-on study".
  - Pre-registered 18 August 2026; single author ("Independent Researcher, NJ"); dataset at Zenodo 10.5281/zenodo.22850887.
- [Q-counterpart] How it reads the null: "Our reading of that result is that it tests the wrong artifact class: instruction files as written in the wild are mostly process and style guidance." It also cites Garg (InfoQ, 10 Sep 2026): "on easy tasks, much of the apparent gain from specifying first was reproduced by a reason-first control with no specification at all".

**Lead 3: mdarena**
- [Q-mdarena] README: "We ran mdarena against a large production monorepo: 20 merged PRs, Claude Opus 4.6, three conditions (bare baseline, existing CLAUDE.md, hand-written alternative)". Result: "The existing CLAUDE.md improved test resolution by ~27% over bare baseline". It does not say whether this is relative or percentage points. No p-value is given, and the repo is not named (github.com/HudsonGri/mdarena README, gh api, fetched 2026-10-10).
- [Q-mdarena] One run per task and condition, by construction. The result path is `output_dir / "runs" / f"{instance_id}__{condition_name}.json"` and work items are built `for task in tasks: for condition in conditions:` with no repeat index (src/mdarena/runner/orchestrator.py). Significance uses `stats.ttest_rel(condition_scores, baseline_scores)` on binary scores and returns None below 5 shared tasks (src/mdarena/evaluation/metrics.py).
- [Q-mdarena] No raw results are in the repo: the tree has only src/, tests/, .claude/skills, CLAUDE.md, README and ROADMAP. When tests are unavailable the code falls back to a diff-overlap score: `RESOLUTION_THRESHOLD = 0.5  # file_overlap > this = "resolved"`. The repo was created 2026-04-05 and last pushed 2026-04-06; it has 67 stars.

**Lead 4: replication or critique of 2602.11988**
- [Q-replication] None of the 29 Semantic Scholar citers has a title about re-running or replicating it, or about other languages (list below). OpenAlex `cite-chain.sh rerun` returned "EMPTY | citers of W7128774696 mentioning replication | 0 total". `fwd` returned 1 citer: "Ranking Is Not Authority: Executable Context-Routing Contracts for Coding Agents" (10.1145/3843779.3844639).
- [Q-replication / Q5] 2608.16630v1 (Mohammadi, Klein, Chadha, Arora, Bindschaedler; 2026-08-17) cites 2602.11988 according to Semantic Scholar.
  - It uses fictional APIs in four languages: "Four hand-authored migrations, Sprocket (Rust), Grimwire (Go), Kestrix (Python), and Zynet (JavaScript), define fictional v1 → v2 APIs."
  - "across 154 closed-book trials on the four fictional migrations no model completes one, and putting the same facts in the prompt lifts 299 of 300 matched trials to at least 9 of the 12 requirements."
  - On SWE-bench: "Because parametric memory substitutes for reading, on SWE-bench, where models likely know the repositories, reads no longer predict success."
  - (https://arxiv.org/html/2608.16630v1 and arXiv API abstract, fetched 2026-10-10. Reached through the Semantic Scholar citer list.)
- [Q-hurt] The same paper, §4.9 "A stale standard is worse than no standard": better-form share is 100% with "a standard agreeing with the code", 33% with "only code demonstrating the convention", and 0% with "a standard demanding the worse form". "Ten trials per condition give 3,385 scored decisions… Deleting an out-of-date convention file beats leaving it in place." Separately: "Across 39 trials the agent follows the document on every contested decision".
- [Q-hurt / Q5] 2610.11007v1 (2026-10-07) is a theory paper with a small empirical part: "appending every instruction with positive standalone value can be arbitrarily worse in net value than selecting an optimal subset… Empirical experiments further show that irrelevant rules drawn from real context files reduce language-model compliance." (arXiv API abstract). Not read in full.
- [lead from snapshot, re-found] 2610.00084v1 (2026-09-07) abstract confirms the lead:
  - "The average profile-baseline accuracy difference is -0.6 percentage points (95% bootstrap interval [-1.5, +0.2] across fixed tasks)"
  - "cost 2.2-4.5 times more per successful call"
  - "On 60 tool-using BioMysteryBench bioinformatics problems (three runs each…), mean solve rates were 46.7% with the profile and 56.7% at baseline, a difference of -10.0 percentage points (95% interval [-16.7, -3.3])"
  - Setup: Gemini 3.8 Flash, Pi agent harness, science question answering rather than coding (arXiv API, fetched 2026-10-10).

**Lead 5: measurements outside Python**
- [Q5] Vercel's eval targets Next.js APIs that models have not seen in training: "Next.js 16 introduces APIs like 'use cache' , connection() , and forbidden() that aren't in current model training data." Also: "Most importantly, we added tests targeting Next.js 16 APIs that aren't in model training data." (https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals, fetched 2026-10-10, curl). The numbers are already known; this adds that the task set is JS/TS and was chosen to be outside training data.
- [Q5] LangChain's skills eval uses Claude Code on LangChain/LangSmith tasks: "On one task to create a LangChain agent, Claude Code never invoked the "langchain agents" skill. Even including a prompt to invoke skills only brought invocation rate up to 70%." Also: "positive ("do this") vs. negative ("don't do this") guidance, and markdown vs. XML tags had similar performance on recorded tasks." (https://www.langchain.com/blog/evaluating-skills, fetched 2026-10-10, curl). No aggregate pass-rate number appears in the fetched body. The "82% vs 9%" figure surfaced only in a search digest that attributes it to an MEXC rewrite.

SOURCE FACTS
- arize.com blog: author meta "Priyan Jindal"; published 2025-10-14, modified 2026-09-25. Arize sells the AX/Phoenix observability products, and the post promotes "Phoenix Experiments". The Cline-rules resource page is an Arize marketing page.
- Arize-ai/prompt-learning: vendor repo with the code and ruleset files.
- arXiv 2609.23270: Sandeep Dhuri, independent and self-funded ("single-author, self-funded study"). v1 2026-09-20, v2 2026-09-30. The intervention is the author's own published frame from his Acuity Press book.
- mdarena: HudsonGri, an open-source tool, created 2026-04-05.
- arXiv 2608.16630: Mohammadi et al., v1 2026-08-17. Affiliations were not extracted.
- arXiv 2610.00084, 2610.11007: abstracts only. Authors were not extracted for 2610.00084.
- Vercel blog (January 2026 per snapshot) and LangChain blog: vendor posts about their own frameworks.

REACHABILITY
- arxiv.org/abs/2609.23270v2 and /html/2609.23270v2: READ (full text, 480 lines).
- arize.com/resources/cline-rules/: READ (full).
- Arize blog: READ (full text and both result images).
- Arize docs execution .md: READ (full).
- Arize repo: READ (tree, 2 READMEs, 8 ruleset headers, main.py grep, test_results_0.csv header).
- mdarena: READ (README in full; orchestrator, metrics and config grepped; ROADMAP grepped, no hits for repeats or variance; issues list).
- Semantic Scholar citations API: READ (29 citers, no `next`).
- OpenAlex via cite-chain: WORKING with 1 forward citer; rerun EMPTY. The coverage gap between 1 and 29 is itself a fact.
- arXiv API searches: READ.
- arxiv.org/html/2608.16630v1: READ (§§1, 3, 4.8–4.9, SWE-bench limit, grepped).
- vercel.com blog, langchain.com blog: READ (grepped).

FRONTIER
- `2608.16630` "The Working Set of a Coding Agent: Coherence Debt in Repository-Scale Tasks"
- `2610.11007` "Curating Always-Loaded Context for LLM Agents: A Capacitated Assortment Model with Censored Feedback"
- `2603.00822` ContextCov: "88.3% constraint compliance (vs. 67.0% and 50.3%)" on SWE-bench Lite 300; "while maintaining functional correctness"
- `2605.06445` Dente, Satriani, Papotti, "Constraint Decay: The Fragility of LLM Agents in Backend Code Generation"
- Garg, "When Spec-Driven Development Pays Off," InfoQ, 2026-09-10, reporting a study accepted at GAISS 2026 (reason-first control)
- `2604.05292v2` Blain and Noiseux, "Broken by Default" ("moved their vulnerability rate by four points")
- `2606.03907` pre-registered protocol: Claude Code and Codex build-vs-buy, from no configuration up to Skills, MCP and permissions
- `2604.15625` ZORO active rules
- `2607.08938` "Better Harnesses, Smaller Models" ("significantly improve performance on 16 of 21 task-SLM pairs")
- `10.1145/3843779.3844639` "Ranking Is Not Authority: Executable Context-Routing Contracts for Coding Agents"
- `2609.34603` "After the Fix" (Skill vs Full memory transfer: 44/29/32pp)
- Arize Claude Code arm: `claude_code/act_rulesets/claude-sonnet-4-5-20250929/`
- Zenodo `10.5281/zenodo.22850887`

DEAD ENDS
- arXiv API query for "low-resource programming", "niche language", "unfamiliar/new/private library" or "version mismatch" combined with agent and skills/documentation/instructions/"context file": only 4 hits, none measuring instruction files on non-Python code apart from the already-known 2603.15401.
- WebSearch for AGENTS.md/skills evaluations on Rust, TypeScript, Lean or Verilog: the digest found none (digest only, not verified).
- OpenAlex rerun for 2602.11988: EMPTY.
- No published GPT-4.1 no-rules test baseline from Arize was found in the blog, the docs or the repo.

SEEN
- https://arxiv.org/abs/2609.23270v2
- https://arxiv.org/html/2609.23270v2
- https://arize.com/resources/cline-rules/
- https://arize.com/blog/optimizing-coding-agent-rules-claude-md-agents-md-clinerules-cursor-rules-for-improved-accuracy/
- the 2 Arize result PNGs
- https://arize.com/docs/ax/cookbooks/prompt-learning/optimizing-coding-agent-prompts-for-execution.md
- github.com/Arize-ai/prompt-learning: tree, cline/README.md, claude_code/README.md, the ruleset files listed above, cline/act_mode/main.py, test_results_0.csv
- github.com/HudsonGri/mdarena: README, orchestrator.py, metrics.py, config.py, ROADMAP.md, issues
- api.semanticscholar.org citations for arXiv:2602.11988
- OpenAlex via cite-chain
- export.arxiv.org: 3 queries
- https://arxiv.org/html/2608.16630v1
- https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals
- https://www.langchain.com/blog/evaluating-skills

OPENED
- What is Arize's GPT-4.1 held-out test accuracy with no rules versus optimized rules? Only the optimized-ruleset test score of 0.313 is in the repo. The model behind the "No rules" 0.4/0.4 file is not stated.
- Does 2604.11088 cite the Arize train-set figure as a test-set result? I did not reread 2604.11088's wording.
- How large is 2610.11007's empirical part (rule counts, models, effect sizes)? It was not read in full.
- Does 2608.16630's stale-standard result (10 trials per condition, one harness plus a second scaffold) carry over to task success, given that it measures share of decisions?
- Does Dente et al. 2605.06445 (constraint decay) measure adherence falling as instruction count grows, with numbers?