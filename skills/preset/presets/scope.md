# scope — front gate before writing code: restate, plan, go/no-go

One-shot. The entry mirror of [[wrap-up]]'s exit gate. Applies to the task about to start. Optional argument names the task: `/preset scope <task-or-#>`.

## Steps

1. **Identify the task.** Argument given → that's the task (issue number → `gh issue view <#> --comments`; gh missing / no such issue → look for a local `issues.md`/`ISSUES.md`/`docs/issues*`; still nothing → treat as free-text). No argument → use the task already in flight from the conversation.
2. **Read before planning.** Pull the relevant files into context — don't plan blind. If `.context/` exists, skim `overview.md` + `active-work.md` for backdrop.
3. **Restate.** One or two lines: what done means for this task, in your words. Surfaces misread early.
4. **Plan.** List the files you'll touch, the approach in 2-3 lines, and any risk/unknown/landmine worth flagging before code exists.
5. **Gate.** Invoke the AskUserQuestion tool for go/no-go. One question, options roughly:
   - "Go — start" → begin the work.
   - "Adjust" (+ Other for notes) → revise the plan, re-run this gate.

Fire once, then start.
