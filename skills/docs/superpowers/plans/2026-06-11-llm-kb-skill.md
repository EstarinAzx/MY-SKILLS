# /llm-kb Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `/llm-kb` skill — a subcommand dispatcher that turns any folder into a personal, Obsidian-compatible LLM-maintained wiki vault with init/ingest/query/lint operations and two deterministic stdlib-only helper scripts.

**Architecture:** Thin SKILL.md router (house preset/ pattern) delegating to four op files under `ops/`; a TEMPLATE.md that init turns into each vault's SCHEMA.md; `scripts/lint.py` (structural checks) and `scripts/search.py` (ranked keyword search) shared by all vaults, tested with stdlib `unittest`. No hooks, no background processes, no LLM calls outside the live session.

**Tech Stack:** Markdown skill files; Python 3 stdlib only (os, re, sys, math, collections, tempfile, unittest). No pip dependencies, no venv.

**Spec:** `docs/superpowers/specs/2026-06-11-llm-kb-design.md` (repo path `skills/docs/superpowers/specs/`).

**Repo layout note:** The git repo root is `C:\Users\S.D\.claude`; the working directory is `C:\Users\S.D\.claude\skills`. All paths below are relative to the working directory unless absolute. Commits run from the working directory; staged paths resolve inside the repo automatically.

---

## File structure

| File | Responsibility |
|---|---|
| `llm-kb/SKILL.md` | Frontmatter triggers + routing table + vault resolution + hard rules + house format |
| `llm-kb/TEMPLATE.md` | Starting SCHEMA.md handed to new vaults (placeholders filled at init) |
| `llm-kb/ops/init.md` | Bootstrap a vault: domain questions → SCHEMA.md + index/log/dirs |
| `llm-kb/ops/ingest.md` | File one source (or batch) into the wiki: summary page, page updates, contradiction flags, index+log sync |
| `llm-kb/ops/query.md` | Index-first retrieval, search.py fallback, file answers back as syntheses |
| `llm-kb/ops/lint.md` | Structural pass via lint.py + semantic pass in-session |
| `llm-kb/scripts/lint.py` | Deterministic checks: broken links, orphans, index drift, frontmatter, log format, uningested raw |
| `llm-kb/scripts/search.py` | TF-IDF keyword ranking over wiki/ + raw/ markdown |
| `llm-kb/scripts/tests/test_lint.py` | unittest coverage for every lint category |
| `llm-kb/scripts/tests/test_search.py` | unittest coverage for tokenizing, ranking, no-hit |

---

### Task 1: Skill dispatcher (SKILL.md)

**Files:**
- Create: `llm-kb/SKILL.md`

- [ ] **Step 1: Write the file**

````markdown
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

Bare `/llm-kb`: if a vault is resolvable (see below) → show status: page count per `wiki/` subfolder, then the last 5 log entries (`Select-String '^## \[' <vault>\log.md | Select-Object -Last 5`). No vault → list the four ops, one line each.

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

Run with the vault path as first argument; one copy here serves every vault:

- `python "<this skill's dir>\scripts\search.py" <vault> <terms...>` — ranked keyword search. Use during query when index.md misses or the vault exceeds ~100 pages.
- `python "<this skill's dir>\scripts\lint.py" <vault>` — structural checks. Always the first step of the lint op.
````

- [ ] **Step 2: Verify frontmatter parses and file landed**

Run: `Select-String -Path llm-kb/SKILL.md -Pattern '^name: llm-kb'`
Expected: one match line.

- [ ] **Step 3: Commit**

```powershell
git add llm-kb/SKILL.md; git commit -m "feat(llm-kb): add skill dispatcher"
```

---

### Task 2: Vault schema template (TEMPLATE.md)

**Files:**
- Create: `llm-kb/TEMPLATE.md`

- [ ] **Step 1: Write the file**

`{{UPPERCASE}}` placeholders are filled by the init op — they are intentional here.

````markdown
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

- {{DATE}} — schema created at init.
````

- [ ] **Step 2: Verify placeholders present (init relies on them)**

Run: `(Select-String -Path llm-kb/TEMPLATE.md -Pattern '\{\{[A-Z_]+\}\}' -AllMatches).Matches.Count`
Expected: 8 (TOPIC ×2 in frontmatter+title, DATE ×2, MISSION, CATEGORY_DIRS, CATEGORIES, INGEST_STYLE).

- [ ] **Step 3: Commit**

```powershell
git add llm-kb/TEMPLATE.md; git commit -m "feat(llm-kb): add vault schema template"
```

---

### Task 3: init op

**Files:**
- Create: `llm-kb/ops/init.md`

- [ ] **Step 1: Write the file**

````markdown
# init — bootstrap a vault

Target directory: the path given as argument, else cwd. If `SCHEMA.md` already exists there, stop — say it is already a vault.

1. Ask (AskUserQuestion, one question block):
   - **Topic + mission** — what is this vault about, in one line?
   - **Kind** — book / research topic / personal tracking / other. Drives category presets:
     - book → `characters/`, `themes/`, `plot-threads/`
     - research → `claims/`, `methods/`, `people/`
     - personal → `goals/`, `observations/`, `experiments/`
     - other → propose 2-4 categories from the topic; confirm with the user.
   - **Ingest style** — interactive (discuss takeaways per source; default) or batch (file with minimal supervision).
2. Write `SCHEMA.md` from this skill's `TEMPLATE.md` with every `{{PLACEHOLDER}}` replaced by real values:
   - `{{CATEGORY_DIRS}}` → one bullet per chosen category dir with a one-line "what belongs here".
   - `{{CATEGORIES}}` → for each category: name, what belongs, its frontmatter `type` value (singular: `character`, `claim`, …).
   - `{{INGEST_STYLE}}` → the chosen style, one sentence.
   - Verify zero `{{` remain in the written file.
3. Create:
   - `index.md` — frontmatter (`type: index`, `updated: <today>`), `# Index`, one `## <Category>` heading per category (including Sources and Syntheses), each section empty.
   - `log.md` — frontmatter (`type: log`), then `## [<today>] init | <topic>`.
   - Directories: `raw/`, `raw/assets/`, `wiki/sources/`, `wiki/syntheses/`, and one `wiki/<category>/` per chosen category.
4. Tell the user: drop sources into `raw/` (Obsidian Web Clipper works well; vault opens directly in Obsidian), then run `/llm-kb ingest <file|all>`. Mention `git init` is optional and theirs to manage.
````

- [ ] **Step 2: Verify**

Run: `Select-String -Path llm-kb/ops/init.md -Pattern 'TEMPLATE.md'`
Expected: one match (init references the template).

- [ ] **Step 3: Commit**

```powershell
git add llm-kb/ops/init.md; git commit -m "feat(llm-kb): add init op"
```

---

### Task 4: ingest op

**Files:**
- Create: `llm-kb/ops/ingest.md`

- [ ] **Step 1: Write the file**

````markdown
# ingest — file a source into the wiki

Read the vault's `SCHEMA.md` first. It may override anything below.

## Resolve targets

- `ingest <file>` → that file in `raw/` (accept bare name with or without extension).
- `ingest all` → every `raw/*.md` and `raw/*.txt` not referenced by a `raw:` frontmatter field in any `wiki/sources/` page. List the targets and count before starting.

## Per source

1. Read the source fully. If it references images present in `raw/assets/`, view the few that carry information (charts, diagrams) — text first, images second.
2. **Interactive mode** (default unless SCHEMA.md or the user says batch): present 3-7 key takeaways as bullets and ask what to emphasize or skip. Batch mode skips the discussion.
3. Write `wiki/sources/<slug>.md`:

   ```markdown
   ---
   type: source
   raw: <exact raw filename>
   updated: <today>
   tags: [<2-4 tags>]
   ---

   # <Source title>

   <One-paragraph summary.>

   ## Key claims
   - <claim, wikilinking every entity/concept it touches> ([[wikilinks]])
   ```

4. Update or create every touched page in the SCHEMA.md categories: append new facts in the relevant section with a `([[<source page>]])` citation. One source touching 10-15 pages is normal; fewer is fine for a thin source. New pages get the category's frontmatter `type`, get added to `index.md`, and must be wikilinked from at least one other page (the source page counts).
5. **Contradiction rule** — never silently overwrite. When a new claim conflicts with an existing page claim, add directly under the older claim:

   ```markdown
   > ⚠️ contradicts [[<new source page>]] — <one line on the conflict>
   ```

   and surface it in the wrap-up.
6. Update `index.md`: new pages under their category with a one-line summary; refresh one-liners that changed.
7. Append to `log.md`:

   ```markdown
   ## [<today>] ingest | <source title>
   - pages touched: [[a]], [[b]], …
   - contradictions flagged: <n or none>
   ```

## Wrap-up (once per batch)

One short report: sources filed, pages created/updated, contradictions flagged, and at most 3 suggested follow-up questions.
````

- [ ] **Step 2: Verify**

Run: `Select-String -Path llm-kb/ops/ingest.md -Pattern 'contradicts'`
Expected: 2 matches (rule + flag template).

- [ ] **Step 3: Commit**

```powershell
git add llm-kb/ops/ingest.md; git commit -m "feat(llm-kb): add ingest op"
```

---

### Task 5: query op

**Files:**
- Create: `llm-kb/ops/query.md`

- [ ] **Step 1: Write the file**

````markdown
# query — answer from the wiki

1. Read the vault's `SCHEMA.md`, then `index.md`.
2. Pick relevant pages from the index and read only those. If the index gives no clear hit, or the vault exceeds ~100 pages, run instead:

   ```powershell
   python "<this skill's dir>\scripts\search.py" <vault> <key terms>
   ```

   and read the top hits.
3. Answer in chat with a `[[page]]` citation on every claim. State what the wiki does NOT cover rather than padding the answer.
4. If the answer produced new synthesis (a comparison, a connection, an analysis — not a plain lookup), offer once to file it back as `wiki/syntheses/<slug>.md`. On yes: write the page (frontmatter `type: synthesis`, `updated`, `tags`), add it to `index.md`, and append to `log.md`:

   ```markdown
   ## [<today>] query | <question>
   - filed: [[<synthesis page>]]
   ```

   Explorations compound in the wiki the same way sources do.
````

- [ ] **Step 2: Verify**

Run: `Select-String -Path llm-kb/ops/query.md -Pattern 'search.py'`
Expected: one match.

- [ ] **Step 3: Commit**

```powershell
git add llm-kb/ops/query.md; git commit -m "feat(llm-kb): add query op"
```

---

### Task 6: lint op

**Files:**
- Create: `llm-kb/ops/lint.md`

- [ ] **Step 1: Write the file**

````markdown
# lint — vault health check

1. Read the vault's `SCHEMA.md`.
2. **Structural pass** (deterministic, free):

   ```powershell
   python "<this skill's dir>\scripts\lint.py" <vault>
   ```

   Output lines are `category<TAB>location<TAB>detail`. Categories: `broken-link`, `no-frontmatter`, `not-in-index`, `index-dangling`, `orphan`, `log-format`, `uningested`. Exit 0 = clean.
3. **Semantic pass** (this session): read `index.md`, every page flagged above, and the 5 most recently updated wiki pages. Look for: contradictions between pages, claims superseded by newer sources, concepts mentioned on 3+ pages without their own page, and gaps worth a web search.
4. Report findings grouped by category, one line each with the proposed fix. Apply fixes only on approval — batch approval is fine. `raw/` is never "fixed" (immutable). `uningested` findings get `/llm-kb ingest` suggested, not an edit.
5. Append to `log.md`: `## [<today>] lint | <n> structural, <m> semantic findings`.
````

- [ ] **Step 2: Verify**

Run: `Select-String -Path llm-kb/ops/lint.md -Pattern 'lint.py'`
Expected: one match.

- [ ] **Step 3: Commit**

```powershell
git add llm-kb/ops/lint.md; git commit -m "feat(llm-kb): add lint op"
```

---

### Task 7: scripts/lint.py (TDD)

**Files:**
- Test: `llm-kb/scripts/tests/test_lint.py`
- Create: `llm-kb/scripts/lint.py`

- [ ] **Step 1: Confirm Python 3 available**

Run: `python --version`
Expected: `Python 3.x`. (If missing, stop and tell the user — the skill's scripts need a system Python 3, no packages.)

- [ ] **Step 2: Write the failing tests**

`llm-kb/scripts/tests/test_lint.py`:

```python
# ------------- test_lint.py — unit tests for vault lint checks ------------- #
"""
Depends on: stdlib only (os, sys, tempfile, unittest); lint.py via sys.path.
Data shapes: builds throwaway vault dirs per test; asserts on Issue namedtuples.
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lint


# ------------------------------ vault builder ------------------------------ #

# write a file inside the temp vault, creating parent dirs
def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class LintTests(unittest.TestCase):
    # fixture vault: alpha<->beta linked, ghost link broken, orphan.md unlinked
    # and missing frontmatter, index lists only alpha
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = self.tmp.name
        write(self.vault, "SCHEMA.md", "---\ntype: schema\n---\n# t\n")
        write(self.vault, "index.md", "---\ntype: index\n---\n# Index\n- [[alpha]] — a page\n")
        write(self.vault, "log.md", "---\ntype: log\n---\n## [2026-06-11] init | t\n")
        write(self.vault, "wiki/concepts/alpha.md", "---\ntype: concept\n---\nlinks [[beta]] and [[ghost]]\n")
        write(self.vault, "wiki/concepts/beta.md", "---\ntype: concept\n---\nback to [[alpha]]\n")
        write(self.vault, "wiki/concepts/orphan.md", "no frontmatter here\n")

    def tearDown(self):
        self.tmp.cleanup()

    def issues(self):
        return lint.collect_issues(self.vault)

    def test_broken_wikilink_flagged(self):
        self.assertTrue(any(i.category == "broken-link" and "ghost" in i.detail for i in self.issues()))

    def test_orphan_flagged(self):
        self.assertTrue(any(i.category == "orphan" and "orphan" in i.location for i in self.issues()))

    def test_missing_frontmatter_flagged(self):
        self.assertTrue(any(i.category == "no-frontmatter" and "orphan" in i.location for i in self.issues()))

    def test_pages_missing_from_index_flagged(self):
        issues = self.issues()
        self.assertTrue(any(i.category == "not-in-index" and "beta" in i.location for i in issues))
        self.assertTrue(any(i.category == "not-in-index" and "orphan" in i.location for i in issues))

    def test_index_dangling_link_flagged(self):
        write(self.vault, "index.md", "---\ntype: index\n---\n- [[alpha]]\n- [[vanished]]\n")
        self.assertTrue(any(i.category == "index-dangling" and "vanished" in i.detail for i in self.issues()))

    def test_malformed_log_entry_flagged(self):
        write(self.vault, "log.md", "---\ntype: log\n---\n## [bad date] init | x\n")
        self.assertTrue(any(i.category == "log-format" for i in self.issues()))

    def test_wellformed_log_entry_not_flagged(self):
        self.assertFalse(any(i.category == "log-format" for i in self.issues()))

    def test_uningested_raw_flagged_until_referenced(self):
        write(self.vault, "raw/clip.md", "an article\n")
        self.assertTrue(any(i.category == "uningested" and "clip.md" in i.location for i in self.issues()))
        write(self.vault, "wiki/sources/clip-source.md", "---\ntype: source\nraw: clip.md\n---\n# c\n[[alpha]]\n")
        self.assertFalse(any(i.category == "uningested" for i in self.issues()))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m unittest discover -s llm-kb/scripts/tests -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'lint'`.

- [ ] **Step 4: Write the implementation**

`llm-kb/scripts/lint.py`:

```python
# ---------- lint.py — structural health checks for an /llm-kb vault -------- #
"""
Depends on: stdlib only (os, re, sys, collections).
Data shapes: Issue = namedtuple(category, location, detail). A vault is a dir
holding SCHEMA.md, index.md, log.md, raw/, wiki/. Output: one issue per line
as "category<TAB>location<TAB>detail"; exit 0 clean, 1 issues, 2 usage error.
"""
import os
import re
import sys
from collections import namedtuple

Issue = namedtuple("Issue", "category location detail")

WIKILINK = re.compile(r"\[\[([^\]|#]+)")
LOG_HEADER = re.compile(r"^## \[\d{4}-\d{2}-\d{2}\] [\w-]+ \| .+$")
RAW_FIELD = re.compile(r"^raw:\s*(.+)$", re.MULTILINE)


# ------------------------------ file helpers ------------------------------- #

# read a file, tolerating absence and bad bytes (lint must never crash)
def read(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


# map every wiki/**/*.md path to its text
def wiki_pages(vault):
    pages = {}
    for dirpath, _dirs, files in os.walk(os.path.join(vault, "wiki")):
        for name in files:
            if name.lower().endswith(".md"):
                path = os.path.join(dirpath, name)
                pages[path] = read(path)
    return pages


def rel(vault, path):
    return os.path.relpath(path, vault).replace(os.sep, "/")


# -------------------------------- checks ----------------------------------- #

# run every structural check; returns a flat, deterministic list of Issues
def collect_issues(vault):
    issues = []
    pages = wiki_pages(vault)
    base = {os.path.splitext(os.path.basename(p))[0].lower(): p for p in pages}
    inbound = {name: 0 for name in base}

    # broken links + frontmatter; count inbound links between wiki pages
    for path, text in sorted(pages.items()):
        for target in WIKILINK.findall(text):
            t = target.strip().lower()
            if t in base:
                if base[t] != path:
                    inbound[t] += 1
            else:
                issues.append(Issue("broken-link", rel(vault, path), "[[%s]]" % target.strip()))
        if not text.lstrip().startswith("---"):
            issues.append(Issue("no-frontmatter", rel(vault, path), "page has no YAML frontmatter"))

    # index drift, both directions
    index_targets = {t.strip().lower() for t in WIKILINK.findall(read(os.path.join(vault, "index.md")))}
    for name in sorted(base):
        if name not in index_targets:
            issues.append(Issue("not-in-index", rel(vault, base[name]), "page missing from index.md"))
    for name in sorted(index_targets - set(base)):
        issues.append(Issue("index-dangling", "index.md", "[[%s]] has no page" % name))

    # orphans — index.md is excluded on purpose: it lists everything by design,
    # so only links from other wiki pages count as "connected"
    for name, count in sorted(inbound.items()):
        if count == 0:
            issues.append(Issue("orphan", rel(vault, base[name]), "no inbound links from other wiki pages"))

    # log entry format
    for n, line in enumerate(read(os.path.join(vault, "log.md")).splitlines(), 1):
        if line.startswith("## ") and not LOG_HEADER.match(line):
            issues.append(Issue("log-format", "log.md:%d" % n, line.strip()))

    # raw sources never ingested (no source page claims them via raw: field)
    referenced = set()
    for text in pages.values():
        for m in RAW_FIELD.findall(text):
            referenced.add(m.strip().lower())
    raw_dir = os.path.join(vault, "raw")
    if os.path.isdir(raw_dir):
        for name in sorted(os.listdir(raw_dir)):
            if name.lower().endswith((".md", ".txt")) and name.lower() not in referenced:
                issues.append(Issue("uningested", "raw/%s" % name, "no wiki/sources page references this file"))

    return issues


# --------------------------------- main ------------------------------------ #

def main(argv):
    if len(argv) != 2 or not os.path.isdir(argv[1]):
        print("usage: lint.py <vault-dir>")
        return 2
    issues = collect_issues(argv[1])
    for i in issues:
        print("%s\t%s\t%s" % i)
    print("%d issue(s)" % len(issues))
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m unittest discover -s llm-kb/scripts/tests -v`
Expected: `Ran 8 tests … OK`.

- [ ] **Step 6: Commit**

```powershell
git add llm-kb/scripts/lint.py llm-kb/scripts/tests/test_lint.py; git commit -m "feat(llm-kb): add deterministic vault lint script"
```

---

### Task 8: scripts/search.py (TDD)

**Files:**
- Test: `llm-kb/scripts/tests/test_search.py`
- Create: `llm-kb/scripts/search.py`

- [ ] **Step 1: Write the failing tests**

`llm-kb/scripts/tests/test_search.py`:

```python
# ---------- test_search.py — unit tests for vault keyword search ----------- #
"""
Depends on: stdlib only (os, sys, tempfile, unittest); search.py via sys.path.
Data shapes: throwaway vault per test; asserts on (score, path) ranking tuples.
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import search


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class SearchTests(unittest.TestCase):
    # fixture: dragons.md dense in "dragon", economy.md unrelated,
    # raw/clip.md mentions dragon once (raw must be searchable too)
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = self.tmp.name
        write(self.vault, "wiki/concepts/dragons.md", "dragon dragon dragon fire wings\n")
        write(self.vault, "wiki/concepts/economy.md", "trade gold market caravan\n")
        write(self.vault, "raw/clip.md", "a dragon appears once in this clip\n")
        write(self.vault, "raw/assets/pic.md", "dragon dragon dragon dragon\n")

    def tearDown(self):
        self.tmp.cleanup()

    def rank(self, query):
        docs = search.collect_docs(self.vault)
        return [os.path.basename(p) for _s, p in search.score_docs(docs, search.tokenize(query))]

    def test_tokenize_lowercases_and_splits(self):
        self.assertEqual(search.tokenize("Dragon-Fire 99!"), ["dragon", "fire", "99"])

    def test_ranks_dense_page_first(self):
        ranking = self.rank("dragon")
        self.assertEqual(ranking[0], "dragons.md")
        self.assertIn("clip.md", ranking)

    def test_no_hits_returns_empty(self):
        self.assertEqual(self.rank("zebra"), [])

    def test_assets_dir_skipped(self):
        self.assertNotIn("pic.md", self.rank("dragon"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m unittest discover -s llm-kb/scripts/tests -v`
Expected: test_lint passes; test_search FAILS with `ModuleNotFoundError: No module named 'search'`.

- [ ] **Step 3: Write the implementation**

`llm-kb/scripts/search.py`:

```python
# ---------- search.py — ranked keyword search over an /llm-kb vault --------- #
"""
Depends on: stdlib only (math, os, re, sys, collections).
Data shapes: docs = {abs path: text} over wiki/**/*.md and raw/*.md|.txt
(raw/assets/ skipped). score_docs returns [(score, path)] descending. Output:
top 10 as "score<TAB>relpath<TAB>first matching line"; exit 2 on usage error.
"""
import math
import os
import re
import sys
from collections import Counter

WORD = re.compile(r"[a-z0-9]+")


def tokenize(text):
    return WORD.findall(text.lower())


# ------------------------------ corpus ------------------------------------- #

# gather searchable markdown/text under wiki/ and raw/ (assets are images)
def collect_docs(vault):
    docs = {}
    for root in (os.path.join(vault, "wiki"), os.path.join(vault, "raw")):
        for dirpath, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d.lower() != "assets"]
            for name in files:
                if name.lower().endswith((".md", ".txt")):
                    path = os.path.join(dirpath, name)
                    try:
                        with open(path, encoding="utf-8", errors="ignore") as f:
                            docs[path] = f.read()
                    except OSError:
                        continue
    return docs


# ------------------------------ scoring ------------------------------------ #

# TF-IDF with sqrt length normalization — enough at personal-vault scale,
# deliberately not a real BM25 (no tuning knobs to maintain)
def score_docs(docs, query_tokens):
    tfs = {p: Counter(tokenize(t)) for p, t in docs.items()}
    df = Counter()
    for tf in tfs.values():
        for term in set(tf):
            df[term] += 1
    results = []
    for path, tf in tfs.items():
        length = sum(tf.values()) or 1
        score = 0.0
        for term in query_tokens:
            if tf[term]:
                score += (tf[term] / math.sqrt(length)) * math.log(1 + len(docs) / df[term])
        if score > 0:
            results.append((score, path))
    results.sort(key=lambda r: (-r[0], r[1]))
    return results


def first_match_line(text, query_tokens):
    for line in text.splitlines():
        low = line.lower()
        if any(t in low for t in query_tokens):
            return line.strip()[:120]
    return ""


# --------------------------------- main ------------------------------------ #

def main(argv):
    if len(argv) < 3 or not os.path.isdir(argv[1]):
        print("usage: search.py <vault-dir> <query terms...>")
        return 2
    vault = argv[1]
    query = tokenize(" ".join(argv[2:]))
    docs = collect_docs(vault)
    for score, path in score_docs(docs, query)[:10]:
        print("%.3f\t%s\t%s" % (score, os.path.relpath(path, vault).replace(os.sep, "/"),
                                first_match_line(docs[path], query)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m unittest discover -s llm-kb/scripts/tests -v`
Expected: `Ran 12 tests … OK` (8 lint + 4 search).

- [ ] **Step 5: Commit**

```powershell
git add llm-kb/scripts/search.py llm-kb/scripts/tests/test_search.py; git commit -m "feat(llm-kb): add deterministic vault search script"
```

---

### Task 9: End-to-end smoke test on a scratch vault

**Files:**
- None created in repo (scratch vault in `$env:TEMP`, deleted after).

- [ ] **Step 1: Build a scratch vault with one deliberate broken link**

```powershell
$v = Join-Path $env:TEMP "llmkb-smoke"; Remove-Item -Recurse -Force $v -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force "$v/wiki/concepts" | Out-Null; New-Item -ItemType Directory -Force "$v/raw" | Out-Null
Set-Content -Encoding utf8 "$v/SCHEMA.md" "---`ntype: schema`n---`n# smoke"
Set-Content -Encoding utf8 "$v/index.md" "---`ntype: index`n---`n- [[alpha]]"
Set-Content -Encoding utf8 "$v/log.md" "---`ntype: log`n---`n## [2026-06-11] init | smoke"
Set-Content -Encoding utf8 "$v/wiki/concepts/alpha.md" "---`ntype: concept`n---`ndragons breathe fire [[missing-page]]"
```

- [ ] **Step 2: Run lint.py against it**

Run: `python llm-kb/scripts/lint.py (Join-Path $env:TEMP "llmkb-smoke")`
Expected output includes: a `broken-link` line for `[[missing-page]]`, an `orphan` line for alpha (no inbound wiki links), final count line; exit code 1 (`$LASTEXITCODE` = 1).

- [ ] **Step 3: Run search.py against it**

Run: `python llm-kb/scripts/search.py (Join-Path $env:TEMP "llmkb-smoke") dragons`
Expected: one result line ranking `wiki/concepts/alpha.md` with the "dragons breathe fire" snippet; exit 0.

- [ ] **Step 4: Clean up scratch vault**

```powershell
Remove-Item -Recurse -Force (Join-Path $env:TEMP "llmkb-smoke")
```

- [ ] **Step 5: Final review and close-out commit**

Check `git status` shows no stray files under `llm-kb/` (no `__pycache__` — add ignore if present):

```powershell
git status --short llm-kb
```

If `__pycache__` appears, create `llm-kb/scripts/.gitignore` containing `__pycache__/` and commit:

```powershell
git add llm-kb/scripts/.gitignore; git commit -m "chore(llm-kb): ignore pycache"
```

---

## Self-review (done at write time)

- **Spec coverage:** dispatcher + bare-status (Task 1), TEMPLATE/SCHEMA co-evolution (Task 2), init with domain tuning (Task 3), ingest with contradiction flags + index/log sync (Task 4), query with index-first + search fallback + file-back (Task 5), lint two-pass (Task 6), deterministic scripts (Tasks 7-8), hard rules embedded in SKILL.md (Task 1). Migration section of spec already executed pre-plan. Non-goals respected: no hooks, no git automation, no extra output formats.
- **Placeholders:** `{{...}}` tokens appear only inside TEMPLATE.md content where they are the deliverable.
- **Type consistency:** `Issue(category, location, detail)` used identically in lint.py and both test files; `collect_docs`/`score_docs`/`tokenize` names match between search.py and test_search.py; category strings in ops/lint.md match lint.py exactly.
