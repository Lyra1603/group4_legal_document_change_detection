"""Reproduce supplied real handoffs and DOCX API outputs without model/RAG."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import monotonic

from fastapi.testclient import TestClient

from backend.demo import app, SAMPLES
from backend.app.pipeline import DocumentInput, parse_documents
from backend.app.document_processing.document_adapter import adapt_documents
from backend.app.change_analysis.text_diff import compute_text_diff, validate_text_diff
from backend.app.change_analysis.semantic_diff import detect_semantic_changes
from backend.app.change_analysis.scorer import score_changes
from backend.app.schemas.contracts import AmendmentItem, SemanticDiffResult
from backend.app.schemas.report_validation import validate_payload, validate_sources, validate_amendment, validate_report

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / 'data/ngocanh-week10/input'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyze(item, documents):
    validate_payload(AmendmentItem, item)
    validate_sources(item, documents)
    text = compute_text_diff(item)
    validate_text_diff(item, text)
    semantic = detect_semantic_changes(item, text)  # never force real context complete
    validate_payload(SemanticDiffResult, semantic)
    result = dict(amendment=deepcopy(item), text_diff=text,
                  semantic_diff=semantic, scoring=score_changes(semantic))
    validate_sources(result, documents)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'data/ngocanh-week10/output')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    documents = json.loads((INPUT / 'ban_giao_kho_nguon.json').read_text(encoding='utf-8'))
    supplied = json.loads((INPUT / 'ban_giao_ca_dung.json').read_text(encoding='utf-8'))
    source_paths = [ROOT / 'data/raw/case_02' / SAMPLES['case_02'][r] for r in ('v1', 's')]
    with TemporaryDirectory() as temporary:
        parsed = parse_documents([DocumentInput(did, role, path.name, path)
                                  for did, role, path in zip(('v1', 's'), ('BASE', 'AMENDMENT'), source_paths)],
                                 Path(temporary), monotonic() + 120)
        boundary = adapt_documents(parsed)
        for did in ('v1', 's'):
            if documents[did] != boundary.documents[did]:
                raise ValueError('Supplied source store differs from repo DOCX: ' + did)
        for item in supplied['items']:
            validate_amendment(item, documents, boundary.clauses)
    results = [analyze(item, documents) for item in supplied['items']]
    def save(name, value):
        (args.output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    save('tho_to_ngocanh_analysis.json', results)
    save('ngocanh_to_ducanh_text_diff.json', [r['text_diff'] for r in results])
    save('ngocanh_to_dung_semantic.json', [r['semantic_diff'] for r in results])
    save('dung_scorer_actual.json', [r['scoring'] for r in results])
    # Negative inputs are derived tests, never presented as additional real cases.
    negatives = []
    for scenario in ('missing_before', 'unresolved_target', 'missing_context'):
        item = deepcopy(supplied['items'][0])
        if scenario == 'missing_before':
            item['before_text'] = None
        elif scenario == 'unresolved_target':
            item.update(applicability='UNRESOLVED', target_unit_ids=[])
        result = analyze(item, documents)
        if not result['semantic_diff']['needs_review']:
            raise AssertionError('Negative input lost review')
        negatives.append(dict(kind='DERIVED_NEGATIVE_TEST_NOT_REAL_HANDOFF', scenario=scenario, result=result))
    save('negative_cases.json', negatives)
    runs = []
    with TestClient(app) as client:
        for case, sample in SAMPLES.items():
            paths = [ROOT / 'data/raw' / case / sample[r] for r in ('v1', 's')]
            with paths[0].open('rb') as old, paths[1].open('rb') as new:
                response = client.post('/api/compare', files={
                    'doc_v1': (paths[0].name, old), 'doc_s': (paths[1].name, new)})
            if response.status_code != 200:
                raise AssertionError(f'{case}: HTTP {response.status_code}')
            report = response.json()
            validate_report(report)
            for result in report['results']:
                if result['text_diff'] is not None:
                    validate_text_diff(result['amendment'], result['text_diff'])
            save(case + '_api_report.json', report)
            runs.append(dict(case=case, http_status=response.status_code, status=report['status'],
                             items=len(report['results']),
                             text_diff_items=sum(r['text_diff'] is not None for r in report['results'])))
    code = ['backend/app/change_analysis/text_diff.py', 'backend/app/change_analysis/semantic_diff.py',
            'backend/app/change_analysis/scorer.py', 'test/handoff_suite/run_ngocanh_week10.py',
            'test/handoff_suite/test_ngocanh_week10.py']
    save('manifest.json', dict(
        generated_at=datetime.now(timezone.utc).isoformat(),
        base_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        code_sha256={p: digest(ROOT / p) for p in code},
        input_sha256={str(p.relative_to(ROOT)).replace('\\', '/'): digest(p)
                      for p in [*INPUT.glob('*.json'), *source_paths]},
        mode='REAL_SUPPLIED_JSON_AND_DOCX_TESTCLIENT_NO_MODEL_NO_LIGHTRAG',
        source_store_matches_repo_docx=True, runs=runs,
        confirmations={'Tho': 'PENDING_HUMAN_REVIEW', 'Duc_Anh': 'PENDING_QUERY_CONSUMER_RERUN',
                       'Dung': 'SCORER_EXECUTED_LOCALLY_HUMAN_REVIEW_PENDING'},
        limits='No independent legal labels, no semantic accuracy benchmark, no live browser or real retrieval verification.'))
    print(json.dumps(runs, ensure_ascii=False))


if __name__ == '__main__':
    main()
