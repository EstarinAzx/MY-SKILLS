---
type: synthesis
updated: 2026-07-17
tags: [synthesis, loops]
---

# loop-engineering

How this ecosystem runs recurring, unattended work — a subsystem of
[[harness-engineering]] (the session-lifecycle + contract corner of the
harness). Four layers, each owning one concern; every layer is swappable
without touching the others.

| Layer | Owns | Piece |
|---|---|---|
| Runner | scheduling — when to fire | built-in `/loop` (ScheduleWakeup / CronCreate) |
| Lifecycle | session mortality — legs, handoff, respawn | [[relay]] |
| Body | the work — what one firing does | [[preset]] loop bodies: `ticket-loop`, `ci-babysit` |
| Contract | what makes a body loop-safe | state-check first / one unit per firing / breadcrumbs / explicit stop signal |

## The core principle

**Everything durable lives in files; nothing lives in the session.** Tracker
tickets carry ticket-loop's progress, PR comments carry ci-babysit's,
`.claude/relay/<slug>.md` carries chain state, `.context/` carries project
handoff ([[context-handoff]]). Sessions are disposable workers: any layer can
die — crash, close, cap — and the system resumes from files. The two stores
meet at leg boot (2026-07-17): a fresh relay leg rehydrates from
`.context/overview.md` + `active-work.md` once if the dir exists — the same
backdrop `pick-up` gets via the wrap-up note's `Start:` pointer, which
`loop-arg`'s state file now carries too. Stop is pull,
not push: a leg re-reads its state file every firing and kills itself on
`stop: true`; nobody has to signal a running session.

## Why relay exists

The runner's primitives are session-bound: ScheduleWakeup fires in-session,
CronCreate jobs are in-memory and die with the session. A long loop therefore
rots its own context and — past the 5-minute prompt-cache TTL — re-reads its
whole history uncached every firing. [[relay]] escapes by making sessions
mortal on purpose: legs of N iterations, handoff file, `Start-Process` a
fresh session, die. Same ritual as [[context-handoff]], automated at a
threshold.

## Composability

A body written to the contract runs three ways with zero changes:
`/preset x` (one-shot), `/loop 30m /preset x` (recurring),
`/relay 30m N=8 /preset x` (recurring + immortal). Sophisticating a loop
workflow means writing a better body — a new preset — not touching runner or
lifecycle. Capability vs recipe boundary: presets orchestrate; new
capability (a tool, an analysis) is a skill the preset calls (ticket-loop
calls `/implement`).

## Decision history

- 2026-07-10 — loop bodies built; rejected a loop-framework skill (`/loop`
  is the framework) and cloud cron routines ("user drives loops
  explicitly"). See [[preset]].
- 2026-07-11/12 — [[relay]] built (spec + live test). Conscious partial
  revisit of the cron-routine rejection: spawn is automated, user keeps
  start, N, permission mode, and three kill switches (`/relay stop`,
  `max_legs`, leg-fencing).
- 2026-07-12 — live test flipped the spawn default to
  `--dangerously-skip-permissions`: an unattended leg under `acceptEdits`
  parks on its first permission prompt. Consequence: relay only bodies you
  trust to run bypass.

## Standing rules

- No hooks, no background LLM anywhere in the loop stack — observability is
  PushNotification, persistence is files ([[knowledge-base-lineup]] rule,
  upheld in both loop decisions).
- One unit of work per firing; the runner re-fires, bodies never chain.
- A loop without a reachable stop signal is a bug: queue-dry / checks-green /
  human-needed for bodies, `stop: true` + `max_legs` for chains.
