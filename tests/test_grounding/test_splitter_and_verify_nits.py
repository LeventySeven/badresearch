"""Two grounding nits surfaced by the live /bad-research run:

1. The uncited-gate sentence splitter over-split on abbreviations / initials
   ("Aidan N.") and ellipses ("...") — the citation-less fragment before the real
   `[N]` got flagged as an uncited sentence. split_sentences must re-join those.
2. `bad verify-citations` was a no-op on the numeric-`[N]` + `## Sources` style: it
   only knew note-id anchors, so `[1]/[2]` never bound and it returned {"results": []}.
   A `--note-bodies/--sources` map (as the uncited-gate already accepts) must let it
   resolve `[N]` to the N-th source (ordinal-seeded store).
"""

from __future__ import annotations

import json

from bad_research.cli.research import _verify_report
from bad_research.grounding.gate import split_sentences


# ── Nit 1: split_sentences ───────────────────────────────────────────────────
def test_split_keeps_single_letter_initial_intact():
    # "Aidan N. Gomez" must stay ONE sentence — not a bare "…Aidan N." fragment.
    out = split_sentences("Vaswani, Aidan N. Gomez, et al. wrote the paper [1].")
    assert len(out) == 1, out
    assert "[1]" in out[0]


def test_split_keeps_ellipsis_intact():
    out = split_sentences("The result was surprising ... and it held up [2].")
    assert len(out) == 1, out


def test_split_keeps_common_abbreviations_intact():
    out = split_sentences("Approved by the F.D.A. in 2019 per the filing [3].")
    assert len(out) == 1, out


def test_split_still_splits_real_sentence_boundaries():
    # a genuine terminator must STILL split — the merge only rejoins false positives.
    out = split_sentences("The sky is blue [1]. Water is wet [2].")
    assert len(out) == 2, out


# ── Nit 2: verify-citations binds numeric [N] via a sources map ───────────────
def test_verify_citations_binds_numeric_n_with_sources(tmp_path):
    report = tmp_path / "report.md"
    report.write_text("# Q\n\nThe sky is blue [1]. Water is wet [2].\n", encoding="utf-8")
    sources = tmp_path / "sources.json"
    sources.write_text(
        json.dumps({"n1": "The sky is blue.", "n2": "Water is wet."}), encoding="utf-8"
    )
    # Before the fix this returned [] (no-op — [N] never bound). Now the ordinal-seeded
    # store resolves [1]->1st source, [2]->2nd, so the verifier actually processes them.
    results = _verify_report(str(report), "tag", note_bodies_path=str(sources))
    assert results, "numeric [N] must bind to the ordinal-seeded store, not be a no-op"
    assert {"1", "2"} & {r.get("anchor_id") for r in results}


def test_verify_citations_without_sources_is_unchanged(tmp_path, monkeypatch):
    # No vault (chdir to an empty dir so Vault.discover finds nothing), no sources ->
    # still an empty, non-crashing result (the no-op contract is preserved).
    monkeypatch.chdir(tmp_path)
    report = tmp_path / "report.md"
    report.write_text("# Q\n\nThe sky is blue [1].\n", encoding="utf-8")
    assert _verify_report(str(report), "tag") == []
