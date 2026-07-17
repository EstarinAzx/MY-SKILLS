---
type: skill
updated: 2026-07-17
tags: [skill, wisp, routing, plugin]
source: built 2026-07-17; spec Wisp repo docs/superpowers/specs/2026-07-17-slot-skill-design.md (#110); session-awareness Wisp #124
---

# slot

`/slot` — the Wisp Slot dance: snapshot the Routing map, rebind a sacrificial
family route (default `haiku`) to any Wisp Target, spawn the Agent tool with
that family word, restore only after every Slot-driven agent finishes. Durable
lease at `~/.claude/slot/lease.json` (never overwritten; stale lease =
explicit recovery, crash cleanup is best-effort by design).

**Delivery (since 2026-07-17 evening): the plugin is the one copy.** Installed
as `wisp-slot@wisp-router` from a **local directory marketplace** pointing at
the Wisp checkout (`D:/.claude/claude projects/autocomplete_extension`). The
old personal skills-dir copy is retired to `~/.claude/_deprecated/slot/`
— the two-copies split is gone. Trap: directory marketplaces still install into
a **versioned cache** (`~/.claude/plugins/cache/wisp-router/wisp-slot/<ver>/`),
so repo edits reach the live skill/hook only after `claude plugin update
wisp-slot@wisp-router` — the FULL id; bare `wisp-slot` fails "not found" (bump
the plugin version for a new cache dir).

**Triage fast path (v1.1.1):** a plain "route X to family Y" ask with no
subagent to run is a persistent routing edit — one `wisp routing set`, surface
warnings, report the prior value, stop. No lease, no checklist, no restore
(added after a live run marched the full 9-step dance for a bare rebind and
left a cruft lease). The full procedure applies only when a subagent runs
through a temporary rebind.

**Session-awareness (Wisp #124, v1.1.0):** the plugin also ships a SessionStart
hook (all sources) — bridged sessions get a Wisp announcement, live family-route
snapshot (`wisp routing --json`, fail-soft), the headless CLI cheat sheet
(`wisp routing` / `wisp providers` / `wisp models <provider>`), and a stale-lease
warning; silent when unbridged. Plus a node statusline badge
(`[WISP fable→gpt-5.6-terra]`, live per-refresh resolution, `!LEASE` marker,
degrades to `[WISP]`). Bridged detection = `ANTHROPIC_BASE_URL` set AND Wisp
home exists (`WISP_HOME` honored) — env alone lies (profile trap). The badge is
wired into elucidate's composed `statusline-wrapper.ps1`, pointing at the
checkout path (stable across versions, unlike the cache).

Iron rule: the Bridge resolves routing per request, so early restore silently
reroutes a live agent — a returned task id proves launch, not completion.
Aliases never work as Agent model values; family words only. Spawn labels the
agent's `description` with the real backend (`<target model>: <task>`) since
the family word misleads in the UI (added 2026-07-17 after live runs; synced to
the plugin copy same day). History: pre-2.0.11 globals needed a source-checkout
fallback (`bun packages/tui/src/index.tsx routing …`) — retired, global is
2.0.13; a live run once hunted the checkout and an accidental TUI open rewrote
all four family routes to anthropic (repaired same session — hence "never
search the filesystem" stayed in the skill until retirement).

Built TDD-style: baseline agents failed the early-restore trap ("binding only
matters at spawn"); skill counters it; 3/3 pressure re-tests green; verified
live end-to-end through a bridged `claude-wisp` session
(`[bridge] route family 'claude-haiku-4-5…' -> codex model=gpt-5.6-terra`).
