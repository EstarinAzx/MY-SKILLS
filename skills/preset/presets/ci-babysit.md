# ci-babysit — watch a PR's checks; green stops the loop, red gets the smallest honest fix

Loop body. Fire via `/loop /preset ci-babysit <pr#|branch>` right after `/preset ship`, or one-shot to check once. Argument names the PR or branch; none given → the current branch's open PR.

## Loop-body contract

Every firing is cheap and idempotent: read check state first, act at most once per distinct failure, leave a breadcrumb, stop the loop the moment a human is needed or everything is green.

## Steps

1. **Read checks.** `gh pr checks <pr>` (fallback `gh run list --branch <branch>`). Three states:
2. **All green** → report in one line + stop signal (dynamic loop → end it; fixed interval → say "green, cancel the loop"). Done.
3. **Pending** → one-line status, end the firing. No analysis, no log-pulling — pending firings must cost almost nothing.
4. **Red** → pull the failing job's log tail and diagnose:
   - **Trivial and mechanical** (lint, format, stale snapshot, obvious import) → fix, run the failing check locally if runnable, push. One fix per firing.
   - **Flaky-looking** (passed before, infra timeout, no related diff) → rerun the job once (`gh run rerun --failed`). Only once per failure — a second identical failure is real.
   - **Real or unclear** → no speculative pushes. Summarize root cause + suspect files as a PR comment, then stop signal — human's turn.
5. **Idempotency guard.** Before fixing or rerunning, check whether the previous firing already tried it (own last commit / own PR comment / rerun already used). Same failure after own fix → escalate per the "real" branch, never fix-push twice for one failure.

One check-and-act per firing, then done.
