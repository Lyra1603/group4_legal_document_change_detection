"""Tests for both supported document_adapter input formats."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from backend.app.pipeline import DocumentInput, ParsedDocument
from backend.app.document_processing.document_adapter import adapt_documents


DOCUMENTS = [
    ("v1", "BASE", "van_ban_goc.docx", "Văn bản gốc V1"),
    ("s", "AMENDMENT", "van_ban_sua_doi.docx", "Văn bản sửa đổi S"),
    ("ref_1", "REFERENCE", "tai_lieu_tham_chieu_1.docx", "Tài liệu tham chiếu 1"),
    ("ref_2", "REFERENCE", "tai_lieu_tham_chieu_2.docx", "Tài liệu tham chiếu 2"),
]


def make_article(document_id, text):
    """Small parser-tree node matching the shape consumed by the Adapter."""
    return {
        "kind": "ARTICLE",
        "node_id": f"{document_id}:article_1",
        "label": "1",
        "heading": "Quy định chung",
        "full_text": text,
        "source_refs": [f"{document_id}:block:0"],
        "children": [],
    }


def make_dict_documents():
    parsed = []
    for document_id, role, filename, text in DOCUMENTS:
        parsed.append({
            "document_id": document_id,
            "role": role,
            "filename": filename,
            "source_blocks": [{
                "source_ref": f"{document_id}:block:0",
                "text": text,
            }],
            "articles": [make_article(document_id, text)],
        })
    return parsed


def make_object_documents():
    parsed = []
    with TemporaryDirectory() as temporary:
        # DocumentInput.path is not read by the Adapter; it is part of the
        # real ParsedDocument/DocumentInput contract, so use a valid Path.
        for document_id, role, filename, text in DOCUMENTS:
            document = DocumentInput(
                document_id=document_id,
                role=role,
                filename=filename,
                path=Path(temporary) / filename,
            )
            tree = {
                "source_blocks": [{
                    "source_ref": f"{document_id}:block:0",
                    "text": text,
                }],
                "articles": [make_article(document_id, text)],
            }
            parsed.append(ParsedDocument(
                document=document,
                tree=tree,
                source_format="DOCX",
            ))
        # The objects contain all needed data in memory. Returning them after
        # the temporary directory closes is safe because Adapter does not
        # access the paths.
        return parsed


class TestAdapterReviewContract(unittest.TestCase):
    def assert_boundary_preserves_all_documents(self, boundary):
        expected_ids = [item[0] for item in DOCUMENTS]
        self.assertEqual(list(boundary.documents.keys()), expected_ids)
        self.assertEqual(list(boundary.clauses.keys()), expected_ids)
        self.assertEqual(list(boundary.units.keys()), expected_ids)

        for document_id, role, filename, text in DOCUMENTS:
            with self.subTest(document_id=document_id):
                extracted = boundary.documents[document_id]
                self.assertEqual(extracted["document_id"], document_id)
                self.assertEqual(extracted["role"], role)
                self.assertEqual(extracted["filename"], filename)
                self.assertEqual(extracted["file_type"], "DOCX")
                self.assertEqual(extracted["blocks"], [{
                    "source_ref": f"{document_id}:block:0",
                    "text": text,
                }])

                self.assertEqual(len(boundary.clauses[document_id]), 1)
                clause = boundary.clauses[document_id][0]
                self.assertEqual(clause["unit_id"], f"{document_id}:article_1")
                self.assertEqual(clause["content"], text)
                self.assertEqual(
                    clause["source_refs"], [f"{document_id}:block:0"]
                )

    def test_adapts_parsed_document_objects_for_v1_s_and_references(self):
        result = adapt_documents(make_object_documents())
        self.assert_boundary_preserves_all_documents(result)

    def test_adapts_parse_docx_dicts_for_v1_s_and_references(self):
        result = adapt_documents(make_dict_documents())
        self.assert_boundary_preserves_all_documents(result)


if __name__ == "__main__":
    unittest.main()
