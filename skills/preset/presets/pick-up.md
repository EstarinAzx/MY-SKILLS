# pick-up — rehydrate from .context/, then start the next task

One-shot. The inverse of [[wrap-up]]: wrap-up writes the handoff note at task end, pick-up reads it to resume. Optional argument = the issue/task to work: `/preset pick-up <#-or-text>`.

## 1. Rehydrate

- If `.context/` does not exist → say so, suggest `/context-init` (or `/context-sync init`), and stop **unless** an issue/task argument was given (then skip to step 2).
- Read `.context/overview.md` (project map) and `.context/active-work.md` (full session state).
- Read `.context/pick-up.md` if it exists — the focused "resume here" note wrap-up left: what was last finished and the next task.

## 2. Resolve what to work on

Find the target in this order — flexible, never hard-depends on `gh`:

1. **Argument given** → try `gh issue view <#> --comments`.
2. gh missing / no such issue → look for a local issues file (`issues.md`, `ISSUES.md`, `docs/issues*`) and find the matching entry.
3. Still nothing → treat the argument as a free-text task description.
4. **No argument** → use the next task from `.context/pick-up.md` (or `active-work.md`).

## 3. Start

Give a 2-3 line plan tying the issue to the context — acceptance criteria plus where it touches the code per `active-work.md`. Then begin. For task-scoped work, also read the relevant `.context/` slice (e.g. `frontend.md`, `api.md`).
