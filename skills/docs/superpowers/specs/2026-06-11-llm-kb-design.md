# /llm-kb — Personal LLM Wiki Skill — Design

**Date:** 2026-06-11
**Status:** Approved (design + helper scripts; kb/ buried same day)
**Replaces:** `~/.claude/kb/` (Karpathy-inspired `llm-personal-kb`, now in `~/.claude/_deprecated/kb/`)

## Goal

A skill that turns any folder into a personal LLM-maintained wiki: a structured, interlinked collection of markdown pages the LLM builds and maintains from sources the user curates. The user sources, explores, and asks questions; the LLM does all summarizing, cross-referencing, filing, and bookkeeping. Knowledge is compiled once on ingest and kept current — not re-derived per query (the anti-RAG stance).

Pattern source: Karpathy's "LLM Wiki" idea file. Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.

## Background: kb/ post-mortem

The old kb/ failed because of **background LLM sessions**, not because of scripts: hooks (session-start/session-end/pre-compact) fired claude-agent-sdk calls invisibly, a flush daemon ran in the background, nightly auto-compile spent tokens unattended, and state files (state.json, last-flush.json) accumulated. It also captured *conversations*, which the user did not want as the input stream.

/llm-kb inverts every one of those choices: manual invocation only, external sources as input, zero hooks, zero background processes, zero LLM calls outside the live session.

## Decisions made

| Question | Decision |
|---|---|
| Relationship to kb/ | Replace it; skill named `/llm-kb`; kb/ moved to `_deprecated/` |
| Vault layout | Per-topic vaults, anywhere — skill is the pattern, any folder becomes an instance |
| Invocation | Subcommand dispatcher: `/llm-kb init\|ingest\|query\|lint` (preset/ house pattern) |
| Machinery | Helper scripts included from day one — deterministic only, no LLM calls, no background |

## Skill structure

```
~/.claude/skills/llm-kb/
  SKILL.md          thin router: parse subcommand → read matching op file → execute
  ops/
    init.md         bootstrap a vault in cwd (or a given path)
    ingest.md       file one source (or batch) into the wiki
    query.md        answer from the wiki; offer to file the answer back
    lint.md         health-check a vault
  scripts/
    search.py       ranked keyword search over a vault (stdlib only)
    lint.py         structural checks: links, orphans, index drift (stdlib only)
  TEMPLATE.md       starting SCHEMA.md template handed to new vaults
```

Bare `/llm-kb`: if cwd is a vault (SCHEMA.md present) → show status (page count, category counts, last 5 log entries via `log.md` tail); otherwise list the four ops.

## Vault anatomy

Created by `/llm-kb init`:

```
<topic>/
  SCHEMA.md     the vault's constitution — structure, conventions, ingest workflow,
                domain-specific page categories. Co-evolves with use. The skill
                reads SCHEMA.md FIRST on every operation and defers to it.
  index.md      content catalog: every page listed with link + one-line summary,
                grouped by category. Updated on every ingest. Read first on query.
  log.md        append-only timeline. Entry prefix format:
                ## [YYYY-MM-DD] <op> | <title>   (grep/Select-String parseable)
  raw/          immutable source documents. Obsidian Web Clipper target.
  raw/assets/   downloaded images for clipped articles.
  wiki/         LLM-owned pages:
    sources/      one summary page per ingested source
    entities/     people, places, products, characters — domain-tuned by SCHEMA.md
    concepts/     ideas, themes, claims
    syntheses/    overview, evolving thesis, comparisons, filed query answers
```

Page format (house convention, identical to .context/ family): YAML frontmatter (`type`, `updated`, `tags`; source pages add `raw:` with the exact raw filename) + `[[wikilinks]]` with no `.md` extension. (Amended at implementation: inline `([[source-page]])` citations replace a separate `sources` frontmatter field.) Every vault opens directly as an Obsidian vault with a working graph view. A vault may be `git init`-ed for history; the skill neither requires nor manages git.

`init` asks the topic plus 2-3 domain questions, then writes a SCHEMA.md *tuned to the domain* from TEMPLATE.md — a book vault gets characters/themes/plot-threads categories; a research vault gets papers/claims/thesis; a trip vault gets places/logistics/itinerary.

## Operations

**ingest** — user drops source into `raw/`, runs `/llm-kb ingest <file|all>`.
Flow per source: read it → discuss key takeaways with the user (interactive is the default; `all` batches with less supervision) → write `wiki/sources/<slug>.md` summary → update or create every touched entity/concept/synthesis page (one source legitimately touches 10-15 pages) → where new data contradicts an existing claim, flag inline on the page: `> ⚠️ contradicts [[page]] — <one line>` → update `index.md` → append `log.md`.

**query** — `/llm-kb query <question>` or natural language inside a vault.
Read `index.md` first, drill into only the relevant pages, synthesize an answer with `[[citations]]`. For vaults past ~100 pages (or on an index miss), run `scripts/search.py <vault> "<terms>"` instead of scanning. After answering, offer to file the answer back as a `wiki/syntheses/` page — explorations compound the same way sources do.

**lint** — `/llm-kb lint`.
Two passes. Structural (free, deterministic): run `scripts/lint.py <vault>` — broken wikilinks, orphan pages, pages missing from index, index entries with no file, missing frontmatter, malformed log entries. Semantic (LLM, in-session): contradictions between pages, claims superseded by newer sources, concepts mentioned often but lacking a page, gaps worth a web search. Report findings; fix on approval.

## Helper scripts

Both Python, **stdlib only** — no venv, no pyproject, no dependencies, nothing to maintain. Both take the vault path as first argument so one copy in the skill serves every vault; vaults themselves stay pure markdown.

- `search.py <vault> <query>` — tokenized keyword scoring (BM25-flavored TF-IDF) over `wiki/**/*.md` and `raw/*.md`; prints ranked `path — score — first matching line` for the LLM to drill into.
- `lint.py <vault>` — the structural checks listed under lint; prints `category<TAB>location<TAB>detail` lines plus a final count line; exit 0 when clean.

## Hard rules (written into SKILL.md)

1. **No hooks. No background processes. No LLM calls outside the live session.** The kb/ failure mode, permanently banned.
2. **raw/ is immutable** — the skill reads sources, never edits them.
3. **SCHEMA.md is per-vault law** — when SCHEMA.md and the skill's defaults disagree, SCHEMA.md wins. This is how each vault co-evolves with its domain.
4. **Scripts stay deterministic** — any future helper must make no network/LLM calls and run only when invoked in-session.
5. **Sync on every ingest** — index.md and log.md updated in the same pass as the pages, never deferred.

## Ecosystem fit

- **Standalone from `.context/`** — project handoff (context-sync/preset loop) is rolling per-repo state; vaults are accumulating per-topic knowledge. Different stores, same markdown conventions (frontmatter + wikilinks), both Obsidian-graphable.
- **Same house authoring style** — thin dispatcher SKILL.md + op files, mirroring preset/.
- **Complements** read-flow (codebase flows) and grill-with-docs (domain glossaries): those write into repos; /llm-kb writes into vaults.

## Migration (executed 2026-06-11)

- `~/.claude/kb/` → `~/.claude/_deprecated/kb/` — done.
- settings.json / settings.local.json checked: kb never wired hooks globally; nothing to strip — done.
- Old kb-* skill experiments already in `template/archive/` — left as-is.

## Non-goals

- No conversation capture (that was kb/; explicitly unwanted).
- No embeddings/RAG infrastructure; index-first + keyword search. qmd documented as a future escape hatch only if a vault outgrows search.py.
- No Marp/chart/canvas output formats in v1 — markdown pages only; formats can be added per-vault via SCHEMA.md later.
- No git automation inside vaults.
