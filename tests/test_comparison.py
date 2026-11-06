"""Contract fixtures test orchestration, not the domain algorithms."""
from io import BytesIO
from pathlib import Path
from threading import BoundedSemaphore
import unittest

from docx import Document
from fastapi.testclient import TestClient

from backend.main import app
from backend.app.comparison import Services, run_comparison
from backend.app.config import Settings
from backend.app.schemas.report_validation import validate_report


def docx_bytes(text='Điều 1. Thời hạn\n30 ngày.'):
    doc = Document()
    doc.add_paragraph(text)
    stream = BytesIO()
    doc.save(stream)
    return stream.getvalue()


def extraction(documents, clauses):
    def evidence(doc_id):
        block = documents[doc_id]['blocks'][0]
        return dict(document_id=doc_id, source_refs=[block['source_ref']], quote=block['text'])
    return [dict(amendment_id='s:a1', operation='AMEND', instruction=evidence('s'),
                 target_document='V1 fixture', target_locator='Điều 1',
                 target_unit_ids=[clauses['v1'][0]['unit_id']], applicability='APPLIES',
                 before_text='30 ngày.', after_text='15 ngày.', after_basis='QUOTED',
                 evidence=[evidence('v1'), evidence('s')], effect_info=[],
                 context=dict(general_context='fixture', evidence=[], references=[]),
                 needs_review=False, review_reason='')]


def semantic(item, text_diff):
    evidence = item['evidence']
    aspect = dict(aspect_id='a1', field_group='TIME_QUANTITY', old_value='30 ngày',
                  new_value='15 ngày', interpretation='Rút ngắn thời hạn.', evidence=evidence,
                  old_quote='30 ngày.', new_quote='15 ngày.', needs_review=False, review_reason='')
    return dict(amendment_id=item['amendment_id'], changes=[dict(change_id='c1',
                is_meaningful_change=True, diff_details='Fixture: 30 -> 15', aspects=[aspect],
                evidence=evidence, old_quote='30 ngày.', new_quote='15 ngày.',
                needs_review=False, review_reason='')], needs_review=False, review_reason='')


def scoring(item, semantic_result):
    return [dict(change_id='c1', category='TIME_QUANTITY', significance='MEDIUM',
                 is_critical=False, reason='Fixture only', needs_review=False, review_reason='')]


def services():
    return Services(extract=extraction, context=lambda item, docs, clauses: item,
                    text_diff=lambda item: dict(amendment_id=item['amendment_id'], changes=[
                        dict(type='REPLACE', old_text='30', new_text='15', old_start=0,
                             old_end=2, new_start=0, new_end=2)]),
                    semantic_diff=semantic, score=scoring)


class UploadTests(unittest.TestCase):
    def setUp(self):
        old = (app.state.settings, app.state.services, app.state.comparison_slots)
        self.addCleanup(self.restore, old)
        app.state.settings = Settings()
        app.state.services = services()
        app.state.comparison_slots = BoundedSemaphore(1)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def restore(self, old):
        app.state.settings, app.state.services, app.state.comparison_slots = old

    def upload(self, **overrides):
        files = dict(doc_v1=('same.docx', docx_bytes()),
                     doc_s=('same.docx', docx_bytes('Điều 1. Sửa đổi\n15 ngày.')))
        files.update(overrides)
        return self.client.post('/api/comparisons', files=files)

    def test_upload_success_and_metadata_and_cleanup(self):
        seen = []
        from backend.app import comparison
        original = comparison.read_and_parse_document
        from unittest.mock import patch
        def capture(path, *args):
            seen.append(Path(path))
            return original(path, *args)
        with patch.object(comparison, 'read_and_parse_document', capture):
            response = self.upload()
        self.assertEqual(response.status_code, 200, response.text)
        report = response.json()
        self.assertEqual(report['status'], 'SUCCESS')
        self.assertEqual(report['base_document']['filename'], report['amendment_document']['filename'])
        self.assertNotEqual(report['base_document']['document_id'], report['amendment_document']['document_id'])
        self.assertEqual(report['results'][0]['scoring'][0]['change_id'], 'c1')
        self.assertTrue(seen)
        self.assertTrue(all(not p.parent.exists() for p in seen))

    def test_default_services_never_fabricate_results(self):
        app.state.services = Services()
        response = self.upload()
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()['status'], 'FAILED')
        self.assertEqual(response.json()['errors'][0]['code'], 'MODULE_NOT_CONFIGURED')
        self.assertEqual(response.json()['results'], [])

    def test_module_failure_retains_amendment_as_partial(self):
        def broken(*args):
            raise RuntimeError('private content should not be returned')
        app.state.services.semantic_diff = broken
        response = self.upload()
        self.assertEqual(response.json()['status'], 'PARTIAL')
        self.assertIsNone(response.json()['results'][0]['semantic_diff'])
        self.assertNotIn('private content', response.text)

    def test_missing_context_is_explicit(self):
        app.state.services.context = None
        response = self.upload()
        self.assertEqual(response.json()['status'], 'PARTIAL')
        self.assertIsNone(response.json()['results'][0]['scoring'])

    def test_invalid_score_is_rejected(self):
        def bad_score(*args):
            result = scoring(*args)
            result[0]['is_critical'] = True
            return result
        app.state.services.score = bad_score
        report = self.upload().json()
        self.assertEqual(report['status'], 'PARTIAL')
        self.assertIsNone(report['results'][0]['scoring'])

    def test_invalid_source_is_rejected(self):
        def broken(docs, clauses):
            result = extraction(docs, clauses)
            result[0]['instruction']['source_refs'] = ['docx:paragraph_999']
            return result
        app.state.services.extract = broken
        self.assertEqual(self.upload().json()['status'], 'FAILED')

    def test_reference_gap_is_partial_and_keeps_direct_change(self):
        def context(item, docs, clauses):
            item['context']['references'] = [dict(reference_id='missing', document_label='Ref',
                target_locator='Điều 2', purpose='context', status='MISSING', evidence=[], reason='Not supplied')]
            return item
        app.state.services.context = context
        report = self.upload().json()
        self.assertEqual(report['status'], 'PARTIAL')
        self.assertEqual(report['results'][0]['scoring'][0]['significance'], 'MEDIUM')
        self.assertIn('REFERENCE_UNAVAILABLE', [w['code'] for w in report['warnings']])

    def test_unknown_content_does_not_become_empty_text_diff(self):
        def context(item, docs, clauses):
            item['after_text'] = None
            item['after_basis'] = 'UNRESOLVED'
            item['needs_review'] = True
            item['review_reason'] = 'Unknown after text'
            return item
        app.state.services.context = context
        app.state.services.semantic_diff = None
        report = self.upload().json()
        self.assertEqual(report['status'], 'PARTIAL')
        self.assertIsNone(report['results'][0]['text_diff'])
        self.assertIsNone(report['results'][0]['semantic_diff'])

    def test_invalid_offsets_are_rejected(self):
        app.state.services.text_diff = lambda item: dict(amendment_id=item['amendment_id'], changes=[
            dict(type='REPLACE', old_text='30', new_text='15', old_start=50, old_end=52, new_start=0, new_end=2)])
        report = self.upload().json()
        self.assertEqual(report['status'], 'PARTIAL')
        self.assertIsNone(report['results'][0]['text_diff'])

    def test_unpropagated_aspect_warning_is_rejected(self):
        def bad_semantic(*args):
            result = semantic(*args)
            result['changes'][0]['aspects'][0]['needs_review'] = True
            result['changes'][0]['aspects'][0]['review_reason'] = 'Needs review'
            return result
        app.state.services.semantic_diff = bad_semantic
        report = self.upload().json()
        self.assertEqual(report['status'], 'PARTIAL')
        self.assertIsNone(report['results'][0]['semantic_diff'])

    def test_openapi_exposes_upload_and_report(self):
        spec = self.client.get('/openapi.json').json()
        operation = spec['paths']['/api/comparisons']['post']
        schema = operation['requestBody']['content']['multipart/form-data']['schema']
        self.assertEqual(schema['required'], ['doc_v1', 'doc_s'])
        self.assertIn('ComparisonReport', str(operation['responses']['200']))

    def test_reference_without_articles_is_allowed(self):
        response = self.upload(reference_files=('reference.docx', docx_bytes('Chỉ có định nghĩa')))
        self.assertEqual(response.json()['status'], 'SUCCESS')
        self.assertEqual(response.json()['reference_documents'][0]['document_id'], 'ref_1')

    def test_input_errors(self):
        self.assertEqual(self.client.post('/api/comparisons', files={'doc_v1': ('x.docx', docx_bytes())}).status_code, 422)
        self.assertEqual(self.upload(doc_s=('x.exe', b'bad')).status_code, 415)
        self.assertEqual(self.upload(doc_s=('x.docx', b'')).status_code, 422)
        self.assertEqual(self.upload(doc_s=('x.docx', b'not a zip')).json()['error']['code'], 'INVALID_DOCX')

    def test_file_limit_and_capacity(self):
        app.state.settings = Settings(max_file_bytes=10)
        self.assertEqual(self.upload().status_code, 413)
        app.state.comparison_slots.acquire()
        try:
            self.assertEqual(self.upload().status_code, 503)
        finally:
            app.state.comparison_slots.release()

    def test_reference_count_limit(self):
        app.state.settings = Settings(max_references=1)
        response = self.client.post('/api/comparisons', files=[
            ('doc_v1', ('v1.docx', docx_bytes())), ('doc_s', ('s.docx', docx_bytes())),
            ('reference_files', ('r1.docx', docx_bytes())), ('reference_files', ('r2.docx', docx_bytes()))])
        self.assertEqual(response.status_code, 413)

    def test_concurrent_request_is_rejected_until_worker_finishes(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Event
        entered, release = Event(), Event()
        def blocked(item, docs, clauses):
            entered.set()
            if not release.wait(10):
                raise TimeoutError('Test worker was not released')
            return item
        app.state.services.context = blocked
        with ThreadPoolExecutor(max_workers=1) as pool:
            first = pool.submit(self.upload)
            try:
                self.assertTrue(entered.wait(10))
                self.assertEqual(self.upload().status_code, 503)
            finally:
                release.set()
            self.assertEqual(first.result(timeout=10).json()['status'], 'SUCCESS')
        self.assertEqual(self.upload().status_code, 200)

    def test_docx_expansion_limit(self):
        app.state.settings = Settings(max_docx_expanded_bytes=10)
        self.assertEqual(self.upload().json()['error']['code'], 'DOCX_EXPANSION_LIMIT')

    def test_request_limit_without_content_length(self):
        from backend.app.api.uploads import BodyLimitMiddleware
        import asyncio
        messages = iter([{'type': 'http.request', 'body': b'123', 'more_body': True},
                         {'type': 'http.request', 'body': b'456', 'more_body': False}])
        sent = []
        async def receive():
            return next(messages)
        async def send(message):
            sent.append(message)
        async def unexpected(*args):
            raise AssertionError('Oversized request reached app')
        asyncio.run(BodyLimitMiddleware(unexpected, 4)({'type': 'http'}, receive, send))
        self.assertEqual(sent[0]['status'], 413)

    def test_legacy_endpoint_is_preserved(self):
        response = self.client.post('/api/compare', json={'doc_v1': 'Điều 1. A\n30 ngày.', 'doc_v2': 'Điều 1. A\n15 ngày.'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

    def test_deadline_reports_failure(self):
        app.state.settings = Settings(deadline_seconds=0.000000001)
        report = self.upload().json()
        self.assertEqual(report['status'], 'FAILED')
        self.assertEqual(report['errors'][0]['code'], 'DEADLINE_EXCEEDED')


if __name__ == '__main__':
    unittest.main()
