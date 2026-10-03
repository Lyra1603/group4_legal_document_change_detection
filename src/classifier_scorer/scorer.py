from src.schemas import AlignedPair, SemanticDiffResult, ScoringResult

def classify_and_score(pair: AlignedPair, sem_diff: SemanticDiffResult) -> ScoringResult:
    """
    Phân loại thay đổi (Change classifier) và chấm mức độ quan trọng (Significance scorer).
    Mục tiêu: Đạt Critical change recall >= 95%.
    """
    if not sem_diff["is_meaningful_change"]:
        return {"category": "STYLISTIC_EDIT", "significance": "LOW", "is_critical": False}

    if pair["align_type"] == "ADDED":
        return {"category": "CLAUSE_ADDED", "significance": "MEDIUM", "is_critical": True}
    if pair["align_type"] == "DELETED":
        return {"category": "CLAUSE_DELETED", "significance": "HIGH", "is_critical": True}

    return {"category": "OBLIGATION_OR_METRIC_CHANGE", "significance": "CRITICAL", "is_critical": True}