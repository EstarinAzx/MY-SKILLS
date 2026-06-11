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

WIKILINK = re.compile(r"\[\[([^\]|#\n]+)")
LOG_HEADER = re.compile(r"^## \[\d{4}-\d{2}-\d{2}\] [\w-]+ \| .+$")
RAW_FIELD = re.compile(r"^raw:\s*(.+)$", re.MULTILINE)


# ------------------------------ file helpers ------------------------------- #

# read a file, tolerating absence and bad bytes (lint must never crash)
def read(path):
    try:
        with open(path, encoding="utf-8-sig", errors="ignore") as f:
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
    # sorted so duplicate stems across category dirs resolve deterministically
    base = {}
    for p in sorted(pages):
        base[os.path.splitext(os.path.basename(p))[0].lower()] = p
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

    # index drift, both directions (keep original casing for fixable output)
    index_links = {}
    for t in WIKILINK.findall(read(os.path.join(vault, "index.md"))):
        index_links.setdefault(t.strip().lower(), t.strip())
    for name in sorted(base):
        if name not in index_links:
            issues.append(Issue("not-in-index", rel(vault, base[name]), "page missing from index.md"))
    for name in sorted(set(index_links) - set(base)):
        issues.append(Issue("index-dangling", "index.md", "[[%s]] has no page" % index_links[name]))

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
    # piped stdout on Windows defaults to cp1252 — unicode details must not crash
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(argv) != 2 or not os.path.isdir(argv[1]):
        print("usage: lint.py <vault-dir>", file=sys.stderr)
        return 2
    issues = collect_issues(argv[1])
    for i in issues:
        print("%s\t%s\t%s" % (i.category, i.location, i.detail.replace("\t", " ")))
    print("%d issue(s)" % len(issues))
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
