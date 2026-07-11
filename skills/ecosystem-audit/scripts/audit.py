# ---- audit.py — deterministic health check for the ~/.claude ecosystem ---- #
"""
Depends on: stdlib only (os, re, sys, collections).

Data shapes:
  Finding = namedtuple(category, location, detail).
  A "skill folder" is any direct child of <root>/skills/ ; it is a loadable
  skill when it holds SKILL.md, and it silently auto-loads as a plugin when it
  holds .claude-plugin/ (the skills-dir footgun). The "vault" is the
  ecosystem-kb llm-kb vault at <root>/ecosystem-kb whose index.md + wiki/**/*.md
  are meant to map every skill.

Output: one finding per line as "category<TAB>location<TAB>detail", then a
count line; exit 0 clean, 1 findings, 2 usage error.

Categories:
  stray-folder       child of skills/ that is neither a skill nor a plugin
  plugin-autoload    child of skills/ with .claude-plugin/ (loads as <x>@skills-dir)
  name-collision     two skill folders declare the same `name:`
  vault-undocumented skill folder named nowhere in the ecosystem-kb vault
  vault-stale-path   a skills/<name>/ path written in the vault has no folder
  claude-md-stale-ref  the universal CLAUDE.md (template/IN USE) names a slash
                       command or /preset arg that no longer resolves
"""
import os
import re
import sys
from collections import namedtuple

Finding = namedtuple("Finding", "category location detail")

# `name:` on the first frontmatter line that has it; greedy-stop at EOL
NAME_FIELD = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
# a real .../claude/skills/<token>/ path reference (either slash). The claude/
# prefix is required so prose slash-lists like "skills/agents/MCP servers" in
# SCHEMA.md don't read as paths
SKILLS_PATH = re.compile(r"claude[\\/]skills[\\/]([A-Za-z0-9 _.-]+?)[\\/]")


# ------------------------------ file helpers ------------------------------- #

# read a file, tolerating absence and bad bytes (the audit must never crash)
def read(path):
    try:
        with open(path, encoding="utf-8-sig", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


# declared skill name from a SKILL.md body, or "" when none is present
def parse_name(text):
    m = NAME_FIELD.search(text)
    return m.group(1).strip() if m else ""


# ------------------------------ inventory ---------------------------------- #

# classify every direct child of skills/ — returns (skills, findings) where
# skills maps folder-name -> declared name, and findings holds the structural
# issues found while walking (stray folders, silent plugin auto-loads)
def scan_skills(skills_dir):
    skills = {}
    findings = []
    if not os.path.isdir(skills_dir):
        return skills, findings
    for entry in sorted(os.listdir(skills_dir)):
        folder = os.path.join(skills_dir, entry)
        # dotfolders (.claude, .git…) are config, never skills — never flag them
        if entry.startswith(".") or not os.path.isdir(folder):
            continue
        has_skill = os.path.isfile(os.path.join(folder, "SKILL.md"))
        has_plugin = os.path.isdir(os.path.join(folder, ".claude-plugin"))
        # .claude-plugin makes the folder load as a plugin with no registry
        # entry — surface it even when it is also a legit skill, since deleting
        # the folder is the only uninstall
        if has_plugin:
            findings.append(Finding("plugin-autoload", "skills/%s" % entry,
                                    "auto-loads as %s@skills-dir" % entry))
        if has_skill:
            skills[entry] = parse_name(read(os.path.join(folder, "SKILL.md")))
        elif not has_plugin:
            # no SKILL.md and no plugin manifest: not loadable, just clutter
            # sitting in the one directory that auto-loads its children
            findings.append(Finding("stray-folder", "skills/%s" % entry,
                                    "no SKILL.md — not a loadable skill"))
    return skills, findings


# duplicate `name:` across folders — two skills answering to one name collide
def name_collisions(skills):
    findings = []
    by_name = {}
    for folder, name in skills.items():
        if name:
            by_name.setdefault(name, []).append(folder)
    for name in sorted(by_name):
        folders = sorted(by_name[name])
        if len(folders) > 1:
            findings.append(Finding("name-collision", ", ".join(folders),
                                    "share name: %s" % name))
    return findings


# ------------------------------ vault checks ------------------------------- #

# concatenated lowercase text of the ecosystem-kb vault (index + every wiki
# page) — the corpus an audited skill must appear in to count as documented
def vault_corpus(vault):
    parts = [read(os.path.join(vault, "index.md"))]
    wiki = os.path.join(vault, "wiki")
    for dirpath, _dirs, files in os.walk(wiki):
        for name in sorted(files):
            if name.lower().endswith(".md"):
                parts.append(read(os.path.join(dirpath, name)))
    return "\n".join(parts).lower()


# skills present on disk but mentioned nowhere in the vault — map drift. Match
# on folder name OR declared name so family pages (one page, many skills) and
# folder!=name cases (elucidate-plugin -> elucidate) both count as documented
def undocumented(skills, corpus):
    findings = []
    for folder in sorted(skills):
        name = skills[folder]
        if folder.lower() not in corpus and (not name or name.lower() not in corpus):
            findings.append(Finding("vault-undocumented", "skills/%s" % folder,
                                    "named nowhere in ecosystem-kb"))
    return findings


# skills/<name>/ paths the vault asserts that no longer exist on disk — catches
# renames (e.g. a page still pointing at skills/read-flow/ after read-flow->trace).
# decisions/ and log.md are skipped: they narrate history, so they name removed
# paths on purpose — a missing path there is the record working, not drift
def stale_paths(vault, skills_dir):
    findings = []
    refs = set()
    for dirpath, _dirs, files in os.walk(vault):
        if os.path.basename(dirpath) == "decisions":
            continue
        for name in sorted(files):
            if name.lower().endswith(".md") and name != "log.md":
                for token in SKILLS_PATH.findall(read(os.path.join(dirpath, name))):
                    refs.add(token.strip())
    for token in sorted(refs):
        if not os.path.isdir(os.path.join(skills_dir, token)):
            findings.append(Finding("vault-stale-path", "ecosystem-kb",
                                    "skills/%s/ referenced but missing" % token))
    return findings


# ------------------------- universal CLAUDE.md check ----------------------- #

# a slash command in prose: slash preceded by line start / whitespace / backtick
# / paren — so path segments (.context/flows.md, ~/.claude/template/...) never match
SLASH_CMD = re.compile(r"(?:^|[\s`(])/([a-z][a-z0-9-]+)", re.MULTILINE)
PRESET_ARG = re.compile(r"/preset\s+([a-z][a-z0-9-]+)")


# the universal CLAUDE.md that getclaude drops into projects names slash
# commands and presets; nothing else checks that file, so silent staleness
# (a renamed skill or preset) surfaces only here
def claude_md_refs(root, skills):
    findings = []
    path = os.path.join(root, "template", "IN USE", "CLAUDE.md")
    text = read(path)
    if not text:
        return findings
    loc = "template/IN USE/CLAUDE.md"
    # resolvable = a skills/ folder name or any declared `name:` value
    known = set(skills) | {n for n in skills.values() if n}
    for cmd in sorted(set(SLASH_CMD.findall(text))):
        if cmd not in known:
            findings.append(Finding("claude-md-stale-ref", loc,
                                    "/%s resolves to no skills/ folder" % cmd))
    presets_dir = os.path.join(root, "skills", "preset", "presets")
    for arg in sorted(set(PRESET_ARG.findall(text))):
        if not os.path.isfile(os.path.join(presets_dir, arg + ".md")):
            findings.append(Finding("claude-md-stale-ref", loc,
                                    "/preset %s has no presets/%s.md" % (arg, arg)))
    return findings


# ------------------------------ orchestration ------------------------------ #

# run every check against a resolved ~/.claude root; deterministic flat list
def collect_findings(root):
    skills_dir = os.path.join(root, "skills")
    vault = os.path.join(root, "ecosystem-kb")
    skills, findings = scan_skills(skills_dir)
    findings += name_collisions(skills)
    findings += claude_md_refs(root, skills)
    if os.path.isdir(vault):
        corpus = vault_corpus(vault)
        findings += undocumented(skills, corpus)
        findings += stale_paths(vault, skills_dir)
    return sorted(findings)


# derive ~/.claude from this script's location (skills/ecosystem-audit/scripts)
# unless the caller names a root explicitly
def resolve_root(argv):
    if len(argv) >= 2:
        return argv[1]
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


# --------------------------------- main ------------------------------------ #

def main(argv):
    # piped stdout on Windows defaults to cp1252 — unicode details must not crash
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    root = resolve_root(argv)
    if not os.path.isdir(os.path.join(root, "skills")):
        print("usage: audit.py [claude-root]   (no skills/ under %s)" % root, file=sys.stderr)
        return 2
    findings = collect_findings(root)
    for f in findings:
        print("%s\t%s\t%s" % (f.category, f.location, f.detail.replace("\t", " ")))
    print("%d finding(s)" % len(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
