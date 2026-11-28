"""Corpus coverage, identity, and browsing without an AI provider."""
import csv
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fastapi.testclient import TestClient

from backend.app.context.corpus_document_graph import build_corpus_graph
from backend.app.context.document_graph import CATALOG_PATH, CORPUS_DIR
from backend.shared_demo import create_app
from test.demo_suite.test_web_demo import docx


class CorpusGraphTests(unittest.TestCase):
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        (self.root / CORPUS_DIR).mkdir(parents=True)
        self.rows = []

    def add_source(self, identity, number, paragraphs=None, *, contents=None, date='2020-01-03'):
        path = Path(CORPUS_DIR) / (identity + '.docx')
        payload = contents if contents is not None else docx(*paragraphs)
        (self.root / path).write_bytes(payload)
        self.rows.append(dict(id=identity, so_ky_hieu=number, title='Văn bản ' + identity,
                              nguon_thu_thap='fixture', ngay_ban_hanh=date, ngay_co_hieu_luc='',
                              download_status='success', download_path=path.as_posix()))
        return payload

    def build(self):
        with (self.root / CATALOG_PATH).open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=self.rows[0].keys())
            writer.writeheader()
            writer.writerows(self.rows)
        return build_corpus_graph(self.root)

    def test_keeps_distinct_versions_aliases_ambiguous_outside_and_isolated_nodes(self):
        body = ['Điều 1. Nội dung', 'Nội dung giữ nguyên.']
        snapshot = self.add_source('base', '01/2020/NĐ-CP', body)
        self.add_source('base_copy', '01/2020/NĐ-CP', contents=snapshot)
        self.add_source('base_other_version', '01/2020/NĐ-CP', ['Điều 1. Nội dung', 'Phiên bản khác.'])
        self.add_source('isolated', '02/2020/NĐ-CP', body)
        self.add_source('target', '05/2020/NĐ-CP', ['Điều 1. Điều khoản đích'])
        original = 'Sửa đổi khoản 1 Điều 4 Nghị định số 05/2020/NĐ-CP.'
        self.add_source('source', '03/2020/NĐ-CP', [
            original, 'Bổ sung Điều 2 Nghị định số 01/2020/NĐ-CP.',
            'Thực hiện theo Nghị định số 04/2020/NĐ-CP.',
        ])
        self.add_source('corrupt', '06/2020/NĐ-CP', contents=b'not a docx')
        graph, report = self.build()

        nodes = {n['id']: n for n in graph['nodes']}
        self.assertIn('dataset:base_other_version', nodes)
        self.assertNotIn('dataset:base_copy', nodes)
        self.assertEqual(nodes['dataset:base']['aliases'][0]['dataset_id'], 'base_copy')
        self.assertEqual(nodes['dataset:base']['version']['snapshot_sha256'], sha256(snapshot).hexdigest())
        self.assertEqual(nodes['dataset:corrupt']['full_text_status'], 'READ_ERROR')
        self.assertEqual(nodes['number:04/2020/NĐ-CP']['full_text_status'], 'MISSING_FULL_TEXT')
        amendment, citation = graph['edges']
        self.assertEqual((amendment['source_id'], amendment['target_id'], amendment['relation']),
                         ('dataset:source', 'dataset:target', 'AMENDS'))
        self.assertEqual(amendment['evidence'][0]['quote'], original)
        self.assertEqual(amendment['evidence'][0]['source_refs'], ['block:1'])
        self.assertEqual((citation['relation'], citation['target_resolution']), ('CITES', 'OUTSIDE_CATALOG'))
        ambiguous, outside = report['needs_review']
        self.assertEqual(ambiguous['reason'], 'AMBIGUOUS_DOCUMENT_NUMBER')
        self.assertEqual(ambiguous['candidate_dataset_ids'], ['base', 'base_copy', 'base_other_version'])
        self.assertEqual(outside['reason'], 'TARGET_OUTSIDE_CATALOG')
        self.assertIn('dataset:isolated', nodes)
        self.assertNotIn('dataset:isolated', {edge[key] for edge in graph['edges']
                                             for key in ('source_id', 'target_id')})

    def test_replacement_quote_does_not_turn_nested_citation_into_directive(self):
        self.add_source('target', '01/2020/NĐ-CP', ['Điều 1. Nội dung'])
        self.add_source('source', '03/2020/NĐ-CP', [
            'Sửa đổi Điều 1 Nghị định số 01/2020/NĐ-CP như sau: “Điều 1. Tên điều',
            'Sửa đổi Điều 2 Nghị định số 02/2020/NĐ-CP “trích dẫn lồng”.',
            'Kết thúc nội dung thay thế.”',
            'Căn cứ Nghị định số 04/2020/NĐ-CP.',
        ])
        graph, _ = self.build()
        self.assertEqual([(e['relation'], e['target_id']) for e in graph['edges']],
                         [('AMENDS', 'dataset:target'), ('BASIS', 'number:04/2020/NĐ-CP')])

    def test_shared_graph_api_reports_missing_data_and_paginates_neighbors(self):
        path = self.root / 'graph.json'
        with TestClient(create_app(settings={}, runtime=self.root / 'runtime',
                                   document_graph_path=path)) as client:
            endpoint = '/api/demo/document-graph'
            missing = client.get(endpoint)
            self.assertEqual(missing.status_code, 503)
            self.assertEqual(missing.json()['detail']['code'], 'DOCUMENT_GRAPH_NOT_BUILT')
            self.add_source('isolate', '01/2020/NĐ-CP', ['Điều 1. Nội dung'])
            self.add_source('source', '03/2020/NĐ-CP', [
                'Căn cứ Nghị định số 04/2020/NĐ-CP.',
                'Thực hiện theo Nghị định số 05/2020/NĐ-CP.',
            ])
            graph, _ = self.build()
            path.write_text(json.dumps(graph, ensure_ascii=False), encoding='utf-8')
            overview = client.get(endpoint + '/overview').json()
            self.assertEqual((overview['node_count'], overview['edge_count']), (4, 2))
            self.assertEqual(len(overview['nodes']), 4)
            self.assertEqual(len(overview['edges']), 2)
            self.assertEqual(
                [(overview['nodes'][a]['id'], overview['nodes'][b]['id'], relation)
                 for a, b, relation in overview['edges']],
                [('dataset:source', 'number:04/2020/NĐ-CP', 'BASIS'),
                 ('dataset:source', 'number:05/2020/NĐ-CP', 'CITES')],
            )
            self.assertIn('dataset:isolate', {node['id'] for node in overview['nodes']})
            found = client.get(endpoint, params={'q': 'van ban isolate'}).json()
            self.assertEqual(found['total'], 1)
            self.assertEqual(found['node_count'], 4)
            self.assertEqual(found['edge_count'], 2)
            self.assertEqual(found['matches'][0]['id'], 'dataset:isolate')
            self.assertEqual(client.get(endpoint, params={'q': 'nonexistent'}).json()['total'], 0)
            self.assertEqual(client.get(endpoint, params={'node_id': 'dataset:isolate'}).json()['edges'], [])
            page = client.get(endpoint, params={'node_id': 'dataset:source', 'offset': 1, 'limit': 1}).json()
            self.assertEqual(page['total'], 2)
            self.assertEqual(page['edges'][0]['relation'], 'CITES')
            self.assertEqual(page['neighbors'][0]['id'], page['edges'][0]['target_id'])
            self.assertEqual(client.get(endpoint, params={'node_id': 'missing'}).status_code, 404)
