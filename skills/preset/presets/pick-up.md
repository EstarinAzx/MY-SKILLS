# pick-up — read the handoff note, resume

One-shot. The inverse of [[wrap-up]]: wrap-up writes `.context/pick-up.md` at task end, pick-up reads it and continues. Optional argument overrides the note: `/preset pick-up <#-or-text>`.

## Steps

1. **No argument** → read `.context/pick-up.md` and do what it says. Pull backdrop from `.context/overview.md` and `active-work.md` only if the note points to them.
   - No `.context/pick-up.md` → say so, suggest `/context-init` (or running `/preset wrap-up` first to leave a note), and stop.
2. **Argument given** → ignore the note; work that target instead. If it's an issue number, `gh issue view <#> --comments`; gh missing / no such issue → look for a local issues file (`issues.md`, `ISSUES.md`, `docs/issues*`); still nothing → treat the argument as free-text.
3. If the target is an issue reference, fetch it. Then give a 2-3 line plan and start.
