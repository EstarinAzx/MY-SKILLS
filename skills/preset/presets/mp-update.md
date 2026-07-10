# mp-update — pull a new mattpocock/skills release into the curated install

One-shot. Codifies the [[mattpocock-skills-lineup]] decision (ecosystem-kb, 2026-07-10) so a release update is mechanical instead of re-derived. Optional argument names a tag: `/preset mp-update v1.2.0`.

## The curated list

Install/update **only** these (engineering: to-spec, to-tickets, wayfinder, research, prototype, implement, triage, domain-modeling, codebase-design, ask-matt, setup-matt-pocock-skills, resolving-merge-conflicts, grill-with-docs, improve-codebase-architecture; productivity: grill-me, grilling, teach).

**Never install:** handoff (context-sync owns handoff), tdd (superpowers sole — [[tdd-lineup]]), code-review (built-in name collision), diagnosing-bugs (superpowers systematic-debugging + bugs-begone), writing-great-skills (superpowers writing-skills).

## Steps

1. **Read the release.** Fetch `https://github.com/mattpocock/skills/releases` (or the tag passed as argument) — note renames, new skills, removed skills.
2. **Backup + clone.** Copy the current curated folders to `~/.claude/_deprecated/mp-pre-<version>-backup/`. Shallow-clone the repo to the scratchpad.
3. **Refresh.** For each curated skill: `rm -rf` the live folder, copy the new one (clean replace kills stale aux files). A skill renamed upstream → move the old live folder into the backup and install under the new name.
4. **New upstream skills** are NOT auto-installed. Evaluate each against the exclusion decision and the one-winner lineup memories; propose install/skip to the user with a one-line reason each.
5. **Reapply the two local patches** (upstream copies won't have them):
   - `implement/SKILL.md`: the `/tdd` line becomes "Use the superpowers:test-driven-development skill where possible, at pre-agreed seams."
   - `ask-matt/SKILL.md`: re-add the "**Local ecosystem note:**" blockquote after the `# Ask Matt` heading (routing: /tdd → superpowers TDD, /handoff → /context-update, /code-review → built-in, diagnosing-bugs → superpowers/bugs-begone).
6. **Verify.** `grep -rln "/tdd\|/handoff" <curated folders>` — hits outside the two patched files and explainer prose are dangling refs to fix. Then run `/preset health`.
7. **Bookkeep.** Update ecosystem-kb pages ([[mattpocock-lifecycle]], [[github-planning]], [[grill-skills]], any skill whose page describes changed behavior), append a log.md entry, and update the mattpocock-skills-lineup memory if the lineup itself changed.
8. **Template.** `python ~/.claude/skills/ecosystem-audit/scripts/template_sync.py --apply`, then commit + push in `template/IN USE/`.

Fire once, then done.
