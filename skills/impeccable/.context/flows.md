---
type: flows
project: impeccable
updated: 2026-06-11
tags: [flows]
---
# Flows

## Live browser iteration (/impeccable live)
- **Question:** How does the live browser iteration flow work in scripts/, end to end?  **Lens:** understand
- **Summary:** `live.mjs` boots a token-protected localhost helper (port 8400+) and injects `/live.js` into the project's HTML; the in-page overlay lets the user pick an element and click Go, which POSTs a `generate` event (element HTML + computed styles + optional annotated screenshot) that the server journals to `.impeccable/live/sessions/<id>.jsonl` and hands to the agent's long-poll; the agent wraps the element in source via `live-wrap.mjs`, writes 3 variant divs + scoped CSS in one edit, replies `done`; the dev server's HMR re-renders, a MutationObserver flips the overlay to CYCLING for arrow-key cycling, and accept/discard events are auto-applied to source by `live-accept.mjs` (with a required agent "carbonize" cleanup when inline CSS was stitched in).
- **Entry:** scripts/live.mjs:30 (liveCli)
- **Key files:** scripts/live-server.mjs (event hub: SSE + /events + /poll + journal), scripts/live-browser.js (overlay: handleGo:2525, startVariantObserver:2085, handleAccept:2989), scripts/live-wrap.mjs (source wrapper), scripts/live-accept.mjs (accept/discard mutator), scripts/live-session-store.mjs (durable journal); contract doc: reference/live.md
- **Updated:** 2026-06-11

## Live-mode variant accept (browser → source file)
- **Question:** Why does accepting a variant in the live browser flow sometimes never land in the source file?  **Lens:** bug
- **Summary:** Accept is two-phase: the browser shows "confirmed" as soon as the live server merely receives the event, while the real source rewrite happens later in live-accept.mjs — and when that rewriter bails (markers not found, generated file), it reports success-shaped `agent_done`, leaving no error anywhere except the agent's stdout.
- **Entry:** scripts/live-browser.js:2989 (`handleAccept`, POST /events at :3009)
- **Key files:** scripts/live-browser.js, scripts/live-server.mjs, scripts/live-poll.mjs, scripts/live-accept.mjs, scripts/live-completion.mjs
- **Key hops:** server enqueue+lease live-server.mjs:561/:605 → agent poll live-poll.mjs:117 → auto-run rewriter live-poll.mjs:150 → file search live-accept.mjs:532 (EXTENSIONS whitelist :20, depth cap :550, cwd-relative) → write live-accept.mjs:205 → completion mapping live-completion.mjs:6 (handled:false → `agent_done`) → store clears pendingEvent live-session-store.mjs:182.
- **Loss modes:** (1) handled:false mapped to agent_done, browser only toasts on `error` (live-browser.js:2240); (2) generated-file fallback requires the agent to persist manually (live-accept.mjs:74); (3) markers unfindable: non-whitelisted extension, >5 dir depth, wrong poll cwd, formatter stripped markers; (4) server stopped before any poll — browser already confirmed and DOM-swapped (live-browser.js:3046).
- **Updated:** 2026-06-11
