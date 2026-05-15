---
name: context-sync
description: Maintain a project-local `.context/` directory that hands off state between conversations — `init` bootstraps it, `update` refreshes it at session end so a fresh agent can pick up without re-reading the chat. Files are Obsidian-compatible (frontmatter + wikilinks) so `.context/` renders as a project-context graph. Use when the user wants to set up project handoff context, snapshot session state for the next agent, or sync .context/ files after a work session.
---

# context-sync

Maintains `.context/` — a project-local directory of handoff files so a fresh agent in a new conversation can pick up where the last one stopped, without re-reading the chat log.

Files are **Obsidian-compatible**: YAML frontmatter, `[[wikilinks]]` between related handoff files, MOC pattern. Open `.context/` as an Obsidian vault root and the graph view shows how project context is structured — `overview` at the center, surface-area files spoking out, gotchas and code-map cross-referencing each other.

This is a **handoff system**, not a knowledge wiki. For compounding cross-session knowledge, use the `kb` skill (separate system at `<cwd>/.memory/`).

## Two modes

- **`init`** — bootstrap `.context/` in a project. Run once. See [INIT.md](INIT.md).
- **`update`** — refresh `.context/` at the end of a work session. See [UPDATE.md](UPDATE.md).

## Routing

Look at the args passed to this skill:

- args contains `init` → follow [INIT.md](INIT.md).
- args contains `update` → follow [UPDATE.md](UPDATE.md).
- no args, `.context/` does not exist → suggest `init` and stop.
- no args, `.context/` exists → suggest `update` and stop.

If still ambiguous, ask the user which mode before proceeding.

## What lives in .context/

The canonical files. Adapt names and add files where the project demands — these are a starting point, not a fixed set.

| File | Role |
|------|------|
| `overview.md` | Project name, one-liner, layout, run commands, conventions. **MOC** — links to every other handoff file. |
| `stack.md` | Languages, frameworks, services, env vars, build system. |
| `active-work.md` | **The handoff baton.** Rolling state — overwritten each `update`. See [HANDOFF-FORMAT.md](HANDOFF-FORMAT.md). |
| `decisions.md` | Settled questions a future agent shouldn't re-debate. Append-only. |

Plus surface-area files, named to fit the project. Common shapes:

- **Web app** → `api.md` (routes), `frontend.md` (pages/components), `backend.md` (schema/auth)
- **CLI / agent** → `api.md` becomes "tools and commands"; `frontend.md` becomes "TUI"; `backend.md` becomes "providers / persistence"
- **Library** → `public-api.md` (exported surface), drop `frontend.md`/`backend.md` entirely
- **Static site / docs** → just `overview.md` + `stack.md` may be enough

Optional but high-value additions:

- `gotchas.md` — non-obvious traps that aren't visible in code or commits. Almost every non-trivial project has them.
- `code-map.md` — per-file index of where each piece of logic lives, with `file:line` citations for split-ownership hotspots (e.g. "FSM is in `predators.ts` but the kill call is in `world.ts:993`"). Worth it when the codebase has ~10+ source files or non-obvious cross-file logic ownership.
- `history.md` — version log / chronological release notes when the project is past a few dozen versions and recent direction matters for handoff.

Templates: [FILE-TEMPLATES.md](FILE-TEMPLATES.md).

## Obsidian compatibility

`.context/` is built to open as an Obsidian vault root. Graph view shows handoff files as nodes connected by `[[wikilinks]]`; backlinks pane and tag explorer work zero-config.

**Conventions applied to every handoff file:**

- **Frontmatter** — YAML at the top with `type`, `project`, `updated`, `tags`. See [FILE-TEMPLATES.md](FILE-TEMPLATES.md).
- **Wikilinks** — cross-reference handoff files with `[[bare-name]]` (no `.md` extension, no path). Obsidian resolves by basename across the vault.
- **MOC** — `overview.md` is the Map of Content. Every other handoff file is reachable from it via a wikilink in the "Map" section.
- **Tags** — broad (`tags: [context, handoff]`) plus topical (`tags: [auth]`) so the tag explorer is useful when multiple files share a theme.

Vault-as-affordance, not as compiler. There is no `daily/`, no `knowledge/`, no compile/query/lint ops in this skill. `.context/` is a curated handoff map, not an accumulating wiki.

## Two modes for `.context/` itself

- **Committed mode** (default) — `.context/` is checked into git. Travels with the repo, accessible to teammates, agents picking up from a fresh clone. Content rule: no machine-specific paths, no personal nicknames, no in-jokes — write for a stranger.
- **Local mode** — `.context/` is gitignored. Solo dev's private working memory; transferred between machines manually. Content rule: anything goes — operator nicknames, machine paths, terse shorthand all fine.

Pick based on whether the project has collaborators. Both are first-class. The difference matters for what content is appropriate, not for which files exist.

## Kickoff incantation for the next agent

After `update`, remind the user they can boot a fresh agent with:

> Read `.context/overview.md` and `.context/active-work.md`, then continue.

For task-scoped work, add the relevant slice (e.g. `.context/frontend.md` for UI work).

## Boundaries

- `.context/` is **project-local**. Do not put personal preferences here — those belong in user-level memory.
- `.context/` is intended to be committed to git. That's how it travels between machines and sessions.
- If `docs/adr/` exists, `decisions.md` should point to ADRs rather than duplicate them.
- Never write code, secrets, or large data dumps into `.context/`. It's a map, not the territory.
- **No hooks.** This skill never modifies `~/.claude/settings.json`. All operations are user-triggered.
- For compounding knowledge across sessions, use `kb`. This skill stays focused on handoff.
