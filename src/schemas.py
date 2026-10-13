"""SRS-compliant data structures for the legal document change detection pipeline.

This module defines the schema as specified in docs/srs.md sections 1.1–1.7.
The old TypedDict schema in this file is preserved for baseline compatibility;
downstream modules will migrate in their own tasks (W6-UPLOAD, W6-READER, etc.).

Naming convention: new dataclass names match the SRS exactly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List

# ── 8 field_group codes (SRS §1.3) ────────────────────────────────────
FIELD_GROUPS: set[str] = {
    "SUBJECT_OBJECT",
    "RIGHTS_DUTIES_ACTIONS",
    "CONDITIONS_EXCEPTIONS",
    "TIME_QUANTITY",
    "PROCEDURE_AUTHORITY",
    "CONSEQUENCES_SANCTIONS",
    "DEFINITIONS_REFERENCES",
    "SCOPE_EFFECT_TRANSITION",
}

# Category used for scoring when wording changed but meaning did not (SRS §1.4)
WORDING_ONLY = "WORDING_ONLY"

# ComparisonReport statuses (SRS §1.7)
STATUS_SUCCESS = "SUCCESS"
STATUS_PARTIAL = "PARTIAL"
STATUS_FAILED = "FAILED"

# AlignedPair types
ALIGN_PAIRED = "PAIRED"
ALIGN_ADDED = "ADDED"
ALIGN_DELETED = "DELETED"

# TextChange types
TEXT_INSERT = "INSERT"
TEXT_DELETE = "DELETE"
TEXT_REPLACE = "REPLACE"

# Significance levels (SRS §1.4)
SIG_LOW = "LOW"
SIG_MEDIUM = "MEDIUM"
SIG_HIGH = "HIGH"
SIG_CRITICAL = "CRITICAL"


# ── §1.1 Clause ───────────────────────────────────────────────────────
@dataclass
class Clause:
    """Một Điều trong một phiên bản văn bản."""
    unit_id: str                      # Duy nhất trong phiên bản, vd "v1:article_5"
    id: str                           # Nhãn Điều, vd "Điều 5"
    title: str                        # "" nếu không có tiêu đề
    content: str                      # Giữ Khoản/Điểm và thứ tự
    source_refs: List[str] = field(default_factory=list)  # Vị trí nguồn


# ── §1.2 AlignedPair ──────────────────────────────────────────────────
@dataclass
class AlignedPair:
    """Cặp Điều được căn chỉnh giữa v1 và v2."""
    pair_key: str                     # Định danh cặp
    align_type: str                   # PAIRED | ADDED | DELETED
    v1: Optional[Clause]              # None khi ADDED
    v2: Optional[Clause]              # None khi DELETED
    needs_review: bool = False
    review_reason: str = ""


# ── §1.3 SemanticDiffResult ───────────────────────────────────────────
@dataclass
class ChangeAspect:
    """Một khía cạnh cụ thể trong một SemanticChange."""
    aspect_id: str                    # Duy nhất trong SemanticChange
    field_group: Optional[str]        # Một trong FIELD_GROUPS; None nếu chưa rõ
    old_value: Optional[str]          # Nội dung trước
    new_value: Optional[str]          # Nội dung sau
    interpretation: str               # Giải thích trước → sau
    old_quote: Optional[str] = None   # Nguyên văn phía cũ
    new_quote: Optional[str] = None   # Nguyên văn phía mới
    needs_review: bool = False
    review_reason: str = ""


@dataclass
class SemanticChange:
    """Một thay đổi quy định; có thể có nhiều ChangeAspect."""
    change_id: str
    is_meaningful_change: Optional[bool]  # True/False/None
    diff_details: str
    aspects: List[ChangeAspect] = field(default_factory=list)
    old_quote: Optional[str] = None
    new_quote: Optional[str] = None
    needs_review: bool = False
    review_reason: str = ""


@dataclass
class SemanticDiffResult:
    """Kết quả phân tích ngữ nghĩa cho một cặp Điều."""
    pair_key: str
    changes: List[SemanticChange] = field(default_factory=list)
    needs_review: bool = False
    review_reason: str = ""


# ── §1.4 ScoringResult ────────────────────────────────────────────────
@dataclass
class ScoringResult:
    """Phân loại và chấm mức độ cho một SemanticChange."""
    change_id: str
    category: Optional[str]           # field_group code | WORDING_ONLY | None
    significance: Optional[str]       # LOW | MEDIUM | HIGH | CRITICAL | None
    is_critical: Optional[bool]       # True iff significance == CRITICAL; None if unknown
    reason: str
    needs_review: bool = False
    review_reason: str = ""


# ── §1.5 ExtractedDocument ────────────────────────────────────────────
@dataclass
class SourceBlock:
    """Một đơn vị trích xuất từ file gốc."""
    source_ref: str                   # vd "pdf:page_1", "docx:paragraph_5"
    text: str


@dataclass
class ExtractedDocument:
    """Đầu ra của Reader."""
    version_id: str                   # "v1" hoặc "v2"
    filename: str
    file_type: str                    # DOCX | PDF_TEXT
    blocks: List[SourceBlock] = field(default_factory=list)


# ── §1.6 TextDiffResult ───────────────────────────────────────────────
@dataclass
class TextChange:
    """Một thay đổi text cụ thể."""
    field: str                        # title | content
    type: str                         # INSERT | DELETE | REPLACE
    old_text: str
    new_text: str
    old_start: int
    old_end: int
    new_start: int
    new_end: int


@dataclass
class TextDiffResult:
    """Đầu ra Text Diff cho một cặp Điều."""
    pair_key: str
    changes: List[TextChange] = field(default_factory=list)


# ── §1.7 ComparisonReport ─────────────────────────────────────────────
@dataclass
class PairResult:
    """Kết quả tổng hợp cho một cặp Điều."""
    alignment: AlignedPair
    text_diff: Optional[TextDiffResult] = None
    semantic_diff: Optional[SemanticDiffResult] = None
    scoring: Optional[List[ScoringResult]] = None


@dataclass
class ProcessingIssue:
    """Cảnh báo hoặc lỗi xử lý."""
    stage: str
    code: str
    message: str
    pair_key: Optional[str] = None


@dataclass
class DocumentIdentity:
    """Nhận diện một phiên bản tài liệu."""
    version_id: str                   # "v1" hoặc "v2"
    filename: str


@dataclass
class ComparisonReport:
    """Báo cáo so sánh tổng hợp — đầu ra cuối cùng của Pipeline."""
    comparison_id: str
    old_document: DocumentIdentity
    new_document: DocumentIdentity
    status: str                       # SUCCESS | PARTIAL | FAILED
    results: List[PairResult] = field(default_factory=list)
    warnings: List[ProcessingIssue] = field(default_factory=list)
    errors: List[ProcessingIssue] = field(default_factory=list)


# ── Legacy TypedDict aliases (baseline compatibility) ─────────────────
# These are used by the existing baseline modules (parser, aligner,
# diff_engine, scorer, evaluator, pipeline).  They will be removed
# when each module migrates to the dataclass schema above.
from typing import TypedDict  # noqa: E402


class LegacyClause(TypedDict):
    id: str
    title: str
    content: str


class LegacySemanticDiffResult(TypedDict):
    is_meaningful_change: bool
    diff_details: str


class LegacyScoringResult(TypedDict):
    category: str
    significance: str
    is_critical: bool


class LegacyAlignedPair(TypedDict):
    pair_key: str
    v1: Optional[LegacyClause]
    v2: Optional[LegacyClause]
    align_type: str
    similarity_score: float
    semantic_diff: Optional[LegacySemanticDiffResult]
    scoring: Optional[LegacyScoringResult]