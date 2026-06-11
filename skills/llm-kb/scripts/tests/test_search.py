# ---------- test_search.py — unit tests for vault keyword search ----------- #
"""
Depends on: stdlib only (os, sys, tempfile, unittest); search.py via sys.path.
Data shapes: throwaway vault per test; asserts on (score, path) ranking tuples.
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import search


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class SearchTests(unittest.TestCase):
    # fixture: dragons.md dense in "dragon", economy.md unrelated,
    # raw/clip.md mentions dragon once (raw must be searchable too)
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = self.tmp.name
        write(self.vault, "wiki/concepts/dragons.md", "dragon dragon dragon fire wings\n")
        write(self.vault, "wiki/concepts/economy.md", "trade gold market caravan\n")
        write(self.vault, "raw/clip.md", "a dragon appears once in this clip\n")
        write(self.vault, "raw/assets/pic.md", "dragon dragon dragon dragon\n")

    def tearDown(self):
        self.tmp.cleanup()

    def rank(self, query):
        docs = search.collect_docs(self.vault)
        return [os.path.basename(p) for _s, p in search.score_docs(docs, search.tokenize(query))]

    def test_tokenize_lowercases_and_splits(self):
        self.assertEqual(search.tokenize("Dragon-Fire 99!"), ["dragon", "fire", "99"])

    def test_ranks_dense_page_first(self):
        ranking = self.rank("dragon")
        self.assertEqual(ranking[0], "dragons.md")
        self.assertIn("clip.md", ranking)

    def test_no_hits_returns_empty(self):
        self.assertEqual(self.rank("zebra"), [])

    def test_assets_dir_skipped(self):
        self.assertNotIn("pic.md", self.rank("dragon"))

    def test_tie_break_is_path_ascending(self):
        write(self.vault, "wiki/concepts/aaa.md", "unicorn horn\n")
        write(self.vault, "wiki/concepts/zzz.md", "unicorn horn\n")
        self.assertEqual(self.rank("unicorn"), ["aaa.md", "zzz.md"])


if __name__ == "__main__":
    unittest.main()
