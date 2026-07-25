"""CLI commands for vault lifecycle and corpus inspection.

Implements the 6 commands the bundled skill depends on but were never wired:
  init          — create a new vault
  vault-tag     — mint a unique <slug>-<6hex> run identifier
  archive-run   — move prior-run scratch files into runs/archive-<tag>-<ts>/
  search        — list/filter notes from vault (by tag / type / query)
  lint          — deterministic file-existence / content checks (4 rules)
  note show     — read one or more notes by id and emit body + frontmatter

All commands emit the canonical Envelope (`cli/_output.output` + `models.output`)
so `--json` payloads match the shape the skill parses (`d["data"][...]`), the
same wrapper `bad doctor`/`bad calibrate` already use.
"""

from __future__ import annotations

import json
import re
import secrets
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer

from bad_research.cli._output import output
from bad_research.models.output import error as envelope_error
from bad_research.models.output import success

if TYPE_CHECKING:
    from bad_research.core.vault import Vault


# ── helpers ──────────────────────────────────────────────────────────────────

def _emit_success(data: Any, *, json_mode: bool, count: int | None = None,
                  vault: str | None = None) -> None:
    """Emit a success Envelope as a JSON line (json_mode) or a human summary."""
    env = success(data, count=count, vault=vault)
    if json_mode:
        output(env, json_mode=True)
    elif isinstance(data, dict):
        for k, v in data.items():
            typer.echo(f"{k}: {v}")
    else:
        typer.echo(str(data))


def _emit_error(message: str, *, json_mode: bool, code: str = "ERROR") -> None:
    """Emit an error Envelope as a JSON line (json_mode) or a stderr message."""
    if json_mode:
        output(envelope_error(message, code=code), json_mode=True)
    else:
        typer.echo(f"ERROR: {message}", err=True)


def _discover_vault() -> Vault:
    from bad_research.core.vault import Vault
    return Vault.discover()


def _parse_note_frontmatter(path: Path) -> dict[str, Any]:
    """Return frontmatter dict for a markdown file, with empty fallback."""
    try:
        from bad_research.core.frontmatter import parse_frontmatter
        meta, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        return meta.model_dump(mode="json", exclude_none=True)
    except Exception:
        return {}


# ── init ─────────────────────────────────────────────────────────────────────

def init_cmd(
    path: str = typer.Argument(".", help="Directory to initialise as a vault"),
    name: str = typer.Option("Research Base", "--name", help="Vault display name"),
    research_dir: str = typer.Option("research", "--research-dir"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Emit JSON"),
) -> None:
    """Initialise a new hyperresearch vault in PATH.

    Creates .hyperresearch/ (config + SQLite DB) and research/ (notes/index/temp).
    No-ops with a clear message when a vault already exists.
    """
    from bad_research.core.vault import Vault, VaultError

    root = Path(path).resolve()
    try:
        vault = Vault.init(root, name=name, research_dir=research_dir)
    except VaultError as exc:
        # Already initialized — surface cleanly rather than crashing
        _emit_error(str(exc), json_mode=json_output, code="VAULT_EXISTS")
        raise typer.Exit(code=1) from exc

    data = {
        "vault_root": str(vault.root),
        "research_dir": str(vault.research_dir),
        "db": str(vault.db_path),
    }
    _emit_success(data, json_mode=json_output, vault=str(vault.root))


# ── vault-tag ────────────────────────────────────────────────────────────────

def vault_tag_cmd(
    slug: str = typer.Argument(..., help="Short topical slug, e.g. efield-dft-sac"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Emit JSON"),
) -> None:
    """Mint a unique vault tag: <slug>-<6hex>.

    The 6-hex suffix is regenerated until it is unique against all
    research/query-*.md and research/notes/final_report_*.md files in the
    current vault, preventing overwrite of any prior run's artifacts.
    """
    vault = _discover_vault()
    research_dir = vault.research_dir

    def _is_taken(tag: str) -> bool:
        # Check query files and final reports for this tag
        for pattern in (
            f"query-{tag}.md",
            f"notes/final_report_{tag}.md",
        ):
            if (research_dir / pattern).exists():
                return True
        return False

    suffix = ""
    vault_tag = ""
    for _ in range(32):  # practically infinite — 16^6 = 16M possibilities
        suffix = secrets.token_hex(3)  # 3 bytes → 6 hex chars
        vault_tag = f"{slug}-{suffix}"
        if not _is_taken(vault_tag):
            break
    else:
        # Astronomically unlikely, but handle it
        _emit_error("could not mint a unique vault tag after 32 attempts",
                    json_mode=json_output, code="TAG_COLLISION")
        raise typer.Exit(code=1)

    data = {"vault_tag": vault_tag, "slug": slug, "suffix": suffix}
    _emit_success(data, json_mode=json_output, vault=str(vault.root))


# ── archive-run ───────────────────────────────────────────────────────────────

# Files/globs in research/ root that belong to a prior run's scratch set
_SCRATCH_NAMES = {
    "scaffold.md",
    "loci.json",
    "comparisons.md",
    "corpus-critic-gaps.json",
    "patch-log.json",
    "polish-log.json",
    "prompt-decomposition.json",
    "readability-recommendations.json",
    "readability-decisions.json",
    "grader-log.json",
    "clarify.json",
}
_SCRATCH_PREFIXES = (
    "critic-findings-",
)


def archive_run_cmd(
    json_output: bool = typer.Option(False, "--json", "-j", help="Emit JSON"),
) -> None:
    """Archive prior-run scratch files into research/runs/archive-<ts>/.

    Moves scaffold, loci, comparisons, critic-findings, patch-log, polish-log,
    prompt-decomposition, and research/temp/* into a timestamped archive
    directory so the next run starts from a clean slate without losing history.

    Final reports (research/notes/final_report_*.md) and canonical query files
    (research/query-*.md) are already namespaced and are left in place.

    No-ops cleanly on a fresh vault — safe to run unconditionally.
    """
    vault = _discover_vault()
    research_dir = vault.research_dir

    # Collect scratch files from research/ root
    to_move: list[Path] = []
    if research_dir.exists():
        for item in research_dir.iterdir():
            if not item.is_file():
                continue
            if item.name in _SCRATCH_NAMES:
                to_move.append(item)
                continue
            for prefix in _SCRATCH_PREFIXES:
                if item.name.startswith(prefix) and item.suffix == ".json":
                    to_move.append(item)
                    break

    # Collect research/temp/* scratch directory
    temp_dir = vault.temp_dir
    has_temp = temp_dir.exists() and any(temp_dir.iterdir())

    if not to_move and not has_temp:
        data: dict[str, Any] = {
            "archived": False,
            "reason": "nothing to archive",
            "moved_files": [],
            "archive_dir": None,
        }
        _emit_success(data, json_mode=json_output, vault=str(vault.root))
        return

    # Build archive destination
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    archive_dir = research_dir / "runs" / f"archive-{ts}"
    archive_dir.mkdir(parents=True, exist_ok=True)

    moved: list[str] = []
    for src in to_move:
        dst = archive_dir / src.name
        shutil.move(str(src), str(dst))
        moved.append(src.name)

    if has_temp:
        dst_temp = archive_dir / "temp"
        shutil.move(str(temp_dir), str(dst_temp))
        # Re-create empty temp dir so the vault layout stays intact
        temp_dir.mkdir(exist_ok=True)
        moved.append("temp/")

    data = {
        "archived": True,
        "archive_dir": str(archive_dir),
        "moved_files": moved,
    }
    _emit_success(data, json_mode=json_output, vault=str(vault.root))


# ── search ────────────────────────────────────────────────────────────────────

def search_cmd(
    query: str = typer.Argument("", help="Search query (empty = list/filter)"),
    tag: str | None = typer.Option(None, "--tag", help="Filter to notes tagged with this value"),
    note_type: str | None = typer.Option(None, "--type", help="Filter by note type (e.g. interim)"),
    top_k: int = typer.Option(20, "--top-k", "-k", help="Max results"),
    include_body: bool = typer.Option(
        False, "--include-body", help="Include each note's full body text in results"
    ),
    raw: bool = typer.Option(
        False, "--raw",
        help="Return fetched bodies UNFENCED (for gates that match source text).",
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="Emit JSON"),
) -> None:
    """Search or list vault notes.

    Empty QUERY with --tag/--type: plain metadata filter (no FTS, no reranker).
    Non-empty QUERY: FTS5 keyword search, optionally filtered by tag/type.

    Emits the canonical Envelope with `data.results` — a JSON array of note
    summaries {id, title, type, tags, path, status, url}. With --include-body
    each result also carries its full `body` text.
    """
    vault = _discover_vault()
    notes_dir = vault.notes_dir

    if not notes_dir.exists():
        _emit_success(
            {"results": [], "count": 0, "query": query, "tag": tag, "type": note_type},
            json_mode=json_output, count=0, vault=str(vault.root),
        )
        return

    # ── Phase 1: collect candidate note files ──────────────────────────────
    # Always use disk-glob + frontmatter so results match the filesystem
    # without requiring a DB sync step. This is correct for both the empty-
    # query (list) path and as a pre-filter before FTS scoring.
    candidates: list[dict[str, Any]] = []
    for md_path in sorted(notes_dir.glob("*.md")):
        fm = _parse_note_frontmatter(md_path)
        note_id = fm.get("id") or md_path.stem
        note_tags: list[str] = fm.get("tags") or []
        n_type: str = fm.get("type") or "note"

        # Metadata filters
        if tag and tag not in note_tags:
            continue
        if note_type and n_type != note_type:
            continue

        candidates.append({
            "id": note_id,
            "title": fm.get("title") or md_path.stem,
            "type": n_type,
            "tags": note_tags,
            "path": str(md_path),
            "status": fm.get("status") or "draft",
            "url": fm.get("source") or "",
            "_body_path": md_path,
        })

    # ── Phase 2: FTS scoring for non-empty queries ─────────────────────────
    results: list[dict[str, Any]] = []
    if query.strip():
        q_lower = query.lower()
        scored: list[tuple[float, dict[str, Any]]] = []
        for note in candidates:
            try:
                body = note["_body_path"].read_text(encoding="utf-8").lower()
            except Exception:
                body = ""
            # Simple term-frequency score (no LLM, no reranker — keeps smoke test cheap)
            terms = q_lower.split()
            score = sum(body.count(t) for t in terms) / max(len(body), 1)
            scored.append((score, note))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [n for sc, n in scored[:top_k] if sc > 0]
        # If all scores are 0, include them all (query had no hits but we still list)
        if not results:
            results = [n for _sc, n in scored[:top_k]]
    else:
        results = candidates[:top_k]

    # Attach body if requested, then strip the internal helper key. The body is
    # frontmatter-stripped (matching `note show`) so downstream skills get clean
    # evidence text, not raw YAML.
    clean: list[dict[str, Any]] = []
    any_fenced = False
    for n in results:
        body_path: Path = n["_body_path"]
        item = {k: v for k, v in n.items() if k != "_body_path"}
        if include_body:
            try:
                from bad_research.core.frontmatter import parse_frontmatter
                meta, body_text = parse_frontmatter(body_path.read_text(encoding="utf-8"))
                # Same fence as `note show`. This path is NOT decorative: the
                # step-8 corpus-critic skill runs `bad search … --include-body -j`
                # and the CLI cheat-sheet advertises it to every agent, so
                # fencing only `note show` would have left attacker page text
                # reaching a Bash-holding agent through a shipped path — with
                # the sibling command's fence making the gap look covered.
                # parse_frontmatter returns a NoteMeta model, not a dict.
                src = getattr(meta, "source", None)
                if src and not raw:
                    from bad_research.quality.injection import wrap_untrusted

                    body_text = wrap_untrusted(body_text, source_url=str(src),
                                               include_preamble=False)
                    any_fenced = True
                item["body"] = body_text
            except Exception:
                item["body"] = ""
        clean.append(item)

    data = {"results": clean, "count": len(clean), "query": query, "tag": tag, "type": note_type}
    if include_body and any_fenced:
        # Preamble ONCE for the whole payload, not per body — see wrap_untrusted.
        from bad_research.quality.injection import INJECTION_PREAMBLE

        data["untrusted_notice"] = INJECTION_PREAMBLE
    _emit_success(data, json_mode=json_output, count=len(clean), vault=str(vault.root))


# ── fetch ──────────────────────────────────────────────────────────────────────

def _normalize_fetch_result(
    url: str, *, tier_max: int | None, instruction: str | None
) -> dict[str, Any]:
    """Fetch + clean `url` and return a normalized {title, body, metadata, ...} dict.

    Default path (no tier/instruction args): the keyless content pipeline
    `web.content.fetch_clean` — deterministic, SSRF-guarded, no model. When
    `--tier-max`/`--instruction` is set, route through the Tier 0→3 browse
    ladder (`browse.fetch_tiered`) exactly as `core.fetcher.fetch_and_save`
    does, so hard (JS/login/anti-bot) pages can escalate. Both shapes (the
    fetch_clean dict and the ladder's WebResult) collapse to the SAME normalized
    dict here.

    The SSRF guard runs BEFORE any network call on both paths — a
    private/loopback/metadata URL raises SSRFError, which the caller surfaces.
    """
    from bad_research.core.fetcher import assert_url_safe

    # SSRF choke point — refuse internal targets before the first byte.
    assert_url_safe(url)

    use_ladder = tier_max is not None or instruction is not None
    if use_ladder:
        from bad_research.browse import fetch_tiered

        res = fetch_tiered(
            url,
            tier_max=tier_max if tier_max is not None else 3,
            instruction=instruction,
        )
        meta = dict(res.metadata or {})
        return {
            "title": res.title or meta.get("title") or "",
            "body": res.content or "",
            "metadata": meta,
            "published_date": meta.get("published_date"),
            "links": getattr(res, "links", []) or [],
        }

    from bad_research.web.content.fetch_clean import fetch_clean

    d = fetch_clean(url)
    meta = dict(d.get("metadata") or {})
    return {
        "title": meta.get("title") or "",
        "body": d.get("markdown") or "",
        "metadata": meta,
        "published_date": d.get("published_date"),
        "links": d.get("links") or [],
    }


def fetch_cmd(
    url: str = typer.Argument(..., help="URL to fetch, clean, and store as a vault note"),
    tag: str = typer.Option(..., "--tag", help="Vault tag to attach to the stored note"),
    tier_max: int | None = typer.Option(
        None, "--tier-max",
        help="Fetch-tier ceiling (0→3 browse-ladder escalation). Omit for the "
             "keyless deterministic content pipeline (Tier 0).",
    ),
    suggested_by: str | None = typer.Option(
        None, "--suggested-by",
        help="Note id whose citation chain led here (records provenance + a vault "
             "graph edge for primary-source chasing).",
    ),
    suggested_by_reason: str | None = typer.Option(
        None, "--suggested-by-reason",
        help="One-line reason the suggesting note pointed at this URL.",
    ),
    instruction: str | None = typer.Option(
        None, "--instruction",
        help="Typed-extract / agentic-browse instruction for the Tier 2-3 ladder "
             "rungs (implies the browse ladder).",
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="Emit JSON"),
) -> None:
    """Fetch a URL, clean it, and store the result as a tagged vault note.

    The core CORPUS bridge the fetcher subagent + skills (steps 2/5/13/16, 11.5)
    call. Uses the keyless content pipeline (`web.content.fetch_clean`) by
    default; `--tier-max`/`--instruction` route through the Tier 0→3 browse
    ladder so hard pages escalate. The SSRF guard refuses private/loopback/
    metadata URLs before any fetch runs.

    Provenance: `--suggested-by <note-id>` records the citing note in
    frontmatter AND embeds a `[[note-id]]` wiki-link in the body so the vault
    graph carries the citation-ancestry edge the width-sweep clustering uses.

    Emits the canonical Envelope with `data` = {note_id, url, title,
    word_count, tag, suggested_by, ...}.
    """
    from bad_research.core.fetcher import SSRFError
    from bad_research.core.note import write_note
    from bad_research.core.vault import VaultError

    try:
        vault = _discover_vault()
    except VaultError as exc:
        _emit_error(str(exc), json_mode=json_output, code="NO_VAULT")
        raise typer.Exit(code=1) from exc

    try:
        norm = _normalize_fetch_result(url, tier_max=tier_max, instruction=instruction)
    except SSRFError as exc:
        # The SSRF guard refusal — surface it cleanly (the skills rely on this).
        _emit_error(str(exc), json_mode=json_output, code="SSRF_REFUSED")
        raise typer.Exit(code=1) from exc
    except Exception as exc:  # network/parse failure — typed error, never a stacktrace
        _emit_error(f"fetch failed: {exc}", json_mode=json_output, code="FETCH_ERROR")
        raise typer.Exit(code=1) from exc

    body = norm["body"]
    if not body.strip():
        _emit_error(
            f"no content extracted from {url!r} (paywall / empty / unfetchable)",
            json_mode=json_output, code="EMPTY_CONTENT",
        )
        raise typer.Exit(code=1)

    title = norm["title"] or url
    meta = norm["metadata"]
    from urllib.parse import urlsplit

    extra: dict[str, Any] = {
        "source": url,
        "source_domain": urlsplit(url).netloc,
        "fetched_at": datetime.now(UTC).isoformat(),
        "fetch_provider": "fetch_clean" if (tier_max is None and instruction is None) else "tiered",
    }
    if norm.get("published_date"):
        extra["published"] = norm["published_date"]
    if suggested_by:
        extra["suggested_by"] = suggested_by
        if suggested_by_reason:
            extra["suggested_by_reason"] = suggested_by_reason

    # Provenance edge: embed a [[suggesting-note]] wiki-link so sync indexes the
    # citation-ancestry edge in the vault graph (width-sweep clusters on it).
    note_body = body
    if suggested_by:
        reason = f" — {suggested_by_reason}" if suggested_by_reason else ""
        note_body = f"{body}\n\n> Suggested by [[{suggested_by}]]{reason}\n"

    note_path = write_note(
        vault.notes_dir,
        title=title,
        body=note_body,
        tags=[tag] if tag else [],
        status="draft",
        note_type="note",  # fetched sources are plain notes — the type the corpus
                            # survey / draft subagents count (NoteType has no 'source';
                            # the survey applies NO type filter, it counts by tag).
        source=url,
        extra_frontmatter=extra,
    )
    note_id = note_path.stem

    data = {
        "note_id": note_id,
        "url": url,
        "title": title,
        "word_count": len(body.split()),
        "tag": tag,
        "path": str(note_path.relative_to(vault.root)),
        "tier_max": tier_max,
        "suggested_by": suggested_by,
        "published_date": norm.get("published_date"),
        "source_domain": extra["source_domain"],
        "language": meta.get("language"),
    }
    _emit_success(data, json_mode=json_output, vault=str(vault.root))


# ── lint ──────────────────────────────────────────────────────────────────────

_LINT_RULES: dict[str, str] = {
    "wrapper-report": (
        "Final report exists and has at least one citation marker "
        "([[note-id]] wikilink, [^…], [Source …], or [N])"
    ),
    "locus-coverage": (
        "research/loci.json exists and every locus id appears in the final report"
    ),
    "scaffold-prompt": (
        "research/scaffold.md exists and contains a non-empty 'User Prompt' section"
    ),
    "patch-surgery": (
        "research/patch-log.json is valid JSON with the canonical patch-log keys "
        "(total_findings / applied / skipped / conflicts / orchestrator_escalated; "
        "legacy hunks/patches also accepted) (or absent on light tier)"
    ),
}

_ALL_RULES = list(_LINT_RULES)

# Citation markers the wrapper-report rule recognises. `[[note-id]]` wikilink is the
# DOCUMENTED DEFAULT citation_style (bad-research-1-decompose §citation_style), so it
# MUST count — a report carrying only wikilinks is cited, not uncited (issue #20).
_CITATION_RE = re.compile(r"\[\[[^\]]+\]\]|\[\^[^\]]+\]|\[Source[^\]]*\]|\[\d+\]", re.IGNORECASE)

# The canonical patch-log schema the step-14 patcher skill mandates (and forbids
# inventing alternates for). The lint rule must accept this shape, not only the
# legacy hunks/patches keys (issue #20).
_PATCH_LOG_CANONICAL_KEYS = frozenset(
    {"total_findings", "applied", "skipped", "conflicts", "orchestrator_escalated"}
)


def _lint_wrapper_report(research_dir: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    # Find any final_report file
    notes_dir = research_dir / "notes"
    reports = list(notes_dir.glob("final_report_*.md")) if notes_dir.exists() else []
    if not reports:
        issues.append({"severity": "error", "rule": "wrapper-report",
                       "message": "No final_report_<vault_tag>.md found in research/notes/"})
        return issues
    # Check for a citation-like marker
    for rpt in reports:
        body = rpt.read_text(encoding="utf-8")
        if not _CITATION_RE.search(body):
            issues.append({"severity": "warning", "rule": "wrapper-report",
                           "message": f"{rpt.name} has no citation markers"})
    return issues


def _lint_locus_coverage(research_dir: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    loci_path = research_dir / "loci.json"
    if not loci_path.exists():
        # Absence is fine on agentic-fast/light (no step 4)
        return [{"severity": "info", "rule": "locus-coverage",
                 "message": "research/loci.json absent (ok for agentic-fast/light tiers)"}]
    try:
        loci = json.loads(loci_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [{"severity": "error", "rule": "locus-coverage",
                 "message": f"research/loci.json is not valid JSON: {exc}"}]

    # Normalise: list of {id:...} or list of strings
    locus_ids: list[str] = []
    for item in (loci if isinstance(loci, list) else loci.get("loci", [])):
        lid = (item.get("id") or item.get("name") or "") if isinstance(item, dict) else str(item)
        if lid:
            locus_ids.append(lid)

    if not locus_ids:
        return issues

    notes_dir = research_dir / "notes"
    reports = list(notes_dir.glob("final_report_*.md")) if notes_dir.exists() else []
    if not reports:
        return [{"severity": "error", "rule": "locus-coverage",
                 "message": "No final report to check locus coverage against"}]

    report_body = reports[0].read_text(encoding="utf-8").lower()
    for lid in locus_ids:
        if lid.lower() not in report_body:
            issues.append({"severity": "warning", "rule": "locus-coverage",
                           "message": f"Locus '{lid}' not found in final report"})
    return issues


def _lint_scaffold_prompt(research_dir: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    scaffold = research_dir / "scaffold.md"
    if not scaffold.exists():
        issues.append({"severity": "error", "rule": "scaffold-prompt",
                       "message": "research/scaffold.md does not exist"})
        return issues
    body = scaffold.read_text(encoding="utf-8")
    # Look for a User Prompt section header followed by non-empty content
    match = re.search(r"#+\s*User Prompt\b.*?\n+(.+)", body, re.IGNORECASE | re.DOTALL)
    if not match or not match.group(1).strip():
        issues.append({"severity": "error", "rule": "scaffold-prompt",
                       "message": "scaffold.md exists but 'User Prompt' section is empty or missing"})
    return issues


def _lint_patch_surgery(research_dir: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    patch_log = research_dir / "patch-log.json"
    if not patch_log.exists():
        # Absence is acceptable on light/agentic-fast tiers
        return [{"severity": "info", "rule": "patch-surgery",
                 "message": "research/patch-log.json absent (ok for light/agentic-fast tiers)"}]
    try:
        data = json.loads(patch_log.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [{"severity": "error", "rule": "patch-surgery",
                 "message": f"research/patch-log.json is not valid JSON: {exc}"}]
    has_canonical = isinstance(data, dict) and bool(_PATCH_LOG_CANONICAL_KEYS & data.keys())
    has_legacy = isinstance(data, dict) and bool(data.get("hunks") or data.get("patches"))
    if not (has_canonical or has_legacy):
        issues.append({"severity": "warning", "rule": "patch-surgery",
                       "message": ("patch-log.json lacks the canonical patch-log keys "
                                   "(total_findings/applied/skipped/conflicts/"
                                   "orchestrator_escalated) or legacy hunks/patches")})
    return issues


_RULE_CHECKERS = {
    "wrapper-report": _lint_wrapper_report,
    "locus-coverage": _lint_locus_coverage,
    "scaffold-prompt": _lint_scaffold_prompt,
    "patch-surgery": _lint_patch_surgery,
}


def lint_cmd(
    rule: str | None = typer.Option(None, "--rule", help=(
        "Run a specific rule: wrapper-report | locus-coverage | scaffold-prompt | patch-surgery. "
        "Omit to run all rules."
    )),
    json_output: bool = typer.Option(False, "--json", "-j", help="Emit JSON"),
) -> None:
    """Run deterministic lint rules against the current vault's research artifacts.

    Each rule checks for the presence / content of a canonical pipeline artifact.
    Exits non-zero if any rule produces an 'error'-severity issue.
    """
    vault = _discover_vault()
    research_dir = vault.research_dir

    rules_to_run = [rule] if rule else _ALL_RULES
    unknown = [r for r in rules_to_run if r not in _RULE_CHECKERS]
    if unknown:
        _emit_error(
            f"unknown rule(s): {', '.join(unknown)}. Valid: {', '.join(_ALL_RULES)}",
            json_mode=json_output, code="UNKNOWN_RULE",
        )
        raise typer.Exit(code=1)

    all_issues: list[dict[str, Any]] = []
    for r in rules_to_run:
        all_issues.extend(_RULE_CHECKERS[r](research_dir))

    has_error = any(i["severity"] == "error" for i in all_issues)
    data = {
        "rules_run": rules_to_run,
        "issues": all_issues,
        "issue_count": len(all_issues),
    }
    # An error-severity issue means the lint FAILED — surface ok=false + exit 1.
    if has_error:
        if json_output:
            env = envelope_error("lint found error-severity issues", code="LINT_FAILED")
            env.data = data
            output(env, json_mode=True)
        else:
            _emit_success(data, json_mode=False)
        raise typer.Exit(code=1)

    _emit_success(data, json_mode=json_output, vault=str(vault.root))


# ── note (subgroup with 'show' subcommand) ────────────────────────────────────

note_app = typer.Typer(
    name="note",
    help="Note management commands.",
    no_args_is_help=True,
)


def _fence_if_fetched(note: Any, *, raw: bool) -> str:
    """Fence a FETCHED page body as untrusted before it reaches an agent.

    This is the one seam all 16 agents already go through to read a source, so
    fencing here covers every one of them — and every agent added later —
    instead of pasting a prose warning into each prompt constant, where it
    silently rots the next time an agent is added (15 of 16 lacked it).

    Only notes carrying a `source` URL are fenced: those are attacker-controlled
    page text. Agent-authored interim notes (drafts, digests, critic findings)
    are our own content and stay clean, so the fence keeps meaning something.

    `raw=True` is reserved for programmatic consumers that match against source
    text. (Today's gates do not reach this seam — the recitation map is built
    from `bad search` and verify-citations reads `research/notes/*.md` directly
    — so the flag exists so that fencing can never silently corrupt a future
    text-matching consumer, not because one calls it now.)
    """
    body = note.body or ""
    if raw:
        return body
    # `NoteMeta` has no `url` field and ignores extras, so `source` is the only
    # signal — both write paths (vault_cmds `note new`, funnel/filter) set it.
    source_url = getattr(note.meta, "source", None)
    if not source_url:
        return body
    from bad_research.quality.injection import wrap_untrusted

    # Markers only. The ~700-char preamble is emitted ONCE per envelope by the
    # caller: prefixing it to every body pushed the real source text past the
    # read window of any agent told to truncate (the step-4 loci-analyst reads
    # "the first ~400 chars", which the preamble alone would entirely fill).
    return wrap_untrusted(body, source_url=str(source_url), include_preamble=False)


def _read_one_note(vault: Vault, note_id: str, *, raw: bool = False) -> dict[str, Any]:
    """Resolve a note by id (notes_dir then temp_dir) and return its payload.

    Returns {ok:False, error, id} if the note is missing or unreadable so the
    batch caller can report per-note status without aborting the whole request.
    """
    from bad_research.core.note import read_note

    note_path: Path | None = None
    for d in (vault.notes_dir, vault.temp_dir):
        candidate = d / f"{note_id}.md"
        if candidate.exists():
            note_path = candidate
            break

    if note_path is None:
        return {"ok": False, "error": f"Note '{note_id}' not found", "id": note_id}

    try:
        note = read_note(note_path, vault.root)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "id": note_id}

    return {
        "ok": True,
        "id": note.meta.id or note_id,
        "title": note.meta.title,
        "tags": note.meta.tags or [],
        "type": note.meta.type,
        "status": note.meta.status,
        "body": _fence_if_fetched(note, raw=raw),
        "path": note.path,
        "word_count": note.word_count,
        "meta": note.meta.model_dump(mode="json", exclude_none=True),
    }


@note_app.command("show")
def note_show_cmd(
    note_ids: list[str] = typer.Argument(..., help="One or more note ids (stems of the .md files)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Emit JSON"),
    raw: bool = typer.Option(
        False, "--raw",
        help="Return fetched bodies UNFENCED (for gates that match source text).",
    ),
) -> None:
    """Show one or more vault notes by id.

    Reads research/notes/<id>.md (or research/temp/<id>.md as fallback) for each
    id, parses frontmatter, and emits the canonical Envelope with
    `data.notes` — a list of per-note payloads {id, title, tags, type, status,
    body, path, word_count, meta}. Exits non-zero if ANY requested id is missing.

    A note carrying a `source` URL is FETCHED page text — attacker-controlled —
    so its body is fenced with the untrusted-content preamble before it reaches
    an agent. Pass `--raw` to get the unfenced body for programmatic matching.
    """
    from bad_research.core.vault import VaultError

    try:
        vault = _discover_vault()
    except VaultError as exc:
        _emit_error(str(exc), json_mode=json_output, code="NO_VAULT")
        raise typer.Exit(code=1) from exc

    notes = [_read_one_note(vault, nid, raw=raw) for nid in note_ids]
    any_missing = any(not n["ok"] for n in notes)

    data = {"notes": notes, "count": len(notes)}
    # Preamble ONCE per envelope, not per body — the bodies carry only the
    # BEGIN/END markers so a truncating reader still reaches real source text.
    if not raw and any("<BEGIN UNTRUSTED CONTENT>" in str(n.get("body", "")) for n in notes):
        from bad_research.quality.injection import INJECTION_PREAMBLE

        data["untrusted_notice"] = INJECTION_PREAMBLE
    if any_missing:
        if json_output:
            env = envelope_error("one or more notes not found", code="NOTE_NOT_FOUND")
            env.data = data
            env.count = len(notes)
            output(env, json_mode=True)
        else:
            _emit_success(data, json_mode=False)
        raise typer.Exit(code=1)

    _emit_success(data, json_mode=json_output, count=len(notes), vault=str(vault.root))


@note_app.command("new")
def note_new_cmd(
    title: str = typer.Argument(..., help="Note title"),
    tag: list[str] = typer.Option(None, "--tag", "--add-tag", help="Tag(s) to attach (repeatable)"),
    note_type: str = typer.Option("note", "--type", help="Note type (e.g. interim, source-analysis)"),
    body: str = typer.Option("", "--body", help="Inline note body markdown"),
    body_file: str = typer.Option(None, "--body-file", help="Read the body from this file ('-' = stdin)"),
    note_id: str = typer.Option(None, "--id", help="Explicit note id (default: slug of the title)"),
    summary: str = typer.Option(None, "--summary", help="One-line summary for the frontmatter"),
    status: str = typer.Option("draft", "--status", help="Lifecycle status (draft|review|evergreen|...)"),
    source: str = typer.Option(None, "--source", help="Source URL recorded in frontmatter"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Emit JSON"),
) -> None:
    """Create a new vault note (markdown + frontmatter) under research/notes/.

    The programmatic counterpart to `bad fetch` (which grounds a URL) — used by the
    depth-investigator / source-analyst subagents to persist interim and
    source-analysis notes. Returns the canonical Envelope with
    `data` = {note_id, path, title, type, status}.
    """
    import sys

    from bad_research.core.note import write_note
    from bad_research.core.vault import VaultError

    try:
        vault = _discover_vault()
    except VaultError as exc:
        _emit_error(str(exc), json_mode=json_output, code="NO_VAULT")
        raise typer.Exit(code=1) from exc

    note_body = body
    if body_file:
        try:
            note_body = sys.stdin.read() if body_file == "-" else Path(body_file).read_text(encoding="utf-8")
        except OSError as exc:
            _emit_error(f"cannot read --body-file {body_file!r}: {exc}",
                        json_mode=json_output, code="BODY_FILE_ERROR")
            raise typer.Exit(code=1) from exc

    path = write_note(
        vault.notes_dir, title, note_body,
        note_id=note_id, tags=list(tag or []), status=status,
        note_type=note_type, source=source, summary=summary,
    )
    data = {
        "note_id": path.stem,
        "path": str(path.relative_to(vault.root)),
        "title": title,
        "type": note_type,
        "status": status,
    }
    _emit_success(data, json_mode=json_output, vault=str(vault.root))


@note_app.command("update")
def note_update_cmd(
    note_id: str = typer.Argument(..., help="Note id (stem of the .md file)"),
    summary: str = typer.Option(None, "--summary", help="Set/replace the one-line summary"),
    add_tag: list[str] = typer.Option(None, "--add-tag", "--tag", help="Tag(s) to add (repeatable; deduped)"),
    status: str = typer.Option(None, "--status", help="Set the lifecycle status"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Emit JSON"),
) -> None:
    """Patch a note's frontmatter in place (summary / tags / status).

    Reads research/notes/<id>.md (or research/temp/<id>.md), updates only the
    fields passed, and rewrites the file with its body untouched — the curation
    counterpart used by the per-session curation pass and the source-analyst.
    Returns `data` = {note_id, path, summary, status, tags}.
    """
    from bad_research.core.frontmatter import render_note
    from bad_research.core.note import read_note
    from bad_research.core.vault import VaultError

    try:
        vault = _discover_vault()
    except VaultError as exc:
        _emit_error(str(exc), json_mode=json_output, code="NO_VAULT")
        raise typer.Exit(code=1) from exc

    note_path: Path | None = None
    for d in (vault.notes_dir, vault.temp_dir):
        candidate = d / f"{note_id}.md"
        if candidate.exists():
            note_path = candidate
            break
    if note_path is None:
        _emit_error(f"Note '{note_id}' not found", json_mode=json_output, code="NOTE_NOT_FOUND")
        raise typer.Exit(code=1)

    note = read_note(note_path, vault.root)
    meta = note.meta
    if summary is not None:
        meta.summary = summary
    if status is not None:
        from bad_research.models.note import NoteStatus
        try:
            meta.status = NoteStatus(status)
        except ValueError as exc:
            valid = ", ".join(s.value for s in NoteStatus)
            _emit_error(f"invalid status {status!r} (valid: {valid})",
                        json_mode=json_output, code="INVALID_STATUS")
            raise typer.Exit(code=1) from exc
    if add_tag:
        existing = list(meta.tags or [])
        for t in add_tag:
            if t not in existing:
                existing.append(t)
        meta.tags = existing

    note_path.write_text(render_note(meta, note.body), encoding="utf-8")
    data = {
        "note_id": meta.id or note_id,
        "path": str(note_path.relative_to(vault.root)),
        "summary": meta.summary,
        "status": meta.status,
        "tags": meta.tags or [],
    }
    _emit_success(data, json_mode=json_output, vault=str(vault.root))
