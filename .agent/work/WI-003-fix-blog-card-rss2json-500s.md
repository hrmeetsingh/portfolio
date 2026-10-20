---
id: WI-003
title: "Fix blog card rss2json 500s"
status: review   # todo | in-progress | blocked | review | done
branch: agent/WI-003-fix-blog-card-rss2json-500s
created: 2026-10-20
updated: 2026-10-20
owner: agent
next-step: User runs npm run dev, blocks api.rss2json.com in DevTools to confirm the fallback, then pushes the branch and opens a PR
---
# WI-003: Fix blog card rss2json 500s

## Goal

The Blogs card always shows posts, even when api.rss2json.com intermittently returns 500.

## Acceptance criteria

- [x] A failed/empty rss2json response is retried (3 attempts, 1s/2s backoff) before giving up
- [x] If all attempts fail, the last good result cached in localStorage is shown, else the static `wpBlogs` list
- [x] A successful fetch refreshes the cache
- [x] No state update after unmount or source/username change
- [x] `npm run build` passes; no new lint errors in `src/components/blog-card/index.tsx`

## Plan

1. Add `fetchMediumWithRetry`, `readCache`, `writeCache` in `blog-card/index.tsx`.
2. Use them in the medium branch of the effect; add an `ignore` flag.

## Decisions

| Date | Decision | Why | Alternatives rejected |
|---|---|---|---|
| 2026-10-20 | Retry + cache + static fallback in the component | `@arifszn/blog-js` swallows errors and returns `[]`, so empty is the only failure signal | Custom proxy (like Apps Script for books): out of scope unless 500s persist |

## Files touched

- `src/components/blog-card/index.tsx` - retry helper, localStorage cache, fallback, effect cleanup

## Progress log

- 2026-10-20 - created
- 2026-10-20 - implemented; build passes. Lint on `blog-card/index.tsx` is clean; remaining prettier errors in `fallback-list.tsx` and other files pre-date this item.

## Blockers / open questions

- Branch was cut from `agent/WI-002-fix-books-card-cors-proxy`, so it contains WI-002 commits. Merge WI-002 first or rebase onto main.
- Not verified in a browser: retries and fallback were not exercised against a real 500.

## Handoff

State: code done and building. Resume by running `npm run dev`, blocking `api.rss2json.com` in DevTools network request blocking, and confirming retries then fallback posts. Then unblock, reload and confirm live posts. Re-run: `npm run build`, `npx eslint src/components/blog-card/index.tsx`.
