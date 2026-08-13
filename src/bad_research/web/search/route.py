"""Vertical routing (dossier 13 §8.2). Fire the right keyless API only on the
right intent — generic WebSearch stays the always-on baseline; Wikipedia is
always-on grounding (1 seed); verticals fan ONLY on the first <=2 seed queries
(politeness, §2.1)."""

from __future__ import annotations

import re

# KNOWN: the verbatim route table (dossier 13 §8.2). Names map to provider
# instances at fan-out time (the funnel owns the name->instance map, KR-6).
VERTICAL_ROUTES: dict[str, list[str]] = {
    "academic": ["openalex", "arxiv", "semantic_scholar", "crossref"],
    "medical": ["europe_pmc", "pubmed", "openalex"],
    "technical": ["arxiv", "openalex", "ddgs"],
    "social": ["last30days"],
    "general": [],
}

_ACADEMIC = re.compile(r"\b(paper|study|et al\.?|arxiv|doi|systematic review|preprint|citation)\b", re.I)
_MEDICAL = re.compile(r"\b(disease|drug|gene|clinical trial|patients?|mg/kg|in vivo|crispr|cancer|therapy)\b", re.I)
_TECHNICAL = re.compile(r"\b(error|stack trace|api|library|framework|protocol|how to (implement|configure))\b", re.I)
# Reception, not literature: the answer lives in threads and comments, and the
# blog post about them is the derivative. Kept narrow on purpose — the social
# lane costs minutes, so it fires on an explicit signal, never on a hunch.
_SOCIAL = re.compile(
    r"\b(reddit|hacker ?news|subreddit|upvot\w*|twitter|tiktok|community|"
    r"sentiment|reception|backlash|complain\w*|what (do|are) (people|users|devs|developers)|"
    r"trending|word of mouth|user reviews?)\b",
    re.I,
)

_SEED_LIMIT = 2          # verticals fan on <=2 seed queries (§8.2)


def detect_intent(question: str) -> str:
    """DESIGNED regex fallback (§8.2); the host model normally tags intent in the
    expansion step. medical > academic > technical > social precedence (most
    specific wins — a medical signal beats the generic "systematic review"/"paper"
    academic cues). Social sits last because it is the widest net and the most
    expensive lane: a question that is BOTH literature and reception is better
    served by the papers, and the always-on WebSearch baseline still covers the
    commentary."""
    if _MEDICAL.search(question):
        return "medical"
    if _ACADEMIC.search(question):
        return "academic"
    if _TECHNICAL.search(question):
        return "technical"
    if _SOCIAL.search(question):
        return "social"
    return "general"


def route_query(question: str, queries: list[str], intent: str) -> list[tuple[str, str]]:
    """Return (query, provider_name) tasks. WebSearch on every query (baseline) +
    Wikipedia on 1 seed (grounding) + intent-routed verticals on <=2 seeds."""
    tasks: list[tuple[str, str]] = [(q, "websearch") for q in queries]
    if queries:
        tasks.append((queries[0], "wikipedia"))            # always-on grounding (1 seed)
    for prov in VERTICAL_ROUTES.get(intent, []):
        for q in queries[:_SEED_LIMIT]:
            tasks.append((q, prov))                        # verticals on seed queries only
    return tasks
