"""Isolated scan-contract and optional real-Gitleaks integration tests.

Run: GITLEAKS_TEST_BINARY=/path/to/gitleaks python3 -B -m unittest discover
     -s git-secret-guard/tests -v
SPDX-License-Identifier: GPL-3.0-only
"""

from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "scan.py"
SPEC = importlib.util.spec_from_file_location("secret_guard", SCRIPT)
GUARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)
BINARY = os.environ.get("GITLEAKS_TEST_BINARY") or shutil.which("gitleaks")
# Construct a nonfunctional GitHub-shaped test value, never a live credential.
SYNTHETIC = "ghp_" + hashlib.sha256(b"git-secret-guard synthetic fixture").hexdigest()[:36]


class ReportContractTests(unittest.TestCase):
    def invoke(self, scan_result):
        with tempfile.TemporaryDirectory(prefix="secret-guard-contract-") as directory:
            output = io.StringIO()
            version = subprocess.CompletedProcess([], 0, b"8.30.1\n", b"")
            with patch.object(GUARD.shutil, "which", return_value=sys.executable), \
                    patch.object(GUARD, "run", side_effect=[version, scan_result]), \
                    redirect_stdout(output):
                code = GUARD.main(["files", "--path", directory])
            return code, json.loads(output.getvalue()), output.getvalue()

    def test_source_fields_are_not_forwarded(self):
        finding = {"File": "config.json", "StartLine": 3, "RuleID": "test",
                   "Commit": "", "Secret": SYNTHETIC, "Match": SYNTHETIC,
                   "Description": SYNTHETIC, "Author": SYNTHETIC,
                   "Email": SYNTHETIC, "ExtraField": SYNTHETIC}
        result = subprocess.CompletedProcess([], 23, json.dumps([finding]).encode(), b"")
        code, report, output = self.invoke(result)
        self.assertEqual(code, 1)
        self.assertNotIn(SYNTHETIC, output)
        self.assertEqual(set(report["findings"][0]), {"file", "line", "rule", "commit"})

    def test_error_output_is_withheld(self):
        result = subprocess.CompletedProcess([], 1, SYNTHETIC.encode(), SYNTHETIC.encode())
        code, report, output = self.invoke(result)
        self.assertEqual((code, report["status"]), (2, "incomplete"))
        self.assertNotIn(SYNTHETIC, output)

    def test_error_diagnostic_invalidates_success(self):
        result = subprocess.CompletedProcess([], 0, b"[]", b"scan error")
        self.assertEqual(self.invoke(result)[0], 2)

    def test_invalid_reports_cannot_pass(self):
        for payload in (b"", b"null", b"{}", b"[null]", b"[{}]", b"bad json"):
            with self.subTest(payload=payload):
                self.assertEqual(self.invoke(subprocess.CompletedProcess([], 0, payload, b""))[0], 2)

    def test_exit_report_disagreement_cannot_pass(self):
        self.assertEqual(self.invoke(subprocess.CompletedProcess([], 23, b"[]", b""))[0], 2)

    def test_timeout_does_not_expose_output(self):
        with patch.object(GUARD.subprocess, "run", side_effect=subprocess.TimeoutExpired(
                [SYNTHETIC], 1, output=SYNTHETIC, stderr=SYNTHETIC)):
            with self.assertRaises(GUARD.Incomplete) as caught:
                GUARD.run(["test"], ".", 1)
        self.assertNotIn(SYNTHETIC, str(caught.exception))

    def test_missing_executable_is_incomplete(self):
        with patch.object(GUARD.shutil, "which", return_value=None), \
                redirect_stdout(io.StringIO()) as output:
            code = GUARD.main(["files"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["status"], "incomplete")

    def test_invalid_timeout_is_incomplete(self):
        with redirect_stdout(io.StringIO()) as output:
            code = GUARD.main(["files", "--timeout", "0"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["status"], "incomplete")

    def test_changed_index_cannot_pass(self):
        with tempfile.TemporaryDirectory(prefix="secret-guard-race-") as directory:
            output = io.StringIO()
            results = [subprocess.CompletedProcess([], 0, b"8.30.1\n", b""),
                       subprocess.CompletedProcess([], 0, b"[]", b"")]
            git_results = [os.fsencode(directory) + b"\n", b"", b"initial index",
                           b"config.txt\0", b"changed index"]
            with patch.object(GUARD.shutil, "which", return_value=sys.executable), \
                    patch.object(GUARD, "run", side_effect=results), \
                    patch.object(GUARD, "git", side_effect=git_results), redirect_stdout(output):
                code = GUARD.main(["staged", "--path", directory])
            self.assertEqual(code, 2)
            self.assertIn("index changed", json.loads(output.getvalue())["reason"])


@unittest.skipUnless(BINARY, "Set GITLEAKS_TEST_BINARY to run real-scanner tests")
class GitleaksIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="secret-guard-integration-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repository with spaces"
        self.repo.mkdir()
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(("GIT_", "GITLEAKS_"))}
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        self.git("init", "-q")
        self.git("config", "user.name", "Synthetic Test")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "commit.gpgsign", "false")

    def git(self, *args, cwd=None):
        result = subprocess.run(["git", *args], cwd=cwd or self.repo, env=self.env,
                                capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, "Git fixture setup failed")
        return result.stdout

    def write(self, name, secret=False):
        path = self.repo / name
        path.write_text('token = "' + (SYNTHETIC if secret else "example") + '"\n', encoding="utf-8")
        return path

    def scan(self, scope, target=None, extra=()):
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), scope, "--path", str(target or self.repo),
             "--gitleaks", BINARY, *extra], env=self.env, capture_output=True, check=False,
        )
        self.assertNotIn(SYNTHETIC.encode(), result.stdout + result.stderr)
        self.assertEqual(result.stderr, b"")
        return result.returncode, json.loads(result.stdout)

    def test_first_commit_clean(self):
        self.write("README.md")
        self.git("add", "README.md")
        code, report = self.scan("staged")
        self.assertEqual((code, report["status"]), (0, "no_findings"))

    def test_first_commit_secret(self):
        self.write("config.txt", secret=True)
        self.git("add", "config.txt")
        code, report = self.scan("staged")
        self.assertEqual(code, 1)
        self.assertIn("github-pat", {entry["rule"] for entry in report["findings"]})

    def test_staged_secret_with_clean_working_file(self):
        self.write("config.txt", secret=True)
        self.git("add", "config.txt")
        self.write("config.txt")
        before = self.git("ls-files", "--stage", "-z")
        status_before = self.git("status", "--porcelain=v1", "-z")
        self.assertEqual(self.scan("staged")[0], 1)
        self.assertEqual(before, self.git("ls-files", "--stage", "-z"))
        self.assertEqual(status_before, self.git("status", "--porcelain=v1", "-z"))
        self.assertNotIn(SYNTHETIC, (self.repo / "config.txt").read_text())

    def test_clean_index_with_unstaged_secret(self):
        self.write("config.txt")
        self.git("add", "config.txt")
        self.write("config.txt", secret=True)
        self.assertEqual(self.scan("staged")[0], 0)
        self.assertEqual(self.scan("files")[0], 1)

    def test_nothing_staged(self):
        self.assertEqual(self.scan("staged")[0], 3)

    def test_no_history(self):
        self.assertEqual(self.scan("history")[0], 3)

    def test_non_git_folder_and_single_hidden_file(self):
        target = self.base / "ordinary folder"
        target.mkdir()
        hidden = target / ".credentials"
        hidden.write_text('token = "' + SYNTHETIC + '"\n')
        self.assertEqual(self.scan("files", target)[0], 1)
        self.assertEqual(self.scan("files", hidden)[0], 1)
        self.assertEqual(self.scan("staged", target)[0], 2)

    def test_deleted_history_secret(self):
        self.write("config.txt", secret=True)
        self.git("add", "config.txt")
        self.git("commit", "-qm", "synthetic fixture")
        self.write("config.txt")
        self.git("add", "config.txt")
        self.git("commit", "-qm", "remove synthetic fixture")
        self.assertEqual(self.scan("files")[0], 0)
        code, report = self.scan("history")
        self.assertEqual(code, 1)
        self.assertTrue(report["findings"][0]["commit"])

    def test_history_in_noncurrent_branch(self):
        self.write("README.md")
        self.git("add", "README.md")
        self.git("commit", "-qm", "base")
        base = self.git("rev-parse", "HEAD").decode().strip()
        self.git("checkout", "-qb", "fixture-branch")
        self.write("config.txt", secret=True)
        self.git("add", "config.txt")
        self.git("commit", "-qm", "synthetic fixture")
        self.git("checkout", "-q", "--detach", base)
        self.assertEqual(self.scan("history")[0], 1)

    def test_shallow_history_is_incomplete(self):
        self.write("README.md")
        self.git("add", "README.md")
        self.git("commit", "-qm", "base")
        clone = self.base / "shallow"
        self.git("clone", "-q", "--depth=1", self.repo.as_uri(), str(clone))
        self.assertEqual(self.scan("history", clone)[0], 2)

    def test_bad_config_is_incomplete(self):
        config = self.base / "broken.toml"
        config.write_text("this is not TOML = [")
        self.assertEqual(self.scan("files", extra=("--config", str(config)))[0], 2)

    def test_missing_target_is_incomplete(self):
        self.assertEqual(self.scan("files", self.base / "absent")[0], 2)

    def test_unusual_filename(self):
        filename = "config space-ü.txt"
        self.write(filename, secret=True)
        self.git("add", "--", filename)
        self.assertEqual(self.scan("staged")[0], 1)

    def test_conflicted_index_is_incomplete(self):
        self.write("config.txt")
        blob = self.git("hash-object", "-w", "config.txt").strip()
        result = subprocess.run(
            ["git", "update-index", "--index-info"], cwd=self.repo, env=self.env,
            input=b"100644 " + blob + b" 1\tconfig.txt\n100644 " + blob + b" 2\tconfig.txt\n",
            capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(self.scan("staged")[0], 2)

    def test_custom_rule_extends_defaults(self):
        config = self.base / "rules.toml"
        config.write_text(
            '[extend]\nuseDefault = true\n[[rules]]\nid = "synthetic-org"\n'
            'description = "Synthetic organization fixture"\nregex = "ORG_TEST_[0-9]{12}"\n'
        )
        self.write("config.txt", secret=True)
        (self.repo / "custom.txt").write_text("ORG_TEST_" + "123456" * 2 + "\n")
        code, report = self.scan("files", extra=("--config", str(config)))
        self.assertEqual(code, 1)
        self.assertTrue({"github-pat", "synthetic-org"}.issubset(
            {entry["rule"] for entry in report["findings"]}))

    @unittest.skipIf(os.name == "nt", "Native POSIX hook fixture")
    def test_native_hook_blocks_and_preserves_existing_step(self):
        import shlex
        hook = self.repo / ".git" / "hooks" / "pre-commit"
        hook.write_text(
            "#!/bin/sh\n"
            "printf 'ran' > .git/existing-hook-ran\n"
            + shlex.quote(str(Path(BINARY).resolve()))
            + ' git --pre-commit --staged --redact=100 --no-banner . || exit "$?"\n'
        )
        hook.chmod(0o700)
        self.write("config.txt", secret=True)
        self.git("add", "config.txt")
        self.write("config.txt")
        attempt = subprocess.run(["git", "commit", "-qm", "blocked fixture"], cwd=self.repo,
                                 env=self.env, capture_output=True, check=False)
        self.assertNotEqual(attempt.returncode, 0)
        self.assertNotIn(SYNTHETIC.encode(), attempt.stdout + attempt.stderr)
        self.assertTrue((self.repo / ".git" / "existing-hook-ran").exists())
        self.git("add", "config.txt")
        self.git("commit", "-qm", "clean fixture passes")

    @unittest.skipIf(os.name == "nt", "Native POSIX hook fixture")
    def test_bundled_pre_commit_uses_configured_absolute_scanner(self):
        hook = self.repo / ".git" / "hooks" / "pre-commit"
        template = SCRIPT.parents[1] / "assets" / "pre-commit"
        hook.write_bytes(template.read_bytes())
        hook.chmod(0o700)
        self.git("config", "--local", "secretguard.gitleaksPath", str(Path(BINARY).resolve()))
        self.write("config.txt", secret=True)
        self.git("add", "config.txt")
        attempt = subprocess.run(
            ["git", "commit", "-qm", "blocked fixture"], cwd=self.repo,
            env={**self.env, "PATH": "/usr/bin:/bin"}, capture_output=True, check=False,
        )
        self.assertNotEqual(attempt.returncode, 0)
        self.assertNotIn(SYNTHETIC.encode(), attempt.stdout + attempt.stderr)

    @unittest.skipIf(os.name == "nt", "Native POSIX hook fixture")
    def test_native_hook_fails_for_missing_scanner_and_invalid_config(self):
        import shlex
        hook = self.repo / ".git" / "hooks" / "pre-commit"
        self.write("README.md")
        self.git("add", "README.md")
        for executable, invalid_config in ((self.base / "missing-scanner", False), (BINARY, True)):
            with self.subTest(invalid_config=invalid_config):
                hook.write_text("#!/bin/sh\n" + shlex.quote(str(executable))
                                + ' git --pre-commit --staged --redact=100 --no-banner . || exit "$?"\n')
                hook.chmod(0o700)
                if invalid_config:
                    (self.repo / ".gitleaks.toml").write_text("invalid TOML = [")
                result = subprocess.run(["git", "commit", "-qm", "must block"], cwd=self.repo,
                                        env=self.env, capture_output=True, check=False)
                self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
