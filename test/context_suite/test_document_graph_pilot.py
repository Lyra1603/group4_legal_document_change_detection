import json
from pathlib import Path
import unittest

from backend.app.context.document_graph import _relations, prepare_pilot
from backend.app.document_processing.parser.legal_structure_parser import parse_docx
from backend.app.schemas.report_validation import validate_sources


ROOT = Path(__file__).resolve().parents[2]


class DocumentGraphPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        selection = json.loads((ROOT / 'data/legal-dataset-study/document-graph-pilot.json').read_text(encoding='utf-8'))
        cls.graph, cls.registry = prepare_pilot(ROOT, selection, 'pilot-test')

    def test_two_docx_and_missing_target_are_separate_nodes(self):
        nodes = {node['id']: node for node in self.graph['nodes']}
        self.assertEqual(nodes['dataset:26170']['number'], '05/2011/TT-BTP')
        self.assertEqual(nodes['dataset:56666']['full_text_status'], 'AVAILABLE_IN_PILOT')
        targets = [node for node in nodes.values() if node['number'] == '22/2010/TT-BTP']
        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0]['full_text_status'], 'AVAILABLE_OUTSIDE_PILOT')
        self.assertTrue((ROOT / targets[0]['source']['path']).is_file())
        self.assertTrue(any(edge['target_id'] == targets[0]['id'] for edge in self.graph['edges']))
        missing = nodes['number:65/2005/NĐ-CP']
        self.assertEqual(missing['full_text_status'], 'MISSING_FULL_TEXT')
        self.assertIsNone(missing['version'])
        self.assertTrue(any(edge['target_id'] == missing['id'] for edge in self.graph['edges']))

    def test_relation_and_review_quotes_reopen_against_original_docx(self):
        sources = {file['document_id']: {'blocks': parse_docx(ROOT / file['path'])['source_blocks']}
                   for file in self.graph['files']}
        validate_sources(self.graph['edges'], sources)
        validate_sources(self.graph['needs_review'], sources)
        edges = [edge for edge in self.graph['edges'] if edge['source_id'] == 'dataset:56666'
                 and edge['target_id'] == 'dataset:26170' and edge['scope'] == ['khoản 2', 'Điều 2']]
        self.assertTrue(edges)
        self.assertEqual(edges[0]['basis'], 'SCOPED_BY_HEADING')
        self.assertEqual([e['source_refs'] for e in edges[0]['evidence']], [['block:22'], ['block:21']])

    def test_index_source_map_resolves_only_selected_blocks(self):
        self.assertEqual(len(self.graph['lightrag_source_map']), 3)
        for record in self.graph['lightrag_source_map']:
            self.assertEqual(self.registry.evidence(dict(file_path=record['file_source'], content=record['text'])),
                             dict(document_id=record['document_id'], source_refs=record['source_refs'], quote=record['text']))

    def test_compound_actions_and_quoted_text_do_not_become_edges(self):
        blocks = [dict(source_ref=f'block:{index}', text=text) for index, text in enumerate([
            'Điều 1. Sửa đổi, bổ sung một số điều của Thông tư số 05/2011/TT-BTP',
            '1. Sửa đổi khoản 1 và bãi bỏ khoản 2 Điều 4 như sau:',
            '“Bãi bỏ Điều 1 Thông tư số 22/2010/TT-BTP.',
            'Kết thúc nội dung thay thế.”',
            '2. Bãi bỏ khoản 2 và 3 Điều 7.',
            '3. Bổ sung khoản 6a, 6b Điều 9.',
            '4. Thực hiện theo quy định tại khoản 1 Điều 2 của Thông tư số 22/2010/TT-BTP.',
        ], 1)]
        relations = list(_relations('dataset:example', '08/2014/TT-BTP', blocks))
        self.assertEqual([r['reason'] for r in relations if 'reason' in r],
                         ['COLLECTIVE_AMENDMENT_HEADING', 'COMPOUND_ACTION'])
        self.assertEqual([(r['relation'], r['target_number'], r['scope']) for r in relations if 'reason' not in r], [
            ('REPEALS', '05/2011/TT-BTP', ['khoản 2 và 3', 'Điều 7']),
            ('SUPPLEMENTS', '05/2011/TT-BTP', ['khoản 6a, 6b', 'Điều 9']),
            ('CITES', '22/2010/TT-BTP', ['khoản 1', 'Điều 2']),
        ])
