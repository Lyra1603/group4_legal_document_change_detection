from typing import List, Dict, Any
from src.schemas import AlignedPair

def evaluate_predictions(predictions: List[AlignedPair], ground_truth: Dict[str, Dict[str, bool]]) -> Dict[str, Any]:
    """
    Tính toán các chỉ số đánh giá theo Evaluation Plan:
    - Change Detection Precision / Recall / F1 (Target F1 >= 0.90)
    - Critical Change Recall (Target >= 95%)
    """
    tp_change, fp_change, fn_change = 0, 0, 0
    tp_critical, fn_critical = 0, 0

    for pred in predictions:
        key = pred["pair_key"]
        if key not in ground_truth or not pred["semantic_diff"] or not pred["scoring"]:
            continue
        gt = ground_truth[key]

        pred_change = pred["semantic_diff"]["is_meaningful_change"]
        actual_change = gt["is_meaningful_change"]
        if pred_change and actual_change: tp_change += 1
        elif pred_change and not actual_change: fp_change += 1
        elif not pred_change and actual_change: fn_change += 1

        pred_crit = pred["scoring"]["is_critical"]
        actual_crit = gt["is_critical"]
        if actual_crit:
            if pred_crit: tp_critical += 1
            else: fn_critical += 1

    precision = tp_change / (tp_change + fp_change) if (tp_change + fp_change) > 0 else 0.0
    recall = tp_change / (tp_change + fn_change) if (tp_change + fn_change) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    critical_recall = tp_critical / (tp_critical + fn_critical) if (tp_critical + fn_critical) > 0 else 0.0

    return {
        "Change_Detection_Precision": round(precision, 4),
        "Change_Detection_Recall": round(recall, 4),
        "Change_Detection_F1": round(f1, 4),
        "Critical_Change_Recall": round(critical_recall, 4)
    }