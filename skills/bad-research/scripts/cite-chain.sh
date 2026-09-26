#!/usr/bin/env bash
# cite-chain.sh — citation chaining over OpenAlex (keyless). Returns pointers, not verdicts.
#
#   bash scripts/cite-chain.sh back  <doi|W-id>            # the works it references (backward)
#   bash scripts/cite-chain.sh fwd   <doi|W-id> [n]        # works citing it, most-cited first (forward)
#   bash scripts/cite-chain.sh rerun <doi|W-id> [n]        # citing works whose text mentions "replication"
#   bash scripts/cite-chain.sh core  <id> <id> [<id>...]   # references shared by several seeds = the field's core
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

# id resolution keeps the reason: a network failure is BLOCKED, only a real 404 is MISSING.
resolve() {
  local x="$1"
  case "$x" in
    W[0-9]*) echo "$x"; return 0 ;;
    https://openalex.org/W*) echo "${x##*/}"; return 0 ;;
  esac
  x="${x#https://doi.org/}"; x="${x#https://dx.doi.org/}"; x="${x#doi:}"; x="${x#DOI:}"
  state "$(get "$API/works/doi:$x?select=id")" "resolve $x" id
}

need_id() {
  [ -z "${1:-}" ] && { sed -n '3,6p' "$0"; exit 2; }
  local r; r=$(resolve "$1"); local rc=$?
  if [ $rc -ne 0 ] || [ -z "$r" ] || [ "${r#W}" = "$r" ]; then printf '%s\n' "$r"; exit 0; fi
  printf '%s' "$r"
}

case "$mode" in back|fwd|rerun) [ -z "${1:-}" ] && { sed -n '3,6p' "$0"; exit 2; } ;; esac

case "$mode" in
  back)  id=$(need_id "${1:-}") || exit $?; case "$id" in W*) ;; *) echo "$id"; exit 0 ;; esac
         state "$(get "$API/works/$id?select=referenced_works")" "backward from $id" list ;;
  fwd)   id=$(need_id "${1:-}") || exit $?; case "$id" in W*) ;; *) echo "$id"; exit 0 ;; esac
         state "$(get "$API/works?filter=cites:$id&sort=cited_by_count:desc&per-page=${2:-15}&select=id,doi,display_name,cited_by_count,publication_year")" "forward from $id" list ;;
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
  *) sed -n '3,8p' "$0"; exit 2 ;;
esac
