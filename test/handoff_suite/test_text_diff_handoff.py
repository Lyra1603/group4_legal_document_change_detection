"""Exercise the integrated DOCX handoff with a deterministic HTTP contract double."""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic
import unittest
from unittest.mock import patch

import httpx

from backend.app import demo_runner
from backend.app.change_analysis.text_diff import compute_text_diff, validate_text_diff
from backend.app.config import LightRAGConfig
from backend.app.context.context_builder import build_retrieval_query
from backend.app.context.lightrag_client import MAX_QUERY_CHARS, LightRAGClient, RetrievalError
from backend.app.pipeline import DocumentInput, run_comparison
from backend.demo import ROOT, SAMPLES
from test.context_suite.support import ContractServer, sample


def reconstruct(before, changes):
    after = before
    for change in reversed(changes):
        start, end = change['old_start'], change['old_end']
        after = after[:start] + change['new_text'] + after[end:]
    return after


class TextDiffTests(unittest.TestCase):
    def test_absent_empty_and_equal_sides(self):
        for before, after, operations in (
            (None, 'known', None), ('known', None, None), (None, None, None),
            ('', '', []), ('same', 'same', []), ('', 'new', ['INSERT']),
            ('old', '', ['DELETE']), ('old', 'NEW', ['REPLACE']),
        ):
            with self.subTest(before=before, after=after):
                item = dict(amendment_id='edge', before_text=before, after_text=after)
                diff = compute_text_diff(item)
                validate_text_diff(item, diff)
                if operations is None:
                    self.assertIsNone(diff)
                    with self.assertRaises(ValueError):
                        validate_text_diff(item, dict(amendment_id='edge', changes=[]))
                    continue
                self.assertEqual(diff['amendment_id'], 'edge')
                self.assertEqual([change['type'] for change in diff['changes']], operations)
                self.assertEqual(reconstruct(before, diff['changes']), after)

    def test_edits_preserve_code_points_and_input(self):
        before = 'A😀a\u0301  khoảng\tgiữ\r\nlặp lặp\nC'
        after = 'Z😀á\t khoảng\tgiữ\nlặp lặp\nD!'
        item = dict(amendment_id='unicode', before_text=before, after_text=after)
        original = deepcopy(item)
        diff = compute_text_diff(item)
        self.assertGreater(len(diff['changes']), 1)
        self.assertEqual(compute_text_diff(item), diff)
        self.assertEqual(item, original)
        validate_text_diff(item, diff)
        self.assertEqual(reconstruct(before, diff['changes']), after)
        for change in diff['changes']:
            self.assertEqual(before[change['old_start']:change['old_end']], change['old_text'])
            self.assertEqual(after[change['new_start']:change['new_end']], change['new_text'])

    def test_validator_rejects_empty_foreign_or_invalid_result(self):
        item = dict(amendment_id='corrupt', before_text='30 days', after_text='15 days')
        diff = compute_text_diff(item)
        broken = {
            'missing': None,
            'foreign': {**diff, 'amendment_id': 'other'},
            'omitted': {**diff, 'changes': []},
            'duplicate': {**diff, 'changes': diff['changes'] * 2},
        }
        for key, value in (
            ('old_start', -1), ('old_end', len(item['before_text']) + 1),
            ('new_start', True), ('new_end', 1.0), ('old_text', 'wrong'), ('type', 'INSERT'),
        ):
            broken[key] = {**diff, 'changes': [{**diff['changes'][0], key: value}]}
        for name, invalid in broken.items():
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_text_diff(item, invalid)

    def test_compact_query_keeps_id_or_rejects_it_when_over_limit(self):
        _, _, item, _ = sample()
        item.update(amendment_id='id-' + 'a' * 4100, before_text='30 days', after_text='15 days')
        query = build_retrieval_query(item, compute_text_diff(item))
        payload = json.loads(query)
        self.assertLessEqual(len(query), MAX_QUERY_CHARS)
        self.assertEqual(payload['amendment_id'], item['amendment_id'])
        self.assertEqual(payload['omitted_change_count'], 0)

        item['amendment_id'] += 'a' * MAX_QUERY_CHARS
        with self.assertRaisesRegex(RetrievalError, 'QUERY_INVALID'):
            build_retrieval_query(item, compute_text_diff(item))


class TextDiffHandoffTests(unittest.TestCase):
    def compare(self, case, *, behavior='normal'):
        samples = SAMPLES[case]
        root = ROOT / 'data' / 'raw' / case
        files = [
            DocumentInput('v1', 'BASE', samples['v1'], root / samples['v1']),
            DocumentInput('s', 'AMENDMENT', samples['s'], root / samples['s']),
        ]
        server = ContractServer(behavior=behavior)
        deadline = monotonic() + 45

        def transport(request):
            if request.url.path == '/query/data':
                self.assertTrue(client.ready)
                self.assertIn(('GET', '/documents/track_status/track-demo'), server.calls)
            return server(request)

        with TemporaryDirectory() as directory:
            client = LightRAGClient(
                LightRAGConfig('http://contract-double', 'demo', top_k=256, max_chunks=5000),
                case, Path(directory), deadline=deadline, transport=httpx.MockTransport(transport),
            )
            try:
                with patch.object(demo_runner, 'detect_semantic_changes',
                                  wraps=demo_runner.detect_semantic_changes) as semantic:
                    report = run_comparison(
                        files, case, deadline=deadline,
                        analysis_runner=lambda *args: demo_runner.run_demo_analysis(
                            *args, context_client=client,
                        ),
                    )
            finally:
                self.assertIsNone(client.cleanup())

        self.assertEqual(report['errors'], [])
        results = [row for row in report['results'] if row['text_diff'] is not None]
        self.assertEqual(semantic.call_count, len(results))
        for row, call in zip(results, semantic.call_args_list):
            item, diff = call.args
            self.assertEqual(item, row['amendment'])
            self.assertEqual(diff, row['text_diff'])
            validate_text_diff(item, diff)
            self.assertEqual(reconstruct(item['before_text'], diff['changes']), item['after_text'])
            self.assertEqual(row['semantic_diff']['amendment_id'], item['amendment_id'])
            self.assertEqual(
                {change['change_id'] for change in row['semantic_diff']['changes']},
                {score['change_id'] for score in row['scoring']},
            )
        return report, results, server.queries

    def test_short_full_query_and_semantic_input(self):
        _, results, queries = self.compare('case_02')
        row, = results
        query, = queries
        payload = json.loads(query)
        self.assertLessEqual(len(query), MAX_QUERY_CHARS)
        self.assertEqual(payload['text_diff'], row['text_diff'])
        for key in ('before_text', 'after_text', 'amendment_id'):
            self.assertEqual(payload[key], row['amendment'][key])

    def test_long_compact_queries_preserve_offsets_and_full_semantic_input(self):
        _, results, queries = self.compare('case_03')
        self.assertEqual(len(results), 13)
        self.assertEqual(len(queries), len(results))
        compact_queries = 0
        for query, row in zip(queries, results):
            item, diff = row['amendment'], row['text_diff']
            payload = json.loads(query)
            self.assertEqual(payload['amendment_id'], item['amendment_id'])
            self.assertLessEqual(len(query), MAX_QUERY_CHARS)
            if 'text_diff' in payload:
                self.assertEqual(payload['text_diff'], diff)
                continue
            compact_queries += 1
            selected = payload['changes']
            self.assertTrue(selected)
            self.assertGreater(payload['omitted_change_count'], 0)
            self.assertEqual(len(selected) + payload['omitted_change_count'], len(diff['changes']))
            for span, change in zip(selected, diff['changes']):
                for key in ('type', 'old_start', 'old_end', 'new_start', 'new_end'):
                    self.assertEqual(span[key], change[key])
                for side, source in (('old', 'before'), ('new', 'after')):
                    start = max(0, change[side + '_start'] - 100)
                    stop = min(change[side + '_end'] + 100, start + 320)
                    self.assertEqual(span[source + '_excerpt'], item[source + '_text'][start:stop])
                self.assertEqual(span['removed_excerpt'], change['old_text'][:100])
                self.assertEqual(span['added_excerpt'], change['new_text'][:100])
        self.assertGreater(compact_queries, 0)

    def test_timeout_leaves_original_diff_in_report(self):
        report, results, queries = self.compare('case_02', behavior='timeout')
        row, = results
        self.assertTrue(queries)
        self.assertEqual(row['text_diff'], compute_text_diff(row['amendment']))
        self.assertEqual(report['status'], 'PARTIAL')
        self.assertIn('RETRIEVAL_TIMEOUT', {warning['code'] for warning in report['warnings']})
