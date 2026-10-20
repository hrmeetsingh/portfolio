---
id: WI-002
title: "Fix books card CORS proxy"
status: review   # todo | in-progress | blocked | review | done
branch: agent/WI-002-fix-books-card-cors-proxy
created: 2026-10-19
updated: 2026-10-19
owner: agent
next-step: User runs npm run dev to eyeball the Books card, then pushes agent/WI-002-fix-books-card-cors-proxy and opens a PR
---
# WI-002: Fix books card CORS proxy

## Goal

Books card loads Goodreads shelves again. The public CORS proxy (api.allorigins.win) is down, so route through our own Google Apps Script proxy.

## Acceptance criteria

- [x] Books card fetches both shelves via `books.proxyUrl` (curl-verified: 200 XML, ACAO *)
- [x] `npm run build` passes; no new lint errors (1 pre-existing no-unused-vars in src/utils/index.tsx)
- [ ] Visual check in browser (npm run dev) - pending, user to do

## Plan

1. Add `proxyUrl` to config types/sanitizer/config, point books-card at it, parse `res.data` directly.

## Decisions

| Date | Decision | Why | Alternatives rejected |
|---|---|---|---|
| 2026-10-19 | Google Apps Script proxy (`proxyUrl` in config) | allorigins 522, corsproxy.io needs API key; own Cloudflare Worker got 403 from Goodreads CloudFront | Public proxy chain, build-time JSON (user wants live fetch), Cloudflare Worker |

## Files touched

- gitprofile.config.ts - books.proxyUrl
- global.d.ts - Books.proxyUrl type
- src/interfaces/sanitized-config.tsx, src/utils/index.tsx - sanitize proxyUrl; display needs userId+proxyUrl
- src/components/books-card/index.tsx - fetch via proxyUrl (responseType text), parse res.data

## Progress log

- 2026-10-19 - created
- 2026-10-19 - diagnosed: allorigins 522, corsproxy.io 401, Cloudflare Worker blocked 403 by Goodreads CloudFront; Apps Script proxy verified with curl
- 2026-10-19 - implemented proxyUrl in config/types/sanitizer/books-card; build passes; reviewer: approve with nits
- 2026-10-19 - committed as 038c50b (5 source/config files + this item); not pushed
- Commit only the 5 source/config files; keep .agent/log, WI-001 and vault/ out of this commit (vault/ vs .vault/ looks like a stray dir, user to check)

## Blockers / open questions

## Handoff

Code done and committed (038c50b). Uncommitted leftovers not part of this item: .agent/log/*, WI-001 file. Apps Script ID is hardcoded in the script (12291100); changing account = edit script + Deploy > Manage deployments > New version. Re-test: `curl -sL "<proxyUrl>?shelf=read" | head`. Don't run prettier on gitprofile.config.ts (reformats unrelated lines).
