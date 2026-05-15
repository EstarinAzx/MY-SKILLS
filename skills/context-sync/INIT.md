# context-sync init

Bootstrap `.context/` for a fresh project. Run once. After this, use `update`.

## Process

### 1. Check existing state

- If `.context/` already exists, ask the user: abort, overwrite, or run `update` instead. Do not proceed without an answer.
- Scan the project root for **existing canonical context docs**: `CONTEXT.md`, `ARCHITECTURE.md`, `<PROJECT>_CONTEXT.md`, a heavy `README.md`, or `docs/overview.md`. If found, ask the user: **absorb** (fold the content into `.context/` files), **reference** (link from `overview.md` and treat as authoritative), or **ignore**. Default to absorb when the doc looks comprehensive.
- Detect the user's preferred mode for `.context/` itself: check `.gitignore` for `.context/`. If gitignored, you're in local mode (terse shorthand fine). Otherwise, committed mode (write for a stranger). When ambiguous, ask.

### 2. Explore the codebase

Use the Agent tool with `subagent_type=Explore` to walk the codebase. Ask it to report:

- Top-level directory layout and what each major directory contains.
- Tech stack from manifests (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.) including versions.
- Build / run / test commands (package scripts, Makefile, README).
- **Project type and user-facing surfaces.** Don't presume web-app shape. Possible surfaces include: HTTP routes, CLI commands, exported library API, agent tools, IDE extension entry points, RPC handlers, scheduled jobs. Report whichever ones exist and where they live.
- Anything in `docs/`, `CLAUDE.md`, `AGENTS.md`, or an existing project-context doc.

Cap the report at ~500 lines.

### 3. Decide the file set

Default file set: `overview.md`, `stack.md`, `active-work.md`, `decisions.md`. These are universal.

Add surface-area files based on what step 2 found. Common patterns:

- **Web app** → `api.md`, `frontend.md`, `backend.md`
- **CLI / TUI / agent** → `api.md` (or `tools.md`) for the tool/command surface, `frontend.md` (or `tui.md`) for any UI, `backend.md` for persistence/providers
- **Library** → `public-api.md` for the exported surface; drop `frontend.md` / `backend.md`
- **Static site / docs** → just `overview.md` + `stack.md` may be enough

Optional but often high-value: `gotchas.md` (almost always worth it for non-trivial projects), `code-map.md` (when the codebase has ~10+ source files or non-obvious split-ownership of logic across files), `history.md` (only if the project has a meaningful version trail).

### 4. Draft and write — with Obsidian conventions

Default mode: draft all files, write all files, then ask the user for revisions in a single round.

**Careful mode** — triggered when the user passes `careful` / `--careful` / `interactive` to the skill, or when the codebase is unfamiliar enough that an off-base draft would waste effort:

- For each file: draft → show → ask "look right?" → iterate once → write.
- Do not dump multiple drafts at once.

For both modes, use [FILE-TEMPLATES.md](FILE-TEMPLATES.md) as starting points — adapt names and structure to fit the project.

**Apply Obsidian conventions** as you write:

- **Frontmatter:** every file starts with YAML — at minimum `type`, `project`, `updated`. See FILE-TEMPLATES.md.
- **Wikilinks:** cross-reference handoff files with `[[bare-name]]`. `overview.md` is the MOC — its "Map" section links to every other handoff file so the graph view roots there.
- **Tags:** add `tags:` in frontmatter for topical files (`auth`, `routing`, `persistence`, etc.) so Obsidian's tag explorer is useful.

### 5. Stub active-work.md and decisions.md

Write `active-work.md` using the schema in [HANDOFF-FORMAT.md](HANDOFF-FORMAT.md), populated with `(no active work yet)` placeholders.

Write `decisions.md` with frontmatter, a header, and an empty body. If `docs/adr/` exists, add a single line: `See \`docs/adr/\` for architectural decision records.`

### 6. Confirm

Report to the user:

- Files created.
- Whether `.context/` is in committed or local mode (and a one-line nudge to commit if it should be).
- Obsidian tip: open `.context/` as a vault root to see the project context as a graph.
- Kickoff incantation: `Read .context/overview.md and .context/active-work.md to start a fresh agent.`

## Discipline

- Do not invent surface area you can't grep for. Mark uncertain content `(needs review)` and ask.
- Reference paths instead of pasting code. `auth middleware at src/middleware/auth.ts` beats a 30-line code dump.
- Short and accurate beats padded to a line target.
- If you absorbed an existing context doc in step 1, make `.context/` standalone afterward — don't leave dangling "see CONTEXT.md" references that defeat the point.
