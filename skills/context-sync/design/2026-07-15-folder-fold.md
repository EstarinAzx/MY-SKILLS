# context-sync folder-fold upgrade — design

**Date:** 2026-07-15
**Status:** approved (design), pending implementation plan
**Skill:** `~/.claude/skills/context-sync/`

## Problem

`.context/` handoff files are flat markdown. Append-only files — chiefly
`decisions.md` — grow without bound. Observed pain (2026-07-15 session): a
`/context-update` run had to read the *tail* of `decisions.md` just to place a
new entry without duplicating, because the file had grown long. The flat
append-only shape does not scale.

`llm-kb` already solved this exact shape: folder-per-category with one entry
per file, a thin index, and a deterministic linter. This upgrade borrows that
structure for the two `.context/` files that actually accumulate, without
importing llm-kb's full wiki apparatus (SCHEMA.md, log.md, raw/, ingest,
search) — context-sync stays a **handoff system**, not a knowledge wiki.

## Decisions (settled in brainstorm)

1. **Driver:** bloat + affordances — folders *and* a health-check affordance,
   not folders alone.
2. **Fold set:** `decisions` and `gotchas` only. Both are append-only and
   unbounded. `history.md` stays flat (it is a terse one-row-per-version table;
   folding it into per-version files is absurd). All rewritten/bounded files
   (`overview`, `active-work`, `stack`, `api`, `frontend`, `backend`,
   `code-map`) stay flat.
3. **Affordance = lint, not search.** Search (TF-IDF) is overkill at ~a dozen
   files; grep/Read already wins. Lint catches the failure mode folders newly
   introduce (index↔entry drift) plus dead wikilinks and staleness.
4. **Self-contained lint.** context-sync gets its own small stdlib linter, with
   **no dependency on llm-kb**. Rationale: context-sync and llm-kb are separate
   skills in the template/MY-SKILLS repo; a cross-skill script dependency would
   silently break context-sync when installed standalone or when llm-kb
   updates. Small logic overlap with llm-kb's lint is accepted for that
   independence.

## Design

### 1 — Folded-folder model (index-file-as-face)

Each folded category becomes **a thin index file at the `.context/` root plus a
folder of entry files**:

```
.context/
  overview.md        MOC — unchanged; still links [[decisions]] [[gotchas]]
  active-work.md     flat, unchanged (the handoff baton)
  stack.md / api.md / code-map.md / ...   flat, unchanged
  history.md         flat table, unchanged
  decisions.md       thin index: one link-line per entry, newest first
  decisions/
    2026-07-15-lift-hardcoded-16k.md
    2026-07-14-<slug>.md
  gotchas.md         thin index
  gotchas/
    anthropic-empty-model-load-bearing.md
```

**Why index-file-as-face** (not `decisions/_index.md`):

- Preserves existing `[[decisions]]` / `[[gotchas]]` wikilinks from
  `overview.md` — nothing else in `.context/` moves.
- Avoids Obsidian basename collision: two `_index.md` files (one per folder)
  resolve ambiguously under Obsidian's basename wikilink resolution.
- Keeps the append operation cheap: write `decisions/<slug>.md`, then prepend
  one link-line to `decisions.md`. A 200-entry index is 200 scannable
  one-liners, versus the 2000-line monolith being replaced.

**Slug conventions:**

- decisions: `YYYY-MM-DD-<kebab-title>.md` — date prefix makes filesystem sort
  chronological; kebab title gives a unique, readable basename for wikilinks.
- gotchas: `<kebab-trap>.md` — gotchas are not chronological, so no date prefix.

**Entry file shape** (decision):

```
---
type: decision
project: <name>
updated: YYYY-MM-DD
tags: [context, decisions, <topic>]
---

# <short title>

**Decision:** <what was decided>
**Why:** <the constraint or alternative considered>
**Reversibility:** easy | hard | one-way

## Related
- [[decisions]] — index
- [[<other entry or handoff file>]]
```

**Index file shape** (`decisions.md`):

```
---
type: decisions-index
project: <name>
updated: YYYY-MM-DD
tags: [context, decisions]
---

# Decisions

Settled questions. One file per decision in `decisions/`. Newest first.

- [[2026-07-15-lift-hardcoded-16k]] — lift hardcoded 16K Anthropic output cap
- [[2026-07-14-<slug>]] — <one-line title>

## Related
- [[overview]]
```

Gotchas mirror this: `type: gotcha` entries / `type: gotchas-index`; the index
may group links under area sub-headings (build, providers, persistence, …) when
that helps, but a flat newest-first list is the default.

### 2 — Skill file changes

- **INIT.md** — always-fold decisions + gotchas (the adaptive/graduate option
  was rejected). Init writes each thin index with an empty list; the folder is
  created lazily on the first real entry (no empty dirs committed to git).
- **UPDATE.md** — the "append a decision" step changes from *append a block to
  `decisions.md`* to: (a) write `decisions/<slug>.md` with the full entry; (b)
  prepend a one-line link to `decisions.md`; (c) bump the index `updated:`. Same
  for the gotchas step. The end of `update` **runs lint** (`python
  <skill>/scripts/lint.py .context`) and surfaces any issues in the Report
  step — cheap insurance against drift accumulating unseen.
- **FILE-TEMPLATES.md** — replace the flat `decisions.md` template with the
  index + entry templates; add the gotchas index + entry pair; extend the
  frontmatter `type:` enum with `decision`, `decisions-index`, `gotcha`,
  `gotchas-index`.
- **SKILL.md** — update the "what lives in .context/" table to show decisions
  and gotchas as folder+index; add a short "Folded folders" subsection
  (index-file-as-face, slug conventions); reword the current "vault-as-
  affordance, not as compiler … no compile/query/lint ops" line — lint is now a
  **health check, not a compiler** (still no ingest / query / SCHEMA.md /
  log.md); add a `scripts/` mention.

### 3 — Mini-lint (`context-sync/scripts/lint.py` + tests)

Stdlib-only, ~70 lines, self-contained (zero llm-kb dependency). Walks the
`.context/` root plus its folders, pruning `.obsidian`, `assets`, and dotdirs.
**Folded pairs are auto-detected**: a folder `X/` at the root with a sibling
`X.md` is a folded category — no config.

Checks:

| category | condition |
|---|---|
| `broken-link` | `[[x]]` where no `.md` in `.context/` has basename `x` |
| `no-frontmatter` | a `.md` file without a leading `---` block |
| `orphan` | an entry with no inbound wikilink from any other file — excludes `overview.md` and `active-work.md` (read directly as kickoff, not necessarily linked-to) |
| `entry-not-indexed` | `decisions/foo.md` exists but is not linked from `decisions.md` |
| `index-dangling` | `decisions.md` links `[[bar]]` but `decisions/bar.md` does not exist |
| `stale` (`--stale [days]`) | an entry whose `updated:` is older than N days (default 90) |

Output contract mirrors llm-kb's lint for operator familiarity:
`category<TAB>location<TAB>detail` lines, a trailing `N issue(s)`, exit `0`
clean / `1` issues / `2` usage error.

Tests: `scripts/tests/test_lint.py` — stdlib `unittest`, temp-dir fixtures, one
assertion per category firing plus a clean-vault-is-zero case.

### 4 — Migration of existing flat `.context/`

Migration is the **same-machine `/context-update` path** — there is no separate
migrate command and no bulk sweep.

On `update`, if `decisions.md` is still a flat monolith (decision blocks
present, no `decisions/` folder) **and** it is actually large, the skill
*offers* to migrate: split each `## YYYY-MM-DD — <title>` block into
`decisions/<date>-<slug>.md`, then rewrite `decisions.md` as the index. This is
on-the-fly and user-confirmed — the same spirit as the existing "back-fill
frontmatter on touch" migration already in UPDATE step 5. It is never forced on
a small file (a 3-entry `decisions.md` has nothing to fix and stays flat).
Gotchas migrate the same way, splitting on `### <title>` blocks.

Because skills are machine-global (`~/.claude/skills/context-sync`), upgrading
the skill once makes every project directory on this machine able to migrate
via `/context-update`. Only the `.context/` *data* is per-project. A project on
a different machine (or one that pulls skills from the MY-SKILLS template) does
not get the upgrade until the template is synced and re-dropped.

## Scope / YAGNI

Explicitly **out**:

- No search wiring (dropped as overkill).
- No SCHEMA.md, log.md, raw/, or ingest flow — context-sync is not becoming a
  wiki.
- No adaptive/graduate fold logic — the fold set is fixed (decisions + gotchas).
- No forced migration — offered on touch, only when bloated.
- `history.md` untouched.

## Post-build sync duty

Per the standing ecosystem rule: after implementation, sync the ecosystem-kb
vault ([[context-handoff]] page) and the MY-SKILLS template in the same session,
then run `/preset health` before any template push.
