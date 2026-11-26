import os
import sys
import tempfile
import unittest
from unittest import mock

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

    def test_token_route_labels_the_pr(self):
        calls = []

        def fake_api(method, url, token, payload=None):
            calls.append((method, url, payload))
            return 201, {}

        with mock.patch.object(raise_pr, "api_request", fake_api):
            raise_pr.label_pr_with_token("o", "r", "https://github.com/o/r/pull/7", "tok")
        self.assertEqual(calls[-1][1], "https://api.github.com/repos/o/r/issues/7/labels")
        self.assertEqual(calls[-1][2], {"labels": ["ai-generated"]})

    def test_token_route_reports_label_failure(self):
        with mock.patch.object(raise_pr, "api_request", lambda *a, **k: (403, {"message": "denied"})):
            with self.assertRaises(raise_pr.Fail):
                raise_pr.label_pr_with_token("o", "r", "https://github.com/o/r/pull/7", "tok")

    def test_gh_route_adds_label_to_pr(self):
        ran = []

        def fake_run(cmd, **kwargs):
            ran.append(cmd)
            return mock.Mock(returncode=0, stdout="", stderr="")

        with mock.patch.object(raise_pr.subprocess, "run", fake_run):
            raise_pr.label_pr_with_gh("https://github.com/o/r/pull/7")
        self.assertIn(["gh", "pr", "edit", "https://github.com/o/r/pull/7", "--add-label", "ai-generated"], ran)

    def test_open_pr_returns_label_error_without_losing_the_url(self):
        with mock.patch.object(raise_pr.shutil, "which", return_value=None), \
             mock.patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}), \
             mock.patch.object(raise_pr, "create_pr_with_token", return_value="https://github.com/o/r/pull/7"), \
             mock.patch.object(raise_pr, "label_pr_with_token", side_effect=raise_pr.Fail("nope")):
            url, error = raise_pr.open_pr("o", "r", "main", "b", "t", "f", "body")
        self.assertEqual(url, "https://github.com/o/r/pull/7")
        self.assertEqual(error, "nope")


if __name__ == "__main__":
    unittest.main()
