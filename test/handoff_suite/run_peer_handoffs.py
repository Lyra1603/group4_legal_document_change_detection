"""Reproduce cross-branch evidence without merging or modifying peer sources."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import unittest
from unittest.mock import patch

from backend.app.change_analysis.text_diff import compute_text_diff, validate_text_diff
from backend.app.change_analysis.semantic_diff import detect_semantic_changes
from backend.app.change_analysis.scorer import score_changes
from backend.app.schemas.contracts import AmendmentResult
from backend.app.schemas.report_validation import validate_payload, validate_sources
from .peer_versions import ROOT, peers, revision
from . import test_peer_handoffs as checks


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--tho-ref', default='origin/tho/document_processing')
    cli.add_argument('--context-ref', default='origin/ducanh/context-integration')
    cli.add_argument('--output', type=Path, default=ROOT / 'data/ngocanh-review/output')
    args = cli.parse_args()
    loaded = peers(args.tho_ref, args.context_ref)
    parser, adapter, consumer, _, provenance = loaded
    # Run the tests against exactly the same resolved commits as the evidence.
    log = io.StringIO()
    with patch.object(checks, 'peers', return_value=loaded):
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(checks.PeerHandoffTests)
        tested = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    print(log.getvalue())
    if not tested.wasSuccessful():
        raise SystemExit(1)
    args.output.mkdir(parents=True, exist_ok=True)
    def save(name, value):
        path = args.output / name
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        return sha(path)
    cases = []
    selected = None
    for case in ('case_01', 'case_02', 'case_03'):
        boundary, items, issues = checks.fresh_case(parser, adapter, case)
        usable = []
        for item in items:
            text = compute_text_diff(item)
            validate_text_diff(item, text)
            if text is not None:
                query = json.loads(consumer.build_retrieval_query(item, text))
                usable.append({'amendment_id': item['amendment_id'], 'target_locator': item['target_locator'],
                               'changes': len(text['changes']), 'query_contains_exact_diff': query['text_diff'] == text})
        cases.append({'case': case, 'items': len(items), 'diff_items': usable, 'issues': issues})
        if case == 'case_02':
            item = next(i for i in items if i['before_text'] is not None and i['after_text'] is not None)
            original = deepcopy(item)
            text = compute_text_diff(item)
            semantic = detect_semantic_changes(item, text)
            result = dict(amendment=item, text_diff=text, semantic_diff=semantic, scoring=score_changes(semantic))
            validate_payload(AmendmentResult, result)
            validate_sources(result, boundary.documents)
            assert item == original
            supplied = json.loads((ROOT / 'data/ngocanh-week10/input/ban_giao_ca_dung.json').read_text(encoding='utf-8'))['items'][0]
            old_store = json.loads((ROOT / 'data/ngocanh-week10/input/ban_giao_kho_nguon.json').read_text(encoding='utf-8'))
            selected = {'kind': 'FRESH_DOCX_PEER_PARSER_ADAPTER_LOCAL_LINKER', 'result': result,
                        'query_payload': json.loads(consumer.build_retrieval_query(item, text)),
                        'comparison_with_original_handoff': {
                            'source_store_equal': old_store == boundary.documents,
                            'fields_equal': {k: supplied[k] == item[k] for k in
                                             ('amendment_id', 'target_locator', 'target_unit_ids',
                                              'before_text', 'after_text', 'evidence')},
                            'original_target_unit_ids': supplied['target_unit_ids'],
                            'fresh_target_unit_ids': item['target_unit_ids']}}
    outputs = {'fresh_case_02.json': save('fresh_case_02.json', selected),
               'docx_cases.json': save('docx_cases.json', cases)}
    (args.output / 'tests.txt').write_text(log.getvalue(), encoding='utf-8')
    outputs['tests.txt'] = sha(args.output / 'tests.txt')
    inputs = sorted((ROOT / 'data/ngocanh-week10/input').glob('*.json'))
    from backend.demo import SAMPLES
    for case, sample in SAMPLES.items():
        inputs.extend(ROOT / 'data/raw' / case / sample[r] for r in ('v1', 's'))
    code = ['backend/app/change_analysis/text_diff.py', 'backend/app/change_analysis/semantic_diff.py',
            'backend/app/change_analysis/scorer.py', 'backend/app/document_processing/amendment_linker.py',
            'backend/app/schemas/contracts.py', 'backend/app/schemas/report_validation.py',
            'test/handoff_suite/peer_versions.py', 'test/handoff_suite/test_peer_handoffs.py',
            'test/handoff_suite/run_peer_handoffs.py']
    save('manifest.json', {
        'generated_at': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
        'ngocanh_commit': revision('HEAD'), 'comparison_main_commit': revision('origin/main'),
        'peer_sources': provenance,
        'local_code_sha256': {p: sha(ROOT / p) for p in code},
        'input_sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in inputs},
        'output_sha256': outputs, 'tests': {'run': tested.testsRun, 'failures': 0, 'errors': 0},
        'mode': 'LOCAL_CROSS_BRANCH_WITH_HTTP_CONTRACT_DOUBLE_NO_REAL_LIGHTRAG',
        'confirmations': {'Tho': 'PEER_CODE_RERUN_LOCALLY_HUMAN_REVIEW_PENDING',
                          'Duc_Anh': 'PEER_QUERY_CONSUMER_RERUN_LOCALLY_HUMAN_REVIEW_PENDING',
                          'Dung': 'SHARED_SCORER_RERUN_LOCALLY_HUMAN_REVIEW_PENDING'},
        'limits': ['No human reviewer confirmation inferred from local execution.',
                   'No complete legal context asserted for real cases; semantics remain null/review.',
                   'Synthetic Unicode/negative tests and HTTP contract double are not real legal cases.',
                   'Peer Git blobs are executed as selected; working tree runtime is not merged with PR #6/#7.']})


if __name__ == '__main__':
    main()
