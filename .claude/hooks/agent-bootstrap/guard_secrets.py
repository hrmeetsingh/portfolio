#!/usr/bin/env python3
"""agent-bootstrap secret guard  (Claude Code PreToolUse hook).

Runs before EVERY tool call. The model cannot skip it: Claude Code executes it
and obeys the decision it prints.

  * deny  - reading secret files / credential stores / the Keychain, dumping
            the environment, writing literal secrets, tampering with the
            guardrails, or running human-only scripts.
  * ask   - running a command through .agent/bin/run-with-secrets.sh. The
            user is prompted every time (macOS Keychain then prompts again).
  * (no output) - no objection; the normal permission flow continues.

Fails closed: an internal error exits 2, which blocks the tool call.
Policy extensions per project live in .agent/secrets.conf (see template).
Compatible with Python 3.9+, standard library only.
"""
import fnmatch
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _abcommon as C  # noqa: E402

SCOPE = "project"
if "--scope" in sys.argv:
    try:
        SCOPE = sys.argv[sys.argv.index("--scope") + 1]
    except IndexError:
        pass

HOME = os.path.expanduser("~")
PREFIX = "[agent-bootstrap guard] "

# ---------------------------------------------------------------- policies --
EXAMPLE_SUFFIXES = (".example", ".sample", ".template", ".dist", ".defaults", ".pub")

SECRET_BASENAMES = [
    ".env", ".env.*", ".envrc", "*.pem", "*.key", "*.p12", "*.pfx", "*.jks",
    "*.keystore", "*.kdbx", "id_rsa*", "id_ed25519*", "id_ecdsa*", "id_dsa*",
    ".netrc", "_netrc", ".git-credentials", ".pgpass", "credentials.json",
    "*service-account*.json", "secrets.yml", "secrets.yaml", "secrets.json",
    ".secrets", ".secrets.*", "*.tfvars", "terraform.tfstate*",
]
SECRET_PATH_PARTS = [
    "/.ssh/", "/.aws/", "/.gnupg/", "/.config/gcloud/", "/.config/gh/",
    "/.docker/config.json", "/.kube/config", "/Library/Keychains/",
    "/.password-store/", "/.azure/", "/.config/op/",
]
HOME_ONLY = [".npmrc", ".pypirc", ".yarnrc.yml", ".gem/credentials", ".cargo/credentials.toml",
             ".cargo/credentials", ".m2/settings.xml", ".gradle/gradle.properties"]

GUARDED_RE = re.compile(
    r"\.claude/settings(\.local)?\.json|\.claude/hooks\b|\.claude/agent-bootstrap\b|"
    r"agent-bootstrap/hooks\b|\.agent/secrets\.(conf|manifest)|\.agent/bootstrap-manifest\.json|"
    r"\.git/hooks\b|managed-settings\.json"
)
HUMAN_ONLY_RE = re.compile(
    r"migrate-env-to-keychain|add-secret\.sh|uninstall-agent-bootstrap|agent-bootstrap/scripts/uninstall\.sh"
)
KEYCHAIN_RE = re.compile(
    r"\bsecurity\b[^;&|\n]*\b(find-(generic|internet)-password|dump-keychain|export|"
    r"add-(generic|internet)-password|delete-(generic|internet)-password|unlock-keychain|"
    r"set-key-partition-list|set-generic-password-partition-list)\b"
)
CRED_CLI_RE = re.compile(
    r"\b(op\s+(read|inject|run|item\s+get|document\s+get)|bw\s+get|gh\s+auth\s+token|"
    r"gcloud\s+auth\s+(print-access-token|print-identity-token|application-default\s+print-access-token)|"
    r"aws\s+configure\s+(get|export-credentials)|aws\s+sts\s+get-session-token|"
    r"vault\s+(kv\s+get|read)|git\s+credential\s+fill|heroku\s+auth:token|doppler\s+secrets|"
    r"az\s+account\s+get-access-token|secret-tool\s+lookup|pass\s+show)\b"
)
ENV_DUMP_INLINE_RE = re.compile(
    r"os\.environ\b(?!\s*(\[|\.get))|process\.env\b(?!\s*(\.|\[))|\bENV\.to_h\b|"
    r"\bputs\s+ENV\b|/proc/[^\s]*/environ|\bgetenv\(\s*\)"
)
SECRET_VALUE_RES = [
    ("aws-access-key", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{50,}")),
    ("anthropic-key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("openai-key", re.compile(r"\bsk-(proj-)?[A-Za-z0-9_-]{32,}")),
    ("slack-token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("stripe-live-key", re.compile(r"\b(sk|rk)_live_[A-Za-z0-9]{20,}")),
]
PLACEHOLDER_RE = re.compile(r"EXAMPLE|example|XXXX|xxxx|0000000|your[-_]?key|REDACTED|<", re.I)

READONLY_VERBS = {"cat", "less", "more", "head", "tail", "ls", "grep", "rg", "jq", "diff",
                  "wc", "stat", "file", "test", "[", "md5", "md5sum", "shasum", "sha256sum"}
GIT_SAFE_SUBCMDS = {"add", "commit", "diff", "log", "show", "status", "ls-files", "blame", "check-ignore"}
SPLIT_RE = re.compile(r"\|\||&&|[;|&\n]|\$\(|`|\(|\)")
SAMPLE_SECRET_NAMES = [".env", ".env.local", ".envrc", "id_rsa", "server.pem", "server.key", "secrets.json"]


# ----------------------------------------------------------- project conf --
def load_conf(proj):
    conf = {"path": [], "cmd": [], "allow-path": []}
    path = os.path.join(proj, ".agent", "secrets.conf")
    if not os.path.isfile(path):
        return conf
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, val = line.split(":", 1)
            key, val = key.strip().lower(), val.strip()
            if key in conf and val:
                conf[key].append(val)
    compiled = []
    for rx in conf["cmd"]:
        try:
            compiled.append(re.compile(rx))
        except re.error:
            pass
    conf["cmd"] = compiled
    return conf


def load_manifest_names(proj):
    names = []
    path = os.path.join(proj, ".agent", "secrets.manifest")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", line):
                    names.append(line)
    return names


# ------------------------------------------------------------ path checks --
def normalize(path, cwd):
    p = os.path.expanduser(str(path).strip().strip("'\""))
    if not os.path.isabs(p):
        p = os.path.join(cwd, p)
    return os.path.normpath(p)


def secret_path_reason(path, cwd, proj, conf):
    if not path:
        return None
    p = normalize(path, cwd)
    base = os.path.basename(p)
    rel = os.path.relpath(p, proj) if p.startswith(proj + os.sep) else p
    for g in conf["allow-path"]:
        if fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(base, g):
            return None
    if base.lower().endswith(EXAMPLE_SUFFIXES):
        return None
    for g in SECRET_BASENAMES:
        if fnmatch.fnmatch(base, g):
            return "secret-file:%s" % g
    unix = p.replace("\\", "/")
    for part in SECRET_PATH_PARTS:
        if part in unix + ("/" if not unix.endswith("/") else ""):
            return "credential-store:%s" % part.strip("/")
    for name in HOME_ONLY:
        if unix == os.path.join(HOME, name).replace("\\", "/"):
            return "credential-store:~/%s" % name
    for g in conf["path"]:
        if fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(base, g):
            return "project-rule:%s" % g
    return None


def guarded_path(path, cwd):
    if not path:
        return False
    p = normalize(path, cwd).replace("\\", "/")
    return bool(GUARDED_RE.search(p)) or p.startswith(os.path.join(HOME, ".claude", "agent-bootstrap"))


# --------------------------------------------------------- bash analysis --
def tokens(segment):
    out = []
    for raw in segment.split():
        raw = raw.strip("\"'`(){}")
        for piece in re.split(r"[=<>:,]", raw):
            piece = piece.strip("\"'`(){}")
            if piece and not piece.startswith("-") and not piece.startswith("$"):
                out.append(piece)
    return out


def first_words(segment):
    words = segment.strip().split()
    # skip leading VAR=value assignments and harmless wrappers
    while words and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[0]) or
                     words[0] in ("sudo", "time", "nice", "nohup", "command", "builtin", "exec")):
        words = words[1:]
    return words


def env_dump(segment):
    w = first_words(segment)
    if not w:
        return False
    verb = os.path.basename(w[0])
    rest = w[1:]
    if verb == "printenv":
        return True
    if verb in ("env", "set", "export", "declare", "typeset") and not rest:
        return True
    if verb == "export" and rest and rest[0] == "-p":
        return True
    if verb in ("declare", "typeset") and rest and re.match(r"^-[a-zA-Z]*[px]", rest[0]) and len(rest) == 1:
        return True
    return False


def analyse_bash(cmd, cwd, proj, conf):
    """Return (decision, rule, reason) or None."""
    cmd = cmd.replace("${HOME}", HOME).replace("$HOME", HOME)
    if "disableAllHooks" in cmd:
        return ("deny", "tamper:disableAllHooks", "Disabling hooks is not allowed for agents.")
    if HUMAN_ONLY_RE.search(cmd):
        return ("deny", "human-only-script",
                "This script handles secret values or removes guardrails, so only a human may run it. "
                "Ask the user to run it in their own terminal.")
    if KEYCHAIN_RE.search(cmd):
        return ("deny", "keychain",
                "Direct Keychain access is blocked. Run the command through "
                ".agent/bin/run-with-secrets.sh -- <command>, which asks the user each time.")
    if CRED_CLI_RE.search(cmd):
        return ("deny", "credential-cli",
                "Printing credentials from a credential CLI is blocked. Use .agent/bin/run-with-secrets.sh.")
    if ENV_DUMP_INLINE_RE.search(cmd):
        return ("deny", "env-dump", "Dumping the process environment is blocked because it can expose secrets.")
    for name, rx in SECRET_VALUE_RES:
        for m in rx.finditer(cmd):
            if not PLACEHOLDER_RE.search(m.group(0)):
                return ("deny", "literal-secret:%s" % name,
                        "The command contains what looks like a real %s. Never place secret values in "
                        "commands; reference them through run-with-secrets.sh instead." % name)
    for rx in conf["cmd"]:
        if rx.search(cmd):
            return ("deny", "project-rule:cmd", "Blocked by a project rule in .agent/secrets.conf.")

    segments = [s for s in SPLIT_RE.split(cmd) if s.strip()]
    for seg in segments:
        if env_dump(seg):
            return ("deny", "env-dump", "Printing environment variables is blocked because it can expose secrets.")
        if GUARDED_RE.search(seg) or os.path.join(HOME, ".claude", "agent-bootstrap") in seg:
            w = first_words(seg)
            verb = os.path.basename(w[0]) if w else ""
            safe = verb in READONLY_VERBS or (verb == "git" and len(w) > 1 and w[1] in GIT_SAFE_SUBCMDS)
            writes = bool(re.search(r"(^|[^0-9&])>(?!\s*&|\s*/dev/null)", seg)) or bool(
                re.search(r"(^|\s)(tee|sed\s+-i\S*|perl\s+-\S*i\S*)(\s|$)|--in-place", seg))
            if not safe or writes:
                return ("deny", "tamper:guardrail-files",
                        "Agent guardrail files (.claude/settings*.json, .claude/hooks, .agent/secrets.*, "
                        ".git/hooks) can only be changed by a human.")
        w = first_words(seg)
        if w and os.path.basename(w[0]) in ("echo", "printf"):
            continue  # literal text, e.g. echo ".env" >> .gitignore
        for tok in tokens(seg):
            why = secret_path_reason(tok, cwd, proj, conf)
            if why:
                return ("deny", why,
                        "Access to secret files and credential stores is blocked (%s). Ask the user, or use "
                        ".agent/bin/run-with-secrets.sh for commands that need secrets." % why)

    if re.search(r"run-with-secrets(\.sh)?\b", cmd):
        inner = cmd.split(" -- ", 1)[1] if " -- " in cmd else cmd
        names = load_manifest_names(proj)
        if re.search(r"\b(echo|printf|tee|cat)\b[^;&|]*\$", inner):
            return ("deny", "secrets:echo", "Commands run with secrets must not echo variables.")
        for seg in [s for s in SPLIT_RE.split(inner) if s.strip()]:
            if env_dump(seg):
                return ("deny", "secrets:env-dump", "Commands run with secrets must not print the environment.")
            w = first_words(seg)
            if w and os.path.basename(w[0]) in ("echo", "printf", "cat", "tee") and "$" in seg:
                return ("deny", "secrets:echo", "Commands run with secrets must not echo variables.")
        for n in names:
            if re.search(r"\$\{?%s\b" % re.escape(n), inner):
                return ("deny", "secrets:reference",
                        "The command references secret %s directly; let the program read it from its "
                        "environment instead." % n)
        listed = ", ".join(names) if names else "(no names in .agent/secrets.manifest yet)"
        return ("ask", "secrets:wrapper",
                "This command will receive secrets: %s. macOS will also ask before releasing each value. "
                "Read the full command before approving." % listed)
    return None


# -------------------------------------------------------------- decisions --
def log_decision(proj, data, decision, rule, tool):
    if SCOPE == "user" and project_guard_registered(proj):
        return
    path = os.path.join(proj, ".agent", "log", "security.log")
    C.append_line(path, "%s %s tool=%s rule=%s session=%s scope=%s" % (
        C.now_iso(), decision.upper(), tool, rule, C.short_session(data), SCOPE),
        header="# agent-bootstrap security log (decisions only, never values)")


def emit(proj, data, tool, decision, rule, reason):
    log_decision(proj, data, decision, rule, tool)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": PREFIX + reason,
    }}))
    sys.exit(0)


def project_guard_registered(proj):
    path = os.path.join(proj, ".claude", "settings.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return "agent-bootstrap/guard_secrets.py" in f.read()
    except Exception:
        return False


def content_strings(tool, ti):
    if tool == "Write":
        return [ti.get("content") or ""]
    if tool == "Edit":
        return [ti.get("new_string") or ""]
    if tool == "MultiEdit":
        return [e.get("new_string") or "" for e in (ti.get("edits") or []) if isinstance(e, dict)]
    if tool == "NotebookEdit":
        return [ti.get("new_source") or ""]
    return []


def main():
    data = C.read_input()
    tool = data.get("tool_name") or ""
    ti = data.get("tool_input") or {}
    proj = C.project_dir(data)
    cwd = data.get("cwd") or proj

    # The user-level copy steps aside when the project registers its own guard.
    if SCOPE == "user" and project_guard_registered(proj):
        return
    conf = load_conf(proj)

    if tool == "Bash" or tool == "PowerShell":
        res = analyse_bash(str(ti.get("command") or ""), cwd, proj, conf)
        if res:
            emit(proj, data, tool, res[0], res[1], res[2])
        return

    if tool in ("Read", "Edit", "Write", "MultiEdit", "NotebookEdit"):
        target = ti.get("file_path") or ti.get("notebook_path") or ""
        if tool != "Read" and guarded_path(target, cwd):
            emit(proj, data, tool, "deny", "tamper:guardrail-files",
                 "Agent guardrail files can only be changed by a human.")
        why = secret_path_reason(target, cwd, proj, conf)
        if why:
            emit(proj, data, tool, "deny", why,
                 "Secret files and credential stores are off-limits to agents (%s). Ask the user." % why)
        for text in content_strings(tool, ti):
            for name, rx in SECRET_VALUE_RES:
                for m in rx.finditer(text):
                    if not PLACEHOLDER_RE.search(m.group(0)):
                        emit(proj, data, tool, "deny", "literal-secret:%s" % name,
                             "The new content contains what looks like a real %s. Keep secrets in the "
                             "Keychain and read them from the environment at run time." % name)
        return

    if tool == "Grep":
        why = secret_path_reason(ti.get("path") or "", cwd, proj, conf)
        glob = ti.get("glob") or ""
        if not why and glob:
            for sample in SAMPLE_SECRET_NAMES:
                if fnmatch.fnmatch(sample, glob) and secret_path_reason(sample, cwd, proj, conf):
                    why = "secret-glob:%s" % glob
                    break
        if why:
            emit(proj, data, tool, "deny", why, "Searching inside secret files is blocked (%s)." % why)
        return

    if tool in ("Glob", "WebSearch", "WebFetch", "TodoWrite", "Task", "Agent", "AskUserQuestion"):
        return

    # Unknown tools (for example MCP filesystem servers): inspect path-like fields.
    if isinstance(ti, dict):
        for k, v in ti.items():
            if isinstance(v, str) and re.search(r"path|file|uri|filename", k, re.I):
                why = secret_path_reason(v.replace("file://", ""), cwd, proj, conf)
                if why:
                    emit(proj, data, tool, "deny", why, "Secret files are off-limits to agents (%s)." % why)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # fail closed
        sys.stderr.write(PREFIX + "guard error, blocking for safety: %r\n" % (exc,))
        sys.exit(2)
