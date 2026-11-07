import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("context_capsule", ROOT / "examples/context_capsule.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ContextPacketTests(unittest.TestCase):
    def setUp(self):
        self.capsule = json.loads((ROOT / "examples/policy_capsule.json").read_text())

    def compile(self, budget=4000):
        return MODULE.compile_context(self.capsule, "adoption ministry funding", budget, "2026-11-07")

    def test_reproducible_source_linked_selection(self):
        a = self.compile()
        self.assertEqual(a, self.compile())
        self.assertEqual(set(a["receipt"]["included"]), {"C1", "C2", "C3"})
        self.assertEqual(a["receipt"]["omitted"], [{"id": "C4", "reason": "expired"}, {"id": "C5", "reason": "review_required"}])
        self.assertEqual(len(a["packet"]["sources"]), 2)
        self.assertEqual(a["receipt"]["packet_bytes"], len(MODULE.encoded(a["packet"])))

    def test_byte_budget_and_comparison_atomicity_across_budgets(self):
        for budget in range(400, 4000, 75):
            result = self.compile(budget)
            ids = result["receipt"]["included"]
            self.assertEqual("C1" in ids, "C2" in ids)
            self.assertLessEqual(result["receipt"]["packet_bytes"], budget)
            self.assertEqual(len(ids) + len(result["receipt"]["omitted"]), 5)

    def test_large_comparison_does_not_starve_later_small_evidence(self):
        result = self.compile(1000)
        self.assertEqual(result["receipt"]["included"], ["C3"])

    def test_inapplicable_comparison_is_reported_instead_of_becoming_one_sided(self):
        self.capsule["claims"][1]["review"] = "proposed"
        result = self.compile()
        self.assertNotIn("C1", result["receipt"]["included"])
        self.assertIn({"id": "C1", "reason": "comparison_incomplete"}, result["receipt"]["omitted"])

    def test_missing_source_or_invented_quote_rejected(self):
        for key, value in [("source_id", "missing"), ("quote", "The pilot has been adopted.")]:
            with self.subTest(key=key):
                capsule = copy.deepcopy(self.capsule)
                capsule["claims"][0][key] = value
                with self.assertRaises(ValueError):
                    MODULE.compile_context(capsule, "adoption", 4000, "2026-11-07")

    def test_unicode_bytes_are_counted(self):
        self.capsule["claims"][2]["text"] += " التمويل" * 100
        result = self.compile(1600)
        self.assertLessEqual(len(MODULE.encoded(result["packet"])), 1600)

    def test_cli_can_emit_exact_bounded_packet_without_inspection_wrapper(self):
        output = subprocess.check_output([sys.executable, str(ROOT / "examples/context_capsule.py"),
                                          "--packet-only", "--budget-bytes", "1000"])
        self.assertLessEqual(len(output), 1000)
        self.assertEqual(json.loads(output)["format"], "tacitus-context-packet/1")

    def test_duplicate_ids_and_impossible_budget_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.compile_context(self.capsule, "adoption " * 100, 256, "2026-11-07")
        self.capsule["claims"].append(self.capsule["claims"][0])
        with self.assertRaises(ValueError):
            self.compile()


if __name__ == "__main__":
    unittest.main()
