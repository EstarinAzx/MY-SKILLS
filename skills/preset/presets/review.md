# review — fresh-eyes review of the working diff before commit

One-shot. The pre-commit slot, just ahead of [[wrap-up]]: catch problems while the diff is still uncommitted and cheap to fix. Defaults to a subagent on purpose — you wrote the code, so reviewing it inline carries author bias; a separate agent gets fresh eyes and returns compressed findings that cost less main context.

## Steps

1. **Scope the diff.** Default target is the uncommitted working diff (`git diff` + staged). Argument narrows it: `/preset review <path-or-base>` reviews a file/dir or a branch range.
2. **Delegate, in order of preference:**
   - **Subagent first** → dispatch the `caveman:cavecrew-reviewer` agent on the diff. Fresh eyes, one-line-per-finding, severity-tagged, no praise.
   - **Fallback** → reviewer agent unavailable → invoke the `/code-review` skill.
   - **Last resort** → neither present → review inline, but say plainly it's *self-review* (author-biased, weaker).
3. **Report.** Findings only, one line each: `path:line — severity: problem → fix`. No scope creep, no "looks good" filler.
4. **Triage, don't auto-fix.** Hand the list back. The user decides what to fix before [[wrap-up]] commits — review flags, it does not land changes.

Fire once, then done.
