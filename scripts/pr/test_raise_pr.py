import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import raise_pr


class RaisePrTest(unittest.TestCase):
    def test_parse_remote_variants(self):
        expected = ("akashvikram249", "capstone_claude")
        for url in (
            "https://github.com/akashvikram249/capstone_claude.git",
            "https://github.com/akashvikram249/capstone_claude",
            "git@github.com:akashvikram249/capstone_claude.git",
            "ssh://git@github.com/akashvikram249/capstone_claude.git",
        ):
            self.assertEqual(raise_pr.parse_remote(url), expected, url)

    def test_parse_remote_rejects_other_hosts(self):
        with self.assertRaises(raise_pr.Fail):
            raise_pr.parse_remote("https://gitlab.com/a/b.git")

    def test_branch_name(self):
        self.assertEqual(
            raise_pr.branch_name("US-103", "Add Bulk Delete: test cases!"),
            "story/us-103-add-bulk-delete-test-cases",
        )

    def test_choose_branch(self):
        choose = raise_pr.choose_branch
        self.assertEqual(choose("US-103", "Bulk delete", "main", "main", None), "story/us-103-bulk-delete")
        self.assertEqual(choose("US-103", "Bulk delete", "story/us-103-bulk-delete", "main", None),
                         "story/us-103-bulk-delete")
        self.assertEqual(choose("US-103", "x", "feature/other", "main", "story/custom"), "story/custom")

    def test_choose_branch_refuses_other_story_branches(self):
        with self.assertRaises(raise_pr.Fail):
            raise_pr.choose_branch("US-103", "Bulk delete", "feature/automated-pr-creation", "main", None)
        with self.assertRaises(raise_pr.Fail):
            raise_pr.choose_branch("US-104", "Other", "story/us-103-bulk-delete", "main", None)

    def test_blocked_files(self):
        for name in (".env", "config/.env.local", "certs/server.pem", "credentials.json"):
            self.assertTrue(raise_pr.BLOCKED_FILE.search(name), name)
        for name in ("README.md", "src/main/Environment.java", "keyboard.js"):
            self.assertFalse(raise_pr.BLOCKED_FILE.search(name), name)

    def test_body_validation_requires_all_sections(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
            handle.write("## Summary\nonly one section\n")
        try:
            with self.assertRaises(raise_pr.Fail):
                raise_pr.validate_body(handle.name)
        finally:
            os.unlink(handle.name)

    def test_publish_requires_approval(self):
        with self.assertRaises(raise_pr.Fail):
            raise_pr.main(["--story", "US-1", "--title", "t", "--body-file", "x.md"])


if __name__ == "__main__":
    unittest.main()
