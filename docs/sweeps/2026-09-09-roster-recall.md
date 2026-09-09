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
