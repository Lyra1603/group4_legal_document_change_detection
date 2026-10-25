import json
from pathlib import Path
import unittest

from src.evaluation.evaluator import evaluate_predictions


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "data" / "T1"


def prediction(pair_key: str, meaningful: bool, critical: bool) -> dict:
    return {
        "pair_key": pair_key,
        "v1": None,
        "v2": None,
        "align_type": "PAIRED",
        "similarity_score": 1.0,
        "semantic_diff": {
            "is_meaningful_change": meaningful,
            "diff_details": "",
        },
        "scoring": {
            "category": "TEST",
            "significance": "CRITICAL" if critical else "LOW",
            "is_critical": critical,
        },
    }


def load_gold() -> list[dict]:
    return [
        json.loads((case / "gold.json").read_text(encoding="utf-8"))
        for case in sorted(FIXTURE_ROOT.iterdir())
        if case.is_dir()
    ]


class EvaluatorTests(unittest.TestCase):
    def test_pilot_gold_cases_are_evaluable(self) -> None:
        gold = load_gold()
        predictions = [
            prediction(
                item["baseline_pair_key"],
                item["expected_meaningful_change"],
                item["expected_critical"],
            )
            for item in gold
        ]
        ground_truth = {
            item["baseline_pair_key"]: {
                "is_meaningful_change": item["expected_meaningful_change"],
                "is_critical": item["expected_critical"],
            }
            for item in gold
        }

        metrics = evaluate_predictions(predictions, ground_truth)

        self.assertEqual(metrics["Change_Detection_Precision"], 1.0)
        self.assertEqual(metrics["Change_Detection_Recall"], 1.0)
        self.assertEqual(metrics["Change_Detection_F1"], 1.0)
        self.assertEqual(metrics["Critical_Change_Recall"], 1.0)

    def test_false_positive_and_false_negative_are_counted(self) -> None:
        predictions = [
            prediction("changed", True, True),
            prediction("unchanged", True, False),
            prediction("missed", False, False),
        ]
        ground_truth = {
            "changed": {"is_meaningful_change": True, "is_critical": True},
            "unchanged": {"is_meaningful_change": False, "is_critical": False},
            "missed": {"is_meaningful_change": True, "is_critical": True},
        }

        metrics = evaluate_predictions(predictions, ground_truth)

        self.assertEqual(metrics["Change_Detection_Precision"], 0.5)
        self.assertEqual(metrics["Change_Detection_Recall"], 0.5)
        self.assertEqual(metrics["Change_Detection_F1"], 0.5)
        self.assertEqual(metrics["Critical_Change_Recall"], 0.5)

    def test_zero_denominators_return_zero(self) -> None:
        metrics = evaluate_predictions([], {})

        self.assertEqual(metrics["Change_Detection_Precision"], 0.0)
        self.assertEqual(metrics["Change_Detection_Recall"], 0.0)
        self.assertEqual(metrics["Change_Detection_F1"], 0.0)
        self.assertEqual(metrics["Critical_Change_Recall"], 0.0)

    def test_missing_prediction_fields_are_skipped_by_baseline(self) -> None:
        incomplete = prediction("incomplete", True, True)
        incomplete["semantic_diff"] = None

        metrics = evaluate_predictions(
            [incomplete],
            {"incomplete": {"is_meaningful_change": True, "is_critical": True}},
        )

        self.assertEqual(metrics["Change_Detection_F1"], 0.0)
        self.assertEqual(metrics["Critical_Change_Recall"], 0.0)


if __name__ == "__main__":
    unittest.main()
