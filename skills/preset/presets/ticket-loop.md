# ticket-loop — work the tracker queue, one ready-for-agent ticket per firing

Loop body. Designed to be fired repeatedly by `/loop /preset ticket-loop` (self-paced) or `/loop 30m /preset ticket-loop`; also works as a plain one-shot "grab me the next ticket". Optional argument filters the queue (a label, milestone, or keyword). ONE ticket per firing — never chain a second, the loop harness re-fires.

## Loop-body contract

Check state before working (a firing must be idempotent), do one unit, leave breadcrumbs on the ticket itself, and signal the loop when the queue is dry: under `/loop` dynamic mode end the loop (ScheduleWakeup stop); under a fixed interval, say "queue empty" so the user cancels.

## Steps

1. **Tracker config.** Read `docs/agents/issue-tracker.md` + `triage-labels.md` (written by `/setup-matt-pocock-skills`). Missing → GitHub via `gh` with the canonical label names.
2. **Pick ONE ticket.** Oldest unblocked `ready-for-agent` ticket matching the filter. Skip any whose "Blocked by" tickets are still open. None left → report queue empty + stop signal (see contract). 
3. **Idempotency guard.** A branch or open PR already named for this ticket → don't restart: resume it if it's yours and unfinished, otherwise comment on the collision, relabel `ready-for-human`, and end the firing.
4. **Work it.** Branch `ticket/<id>-<slug>`, then `/implement` on the ticket body (drives superpowers TDD + code review). Scope is the ticket, nothing else — adjacent problems become a comment, not a detour.
5. **Gate.** Full test suite + typecheck green → commit and push/PR per repo convention. Not green after honest effort, or the ticket turns out ambiguous/destructive → stop coding, relabel `ready-for-human`.
6. **Breadcrumb.** Comment on the ticket either way: what was done, PR link, or exactly where it got stuck and why. Close/relabel per outcome. The comment is the handoff to the next firing (or the human) — write it so a cold reader can continue.

One ticket per firing, then done.
