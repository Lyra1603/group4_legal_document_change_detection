"""Số của chính văn bản, không phải số hiệu được viện dẫn; tên mặc định/API/CLI."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from docx import Document
from backend.app.document_processing.document_number import identify_document_number, normalize_document_number, resolve_docx_output
from backend.app.document_processing.html_to_docx import convert_html_to_docx
from backend.app.document_processing.pdf_to_docx import convert_pdf_to_docx


class DocumentNumberTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)

    def html_source(self,text):
        source=self.root/'input.html'
        source.write_text(text,encoding='utf-8')
        return source

    def test_screenshot_numbers_and_windows_filenames(self):
        for value in ('84/2026/TT-BXD','413/2026/NĐ-CP','17/2026/TT-BTP'):
            with self.subTest(value=value):
                number,evidence=identify_document_number('CƠ QUAN\nSố: '+value+'\nHà Nội\nCăn cứ Luật số 91/2015/QH13')
                self.assertEqual(number,value)
                self.assertEqual(resolve_docx_output(self.root/'in.pdf',None,number).name,value.replace('/','_')+'.docx')
                self.assertEqual(evidence[0]['source'],'document_header')

    def test_label_split_over_lines_and_separators(self):
        number,_=identify_document_number('Số ký hiệu\n 001 / 2026 / TT - BTP\n')
        self.assertEqual(number,'001/2026/TT-BTP')

    def test_number_without_year(self):
        self.assertEqual(normalize_document_number('25/VBHN-BTC'),'25/VBHN-BTC')
        self.assertEqual(normalize_document_number('01/GD-ĐT'),'01/GD-ĐT')

    def test_references_are_not_document_identity(self):
        number,_=identify_document_number('THÔNG TƯ\nSửa đổi Thông tư số 05/2011/TT-BTP\nCăn cứ Bộ luật số 91/2015/QH13\nĐiều 1. Số: 02/2026/TT-BTP')
        self.assertIsNone(number)

    def test_title_uses_own_first_number_not_target(self):
        number,_=identify_document_number(title='Thông tư số 08/2014/TT-BTP Sửa đổi Thông tư số 05/2011/TT-BTP')
        self.assertEqual(number,'08/2014/TT-BTP')

    def test_conflicting_header_values_fail(self):
        with self.assertRaisesRegex(ValueError,'xung đột'):
            identify_document_number('Số: 84/2026/TT-BXD\nSố: 17/2026/TT-BTP')

    def test_provided_metadata_conflict_fails(self):
        with self.assertRaisesRegex(ValueError,'xung đột'):
            identify_document_number('Số: 84/2026/TT-BXD',provided='17/2026/TT-BTP')

    def test_bad_metadata_cannot_escape_output_directory(self):
        for value in ('../x','84/2026/TT-BXD.docx','C:\\evil','', '17/2026/TT-BTP/../../x'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_document_number(value)

    def test_html_default_name_from_metadata_table(self):
        source=self.html_source('<table><tr><td>Số ký hiệu</td><td>84/2026/TT-BXD</td></tr></table><p>Điều 1. Nội dung</p>')
        output,log=convert_html_to_docx(source)
        self.assertEqual(output.name,'84_2026_TT-BXD.docx')
        report=json.loads(log.read_text(encoding='utf-8'))
        self.assertEqual(report['document_number'],'84/2026/TT-BXD')
        self.assertTrue(report['automatic_output_name'])

    def test_html_meta_tag_name_and_output_dir(self):
        source=self.html_source('<html><head><meta name="so_ky_hieu" content="17/2026/TT-BTP"></head><body><p>Nội dung</p></body></html>')
        output,_=convert_html_to_docx(source,output_dir=self.root/'out')
        self.assertEqual(output,self.root/'out/17_2026_TT-BTP.docx')

    def test_html_missing_number_requires_metadata_or_manual_output(self):
        source=self.html_source('<p>Sửa đổi Thông tư số 05/2011/TT-BTP</p>')
        with self.assertRaisesRegex(ValueError,'Không xác định'):
            convert_html_to_docx(source)
        self.assertFalse(list(self.root.glob('*.docx')))
        output,log=convert_html_to_docx(source,document_number='08/2014/TT-BTP')
        self.assertEqual(output.name,'08_2014_TT-BTP.docx')
        self.assertEqual(json.loads(log.read_text(encoding='utf-8'))['document_number_evidence'][0]['source'],'provided_metadata')

    def test_html_conflicting_numbers_does_not_write(self):
        source=self.html_source('<p>Số: 84/2026/TT-BXD</p><p>Nội dung</p>')
        with self.assertRaises(ValueError):
            convert_html_to_docx(source,document_number='17/2026/TT-BTP')
        self.assertFalse(list(self.root.glob('*.docx')))

    def test_explicit_output_is_backward_compatible_and_does_not_overwrite(self):
        source=self.html_source('<p>Số: 84/2026/TT-BXD</p><p>Nội dung</p>')
        output,log=convert_html_to_docx(source,self.root/'chosen.docx')
        self.assertEqual(output.name,'chosen.docx')
        self.assertFalse(json.loads(log.read_text(encoding='utf-8'))['automatic_output_name'])
        with self.assertRaises(FileExistsError): convert_html_to_docx(source,self.root/'chosen.docx')

    def test_default_name_collision_does_not_overwrite(self):
        source=self.html_source('<p>Số: 84/2026/TT-BXD</p><p>Nội dung</p>')
        output,_=convert_html_to_docx(source)
        old=output.read_bytes()
        with self.assertRaises(FileExistsError): convert_html_to_docx(source)
        self.assertEqual(output.read_bytes(),old)

    def test_pdf_module_from_docx_default_and_report(self):
        source=self.root/'source.docx'
        doc=Document(); doc.add_paragraph('Số: 413/2026/NĐ-CP'); doc.add_paragraph('Điều 1. Nội dung'); doc.save(source)
        output,log=convert_pdf_to_docx(source,from_docx=True)
        self.assertEqual(output.name,'413_2026_NĐ-CP.docx')
        self.assertEqual(json.loads(log.read_text(encoding='utf-8'))['document_number'],'413/2026/NĐ-CP')
        self.assertEqual(Document(source).paragraphs[0].text,'Số: 413/2026/NĐ-CP')

    def test_manual_output_and_output_dir_cannot_be_combined(self):
        with self.assertRaises(ValueError): resolve_docx_output(self.root/'in.html',self.root/'x.docx','17/2026/TT-BTP',self.root/'out')

    def test_cli_optional_output_name(self):
        source=self.html_source('<p>Số: 17/2026/TT-BTP</p><p>Nội dung</p>')
        module=Path(sys.modules[convert_html_to_docx.__module__].__file__)
        result=subprocess.run([sys.executable,'-B',str(module),str(source)],capture_output=True,env={**os.environ,'PYTHONIOENCODING':'ascii'})
        self.assertEqual(result.returncode,0,result.stderr.decode('utf-8'))
        self.assertTrue((self.root/'17_2026_TT-BTP.docx').exists())


if __name__=='__main__': unittest.main()
