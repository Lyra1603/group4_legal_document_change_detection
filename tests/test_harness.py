"""Verify completion gates, independently of the legal-diff implementation."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "coding_harness",
    Path(__file__).resolve().parents[1] / "scripts/harness.py",
)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)

_ROOT = Path(__file__).resolve().parents[1]
_HARNESS_SCRIPT = _ROOT / "scripts" / "harness.py"
_PYTHON = sys.executable


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


class TestStatusUnicode(unittest.TestCase):
    """Regression: harness status must exit 0 and not crash under a
    narrow-codepage console (simulated via PYTHONIOENCODING=cp1252)."""

    def test_status_exits_zero_under_cp1252_env(self):
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "cp1252"
        result = subprocess.run(
            [_PYTHON, str(_HARNESS_SCRIPT), "status"],
            cwd=str(_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=(
                f"harness status failed under cp1252 env.\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            ),
        )
        # Task list phải xuất hiện
        self.assertIn("W6-SCHEMA", result.stdout, "Task list missing from status output")
        # reconfigure(errors='replace') => không crash; không có UnicodeEncodeError
        self.assertNotIn("UnicodeEncodeError", result.stderr)
        self.assertNotIn("charmap codec", result.stderr)


if __name__ == "__main__":
    unittest.main()
