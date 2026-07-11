# ---- test_audit.py — fixture-driven checks for audit.py ------------------- #
"""
Depends on: stdlib only (os, sys, tempfile). Run with `python test_audit.py`;
prints "OK" and exits 0 on success, raises on the first failed assertion.

Data shapes: each test builds a throwaway ~/.claude tree under a TemporaryDirectory
(skills/ + ecosystem-kb/), runs audit.collect_findings, and asserts on the
(category, location) pairs returned.
"""
import os
import sys
import tempfile

# import the module under test from the parent scripts/ dir
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import audit


# ------------------------------ fixture helper ----------------------------- #

# write text to <root>/<relpath>, creating parent dirs — the one primitive every
# test uses to lay down skill folders and vault pages
def make(root, relpath, text=""):
    path = os.path.join(root, relpath.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def cats(findings):
    return {(f.category, f.location) for f in findings}


# --------------------------------- tests ----------------------------------- #

# every category fires exactly where expected, and the noise cases stay silent
def test_all_categories():
    with tempfile.TemporaryDirectory() as root:
        # a stray folder: no SKILL.md, no plugin manifest
        make(root, "skills/junk/notes.txt", "hi")
        # a silent plugin auto-load
        make(root, "skills/plug/.claude-plugin/plugin.json", "{}")
        # two skills colliding on name:
        make(root, "skills/a/SKILL.md", "---\nname: dup\n---\n")
        make(root, "skills/b/SKILL.md", "---\nname: dup\n---\n")
        # a skill the vault never mentions
        make(root, "skills/lonely/SKILL.md", "---\nname: lonely\n---\n")
        # a documented skill (named in index.md) must NOT be flagged
        make(root, "skills/known/SKILL.md", "---\nname: known\n---\n")
        # a dotfolder must be skipped entirely
        make(root, "skills/.hidden/x.txt", "x")

        # vault: documents `known`; asserts a missing path; history names another
        make(root, "ecosystem-kb/index.md", "- [[known]] — the known skill\n")
        make(root, "ecosystem-kb/wiki/skills/known.md",
             "page references ~/.claude/skills/ghost/ which is gone\n")
        # these live in history-only files and must be IGNORED by stale-path
        make(root, "ecosystem-kb/wiki/decisions/old.md",
             "removed ~/.claude/skills/buried/ in the purge\n")
        make(root, "ecosystem-kb/log.md", "renamed ~/.claude/skills/former/ to x\n")

        got = cats(audit.collect_findings(root))

        assert ("stray-folder", "skills/junk") in got
        assert ("plugin-autoload", "skills/plug") in got
        assert ("name-collision", "a, b") in got
        assert ("vault-undocumented", "skills/lonely") in got
        assert ("vault-stale-path", "ecosystem-kb") in got
        # negatives
        assert not any(loc == "skills/.hidden" for _c, loc in got)
        assert ("vault-undocumented", "skills/known") not in got
        # stale-path must not fire on the decisions/ or log.md history refs
        ghosts = {f.detail for f in audit.collect_findings(root)
                  if f.category == "vault-stale-path"}
        assert any("ghost" in d for d in ghosts)
        assert not any("buried" in d or "former" in d for d in ghosts)


# the universal CLAUDE.md's slash commands must resolve to skills; /preset args
# to preset files. Path-like slashes (.context/flows.md, ~/.claude/...) are noise
def test_claude_md_refs():
    with tempfile.TemporaryDirectory() as root:
        make(root, "skills/trace/SKILL.md", "---\nname: trace\n---\n")
        make(root, "skills/preset/SKILL.md", "---\nname: preset\n---\n")
        make(root, "skills/preset/presets/wrap-up.md", "# wrap-up\n")
        make(root, "ecosystem-kb/index.md", "- [[trace]] x\n- [[preset]] x\n")
        make(root, "template/IN USE/CLAUDE.md",
             "run `/trace` and `/preset wrap-up` and `/preset ghost-preset`\n"
             "also `/vanished` should flag\n"
             "noise: `.context/flows.md` and `~/.claude/template/IN USE/CLAUDE.md`\n"
             "and wiki/syntheses/ecosystem-overview.md stay silent\n")

        got = audit.collect_findings(root)
        details = {f.detail for f in got if f.category == "claude-md-stale-ref"}

        assert any("/vanished" in d for d in details)
        assert any("ghost-preset" in d for d in details)
        # live refs and path noise must not fire
        assert not any("/trace" in d for d in details)
        assert not any("wrap-up" in d for d in details)
        assert not any("flows" in d or "template" in d or "syntheses" in d
                       for d in details)


# a fully consistent tiny tree produces zero findings
def test_clean_tree():
    with tempfile.TemporaryDirectory() as root:
        make(root, "skills/solo/SKILL.md", "---\nname: solo\n---\n")
        make(root, "ecosystem-kb/index.md", "- [[solo]] — only skill\n")
        assert audit.collect_findings(root) == []


if __name__ == "__main__":
    test_all_categories()
    test_claude_md_refs()
    test_clean_tree()
    print("OK")
