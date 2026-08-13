"""Intent detection + vertical routing (seed-only verticals, always-on grounding)."""

from __future__ import annotations

from bad_research.web.search.route import VERTICAL_ROUTES, detect_intent, route_query


def test_routes_table_matches_dossier():
    assert VERTICAL_ROUTES["academic"] == ["openalex", "arxiv", "semantic_scholar", "crossref"]
    assert VERTICAL_ROUTES["medical"] == ["europe_pmc", "pubmed", "openalex"]
    assert VERTICAL_ROUTES["technical"] == ["arxiv", "openalex", "ddgs"]
    assert VERTICAL_ROUTES["general"] == []


def test_detect_intent_regex_fallback():
    assert detect_intent("systematic review of et al. arxiv papers") == "academic"
    assert detect_intent("clinical trial drug dosage mg/kg in vivo") == "medical"
    assert detect_intent("how to implement an API library stack trace") == "technical"
    assert detect_intent("best pizza in town") == "general"


def test_social_route_is_the_last30days_lane():
    assert VERTICAL_ROUTES["social"] == ["last30days"]


def test_detect_intent_reads_reception_questions_as_social():
    assert detect_intent("what do users say about the new pricing") == "social"
    assert detect_intent("reddit reception of the rewrite") == "social"
    assert detect_intent("is there backlash to the rebrand") == "social"
    assert detect_intent("hacker news sentiment on rust in the kernel") == "social"


def test_social_never_outranks_a_more_specific_intent():
    # A question that is both literature and reception gets the papers; the
    # always-on WebSearch baseline still carries the commentary, and the social
    # lane costs minutes we should not spend on a hunch.
    assert detect_intent("what do people say about the arxiv preprint") == "academic"
    assert detect_intent("patients complain about the therapy") == "medical"


def test_a_general_query_is_still_general():
    # Regression guard: the social cues must stay narrow enough that the
    # byte-identical no-verticals path survives for ordinary queries.
    for q in ("best pizza in town", "weather in Lisbon next week", "how tall is Everest"):
        assert detect_intent(q) == "general"


def test_route_query_baseline_websearch_on_every_query():
    tasks = route_query("q", ["a", "b", "c"], "general")
    ws = [(q, p) for (q, p) in tasks if p == "websearch"]
    assert {q for q, _ in ws} == {"a", "b", "c"}     # WebSearch fans every query
    # always-on Wikipedia grounding on 1 seed
    assert ("a", "wikipedia") in tasks
    assert sum(1 for _, p in tasks if p == "wikipedia") == 1


def test_route_query_academic_verticals_seed_only():
    tasks = route_query("q", ["a", "b", "c", "d"], "academic")
    # verticals fan ONLY on the first <=2 seed queries
    oalex = [(q, p) for (q, p) in tasks if p == "openalex"]
    assert {q for q, _ in oalex} == {"a", "b"}        # seeds only, never c/d
    assert ("a", "arxiv") in tasks
    assert ("a", "crossref") in tasks
    assert ("a", "semantic_scholar") in tasks


def test_route_query_medical_intent():
    tasks = route_query("q", ["a", "b"], "medical")
    provs = {p for _, p in tasks}
    assert "europe_pmc" in provs and "pubmed" in provs
    assert "arxiv" not in provs                       # not in the medical route
