#!/usr/bin/env bash
# add-secret.sh - HUMAN-ONLY. Store one secret in the OS keychain for this project.
#
#   .agent/bin/add-secret.sh NAME          # prompts for the value (not echoed)
#   .agent/bin/add-secret.sh --list        # list the names in the manifest
#
# Run this in your own terminal, not through an agent (the guard hook blocks
# agents from running it). On macOS the item is created with an EMPTY list of
# trusted applications (-T ""), so macOS asks you every time anything reads it.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
MANIFEST="$ROOT/.agent/secrets.manifest"

if [ "${1:-}" = "--list" ]; then
  grep -E '^[A-Za-z_][A-Za-z0-9_]*$' "$MANIFEST" 2>/dev/null || echo "(no secrets registered)"
  exit 0
fi
name="${1:-}"
if ! printf '%s' "$name" | grep -Eq '^[A-Za-z_][A-Za-z0-9_]*$'; then
  echo "usage: $0 NAME   (NAME must be a valid environment variable name)" >&2
  exit 64
fi
if [ ! -t 0 ]; then
  echo "add-secret: run this in an interactive terminal so the value is typed, not piped." >&2
  exit 1
fi
service="$(awk -F= '/^service=/{print $2; exit}' "$MANIFEST" 2>/dev/null || true)"
if [ -z "$service" ]; then
  echo "add-secret: missing service= line in $MANIFEST (re-run the agent-bootstrap skill)." >&2
  exit 65
fi

case "$(uname -s)" in
  Darwin)
    if security find-generic-password -s "$service" -a "$name" >/dev/null 2>&1; then
      printf 'A keychain item for %s already exists. Replace it? [y/N] ' "$name"
      read -r answer
      case "$answer" in y|Y|yes) ;; *) echo "Unchanged."; exit 0 ;; esac
      security delete-generic-password -s "$service" -a "$name" >/dev/null
    fi
    echo "Type the value for $name (input is hidden; macOS asks twice):"
    # -w as the LAST argument makes `security` prompt for the value, keeping it out of argv.
    security add-generic-password -s "$service" -a "$name" -l "$service/$name" \
      -j "agent-bootstrap secret for $(basename "$ROOT")" -T "" -w
    ;;
  *)
    if ! command -v secret-tool >/dev/null 2>&1; then
      echo "add-secret: install libsecret-tools (secret-tool) or use macOS." >&2
      exit 1
    fi
    secret-tool store --label="$service/$name" service "$service" account "$name"
    ;;
esac

if ! grep -qx "$name" "$MANIFEST"; then
  printf '%s\n' "$name" >> "$MANIFEST"
fi
echo "Stored $name. Agents can now use it only via: .agent/bin/run-with-secrets.sh -- <command>"
