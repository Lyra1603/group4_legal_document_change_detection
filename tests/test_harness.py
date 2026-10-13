"""Verify completion gates, independently of the legal-diff implementation."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("coding_harness", Path(__file__).resolve().parents[1] / "scripts/harness.py")
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


class HarnessGates(unittest.TestCase):
    def test_missing_task_tests_cannot_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(harness, "ROOT", Path(folder)):
                with self.assertRaisesRegex(RuntimeError, "BLOCKED"):
                    harness.verify([{"id": "EXAMPLE", "test_file": "tests/missing.py"}], "EXAMPLE")

    def test_zero_tests_cannot_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "tests").mkdir()
            (root / "tests/test_zero_gate.py").write_text("# No tests\n")
            with patch.object(harness, "ROOT", root):
                with self.assertRaisesRegex(RuntimeError, "zero tests"):
                    harness.verify([{"id": "EXAMPLE", "test_file": "tests/test_zero_gate.py"}], "EXAMPLE")

    def test_done_without_review_is_rejected(self):
        data = json.loads(harness.TASKS.read_text(encoding="utf-8"))
        data["tasks"][0].update(status="done", evidence=["test ran"], reviewer=None)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tasks.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with patch.object(harness, "TASKS", path):
                with self.assertRaisesRegex(ValueError, "reviewer"):
                    harness.load_tasks()


if __name__ == "__main__":
    unittest.main()
