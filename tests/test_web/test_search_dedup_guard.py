"""Task 5: within-run dedup guard in retrieve_until_good.

A query already fanned out this run is skipped rather than re-issued. The loop's
injected `fan_out` is opaque (`list[str] -> list[WebResult]`), so the query string
is the dedup key available at this seam (the plan's ideal (provider, args) key is
not visible here — provider routing happens inside fan_out). Style matches
test_search_loop.py: injected callables, no network."""

from __future__ import annotations

from bad_research.web.base import WebResult
from bad_research.web.search.base import KeylessSearchConfig
from bad_research.web.search.loop import retrieve_until_good


def _pool(domain: str, scores: list[float]) -> list[WebResult]:
    out = []
    for i, s in enumerate(scores):
        r = WebResult(url=f"https://{domain}/{i}", title=f"{domain}-{i}", content="c")
        r.metadata["score"] = s
        out.append(r)
    return out


def test_reissued_query_across_rounds_is_skipped():
    # Round 1 issues [q1, q2]; the reformulation re-proposes q2 (a duplicate) plus
    # a new q3. The guard must skip q2 the second time — fan_out sees it once, and
    # round 2 only gets the genuinely new q3.
    received: list[list[str]] = []

    def expand(q, findings=None, gaps=None):
        # `findings is not None` => this is the reformulation call (round 2+).
        return ["q2", "q3"] if findings is not None else ["q1", "q2"]

    def fan_out(queries):
        received.append(list(queries))
        # fresh domain each call (no saturation), all < 0.70 (quality never fires)
        # so the loop is forced to reformulate into a second round.
        return _pool(f"d{len(received)}", [0.1, 0.1])

    def rerank(question, pool):
        return pool

    cfg = KeylessSearchConfig(max_rounds=2)
    retrieve_until_good("question", cfg=cfg, expand=expand,
                        fan_out=fan_out, rerank=rerank)

    flat = [q for call in received for q in call]
    assert flat.count("q2") == 1, "the re-issued query must be fanned out only once"
    assert received[0] == ["q1", "q2"]
    assert received[1] == ["q3"], "round 2 must skip the already-issued q2"


def test_within_round_duplicate_query_is_collapsed():
    # A single expand that returns the same query twice must fan it out once.
    received: list[list[str]] = []

    def fan_out(queries):
        received.append(list(queries))
        return _pool("only", [0.9])  # clears 0.70 -> stop after round 1

    retrieve_until_good(
        "question",
        cfg=KeylessSearchConfig(max_rounds=1),
        expand=lambda q, **kw: ["dup", "dup", "other"],
        fan_out=fan_out,
        rerank=lambda question, pool: pool,
    )
    assert received == [["dup", "other"]], "within-round duplicate must be collapsed"


def test_total_overlap_reformulation_preserves_best_effort():
    # Regression: round 1 finds a partial passing set (< min_pass_fraction, so the
    # loop reformulates), but the reformulation re-proposes ONLY already-issued
    # queries. _dedup_queries then returns [] — the loop must return round 1's
    # best-effort `passing`, NOT drop it to [] by fanning out an empty query list.
    calls = {"n": 0}

    def expand(q, findings=None, gaps=None):
        return ["q1"]  # the reformulation re-proposes the same single query

    def fan_out(queries):
        calls["n"] += 1
        return _pool("d", [0.9, 0.1, 0.1, 0.1])  # 1/4 = 25% < 30% -> forces reformulate

    trace: dict = {}
    out = retrieve_until_good(
        "question",
        cfg=KeylessSearchConfig(max_rounds=3),
        expand=expand,
        fan_out=fan_out,
        rerank=lambda question, pool: pool,
        trace=trace,
    )
    assert len(out) == 1, "best-effort passing must be preserved, not dropped to []"
    assert trace["stopped_reason"] == "exhausted"
    assert calls["n"] == 1, "must NOT fan_out an empty query list on the exhausted round"
