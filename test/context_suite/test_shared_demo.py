"""Shared HTTP/runner integration using an explicitly labelled HTTP double.

No provider calls. Real-service evidence is recorded separately.
"""
import json
from pathlib import Path
import tempfile
import time
import unittest

import httpx
from fastapi.testclient import TestClient

from backend.shared_demo import create_app, ROOT
from backend.app.config import LightRAGConfig
from backend.app.context.lightrag_client import LightRAGClient, RetrievalError
from backend.app.context.shared_service import SharedContextService, graph_view
from backend.app.context.metadata_corpus import load_metadata
from backend.app.schemas.report_validation import validate_report
from test.context_suite.support import ContractServer
from test.demo_suite.test_web_demo import base_docx, amendment_docx

SETTINGS = dict(LEGAL_AI_PROVIDER='gemini', GEMINI_API_KEY='provider-secret-not-for-browser',
                GEMINI_MODEL='contract-model', GEMINI_EMBEDDING_MODEL='contract-embedding', GEMINI_EMBEDDING_DIM='3072')


class DoubleOwnedServer:
    """No Docker/LLM: fresh HTTP double per owned service."""
    instances = []
    behavior = 'normal'
    startup_failure = None
    def __init__(self, runtime, session_id, settings, *, budget):
        self.session_id = self.comparison_id = session_id
        self.directory = Path(runtime) / session_id
        self.deadline = time.monotonic() + budget
        self.finished = False
        self.client = None
        self.backend = ContractServer(behavior=self.behavior)
        self.instances.append(self)

    def start(self):
        if self.startup_failure:
            raise RetrievalError(self.startup_failure)
        self.client = LightRAGClient(LightRAGConfig('http://double:9621','demo',api_key='server-secret-not-for-browser',poll_interval=.001),
            self.comparison_id, self.directory, deadline=self.deadline, transport=httpx.MockTransport(self.backend))
        return self.client

    def finish(self):
        self.finished = True
        if self.client:
            code=self.client.cleanup();self.client.close()
            return [code] if code else []
        return []


class SharedDemoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        DoubleOwnedServer.instances=[];DoubleOwnedServer.behavior='normal';DoubleOwnedServer.startup_failure=None
        self.service=SharedContextService(ROOT,self.temp.name,SETTINGS,server_factory=DoubleOwnedServer)
        self.client=TestClient(create_app(service=self.service))
        self.addCleanup(self.client.close)
        self.addCleanup(self.service.close)

    def index(self):
        response=self.client.post('/api/demo/corpus/index')
        self.assertEqual(response.status_code,202,response.text)
        self.service.executor.submit(lambda:None).result(timeout=5)
        return self.client.get('/api/demo/corpus').json()

    def compare(self):
        response=self.client.post('/api/compare',files={
            'doc_v1':('v1.docx',base_docx('Điều 2. Thời hạn','Phải báo cáo trong 30 ngày.')),
            'doc_s':('s.docx',amendment_docx('Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 2.'))})
        self.assertEqual(response.status_code,200,response.text)
        validate_report(response.json())
        return response.json()

    def test_browsers_need_no_server_key_and_receive_no_secrets(self):
        for path in ('/','/health','/api/demo/config','/api/demo/corpus'):
            response=self.client.get(path)
            self.assertEqual(response.status_code,200)
            self.assertNotIn(SETTINGS['GEMINI_API_KEY'],response.text)
            self.assertNotIn('server-secret-not-for-browser',response.text)
        self.assertFalse(self.client.get('/api/demo/config').json()['server_key_required_in_browser'])
        self.assertIn('shared.js',self.client.get('/').text)

    def test_real_metadata_ids_and_provenance_survive_query(self):
        state=self.index();self.assertEqual(state['state'],'READY')
        self.assertEqual({v['dataset_id'] for v in state['sources'].values()},{'18128','95942'})
        self.assertFalse(state['full_text_indexed'])
        response=self.client.post('/api/demo/corpus/query',json={'query':'Bộ luật Dân sự 2015'})
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(len(response.json()['evidence']),2)
        self.assertFalse(response.json()['legal_impact_confirmed'])
        self.assertEqual(len(DoubleOwnedServer.instances),1)
        self.index();self.assertEqual(len(DoubleOwnedServer.instances),1)

    def test_query_requires_ready_index(self):
        response=self.client.post('/api/demo/corpus/query',json={'query':'test'})
        self.assertEqual(response.status_code,503)
        self.assertEqual(response.json()['detail']['code'],'INDEX_NOT_READY')
        self.assertEqual(DoubleOwnedServer.instances,[])

    def test_missing_provider_is_reported_without_prompting_browser_for_key(self):
        self.service.settings={}
        state=self.index()
        self.assertEqual(state['state'],'FAILED')
        self.assertEqual(state['issues'],['REAL_SERVICE_CONFIGURATION_REQUIRED'])
        self.assertEqual(self.client.post('/api/demo/corpus/index').status_code,409)

    def test_foreign_source_is_rejected(self):
        DoubleOwnedServer.behavior='foreign';self.index()
        response=self.client.post('/api/demo/corpus/query',json={'query':'test'})
        self.assertEqual(response.status_code,503)
        self.assertEqual(response.json()['detail']['code'],'RETRIEVAL_SOURCE_MISMATCH')

    def test_empty_retrieval_is_not_a_negative_legal_verdict(self):
        DoubleOwnedServer.behavior='empty';self.index()
        response=self.client.post('/api/demo/corpus/query',json={'query':'test'})
        self.assertEqual(response.status_code,503)
        self.assertEqual(response.json()['detail']['code'],'RETRIEVAL_EMPTY')

    def test_busy_serializes_provider_work(self):
        self.service.gate.acquire()
        try:
            response=self.client.post('/api/demo/corpus/index')
            self.assertEqual(response.status_code,409)
            self.assertEqual(DoubleOwnedServer.instances,[])
        finally:self.service.gate.release()

    def test_real_docx_http_runner_uses_context_and_preserves_corpus(self):
        self.index();corpus=DoubleOwnedServer.instances[0]
        report=self.compare()
        self.assertNotIn('LIGHTRAG_DISABLED',{v['code'] for v in report['warnings']})
        self.assertIn('RETRIEVAL_SCOPE_LIMITED',{v['code'] for v in report['warnings']})
        sidecar=self.client.get('/api/demo/contexts/'+report['comparison_id']).json()
        self.assertEqual(sidecar['state'],'READY',sidecar)
        self.assertTrue(sidecar['items'][0]['verified'])
        self.assertFalse(corpus.finished)
        self.assertTrue(DoubleOwnedServer.instances[-1].finished)
        self.assertEqual(DoubleOwnedServer.instances[-1].client.state['comparison_id'],report['comparison_id'])
        self.assertEqual(self.client.post('/api/demo/corpus/query',json={'query':'test'}).status_code,200)

    def test_provider_failure_keeps_text_diff_and_reports_issue(self):
        DoubleOwnedServer.startup_failure='DOCKER_UNAVAILABLE'
        report=self.compare()
        self.assertEqual(report['status'],'PARTIAL')
        self.assertIsNotNone(report['results'][0]['text_diff'])
        self.assertIn('DOCKER_UNAVAILABLE',{v['code'] for v in report['warnings']})
        state=self.client.get('/api/demo/contexts/'+report['comparison_id']).json()
        self.assertFalse(state['items'][0]['verified'])
        self.assertEqual(state['state'],'PARTIAL')

    def test_graph_keeps_source_evidence_and_does_not_claim_legal_truth(self):
        registry,_=load_metadata(ROOT,'source-test')
        source=next(iter(registry.chunks))
        graph={'nodes':[{'id':'Bộ luật','properties':{'file_path':source,'description':'test'}}],
               'edges':[{'source':'Bộ luật','target':'Bộ luật','properties':{'file_path':source,'description':'test'}}]}
        view=graph_view(graph,registry)
        self.assertEqual(view['nodes'][0]['sources'][0]['document_id'],'ref_1')
        self.assertFalse(view['edges'][0]['legal_relation_verified'])
        graph['edges'][0]['target']='missing'
        with self.assertRaises(ValueError):graph_view(graph,registry)

    def test_failed_query_keeps_previous_evidence_and_public_error(self):
        self.index()
        first=self.client.post('/api/demo/corpus/query',json={'query':'test'}).json()
        DoubleOwnedServer.instances[0].backend.behavior='timeout'
        failed=self.client.post('/api/demo/corpus/query',json={'query':'test'})
        self.assertEqual(failed.status_code,503)
        state=self.client.get('/api/demo/corpus').json()
        self.assertEqual(state['evidence'],first['evidence'])
        self.assertEqual(state['issues'],['RETRIEVAL_TIMEOUT'])
        self.assertEqual(state['state'],'READY')  # index exists, query failed

    def test_malformed_graph_does_not_become_source_mismatch(self):
        self.index()
        self.service.corpus_client.graph=lambda: {'nodes':None}
        response=self.client.post('/api/demo/corpus/query',json={'query':'test'})
        self.assertEqual(response.json()['detail']['code'],'GRAPH_PROTOCOL_ERROR')
