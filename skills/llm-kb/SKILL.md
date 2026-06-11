---
name: llm-kb
description: Personal LLM wiki — turn any folder into a per-topic knowledge vault the LLM builds and maintains from sources the user curates. Use when user types /llm-kb [init|ingest|query|lint], says "ingest this article/paper/chapter", "start a wiki/vault for X", "ask the wiki", or "lint the vault". Vaults are Obsidian-compatible markdown (SCHEMA.md + index.md + log.md + raw/ + wiki/).
---

# /llm-kb — personal LLM wiki

You maintain per-topic wiki vaults. The user curates sources and asks questions; you do all summarizing, cross-referencing, filing, and bookkeeping. Knowledge is compiled once at ingest and kept current — never re-derived per query.

## Routing

`/llm-kb <subcommand> [args]` — read the matching op file in this skill's `ops/` directory and follow it:

| Subcommand | Op file |
|---|---|
| `init [path]` | `ops/init.md` |
| `ingest <file\|all>` | `ops/ingest.md` |
| `query <question>` | `ops/query.md` |
| `lint` | `ops/lint.md` |

Bare `/llm-kb`: if a vault is resolvable (see below) → show status: page count per `wiki/` subfolder, then the last 5 log entries (`Select-String '^## \[' "<vault>\log.md" | Select-Object -Last 5`). No vault → list the four ops, one line each.

Natural language maps to the same ops: "ingest/file this" → ingest; "what does the wiki say about…" → query; "health-check the vault" → lint; "start a wiki/vault" → init.

## Resolving the vault

The vault is the nearest directory at-or-above cwd containing `SCHEMA.md`, unless the user names a path. If no vault is found and the op is not `init`, say so and offer `/llm-kb init`.

## Hard rules

1. **No hooks, no background processes, no LLM calls outside this live session.** Never suggest them.
2. **raw/ is immutable** — read sources, never edit them.
3. **SCHEMA.md is vault law** — read it FIRST on every op; where it disagrees with the op files, SCHEMA.md wins. That is how each vault co-evolves with its domain.
4. **Scripts stay deterministic** — helpers in `scripts/` make no network or LLM calls and only run when invoked in-session.
5. **Sync every ingest** — index.md and log.md are updated in the same pass as the pages, never deferred.

## House format

Every wiki page: YAML frontmatter (`type`, `updated`, `tags`; source pages add `raw:` with the exact raw filename) + `[[wikilinks]]` using bare page names, no `.md`. Log entries: `## [YYYY-MM-DD] <op> | <title>`. Every vault opens directly as an Obsidian vault with a working graph view.

## Helper scripts

Run with the vault path as first argument; one copy here serves every vault. `<this skill's dir>` is the path printed as "Base directory for this skill" when this skill loads — use it verbatim, quoted:

- `python "<this skill's dir>\scripts\search.py" <vault> <terms...>` — ranked keyword search. Use during query when index.md misses or the vault exceeds ~100 pages.
- `python "<this skill's dir>\scripts\lint.py" <vault>` — structural checks. Always the first step of the lint op.
