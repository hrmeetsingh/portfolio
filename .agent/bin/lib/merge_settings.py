#!/usr/bin/env python3
"""Idempotently add or remove agent-bootstrap hooks and permission rules in a
Claude Code settings file.

  merge_settings.py --scope project --project DIR [--on-failure-block] [--plan-mode] [--dry-run]
  merge_settings.py --scope user    --project DIR [--on-failure-block] [--dry-run]
  merge_settings.py --scope project|user --project DIR --remove

Every hook handler we add contains the string "agent-bootstrap" in its command,
so re-running replaces our handlers in place and never duplicates them. Rules
and keys are recorded in a manifest only when this script added them, so
--remove takes out exactly what bootstrap put in and leaves your own settings.
"""
import argparse
import json
import os
import shutil
import sys
import time

MARK = "agent-bootstrap"
HOME = os.path.expanduser("~")


def hook(path_expr, script, timeout, extra="", block_on_failure=False):
    h = {"type": "command",
         "command": 'python3 -E -s "%s/%s"%s' % (path_expr, script, (" " + extra) if extra else ""),
         "timeout": timeout}
    if block_on_failure:
        h["onFailure"] = "block"
    return h


def project_spec(on_failure, plan_mode):
    p = "${CLAUDE_PROJECT_DIR}/.claude/hooks/agent-bootstrap"
    hooks = {
        "PreToolUse": [{"matcher": "*", "hooks": [
            hook(p, "guard_secrets.py", 15, "--scope project", block_on_failure=on_failure)]}],
        "PostToolUse": [{"matcher": "Edit|Write|MultiEdit|NotebookEdit|Bash", "hooks": [
            hook(p, "log_change.py", 15)]}],
        "SessionStart": [{"hooks": [hook(p, "session_start.py", 30)]}],
        "Stop": [{"hooks": [hook(p, "stop_handoff.py", 30)]}],
        "ConfigChange": [{"hooks": [hook(p, "config_guard.py", 15)]}],
    }
    deny = [
        "Read(.env)", "Read(.env.*)", "Read(!.env.example)", "Read(!.env.sample)", "Read(!.env.template)",
        "Read(.envrc)", "Read(**/*.pem)", "Read(**/*.key)", "Read(**/*.p12)", "Read(**/*.pfx)",
        "Read(**/id_rsa*)", "Read(**/id_ed25519*)", "Read(**/credentials.json)", "Read(**/*.tfvars)",
        "Edit(/.claude/settings.json)", "Edit(/.claude/settings.local.json)", "Edit(/.claude/hooks/**)",
        "Edit(/.agent/secrets.conf)", "Edit(/.agent/secrets.manifest)", "Edit(/.agent/bootstrap-manifest.json)",
        "Bash(security find-generic-password *)", "Bash(security find-internet-password *)",
        "Bash(security dump-keychain *)", "Bash(printenv *)", "Bash(env)",
    ]
    ask = ["Bash(*run-with-secrets*)", "Bash(git push *)"]
    keys = {"disableBypassPermissionsMode": "disable"}
    if plan_mode:
        keys["defaultMode"] = "plan"
    return hooks, {"deny": deny, "ask": ask}, keys


def user_spec(on_failure):
    p = "$HOME/.claude/agent-bootstrap/hooks"
    hooks = {
        "PreToolUse": [{"matcher": "*", "hooks": [
            hook(p, "guard_secrets.py", 15, "--scope user", block_on_failure=on_failure)]}],
        "ConfigChange": [{"hooks": [hook(p, "config_guard.py", 15)]}],
    }
    deny = [
        "Read(~/.ssh/**)", "Read(~/.aws/**)", "Read(~/.gnupg/**)", "Read(~/.config/gcloud/**)",
        "Read(~/.config/gh/**)", "Read(~/.docker/config.json)", "Read(~/.kube/config)", "Read(~/.netrc)",
        "Read(~/.git-credentials)", "Read(~/.npmrc)", "Read(~/.pypirc)", "Read(~/Library/Keychains/**)",
        "Edit(~/.claude/settings.json)", "Edit(~/.claude/agent-bootstrap/**)",
        "Bash(security find-generic-password *)", "Bash(security find-internet-password *)",
        "Bash(security dump-keychain *)", "Bash(printenv *)", "Bash(env)",
    ]
    return hooks, {"deny": deny, "ask": []}, {}


def load(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()
    return json.loads(text) if text else {}


def write_atomic(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp-agent-bootstrap"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def strip_ours(hooks):
    removed = 0
    for event in list(hooks.keys()):
        groups = hooks.get(event) or []
        kept = []
        for g in groups:
            hs = [h for h in (g.get("hooks") or []) if MARK not in json.dumps(h)]
            removed += len(g.get("hooks") or []) - len(hs)
            if hs:
                g = dict(g)
                g["hooks"] = hs
                kept.append(g)
        if kept:
            hooks[event] = kept
        else:
            del hooks[event]
    return removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", choices=["project", "user"], required=True)
    ap.add_argument("--project", required=True)
    ap.add_argument("--on-failure-block", action="store_true")
    ap.add_argument("--plan-mode", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--remove", action="store_true")
    a = ap.parse_args()

    proj = os.path.abspath(a.project)
    if a.scope == "project":
        target = os.path.join(proj, ".claude", "settings.json")
        manifest_path = os.path.join(proj, ".agent", "bootstrap-manifest.json")
        spec = project_spec(a.on_failure_block, a.plan_mode)
    else:
        target = os.path.join(HOME, ".claude", "settings.json")
        manifest_path = os.path.join(HOME, ".claude", "agent-bootstrap", "installed.json")
        spec = user_spec(a.on_failure_block)
    spec_hooks, spec_rules, spec_keys = spec

    settings = load(target)
    manifest = load(manifest_path)
    rec = manifest.setdefault("settings", {"rules": {"deny": [], "ask": []}, "keys": []})
    summary = {"file": target, "scope": a.scope, "hooks": [], "rules_added": {"deny": [], "ask": []},
               "keys_added": [], "removed_handlers": 0, "backup": None}

    hooks = settings.get("hooks") or {}
    summary["removed_handlers"] = strip_ours(hooks)
    perms = settings.get("permissions") or {}

    if a.remove:
        for kind in ("deny", "ask"):
            ours = set(rec["rules"].get(kind, []))
            if kind in perms:
                perms[kind] = [r for r in perms[kind] if r not in ours]
                if not perms[kind]:
                    del perms[kind]
        for key in rec.get("keys", []):
            perms.pop(key, None)
    else:
        for event, groups in spec_hooks.items():
            hooks.setdefault(event, []).extend(groups)
            summary["hooks"].append(event)
        for kind in ("deny", "ask"):
            lst = perms.setdefault(kind, [])
            for rule in spec_rules[kind]:
                if rule not in lst:
                    lst.append(rule)
                    summary["rules_added"][kind].append(rule)
                    if rule not in rec["rules"].setdefault(kind, []):
                        rec["rules"][kind].append(rule)
            if not lst:
                del perms[kind]
        for key, val in spec_keys.items():
            if key not in perms:
                perms[key] = val
                summary["keys_added"].append(key)
                if key not in rec["keys"]:
                    rec["keys"].append(key)

    if hooks:
        settings["hooks"] = hooks
    else:
        settings.pop("hooks", None)
    if perms:
        settings["permissions"] = perms
    else:
        settings.pop("permissions", None)

    if a.dry_run:
        summary["dry_run"] = True
        print(json.dumps(summary, indent=2))
        return 0

    if os.path.exists(target):
        backup = target + ".pre-agent-bootstrap.bak"
        if not os.path.exists(backup):
            shutil.copy2(target, backup)
            summary["backup"] = backup
    write_atomic(target, settings)

    if a.remove:
        if os.path.exists(manifest_path):
            data = load(manifest_path)
            data.pop("settings", None)
            if a.scope == "user":
                os.remove(manifest_path)
            else:
                write_atomic(manifest_path, data)
    else:
        manifest["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        if a.scope == "user":
            projects = manifest.setdefault("projects", [])
            if proj not in projects:
                projects.append(proj)
        write_atomic(manifest_path, manifest)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
