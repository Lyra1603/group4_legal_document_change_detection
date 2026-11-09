"""Standalone boundary tests; no API, storage, model or LightRAG imports."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from backend.app.schemas.contracts import (
    AmendmentItem, AmendmentResult, AnalysisContext, ChangeAspect, Clause,
    ComparisonReport, DocumentIdentity, EffectInfo, EvidenceRef,
    ExtractedDocument, ProcessingIssue, ReferenceRequirement, ScoringResult,
    SemanticChange, SemanticDiffResult, SourceBlock, TextChange, TextDiffResult,
)
from backend.app.schemas.report_validation import (
    GROUPS, validate_amendment, validate_payload, validate_report, validate_sources,
)
from backend.app.schemas.validation import validate_extracted_document

FIXTURE = Path(__file__).resolve().parents[1] / 'fixtures' / 'reports' / 'common_contract.json'


def load_case():
    return json.loads(FIXTURE.read_text(encoding='utf-8'))


def validate_case(case):
    # These are distinct boundaries: report validation does not check the store.
    for document in case['documents'].values():
        validate_extracted_document(document)
    for result in case['report']['results']:
        validate_amendment(result['amendment'], case['documents'], case['clauses'])
    validate_sources(case['report'], case['documents'])
    validate_report(case['report'])


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.case = load_case()
        self.report = self.case['report']
        self.result = self.report['results'][0]
        self.item = self.result['amendment']
        self.change = self.result['semantic_diff']['changes'][0]
        self.aspect = self.change['aspects'][0]
        self.score = self.result['scoring'][0]

    def rejects(self):
        with self.assertRaises(ValueError):
            validate_case(self.case)

    def test_valid_complete_report_and_block_sources(self):
        validate_case(self.case)
        self.assertEqual(self.item['instruction']['source_refs'], ['block:1'])

    def test_every_contract_rejects_missing_required_field(self):
        values = [
            (ComparisonReport, self.report), (AmendmentResult, self.result),
            (AmendmentItem, self.item), (SemanticDiffResult, self.result['semantic_diff']),
            (SemanticChange, self.change), (ChangeAspect, self.aspect),
            (ScoringResult, self.score), (TextDiffResult, self.result['text_diff']),
            (TextChange, self.result['text_diff']['changes'][0]),
            (ExtractedDocument, self.case['documents']['v1']),
            (SourceBlock, self.case['documents']['v1']['blocks'][0]),
            (Clause, self.case['clauses']['v1'][0]),
            (DocumentIdentity, self.report['base_document']),
            (EvidenceRef, self.item['instruction']), (AnalysisContext, self.item['context']),
            (EffectInfo, self.item['effect_info'][0]),
            (ReferenceRequirement, self.item['context']['references'][0]),
            (ProcessingIssue, dict(stage='analysis', code='TEST', message='test', amendment_id=None)),
        ]
        for kind, value in values:
            for field in value:
                bad = deepcopy(value)
                del bad[field]
                with self.subTest(kind=kind.__name__, missing=field):
                    with self.assertRaises(ValueError):
                        validate_payload(kind, bad)

    def test_nullable_key_still_required(self):
        del self.aspect['old_value']
        self.rejects()

    def test_strict_boolean_type(self):
        self.score['is_critical'] = 0
        self.rejects()

    def test_invalid_enums(self):
        pairs = [(self.item, 'operation'), (self.item, 'applicability'),
                 (self.item, 'after_basis'), (self.report, 'status'),
                 (self.report['base_document'], 'role'), (self.score, 'significance'),
                 (self.result['text_diff']['changes'][0], 'type')]
        for node, key in pairs:
            old = node[key]
            node[key] = 'invalid'
            with self.subTest(field=key):
                self.rejects()
            node[key] = old

    def test_blank_identifiers(self):
        for node, key in [(self.report, 'comparison_id'), (self.item, 'amendment_id'),
                          (self.change, 'change_id'), (self.aspect, 'aspect_id')]:
            old = node[key]
            node[key] = '  '
            with self.subTest(field=key):
                self.rejects()
            node[key] = old

    def test_duplicate_amendment_id(self):
        self.report['results'].append(deepcopy(self.result))
        self.rejects()

    def test_duplicate_change_id_within_result(self):
        self.result['semantic_diff']['changes'].append(deepcopy(self.change))
        self.rejects()

    def test_duplicate_aspect_id(self):
        self.change['aspects'].append(deepcopy(self.aspect))
        self.rejects()

    def test_module_amendment_id_must_match(self):
        for key in ['text_diff', 'semantic_diff']:
            self.result[key]['amendment_id'] = 's:other'
            with self.subTest(module=key):
                self.rejects()
            self.result[key]['amendment_id'] = self.item['amendment_id']

    def test_document_identity_and_filename(self):
        for key, value in [('document_id', 'wrong'), ('role', 'REFERENCE'),
                           ('filename', 'C:\\private\\base.docx')]:
            old = self.report['base_document'][key]
            self.report['base_document'][key] = value
            with self.subTest(field=key):
                self.rejects()
            self.report['base_document'][key] = old

    def test_duplicate_document_ids(self):
        self.report['reference_documents'][0]['document_id'] = 'v1'
        self.rejects()

    def test_source_document_must_exist(self):
        self.item['instruction']['document_id'] = 'unknown'
        self.rejects()

    def test_source_block_must_exist(self):
        self.item['instruction']['source_refs'] = ['block:999']
        self.rejects()

    def test_empty_source_refs(self):
        self.item['instruction']['source_refs'] = []
        self.rejects()

    def test_quote_must_be_verbatim(self):
        for quote in ['', 'Không có trong nguồn', 'Doanh nghiep']:
            self.item['instruction']['quote'] = quote
            with self.subTest(quote=quote):
                self.rejects()

    def test_instruction_must_be_from_s(self):
        self.item['instruction'] = deepcopy(self.aspect['evidence'][0])
        self.rejects()

    def test_target_unit_must_exist(self):
        self.item['target_unit_ids'] = ['v1:unknown']
        self.rejects()

    def test_unresolved_target_requires_review(self):
        self.item['applicability'] = 'UNRESOLVED'
        self.item.update(needs_review=False, review_reason='')
        self.report['status'] = 'PARTIAL'
        self.rejects()

    def test_missing_target_requires_review(self):
        self.item['target_unit_ids'] = []
        self.item.update(needs_review=False, review_reason='')
        self.rejects()

    def test_reference_status_enum(self):
        self.item['context']['references'][0]['status'] = 'FOUND'
        self.rejects()

    def test_unknown_content_cannot_be_diffed(self):
        self.item['after_text'] = None
        self.item['after_basis'] = 'UNRESOLVED'
        self.rejects()

    def test_offset_slices_and_bounds(self):
        edit = self.result['text_diff']['changes'][0]
        for key, value in [('old_start', -1), ('old_end', 900), ('new_text', 'khác')]:
            old = edit[key]
            edit[key] = value
            with self.subTest(field=key):
                self.rejects()
            edit[key] = old

    def test_insert_delete_empty_side(self):
        edit = self.result['text_diff']['changes'][0]
        for op in ['INSERT', 'DELETE']:
            edit['type'] = op
            with self.subTest(operation=op):
                self.rejects()

    def test_valid_add_and_repeal(self):
        for op in ['ADD', 'REPEAL']:
            c = load_case()
            r = c['report']['results'][0]
            a = r['amendment']
            a['operation'] = op
            old, new = a['before_text'], a['after_text']
            if op == 'ADD':
                a['before_text'] = None
                a['target_unit_ids'] = []
                e = dict(type='INSERT', old_text='', new_text=new, old_start=0,
                         old_end=0, new_start=0, new_end=len(new))
            else:
                a['after_text'] = None
                a['after_basis'] = 'ABSENT'
                e = dict(type='DELETE', old_text=old, new_text='', old_start=0,
                         old_end=len(old), new_start=0, new_end=0)
            r['text_diff']['changes'] = [e]
            with self.subTest(operation=op):
                validate_case(c)

    def test_valid_groups_and_scoring_levels(self):
        self.assertEqual(len(GROUPS), 8)
        for group in GROUPS:
            self.aspect['field_group'] = self.score['category'] = group
            for level in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
                self.score['significance'] = level
                self.score['is_critical'] = level == 'CRITICAL'
                with self.subTest(group=group, level=level):
                    validate_case(self.case)

    def test_invalid_field_group_and_category(self):
        for node, key in [(self.aspect, 'field_group'), (self.score, 'category')]:
            old = node[key]
            node[key] = 'FOUR_GROUP_PLACEHOLDER'
            with self.subTest(field=key):
                self.rejects()
            node[key] = old

    def test_unknown_group_requires_review(self):
        self.aspect['field_group'] = None
        self.rejects()

    def test_resolved_aspect_requires_evidence(self):
        self.aspect['evidence'] = []
        self.rejects()

    def test_review_flag_and_reason(self):
        self.score['needs_review'] = True
        self.rejects()

    def test_aspect_warning_must_propagate(self):
        self.aspect.update(needs_review=True, review_reason='Cần đối chiếu')
        self.rejects()

    def test_change_warning_must_propagate(self):
        self.change.update(needs_review=True, review_reason='Cần đối chiếu')
        self.rejects()

    def test_unknown_meaning_requires_review(self):
        self.change['is_meaningful_change'] = None
        self.rejects()

    def test_meaningful_change_requires_aspects(self):
        self.change['aspects'] = []
        self.rejects()

    def test_one_score_per_change(self):
        for scores in [[], [deepcopy(self.score), deepcopy(self.score)]]:
            self.result['scoring'] = scores
            self.rejects()

    def test_score_must_reference_change(self):
        self.score['change_id'] = 'missing'
        self.rejects()

    def test_category_must_come_from_aspects(self):
        self.score['category'] = 'SUBJECT_OBJECT'
        self.rejects()

    def test_critical_flag_consistency(self):
        self.score['is_critical'] = True
        self.rejects()

    def test_null_significance_requires_null_critical_and_review(self):
        self.score['significance'] = None
        self.rejects()
        self.score.update(is_critical=None, needs_review=True, review_reason='Chưa đủ căn cứ')
        validate_case(self.case)

    def test_unknown_meaning_cannot_be_scored(self):
        self.change.update(is_meaningful_change=None, needs_review=True, review_reason='Chưa rõ')
        self.result['semantic_diff'].update(needs_review=True, review_reason='Chưa rõ')
        self.score.update(needs_review=True, review_reason='Chưa rõ')
        self.rejects()
        self.score.update(significance=None, is_critical=None)
        validate_case(self.case)

    def test_wording_only_requires_no_aspects_low_and_wording_category(self):
        self.change.update(is_meaningful_change=False, aspects=[])
        self.rejects()
        self.score.update(category='WORDING_ONLY', significance='LOW', is_critical=False)
        validate_case(self.case)
        self.score.update(significance='HIGH')
        self.rejects()

    def test_success_cannot_have_errors(self):
        self.report['errors'] = [dict(stage='semantic', code='FAILED', message='Lỗi', amendment_id='s:a1')]
        self.rejects()

    def test_success_cannot_have_incomplete_applicable_analysis(self):
        for key in ['text_diff', 'semantic_diff', 'scoring']:
            old = self.result[key]
            self.result[key] = None
            with self.subTest(module=key):
                self.rejects()
            self.result[key] = old

    def test_partial_preserves_amendment_with_null_steps(self):
        self.report['status'] = 'PARTIAL'
        for key in ['text_diff', 'semantic_diff', 'scoring']:
            self.result[key] = None
        self.report['warnings'] = [dict(stage='analysis', code='NOT_RUN', message='Chưa chạy', amendment_id='s:a1')]
        validate_case(self.case)

    def test_failed_empty_report(self):
        self.report.update(status='FAILED', results=[], errors=[dict(stage='analysis', code='NOT_CONFIGURED', message='Chưa nối', amendment_id=None)])
        validate_case(self.case)

    def test_reader_validation(self):
        doc = self.case['documents']['v1']
        for field, value in [('role', 'UNKNOWN'), ('file_type', 'SCAN'), ('document_id', '')]:
            old = doc[field]
            doc[field] = value
            with self.subTest(field=field):
                self.rejects()
            doc[field] = old
        doc['blocks'].append(deepcopy(doc['blocks'][0]))
        self.rejects()
        doc['blocks'].pop()
        for b in doc['blocks']:
            b['text'] = ' '
        self.rejects()


class KnownBaselineGaps(unittest.TestCase):
    """Expected failures record proposed checks, not changes to the chosen code."""
    @unittest.expectedFailure
    def test_global_change_id_uniqueness_not_enforced(self):
        c = load_case()
        other = deepcopy(c['report']['results'][0])
        other['amendment']['amendment_id'] = 's:a2'
        other['text_diff']['amendment_id'] = 's:a2'
        other['semantic_diff']['amendment_id'] = 's:a2'
        c['report']['results'].append(other)
        with self.assertRaises(ValueError):
            validate_case(c)

    @unittest.expectedFailure
    def test_complete_text_reconstruction_not_enforced(self):
        c = load_case()
        c['report']['results'][0]['text_diff']['changes'] = []
        with self.assertRaises(ValueError):
            validate_case(c)


if __name__ == '__main__':
    unittest.main()
