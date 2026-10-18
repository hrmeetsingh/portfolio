#!/usr/bin/env bash
# new-work-item.sh - create the next work item from .agent/work/_TEMPLATE.md
#
#   .agent/bin/new-work-item.sh "Add retry to sync job" [--branch]
#
# --branch also creates (or switches to) the git branch agent/WI-NNN-<slug>.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
WDIR="$ROOT/.agent/work"
TEMPLATE="$WDIR/_TEMPLATE.md"
title="${1:-}"
want_branch="${2:-}"

if [ -z "$title" ]; then
  echo "usage: $0 \"<title>\" [--branch]" >&2
  exit 64
fi
[ -f "$TEMPLATE" ] || { echo "missing $TEMPLATE" >&2; exit 66; }

last=0
for f in "$WDIR"/WI-*.md; do
  [ -e "$f" ] || continue
  n="$(basename "$f" | sed -E 's/^WI-0*([0-9]+).*/\1/')"
  case "$n" in ''|*[!0-9]*) continue ;; esac
  [ "$n" -gt "$last" ] && last="$n"
done
num="$(printf '%03d' $((last + 1)))"
id="WI-$num"
slug="$(printf '%s' "$title" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//' | cut -c1-40)"
slug="${slug%-}"
branch="agent/$id-$slug"
today="$(date +%Y-%m-%d)"
out="$WDIR/$id-$slug.md"

python3 - "$TEMPLATE" "$out" "$id" "$title" "$branch" "$today" <<'PY'
import sys
src, dst, wid, title, branch, today = sys.argv[1:7]
text = open(src, encoding="utf-8").read()
for k, v in {"{{ID}}": wid, "{{TITLE}}": title.replace('"', "'"), "{{BRANCH}}": branch, "{{DATE}}": today}.items():
    text = text.replace(k, v)
open(dst, "w", encoding="utf-8").write(text)
PY

if [ "$want_branch" = "--branch" ]; then
  if git -C "$ROOT" show-ref --verify --quiet "refs/heads/$branch"; then
    git -C "$ROOT" switch "$branch"
  else
    git -C "$ROOT" switch -c "$branch"
  fi
fi
echo "$out"
