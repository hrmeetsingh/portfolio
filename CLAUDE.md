# portfolio

Harmeet Singh's personal portfolio site, a fork of [GitProfile](https://github.com/arifszn/gitprofile) (Vite + React 18 + TypeScript, Tailwind/DaisyUI). It is configured through `gitprofile.config.ts` and rendered by `src/components/gitprofile.tsx` as a set of cards (avatar, details, skills, experience, education, certifications, publications, projects, blog, books). Blog posts come from Medium/Dev via `@arifszn/blog-js`, books from Goodreads RSS through a CORS proxy. It is deployed to GitHub Pages by `.github/workflows/deploy-pages.yml`, and `fetch-and-commit.yml` refreshes a resume PDF weekly.

## Conventions

- One folder per component in `src/components/<kebab-name>/index.tsx`, function components with hooks.
- Formatting by Prettier (`.prettierrc`), linting by ESLint with `--max-warnings 0`; run both before committing.
- Site content and feature toggles live in `gitprofile.config.ts`, not in components.
- No automated tests exist; verify with `npm run build` (tsc + vite build) and `npm run lint`.
- Network fetches (Goodreads, Medium) fail soft with an error message in the card.

<!-- agent-bootstrap:start (managed block; re-running the skill rewrites it, so edit outside it) -->
## Agent workflow

- **Map first.** Start at `.vault/_map.md`, then the module notes in `.vault/modules/`. After structural changes run `python3 .agent/bin/vault_extract.py`, then fill any `## Purpose` still marked `agent: fill`.
- **Work items are the unit of work and handoff.** Everything lives in `.agent/work/WI-*.md`. Create one with `.agent/bin/new-work-item.sh "<title>" --branch`. Keep `status`, `next-step`, Decisions, Files touched and Handoff current. A Stop hook sends you back if code changed and the item was not updated.
- **Branches.** One branch per item, named `agent/WI-NNN-<slug>`. Commit in small steps. `git push` always asks the user.
- **Approval gates.** Plan first and wait for approval before editing. Before proposing a commit, run the `reviewer` subagent against the item's acceptance criteria.
- **History.** The git tag `pre-agent-baseline` marks where agent work began. `.agent/BASELINE.md` describes the project at that point. `.agent/log/` is appended automatically by hooks.
- **Secrets.** Never read, print or write secret values. A command that needs secrets runs as `.agent/bin/run-with-secrets.sh -- <command>`; the user approves every use and macOS asks again. Reading `.env` files, keychains or credential stores is blocked by hooks; ask the user instead.
- **Guardrail files are human-only.** That covers `.claude/settings*.json`, `.claude/hooks/`, `.agent/secrets.*` and `.git/hooks/`.

## Commands

- Install: `npm install`
- Build: `npm run build`
- Test: _not detected - ask the user and fill in_
- Lint: `npm run lint`
- Format: `npm run prettier:fix`
- Run: `npm run dev`
<!-- agent-bootstrap:end -->
