# ------------- test_lint.py — unit tests for vault lint checks ------------- #
"""
Depends on: stdlib only (contextlib, datetime, io, os, sys, tempfile, unittest); lint.py via sys.path.
Data shapes: builds throwaway vault dirs per test; asserts on Issue namedtuples.
"""
import contextlib
import datetime
import io
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lint


# ------------------------------ vault builder ------------------------------ #

# write a file inside the temp vault, creating parent dirs
def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class LintTests(unittest.TestCase):
    # fixture vault: alpha<->beta linked, ghost link broken, orphan.md unlinked
    # and missing frontmatter, index lists only alpha
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = self.tmp.name
        write(self.vault, "SCHEMA.md", "---\ntype: schema\n---\n# t\n")
        write(self.vault, "index.md", "---\ntype: index\n---\n# Index\n- [[alpha]] — a page\n")
        write(self.vault, "log.md", "---\ntype: log\n---\n## [2026-06-11] init | t\n")
        write(self.vault, "wiki/concepts/alpha.md", "---\ntype: concept\n---\nlinks [[beta]] and [[ghost]]\n")
        write(self.vault, "wiki/concepts/beta.md", "---\ntype: concept\n---\nback to [[alpha]]\n")
        write(self.vault, "wiki/concepts/orphan.md", "no frontmatter here\n")

    def tearDown(self):
        self.tmp.cleanup()

    def issues(self):
        return lint.collect_issues(self.vault)

    def test_broken_wikilink_flagged(self):
        self.assertTrue(any(i.category == "broken-link" and "ghost" in i.detail for i in self.issues()))

    def test_orphan_flagged(self):
        self.assertTrue(any(i.category == "orphan" and "orphan" in i.location for i in self.issues()))

    def test_missing_frontmatter_flagged(self):
        self.assertTrue(any(i.category == "no-frontmatter" and "orphan" in i.location for i in self.issues()))

    def test_pages_missing_from_index_flagged(self):
        issues = self.issues()
        self.assertTrue(any(i.category == "not-in-index" and "beta" in i.location for i in issues))
        self.assertTrue(any(i.category == "not-in-index" and "orphan" in i.location for i in issues))

    def test_index_dangling_link_flagged(self):
        write(self.vault, "index.md", "---\ntype: index\n---\n- [[alpha]]\n- [[vanished]]\n")
        self.assertTrue(any(i.category == "index-dangling" and "vanished" in i.detail for i in self.issues()))

    def test_malformed_log_entry_flagged(self):
        write(self.vault, "log.md", "---\ntype: log\n---\n## [bad date] init | x\n")
        self.assertTrue(any(i.category == "log-format" for i in self.issues()))

    def test_wellformed_log_entry_not_flagged(self):
        self.assertFalse(any(i.category == "log-format" for i in self.issues()))

    def test_uningested_raw_flagged_until_referenced(self):
        write(self.vault, "raw/clip.md", "an article\n")
        self.assertTrue(any(i.category == "uningested" and "clip.md" in i.location for i in self.issues()))
        write(self.vault, "wiki/sources/clip-source.md", "---\ntype: source\nraw: clip.md\n---\n# c\n[[alpha]]\n")
        self.assertFalse(any(i.category == "uningested" for i in self.issues()))

    def test_wikilink_does_not_span_lines(self):
        write(self.vault, "wiki/concepts/gamma.md", "---\ntype: concept\n---\n[[run\naway]] then [[alpha]]\n")
        for issue in self.issues():
            self.assertNotIn("\n", issue.detail)

    def test_bom_frontmatter_not_flagged(self):
        write(self.vault, "wiki/concepts/delta.md", "﻿---\ntype: concept\n---\nsee [[alpha]]\n")
        self.assertFalse(any(i.category == "no-frontmatter" and "delta" in i.location for i in self.issues()))

    def test_clean_vault_has_no_issues(self):
        clean = tempfile.TemporaryDirectory()
        try:
            v = clean.name
            write(v, "SCHEMA.md", "---\ntype: schema\n---\n# t\n")
            write(v, "index.md", "---\ntype: index\n---\n# Index\n- [[alpha]] — a\n- [[beta]] — b\n")
            write(v, "log.md", "---\ntype: log\n---\n## [2026-06-11] init | t\n")
            write(v, "wiki/concepts/alpha.md", "---\ntype: concept\n---\nsee [[beta]]\n")
            write(v, "wiki/concepts/beta.md", "---\ntype: concept\n---\nsee [[alpha]]\n")
            self.assertEqual(lint.collect_issues(v), [])
        finally:
            clean.cleanup()

    def test_stale_page_flagged_and_fresh_not(self):
        write(self.vault, "wiki/concepts/old.md", "---\ntype: concept\nupdated: 2025-01-01\n---\nsee [[alpha]]\n")
        write(self.vault, "wiki/concepts/recent.md", "---\ntype: concept\nupdated: 2026-06-01\n---\nsee [[alpha]]\n")
        stale = lint.stale_issues(self.vault, 90, today=datetime.date(2026, 6, 12))
        self.assertTrue(any(i.category == "stale" and "old" in i.location for i in stale))
        self.assertFalse(any(i.category == "stale" and "recent" in i.location for i in stale))

    def test_source_newer_than_page_flagged(self):
        write(self.vault, "raw/clip.md", "article\n")
        write(self.vault, "wiki/sources/clip-source.md", "---\ntype: source\nraw: clip.md\n---\nsee [[alpha]]\n")
        # force the raw source's mtime to be newer than the page derived from it
        os.utime(os.path.join(self.vault, "wiki", "sources", "clip-source.md"), (1000, 1000))
        os.utime(os.path.join(self.vault, "raw", "clip.md"), (2000, 2000))
        stale = lint.stale_issues(self.vault, 99999)
        self.assertTrue(any(i.category == "source-newer" and "clip-source" in i.location for i in stale))

    def test_parse_args_handles_stale_flag(self):
        self.assertEqual(lint.parse_args([self.vault]), ([self.vault], False, 90))
        self.assertEqual(lint.parse_args([self.vault, "--stale"]), ([self.vault], True, 90))
        self.assertEqual(lint.parse_args([self.vault, "--stale", "30"]), ([self.vault], True, 30))

    def test_main_output_format_and_exit_codes(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(lint.main(["lint.py", self.vault]), 1)
        lines = out.getvalue().strip().splitlines()
        self.assertTrue(lines[-1].endswith("issue(s)"))
        for line in lines[:-1]:
            self.assertEqual(line.count("\t"), 2)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(lint.main(["lint.py"]), 2)


if __name__ == "__main__":
    unittest.main()
