#!/usr/bin/env python3
"""agent-bootstrap handoff gate  (Claude Code Stop hook).

If code changed during this session but no active work item was updated after
the last change, the agent is sent back once to record status, decisions,
files touched and the next step. That keeps every pause resumable.

Loop-safe: when Claude Code reports stop_hook_active (the agent is already
continuing because of this hook), the stop is allowed and a warning is stored
for the next SessionStart instead.
"""
import json
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _abcommon as C  # noqa: E402

IGNORED_PREFIXES = (".agent/", ".vault/", ".claude/", "CLAUDE.md", ".gitignore")


def changed_since(proj, since):
    """Paths with uncommitted changes, or committed after `since`, excluding agent metadata."""
    files, latest = [], 0.0
    try:
        out = subprocess.run(["git", "-C", proj, "status", "--porcelain", "-uall"],
                             capture_output=True, text=True, timeout=8)
        for line in out.stdout.splitlines():
            path = line[3:].split(" -> ")[-1].strip().strip('"')
            if not path or path.startswith(IGNORED_PREFIXES):
                continue
            full = os.path.join(proj, path)
            mtime = os.path.getmtime(full) if os.path.exists(full) else time.time()
            if mtime >= since:
                files.append(path)
                latest = max(latest, mtime)
        since_iso = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(since))
        out = subprocess.run(["git", "-C", proj, "log", "--since=" + since_iso, "--name-only",
                              "--format=%ct"], capture_output=True, text=True, timeout=8)
        commit_ts = 0.0
        for line in out.stdout.splitlines():
            line = line.strip()
            if line.isdigit():
                commit_ts = float(line)
            elif line and not line.startswith(IGNORED_PREFIXES):
                files.append(line)
                latest = max(latest, commit_ts)
    except Exception:
        pass
    return sorted(set(files)), latest


def block(reason):
    print(json.dumps({"decision": "block", "reason": "[agent-bootstrap handoff] " + reason}))
    sys.exit(0)


def main():
    data = C.read_input()
    proj = C.project_dir(data)
    if not C.is_bootstrapped(proj):
        return
    state = C.load_json(C.state_path(proj, data), {}) or {}
    since = float(state.get("started_at") or (time.time() - 6 * 3600))
    files, latest = changed_since(proj, since)
    if not files:
        return

    active = C.active_work_items(proj)
    updated = [w for w in active if w["_mtime"] >= latest - 1]
    if updated:
        return

    if data.get("stop_hook_active"):
        C.save_json(os.path.join(proj, ".agent", "state", "handoff-warning.json"), {
            "session": C.short_session(data), "time": C.now_iso(), "files": files[:20]})
        C.append_line(os.path.join(proj, ".agent", "log", C.today() + ".md"),
                      "- %s [%s] WARNING: session stopped without a work-item handoff (%d files changed)" % (
                          C.now_iso()[11:], C.short_session(data), len(files)))
        return

    shown = ", ".join(files[:10]) + (" ..." if len(files) > 10 else "")
    if not active:
        block("This session changed %d file(s) (%s) but there is no active work item. Create one with "
              ".agent/bin/new-work-item.sh \"<title>\" and fill in status, decisions, files-touched and "
              "next-step before stopping." % (len(files), shown))
    names = ", ".join(w["_file"] for w in active)
    block("This session changed %d file(s) (%s) after the active work item was last updated (%s). Update "
          "its status, decisions, files-touched and next-step so the next agent can resume, then stop."
          % (len(files), shown, names))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write("agent-bootstrap stop hook: %r\n" % (exc,))
        sys.exit(0)
