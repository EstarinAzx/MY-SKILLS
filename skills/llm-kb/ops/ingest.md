# ingest — file a source into the wiki

Read the vault's `SCHEMA.md` first. It may override anything below.

## Resolve targets

- `ingest <file>` → that file in `raw/` (accept bare name with or without extension).
- `ingest all` → every `raw/*.md` and `raw/*.txt` not referenced by a `raw:` frontmatter field in any `wiki/sources/` page. Flat scan only — subdirectories of `raw/` are not scanned. List the targets and count before starting.
- If `ingest all` finds 0 targets, report "All raw files already ingested" and stop.

## Per source

1. Read the source fully. If it references images present in `raw/assets/`, view the few that carry information (charts, diagrams) — text first, images second.
2. **Interactive mode** (default unless SCHEMA.md or the user says batch): present 3-7 key takeaways as bullets and ask what to emphasize or skip. Batch mode skips the discussion. `ingest all` implies batch unless SCHEMA.md says otherwise.
3. Write `wiki/sources/<slug>.md` — derive `<slug>` from the source filename stem: lowercase, non-alphanumeric runs become single hyphens (`My Article (v2).md` → `my-article-v2`):

   ```markdown
   ---
   type: source
   raw: <exact raw filename>
   updated: <today>
   tags: [<2-4 tags>]
   ---

   # <Source title>

   <One-paragraph summary.>

   ## Key claims
   - <claim, wikilinking every entity/concept it touches> ([[wikilinks]])
   ```

4. Update or create every touched page in the SCHEMA.md categories: append new facts in the relevant section with a `([[<source page>]])` citation. If the page has a `## Sources` or `## References` section, append there; otherwise append at the bottom. Bump each touched page's `updated` frontmatter field. One source touching 10-15 pages is normal; fewer is fine for a thin source. New pages get the category's frontmatter `type`, get added to `index.md`, and must be wikilinked from at least one other page (the source page counts).
5. **Contradiction rule** — never silently overwrite. When a new claim conflicts with an existing page claim, add directly under the older claim:

   ```markdown
   > ⚠️ contradicts [[<new source page>]] — <one line on the conflict>
   ```

   and surface it in the wrap-up.
6. Update `index.md`: new pages under their category with a one-line summary; refresh one-liners that changed.
7. Append to `log.md`:

   ```markdown
   ## [<today>] ingest | <source title>
   - pages touched: [[a]], [[b]], …
   - contradictions flagged: <n or none>
   ```

## Wrap-up (once per batch)

One short report: sources filed, pages created/updated, contradictions flagged, and at most 3 suggested follow-up questions.
