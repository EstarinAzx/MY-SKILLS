# ship — push the branch, open a PR from the diff

One-shot. The successor to [[wrap-up]]: wrap-up stops at the local commit on purpose; ship takes the committed branch the rest of the way. Run it after the work is committed. Optional argument sets the PR base: `/preset ship <base-branch>` (default: the repo's main/master).

## Steps

1. **Preflight.** Confirm the work is committed (`git status` clean-ish) and you're not on the default branch. On main/master → stop and say so; the commit should have branched first (see [[wrap-up]]).
2. **Sync.** Push the current branch with upstream set (`git push -u origin <branch>`).
3. **Compose the PR.** Generate title + body from the diff against base (`git diff <base>...HEAD`), not from memory. Body: what changed and why, in a few lines; link any issue the work closes (`Closes #<n>`). Keep it tight.
4. **Open.** `gh pr create --base <base> --title ... --body ...`. gh missing / not authed → print the title + body and the compare URL for the user to open manually.
5. **Report.** Return the PR URL. Do not merge. Do not push more unless asked.

Fire once, then done.
