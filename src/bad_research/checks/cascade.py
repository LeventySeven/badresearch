"""One screen, two layers: the fixed web prefilter first, the accreting filter on top.

**Reuse before rebuild.** `bad_research/quality/prefilter.py` has shipped here for
a long time and does the cold-start job well *on URLs*. Measured: it scores a
content farm at 3 SEO signals, arXiv at 0, and tiers arXiv as `reference`. It
was already the answer to half the noise problem and I built a second filter
without reading it.

**But it cannot accrete**, and it cannot see outside the web lane. The regexes
and the domain table are fixed, so it knows exactly as much on run 500 as on run
1; and measured on the items the corpus lanes actually screen — a person, a
teardown filename, a transcript heading — it returns `seo=0 / tier=blog` every
time. Those are not URLs, so a zero there is not a clean bill, it is a layer that
cannot see. This module says so instead of banking a free pass.

**So they compose, in the order the IR literature converges on:** the free fixed
filter first, the learned one only on what survives. That ordering is the whole
point — fixed rules cost nothing and never improve, learned ones cost decisions
and compound, so the accreting layer should never spend a decision on something
already obviously junk.

Every cut names the layer that made it, because "rejected" from a static regex
and "rejected" from something this run learned are different claims and want
different scrutiny.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

from bad_research.checks.discriminate import Cut, Discriminator
from bad_research.quality.prefilter import domain_tier, is_blocklisted, seo_farm_score

# The prefilter's own documented threshold: block at two or more SEO signals.
SEO_BLOCK_AT = 2
_URL = re.compile(r"https?://\S+")


@dataclass(frozen=True)
class CascadeReport:
    considered: int
    kept: tuple[Cut, ...]
    rejected: tuple[Cut, ...]
    abstained: tuple[Cut, ...]
    by_layer: dict[str, int]
    canaries_killed: tuple[Cut, ...]
    canaries_untested: tuple[str, ...]
    safe: bool | None
    caveat: str

    def to_dict(self) -> dict[str, object]:
        return {
            "considered": self.considered,
            "kept": [c.item for c in self.kept],
            "rejected": [{"item": c.item, "because": c.because} for c in self.rejected],
            "abstained": [{"item": c.item, "because": c.because} for c in self.abstained],
            "by_layer": self.by_layer,
            "canaries_killed": [{"item": c.item, "because": c.because} for c in self.canaries_killed],
            "canaries_untested": list(self.canaries_untested),
            "safe": self.safe,
            "caveat": self.caveat,
        }


def _web_verdict(item: str) -> tuple[str, str | None]:
    """('web-prefilter', why) to cut, ('web-prefilter-skipped', None) when not a URL."""
    m = _URL.search(item)
    if not m:
        return "web-prefilter-skipped", None
    url = m.group(0)
    if is_blocklisted(url):
        return "web-prefilter", "web-prefilter: host is blocklisted"
    score = seo_farm_score(url, item, "")
    if score >= SEO_BLOCK_AT:
        return "web-prefilter", (f"web-prefilter: seo-farm score {score} >= {SEO_BLOCK_AT} "
                                 f"(tier {domain_tier(url).name})")
    return "web-prefilter", None


def cascade_screen(candidates: Iterable[str], learned: Discriminator) -> CascadeReport:
    """Free fixed signals first; the run's accumulated reject-signals on survivors."""
    by_layer: dict[str, int] = {}
    kept: list[Cut] = []
    rejected: list[Cut] = []
    survivors: list[str] = []
    considered = 0

    for c in candidates:
        considered += 1
        layer, why = _web_verdict(c)
        if layer == "web-prefilter-skipped":
            by_layer["web-prefilter-skipped"] = by_layer.get("web-prefilter-skipped", 0) + 1
            survivors.append(c)
            continue
        if why:
            by_layer["web-prefilter"] = by_layer.get("web-prefilter", 0) + 1
            rejected.append(Cut(c, why))
            continue
        survivors.append(c)

    inner = learned.screen(survivors)
    for c in inner.rejected:
        by_layer["learned"] = by_layer.get("learned", 0) + 1
        rejected.append(Cut(c.item, f"learned: {c.because}"))
    kept.extend(inner.kept)

    # The canary verdict must be taken over the CASCADE, not over its second layer.
    # A canary the web regex kills never reaches `learned.screen`, so the inner
    # report would call it untested and print SAFE while the composed filter had
    # in fact deleted a known-good item. The whole instrument is "if the filter
    # kills one it has over-learned", and after composition the filter is both
    # layers.
    killed: list[Cut] = []
    for c in sorted(learned.canaries):
        layer, why = _web_verdict(c)
        if why:
            killed.append(Cut(c, why))
    web_killed = {c.item for c in killed}
    killed.extend(c for c in inner.canaries_killed if c.item not in web_killed)
    killed.sort(key=lambda c: c.item)

    screened = {c.item for c in [*kept, *rejected, *inner.abstained]}
    untested = tuple(c for c in sorted(learned.canaries) if c not in screened)

    if not learned.canaries:
        safe, caveat = None, (
            "UNMEASURED — no canaries were planted, so this cascade's false-negative rate is "
            "unknown. That is not the same as low. Plant known-good items in the pool."
        )
    elif len(untested) == len(learned.canaries):
        safe, caveat = None, (
            f"UNMEASURED — none of the {len(learned.canaries)} canaries was in the candidate pool, "
            "so none was screened by either layer. Their survival is not evidence."
        )
    elif killed:
        layers = sorted({c.because.split(":")[0] for c in killed})
        safe, caveat = False, (
            f"UNSAFE — the cascade would kill {len(killed)} known-good item(s), at: "
            f"{', '.join(layers)}. Fix the layer named, not the other one."
        )
    else:
        live = len(learned.canaries) - len(untested)
        safe, caveat = True, (
            f"{live} of {len(learned.canaries)} canaries were screened by this cascade and survived"
            + (f"; {len(untested)} were not in the pool and tested nothing. " if untested else ". ")
            + "That bounds the false-negative rate only for garbage resembling those items."
        )

    if by_layer.get("web-prefilter-skipped"):
        caveat = (f"{by_layer['web-prefilter-skipped']} item(s) carried no URL, so the web layer "
                  "could not see them — that is a skip, not a clean pass. " + caveat)
    return CascadeReport(considered, tuple(kept), tuple(rejected), inner.abstained,
                         by_layer, tuple(killed), untested, safe, caveat)


__all__ = ["SEO_BLOCK_AT", "CascadeReport", "cascade_screen"]
