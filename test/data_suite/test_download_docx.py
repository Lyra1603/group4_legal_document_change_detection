"""Offline download-to-DOCX and retry regression tests."""
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

root=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('download_docx',root/'data/legal-dataset-study/open_document.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
HTML='<html><body><p>Điều 1. Nội dung tiếng Việt.</p></body></html>'

class DownloadDocxTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)
        self.csv=self.folder/'candidates.csv'
        with self.csv.open('w',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=['id','so_ky_hieu','title'])
            writer.writeheader()
            writer.writerow({'id':'1','so_ky_hieu':'100/2006/NĐ-CP','title':'Nghị định'})
        self.output=self.folder/'result'

    def run_case(self,html=HTML,**options):
        return module.download_documents(['1'],candidates_path=self.csv,output_dir=self.output,
            manifest_path=None,convert_docx=True,
            stream_factory=lambda:iter([{'id':'1','content_html':html}]),**options)

    def test_convert_and_retry_without_fetch(self):
        report=self.run_case()
        self.assertFalse(report['has_errors'],report)
        result=report['results'][0]
        self.assertEqual(result['status'],'converted')
        target=Path(result['path'])
        self.assertEqual(target.name,'100_2006_NĐ-CP.docx')
        self.assertFalse(list(self.output.glob('*.report.json')))
        self.assertEqual([p.suffix for p in self.output.iterdir()], ['.docx'])
        before=target.read_bytes()
        def no_network():
            raise AssertionError('Retry must use existing HTML')
        repeated=module.download_documents(['1'],candidates_path=self.csv,output_dir=self.output,
            manifest_path=None,convert_docx=True,stream_factory=no_network)
        self.assertEqual(repeated['results'][0]['status'],'skipped_unverified')
        self.assertEqual(target.read_bytes(),before)

    def test_conflicting_number_preserves_html_and_reports_error(self):
        report=self.run_case('<html><body><p>Số: 99/2026/TT-BTP</p></body></html>')
        self.assertTrue(report['has_errors'])
        self.assertEqual(report['results'][0]['status'],'conversion_error')
        self.assertFalse((self.output/'vbpl-1.html').exists())
        self.assertFalse(list(self.output.glob('*.docx')))

    def test_dry_run_creates_no_files(self):
        report=self.run_case(dry_run=True)
        self.assertEqual(report['results'][0]['status'],'would_download_and_convert')
        self.assertEqual(Path(report['results'][0]['path']).name,'100_2006_NĐ-CP.docx')
        self.assertFalse(self.output.exists())

    def test_corrupt_docx_is_not_overwritten(self):
        report=self.run_case()
        target=Path(report['results'][0]['path'])
        target.write_bytes(b'corrupt')
        repeated=self.run_case()
        self.assertEqual(repeated['results'][0]['status'],'existing_invalid')
        self.assertEqual(target.read_bytes(),b'corrupt')


    def test_legacy_document_number(self):
        from backend.app.document_processing.document_number import normalize_document_number
        self.assertEqual(normalize_document_number('68-HĐBT'), '68-HĐBT')
