---
id: WI-005
title: "Goodreads widget fallback for books card"
status: review   # todo | in-progress | blocked | review | done
branch: agent/WI-005-goodreads-widget-fallback-for-books-card
created: 2026-11-01
updated: 2026-11-01
owner: agent
next-step: User pushes the branch (git push -u origin agent/WI-005-goodreads-widget-fallback-for-books-card) and opens a PR; then mark done
---
# WI-005: Goodreads widget fallback for books card

## Goal

Goodreads retired its public shelf RSS feeds (late Oct 2026; `/review/list_rss/<id>` 404s, `/review/list/<id>` needs sign-in), so the Books card showed "Check the Goodreads user ID and proxyUrl". Make the card read the read shelf from the still-public Goodreads custom widget instead.

## Acceptance criteria

- [x] Card parses the widget output (`var widget_code = '...'` HTML with `gr_custom_*_<widget_id>` classes) into title, author, cover, link per book
- [x] ~~Both shelves work~~ Waived (user decision): only the `read` shelf is supported; Goodreads serves the read shelf even for the currently-reading widget 1793537588
- [x] A non-parseable proxy response (e.g. `Upstream error 404`) shows "Goodreads feed unavailable", not a silent empty list
- [x] `npm run build` and `npm run lint` pass
- [x] Apps Script contract documented here (script lives outside the repo)
- [x] User confirmed the card renders in `npm run dev`

## Plan (as executed)

1. Card (`src/components/books-card/index.tsx`): `parseRSSFeed` replaced by `parseWidget`: extract the JS string literal, unescape (`\"`, `<\/`, `\n`, `\uXXXX`), parse with DOMParser, read `[class^="gr_custom_each_container_"]` items. Link and cover URLs are resolved against goodreads.com and only http(s) is kept.
2. Single request `proxyUrl?shelf=read`.
3. Apps Script (applied by user, verified live): `doGet` fetches `https://www.goodreads.com/review/custom_widget/12291100?widget_id=1793537089` for `shelf=read` and returns the body as text. `WIDGETS` map allows adding more shelves.

## Decisions

| Date | Decision | Why | Alternatives rejected |
|---|---|---|---|
| 2026-11-01 | Use public custom widget via existing Apps Script proxy | Still returns 200 without sign-in for user 12291100; keeps live card and config shape | CSV export to JSON (manual refresh); Hardcover (migration); cookie scraping (credentials) |
| 2026-11-01 | Read shelf only; drop currently-reading (user) | widget_id is bound to a stored config and URL params are ignored; widget 1793537588 previews currently-reading in the generator but the public URL returns the read shelf (re-fetched twice, with referer/cache-bust) | Recreate widget; CSV export |
| 2026-11-01 | Validate link/cover URL scheme | Reviewer: a compromised proxy could inject `javascript:` hrefs | none |

## Files touched

- src/components/books-card/index.tsx - widget parser (prefix selectors so any widget_id suffix works), http(s)-only URLs, `\uXXXX` decoding, read shelf only, "Goodreads feed unavailable" error. `status: 'reading'` type and badge remain in `BookItem` but are unreachable now; kept in case currently-reading returns.

## Progress log

- 2026-11-01 - created; probed widget (query params ignored, widget_id selects shelf)
- 2026-11-01 - parser written; fixed class selectors (real widgets use `_<widget_id>` suffix, not `_1`)
- 2026-11-01 - currently-reading widget still serves read; dropped per user
- 2026-11-01 - user updated Apps Script; `?shelf=read` verified live (200, 10 books parsed by the card's extraction logic)
- 2026-11-01 - reviewer findings addressed: URL scheme validation, `\u` decoding, work item rewritten

- 2026-11-01 - user verified the card; committed locally as 'Read Goodreads books from the public widget' (not pushed)

## Blockers / open questions

- Currently-reading: revisit only if Goodreads fixes widget 1793537588 (re-fetch `custom_widget/12291100?widget_id=1793537588`; if it returns `shelf=currently-reading`, add it to the script's `WIDGETS` and restore the second request in the card).
- Untracked `.agent/work/WI-001-bootstrap-agent-workflow.md` is unrelated; do not commit it with this item.

## Handoff

Code and Apps Script are done and `npm run build` / `npm run lint` pass. Visual check done and committed locally; only push and PR remain (user). Re-run: `npm run dev`, open the Books card.
