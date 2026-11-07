"""Synthetic regression cases, not a legal-quality benchmark or independent test set."""
import copy
import unittest

from src.local_analysis import analyze_amendment
from src.text_diff.diff_engine import compute_text_diff
from src.semantic_diff.diff_engine import detect_semantic_changes
from src.classifier_scorer.scorer import classify_and_score, score_semantic_change


def fixture(before='Hồ sơ phải nộp trong thời hạn 30 ngày.',
            after='Hồ sơ phải nộp trong thời hạn 15 ngày.'):
    return dict(amendment_id='synthetic-01', operation='AMEND', applicability='APPLIES',
        target_document='base-example', target_unit_ids=['base-example:article_5'],
        target_locator='Điều 5', before_text=before, after_text=after, after_basis='QUOTED',
        instruction=dict(document_id='amendment-example', source_refs=['fixture:instruction'],
                         quote='Thay nội dung Điều 5 bằng: ' + (after or '')),
        evidence=[dict(document_id='base-example', source_refs=['fixture:base'], quote=before or '')],
        context=dict(general_context='SYNTHETIC: nghĩa vụ nộp hồ sơ.', evidence=[], references=[]),
        effect_info=[], needs_review=False, review_reason='')


class TextDiffTests(unittest.TestCase):
    def test_offsets_and_reconstruction(self):
        for before, after in [('abc', 'abXc'), ('abc', 'ac'), ('30 ngày', '15 ngày'),
                              ('', 'mới'), ('cũ', ''), ('a' * 300 + 'X', 'a' * 300 + 'Y'),
                              ('Nộp hồ sơ\nĐiều 2', 'Nộp đủ hồ sơ\nĐiều 2')]:
            with self.subTest(before=before[:20], after=after[:20]):
                result = compute_text_diff('t', before, after)
                rebuilt = before
                for c in reversed(result.changes):
                    self.assertEqual(c.old_text, before[c.old_start:c.old_end])
                    self.assertEqual(c.new_text, after[c.new_start:c.new_end])
                    rebuilt = rebuilt[:c.old_start] + c.new_text + rebuilt[c.old_end:]
                self.assertEqual(rebuilt, after)

    def test_missing_and_identical(self):
        self.assertIsNone(compute_text_diff('t', None, ''))
        self.assertIsNone(compute_text_diff('t', '', None))
        self.assertEqual(compute_text_diff('t', 'x', 'x').changes, [])
        self.assertEqual(compute_text_diff('t', '', '').changes, [])


class AnalysisTests(unittest.TestCase):
    def run_item(self, item):
        return analyze_amendment(item, context_complete=True)

    def test_deadline_with_caller_input_locations(self):
        item = fixture()
        result = self.run_item(item)
        self.assertFalse(result['needs_review'])
        change = result['semantic_diff']['changes'][0]
        self.assertTrue(change['is_meaningful_change'])
        self.assertEqual(change['aspects'][0]['old_value'], '30 ngày')
        self.assertEqual(change['aspects'][0]['new_value'], '15 ngày')
        self.assertEqual(result['scoring'][0]['significance'], 'HIGH')
        self.assertFalse(result['scoring'][0]['is_critical'])
        self.assertEqual(change['evidence'][0]['source_refs'], ['fixture:base'])

    def test_identical_local_text(self):
        result = self.run_item(fixture('Nộp hồ sơ.', 'Nộp hồ sơ.'))
        self.assertEqual(result['semantic_diff']['changes'], [])
        self.assertEqual(result['scoring'], [])

    def test_wording_equivalence(self):
        result = self.run_item(fixture('Nộp chậm nhất vào ngày 12.', 'Nộp không muộn hơn ngày 12.'))
        self.assertFalse(result['semantic_diff']['changes'][0]['is_meaningful_change'])
        self.assertEqual(result['scoring'][0]['category'], 'WORDING_ONLY')
        self.assertEqual(result['scoring'][0]['significance'], 'LOW')

    def test_unknown_semantics_not_fabricated(self):
        result = self.run_item(fixture('Đơn vị phải báo cáo.', 'Đơn vị không phải báo cáo.'))
        self.assertTrue(result['needs_review'])
        self.assertIsNone(result['semantic_diff']['changes'][0]['is_meaningful_change'])
        self.assertIsNone(result['scoring'][0]['significance'])

    def test_missing_inputs_and_sources(self):
        for field, value in [('before_text', None), ('after_text', None), ('evidence', []),
                             ('target_unit_ids', []), ('applicability', 'UNRESOLVED')]:
            with self.subTest(field=field):
                item = fixture()
                item[field] = value
                result = self.run_item(item)
                self.assertTrue(result['needs_review'])
                self.assertIsNone(result['scoring'][0]['significance'])

    def test_unconfirmed_context(self):
        self.assertTrue(analyze_amendment(fixture())['needs_review'])

    def test_missing_reference_and_effect_warning(self):
        for kind in ('reference', 'effect', 'upstream'):
            item = fixture()
            if kind == 'reference':
                item['context']['references'] = [{'reference_id': 'ref-2', 'status': 'MISSING'}]
            elif kind == 'effect':
                item['effect_info'] = [{'needs_review': True, 'review_reason': 'Hiệu lực mơ hồ.'}]
            else:
                item.update(needs_review=True, review_reason='Đích chưa chắc.')
            result = self.run_item(item)
            self.assertTrue(result['needs_review'])
            self.assertIsNone(result['scoring'][0]['is_critical'])

    def test_derived_content_is_not_a_quote(self):
        item = fixture()
        item['after_basis'] = 'DERIVED'
        result = self.run_item(item)
        self.assertIsNone(result['semantic_diff']['changes'][0]['new_quote'])
        self.assertTrue(result['needs_review'])

    def test_add_repeal_and_other_document(self):
        for operation in ('ADD', 'REPEAL'):
            item = fixture()
            item['operation'] = operation
            item['before_text' if operation == 'ADD' else 'after_text'] = None
            result = self.run_item(item)
            self.assertIsNone(result['text_diff'])
            self.assertTrue(result['needs_review'])
            self.assertEqual(result['amendment']['instruction'], item['instruction'])
        item = fixture()
        item['applicability'] = 'OTHER_DOCUMENT'
        self.assertIsNone(self.run_item(item)['semantic_diff'])

    def test_input_not_mutated(self):
        item = fixture()
        original = copy.deepcopy(item)
        self.run_item(item)
        self.assertEqual(item, original)

    def test_multiple_changes_not_reduced_to_deadline(self):
        for before, after in [
            ('A nộp trong thời hạn 30 ngày.', 'B nộp trong thời hạn 15 ngày.'),
            ('Nộp trong thời hạn 30 ngày.', 'Không nộp trong thời hạn 15 ngày.'),
            ('Nộp trong thời hạn 1,30 ngày.', 'Nộp trong thời hạn 1,15 ngày.'),
        ]:
            result = self.run_item(fixture(before, after))
            self.assertTrue(result['needs_review'])

    def test_old_callers_do_not_receive_fake_certainty(self):
        result = detect_semantic_changes('x', '30 ngày', '15 ngày')
        self.assertTrue(result.needs_review)
        self.assertEqual(result.changes[0].evidence, [])
        for description in ('x', 'x' * 1000):
            score = classify_and_score('x', [], description)
            self.assertIsNone(score.significance)

    def test_aspect_warning_propagates_to_score(self):
        change = detect_semantic_changes('x', fixture()['before_text'], fixture()['after_text'],
            evidence=fixture()['evidence'] + [fixture()['instruction']],
            before_document_id='base-example', after_document_id='amendment-example',
            context_complete=True).changes[0]
        change.aspects[0].needs_review = True
        change.aspects[0].review_reason = 'Cần kiểm tra đơn vị.'
        score = score_semantic_change(change)
        self.assertTrue(score.needs_review)
        self.assertIsNone(score.significance)
        self.assertIn('đơn vị', score.review_reason)

    def test_wording_without_evidence_cannot_be_scored_low(self):
        from src.analysis_contracts import SemanticChange
        change = SemanticChange(change_id='x', is_meaningful_change=False,
                                diff_details='Tương đương', aspects=[], evidence=[])
        score = score_semantic_change(change)
        self.assertTrue(score.needs_review)
        self.assertIsNone(score.significance)


if __name__ == '__main__':
    unittest.main(verbosity=2)
