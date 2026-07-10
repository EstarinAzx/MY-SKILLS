# ---------- search.py — ranked keyword search over an /llm-kb vault --------- #
"""
Depends on: stdlib only (math, os, re, sys, collections).
Data shapes: docs = {abs path: text} over wiki/**/* and raw/**/* (.md|.txt;
any assets/ dir pruned). score_docs returns [(score, path)] descending. Output:
top 10 as "score<TAB>relpath<TAB>first matching line"; exit 2 on usage error.
"""
import math
import os
import re
import sys
from collections import Counter

WORD = re.compile(r"[a-z0-9]+")
WIKILINK = re.compile(r"\[\[([^\]|#\n]+)")


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
                        with open(path, encoding="utf-8-sig", errors="ignore") as f:
                            docs[path] = f.read()
                    except OSError:
                        continue
    return docs


# ------------------------------ scoring ------------------------------------ #

# TF-IDF with sqrt length normalization — enough at personal-vault scale,
# deliberately not a real BM25 (no tuning knobs to maintain)
# (repeated query terms intentionally add weight)
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
    query_set = set(query_tokens)
    for line in text.splitlines():
        if query_set & set(tokenize(line)):
            return line.strip()[:120].replace("\t", " ")
    return ""


# ------------------------- registry & cross-vault -------------------------- #

# ~/.claude/vault-registry.txt, derived from this script's location so one
# registry serves every vault
def default_registry():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "vault-registry.txt"))


# vault paths from the registry — blank lines and # comments ignored
def load_registry(path):
    vaults = []
    try:
        with open(path, encoding="utf-8-sig", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    vaults.append(line)
    except OSError:
        pass
    return vaults


# search every registered vault and merge, each hit tagged "vault/relpath".
# per-vault IDF is local and merged by raw score — good enough at personal scale
def search_all(vaults, query):
    merged = []
    for vault in vaults:
        if not os.path.isdir(vault):
            continue
        tag = os.path.basename(os.path.normpath(vault))
        docs = collect_docs(vault)
        for score, path in score_docs(docs, query):
            relpath = os.path.relpath(path, vault).replace(os.sep, "/")
            merged.append((score, "%s/%s" % (tag, relpath), first_match_line(docs[path], query)))
    merged.sort(key=lambda r: (-r[0], r[1]))
    return merged


# ------------------------------ backlinks ---------------------------------- #

# wiki pages linking TO <page> via [[page]] (alias/heading suffix stripped,
# case-insensitive) — the inbound view that lint's orphan check cannot show
def backlinks(vault, page):
    target = page.strip().lower()
    hits = []
    for dirpath, dirs, files in os.walk(os.path.join(vault, "wiki")):
        dirs[:] = [d for d in dirs if d.lower() != "assets"]
        for name in sorted(files):
            if not name.lower().endswith(".md"):
                continue
            path = os.path.join(dirpath, name)
            try:
                with open(path, encoding="utf-8-sig", errors="ignore") as f:
                    text = f.read()
            except OSError:
                continue
            if any(t.strip().lower() == target for t in WIKILINK.findall(text)):
                hits.append(os.path.relpath(path, vault).replace(os.sep, "/"))
    return sorted(hits)


# --------------------------------- main ------------------------------------ #

def main(argv):
    # piped stdout on Windows defaults to cp1252 — unicode snippets must not crash
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # --all <terms...> — federated search across every registered vault
    if len(argv) >= 2 and argv[1] == "--all":
        if len(argv) < 3:
            print("usage: search.py --all <query terms...>", file=sys.stderr)
            return 2
        vaults = load_registry(default_registry())
        if not vaults:
            print("no vaults registered — add paths to %s" % default_registry(), file=sys.stderr)
            return 2
        for score, tagged, line in search_all(vaults, tokenize(" ".join(argv[2:])))[:10]:
            print("%.3f\t%s\t%s" % (score, tagged, line))
        return 0

    # --backlinks <vault> <page> — pages linking to a given page
    if len(argv) >= 2 and argv[1] == "--backlinks":
        if len(argv) != 4 or not os.path.isdir(argv[2]):
            print("usage: search.py --backlinks <vault-dir> <page-name>", file=sys.stderr)
            return 2
        for relpath in backlinks(argv[2], argv[3]):
            print(relpath)
        return 0

    # default: single-vault ranked search (original contract, unchanged)
    if len(argv) < 3 or not os.path.isdir(argv[1]):
        print("usage: search.py <vault-dir> <query terms...>", file=sys.stderr)
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
