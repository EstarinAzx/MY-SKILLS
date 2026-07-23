---
name: relay
description: Self-relaying loops — wraps the built-in /loop so long loops run in legs of N iterations, hand off through a state file, and respawn a fresh session (dodges context rot and uncached re-read cost). Use when the user types /relay (e.g. /relay 10m N=8 /preset ticket-loop), /relay stop, or asks for a long-running loop that will not rot its context.
---

# /relay — self-relaying loops

Wrapper around the built-in `/loop`. The loop runs in **legs** of N
iterations. At a leg boundary the session writes a handoff into the state
file, spawns a fresh Claude background session whose injected first prompt is
this same `/relay` command, and stops its own loop. The next leg appears in
`claude agents`; its context is just startup hooks + this skill + the handoff.

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

**claude-wisp / gateway wrapper support:** Relay now properly tracks and re-uses the exact binary (plain `claude` vs your wrapper `claude-wisp`). See "Binary resolution" below. Recommended: set `CLAUDE_BINARY=claude-wisp` in your environment.

**claude-wisp / local gateway support:** Relay now honors `CLAUDE_BINARY` (or auto-detects). Set `CLAUDE_BINARY=claude-wisp` in your environment when using the wrapper so legs keep spawning the same binary. The chosen binary is persisted in the state file.

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
binary: claude-wisp          # persisted — keeps using your local gateway wrapper
---

## Handoff

(rewritten at each relay: Done / In flight / Next / Gotchas)

## Breadcrumbs

- [leg 1 / iter 1] one line per firing
```

**Prose block is optional (external-state bodies).** The `## Handoff` +
`## Breadcrumbs` (+ any Gotchas) prose is the cold-reader memory for the next
leg — and the whole file is re-read into every fresh leg, so it is a recurring
per-leg context cost. When the body has its **own durable external state**
(`loop-arg` → `.claude/loop-arg.md`; `ticket-loop` → tracker tickets;
`ci-babysit` → PR checks + comments), that prose block is pure duplication and
collapses to a one-line pointer:

```markdown
## Handoff
state: .claude/loop-arg.md      # GOAL + NEXT + Log live here
```

When the body has **no** external store (an ad-hoc prose body like
`/relay "refactor auth until tests pass"`), the full Done / In-flight / Next /
Gotchas block is **required** — it is the chain's only cross-leg memory. The
frontmatter counters never move either way — they are machinery, not memory.

## Binary resolution (claude-wisp and local gateway wrappers)

When using a wrapper such as `claude-wisp` (your local gateway / model router), relay must consistently spawn legs with the **same binary** that started the chain. Otherwise later legs silently fall back to the real `claude` and bypass your gateway.

Resolution order (first match wins):

1. `binary:` value already stored in the relay state file (`.claude/relay/<slug>.md`).
2. `$env:CLAUDE_BINARY` environment variable.
3. Auto-detection: if the current process/command line contains "wisp", or certain wrapper-specific environment variables are present, use `claude-wisp`.
4. Default: `claude`.

The chosen binary is immediately written back into the state file under `binary:`. This guarantees that:
- resumes use the same binary,
- the next leg (when `iter == n`) is spawned with the same binary,
- you can force a different launcher by editing the state file directly.

**Recommended setup (claude-wisp users)**

> wisp-router ≥ 2.0.8: the `claude-wisp` launcher sets `CLAUDE_BINARY=claude-wisp` on the
> spawned session itself, so this profile export is only needed on older versions.

```powershell
# Put this in your PowerShell profile or session startup
$env:CLAUDE_BINARY = "claude-wisp"
```

After that, normal `/relay` usage will automatically use `claude-wisp` for the entire chain.

You can also override per-relay by editing the state file:

```yaml
binary: claude-wisp     # or "claude", or any other name on PATH
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
3. **Rehydrate project context.** `.context/` exists at the target project
   root → read `.context/overview.md` + `active-work.md` once, at boot —
   never per firing. A fresh leg's context is only startup hooks + this
   skill + the state file; this step gives it the same backdrop
   `/preset pick-up` gets from the wrap-up note. No `.context/` → skip
   silently.
4. **Determine binary for this leg and future legs** (critical for claude-wisp users):
   - If the state file already has a `binary:` field, use it.
   - Else if `$env:CLAUDE_BINARY` is set, use that value.
   - Else try to detect: if the current process / command line contains "wisp" (or certain wisp-specific env vars are present), use `claude-wisp`.
   - Otherwise default to `claude`.
   - Persist the chosen binary into the state file as `binary: <name>` so every future leg (including after resume) uses exactly the same launcher. This is how relay works reliably with your local gateway wrapper.
5. Remember this session's own leg number (the file's `leg` at boot).
6. Start the loop: follow the built-in `/loop` skill with the given
   interval and the per-firing contract below wrapped around the body.

## Per-firing contract

1. **Fence.** Read the state file. If `stop: true`, or the file's `leg` ≠
   this session's boot leg → end the loop (dynamic mode: ScheduleWakeup
   stop; cron mode: CronDelete). No spawn. Stopped and orphaned legs die
   here.
2. **Work.** One unit of the body, exactly as the body prescribes.
3. **Book-keep.** Increment `iter`. Append a one-line summary where the next
   leg will read it: `- [leg <k> / iter <i>] <summary>` to `## Breadcrumbs`
   **for an ad-hoc prose body**; **for an external-state body the body already
   logs its own progress** (`loop-arg` step 4 appends to `## Log`), so relay
   keeps no second trail.
4. **Body signaled done** (queue dry / checks green / human needed) → set
   `stop: true`, rewrite Handoff with the closing state, stop the loop. No
   spawn.
5. **`iter == n`** → relay sequence.

## Relay sequence

1. **External-state body** → the `## Handoff` is just the `state:` pointer;
   there is nothing to rewrite (the body's own store carries Done/Next).
   **Ad-hoc prose body** → rewrite `## Handoff` (Done / In flight / Next /
   Gotchas) for a cold reader — the next leg sees only this — and prune
   `## Breadcrumbs` to the leg just finished. Either way: set `iter: 0`,
   increment `leg`.
2. New `leg` > `max_legs` → set `stop: true`, PushNotification
   "relay: <slug> hit max_legs", stop the loop. No spawn.
3. Spawn the next leg using the **same binary** that was used for this leg (stored in state file under `binary:`).

   For script-based wrappers (claude-wisp.cmd, .ps1, etc.), we go through `cmd.exe /c` because direct `Start-Process` on the wrapper frequently fails to properly launch a background agent.

   Always give the spawned leg a **memorable display name** via `-n/--name`, so
   it is recognisable in `claude agents` / the session picker instead of an
   opaque auto-title. Convention: `relay·<slug>·leg<k>` where `k` is the leg
   number being spawned (`$state.leg`, already incremented in step 1). Append
   the target ticket when the body carries one and it is known.

   ```powershell
   $binary = if ($state.binary) { $state.binary } else { "claude" }

   # Memorable name for `claude agents`: prefix + slug + the leg being spawned.
   $slug = if ($state.slug) { $state.slug }
           elseif ($statePath) { (Split-Path -Leaf $statePath) -replace '\.md$','' }
           else { 'relay' }
   $legName = "relay·$slug·leg$($state.leg)"

   # Rebuild the full /relay command string from the state
   $relayCmd = "/relay"
   if ($state.interval) { $relayCmd += " $($state.interval)" }
   $relayCmd += " N=$($state.n)"
   if ($state.spawn_flags) { $relayCmd += " $($state.spawn_flags)" }
   $relayCmd += " $($state.body)"

   if ($binary -match 'wisp|wrapper|\.cmd$|\.ps1$') {
       # Use cmd.exe wrapper for npm-style / script launchers.
       # This is significantly more reliable for --background.
       Start-Process cmd -ArgumentList @(
           '/c',
           $binary,
           '--background',
           '--dangerously-skip-permissions',
           '--name', $legName,
           "`"$relayCmd`""
       ) -WindowStyle Hidden
   } else {
       Start-Process $binary -ArgumentList @(
           '--background',
           '--dangerously-skip-permissions',
           '--name', $legName,
           "`"$relayCmd`""
       ) -WindowStyle Hidden
   }
   ```

   This is the reliable spawn path for `claude-wisp` (your local gateway wrapper). Direct `Start-Process claude-wisp` often does not register a visible background leg. The `--name` makes each leg self-identify in the agents list (e.g. `relay·relay-leg·leg2`).

4. If spawning fails (`claude` missing from PATH, invalid arguments, or process
   launch error), PushNotification `"relay: <slug> background spawn failed"`,
   set `stop: true`, stop the loop, and do not retry. Do not print the success
   line below.
5. After a successful spawn, PushNotification
   `"relay: leg <k> spawned for <slug>"` (load the tool via ToolSearch if
   deferred), stop own loop, and end the user-facing response with exactly:

   ```text
   [relay: leg <k> scheduled loop is running in claude agents]
   ```

## The relay-leg pattern (recommended composition)

The most efficient way this skill has been run: `/relay N=1 read and follow
.claude/relay-leg.md` draining a whole spec's tracer-bullet tickets, unattended.
It is a **composition** of pieces above, each taken to its limit — copy it when a
batch of tracker tickets needs to be worked one at a time without a human:

- **N=1 — one ticket per leg.** Each leg does exactly one tracer-bullet ticket
  end-to-end (branch → work → gate → squash-merge → close), then relays. Every
  leg is cache-fresh for a single unit; no rot accumulates mid-batch.
- **The body is a file the leg reads,** not inline text: `read and follow
  .claude/relay-leg.md`. The loop-body contract (pick / idempotency guard / work
  / gate / wrap-up / stop) lives in that versioned project file, so the `/relay`
  command and the handoff stay tiny and the body evolves in-repo. This is the
  files-not-sessions principle applied to the *body* itself.
- **External-state body → pointer handoff.** Progress lives in the tracker
  (issues + native dependencies) and `.context/`, so `## Handoff` is the bare
  `state:` pointer (the prose-block rule above at its limit).
- **Optional — delegate the grunt via the slot skill (`wisp-slot:slot`), the
  relay×slot composition.** *A per-body user choice, not a relay or relay-leg
  default; most bodies just do the work inline.* When a body opts in, a leg
  becomes a slot *driver*: the leg's own model owns architecture, decomposition,
  review, and the gate, while the mechanical implementation is delegated to a cheaper
  Wisp Target (e.g. `xai/grok-4.5`) by temporarily rebinding the `haiku` Slot.
  Follow the **slot skill's live mechanic — `wisp snapshot <family>` /
  `wisp snapshot revert <family>`** (wisp-router ≥ 2.0.24). The **Iron Rule**
  holds inside a leg: restore the Slot only after *every* grunt agent of that
  leg has finished, and before the gate, so a later crash never strands the
  route. A serial (N=1) chain can also recover a Slot a dead prior leg left
  bound by reverting its held snapshot at boot.
  > **Gotcha:** the retired `~/.claude/slot/lease-<family>.json` files are
  > **gone** — the snapshot store is the recovery record. A body file that still
  > names lease files is stale; follow the live slot skill, not the body.
- **Gateless unattended wrap-up.** The wrap-up eyeball gate is auto-go;
  `/context-update` runs each leg; `.context/` commits ride main only.
- **Spec-batch drainer + self-close.** The body's frontier query picks the
  oldest open, unblocked `ready-for-agent` ticket; body-signaled done
  (per-firing contract step 4) fires when the queue empties, and the final leg
  closes the delivered spec. No leg is spawned past an empty queue.

Proven live: claude-wrapper spec #9, legs 1–5 landing tickets #10–#14, every leg
gate-green, one reviewed grunt per leg, zero human touches.

## Kill switches

- `/relay stop [slug]` — or hand-edit `stop: true` into the state file
  from any session or editor; every leg checks it every firing and at boot.
- `max_legs` (default 20) — relay sequence step 2.
- Leg-fencing — per-firing contract step 1; duplicate/orphan legs
  self-terminate.

## Sharp edges

- **Permissions.** The spawned session runs unattended with
  `--dangerously-skip-permissions` by default — anything less parks the
  background leg on its first permission prompt until a human opens
  `claude agents`
  (live test 2026-07-12: `acceptEdits` stalled on the loop skill's own
  "Use skill?" prompt). Relay chains therefore carry full-permission risk
  by construction: only relay bodies you would trust to run bypass, and
  `mode=accept` exists for edit-only bodies in pre-allowlisted projects.
- **Crash mid-leg** → the chain dies silently. No watchdog, by design (no
  hooks / no background LLM). The per-relay PushNotification is the
  observability. Re-running the same /relay command revives the chain.
- **Spawn failure** (claude not on PATH, etc.) → PushNotification, set
  `stop: true`, no retry.

- **claude-wisp / wrapper binaries + `--background`**
  Direct `Start-Process claude-wisp` (or `claude-wisp.cmd`) is flaky for background agents.
  The skill now forces wrappers through `cmd.exe /c`:
  ```powershell
  Start-Process cmd -ArgumentList @('/c', $binary, '--background', '--dangerously-skip-permissions', "`"$relayCmd`"") -WindowStyle Hidden
  ```
  This is the only reliable way we've seen so far to get a proper background leg when using a local gateway wrapper.
  If a leg still doesn't appear in `claude agents`, check that the wrapper actually launched something (look for recent `claude.exe` processes with the relay command).
