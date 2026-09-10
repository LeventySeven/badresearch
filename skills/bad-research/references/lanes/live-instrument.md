# Lane: live-instrument

## Reach for this when
- The answer is a NUMBER that exists only in a running system — metrics API, dashboard, log stream, database, process timing — and no document states it.
- You are about to size, price, or capacity-plan from a vendor console figure (Render RAM, Hetzner disk, egress GB, hours logged).
- A claim in a doc has a number in it and you need to check whether the number is still true.
- Someone reports a peak, a total, or a count and did not say at what resolution or over what window.

## Commands
All run 2026-09-08 on this machine; output pasted is real.

```bash
# READ-ONLY open. Always the file: URI — a plain path CREATES a 0-byte db on a typo.
sqlite3 "file:$PWD/db.sqlite?mode=ro" "select count(*) from sources;"      # -> 24

# Same metric at two resolutions, one window. This is the core move of the lane.
peak(){ jq -r '.timestamp' history.jsonl | awk -v b=$1 '{print int($1/(b*1000))}' \
        | sort | uniq -c | sort -rn | head -1 | awk -v b=$1 '{printf "%.3f", $1/(b/60)}'; }
peak 60      # -> 11.000 events/min   (60s buckets, 30d window)
peak 3600    # ->  0.333 events/min   (3600s buckets, SAME DATA)

# Same resolution, three windows — the peak moves 5.5x.
# window=1d 60s -> 2/min | window=7d 60s -> 2/min | window=30d 60s -> 11/min

# UNION check. Fetch every page, then count DISTINCT ids against the source's own count.
: > /tmp/pg; cur=""; for p in 1 2 3 4 5; do
  sqlite3 "file:$PWD/db.sqlite?mode=ro" \
    "select source_id||'|'||domain from sources where domain >= '$cur' order by domain limit 5;" >> /tmp/pg
  cur=$(tail -1 /tmp/pg | cut -d'|' -f2); done
wc -l < /tmp/pg; cut -d'|' -f1 /tmp/pg | sort -u | wc -l    # -> 25 rows, 20 distinct, count=24

# CONTROL arm. Treatment minus a no-op of the same shape, 5 reps, report the median.
runs(){ for i in 1 2 3 4 5; do /usr/bin/time -p sqlite3 db.sqlite "$1" 2>&1 \
        | awk '/^real/{print $2}'; done | sort -n | awk '{a[NR]=$1} END{print a[int((NR+1)/2)]}'; }
runs "with recursive s(x) as (select 1 union all select x+1 from s where x<5000000) select count(*) from s;"  # -> 0.36
runs "select 1;"                                                                                             # -> 0.00

# HTTP instrument: status + timing, body discarded, secret never in argv.
printf 'header = "Authorization: Bearer %s"\n' "$TOKEN" | curl -sS -K - -o /dev/null \
  -w 'http=%{http_code} ttfb=%{time_starttransfer}s total=%{time_total}s bytes=%{size_download}\n' \
  --max-time 10 https://api.example.com/metrics       # -> http=200 ttfb=0.343720s total=0.343877s bytes=678
curl -sS -D - -o /dev/null https://api.example.com/x | grep -i '^x-ratelimit'   # paging budget before you page
```

## Reachability probe
```bash
probe(){ out=$(sqlite3 -cmd '.timeout 2000' "file:$1?mode=ro" "select count(*) from $2;" 2>&1); rc=$?
  if [ $rc -ne 0 ]; then echo "BROKEN rc=$rc :: $out"
  elif [ "$out" = "0" ]; then echo "EMPTY rows=0"
  else echo "WORKING rows=$out"; fi; }
```
Measured on four real dbs:
- `WORKING rows=24` — instrument answering, has data. Proceed.
- `EMPTY rows=0` — instrument answering, genuinely nothing in the window. A real finding; report the zero.
- `BROKEN rc=1 :: Error: unable to open database "file:...?mode=ro": unable to open database file` — path wrong/unreadable. (Inside a loop over a glob this same case also surfaced as `Error: in prepare, unable to open database file (14)`; both are the missing-path state.)
- `BROKEN rc=1 :: Error: in prepare, no such table: sources` — reached it, schema differs. Different fix.

For HTTP the same three states are `http=200` + non-zero `bytes`; `http=200` + an empty result array; and non-2xx or `total` at your `--max-time`.

## What counts as evidence here
One line, all six fields, or it is not evidence:
`<exact query or URL issued> | resolution=<bucket> | window=<span, with as-of date> | value=<raw number> | unit=<unit> | bound=<>= | <= | exact>`

Worked example from this run:
`jq .timestamp history.jsonl, 60s buckets | resolution=60s | window=30d as-of 2026-09-08 | value=11 | unit=events/min | bound=>=`

`bound=exact` is only allowed when the instrument returns a total the source itself computes (a `count(*)`, a billing line), never for anything sampled.

## Driven on real data, 2026-09-08 — what the resolution actually costs

The lane's core move, run against this repo's own commit stream (460 commits, 105.1 days,
2026-05-26 .. 2026-09-08). One metric, one window, three bucket sizes:

| buckets | peak | busiest bucket held |
|---|---:|---:|
| 60s | **8.000 commits/min** | 8 |
| 3600s | 0.550 commits/min | 33 |
| 86400s | 0.139 commits/min | 200 |

**The hourly view understates the true peak by 93%, the daily view by 98% — on identical data.**
Every one of those numbers is defensible and only the first answers "how bursty is this". So report
a bound (`≥ 8/min at 60s resolution`), never a bare figure, and state the bucket size beside it or
the number means nothing.

Two honest notes from the same run, because a check that can only pass is not a check:

- **The union check passed and did not discriminate.** Paging five pages of 100 gave 460 rows, 460
  distinct ids, against the source's own count of 460 — but the naive sum-of-pages would *also* have
  matched here. This run is a control, not a demonstration that the check catches anything. It earns
  its place on the pages where the two diverge; do not cite a passing union check as evidence the
  paging was sound unless you can say what it would have looked like broken.
- **The control arm was 0.06s against a 0.00s no-op** (5 reps, median). A treatment that close to the
  floor cannot support a claim about cost, and saying so is the result.

## Traps
- **A plain sqlite path CREATES the file.** `sqlite3 /bad/path.db "select..."` made a real 0-byte `nope.db` and then said `no such table` — a missing-path error disguised as a schema error, plus a filesystem write. `file:...?mode=ro` returns `unable to open database file` and creates nothing. Verified both ways.
- **Resolution understates peaks, always downward.** Same 4,354 events: 60s buckets peak at 11/min, 3600s buckets at 0.333/min. The coarse number is **3.0% of the true peak — a 33x understatement**. Averaging a bucket cannot recover what the bucket flattened, so the error only ever runs one way. This is why the honest form is `>= 11 events/min at 60s`, never `11 events/min`.
- **Window moves the peak as much as resolution does.** Same 60s buckets: 1d and 7d both peak at 2/min, 30d peaks at 11/min. A number without its window is not a number.
- **Totals reconcile while rows are missing.** Cursor on a non-unique column with `>=` returned **25 rows but only 20 distinct against a source count of 24** — fetched-total (25) exceeded the count (24), so every "did I get everything" check based on totals passed while 4 of 24 rows were never seen. Only `sort -u` on ids catches it. Page on a unique key, and assert the union.
- **`2>/dev/null` collapses BROKEN into EMPTY.** Enumerating 7 dbs with stderr dropped, 4 came back blank; with stderr kept, 2 were `unable to open database file` (broken) and 2 were `0` (genuinely empty). Never silence stderr on a probe.
- **The instrument floor can be larger than the effect.** `/usr/bin/time -p` resolves to 0.01s: treatment and control both read `0.00` on a 13k-row join. That is not "no difference", it is `< 0.01s`. Check the floor before believing a null.
- **No control means you measured the instrument.** Startup cost sat under the floor here (control median 0.00 vs treatment 0.36), which is only knowable because the control was run. Without it, 0.36 could have been all process spawn.
- **`-H "Authorization: Bearer $TOKEN"` puts the secret in argv** where `ps` reads it. `curl -K -` on stdin does not — confirmed by `ps -o args=` showing only `curl -sS -K - -o /dev/null --max-time 10 <url>`. Read credentials from the project's own secret path into the environment, assert on `${#VAR}` and a prefix, never echo a value, never write one to disk or into a report.
- **Live numbers are as-of, not true.** Every value carries the timestamp it was read; re-probe rather than reusing a number from earlier in the session.
- **If the instrument is a video dashboard** read through captions, the caption text is SUBSTANCE, never QUOTATION — a verified case rendered "Claude Code" as "Cloud Code". Read the number off the frame, never off the transcript.

## Enumeration line
`live-instrument | files listed 22 | candidates selected 1 | cut line probe returned WORKING (rows>0); EMPTY and BROKEN both cut`

Real run, 2026-09-08: `ls */.hyperresearch/hyperresearch.db */.bad-research/*.db` listed 22; 7 held the target table; the probe returned 2 BROKEN, 4 EMPTY, 1 WORKING (`skaledotai sources=24`), so 1 was selected. A lane selecting 0 still emits this line with `candidates selected 0`.
