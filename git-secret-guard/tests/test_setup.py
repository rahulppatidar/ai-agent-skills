"""Exercise the prerequisite planner without installing or downloading anything.

SPDX-License-Identifier: GPL-3.0-only
"""

import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "setup.sh"


@unittest.skipIf(os.name == "nt", "POSIX bootstrap fixture")
class PosixSetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="secret-guard-setup-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.bin = self.base / "bin"
        self.bin.mkdir()
        self.env = os.environ.copy()
        self.env["HOME"] = str(self.base / "home")
        self.env.pop("XDG_BIN_HOME", None)
        self.env["PATH"] = str(self.bin) + os.pathsep + self.env["PATH"]

    def executable(self, name, body):
        path = self.bin / name
        path.write_text("#!/bin/sh\n" + body, encoding="utf-8")
        path.chmod(0o700)
        return path

    def run_setup(self, *args):
        return subprocess.run(
            ["sh", str(SCRIPT), *args], env=self.env,
            capture_output=True, text=True, check=False,
        )

    def valid_gitleaks(self):
        return self.executable("gitleaks", "echo 8.30.1\n")

    def test_scan_ready_needs_only_gitleaks(self):
        self.valid_gitleaks()
        result = self.run_setup("check", "scan")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: ready", result.stdout)
        self.assertIn("No installation is required.", result.stdout)

    def test_user_local_gitleaks_is_found_without_path_change(self):
        local_bin = Path(self.env["HOME"]) / ".local" / "bin"
        local_bin.mkdir(parents=True)
        installed = local_bin / "gitleaks"
        installed.write_text("#!/bin/sh\necho 8.30.1\n", encoding="utf-8")
        installed.chmod(0o700)
        result = self.run_setup("check", "scan")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("gitleaks: 8.30.1", result.stdout)
        self.assertIn(f"gitleaks-path: {installed}", result.stdout)

    def test_supported_user_local_gitleaks_wins_over_old_path_version(self):
        self.executable("gitleaks", "echo 8.18.0\n")
        local_bin = Path(self.env["HOME"]) / ".local" / "bin"
        local_bin.mkdir(parents=True)
        installed = local_bin / "gitleaks"
        installed.write_text("#!/bin/sh\necho 8.30.1\n", encoding="utf-8")
        installed.chmod(0o700)
        result = self.run_setup("check", "scan")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"gitleaks-path: {installed}", result.stdout)

    def test_old_gitleaks_produces_stable_reviewable_plan(self):
        self.executable("gitleaks", "echo 8.18.0\n")
        first = self.run_setup("check", "scan")
        second = self.run_setup("check", "scan")
        self.assertEqual(first.returncode, 10)
        self.assertEqual(second.returncode, 10)
        self.assertIn("status: confirmation-required", first.stdout)
        self.assertIn("missing: gitleaks", first.stdout)
        first_id = re.search(r"^plan-id: (\S+)$", first.stdout, re.MULTILINE).group(1)
        second_id = re.search(r"^plan-id: (\S+)$", second.stdout, re.MULTILINE).group(1)
        self.assertEqual(first_id, second_id)

    def test_install_refuses_wrong_or_missing_plan_id_before_changes(self):
        self.executable("gitleaks", "echo 8.18.0\n")
        for args in (("install", "scan"), ("install", "scan", "--approve", "wrong")):
            with self.subTest(args=args):
                result = self.run_setup(*args)
                self.assertEqual(result.returncode, 2)
                self.assertIn("Installation refused", result.stderr)
                self.assertFalse((Path(self.env["HOME"]) / ".local" / "bin").exists())

    def test_pre_commit_does_not_require_python(self):
        self.valid_gitleaks()
        self.executable(
            "python3",
            "case \"$*\" in *print*) echo 3.8.0; exit 0;; *) exit 1;; esac\n",
        )
        result = self.run_setup("check", "pre-commit")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pre_push_requires_supported_python(self):
        self.valid_gitleaks()
        self.executable(
            "python3",
            "case \"$*\" in *print*) echo 3.8.0; exit 0;; *) exit 1;; esac\n",
        )
        result = self.run_setup("check", "pre-push")
        self.assertEqual(result.returncode, 10)
        self.assertRegex(result.stdout, r"missing: .*python3")


if __name__ == "__main__":
    unittest.main()
