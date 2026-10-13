"""Fixture factory for SRS-compliant schema objects.

Produces ready-made instances for SUCCESS, PARTIAL and undetermined scenarios.
Each builder accepts keyword overrides so tests can tweak individual fields.
"""
from __future__ import annotations

from src.schemas import (
    Clause,
    AlignedPair,
    ChangeAspect,
    SemanticChange,
    SemanticDiffResult,
    ScoringResult,
    SourceBlock,
    ExtractedDocument,
    TextChange,
    TextDiffResult,
    PairResult,
    ProcessingIssue,
    DocumentIdentity,
    ComparisonReport,
    ALIGN_PAIRED,
    ALIGN_ADDED,
    ALIGN_DELETED,
    STATUS_SUCCESS,
    STATUS_PARTIAL,
    STATUS_FAILED,
    SIG_HIGH,
    WORDING_ONLY,
    SIG_LOW,
    TEXT_REPLACE,
)


# ── Clause helpers ────────────────────────────────────────────────────

def make_clause_v1(**kw) -> Clause:
    defaults = dict(
        unit_id="v1:article_10",
        id="Điều 10",
        title="Thời hạn nộp hồ sơ",
        content="Tổ chức phải nộp hồ sơ trong 30 ngày.",
        source_refs=["docx:paragraph_42"],
    )
    defaults.update(kw)
    return Clause(**defaults)


def make_clause_v2(**kw) -> Clause:
    defaults = dict(
        unit_id="v2:article_10",
        id="Điều 10",
        title="Thời hạn nộp hồ sơ",
        content="Tổ chức phải nộp hồ sơ trong 15 ngày.",
        source_refs=["docx:paragraph_45"],
    )
    defaults.update(kw)
    return Clause(**defaults)


# ── SUCCESS fixture: deadline 30 → 15 ────────────────────────────────

def make_success_report(**kw) -> ComparisonReport:
    """Báo cáo SUCCESS hoàn chỉnh: một cặp Điều, thay đổi thời hạn."""
    c1 = make_clause_v1()
    c2 = make_clause_v2()

    alignment = AlignedPair(
        pair_key="v1:article_10::v2:article_10",
        align_type=ALIGN_PAIRED,
        v1=c1,
        v2=c2,
    )
    text_diff = TextDiffResult(
        pair_key=alignment.pair_key,
        changes=[
            TextChange(
                field="content",
                type=TEXT_REPLACE,
                old_text="30",
                new_text="15",
                old_start=29,
                old_end=31,
                new_start=29,
                new_end=31,
            )
        ],
    )
    aspect = ChangeAspect(
        aspect_id="a1",
        field_group="TIME_QUANTITY",
        old_value="30 ngày",
        new_value="15 ngày",
        interpretation="Rút ngắn thời hạn nộp hồ sơ từ 30 xuống 15 ngày.",
        old_quote="trong 30 ngày",
        new_quote="trong 15 ngày",
    )
    sem_change = SemanticChange(
        change_id="chg-001",
        is_meaningful_change=True,
        diff_details="Rút ngắn thời hạn nộp hồ sơ từ 30 ngày xuống 15 ngày.",
        aspects=[aspect],
        old_quote="Tổ chức phải nộp hồ sơ trong 30 ngày.",
        new_quote="Tổ chức phải nộp hồ sơ trong 15 ngày.",
    )
    sem_diff = SemanticDiffResult(
        pair_key=alignment.pair_key,
        changes=[sem_change],
    )
    scoring = [
        ScoringResult(
            change_id="chg-001",
            category="TIME_QUANTITY",
            significance=SIG_HIGH,
            is_critical=False,
            reason="Rút ngắn thời hạn nộp hồ sơ 50%; ảnh hưởng quy trình.",
        )
    ]
    pair_result = PairResult(
        alignment=alignment,
        text_diff=text_diff,
        semantic_diff=sem_diff,
        scoring=scoring,
    )
    defaults = dict(
        comparison_id="cmp-001",
        old_document=DocumentIdentity(version_id="v1", filename="luat-2020.docx"),
        new_document=DocumentIdentity(version_id="v2", filename="luat-2025.docx"),
        status=STATUS_SUCCESS,
        results=[pair_result],
    )
    defaults.update(kw)
    return ComparisonReport(**defaults)


# ── PARTIAL fixture: scoring failed ───────────────────────────────────

def make_partial_report(**kw) -> ComparisonReport:
    """Báo cáo PARTIAL: semantic_diff xong nhưng scoring = None (lỗi)."""
    c1 = make_clause_v1()
    c2 = make_clause_v2()
    alignment = AlignedPair(
        pair_key="v1:article_10::v2:article_10",
        align_type=ALIGN_PAIRED,
        v1=c1,
        v2=c2,
    )
    sem_diff = SemanticDiffResult(
        pair_key=alignment.pair_key,
        changes=[
            SemanticChange(
                change_id="chg-001",
                is_meaningful_change=True,
                diff_details="Thay đổi thời hạn.",
                old_quote="trong 30 ngày",
                new_quote="trong 15 ngày",
            )
        ],
    )
    pair_result = PairResult(
        alignment=alignment,
        semantic_diff=sem_diff,
        scoring=None,  # bước scoring thất bại
    )
    error = ProcessingIssue(
        stage="scorer",
        code="SCORER_TIMEOUT",
        message="Scoring bị timeout.",
        pair_key=alignment.pair_key,
    )
    defaults = dict(
        comparison_id="cmp-002",
        old_document=DocumentIdentity(version_id="v1", filename="luat-2020.docx"),
        new_document=DocumentIdentity(version_id="v2", filename="luat-2025.docx"),
        status=STATUS_PARTIAL,
        results=[pair_result],
        errors=[error],
    )
    defaults.update(kw)
    return ComparisonReport(**defaults)


# ── Undetermined fixture ──────────────────────────────────────────────

def make_undetermined_report(**kw) -> ComparisonReport:
    """Báo cáo SUCCESS nhưng có kết quả chưa xác định (is_meaningful_change = None)."""
    c1 = make_clause_v1(content="Áp dụng theo quy định hiện hành.")
    c2 = make_clause_v2(content="Áp dụng theo quy định pháp luật.")
    alignment = AlignedPair(
        pair_key="v1:article_10::v2:article_10",
        align_type=ALIGN_PAIRED,
        v1=c1,
        v2=c2,
    )
    sem_change = SemanticChange(
        change_id="chg-003",
        is_meaningful_change=None,
        diff_details="Thay 'quy định hiện hành' bằng 'quy định pháp luật'; chưa rõ đổi nghĩa.",
        aspects=[],
        old_quote="quy định hiện hành",
        new_quote="quy định pháp luật",
        needs_review=True,
        review_reason="Chưa đủ ngữ cảnh để xác định đây là sửa diễn đạt hay đổi phạm vi.",
    )
    sem_diff = SemanticDiffResult(
        pair_key=alignment.pair_key,
        changes=[sem_change],
        needs_review=True,
        review_reason="Có thay đổi chưa xác định.",
    )
    scoring = [
        ScoringResult(
            change_id="chg-003",
            category=None,
            significance=None,
            is_critical=None,
            reason="Chưa xác định mức độ.",
            needs_review=True,
            review_reason="is_meaningful_change chưa xác định.",
        )
    ]
    pair_result = PairResult(
        alignment=alignment,
        semantic_diff=sem_diff,
        scoring=scoring,
    )
    defaults = dict(
        comparison_id="cmp-003",
        old_document=DocumentIdentity(version_id="v1", filename="luat-2020.docx"),
        new_document=DocumentIdentity(version_id="v2", filename="luat-2025.docx"),
        status=STATUS_SUCCESS,
        results=[pair_result],
    )
    defaults.update(kw)
    return ComparisonReport(**defaults)


# ── ADDED / DELETED fixture ──────────────────────────────────────────

def make_added_pair(**kw) -> PairResult:
    """Điều chỉ có ở v2 (thêm mới)."""
    c2 = make_clause_v2(unit_id="v2:article_99", id="Điều 99",
                        title="Điều mới", content="Nội dung mới.")
    alignment = AlignedPair(
        pair_key="None::v2:article_99",
        align_type=ALIGN_ADDED,
        v1=None,
        v2=c2,
    )
    return PairResult(alignment=alignment)


def make_deleted_pair(**kw) -> PairResult:
    """Điều chỉ có ở v1 (bị xóa)."""
    c1 = make_clause_v1(unit_id="v1:article_88", id="Điều 88",
                        title="Điều cũ", content="Nội dung cũ.")
    alignment = AlignedPair(
        pair_key="v1:article_88::None",
        align_type=ALIGN_DELETED,
        v1=c1,
        v2=None,
    )
    return PairResult(alignment=alignment)

