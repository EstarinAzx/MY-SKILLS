# -- template_sync.py — live ~/.claude vs template/IN USE drift check + mirror -- #
"""
Depends on: stdlib only (os, shutil, sys, collections).

Data shapes:
  Finding = namedtuple(category, location, detail).
  The "live" side is <root>/skills and <root>/ecosystem-kb; the "template"
  side is the same two areas under <root>/template/IN USE (the copy pushed to
  the MY-SKILLS remote). A folder/file "snapshot" is {relpath: bytes} with
  newlines normalized, so git CRLF churn never reads as drift.

Mirror rules (asymmetric on purpose):
  skills/        curated — only folders present on BOTH sides are mirrored on
                 --apply; live-only folders are reported as candidates, never
                 auto-added; template-only folders are reported, never deleted.
  ecosystem-kb/  full mirror — the template vault carries every page, so
                 --apply copies drifted + live-only files and deletes
                 template-only ones.

Output: audit.py contract — "category<TAB>location<TAB>detail" lines then a
count line; exit 0 clean, 1 findings, 2 usage error. With --apply, applied
findings print as "synced<TAB>..." and don't count against the exit code.

Categories: drift, live-only, template-only.
"""
import os
import shutil
import sys
from collections import namedtuple

Finding = namedtuple("Finding", "category location detail")

TEMPLATE_REL = os.path.join("template", "IN USE")
# .obsidian is per-machine editor state, .claude is session-local state
# (settings.local.json, relay chain files) — never meaningful drift
IGNORED_DIRS = {"__pycache__", ".pytest_cache", ".git", ".obsidian", ".claude"}
IGNORED_SUFFIXES = (".pyc",)


# ------------------------------ snapshots ---------------------------------- #

# read one file as newline-normalized bytes; unreadable files become b"" so a
# permissions hiccup surfaces as drift, not a crash
def read_norm(path):
    try:
        with open(path, "rb") as f:
            return f.read().replace(b"\r\n", b"\n")
    except OSError:
        return b""


# walk base into {relpath: normalized bytes}, skipping caches and VCS innards
def snapshot(base):
    snap = {}
    for dirpath, dirs, files in os.walk(base):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRS)
        for name in sorted(files):
            if name.endswith(IGNORED_SUFFIXES):
                continue
            full = os.path.join(dirpath, name)
            snap[os.path.relpath(full, base).replace(os.sep, "/")] = read_norm(full)
    return snap


# ------------------------------ skills area -------------------------------- #

# compare skills/ folder-by-folder: drift on common folders, report-only for
# one-sided ones (the template's skill list is a deliberate curation)
def compare_skills(live_dir, tpl_dir):
    findings = []
    live = {d for d in os.listdir(live_dir)
            if os.path.isdir(os.path.join(live_dir, d)) and d not in IGNORED_DIRS} if os.path.isdir(live_dir) else set()
    tpl = {d for d in os.listdir(tpl_dir)
           if os.path.isdir(os.path.join(tpl_dir, d)) and d not in IGNORED_DIRS} if os.path.isdir(tpl_dir) else set()
    for name in sorted(live & tpl):
        if snapshot(os.path.join(live_dir, name)) != snapshot(os.path.join(tpl_dir, name)):
            findings.append(Finding("drift", "skills/" + name, "content differs from live"))
    for name in sorted(live - tpl):
        findings.append(Finding("live-only", "skills/" + name, "not in template — candidate to add"))
    for name in sorted(tpl - live):
        findings.append(Finding("template-only", "skills/" + name, "no live counterpart"))
    return findings


# mirror one drifted skill folder: clean replace so files deleted live die too
def apply_skill(live_dir, tpl_dir, name):
    dst = os.path.join(tpl_dir, name)
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(os.path.join(live_dir, name), dst,
                    ignore=shutil.ignore_patterns(*IGNORED_DIRS, "*.pyc"))


# ------------------------------ vault area --------------------------------- #

# compare ecosystem-kb file-by-file — the template vault is a full mirror
def compare_vault(live_kb, tpl_kb):
    findings = []
    live = snapshot(live_kb) if os.path.isdir(live_kb) else {}
    tpl = snapshot(tpl_kb) if os.path.isdir(tpl_kb) else {}
    for rel in sorted(live.keys() | tpl.keys()):
        loc = "ecosystem-kb/" + rel
        if rel in live and rel in tpl:
            if live[rel] != tpl[rel]:
                findings.append(Finding("drift", loc, "content differs from live"))
        elif rel in live:
            findings.append(Finding("live-only", loc, "missing from template"))
        else:
            findings.append(Finding("template-only", loc, "deleted live"))
    return findings


# mirror one vault finding: copy for drift/live-only, delete for template-only
def apply_vault(live_kb, tpl_kb, finding):
    rel = finding.location[len("ecosystem-kb/"):].replace("/", os.sep)
    dst = os.path.join(tpl_kb, rel)
    if finding.category == "template-only":
        try:
            os.remove(dst)
        except OSError:
            pass
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(os.path.join(live_kb, rel), dst)


# ------------------------------ orchestration ------------------------------ #

# full drift list for a resolved root; deterministic order
def collect_findings(root):
    tpl = os.path.join(root, TEMPLATE_REL)
    findings = compare_skills(os.path.join(root, "skills"), os.path.join(tpl, "skills"))
    findings += compare_vault(os.path.join(root, "ecosystem-kb"), os.path.join(tpl, "ecosystem-kb"))
    return sorted(findings)


# mirror everything mirrorable; returns (synced, remaining) finding lists.
# skills live-only/template-only stay remaining — curation is a human call
def apply_findings(root, findings):
    tpl = os.path.join(root, TEMPLATE_REL)
    synced, remaining = [], []
    for f in findings:
        if f.location.startswith("skills/") and f.category == "drift":
            apply_skill(os.path.join(root, "skills"), os.path.join(tpl, "skills"),
                        f.location[len("skills/"):])
            synced.append(f)
        elif f.location.startswith("ecosystem-kb/"):
            apply_vault(os.path.join(root, "ecosystem-kb"), os.path.join(tpl, "ecosystem-kb"), f)
            synced.append(f)
        else:
            remaining.append(f)
    return synced, remaining


# --------------------------------- main ------------------------------------ #

def resolve_root(args):
    if args:
        return args[0]
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = [a for a in argv[1:] if a != "--apply"]
    do_apply = "--apply" in argv[1:]
    root = resolve_root(args)
    if not os.path.isdir(os.path.join(root, TEMPLATE_REL)):
        print("usage: template_sync.py [claude-root] [--apply]   (no %s under %s)"
              % (TEMPLATE_REL, root), file=sys.stderr)
        return 2
    findings = collect_findings(root)
    if do_apply:
        synced, findings = apply_findings(root, findings)
        for f in synced:
            print("synced\t%s\t%s" % (f.location, f.detail.replace("\t", " ")))
    for f in findings:
        print("%s\t%s\t%s" % (f.category, f.location, f.detail.replace("\t", " ")))
    print("%d finding(s)" % len(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
