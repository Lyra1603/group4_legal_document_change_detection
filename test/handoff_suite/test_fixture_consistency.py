"""Fixture consistency and narrow real-function checks, never real RAG acceptance."""
import json
from pathlib import Path
import unittest

from backend.app.schemas.contracts import TextDiffResult, SemanticDiffResult, ScoringResult
from backend.app.schemas.report_validation import validate_payload, validate_sources, validate_amendment, validate_report
from backend.app.schemas.validation import validate_extracted_document
from backend.app.change_analysis.text_diff import compute_text_diff
from backend.app.change_analysis.scorer import score_changes
from backend.app.demo_runner import classify_demo_results

BASE = Path(__file__).resolve().parents[2] / 'data/module_handoff_fixtures'


def load(stage, filename='deadline_reduction.json'):
    return json.loads((BASE/stage/filename).read_text(encoding='utf-8'))


class HandoffFixtureTests(unittest.TestCase):
    def setUp(self):
        self.source = load('adapter_to_linker')
        self.documents = self.source['input']['documents']
        self.clauses = self.source['input']['clauses']

    def test_source_metadata_and_all_embedded_contracts(self):
        for document in self.documents.values():
            validate_extracted_document(document)
        def walk(value):
            if isinstance(value, list):
                for child in value:
                    walk(child)
            elif isinstance(value, dict):
                if {'operation', 'instruction', 'target_unit_ids', 'after_basis'} <= value.keys():
                    validate_amendment(value, self.documents, self.clauses)
                    if value['applicability'] == 'APPLIES':
                        self.assertEqual(value['target_document'], 'v1')
                if {'base_document', 'results', 'status', 'comparison_id'} <= value.keys():
                    validate_report(value)
                    self.assertEqual(value['status'], 'PARTIAL')
                if {'amendment_id', 'changes'} <= value.keys():
                    kind = SemanticDiffResult if 'needs_review' in value else TextDiffResult
                    validate_payload(kind, value)
                if {'change_id', 'significance', 'is_critical', 'reason'} <= value.keys():
                    validate_payload(ScoringResult, value)
                    self.assertIsNone(value['significance'])
                    self.assertIsNone(value['is_critical'])
                    self.assertTrue(value['needs_review'])
                for child in value.values():
                    walk(child)
        for path in BASE.glob('*/deadline_reduction.json'):
            fixture = json.loads(path.read_text(encoding='utf-8'))
            self.assertIn('NOT_RUNTIME_PROOF', fixture['metadata']['kind'])
            validate_sources(fixture, self.documents)
            walk(fixture)

    def test_adjacent_stages_use_identical_items_and_results(self):
        item = self.source['expected_output'][0]
        self.assertEqual(item, load('document_to_text_diff')['input'])
        self.assertEqual(item, load('text_diff_and_index_to_query')['input']['amendment'])
        self.assertEqual(item, load('retrieval_to_context')['input']['amendment'])
        enriched = load('retrieval_to_context')['expected_output']
        self.assertEqual(enriched, load('context_and_text_diff_to_semantic')['input']['amendment'])
        self.assertEqual(enriched, load('semantic_to_scorer')['input']['amendment'])
        diff = load('document_to_text_diff')['expected_output']
        self.assertEqual(diff, load('context_and_text_diff_to_semantic')['input']['text_diff'])
        self.assertEqual(diff, load('text_diff_and_index_to_query')['input']['text_diff'])
        semantic = load('context_and_text_diff_to_semantic')['expected_output']
        self.assertEqual(semantic, load('semantic_to_scorer')['input']['semantic_diff'])
        report = load('analysis_to_pipeline')['expected_output']
        self.assertEqual(report, load('api_to_frontend')['input'])
        self.assertEqual(report['results'][0]['text_diff'], diff)
        self.assertEqual(report['results'][0]['semantic_diff'], semantic)
        self.assertEqual(report['results'][0]['amendment'], enriched)
        self.assertEqual(report['results'][0]['scoring'], load('semantic_to_scorer')['expected_output'])
        self.assertIsNone(load('api_to_frontend')['expected_output']['significance'])

    def test_diff_reconstructs_after_and_offsets_match(self):
        fixture = load('document_to_text_diff')
        item, diff = fixture['input'], fixture['expected_output']
        before, after = item['before_text'], item['after_text']
        pieces, cursor = [], 0
        for change in diff['changes']:
            start, end = change['old_start'], change['old_end']
            self.assertGreaterEqual(start, cursor)
            self.assertEqual(before[start:end], change['old_text'])
            self.assertEqual(after[change['new_start']:change['new_end']], change['new_text'])
            pieces.extend([before[cursor:start], change['new_text']])
            cursor = end
        pieces.append(before[cursor:])
        self.assertEqual(''.join(pieces), after)

    def test_real_text_diff_matches_handoff_fixture(self):
        fixture = load('document_to_text_diff')
        self.assertEqual(compute_text_diff(fixture['input']), fixture['expected_output'])

    def test_real_scorer_preserves_unreviewed_severity_on_shared_case(self):
        fixture = load('semantic_to_scorer')
        actual = score_changes(fixture['input']['semantic_diff'])
        self.assertEqual(len(actual), len(fixture['expected_output']))
        for score, expected in zip(actual, fixture['expected_output']):
            validate_payload(ScoringResult, score)
            for key in ['change_id', 'category', 'significance', 'is_critical', 'needs_review']:
                self.assertEqual(score[key], expected[key])
            self.assertTrue(score['review_reason'])

    def test_real_demo_classifier_matches_partial_handoff_report(self):
        report = load('analysis_to_pipeline')['expected_output']
        self.assertEqual(classify_demo_results(report['results']), report['status'])

    def test_query_gate_fixtures_do_not_claim_execution(self):
        for filename in ['index_not_ready.json', 'text_diff_not_ready.json']:
            fixture = load('text_diff_and_index_to_query', filename)
            ready = fixture['input']['index_ready'] and fixture['input']['text_diff'] is not None
            self.assertFalse(ready)
            self.assertFalse(fixture['expected_output']['query_executed'])
            self.assertTrue(fixture['expected_output']['review_reason_required'])

    def test_negative_scenarios_keep_instructions_and_expected_projection(self):
        paths = list((BASE/'scenarios').glob('*.json'))
        self.assertEqual(len(paths), 6)
        for path in paths:
            fixture = json.loads(path.read_text(encoding='utf-8'))
            self.assertIn('NOT_FULL_RUNTIME_PAYLOAD', fixture['metadata']['kind'])
            data, expected = fixture['input'], fixture['expected']
            for document in data['documents'].values():
                validate_extracted_document(document)
            known = {b['source_ref'] for b in data['documents']['s']['blocks']}
            self.assertEqual(expected['http_status'], 200)
            self.assertEqual(expected['status'], 'PARTIAL' if expected['usable_results'] else 'FAILED')
            for item in expected['items']:
                self.assertTrue(set(item['instruction_source_refs']) <= known)
                if item.get('analysis_permitted') is False or item.get('applicability') in {'UNRESOLVED','OTHER_DOCUMENT'}:
                    self.assertIsNone(item['text_diff'])
                    self.assertIsNone(item['semantic_diff'])
                    self.assertTrue(item['needs_review'])
                    self.assertTrue(item['review_reason_required'])


if __name__ == '__main__':
    unittest.main()
