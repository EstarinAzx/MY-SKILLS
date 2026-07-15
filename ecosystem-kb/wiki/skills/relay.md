---
type: skill
updated: 2026-07-16
tags: [skill, loops, handoff]
source: built 2026-07-12; spec skills/docs/superpowers/specs/2026-07-11-relay-design.md
---

# relay

Self-relaying loops — `/relay [interval] [N=10] [mode=bypass|accept] <body>`
wraps the built-in `/loop` so a long loop runs in **legs** of N iterations.
At each leg boundary the session rewrites the Handoff section of
`.claude/relay/<slug>.md` (project-local; scratchpad is session-specific),
spawns a fresh background session via `Start-Process claude` with
`--background` and the same `/relay` command injected as its first prompt, then
stops its own loop. The leg is visible and manageable through `claude agents`;
that command opens the manager and is not itself used to spawn the prompted
leg. Fresh leg = startup hooks + skill + handoff only — context rot and
uncached full-history re-reads (5-min cache TTL) reset every leg.

Layering: relay owns state file + counting + handoff + spawn; `/loop` owns
scheduling; the body (usually a [[preset]] loop body) owns the work and its
loop-body contract, unchanged.

Kill switches, mandatory because spawn is automated: `/relay stop [slug]`
(any session or editor — it is a file edit), `max_legs: 20` cap +
PushNotification, and leg-fencing (a firing whose session leg ≠ file leg
dies silently — orphans self-terminate). Body-signaled done also sets
`stop: true`, so a finished chain never respawns; re-running the same
command revives a mid-leg crash (resume matches on the `body:` field, not
re-derived slug). After a successful spawn, the old leg ends with
`[relay: leg <k> scheduled loop is running in claude agents]`; spawn failures
set `stop: true`, notify, and never print that success line.

Sharp edge: spawned legs run unattended — default spawn flag is
`--dangerously-skip-permissions`, flipped from the spec's `acceptEdits`
after the 2026-07-12 live test: leg 2 parked on the loop skill's own "Use
skill?" prompt, so anything short of bypass stalls every leg at boot.
Consequence: only relay bodies trusted to run bypass; `mode=accept`
remains for edit-only bodies in pre-allowlisted projects. Crash mid-leg
dies silently by design: no watchdog
hook (standing no-hooks/no-background-LLM rule); the per-relay
PushNotification is the observability.

Decision note: partial, conscious revisit of the 2026-07-10 "user drives
loops explicitly" rejection of cron routines — spawning is automated, but
the user still starts every chain, picks N and the permission mode, and
holds three kill switches.

Binary resolution (2026-07-16) — legs must respawn with the **same** launcher
that started the chain, or a claude-wisp / local-gateway wrapper silently
drops to the real `claude` and bypasses the router. A new `binary:` state
field is resolved once (first-match wins: stored `binary:` → `$env:CLAUDE_BINARY`
→ "wisp"-in-command-line/env autodetect → default `claude`) and persisted, so
resumes and every future leg reuse it; edit the field to force a different
launcher. Wrapper binaries (`wisp` / `.cmd` / `.ps1`) spawn through
`cmd.exe /c` — direct `Start-Process claude-wisp --background` is flaky and
often registers no visible leg. Recommended setup: `$env:CLAUDE_BINARY =
"claude-wisp"` in the PowerShell profile. Doc-only change to the skill (no new
kill switch, cap, or fencing).
