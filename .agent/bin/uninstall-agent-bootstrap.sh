#!/usr/bin/env bash
# uninstall-agent-bootstrap.sh - HUMAN-ONLY. Remove what agent-bootstrap installed.
#
#   .agent/bin/uninstall-agent-bootstrap.sh [--project] [--user] [--purge]
#
#   --project  remove this project's hooks, permission rules and settings keys
#              that bootstrap added (your own rules are kept), the hook scripts,
#              the CLAUDE.md managed block and the commit-trailer git hook.  (default)
#   --user     remove the single shared user-level guard from ~/.claude/settings.json
#              and ~/.claude/agent-bootstrap/. Do this when no project needs it any more.
#   --purge    with --project: also delete .agent/ and .vault/ (asks first).
#
# Close Claude Code first: while a session runs, the ConfigChange hook blocks
# changes that remove the guard (that is the point of it).
set -euo pipefail

if [ "${CLAUDECODE:-}" = "1" ]; then
  echo "Refusing to run inside a Claude Code session. Run this in your own terminal." >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
MERGE="$ROOT/.agent/bin/lib/merge_settings.py"
DO_PROJECT=0
DO_USER=0
PURGE=0
for a in "$@"; do
  case "$a" in
    --project) DO_PROJECT=1 ;;
    --user) DO_USER=1 ;;
    --purge) PURGE=1 ;;
    -h|--help) sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option $a" >&2; exit 64 ;;
  esac
done
[ $DO_PROJECT = 0 ] && [ $DO_USER = 0 ] && DO_PROJECT=1

if [ $DO_PROJECT = 1 ]; then
  echo "==> Project: $ROOT"
  python3 "$MERGE" --scope project --project "$ROOT" --remove >/dev/null
  echo "    removed agent-bootstrap hooks and the rules/keys it added from .claude/settings.json"
  rm -rf "$ROOT/.claude/hooks/agent-bootstrap"
  echo "    removed .claude/hooks/agent-bootstrap/"
  python3 - "$ROOT/CLAUDE.md" <<'PY'
import os, re, sys
p = sys.argv[1]
if os.path.exists(p):
    t = open(p, encoding="utf-8").read()
    n = re.sub(r"\n*<!-- agent-bootstrap:start.*?<!-- agent-bootstrap:end -->\n?", "\n", t, flags=re.S)
    if n != t:
        open(p, "w", encoding="utf-8").write(n.rstrip() + "\n")
        print("    removed the managed block from CLAUDE.md")
PY
  GH="$(git -C "$ROOT" rev-parse --git-path hooks 2>/dev/null || echo .git/hooks)"
  case "$GH" in /*) ;; *) GH="$ROOT/$GH" ;; esac
  if [ -f "$GH/prepare-commit-msg" ] && grep -q "agent-bootstrap" "$GH/prepare-commit-msg"; then
    rm -f "$GH/prepare-commit-msg"
    echo "    removed the commit-trailer git hook"
  fi
  rm -f "$ROOT/.agent/bootstrap-manifest.json"
  echo "    kept: .claude/agents/*, .agent/ (work items, logs, baseline), .vault/, git tag pre-agent-baseline"
  if [ $PURGE = 1 ]; then
    printf 'Delete .agent/ and .vault/ permanently? [y/N] '
    read -r ans
    case "$ans" in y|Y|yes) rm -rf "$ROOT/.agent" "$ROOT/.vault"; echo "    deleted .agent/ and .vault/" ;; *) echo "    kept" ;; esac
  fi
fi

if [ $DO_USER = 1 ]; then
  echo "==> User level (~/.claude)"
  python3 "$MERGE" --scope user --project "$ROOT" --remove >/dev/null
  rm -rf "$HOME/.claude/agent-bootstrap"
  echo "    removed the shared guard entry from ~/.claude/settings.json and ~/.claude/agent-bootstrap/"
fi
echo "Done. Start a new Claude Code session for the change to take effect."
