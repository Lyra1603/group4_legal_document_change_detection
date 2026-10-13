"""Small, dependency-free coding harness. Run from any directory."""
import argparse
import ast
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "harness/tasks.json"


def load_tasks():
    data = json.loads(TASKS.read_text(encoding="utf-8"))
    tasks = data["tasks"]
    ids = [t["id"] for t in tasks]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate task IDs")
    known = set(ids)
    for task in tasks:
        if task["status"] not in {"todo", "in_progress", "blocked", "review", "done"}:
            raise ValueError(f"Invalid status: {task['id']}")
        if not task["acceptance"] or not task["test_file"]:
            raise ValueError(f"Missing acceptance/test_file: {task['id']}")
        if not set(task["depends_on"]).issubset(known):
            raise ValueError(f"Unknown dependency: {task['id']}")
        path = (ROOT / task["test_file"]).resolve()
        if not path.is_relative_to(ROOT / "tests") or path.suffix != ".py":
            raise ValueError(f"Test must be a Python file under tests/: {task['id']}")
        if task["status"] == "done" and not task.get("evidence"):
            raise ValueError(f"done requires evidence and reviewer: {task['id']}")
        if task["status"] == "done" and not task.get("reviewer"):
            raise ValueError(f"done requires reviewer: {task['id']}")
    if sum(t["status"] == "in_progress" for t in tasks) > 1:
        raise ValueError("This branch supports one in_progress task at a time")
    return tasks


def status(tasks):
    result = subprocess.run(["git", "status", "--short", "--branch"], cwd=ROOT)
    if result.returncode:
        raise RuntimeError("Cannot read git state")
    for task in tasks:
        print(f"{task['id']}: {task['status']} | {task['owner']} | {task['title']}")


def check(tasks):
    files = sorted((ROOT / "src").rglob("*.py"))
    files += sorted((ROOT / "backend").rglob("*.py"))
    files += sorted((ROOT / "scripts").rglob("*.py"))
    for path in files:
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    print(f"PASS: harness manifest and syntax ({len(files)} Python files)")
    sys.path.insert(0, str(ROOT))
    from src.pipeline import run_pipeline
    old = "Điều 1. Thời hạn nộp hồ sơ\nTổ chức phải nộp hồ sơ trong 30 ngày."
    new = "Điều 1. Thời hạn nộp hồ sơ\nTổ chức phải nộp hồ sơ trong 15 ngày."
    report = run_pipeline(old, new)
    if not isinstance(report, list) or len(report) != 1:
        raise RuntimeError("Baseline smoke: expected one aligned pair")
    pair = report[0]
    if pair["align_type"] != "PAIRED" or not pair["semantic_diff"]["is_meaningful_change"]:
        raise RuntimeError("Baseline smoke: deadline change was not detected")
    print("PASS: existing text baseline smoke (synthetic deadline example)")
    print("NOT VERIFIED: upload, new SRS schema, UI or legal accuracy metrics.")
    print("When Pipeline changes, update this smoke to the reviewed new contract.")


def verify(tasks, task_id):
    matches = [t for t in tasks if t["id"] == task_id]
    if not matches:
        raise ValueError(f"Unknown task: {task_id}")
    task = matches[0]
    path = ROOT / task["test_file"]
    if not path.is_file():
        raise RuntimeError(f"BLOCKED: missing {task['test_file']}; write behavioral tests before claiming completion")
    sys.path.insert(0, str(ROOT))
    suite = unittest.defaultTestLoader.discover(str(path.parent), pattern=path.name)
    if suite.countTestCases() == 0:
        raise RuntimeError("BLOCKED: test discovery found zero tests")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful() or result.testsRun == len(result.skipped):
        raise RuntimeError("Verification failed or every test was skipped")
    print(f"PASS: {task_id} behavioral tests; human review still required.")
    print("Record command, commit/diff, test count and limitations in progress.md.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["status", "check", "verify"])
    parser.add_argument("task_id", nargs="?")
    args = parser.parse_args()
    try:
        tasks = load_tasks()
        if args.action == "status":
            status(tasks)
        elif args.action == "check":
            check(tasks)
        elif not args.task_id:
            parser.error("verify requires TASK_ID")
        else:
            verify(tasks, args.task_id)
    except (ValueError, KeyError, OSError, RuntimeError, ImportError, SyntaxError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
