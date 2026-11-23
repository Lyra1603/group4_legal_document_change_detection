import unittest
from backend.app.document_processing.parser import legal_structure_parser as p


def _blocks(texts):
    return [
        {
            "source_ref": f"block:{i+1}",
            "kind": "PARAGRAPH",
            "text": t,
        }
        for i, t in enumerate(texts)
    ]


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
        blocks = _blocks(texts)
        root, _ = p._Parser(blocks, "s").parse(p._lines(blocks))
        labels = [n["label"] for n in root["children"] if n["kind"] == "ARTICLE"]
        self.assertIn("2", labels)
        self.assertNotIn("24", labels)

    def test_noi_nhan_inside_quote_does_not_cut_body(self):
        blocks = _blocks([
            "Điều 1. Sửa đổi",
            "“Trích dẫn có nội dung Nơi nhận: cơ quan A”",
            "Điều 2. Hiệu lực",
            "1. Nội dung Điều 2",
        ])
        body, tail = p._cut_at_annex(blocks)
        body_text = "\n".join(b["text"] for b in body)
        self.assertIn("Điều 2. Hiệu lực", body_text)
        self.assertEqual(tail, [])

    def test_noi_nhan_in_multiline_quote_does_not_cut_body(self):
        blocks = _blocks([
            "Điều 1. Sửa đổi",
            "“Trích dẫn mở",
            "Nơi nhận: cơ quan A",
            "Trích dẫn đóng”",
            "Điều 2. Hiệu lực",
        ])
        body, tail = p._cut_at_annex(blocks)
        self.assertEqual(len(body), 5)
        self.assertEqual(tail, [])

    def test_real_noi_nhan_cuts_body(self):
        blocks = _blocks([
            "Điều 1. Nội dung",
            "1. Khoản cuối",
            "Nơi nhận:",
            "Cơ quan A",
        ])
        body, tail = p._cut_at_annex(blocks)
        self.assertEqual(len(body), 2)
        self.assertEqual(tail[0]["text"], "Nơi nhận:")
        self.assertEqual(tail[1]["text"], "Cơ quan A")

    def test_real_annex_cuts_body(self):
        blocks = _blocks([
            "Điều 1. Nội dung",
            "1. Khoản cuối",
            "PHỤ LỤC",
            "Bảng biểu",
        ])
        body, tail = p._cut_at_annex(blocks)
        self.assertEqual(len(body), 2)
        self.assertEqual(tail[0]["text"], "PHỤ LỤC")

    def test_signature_is_outside_article_content(self):
        blocks = _blocks([
            "Điều 1. Nội dung",
            "1. Khoản cuối của Điều 1",
            "KT. BỘ TRƯỞNG",
            "PHÓ THỐNG ĐỐC",
            "Nguyễn Văn A",
        ])
        parser = p._Parser(blocks, "test")
        root, outside = parser.parse(p._lines(blocks))
        parser.finish(root)
        article = next(n for n in root["children"] if n["kind"] == "ARTICLE")

        self.assertNotIn("KT. BỘ TRƯỞNG", article["full_text"])
        self.assertNotIn("PHÓ THỐNG ĐỐC", article["full_text"])
        self.assertNotIn("Nguyễn Văn A", article["full_text"])

        self.assertEqual(
            [x["text"] for x in outside],
            ["KT. BỘ TRƯỞNG", "PHÓ THỐNG ĐỐC", "Nguyễn Văn A"],
        )
        self.assertTrue(all(x["region"] == "AFTER_BODY" for x in outside))

    def test_signature_inside_quote_is_not_cut_out(self):
        blocks = _blocks([
            "Điều 1. Nội dung",
            "“KT. BỘ TRƯỞNG là cụm từ trong trích dẫn”",
            "1. Khoản tiếp theo",
        ])
        parser = p._Parser(blocks, "test")
        root, outside = parser.parse(p._lines(blocks))
        parser.finish(root)
        article = next(n for n in root["children"] if n["kind"] == "ARTICLE")
        self.assertIn("KT. BỘ TRƯỞNG", article["full_text"])
        self.assertEqual(outside, [])

    def test_unclosed_quote_warns(self):
        texts = ["Điều 1. A", "“Nội dung không đóng", "Điều 2. B"]
        parser = p._Parser(_blocks(texts), "s")
        parser.parse(p._lines(_blocks(texts)))
        self.assertIn("UNCLOSED_QUOTATION", [w["code"] for w in parser.warnings])


if __name__ == "__main__":
    unittest.main()
