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

### 4. Append to decisions.md — only if warranted

Append a new entry ONLY if a load-bearing decision was made this session. A load-bearing decision:

- Constrains future work ("we picked Zustand over Redux")
- Closes a path someone might re-propose ("tried server components here, doesn't work because…")
- Codifies a non-obvious tradeoff

Skip ephemeral choices and anything obvious from the code.

Format:

```
## YYYY-MM-DD — <short title>
**Decision:** <what was decided>
**Why:** <the reason — the constraint or alternative considered>
**Reversibility:** <easy / hard / one-way>
```

If `docs/adr/` exists and the decision warrants an ADR, suggest writing one and reference it from `decisions.md` instead of duplicating.

Bump frontmatter `updated:` to today.

### 5. Update structural files only on actual structural change

For `overview.md`, `stack.md`, `api.md`, `frontend.md`, `backend.md`, `code-map.md`, `gotchas.md`, `history.md`:

- Update if this session added / removed / renamed an endpoint, route, page, schema table, store, env var, or major dependency.
- For `code-map.md` specifically: also re-anchor line citations if a heavily-cited file was edited substantially this session. Line numbers drift; file/function pointers are durable. A targeted refresh (only the citations that moved) beats a full rewrite.
- For `gotchas.md`: append new traps discovered this session if they're genuinely non-obvious and not already covered by an inline code comment.
- Otherwise leave alone.

When you touch a file:

- Bump frontmatter `updated:` to today.
- Add wikilinks if the change introduces a new relationship between handoff files (e.g. a new env var in `stack.md` referenced from `backend.md`).
- If `overview.md` gains or loses a handoff file from its scope, update the "Map" section.
- **Back-fill on the fly:** if the file lacks YAML frontmatter or a `## Related` wikilinks section (legacy `.context/` from before Obsidian conventions), add them per [FILE-TEMPLATES.md](FILE-TEMPLATES.md). One-time migration as files get touched naturally.

Don't rewrite these prophylactically. Churn here defeats the point.

### 6. Report

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
