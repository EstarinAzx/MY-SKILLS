# health — one-command health check of the whole ~/.claude ecosystem

One-shot. Off-loop maintenance: runs every deterministic checker in one pass and reads the results back as a single punch list. Use after installing/updating skills, before pushing the template, or whenever things feel drifty.

## Steps

1. **Skills ↔ vault.** Run `python ~/.claude/skills/ecosystem-audit/scripts/audit.py`. Known-standing findings (`skills/docs` stray folder, `elucidate-plugin` autoload) are expected — list them last, marked "standing".
2. **Template drift.** Run `python ~/.claude/skills/ecosystem-audit/scripts/template_sync.py`. `drift` rows mean the pushed copy lags live; `live-only` skill rows are curation candidates, not errors.
3. **Vault lint.** For each vault in `~/.claude/vault-registry.txt`, run `python ~/.claude/skills/llm-kb/scripts/lint.py <vault> --stale 30`.
4. **Report.** One punch list grouped by source (audit / template / lint), worst-first, each row with a one-line recommended action. All clean → say so in one line.
5. **Offer fixes, don't apply.** Only two exceptions may be offered proactively: `template_sync.py --apply` (mutates only the template copy — after applying, remind about commit+push in the template repo) and writing missing vault pages. Anything destructive (deleting folders, removing pages) needs explicit per-item confirmation.

Fire once, then done.
