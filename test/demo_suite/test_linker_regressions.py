"""Exercise real HTTP/Parser/Linker paths for the merge-blocking regressions."""
import unittest

from fastapi.testclient import TestClient

from backend.demo import app
from backend.app.schemas.report_validation import validate_report
from test.demo_suite.test_web_demo import docx, base_docx, amendment_docx


class LinkerRegressionTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def compare(self, before, amendment):
        response = self.client.post('/api/compare', files={
            'doc_v1': ('v1.docx', before), 'doc_s': ('s.docx', amendment)})
        self.assertEqual(response.status_code, 200, response.text[:500])
        report = response.json()
        validate_report(report)
        return report

    def assert_blocked(self, report, applicability='UNRESOLVED'):
        self.assertEqual(len(report['results']), 1)
        result = report['results'][0]
        item = result['amendment']
        self.assertEqual(item['applicability'], applicability)
        self.assertIsNone(item['before_text'])
        self.assertIsNone(item['after_text'])
        self.assertIsNone(result['text_diff'])
        self.assertIsNone(result['semantic_diff'])
        self.assertIsNone(result['scoring'])
        self.assertTrue(item['needs_review'])
        self.assertTrue(item['review_reason'])
        self.assertTrue(item['instruction']['quote'])
        return item

    def test_different_name_without_number_never_modifies_selected_v1(self):
        instruction = 'Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 2 của Văn bản B.'
        report = self.compare(docx('Văn bản A','Điều 2. Thời hạn','30 ngày.'),
                              docx('Điều 1. Sửa đổi',instruction))
        item = self.assert_blocked(report)
        self.assertNotEqual(item['target_document'], 'v1')
        self.assertEqual(item['instruction']['quote'], instruction)

    def test_missing_base_number_is_unknown_not_other_document(self):
        report = self.compare(docx('Điều 2. Thời hạn','30 ngày.'),
            docx('Điều 1. Sửa đổi','Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 2 của Thông tư số 34/2017/TT-BTC.'))
        self.assert_blocked(report)

    def test_unqualified_instruction_without_verified_scope_is_unresolved(self):
        report = self.compare(docx('Điều 2. Thời hạn','30 ngày.'),
                              docx('Điều 1. Sửa đổi','Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 2.'))
        self.assert_blocked(report)

    def test_direct_name_overrides_inherited_document_number(self):
        report = self.compare(docx('Số: 34/2017/TT-BTC','Điều 2. Thời hạn','30 ngày.'),
            docx('Điều 1. Sửa đổi một số điều của Thông tư số 34/2017/TT-BTC',
                 'Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 2 của Văn bản B.'))
        self.assert_blocked(report)

    def test_name_prefix_is_not_identity_match(self):
        report = self.compare(docx('Văn bản AB','Điều 2. Thời hạn','30 ngày.'),
            docx('Điều 1. Sửa đổi','Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 2 của Văn bản A.'))
        self.assert_blocked(report)

    def test_exact_name_and_document_number_can_resolve_v1(self):
        for header, target in [('VĂN BẢN MẪU A','Văn bản mẫu A'),('Số: 34/2017/TT-BTC','Thông tư số 34/2017/TT-BTC')]:
            with self.subTest(header=header):
                report = self.compare(docx(header,'Điều 2. Thời hạn','30 ngày.'),
                    docx('Điều 1. Sửa đổi',f'Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 2 của {target}.'))
                result = report['results'][0]
                self.assertEqual(result['amendment']['target_document'],'v1')
                self.assertEqual(result['amendment']['applicability'],'APPLIES')
                self.assertIn('15 ngày',result['amendment']['after_text'])
                self.assertIsNotNone(result['text_diff'])

    def test_different_verified_numbers_are_other_document(self):
        report = self.compare(docx('Số: 34/2017/TT-BTC','Điều 2. Thời hạn','30 ngày.'),
            docx('Điều 1. Sửa đổi','Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 2 của Thông tư số 99/2020/TT-BTC.'))
        self.assert_blocked(report,'OTHER_DOCUMENT')

    def test_number_in_article_body_is_not_document_identity(self):
        report = self.compare(docx('Điều 2. Thời hạn','Số: 34/2017/TT-BTC','30 ngày.'),
            docx('Điều 1. Sửa đổi','Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 2 của Thông tư số 34/2017/TT-BTC.'))
        self.assert_blocked(report)

    def test_unknown_operations_cannot_become_amend_via_quoted_text(self):
        instructions = [f'{action} Điều 2 như sau:' for action in ['Chuyển','Tách','Hợp nhất','Đánh lại số']]
        instructions += [f'Điều 2 được {action} như sau:' for action in ['chuyển','tách','hợp nhất','đánh lại số']]
        for instruction in instructions:
            with self.subTest(instruction=instruction):
                report = self.compare(base_docx('Điều 2. Nội dung','Nội dung cũ.'),
                    amendment_docx(instruction,'“Điều 2. Nội dung mới.”'))
                item = self.assert_blocked(report,'APPLIES')
                self.assertEqual(item['operation'],'UNRESOLVED')
                self.assertEqual(item['instruction']['quote'],instruction)
                self.assertIn('UNSUPPORTED_OPERATION',{w['code'] for w in report['warnings']})

    def test_unsupported_item_does_not_drop_a_supported_sibling(self):
        report = self.compare(base_docx('Điều 2. Nội dung','30 ngày.'),
            amendment_docx('Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 2.',
                           'Chuyển Điều 2 như sau:','“Điều 2. Nội dung mới.”'))
        self.assertEqual(len(report['results']),2)
        self.assertIsNotNone(report['results'][0]['text_diff'])
        self.assertIsNone(report['results'][1]['text_diff'])
        self.assertEqual(report['results'][1]['amendment']['operation'],'UNRESOLVED')


if __name__ == '__main__':
    unittest.main()
