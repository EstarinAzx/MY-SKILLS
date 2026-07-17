# loop-arg — self-prompting loop body: pursue one GOAL, writing your own next step each firing

Loop body. Seed a GOAL once, then each firing does ONE concrete step toward it and rewrites the prompt for the firing after it. The prompt is data — a living file — not a fixed preset. Fire via `/preset loop-arg "<goal>"` (seed / one-shot), `/loop /preset loop-arg "<goal>"` (self-paced), or `/relay N=8 /preset loop-arg "<goal>"` (immortal; always run an unattended chain under `max_legs`, never bare `/loop`). This is the inversion of `ticket-loop`: the last step rewrites the body's own next prompt.

## State file — `.claude/loop-arg.md`

At the **target project root** (never the scratchpad — session-specific). Slug fixed: `loop-arg`.

```markdown
---
goal: <fixed — set once at seed from the /preset arg, never rewritten>
stop: false
---

Start: read .context/overview.md + active-work.md   <- only if .context/ exists at seed

## Next
<the concrete next step written for yourself last firing>

## Log
- [firing 1] one line: what got done
```

`goal:` is the anchor — written once, never touched again. `## Next` is overwritten every firing (the self-prompt). `## Log` is append-only, one line per firing — this is the body's memory; never drop it.

## Loop-body contract

Check state first (the seed guard + goal check make every firing idempotent — a respawn never re-seeds or redoes finished work), do one unit, leave the breadcrumb in `## Log` where the next firing reads it, and signal the loop the moment the goal is met.

## Steps

1. **Seed guard.** `.claude/loop-arg.md` missing → this is firing 1: write `goal:` from the `/preset loop-arg "<goal>"` argument (if the arg is vague, sharpen it into a statement with a checkable done-condition before writing), set `## Next` to the first concrete step, initialize an empty `## Log`, then end the firing. `.context/` exists at the project root → include the `Start:` pointer line (same pattern as the wrap-up note) so a cold session that opens this file knows where the project backdrop lives; no `.context/` → omit the line. File exists → **ignore the arg** (a relay respawn re-injects the original command; re-seeding would reset GOAL), read the file, and follow its `Start:` pointer if present and this session hasn't read those files yet.
2. **Goal check.** Read `goal:` and `## Log`. Goal met? → set `stop: true`, append a closing `## Log` line, and signal the loop to stop: dynamic `/loop` → end it (ScheduleWakeup stop); fixed interval → say "goal met, cancel the loop"; under `/relay` → also set the relay state file's `stop: true`. Do NOT rewrite `## Next`. Done.
3. **Do NEXT.** Execute exactly what `## Next` says — ONE unit of work. Never chain a second step; the runner re-fires.
4. **Self-prompt.** Decide the next concrete step toward GOAL given what `## Log` now shows, and **overwrite `## Next`** with it. Append one `## Log` line for the step just completed.

One step per firing, then done. GOAL is the fixed anchor; NEXT is the moving part.
