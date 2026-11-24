"""Context-only handoff runner. It neither resolves V1 nor concludes B impact."""
from copy import deepcopy
import time
import re
import unicodedata

from ..change_analysis.text_diff import compute_text_diff
from .context_builder import build_context, prepare_index, validate_query_diff
from .lightrag_client import RetrievalError, UPSTREAM_COMMIT


def retrieve_candidates(client, registry, query):
    """Validate the complete batch atomically, including candidates for B."""
    try:
        raw = client.query(query)
        evidence = [registry.evidence(c) for c in raw['chunks']]
        if not evidence:
            raise RetrievalError('RETRIEVAL_EMPTY_UNCONFIRMED')
        return {'status':'CANDIDATES_ONLY', 'evidence':evidence, 'issues':[],
                'legal_impact_confirmed':False}
    except (RetrievalError,ValueError) as exc:
        return {'status':'UNVERIFIED', 'evidence':[], 'issues':[{
            'stage':'context', 'code':exc.code if isinstance(exc,RetrievalError) else 'RETRIEVAL_SOURCE_REJECTED',
            'message':'Retrieval candidates unverified; no legal absence/impact conclusion.'}],
            'legal_impact_confirmed':False}


def run_case(case, client, registry, *, text_diff=None, repeats=1):
    if type(repeats) is not int or not 1 <= repeats <= 3:
        raise ValueError('Use one to three bounded retrieval samples')
    if client is None:
        raise ValueError('An explicit retrieval client is required; disabled is only the baseline')
    if registry.documents != {d['document_id']:d for d in case.documents}:
        raise ValueError('Registry belongs to different source documents')
    for chunk in registry.chunks.values():
        if (chunk.comparison_id != client.comparison_id
                or chunk.version != case.provenance[chunk.document_id]['version_id']):
            raise ValueError('Registry/client comparison or source version mismatch')
    expected = {
        (d['document_id'], d['role'], case.provenance[d['document_id']]['version_id'], block['source_ref']): block['text']
        for d in case.documents for block in d['blocks'] if block['text'].strip()
    }
    actual = {(c.document_id, c.role, c.version, c.source_ref): c.text for c in registry.chunks.values()}
    if actual != expected or len(actual) != len(registry.chunks):
        raise ValueError('Registry omits, duplicates or changes source blocks')
    item = deepcopy(case.amendment)
    text = compute_text_diff(item) if text_diff is None else deepcopy(text_diff)
    validate_query_diff(item,text)
    t = time.perf_counter()
    disabled = build_context(item,registry,None,text_diff=text)
    disabled_ms = (time.perf_counter()-t)*1000
    t = time.perf_counter()
    prepared = prepare_index(item,registry,client)
    index_ms = (time.perf_counter()-t)*1000
    results, latencies = [], []
    if not prepared.issues:
        for _ in range(repeats):
            t = time.perf_counter()
            result = build_context(prepared.amendment,registry,client,text_diff=text)
            results.append(result)
            latencies.append((time.perf_counter()-t)*1000)
    enabled = results[0] if results else prepared
    all_issues = []
    for sample in results or [prepared]:
        for issue in sample.issues:
            if issue not in all_issues:
                all_issues.append(issue)
    query_samples = [{'sample': i + 1, 'latency_ms': elapsed,
                      'verified': not sample.issues, 'issues': deepcopy(sample.issues)}
                     for i, (sample, elapsed) in enumerate(zip(results, latencies))]
    candidates = None
    if case.candidate_query and not prepared.issues:
        candidates = retrieve_candidates(client,registry,case.candidate_query)
    traces=[]
    for e in enabled.amendment['context']['evidence']:
        traces.append(case.trace(e))
    candidate_traces=[case.trace(e) for e in candidates['evidence']] if candidates else []
    result = {'case_id':case.case_id,'source_kind':case.source_kind,
              'snapshot_id':case.snapshot_id,'upstream_commit':UPSTREAM_COMMIT,
              'comparison_id':next(iter(registry.chunks.values())).comparison_id,
              'text_diff':text,
              'disabled':{'amendment':disabled.amendment,'latency_ms':disabled_ms},
              'enabled':{'amendment':enabled.amendment,'issues':all_issues,
                         'index_ms':index_ms,'query_latency_ms':latencies,'query_samples':query_samples,
                         'raw_retrieval':enabled.retrieved,'source_trace':traces,
                         'repeat_consistent':all(r.amendment==enabled.amendment for r in results) if results else None},
              'candidate_retrieval':candidates,'candidate_source_trace':candidate_traces,
              'registry':registry.manifest(),'project_source_graph':registry.source_graph(),
              'retrieval_completed':len(results) == repeats and not all_issues,
              'semantic_executed':False,'legal_correctness_evaluated':False,
              'limits':['Context-only test, not a complete product or a legal-impact verdict.',
                        'One source block per chunk; oversize blocks are rejected, not truncated.',
                        'B retrieval returns candidates only. No legal relation is inferred.',
                        'Source/review label describes input provenance, not independently proven legal truth.']}
    return result


def audit_extracted_graph(graph, registry):
    """Observed KG metadata audit only; never promote edges to legal evidence."""
    if not isinstance(graph, dict) or not isinstance(graph.get('nodes'), list):
        raise ValueError('Malformed extracted graph')
    unknown=[]; shared_units=[]; labels={}
    for node in graph['nodes']:
        if not isinstance(node, dict) or not isinstance(node.get('properties'), dict):
            raise ValueError('Malformed graph node')
        props=node['properties']
        if not isinstance(props.get('file_path'), str) or not isinstance(node.get('id'), str):
            raise ValueError('Malformed graph source metadata')
        label=node['id']
        normalized=unicodedata.normalize('NFC',label).casefold().strip()
        labels.setdefault(normalized,[]).append(label)
        paths=props.get('file_path','').split('<SEP>')
        docs=set()
        for path in paths:
            if path not in registry.chunks:
                unknown.append({'node':label,'file_path':path})
            else:
                docs.add(registry.chunks[path].document_id)
        if re.match(r'^(điều|khoản|điểm)\s',normalized) and len(docs)>1:
            shared_units.append({'node':label,'document_ids':sorted(docs)})
    return {'kind':'OBSERVED_KG_METADATA_AUDIT_NOT_LEGAL_VALIDATION',
            'unknown_sources':unknown,'possible_cross_document_unit_merges':shared_units,
            'duplicate_normalized_labels':[v for v in labels.values() if len(v)>1],
            'canonical_identity_authority':'PROJECT_SOURCE_REGISTRY',
            'legal_relations_verified':False}
