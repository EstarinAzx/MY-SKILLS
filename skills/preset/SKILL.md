---
name: preset
description: Personal prompt-preset library. Loads a named, reusable instruction block on demand instead of retyping it. Use when the user types /preset <name> (e.g. /preset wrap-up), or /preset alone to list available presets.
---

# /preset

Dispatcher for the user's personal prompt-preset library. Each preset is a reusable instruction block stored as its own file under `presets/`.

## Usage

`/preset <name> [args]` — load the preset and follow it; `[args]` pass through to the preset.
`/preset`               — list available presets.

## Available presets

The session-handoff loop, in order: a session goes in one door, through the gates, out the other.

| Preset | Slot | Purpose |
|---|---|---|
| `init`     | door zero (idea) | Raw idea → `grill-me` interview → `/hp` MVD → `to-spec` → `to-tickets`; one up-front choice of destination (GitHub issues or local md) that also seeds a conditional `/setup-matt-pocock-skills` offer when `docs/agents/` is missing, then hand off to `scope`. |
| `pick-up`  | start (baton) | Read the `.context/pick-up.md` note left by `wrap-up` and resume the exact next task. |
| `catch-up` | start (no baton) | No note → orient from live git/PR/`.context/` state and ask what to work on. |
| `scope`    | entry gate | Restate the task, plan files-to-touch + risks, go/no-go before any code. |
| `review`   | pre-commit | Fresh-eyes review of the working diff (subagent first), findings only, no auto-fix. |
| `wrap-up`  | exit gate | Eyeball go/no-go → `context-update` → write the `pick-up.md` handoff note → commit. |
| `ship`     | post-commit | Push the branch and open a PR composed from the diff. |
| `learn`    | off-loop (anytime) | Trace a flow via `trace`, mini-grill any vocabulary mismatches (grill-with-docs machinery) → resolved terms land in `CONTEXT.md`. |
| `prompt-writer` | off-loop (anytime) | Turn a rough ask into a paste-ready agent/subagent prompt — verify the claims against reality, scope each target, set boundaries, cut ceremony; output the block + a short "what changed". |
| `health`   | off-loop (maintenance) | Run every deterministic checker (ecosystem audit, template drift, vault lint) and report one punch list; offers fixes, applies only template mirroring on confirmation. |
| `mp-update` | off-loop (maintenance) | Pull a new mattpocock/skills release: refresh the curated list, never install the excluded five, reapply the two local patches, verify, sync vault + template. |
| `ticket-loop` | loop body | One `ready-for-agent` tracker ticket per firing: pick → branch → `/implement` → gate → breadcrumb comment; queue empty → stop the loop. |
| `ci-babysit` | loop body | Watch a PR's checks: green → stop, pending → cheap one-liner, red → smallest honest fix or escalate to human; never fix-push twice for one failure. |

Steady-state cycle is `pick-up` → work → `wrap-up`; `scope`/`review`/`ship` are opt-in bookends, `catch-up` the fallback door when no note exists, and `init` runs once before the loop ever starts — when all that exists is an idea. `learn` and `prompt-writer` sit off-loop entirely — invoke anytime to map a flow (`learn`) or to forge a clean prompt for the next agent (`prompt-writer`). `health` and `mp-update` are the off-loop maintenance pair: whole-ecosystem checkup, and the curated mattpocock release-update procedure.

## Loop bodies

`ticket-loop` and `ci-babysit` are written for the built-in `/loop` runner: `/loop /preset ticket-loop` (self-paced) or `/loop 30m /preset ci-babysit 42`. They also run fine as one-shots. Every loop body honors the same contract: **check state first** (each firing idempotent — never redo finished work), **one unit of work per firing** (the runner re-fires; the preset never chains), **breadcrumbs** where the next firing will look (ticket comment, PR comment), and an **explicit stop signal** when the queue is dry, the checks are green, or a human is needed. `health` is loopable as-is (`/loop 1d /preset health`) — it's naturally idempotent. Long chains: wrap with `/relay` (`/relay 30m N=8 /preset ticket-loop`) — same body, but the loop relays to a fresh session every N firings via a handoff file, so context never rots.

## Process

1. Split the text after `/preset` into the **first token** (the preset name) and **the rest** (optional arguments passed through to the preset).
2. **No preset name** → list every `presets/*.md` file by name with its one-line purpose (the file's first heading line), then stop.
3. **Preset name given** → load `presets/<name>.md`.
   - Match found → follow that file's instructions for the current task, treating any passed-through arguments as the preset's input. The block is injected as an active instruction; treat it as if the user typed it.
   - No match → say so and list the available presets.

Presets are **one-shot**: they apply to the current/next task only, not the rest of the session.
