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
| `pick-up`  | start (baton) | Read the `.context/pick-up.md` note left by `wrap-up` and resume the exact next task. |
| `catch-up` | start (no baton) | No note → orient from live git/PR/`.context/` state and ask what to work on. |
| `scope`    | entry gate | Restate the task, plan files-to-touch + risks, go/no-go before any code. |
| `review`   | pre-commit | Fresh-eyes review of the working diff (subagent first), findings only, no auto-fix. |
| `wrap-up`  | exit gate | Eyeball go/no-go → `context-update` → write the `pick-up.md` handoff note → commit. |
| `ship`     | post-commit | Push the branch and open a PR composed from the diff. |

Steady-state cycle is `pick-up` → work → `wrap-up`; `scope`/`review`/`ship` are opt-in bookends, `catch-up` the fallback door when no note exists.

## Process

1. Split the text after `/preset` into the **first token** (the preset name) and **the rest** (optional arguments passed through to the preset).
2. **No preset name** → list every `presets/*.md` file by name with its one-line purpose (the file's first heading line), then stop.
3. **Preset name given** → load `presets/<name>.md`.
   - Match found → follow that file's instructions for the current task, treating any passed-through arguments as the preset's input. The block is injected as an active instruction; treat it as if the user typed it.
   - No match → say so and list the available presets.

Presets are **one-shot**: they apply to the current/next task only, not the rest of the session.
