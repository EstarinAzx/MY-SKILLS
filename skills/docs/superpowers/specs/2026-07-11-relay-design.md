# /relay — Self-Relaying Loops — Design

**Date:** 2026-07-11
**Status:** Approved (brainstorm 2026-07-11); amended 2026-07-12 after live
test — default spawn flag is `--dangerously-skip-permissions`, not
`--permission-mode acceptEdits`: an unattended leg under acceptEdits parked
on the loop skill's own permission prompt at boot. `mode=accept` demoted to
opt-in for edit-only bodies in pre-allowlisted projects.

Amended 2026-07-15 — spawned legs now use Claude Code's native `--background`
mode and are managed through `claude agents`; `claude agents` itself is not the
spawn command because it accepts no initial Relay prompt.

## Problem

Long-running `/loop` sessions rot. Every firing lands in the same session, so
context grows monotonically; past the 5-minute prompt-cache TTL each wakeup
re-reads the whole conversation uncached. Cost climbs linearly with loop age
and quality degrades as the context fills with stale iterations. The built-in
scheduling primitives cannot escape this: `ScheduleWakeup` fires in-session,
and `CronCreate` jobs are session-only (in-memory, dead when the session
exits) — neither can outlive or spawn a session.

## Solution

`/relay` — a wrapper skill around the built-in `/loop`. It runs the loop in
**legs** of N iterations. At the end of a leg the session writes a handoff to
a state file, spawns a fresh Claude background session whose
injected first prompt is the same `/relay` command, and stops its own loop.
The new leg resumes from the handoff with a near-empty context. The chain
continues until the work signals done, a stop flag is set, or a leg cap is
hit.

Same ritual as the `.context/` handoff family, applied to loop firings and
automated at a threshold.

### Layering

```
/relay          ← this skill: state file + iteration counting + handoff + spawn
   └─ /loop     ← built-in: scheduling machinery (ScheduleWakeup / cron)
        └─ body ← /preset ticket-loop etc. — does the work
```

`/relay` adds nothing to scheduling. It wraps each firing with bookkeeping and
takes over at the leg boundary. Plain `/loop` is untouched; relay is explicit
opt-in per loop.

## Invocation

```
/relay [interval] [N=10] <body>
```

- `interval` optional — omitted means self-paced (dynamic ScheduleWakeup),
  same as bare `/loop`.
- `N` — iterations per leg, default 10.
- `<body>` — any loop body, typically a `/preset` loop preset. Existing
  loop-body contract (state-check first / one unit per firing / breadcrumbs /
  explicit stop signal) is preserved unchanged.
- `/relay stop [slug]` — kill switch subcommand (see Kill switches). Slug
  optional when the project has exactly one relay state file; with several,
  the skill asks which.

Example: `/relay 10m N=8 /preset ticket-loop`

## State file — the handoff carrier

`.claude/relay/<slug>.md` in the project root. Project-local because the
scratchpad is session-specific (a new leg gets a different one) and the
spawned session inherits the cwd. `<slug>` derives from the body (e.g.
`ticket-loop`).

```yaml
---
body: /preset ticket-loop
interval: 10m
n: 8            # iterations per leg
leg: 3          # current leg number
iter: 2         # iterations done this leg
max_legs: 20
stop: false
spawn_flags: --dangerously-skip-permissions
---
## Handoff
(rewritten at each relay: done / in-flight / next unit / gotchas)

## Breadcrumbs
(one line per iteration; pruned to the current leg at relay time)
```

Created at first invocation (`leg: 1, iter: 0`). On boot, `/relay` checks for
an existing state file for the slug: present with `stop: false` → **resume
mode** (read Handoff, continue — this also revives a chain that died
mid-leg); absent or `stop: true` → **init mode** (fresh file, leg 1).

## Per-firing contract (wrapped around the body)

1. **Start:** read the state file.
   - `stop: true` → end loop, no spawn.
   - file `leg` ≠ own leg → end loop silently. (Leg-fencing: an orphan leg —
     spawn succeeded but the old loop somehow kept firing — dies on its next
     firing.)
2. **Middle:** one unit of the body, unchanged.
3. **End:** increment `iter`, append a breadcrumb line.
   - `iter == n` → relay sequence.

## Relay sequence (end of a leg)

1. Rewrite `## Handoff` (done / in-flight / next unit / gotchas). Prune
   Breadcrumbs to the finished leg. Set `iter: 0`, increment `leg`.
2. Spawn a native background agent in the same cwd:
   ```powershell
   Start-Process claude -ArgumentList @('--background','--dangerously-skip-permissions','"/relay 10m N=8 /preset ticket-loop"')
   ```
   (flags come from `spawn_flags`).
3. On successful spawn print exactly:
   ```text
   [relay: leg <k> scheduled loop is running in claude agents]
   ```
   and `PushNotification`: "relay: leg <k> spawned for <slug>".
   If spawn fails, set `stop: true`, notify, stop without retry, and do not
   print the success line.
4. Stop own loop (ScheduleWakeup stop / CronDelete). The old foreground
   session only stops its loop and may be closed; the newly spawned background
   session appears in `claude agents`.

## Kill switches

Auto-spawn demands these:

- **`/relay stop`** — sets `stop: true` in the state file. Works from any
  session or any editor; it is just a file edit. Every leg checks it at every
  firing and at boot.
- **`max_legs`** (default 20) — `leg >= max_legs` → stop + PushNotification
  "relay chain hit cap".
- **Leg-fencing** — duplicate/orphan legs self-terminate on leg mismatch.

## Permissions — the sharp edge

The original 2026-07-11 design chose default `spawn_flags: --permission-mode
acceptEdits` because spawned sessions run unattended. A 2026-07-12 live test
showed that acceptEdits parked on the loop skill's own permission prompt at
boot. The current default is `spawn_flags: --dangerously-skip-permissions`;
`mode=accept` remains opt-in for edit-only bodies in pre-allowlisted projects.
The skill doc warns loudly about the bypass default, and the user can review
each background leg through `claude agents`.

## Accepted failure modes (v1)

- **Crash mid-leg** → chain dies silently. No watchdog hook, by design —
  preserves the no-background-LLM philosophy. The per-relay PushNotification
  is the observability.
- **Spawn failure** (claude not on PATH, etc.) → notify + stop; no retry.

## Not building

- Watchdog / SessionEnd hooks (rejected trigger option; hook complexity,
  runaway-chain risk).
- Cross-project relay registry.
- Headless `claude -p` legs — a one-turn process cannot hold ScheduleWakeup
  firings.
- Cloud cron routines — already rejected in the vault ("user drives loops
  explicitly").

## Decision note

The vault's 2026-07-10 preset decision rejected cron routines because "user
drives loops explicitly." `/relay` consciously revisits *part* of that:
spawning is automated, but the user still explicitly starts every chain,
picks N and the permission mode, and holds three kill switches. Record as an
amendment on the preset/vault pages, not a reversal.

## Ecosystem bookkeeping

- New skill folder: `~/.claude/skills/relay/SKILL.md`.
- Vault: new `wiki/skills/relay.md` page; amendment note on the preset page
  and the loop decision.

## Success criteria

- A `/relay`-started loop crosses a leg boundary unattended: handoff written,
  new background session appears in claude agents, new leg resumes the work
  correctly from the Handoff section alone.
- `/relay stop` halts the chain within one firing.
- Orphan legs die on their next firing (leg-fencing verified).
- Plain `/loop` behavior unchanged.
