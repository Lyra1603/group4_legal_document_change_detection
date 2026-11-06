import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from docx import Document

from backend.app.document_processing.document_reader import ReadError, read_document
from backend.app.document_processing.parser.doc_parser import parse_document
from backend.app.pipeline import read_and_parse_document, run_pipeline


class ReaderParserTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'sample.docx'

    def test_docx_sources_and_table_survive_pipeline(self):
        doc = Document()
        doc.add_paragraph('Mở đầu')
        doc.add_paragraph('')
        doc.add_paragraph('Điều 2. Thời hạn')
        doc.add_paragraph('Nộp trong 30 ngày.')
        table = doc.add_table(rows=1, cols=2)
        table.cell(0, 0).text = 'Loại A'
        table.cell(0, 1).text = '15 ngày'
        doc.add_paragraph('Điều 5a. Trách nhiệm\nPhải báo cáo.')
        doc.add_paragraph('Nơi nhận:')
        doc.add_paragraph('Không phải nội dung Điều')
        doc.save(self.path)
        result = read_and_parse_document(str(self.path), 'v1', 'BASE')
        blocks = result['document']['blocks']
        clauses = result['clauses']
        self.assertEqual([c['unit_id'] for c in clauses], ['v1:article_2', 'v1:article_5a'])
        self.assertEqual(clauses[0]['source_refs'], ['docx:paragraph_3', 'docx:paragraph_4', 'docx:table_1'])
        self.assertIn('Loại A | 15 ngày', clauses[0]['content'])
        self.assertEqual(clauses[1]['content'], 'Phải báo cáo.')
        refs = {b['source_ref'] for b in blocks}
        for clause in clauses:
            self.assertTrue(set(clause['source_refs']) <= refs)
        self.assertEqual(blocks[0]['text'], 'Mở đầu')
        self.assertEqual(blocks[-1]['text'], 'Không phải nội dung Điều')

    def test_shared_fixture_contract(self):
        fixture = json.loads((Path(__file__).parent / 'fixtures' / 'reader_parser_case.json').read_text(encoding='utf-8'))
        self.assertEqual(parse_document(fixture['extracted_document']), fixture['expected_clauses'])

    def test_empty_docx(self):
        Document().save(self.path)
        with self.assertRaises(ReadError) as raised:
            read_document(str(self.path), 'v1', 'BASE')
        self.assertEqual(raised.exception.code, 'NO_TEXT')

    def test_corrupt_docx(self):
        self.path.write_text('invalid', encoding='utf-8')
        with self.assertRaises(ReadError) as raised:
            read_document(str(self.path), 'v1', 'BASE')
        self.assertEqual(raised.exception.code, 'READ_FAILED')

    def test_missing_file_and_invalid_role(self):
        with self.assertRaises(ReadError) as raised:
            read_document(str(self.path), 'v1', 'BASE')
        self.assertEqual(raised.exception.code, 'FILE_NOT_FOUND')
        with self.assertRaises(ValueError):
            read_document(str(self.path), 'v1', 'INVALID')

    def test_no_articles_and_duplicate_articles(self):
        for lines, code in [(['Lời mở đầu'], 'STRUCTURE_NOT_FOUND'),
                            (['Điều 1. A', 'Điều 1. B'], 'AMBIGUOUS_STRUCTURE')]:
            with self.subTest(code=code):
                doc = Document()
                for line in lines:
                    doc.add_paragraph(line)
                doc.save(self.path)
                with self.assertRaises(ReadError) as raised:
                    read_and_parse_document(str(self.path), 'v1', 'BASE')
                self.assertEqual(raised.exception.code, code)

    def test_legacy_pipeline_has_document_scoped_ids(self):
        result = run_pipeline('Điều 1. Hạn\n30 ngày.', 'Điều 1. Hạn\n15 ngày.')
        self.assertEqual(result[0]['v1']['unit_id'], 'v1:article_1')
        self.assertEqual(result[0]['v2']['unit_id'], 'v2:article_1')
        self.assertEqual(result[0]['v1']['source_refs'], [])
        self.assertTrue(result[0]['semantic_diff']['is_meaningful_change'])

    def test_text_pdf_keeps_page_source(self):
        import pymupdf
        path = self.path.with_suffix('.pdf')
        pdf = pymupdf.open()
        pdf.new_page().insert_text((72, 72), 'Readable reference text')
        pdf.save(path)
        pdf.close()
        result = read_and_parse_document(str(path), 'ref_1', 'REFERENCE')
        self.assertEqual(result['document']['blocks'][0]['source_ref'], 'pdf:page_1')
        self.assertIn('Readable reference text', result['document']['blocks'][0]['text'])
        self.assertEqual(result['clauses'], [])


if __name__ == '__main__':
    unittest.main()
