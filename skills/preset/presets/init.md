# init — idea → grill → PRD → issues, one funnel

One-shot. Door zero: turns a raw idea into settled decisions, a PRD, and a grabbable issue list — before the [[pick-up]]/[[wrap-up]] loop ever starts. Optional argument seeds the idea: `/preset init <idea>`.

## Steps

1. **Capture the idea.** Argument given → that's the idea. No argument → ask one line: "What's the idea?". If the idea arrives already well-specified (constraints, stack, scope all stated), say so and offer a *short* grill (only the unresolved branches) instead of the full interview.
2. **Pick the destination once.** Invoke the AskUserQuestion tool — where should the PRD + issues live? One answer governs steps 4, 7 and 8; never re-ask.
   - **GitHub** → PRD and slices become GitHub issues. Verify `gh auth status` and a remote exist first; if either is missing, say so and fall back to Local.
   - **Local md** → PRD at `docs/prd.md`, slices as `docs/issues/NN-<slug>.md` — exactly where [[scope]]'s no-gh fallback already looks.
3. **Bootstrap memory (conditional).** If `.context/` does not exist, offer `/context-init` before grilling — grill decisions and the PRD pointer need somewhere durable to land. If the user declines, continue without it.
4. **Tracker config (conditional).** If `docs/agents/` does not exist, offer `/setup-matt-pocock-skills` — seed its issue-tracker section from step 2's answer (never re-ask it); triage labels and domain-doc layout take the canonical defaults unless the user objects. Declined → continue; the tracker skills fall back to their defaults.
5. **Grill.** If the project has a domain model on record — a `CONTEXT.md` or `docs/adr/` — invoke `/grill-with-docs` so the idea is challenged against the existing vocabulary and decisions, and the docs are updated inline. Otherwise invoke `/grill-me`. Either way, walk the decision tree until the design is settled; wrap-up records decisions to `.context/decisions.md` when present.
6. **Map the happy path.** Decisions settled → invoke `/hp` on the agreed design to draw the golden-path MVD; it writes `.context/happy-path.md`. Default mode `ux+beat` unless the user picks another. The PRD (next step) embeds it.
7. **PRD.** Invoke `/to-spec` (renamed from to-prd in mattpocock/skills v1.1.0) on the grilled context, embedding the MVD from `.context/happy-path.md`. Destination GitHub → as written (submits an issue). Destination Local → same spec template, but write `docs/prd.md` instead of creating an issue.
8. **Issues.** Invoke `/to-tickets` (renamed from to-issues in v1.1.0) against the PRD. Destination GitHub → as written. Destination Local → same vertical-slice process and ticket template, but one file per slice at `docs/issues/NN-<slug>.md`, numbered in dependency order, with "Blocked by" naming sibling files; in the PRD, link the slice files so the set reads as one unit.
9. **Hand off.** Close by naming the first unblocked slice and suggest `/preset scope <that issue>` to enter the work loop.

Fire once, then the funnel is done — implementation belongs to the loop, not to this preset.
