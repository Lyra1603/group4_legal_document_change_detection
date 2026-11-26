"""S-only handoff, source boundaries and bounded retrieval regressions."""
from dataclasses import replace
import json
import unittest

from fastapi.testclient import TestClient

from backend.app.change_analysis.text_diff import compute_text_diff
from backend.app.context.chunk_builder import SourceChunk
from backend.app.context.context_builder import build_retrieval_query
from backend.app.context.lightrag_client import MAX_QUERY_CHARS
from backend.app.context.shared_service import graph_view
from backend.app.context.source_registry import SourceRegistry
from backend.app.document_processing.parser.legal_structure_parser import parse_docx
from backend.app.document_processing.target_lookup import discover_targets, load_catalog
from backend.app.pipeline import DocumentInput, ParsedDocument
from backend.demo import SAMPLES
from backend.shared_demo import ROOT, create_app


def sample(case, prefix):
    return next((ROOT / 'data/raw' / case).glob(prefix + '*.docx'))


class SharedTargetLookupTests(unittest.TestCase):
    def test_s_only_selects_known_snapshot_and_runs_existing_compare(self):
        amendment = ROOT / 'data/raw/case_02' / SAMPLES['case_02']['s']
        with TestClient(create_app(settings={})) as client:
            lookup = client.post('/api/demo/targets', files={'doc_s': (amendment.name, amendment.read_bytes())})
            self.assertEqual(lookup.status_code, 200, lookup.text)
            target, = lookup.json()['targets']
            self.assertEqual((target['document_number'], target['status']), ('22/2019/TT-NHNN', 'AUTO_MATCH'))
            candidate, = target['candidates']
            response = client.get('/api/demo/targets/candidates/' + candidate['id'])
            self.assertEqual(response.status_code, 200)
            v1 = (candidate['filename'], response.content)
            verified = client.post('/api/demo/targets/verify-v1', files={'doc_v1': v1},
                                   data={'document_number': target['document_number']})
            self.assertEqual(verified.status_code, 200, verified.text)
            report = client.post('/api/compare', files={'doc_v1': v1, 'doc_s': (amendment.name, amendment.read_bytes())})
            self.assertEqual(report.status_code, 200, report.text)
            self.assertTrue(any(item['text_diff'] for item in report.json()['results']))

    def test_one_s_has_candidate_for_one_target_and_requests_other_base(self):
        amendment = sample('case_10', '08')
        candidate_v1 = sample('case_10', '05')
        with TestClient(create_app(settings={})) as client:
            lookup = client.post('/api/demo/targets', files={'doc_s': (amendment.name, amendment.read_bytes())})
            self.assertEqual(lookup.status_code, 200, lookup.text)
            targets = {item['document_number']: item for item in lookup.json()['targets']}
            self.assertEqual(set(targets), {'05/2011/TT-BTP', '22/2010/TT-BTP'})
            self.assertEqual(targets['05/2011/TT-BTP']['status'], 'NEEDS_CONFIRMATION')
            self.assertTrue(targets['05/2011/TT-BTP']['candidates'])
            self.assertEqual(targets['22/2010/TT-BTP']['status'], 'NEEDS_V1')
            self.assertTrue(targets['22/2010/TT-BTP']['instructions'])
            mismatched = client.post('/api/demo/targets/verify-v1',
                files={'doc_v1': (candidate_v1.name, candidate_v1.read_bytes())},
                data={'document_number': '22/2010/TT-BTP'})
            self.assertEqual(mismatched.status_code, 422)
            self.assertEqual(mismatched.json()['detail']['code'], 'V1_IDENTITY_MISMATCH')
            self.assertEqual(client.get('/api/demo/targets/candidates/unknown').status_code, 404)

    def test_two_candidate_versions_never_auto_match(self):
        amendment = ROOT / 'data/raw/case_02' / SAMPLES['case_02']['s']
        parsed = ParsedDocument(DocumentInput('s', 'AMENDMENT', amendment.name, amendment),
                                parse_docx(amendment, document_id='s'), 'DOCX')
        original, = [candidate for candidate in load_catalog(ROOT) if candidate.number == '22/2019/TT-NHNN']
        target, = discover_targets(parsed, [original, replace(original, digest='alternate-snapshot')])['targets']
        self.assertEqual(target['status'], 'NEEDS_CONFIRMATION')
        self.assertEqual(len(target['candidates']), 2)


class ContextReviewRegressionTests(unittest.TestCase):
    def test_long_unit_compacts_query_and_keeps_original_diff(self):
        prefix = 'Nội dung khoản trước khi sửa. ' * 155
        item = {'amendment_id':'review-unit', 'instruction':{'quote':'Thay 30 ngày bằng 15 ngày'},
                'target_document':'v1', 'target_locator':'Điều 5',
                'before_text':prefix + 'Thời hạn là 30 ngày.',
                'after_text':prefix + 'Thời hạn là 15 ngày.'}
        diff = compute_text_diff(item)
        query = build_retrieval_query(item, diff)
        self.assertLessEqual(len(query), MAX_QUERY_CHARS)
        parsed = json.loads(query)
        self.assertEqual(parsed['omitted_change_count'], 0)
        self.assertIn('30 ngày', parsed['changes'][0]['before_excerpt'])
        self.assertIn('15 ngày', parsed['changes'][0]['after_excerpt'])
        self.assertEqual(parsed['changes'][0]['old_start'], diff['changes'][0]['old_start'])
        self.assertEqual(diff, compute_text_diff(item))

    def test_graph_omits_nodes_and_edges_without_valid_sources(self):
        registry = SourceRegistry(
            [SourceChunk('session','native','s','AMENDMENT','upload','block:1','Đoạn gốc','Đoạn gốc')],
            [{'document_id':'s','role':'AMENDMENT','blocks':[{'source_ref':'block:1','text':'Đoạn gốc'}]}])
        graph = {'nodes': [{'id':'grounded','properties':{'file_path':'native'}},
                           {'id':'unknown','properties':{'file_path':'foreign'}}],
                 'edges': [
                    {'source':'grounded','target':'grounded','properties':{'file_path':'native'}},
                    {'source':'grounded','target':'grounded','properties':{'file_path':'native<SEP>foreign'}},
                    {'source':'grounded','target':'unknown','properties':{'file_path':'native'}},
                 ]}
        result = graph_view(graph, registry)
        self.assertEqual([node['id'] for node in result['nodes']], ['grounded'])
        self.assertEqual(len(result['edges']), 1)
        self.assertEqual(result['audit']['omitted_nodes_without_source'], 1)
        self.assertEqual([edge['reason'] for edge in result['audit']['omitted_edges']],
                         ['MISSING_SOURCE','ENDPOINT_WITHOUT_SOURCE'])
