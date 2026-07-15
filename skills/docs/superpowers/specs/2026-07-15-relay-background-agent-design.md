# Relay Background-Agent Spawn — Design

**Date:** 2026-07-15
**Status:** Approved in conversation

## Problem

Relay currently starts each new leg as an interactive Claude Code session:

```powershell
Start-Process claude -ArgumentList @('--dangerously-skip-permissions','"/relay 10m N=8 /preset ticket-loop"')
```

This opens a separate interactive session for every leg. Claude Code now supports
background sessions through `--background` (short form `--bg`) and exposes them
through the `claude agents` manager. Relay should use that native lifecycle so
long chains do not accumulate terminal windows.

`claude agents` itself is not the spawn command. It opens the background-agent
manager and accepts no initial Relay prompt. The spawned leg must therefore run
as `claude --background <relay prompt>`; `claude agents` is only the inspection
and management surface.

## Solution

Add `--background` to Relay's existing `Start-Process` argument list:

```powershell
Start-Process claude -ArgumentList @(
  '--background',
  '--dangerously-skip-permissions',
  '"/relay 10m N=8 /preset ticket-loop"'
)
```

The process starts a background Claude session, registers it in the native agent
view, and returns. The user can inspect or manage active legs with:

```powershell
claude agents
```

Relay still launches from the target project root so the background session
inherits the project working directory and finds the same
`.claude/relay/<slug>.md` state file.

## Scope

Modify only documentation and prompt instructions that define Relay's spawn
behavior:

- `skills/relay/SKILL.md`
- `skills/docs/superpowers/specs/2026-07-11-relay-design.md`
- `ecosystem-kb/wiki/skills/relay.md`
- `ecosystem-kb/wiki/syntheses/loop-engineering.md` if its foreground-session
  wording requires correction
- `ecosystem-kb/log.md`
- `ecosystem-kb/index.md` only if its Relay summary requires correction

No script, hook, wrapper, scheduler, state key, or new abstraction will be
added. Plain `/loop` remains untouched.

## Relay Sequence

At `iter == n`:

1. Rewrite `## Handoff` for a cold reader.
2. Reset `iter`, increment `leg`, and enforce `max_legs`.
3. From the project root, rebuild the Relay command from state frontmatter.
4. Start `claude` with `--background`, the existing permission flags, and the
   quoted Relay command as one prompt argument.
5. Send the existing spawn notification.
6. Stop the old leg's loop. After spawn succeeds, end the old leg's user-facing
   response with exactly:

   ```text
   [relay: leg <k> scheduled loop is running in claude agents]
   ```

   Do not print this success message when spawning fails. The old foreground
   session may be closed; no new interactive terminal is needed for the
   background leg.

The background leg follows the existing boot path: match state by exact `body:`,
read Handoff and Breadcrumbs, remember its boot leg, then resume `/loop`.

## Permissions and Safety

Permission behavior does not change:

- `mode=bypass` remains the default and maps to
  `--dangerously-skip-permissions`.
- `mode=accept` remains available for edit-only bodies in projects whose
  allowlist covers every required action.
- Only trusted bodies should run in bypass mode.

Existing kill switches remain mandatory:

- `stop: true`
- `max_legs: 20`
- leg fencing
- body-signaled completion

Background execution makes the current safety wording more important, not less:
the next leg is unattended and may no longer have a visible terminal window.

## Failure Behavior

Existing behavior remains:

- Spawn failure sets `stop: true`, sends a failure notification, and does not
  retry.
- Mid-leg crash has no watchdog; rerunning the same Relay command revives the
  chain from its state file.
- Duplicate or stale legs self-terminate through leg fencing.
- Body completion and `max_legs` prevent another spawn.

Native background-agent inspection adds one manual recovery surface:
`claude agents` shows active background sessions. Relay will document this as
an operator command, not call it automatically.

## Verification

Implementation verification will avoid starting a real Relay chain:

1. Confirm installed CLI exposes `--background` and `claude agents`.
2. Run one cheap background-session smoke test with a harmless prompt and a
   bounded permission mode.
3. Confirm the command returns immediately and the session appears in
   `claude agents --json` for the same working directory.
4. Confirm the Relay prompt remains one positional argument after PowerShell
   quoting.
5. Search Relay docs and vault pages for stale claims that every leg opens a new
   terminal window.
6. Run ecosystem audit and vault lint; report unrelated existing findings
   without expanding scope.

No full multi-leg acceptance test will run automatically because it would start
an unattended chain. A manual test can use a cheap body with `N=1`, inspect it
through `claude agents`, then set `stop: true`.

## Success Criteria

- Each Relay boundary dispatches the next leg as a Claude Code background
  session.
- The next leg receives the exact reconstructed `/relay` command as its first
  prompt.
- The background session starts in the target project and resumes from the
  existing state file.
- `claude agents` can list and manage the spawned leg.
- Existing handoff, fencing, stopping, cap, notification, and permission
  semantics remain unchanged.
- Relay no longer claims or requires that every next leg occupies a new
  interactive terminal window.
- After a successful spawn, the old leg's final user-facing line is
  `[relay: leg <k> scheduled loop is running in claude agents]`; failed spawns
  never print it.
