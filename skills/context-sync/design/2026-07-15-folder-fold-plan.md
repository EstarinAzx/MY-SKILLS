# context-sync Folder-Fold Upgrade — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fold the two append-only `.context/` files (`decisions`, `gotchas`) into a thin-index + entry-folder shape and give context-sync a self-contained stdlib linter that catches index/entry drift.

**Architecture:** Each folded category is a root index file (`decisions.md`) that lists `[[wikilinks]]` to one-entry-per-file content in a sibling folder (`decisions/`). A standalone `scripts/lint.py` walks `.context/`, auto-detects folded pairs (root `X.md` + sibling `X/`), and reports broken links, orphans, index↔entry drift, and staleness. The skill's INIT/UPDATE/SKILL/FILE-TEMPLATES docs are updated to write and maintain this shape.

**Tech Stack:** Python 3 stdlib only (`os`, `re`, `datetime`, `collections`, `unittest`). Markdown skill docs. No third-party deps.

## Global Constraints

- Python **stdlib only** — no pip installs, no imports outside `os re datetime sys collections tempfile unittest`.
- Lint script is **self-contained** — zero import of or dependency on `llm-kb`'s scripts.
- Fold set is **fixed**: `decisions` + `gotchas` only. `history.md` and all bounded files stay flat.
- Output contract for lint: `category<TAB>location<TAB>detail` lines, trailing `N issue(s)`, exit `0` clean / `1` issues / `2` usage error.
- Wikilinks are `[[bare-name]]` (no `.md`, no path); Obsidian resolves by basename.
- Skill files live under `C:\Users\S.D\.claude\skills\context-sync\`. Repo root is `~/.claude` (default-deny `.gitignore`; only `/skills/` and `/ecosystem-kb/` are tracked).
- Commit messages: Conventional Commits.

---

### Task 1: Mini-lint script + tests

**Files:**
- Create: `skills/context-sync/scripts/lint.py`
- Test: `skills/context-sync/scripts/tests/test_lint.py`

**Interfaces:**
- Consumes: nothing (leaf).
- Produces:
  - `collect_issues(ctx: str) -> list[Issue]` where `Issue = namedtuple("Issue", "category location detail")`.
  - `stale_issues(ctx: str, max_age_days: int, today: datetime.date|None = None) -> list[Issue]`.
  - CLI: `python lint.py <context-dir> [--stale [days]]`.
  - Issue categories emitted: `broken-link`, `no-frontmatter`, `orphan`, `entry-not-indexed`, `index-dangling`, `stale`.

- [ ] **Step 1: Write the failing tests**

Create `skills/context-sync/scripts/tests/test_lint.py`:

```python
# tests for lint.py — one case per issue category plus a clean-vault baseline
import datetime
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import lint  # noqa: E402

FM = "---\ntype: t\nupdated: 2026-07-15\n---\n\n"


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# a lint-clean handoff dir: overview links every root file; decisions is a
# folded pair whose single entry is indexed and back-links its index
def make_clean(root):
    write(os.path.join(root, "overview.md"), FM + "# O\n[[active-work]] [[stack]] [[decisions]]\n")
    write(os.path.join(root, "active-work.md"), FM + "# A\n[[overview]]\n")
    write(os.path.join(root, "stack.md"), FM + "# S\n[[overview]]\n")
    write(os.path.join(root, "decisions.md"), FM + "# D\n[[2026-07-15-x]]\n[[overview]]\n")
    write(os.path.join(root, "decisions", "2026-07-15-x.md"), FM + "# X\n[[decisions]]\n")


class LintTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def cats(self, stale=None):
        issues = lint.collect_issues(self.tmp)
        if stale is not None:
            issues += lint.stale_issues(self.tmp, 90, today=stale)
        return [i.category for i in issues]

    def test_clean_is_zero(self):
        make_clean(self.tmp)
        self.assertEqual(self.cats(), [])

    def test_broken_link(self):
        make_clean(self.tmp)
        write(os.path.join(self.tmp, "stack.md"), FM + "# S\n[[overview]] [[nope]]\n")
        self.assertIn("broken-link", self.cats())

    def test_no_frontmatter(self):
        make_clean(self.tmp)
        write(os.path.join(self.tmp, "stack.md"), "# S no frontmatter\n[[overview]]\n")
        self.assertIn("no-frontmatter", self.cats())

    def test_orphan(self):
        make_clean(self.tmp)
        # a non-entry-point page nobody links to
        write(os.path.join(self.tmp, "lonely.md"), FM + "# L\n[[overview]]\n")
        self.assertIn("orphan", self.cats())

    def test_entry_not_indexed(self):
        make_clean(self.tmp)
        # a second entry the index does not link
        write(os.path.join(self.tmp, "decisions", "2026-07-14-y.md"), FM + "# Y\n[[decisions]]\n")
        self.assertIn("entry-not-indexed", self.cats())

    def test_index_dangling(self):
        make_clean(self.tmp)
        # the index links an entry file that does not exist
        write(os.path.join(self.tmp, "decisions.md"),
              FM + "# D\n[[2026-07-15-x]] [[2099-01-01-ghost]]\n[[overview]]\n")
        cats = self.cats()
        self.assertIn("index-dangling", cats)
        self.assertNotIn("broken-link", cats)  # a dead link inside an index is not a plain broken-link

    def test_stale(self):
        make_clean(self.tmp)
        # today far past every page's 2026-07-15 stamp -> all stale
        self.assertIn("stale", self.cats(stale=datetime.date(2027, 1, 1)))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest skills/context-sync/scripts/tests/test_lint.py -v` (or `python skills/context-sync/scripts/tests/test_lint.py`)
Expected: FAIL / ERROR — `ModuleNotFoundError: No module named 'lint'` (script not yet created).

- [ ] **Step 3: Write the implementation**

Create `skills/context-sync/scripts/lint.py`:

```python
# ---------------- lint.py — structural health checks for a .context/ handoff dir ------------ #
"""
Depends on: stdlib only (datetime, os, re, sys, collections).
Data shapes: pages = {abs path: text} over <ctx>/**/*.md (.obsidian, assets and
dot dirs pruned). A "folded pair" is a root file X.md with a sibling dir X/;
its entries are X/*.md. Output: one issue per line "category<TAB>location<TAB>
detail", trailing "N issue(s)"; exit 0 clean, 1 issues, 2 usage error.
"""
import datetime
import os
import re
import sys
from collections import namedtuple

Issue = namedtuple("Issue", "category location detail")

WIKILINK = re.compile(r"\[\[([^\]|#\n]+)")
UPDATED = re.compile(r"^updated:\s*(\d{4})-(\d{2})-(\d{2})", re.MULTILINE)

# files the next agent reads directly as kickoff — not expected to be linked-to
ENTRY_POINTS = {"overview", "active-work"}
PRUNE_DIRS = {".obsidian", "assets"}


# ------------------------------ file helpers ------------------------------- #

# read a file, tolerating absence and bad bytes (lint must never crash)
def read(path):
    try:
        with open(path, encoding="utf-8-sig", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def stem(path):
    return os.path.splitext(os.path.basename(path))[0].lower()


def rel(ctx, path):
    return os.path.relpath(path, ctx).replace(os.sep, "/")


# every .md under the handoff dir, pruning Obsidian/asset/dot dirs
def collect_pages(ctx):
    pages = {}
    for dirpath, dirs, files in os.walk(ctx):
        dirs[:] = [d for d in dirs if d.lower() not in PRUNE_DIRS and not d.startswith(".")]
        for name in files:
            if name.lower().endswith(".md"):
                path = os.path.join(dirpath, name)
                pages[path] = read(path)
    return pages


# ------------------------------ folded pairs ------------------------------- #

# a root file X.md with a sibling directory X/ is a folded category;
# returns {X_lower: (index_path, {entry_stem: entry_path})}
def folded_pairs(ctx, pages):
    pairs = {}
    for path in pages:
        if os.path.dirname(path) != ctx:  # index files live at the context root
            continue
        folder = os.path.join(ctx, stem(path))
        if os.path.isdir(folder):
            entries = {stem(p): p for p in pages if os.path.dirname(p) == folder}
            pairs[stem(path)] = (path, entries)
    return pairs


# -------------------------------- checks ----------------------------------- #

# run every structural check; returns a flat, deterministic list of Issues
def collect_issues(ctx):
    ctx = os.path.normpath(ctx)
    issues = []
    pages = collect_pages(ctx)
    base = {}
    for p in sorted(pages):
        base[stem(p)] = p
    pairs = folded_pairs(ctx, pages)
    index_paths = {ip for ip, _ in pairs.values()}
    inbound = {stem(p): 0 for p in pages}

    # broken links + frontmatter; count inbound links between pages.
    # a dead link inside a folded index is a dangling entry, not a plain break.
    for path, text in sorted(pages.items()):
        is_index = path in index_paths
        for target in WIKILINK.findall(text):
            t = target.strip().lower()
            if t in base:
                if base[t] != path:
                    inbound[t] += 1
            elif is_index:
                issues.append(Issue("index-dangling", rel(ctx, path), "[[%s]] has no entry" % target.strip()))
            else:
                issues.append(Issue("broken-link", rel(ctx, path), "[[%s]]" % target.strip()))
        if not text.lstrip().startswith("---"):
            issues.append(Issue("no-frontmatter", rel(ctx, path), "page has no YAML frontmatter"))

    # every entry file must be linked from its folder's index
    for name, (index_path, entries) in sorted(pairs.items()):
        linked = {x.strip().lower() for x in WIKILINK.findall(pages[index_path])}
        for est, epath in sorted(entries.items()):
            if est not in linked:
                issues.append(Issue("entry-not-indexed", rel(ctx, epath), "not linked from %s.md" % name))

    # orphans — entry points excluded (they are read directly, not linked-to)
    for name, count in sorted(inbound.items()):
        if count == 0 and name not in ENTRY_POINTS:
            issues.append(Issue("orphan", rel(ctx, base[name]), "no inbound links from other pages"))

    return issues


# ------------------------------ staleness ---------------------------------- #

# opt-in freshness pass (--stale): pages whose `updated:` date is older than
# max_age_days. today is injectable so tests stay deterministic.
def stale_issues(ctx, max_age_days, today=None):
    ctx = os.path.normpath(ctx)
    issues = []
    if today is None:
        today = datetime.date.today()
    for path, text in sorted(collect_pages(ctx).items()):
        m = UPDATED.search(text)
        if not m:
            continue
        try:
            stamped = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            continue
        age = (today - stamped).days
        if age > max_age_days:
            issues.append(Issue("stale", rel(ctx, path), "updated %s, %dd old" % (stamped.isoformat(), age)))
    return issues


# --------------------------------- main ------------------------------------ #

# split argv into the one context-dir path and the optional `--stale [days]`
def parse_args(args):
    do_stale = False
    max_age = 90
    positional = []
    i = 0
    while i < len(args):
        if args[i] == "--stale":
            do_stale = True
            if i + 1 < len(args) and args[i + 1].isdigit():
                max_age = int(args[i + 1])
                i += 1
        else:
            positional.append(args[i])
        i += 1
    return positional, do_stale, max_age


def main(argv):
    # piped stdout on Windows defaults to cp1252 — unicode details must not crash
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    positional, do_stale, max_age = parse_args(argv[1:])
    if len(positional) != 1 or not os.path.isdir(positional[0]):
        print("usage: lint.py <context-dir> [--stale [days]]", file=sys.stderr)
        return 2
    issues = collect_issues(positional[0])
    if do_stale:
        issues += stale_issues(positional[0], max_age)
    for i in issues:
        print("%s\t%s\t%s" % (i.category, i.location, i.detail.replace("\t", " ")))
    print("%d issue(s)" % len(issues))
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python skills/context-sync/scripts/tests/test_lint.py -v`
Expected: PASS — 7 tests OK.

- [ ] **Step 5: Smoke-test the CLI**

Run (Git Bash): build a tiny clean dir and lint it —
```bash
python skills/context-sync/scripts/lint.py skills/context-sync/scripts 2>/dev/null; echo "exit=$?"
```
Expected: prints `0 issue(s)` (the `scripts/` dir has no `.md`) and `exit=0`. Confirms arg parsing + clean exit.

- [ ] **Step 6: Commit**

```bash
git add skills/context-sync/scripts/lint.py skills/context-sync/scripts/tests/test_lint.py
git commit -m "feat(context-sync): add self-contained .context/ linter"
```

---

### Task 2: FILE-TEMPLATES.md — index + entry templates

**Files:**
- Modify: `skills/context-sync/FILE-TEMPLATES.md` (frontmatter enum ~line 13; replace the `decisions.md (initial)` block ~lines 185-206; add gotchas index + entry after it)
- Verify: build a scratch `.context/` from these templates, lint with Task 1 → 0 issues.

**Interfaces:**
- Consumes: Task 1's `lint.py` (for the verification step only).
- Produces: canonical templates `decisions.md` (index), `decisions/<entry>.md`, `gotchas.md` (index), `gotchas/<entry>.md` used by INIT and UPDATE.

- [ ] **Step 1: Extend the frontmatter `type:` enum**

In `FILE-TEMPLATES.md`, replace the enum line (currently):
```
type: overview | stack | active-work | decisions | api | frontend | backend | gotchas | code-map | history
```
with:
```
type: overview | stack | active-work | decisions-index | decision | api | frontend | backend | gotchas-index | gotcha | code-map | history
```

- [ ] **Step 2: Replace the `## decisions.md (initial)` section**

Replace the whole `## decisions.md (initial)` block with this folded pair:

````markdown
## decisions.md (folded index) + decisions/ entries

`decisions` is a **folded category**: a thin index at the root plus one file per
decision in `decisions/`. The index lists newest-first `[[wikilinks]]`; content
lives in the entries. This keeps the index scannable no matter how many
decisions accumulate.

**Index — `decisions.md`:**

```
---
type: decisions-index
project: <name>
updated: YYYY-MM-DD
tags: [context, decisions]
---

# Decisions

Settled questions. One file per decision in `decisions/`. Newest first.

<!-- one line per entry, newest at top -->
- [[2026-07-15-lift-hardcoded-16k]] — lift the hardcoded 16K Anthropic output cap

## Related

- [[overview]]
```

At `init` the list is empty (folder created lazily on the first entry). If
`docs/adr/` exists, add a line under the intro: `For substantial architectural
decisions prefer an ADR in \`docs/adr/\` and link it from an entry here.`

**Entry — `decisions/YYYY-MM-DD-<kebab-title>.md`:**

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

Slug rule: `YYYY-MM-DD-<kebab-title>.md` — the date prefix sorts entries
chronologically on disk; the kebab title is a unique, readable wikilink
basename. The `[[decisions]]` back-link keeps the entry non-orphan.
````

- [ ] **Step 3: Rewrite the `## gotchas.md` section as a folded pair**

Replace the existing `## gotchas.md (optional but high-value)` block with:

````markdown
## gotchas.md (folded index) + gotchas/ entries (optional but high-value)

`gotchas` folds the same way as `decisions`, but entries are not chronological,
so slugs carry no date. Each entry is one trap: what looks normal but isn't, why
it's load-bearing, and the rule to follow.

**Index — `gotchas.md`:**

```
---
type: gotchas-index
project: <name>
updated: YYYY-MM-DD
tags: [context, gotchas]
---

# Gotchas

Non-obvious traps. One file per trap in `gotchas/`. Group under area headings if
it helps; a flat list is fine.

- [[anthropic-empty-model-load-bearing]] — empty model field is required for Anthropic

## Related

- [[overview]]
```

**Entry — `gotchas/<kebab-trap>.md`:**

```
---
type: gotcha
project: <name>
updated: YYYY-MM-DD
tags: [context, gotchas, <area>]
---

# <short trap name>

**The trap:** <what looks normal but isn't>
**Why:** <root cause / constraint>
**Rule:** <what to do or not do>

## Related

- [[gotchas]] — index
- [[code-map]] — where the load-bearing code lives
```

Skip anything obvious from the code or already covered by an inline comment.
````

- [ ] **Step 4: Verify templates lint clean (end-to-end agreement)**

Build a scratch `.context/` populated from the new templates and lint it. Run in Git Bash:
```bash
D="$(mktemp -d)/.context"; mkdir -p "$D/decisions" "$D/gotchas"
printf -- '---\ntype: overview\nupdated: 2026-07-15\n---\n\n# Overview\n\n## Map\n- [[active-work]]\n- [[stack]]\n- [[decisions]]\n- [[gotchas]]\n' > "$D/overview.md"
printf -- '---\ntype: active-work\nupdated: 2026-07-15\n---\n\n# Active Work\n[[overview]]\n' > "$D/active-work.md"
printf -- '---\ntype: stack\nupdated: 2026-07-15\n---\n\n# Stack\n[[overview]]\n' > "$D/stack.md"
printf -- '---\ntype: decisions-index\nupdated: 2026-07-15\n---\n\n# Decisions\n- [[2026-07-15-lift-hardcoded-16k]]\n\n## Related\n- [[overview]]\n' > "$D/decisions.md"
printf -- '---\ntype: decision\nupdated: 2026-07-15\n---\n\n# X\n\n## Related\n- [[decisions]]\n' > "$D/decisions/2026-07-15-lift-hardcoded-16k.md"
printf -- '---\ntype: gotchas-index\nupdated: 2026-07-15\n---\n\n# Gotchas\n- [[anthropic-empty-model-load-bearing]]\n\n## Related\n- [[overview]]\n' > "$D/gotchas.md"
printf -- '---\ntype: gotcha\nupdated: 2026-07-15\n---\n\n# T\n\n## Related\n- [[gotchas]]\n' > "$D/gotchas/anthropic-empty-model-load-bearing.md"
python skills/context-sync/scripts/lint.py "$D"; echo "exit=$?"
```
Expected: `0 issue(s)` and `exit=0`. If any issue prints, the templates and linter disagree — fix the template (not the linter) unless the linter rule is wrong.

- [ ] **Step 5: Commit**

```bash
git add skills/context-sync/FILE-TEMPLATES.md
git commit -m "docs(context-sync): fold decisions/gotchas templates into index+entry"
```

---

### Task 3: INIT.md — always-fold bootstrap

**Files:**
- Modify: `skills/context-sync/INIT.md` (step 5 "Stub active-work.md and decisions.md" ~lines 57-60)

**Interfaces:**
- Consumes: Task 2's index templates.
- Produces: init behavior that writes folded indexes with empty lists and no empty folders.

- [ ] **Step 1: Rewrite step 5 to fold decisions + gotchas**

Replace the `### 5. Stub active-work.md and decisions.md` section with:

```markdown
### 5. Stub active-work.md and the folded indexes

Write `active-work.md` using the schema in [HANDOFF-FORMAT.md](HANDOFF-FORMAT.md), populated with `(no active work yet)` placeholders.

`decisions` and `gotchas` are **always folded** (a thin root index + a sibling entry folder). At init:

- Write `decisions.md` as the index template from [FILE-TEMPLATES.md](FILE-TEMPLATES.md) with an **empty** entry list. Do **not** create an empty `decisions/` folder — it is created lazily when the first entry is written on `update`. If `docs/adr/` exists, add the ADR-preference line noted in the template.
- If the project warrants `gotchas` (almost always does for non-trivial projects), write `gotchas.md` as its index template with an empty list; the `gotchas/` folder is likewise created on first entry.

Entry files (`decisions/<slug>.md`, `gotchas/<slug>.md`) are never written at init — there is nothing to record yet.
```

- [ ] **Step 2: Add a one-line pointer in step 4's Obsidian conventions**

In `### 4. Draft and write`, under the "Apply Obsidian conventions" bullets, append this bullet:
```markdown
- **Folded categories:** `decisions` and `gotchas` are written as a root index file plus a `[[wikilink]]` list into a sibling entry folder — see [FILE-TEMPLATES.md](FILE-TEMPLATES.md). The index is the wikilink target (`[[decisions]]`), so `overview.md`'s Map links to it unchanged.
```

- [ ] **Step 3: Verify internal consistency**

Run: `grep -n "decisions/" skills/context-sync/INIT.md`
Expected: the lazy-folder wording appears; no instruction to create an empty `decisions/` dir at init.

- [ ] **Step 4: Commit**

```bash
git add skills/context-sync/INIT.md
git commit -m "docs(context-sync): init always-folds decisions/gotchas (lazy folders)"
```

---

### Task 4: UPDATE.md — write-entry / prepend-index / lint / migration

**Files:**
- Modify: `skills/context-sync/UPDATE.md` (step 4 append-decision ~lines 30-50; step 5 gotchas bullet ~line 58; step 6 Report ~lines 71-78; add a migration subsection)

**Interfaces:**
- Consumes: Task 1's `lint.py`, Task 2's entry/index templates.
- Produces: the maintenance flow that keeps folded categories drift-free.

- [ ] **Step 1: Rewrite step 4 (append a decision) as the folded write**

Replace the `### 4. Append to decisions.md — only if warranted` section body (keep the "load-bearing decision" criteria) with:

````markdown
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
````

- [ ] **Step 2: Rewrite the gotchas bullet in step 5**

In `### 5. Update structural files only on actual structural change`, replace the `gotchas.md` bullet with:
```markdown
- For `gotchas`: append new traps discovered this session if genuinely non-obvious and not already covered by an inline code comment. `gotchas` is folded — write `gotchas/<kebab-trap>.md` from the entry template (back-linking `[[gotchas]]`), prepend a link line to `gotchas.md`, and bump the index `updated:`. Create the `gotchas/` folder on the first entry.
```

- [ ] **Step 3: Add the migration subsection (after step 5)**

Insert a new subsection before `### 6. Report`:

````markdown
### 5b. Migrate a legacy flat file — offer, don't force

If `decisions.md` is still a **flat monolith** (dated `## YYYY-MM-DD — …` blocks in the file, no `decisions/` folder) **and** it is actually long enough to hurt (roughly 10+ entries or past a few hundred lines), offer to fold it:

- Split each `## YYYY-MM-DD — <title>` block into `decisions/<date>-<kebab-title>.md` (entry template; the block body maps onto `Decision`/`Why`/`Reversibility`).
- Rewrite `decisions.md` as the index: newest-first link list + `## Related → [[overview]]`.
- Run lint (step 6) afterward to confirm no drift.

Do this only with the user's go-ahead, and never on a small file — a 3-entry `decisions.md` has nothing to fix and stays flat. Migrate `gotchas.md` the same way, splitting on `### <title>` blocks. This is the same "back-fill on touch" spirit as the frontmatter migration in step 5.
````

- [ ] **Step 4: Add the lint pass to step 6 (Report)**

In `### 6. Report`, add as the first action:
```markdown
- **Run lint:** `python "<this skill's dir>\scripts\lint.py" .context` (add `--stale` to also flag pages past 90 days). Surface any `broken-link` / `orphan` / `entry-not-indexed` / `index-dangling` lines in the report so drift is caught the moment it appears. A clean run prints `0 issue(s)`.
```

- [ ] **Step 5: Verify internal consistency**

Run: `grep -n "lint.py\|decisions/\|entry-not-indexed\|Migrate" skills/context-sync/UPDATE.md`
Expected: the folded-write steps, the lint pass, and the migration subsection are all present.

- [ ] **Step 6: Commit**

```bash
git add skills/context-sync/UPDATE.md
git commit -m "docs(context-sync): folded-write flow, lint pass, legacy migration"
```

---

### Task 5: SKILL.md — table, folded-folders note, reword, scripts mention

**Files:**
- Modify: `skills/context-sync/SKILL.md` (the "What lives in .context/" table ~lines 34-40; the "Vault-as-affordance" paragraph ~line 67; add a Folded-folders subsection and a Scripts mention)

**Interfaces:**
- Consumes: everything above (describes the finished shape).
- Produces: the skill's front-door description matching the new model.

- [ ] **Step 1: Update the canonical-files table**

In the `## What lives in .context/` table, replace the `decisions.md` row with:
```markdown
| `decisions.md` + `decisions/` | Settled questions a future agent shouldn't re-debate. **Folded:** thin index at root, one file per decision in `decisions/`. Append = new entry file + index link. |
```
And in the "Optional but high-value additions" list, replace the `gotchas.md` bullet with:
```markdown
- `gotchas.md` + `gotchas/` — non-obvious traps not visible in code or commits. **Folded** like `decisions`: index + one file per trap. Almost every non-trivial project has them.
```

- [ ] **Step 2: Reword the "no compile/query/lint ops" line**

Replace this sentence in the "Obsidian compatibility" section:
```
Vault-as-affordance, not as compiler. There is no `daily/`, no `knowledge/`, no compile/query/lint ops in this skill. `.context/` is a curated handoff map, not an accumulating wiki.
```
with:
```
Vault-as-affordance, not as compiler. `.context/` ships one deterministic **health check** — `scripts/lint.py` (broken links, orphans, index↔entry drift, staleness) — but no ingest, no query engine, no `SCHEMA.md`, no `log.md`. It stays a curated handoff map, not an accumulating wiki.
```

- [ ] **Step 3: Add a "Folded folders" subsection**

After the "What lives in .context/" section, insert:
````markdown
## Folded folders

Two categories accumulate without bound, so they fold from a single file into a
**thin index + entry folder** (the shape `llm-kb` uses for its wiki):

- `decisions.md` (index) + `decisions/YYYY-MM-DD-<slug>.md` (entries)
- `gotchas.md` (index) + `gotchas/<slug>.md` (entries)

The **index is the wikilink target** — `overview.md` still links `[[decisions]]`
unchanged, and it resolves to `decisions.md`. Entries back-link their index
(`[[decisions]]`) so they are never orphans. Recording an item is: write the
entry file, prepend one link line to the index. A 200-entry index is 200
scannable one-liners — not a 2000-line monolith.

Everything else stays a flat file: `overview`, `active-work`, `stack`, `api`,
`frontend`, `backend`, `code-map`, and `history` (a terse one-row-per-version
table that resists bloat on its own).
````

- [ ] **Step 4: Add a Scripts line to Boundaries**

In `## Boundaries`, add:
```markdown
- **Health check:** `scripts/lint.py` is stdlib-only and self-contained — it does not import or depend on `llm-kb`. Run it during `update`; it never runs on a hook or in the background.
```

- [ ] **Step 5: Verify consistency + full test suite still green**

Run:
```bash
grep -n "Folded\|lint.py\|decisions/" skills/context-sync/SKILL.md
python skills/context-sync/scripts/tests/test_lint.py
```
Expected: folded-folders wording present; tests still PASS (no code changed, sanity check).

- [ ] **Step 6: Commit**

```bash
git add skills/context-sync/SKILL.md
git commit -m "docs(context-sync): document folded folders + lint health check"
```

---

## Post-implementation (out of plan scope, tracked for the session)

Per the standing ecosystem rule, after the plan is executed: sync the ecosystem-kb vault (`wiki/skills/context-handoff.md`, index, log), mirror the change into the MY-SKILLS template, and run `/preset health` before any template push. These are ecosystem-maintenance steps, not part of the skill build itself.

## Self-Review

**Spec coverage:**
- Folded-folder model (index-file-as-face, slugs, entry/index shapes) → Task 2 (templates), Task 5 (SKILL doc). ✓
- Skill changes INIT/UPDATE/FILE-TEMPLATES/SKILL → Tasks 3/4/2/5. ✓
- Mini-lint (6 categories, contract, tests, self-contained) → Task 1. ✓
- Migration of legacy flat files via `/context-update` → Task 4 step 3. ✓
- YAGNI cuts (no search/SCHEMA/log/adaptive/forced-migration, history flat) → honored; no task adds them. ✓

**Placeholder scan:** No TBD/TODO. `<name>`/`<slug>`/`<topic>` are intended template tokens inside code fences, not plan gaps. Every code step shows complete content. ✓

**Type consistency:** `collect_issues(ctx)`, `stale_issues(ctx, max_age_days, today=None)`, `Issue(category, location, detail)`, categories `broken-link|no-frontmatter|orphan|entry-not-indexed|index-dangling|stale` — used identically in Task 1's implementation, its tests, and Task 4/5 doc references. `[[decisions]]`/`[[gotchas]]` as index wikilink targets consistent across Tasks 2-5. ✓
