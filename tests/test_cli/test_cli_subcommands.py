import json

from typer.testing import CliRunner

from bad_research.cli import app

runner = CliRunner()


def test_route_command_classifies(tmp_path):
    d = tmp_path / "decomp.json"
    d.write_text(json.dumps({"sub_questions": ["what is X"], "entities": [],
                             "response_format": "short", "time_periods": [],
                             "contradiction_terms": [], "domains": ["tech"]}))
    res = runner.invoke(app, ["route", "--decomposition", str(d), "--json"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["route"] == "fast"


def test_route_apply_writes_field(tmp_path):
    d = tmp_path / "decomp.json"
    d.write_text(json.dumps({"sub_questions": [f"q{i}" for i in range(8)],
                             "entities": [], "response_format": "argumentative",
                             "time_periods": [], "contradiction_terms": ["vs"],
                             "domains": ["a"]}))
    res = runner.invoke(app, ["route", "--decomposition", str(d), "--apply", "--json"])
    assert res.exit_code == 0
    assert json.loads(d.read_text())["route"] == "full"


def test_route_apply_idempotent_and_reason_present(tmp_path):
    d = tmp_path / "decomp.json"
    d.write_text(json.dumps({"sub_questions": ["q1", "q2", "q3", "q4"], "entities": [],
                             "response_format": "structured", "time_periods": [],
                             "contradiction_terms": [], "domains": ["tech"]}))
    res = runner.invoke(app, ["route", "--decomposition", str(d), "--apply", "--json"])
    out = json.loads(res.stdout)
    assert out["route"] == "fast"
    assert out["applied"] is True
    assert out["reason"]


def test_route_command_emits_query_shape(tmp_path):
    # E12: the route CLI also emits query_shape (fan-out shape) + shape_reason,
    # ORTHOGONAL to the route. A single-entity factual is `straightforward`.
    d = tmp_path / "decomp.json"
    d.write_text(json.dumps({"sub_questions": ["what is the population of Tokyo"],
                             "entities": ["Tokyo"], "response_format": "short",
                             "time_periods": [], "contradiction_terms": [],
                             "domains": ["geo"]}))
    res = runner.invoke(app, ["route", "--decomposition", str(d), "--json"])
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert out["query_shape"] == "straightforward"
    assert out["shape_reason"]
    # the route field is still the unchanged fast classification
    assert out["route"] == "fast"


def test_route_apply_writes_query_shape_field(tmp_path):
    # a multi-entity survey applies a `breadth_first` shape WITHOUT changing route
    d = tmp_path / "decomp.json"
    d.write_text(json.dumps({"sub_questions": [f"metric {i}" for i in range(8)],
                             "entities": ["Norway", "Sweden", "Denmark"],
                             "response_format": "structured", "modality": "compare",
                             "time_periods": [], "contradiction_terms": [],
                             "domains": ["econ"]}))
    res = runner.invoke(app, ["route", "--decomposition", str(d), "--apply", "--json"])
    assert res.exit_code == 0
    written = json.loads(d.read_text())
    assert written["query_shape"] == "breadth_first"
    # route is whatever it was before E12 (the B-5 survey down-route still holds)
    assert written["route"] == "fast"


def test_route_emits_machine_readable_fanout_coverage(tmp_path):
    # issue #36: a survey wider than the loci cap must report what it will NOT
    # cover as data, so an orchestrator branches on `deferred` instead of
    # parsing `shape_reason` prose.
    from bad_research.skills import routing_constants as R  # noqa: N812

    d = tmp_path / "decomp.json"
    d.write_text(json.dumps({"sub_questions": [f"option {i}" for i in range(25)],
                             "entities": [], "response_format": "structured",
                             "modality": "collect", "time_periods": [],
                             "contradiction_terms": [], "domains": ["tech"]}))
    res = runner.invoke(app, ["route", "--decomposition", str(d), "--json"])
    assert res.exit_code == 0
    fan = json.loads(res.stdout)["fanout"]
    assert fan["shape"] == "breadth_first"
    assert fan["n_subq"] == 25
    assert fan["cap"] == R.LOCI_MAX
    assert fan["k"] == R.LOCI_MAX
    assert fan["deferred"] == 25 - R.LOCI_MAX


def test_route_fast_flag_overrides(tmp_path):
    # A decomposition the router would call "full" (multi-domain), forced to fast.
    decomp = tmp_path / "decomp.json"
    decomp.write_text(json.dumps({
        "sub_questions": ["a", "b"], "entities": [], "time_periods": [],
        "response_format": "structured", "contradiction_terms": [],
        "domains": ["a", "b", "c"],
    }))
    result = runner.invoke(app, ["route", "--decomposition", str(decomp), "--fast", "--json"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["route"] == "fast"


def test_route_fast_and_full_mutually_exclusive(tmp_path):
    decomp = tmp_path / "decomp.json"
    decomp.write_text(json.dumps({"sub_questions": ["a"], "entities": [], "domains": ["x"],
                                  "response_format": "short"}))
    result = runner.invoke(app, ["route", "--decomposition", str(decomp), "--fast", "--full"])
    assert result.exit_code != 0


# ── E11 plan-gate: route CLI reports the gate decision (default = no gate) ─────

def test_route_plan_gate_default_is_false(tmp_path):
    # Default (no interactivity flag): non-interactive → plan_gate.would_gate False,
    # even for a full-tier query. This is what keeps automated runs flowing through.
    d = tmp_path / "decomp.json"
    d.write_text(json.dumps({"sub_questions": [f"q{i}" for i in range(8)],
                             "entities": [], "response_format": "argumentative",
                             "time_periods": [], "contradiction_terms": ["vs"],
                             "domains": ["a"]}))
    res = runner.invoke(app, ["route", "--decomposition", str(d), "--json"])
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert out["route"] == "full"
    assert out["plan_gate"]["would_gate"] is False


def test_route_plan_gate_interactive_full_fires(tmp_path):
    d = tmp_path / "decomp.json"
    d.write_text(json.dumps({"sub_questions": [f"q{i}" for i in range(8)],
                             "entities": [], "response_format": "argumentative",
                             "time_periods": [], "contradiction_terms": ["vs"],
                             "domains": ["a"]}))
    res = runner.invoke(app, ["route", "--decomposition", str(d),
                              "--interactive", "--json"])
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert out["plan_gate"]["would_gate"] is True


def test_route_plan_gate_interactive_but_wrapped_does_not_fire(tmp_path):
    d = tmp_path / "decomp.json"
    d.write_text(json.dumps({"sub_questions": [f"q{i}" for i in range(8)],
                             "entities": [], "response_format": "argumentative",
                             "time_periods": [], "contradiction_terms": ["vs"],
                             "domains": ["a"]}))
    res = runner.invoke(app, ["route", "--decomposition", str(d),
                              "--interactive", "--wrapped", "--json"])
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert out["plan_gate"]["would_gate"] is False


def test_uncited_gate_command_registered():
    res = runner.invoke(app, ["uncited-gate", "--help"])
    assert res.exit_code == 0


# ── A-3: standalone uncited-gate (no pre-populated vault) ────────────────────

def test_uncited_gate_standalone_with_note_bodies_resolves_cites(tmp_path, monkeypatch):
    # Run OUTSIDE Claude Code: a tmp cwd with NO vault. --note-bodies supplies the
    # universe of valid sources; a fully-cited report ships clean (exit 0).
    monkeypatch.chdir(tmp_path)
    report = tmp_path / "r.md"
    report.write_text(
        "Southeast Asian GMV grew 12.4% in 2024 [1].\n"
        "Vietnam led the region at 64% penetration [[src-vn]].\n",
        encoding="utf-8",
    )
    notes = tmp_path / "notes.json"
    notes.write_text(
        json.dumps({"src-sea": "a 12.4% YoY expansion", "src-vn": "Vietnam at 64%"}),
        encoding="utf-8",
    )
    res = runner.invoke(app, ["uncited-gate", "--report", str(report),
                              "--note-bodies", str(notes), "--vault-tag", "x", "--json"])
    assert res.exit_code == 0, res.stdout + (res.stderr or "")
    assert json.loads(res.stdout)["uncited"] == []


def test_uncited_gate_citation_drift_warns_but_ships(tmp_path, monkeypatch):
    # A factual claim cites a note whose body is about something else entirely.
    # Phase-1 'bind, not count': this is a NON-BLOCKING drift warning — the report
    # ships (exit 0), the drift lands under `warnings`, and `uncited` stays empty.
    monkeypatch.chdir(tmp_path)
    report = tmp_path / "r.md"
    report.write_text(
        "Southeast Asian e-commerce GMV grew 12.4% in 2024 [1].\n", encoding="utf-8")
    off_topic = (
        "Arctic terns undertake the longest annual migration of any bird, flying from "
        "their Arctic breeding grounds to the Antarctic and back, a round trip that can "
        "exceed ninety thousand kilometres over a lifetime spanning three decades.")
    notes = tmp_path / "notes.json"
    notes.write_text(json.dumps({"src1": off_topic}), encoding="utf-8")
    res = runner.invoke(app, ["uncited-gate", "--report", str(report),
                              "--note-bodies", str(notes), "--vault-tag", "x", "--json"])
    assert res.exit_code == 0, res.stdout + (res.stderr or "")   # SHIPS — drift never blocks
    out = json.loads(res.stdout)
    assert out["uncited"] == []
    assert len(out["warnings"]) == 1
    assert out["warnings"][0]["reason"] == "citation-drift"


def test_uncited_gate_standalone_flags_uncited_factual_sentence(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    report = tmp_path / "r.md"
    # one cited line + one genuinely uncited factual sentence
    report.write_text(
        "Southeast Asian GMV grew 12.4% in 2024 [1].\n"
        "Indonesia reportedly led the region at 71% penetration.\n",
        encoding="utf-8",
    )
    notes = tmp_path / "notes.json"
    notes.write_text(json.dumps({"src-sea": "a 12.4% YoY expansion"}), encoding="utf-8")
    res = runner.invoke(app, ["uncited-gate", "--report", str(report),
                              "--note-bodies", str(notes), "--vault-tag", "x", "--json"])
    assert res.exit_code == 1
    uncited = json.loads(res.stdout)["uncited"]
    assert len(uncited) == 1
    assert "Indonesia" in uncited[0]["sentence"]


def test_uncited_gate_missing_db_is_clean_zero_anchors_not_traceback(tmp_path, monkeypatch):
    # No vault, no --note-bodies: the gate must auto-init the schema and report
    # "0 anchors" (every factual sentence uncited) rather than raising
    # OperationalError: no such table: claim_anchors.
    monkeypatch.chdir(tmp_path)
    report = tmp_path / "r.md"
    report.write_text("A neutral framing sentence with no claims at all.\n", encoding="utf-8")
    res = runner.invoke(app, ["uncited-gate", "--report", str(report),
                              "--vault-tag", "x", "--json"])
    # No traceback (the bug was a crash). A no-claim report ships clean.
    assert res.exception is None, res.exception
    assert res.exit_code == 0
    assert json.loads(res.stdout)["uncited"] == []


def test_verify_citations_standalone_keyless_no_vault_degrades(tmp_path, monkeypatch):
    # Standalone keyless, NO vault: _verify_report must mirror _uncited_gate —
    # catch VaultError and fall back to an empty in-memory store rather than
    # crashing with VaultError before the keyless degrade can run.
    monkeypatch.chdir(tmp_path)
    report = tmp_path / "r.md"
    report.write_text("# Report\n\nThe sky is blue [1].\n", encoding="utf-8")
    res = runner.invoke(app, ["verify-citations", "--report", str(report),
                              "--vault-tag", "t", "--json"])
    assert res.exception is None, res.exception
    assert res.exit_code == 0
    assert "results" in json.loads(res.stdout)


def test_verify_citations_standalone_keyless_fresh_db_no_table_degrades(tmp_path, monkeypatch):
    # Vault present but a fresh anchors.db with no claim_anchors table: the
    # command must auto-init the schema (idempotent) so it degrades instead of
    # raising OperationalError: no such table: claim_anchors.
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".hyperresearch").mkdir()
    report = tmp_path / "r.md"
    report.write_text("# Report\n\nThe sky is blue [1].\n", encoding="utf-8")
    res = runner.invoke(app, ["verify-citations", "--report", str(report),
                              "--vault-tag", "t", "--json"])
    assert res.exception is None, res.exception
    assert res.exit_code == 0
    assert "results" in json.loads(res.stdout)


def test_all_research_subcommands_registered():
    for cmd in ("route", "funnel-gather", "retrieve", "verify-citations", "uncited-gate"):
        res = runner.invoke(app, [cmd, "--help"])
        assert res.exit_code == 0, cmd


def test_verify_citations_accepts_effort_flag():
    # E4: verify-citations exposes --effort so the high-effort self-consistency lane
    # can be turned on for high-stakes verification (--effort high). The flag is
    # documented in the command help.
    res = runner.invoke(app, ["verify-citations", "--help"])
    assert res.exit_code == 0
    # C-5: --effort is the single canonical flag; the --reasoning-effort alias is gone.
    assert "--effort" in res.stdout
    assert "--reasoning-effort" not in res.stdout


def test_verify_citations_cmd_has_only_effort_not_reasoning_effort_alias():
    """After C-5: --reasoning-effort alias removed; only --effort is canonical."""
    r = runner.invoke(app, ["verify-citations", "--help"])
    assert "--effort" in r.stdout, "--effort flag must be present"
    assert "--reasoning-effort" not in r.stdout, \
        "--reasoning-effort alias must be removed; use --effort only"


def test_funnel_gather_cmd_has_only_effort_not_reasoning_effort_alias():
    r = runner.invoke(app, ["funnel-gather", "--help"])
    assert "--effort" in r.stdout
    assert "--reasoning-effort" not in r.stdout


def test_funnel_gather_json_emits_error_envelope_not_traceback(monkeypatch):
    # issue #24: a connection/DNS error inside run_funnel (e.g. an unreachable
    # search-provider host on the fan-out) must NOT propagate as an uncaught
    # traceback. Under --json the caller gets a parseable {"ok": false, ...}
    # envelope and a clean non-zero exit, so an orchestrator can branch on it.
    import bad_research.cli.research as research_mod

    def _boom(*a, **k):
        raise ConnectionError("[Errno 8] nodename nor servname provided, or not known")

    monkeypatch.setattr(research_mod, "run_funnel", _boom)

    res = runner.invoke(app, ["funnel-gather", "some query", "--mode", "full", "--json"])
    assert res.exit_code != 0                      # non-zero, but CLEAN
    assert res.exception is None or isinstance(res.exception, SystemExit)
    env = json.loads(res.stdout)                   # parseable, not a stack trace
    assert env["ok"] is False
    assert env["stage"] == "funnel-gather"
    assert "nodename nor servname" in env["error"]
    assert env["error_type"] == "ConnectionError"


def test_verify_report_threads_effort_into_verifier(tmp_path, monkeypatch):
    # The --effort value reaches CitationVerifier.effort (so the high-effort vote
    # actually fires on a real run, not just when constructed directly in a test).
    import bad_research.cli.research as research_mod
    from bad_research.grounding import verifier as verifier_mod

    captured: dict[str, object] = {}
    real_init = verifier_mod.CitationVerifier.__init__

    def _spy_init(self, *, nli, llm, effort=None):
        captured["effort"] = effort
        real_init(self, nli=nli, llm=llm, effort=effort)

    monkeypatch.setattr(verifier_mod.CitationVerifier, "__init__", _spy_init)

    # Stub the heavy adapter pieces so _verify_report runs offline.
    class _Vault:
        root = str(tmp_path)

    monkeypatch.setattr(research_mod, "_verify_report", research_mod._verify_report)
    from bad_research.core.vault import Vault

    monkeypatch.setattr(Vault, "discover", classmethod(lambda cls: _Vault()))

    class _Cfg:
        @staticmethod
        def load():
            return _Cfg()

    from bad_research.config import BadResearchConfig

    monkeypatch.setattr(BadResearchConfig, "load", staticmethod(lambda: _Cfg()))

    class _LLM:
        name = "stub"

        def complete(self, *a, **k):  # never called on an empty report
            raise AssertionError("no LLM expected on an empty report")

    monkeypatch.setattr(research_mod, "get_llm_provider", lambda *a, **k: _LLM(), raising=False)
    import bad_research.llm.base as llm_base

    monkeypatch.setattr(llm_base, "get_llm_provider", lambda *a, **k: _LLM())

    report = tmp_path / "report.md"
    report.write_text("Just an intro with no citations.\n", encoding="utf-8")

    research_mod._verify_report(str(report), "tag-1", effort="high")
    assert captured["effort"] == "high"
