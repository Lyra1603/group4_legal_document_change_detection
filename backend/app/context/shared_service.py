"""One team-facing backend, private per-comparison services and one demo corpus.

The upstream key never crosses the browser API. A single process serializes
provider work; corpus cleanup is separate from comparison cleanup.
"""
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from threading import Lock
import time
import uuid

from ..demo_runner import run_demo_analysis
from ..pipeline import issue
from .owned_server import OwnedLightRAG
from .provider_settings import provider_environment
from .lightrag_client import RetrievalError
from .case_runner import audit_extracted_graph
from .metadata_corpus import load_metadata


def graph_view(graph, registry):
    audit = audit_extracted_graph(graph, registry)
    def sources(properties):
        return [dict(document_id=registry.chunks[p].document_id,
                     source_refs=list(registry.chunks[p].source_refs),
                     quote=registry.chunks[p].text)
                for p in properties.get('file_path', '').split('<SEP>') if p in registry.chunks]
    nodes = [dict(id=n['id'], description=str(n['properties'].get('description', '')),
                  sources=sources(n['properties'])) for n in graph['nodes']]
    ids = {n['id'] for n in nodes}
    edges = []
    if not isinstance(graph.get('edges'), list):
        raise ValueError('Malformed graph edges')
    for edge in graph['edges']:
        if not isinstance(edge, dict) or not isinstance(edge.get('properties'), dict):
            raise ValueError('Malformed graph edge')
        if edge.get('source') not in ids or edge.get('target') not in ids:
            raise ValueError('Graph edge endpoint missing')
        refs = sources(edge['properties'])
        edges.append(dict(source=edge['source'], target=edge['target'],
            description=str(edge['properties'].get('description', '')),
            sources=refs, legal_relation_verified=False))
    return dict(kind='OBSERVED_LIGHTRAG_KG_NOT_LEGAL_VERDICT', nodes=nodes, edges=edges, audit=audit)


class SharedContextService:
    def __init__(self, root, runtime, settings, *, server_factory=OwnedLightRAG):
        self.root, self.runtime = Path(root), Path(runtime)
        self.settings = dict(settings)
        self.server_factory = server_factory
        self.gate, self.state_lock = Lock(), Lock()
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='pocs-corpus')
        self.corpus_server = self.corpus_client = self.corpus_registry = None
        self.corpus = dict(state='IDLE', issues=[], source_kind='REAL_DATASET_METADATA',
                           full_text_indexed=False, sources={}, graph=None, evidence=[])
        self.comparisons = OrderedDict()

    @property
    def configured(self):
        try:
            provider_environment(self.settings)
        except RetrievalError:
            return False
        return True

    def _server(self, session, budget):
        if not self.configured:
            raise RetrievalError('REAL_SERVICE_CONFIGURATION_REQUIRED')
        return self.server_factory(self.runtime, session, self.settings, budget=budget)

    def status(self):
        with self.state_lock:
            return deepcopy(self.corpus)

    def _update(self, **values):
        with self.state_lock:
            self.corpus.update(values)

    def start_corpus(self):
        if self.status()['state'] == 'READY':
            return self.status()  # no duplicate ingestion/provider call
        if not self.gate.acquire(blocking=False):
            raise RetrievalError('DEMO_BUSY')
        if self.status()['state'] in ('FAILED', 'INDEXING'):
            self.gate.release()
            # Failed ingress may have partially indexed sources. Do not replay
            # automatically or replace a shared corpus under another browser.
            raise RetrievalError('CORPUS_RESTART_REQUIRED')
        self._update(state='INDEXING', issues=[])
        self.executor.submit(self._index_corpus)
        return self.status()

    def _index_corpus(self):
        try:
            session = uuid.uuid4().hex
            registry, bindings = load_metadata(self.root, session)
            self._update(sources=bindings)
            self.corpus_registry = registry
            self.corpus_server = self._server(session, 600)
            self.corpus_client = self.corpus_server.start()
            self.corpus_client.index(list(registry.chunks.values()))
            graph = graph_view(self.corpus_client.graph(), registry)
            self._update(state='READY', graph=graph)
        except RetrievalError as exc:
            self._update(state='FAILED', issues=[exc.code])
        except Exception:
            self._update(state='FAILED', issues=['CORPUS_PREPARATION_FAILED'])
        finally:
            self.gate.release()

    def query(self, text):
        if self.status()['state'] != 'READY':
            raise RetrievalError('INDEX_NOT_READY')
        if not self.gate.acquire(blocking=False):
            raise RetrievalError('DEMO_BUSY')
        try:
            client = self.corpus_client
            client.deadline = time.monotonic() + 180
            raw = client.query(text)
            evidence = [self.corpus_registry.evidence(c) for c in raw['chunks']]
            # Empty retrieval is explicit; it is not a legal conclusion.
            if not evidence:
                raise RetrievalError('RETRIEVAL_EMPTY')
            try:
                graph = graph_view(client.graph(), self.corpus_registry)
            except ValueError:
                raise RetrievalError('GRAPH_PROTOCOL_ERROR') from None
            self._update(evidence=evidence, graph=graph, issues=[])
            return dict(evidence=evidence, sources=self.status()['sources'], graph=graph,
                        legal_impact_confirmed=False)
        except ValueError:
            self._update(issues=['RETRIEVAL_SOURCE_MISMATCH'])
            raise RetrievalError('RETRIEVAL_SOURCE_MISMATCH') from None
        except RetrievalError as exc:
            self._update(issues=[exc.code])
            raise
        finally:
            self.gate.release()

    def context(self, comparison_id):
        with self.state_lock:
            return deepcopy(self.comparisons.get(comparison_id))

    def compare(self, parsed, comparison_id, deadline):
        server = client = None
        artifact = dict(state='FAILED', issues=[], items=[], graph=None,
                        index_scope='CITED_AMENDMENT_BLOCKS_AND_UPLOADED_REFERENCES')
        acquired = self.gate.acquire(blocking=False)
        try:
            if not acquired:
                raise RetrievalError('DEMO_BUSY')
            server = self._server(uuid.uuid4().hex, max(30, min(600, int(deadline - time.monotonic()))))
            server.deadline = min(server.deadline, deadline)
            server.comparison_id = comparison_id
            client = server.start()
        except RetrievalError as exc:
            artifact['issues'].append(exc.code)
        except (ValueError, OSError):
            artifact['issues'].append('REAL_SERVICE_CONFIGURATION_REQUIRED')
        outcome = None
        try:
            def capture(context, text, registry):
                artifact['items'].append(dict(amendment_id=context.amendment['amendment_id'],
                    evidence=context.amendment['context']['evidence'],
                    general_context=context.amendment['context']['general_context'],
                    verified=bool(client and client.ready and not context.issues), issues=context.issues))
                if client is not None and client.ready:
                    try:
                        artifact['graph'] = graph_view(client.graph(), registry)
                    except (RetrievalError, ValueError):
                        artifact['issues'].append('GRAPH_UNAVAILABLE_OR_UNVERIFIED')
            outcome = run_demo_analysis(parsed, comparison_id, deadline,
                context_client=client, context_sink=capture,
                pack_context_blocks=self.settings.get('LEGAL_AI_PROVIDER') == 'groq-jina')
            artifact['state'] = 'READY' if artifact['items'] and all(x['verified'] for x in artifact['items']) and not artifact['issues'] else 'PARTIAL'
            for code in artifact['issues']:
                outcome.warnings.append(issue('context', code, 'LightRAG chưa xác minh được; xem trạng thái Context.'))
            return outcome
        finally:
            if server:
                cleanup_issues = server.finish()
                artifact['issues'].extend(cleanup_issues)
                if outcome is not None:
                    for code in cleanup_issues:
                        outcome.warnings.append(issue('context', code, 'Chưa xác nhận dọn xong tài nguyên riêng của lượt chạy.'))
                    if cleanup_issues and outcome.status == 'SUCCESS':
                        outcome.status = 'PARTIAL'
            if artifact['issues'] and artifact['state'] == 'READY':
                artifact['state'] = 'PARTIAL'
            with self.state_lock:
                self.comparisons[comparison_id] = artifact
                while len(self.comparisons) > 10:
                    self.comparisons.popitem(last=False)
            if acquired:
                self.gate.release()

    def close(self):
        self.executor.shutdown(wait=True, cancel_futures=True)
        if self.corpus_server:
            return self.corpus_server.finish()
        return []
