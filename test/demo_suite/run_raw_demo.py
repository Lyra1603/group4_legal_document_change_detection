"""Run actual HTTP uploads against the local demo; never substitutes fixture answers."""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from time import perf_counter

import httpx

from backend.demo import ROOT, SAMPLES
from backend.app.schemas.report_validation import validate_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    parser.add_argument('--output', type=Path, default=Path('data/demo-results'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    runs = []
    with httpx.Client(base_url=args.base_url, timeout=330, trust_env=False) as client:
        config = client.get('/api/demo/config').raise_for_status().json()
        if config.get('mode') != 'LOCAL_RULES_PARTIAL':
            raise ValueError('Expected an explicitly labelled local-rules demo')
        for case, sample in SAMPLES.items():
            with ExitStack() as stack:
                files, inputs = {}, {}
                for role, field in [('v1','doc_v1'),('s','doc_s')]:
                    path = ROOT/'data/raw'/case/sample[role]
                    inputs[role] = {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                    files[field] = (path.name,stack.enter_context(path.open('rb')))
                start = perf_counter()
                response = client.post('/api/compare',files=files)
                response.raise_for_status()
                report = response.json()
                validate_report(report)
                output = args.output/f'{case}.json'
                output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                runs.append({'case':case,'input':inputs,'http_status':response.status_code,
                             'report_status':report['status'],'items':len(report['results']),
                             'text_diff_items':sum(r['text_diff'] is not None for r in report['results']),
                             'elapsed_ms':round((perf_counter()-start)*1000,3),
                             'output':output.as_posix(),'errors':report['errors']})
    manifest = {'generated_at':datetime.now(timezone.utc).isoformat(),
                'mode':'REAL_HTTP_LOCAL_RULES_NO_LIGHTRAG_NO_MODEL','runs':runs,
                'limits':'Source-bound text diff only; no validated semantic/severity conclusions. Input files are repo copies, not verified current legal texts.'}
    (args.output/'run-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{k:r[k] for k in ('case','report_status','items','text_diff_items','elapsed_ms')} for r in runs]))


if __name__ == '__main__':
    main()
