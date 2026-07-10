# query — answer from the wiki

1. Read the vault's `SCHEMA.md`, then `index.md`.
2. Pick relevant pages from the index and read only those. If the index gives no clear hit, or the vault exceeds ~100 pages, run instead:

   ```powershell
   python "<this skill's dir>\scripts\search.py" <vault> <key terms>
   ```

   (`<this skill's dir>` = the path printed as "Base directory for this skill" when this skill loads; quote both paths.) Read the top hits. If the answer might live in another vault, use `search.py --all <terms>` to search every registered vault at once; to see what links to a page, use `search.py --backlinks <vault> <page>`.
3. Answer in chat with a `[[page]]` citation on every claim. State what the wiki does NOT cover rather than padding the answer.
4. If the answer produced new synthesis (a comparison, a connection, an analysis — not a plain lookup), offer once to file it back as `wiki/syntheses/<slug>.md` (slug: lowercase the question's key words, non-alphanumeric runs → single hyphens, keep it short). On yes: write the page (frontmatter `type: synthesis`, `updated`, `tags`), add it to `index.md`, add a `[[<synthesis page>]]` wikilink from the most relevant existing wiki page (index.md does not count as an inbound link), and append to `log.md`:

   ```markdown
   ## [<today>] query | <question>
   - filed: [[<synthesis page>]]
   ```

   Explorations compound in the wiki the same way sources do.
