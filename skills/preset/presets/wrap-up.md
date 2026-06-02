# wrap-up — finish-task gate, then context-update, handoff note + commit

One-shot. Applies to the task currently in flight (or the next one if none is running).

When you finish that task:

1. **Gate.** Invoke the AskUserQuestion tool to stand by for the user's go/no-go after their eyeball test. One question, options roughly:
   - "Go — land it" → proceed to step 2.
   - "Needs changes" (+ Other for notes) → make the fixes, then re-run this gate.
2. **Context update (conditional).** On "go", if a `.context/` directory exists in the repo, invoke `/context-update`. If there is no `.context/`, invoke `/context-init`.
3. **Handoff note.** Write/update `.context/pick-up.md` — the self-contained baton `/preset pick-up` reads next session. Open it with a pointer line — `Start: read .context/overview.md + active-work.md` — so pick-up rehydrates the project before working. Then record: what this task finished, the single next task + pointers (issue #, files touched), and any landmine — enough that `pick-up` needs nothing else. Keep it short; full state lives in `active-work.md`.
4. **Commit.** Stage the work (including the updated `.context/`) and commit with a clear conventional-commit message. If on the default branch (main/master), create a branch first per repo rules. Do not push unless asked.

Fire once, then done.
