"""Reuse what is already here: the fixed web prefilter FIRST, the accreting filter on top.

`bad_research/quality/prefilter.py` has shipped for a long time and does the
cold-start job well **on URLs** — measured: it scores a content farm at 3
signals, arXiv at 0, and tiers arXiv as `reference`. What it cannot do is
accrete: the regexes and the domain table are fixed, so it knows exactly as much
on run 500 as on run 1.

And measured the other way, it has no reach outside the web lane at all: on
`Tim Dettmers | Allen Institute for AI`, on a teardown filename, on a transcript
section heading, it returns seo=0 / tier=blog every time — the items the corpus
lanes actually screen are not URLs.

So the two are complementary and belong in one cascade, which is also the shape
the IR literature converges on: a cheap fixed filter first, an expensive or
learned one only on what survives.

The order matters and is the point. The fixed rules cost nothing and never
improve; the learned ones cost decisions and compound. Running the free one
first means the accreting filter only ever spends its decisions on candidates
that were not already obviously junk.
"""
from __future__ import annotations

from bad_research.checks.cascade import cascade_screen
from bad_research.checks.discriminate import Decision, Discriminator

FARM = "https://top10bestaitools.com/best-10-ai-tools | Top 10 BEST AI Tools You NEED! (#7 will shock you)"
ARXIV = "https://arxiv.org/abs/2501.18539 | ARM: Can we Retrieve Everything All at Once?"
BLOGGY = "https://someblog.dev/p/retrieval | recruiting coordinator writes about hiring"


def test_the_fixed_web_filter_catches_junk_the_learned_one_has_never_seen():
    """Cold start: zero decisions, and the farm still goes."""
    r = cascade_screen([FARM, ARXIV], Discriminator())
    assert FARM in [c.item for c in r.rejected]
    assert "seo" in [c.because for c in r.rejected if c.item == FARM][0].lower()
    assert ARXIV in [c.item for c in r.kept]


def test_the_learned_filter_catches_what_the_fixed_one_cannot_see():
    """The blog URL is clean by every web signal; only accumulated decisions
    reject it, and only because this run learned what it is looking for."""
    d = Discriminator()
    for n in ("X | recruiting coordinator", "Y | events coordinator", "Z | hiring coordinator"):
        d.record(Decision(n, "reject", "ops role"))
    d.record(Decision("W | first-author retrieval paper", "accept", "artifact"))
    fixed_only = cascade_screen([BLOGGY], Discriminator())
    both = cascade_screen([BLOGGY], d)
    assert BLOGGY in [c.item for c in fixed_only.kept], "web signals see nothing wrong"
    assert BLOGGY in [c.item for c in both.rejected], "the learned layer does"


def test_the_cascade_reports_WHICH_layer_made_each_cut():
    d = Discriminator()
    for n in ("X | recruiting coordinator", "Y | events coordinator"):
        d.record(Decision(n, "reject", "ops role"))
    d.record(Decision("W | first-author paper", "accept", "artifact"))
    r = cascade_screen([FARM, BLOGGY, ARXIV], d)
    layers = {c.item: c.because.split(":")[0] for c in r.rejected}
    assert layers[FARM].startswith("web-prefilter")
    assert layers[BLOGGY].startswith("learned")
    assert r.by_layer["web-prefilter"] == 1 and r.by_layer["learned"] == 1


def test_a_non_url_item_skips_the_web_layer_instead_of_being_scored_zero():
    """Measured: the prefilter returns seo=0/tier=blog for every non-URL item, so
    running it there is not a clean pass — it is a layer that cannot see. Say so
    rather than banking a free 'kept'."""
    r = cascade_screen(["Tim Dettmers | Allen Institute for AI"], Discriminator())
    assert r.by_layer.get("web-prefilter-skipped") == 1


def test_the_free_layer_runs_first_so_decisions_are_not_spent_on_obvious_junk():
    d = Discriminator()
    for n in ("X | recruiting coordinator", "Y | events coordinator"):
        d.record(Decision(n, "reject", "ops"))
    d.record(Decision("W | first-author paper", "accept", "artifact"))
    r = cascade_screen([FARM], d)
    assert r.by_layer["web-prefilter"] == 1
    assert r.by_layer.get("learned", 0) == 0, "the learned layer never had to look at it"


def test_a_canary_the_WEB_layer_kills_is_reported_dead():
    """The canary measures the composed filter, not its second half.

    Before this, the canary verdict came from `learned.screen`, which never sees
    what the web regex already cut. A known-good URL that tripped the SEO rule
    was therefore reported as "not in the pool, tested nothing" and the cascade
    printed a clean UNMEASURED — the one state that must never hide a kill.
    """
    from bad_research.checks.cascade import cascade_screen
    from bad_research.checks.discriminate import Discriminator

    canary = ("https://top10bestaitools.com/ai-research "
              "Top 10 Best AI Tools for Research in 2026: The Ultimate Guide")
    d = Discriminator(canaries={canary})
    report = cascade_screen([canary, "https://arxiv.org/abs/2501.18539"], d)

    assert report.safe is False, report.caveat
    assert [c.item for c in report.canaries_killed] == [canary]
    assert "web-prefilter" in report.canaries_killed[0].because
    assert "web-prefilter" in report.caveat, "the caveat must name the layer that killed it"


def test_the_cascade_command_runs_and_exits_1_on_a_dead_canary(tmp_path):
    """Wired, not merely importable — the library-only version was the gap."""
    import subprocess
    import sys

    junk = ("https://top10bestaitools.com/ai-research "
            "Top 10 Best AI Tools for Research in 2026: The Ultimate Guide")
    (tmp_path / "cands.txt").write_text(f"{junk}\nhttps://arxiv.org/abs/2501.18539\n")
    (tmp_path / "canaries.txt").write_text(f"{junk}\n")

    r = subprocess.run(
        [sys.executable, "-m", "bad_research", "cascade",
         "--candidates", str(tmp_path / "cands.txt"),
         "--canaries", str(tmp_path / "canaries.txt")],
        capture_output=True, text=True,
    )
    assert r.returncode == 1, r.stdout + r.stderr
    assert "CANARY DEAD" in r.stdout
