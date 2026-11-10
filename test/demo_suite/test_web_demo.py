"""Real DOCX -> HTTP -> Parser/Linker -> diff -> validated report, no mock model."""
from io import BytesIO
import unittest
from xml.sax.saxutils import escape
import zipfile

from fastapi.testclient import TestClient

from backend.demo import app, ROOT, SAMPLES
from backend.main import app as default_app
from backend.app.schemas.report_validation import validate_report


def docx(*paragraphs):
    output = BytesIO()
    xml = '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
    xml += ''.join(f'<w:p><w:r><w:t>{escape(p)}</w:t></w:r></w:p>' for p in paragraphs)
    xml += '</w:body></w:document>'
    with zipfile.ZipFile(output, 'w') as archive:
        archive.writestr('word/document.xml', xml)
    return output.getvalue()


class WebDemoTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def compare(self, before, amendment, *, references=None):
        files = [('doc_v1',('v1.docx', before)), ('doc_s',('s.docx', amendment))]
        files += [('reference_files',(f'ref_{i}.docx',value)) for i,value in enumerate(references or [])]
        return self.client.post('/api/compare', files=files)

    def test_main_default_not_mutated_by_demo_composition(self):
        self.assertIsNone(default_app.state.analysis_runner)
        with TestClient(default_app) as client:
            self.assertFalse(client.get('/health').json()['comparison_ready'])

    def test_real_raw_cases_and_source_preserving_offsets(self):
        expected = {'case_01':(2,1), 'case_02':(1,1), 'case_03':(13,13)}
        for case, sample in SAMPLES.items():
            with self.subTest(case=case):
                root = ROOT/'data'/'raw'/case
                response = self.compare((root/sample['v1']).read_bytes(), (root/sample['s']).read_bytes())
                self.assertEqual(response.status_code,200,response.text[:500])
                report = response.json()
                validate_report(report)
                self.assertEqual(report['status'],'PARTIAL')
                self.assertFalse(report['errors'])
                self.assertEqual((len(report['results']),sum(r['text_diff'] is not None for r in report['results'])),expected[case])
                for result in report['results']:
                    if result['text_diff'] is None:
                        continue
                    item = result['amendment']
                    reconstructed, cursor = [], 0
                    for change in result['text_diff']['changes']:
                        reconstructed.extend([item['before_text'][cursor:change['old_start']],change['new_text']])
                        cursor = change['old_end']
                    reconstructed.append(item['before_text'][cursor:])
                    self.assertEqual(''.join(reconstructed),item['after_text'])
                    self.assertEqual(result['semantic_diff']['changes'][0]['is_meaningful_change'],None)
                    self.assertTrue(all(score['significance'] is None for score in result['scoring']))

    def test_literal_phrase_derivation_is_not_source_quote(self):
        response = self.compare(docx('Điều 2. Thời hạn','Phải báo cáo trong 30 ngày.'),
                                docx('Điều 1. Sửa đổi','Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 2.'))
        report = response.json(); validate_report(report)
        result = report['results'][0]
        self.assertEqual(result['amendment']['after_basis'],'DERIVED')
        self.assertIn('15 ngày',result['amendment']['after_text'])
        self.assertIsNone(result['semantic_diff']['changes'][0]['new_quote'])

    def test_out_of_scope_but_supported_item_survives(self):
        response = self.compare(docx('Điều 2. Thời hạn','Phải báo cáo trong 30 ngày.'),
            docx('Điều 1. Sửa đổi','Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 2.','Bãi bỏ Điều 2.'))
        report = response.json(); validate_report(report)
        self.assertEqual(len(report['results']),2)
        self.assertIsNotNone(report['results'][0]['text_diff'])
        self.assertIsNone(report['results'][1]['text_diff'])
        self.assertIn('UNSUPPORTED_OPERATION',{w['code'] for w in report['warnings']})
        self.assertEqual(report['results'][1]['amendment']['instruction']['quote'],'Bãi bỏ Điều 2.')

    def test_ambiguous_old_phrase_not_replaced(self):
        response = self.compare(docx('Điều 2. Thời hạn','30 ngày hoặc 30 ngày.'),
            docx('Điều 1. Sửa đổi','Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 2.'))
        report = response.json(); validate_report(report)
        self.assertIsNone(report['results'][0]['amendment']['after_text'])
        self.assertIn('PHRASE_NOT_UNIQUE',{w['code'] for w in report['warnings']})

    def test_missing_and_duplicate_target_are_not_guessed(self):
        for paragraphs in [('Điều 3. Khác','Nội dung.'),('Điều 2. Một','30 ngày.','Điều 2. Hai','30 ngày.')]:
            response = self.compare(docx(*paragraphs),docx('Điều 1. Sửa đổi','Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 2.'))
            report = response.json(); validate_report(report)
            self.assertIsNone(report['results'][0]['text_diff'])
            self.assertIn('TARGET_NOT_UNIQUE',{w['code'] for w in report['warnings']})

    def test_wrong_document_not_linked_by_article_number(self):
        a,b = SAMPLES['case_01'],SAMPLES['case_02']
        response = self.compare((ROOT/'data/raw/case_01'/a['v1']).read_bytes(),(ROOT/'data/raw/case_02'/b['s']).read_bytes())
        report=response.json(); validate_report(report)
        self.assertEqual(report['results'][0]['amendment']['applicability'],'OTHER_DOCUMENT')
        self.assertIsNone(report['results'][0]['text_diff'])

    def test_broken_quote_and_relabel_not_applied(self):
        for new in ['“2. Thiếu dấu đóng','“3. Sai nhãn.”']:
            response=self.compare(docx('Điều 2. Thời hạn','2. Trước.'),
                docx('Điều 1. Sửa đổi','Điều 2 được sửa đổi như sau:',new))
            report=response.json(); validate_report(report)
            self.assertIsNone(report['results'][0]['amendment']['after_text'])

    def test_unrecognized_instructions_not_no_change(self):
        response=self.compare(docx('Điều 1. Nội dung','Một.'),docx('Điều 1. Nội dung','Không có mẫu chỉ dẫn nhận diện được.'))
        report=response.json(); validate_report(report)
        self.assertEqual(report['status'],'PARTIAL')
        self.assertIn('INSTRUCTIONS_NOT_RECOGNIZED',{w['code'] for w in report['warnings']})

    def test_reference_attachment_never_confirms_completeness(self):
        response=self.compare(docx('Điều 2. Nội dung','30 ngày.'),
            docx('Điều 1. Sửa đổi','Thay cụm từ “30 ngày” bằng “15 ngày” tại Điều 2.'),references=[docx('Định nghĩa chưa đối chiếu.')])
        report=response.json(); validate_report(report)
        self.assertEqual(len(report['reference_documents']),1)
        self.assertIn('REFERENCES_NOT_ANALYZED',{w['code'] for w in report['warnings']})

    def test_file_errors_are_distinct_from_domain_warnings(self):
        self.assertEqual(self.client.post('/api/compare').status_code,422)
        response=self.compare(b'not a zip',docx('Điều 1. Mẫu'))
        self.assertEqual(response.status_code,422)
        self.assertEqual(response.json()['detail']['code'],'UNREADABLE_DOCUMENT')
        response=self.client.post('/api/compare',files={'doc_v1':('v1.exe',b'x'),'doc_s':('s.docx',docx('Điều 1. Mẫu'))})
        self.assertEqual(response.status_code,415)
        response=self.compare(b'',docx('Điều 1. Mẫu'))
        self.assertEqual(response.status_code,422)
        self.assertEqual(response.json()['detail']['code'],'EMPTY_FILE')

    def test_static_page_and_sample_download_paths(self):
        self.assertIn('Chọn văn bản gốc',self.client.get('/').text)
        self.assertEqual(self.client.get('/assets/pages/demo.js').status_code,200)
        self.assertEqual(self.client.get('/api/demo/files/case_02/v1').status_code,200)
        self.assertEqual(self.client.get('/api/demo/files/case_02/v2').status_code,404)
        self.assertEqual(self.client.get('/api/demo/files/unknown/s').status_code,404)
        self.assertFalse(self.client.get('/api/demo/config').json()['lightrag_enabled'])


if __name__ == '__main__':
    unittest.main()
