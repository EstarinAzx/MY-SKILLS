---
type: schema
topic: Claude ecosystem
updated: 2026-06-12
---

# Claude ecosystem — vault schema

Mission: Living map of S.D's Claude Code setup — every plugin, skill, mode, config mechanism, and the decisions behind them — so any session can answer "what do we have and why" without re-deriving it.

This file is this vault's law. The LLM reads it first on every operation and defers to it over the skill's defaults. Evolve it as the domain teaches you what works; note changes in the Evolution log below.

## Layout

- `raw/` — immutable sources (Obsidian Web Clipper target). Never edited.
- `raw/assets/` — downloaded images for clipped articles.
- `wiki/` — LLM-owned pages; everything under it is written and maintained by the LLM.
- `wiki/sources/` — one summary page per ingested source.
- `wiki/plugins/` — one page per installed Claude Code plugin (marketplace or directory-loaded): what it provides, where it lives, how it loads.
- `wiki/skills/` — one page per standalone skill or tight skill family in `~/.claude/skills/`: trigger, purpose, routing notes.
- `wiki/config/` — harness mechanics: settings.json, hooks, MCP servers, memory system, plugin-loading rules.
- `wiki/decisions/` — lineups, deprecations, and why-we-chose-X records; each page is one settled decision.
- `wiki/syntheses/` — overview, evolving thesis, comparisons, filed query answers.
- `index.md` — every page, one line each, grouped by category. Read first on query.
- `log.md` — append-only timeline: `## [YYYY-MM-DD] <op> | <title>`.

## Page categories

- **Plugins** — installed Claude Code plugins. What belongs: install source, version, skills/agents/MCP servers it contributes, session behavior. Frontmatter `type: plugin`.
- **Skills** — standalone skills under `~/.claude/skills/` (not plugin-bundled). Tight families share one page. What belongs: trigger phrases, purpose, routing vs neighbors. Frontmatter `type: skill`.
- **Config** — harness mechanics and their current values. What belongs: settings, hooks, MCP wiring, memory, loading rules. Frontmatter `type: config`.
- **Decisions** — settled choices with their why. What belongs: date, what was kept/cut, rationale, how to apply. Frontmatter `type: decision`.

## Conventions

- Frontmatter on every wiki page: `type`, `updated`, `tags`; source pages add `raw: <exact raw filename>`.
- Links are `[[bare-page-name]]` — no paths, no `.md`.
- Contradiction flag, placed directly under the older claim:
  `> ⚠️ contradicts [[page]] — <one line on the conflict>`
- Citations: claims on entity/concept pages cite their source page: `([[source-page]])`.
- **Vault-specific:** the primary source is live inspection of `~/.claude` (settings.json, installed_plugins.json, skills/ tree, memory/). Pages note `source: live inspection <date>` in place of a `raw:` field. `raw/` stays available for clipped external docs (changelogs, plugin READMEs).

## Ingest workflow

Batch: file sources with minimal supervision; surface only contradictions or schema-changing findings.

## Evolution log

Free-form notes, newest first — not the log.md entry format.

- 2026-06-12 — schema created at init; initial population by live sweep of ~/.claude in the same session.
