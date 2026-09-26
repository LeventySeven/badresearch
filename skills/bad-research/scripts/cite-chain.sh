#!/usr/bin/env bash
# cite-chain.sh — citation chaining over OpenAlex (keyless). Returns pointers, not verdicts.
#
#   bash scripts/cite-chain.sh back  <doi|W-id>            # the works it references (backward)
#   bash scripts/cite-chain.sh fwd   <doi|W-id> [n]        # works citing it, most-cited first (forward)
#   bash scripts/cite-chain.sh rerun <doi|W-id> [n]        # citing works that mention replication/reproduction
#   bash scripts/cite-chain.sh core  <id> <id> [<id>...]   # references shared by several seeds = the field's core
#
# WHY: following references of references found 51% of a large review's sources where the planned
# database search found 30%, at a useful paper every 15 minutes against every 40. Sorting the citing
# papers by their OWN citations surfaces the pivotal ones (Tao); references shared across seeds mark
# the core of a field (Keshav). Failed reruns are cited by few later citers, so look for them INSIDE the
# original's citers. `rerun` matches the words, not the design: it finds papers that MENTION replication
# — read them to learn whether they are one.
#
# States, per this skill's taxonomy: WORKING (rows printed), EMPTY (the API answered, 0 rows),
# MISSING (the id did not resolve), BLOCKED (HTTP error / no network). Never silence.
set -uo pipefail
API=https://api.openalex.org
mode="${1:-}"; shift || true

resolve() {  # doi or W-id -> W-id, or empty
  local x="$1"
  case "$x" in
    W[0-9]*) echo "$x" ;;
    https://openalex.org/W*) echo "${x##*/}" ;;
    *) x="${x#https://doi.org/}"; x="${x#doi:}"
       timeout 30 curl -sS --max-time 25 "$API/works/doi:$x?select=id" 2>/dev/null \
         | python3 -c 'import sys,json
try: print(json.load(sys.stdin)["id"].rsplit("/",1)[-1])
except Exception: pass' ;;
  esac
}

get() { timeout 30 curl -sS --max-time 25 -w '\n@@%{http_code}' "$1" 2>/dev/null; }

EMIT_PY=$(cat <<'PY'
import sys, json, re
raw = sys.stdin.read(); label = sys.argv[1]
m = re.search(r"@@(\d+)\s*$", raw); code = m.group(1) if m else "000"
body = raw[:m.start()] if m else raw
if code != "200":
    print(f"BLOCKED | {label} | http {code}"); sys.exit(0)
d = json.loads(body)
rows = d.get("results")
if rows is None:  # a single work: its references (backward)
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
emit() { printf '%s' "$1" | python3 -c "$EMIT_PY" "$2"; }   # $1=body+@@code  $2=label

case "$mode" in
  back|fwd|rerun)
    id=$(resolve "${1:-}")
    [ -z "$id" ] && { echo "MISSING | ${1:-<none>} did not resolve to an OpenAlex work"; exit 0; }
    n="${2:-15}"
    case "$mode" in
      back)  emit "$(get "$API/works/$id?select=referenced_works")" "backward from $id" ;;
      fwd)   emit "$(get "$API/works?filter=cites:$id&sort=cited_by_count:desc&per-page=$n&select=id,doi,display_name,cited_by_count,publication_year")" "forward from $id" ;;
      rerun) emit "$(get "$API/works?filter=cites:$id&search=replication&per-page=$n&select=id,doi,display_name,cited_by_count,publication_year")" "citers of $id mentioning replication" ;;
    esac ;;
  core)
    [ "$#" -lt 2 ] && { echo "usage: cite-chain.sh core <id> <id> [<id>...]"; exit 2; }
    ids=(); for x in "$@"; do r=$(resolve "$x"); [ -n "$r" ] && ids+=("$r") || echo "MISSING | $x did not resolve"; done
    [ "${#ids[@]}" -lt 2 ] && { echo "EMPTY | fewer than two seeds resolved"; exit 0; }
    for id in "${ids[@]}"; do get "$API/works/$id?select=referenced_works"; echo; echo "@@@"; done | python3 -c '
import sys, json, re, collections
chunks=[c for c in sys.stdin.read().split("@@@") if c.strip()]
cnt=collections.Counter(); n=0
for c in chunks:
    body=re.sub(r"@@\d+\s*$","",c.strip())
    try: refs=json.loads(body).get("referenced_works") or []
    except Exception: continue
    n+=1; cnt.update(set(refs))
shared=[(w,k) for w,k in cnt.most_common() if k>1]
print(("WORKING" if shared else "EMPTY")+f" | core across {n} seeds | {len(shared)} references shared by 2+ seeds")
for w,k in shared[:30]: print(f"{k} seeds  {w}")' ;;
  *) sed -n '2,8p' "$0"; exit 2 ;;
esac
