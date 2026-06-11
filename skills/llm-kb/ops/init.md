# init — bootstrap a vault

Target directory: the path given as argument, else cwd. If `SCHEMA.md` already exists there, stop — say it is already a vault. If the target directory does not exist, create it (and its parents) first.

1. Ask (AskUserQuestion; a second round follows only if kind is "other": propose, then confirm categories):
   - **Topic** — short vault name, a noun phrase (e.g. "Karpathy papers").
   - **Mission** — one-line purpose sentence for the vault.
   - **Kind** — book / research topic / personal tracking / other. Drives category presets:
     - book → `characters/`, `themes/`, `plot-threads/`
     - research → `claims/`, `methods/`, `people/`
     - personal → `goals/`, `observations/`, `experiments/`
     - other → propose 2-4 categories from the topic; confirm with the user.
   - **Ingest style** — interactive (discuss takeaways per source; default) or batch (file with minimal supervision).
2. Write `SCHEMA.md` from this skill's `TEMPLATE.md` with every `{{PLACEHOLDER}}` replaced by real values:
   - `{{TOPIC}}` → the vault name (both occurrences).
   - `{{MISSION}}` → the one-line mission sentence.
   - `{{DATE}}` → today's date, YYYY-MM-DD (both occurrences).
   - `{{CATEGORY_DIRS}}` → one bullet per chosen category dir in the `wiki/<category>/` form, with a one-line "what belongs here" (matching the surrounding Layout bullets).
   - `{{CATEGORIES}}` → for each category: name, what belongs, its frontmatter `type` value (singular: `character`, `claim`, …).
   - `{{INGEST_STYLE}}` → the chosen style, one sentence.
   - Verify zero `{{` remain in the written file, and that it landed in the target directory.
3. Create:
   - `index.md` — frontmatter (`type: index`, `updated: <today>`), `# Index`, one `## <Category>` heading per category (including Sources and Syntheses), each section empty.
   - `log.md` — frontmatter (`type: log`; no `updated` field — the file is append-only), then `## [<today>] init | <topic>`.
   - Directories: `raw/`, `raw/assets/`, `wiki/sources/`, `wiki/syntheses/`, and one `wiki/<category>/` per chosen category.
4. Tell the user: drop sources into `raw/` (Obsidian Web Clipper works well; vault opens directly in Obsidian), then run `/llm-kb ingest <file|all>`. Mention `git init` is optional and theirs to manage.
