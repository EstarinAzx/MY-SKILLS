# catch-up — orient in the repo from cold, no handoff note needed

One-shot. The no-baton cousin of [[pick-up]]: pick-up reads a `.context/pick-up.md` note left by [[wrap-up]]; catch-up works on any repo by reading live state. Use when you land in an unfamiliar or stale checkout with no note.

## Steps

1. **Git state.** Current branch, how it sits vs the default (ahead/behind), and uncommitted changes (`git status -s`, recent `git log --oneline -10`).
2. **In-flight work.** Open PRs and assigned/recent issues if `gh` is available (`gh pr list`, `gh pr status`). gh missing → skip, note it.
3. **Project context.** If `.context/` exists, skim `overview.md` + `active-work.md`. If a `.context/pick-up.md` note is sitting there, point the user at `/preset pick-up` and stop — that's the better entry.
4. **Report.** 4-6 lines: where the branch stands, what's uncommitted, what's open, and the most likely next task. End by asking what to work on — catch-up orients, it does not start work.

Fire once, then done.
