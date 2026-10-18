# .agent/ - agent workflow state

Created by the `agent-bootstrap` skill. Commit everything here except `state/`.

| Path | What it is | Who writes it |
|---|---|---|
| `BASELINE.md` | The project before agents (the "before" log) | bootstrap + agent, once |
| `work/WI-*.md` | One file per work item: goal, plan, decisions, handoff | agents, continuously |
| `work/_TEMPLATE.md` | Template used by `bin/new-work-item.sh` | humans |
| `log/YYYY-MM-DD.md` | Automatic change log (the "after" log) | PostToolUse hook |
| `log/security.log` | Guard decisions (never values) | PreToolUse / ConfigChange hooks |
| `secrets.manifest` | Secret NAMES + keychain service; no values | humans via `bin/add-secret.sh` |
| `secrets.conf` | Extra guard rules for this project | humans only |
| `bootstrap-manifest.json` | What bootstrap installed (used by uninstall) | bootstrap |
| `BOOTSTRAP_REPORT.md` | What was configured and what to watch | bootstrap |
| `state/` | Per-session scratch (gitignored) | hooks |
| `bin/` | Helper scripts | bootstrap |

## Resume after a pause

1. Open Claude Code in the repo. The SessionStart hook lists the active work items and their next steps.
2. Tell the agent: "resume WI-NNN". It reads the work item's Handoff section, then the vault notes it links.

## Human-only commands (the guard blocks agents from running these)

```bash
.agent/bin/add-secret.sh NAME                  # store one secret in the Keychain
.agent/bin/migrate-env-to-keychain.sh .env     # move a dotenv file into the Keychain
.agent/bin/uninstall-agent-bootstrap.sh --project [--user]   # remove guardrails (close Claude Code first)
```
