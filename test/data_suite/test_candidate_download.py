"""Offline checks for candidate membership, deduplication and safe HTML writes."""
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
import zipfile

module_path=Path(__file__).with_name('open_document_revised.py')
if not module_path.exists():
    module_path=Path(__file__).resolve().parents[2]/'data/legal-dataset-study/open_document.py'
spec=importlib.util.spec_from_file_location('candidate_downloader',module_path)
downloader=importlib.util.module_from_spec(spec); spec.loader.exec_module(downloader)
HTML='<html><head><title>Văn bản</title></head><body><p>Điều 1. Nội dung tiếng Việt.</p></body></html>'


class CandidateDownloadTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name); self.csv=self.root/'candidates.csv'; self.output=self.root/'target'
        self.rows=[{'id':str(i),'so_ky_hieu':f'{i:02}/2026/TT-BTP','title':f'Văn bản {i}'} for i in range(1,5)]
        self.write_csv(self.csv,self.rows)

    def write_csv(self,path,rows):
        with path.open('w',encoding='utf-8-sig',newline='') as handle:
            writer=csv.DictWriter(handle,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)

    def run_download(self,ids=None,**kwargs):
        return downloader.download_documents(ids,candidates_path=self.csv,output_dir=self.output,manifest_path=None,**kwargs)

    def existing(self,identity='1',content=HTML,subfolder=None):
        folder=self.output/subfolder if subfolder else self.output
        folder.mkdir(parents=True,exist_ok=True)
        path=folder/f'vbpl-{identity}.html'; path.write_text(content,encoding='utf-8'); return path

    def source_record(self,path,identity='1',**overrides):
        record={'dataset':downloader.DATASET,'revision':downloader.REVISION,'id':identity,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}|overrides
        path.with_suffix('.source.json').write_text(json.dumps(record),encoding='utf-8')

    def docx(self,path):
        path.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(path,'w') as archive:
            archive.writestr('word/document.xml','<document/>')

    def test_unknown_id_rejected_before_network_or_directory_creation(self):
        network=Mock()
        with self.assertRaisesRegex(ValueError,'không có'):
            self.run_download(['1','999'],stream_factory=network)
        network.assert_not_called(); self.assertFalse(self.output.exists())

    def test_legacy_html_in_subfolder_skipped_without_network(self):
        path=self.existing(subfolder='case_01'); before=path.read_bytes(); network=Mock()
        report=self.run_download(['1'],stream_factory=network)
        self.assertEqual(report['counts'],{'skipped_unverified':1})
        self.assertEqual(path.read_bytes(),before); network.assert_not_called()

    def test_empty_or_invalid_existing_html_never_overwritten(self):
        for content in ('','<html><body> </body></html>'):
            with self.subTest(content=content):
                path=self.existing(content=content); network=Mock()
                report=self.run_download(['1'],stream_factory=network)
                self.assertEqual(report['counts'],{'existing_invalid':1})
                self.assertEqual(path.read_text(encoding='utf-8'),content); network.assert_not_called()

    def test_source_verified_existing_file_skipped(self):
        path=self.existing(); self.source_record(path); network=Mock()
        report=self.run_download(['1'],stream_factory=network)
        self.assertEqual(report['counts'],{'skipped_existing':1}); network.assert_not_called()

    def test_wrong_revision_and_hash_are_not_claimed_valid(self):
        path=self.existing(); self.source_record(path,revision='different')
        report=self.run_download(['1'],stream_factory=Mock())
        self.assertEqual(report['counts'],{'existing_identity_conflict':1})
        self.source_record(path,sha256='wrong')
        report=self.run_download(['1'],stream_factory=Mock())
        self.assertEqual(report['counts'],{'existing_invalid':1})

    def test_malformed_source_record_is_reported(self):
        path=self.existing(); path.with_suffix('.source.json').write_text('[]',encoding='utf-8')
        self.assertEqual(self.run_download(['1'],stream_factory=Mock())['counts'],{'existing_invalid':1})

    def test_download_saves_utf8_html_and_source_identity(self):
        network=Mock(return_value=iter([{'id':'1','content_html':HTML}]))
        report=self.run_download(['1'],stream_factory=network)
        path=self.output/'vbpl-1.html'
        self.assertEqual(report['counts'],{'downloaded':1}); self.assertEqual(path.read_text(encoding='utf-8'),HTML)
        source=json.loads(path.with_suffix('.source.json').read_text(encoding='utf-8'))
        self.assertEqual((source['dataset'],source['revision'],source['id']),(downloader.DATASET,downloader.REVISION,'1'))
        self.assertEqual(source['sha256'],hashlib.sha256(path.read_bytes()).hexdigest())
        network.assert_called_once()

    def test_source_empty_body_is_rejected_and_not_saved(self):
        network=lambda:iter([{'id':'1','content_html':'<html><head><title>Luật</title></head><body><script>x</script></body></html>'}])
        report=self.run_download(['1'],stream_factory=network)
        self.assertEqual(report['counts'],{'empty_or_invalid_html':1}); self.assertFalse(self.output.exists())

    def test_html_validation_accepts_fragment_but_not_head_or_image_only(self):
        self.assertGreater(downloader.validate_html('<p>Điều 1. Nội dung</p>')['non_whitespace_characters'],0)
        for content in ('<html><head><title>Tên luật</title></head></html>','<body><img src="x"></body>','<body>&nbsp;\u200b</body>'):
            with self.subTest(content=content), self.assertRaises(ValueError): downloader.validate_html(content)

    def test_batch_stream_used_once_and_closed_after_found_ids(self):
        closed=[]
        def documents():
            try:
                yield {'id':'999','content_html':HTML}
                yield {'id':'1','content_html':HTML}
                yield {'id':'2','content_html':HTML}
                raise AssertionError('Must stop after all selected IDs are found')
            finally: closed.append(True)
        network=Mock(side_effect=documents)
        report=self.run_download(['1','1','2'],stream_factory=network)
        self.assertEqual(report['counts'],{'downloaded':2}); self.assertEqual(closed,[True]); network.assert_called_once()
        second=Mock()
        self.assertEqual(self.run_download(['1','2'],stream_factory=second)['counts'],{'skipped_existing':2})
        second.assert_not_called()

    def test_named_docx_in_target_subfolder_is_possible_duplicate(self):
        self.docx(self.output/'case_09/01_2026_TT-BTP.docx'); network=Mock()
        report=self.run_download(['1'],stream_factory=network)
        self.assertEqual(report['counts'],{'skipped_unverified':1}); network.assert_not_called()

    def test_manifest_checks_identity_and_only_files_inside_target(self):
        path=self.output/'case_09/renamed.docx'; self.docx(path)
        manifest=self.root/'manifest.csv'
        record={'document_id':'th1nhng0:1','local_path':str(path.relative_to(self.root)),
                'parent_files':downloader.DATASET+'@'+downloader.REVISION+':content:id=1','sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        self.write_csv(manifest,[record]); network=Mock()
        report=downloader.download_documents(['1'],candidates_path=self.csv,output_dir=self.output,manifest_path=manifest,manifest_root=self.root,stream_factory=network)
        self.assertEqual(report['counts'],{'skipped_existing':1}); network.assert_not_called()
        other=self.root/'other_target'
        report=downloader.download_documents(['1'],candidates_path=self.csv,output_dir=other,manifest_path=manifest,manifest_root=self.root,stream_factory=lambda:iter([{'id':'1','content_html':HTML}]))
        self.assertEqual(report['counts'],{'downloaded':1})

    def test_limit_counts_missing_documents_not_existing_files(self):
        self.existing('1')
        report=self.run_download(all_candidates=True,limit=2,stream_factory=lambda:iter([{'id':str(i),'content_html':HTML} for i in range(1,5)]))
        self.assertEqual(report['counts'],{'skipped_unverified':1,'downloaded':2})
        self.assertEqual(report['unexamined_due_to_limit'],1); self.assertFalse((self.output/'vbpl-4.html').exists())

    def test_dry_run_does_not_create_folder_or_call_network(self):
        network=Mock()
        report=self.run_download(all_candidates=True,limit=2,dry_run=True,stream_factory=network)
        self.assertEqual(report['counts'],{'would_download':2}); self.assertFalse(self.output.exists()); network.assert_not_called()

    def test_network_failure_preserves_completed_files(self):
        def documents():
            yield {'id':'1','content_html':HTML}
            raise ConnectionError('network interrupted')
        report=self.run_download(['1','2'],stream_factory=documents)
        self.assertEqual(report['counts'],{'downloaded':1,'download_error':1})
        self.assertEqual((self.output/'vbpl-1.html').read_text(encoding='utf-8'),HTML)
        self.assertFalse((self.output/'vbpl-2.html').exists())

    def test_missing_id_from_content_is_reported(self):
        report=self.run_download(['1'],stream_factory=lambda:iter([]))
        self.assertEqual(report['counts'],{'not_found':1}); self.assertFalse(self.output.exists())

    def test_file_appearing_during_fetch_is_not_overwritten(self):
        def fetch():
            self.existing(content='<p>File tạo bởi tiến trình khác.</p>')
            return iter([{'id':'1','content_html':HTML}])
        report=self.run_download(['1'],stream_factory=fetch)
        self.assertEqual(report['counts'],{'skipped_unverified':1})
        self.assertIn('tiến trình khác',(self.output/'vbpl-1.html').read_text(encoding='utf-8'))

    def test_exclusive_source_record_write_rolls_back_only_new_html(self):
        self.output.mkdir(); sidecar=self.output/'vbpl-1.source.json'; sidecar.write_text('keep',encoding='utf-8')
        with self.assertRaises(FileExistsError): downloader._save(HTML,self.rows[0],self.output)
        self.assertFalse((self.output/'vbpl-1.html').exists()); self.assertEqual(sidecar.read_text(),'keep')

    def test_uuid_string_id_and_duplicate_candidate_rejection(self):
        identity='abc-123-def'; self.write_csv(self.csv,[self.rows[0]|{'id':identity}])
        report=self.run_download([identity],stream_factory=lambda:iter([{'id':identity,'content_html':HTML}]))
        self.assertEqual(report['counts'],{'downloaded':1})
        self.write_csv(self.csv,[self.rows[0],self.rows[0]])
        with self.assertRaises(ValueError): self.run_download(['1'],dry_run=True)

    def test_cli_requires_selection_and_can_plan_without_datasets(self):
        result=subprocess.run([sys.executable,'-B',str(module_path)],capture_output=True)
        self.assertEqual(result.returncode,2)
        result=subprocess.run([sys.executable,'-B',str(module_path),'--id','1','--candidates',str(self.csv),'--output-dir',str(self.output),'--manifest',str(self.root/'missing.csv'),'--dry-run'],capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr.decode('utf-8')); self.assertFalse(self.output.exists())

    def test_id_named_docx_and_number_named_pdf_are_possible_duplicates(self):
        for extension in ('docx','pdf'):
            folder=self.root/extension; folder.mkdir()
            path=folder/('vbpl-1.docx' if extension=='docx' else '01_2026_TT-BTP.pdf')
            if extension=='docx': self.docx(path)
            else: path.write_bytes(b'%PDF-1.7\nSource requires manual review')
            network=Mock()
            report=downloader.download_documents(['1'],candidates_path=self.csv,output_dir=folder,manifest_path=None,stream_factory=network)
            self.assertEqual(report['counts'],{'skipped_unverified':1}); network.assert_not_called()

    def test_malformed_manifest_fails_before_network(self):
        manifest=self.root/'bad-manifest.csv'; manifest.write_text('wrong_column\nvalue\n',encoding='utf-8')
        network=Mock()
        with self.assertRaisesRegex(ValueError,'Manifest'):
            downloader.download_documents(['1'],candidates_path=self.csv,output_dir=self.output,manifest_path=manifest,stream_factory=network)
        network.assert_not_called(); self.assertFalse(self.output.exists())

    def test_cli_dry_run_can_write_only_explicitly_requested_report(self):
        report=self.root/'plan.json'
        result=subprocess.run([sys.executable,'-B',str(module_path),'--id','1','--candidates',str(self.csv),'--output-dir',str(self.output),'--manifest',str(self.root/'missing.csv'),'--dry-run','--report',str(report)],capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr.decode('utf-8'))
        self.assertEqual(json.loads(report.read_text(encoding='utf-8'))['counts'],{'would_download_and_convert':1})
        self.assertFalse(self.output.exists())


if __name__=='__main__': unittest.main()
