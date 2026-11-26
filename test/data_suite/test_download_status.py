import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'data/legal-dataset-study' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


downloader = load('status_downloader', 'open_document.py')
rules = load('status_rules', 'civil_metadata_rules.py')


class DownloadStatusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.candidates = self.root / 'candidates.csv'
        self.rows = [dict.fromkeys(rules.COLUMNS, '') | {
            'id': str(n), 'title': 'dân sự', 'so_ky_hieu': f'{n}/2020/NĐ-CP'} for n in (1, 2)]
        self.write(self.candidates, self.rows)

    def write(self, path, rows, columns=None):
        with path.open('w', encoding='utf-8-sig', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=columns or rules.COLUMNS)
            writer.writeheader()
            writer.writerows(rows)

    def read(self):
        with self.candidates.open(encoding='utf-8-sig', newline='') as handle:
            return list(csv.DictReader(handle))

    def run_download(self, ids, stream, **options):
        return downloader.download_documents(ids, candidates_path=self.candidates,
            output_dir=self.root / 'output', manifest_path=None,
            stream_factory=lambda: iter(stream), **options)

    def test_per_document_write_and_network_failure(self):
        def stream():
            yield {'id': '1', 'content_html': '<body>Content</body>'}
            rows = self.read()
            self.assertEqual(rows[0]['download_status'], 'success')
            self.assertEqual(rows[1]['download_status'], '')
            raise OSError('network interrupted')
        result = self.run_download(['1', '2'], stream())
        self.assertTrue(result['has_errors'])
        rows = self.read()
        self.assertEqual([r['download_status'] for r in rows], ['success', 'failed'])
        self.assertIn('download_error', rows[1]['download_result'])

    def test_empty_source_not_found_and_preserve_metadata(self):
        self.run_download(['1', '2'], [{'id': '1', 'content_html': '<body></body>'}])
        rows = self.read()
        self.assertEqual([r['download_status'] for r in rows], ['failed', 'failed'])
        self.assertTrue(rows[1]['download_result'].startswith('not_found'))
        self.assertEqual([{c: r[c] for c in rules.COLUMNS} for r in rows], self.rows)

    def test_dry_run_does_not_touch_csv(self):
        before = self.candidates.read_bytes()
        self.run_download(['1'], [], dry_run=True)
        self.assertEqual(self.candidates.read_bytes(), before)

    def test_docx_result_and_unverified_retry(self):
        self.run_download(['1'], [{'id': '1', 'content_html': '<body>Content</body>'}], convert_docx=True)
        row = self.read()[0]
        self.assertEqual(row['download_status'], 'success')
        self.assertTrue(row['download_path'].endswith('.docx'))
        self.run_download(['1'], [], convert_docx=True)
        self.assertEqual(self.read()[0]['download_status'], 'failed')
        self.assertTrue(self.read()[0]['download_result'].startswith('skipped_unverified'))

    def test_concurrent_csv_edit_is_preserved(self):
        def stream():
            self.candidates.write_bytes(self.candidates.read_bytes() + b'\n')
            self.changed = self.candidates.read_bytes()
            yield {'id': '1', 'content_html': '<body>Content</body>'}
        with self.assertRaises(downloader.CandidateUpdateError):
            self.run_download(['1'], stream())
        self.assertEqual(self.candidates.read_bytes(), self.changed)

    def test_metadata_filter_preserves_status_and_new_rows(self):
        metadata = self.root / 'metadata.csv'
        self.write(metadata, self.rows)
        self.run_download(['1'], [{'id': '1', 'content_html': '<body>Content</body>'}])
        before = self.read()
        self.write(self.candidates, before[:1], list(before[0]))
        metadata_before = metadata.read_bytes()
        rules.expand_candidates(metadata, self.candidates)
        rows = self.read()
        self.assertEqual(rows[0], before[0])
        self.assertEqual(rows[1]['download_status'], '')
        self.assertEqual(metadata.read_bytes(), metadata_before)
