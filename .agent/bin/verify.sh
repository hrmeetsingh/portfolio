#!/usr/bin/env bash
# verify.sh - prove the agent-bootstrap guardrails work in this project.
#
#   .agent/bin/verify.sh [--project DIR]
#
# Feeds synthetic tool calls to the real guard hook and checks each decision,
# checks that settings files register the hooks, and smoke-tests the other
# hooks. No secrets are read; test inputs are built at run time.
# Exit code = number of failed checks.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
if [ "${1:-}" = "--project" ] && [ -n "${2:-}" ]; then ROOT="$(cd "$2" && pwd -P)"; fi

python3 - "$ROOT" <<'PY'
import json, os, subprocess, sys

root = sys.argv[1]
home = os.path.expanduser("~")
hooks = os.path.join(root, ".claude", "hooks", "agent-bootstrap")
guard = os.path.join(hooks, "guard_secrets.py")
fails = 0

def report(ok, label, detail=""):
    global fails
    if not ok:
        fails += 1
    print("%s  %s%s" % ("PASS" if ok else "FAIL", label, (" - " + detail) if (detail and not ok) else ""))

def run_hook(script, payload, extra=()):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=root)
    p = subprocess.run([sys.executable, "-E", "-s", script] + list(extra), input=json.dumps(payload),
                       capture_output=True, text=True, env=env, timeout=30)
    return p.returncode, p.stdout, p.stderr

def decision(tool, tool_input):
    payload = {"session_id": "verify", "cwd": root, "hook_event_name": "PreToolUse",
               "tool_name": tool, "tool_input": tool_input}
    code, out, err = run_hook(guard, payload, ["--scope", "project"])
    if code == 2:
        return "deny(exit2)"
    if code != 0:
        return "error:%d %s" % (code, err.strip()[:120])
    if not out.strip():
        return "allow"
    try:
        return json.loads(out)["hookSpecificOutput"]["permissionDecision"]
    except Exception:
        return "unparseable"

fake_aws = "AKIA" + "Q7XK2M4N8P1R5T3V"          # assembled so this file holds no literal key
cases = [
    ("deny", "Read",  {"file_path": os.path.join(root, ".env")}, "Read .env"),
    ("deny", "Read",  {"file_path": os.path.join(root, "config", ".env.production")}, "Read config/.env.production"),
    ("deny", "Read",  {"file_path": os.path.join(home, ".ssh", "id_ed25519")}, "Read ~/.ssh key"),
    ("deny", "Bash",  {"command": "cat .env"}, "cat .env"),
    ("deny", "Bash",  {"command": "/usr/bin/security find-generic-password -s x -a y -w"}, "keychain read via absolute path"),
    ("deny", "Bash",  {"command": "sh -c 'security dump-keychain'"}, "keychain dump inside sh -c"),
    ("deny", "Bash",  {"command": "printenv"}, "printenv"),
    ("deny", "Bash",  {"command": "env | grep TOKEN"}, "env | grep"),
    ("deny", "Bash",  {"command": "python3 -c 'import os; print(os.environ)'"}, "python os.environ dump"),
    ("deny", "Bash",  {"command": "gh auth token"}, "gh auth token"),
    ("deny", "Bash",  {"command": "cp .env /tmp/x"}, "copy .env"),
    ("deny", "Bash",  {"command": "export K=%s && ./deploy" % fake_aws}, "literal AWS key in command"),
    ("deny", "Write", {"file_path": os.path.join(root, "src", "c.py"), "content": "KEY='%s'" % fake_aws}, "write literal AWS key"),
    ("deny", "Edit",  {"file_path": os.path.join(root, ".claude", "settings.json"), "old_string": "a", "new_string": "b"}, "edit project settings"),
    ("deny", "Write", {"file_path": os.path.join(root, ".claude", "hooks", "agent-bootstrap", "guard_secrets.py"), "content": ""}, "overwrite guard hook"),
    ("deny", "Bash",  {"command": "echo '{\"disableAllHooks\": true}' > .claude/settings.local.json"}, "disableAllHooks via shell"),
    ("deny", "Bash",  {"command": "rm .claude/hooks/agent-bootstrap/guard_secrets.py"}, "delete guard hook"),
    ("deny", "Bash",  {"command": ".agent/bin/add-secret.sh API_KEY"}, "agent runs human-only add-secret"),
    ("deny", "Bash",  {"command": ".agent/bin/uninstall-agent-bootstrap.sh --project"}, "agent runs uninstall"),
    ("deny", "Grep",  {"pattern": "KEY", "path": os.path.join(root, ".env")}, "grep inside .env"),
    ("deny", "Bash",  {"command": ".agent/bin/run-with-secrets.sh -- printenv"}, "secrets wrapper + printenv"),
    ("ask",  "Bash",  {"command": ".agent/bin/run-with-secrets.sh -- npm test"}, "secrets wrapper asks every time"),
    ("allow", "Read", {"file_path": os.path.join(root, "README.md")}, "Read README.md"),
    ("allow", "Read", {"file_path": os.path.join(root, ".env.example")}, "Read .env.example"),
    ("allow", "Bash", {"command": "git status"}, "git status"),
    ("allow", "Bash", {"command": "echo '.env' >> .gitignore"}, "echo .env >> .gitignore"),
    ("allow", "Bash", {"command": "cat .claude/settings.json"}, "read project settings"),
    ("allow", "Write", {"file_path": os.path.join(root, "docs", "x.md"), "content": "AKIAIOSFODNN7EXAMPLE"}, "documented placeholder key"),
]

print("Guard decisions (synthetic tool calls):")
if not os.path.isfile(guard):
    report(False, "guard hook present", guard)
else:
    for expected, tool, ti, label in cases:
        got = decision(tool, ti)
        ok = got == expected or (expected == "deny" and got.startswith("deny"))
        report(ok, "%-5s %s" % (expected, label), "" if ok else "got %s" % got)

print("\nSettings:")
def has(path, needle):
    try:
        return needle in open(path, encoding="utf-8").read()
    except Exception:
        return False
proj_settings = os.path.join(root, ".claude", "settings.json")
try:
    s = json.load(open(proj_settings, encoding="utf-8"))
    report(True, "project settings parse")
    events = set((s.get("hooks") or {}).keys())
    need = {"PreToolUse", "PostToolUse", "SessionStart", "Stop", "ConfigChange"}
    report(need <= events, "project hooks registered", ", ".join(sorted(need - events)) if not need <= events else "")
    deny = (s.get("permissions") or {}).get("deny") or []
    report("Read(.env)" in deny and any("find-generic-password" in r for r in deny), "project deny rules present")
    ask = (s.get("permissions") or {}).get("ask") or []
    report(any("run-with-secrets" in r for r in ask), "ask rule for run-with-secrets")
    report(not s.get("disableAllHooks"), "hooks not disabled")
except Exception as exc:
    report(False, "project settings parse", repr(exc))

manifest = json.load(open(os.path.join(root, ".agent", "bootstrap-manifest.json"))) if os.path.exists(
    os.path.join(root, ".agent", "bootstrap-manifest.json")) else {}
if manifest.get("user_level"):
    us = os.path.join(home, ".claude", "settings.json")
    report(has(us, "agent-bootstrap/hooks/guard_secrets.py"), "user-level guard registered (~/.claude/settings.json)")
    report(os.path.isfile(os.path.join(home, ".claude", "agent-bootstrap", "hooks", "guard_secrets.py")), "user-level guard script present")
    try:
        txt = open(us, encoding="utf-8").read()
        report(txt.count("agent-bootstrap/hooks/guard_secrets.py") == 1, "exactly one user-level guard entry")
    except Exception:
        pass
if manifest.get("on_failure_block"):
    report(True, "guard fails closed if it cannot start (onFailure: block)")
else:
    print("WARN  guard fails open if python3 is missing or it times out - upgrade Claude Code to >= 2.1.295 "
          "and re-run the skill (guard errors already block via exit 2)")

print("\nOther hooks:")
code, out, _ = run_hook(os.path.join(hooks, "session_start.py"),
                        {"session_id": "verify-session", "cwd": root, "hook_event_name": "SessionStart", "source": "startup"})
report(code == 0 and "agent context" in out, "SessionStart injects context")
code, out, _ = run_hook(os.path.join(hooks, "config_guard.py"),
                        {"session_id": "verify", "cwd": root, "hook_event_name": "ConfigChange",
                         "source": "project_settings", "file_path": proj_settings})
report(code == 0, "ConfigChange accepts the current settings")
try:
    os.remove(os.path.join(root, ".agent", "state", "session-verify-session.json"))
except OSError:
    pass

print("\nProject files:")
for rel in (".agent/BASELINE.md", ".agent/work/_TEMPLATE.md", ".agent/secrets.manifest", ".agent/bin/run-with-secrets.sh",
            ".agent/bin/vault_extract.py", "CLAUDE.md"):
    report(os.path.exists(os.path.join(root, rel)), rel)
if manifest.get("vault_enabled", True):
    report(os.path.exists(os.path.join(root, ".vault", "_map.md")), ".vault/_map.md", "run python3 .agent/bin/vault_extract.py")
else:
    print("SKIP  .vault/_map.md (bootstrap ran with --skip-vault)")
tag = subprocess.run(["git", "-C", root, "rev-parse", "-q", "--verify", "refs/tags/pre-agent-baseline"], capture_output=True)
report(tag.returncode == 0, "git tag pre-agent-baseline")

print("\n%s: %d failed check(s)" % ("OK" if fails == 0 else "ATTENTION", fails))
sys.exit(min(fails, 100))
PY
