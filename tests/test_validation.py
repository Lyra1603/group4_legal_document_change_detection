import json
import unittest
from pathlib import Path

from backend.app.schemas.validation import validate_extracted_document


FIXTURE_PATH = (
    Path(__file__).parent / "fixtures" / "reader_parser_case.json"
)


class TestExtractedDocumentValidation(unittest.TestCase):
    def setUp(self):
        fixture = json.loads(
            FIXTURE_PATH.read_text(encoding="utf-8")
        )
        self.document = fixture["extracted_document"]

    def test_accepts_valid_document(self):
        validate_extracted_document(self.document)

    def test_rejects_duplicate_source_ref(self):
        blocks = self.document["blocks"]
        blocks[1]["source_ref"] = blocks[0]["source_ref"]

        with self.assertRaisesRegex(ValueError, "bị trùng"):
            validate_extracted_document(self.document)

    def test_rejects_missing_document_id(self):
        del self.document["document_id"]

        with self.assertRaisesRegex(ValueError, "Thiếu trường"):
            validate_extracted_document(self.document)

    def test_rejects_document_without_text(self):
        for block in self.document["blocks"]:
            block["text"] = "   "

        with self.assertRaisesRegex(ValueError, "không có nội dung"):
            validate_extracted_document(self.document)