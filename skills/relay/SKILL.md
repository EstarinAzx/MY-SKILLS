---
name: relay
description: Self-relaying loops — wraps the built-in /loop so long loops run in legs of N iterations, hand off through a state file, and respawn a fresh session (dodges context rot and uncached re-read cost). Use when the user types /relay (e.g. /relay 10m N=8 /preset ticket-loop), /relay stop, or asks for a long-running loop that will not rot its context.
---

# /relay — self-relaying loops

Wrapper around the built-in `/loop`. The loop runs in **legs** of N
iterations. At a leg boundary the session writes a handoff into the state
file, spawns a fresh Claude session whose injected first prompt is this same
`/relay` command, and stops its own loop. A fresh leg's context is just:
startup hooks + this skill + the handoff.

Relay adds no scheduling — `/loop` owns that:

```
/relay          ← state file + iteration counting + handoff + spawn
   └─ /loop     ← built-in scheduling (ScheduleWakeup / cron)
        └─ body ← /preset ticket-loop etc. — does the work
```

## Usage

```
/relay [interval] [N=10] [mode=bypass|accept] <body>
/relay stop [slug]
```

- `interval` — optional; omitted = self-paced dynamic mode, exactly like bare `/loop`.
- `N` — iterations per leg (default 10).
- `mode` — spawn permission flag: `bypass` (default) → `--dangerously-skip-permissions`; `accept` → `--permission-mode acceptEdits`. Bypass is the default because a spawned leg is unattended and `acceptEdits` parks on its first Skill/shell permission prompt (verified live 2026-07-12); use `accept` only when the body is edit-only and the project has the needed allowlist entries.
- `<body>` — any loop body. The loop-body contract (state-check first / one unit per firing / breadcrumbs / explicit stop signal) applies unchanged.

Example: `/relay 10m N=8 /preset ticket-loop`

## State file

`.claude/relay/<slug>.md` at the **target project's root** — never the
scratchpad (session-specific; the next leg gets a different one). Slug:
body kebab-cased (`/preset ticket-loop` → `ticket-loop`; an ad-hoc prose
body → a stable 2-3 word kebab summary).

```markdown
---
body: /preset ticket-loop
interval: 10m
n: 8
leg: 1
iter: 0
max_legs: 20
stop: false
spawn_flags: --dangerously-skip-permissions
---

## Handoff

(rewritten at each relay: Done / In flight / Next / Gotchas)

## Breadcrumbs

- [leg 1 / iter 1] one line per firing
```

## Boot — every /relay invocation

1. **`stop` subcommand** → look in `.claude/relay/`: exactly one state file
   (or slug given) → set `stop: true` in it, confirm to user. Several files
   and no slug → list them, ask which. Then done — no loop.
2. Otherwise scan `.claude/relay/*.md` for a file whose `body:` field
   exactly matches this invocation's body (match on `body:`, not a
   re-derived slug — slug derivation may drift between sessions).
   - Match found and `stop: false` → **resume**: read Handoff +
     Breadcrumbs, announce "resuming <slug>, leg <k>". This also revives a
     chain that died mid-leg.
   - No match, or the match has `stop: true` → **init**: write a fresh
     state file (`leg: 1, iter: 0`), frontmatter from the invocation args.
3. Remember this session's own leg number (the file's `leg` at boot).
4. Start the loop: follow the built-in `/loop` skill with the given
   interval and the per-firing contract below wrapped around the body.

## Per-firing contract

1. **Fence.** Read the state file. If `stop: true`, or the file's `leg` ≠
   this session's boot leg → end the loop (dynamic mode: ScheduleWakeup
   stop; cron mode: CronDelete). No spawn. Stopped and orphaned legs die
   here.
2. **Work.** One unit of the body, exactly as the body prescribes.
3. **Book-keep.** Increment `iter`; append
   `- [leg <k> / iter <i>] <one-line summary>` to Breadcrumbs.
4. **Body signaled done** (queue dry / checks green / human needed) → set
   `stop: true`, rewrite Handoff with the closing state, stop the loop. No
   spawn.
5. **`iter == n`** → relay sequence.

## Relay sequence

1. Rewrite `## Handoff` — Done / In flight / Next / Gotchas, written for a
   cold reader: the next leg sees only this. Prune Breadcrumbs to the leg
   just finished. Set `iter: 0`, increment `leg`.
2. New `leg` > `max_legs` → set `stop: true`, PushNotification
   "relay: <slug> hit max_legs", stop the loop. No spawn.
3. Spawn the next leg (PowerShell tool, from the project root — the new
   session must inherit this cwd). Rebuild args from frontmatter
   (`spawn_flags` + `interval` + `n` + `body`); the quoted final element
   keeps the /relay command a single argument:

   ```powershell
   Start-Process claude -ArgumentList @('--dangerously-skip-permissions','"/relay 10m N=8 /preset ticket-loop"')
   ```

4. PushNotification: "relay: leg <k> spawned for <slug>" (load the tool
   via ToolSearch if deferred).
5. Stop own loop and tell the user this window is now an idle husk — safe
   to close.

## Kill switches

- `/relay stop [slug]` — or hand-edit `stop: true` into the state file
  from any session or editor; every leg checks it every firing and at boot.
- `max_legs` (default 20) — relay sequence step 2.
- Leg-fencing — per-firing contract step 1; duplicate/orphan legs
  self-terminate.

## Sharp edges

- **Permissions.** The spawned session runs unattended with
  `--dangerously-skip-permissions` by default — anything less parks the
  leg on its first permission prompt until a human looks at its window
  (live test 2026-07-12: `acceptEdits` stalled on the loop skill's own
  "Use skill?" prompt). Relay chains therefore carry full-permission risk
  by construction: only relay bodies you would trust to run bypass, and
  `mode=accept` exists for edit-only bodies in pre-allowlisted projects.
- **Crash mid-leg** → the chain dies silently. No watchdog, by design (no
  hooks / no background LLM). The per-relay PushNotification is the
  observability. Re-running the same /relay command revives the chain.
- **Spawn failure** (claude not on PATH, etc.) → PushNotification, set
  `stop: true`, no retry.
