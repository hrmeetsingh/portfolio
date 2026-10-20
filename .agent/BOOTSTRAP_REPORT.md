# agent-bootstrap report

Generated 2026-10-18 14:17 for `/Users/harmeetsingh/Documents/code/portfolio`.

## What was configured

| Area | Result |
|---|---|
| Baseline | tag `pre-agent-baseline` created at 2e9c427; `.agent/BASELINE.md` (agent fills the narrative) |
| Change log | PostToolUse hook appends to `.agent/log/YYYY-MM-DD.md`; commits on `agent/WI-*` branches get an `Agent-Work-Item` trailer (installed in .git/hooks/prepare-commit-msg) |
| Handoff | work items in `.agent/work/`; SessionStart hook injects active items; Stop hook enforces handoff updates |
| Project map | Obsidian vault in `.vault/` (vault: .vault | modules: 28 | dependency edges: 54 | archived notes: 0) |
| Secret guard (project) | PreToolUse hook on every tool + deny/ask rules in `.claude/settings.json` |
| Secret guard (user) | one shared PreToolUse + ConfigChange hook in `~/.claude/settings.json` |
| Tamper protection | ConfigChange hook blocks removing the guard or `disableAllHooks` mid-session; Edit deny rules on guardrail files |
| Subagents | `.claude/agents/`: explorer, implementer, reviewer, vault-curator (4 new) |
| CLAUDE.md | CLAUDE.md: created |
| Fail-closed guard | yes (`onFailure: block`) |

Detected stack: typescript. Commands: install=`npm install`, build=`npm run build`, lint=`npm run lint`, run=`npm run dev`

### Permission rules added

Project (`.claude/settings.json`):
- deny: `Read(.env)`, `Read(.env.*)`, `Read(!.env.example)`, `Read(!.env.sample)`, `Read(!.env.template)`, `Read(.envrc)`, `Read(**/*.pem)`, `Read(**/*.key)`, `Read(**/*.p12)`, `Read(**/*.pfx)`, `Read(**/id_rsa*)`, `Read(**/id_ed25519*)`, `Read(**/credentials.json)`, `Read(**/*.tfvars)`, `Edit(/.claude/settings.json)`, `Edit(/.claude/settings.local.json)`, `Edit(/.claude/hooks/**)`, `Edit(/.agent/secrets.conf)`, `Edit(/.agent/secrets.manifest)`, `Edit(/.agent/bootstrap-manifest.json)`, `Bash(security find-generic-password *)`, `Bash(security find-internet-password *)`, `Bash(security dump-keychain *)`, `Bash(printenv *)`, `Bash(env)`
- ask: `Bash(*run-with-secrets*)`, `Bash(git push *)`
- settings keys: `disableBypassPermissionsMode`, `defaultMode`

User (`~/.claude/settings.json`):
- deny: (none new)

## Be careful about

1. **Don't click "Always Allow" in the macOS Keychain dialog** for `security`. That removes the per-access prompt for that item. Click **Allow**.
2. **Read the full command before approving `run-with-secrets.sh`.** The approved command gets real secret values in its environment.
3. **Choosing "Yes, don't ask again" on a prompt** saves an allow rule to `.claude/settings.local.json`. Ask and deny rules still win over it, but review that file now and then.
4. **Deny rules match command text.** `/usr/bin/cat .env` or a Python script that opens `.env` is caught by the hook's patterns, not by the rules, and only best-effort. The real protection is that secrets no longer live in the repo. Move them to the Keychain (see the secrets report).
5. **Guardrail edits are human-only.** Agents can't edit `.claude/settings*.json`, `.claude/hooks/`, `.agent/secrets.*` or `~/.claude/settings.json`, and Claude Code can't make those edits for you while the guard is active. Edit them yourself, then restart the session.
6. **Uninstall with Claude Code closed:** `.agent/bin/uninstall-agent-bootstrap.sh --project [--user]`. While a session runs, the ConfigChange hook blocks the change.
7. **Default mode is plan** (if it was added above). Every session starts read-only until you approve a plan. Remove `permissions.defaultMode` to change this.
8. **Strongest option.** If you want the guard to be impossible to disable from the repo, copy the deny rules and hooks into managed settings (see reference/security-model.md).

## Secrets

`dotenv files: 0 | other secret files: 0 | hard-coded findings: 0 | ever committed: 0`. Full list in `.agent/state/secrets-report.md` (names only).

## Verification

```
Guard decisions (synthetic tool calls):
PASS  deny  Read .env
PASS  deny  Read config/.env.production
PASS  deny  Read ~/.ssh key
PASS  deny  cat .env
PASS  deny  keychain read via absolute path
PASS  deny  keychain dump inside sh -c
PASS  deny  printenv
PASS  deny  env | grep
PASS  deny  python os.environ dump
PASS  deny  gh auth token
PASS  deny  copy .env
PASS  deny  literal AWS key in command
PASS  deny  write literal AWS key
PASS  deny  edit project settings
PASS  deny  overwrite guard hook
PASS  deny  disableAllHooks via shell
PASS  deny  delete guard hook
PASS  deny  agent runs human-only add-secret
PASS  deny  agent runs uninstall
PASS  deny  grep inside .env
PASS  deny  secrets wrapper + printenv
PASS  ask   secrets wrapper asks every time
PASS  allow Read README.md
PASS  allow Read .env.example
PASS  allow git status
PASS  allow echo .env >> .gitignore
PASS  allow read project settings
PASS  allow documented placeholder key

Settings:
PASS  project settings parse
PASS  project hooks registered
PASS  project deny rules present
PASS  ask rule for run-with-secrets
PASS  hooks not disabled
PASS  user-level guard registered (~/.claude/settings.json)
PASS  user-level guard script present
PASS  exactly one user-level guard entry
PASS  guard fails closed if it cannot start (onFailure: block)

Other hooks:
PASS  SessionStart injects context
PASS  ConfigChange accepts the current settings

Project files:
PASS  .agent/BASELINE.md
PASS  .agent/work/_TEMPLATE.md
PASS  .agent/secrets.manifest
PASS  .agent/bin/run-with-secrets.sh
PASS  .agent/bin/vault_extract.py
PASS  CLAUDE.md
PASS  .vault/_map.md
PASS  git tag pre-agent-baseline

OK: 0 failed check(s)
```
