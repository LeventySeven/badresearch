"""A lane that was never BUILT emitted no row at all (issue #39).

`_build_providers` swallowed a ddgs import failure with a bare `pass`, so the
lane simply never appeared in `providers`. `fan_out` can only report on providers
it was handed, so `provider_outcomes` was silent about the absence entirely — and
the run reported a research gap on a topic its always-on breadth lane never
searched.
"""

from __future__ import annotations

import bad_research.cli.research as RESEARCH  # noqa: N812


class _Cfg:
    searxng_endpoint = ""


def test_a_ddgs_that_cannot_be_constructed_is_recorded(monkeypatch):
    import bad_research.web.search.base as BASE  # noqa: N812

    def _boom(*a, **k):
        raise ImportError("DdgsProvider requires: pip install ddgs")

    monkeypatch.setattr(BASE, "DdgsProvider", _boom)
    skipped: dict = {}
    RESEARCH._build_providers(_Cfg(), skipped=skipped)

    assert skipped == {"ddgs": "skipped-unconfigured"}


def test_a_totally_unimportable_search_module_records_both_lanes(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def _fake_import(name, *a, **k):
        if name == "bad_research.web.search.base":
            raise ImportError("no web stack")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    skipped: dict = {}
    provs = RESEARCH._build_providers(_Cfg(), skipped=skipped)

    assert provs == []
    assert skipped == {"ddgs": "skipped-unconfigured",
                       "websearch": "skipped-unconfigured"}


def test_an_unconfigured_searxng_is_not_recorded():
    """Opt-in infrastructure most installs never intend to run. A row on every
    run would be noise that trains the reader to ignore the field."""
    skipped: dict = {}
    RESEARCH._build_providers(_Cfg(), skipped=skipped)
    assert "searxng" not in skipped


def test_skipped_is_optional_and_the_default_call_is_unchanged():
    """No caller or test fake breaks: the parameter is additive."""
    assert isinstance(RESEARCH._build_providers(_Cfg()), list)


def test_a_skipped_lane_reaches_the_envelope_as_a_coverage_gap(monkeypatch, tmp_path):
    """The whole point: the absence becomes visible to the orchestrating model."""
    monkeypatch.chdir(tmp_path)

    class _Vault:
        root = tmp_path
        def close(self) -> None: ...

    class _Engine:
        def index(self, notes): ...
        def search(self, q, mode="light", top_k=10):
            return []
        def close(self) -> None: ...

    class _Store:
        stored_note_ids: list[str] = []

    def _providers(cfg, skipped=None):
        if skipped is not None:
            skipped["ddgs"] = "skipped-unconfigured"
        return []

    async def _fake_gather(query, **kw):
        stats = kw.get("stats")
        if stats is not None:
            stats.update({"provider_outcomes": {"websearch": "unavailable"},
                          "degraded_reasons": [], "degraded": False,
                          "coverage_gaps": [], "n_fetch_failed": 0})
        return []

    monkeypatch.setattr(RESEARCH, "_build_providers", _providers)
    monkeypatch.setattr(RESEARCH, "_build_vertical_providers", lambda q: [])
    monkeypatch.setattr(RESEARCH, "_build_tiered_fetcher", lambda cfg: None)
    monkeypatch.setattr(RESEARCH, "_build_engine", lambda cfg, vault: _Engine())
    monkeypatch.setattr("bad_research.core.vault.Vault.discover", classmethod(lambda cls: _Vault()))
    monkeypatch.setattr("bad_research.funnel.store.VaultStore", lambda *a, **k: _Store())
    monkeypatch.setattr("bad_research.funnel.gather", _fake_gather)

    env = RESEARCH.run_funnel("q", mode="light", vault_tag="t")

    assert env["provider_outcomes"]["ddgs"] == "skipped-unconfigured"
    assert {"provider": "ddgs", "outcome": "skipped-unconfigured"} in env["coverage_gaps"]
    assert env["degraded"] is False, "an unbuilt lane is a gap, not a hard STOP"
