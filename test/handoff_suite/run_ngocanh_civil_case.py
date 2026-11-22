"""Run the provisional case_09 against the existing two-file demo API."""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from fastapi.testclient import TestClient

from backend.app.change_analysis.scorer import score_changes
from backend.app.change_analysis.semantic_diff import detect_semantic_changes
from backend.app.change_analysis.text_diff import compute_text_diff, validate_text_diff
from backend.app.schemas.contracts import AmendmentResult
from backend.app.schemas.report_validation import validate_payload, validate_report, validate_sources
from backend.demo import app


SOURCE_REVISION = '33aeeec1c3681d8247d382689ac3f139d2727824'
SOURCES = {'doc_v1': '29_2023_QH15_v1.pdf', 'doc_s': '43_2024_QH15_amendment.pdf'}


def analyze_verified_excerpts(files):
    # Manual locator selection for this handoff only. Production lookup is exercised separately by the API.
    import pymupdf

    documents = {}
    for document_id, page in [('v1', 67), ('s', 2)]:
        with pymupdf.open(stream=files[f'doc_{document_id}'][1], filetype='pdf') as pdf:
            source = ' '.join(pdf[page - 1].get_text().split())
        documents[document_id] = {'blocks': [{'source_ref': f'page:{page}', 'text': source}]}
    old = documents['v1']['blocks'][0]['text'].split('Điều 82. Hiệu lực thi hành ', 1)[1].split(' 2. ', 1)[0]
    directive = documents['s']['blocks'][0]['text'].split('Điều 3. ', 1)[1].split(' Điều 4. ', 1)[0]
    instruction, quoted = directive.split(' “', 1)
    new = quoted.split('”', 1)[0]
    evidence = [
        {'document_id': 's', 'source_refs': ['page:2'], 'quote': instruction},
        {'document_id': 'v1', 'source_refs': ['page:67'], 'quote': old},
        {'document_id': 's', 'source_refs': ['page:2'], 'quote': new},
    ]
    item = dict(amendment_id='case_09:manual:article82_clause1', operation='AMEND', instruction=evidence[0],
                target_document='v1', target_locator='Điều 82 / khoản 1', target_unit_ids=['v1:82:1'],
                applicability='APPLIES', before_text=old, after_text=new, after_basis='QUOTED', evidence=evidence,
                context={'general_context': '', 'evidence': [], 'references': []}, effect_info=[],
                needs_review=True, review_reason='Chờ đối chiếu ngữ cảnh và quy định chuyển tiếp.')
    missing = deepcopy(item)
    missing.update(before_text=None, target_document='', target_unit_ids=[], applicability='UNRESOLVED',
                   evidence=[evidence[0], evidence[2]], review_reason='Thiếu V1 để xác minh đích và nội dung trước.')
    results = []
    for amendment in (item, missing):
        diff = compute_text_diff(amendment)
        validate_text_diff(amendment, diff)
        semantic = detect_semantic_changes(amendment, diff)
        result = dict(amendment=amendment, text_diff=diff, semantic_diff=semantic, scoring=score_changes(semantic))
        validate_payload(AmendmentResult, result)
        validate_sources(result, documents)
        results.append(result)
    return {'mode': 'MANUAL_LOCATORS_REAL_PDF_MODULE_EXECUTION', 'complete_source_pair': results[0],
            'simulated_missing_v1': results[1]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    files = {field: (filename, subprocess.check_output(
        ['git', 'show', f'{SOURCE_REVISION}:data/raw/case_09/{filename}']))
        for field, filename in SOURCES.items()}
    with TestClient(app) as client:
        response = client.post('/api/compare', files=files)
        missing = client.post('/api/compare', files={'doc_s': files['doc_s']})
    report = response.json()
    if response.is_success:
        validate_report(report)
        for result in report['results']:
            validate_text_diff(result['amendment'], result['text_diff'])
    artifact = {
        'case_id': 'case_09', 'source_revision': SOURCE_REVISION,
        'input_sha256': {name: sha256(content).hexdigest() for name, content in files.values()},
        'http_status': response.status_code, 'report': report,
        's_only_http_status': missing.status_code, 's_only_response': missing.json(),
        'analysis_handoff': analyze_verified_excerpts(files),
    }
    args.output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
