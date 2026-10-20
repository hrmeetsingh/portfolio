"""Shared helpers for agent-bootstrap hooks.

Kept dependency-free and compatible with Python 3.9 (the python3 that ships
with the macOS Command Line Tools).
"""
import json
import os
import re
import sys
import time

MARKER = "agent-bootstrap"
ACTIVE_STATUSES = ("in-progress", "review", "blocked")


def read_input():
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def project_dir(data):
    d = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    return os.path.abspath(os.path.expanduser(d))


def agent_dir(proj):
    return os.path.join(proj, ".agent")


def is_bootstrapped(proj):
    return os.path.isfile(os.path.join(proj, ".agent", "bootstrap-manifest.json"))


def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def today():
    return time.strftime("%Y-%m-%d")


def append_line(path, line, header=None):
    """Append one line; create the file (with an optional header) if missing."""
    d = os.path.dirname(path)
    if not os.path.isdir(d):
        return False
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8") as f:
        if new and header:
            f.write(header.rstrip("\n") + "\n\n")
        f.write(line.rstrip("\n") + "\n")
    return True


def short_session(data):
    sid = str(data.get("session_id") or "unknown")
    return sid[:8]


def state_path(proj, data):
    sid = re.sub(r"[^A-Za-z0-9_-]", "", str(data.get("session_id") or "unknown"))[:64]
    return os.path.join(proj, ".agent", "state", "session-%s.json" % sid)


def load_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, obj):
    d = os.path.dirname(path)
    if not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


FRONT_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def parse_front_matter(text):
    """Very small YAML-ish parser: `key: value` lines only."""
    m = FRONT_RE.match(text)
    meta = {}
    if not m:
        return meta
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, v = line.split(":", 1)
            v = re.split(r"\s+#", v, 1)[0]  # drop trailing comments
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta


def work_items(proj):
    """Return a list of dicts for every .agent/work/WI-*.md file."""
    wdir = os.path.join(proj, ".agent", "work")
    items = []
    if not os.path.isdir(wdir):
        return items
    for name in sorted(os.listdir(wdir)):
        if not (name.startswith("WI-") and name.endswith(".md")):
            continue
        path = os.path.join(wdir, name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            continue
        meta = parse_front_matter(text)
        meta["_file"] = os.path.relpath(path, proj)
        meta["_mtime"] = os.path.getmtime(path)
        items.append(meta)
    return items


def active_work_items(proj):
    return [w for w in work_items(proj) if w.get("status", "").lower() in ACTIVE_STATUSES]
