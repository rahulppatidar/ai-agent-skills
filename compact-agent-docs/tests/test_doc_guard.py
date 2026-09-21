from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "doc_guard.py"


class DocGuardTests(unittest.TestCase):
    def run_guard(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_inventory_finds_standard_linked_and_unlinked_documents(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "AGENTS.md").write_text("Read [the PRD](docs/product-prd.md).\n", encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs" / "product-prd.md").write_text("# Product requirements\n", encoding="utf-8")
            (root / "custom-notes.md").write_text("# Unlinked notes\n", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "ignored.md").write_text("ignored\n", encoding="utf-8")

            result = self.run_guard("inventory", str(root), "--json")

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            by_path = {entry["path"]: entry for entry in report["documents"]}
            self.assertEqual(set(by_path), {"AGENTS.md", "custom-notes.md", "docs/product-prd.md"})
            self.assertEqual(by_path["AGENTS.md"]["role"], "agent")
            self.assertEqual(by_path["docs/product-prd.md"]["role"], "business")
            self.assertEqual(by_path["custom-notes.md"]["role"], "custom")
            self.assertEqual(by_path["docs/product-prd.md"]["inbound_links"], 1)

    def test_inventory_reports_broken_local_links(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("See [missing](docs/missing.md).\n", encoding="utf-8")

            result = self.run_guard("inventory", str(root), "--json")

            report = json.loads(result.stdout)
            self.assertEqual(report["documents"][0]["broken_local_links"], ["docs/missing.md"])

    def test_inventory_fails_for_missing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            missing = Path(temporary) / "missing"

            result = self.run_guard("inventory", str(missing), "--json")

            self.assertEqual(result.returncode, 2)
            self.assertIn("target does not exist", result.stderr)

    def test_inventory_ignores_links_inside_code_examples(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "linked.md").write_text("# Linked\n", encoding="utf-8")
            (root / "README.md").write_text(
                "Syntax: `[label](path)`. Read `linked.md`.\n\n"
                "```markdown\n[example](missing.md)\n```\n",
                encoding="utf-8",
            )

            result = self.run_guard("inventory", str(root), "--json")

            report = json.loads(result.stdout)
            by_path = {entry["path"]: entry for entry in report["documents"]}
            self.assertEqual(by_path["README.md"]["broken_local_links"], [])
            self.assertEqual(by_path["linked.md"]["inbound_links"], 0)

    def test_compare_flags_removed_protected_literals(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            before = root / "before.md"
            after = root / "after.md"
            before.write_text(
                "Run `deploy --safe`. See [guide](ops/runbook.md) and https://example.com.\n",
                encoding="utf-8",
            )
            after.write_text("Deploy safely.\n", encoding="utf-8")

            result = self.run_guard("compare", str(before), str(after), "--strict")

            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertFalse(report["strict_checks_passed"])
            self.assertIn("deploy --safe", report["high_risk_removed"]["inline_code"])
            self.assertFalse(report["semantic_equivalence_proven"])

    def test_compare_allows_rewording_but_does_not_claim_equivalence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            before = root / "before.md"
            after = root / "after.md"
            before.write_text("You must run `check`.\n", encoding="utf-8")
            after.write_text("Run `check`; this is required.\n", encoding="utf-8")

            result = self.run_guard("compare", str(before), str(after), "--strict")

            self.assertEqual(result.returncode, 0, result.stdout)
            report = json.loads(result.stdout)
            self.assertTrue(report["strict_checks_passed"])
            self.assertFalse(report["semantic_equivalence_proven"])
            self.assertTrue(report["literal_deltas"]["modal_terms"]["removed"])

    def test_compare_strict_flags_removed_number(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            before = root / "before.md"
            after = root / "after.md"
            before.write_text("Transactions must remain below 5000 USD.\n", encoding="utf-8")
            after.write_text("Transactions have a limit.\n", encoding="utf-8")

            result = self.run_guard("compare", str(before), str(after), "--strict")

            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertEqual(report["high_risk_removed"]["numbers"], ["5000"])


if __name__ == "__main__":
    unittest.main()
