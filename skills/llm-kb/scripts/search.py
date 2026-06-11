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


# --------------------------------- main ------------------------------------ #

def main(argv):
    # piped stdout on Windows defaults to cp1252 — unicode snippets must not crash
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
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
