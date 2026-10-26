from typing import List, Optional
from pydantic import BaseModel

class ScoringResult(BaseModel):
    change_id: str
    category: str              # Ví dụ: ADMINISTRATIVE, FINANCIAL, TECHNICAL, v.v.
    significance: str          # Ví dụ: MAJOR, MINOR
    impact_score: float        # Điểm số đánh giá từ 0.0 đến 1.0
    rationale: str             # Giải thích lý do phân loại và chấm điểm
    needs_review: bool = False
    review_reason: str = ""

def classify_and_score(change_id: str, aspects: List[dict], diff_details: str) -> ScoringResult:
    """
    Hàm phân loại danh mục và chấm mức độ nghiêm trọng (Scorer) cho một SemanticChange.
    """
    # Logic baseline phân loại và chấm điểm dựa trên độ dài hoặc nội dung thay đổi
    is_major = len(diff_details) > 20
    significance = "MAJOR" if is_major else "MINOR"
    impact_score = 0.8 if is_major else 0.3

    return ScoringResult(
        change_id=change_id,
        category="REGULATORY_COMPLIANCE",  # Danh mục mặc định theo SRS
        significance=significance,
        impact_score=impact_score,
        rationale=f"Đã phân tích dựa trên chi tiết thay đổi: '{diff_details}'. Đánh giá mức độ tác động: {significance}.",
        needs_review=False,
        review_reason=""
    )