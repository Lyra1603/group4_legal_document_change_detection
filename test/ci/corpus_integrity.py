"""Check the generated corpus against the checked-in DOCX and catalogue."""
import argparse
from collections import defaultdict
import csv
from hashlib import sha256
import io
import json
from pathlib import Path
import subprocess

from backend.app.context.corpus_document_graph import RELATIONS
from backend.app.context.document_graph import CATALOG_PATH, CORPUS_DIR
from backend.app.document_processing.parser.legal_structure_parser import parse_docx


def read_rows(text):
    return list(csv.DictReader(io.StringIO(text)))


def check_baseline(base, current):
    old_text = subprocess.check_output(
        ['git', 'show', f'{base}:{CATALOG_PATH}']).decode('utf-8-sig')
    previous = read_rows(old_text)
    old_success = {row['id'] for row in previous if row['download_status'] == 'success'}
    dropped = sorted(old_success - current.keys())
    deleted = subprocess.check_output(
        ['git', 'diff', '--no-renames', '--name-only', '--diff-filter=D', '-z',
         base, 'HEAD', '--', CORPUS_DIR]).decode('utf-8').split('\0')
    docx_deleted = [path for path in deleted if path.lower().endswith('.docx')]
    for path in docx_deleted:
        print(f'WARNING: Removed DOCX relative to {base}: {path}', flush=True)
    if dropped:
        raise ValueError(f'{len(dropped)} previously successful records no longer successful: {dropped}')
    return len(docx_deleted)


def validate(root, output, base=None):
    catalog = root / CATALOG_PATH
    rows = read_rows(catalog.read_text(encoding='utf-8-sig'))
    successful = [row for row in rows if row['download_status'] == 'success']
    by_id = {row['id']: row for row in successful}
    if len(by_id) != len(successful) or '' in by_id:
        raise ValueError('Successful records must have distinct, nonempty IDs')
    corpus = (root / CORPUS_DIR).resolve()
    paths = {}
    seen_paths = set()
    for key, row in by_id.items():
        path = (root / row['download_path']).resolve()
        if not path.is_relative_to(corpus) or path.suffix.lower() != '.docx' or not path.is_file():
            raise ValueError(f'Successful row {key} has no DOCX in the corpus: {row["download_path"]}')
        if path in seen_paths:
            raise ValueError(f'Several successful rows refer to the same DOCX: {path}')
        paths[key] = path
        seen_paths.add(path)
    deleted_count = check_baseline(base, by_id) if base else 0

    graph = json.loads((output / 'document-graph.json').read_text(encoding='utf-8'))
    report = json.loads((output / 'build-report.json').read_text(encoding='utf-8'))
    files = {item['dataset_id']: item for item in report['files']}
    if set(files) != set(by_id) or any(item['status'] != 'READ' for item in files.values()):
        raise ValueError('The graph build must read every successful DOCX')
    nodes = {node['id']: node for node in graph['nodes']}
    if len(nodes) != len(graph['nodes']) or {item['document_id'] for item in files.values()} - nodes.keys():
        raise ValueError('Missing or duplicated document nodes')
    for key, item in files.items():
        if (root / item['path']).resolve() != paths[key]:
            raise ValueError(f'Graph source path differs from the catalogue for {key}')
        if sha256(paths[key].read_bytes()).hexdigest() != item['sha256']:
            raise ValueError(f'DOCX digest differs from the build report for {key}')

    grouped = defaultdict(list)
    edge_ids = set()
    for edge in graph['edges']:
        source = edge['source_id']
        if (edge['id'] in edge_ids or source not in nodes or edge['target_id'] not in nodes
                or edge['relation'] not in RELATIONS or not edge['evidence']):
            raise ValueError(f'Invalid edge {edge["id"]}')
        edge_ids.add(edge['id'])
        grouped[source].extend(edge['evidence'])
    for source, entries in grouped.items():
        node = nodes[source]
        item = files[node['dataset_id']]
        blocks = {block['source_ref']: block['text']
                  for block in parse_docx(root / item['path'], document_id=source)['source_blocks']}
        for evidence in entries:
            refs = evidence['source_refs']
            if (evidence['document_id'] != source or not refs or any(ref not in blocks for ref in refs)
                    or evidence['quote'] != '\n'.join(blocks[ref] for ref in refs)):
                raise ValueError(f'Incorrect source evidence in {source} at {refs}')
    return dict(docx_read=len(files), nodes=len(nodes), edges=len(edge_ids),
                quotes=sum(map(len, grouped.values())), removed_docx=deleted_count,
                file_issues=report['summary']['file_issues_by_reason'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--graph-dir', type=Path, required=True)
    parser.add_argument('--base')
    args = parser.parse_args()
    result = validate(Path.cwd(), args.graph_dir, args.base)
    summary = json.dumps(result, ensure_ascii=False)
    (args.graph_dir / 'integrity-summary.json').write_text(summary + '\n', encoding='utf-8')
    print(summary)


if __name__ == '__main__':
    main()
