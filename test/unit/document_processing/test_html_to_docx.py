"""Offline regression checks; run from the repo root with unittest discover."""
import json
import os
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest

from docx import Document
from docx.oxml.ns import qn

from backend.app.document_processing.html_to_docx import convert_html_to_docx


class HtmlToDocxTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def convert(self, text, encoding='utf-8', **kwargs):
        source = self.root / 'input.html'
        source.write_bytes(text.encode(encoding))
        output, report = convert_html_to_docx(source, self.root / 'out.docx', **kwargs)
        return Document(output), json.loads(report.read_text(encoding='utf-8'))

    def test_vietnamese_and_inline_styles_and_breaks(self):
        doc, report = self.convert('<html><meta charset="utf-8"><body><p>Điều 1. A <b>nghĩa <i>vụ</i></b><br/>khác &amp; mới.</p></body></html>')
        self.assertEqual(doc.paragraphs[0].text, 'Điều 1. A nghĩa vụ\nkhác & mới.')
        self.assertTrue(any(r.bold and r.italic and r.text == 'vụ' for r in doc.paragraphs[0].runs))
        self.assertTrue(report['integrity_non_whitespace_exact_match'])

    def test_fragment_and_inline_tail_around_blocks(self):
        doc, _ = self.convert('Đầu <span>giữa</span><div><p>Khoản 1.</p></div>Đuôi <b>cuối</b>')
        self.assertEqual([p.text for p in doc.paragraphs], ['Đầu giữa', 'Khoản 1.', 'Đuôi cuối'])

    def test_reject_empty_body_despite_head_or_script(self):
        for text in ('<html><head><title>Luật</title></head><body> </body></html>',
                     '<html><body><script>alert(1)</script><style>p{}</style></body></html>',
                     '<html><body><img src="https://example.invalid/image.png"></body></html>'):
            with self.subTest(text=text):
                (self.root / 'input.html').write_text(text, encoding='utf-8')
                with self.assertRaises(ValueError):
                    convert_html_to_docx(self.root/'input.html', self.root/'out.docx')
                self.assertFalse((self.root/'out.docx').exists())
                self.assertFalse((self.root/'out.report.json').exists())

    def test_tables_keep_order_and_rowspan_colspan(self):
        doc, report = self.convert('<p>Trước</p><table><caption>Bảng phí</caption><tr><th rowspan="2">A</th><th colspan="2">B</th></tr><tr><td>C</td><td>D</td></tr></table><p>Sau</p>')
        self.assertEqual(report['table_count'], 1)
        self.assertEqual(report['merged_cell_count'], 2)
        texts = doc.element.body.xpath('.//w:t/text()')
        self.assertEqual(texts, ['Trước', 'Bảng phí', 'A', 'B', 'C', 'D', 'Sau'])
        self.assertEqual(doc.tables[0].cell(0,0)._tc, doc.tables[0].cell(1,0)._tc)
        self.assertEqual(doc.tables[0].cell(0,1)._tc, doc.tables[0].cell(0,2)._tc)

    def test_nested_table_not_duplicated(self):
        doc, report = self.convert('<table><tr><td><p>A</p><table><tr><td>B</td></tr></table><p>C</p></td><td>D</td></tr></table>')
        self.assertEqual(doc.element.body.xpath('.//w:t/text()'), ['A','B','C','D'])
        self.assertEqual(report['table_count'],2)

    def test_nested_lists_literal_labels_reported(self):
        doc, report = self.convert('<ol start="3"><li><p>Một</p><ul><li>Hai</li></ul></li><li value="8">Ba</li></ol>')
        self.assertEqual([p.text for p in doc.paragraphs], ['3. Một','• Hai','8. Ba'])
        self.assertEqual(len(report['generated_list_labels']),3)
        self.assertTrue(report['integrity_non_whitespace_exact_match'])

    def test_encoding_and_replacement_character_fail_closed(self):
        text='<html><head><meta charset="windows-1258"></head><body><p>ABC</p></body></html>'
        _, report=self.convert(text,encoding='cp1258')
        self.assertEqual(report['encoding'],'windows-1258')
        for path in (self.root/'out.docx',self.root/'out.report.json'): path.unlink()
        with self.assertRaises(ValueError):
            self.convert('<p>Luật \ufffd</p>')

    def test_no_overwrite_docx_or_report(self):
        self.convert('<p>Nội dung</p>')
        original=(self.root/'out.docx').read_bytes()
        with self.assertRaises(FileExistsError): self.convert('<p>Khác</p>')
        self.assertEqual(original,(self.root/'out.docx').read_bytes())
        (self.root/'out.docx').unlink()
        with self.assertRaises(FileExistsError): self.convert('<p>Khác</p>')
        self.assertFalse((self.root/'out.docx').exists())

    def test_invalid_spans_rejected_without_outputs(self):
        with self.assertRaises(ValueError):
            self.convert('<table><tr><td rowspan="3">A</td></tr></table>')
        self.assertFalse((self.root/'out.docx').exists())

    def test_assets_and_links_are_reported_without_network(self):
        doc, report=self.convert('<p>A<img src="https://example.invalid/a.png"><a href="https://example.invalid">B</a></p>')
        self.assertEqual(doc.paragraphs[0].text,'AB')
        self.assertEqual(report['links'][0]['href'],'https://example.invalid')
        self.assertIn('IMAGES_NOT_EMBEDDED',[w['code'] for w in report['warnings']])

    def test_br_between_legal_units_stays_a_line_break(self):
        doc, _=self.convert('<p>Điều 1. Nội dung<br>1. Khoản một<br>a) Điểm một</p>')
        self.assertEqual(doc.paragraphs[0].text,'Điều 1. Nội dung\n1. Khoản một\na) Điểm một')

    def test_inline_normal_overrides_and_superscript(self):
        doc, _=self.convert('<p><b>A<span style="font-weight:normal">B</span></b><sup>2</sup><sub>3</sub></p>')
        runs={r.text:r for r in doc.paragraphs[0].runs}
        self.assertTrue(runs['A'].bold)
        self.assertFalse(runs['B'].bold)
        self.assertTrue(runs['2'].font.superscript)
        self.assertTrue(runs['3'].font.subscript)

    def test_html_indentation_collapses_but_pre_keeps_newlines(self):
        doc, _=self.convert('<div style="text-align:center;font-weight:bold">\n<div>\n  Cơ quan\n ban hành\n</div>\n</div><pre>  A\n B</pre>')
        self.assertEqual(doc.paragraphs[0].text,'Cơ quan ban hành')
        self.assertEqual(doc.paragraphs[1].text,'  A\n B')
        self.assertTrue(doc.paragraphs[0].runs[0].bold)
        self.assertEqual(int(doc.paragraphs[0].alignment),1)

    def test_cli_vietnamese_paths_work_with_ascii_terminal_default(self):
        source=self.root/'đầu_vào.html'
        source.write_text('<p>Nội dung</p>',encoding='utf-8')
        module=Path(sys.modules[convert_html_to_docx.__module__].__file__)
        result=subprocess.run([sys.executable,'-B',str(module),str(source),str(self.root/'đầu_ra.docx')],
                              capture_output=True,env={**os.environ,'PYTHONIOENCODING':'ascii'})
        self.assertEqual(result.returncode,0,result.stderr.decode('utf-8'))
        self.assertIn('đầu_ra.docx',result.stdout.decode('utf-8'))
        self.assertTrue((self.root/'đầu_ra.docx').exists())


if __name__=='__main__':
    unittest.main()
