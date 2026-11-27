"""Export the document graph and optionally verify retrieval on a dedicated LightRAG container."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from time import monotonic
from uuid import uuid4

from .app.context.case_runner import retrieve_candidates
from .app.context.document_graph import prepare_pilot
from .app.context.lightrag_client import RetrievalError, UPSTREAM_COMMIT
from .app.context.owned_server import OwnedLightRAG, read_provider_env
from .app.context.shared_service import graph_view

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SELECTION = ROOT / 'data/legal-dataset-study/document-graph-pilot.json'


def _write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def _run_live(args, session, selection, registry):
    result = dict(mode='REAL_LIGHTRAG_HTTP', session_id=session, upstream_commit=UPSTREAM_COMMIT,
                  generated_at=datetime.now(timezone.utc).isoformat(), index_ready=False,
                  indexed_documents=[], retrieval=None, expected_evidence=selection['expected_evidence'],
                  expected_evidence_found=False, upstream_graph=None, graph_audit=None,
                  failure=None, graph_issue=None, cleanup_issues=[])
    server = None
    started = monotonic()
    try:
        try:
            settings = read_provider_env(args.provider_env_file)
        except (OSError, ValueError):
            raise RetrievalError('INVALID_PROVIDER_ENV_FILE') from None
        server = OwnedLightRAG(args.runtime_dir, session, settings, budget=args.budget)
        client = server.start()
        result.update(provider=server.profile, docker_image_id=server.image_id)
        client.index(list(registry.chunks.values()))
        result['index_ready'] = client.ready
        result['indexed_documents'] = [dict(file_source=source, lightrag_document_id=upstream_id)
                                        for source, upstream_id in sorted(client.ids.items())]
        query = selection['query']
        retrieval = retrieve_candidates(client, registry, query)
        result.update(query=query, retrieval=retrieval)
        expected = result['expected_evidence']
        expected_text = registry.documents[expected['document_id']]['blocks']
        quote, = [block['text'] for block in expected_text if block['source_ref'] == expected['source_ref']]
        result['expected_evidence_found'] = any(
            item['document_id'] == expected['document_id'] and expected['source_ref'] in item['source_refs']
            and quote in item['quote'] for item in retrieval['evidence'])
        try:
            graph = client.graph()
            result['graph_audit'] = graph_view(graph, registry)['audit']
            result['upstream_graph'] = graph
        except (RetrievalError, ValueError) as exc:
            result['graph_issue'] = exc.code if isinstance(exc, RetrievalError) else 'GRAPH_PROTOCOL_ERROR'
    except RetrievalError as exc:
        result['failure'] = exc.code
    except OSError:
        result['failure'] = 'LOCAL_CONFIG_OR_RUNTIME_UNAVAILABLE'
    finally:
        if server:
            result['cleanup_issues'] = server.finish()
    result['elapsed_seconds'] = round(monotonic() - started, 2)
    result['verified'] = bool(result['index_ready'] and result['expected_evidence_found']
                              and not result['failure'] and not result['graph_issue']
                              and not result['cleanup_issues'])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selection', type=Path, default=DEFAULT_SELECTION)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--mode', choices=['graph', 'real'], default='graph')
    parser.add_argument('--provider-env-file', type=Path)
    parser.add_argument('--runtime-dir', type=Path, default=ROOT / 'runtime/lightrag/document-graph-sessions')
    parser.add_argument('--budget', type=int, default=600)
    args = parser.parse_args()
    if args.mode == 'real' and args.provider_env_file is None:
        parser.error('--mode real requires --provider-env-file')
    if not 30 <= args.budget <= 1800:
        parser.error('--budget must be between 30 and 1800 seconds')
    selection = json.loads(args.selection.read_text(encoding='utf-8-sig'))
    session = uuid4().hex
    graph, registry = prepare_pilot(ROOT, selection, session)
    expected = selection['expected_evidence']
    if not any(chunk.document_id == expected['document_id'] and expected['source_ref'] in chunk.source_refs
               for chunk in registry.chunks.values()):
        parser.error('The expected evidence must be included in the selected index blocks.')
    # A fresh output directory keeps graph-only and real runs from sharing stale evidence.
    args.output_dir.mkdir(parents=True, exist_ok=False)
    _write_json(args.output_dir / 'document-graph.json', graph)
    print(json.dumps(dict(mode=args.mode, documents=len(graph['files']), nodes=len(graph['nodes']),
                          edges=len(graph['edges']), review=len(graph['needs_review']),
                          index_records=len(registry.chunks))), flush=True)
    if args.mode == 'graph':
        return 0
    result = _run_live(args, session, selection, registry)
    _write_json(args.output_dir / 'lightrag-live.json', result)
    print(json.dumps({field: result[field] for field in
                     ('mode', 'index_ready', 'expected_evidence_found', 'verified', 'failure',
                      'graph_issue', 'cleanup_issues', 'elapsed_seconds')}), flush=True)
    return 0 if result['verified'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
