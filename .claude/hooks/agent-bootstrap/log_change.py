#!/usr/bin/env python3
"""agent-bootstrap change log  (Claude Code PostToolUse hook).

Appends one line per file change or non-trivial shell command to
.agent/log/YYYY-MM-DD.md, so the agent-era history exists even when nobody
remembers to write it. Records paths and redacted commands, never file content.
"""
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _abcommon as C  # noqa: E402

READ_ONLY = {"ls", "cat", "head", "tail", "grep", "rg", "find", "pwd", "echo", "wc", "which",
             "stat", "file", "less", "tree", "diff", "jq", "sort", "uniq", "cd", "true"}
GIT_READ = {"status", "log", "diff", "show", "branch", "ls-files", "blame", "rev-parse", "remote", "fetch"}
REDACT_RE = re.compile(r"((?:token|secret|password|passwd|apikey|api_key|key)\s*[=:]\s*)\S+", re.I)


def describe_bash(cmd):
    words = cmd.strip().split()
    if not words:
        return None
    verb = os.path.basename(words[0])
    if verb in READ_ONLY:
        return None
    if verb == "git" and len(words) > 1 and words[1] in GIT_READ:
        return None
    one_line = " ".join(cmd.split())
    one_line = REDACT_RE.sub(r"\1[redacted]", one_line)
    if len(one_line) > 160:
        one_line = one_line[:157] + "..."
    return "`$ %s`" % one_line.replace("`", "'")


def main():
    data = C.read_input()
    proj = C.project_dir(data)
    if not C.is_bootstrapped(proj):
        return
    tool = data.get("tool_name") or ""
    ti = data.get("tool_input") or {}
    if tool == "Bash":
        what = describe_bash(str(ti.get("command") or ""))
    else:
        target = ti.get("file_path") or ti.get("notebook_path") or ""
        if not target:
            return
        rel = os.path.relpath(os.path.abspath(target), proj) if os.path.isabs(target) else target
        if rel.startswith(".agent" + os.sep + "log"):
            return
        what = "%s `%s`" % (tool, rel)
    if not what:
        return
    who = data.get("agent_type") or "main"
    line = "- %s [%s/%s] %s" % (C.now_iso()[11:], C.short_session(data), who, what)
    path = os.path.join(proj, ".agent", "log", C.today() + ".md")
    C.append_line(path, line, header="# Agent log %s\n\nAuto-appended by the agent-bootstrap PostToolUse hook. "
                                      "Format: time [session/agent] action." % C.today())


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # logging must never break the session
        sys.stderr.write("agent-bootstrap log hook: %r\n" % (exc,))
        sys.exit(0)
