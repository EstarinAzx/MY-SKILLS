# -- test_template_sync.py — fixture-driven checks for template_sync.py ----- #
"""
Depends on: stdlib only (os, sys, tempfile). Run with
`python test_template_sync.py`; prints "OK" and exits 0 on success, raises on
the first failed assertion.

Data shapes: each test lays a throwaway root (skills/ + ecosystem-kb/ + a
template/IN USE mirror), runs collect_findings / apply_findings, and asserts
on (category, location) pairs.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import template_sync


# ------------------------------ fixture helper ----------------------------- #

def make(root, relpath, text=""):
    path = os.path.join(root, relpath.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def cats(findings):
    return {(f.category, f.location) for f in findings}


# --------------------------------- tests ----------------------------------- #

# every category fires where expected; CRLF-vs-LF alone is never drift
def test_detection():
    with tempfile.TemporaryDirectory() as root:
        tpl = "template/IN USE/"
        # common skill, drifted content
        make(root, "skills/a/SKILL.md", "new")
        make(root, tpl + "skills/a/SKILL.md", "old")
        # common skill, same text but CRLF in template — must stay silent
        make(root, "skills/same/SKILL.md", "x\ny\n")
        make(root, tpl + "skills/same/SKILL.md", "x\r\ny\r\n")
        # one-sided skills
        make(root, "skills/liveonly/SKILL.md", "l")
        make(root, tpl + "skills/tplonly/SKILL.md", "t")
        # vault: drift, live-only, template-only
        make(root, "ecosystem-kb/index.md", "new")
        make(root, tpl + "ecosystem-kb/index.md", "old")
        make(root, "ecosystem-kb/wiki/new-page.md", "n")
        make(root, tpl + "ecosystem-kb/wiki/dead-page.md", "d")

        got = cats(template_sync.collect_findings(root))
        assert got == {
            ("drift", "skills/a"),
            ("live-only", "skills/liveonly"),
            ("template-only", "skills/tplonly"),
            ("drift", "ecosystem-kb/index.md"),
            ("live-only", "ecosystem-kb/wiki/new-page.md"),
            ("template-only", "ecosystem-kb/wiki/dead-page.md"),
        }, got


# --apply mirrors drifted skills + the whole vault; curation findings remain
def test_apply():
    with tempfile.TemporaryDirectory() as root:
        tpl = "template/IN USE/"
        make(root, "skills/a/SKILL.md", "new")
        make(root, "skills/a/extra.md", "kept")
        make(root, tpl + "skills/a/SKILL.md", "old")
        make(root, tpl + "skills/a/stale.md", "must die")
        make(root, "skills/liveonly/SKILL.md", "l")
        make(root, "ecosystem-kb/index.md", "new")
        make(root, tpl + "ecosystem-kb/index.md", "old")
        make(root, "ecosystem-kb/wiki/new-page.md", "n")
        make(root, tpl + "ecosystem-kb/wiki/dead-page.md", "d")

        synced, remaining = template_sync.apply_findings(
            root, template_sync.collect_findings(root))
        # only the curation call is left for a human
        assert cats(remaining) == {("live-only", "skills/liveonly")}, remaining
        # clean replace: stale file gone, extra file arrived
        base = os.path.join(root, "template", "IN USE")
        assert not os.path.exists(os.path.join(base, "skills", "a", "stale.md"))
        assert os.path.exists(os.path.join(base, "skills", "a", "extra.md"))
        # vault mirrored fully, dead page deleted
        assert os.path.exists(os.path.join(base, "ecosystem-kb", "wiki", "new-page.md"))
        assert not os.path.exists(os.path.join(base, "ecosystem-kb", "wiki", "dead-page.md"))
        # a second pass is clean apart from the curation finding
        again = cats(template_sync.collect_findings(root))
        assert again == {("live-only", "skills/liveonly")}, again


if __name__ == "__main__":
    test_detection()
    test_apply()
    print("OK")
