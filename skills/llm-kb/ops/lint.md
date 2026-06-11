# lint — vault health check

1. Read the vault's `SCHEMA.md`.
2. **Structural pass** (deterministic, free):

   ```powershell
   python "<this skill's dir>\scripts\lint.py" <vault>
   ```

   (`<this skill's dir>` = the path printed as "Base directory for this skill" when this skill loads; quote both paths.) Output lines are `category<TAB>location<TAB>detail`. Categories: `broken-link`, `no-frontmatter`, `not-in-index`, `index-dangling`, `orphan`, `log-format`, `uningested`. Exit 0 = clean. The last output line is a `<n> issue(s)` summary.
3. **Semantic pass** (this session): read `index.md`, every page flagged above, and the 5 most recently updated wiki pages. Look for: contradictions between pages, claims superseded by newer sources, concepts mentioned on 3+ pages without their own page, and gaps worth a web search.
4. Report findings grouped by category, one line each with the proposed fix. Apply fixes only on approval — batch approval is fine. `raw/` is never "fixed" (immutable). `uningested` findings get `/llm-kb ingest` suggested, not an edit.
5. Append to `log.md`: `## [<today>] lint | <n> structural, <m> semantic findings`.
