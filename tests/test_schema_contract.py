"""Behavioral tests for W6-SCHEMA: SRS-compliant schema and fixtures.

Verifies:
- Schema has ChangeAspect, DocumentIdentity and ComparisonReport per SRS.
- Fixtures cover SUCCESS, PARTIAL and undetermined; null differs from empty list.
- Field_group values are valid; constants are consistent.
"""
from __future__ import annotations

import sys
import unittest
from dataclasses import fields as dc_fields
from pathlib import Path

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.schemas import (
    # Dataclass types
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
    # Constants
    FIELD_GROUPS,
    WORDING_ONLY,
    STATUS_SUCCESS,
    STATUS_PARTIAL,
    STATUS_FAILED,
    ALIGN_PAIRED,
    ALIGN_ADDED,
    ALIGN_DELETED,
    TEXT_INSERT,
    TEXT_DELETE,
    TEXT_REPLACE,
    SIG_LOW,
    SIG_MEDIUM,
    SIG_HIGH,
    SIG_CRITICAL,
)
from tests.fixtures import (
    make_clause_v1,
    make_clause_v2,
    make_success_report,
    make_partial_report,
    make_undetermined_report,
    make_added_pair,
    make_deleted_pair,
)


# ── 1. Schema structure tests ────────────────────────────────────────

class TestClauseSchema(unittest.TestCase):
    """SRS §1.1: Clause has unit_id, id, title, content, source_refs."""

    def test_clause_fields(self):
        names = {f.name for f in dc_fields(Clause)}
        self.assertEqual(names, {"unit_id", "id", "title", "content", "source_refs"})

    def test_clause_construction(self):
        c = make_clause_v1()
        self.assertEqual(c.unit_id, "v1:article_10")
        self.assertEqual(c.id, "Điều 10")
        self.assertIsInstance(c.source_refs, list)
        self.assertTrue(len(c.source_refs) > 0)


class TestAlignedPairSchema(unittest.TestCase):
    """SRS §1.2: AlignedPair structure and invariants."""

    def test_paired_has_both(self):
        c1, c2 = make_clause_v1(), make_clause_v2()
        pair = AlignedPair(
            pair_key="k", align_type=ALIGN_PAIRED, v1=c1, v2=c2
        )
        self.assertIsNotNone(pair.v1)
        self.assertIsNotNone(pair.v2)

    def test_added_v1_is_none(self):
        c2 = make_clause_v2()
        pair = AlignedPair(
            pair_key="k", align_type=ALIGN_ADDED, v1=None, v2=c2
        )
        self.assertIsNone(pair.v1)
        self.assertIsNotNone(pair.v2)

    def test_deleted_v2_is_none(self):
        c1 = make_clause_v1()
        pair = AlignedPair(
            pair_key="k", align_type=ALIGN_DELETED, v1=c1, v2=None
        )
        self.assertIsNotNone(pair.v1)
        self.assertIsNone(pair.v2)

    def test_needs_review_default_false(self):
        pair = AlignedPair(
            pair_key="k", align_type=ALIGN_PAIRED,
            v1=make_clause_v1(), v2=make_clause_v2(),
        )
        self.assertFalse(pair.needs_review)
        self.assertEqual(pair.review_reason, "")


class TestChangeAspectSchema(unittest.TestCase):
    """SRS §1.3: ChangeAspect has required fields and valid field_group."""

    def test_required_fields(self):
        names = {f.name for f in dc_fields(ChangeAspect)}
        expected = {
            "aspect_id", "field_group", "old_value", "new_value",
            "interpretation", "old_quote", "new_quote",
            "needs_review", "review_reason",
        }
        self.assertEqual(names, expected)

    def test_field_group_values(self):
        """All 8 field_group codes are present."""
        self.assertEqual(len(FIELD_GROUPS), 8)
        self.assertIn("TIME_QUANTITY", FIELD_GROUPS)
        self.assertIn("SUBJECT_OBJECT", FIELD_GROUPS)
        self.assertIn("CONSEQUENCES_SANCTIONS", FIELD_GROUPS)

    def test_field_group_none_allowed(self):
        a = ChangeAspect(
            aspect_id="x", field_group=None,
            old_value=None, new_value=None,
            interpretation="Chưa phân nhóm được.",
            needs_review=True,
            review_reason="Chưa rõ nhóm.",
        )
        self.assertIsNone(a.field_group)
        self.assertTrue(a.needs_review)


class TestSemanticChangeSchema(unittest.TestCase):
    """SRS §1.3: SemanticChange and is_meaningful_change tri-state."""

    def test_is_meaningful_change_can_be_none(self):
        sc = SemanticChange(
            change_id="c", is_meaningful_change=None,
            diff_details="Chưa xác định.",
            needs_review=True,
            review_reason="Thiếu ngữ cảnh.",
        )
        self.assertIsNone(sc.is_meaningful_change)

    def test_is_meaningful_change_true(self):
        sc = SemanticChange(
            change_id="c", is_meaningful_change=True,
            diff_details="Đổi thời hạn.",
        )
        self.assertTrue(sc.is_meaningful_change)

    def test_is_meaningful_change_false(self):
        sc = SemanticChange(
            change_id="c", is_meaningful_change=False,
            diff_details="Sửa diễn đạt.",
        )
        self.assertFalse(sc.is_meaningful_change)


class TestScoringResultSchema(unittest.TestCase):
    """SRS §1.4: ScoringResult with nullable fields."""

    def test_required_fields(self):
        names = {f.name for f in dc_fields(ScoringResult)}
        expected = {
            "change_id", "category", "significance", "is_critical",
            "reason", "needs_review", "review_reason",
        }
        self.assertEqual(names, expected)

    def test_critical_iff_significance_critical(self):
        sr = ScoringResult(
            change_id="c", category="TIME_QUANTITY",
            significance=SIG_CRITICAL, is_critical=True,
            reason="Test.",
        )
        self.assertTrue(sr.is_critical)
        self.assertEqual(sr.significance, SIG_CRITICAL)

    def test_null_when_undetermined(self):
        sr = ScoringResult(
            change_id="c", category=None,
            significance=None, is_critical=None,
            reason="Chưa xác định.",
            needs_review=True,
            review_reason="is_meaningful_change = None.",
        )
        self.assertIsNone(sr.significance)
        self.assertIsNone(sr.is_critical)
        self.assertIsNone(sr.category)
        self.assertTrue(sr.needs_review)

    def test_wording_only_category(self):
        sr = ScoringResult(
            change_id="c", category=WORDING_ONLY,
            significance=SIG_LOW, is_critical=False,
            reason="Chỉ sửa văn phong.",
        )
        self.assertEqual(sr.category, "WORDING_ONLY")
        self.assertEqual(sr.significance, "LOW")


class TestDocumentIdentitySchema(unittest.TestCase):
    """SRS §1.7: DocumentIdentity in ComparisonReport."""

    def test_fields(self):
        di = DocumentIdentity(version_id="v1", filename="abc.docx")
        self.assertEqual(di.version_id, "v1")
        self.assertEqual(di.filename, "abc.docx")


class TestComparisonReportSchema(unittest.TestCase):
    """SRS §1.7: ComparisonReport structure."""

    def test_required_fields(self):
        names = {f.name for f in dc_fields(ComparisonReport)}
        expected = {
            "comparison_id", "old_document", "new_document",
            "status", "results", "warnings", "errors",
        }
        self.assertEqual(names, expected)

    def test_status_constants(self):
        self.assertEqual(STATUS_SUCCESS, "SUCCESS")
        self.assertEqual(STATUS_PARTIAL, "PARTIAL")
        self.assertEqual(STATUS_FAILED, "FAILED")


class TestExtractedDocumentSchema(unittest.TestCase):
    """SRS §1.5: ExtractedDocument and SourceBlock."""

    def test_source_block(self):
        sb = SourceBlock(source_ref="pdf:page_1", text="Nội dung.")
        self.assertEqual(sb.source_ref, "pdf:page_1")

    def test_extracted_document(self):
        ed = ExtractedDocument(
            version_id="v1", filename="doc.pdf", file_type="PDF_TEXT",
            blocks=[SourceBlock(source_ref="pdf:page_1", text="x")],
        )
        self.assertEqual(len(ed.blocks), 1)


class TestTextDiffSchema(unittest.TestCase):
    """SRS §1.6: TextChange and TextDiffResult."""

    def test_text_change_types(self):
        self.assertEqual(TEXT_INSERT, "INSERT")
        self.assertEqual(TEXT_DELETE, "DELETE")
        self.assertEqual(TEXT_REPLACE, "REPLACE")

    def test_text_diff_empty_changes(self):
        td = TextDiffResult(pair_key="k")
        self.assertEqual(td.changes, [])


# ── 2. Fixture behavioral tests ──────────────────────────────────────

class TestSuccessFixture(unittest.TestCase):
    """SUCCESS fixture: deadline 30 → 15."""

    def setUp(self):
        self.report = make_success_report()

    def test_status_success(self):
        self.assertEqual(self.report.status, STATUS_SUCCESS)

    def test_document_identity(self):
        self.assertEqual(self.report.old_document.version_id, "v1")
        self.assertEqual(self.report.new_document.version_id, "v2")
        self.assertTrue(len(self.report.old_document.filename) > 0)

    def test_one_pair_result(self):
        self.assertEqual(len(self.report.results), 1)

    def test_pair_is_paired(self):
        pr = self.report.results[0]
        self.assertEqual(pr.alignment.align_type, ALIGN_PAIRED)
        self.assertIsNotNone(pr.alignment.v1)
        self.assertIsNotNone(pr.alignment.v2)

    def test_text_diff_present(self):
        pr = self.report.results[0]
        self.assertIsNotNone(pr.text_diff)
        self.assertEqual(len(pr.text_diff.changes), 1)
        self.assertEqual(pr.text_diff.changes[0].type, TEXT_REPLACE)

    def test_semantic_diff_meaningful(self):
        pr = self.report.results[0]
        self.assertIsNotNone(pr.semantic_diff)
        self.assertEqual(len(pr.semantic_diff.changes), 1)
        sc = pr.semantic_diff.changes[0]
        self.assertTrue(sc.is_meaningful_change)
        self.assertEqual(len(sc.aspects), 1)
        self.assertEqual(sc.aspects[0].field_group, "TIME_QUANTITY")

    def test_scoring_present(self):
        pr = self.report.results[0]
        self.assertIsNotNone(pr.scoring)
        self.assertIsInstance(pr.scoring, list)
        self.assertEqual(len(pr.scoring), 1)
        self.assertEqual(pr.scoring[0].significance, SIG_HIGH)
        self.assertFalse(pr.scoring[0].is_critical)

    def test_scoring_change_id_links_to_semantic_change(self):
        """SRS §1.4 / §1.7: ScoringResult.change_id phải tham chiếu change_id của SemanticChange."""
        pr = self.report.results[0]
        change_ids = {sc.change_id for sc in pr.semantic_diff.changes}
        self.assertTrue(len(change_ids) > 0)
        for sr in pr.scoring:
            self.assertIn(sr.change_id, change_ids)

    def test_evidence_quotes_match_clause_content(self):
        """SRS §1.3: old_quote / new_quote phải là đoạn trích nguyên văn từ Clause."""
        pr = self.report.results[0]
        v1_text = f"{pr.alignment.v1.title}\n{pr.alignment.v1.content}"
        v2_text = f"{pr.alignment.v2.title}\n{pr.alignment.v2.content}"
        sc = pr.semantic_diff.changes[0]
        self.assertIn(sc.old_quote, v1_text)
        self.assertIn(sc.new_quote, v2_text)
        for aspect in sc.aspects:
            if aspect.old_quote:
                self.assertIn(aspect.old_quote, v1_text)
            if aspect.new_quote:
                self.assertIn(aspect.new_quote, v2_text)

    def test_source_refs_present_and_formatted(self):
        """SRS §1.1 / §1.5: Vị trí nguồn phải có tiền tố rõ ràng (docx: hoặc pdf:)."""
        pr = self.report.results[0]
        self.assertTrue(len(pr.alignment.v1.source_refs) > 0)
        self.assertTrue(len(pr.alignment.v2.source_refs) > 0)
        for ref in pr.alignment.v1.source_refs:
            self.assertTrue(ref.startswith(("docx:", "pdf:")))
        for ref in pr.alignment.v2.source_refs:
            self.assertTrue(ref.startswith(("docx:", "pdf:")))

    def test_text_diff_offsets_slice_exact_content(self):
        """SRS §1.6: Vị trí [start, end) phải khớp chính xác chuỗi của Clause tương ứng."""
        pr = self.report.results[0]
        c1 = pr.alignment.v1
        c2 = pr.alignment.v2
        for change in pr.text_diff.changes:
            target_v1 = getattr(c1, change.field)
            target_v2 = getattr(c2, change.field)
            self.assertEqual(target_v1[change.old_start:change.old_end], change.old_text)
            self.assertEqual(target_v2[change.new_start:change.new_end], change.new_text)

    def test_no_warnings_no_errors(self):
        self.assertEqual(len(self.report.warnings), 0)
        self.assertEqual(len(self.report.errors), 0)


class TestPartialFixture(unittest.TestCase):
    """PARTIAL fixture: scoring = None (failed step)."""

    def setUp(self):
        self.report = make_partial_report()

    def test_status_partial(self):
        self.assertEqual(self.report.status, STATUS_PARTIAL)

    def test_scoring_is_none_not_empty_list(self):
        """SRS: null khác danh sách rỗng."""
        pr = self.report.results[0]
        self.assertIsNone(pr.scoring)

    def test_has_error(self):
        self.assertTrue(len(self.report.errors) > 0)
        self.assertEqual(self.report.errors[0].stage, "scorer")

    def test_semantic_diff_still_present(self):
        pr = self.report.results[0]
        self.assertIsNotNone(pr.semantic_diff)


class TestUndeterminedFixture(unittest.TestCase):
    """Undetermined: is_meaningful_change = None, significance = None."""

    def setUp(self):
        self.report = make_undetermined_report()

    def test_meaningful_change_is_none(self):
        sc = self.report.results[0].semantic_diff.changes[0]
        self.assertIsNone(sc.is_meaningful_change)

    def test_scoring_significance_is_none(self):
        sr = self.report.results[0].scoring[0]
        self.assertIsNone(sr.significance)
        self.assertIsNone(sr.is_critical)
        self.assertIsNone(sr.category)

    def test_needs_review_propagated(self):
        pr = self.report.results[0]
        self.assertTrue(pr.semantic_diff.needs_review)
        self.assertTrue(pr.scoring[0].needs_review)

    def test_aspects_empty_but_not_false_conclusion(self):
        """SRS: aspects rỗng + is_meaningful_change=None ≠ 'không có thay đổi'."""
        sc = self.report.results[0].semantic_diff.changes[0]
        self.assertEqual(sc.aspects, [])
        self.assertIsNone(sc.is_meaningful_change)  # NOT False


class TestNullVsEmptyList(unittest.TestCase):
    """SRS requirement: null ≠ empty list for scoring and changes."""

    def test_scoring_none_means_step_failed(self):
        pr = PairResult(
            alignment=AlignedPair(
                pair_key="k", align_type=ALIGN_PAIRED,
                v1=make_clause_v1(), v2=make_clause_v2(),
            ),
            scoring=None,
        )
        self.assertIsNone(pr.scoring)

    def test_scoring_empty_list_means_nothing_to_score(self):
        pr = PairResult(
            alignment=AlignedPair(
                pair_key="k", align_type=ALIGN_PAIRED,
                v1=make_clause_v1(), v2=make_clause_v2(),
            ),
            scoring=[],
        )
        self.assertIsNotNone(pr.scoring)
        self.assertEqual(len(pr.scoring), 0)

    def test_changes_empty_means_no_change_found(self):
        sdr = SemanticDiffResult(pair_key="k", changes=[])
        self.assertEqual(sdr.changes, [])


class TestAddedDeletedFixtures(unittest.TestCase):
    """ADDED and DELETED pair fixtures."""

    def test_added_v1_none(self):
        pr = make_added_pair()
        self.assertEqual(pr.alignment.align_type, ALIGN_ADDED)
        self.assertIsNone(pr.alignment.v1)
        self.assertIsNotNone(pr.alignment.v2)

    def test_deleted_v2_none(self):
        pr = make_deleted_pair()
        self.assertEqual(pr.alignment.align_type, ALIGN_DELETED)
        self.assertIsNotNone(pr.alignment.v1)
        self.assertIsNone(pr.alignment.v2)


if __name__ == "__main__":
    unittest.main()

