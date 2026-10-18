#!/usr/bin/env bash
# migrate-env-to-keychain.sh - HUMAN-ONLY. Move KEY=VALUE pairs from a dotenv
# file into the OS keychain and register their NAMES in .agent/secrets.manifest.
#
#   .agent/bin/migrate-env-to-keychain.sh .env [--yes]
#
# The file is NOT deleted. After checking that your app works through
# .agent/bin/run-with-secrets.sh, delete it yourself and rotate any value that
# was ever committed to git. Values are passed to `security` on its command
# line for a moment; run this on your own machine only.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
MANIFEST="$ROOT/.agent/secrets.manifest"
file="${1:-}"
assume_yes="${2:-}"

if [ -z "$file" ] || [ ! -f "$file" ]; then
  echo "usage: $0 <dotenv-file> [--yes]" >&2
  exit 64
fi
if [ ! -t 0 ] && [ "$assume_yes" != "--yes" ]; then
  echo "migrate: run this in an interactive terminal (or pass --yes)." >&2
  exit 1
fi
service="$(awk -F= '/^service=/{print $2; exit}' "$MANIFEST" 2>/dev/null || true)"
if [ -z "$service" ]; then
  echo "migrate: missing service= line in $MANIFEST (re-run the agent-bootstrap skill)." >&2
  exit 65
fi

store() {
  # $1 name, $2 value
  case "$(uname -s)" in
    Darwin)
      security delete-generic-password -s "$service" -a "$1" >/dev/null 2>&1 || true
      security add-generic-password -s "$service" -a "$1" -l "$service/$1" \
        -j "agent-bootstrap secret for $(basename "$ROOT")" -T "" -w "$2"
      ;;
    *)
      printf '%s' "$2" | secret-tool store --label="$service/$1" service "$service" account "$1"
      ;;
  esac
}

names=""
while IFS= read -r line || [ -n "$line" ]; do
  line="${line#"${line%%[![:space:]]*}"}"          # trim leading whitespace
  case "$line" in ''|'#'*) continue ;; esac
  line="${line#export }"
  case "$line" in *=*) ;; *) continue ;; esac
  key="${line%%=*}"
  value="${line#*=}"
  key="$(printf '%s' "$key" | tr -d '[:space:]')"
  printf '%s' "$key" | grep -Eq '^[A-Za-z_][A-Za-z0-9_]*$' || continue
  case "$value" in
    \"*\") value="${value#\"}"; value="${value%\"}" ;;
    \'*\') value="${value#\'}"; value="${value%\'}" ;;
    *) value="${value%% #*}" ;;                      # strip trailing comment on unquoted values
  esac
  [ -n "$value" ] || { echo "skip $key (empty)"; continue; }
  names="$names $key"
done < "$file"

if [ -z "$names" ]; then
  echo "No KEY=VALUE pairs found in $file."
  exit 0
fi
echo "Will store these names in the keychain service '$service':$names"
if [ "$assume_yes" != "--yes" ]; then
  printf 'Proceed? [y/N] '
  read -r answer </dev/tty
  case "$answer" in y|Y|yes) ;; *) echo "Aborted."; exit 0 ;; esac
fi

while IFS= read -r line || [ -n "$line" ]; do
  line="${line#"${line%%[![:space:]]*}"}"
  case "$line" in ''|'#'*) continue ;; esac
  line="${line#export }"
  case "$line" in *=*) ;; *) continue ;; esac
  key="$(printf '%s' "${line%%=*}" | tr -d '[:space:]')"
  value="${line#*=}"
  printf '%s' "$key" | grep -Eq '^[A-Za-z_][A-Za-z0-9_]*$' || continue
  case "$value" in
    \"*\") value="${value#\"}"; value="${value%\"}" ;;
    \'*\') value="${value#\'}"; value="${value%\'}" ;;
    *) value="${value%% #*}" ;;
  esac
  [ -n "$value" ] || continue
  store "$key" "$value"
  grep -qx "$key" "$MANIFEST" || printf '%s\n' "$key" >> "$MANIFEST"
  echo "stored $key"
done < "$file"
unset value

cat <<EOF

Done. Next steps (yours, not the agent's):
  1. Test:   .agent/bin/run-with-secrets.sh -- <your dev/test command>
             macOS will ask for each secret; click "Allow" (not "Always Allow").
  2. Delete: rm "$file"   (keep a .env.example with names only if useful)
  3. Rotate: any value that was ever committed to git history is exposed; rotate it at the provider.
EOF
