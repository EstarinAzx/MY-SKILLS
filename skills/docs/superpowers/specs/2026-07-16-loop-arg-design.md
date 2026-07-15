# loop-arg — self-prompting loop body

**Date:** 2026-07-16
**Status:** design, approved for planning
**Related:** [[relay]], [[preset]], loop-engineering synthesis

## Problem

Every existing loop body (`ticket-loop`, `ci-babysit`) runs the **same fixed
prompt** every firing — the work varies because external state (tracker queue,
PR checks) varies, but the instruction block is static. There is no loop body
that lets Claude **decide its own next step** and drive itself toward a goal
across firings.

The user wants an autonomous goal-seeking loop: seed a GOAL once, and each
firing does one concrete step toward it, then writes the *next* step for the
firing after it. The prompt becomes data — a living file — instead of a fixed
preset. This extends the ecosystem's core "everything durable lives in files"
principle to the prompt itself.

## What we're building

**One preset + one state file.** No separate `/prompt-loop` command — the
self-prompt write is the body's last step, not its own skill (fewest moving
parts).

- `preset/presets/loop-arg.md` — the loop body.
- `.claude/loop-arg.md` — the body's durable state (GOAL + NEXT + Log), at the
  **target project root**, created on first firing.

Invocation:

```
/preset loop-arg "<goal>"            # one-shot / seed
/loop /preset loop-arg "<goal>"      # recurring, self-paced
/relay N=8 /preset loop-arg "<goal>" # recurring + immortal (dodges context rot)
```

### Non-goals

- Not a new scheduling mechanism — `/loop` owns scheduling, unchanged.
- Not a new session-mortality mechanism — `/relay` owns legs/spawn, unchanged.
- No `/prompt-loop` skill — collapsed into the body's step 4.
- No human-steering / hybrid mode — Claude self-prompts; the human's controls
  are the GOAL at seed and relay's kill switches. (Editing `.claude/loop-arg.md`
  by hand between firings still works as a side effect, but it is not a
  designed feature.)

## Design decisions (from brainstorming)

1. **Claude self-prompts** — at the end of each firing Claude decides its own
   next step and overwrites the NEXT section. Autonomous, goal-driven.
2. **Goal-completion anchor** — `.claude/loop-arg.md` holds a fixed `goal:`
   (set once at seed) plus a rewritten `## Next`. Each firing checks "goal
   met?" first and stops the loop if so. The goal both steers the self-prompt
   and ends the loop — the guardrail against a self-writing prompt running
   forever or drifting.
3. **One preset + the file** — a single body seeds on first firing, then
   read → check → do → rewrite every firing after.

## State file — `.claude/loop-arg.md`

At the target project's root (never the scratchpad — session-specific). Slug is
fixed: `loop-arg`.

```markdown
---
goal: <fixed — set once at seed from the /preset arg, never rewritten>
stop: false
---

## Next
<the concrete next step Claude wrote for itself last firing>

## Log
- [firing 1] one line: what got done
- [firing 2] ...
```

- `goal:` — the anchor. Written once at seed; never touched again.
- `stop:` — set `true` when the goal is met (or Claude judges itself stuck).
  Mirrors relay's own stop convention.
- `## Next` — overwritten every firing. This is the self-prompt.
- `## Log` — append-only, one line per firing. **This is the body's memory —
  never optional.** Drop it and self-prompting goes blind (no record of what
  was already tried).

## Per-firing flow (the whole body)

1. **Seed guard.** `.claude/loop-arg.md` missing → this is firing 1: write
   `goal:` from the `/preset loop-arg "<goal>"` argument, set `## Next` to the
   first concrete step, initialize empty Log, done for this firing. File
   exists → **ignore the arg** (a relay respawn re-injects the original
   command, arg and all — the seed must be idempotent), read the file.
2. **Goal check.** Read `goal:` and Log. Goal met? → set `stop: true`, append
   a closing Log line, signal the loop to stop (dynamic mode: ScheduleWakeup
   stop; fixed interval: say "goal met" so the user cancels; under relay:
   set relay's `stop: true` too). Do **not** rewrite NEXT. End.
3. **Do NEXT.** Execute exactly what `## Next` says — one unit of work. Never
   chain a second step; the runner re-fires.
4. **Self-prompt.** Decide the next concrete step toward GOAL given what the
   Log now shows. **Overwrite `## Next`** with it. Append one Log line for the
   step just completed.

This is the inversion of `ticket-loop`: step 4 rewrites the body's own prompt.
GOAL is the fixed anchor; NEXT is the moving part.

## Loop-body contract compliance

The body honors the standing loop-body contract:

- **Check state first** — step 1 (seed guard) + step 2 (goal check) make every
  firing idempotent; a respawn never re-seeds or redoes finished work.
- **One unit per firing** — step 3, explicit "never chain a second."
- **Breadcrumbs where the next firing looks** — the `## Log` + `## Next`
  sections; the next firing reads exactly this file.
- **Explicit stop signal** — step 2 goal-completion, plus relay's `max_legs`
  and `/relay stop` as blunt backstops.

## Relay integration — the cross-leg prose block becomes optional

**Separate change, same spec** (touches `relay/SKILL.md` + the vault page, and
by extension the contract `ticket-loop` / `ci-babysit` already satisfy).

A relay chain writes `.claude/relay/<slug>.md` with two kinds of content — and
the whole file is read into every fresh leg at boot, so every prose line in it
is a recurring per-leg context cost:

- **Frontmatter counters** (`body/interval/n/leg/iter/max_legs/stop/spawn_flags/binary`)
  — relay's own machinery: `iter` fences firings, `iter==n` triggers the spawn,
  `stop`/`max_legs` are kill switches. **Unchanged, always present, cheap.**
- **The cross-leg prose block** — `## Handoff` (Done / In-flight / Next /
  Gotchas) **and** `## Breadcrumbs` (one line per firing, pruned to the current
  leg). This is the cold-reader memory for the next leg — and the bloat.

The **entire prose block** (Handoff + Breadcrumbs + Gotchas) is **redundant when
the body has its own external state store**, and **load-bearing when it
doesn't**. It is redundant as a unit, not part-by-part: Breadcrumbs duplicate
the body's own per-firing log, and Gotchas duplicate wherever the body already
parks warnings. Two log trails that can drift out of sync, both re-read into
every leg.

| Body | External state store | Prose block (Handoff+Breadcrumbs+Gotchas) |
|---|---|---|
| `loop-arg` | `.claude/loop-arg.md` (GOAL+NEXT+Log) | fully subsumed → pointer |
| `ticket-loop` | tracker tickets + labels | subsumed (queue is the state) → pointer |
| `ci-babysit` | PR checks + comments | subsumed → pointer |
| ad-hoc prose (`/relay "refactor auth until tests pass"`) | **none** | **the only memory** → keep in full |

### New rule

> If the relay body has its own durable external state, the whole
> `## Handoff` + `## Breadcrumbs` + Gotchas prose block collapses to a one-line
> `state:` pointer. If the body has none (ad-hoc prose body), the full block is
> **required** — it is the chain's only cross-leg memory.

Pointer form, for a `loop-arg` chain — the entire prose block is just:

```markdown
## Handoff
state: .claude/loop-arg.md      # GOAL + NEXT + Log live here
```

The per-firing "append to `## Breadcrumbs`" step (relay's per-firing contract
step 3) is, for an external-state body, satisfied by the body appending to its
own store — e.g. `loop-arg` step 4 appends to `## Log`. Relay does not keep a
second trail.

**Not a global deprecation.** Deleting the prose block everywhere would break
the ad-hoc-prose case, which has nowhere else to store cross-leg progress or
gotchas. The frontmatter counters never move — they are machinery, not memory.
`loop-arg`'s own `## Log` is unaffected by this rule: that is the *body's* state,
not relay's prose block, and it is mandatory.

## Files to create / change

1. **create** `preset/presets/loop-arg.md` — the loop body (per-firing flow
   above, written to the preset house style like `ticket-loop.md`).
2. **edit** `preset/SKILL.md` — add `loop-arg` to the loop-bodies table + the
   loop-bodies prose.
3. **edit** `relay/SKILL.md` — add the "whole prose block (Handoff +
   Breadcrumbs + Gotchas) collapses to a `state:` pointer when the body has
   external state" rule to the state-file + per-firing-contract + relay-sequence
   sections (per-firing step 3 "append to Breadcrumbs" becomes conditional).
4. **edit** vault `wiki/skills/relay.md` and `wiki/skills/preset.md` — record
   the prose-block-optional rule and the new loop body.
5. **edit** vault `index.md` + `~/.claude/CLAUDE.md` routing sheet — new loop
   body in the situation→invoke table (recurring autonomous goal-seeking).

## Sharp edges

- **Runaway self-prompt.** A body that writes its own next prompt can drift off
  goal or loop forever. Mitigations, in order: the goal-completion check (step
  2, primary), relay `max_legs` (blunt cap), `/relay stop` / hand-edit
  `stop: true`. A `loop-arg` chain should always run under `max_legs` — never
  bare `/loop` for an unattended long run.
- **Seed idempotency.** The seed arg is re-injected on every relay respawn. Step
  1 MUST ignore the arg when the file exists, or a respawn resets GOAL. This is
  the single most important correctness point.
- **Goal quality.** A vague GOAL makes step 2 unanswerable and the loop never
  self-terminates. The seed step should write a GOAL with a checkable
  done-condition; if the user's `<goal>` arg is vague, the seed firing should
  sharpen it into a testable statement before writing it.
- **Permissions.** Same as any relay body: an unattended `loop-arg` chain runs
  `--dangerously-skip-permissions` by default. Only relay a `loop-arg` goal you
  trust to run bypass.
