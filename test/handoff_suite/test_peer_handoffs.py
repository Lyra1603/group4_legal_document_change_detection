"""Cross-branch handoffs against actual peer code; no live retrieval claims."""
from copy import deepcopy
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier
from time import monotonic
import unittest

import httpx

from backend.app.pipeline import DocumentInput, ParsedDocument
from backend.app.document_processing.amendment_linker import link_amendments
from backend.app.change_analysis.text_diff import compute_text_diff, validate_text_diff
from backend.app.change_analysis.semantic_diff import detect_semantic_changes
from backend.app.change_analysis.scorer import score_changes
from backend.app.context.chunk_builder import build_chunks
from backend.app.context.source_registry import SourceRegistry
from backend.app.context.lightrag_client import LightRAGClient
from backend.app.config import LightRAGConfig
from backend.app.schemas.contracts import AmendmentResult, SemanticDiffResult, ScoringResult
from backend.app.schemas.report_validation import validate_payload, validate_sources, validate_amendment
from .peer_versions import ROOT, peers
from test.context_suite.support import ContractServer


def fresh_case(parser, adapter, case):
    from backend.demo import SAMPLES
    sample = SAMPLES[case]
    parsed = []
    for did, role, key in [('v1', 'BASE', 'v1'), ('s', 'AMENDMENT', 's')]:
        path = ROOT / 'data/raw' / case / sample[key]
        tree = parser.parse_docx(path, document_id=did)
        parsed.append(ParsedDocument(DocumentInput(did, role, path.name, path), tree, 'DOCX'))
    boundary = adapter.adapt_documents(parsed)
    items, issues = link_amendments(boundary)
    return boundary, items, issues


class PeerHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            loaded = peers()
        except subprocess.CalledProcessError as exc:
            raise unittest.SkipTest('Peer Git refs unavailable; fetch the branches or run the pinned evidence runner') from exc
        cls.parser, cls.adapter, cls.consumer, cls.bridge, cls.provenance = loaded
        cls.boundary, cls.items, _ = fresh_case(cls.parser, cls.adapter, 'case_02')
        cls.item = next(i for i in cls.items if i['before_text'] is not None and i['after_text'] is not None)

    def test_fresh_parser_adapter_all_docx_cases(self):
        for case in ('case_01', 'case_02', 'case_03'):
            with self.subTest(case=case):
                boundary, items, _ = fresh_case(self.parser, self.adapter, case)
                self.assertTrue(items)
                for item in items:
                    validate_amendment(item, boundary.documents, boundary.clauses)
                    text = compute_text_diff(item)
                    validate_text_diff(item, text)
                    if text is not None:
                        payload = json.loads(self.consumer.build_retrieval_query(item, text))
                        self.assertEqual(payload['amendment_id'], item['amendment_id'])
                        self.assertEqual(payload['text_diff'], text)
                        self.assertEqual(payload['before_text'], item['before_text'])
                        self.assertEqual(payload['after_text'], item['after_text'])

    def test_original_handoff_is_compared_without_rewriting_fixture(self):
        supplied = json.loads((ROOT / 'data/ngocanh-week10/input/ban_giao_ca_dung.json').read_text(encoding='utf-8'))
        old = supplied['items'][0]
        # Node IDs may change after parser fixes; compare the same legal locator.
        self.assertEqual(old['target_locator'], self.item['target_locator'])
        for key in ('before_text', 'after_text', 'amendment_id'):
            self.assertEqual(old[key], self.item[key], key)

    def test_consumer_rejects_bad_id_offset_and_omitted_changes(self):
        text = compute_text_diff(self.item)
        bad_id = {**text, 'amendment_id': 'foreign'}
        bad_offset = deepcopy(text)
        bad_offset['changes'][0]['old_start'] = -1
        variants = [bad_id, bad_offset, {**text, 'changes': []}]
        chunks = build_chunks('peer-check', list(self.boundary.documents.values()),
                              {d: 'uploaded-source' for d in self.boundary.documents},
                              max_chunks=5000, max_chars=100000)
        registry = SourceRegistry(chunks, list(self.boundary.documents.values()))
        class MustNotQuery:
            def query(self, query):
                raise AssertionError('Invalid diff reached retrieval')
        for text in variants:
            with self.subTest(diff=text):
                with self.assertRaises(ValueError):
                    self.consumer.build_retrieval_query(self.item, text)
                result = self.consumer.build_context(self.item, registry, MustNotQuery(), text_diff=text)
                self.assertEqual(result.issues[0]['code'], 'TEXT_DIFF_INVALID')
                self.assertTrue(result.amendment['needs_review'])

    def test_query_keeps_unicode_and_insert_delete_spans(self):
        for before, after in [('', '😀 á'), ('xóa', ''), ('á', 'á'), ('giữ', 'giữ')]:
            item = deepcopy(self.item)
            item.update(before_text=before, after_text=after)
            text = compute_text_diff(item)
            payload = json.loads(self.consumer.build_retrieval_query(item, text))
            self.assertEqual(payload['text_diff'], text)
            validate_text_diff(item, payload['text_diff'])

    def test_peer_bridge_waits_for_index_and_diff_before_query(self):
        barrier = Barrier(2, timeout=5)
        events = []
        original = deepcopy(self.item)
        def prepare(item):
            barrier.wait()
            events.append('index')
            return self.consumer.ContextBuild(item, [], None)
        def diff(item):
            barrier.wait()
            text = compute_text_diff(item)
            events.append('text')
            return text
        def query(item, text):
            self.assertEqual(set(events), {'index', 'text'})
            payload = json.loads(self.consumer.build_retrieval_query(item, text))
            self.assertEqual(payload['text_diff'], compute_text_diff(original))
            events.append('query_payload')
            return self.consumer.ContextBuild(item, [], None)
        def semantic(item, text):
            self.assertEqual(events[-1], 'query_payload')
            events.append('semantic')
            return detect_semantic_changes(item, text)
        _, _, result = self.bridge.run_semantic_stage(self.item, context_prepare=prepare,
            context_work=query, text_diff=diff, semantic_diff=semantic)
        self.assertTrue(result['needs_review'])
        self.assertEqual(self.item, original)

    def test_actual_diff_reaches_http_query_contract_after_index_ready(self):
        # HTTP contract double only: no model and no real LightRAG service.
        chunks = build_chunks('peer-http', list(self.boundary.documents.values()),
                              {d: 'uploaded-source' for d in self.boundary.documents},
                              max_chunks=5000, max_chars=100000)
        sources = {(e['document_id'], ref) for e in self.item['evidence'] for ref in e['source_refs']}
        chunks = [c for c in chunks if (c.document_id, c.source_ref) in sources]
        registry = SourceRegistry(chunks, list(self.boundary.documents.values()))
        server = ContractServer()
        queries = []
        def handle(request):
            if request.url.path == '/query/data':
                queries.append(json.loads(request.content)['query'])
            return server(request)
        config = LightRAGConfig('http://contract-double', 'demo', top_k=32)
        with TemporaryDirectory() as temporary:
            client = LightRAGClient(config, 'peer-http', Path(temporary), deadline=monotonic() + 10,
                                    transport=httpx.MockTransport(handle))
            text = compute_text_diff(self.item)
            try:
                # Readiness must block retrieval before any HTTP query is sent.
                blocked = self.consumer.build_context(self.item, registry, client, text_diff=text)
                self.assertEqual(blocked.issues[0]['code'], 'INDEX_NOT_READY')
                self.assertEqual(queries, [])
                prepared = self.consumer.prepare_index(self.item, registry, client)
                self.assertEqual(prepared.issues, [])
                context = self.consumer.build_context(prepared.amendment, registry, client, text_diff=text)
                self.assertEqual(context.issues, [])
                self.assertEqual(len(queries), 1)
                self.assertEqual(json.loads(queries[0])['text_diff'], text)
                self.assertEqual(json.loads(queries[0])['amendment_id'], self.item['amendment_id'])
                validate_sources(context.amendment, self.boundary.documents)
                # Successful transport still does not confirm legal context.
                semantic = detect_semantic_changes(context.amendment, text)
                self.assertIsNone(semantic['changes'][0]['is_meaningful_change'])
            finally:
                self.assertIsNone(client.cleanup())

    def test_real_semantic_to_scorer_uses_shared_contract(self):
        text = compute_text_diff(self.item)
        semantic = detect_semantic_changes(self.item, text)
        validate_payload(SemanticDiffResult, semantic)
        scores = score_changes(semantic)
        result = dict(amendment=self.item, text_diff=text, semantic_diff=semantic, scoring=scores)
        self.assertEqual(set(result), {'amendment', 'text_diff', 'semantic_diff', 'scoring'})
        validate_payload(AmendmentResult, result)
        validate_sources(result, self.boundary.documents)
        self.assertEqual([c['change_id'] for c in semantic['changes']], [s['change_id'] for s in scores])
        for change, score in zip(semantic['changes'], scores):
            validate_payload(ScoringResult, score)
            self.assertIsNone(change['is_meaningful_change'])
            self.assertTrue(change['needs_review'])
            self.assertTrue(change['review_reason'])
            self.assertIsNone(score['significance'])
            self.assertIsNone(score['is_critical'])
            self.assertTrue(score['needs_review'])
            self.assertIn(change['review_reason'], score['review_reason'])


if __name__ == '__main__':
    unittest.main()
