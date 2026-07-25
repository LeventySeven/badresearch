"""Stage-16 deterministic no-uncited-claim gate. Pure string + table, $0, no LLM.
Hard pass/fail: any non-trivial factual sentence that lacks a verifiable, verified
citation blocks ship. Extends hyperresearch R2 density (hooks.py:1126). dossier §5."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .anchors import AnchorStore
from .render import extract_citations

# Hedge-frame openers that exempt a sentence (dossier §5.1 allowlist).
_HEDGE_OPENERS = ("in general,", "broadly,", "generally,", "overall,")
# Meta / framing sentence stems that carry no [N].
_META_STEMS = ("this report", "this section", "this analysis", "we cover", "the following")
# A leading bold label on a verdict/summary line (`**Bottom line:**`, `**Key
# takeaway:**`, `**Verdict:**`). Stripped before classification so the label's
# capitalised words ("Bottom", "Line") don't read as a non-initial named entity and
# falsely flag an otherwise-trivial line ("**Bottom line:** cut.") as a factual claim
# (issue #18). A verdict line that DOES carry a real claim still flags on the residual
# text ("**Bottom line:** Vietnam exported 7M tonnes" keeps its number).
_LEADING_BOLD_LABEL = re.compile(r"^\s*\*\*[^*]+\*\*[:.]?\s*")
_NAMED_ENTITY = re.compile(r"\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b")
_NUMBER = re.compile(r"\d")
_COMPARATIVE = re.compile(
    r"\b(more|less|fewer|greater|higher|lower|larger|smaller|most|least|best|worst|"
    r"led|leading|highest|lowest|than|fastest|slowest)\b", re.IGNORECASE)
_CAUSAL_TEMPORAL = re.compile(
    r"\b(because|therefore|caused|causes|due to|results? in|since|after|before|"
    r"led to|drove|grew|fell|rose|declined|increased|decreased)\b", re.IGNORECASE)


@dataclass
class Finding:
    failure_mode: str   # uncited-claim | dangling-cite | unverified-cite
    severity: str       # critical | major | minor
    location: str       # the offending sentence
    recommendation: str


def strip_sources_section(report_md: str) -> str:
    """Drop everything from a `## Sources` (or `# References`) heading onward --
    the gate only judges the prose body (matches R2's exclusion)."""
    lines = report_md.splitlines()
    out: list[str] = []
    for line in lines:
        if re.match(r"^\s*#{1,6}\s+(sources|references)\b", line, re.IGNORECASE):
            break
        out.append(line)
    return "\n".join(out)


# A piece made up only of citation tokens (+ trailing punctuation) -- it belongs
# to the sentence it trails, not a sentence of its own.
_CITES_ONLY = re.compile(r"^\s*(?:\[\[[^\]]+\]\]|\[\d+\])(?:\s*(?:\[\[[^\]]+\]\]|\[\d+\]))*\s*[.;,]?\s*$")

# ── A-2: formatting-line skip set (false-positive guard) ─────────────────────
# A bold-only line is a pseudo-heading (`**Key Findings 2024**`), not a sentence.
_BOLD_ONLY = re.compile(r"^\*\*[^*].*\*\*$")
# A markdown table row / divider: starts (after optional indent) with a pipe.
_TABLE_ROW = re.compile(r"^\s*\|")
# A fenced-code delimiter line: ``` or ~~~ (optionally with a language tag).
_CODE_FENCE = re.compile(r"^\s*(?:`{3,}|~{3,})")
# A line whose entire visible content is one inline code span (`...`).
_CODE_SPAN_ONLY = re.compile(r"^\s*`[^`]+`\s*$")
# A line whose ENTIRE visible content is one or more bold spans (with optional
# trailing punctuation) — a formatting pseudo-heading fragment, not a factual
# sentence. Catches `**Important:**` and `**Key Findings 2024**` (the latter is
# also caught by _BOLD_ONLY's `^\*\*[^*].*\*\*$`; this is an explicit complement
# / belt-and-suspenders for G1).
_BOLD_SPAN_ONLY = re.compile(r"^\s*(?:\*\*[^*]+\*\*[.:]?\s*)+$")
# A leading list marker: a bullet (`-`/`*`/`+`) or an ordinal (`1.`/`1)`),
# stripped so a numbered item is ONE sentence (not the `1.` fragment + the rest).
_LIST_MARKER = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


def _is_formatting_line(line: str) -> bool:
    """True for structural chrome that carries no factual claim: bold-only
    pseudo-headings, markdown headings, table rows/dividers, lone inline code
    spans, and lines whose entire content is bold spans (G1 belt-and-suspenders).
    Code-fence handling is stateful and lives in `split_sentences`."""
    if line.startswith("#"):
        return True
    if _BOLD_ONLY.match(line):
        return True
    if _BOLD_SPAN_ONLY.match(line):
        return True
    if _TABLE_ROW.match(line):
        return True
    return bool(_CODE_SPAN_ONLY.match(line))


# A sentence piece that ENDS with one of these did not actually end a sentence — the
# trailing "." is an abbreviation / initial ("Aidan N.", "F.D.A.") or an ellipsis
# ("..."), not a terminator. split_sentences re-joins the spuriously split fragment
# forward, so the citation-less fragment before the real [N] is not flagged uncited.
_ABBREVIATIONS = (
    "dr", "mr", "mrs", "ms", "prof", "sr", "jr", "st", "vs", "etc", "al", "inc",
    "ltd", "co", "corp", "no", "nos", "fig", "eq", "vol", "pp", "ref", "cf",
    "approx", "rev", "gen", "sen", "gov", "rep",
)
_NON_TERMINAL_END = re.compile(
    r"(?:\.\.\.|…"                                        # ellipsis  ... or …
    r"|(?<![A-Za-z])[A-Za-z]\."                                # lone initial: "Aidan N.", "F.D.A."
    r"|(?<![A-Za-z])(?:" + "|".join(_ABBREVIATIONS) + r")\.)"  # common abbreviation
    r"$",
    re.IGNORECASE,
)


def split_sentences(text: str) -> list[str]:
    parts: list[str] = []
    in_code_fence = False
    for raw in text.splitlines():
        line = raw.strip()
        if _CODE_FENCE.match(line):
            # Toggle in/out of a fenced code block; the fence line itself is chrome.
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue  # source code, not prose -- never a factual sentence
        if not line or _is_formatting_line(line):
            continue
        # Strip a leading list marker so `1. Vietnam led ...` is one sentence,
        # not the spurious fragment `1.` split off by the ordinal's period.
        line = _LIST_MARKER.sub("", line, count=1).strip()
        if not line:
            continue
        line_parts: list[str] = []
        for piece in re.split(r"(?<=[.!?])\s+", line):
            piece = piece.strip()
            if not piece:
                continue
            # The "." that split this piece off was NOT a terminator — it was an
            # abbreviation/initial ("Aidan N.") or an ellipsis ("...") — so re-join
            # forward rather than leaving a citation-less fragment the uncited-gate
            # would flag as its own sentence (live-run finding).
            if line_parts and _NON_TERMINAL_END.search(line_parts[-1]):
                line_parts[-1] = f"{line_parts[-1]} {piece}"
            else:
                line_parts.append(piece)
        for piece in line_parts:
            # A trailing citation-only fragment (`. [[note-id]]`) is split off the
            # preceding sentence by the terminal period -- re-attach it so the
            # factual sentence keeps its citation (dossier §5.1 "in/adjacent to").
            if parts and _CITES_ONLY.match(piece):
                parts[-1] = f"{parts[-1]} {piece}"
            else:
                parts.append(piece)
    return parts


def is_factual_claim(sentence: str) -> bool:
    """A non-trivial factual claim: has a number, named entity, comparative/
    superlative, or causal/temporal assertion -- and is NOT a question, a
    meta-sentence, or a hedge-frame opener (dossier §5.1)."""
    # Strip a leading bold label (`**Bottom line:**` …) so it neither injects a
    # phantom sentence-initial entity nor hides the real opener (issue #18).
    s = _LEADING_BOLD_LABEL.sub("", sentence.strip(), count=1).strip()
    low = s.lower()
    if not s:
        return False
    if s.endswith("?"):
        return False
    if any(low.startswith(o) for o in _HEDGE_OPENERS):
        return False
    if any(low.startswith(m) for m in _META_STEMS):
        return False
    # Strip citation tokens before scanning for entities (so [[note-id]] isn't an entity).
    bare = re.sub(r"\[\[[^\]]+\]\]|\[\d+\]", "", s)
    if _NUMBER.search(bare):
        return True
    if _COMPARATIVE.search(bare):
        return True
    if _CAUSAL_TEMPORAL.search(bare):
        return True
    # Named entity that isn't merely the sentence-initial capital.
    ents = [m.group(0) for m in _NAMED_ENTITY.finditer(bare)]
    non_initial = [e for e in ents if not bare.lstrip().startswith(e)]
    return len(non_initial) >= 1


def no_uncited_claim_gate(report_md: str, anchors: AnchorStore) -> list[Finding]:
    findings: list[Finding] = []
    body = strip_sources_section(report_md)
    for sent in split_sentences(body):
        if not is_factual_claim(sent):
            continue
        cites = extract_citations(sent)
        if not cites:
            findings.append(Finding(
                "uncited-claim", "critical", sent,
                "Non-trivial factual sentence carries no citation. Add a vault cite or hedge/cut."))
            continue
        for c in cites:
            anchor = anchors.get(c)
            if anchor is None:
                findings.append(Finding(
                    "dangling-cite", "critical", sent,
                    f"Citation {c} resolves to no claim_anchor -- remove or repoint."))
                continue
            if anchor.verified != 1:
                # Severity depends on the recorded verify_score. A span that
                # explicitly does NOT support the claim (score < PARTIAL_LOW)
                # blocks ship as critical (G4 gate tightening, round2-citation
                # §4); the partial band ([PARTIAL_LOW, SUPPORTED_FLOOR)) and the
                # unscored case stay major.
                from .verifier import PARTIAL_LOW
                if anchor.verify_score is not None and anchor.verify_score < PARTIAL_LOW:
                    severity = "critical"
                    rec = (
                        f"Citation {c} verify_score={anchor.verify_score:.2f} < {PARTIAL_LOW} "
                        f"-- span explicitly does not support the claim. Drop or reground.")
                else:
                    severity = "major"
                    rec = (
                        f"Citation {c} was not confirmed by the CitationVerifier -- re-run Tier B or hedge.")
                findings.append(Finding("unverified-cite", severity, sent, rec))
            # Citation-drift WARN (non-blocking) — applies to ANY resolved anchor,
            # incl. the keyless whole-body verified=1 seed the older logic waves through.
            drift = _citation_drift_finding(sent, c, anchor)
            if drift is not None:
                findings.append(drift)
    return findings


_URL_RE = re.compile(r"https?://[^\s<>\"'\)\]\}]+")


def _canonical_url(url: str) -> str:
    """Normalize for comparison: drop trailing punctuation and a trailing slash.

    A URL written mid-prose picks up the sentence's punctuation — `(https://x/y).`
    — and must still match the `https://x/y` we stored.
    """
    return url.rstrip(".,;:!?").rstrip("/")


def ungrounded_url_gate(report_md: str, known_urls: set[str]) -> list[Finding]:
    """Flag `http(s)://` URLs in the PROSE that we never actually fetched.

    The uncited gate validates `[N]` markers against claim_anchors, but a bare
    URL written into a sentence is unchecked: "according to
    https://example.com/fake-study [3]" satisfies the uncited gate (the sentence
    IS cited) while the URL itself is invented. This closes that hole.

    Adapted from Silver's `ungroundedUrlWarning` — fail loud when the grounding
    mechanism did not engage, instead of trusting a prompt that asks the model
    not to fabricate. Deterministic and KEYLESS: pure string comparison against
    the URLs already in the vault, no model call and no network.

    MINOR, deliberately: a URL can legitimately be the SUBJECT of the research
    ("the breach at https://victim.example/login"), so blocking would punish a
    report about a website. `uncited_gate_cmd` blocks on critical+major and
    routes `minor` to its non-blocking `warnings` channel — the same treatment
    the citation-drift WARNING already gets — so this is VISIBLE to the
    orchestrator and the polish pass without failing the run. Each distinct URL
    is reported once, however often it recurs.
    """
    known = {_canonical_url(u) for u in known_urls}
    body = strip_sources_section(report_md)
    findings: list[Finding] = []
    seen: set[str] = set()
    for raw in _URL_RE.findall(body):
        url = _canonical_url(raw)
        if not url or url in known or url in seen:
            continue
        seen.add(url)
        findings.append(Finding(
            "ungrounded-url", "minor", raw,
            f"URL {raw} appears in the report but no fetched source has it. "
            f"Either it was fabricated, or the source was never grounded into "
            f"the vault -- verify it, cite the real source, or cut the URL.",
        ))
    return findings


def gate_blocks_ship(findings: list[Finding]) -> bool:
    """A run does not ship with any open `critical` finding (dossier §5.2)."""
    return any(f.severity == "critical" for f in findings)


# ── E9: keyless semantic span support-check — lexical pre-filter ──────────────
# STEAL_LIST #4 (OpenAI `【ref†L42-L58】`): bind a claim to a SPECIFIC supporting
# span, not merely "a citation exists." On the keyless path the no-op NLI passes a
# *paraphrased* claim regardless of whether the cited span supports it. The cheap
# lexical pre-filter below bounds the cost of catching that: claim ≈ quote (overlap
# >= CLAIM_QUOTE_OVERLAP_SKIP) → accept on byte-identity, skip the host judge ($0);
# below it (a genuine paraphrase) → route to the batched host-model entailment judge.

# A claim whose token set is >= this fraction contained in the cited span is treated
# as "≈ the quote" — verbatim/near-verbatim. NOTE: this band is NOT covered by Tier-A:
# Tier-A byte-identity checks span-vs-body integrity (the quoted_support still sits at
# [char_start:char_end] with a matching SHA), NOT report-sentence-vs-span fidelity. The
# old residual risk in this band — a >=0.8-overlap report sentence that flipped a number
# or negation ("grew 12%" vs a span saying "grew 21%") — is now closed KEYLESSLY by
# `numeric_or_negation_mismatch` below: such a pair is denied the shortcut and escalated
# to the batched host-model judge (the `[local]`/keyed CrossEncoderNLI lane is still the
# upgrade for the harder semantic-paraphrase cases). On the keyless+host path we accept
# the near-verbatim band ONLY when numbers + negation agree, to bound host-token cost.
# dossier §2.2.
CLAIM_QUOTE_OVERLAP_SKIP = 0.8

_WORD_RE = re.compile(r"[a-z0-9]+")
# Stop tokens are stripped before overlap so two sentences are not judged "the same"
# merely for sharing "the/of/in"; this makes the ratio track CONTENT overlap.
_OVERLAP_STOP = frozenset({
    "the", "a", "an", "of", "to", "in", "on", "at", "for", "and", "or", "but",
    "is", "are", "was", "were", "be", "been", "by", "with", "as", "that", "this",
    "these", "those", "it", "its", "from", "into", "over", "under", "than", "then", "so",
})


def _content_tokens(text: str) -> set[str]:
    """Lowercased alphanumeric content tokens (stop words removed) — the unit the
    claim↔quote overlap ratio is computed over."""
    return {t for t in _WORD_RE.findall((text or "").lower()) if t not in _OVERLAP_STOP}


def claim_quote_overlap(claim: str, quote: str) -> float:
    """Fraction of the CLAIM's content tokens that also appear in the cited QUOTE
    (token-containment, asymmetric on purpose: the question is "is the claim covered
    by the span?", not "are the two equal in length?"). 1.0 = every claim word is in
    the quote (verbatim/near-verbatim); ~0.0 = the claim paraphrases something the
    span never says. An empty claim trivially overlaps (nothing to support)."""
    c = _content_tokens(claim)
    if not c:
        return 1.0
    q = _content_tokens(quote)
    return len(c & q) / len(c)


# ── Citation-drift WARN — phase 1 of "bind, not count" ────────────────────────
# The keyless gate seeds whole-body anchors verified=1, so today a cite passes as
# long as the note FILE exists — it never checks the note is ON-TOPIC. This adds a
# NON-BLOCKING signal: when a factual claim's content tokens barely appear anywhere
# in the cited note body, the cite is probably pointing at the wrong source (drift).
# It is `minor` on purpose — it must NOT block ship (a block-flip is phase 2, after
# located-span binding via build_from_claims + real-run validation of the false-
# positive rate). Conservative thresholds keep noise low: only egregious drift, on a
# substantial cited body, for a claim with enough content to judge.
CITATION_DRIFT_WARN_THRESHOLD = 0.2   # < 20% of the claim's content tokens in the cited note
_DRIFT_MIN_CLAIM_TOKENS = 4           # skip trivial/short claims
_DRIFT_MIN_SPAN_CHARS = 200           # only when the cited span is a substantial body


def _citation_drift_finding(sentence: str, cite: str, anchor: object) -> Finding | None:
    """Non-blocking drift signal: the cited note shares almost none of the claim's
    content tokens — probably the wrong source. Returns a `minor` Finding or None.

    Deliberately does not depend on the CitationVerifier having run, so it catches drift
    on the keyless whole-body-seed path where every anchor is stamped verified=1."""
    quote = getattr(anchor, "quoted_support", "") or ""
    if len(quote) < _DRIFT_MIN_SPAN_CHARS:
        return None
    if len(_content_tokens(sentence)) < _DRIFT_MIN_CLAIM_TOKENS:
        return None
    if claim_quote_overlap(sentence, quote) >= CITATION_DRIFT_WARN_THRESHOLD:
        return None
    pct = int(CITATION_DRIFT_WARN_THRESHOLD * 100)
    return Finding(
        "citation-drift", "minor", sentence,
        f"Citation {cite} note shares <{pct}% of this claim's content words -- likely "
        f"citation drift (wrong source). Verify the note actually supports the claim, or "
        f"repoint the cite. (Non-blocking warning.)")


# ── Numeric / negation / directional divergence guard (audit 2026-06-01 row 6;
#    extended 2026-06-02 with the antonym axis) ──────────────────────────────────
# The >=0.8-overlap "near-verbatim -> ENTAILMENT, skip the judge" shortcut above used
# to admit a claim that FLIPPED a number, date, negation, OR direction while keeping
# high lexical overlap ("grew 12%" vs a span saying "grew 21%"; "does not cause" vs
# "causes"; "grew 2.1%" vs "declined 2.1%"). That was the keyless flip gap the docstring
# above deferred to the [local] lane. This deterministic, keyless guard closes all three
# axes: when the claim carries a number/date the span lacks, a different negation
# polarity, OR a directional/antonym flip relative to the span, the near-verbatim
# shortcut is DENIED so the pair escalates to the batched host-model judge (JUDGE_SYSTEM
# already mandates exact number matching and flags opposites). Conservative by design —
# it only ever *adds* an escalation (one host call), never silences one, so it cannot
# mask a real support.
_NUM_RE = re.compile(r"\d[\d,]*\.?\d*")
_NEGATION = frozenset({
    "not", "no", "never", "none", "cannot", "without", "neither", "nor",
    "fails", "fail", "failed", "lacks", "lack", "absent", "unable",
})

# ── Directional / antonym divergence guard (audit 2026-06-02) ──────────────────
# The numeric+negation guard above misses a same-number, same-polarity DIRECTIONAL
# flip: "GDP grew 2.1%" vs a span saying "GDP declined 2.1%" (the digit 2.1 sits on
# both sides; neither negates) used to slip through the >=0.8-overlap near-verbatim
# shortcut and be rubber-stamped as ENTAILMENT — WRONG. Likewise "ratified by all" vs
# "rejected by all". This deterministic, keyless lexicon of OPPOSED terms closes that
# hole: if one side contains a term whose opposite appears on the OTHER side (and that
# opposite is NOT also present on the first side), the pair is flagged and escalated to
# the batched host-model judge. Conservative + symmetric, exactly like the existing
# guard — it only ever ADDS an escalation; it can never silence a real support. The
# "opposite not also present on the first side" rule is the false-positive guard: a
# pair with the SAME antonym on both sides (both say "rose") never flags.
_ANTONYM_PAIRS: tuple[tuple[str, str], ...] = (
    ("grew", "declined"),
    ("grew", "shrank"),
    ("rose", "fell"),
    ("increased", "decreased"),
    ("gained", "lost"),
    ("up", "down"),
    ("higher", "lower"),
    ("more", "less"),
    ("ratified", "rejected"),
    ("approved", "denied"),
    ("accepted", "rejected"),
    ("confirmed", "denied"),
    ("positive", "negative"),
    ("supports", "opposes"),
    ("improved", "worsened"),
    ("expanded", "contracted"),
    ("surplus", "deficit"),
)
# Flattened lookup: term -> frozenset of its opposite terms. A term may oppose more
# than one word (e.g. "rejected" opposes both "ratified" and "accepted"), so the value
# is a set, populated symmetrically from _ANTONYM_PAIRS.
_ANTONYMS: dict[str, frozenset[str]] = {}
for _a, _b in _ANTONYM_PAIRS:
    _ANTONYMS[_a] = _ANTONYMS.get(_a, frozenset()) | {_b}
    _ANTONYMS[_b] = _ANTONYMS.get(_b, frozenset()) | {_a}
del _a, _b


def directional_antonym_mismatch(claim: str, quote: str) -> bool:
    """True when CLAIM and QUOTE disagree on a DIRECTIONAL/ANTONYM term: one side
    contains a term (e.g. "grew") whose opposite (e.g. "declined") appears on the OTHER
    side and is NOT also present on the first side. Catches same-number, same-polarity
    flips the numeric/negation guard misses ("grew 2.1%" vs "declined 2.1%", "ratified
    by all" vs "rejected by all"). Keyless + deterministic + conservative: it only ever
    signals an escalation, never a support.

    The "opposite not also on the first side" rule is the false-positive guard — when
    the SAME antonym sits on both sides (both say "rose") or one sentence names both
    poles, no flip is signalled; only a genuine cross-side flip flags."""
    c_tokens = frozenset(_WORD_RE.findall((claim or "").lower()))
    q_tokens = frozenset(_WORD_RE.findall((quote or "").lower()))
    for term in c_tokens:
        opposites = _ANTONYMS.get(term)
        if opposites and (opposites & q_tokens) and not (opposites & c_tokens):
            return True
    for term in q_tokens:
        opposites = _ANTONYMS.get(term)
        if opposites and (opposites & c_tokens) and not (opposites & q_tokens):
            return True
    return False


def _numbers(text: str) -> set[str]:
    """Bare numeric cores in `text`, commas + trailing dots stripped so '1,200' ->
    '1200' and '21%' -> '21' (the '%' sits outside the match)."""
    out: set[str] = set()
    for m in _NUM_RE.findall(text or ""):
        norm = m.replace(",", "").rstrip(".")
        if norm:
            out.add(norm)
    return out


def _has_negation(text: str) -> bool:
    low = (text or "").lower()
    if re.search(r"n't\b", low):  # contractions (doesn't / isn't / won't ...)
        return True
    return any(t in _NEGATION for t in _WORD_RE.findall(low))


def numeric_or_negation_mismatch(claim: str, quote: str) -> bool:
    """True when the CLAIM and QUOTE diverge on any of three deterministic axes, all
    of which DENY the near-verbatim ENTAILMENT shortcut so the pair is escalated to the
    host judge instead of rubber-stamped:

      1. NUMBER/DATE: the claim carries a number the quote does not contain.
      2. NEGATION: the two differ in negation polarity (one negates, the other doesn't).
      3. DIRECTION/ANTONYM: one side flips a directional/antonym term relative to the
         other (e.g. "grew" vs "declined", "ratified" vs "rejected") — a same-number,
         same-polarity contradiction the first two axes miss (see
         `directional_antonym_mismatch`).

    Keyless + deterministic + conservative: it only ever ADDS an escalation, never
    silences a real support, so callers in verifier.py need no change."""
    cn = _numbers(claim)
    if cn and not cn <= _numbers(quote):
        return True
    if _has_negation(claim) != _has_negation(quote):
        return True
    return directional_antonym_mismatch(claim, quote)
