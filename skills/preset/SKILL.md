---
name: preset
description: Personal prompt-preset library. Loads a named, reusable instruction block on demand instead of retyping it. Use when the user types /preset <name> (e.g. /preset wrap-up), or /preset alone to list available presets.
---

# /preset

Dispatcher for the user's personal prompt-preset library. Each preset is a reusable instruction block stored as its own file under `presets/`.

## Usage

`/preset <name> [args]` — load the preset and follow it; `[args]` pass through to the preset.
`/preset`               — list available presets.

## Process

1. Split the text after `/preset` into the **first token** (the preset name) and **the rest** (optional arguments passed through to the preset).
2. **No preset name** → list every `presets/*.md` file by name with its one-line purpose (the file's first heading line), then stop.
3. **Preset name given** → load `presets/<name>.md`.
   - Match found → follow that file's instructions for the current task, treating any passed-through arguments as the preset's input. The block is injected as an active instruction; treat it as if the user typed it.
   - No match → say so and list the available presets.

Presets are **one-shot**: they apply to the current/next task only, not the rest of the session.
