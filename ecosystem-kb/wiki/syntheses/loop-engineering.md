---
type: synthesis
updated: 2026-07-23
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

## The relay-leg pattern (2026-07-23)

The most refined use of the stack observed so far:
`/relay N=1 read and follow .claude/relay-leg.md` draining a whole spec's
tracer-bullet tickets, fully unattended. The moves compound into one efficient
loop, each an existing rule taken to its limit (the grunt-delegation move is
**optional** — a per-body user choice, not a relay default):

- **N=1 — one ticket per leg.** A leg does exactly one tracer-bullet ticket
  end-to-end (branch → work → gate → squash-merge → close), then hands off.
  Cache-fresh context per unit; no rot accumulates across tickets.
- **The body is a file the leg reads,** not inline text. `… read and follow
  .claude/relay-leg.md` — the loop-body contract lives in a versioned project
  file (files-not-sessions applied to the *body* itself). Edit the file and
  every future leg picks it up; the `/relay` command and the handoff stay tiny.
- **External-state body → pointer handoff.** Tracker (GitHub issues + native
  dependencies) and `.context/` carry all progress, so the relay Handoff
  collapses to a one-line `state:` pointer — the prose-block-optional rule at
  its limit.
- **Optional — delegate the grunt via [[slot]]** (a per-body user choice, not a
  relay default; most bodies work inline). When a body opts in, the leg's own
  model owns architecture, decomposition, review, and the gate; the mechanical
  implementation is delegated to a cheap Wisp Target (grok-4.5) by temporarily
  rebinding the `haiku` Slot. The Iron Rule holds — restore only after every
  grunt agent finishes, before the gate. This is the **relay×slot composition**:
  a relay leg *can be* a slot *driver*, which neither skill page noted before.
- **Gateless unattended wrap-up.** The wrap-up eyeball gate is auto-go;
  `/context-update` runs each leg; `.context/` commits ride main only.
- **Spec-batch drainer + self-close.** The frontier query picks the oldest open,
  unblocked `ready-for-agent` ticket; body-signaled done (`stop: true`) fires
  when the queue empties, and the final leg closes the delivered spec.

Live run: claude-wrapper spec #9, legs 1–5 landing #10 → #14, every leg
gate-green (typecheck · tests · build), one reviewed grunt per leg, zero human
touches. **Gotcha:** a body that drives slot must use the current CLI mechanic
(`wisp snapshot` / `wisp snapshot revert`, [[slot]] v1.3.0) — **not** the retired
`lease-<family>.json` files. A stale body file still naming leases misleads a
cold leg (the live slot skill is snapshot-based; follow the skill, not the body).

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
- 2026-07-23 — the **relay-leg pattern** proven live (claude-wrapper spec #9,
  legs 1–5 → #10–#14): N=1 one-ticket-per-leg + file-body + pointer handoff +
  gateless wrap-up + spec-batch self-close, with an **optional** slot-delegated
  grunt (user-chosen this run: Fable led, Grok grunted). Captures the
  **relay×slot composition** — a leg *can* drive [[slot]].

## Standing rules

- No hooks, no background LLM anywhere in the loop stack — observability is
  PushNotification, persistence is files ([[knowledge-base-lineup]] rule,
  upheld in both loop decisions).
- One unit of work per firing; the runner re-fires, bodies never chain.
- A loop without a reachable stop signal is a bug: queue-dry / checks-green /
  human-needed for bodies, `stop: true` + `max_legs` for chains.
