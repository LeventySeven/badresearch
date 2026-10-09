#!/usr/bin/env bash
# cite-chain.sh — citation chaining over OpenAlex (keyless). Returns pointers, not verdicts.
#
#   bash scripts/cite-chain.sh back  <doi|W-id>            # the works it references (backward)
#   bash scripts/cite-chain.sh fwd   <doi|W-id> [n]        # works citing it, most-cited first (forward)
#   bash scripts/cite-chain.sh rerun <doi|W-id> [n]        # citing works whose text mentions "replication"
#   bash scripts/cite-chain.sh core  <id> <id> [<id>...]   # references shared by several seeds = the field's core
#   bash scripts/cite-chain.sh s2fwd   <doi|arXiv:id> [n]  # Semantic Scholar citers, most-cited first
#   bash scripts/cite-chain.sh s2back  <doi|arXiv:id>      # Semantic Scholar references
#   bash scripts/cite-chain.sh s2rerun <doi|arXiv:id>      # citers whose citing SENTENCE says replicate/reproduce/fail
#
# <id> may be a DOI, an OpenAlex W-id, or an arXiv id (2504.13837 or arXiv:2504.13837).
# COVERAGE: OpenAlex indexes arXiv-only and recent work thinly. Measured 2026-10-10: one paper had 3
# OpenAlex citers and 1,123 on Semantic Scholar; others 1 vs 29, 1 vs 38. `fwd` checks the S2 count
# and prints a COVERAGE line when OpenAlex sees under half of it — then use the s2* modes.
#
# Run it from this skill's directory, or give its full path.
#
# WHY: following references of references found 51% of a large review's sources where the planned
# database search found 30%, at a useful paper every 15 minutes against every 40. Sorting the citing
# papers by their OWN citations surfaces the pivotal ones (Tao); references shared across seeds mark
# the core of a field (Keshav). Failed reruns are cited by few later citers, so look for them INSIDE the
# original's citers. `rerun` matches a word, not a design: read what it returns to learn whether it is one.
#
# Every call prints exactly one state line first, in this skill's taxonomy, and never prints nothing:
#   WORKING  rows follow            EMPTY  the API answered, 0 rows (the only state that licenses "not there")
#   MISSING  the id does not exist  BLOCKED  network down, HTTP error, or an unparseable body
#   EXHAUSTED  rate-limited (HTTP 429) — nothing may be concluded; retry later
set -uo pipefail
API=https://api.openalex.org
mode="${1:-}"; shift || true

get() { timeout 30 curl -sS --max-time 25 -w '\n@@%{http_code}' "$1" 2>&1; }

STATE_PY=$(cat <<'PY'
import sys, json, re
raw = sys.stdin.read(); label = sys.argv[1]
m = re.search(r"@@(\d+)\s*$", raw); code = m.group(1) if m else "000"
body = raw[:m.start()] if m else raw
if code == "429":
    print(f"EXHAUSTED | {label} | http 429 (rate-limited) — retry later; nothing may be concluded"); sys.exit(3)
if code == "404":
    print(f"MISSING | {label} | http 404 — no such work"); sys.exit(4)
if code != "200":
    why = body.strip().splitlines()[-1][:120] if body.strip() else "no response"
    print(f"BLOCKED | {label} | http {code} ({why})"); sys.exit(5)
try:
    d = json.loads(body)
except Exception:
    print(f"BLOCKED | {label} | http 200 but the body was not JSON ({body.strip()[:80]!r})"); sys.exit(5)
mode = sys.argv[2]
if mode == "id":
    wid = (d.get("id") or "").rsplit("/", 1)[-1]
    print(wid if wid else "MISSING"); sys.exit(0 if wid else 4)
rows = d.get("results")
if rows is None:
    refs = d.get("referenced_works") or []
    print(("WORKING" if refs else "EMPTY") + f" | {label} | {len(refs)} references")
    for r in refs: print(r)
    sys.exit(0)
total = (d.get("meta") or {}).get("count", len(rows))
print(("WORKING" if rows else "EMPTY") + f" | {label} | {total} total, showing {len(rows)}")
for w in rows:
    wid = (w.get("id") or "").rsplit("/", 1)[-1]
    name = (w.get("display_name") or "")[:110]
    print(f"{w.get('cited_by_count', 0):>6}  {w.get('publication_year', '')}  {wid}  {w.get('doi') or ''}  {name}")
PY
)
state() { printf '%s' "$1" | python3 -c "$STATE_PY" "$2" "$3"; }   # body+@@code, label, mode
S2_PY=$(cat <<'PY'
import sys, json, re, subprocess
mode, raw, n = sys.argv[1], sys.argv[2], int(sys.argv[3] or 0)
x = re.sub(r"^https?://(dx\.)?doi\.org/", "", raw); x = re.sub(r"^(doi|DOI):", "", x)
if re.match(r"^(arXiv|arxiv):", x): sid = "arXiv:" + x.split(":", 1)[1]
elif re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", x): sid = "arXiv:" + x
elif x.startswith("10.48550/arXiv."): sid = "arXiv:" + x.split("arXiv.", 1)[1]
elif x.startswith("10."): sid = "DOI:" + x
else:
    print(f"MISSING | {mode} | {raw}: Semantic Scholar needs a DOI or an arXiv id, not an OpenAlex W-id"); sys.exit(4)
API = "https://api.semanticscholar.org/graph/v1/paper/"
def get(url):
    import time
    for wait in (0, 4, 10):              # keyless S2 throttles bursts; two short retries, then EXHAUSTED
        time.sleep(wait)
        r = subprocess.run(["curl", "-sS", "--max-time", "40", "-w", "\n@@%{http_code}", url], capture_output=True, text=True)
        body, _, code = r.stdout.rpartition("\n@@")
        if code.strip() != "429": break
    return code.strip() or "000", body
def fail(code, body, label):
    if code == "429": print(f"EXHAUSTED | {label} | http 429 (Semantic Scholar rate limit) — wait and retry; nothing may be concluded"); sys.exit(3)
    if code == "404": print(f"MISSING | {label} | http 404 — Semantic Scholar has no {sid}"); sys.exit(4)
    print(f"BLOCKED | {label} | http {code} ({body.strip()[:100]!r})"); sys.exit(5)
if mode == "count":
    code, body = get(API + sid + "?fields=citationCount")
    if code != "200": print(f"unknown ({code})"); sys.exit(1)
    print(json.loads(body).get("citationCount", 0)); sys.exit(0)
edge = "references" if mode == "s2back" else "citations"
key = "citedPaper" if edge == "references" else "citingPaper"
rows, off = [], 0
while True:
    fields = "title,year,citationCount,externalIds" + (",contexts" if mode == "s2rerun" else "")
    code, body = get(f"{API}{sid}/{edge}?fields={fields}&limit=1000&offset={off}")
    if code != "200": fail(code, body, f"{mode} {sid}")
    try: d = json.loads(body)
    except Exception: print(f"BLOCKED | {mode} {sid} | http 200 but not JSON"); sys.exit(5)
    for e in d.get("data") or []:
        p = e.get(key) or {}
        if p.get("title"): rows.append((p, e.get("contexts") or []))
    if d.get("next") is None or len(rows) >= 5000: break
    off = d["next"]
if mode == "s2rerun":
    pat = re.compile(r"replicat|reproduc|re-?ran|rerun|fail(ed|s)? to|did not hold|contrary to|challeng", re.I)
    rows = [(p, [c for c in cs if pat.search(c)]) for p, cs in rows]
    rows = [(p, cs) for p, cs in rows if cs]
rows.sort(key=lambda t: -(t[0].get("citationCount") or 0))
label = {"s2fwd": f"forward from {sid}", "s2back": f"backward from {sid}", "s2rerun": f"citers of {sid} whose citing sentence says replicate/reproduce/fail"}[mode]
print(("WORKING" if rows else "EMPTY") + f" | {label} | {len(rows)} total (Semantic Scholar), showing {min(len(rows), n or 15)}")
for p, cs in rows[: (n or 15)]:
    ex = p.get("externalIds") or {}
    pid = ("arXiv:" + ex["ArXiv"]) if ex.get("ArXiv") else (("DOI:" + ex["DOI"]) if ex.get("DOI") else "")
    print(f"{p.get('citationCount') or 0:>6}  {p.get('year') or ''}  {pid}  {(p.get('title') or '')[:110]}")
    for c in cs[:2]: print(f"          ↳ \"{c.strip()[:220]}\"")
PY
)
s2() { python3 -c "$S2_PY" "$1" "$2" "${3:-0}"; }


# id resolution keeps the reason: a network failure is BLOCKED, only a real 404 is MISSING.
resolve() {
  local x="$1"
  case "$x" in
    W[0-9]*) echo "$x"; return 0 ;;
    https://openalex.org/W*) echo "${x##*/}"; return 0 ;;
  esac
  x="${x#https://doi.org/}"; x="${x#https://dx.doi.org/}"; x="${x#doi:}"; x="${x#DOI:}"
  case "$x" in arXiv:*|arxiv:*) x="10.48550/arXiv.${x#*:}" ;; [0-9][0-9][0-9][0-9].[0-9]*) x="10.48550/arXiv.$x" ;; esac
  state "$(get "$API/works/doi:$x?select=id")" "resolve $x" id
}

need_id() {
  [ -z "${1:-}" ] && { sed -n '3,6p' "$0"; exit 2; }
  local r; r=$(resolve "$1"); local rc=$?
  if [ $rc -ne 0 ] || [ -z "$r" ] || [ "${r#W}" = "$r" ]; then printf '%s\n' "$r"; exit 0; fi
  printf '%s' "$r"
}

case "$mode" in back|fwd|rerun|s2fwd|s2back|s2rerun) [ -z "${1:-}" ] && { sed -n '3,9p' "$0"; exit 2; } ;; esac

case "$mode" in
  back)  id=$(need_id "${1:-}") || exit $?; case "$id" in W*) ;; *) echo "$id"; exit 0 ;; esac
         state "$(get "$API/works/$id?select=referenced_works")" "backward from $id" list ;;
  fwd)   id=$(need_id "${1:-}") || exit $?; case "$id" in W*) ;; *) echo "$id"; exit 0 ;; esac
         out=$(state "$(get "$API/works?filter=cites:$id&sort=cited_by_count:desc&per-page=${2:-15}&select=id,doi,display_name,cited_by_count,publication_year")" "forward from $id" list); rc=$?
         printf '%s\n' "$out"
         oa=$(printf '%s\n' "$out" | head -1 | sed -n 's/.*| \([0-9][0-9]*\) total.*/\1/p'); oa=${oa:-0}
         case "${1:-}" in W[0-9]*|https://openalex.org/W*) ;; *)
           if s2n=$(s2 count "$1" 2>/dev/null); then
             [ "$s2n" -gt $((2 * oa + 5)) ] && echo "COVERAGE | OpenAlex sees $oa citers, Semantic Scholar $s2n — this index is thin here; run: cite-chain.sh s2fwd $1"
           else
             echo "COVERAGE | unchecked (Semantic Scholar: $s2n) — OpenAlex is thin on arXiv-era work; if this list looks short, run: cite-chain.sh s2fwd $1"
           fi ;;
         esac
         exit $rc ;;
  s2fwd|s2back|s2rerun) s2 "$mode" "$1" "${2:-15}" ;;
  rerun) id=$(need_id "${1:-}") || exit $?; case "$id" in W*) ;; *) echo "$id"; exit 0 ;; esac
         state "$(get "$API/works?filter=cites:$id&search=replication&per-page=${2:-15}&select=id,doi,display_name,cited_by_count,publication_year")" "citers of $id mentioning replication" list ;;
  core)
    [ "$#" -lt 2 ] && { echo "usage: cite-chain.sh core <id> <id> [<id>...]"; exit 2; }
    tmp=$(mktemp); trap 'rm -f "$tmp"' EXIT; bad=0
    for x in "$@"; do
      r=$(resolve "$x"); rc=$?
      if [ $rc -ne 0 ] || [ "${r#W}" = "$r" ]; then echo "seed $x -> $r"; bad=1; continue; fi
      out=$(state "$(get "$API/works/$r?select=referenced_works")" "seed $r" list); rc=$?
      echo "seed $r -> $(printf '%s\n' "$out" | head -1)"
      [ $rc -ne 0 ] && { bad=1; continue; }
      printf '%s\n' "$out" | tail -n +2 | sort -u | sed "s|^|$r |" >> "$tmp"
    done
    python3 - "$tmp" "$bad" <<'PY'
import sys, collections
path, bad = sys.argv[1], sys.argv[2] == "1"
seeds = collections.defaultdict(set)
for line in open(path):
    parts = line.split()
    if len(parts) == 2: seeds[parts[1]].add(parts[0])
n = len({s for v in seeds.values() for s in v})
shared = sorted(((w, len(s)) for w, s in seeds.items() if len(s) > 1), key=lambda t: -t[1])
if bad and n < 2:
    print(f"BLOCKED | core | fewer than two seeds were readable — nothing may be concluded"); sys.exit(0)
state = "WORKING" if shared else "EMPTY"
note = " (some seeds unreadable — see the seed lines above; EMPTY here does not mean none exist)" if bad else ""
print(f"{state} | core across {n} readable seeds | {len(shared)} references shared by 2+ seeds{note}")
for w, k in shared[:30]: print(f"{k} seeds  {w}")
PY
    ;;
  *) sed -n '3,12p' "$0"; exit 2 ;;
esac
