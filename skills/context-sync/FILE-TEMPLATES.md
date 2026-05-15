# Templates for .context/ files

Starting points for `init`. Adjust to fit the actual project. The right length is whatever fits — the templates suggest a shape, not a quota.

File names are also adjustable — `api.md` may become `tools.md` for a CLI, `public-api.md` for a library, etc. Pick names that match the project's vocabulary.

## Frontmatter convention

Every handoff file starts with YAML frontmatter so Obsidian indexes it cleanly:

```
---
type: overview | stack | active-work | decisions | api | frontend | backend | gotchas | code-map | history
project: <project-name>
updated: YYYY-MM-DD
tags: [context, <topic1>, <topic2>]
---
```

Bump `updated:` whenever the file is edited. `tags:` are optional but make Obsidian's tag explorer useful when several handoff files share a theme (e.g. tag the auth-relevant files with `auth`).

Wikilinks in body use `[[bare-name]]` (no `.md`, no path). Obsidian resolves by basename across the vault.

## overview.md (the MOC)

`overview.md` is the Map of Content — link out to every other handoff file so the Obsidian graph view roots here.

```
---
type: overview
project: <name>
updated: YYYY-MM-DD
tags: [context, overview]
---

# Overview

**Project:** <name>
**One-liner:** <what it is, in one sentence>

## Layout
- `src/` — <what's here>
- `tests/` — <what's here>
- `docs/` — <what's here>
<keep to top-level dirs that matter>

## How to run
- Dev: `<command>`
- Test: `<command>`
- Build: `<command>`

## Where to look first
- Entry point: `<file>`
- Routing: `<file>`
- <Anything else a new agent should hit before exploring>

## Conventions
<Only non-obvious ones. Skip "we use TypeScript" — that's evident.>

## Map

- [[stack]] — languages, frameworks, env vars
- [[active-work]] — current handoff state
- [[decisions]] — settled questions
- [[api]] — <or [[tools]] / [[public-api]] — the user-facing surface>
- [[frontend]] — <if applicable>
- [[backend]] — <if applicable>
- [[gotchas]] — non-obvious traps
- [[code-map]] — where each piece of logic lives
- [[history]] — version trail
```

## stack.md

```
---
type: stack
project: <name>
updated: YYYY-MM-DD
tags: [context, stack]
---

# Stack

## Languages & runtime
- <language>: <version>
- <runtime>: <version>

## Frameworks
- <framework>: <version> — <one-line role>

## Services
- Database: <which, version>
- Cache: <which, version>
- <other infra>

## Key libraries
<Only ones that shape how code is written — state libs, ORMs, test runners. Skip lodash-tier dependencies.>

## Env vars
- `VAR_NAME` — <what it does, default if any>
<List the ones an agent will trip over without.>

## Related

- [[overview]] — project shape
- [[backend]] — how the stack is wired up
```

## api.md (or tools.md / public-api.md / etc.)

The project's user-facing or LLM-facing surface. Shape depends on project type:

**Web app — HTTP API:**
- **Routes** (grouped by resource) — for each: method, path, auth requirement, request shape, response shape
- **Auth model** (how requests are authenticated)
- **Error format** (shape of error responses)
- **Versioning** (if any)

**CLI / agent — tools and commands:**
- **Tools** (one row per tool: name, what it does, where the implementation lives)
- **Slash commands** (or equivalent user-callable commands)
- **External APIs consumed** (LLM providers, MCP servers, third-party APIs)
- **Auth model** (how each external dep is authenticated)

**Library — exported surface:**
- **Public API** (functions, classes, types — point to the file rather than re-doc the signatures)
- **Stability guarantees** (semver, deprecations)

For all shapes: keep terse — point to the handler/implementation file rather than copying types.

Frontmatter: `type: api` (or `tools` / `public-api`). Tag with topical themes touched (e.g. `tags: [context, api, auth]` if the auth model is documented here).

End with a `## Related` section linking [[overview]] and any other touched files ([[backend]], [[stack]]).

## frontend.md

```
---
type: frontend
project: <name>
updated: YYYY-MM-DD
tags: [context, frontend]
---

# Frontend

- **Pages / routes** (path → component)
- **State management** (which lib, where stores live, key store names)
- **Component conventions** (naming, file layout)
- **Design tokens** (where they live, how to use)

## Related

- [[overview]]
- [[api]] — backend surface this frontend consumes
- [[stack]]
```

## backend.md

```
---
type: backend
project: <name>
updated: YYYY-MM-DD
tags: [context, backend]
---

# Backend

- **Schema** (tables and relations — terse, point to migrations for detail)
- **Auth flow** (where it starts, where it ends)
- **Business-logic modules** (one line per major one)
- **Test setup** (how to run integration vs unit, fixture/seed strategy)

## Related

- [[overview]]
- [[api]] — the routes that hit this backend
- [[stack]]
- [[gotchas]] — non-obvious traps in business logic
```

## decisions.md (initial)

```
---
type: decisions
project: <name>
updated: YYYY-MM-DD
tags: [context, decisions]
---

# Decisions

Settled questions. Append-only. Each entry is dated.

If `docs/adr/` exists, prefer ADRs over entries here for substantial architectural decisions — link to them from this file.

## Related

- [[overview]]

---
```

## gotchas.md (optional but high-value)

Non-obvious traps that will burn time if you don't know them. Group by area (build, UI, providers, persistence, etc.).

For each gotcha:

- **The trap** — what looks normal but isn't
- **Why** — root cause or constraint
- **Workaround / rule** — what to do or not do

Skip anything obvious from reading the code. Skip anything covered by a comment in the code (the comment is doing the job). The right content here is institutional memory: "this looks wrong but is actually load-bearing because..." or "we tried X and it failed because Y."

```
---
type: gotchas
project: <name>
updated: YYYY-MM-DD
tags: [context, gotchas]
---

# Gotchas

### Don't re-add model validation for Anthropic providers

`sanitizeProfile()` in `src/utils/providerProfiles.ts` allows empty model fields for Anthropic providers. This is **load-bearing** — it enables the "Subscription default" feature where the model resolves dynamically based on the user's subscription tier.

If you re-add validation that requires a model string for Anthropic, subscription-default users will be locked out.

## Related

- [[code-map]] — where the load-bearing functions live
- [[backend]] — context for the auth/provider flow
```

## code-map.md (optional, for codebases with split logic ownership)

Per-file index of where each piece of logic actually lives. Worth it when the natural-sounding answer to "where does X happen?" is wrong — e.g. the FSM lives in one file but the strike call lives in another.

When it earns its keep: ~10+ source files; some files are large enough (>500 lines) that they hide cross-cutting logic; split ownership across files isn't obvious from filenames. Skip if filenames already tell the story.

Shape:

- **TL;DR** — one paragraph or ASCII diagram of how the layers fit (e.g. `main → render+ui → workerBridge → worker → sim`).
- **Per-layer tables** — one section per layer/area; rows are `file → what lives here`, with `file:line` markdown links for the load-bearing spots.
- **Quick-jump table** at the bottom — maps natural-language questions ("why are X dying?", "why isn't Y growing?") to specific `file:line` citations. Usually the highest-value section.

Sample skeleton:

```
---
type: code-map
project: <name>
updated: YYYY-MM-DD
tags: [context, code-map]
---

# Code Map

Where each piece of logic lives in `<src-dir>/`.

<one paragraph or small ASCII diagram of the layer shape>

## <Layer name> (`<path>`)

| File | What lives here |
|---|---|
| [<file>](<path>) | <what it owns + key constants if non-obvious> |
...

## Quick "where do I look for…?"

| Question | Start at |
|---|---|
| "<behavioural question>" | [<file:line>](<path#Lnnn>) |
...

## Related

- [[gotchas]]
- [[backend]]
```

Maintenance: line numbers drift as files change; file/function pointers stay correct. Refresh citations during `update` when a heavily-cited file was edited substantially this session.

## history.md (optional, for projects with a long version trail)

Chronological release log. One row per version with commit SHA and one-line headline. Goal is to give a fresh agent a sense of recent direction at a glance — not to replicate `git log`.

Useful when there's a per-version changelog elsewhere (gitignored release notes, GitHub releases) and you want a stripped-down version inside `.context/` for handoff.

```
---
type: history
project: <name>
updated: YYYY-MM-DD
tags: [context, history]
---

# History

| Version | Commit | Headline |
|---|---|---|
| **0.3.67** | `b00ad0b` | one-line description |
| **0.3.66** | `bac4b27` | one-line description |

## Themes

<3-5 bullets summarizing recent direction>

## Related

- [[overview]]
- [[decisions]]
```
