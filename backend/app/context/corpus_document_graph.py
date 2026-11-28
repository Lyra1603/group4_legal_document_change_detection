"""Generate a versioned graph of direct references from the local DOCX corpus."""
from collections import Counter, defaultdict
import csv
from hashlib import sha256
from pathlib import Path
from time import monotonic
from xml.etree.ElementTree import ParseError
from zipfile import BadZipFile

from .document_graph import (
    CATALOG_PATH, CORPUS_DIR, DATASET, REVISION, _metadata_node, _number, _relations,
)
from ..document_processing.parser.legal_structure_parser import parse_docx

GRAPH_FILENAME = 'document-graph.json'
RUN_DIRECTORY = 'runtime/lightrag/document-relation-graph'
RELATIONS = ('AMENDS', 'SUPPLEMENTS', 'REPEALS', 'CITES', 'BASIS')


def _path_key(path):
    # Compare catalogue and filesystem spelling, including on Windows.
    return Path(path).as_posix().casefold()


def build_corpus_graph(root):
    started = monotonic()
    root = root.resolve()
    catalog = root / CATALOG_PATH
    snapshot = catalog.read_bytes()
    with catalog.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    corpus = (root / CORPUS_DIR).resolve()
    docs = {}
    for path in sorted(corpus.rglob('*')):
        if path.suffix.lower() == '.docx' and path.is_file() and path.resolve().is_relative_to(corpus):
            docs.setdefault(_path_key(path.relative_to(root)), []).append(path)

    by_id = defaultdict(list)
    by_number = defaultdict(list)
    successes = defaultdict(list)
    file_issues = []
    for row in rows:
        by_id[row['id']].append(row)
        if number := _number(row['so_ky_hieu']):
            by_number[number].append(row)
        if row['download_status'] == 'success':
            key = _path_key(row['download_path'])
            successes[key].append(row)
            if key not in docs:
                file_issues.append(dict(reason='SUCCESS_WITHOUT_LOCAL_DOCX',
                                        dataset_id=row['id'], path=row['download_path']))

    duplicate_ids = {key for key, items in by_id.items() if not key or len(items) > 1}
    for key in sorted(duplicate_ids):
        file_issues.append(dict(reason='MISSING_OR_DUPLICATE_DATASET_ID', dataset_id=key,
                                records=len(by_id[key])))
    nodes, files, blocks_by_node, row_nodes = {}, [], {}, {}
    hashes = defaultdict(list)
    input_count = 0
    warning_counts = Counter()
    for key, paths in docs.items():
        candidates = successes.get(key, [])
        if len(paths) != 1 or len(candidates) != 1:
            file_issues.append(dict(reason='NO_SUCCESS_RECORD' if len(paths) == 1 and not candidates
                                    else 'AMBIGUOUS_FILE_MAPPING',
                                    paths=[p.relative_to(root).as_posix() for p in paths],
                                    candidate_dataset_ids=[r['id'] for r in candidates]))
            continue
        input_count += 1
        path, row = paths[0], candidates[0]
        relative = path.relative_to(root).as_posix()
        if row['id'] in duplicate_ids:
            file_issues.append(dict(reason='DOCX_ID_UNRESOLVED', path=relative, dataset_id=row['id']))
            continue
        node = _metadata_node(row)
        node['number_raw'] = row['so_ky_hieu'] or None
        node['source']['path'] = relative
        file = dict(document_id=node['id'], dataset_id=row['id'], path=relative)
        files.append(file)
        digest = None
        try:
            digest = sha256(path.read_bytes()).hexdigest()
            parsed = parse_docx(path, document_id=node['id'])
            blocks = parsed['source_blocks']
            if not any(block['text'].strip() for block in blocks):
                raise ValueError('No readable source blocks')
        except (OSError, BadZipFile, ParseError, KeyError, ValueError) as exc:
            node['full_text_status'] = 'READ_ERROR'
            node['version']['snapshot_sha256'] = digest
            file.update(status='READ_ERROR', sha256=digest)
            file_issues.append(dict(reason='DOCX_READ_ERROR', dataset_id=row['id'], path=relative,
                                    error=type(exc).__name__))
            nodes[node['id']] = node
            row_nodes[row['id']] = node['id']
            continue

        node['version']['snapshot_sha256'] = digest
        node['full_text_status'] = 'AVAILABLE'
        warning_counts.update(w['code'] for w in parsed['warnings'])
        file.update(status='READ', sha256=digest, parsed_blocks=len(blocks),
                    parser_status=parsed['status'],
                    parser_warnings=[dict(code=w['code'], source_refs=w.get('source_refs', []))
                                     for w in parsed['warnings']])
        if node['number'] is None:
            file_issues.append(dict(reason='UNNORMALIZED_DOCUMENT_NUMBER', dataset_id=row['id'],
                                    number_raw=node['number_raw'], path=relative))
        # Merge only same bytes + same known number. A different reported issue date
        # may denote a distinct record/version and stays unresolved.
        same_number = [n for n in hashes[digest] if nodes[n]['number'] == node['number']
                       and node['number'] is not None
                       and nodes[n]['version']['issued_date_reported'] ==
                       node['version']['issued_date_reported']]
        if same_number:
            canonical = same_number[0]
            nodes[canonical].setdefault('aliases', []).append(
                dict(dataset_id=row['id'], source=node['source'], title=node['title']))
            row_nodes[row['id']] = canonical
            file['document_id'] = canonical
            file_issues.append(dict(reason='DUPLICATE_SNAPSHOT', dataset_id=row['id'],
                                    path=relative, canonical_id=canonical, sha256=digest))
            continue
        if hashes[digest]:
            file_issues.append(dict(reason='SAME_BYTES_DIFFERENT_OR_UNKNOWN_IDENTITY',
                                    document_ids=[*hashes[digest], node['id']], sha256=digest))
        hashes[digest].append(node['id'])
        nodes[node['id']] = node
        row_nodes[row['id']] = node['id']
        blocks_by_node[node['id']] = blocks

    number_nodes = {number: {row_nodes.get(row['id'], f'dataset:{row["id"]}') for row in group}
                    for number, group in by_number.items()}
    ambiguous_numbers = dict(
        (number, dict(candidate_dataset_ids=sorted({row['id'] for row in by_number[number]}),
                      candidate_node_ids=sorted(candidates)))
        for number, candidates in number_nodes.items()
        if len(candidates) > 1 or any(row['id'] in duplicate_ids for row in by_number[number])
    )
    edges, review = [], []
    for source_id, blocks in blocks_by_node.items():
        for record in _relations(source_id, nodes[source_id]['number'], blocks, track_inline_quotes=True):
            if 'reason' in record:
                review.append(dict(source_id=source_id, **record))
                continue
            number = record.pop('target_number')
            matches = by_number.get(number, [])
            candidates = number_nodes.get(number, ())
            reference = dict(source_id=source_id, mentioned_numbers=[number],
                             candidate_dataset_ids=sorted({r['id'] for r in matches}), **record)
            if number in ambiguous_numbers:
                review.append(dict(reason='AMBIGUOUS_DOCUMENT_NUMBER', **reference))
                continue
            target_id = next(iter(candidates), f'number:{number}')
            if target_id == source_id:
                continue
            if target_id not in nodes:
                target = (_metadata_node(matches[0]) if matches else
                          dict(id=target_id, number=number, title=None, dataset_id=None,
                               source=None, version=None))
                target['full_text_status'] = 'MISSING_FULL_TEXT'
                nodes[target_id] = target
            resolution = ('MATCHED_CATALOG_NUMBER' if matches else 'OUTSIDE_CATALOG')
            if nodes[target_id]['full_text_status'] != 'AVAILABLE':
                review.append(dict(reason='TARGET_WITHOUT_READABLE_DOCX' if matches else
                                   'TARGET_OUTSIDE_CATALOG', target_id=target_id, **reference))
            edges.append(dict(id=f'edge:{len(edges)+1}', source_id=source_id, target_id=target_id,
                              target_resolution=resolution, legal_version_verified=False, **record))

    counts = Counter(edge['relation'] for edge in edges)
    degree = {edge[end] for edge in edges for end in ('source_id', 'target_id')}
    summary = dict(corpus_docx=sum(map(len, docs.values())), input_docx=input_count,
                   read_docx=sum(f['status'] == 'READ' for f in files), nodes=len(nodes),
                   node_status=dict(Counter(n['full_text_status'] for n in nodes.values())),
                   isolated_nodes=len(nodes.keys() - degree), edges=len(edges),
                   ambiguous_catalog_numbers=len(ambiguous_numbers),
                   edges_by_type={relation: counts[relation] for relation in RELATIONS},
                   review_by_reason=dict(Counter(item['reason'] for item in review)),
                   file_issues_by_reason=dict(Counter(item['reason'] for item in file_issues)),
                   parser_warnings_by_code=dict(warning_counts),
                   elapsed_seconds=round(monotonic() - started, 2))
    graph = dict(dataset=DATASET, revision=REVISION, catalog_path=CATALOG_PATH,
                 catalog_sha256=sha256(snapshot).hexdigest(), legal_effect_verified=False,
                 summary=summary, nodes=list(nodes.values()), edges=edges)
    return graph, dict(summary=summary, files=files, file_issues=file_issues,
                       ambiguous_catalog_numbers=ambiguous_numbers, needs_review=review)
