"""Check the unchanged main Pipeline, using stdlib DOCX and test-only adapters."""
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.sax.saxutils import escape
import unittest
import zipfile

from backend.app.pipeline import AnalysisOutcome, DocumentInput, run_comparison
from backend.app.schemas.report_validation import validate_report
from test_contracts import load_case, validate_case


def write_docx(path, paragraphs):
    content = ''.join('<w:p><w:r><w:t>' + escape(p) + '</w:t></w:r></w:p>'
                      for p in paragraphs)
    xml = ('<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           '<w:body>' + content + '</w:body></w:document>')
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('word/document.xml', xml)


def boundary_data(parsed):
    """Example only. The production document_adapter.py remains unchanged."""
    documents, clauses = {}, {}
    for parsed_document in parsed:
        identity = parsed_document.document.identity()
        key = identity['document_id']
        documents[key] = dict(**identity, file_type='DOCX', blocks=[
            dict(source_ref=b['source_ref'], text=b['text'])
            for b in parsed_document.tree['source_blocks']
        ])
        clauses[key] = [dict(unit_id=a['node_id'], id='Điều ' + a['label'],
                             title=a['heading'], content=a['full_text'],
                             source_refs=a['source_refs'])
                        for a in parsed_document.tree['articles']]
    return documents, clauses


class MainCompatibilityTests(unittest.TestCase):
    def inputs(self, directory):
        case = load_case()
        paths = []
        for key in ['v1', 's', 'ref_1']:
            doc = case['documents'][key]
            path = Path(directory) / doc['filename']
            # References need not contain articles; V1/S do.
            texts = [b['text'] for b in doc['blocks']]
            if key != 'ref_1':
                texts[0] = 'Điều 1. ' + texts[0]
            write_docx(path, texts)
            paths.append(DocumentInput(key, doc['role'], doc['filename'], path))
        return paths

    def test_main_default_failed_envelope_is_schema_compatible(self):
        with TemporaryDirectory() as directory:
            report = run_comparison(self.inputs(directory), 'main-no-runner')
        validate_report(report)
        self.assertEqual(report['status'], 'FAILED')
        self.assertEqual(report['results'], [])
        self.assertIn('ANALYSIS_NOT_CONFIGURED', {e['code'] for e in report['errors']})

    def test_validating_runner_can_bridge_native_blocks_without_renaming(self):
        def runner(parsed, comparison_id, deadline):
            case = load_case()
            documents, clauses = boundary_data(parsed)
            case['documents'], case['clauses'] = documents, clauses
            case['report']['results'][0]['amendment']['target_unit_ids'] = [clauses['v1'][0]['unit_id']]
            # Native parser uses the same block:N refs; quote remains verbatim.
            self.assertEqual(documents['v1']['blocks'][0]['source_ref'], 'block:1')
            self.assertTrue(clauses['v1'][0]['unit_id'].startswith('v1:'))
            case['report']['comparison_id'] = comparison_id
            validate_case(case)
            return AnalysisOutcome('SUCCESS', case['report']['results'])
        with TemporaryDirectory() as directory:
            report = run_comparison(self.inputs(directory), 'runner-fixture', analysis_runner=runner)
        validate_report(report)
        self.assertEqual(report['status'], 'SUCCESS')
        self.assertEqual(report['results'][0]['amendment']['amendment_id'], 's:a1')

    def test_runner_boundary_rejects_invalid_source_and_pipeline_returns_failed(self):
        def runner(parsed, comparison_id, deadline):
            case = load_case()
            case['documents'], case['clauses'] = boundary_data(parsed)
            case['report']['results'][0]['amendment']['instruction']['source_refs'] = ['block:999']
            validate_case(case)
            self.fail('Invalid source should fail at the runner boundary')
        with TemporaryDirectory() as directory:
            report = run_comparison(self.inputs(directory), 'runner-bad-source', analysis_runner=runner)
        validate_report(report)
        self.assertEqual(report['status'], 'FAILED')
        self.assertIn('PROCESSING_FAILED', {e['code'] for e in report['errors']})


if __name__ == '__main__':
    unittest.main()
