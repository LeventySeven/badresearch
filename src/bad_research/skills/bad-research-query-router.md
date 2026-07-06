---
name: bad-research-query-router
user-invocable: false
description: >
  Step 1.5 of the Bad Research pipeline — classifies the decomposition into a
  route (fast / full) and writes it to
  research/prompt-decomposition.json.
---

# Step 1.5 — Query router

**Tier gate:** Runs for ALL runs (it IS the tier/mode decision). The router
never down-routes a query that step 1 marked `full` for a stated reason —
contested topics, time_periods, and argumentative formats always route `full`.

**Goal:** route trivial/bounded/mid-size structured queries to the cheap bounded
ReAct `fast` mode (Reason+Act loop, step-capped) and complex/contested queries to
the full 16-step pipeline. The signal is Bad Research's OWN Step-1 decomposition —
no new classifier.

**`pipeline_tier` vs `route`:** step 1 set `pipeline_tier` as an initial tier
*signal*; this step makes the authoritative routing decision and writes it to
the `route` field. `route` is what the orchestrator sequences from; `pipeline_tier`
is just one input to it.

## Recover state

Read:
- `research/prompt-decomposition.json` — sub_questions, entities, response_format,
  time_periods, contradiction_terms, domains, pipeline_tier
- `research/scaffold.md` — vault_tag

## Procedure

1. Run the deterministic router over the decomposition:
   ```bash
   bad route --decomposition research/prompt-decomposition.json --json
   ```
   It applies this fixed decision tree (mirrors `router.py::classify_route`):
   - **fast** if NOT a full-tier trigger (no contradiction terms, no time_periods,
     not argumentative, not multi-domain, breadth survives the modality gate)
   - **full** else

   The command prints
   `{"route": "fast"|"full", "reason": "...", "query_shape": "straightforward"|"breadth_first"|"depth_first", "shape_reason": "...", "applied": false}`.

   **`query_shape` is ORTHOGONAL to the route** (E12, Claude Research
   `research_lead_agent.md:12-29`). The route is the cost tier — *how many*
   resources (fast/full). The shape is the fan-out arrangement —
   *how they're arranged*: `depth_first` (one topic, multiple perspectives →
   investigators run **sequentially**, each reading the prior's committed
   position), `breadth_first` (independent sub-questions → investigators run **in
   parallel**, importance-ordered, `K = min(n_subq, cap)`), `straightforward` (a
   **single** investigator). The `query_shape` field is NEW and ADDS the fan-out
   shape; it **does not change the route** decision — `classify_route`'s
   fast/full output is identical with or without it. A `full` route
   can carry any of the three shapes; steps 4–5 branch their fan-out on the shape.

2. **Honor the existing tier.** If step 1 set `pipeline_tier: "full"` for a
   stated reason (time_periods present, argumentative, contested), the router
   MUST NOT down-route below `full`. The router can only choose `fast`
   or up-route to `full`; never silently demote a `full`.

3. Write the chosen route back into the decomposition:
   ```bash
   bad route --decomposition research/prompt-decomposition.json --apply --json
   ```
   This adds the top-level `"route"` field AND the `"query_shape"` field to
   `research/prompt-decomposition.json` (both written in the one `--apply` call).

4. Record a one-line rationale (the CLI's `reason` field) in `research/scaffold.md`
   under a `## Route rationale` subsection. Add the CLI's `shape_reason` on the
   next line as the `query_shape` rationale (which fan-out arrangement and why).

## Exit criterion

- `research/prompt-decomposition.json` has a `"route"` field ∈ {fast, full}
- `research/prompt-decomposition.json` has a `"query_shape"` field ∈ {straightforward, breadth_first, depth_first}
- A route never demotes a justified `full`
- The `query_shape` write never changed the `route` (orthogonal — shape ADDS, route is unchanged)
- `research/scaffold.md` has a `## Route rationale` subsection

## Next step

Return to the entry skill (`bad-research`). Sequence by route:
- **fast** → `Skill(skill: "bad-research-fast")` (then the slim citation-grounding pass + slim critic before step 15 polish; its breadth branch spawns K parallel researchers for a wider mid-tier answer)
- **full** → `Skill(skill: "bad-research-2-width-sweep")` (full path)
