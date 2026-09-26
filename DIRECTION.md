# DIRECTION — the owner's instructions, verbatim

**This file outranks every other document in this repo.** Where it and any skill, doc, audit or
README disagree, this file wins. Do not paraphrase it, do not "clean it up", do not summarise it
into a spec and then work from the spec. Read it first, every session.

Captured 2026-09-07/08 from the session that opened the revamp. Owner's words are quoted exactly as
typed, including typos. Anything not in a quote block is annotation and carries no authority.

---

## 1. The opening ask

> check desktop/badresearch
> Now analyze this whole folder and whole skills first. I think maybe we should somehow make it
> simpler if it's needed, because I think it's a lot overcomplicated for now.
>
> And also, when we are using this research skill, sometimes a lot of things that does not work. For
> example, step-by-step skills — they're not working, and coding agents have to read them manually
> and not invoke it. So it's first error.
>
> And second, I think we should revamp it fully. So don't skimp — no need to maybe enhance the skill
> if it's bad, or enhance it somehow, when we can just fully revamp it. Because quality is a
> priority. So do not skimp on that. If everything needs full revamp of anything, we should do that.
>
> And what I think the skill should be. So like AI research skills — firstly we should do systematic
> approach and check how real researchers from top companies, from top startups, that have done
> multiple things, multiple great researchers, worked in great companies, great startups — how they
> do their work.
>
> And I think research basically is like making deep and broad research and searching for multiple
> interconnections everywhere. For example — yeah, I think [a searcher] searches for one thing, but
> a researcher finds one thing, and after he finds one thing he got more info in context to find
> another thing, and he connects these two things. After that he finds — since he knows these two
> things, he knows a lot more. So he's systematically making anything broader and deeper, because he
> knows more and more. And after some time he knows this thing, this thing, and that allows him to
> find even more connected things, even more relevant things than he will ever find from one-step
> research. Like research should be multi-step, multi-iterations.
>
> And also, knowing a lot of things in your research also makes you find counterparts of your
> research. So when you know a lot of things, you can research counterparts of it to be 100% sure.
> So I think — this is my mind on it.
>
> And like, this interconnecting — I think analogy of it is graphs. But graphs will be overkill for
> research. But I think it's somehow similar to how graph databases and graphs work, because they
> allow building interconnection, multiple connections across different things, to connect
> everything. So not only like graphs are making your data look like graphs — but research makes
> your data look like graphs. And graphs allow you to expand more, to find more relevant, more
> alpha, more significant information that might be less easy to find. But with all these graphs,
> everything you found, it might be easier to find afterwards — easier to find other info,
> counterpart, maybe some little details.
>
> So I think this is how the skill should work. Maybe we could keep some things, but if needed we
> should revamp everything we need.
>
> Also, we should align it to how different researchers — AI researchers, or regular researchers,
> R&D researchers — and how different skills and different deep-search in AI works. But I think, as
> I told you, [we should] steal from other projects, other startups, other products. And check with
> our gathering-context skill — there's a lot of top sources in YouTube, articles, maybe
> repositories of other projects. We should use it as our source to make this skill, to make this
> whole pipeline.
>
> use get shit done skill, brainstorming, gathering context

## 2. On sources

> remember to use top sources yourself and give them to agents, top similar projects, but only true
> alpha, no noise or bullshit, our top yt channels in skills via yt dlp

> use our top sources, list me all yt channels in our gathering context skill and as I told you,
> graphs are only similarity/intuintion

## 3. The goal, restated — and the authorization to go drastic

> how is it going
> and as I told you if needed and ig it will be needed we will rewamp the whole skill set
> drastically, per our goal, make agents and coging agentic cli's SOTA at any kind of research
> use ALL our channels, ALL our top sources, videos, podcasts, transcripts, articles, researches,
> guides, workflows, pipelines from goated people, engineers, researchers at top companies,
> startups, research labs
> also use desktop/researchfms teardowns all at the same time via multiple agents per source

## 4. Decisions the owner made when asked

- **Run the system before redesigning it.** Chose: cheap arms *and* the full route — badresearch
  fast, a plain Claude+WebSearch session, and the full 19-stage route, blind-judged, in an isolated
  directory. Rationale given in the question and accepted: every cut is otherwise an unmeasured
  opinion, and the revamp would ship with no baseline.
- **Create this file.** Chose: "yes and save my words from this session start."

## 5. 2026-09-26 — the rebuild lost depth; research it again from scratch

Given after the rebuild branch (`feat/research-rebuild-slice-1`) was found unmerged. Pasted by the
owner, verbatim:

> We had a huge research before on how research actually works best — how to find genuinely quality
> information on any topic, the alpha, not marketing noise. A source's popularity doesn't always
> correlate with quality — look for popular and unpopular sources.
>
> Intuitively it resembles a graph database. Only intuitively — don't implement one.
>
> Do the research again from scratch, because that research seemed very weak to me. With
> gathering-context and the Twitter API: research how top researchers actually find research — how
> they get the top 1%, filter junk, get even the rarest information.
>
> Why a systematic approach? Because you're looking for interconnections between every piece of
> knowledge. The more that web grows, the easier it becomes to find new information. Broad-first,
> then dig deeper using what you already found.
>
> Parallel agents can do this, but they must pass their knowledge to each other as
> interconnections, so they don't find the same information twice.
>
> What I'm getting at: after we revamped Bad Research, it became simpler and smaller — but I'm
> afraid we lost quality. The previous version wasn't aligned to this direction, but it was deeper
> and broader. Yes, over-engineered, over-complicated somewhere; we lightened it — but I sense we
> lost quality. The skill we ended up with isn't enough for genuinely multi-step, multi-round
> research.
>
> My direction needs to be tested. On Twitter: only the best practitioners, founders, researchers —
> from the best research labs or top startups. The end state: aligned to the new direction, super
> high quality, and at the same time simple.

Annotation (no authority): this adds four things the earlier sections did not say — **popularity is
not quality, so sample the unpopular on purpose**; **broad FIRST, then deep**, stated as an order;
**parallel workers must hand each other what they found so nothing is found twice**; and **the
direction itself is a hypothesis to be tested against the best practitioners**, not a spec to obey.
It also states the regression the owner perceives: the merged skill is not enough for genuinely
multi-round research.

### On the form (2026-09-26, same session, verbatim)

> it may be pack of skills, like sequentiall skills or agents if needed, with references and other
> stuff we can use in skills, you can check, but the main point is quality and what we got as a result,
> but it might be 1 big skill, pack of skills and agents, etc etc etc

Annotation (no authority): the FORM is open — one skill, a pack of skills, sequential skills, agents,
references. The measure is the quality of the result. So a form is chosen by what a real run shows it
fixes, not by a preference for small or for simple.

---

## What this file BINDS — read as constraints, not as suggestions

1. **The goal is SOTA research for agentic CLIs**, not a better badresearch. Nothing in the current
   repo is preserved for sentiment. A drastic revamp of the whole skill set is explicitly authorized.
2. **Quality over economy.** "don't skimp" — twice. Do not propose the cheaper option because it is
   cheaper.
3. **Simpler if simpler is better** — the complaint is "a lot overcomplicated", but "simpler" is a
   means, never the goal. Do not trade capability for line count.
4. **The step-skills-don't-fire defect is a named, first-class bug.** "So it's first error."
5. **Research = multi-step accretion.** Each finding must make the next search better. A searcher
   searches for one thing; a researcher connects what he found and uses it to find the next thing.
6. **Counterpart-hunting is the explicit second half of the ask**, not an afterthought: "knowing a
   lot of things in your research also makes you find counterparts of your research... to be 100%
   sure."
7. **GRAPHS ARE AN ANALOGY, NOT A SPEC.** Stated twice, the second time as a correction:
   "graphs are only similarity/intuintion", and in the original, "graphs will be overkill for
   research". Do not build a knowledge graph on the strength of this file. What he is describing is
   interconnection and compounding reach — build whatever cheapest structure delivers that.
8. **Ground it in how real researchers at top companies/startups/labs actually work**, and steal
   from other projects, startups and products.
9. **Use the owner's own source lanes**: the 32 verified YouTube channels in
   `compound-v/references/channels.tsv` via `yt.sh` (yt-dlp), the `~/Desktop/researchfms` teardowns
   (407) and transcripts (41), `~/Desktop/guidesfm` articles (190) and x-guides (100). Multiple
   agents per source, in parallel. **Only true alpha — "no noise or bullshit."**
10. **Route through the kit**: get-shit-done, brainstorming, gathering-context.

## What this file does NOT yet contain — ask before assuming

- The transcript of the specific run that triggered "step-by-step skills are not working".
- Five real queries the owner actually asks this tool. **The only two preserved runs in the repo are
  "best tRPC patterns" and "engineering guides written by real founders" — both web-doc lookups,
  neither a literature question.** If those are representative, the scholarly/citation-graph lane is
  out of scope; if they are not, the corpus is scoped wrong. This is unresolved.
- What "overcomplicated" costs him concretely: token spend, wall-clock, cognitive load reading the
  chain, or bad reports. Nobody has priced it.
- One report he would call excellent and one he would call bad, with the reason.
