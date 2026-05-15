# active-work.md schema

`active-work.md` is THE handoff file. A fresh agent in a new conversation reads it (plus `overview.md`) to know where to pick up. Optimize for that reader.

**Rolling state, not a log.** Each `update` overwrites the previous content.

The `_Last updated: by_` line should name the model and mode. `Opus 4.7 (auto)` beats `agent` — when something looks wrong later, the next reader knows whether it was the user typing or which model wrote it.

## Schema

```
---
type: active-work
project: <name>
updated: YYYY-MM-DD
tags: [context, active-work]
---

# Active Work

_Last updated: YYYY-MM-DD HH:MM by <model name + "(auto)" | user>_
_At commit: <short SHA, or "uncommitted">_

## Current focus
<1-3 sentences. What is the work-in-progress about? Why does it matter?>

## State
- **In flight:** <what's being worked on right now, with file paths>
- **Done this session:** <what was completed and committed/staged>
- **Blocked:** <anything waiting on user input, external dep, or unresolved>

## Pick up here
<Imperative instructions for the next agent. Be specific:
- "Open src/cart.ts:142 — the failing assertion is on the type of `payload`."
- "Run `npm test cart` — three tests fail; fix in order."
- If nothing is in flight, write: "No active work — pick a new task.">

## Open questions
<Questions the user needs to answer before progress unblocks. One per line. Empty if none.>

## Recent context
<3-5 bullets of session-level facts that aren't obvious from `git log`:
- "Tried approach X, failed because Y, switched to Z."
- "User wants the broker fee configurable per-listing, not global."
Skip anything obvious from the code or commit messages.>

## Related
<Wikilinks to whichever handoff files are relevant to the work in flight this session. Dynamic — changes each update. Always include [[overview]]. Add others based on what's being touched:
- [[overview]]
- [[backend]] — if backend work is in flight
- [[api]] — if API work is in flight
- [[gotchas]] — if a gotcha is load-bearing for the current work
- [[decisions]] — if recent decisions shape what's next>
```

## Length target

The whole file should fit in ~80 lines. If it grows past that, you're logging instead of summarizing — strip back.

## What does NOT belong here

- Architecture overview → `overview.md`
- API specs → `api.md`
- Stable decisions → `decisions.md`
- A history of past sessions — this is rolling. Past state is gone on purpose.
