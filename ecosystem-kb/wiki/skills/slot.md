---
type: skill
updated: 2026-07-17
tags: [skill, wisp, routing]
source: built 2026-07-17; spec Wisp repo docs/superpowers/specs/2026-07-17-slot-skill-design.md (#110)
---

# slot

`/slot` — the Wisp Slot dance: snapshot the Routing map, rebind a sacrificial
family route (default `haiku`) to any Wisp Target, spawn the Agent tool with
that family word, restore only after every Slot-driven agent finishes. Durable
lease at `C:/Users/S.D/.claude/slot/lease.json` (absolute path on purpose — a
live run wrote it cwd-relative before the path was pinned; never overwritten;
stale lease = explicit recovery, crash cleanup is best-effort by design).

Iron rule: the Bridge resolves routing per request, so early restore silently
reroutes a live agent — a returned task id proves launch, not completion.
Aliases never work as Agent model values; family words only. Spawn labels the
agent's `description` with the real backend (`<target model>: <task>`, e.g.
`gpt-5.6-sol: reply with one`) since the family word misleads in the UI
(added 2026-07-17 after live runs). `wisp routing`
needs wisp-router > 2.0.10 — older global → run the source entry
(`bun packages/tui/src/index.tsx routing …`) from the hardcoded checkout
`D:/.claude/claude projects/autocomplete_extension` (never search for it; a
live run burned minutes hunting, and an accidental TUI open during that hunt
rewrote all four family routes to anthropic — repaired same session).

Built TDD-style: baseline agents failed the early-restore trap (“binding only
matters at spawn”); skill counters it; 3/3 pressure re-tests green; verified
live end-to-end through a bridged `claude-wisp` session
(`[bridge] route family 'claude-haiku-4-5…' -> codex model=gpt-5.6-terra`).
