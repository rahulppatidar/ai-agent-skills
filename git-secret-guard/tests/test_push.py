"""Exercise native pre-push hooks against disposable local bare remotes.

SPDX-License-Identifier: GPL-3.0-only
"""

from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_scan as fixtures


@unittest.skipUnless(fixtures.BINARY and os.name != "nt", "Requires Gitleaks and POSIX native hooks")
class PushIntegrationTests(unittest.TestCase):
    git = fixtures.GitleaksIntegrationTests.git
    write = fixtures.GitleaksIntegrationTests.write
    scan = fixtures.GitleaksIntegrationTests.scan

    def setUp(self):
        fixtures.GitleaksIntegrationTests.setUp(self)
        self.git("branch", "-M", "main")
        self.remote = self.base / "remote.git"
        self.git("init", "--bare", "-q", str(self.remote))
        self.git("remote", "add", "origin", str(self.remote))
        destination = self.repo / ".secret-guard"
        destination.mkdir()
        shutil.copyfile(fixtures.SCRIPT, destination / "scan.py")
        template = fixtures.SCRIPT.parents[1] / "assets" / "pre-push"
        self.hook = self.repo / ".git" / "hooks" / "pre-push"
        self.hook.write_bytes(template.read_bytes())
        self.hook.chmod(0o700)
        self.git("config", "--local", "secretguard.pythonPath", sys.executable)
        self.git("config", "--local", "secretguard.gitleaksPath", str(Path(fixtures.BINARY).resolve()))
        self.env["PATH"] = str(Path(fixtures.BINARY).resolve().parent) + os.pathsep + self.env["PATH"]

    def commit(self, secret=False):
        self.write("settings.txt", secret)
        self.git("add", "settings.txt")
        self.git("commit", "-qm", "synthetic fixture")
        return self.git("rev-parse", "HEAD").decode().strip()

    def push(self, *refs, blocked=False):
        result = subprocess.run(["git", "push", "origin", *refs], cwd=self.repo,
                                env=self.env, capture_output=True, check=False)
        self.assertNotIn(fixtures.SYNTHETIC.encode(), result.stdout + result.stderr)
        if blocked:
            self.assertNotEqual(result.returncode, 0)
        else:
            self.assertEqual(result.returncode, 0, "Expected push to pass")
        return result

    def remote_refs(self):
        return self.git("for-each-ref", "--format=%(refname) %(objectname)", cwd=self.remote)

    def hook_input(self, data, extra=()):
        result = subprocess.run(
            [sys.executable, "-B", str(fixtures.SCRIPT), "pre-push", "--hook",
             "--path", str(self.repo), "--gitleaks", fixtures.BINARY, *extra],
            input=data.encode(), cwd=self.repo, env=self.env, capture_output=True, check=False,
        )
        self.assertNotIn(fixtures.SYNTHETIC.encode(), result.stdout + result.stderr)
        return result.returncode, json.loads(result.stdout)

    def test_clean_first_update_tag_and_deletion_pushes(self):
        self.commit()
        self.push("main")
        (self.repo / "extra.md").write_text("Ordinary documentation.\n")
        self.git("add", "extra.md")
        self.git("commit", "-qm", "clean update")
        self.push("main")
        self.git("tag", "-a", "v-test", "-m", "synthetic tag")
        self.push("refs/tags/v-test")
        self.push(":refs/tags/v-test")
        self.assertNotIn(b"refs/tags/v-test", self.remote_refs())
        self.assertIn(b"refs/heads/main", self.remote_refs())

    def test_added_then_deleted_secret_blocks_first_push(self):
        self.commit(secret=True)
        self.commit()
        self.push("main", blocked=True)
        self.assertEqual(self.remote_refs(), b"")

    def test_multi_ref_push_checks_noncurrent_branch(self):
        self.commit()
        self.git("checkout", "-qb", "secret-branch")
        self.commit(secret=True)
        self.git("checkout", "-q", "main")
        self.push("main", "secret-branch", blocked=True)
        self.assertEqual(self.remote_refs(), b"")

    def test_unrelated_branch_does_not_block_clean_push(self):
        self.commit()
        self.git("checkout", "-qb", "unrelated")
        self.commit(secret=True)
        self.push("main")
        self.assertIn(b"refs/heads/main", self.remote_refs())
        self.assertNotIn(b"unrelated", self.remote_refs())

    def test_commit_tags_with_secret_ancestry_block(self):
        self.commit(secret=True)
        self.git("tag", "lightweight")
        self.git("tag", "-a", "annotated", "-m", "synthetic tag")
        for tag in ("lightweight", "annotated"):
            self.push("refs/tags/" + tag, blocked=True)
        self.assertEqual(self.remote_refs(), b"")

    def test_blob_tag_blocks_as_unsupported(self):
        self.write("blob.txt")
        blob = self.git("hash-object", "-w", "blob.txt").decode().strip()
        self.git("tag", "blob-tag", blob)
        self.push("refs/tags/blob-tag", blocked=True)
        self.assertEqual(self.remote_refs(), b"")

    def test_force_push_secret_blocks_and_preserves_remote(self):
        self.commit()
        self.push("main")
        before = self.remote_refs()
        self.git("checkout", "-q", "--orphan", "replacement")
        self.commit(secret=True)
        self.push("--force", "HEAD:refs/heads/main", blocked=True)
        self.assertEqual(self.remote_refs(), before)

    def test_clean_force_push_is_scanned_and_passes(self):
        self.commit()
        self.push("main")
        self.git("checkout", "-q", "--orphan", "replacement")
        replacement = self.commit()
        self.push("--force", "HEAD:refs/heads/main")
        self.assertIn(replacement.encode(), self.remote_refs())

    def test_merge_resolution_secret_blocks(self):
        self.commit()
        self.git("checkout", "-qb", "side")
        (self.repo / "side.md").write_text("side\n")
        self.git("add", "side.md")
        self.git("commit", "-qm", "side")
        self.git("checkout", "-q", "main")
        (self.repo / "main.md").write_text("main\n")
        self.git("add", "main.md")
        self.git("commit", "-qm", "main")
        self.git("merge", "--no-ff", "--no-commit", "side")
        self.commit(secret=True)
        self.assertEqual(self.scan("history")[0], 1)
        self.push("main", blocked=True)
        self.assertEqual(self.remote_refs(), b"")

    def test_malformed_and_missing_object_input_blocks(self):
        missing = "f" * 40
        zero = "0" * 40
        for data in ("invalid input\n", f"HEAD --all refs/heads/main {zero}\n",
                     f"HEAD {missing} refs/heads/main {zero}\n"):
            code, report = self.hook_input(data)
            self.assertEqual((code, report["status"]), (2, "incomplete"))

    def test_missing_remote_base_does_not_hide_history(self):
        tip = self.commit(secret=True)
        code, _ = self.hook_input(f"HEAD {tip} refs/heads/main {'f' * 40}\n")
        self.assertEqual(code, 1)

    def test_deletion_and_empty_input_are_explicit_no_ops(self):
        for data in ("", f"(delete) {'0' * 40} refs/heads/old {'f' * 40}\n"):
            code, report = self.hook_input(data)
            self.assertEqual((code, report["status"]), (0, "nothing_to_scan"))

    def test_invalid_config_blocks_push(self):
        self.commit()
        (self.repo / ".gitleaks.toml").write_text("invalid TOML = [")
        self.push("main", blocked=True)
        self.assertEqual(self.remote_refs(), b"")

    def test_missing_scanner_blocks_push(self):
        self.commit()
        # Use an explicitly nonexistent configured executable rather than altering system PATH.
        self.git("config", "--local", "secretguard.gitleaksPath", "./missing-scanner")
        self.push("main", blocked=True)
        self.assertEqual(self.remote_refs(), b"")

    def test_shallow_push_input_is_incomplete(self):
        tip = self.commit()
        shallow = self.base / "shallow"
        self.git("clone", "-q", "--depth=1", self.repo.as_uri(), str(shallow))
        code, report = self.hook_input(
            f"HEAD {tip} refs/heads/main {'0' * 40}\n", extra=("--path", str(shallow)))
        self.assertEqual((code, report["status"]), (2, "incomplete"))


class HookExitContractTests(unittest.TestCase):
    def test_empty_staged_hook_succeeds_without_claiming_clean(self):
        with patch.object(fixtures.GUARD, "scan", return_value=3):
            self.assertEqual(fixtures.GUARD.main(["staged", "--hook"]), 0)
            self.assertEqual(fixtures.GUARD.main(["staged"]), 3)

    def test_hook_flag_does_not_hide_failures(self):
        for code in (1, 2):
            with patch.object(fixtures.GUARD, "scan", return_value=code):
                self.assertEqual(fixtures.GUARD.main(["pre-push", "--hook"]), code)

    def test_hook_flag_rejects_audit_mode(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(fixtures.GUARD.main(["history", "--hook"]), 2)


if __name__ == "__main__":
    unittest.main()
