# Recall test — "find all the great AI researchers, including the obscure"

The owner named this as the shape of work he actually does, and it is a regime the depth machinery does
not cover. Three passes over one identical population definition, by three different **methods**, run
blind to each other so the overlaps mean something.

## Pass A — local corpus, offline, rank-blind

`local | files listed 723 | names extracted 4,013 | cut line: product/growth/design essayists, VCs,
journalists, hosts, corporate bylines, and moderators with no artifact of their own`

939 individually listed with `path:line`; **3,074 more in one file**, counted with a stated extraction
rule rather than pasted.

### It caught a defect in my own instruction, and it is the finding of the run

The brief — and my shipped lane recipe, and `lane-probes.sh`, and the corpus map that loads into every
session — all globbed `TRANSCRIPTS_*.md`. That is a **prefix** glob, and the directory does not only use
that prefix. Measured:

| glob | files |
|---|---:|
| `TRANSCRIPTS_*.md` | 41 |
| `*TRANSCRIPT*.md` | **42** |

The dropped file is `ICML_TRANSCRIPTS.md`: **23,000 lines, 761 `**Authors:**` rows, ~3,074 distinct
researcher names — more than the other 41 files hold combined.** For this question the glob was hiding
77% of the enumerable population, and the reader flagged it rather than silently obeying the brief.

**41 looked right.** It matched the number written in the corpus map, so every prior run confirmed it.
A glob that returns a plausible count is the worst kind of wrong. Anchor on the distinctive substring,
never on the prefix somebody used first. Fixed in the lane recipe, the probe script, and the corpus map.

### Structural blindness of this method — checked, and one claim corrected

- **Anthropic-shaped, and worse than the reader said.** Lab mentions across the 190-article manifest:
  **Anthropic 32, OpenAI 14, DeepMind 5, Google 2, Meta 2.** Anthropic is 58% of lab-attributable
  articles, more than double the next. A DeepMind or Meta researcher of equal standing to an enumerated
  Anthropic one is very likely missed — not because they are less good, but because this corpus was
  assembled by someone working with Claude.
- **The obscure tail is concentrated in one file — but the reader overstated it, and I checked.** The
  claim was that removing `TRANSCRIPTS_COHERE_LABS.md` (47 talks) collapses the long tail to near zero.
  Measured: Telefónica and Potsdam appear in **that file and nowhere else**; MBZUAI and UBC appear in 2
  other files; Mila appears in 7 others (though 175 mentions there against a handful elsewhere); Yale
  and Brown appear *more* often elsewhere (8 and 14 files). So: **single-sourced for the smallest
  institutions, concentrated but not exclusive for the rest.** The dependency is real and narrower
  than claimed.
- **English-language, US/UK/EU.** DeepSeek reaches the corpus as one name from a BibTeX; Moonshot as
  three. A researcher publishing primarily in Chinese, Japanese, Korean or Russian is invisible except
  through an English arXiv byline.
- **Cannot see anyone who only publishes papers.** Every lane except the ICML file is *curated media* —
  essays someone chose, threads someone mirrored, talks someone captioned. A prolific researcher with
  no public presence appears only via ICML 2026: one venue, one year, doing all the work of
  representing normal academic publishing.
- **~40 people exist only as a first name or a caption garble** ("Nana", "Shrimai", "Jeff Don" for
  Jiafei Duan, "Adeep" for Ekdeep Singh Lubana). Offline they are unresolvable by construction — which
  is a genuine overlap opportunity for the other two passes.
- **407 teardowns produced ~60 names, clustered in five files.** The other ~400 are product RE with no
  people in them. A researcher at a company nobody tore down is invisible.

## Pass B — live web, silver only

`web | entry points 46 attempted / 29 productive | names 1,663 unique | cut line: unlinked directory
rows with no observed artifact, titled ops/finance/comms staff, journalists, collective bylines`

**It never invoked WebSearch.** Every name came from a page opened with silver, so this pass is
roster-based rather than rank-ordered — which makes it more independent of pass A than a search-ranked
pass would have been, and is why the pair is usable at all.

### Its own diagnosis, and it is the sharpest sentence of the run

> *The live web surfaces **institutions, not people**. A DeepMind research scientist who mentors nobody
> and organises nothing is invisible to me, no matter how good their papers are.*

Every name it found came from an organisation that publishes a roster or a committee that publishes a
list. So the labs with **no enumerable staff directory** — DeepMind, OpenAI, Meta FAIR, Microsoft
Research, Mistral, xAI, Thinking Machines, Anthropic — are reachable only *sideways*, as a MATS mentor,
a workshop organiser, or a blog first-author. That blind spot lands precisely on the highest-output
population.

Four more, each named with the evidence:
- **The person whose only artifact is a paper.** Main-track proceedings run to tens of thousands of
  authors behind paginated JS-rendered sites; it could not enumerate them and said so.
- **Talks and podcasts: zero.** `machinelearningstreettalk.com` was refused by silver's own egress
  policy — *the entire podcast-guest lane is closed to this method*, and that is a BLOCKED state, not
  an empty one.
- **Non-Anglophone and Global South.** Both deliberate corrections failed: Masakhane 404, Deep Learning
  Indaba connection-timeout twice. **Unmeasured, not empty**, and reported that way.
- **Anyone who left.** Team pages render the present tense. A person who wrote a field-defining essay
  in 2019 and then left research is dropped by every roster-based entry point — and still meets the
  population definition exactly.

### Two things it did that are worth more than the roster

It cut **156 Ai2 directory rows** for having no observed artifact, then **listed them anyway**, naming
Iz Beltagy, Sewon Min, Tim Dettmers, Pradeep Dasigi, Arman Cohan among them and writing: *"read it as
my false-negative, not their false-positive."* That is an exclusion made auditable instead of silent.

And it found **two defects in its own extraction** — a parallel pass that interleaved output and
scrambled the post↔author mapping, and an off-by-one that captured affiliation lines instead of names.
Both were caught **by reading the output, not by a tool erroring.**

## The number, after two of three passes

| | |
|---|---:|
| A — ICML authors, extracted with A's own published rule (verified: 3,059 vs its claimed ~3,074) | 3,059 |
| B — live-web roster | 1,663 |
| overlap, sampled 31/106 across B's blocks | ≈ 486 (29.2%) |
| **estimated population** | **≈ 10,500** |
| held (union) | ≈ 4,236 |
| **coverage** | **≈ 40%** |

**And every error in it points the same way.** The sampled overlap was tested only against A's ICML
slice, not its other 939 names, so `m` is a lower bound → the population is an upper bound → coverage
is a lower bound. But A and B are also **not fully independent** — both over-weight Anglophone
safety/interpretability labs — and dependence inflates the overlap, which shrinks the population, which
*inflates* coverage. So ~40% is the optimistic reading of a lower bound, on a population definition
that is itself Anglophone-shaped.

Two independent methods, both run to exhaustion of their own entry points, hold well under half of what
they jointly imply exists. That is the honest answer to "how good is our research at this", and no
precision gate in the kit would have surfaced it.
