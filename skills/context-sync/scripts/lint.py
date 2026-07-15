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
