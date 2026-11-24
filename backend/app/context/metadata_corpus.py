"""Bounded metadata-only corpus. Does not manufacture legal text or amendments."""
import csv
import hashlib
import json
from pathlib import Path

from .chunk_builder import SourceChunk
from .source_registry import SourceRegistry

DATASET = 'th1nhng0/vietnamese-legal-documents'
REVISION = '8977887f17be2defae4c5171d55562e1cde7d695'
IDS = ('18128', '95942')


def load_metadata(root: Path, session: str):
    path = root / 'data/legal-dataset-study/data/metadata.csv'
    with path.open(encoding='utf-8-sig', newline='') as stream:
        rows = {r['id']: r for r in csv.DictReader(stream) if r['id'] in IDS}
    if set(rows) != set(IDS):
        raise ValueError('Required metadata rows are missing')
    chunks, documents, bindings = [], [], {}
    for index, dataset_id in enumerate(IDS, 1):
        row = rows[dataset_id]
        did, ref = f'ref_{index}', 'block:1'
        text = f'Dataset: {DATASET}\nRevision: {REVISION}\n' + '\n'.join(f'{k}: {v}' for k, v in row.items())
        source = f'metadata-vbpl-{dataset_id}-' + hashlib.sha256(text.encode()).hexdigest()[:16] + '.txt'
        header = 'POCS_SOURCE ' + json.dumps(dict(comparison=session, document_id=did,
            role='REFERENCE', version=REVISION, source_ref=ref), ensure_ascii=False) + '\n'
        chunks.append(SourceChunk(session, source, did, 'REFERENCE', REVISION, ref, text, header + text))
        # Internal source map only: these records are NOT ExtractedDocument/DOCX.
        documents.append(dict(document_id=did, role='REFERENCE', blocks=[dict(source_ref=ref, text=text)]))
        bindings[did] = dict(dataset=DATASET, revision=REVISION, dataset_id=dataset_id,
            source_identity=f'{DATASET}@{REVISION}:{dataset_id}', metadata=row,
            scope='METADATA_ONLY', current_legal_status_verified=False,
            source_ref=ref, source_sha256=hashlib.sha256(text.encode()).hexdigest())
    return SourceRegistry(chunks, documents), bindings
