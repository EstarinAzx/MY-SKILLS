# context-sync update

Refresh `.context/` at any context-switch — end of a work session, or before forking the work to a different task or session. Designed to leave a clean handoff for the next agent in a new conversation.

## Process

### 1. Verify state

- Confirm `.context/` exists. If not, suggest `init` and stop.
- Read `.context/active-work.md` and `.context/decisions.md` so you know prior state.

### 2. Gather what changed

Two sources, used together:

- **This conversation** — what was just worked on, decided, mid-flight, or blocked.
- **Git** — `git log` since the commit referenced in `active-work.md` (or last 20 commits if unknown), and `git diff` for uncommitted changes.

If the project is not a git repo (no `.git/`), skip the git step and ask the user for a session summary before writing — there's no fallback ground truth.

If the conversation has been compacted and your memory of it is thin, lean on git as primary and ask the user to fill gaps before writing.

### 3. Update active-work.md (rolling — overwrite)

Rewrite from scratch using the schema in [HANDOFF-FORMAT.md](HANDOFF-FORMAT.md). New content reflects **current** state, not history. Past content is gone — that's intentional. The next agent reads only this file (plus `overview.md`) to know where to pick up; optimize for that reader.

Preserve YAML frontmatter and existing wikilinks when rewriting. Bump `updated:` in frontmatter to today.

### 4. Record a decision — only if warranted

Append a decision ONLY if a load-bearing decision was made this session. A load-bearing decision:

- Constrains future work ("we picked Zustand over Redux")
- Closes a path someone might re-propose ("tried server components here, doesn't work because…")
- Codifies a non-obvious tradeoff

Skip ephemeral choices and anything obvious from the code.

`decisions` is folded, so recording one is three moves:

1. **Write the entry** `decisions/YYYY-MM-DD-<kebab-title>.md` using the entry template in [FILE-TEMPLATES.md](FILE-TEMPLATES.md) (`Decision` / `Why` / `Reversibility`, plus a `## Related` block that back-links `[[decisions]]`). Create the `decisions/` folder now if this is the first entry.
2. **Prepend a link line** to `decisions.md` at the top of the list, newest first: `- [[YYYY-MM-DD-<kebab-title>]] — <one-line title>`.
3. **Bump `updated:`** to today on the index (and the entry carries today already).

If `docs/adr/` exists and the decision warrants an ADR, write the ADR and make the `decisions/` entry a one-line pointer to it instead of duplicating.

### 5. Update structural files only on actual structural change

For `overview.md`, `stack.md`, `api.md`, `frontend.md`, `backend.md`, `code-map.md`, `gotchas.md`, `history.md`:

- Update if this session added / removed / renamed an endpoint, route, page, schema table, store, env var, or major dependency.
- For `code-map.md` specifically: also re-anchor line citations if a heavily-cited file was edited substantially this session. Line numbers drift; file/function pointers are durable. A targeted refresh (only the citations that moved) beats a full rewrite.
- For `gotchas`: append new traps discovered this session if genuinely non-obvious and not already covered by an inline code comment. `gotchas` is folded — write `gotchas/<kebab-trap>.md` from the entry template (back-linking `[[gotchas]]`), prepend a link line to `gotchas.md`, and bump the index `updated:`. Create the `gotchas/` folder on the first entry.
- Otherwise leave alone.

When you touch a file:

- Bump frontmatter `updated:` to today.
- Add wikilinks if the change introduces a new relationship between handoff files (e.g. a new env var in `stack.md` referenced from `backend.md`).
- If `overview.md` gains or loses a handoff file from its scope, update the "Map" section.
- **Back-fill on the fly:** if the file lacks YAML frontmatter or a `## Related` wikilinks section (legacy `.context/` from before Obsidian conventions), add them per [FILE-TEMPLATES.md](FILE-TEMPLATES.md). One-time migration as files get touched naturally.

Don't rewrite these prophylactically. Churn here defeats the point.

### 5b. Migrate a legacy flat file — offer, don't force

If `decisions.md` is still a **flat monolith** (dated `## YYYY-MM-DD — …` blocks in the file, no `decisions/` folder) **and** it is actually long enough to hurt (roughly 10+ entries or past a few hundred lines), offer to fold it:

- Split each `## YYYY-MM-DD — <title>` block into `decisions/<date>-<kebab-title>.md` (entry template; the block body maps onto `Decision`/`Why`/`Reversibility`).
- Rewrite `decisions.md` as the index: newest-first link list + `## Related → [[overview]]`.
- Run lint (step 6) afterward to confirm no drift.

Do this only with the user's go-ahead, and never on a small file — a 3-entry `decisions.md` has nothing to fix and stays flat. Migrate `gotchas.md` the same way, splitting on `### <title>` blocks. This is the same "back-fill on touch" spirit as the frontmatter migration in step 5.

### 6. Report

- **Run lint:** `python "<this skill's dir>\scripts\lint.py" .context` (add `--stale` to also flag pages past 90 days). Surface any `broken-link` / `orphan` / `entry-not-indexed` / `index-dangling` lines in the report so drift is caught the moment it appears. A clean run prints `0 issue(s)`.

Tell the user, briefly:

- Which files changed (and which were deliberately untouched)
- Any decisions appended
- The kickoff incantation for the next agent

If you guessed at anything ambiguous, flag it so the user can correct before the next handoff.

## Discipline

- `active-work.md` is current state, not a chat log. No "we discussed X then Y."
- Don't move information into `.context/` that already lives in committed code or commit messages.
- Don't update structural files just because tokens were spent in their area.
- Don't define domain terms in `.context/`. If a `CONTEXT.md` glossary exists, it owns the ubiquitous language — reference it, never copy term definitions. A term sharpened this session belongs in `CONTEXT.md` (via `/grill-with-docs`), not in a `.context/` file.
