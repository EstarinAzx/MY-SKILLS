---
type: schema
topic: {{TOPIC}}
updated: {{DATE}}
---

# {{TOPIC}} — vault schema

Mission: {{MISSION}}

This file is this vault's law. The LLM reads it first on every operation and defers to it over the skill's defaults. Evolve it as the domain teaches you what works; note changes in the Evolution log below.

## Layout

- `raw/` — immutable sources (Obsidian Web Clipper target). Never edited.
- `raw/assets/` — downloaded images for clipped articles.
- `wiki/` — LLM-owned pages; everything under it is written and maintained by the LLM.
- `wiki/sources/` — one summary page per ingested source.
- {{CATEGORY_DIRS}}
- `wiki/syntheses/` — overview, evolving thesis, comparisons, filed query answers.
- `index.md` — every page, one line each, grouped by category. Read first on query.
- `log.md` — append-only timeline: `## [YYYY-MM-DD] <op> | <title>`.

## Page categories

{{CATEGORIES}}

## Conventions

- Frontmatter on every wiki page: `type`, `updated`, `tags`; source pages add `raw: <exact raw filename>`.
- Links are `[[bare-page-name]]` — no paths, no `.md`.
- Contradiction flag, placed directly under the older claim:
  `> ⚠️ contradicts [[page]] — <one line on the conflict>`
- Citations: claims on entity/concept pages cite their source page: `([[source-page]])`.

## Ingest workflow

{{INGEST_STYLE}}

## Evolution log

Free-form notes, newest first — not the log.md entry format.

- {{DATE}} — schema created at init.
