#!/usr/bin/env python3
"""agent-bootstrap config guard  (Claude Code ConfigChange hook).

Claude Code fires ConfigChange when a settings file changes during a session.
Exiting 2 stops that change from taking effect in the running session. This
hook blocks changes that would remove the secret guard or switch hooks off,
so a prompt-injected agent cannot quietly disable its own guardrails.

To remove the guardrails on purpose, close Claude Code and run
.agent/bin/uninstall-agent-bootstrap.sh in your own terminal.
"""
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _abcommon as C  # noqa: E402

GUARD_MARK = "agent-bootstrap/guard_secrets.py"
USER_GUARD_MARK = "agent-bootstrap/hooks/guard_secrets.py"


def deny(proj, data, why):
    C.append_line(os.path.join(proj, ".agent", "log", "security.log"),
                  "%s BLOCK config-change source=%s reason=%s session=%s" % (
                      C.now_iso(), data.get("source"), why, C.short_session(data)),
                  header="# agent-bootstrap security log (decisions only, never values)")
    sys.stderr.write("[agent-bootstrap] configuration change blocked: %s\n" % why)
    sys.exit(2)


def main():
    data = C.read_input()
    proj = C.project_dir(data)
    source = data.get("source") or ""
    path = data.get("file_path") or ""
    if source not in ("user_settings", "project_settings", "local_settings") or not path:
        return
    if not os.path.isfile(path):
        if source == "project_settings" and C.is_bootstrapped(proj):
            deny(proj, data, "project settings file was removed")
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        settings = json.loads(text)
    except Exception:
        return  # unreadable / mid-write: Claude Code will not apply invalid JSON either
    if settings.get("disableAllHooks") is True:
        deny(proj, data, "disableAllHooks=true")
    if source == "project_settings" and C.is_bootstrapped(proj) and GUARD_MARK not in text:
        deny(proj, data, "project secret guard removed")
    if source == "user_settings":
        installed = os.path.join(os.path.expanduser("~"), ".claude", "agent-bootstrap", "installed.json")
        if os.path.isfile(installed) and USER_GUARD_MARK not in text:
            deny(proj, data, "user-level secret guard removed")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        sys.stderr.write("agent-bootstrap config guard error: %r\n" % (exc,))
        sys.exit(0)
