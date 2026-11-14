"""Business incompleteness must not masquerade as a successful or crashed server."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.demo import app
from backend.main import compare_documents
from backend.app.demo_runner import classify_demo_results
from backend.app.pipeline import AnalysisOutcome, issue
from backend.app.schemas.report_validation import validate_report
from test.demo_suite.test_web_demo import docx, base_docx, amendment_docx


class ReportStatusTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def compare(self, amendment):
        return self.client.post('/api/compare', files={
            'doc_v1': ('v1.docx', base_docx('Điều 2. Thời hạn','30 ngày.')),
            'doc_s': ('s.docx', amendment)})

    def test_only_unsupported_returns_failed_with_items_and_http_200(self):
        response = self.compare(amendment_docx('Bãi bỏ Điều 2.'))
        self.assertEqual(response.status_code, 200)
        report = response.json(); validate_report(report)
        self.assertEqual(report['status'], 'FAILED')
        self.assertEqual(len(report['results']), 1)
        self.assertEqual(report['results'][0]['amendment']['instruction']['quote'], 'Bãi bỏ Điều 2.')
        self.assertIn('NO_USABLE_ANALYSIS', {w['code'] for w in report['warnings']})
        self.assertFalse(report['errors'])

    def test_only_unknown_target_returns_failed_not_partial(self):
        response = self.compare(amendment_docx('Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 99.'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'FAILED')
        self.assertEqual(response.json()['results'][0]['amendment']['applicability'], 'UNRESOLVED')

    def test_useful_text_with_unknown_semantics_remains_partial(self):
        response = self.compare(amendment_docx('Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 2.'))
        report = response.json(); validate_report(report)
        self.assertEqual(report['status'], 'PARTIAL')
        self.assertIsNotNone(report['results'][0]['text_diff'])
        self.assertIsNone(report['results'][0]['scoring'][0]['significance'])

    def test_mixed_keeps_both_items_and_partial(self):
        response = self.compare(amendment_docx('Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 2.','Bãi bỏ Điều 2.'))
        report = response.json(); validate_report(report)
        self.assertEqual(report['status'], 'PARTIAL')
        self.assertEqual(len(report['results']), 2)
        self.assertIsNotNone(report['results'][0]['text_diff'])
        self.assertIsNone(report['results'][1]['text_diff'])

    def test_runtime_exception_and_timeout_keep_error_http_status(self):
        def crash(*args):
            raise RuntimeError('test-only internal exception')
        def timeout(*args):
            raise TimeoutError('test-only timeout')
        cases = [(crash,500,'PROCESSING_FAILED'),(timeout,504,'PROCESSING_TIMEOUT'),(None,501,'ANALYSIS_NOT_CONFIGURED')]
        for runner, status, code in cases:
            with self.subTest(code=code):
                # Separate app isolates test doubles from the real demo runner.
                probe = FastAPI()
                probe.state.analysis_runner = runner
                probe.add_api_route('/api/compare', compare_documents, methods=['POST'])
                with TestClient(probe) as client:
                    response = client.post('/api/compare', files={
                        'doc_v1':('v1.docx',base_docx('Điều 2. Nội dung','30 ngày.')),
                        'doc_s':('s.docx',amendment_docx('Bãi bỏ Điều 2.'))})
                self.assertEqual(response.status_code,status)
                report = response.json(); validate_report(report)
                self.assertEqual(report['status'],'FAILED')
                self.assertIn(code,{e['code'] for e in report['errors']})

    def test_explicit_processing_errors_are_not_downgraded_to_http_200(self):
        probe = FastAPI()
        probe.state.analysis_runner = lambda *args: AnalysisOutcome(
            'FAILED', [], [], [issue('analysis','ANALYSIS_SERVICE_FAILED','Test-only service failure')])
        probe.add_api_route('/api/compare', compare_documents, methods=['POST'])
        with TestClient(probe) as client:
            response = client.post('/api/compare', files={
                'doc_v1':('v1.docx',base_docx('Điều 2. Nội dung','30 ngày.')),
                'doc_s':('s.docx',amendment_docx('Bãi bỏ Điều 2.'))})
        self.assertEqual(response.status_code,500)
        self.assertTrue(response.json()['errors'])

    def test_no_changes_is_still_a_usable_text_result_not_a_global_conclusion(self):
        response = self.compare(amendment_docx('Thay cụm từ “30 ngày” bằng “30 ngày” tại Điều 2.'))
        report = response.json(); validate_report(report)
        self.assertEqual(report['status'],'PARTIAL')
        self.assertEqual(report['results'][0]['text_diff']['changes'],[])
        self.assertTrue(report['results'][0]['semantic_diff']['needs_review'])

    def test_success_requires_complete_non_reviewed_results(self):
        # A schema-valid fixture, not a claim that the live baseline produces SUCCESS.
        fixture = json.loads((Path(__file__).resolve().parents[1]/'fixtures/reports/common_contract.json').read_text(encoding='utf-8'))
        result = deepcopy(fixture['report']['results'][0])
        def clear_review(value):
            if isinstance(value, dict):
                if 'needs_review' in value:
                    value.update(needs_review=False,review_reason='')
                for child in value.values(): clear_review(child)
            elif isinstance(value, list):
                for child in value: clear_review(child)
        clear_review(result)
        self.assertEqual(classify_demo_results([result]),'SUCCESS')
        result['amendment']['needs_review'] = True
        result['amendment']['review_reason'] = 'Still unresolved context'
        self.assertEqual(classify_demo_results([result]),'PARTIAL')
        self.assertEqual(classify_demo_results([]),'FAILED')


if __name__ == '__main__':
    unittest.main()
