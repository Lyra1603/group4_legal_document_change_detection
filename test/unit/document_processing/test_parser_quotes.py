import unittest
from backend.app.document_processing.parser import legal_structure_parser as p


def _blocks(texts):
    return [{"source_ref": f"block:{i+1}", "kind": "PARAGRAPH", "text": t} for i, t in enumerate(texts)]


class QuoteTests(unittest.TestCase):
    def test_article_inside_closed_quote_is_not_outside(self):
        texts = [
            "Điều 1. Sửa đổi",
            "Khoản 1 được sửa như sau:",
            "“Điều 23. Hiệu lực",
            "1. Nội dung",
            "Điều 24. Trong trích dẫn”",
            "Điều 2. Hiệu lực",
            "1. Nội dung ngoài",
        ]
        root, _ = p._Parser(_blocks(texts), "s").parse(p._lines(_blocks(texts)))
        labels = [n["label"] for n in root["children"] if n["kind"] == "ARTICLE"]
        self.assertIn("2", labels)
        self.assertNotIn("24", labels)

    def test_unclosed_quote_warns(self):
        texts = ["Điều 1. A", "“Nội dung không đóng", "Điều 2. B"]
        parser = p._Parser(_blocks(texts), "s")
        parser.parse(p._lines(_blocks(texts)))
        self.assertIn("UNCLOSED_QUOTATION", [w["code"] for w in parser.warnings])


if __name__ == "__main__":
    unittest.main()