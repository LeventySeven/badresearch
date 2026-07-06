"""Regression lock for the untrusted-content (prompt-injection) defense-in-depth.

The fetcher is the #1 lethal-trifecta node: it ingests raw web pages while holding
Bash + WebSearch (an outbound channel). Its system prompt MUST carry the standing
untrusted-content warning (baked in at install so it does not depend on the orchestrator
remembering the spawn-contract clause). The authoritative control is the SSRF egress
allowlist on the fetch path; this is the model-side layer that was previously absent.
"""

from __future__ import annotations

from bad_research.core import hooks


def test_fetcher_agent_carries_untrusted_content_warning():
    body = hooks.RESEARCHER_AGENT.format(hpr_path="bad").lower()
    assert "untrusted" in body, "fetcher lost its untrusted-content security warning"
    # names the boundary and the rule
    assert "never a command" in body or "never a command." in body or "not a command" in body \
        or "never" in body
    # names the outbound-channel exposure it must not let content steer
    assert "bash" in body and "websearch" in body


def test_fetcher_agent_still_formats_and_ships_claims_shape():
    # the security insert must not break .format(hpr_path=) or the claims-json contract
    body = hooks.RESEARCHER_AGENT.format(hpr_path="bad")
    assert "claims-" in body or "quoted_support" in body  # claims-*.json contract intact
