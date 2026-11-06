from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import time
import unittest

from backend.app.schemas.report_validation import validate_report
from backend.app.storage import workspace, sweep


class StorageTests(unittest.TestCase):
    def test_live_workspace_is_not_swept_and_finally_cleans_it(self):
        with TemporaryDirectory() as root:
            with workspace(root) as directory:
                (directory / 'input.docx').write_bytes(b'data')
                old = time.time() - 172800
                os.utime(directory / '.lease', (old, old))
                sweep(root)
                self.assertTrue(directory.exists())
            self.assertFalse(directory.exists())

    def test_stale_owned_directory_is_swept_unrelated_directory_is_kept(self):
        with TemporaryDirectory() as root:
            stale = Path(root) / ('comparison-' + 'a' * 32)
            stale.mkdir()
            (stale / '.lease').write_bytes(b'1')
            old = time.time() - 172800
            os.utime(stale / '.lease', (old, old))
            unrelated = Path(root) / 'user-documents'
            unrelated.mkdir()
            sweep(root)
            self.assertFalse(stale.exists())
            self.assertTrue(unrelated.exists())


class ContractTests(unittest.TestCase):
    def test_status_enum_and_metadata_are_checked(self):
        report = dict(comparison_id='test', base_document=dict(document_id='v1', role='BASE', filename='base.docx'),
                      amendment_document=dict(document_id='s', role='AMENDMENT', filename='s.docx'),
                      reference_documents=[], status='FAILED', results=[], warnings=[], errors=[])
        validate_report(report)
        for field, value in [('status', 'success'), ('base_document', dict(document_id='v1', role='BASE', filename='C:/private/base.docx'))]:
            bad = deepcopy(report)
            bad[field] = value
            with self.assertRaises(ValueError):
                validate_report(bad)


if __name__ == '__main__':
    unittest.main()
