"""Ngoc Anh's week-10 handoffs: real supplied data and labelled synthetic edges."""
from copy import deepcopy
import json
from pathlib import Path
import random
import unittest

from backend.app.change_analysis.text_diff import compute_text_diff, validate_text_diff
from backend.app.change_analysis.semantic_diff import detect_semantic_changes
from backend.app.change_analysis.scorer import score_changes
from backend.app.schemas.contracts import AmendmentItem, SemanticDiffResult, TextDiffResult, ScoringResult
from backend.app.schemas.report_validation import validate_payload, validate_sources

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / 'data/ngocanh-week10/input'


def real_handoff():
    return json.loads((INPUT / 'ban_giao_ca_dung.json').read_text(encoding='utf-8'))


def synthetic_item():
    """Known complete context here is a test assumption, never real-case evidence."""
    item = deepcopy(real_handoff()['items'][0])
    item.update(amendment_id='synthetic:deadline', needs_review=False, review_reason='',
                before_text='Cơ quan giải quyết trong thời hạn 30 ngày.',
                after_text='Cơ quan giải quyết trong thời hạn 15 ngày.')
    item['evidence'] = [dict(document_id='v1', source_refs=['fixture:old'], quote=item['before_text']),
                        dict(document_id='s', source_refs=['fixture:new'], quote=item['after_text'])]
    return item


class TextDiffHandoffTests(unittest.TestCase):
    def test_real_item_source_offsets_and_reconstruction(self):
        documents = json.loads((INPUT / 'ban_giao_kho_nguon.json').read_text(encoding='utf-8'))
        for item in real_handoff()['items']:
            validate_payload(AmendmentItem, item)
            validate_sources(item, documents)
            result = compute_text_diff(item)
            validate_payload(TextDiffResult, result)
            validate_text_diff(item, result)
            self.assertTrue(result['changes'])
            self.assertEqual(item['amendment_id'], result['amendment_id'])

    def test_edges_preserve_original_code_point_offsets(self):
        for before, after in [('', ''), ('', 'thêm'), ('xóa', ''), ('giữ', 'giữ'),
                              ('30 ngày', '15 ngày'), ('😀 Điều 1\r\na', '😀 Điều 1\r\nb'),
                              ('a\u0301  x', 'á\tx'), ('a' * 300 + 'b', 'a' * 300 + 'c')]:
            with self.subTest(before=before, after=after):
                item = dict(amendment_id='edge', before_text=before, after_text=after)
                validate_text_diff(item, compute_text_diff(item))

    def test_missing_is_distinct_from_empty(self):
        for before, after in [(None, 'a'), ('a', None), (None, None)]:
            item = dict(amendment_id='missing', before_text=before, after_text=after)
            self.assertIsNone(compute_text_diff(item))
            validate_text_diff(item, None)

    def test_random_reconstruction(self):
        rng = random.Random(10)
        for _ in range(200):
            before, after = (''.join(rng.choices('ab á\u0301😀\r\n', k=rng.randrange(60))) for _ in range(2))
            item = dict(amendment_id='random', before_text=before, after_text=after)
            validate_text_diff(item, compute_text_diff(item))

    def test_reject_incomplete_foreign_and_corrupt_diff(self):
        item = synthetic_item()
        result = compute_text_diff(item)
        variants = [None, {**result, 'amendment_id': 'other'}, {**result, 'changes': []}]
        for key, value in [('old_start', -1), ('new_start', True), ('old_text', 'wrong'), ('type', 'INSERT')]:
            broken = deepcopy(result)
            broken['changes'][0][key] = value
            variants.append(broken)
        broken = deepcopy(result)
        broken['changes'] *= 2
        variants.append(broken)
        for broken in variants:
            with self.subTest(diff=broken), self.assertRaises(ValueError):
                validate_text_diff(item, broken)


class SemanticHandoffTests(unittest.TestCase):
    def analyze(self, item, complete=False, diff='auto'):
        result = detect_semantic_changes(item, compute_text_diff(item) if diff == 'auto' else diff,
                                         context_complete=complete)
        validate_payload(SemanticDiffResult, result)
        return result

    def assert_unknown(self, result):
        self.assertTrue(result['needs_review'])
        self.assertTrue(result['review_reason'])
        self.assertIsNone(result['changes'][0]['is_meaningful_change'])
        for score in score_changes(result):
            validate_payload(ScoringResult, score)
            self.assertIsNone(score['significance'])
            self.assertTrue(score['needs_review'])

    def test_real_missing_context_to_real_scorer(self):
        item = real_handoff()['items'][0]
        original = deepcopy(item)
        result = self.analyze(item)
        self.assert_unknown(result)
        validate_sources(result, json.loads((INPUT / 'ban_giao_kho_nguon.json').read_text(encoding='utf-8')))
        self.assertEqual(item, original)
        self.assertEqual(result['changes'][0]['change_id'], score_changes(result)[0]['change_id'])

    def test_supported_deadline_on_synthetic_confirmed_context(self):
        result = self.analyze(synthetic_item(), complete=True)
        change = result['changes'][0]
        self.assertIs(change['is_meaningful_change'], True)
        self.assertEqual(change['aspects'][0]['field_group'], 'TIME_QUANTITY')
        self.assertEqual((change['aspects'][0]['old_value'], change['aspects'][0]['new_value']), ('30 ngày', '15 ngày'))
        score, = score_changes(result)
        validate_payload(ScoringResult, score)
        self.assertEqual(score['change_id'], change['change_id'])
        self.assertEqual(score['category'], 'TIME_QUANTITY')
        self.assertIsNone(score['significance'])
        self.assertIsNone(score['is_critical'])
        self.assertTrue(score['needs_review'])
        self.assertIn('rubric', score['review_reason'])

    def test_context_flag_does_not_override_upstream_review(self):
        self.assert_unknown(self.analyze(real_handoff()['items'][0], complete=True))

    def test_missing_context_alone_blocks_supported_rule(self):
        item = synthetic_item()
        self.assertFalse(item['needs_review'])
        self.assert_unknown(self.analyze(item))

    def test_unresolved_references_effects_targets_and_operations(self):
        for kind in ('reference', 'effect', 'target', 'operation', 'derived', 'source'):
            item = synthetic_item()
            if kind == 'reference':
                item['context']['references'] = [dict(reference_id='missing', status='MISSING', evidence=[])]
            elif kind == 'effect':
                item['effect_info'] = [dict(needs_review=True, review_reason='Chưa rõ hiệu lực')]
            elif kind == 'target':
                item.update(applicability='UNRESOLVED', target_unit_ids=[])
            elif kind == 'operation':
                item['operation'] = 'ADD'
            elif kind == 'derived':
                item['after_basis'] = 'DERIVED'
            else:
                item['evidence'][0]['source_refs'] = []
            with self.subTest(kind=kind):
                result = self.analyze(item, complete=True)
                self.assert_unknown(result)
                if kind == 'derived':
                    self.assertIsNone(result['changes'][0]['new_quote'])

    def test_bad_diff_never_creates_semantic_certainty(self):
        item = synthetic_item()
        for diff in (None, {'amendment_id': 'other', 'changes': []},
                     {'amendment_id': item['amendment_id'], 'changes': []}):
            result = self.analyze(item, complete=True, diff=diff)
            self.assert_unknown(result)
            self.assertIn('Chưa có Text Diff hợp lệ', result['changes'][0]['diff_details'])

    def test_equal_and_equivalent_wording(self):
        for before, after, equal in [('Giữ nguyên.', 'Giữ nguyên.', True),
                                     ('Nộp chậm nhất vào ngày 15.', 'Nộp không muộn hơn ngày 15.', False)]:
            item = synthetic_item()
            item.update(before_text=before, after_text=after)
            item['evidence'][0]['quote'], item['evidence'][1]['quote'] = before, after
            result = self.analyze(item, complete=True)
            if equal:
                self.assertEqual(result['changes'], [])
            else:
                self.assertIs(result['changes'][0]['is_meaningful_change'], False)
                self.assertEqual(score_changes(result)[0]['category'], 'WORDING_ONLY')


if __name__ == '__main__':
    unittest.main()
