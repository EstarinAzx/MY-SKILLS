# tests for lint.py — one case per issue category plus a clean-vault baseline
import datetime
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import lint  # noqa: E402

FM = "---\ntype: t\nupdated: 2026-07-15\n---\n\n"


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# a lint-clean handoff dir: overview links every root file; decisions is a
# folded pair whose single entry is indexed and back-links its index
def make_clean(root):
    write(os.path.join(root, "overview.md"), FM + "# O\n[[active-work]] [[stack]] [[decisions]]\n")
    write(os.path.join(root, "active-work.md"), FM + "# A\n[[overview]]\n")
    write(os.path.join(root, "stack.md"), FM + "# S\n[[overview]]\n")
    write(os.path.join(root, "decisions.md"), FM + "# D\n[[2026-07-15-x]]\n[[overview]]\n")
    write(os.path.join(root, "decisions", "2026-07-15-x.md"), FM + "# X\n[[decisions]]\n")


class LintTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def cats(self, stale=None):
        issues = lint.collect_issues(self.tmp)
        if stale is not None:
            issues += lint.stale_issues(self.tmp, 90, today=stale)
        return [i.category for i in issues]

    def test_clean_is_zero(self):
        make_clean(self.tmp)
        self.assertEqual(self.cats(), [])

    def test_broken_link(self):
        make_clean(self.tmp)
        write(os.path.join(self.tmp, "stack.md"), FM + "# S\n[[overview]] [[nope]]\n")
        self.assertIn("broken-link", self.cats())

    def test_no_frontmatter(self):
        make_clean(self.tmp)
        write(os.path.join(self.tmp, "stack.md"), "# S no frontmatter\n[[overview]]\n")
        self.assertIn("no-frontmatter", self.cats())

    def test_orphan(self):
        make_clean(self.tmp)
        # a non-entry-point page nobody links to
        write(os.path.join(self.tmp, "lonely.md"), FM + "# L\n[[overview]]\n")
        self.assertIn("orphan", self.cats())

    def test_entry_not_indexed(self):
        make_clean(self.tmp)
        # a second entry the index does not link
        write(os.path.join(self.tmp, "decisions", "2026-07-14-y.md"), FM + "# Y\n[[decisions]]\n")
        self.assertIn("entry-not-indexed", self.cats())

    def test_index_dangling(self):
        make_clean(self.tmp)
        # the index links an entry file that does not exist
        write(os.path.join(self.tmp, "decisions.md"),
              FM + "# D\n[[2026-07-15-x]] [[2099-01-01-ghost]]\n[[overview]]\n")
        cats = self.cats()
        self.assertIn("index-dangling", cats)
        self.assertNotIn("broken-link", cats)  # a dead link inside an index is not a plain broken-link

    def test_stale(self):
        make_clean(self.tmp)
        # today far past every page's 2026-07-15 stamp -> all stale
        self.assertIn("stale", self.cats(stale=datetime.date(2027, 1, 1)))


if __name__ == "__main__":
    unittest.main()
