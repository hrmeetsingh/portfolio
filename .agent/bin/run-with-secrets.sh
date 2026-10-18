#!/usr/bin/env bash
# run-with-secrets.sh - run ONE command with secrets injected from the OS keychain.
#
#   .agent/bin/run-with-secrets.sh [--only NAME[,NAME...]] -- <command> [args...]
#
# Secret NAMES live in .agent/secrets.manifest (values never touch the repo).
# Values come from the macOS Keychain (or libsecret `secret-tool` on Linux) and
# exist only in the environment of the command you pass.
#
# Two deterministic approval gates protect every run:
#   1. Claude Code asks you (agent-bootstrap PreToolUse hook + an `ask` rule).
#   2. macOS asks you, because items are stored with an empty trusted-app list
#      (security add-generic-password -T ""). Click "Allow", not "Always Allow".
#
# Never pipe the output of this script into anything that echoes the
# environment. The guard hook rejects such commands, but read before approving.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
MANIFEST="$ROOT/.agent/secrets.manifest"

usage() {
  sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
}

only=""
while [ $# -gt 0 ]; do
  case "$1" in
    --only) only="${2:-}"; shift 2 ;;
    --) shift; break ;;
    -h|--help) usage; exit 0 ;;
    *) break ;;
  esac
done
if [ $# -eq 0 ]; then
  usage >&2
  exit 64
fi
if [ ! -f "$MANIFEST" ]; then
  echo "run-with-secrets: $MANIFEST not found. Add secrets with .agent/bin/add-secret.sh NAME (in your own terminal)." >&2
  exit 66
fi

service="$(awk -F= '/^service=/{print $2; exit}' "$MANIFEST")"
if [ -z "$service" ]; then
  echo "run-with-secrets: no service= line in $MANIFEST" >&2
  exit 65
fi

fetch() {
  # $1 = account (secret name)
  case "$(uname -s)" in
    Darwin) security find-generic-password -s "$service" -a "$1" -w 2>/dev/null ;;
    *)
      if command -v secret-tool >/dev/null 2>&1; then
        secret-tool lookup service "$service" account "$1"
      else
        echo "run-with-secrets: no supported keychain backend (need macOS 'security' or 'secret-tool')." >&2
        return 1
      fi ;;
  esac
}

injected=""
for name in $(grep -E '^[A-Za-z_][A-Za-z0-9_]*$' "$MANIFEST" || true); do
  if [ -n "$only" ]; then
    case ",$only," in *",$name,"*) ;; *) continue ;; esac
  fi
  if ! value="$(fetch "$name")" || [ -z "$value" ]; then
    echo "run-with-secrets: could not read '$name' (missing, or access was denied in the keychain prompt)." >&2
    exit 1
  fi
  export "$name=$value"
  injected="$injected $name"
done
unset value

echo "run-with-secrets: injected:${injected:- (none)}" >&2
exec "$@"
