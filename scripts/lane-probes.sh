#!/usr/bin/env bash
# Every lane answers its own question or reports an explicit, honest zero.
#
# This is S5's check made runnable. It exists because the failure it guards
# against is silence: a lane whose tool is broken and a lane whose topic is
# genuinely absent produce identical empty output, and treating the first as the
# second is how a research answer becomes a guess with citations.
#
# So no probe here is allowed to print nothing. Each returns one of
# WORKING / EMPTY / BLOCKED / MISSING, and an unclassifiable result is itself a
# failure of the probe, reported as UNCLASSIFIED rather than skipped.
#
# Exit 1 if any lane is UNCLASSIFIED. A lane reporting BLOCKED or MISSING is a
# healthy probe telling the truth, not a failure of this script.
set -uo pipefail
R="${RESEARCH_ROOT:-$HOME/Desktop}"
CV="${COMPOUND_V:-$R/compound-v}"
fail=0

say(){ printf '%-22s %-12s %s\n' "$1" "$2" "$3"; [ "$2" = UNCLASSIFIED ] && fail=1; return 0; }

# 1. local-corpus — four roots, enumerated live. A count written down is stale by construction.
t=$(find "$R/researchfms/teardowns"        -maxdepth 1 -name '*.md'            2>/dev/null | wc -l | tr -d ' ')
r=$(find "$R/researchfms/Transcripts"      -maxdepth 1 -name 'TRANSCRIPTS_*.md' 2>/dev/null | wc -l | tr -d ' ')
a=$(find "$R/guidesfm/research/articles"   -maxdepth 1 -name '*.md'            2>/dev/null | wc -l | tr -d ' ')
x=$(find "$R/guidesfm/research/x-guides"   -maxdepth 1 -name '*.md'            2>/dev/null | wc -l | tr -d ' ')
if [ "$t$r$a$x" = "0000" ]; then say local-corpus MISSING "no root resolved under $R"
elif [ "$t" -gt 0 ] && [ "$r" -gt 0 ] && [ "$a" -gt 0 ] && [ "$x" -gt 0 ]; then
  say local-corpus WORKING "teardowns $t / transcripts $r / articles $a / x-guides $x"
else say local-corpus MISSING "a root is empty: $t/$r/$a/$x"; fi

# 2. artifact-re — the registry answering is the signal; E404 is EMPTY, ENOTFOUND is BROKEN.
o=$(npm view left-pad version 2>&1 | head -1)
case "$o" in
  *ENOTFOUND*|*ECONNREFUSED*|*ETIMEDOUT*|*"network request"*) say artifact-re BLOCKED "$o" ;;
  *E404*|*"Not found"*)                                        say artifact-re EMPTY   "$o" ;;
  [0-9]*)                                                      say artifact-re WORKING "left-pad@$o" ;;
  *)                                                           say artifact-re UNCLASSIFIED "$o" ;;
esac

# 3. delta-vs-pinned-ref — 0 is UNCHANGED and reportable, 1 is a delta, 128 is a bad ref.
git -C "$PWD" diff --quiet HEAD~1 HEAD -- . 2>/dev/null; rc=$?
case $rc in
  0)   say delta-vs-pinned-ref EMPTY   "UNCHANGED HEAD~1..HEAD (a result, not a failure)" ;;
  1)   say delta-vs-pinned-ref WORKING "delta present HEAD~1..HEAD" ;;
  128) say delta-vs-pinned-ref MISSING "bad revision — stale clone or wrong tag" ;;
  *)   say delta-vs-pinned-ref UNCLASSIFIED "rc=$rc" ;;
esac

# 4. terms-and-pricing — code!=200 or chars<500 is BLOCKED; anchors present is WORKING.
o=$(curl -sL --compressed -m 25 -A "Mozilla/5.0" -w '\n@@%{http_code}\n' https://www.anthropic.com/legal/aup 2>/dev/null | python3 -c '
import re,sys
raw=sys.stdin.read(); m=re.search(r"@@(\d+)\s*$",raw); code=m.group(1) if m else "0"
h=re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>"," ",raw[:m.start()] if m else raw)
t=re.sub(r"\s+"," ",re.sub(r"(?s)<[^>]+>"," ",h)).strip()
print(code,len(t),len(re.findall(r"(?i)last updated|effective|version dated",t)))' 2>/dev/null)
set -- ${o:-0 0 0}
if [ "${1:-0}" != 200 ] || [ "${2:-0}" -lt 500 ]; then say terms-and-pricing BLOCKED "code=${1:-?} chars=${2:-?}"
elif [ "${3:-0}" -gt 0 ]; then say terms-and-pricing WORKING "code=$1 chars=$2 datemarks=$3"
else say terms-and-pricing EMPTY "code=$1 chars=$2 but no dateline — weaker citation"; fi

# 5. web-live — silver's own error: prefix is the classifier; never infer from byte count alone.
o=$(timeout 90 silver read https://example.com/ 2>&1 | head -3)
case "$o" in
  *"CAPTCHA"*|*"denied by policy"*|*"HTTP error status"*) say web-live BLOCKED "${o%%$'\n'*}" ;;
  *"Example Domain"*)                                     say web-live WORKING "example.com rendered" ;;
  error:*)                                                say web-live MISSING "${o%%$'\n'*}" ;;
  *)                                                      say web-live UNCLASSIFIED "${o%%$'\n'*}" ;;
esac

# 6. practitioner-video — a stderr banner means partial failure, NOT an empty tier.
o=$(cd "$CV" 2>/dev/null && timeout 300 bash scripts/yt.sh sweep "agent" 12 podcast 2>/tmp/yt.err); rc=$?
n=$(printf '%s' "$o" | sed -n 's/^# \([0-9][0-9]*\) titles matched\..*/\1/p' | head -1)
if [ -s /tmp/yt.err ]; then say practitioner-video BLOCKED "$(head -1 /tmp/yt.err)"
elif [ "$rc" -ne 0 ]; then say practitioner-video BLOCKED "exit $rc"
elif [ "${n:-x}" = 0 ]; then say practitioner-video EMPTY "0 titles matched, no stderr banner"
elif [ -n "${n:-}" ]; then say practitioner-video WORKING "$n titles matched"
else say practitioner-video UNCLASSIFIED "no footer line"; fi

# 7. live-instrument — an instrument that cannot answer is BROKEN, not a zero.
o=$(git -C "$PWD" rev-list --count HEAD 2>&1)
case "$o" in
  [0-9]*) [ "$o" -gt 0 ] && say live-instrument WORKING "commit stream, $o events" \
                         || say live-instrument EMPTY "instrument answered, 0 rows" ;;
  *)      say live-instrument MISSING "$o" ;;
esac

# 8. people-track-record — three ways to print 0; they are not the same finding.
P="$CV/references/practitioners.tsv"
roster=$(grep -c -v -e '^#' -e '^$' "$P" 2>/dev/null || echo BROKEN)
gh_o=$(gh api users/simonw --jq .login 2>&1 | head -1)
if [ "$roster" = BROKEN ] || [ ! -f "$P" ]; then say people-track-record MISSING "roster not readable at $P"
elif [ "$gh_o" != simonw ]; then say people-track-record BLOCKED "gh=$gh_o"
elif [ "$roster" -eq 0 ]; then say people-track-record EMPTY "roster present, 0 data rows"
else say people-track-record WORKING "roster=$roster gh=$gh_o"; fi

echo
[ $fail -eq 0 ] && echo "PASS | every lane named its state; none returned silence" \
                || echo "FAIL | a lane returned something its own taxonomy cannot classify"
exit $fail
