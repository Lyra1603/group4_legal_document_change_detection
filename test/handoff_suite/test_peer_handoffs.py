"""Handoffs on one integrated source tree; no live retrieval claims."""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier
from time import monotonic
import unittest
from unittest.mock import patch

import httpx

from backend.app.pipeline import DocumentInput, ParsedDocument, run_comparison
from backend.app import demo_runner
from backend.app.document_processing.amendment_linker import link_amendments
from backend.app.change_analysis.text_diff import compute_text_diff, validate_text_diff
from backend.app.change_analysis.semantic_diff import detect_semantic_changes
from backend.app.change_analysis.scorer import score_changes
from backend.app.context.chunk_builder import build_chunks
from backend.app.context.source_registry import SourceRegistry
from backend.app.context.lightrag_client import MAX_QUERY_CHARS, LightRAGClient
from backend.app.config import LightRAGConfig
from backend.app.schemas.contracts import AmendmentResult, SemanticDiffResult, ScoringResult
from backend.app.schemas.report_validation import validate_payload, validate_report, validate_sources, validate_amendment
from test.context_suite.support import ContractServer
from test.handoff_suite.peer_versions import ROOT, peers


def sample_inputs(case):
    from backend.demo import SAMPLES
    sample = SAMPLES[case]
    return [DocumentInput(did, role, sample[did], ROOT / 'data/raw' / case / sample[did])
            for did, role in [('v1', 'BASE'), ('s', 'AMENDMENT')]]


def fresh_case(parser, adapter, case):
    parsed = [ParsedDocument(doc, parser.parse_docx(doc.path, document_id=doc.document_id), 'DOCX')
              for doc in sample_inputs(case)]
    boundary = adapter.adapt_documents(parsed)
    items, issues = link_amendments(boundary)
    return boundary, items, issues


class PeerHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser, cls.adapter, cls.consumer, cls.bridge, cls.provenance = peers()
        cls.boundary, cls.items, _ = fresh_case(cls.parser, cls.adapter, 'case_02')
        cls.item = next(i for i in cls.items if i['before_text'] is not None and i['after_text'] is not None)

    def assert_query_matches_diff(self, query, item, diff):
        self.assertLessEqual(len(query), MAX_QUERY_CHARS)
        payload = json.loads(query)
        self.assertEqual(payload['amendment_id'], item['amendment_id'])
        if 'text_diff' in payload:
            self.assertEqual(payload['text_diff'], diff)
            self.assertEqual(payload['before_text'], item['before_text'])
            self.assertEqual(payload['after_text'], item['after_text'])
            return 'full'
        compact = payload['changes']
        self.assertEqual(len(compact) + payload['omitted_change_count'], len(diff['changes']))
        if diff['changes']:
            self.assertTrue(compact)
        for span, original in zip(compact, diff['changes']):
            for key in ('type', 'old_start', 'old_end', 'new_start', 'new_end'):
                self.assertEqual(span[key], original[key])
            for source, prefix, excerpt in [('before_text', 'old', 'before_excerpt'),
                                            ('after_text', 'new', 'after_excerpt')]:
                start = max(0, original[prefix + '_start'] - 100)
                end = min(original[prefix + '_end'] + 100, start + 320)
                self.assertEqual(span[excerpt], item[source][start:end])
            self.assertEqual(span['removed_excerpt'], original['old_text'][:100])
            self.assertEqual(span['added_excerpt'], original['new_text'][:100])
        return 'compact'

    def test_fresh_parser_adapter_all_docx_cases(self):
        modes = set()
        for case in ('case_01', 'case_02', 'case_03'):
            with self.subTest(case=case):
                boundary, items, _ = fresh_case(self.parser, self.adapter, case)
                self.assertTrue(items)
                for item in items:
                    validate_amendment(item, boundary.documents, boundary.clauses)
                    text = compute_text_diff(item)
                    validate_text_diff(item, text)
                    if text is not None:
                        query = self.consumer.build_retrieval_query(item, text)
                        modes.add(self.assert_query_matches_diff(query, item, text))
        self.assertEqual(modes, {'full', 'compact'})

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

    def test_compact_query_keeps_full_id_and_rejects_an_id_that_cannot_fit(self):
        item = deepcopy(self.item)
        item['amendment_id'] = 's:' + 'a' * 4000
        diff = compute_text_diff(item)
        query = self.consumer.build_retrieval_query(item, diff)
        self.assertEqual(self.assert_query_matches_diff(query, item, diff), 'compact')

        item['amendment_id'] = 's:' + 'a' * MAX_QUERY_CHARS
        registry = SourceRegistry(
            build_chunks('long-id', list(self.boundary.documents.values()),
                         {d: 'uploaded-source' for d in self.boundary.documents},
                         max_chunks=5000, max_chars=100000),
            list(self.boundary.documents.values()))
        class MustNotQuery:
            def query(self, query):
                raise AssertionError('An over-limit ID reached retrieval')
        result = self.consumer.build_context(item, registry, MustNotQuery(), text_diff=compute_text_diff(item))
        self.assertEqual(result.issues[0]['code'], 'QUERY_INVALID')
        self.assertEqual(result.amendment['amendment_id'], item['amendment_id'])

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

    def test_long_case_keeps_full_diff_for_semantic_and_report(self):
        server = ContractServer()
        readiness = []
        def transport(request):
            if request.url.path == '/query/data':
                readiness.append(client.ready)
            return server(request)
        with TemporaryDirectory() as work:
            config = LightRAGConfig('http://contract-double', 'demo', top_k=256, max_chunks=5000)
            client = LightRAGClient(config, 'long-docx', Path(work), deadline=monotonic() + 45,
                                    transport=httpx.MockTransport(transport))
            def analyze(parsed, comparison_id, deadline):
                return demo_runner.run_demo_analysis(parsed, comparison_id, deadline, context_client=client)
            try:
                with patch.object(demo_runner, 'detect_semantic_changes', wraps=detect_semantic_changes) as semantic:
                    report = run_comparison(sample_inputs('case_03'), 'long-docx',
                                            deadline=client.deadline, analysis_runner=analyze)
                validate_report(report)
                self.assertFalse(report['errors'])
                self.assertFalse([w for w in report['warnings'] if w['stage'] == 'context'
                                  and w['code'] != 'RETRIEVAL_SCOPE_LIMITED'])
                results = [r for r in report['results'] if r['text_diff'] is not None]
                self.assertEqual(len(semantic.call_args_list), len(results))
                self.assertEqual(len(server.queries), len(results))
                self.assertTrue(all(readiness))
                formats = set()
                for call, query, result in zip(semantic.call_args_list, server.queries, results):
                    item, diff = call.args
                    self.assertEqual(diff, result['text_diff'])
                    self.assertEqual(diff, compute_text_diff(item))
                    formats.add(self.assert_query_matches_diff(query, item, diff))
                self.assertIn('compact', formats)
            finally:
                try:
                    self.assertIsNone(client.cleanup())
                finally:
                    client.close()

    def test_failed_retrieval_preserves_real_docx_text_diff(self):
        server = ContractServer(behavior='timeout')
        with TemporaryDirectory() as work:
            client = LightRAGClient(LightRAGConfig('http://contract-double', 'demo', top_k=32),
                                    'query-timeout', Path(work), deadline=monotonic() + 30,
                                    transport=httpx.MockTransport(server))
            def analyze(parsed, comparison_id, deadline):
                return demo_runner.run_demo_analysis(parsed, comparison_id, deadline, context_client=client)
            try:
                report = run_comparison(sample_inputs('case_02'), 'query-timeout',
                                        deadline=client.deadline, analysis_runner=analyze)
                validate_report(report)
                self.assertEqual(report['status'], 'PARTIAL')
                self.assertIn('RETRIEVAL_TIMEOUT', {issue['code'] for issue in report['warnings']})
                self.assertTrue(server.queries)
                result, = report['results']
                self.assertEqual(result['text_diff'], compute_text_diff(result['amendment']))
                validate_text_diff(result['amendment'], result['text_diff'])
            finally:
                try:
                    self.assertIsNone(client.cleanup())
                finally:
                    client.close()

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
