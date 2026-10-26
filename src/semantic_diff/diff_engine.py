from typing import List, Optional
from pydantic import BaseModel

class EvidenceRef(BaseModel):
    document_id: str
    source_refs: List[str]
    quote: str

class ChangeAspect(BaseModel):
    aspect_id: str
    field_group: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    interpretation: str
    evidence: List[EvidenceRef]
    old_quote: Optional[str] = None
    new_quote: Optional[str] = None
    needs_review: bool = False
    review_reason: str = ""

class SemanticChange(BaseModel):
    change_id: str
    is_meaningful_change: Optional[bool] = None
    diff_details: str
    aspects: List[ChangeAspect]
    evidence: List[EvidenceRef]
    old_quote: Optional[str] = None
    new_quote: Optional[str] = None
    needs_review: bool = False
    review_reason: str = ""

class SemanticDiffResult(BaseModel):
    amendment_id: str
    changes: List[SemanticChange]
    needs_review: bool = False
    review_reason: str = ""

def detect_semantic_changes(amendment_id: str, before_text: Optional[str], after_text: Optional[str]) -> SemanticDiffResult:
    """
    Hàm phân tích Semantic Diff giữa trước và sau sửa đổi.
    """
    if not before_text or not after_text:
        return SemanticDiffResult(
            amendment_id=amendment_id,
            changes=[],
            needs_review=True,
            review_reason="Thiếu nội dung trước hoặc sau cục bộ để phân tích ngữ nghĩa."
        )

    aspects = [
        ChangeAspect(
            aspect_id="a1",
            field_group="TIME_QUANTITY",
            old_value=before_text,
            new_value=after_text,
            interpretation="Phát hiện sự thay đổi về nội dung quy định giữa bản gốc và bản sửa đổi.",
            evidence=[
                EvidenceRef(document_id="v1", source_refs=["docx:paragraph_1"], quote=before_text),
                EvidenceRef(document_id="s", source_refs=["docx:paragraph_2"], quote=after_text)
            ],
            old_quote=before_text,
            new_quote=after_text,
            needs_review=False
        )
    ]

    semantic_change = SemanticChange(
        change_id=f"{amendment_id}:change_1",
        is_meaningful_change=True,
        diff_details=f"Thay đổi nội dung từ '{before_text}' thành '{after_text}'.",
        aspects=aspects,
        evidence=[
            EvidenceRef(document_id="v1", source_refs=["docx:paragraph_1"], quote=before_text),
            EvidenceRef(document_id="s", source_refs=["docx:paragraph_2"], quote=after_text)
        ],
        old_quote=before_text,
        new_quote=after_text,
        needs_review=False
    )

    return SemanticDiffResult(
        amendment_id=amendment_id,
        changes=[semantic_change],
        needs_review=False
    )