# Baseline: portfolio before agents

This file records the state of the project when agent-driven development began. It is the "before" half of the change history. Everything after the git tag `pre-agent-baseline` is agent-era work, tracked in `.agent/log/` and in commits that reference work items.

## Facts (generated)

| Item | Value |
|---|---|
| Bootstrapped | 2026-10-18 14:17 |
| Baseline tag | `pre-agent-baseline` → `cf1ecb2` |
| Branch at bootstrap | main |
| Commits before agents | 1097 |
| Contributors before agents | 28 |
| First commit | 2021-08-21 050ccad Initial commit |
| Last manual commit | 2026-07-14 2e9c427 Update cors proxy |
| Uncommitted paths at bootstrap | 1 (see `git stash list` / working tree) |
| Detected stack | typescript |
| Manifests | package.json |

Useful queries:

```bash
git log --oneline pre-agent-baseline            # manual era
git log --oneline pre-agent-baseline..HEAD      # agent era
git log pre-agent-baseline..HEAD --grep "Agent-Work-Item:"   # commits tied to work items
```

## Manual-era history (agent fills from `git log`)

- **2021-08:** Repository starts as the upstream GitProfile project (1097 commits and 28 contributors include upstream history).
- **2024-08 (late):** Personal fork set up: GitHub Pages deploy workflow, lint and peer-dependency fixes, formatting.
- **2024-08/09:** Weekly `fetch-and-commit` workflow to pull a resume PDF using repo secrets, plus metadata and analytics.
- **2024-09:** Styling passes and metadata updates.
- **2024-12 to 2025-02:** Profile, projects and blog updates, including Medium blogs.
- **2025-01:** Theme switching enabled and default theme changed.
- **2025-09:** Base path changed to relative for hosting, Twitter renamed to X, a downloadable resume added and then reverted.
- **2025-11:** Dynamic Goodreads books card (parallel shelf fetching), CORS proxy, title icons, blog and details-card styling.
- **2026-01 to 2026-07:** CORS fixes and proxy provider changes; the last manual commit is "Update cors proxy" (2026-07-14).

## Architecture at baseline (agent fills)

A single-page Vite/React app. `src/main.tsx` mounts `GitProfile` (`src/components/gitprofile.tsx`), which reads `gitprofile.config.ts` and composes the card components. Data comes from the GitHub API, Medium/Dev (blog-js) and Goodreads RSS (via a third-party CORS proxy). Builds deploy to GitHub Pages. See [[.vault/_map|the vault map]] for module notes.

## Known issues and debt at baseline (agent fills; confirm with the user)

- No TODO/FIXME/HACK markers found in `src`.
- No automated tests (no test script in `package.json`).
- Fragile (inferred): Goodreads books fetching depends on a third-party CORS proxy that has been swapped repeatedly (commits in 2025-11, 2026-01, 2026-02, 2026-07).
- Inferred: `fetch-and-commit.yml` pushes to a `static-data` branch using repo secrets; check it still works.
- Unchecked: dependency freshness (`@arifszn/blog-js` and other packages).

## Work in progress at baseline (confirm with the user)

None. The user confirmed nothing was in progress at bootstrap.
