# ---------- lint.py — structural health checks for an /llm-kb vault -------- #
"""
Depends on: stdlib only (os, re, sys, collections).
Data shapes: Issue = namedtuple(category, location, detail). A vault is a dir
holding SCHEMA.md, index.md, log.md, raw/, wiki/. Output: one issue per line
as "category<TAB>location<TAB>detail"; exit 0 clean, 1 issues, 2 usage error.
"""
import datetime
import os
import re
import sys
from collections import namedtuple

Issue = namedtuple("Issue", "category location detail")

WIKILINK = re.compile(r"\[\[([^\]|#\n]+)")
LOG_HEADER = re.compile(r"^## \[\d{4}-\d{2}-\d{2}\] [\w-]+ \| .+$")
RAW_FIELD = re.compile(r"^raw:\s*(.+)$", re.MULTILINE)
UPDATED = re.compile(r"^updated:\s*(\d{4})-(\d{2})-(\d{2})", re.MULTILINE)


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


# ------------------------------ staleness ---------------------------------- #

# opt-in freshness pass (--stale): pages whose `updated:` date is older than
# max_age_days, and source pages whose immutable raw/ file was modified after
# the page derived from it. today is injectable so tests stay deterministic.
def stale_issues(vault, max_age_days, today=None):
    issues = []
    if today is None:
        today = datetime.date.today()
    for path, text in sorted(wiki_pages(vault).items()):
        m = UPDATED.search(text)
        if m:
            try:
                stamped = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except ValueError:
                stamped = None
            if stamped is not None:
                age = (today - stamped).days
                if age > max_age_days:
                    issues.append(Issue("stale", rel(vault, path),
                                        "updated %s, %dd old" % (stamped.isoformat(), age)))
        # raw source edited after the page = the page may no longer reflect it
        for raw_name in RAW_FIELD.findall(text):
            raw_path = os.path.join(vault, "raw", raw_name.strip())
            try:
                if os.path.getmtime(raw_path) > os.path.getmtime(path):
                    issues.append(Issue("source-newer", rel(vault, path),
                                        "raw/%s newer than page" % raw_name.strip()))
            except OSError:
                pass
    return issues


# --------------------------------- main ------------------------------------ #

# split argv into the one vault path and the optional `--stale [days]` flag
def parse_args(args):
    do_stale = False
    max_age = 90
    positional = []
    i = 0
    while i < len(args):
        if args[i] == "--stale":
            do_stale = True
            # a bare integer right after --stale overrides the 90-day default
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
        print("usage: lint.py <vault-dir> [--stale [days]]", file=sys.stderr)
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
