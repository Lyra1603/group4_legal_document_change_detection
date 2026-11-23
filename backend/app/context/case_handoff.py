"""Internal, versioned input for the Context owner; not a new API contract.

Adapters may produce this input from approved corpus sources. Source identity
and version live outside legacy v1/s/ref_* IDs; never infer them from filenames.
"""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import re
from urllib.parse import urlsplit

from ..schemas.contracts import AmendmentItem, ExtractedDocument
from ..schemas.report_validation import validate_payload, validate_sources
from .chunk_builder import build_chunks
from .source_registry import SourceRegistry

DATASETS = {'th1nhng0/vietnamese-legal-documents',
            'vohuutridung/vietnamese-legal-documents'}


def content_digest(document):
    value = json.dumps(document['blocks'], ensure_ascii=False, sort_keys=True,
                       separators=(',', ':'))
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


@dataclass(frozen=True)
class ContextCase:
    case_id: str
    snapshot_id: str
    source_kind: str
    documents: list[dict]
    provenance: dict
    amendment: dict
    candidate_query: str | None

    @classmethod
    def from_dict(cls, raw):
        if not isinstance(raw, dict) or raw.get('format') != 'pocs-context-case-v1':
            raise ValueError('Unsupported Context case format')
        for key in ('case_id', 'snapshot_id'):
            if not isinstance(raw.get(key), str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', raw[key]):
                raise ValueError('Invalid case or snapshot identity')
        kind = raw.get('source_kind')
        if kind not in {'SYNTHETIC', 'LOCAL_UNREVIEWED', 'DATASET_UNREVIEWED', 'DATASET_REVIEWED'}:
            raise ValueError('Explicit source/review label required')
        docs, provenance = raw.get('documents'), raw.get('provenance')
        if not isinstance(docs, list) or not docs or not isinstance(provenance, dict):
            raise ValueError('Documents and provenance required')
        ids, roles = set(), []
        for doc in docs:
            validate_payload(ExtractedDocument, doc)
            did = doc['document_id']
            if not did or did in ids or doc['role'] not in {'BASE', 'AMENDMENT', 'REFERENCE'}:
                raise ValueError('Duplicate identity or invalid role')
            ids.add(did); roles.append(doc['role'])
            refs = [b['source_ref'] for b in doc['blocks']]
            if not refs or len(set(refs)) != len(refs) or any(not r for r in refs):
                raise ValueError('Empty/duplicate source locators')
            meta = provenance.get(did)
            if not isinstance(meta, dict):
                raise ValueError('Source provenance missing')
            for key in ('source_identity', 'version_id'):
                if not isinstance(meta.get(key), str) or not meta[key].strip():
                    raise ValueError('Source identity/version missing')
            if meta.get('content_sha256') != content_digest(doc):
                raise ValueError('Source content digest mismatch')
            paths = meta.get('unit_paths')
            if not isinstance(paths, dict) or set(paths) != set(refs) or any(not isinstance(v,str) or not v for v in paths.values()):
                raise ValueError('Every block needs an explicit source location')
            if kind.startswith('DATASET') and meta.get('origin') != 'UPLOAD':
                if meta.get('dataset') not in DATASETS or not meta.get('dataset_id'):
                    raise ValueError('Dataset-qualified identity required')
                if not isinstance(meta.get('revision'), str) or not re.fullmatch('[0-9a-f]{40}', meta['revision']):
                    raise ValueError('Pin a dataset commit, not a moving branch')
                url = urlsplit(meta.get('source_url', ''))
                if url.scheme not in {'https','http'} or not url.netloc or url.username or url.password:
                    raise ValueError('Source URL required')
        if kind.startswith('DATASET') and not any(m.get('dataset') in DATASETS for m in provenance.values()):
            raise ValueError('Dataset case requires at least one qualified dataset source')
        if roles.count('BASE') != 1 or roles.count('AMENDMENT') != 1 or set(provenance) != ids:
            raise ValueError('One local V1, one S and exact provenance mapping required')
        if {d['role']:d['document_id'] for d in docs if d['role'] != 'REFERENCE'} != {'BASE':'v1','AMENDMENT':'s'}:
            raise ValueError('Preserve legacy local v1/s identity')
        if len({(m['source_identity'],m['version_id']) for m in provenance.values()}) != len(docs):
            raise ValueError('Ambiguous source versions')
        item = raw.get('amendment')
        validate_payload(AmendmentItem,item)
        validate_sources(item,{d['document_id']:d for d in docs})
        if item['instruction']['document_id'] != 's' or item['target_document'] != 'v1' or item['applicability'] != 'APPLIES':
            raise ValueError('Context query requires an already resolved local amendment')
        if not isinstance(item['before_text'],str) or not isinstance(item['after_text'],str):
            raise ValueError('Context query needs known before/after; never invent V1')
        if not item['before_text'] or not any(item['before_text'] in e['quote'] for e in item['evidence'] if e['document_id']=='v1'):
            raise ValueError('Before text lacks literal V1 evidence')
        if item['after_basis'] == 'QUOTED' and not any(item['after_text'] in e['quote'] for e in [item['instruction'],*item['evidence']] if e['document_id']=='s'):
            raise ValueError('Quoted after text lacks S evidence')
        query = raw.get('candidate_query')
        if query is not None and (not isinstance(query,str) or not query.strip() or len(query)>8000):
            raise ValueError('Candidate query invalid')
        return cls(raw['case_id'],raw['snapshot_id'],kind,deepcopy(docs),deepcopy(provenance),deepcopy(item),query)

    def registry(self, comparison_id, *, max_chunks=100, max_chars=12000):
        versions = {did:m['version_id'] for did,m in self.provenance.items()}
        return SourceRegistry(build_chunks(comparison_id,self.documents,versions,
                              max_chunks=max_chunks,max_chars=max_chars),self.documents)

    def trace(self, evidence):
        validate_sources(evidence,{d['document_id']:d for d in self.documents})
        meta = self.provenance[evidence['document_id']]
        return {'evidence':deepcopy(evidence), 'source_identity':meta['source_identity'],
                'version_id':meta['version_id'], 'content_sha256':meta['content_sha256'],
                'dataset':meta.get('dataset'), 'dataset_id':meta.get('dataset_id'),
                'revision':meta.get('revision'), 'source_url':meta.get('source_url'),
                'unit_paths':[meta['unit_paths'][r] for r in evidence['source_refs']]}
