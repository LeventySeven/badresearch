from __future__ import annotations

from bad_research.funnel.canonical import canonicalize_url


def test_strips_trailing_slash():
    assert canonicalize_url("https://a.com/p") == canonicalize_url("https://a.com/p/")


def test_strips_hash_fragment():
    assert canonicalize_url("https://a.com/p#section") == canonicalize_url("https://a.com/p")


def test_strips_www():
    assert canonicalize_url("https://www.a.com/p") == canonicalize_url("https://a.com/p")


def test_strips_default_port():
    assert canonicalize_url("https://a.com:443/p") == canonicalize_url("https://a.com/p")
    assert canonicalize_url("http://a.com:80/p") == canonicalize_url("http://a.com/p")


def test_strips_index_files():
    assert canonicalize_url("https://a.com/docs/index.html") == canonicalize_url("https://a.com/docs")
    assert canonicalize_url("https://a.com/index.php") == canonicalize_url("https://a.com")


def test_lowercases_scheme_and_host_keeps_path_case():
    assert canonicalize_url("HTTPS://A.COM/Path") == "https://a.com/Path"


def test_preserves_query_string():
    # query is meaningful (e.g. ?id=5); do NOT strip it
    out = canonicalize_url("https://a.com/p?id=5")
    assert "id=5" in out


def test_distinct_paths_stay_distinct():
    assert canonicalize_url("https://a.com/p") != canonicalize_url("https://a.com/q")


# ---- tracking-param stripping (utm_*/fbclid/gclid/… twins collapse) --------

def test_strips_utm_tracking_params():
    assert canonicalize_url("https://a.com/p?utm_source=x") == canonicalize_url("https://a.com/p")


def test_strips_click_id_tracking_params():
    assert canonicalize_url("https://a.com/p?fbclid=abc&gclid=def") == canonicalize_url("https://a.com/p")


def test_strips_mailchimp_and_instagram_tracking_params():
    assert canonicalize_url("https://a.com/p?mc_eid=1&mc_cid=2&igshid=z") == canonicalize_url("https://a.com/p")


def test_keeps_semantic_params_drops_tracking():
    out = canonicalize_url("https://a.com/p?id=5&utm_campaign=spring")
    assert "id=5" in out
    assert "utm_campaign" not in out


# ---- AMP / mobile twin stripping -------------------------------------------

def test_strips_amp_subdomain():
    assert canonicalize_url("https://amp.a.com/p") == canonicalize_url("https://a.com/p")


def test_strips_mobile_subdomain():
    assert canonicalize_url("https://m.a.com/p") == canonicalize_url("https://a.com/p")


def test_strips_old_subdomain():
    # old.reddit.com serves the SAME thread as reddit.com (issue #40).
    assert canonicalize_url("https://old.reddit.com/r/x") == canonicalize_url(
        "https://reddit.com/r/x")


def test_keeps_a_registrable_domain_that_merely_starts_with_a_prefix():
    # `m.com` / `old.com` are ordinary domains, not prefixed hosts — stripping
    # the prefix would collapse them onto the bare TLD and collide with
    # every other *.com.
    assert canonicalize_url("https://m.com/p") == "https://m.com/p"
    assert canonicalize_url("https://old.com/p") == "https://old.com/p"
    assert canonicalize_url("https://amp.com/p") == "https://amp.com/p"


def test_strips_trailing_amp_path_segment():
    assert canonicalize_url("https://a.com/story/amp") == canonicalize_url("https://a.com/story")


def test_strips_leading_amp_path_segment():
    assert canonicalize_url("https://a.com/amp/story") == canonicalize_url("https://a.com/story")
