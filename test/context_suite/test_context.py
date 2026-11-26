from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import tempfile
from threading import Barrier
from time import monotonic
import unittest

import httpx

from backend.app.config import LightRAGConfig
from backend.app.context.chunk_builder import build_chunks, documents_from_parsed
from backend.app.context.context_builder import (
    build_context, build_retrieval_query, prepare_context, prepare_index,
)
from backend.app.change_analysis.text_diff import compute_text_diff
from backend.app.context.lightrag_client import MAX_QUERY_CHARS, LightRAGClient, RetrievalError
from backend.app.context.semantic_bridge import run_semantic_stage
from backend.app.context.source_registry import SourceRegistry
from backend.app.schemas.report_validation import validate_amendment, validate_sources
from test.context_suite.support import ContractServer, sample


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.documents, self.versions, self.item, self.fixture = sample()
        self.chunks = build_chunks("c1", self.documents, self.versions)
        self.registry = SourceRegistry(self.chunks, self.documents)
        self.diff = compute_text_diff(self.item)

    def client(self, behavior="normal", *, workspace="demo", url="http://localhost:9621", comparison="c1", deadline=None):
        server = ContractServer(workspace, behavior)
        config = LightRAGConfig(url, workspace, poll_interval=0.001)
        client = LightRAGClient(config, comparison, Path(self.temporary.name),
                               deadline=deadline or monotonic() + 5, transport=httpx.MockTransport(server))
        self.addCleanup(client.close)
        return client, server

    def test_context_contract_and_source_trace(self):
        client, server = self.client()
        client.index(self.chunks)
        result = build_context(self.item, self.registry, client, text_diff=self.diff)
        self.assertFalse(result.issues)
        validate_sources(result.amendment, self.registry.documents)
        validate_amendment(result.amendment, self.registry.documents, self.fixture["clauses"])
        self.assertIn("ref_2", {e["document_id"] for e in result.amendment["context"]["evidence"]})
        self.assertEqual(self.item, self.fixture["report"]["results"][0]["amendment"])
        self.assertIsNone(client.cleanup())
        self.assertEqual(set(server.deleted), {"doc-0", "doc-1", "doc-2", "doc-3"})
        self.assertIn("DELETION_CONFIRMED", json.loads(client.ledger.read_text())["phase"])

    def test_duplicate_index_is_noop(self):
        client, server = self.client()
        client.index(self.chunks)
        client.index(self.chunks)
        self.assertEqual(server.calls.count(("POST", "/documents/texts")), 1)

    def test_concurrent_duplicate_index_is_noop(self):
        client, server = self.client()
        with ThreadPoolExecutor(2) as pool:
            list(pool.map(lambda _: client.index(self.chunks), [1, 2]))
        self.assertEqual(server.calls.count(("POST", "/documents/texts")), 1)

    def test_same_article_different_document_version_not_merged(self):
        self.assertEqual(self.chunks[2].text, self.chunks[3].text)
        self.assertNotEqual(self.chunks[2].file_source, self.chunks[3].file_source)
        graph = self.registry.source_graph()
        self.assertEqual(len(graph["nodes"]), 8)
        self.assertFalse(any(e["inferred"] for e in graph["edges"]))

    def test_duplicate_document_and_source_ids_rejected(self):
        with self.assertRaises(ValueError):
            build_chunks("c", self.documents + [self.documents[0]], self.versions)
        docs = deepcopy(self.documents)
        docs[0]["blocks"] *= 2
        with self.assertRaises(ValueError):
            build_chunks("c", docs, self.versions)

    def test_other_comparison_source_rejected(self):
        foreign = build_chunks("foreign", self.documents, self.versions)[0]
        with self.assertRaises(ValueError):
            self.registry.evidence({"file_path": foreign.file_source, "content": foreign.text})

    def test_no_basename_matching(self):
        with self.assertRaises(ValueError):
            self.registry.evidence({"file_path": "/foreign/" + self.chunks[0].file_source, "content": self.chunks[0].text})

    def test_retrieval_failures_preserve_reference_status_and_context(self):
        for i, behavior in enumerate(("foreign", "paraphrase", "empty", "timeout")):
            with self.subTest(behavior=behavior):
                client, _ = self.client(behavior, url=f"http://localhost:{9630+i}")
                client.index(self.chunks)
                result = build_context(self.item, self.registry, client, text_diff=self.diff)
                self.assertTrue(result.issues)
                self.assertEqual(result.amendment["context"], self.item["context"])
                self.assertTrue(result.amendment["needs_review"])
                self.assertNotIn("MISSING", str(result.issues))
                client.cleanup()

    def test_query_before_ready(self):
        client, _ = self.client()
        with self.assertRaisesRegex(RetrievalError, "INDEX_NOT_READY"):
            client.query("find a source")

    def test_index_not_ready_deadline(self):
        client, server = self.client("pending", deadline=monotonic() + 0.025)
        with self.assertRaises(RetrievalError):
            client.index(self.chunks)
        self.assertFalse(any(p == "/query/data" for _, p in server.calls))
        client.cleanup()

    def test_server_reserved_across_comparisons_and_processes(self):
        first, _ = self.client()
        with self.assertRaisesRegex(RetrievalError, "SERVER_RESERVED"):
            self.client(comparison="c2")
        first.close()
        with self.assertRaisesRegex(RetrievalError, "SERVER_RESERVED"):
            self.client(comparison="c2")

    def test_concurrent_comparisons_separate_servers(self):
        def run(index):
            cid = f"comparison-{index}"
            chunks = build_chunks(cid, self.documents, self.versions)
            registry = SourceRegistry(chunks, self.documents)
            client, server = self.client(url=f"http://localhost:{9700+index}", comparison=cid, workspace=f"w{index}")
            try:
                client.index(chunks)
                data = client.query("find reporting rules")
                self.assertTrue(all(r["file_path"] in registry.chunks for r in data["chunks"]))
                return {r["file_path"] for r in data["chunks"]}
            finally:
                client.cleanup()
        with ThreadPoolExecutor(2) as pool:
            a, b = list(pool.map(run, [1, 2]))
        self.assertTrue(a.isdisjoint(b))

    def test_cleanup_busy_is_pending_and_never_global_delete(self):
        client, server = self.client("cleanup_busy")
        client.index(self.chunks)
        self.assertEqual(client.cleanup(), "CLEANUP_PENDING")
        self.assertEqual(json.loads(client.ledger.read_text())["phase"], "CLEANUP_PENDING")
        self.assertFalse(any(m == "DELETE" and p == "/documents" for m, p in server.calls))

    def test_lost_upload_ack_no_retry_and_quarantine(self):
        client, server = self.client("lost_ack")
        with self.assertRaises(RetrievalError):
            client.index(self.chunks)
        with self.assertRaisesRegex(RetrievalError, "INDEX_SUBMISSION_UNCERTAIN"):
            client.index(self.chunks)
        self.assertEqual(client.cleanup(), "CLEANUP_PENDING")
        self.assertEqual(server.calls.count(("POST", "/documents/texts")), 1)
        self.assertFalse(server.deleted)

    def test_scope_mismatch_fails_before_upload(self):
        client, server = self.client()
        server.workspace = "foreign"
        with self.assertRaisesRegex(RetrievalError, "SERVER_SCOPE_UNVERIFIED"):
            client.index(self.chunks)
        self.assertNotIn(("POST", "/documents/texts"), server.calls)

    def test_index_error_preserves_code_at_context_boundary(self):
        client, server = self.client()
        server.workspace = "wrong"
        result = prepare_context(self.item, self.registry, client)
        self.assertEqual(result.issues[0]["code"], "SERVER_SCOPE_UNVERIFIED")
        self.assertEqual(result.amendment["context"], self.item["context"])
        self.assertTrue(result.amendment["needs_review"])

    def test_disabled_retrieval_preserves_input(self):
        result = build_context(self.item, self.registry, None)
        self.assertEqual(result.amendment, self.item)
        self.assertIsNot(result.amendment, self.item)

    def test_parallel_index_text_then_query_then_semantic(self):
        client, server = self.client()
        barrier = Barrier(2, timeout=2)
        completed = set()
        def context_prepare(item):
            barrier.wait()
            result = prepare_index(item, self.registry, client)
            self.assertFalse(server.queries)
            completed.add("index")
            return result
        def text_diff(item):
            barrier.wait()
            completed.add("text")
            return deepcopy(self.diff)
        def context_work(item, text):
            self.assertEqual(completed, {"index", "text"})
            result = build_context(item, self.registry, client, text_diff=text)
            query = json.loads(server.queries[0])
            self.assertEqual(query['text_diff'], self.diff)
            self.assertEqual(query['instruction_source'], self.item['instruction'])
            completed.add('query')
            return result
        def semantic_diff(item, text):
            self.assertEqual(completed, {"index", "text", "query"})
            self.assertEqual(text, self.diff)
            self.assertGreater(len(item["context"]["evidence"]), len(self.item["context"]["evidence"]))
            return deepcopy(self.fixture["report"]["results"][0]["semantic_diff"])
        try:
            run_semantic_stage(self.item, context_prepare=context_prepare,
                               context_work=context_work, text_diff=text_diff, semantic_diff=semantic_diff)
        finally:
            client.cleanup()

    def test_bounds_and_secret_repr(self):
        with self.assertRaises(ValueError):
            build_chunks("c", self.documents, self.versions, max_chars=2)
        self.assertNotIn("secret-value", repr(LightRAGConfig("http://localhost", "w", api_key="secret-value")))

    def test_query_diff_handles_unicode_insert_delete_and_no_change(self):
        for before, after in [('Điều 2', 'Điều 2 mới'), ('Điều 2 mới', 'Điều 2'),
                              ('30 ngày', '15 ngày'), ('không đổi', 'không đổi')]:
            with self.subTest(before=before, after=after):
                item = deepcopy(self.item)
                item.update(before_text=before, after_text=after)
                diff = compute_text_diff(item)
                query = json.loads(build_retrieval_query(item, diff))
                self.assertEqual(query['text_diff'], diff)
                self.assertEqual(query['before_text'], before)
                self.assertEqual(query['after_text'], after)

    def test_invalid_or_missing_diff_never_queries(self):
        client, server = self.client()
        client.index(self.chunks)
        wrong_id = deepcopy(self.diff)
        wrong_id['amendment_id'] = 'another'
        wrong_offset = deepcopy(self.diff)
        wrong_offset['changes'][0]['old_start'] = -1
        wrong_quote = deepcopy(self.diff)
        wrong_quote['changes'][0]['new_text'] = 'fabricated'
        wrong_type = deepcopy(self.diff)
        wrong_type['changes'][0]['type'] = 'INSERT'
        incomplete = deepcopy(self.diff)
        incomplete['changes'] = []
        for diff in [None, wrong_id, wrong_offset, wrong_quote, wrong_type, incomplete]:
            with self.subTest(diff=diff):
                result = build_context(self.item, self.registry, client, text_diff=diff)
                self.assertTrue(result.issues)
                self.assertEqual(result.amendment['context'], self.item['context'])
                self.assertTrue(result.amendment['needs_review'])
        self.assertFalse(server.queries)
        client.cleanup()

    def test_long_locator_still_queries_and_preserves_context(self):
        client, server = self.client()
        client.index(self.chunks)
        item = deepcopy(self.item)
        item['target_locator'] = 'x' * 8001
        result = build_context(item, self.registry, client, text_diff=self.diff)
        self.assertFalse(result.issues)
        self.assertEqual(len(server.queries), 1)
        self.assertLessEqual(len(server.queries[0]), MAX_QUERY_CHARS)
        self.assertEqual(result.amendment['target_locator'], item['target_locator'])
        validate_sources(result.amendment, self.registry.documents)
        client.cleanup()

    def test_sequential_wrapper_uses_diff_and_does_not_mutate_inputs(self):
        client, server = self.client()
        item, diff = deepcopy(self.item), deepcopy(self.diff)
        result = prepare_context(item, self.registry, client, text_diff=diff)
        self.assertFalse(result.issues)
        self.assertEqual(len(server.queries), 1)
        self.assertEqual(item, self.item)
        self.assertEqual(diff, self.diff)
        client.cleanup()

    def test_bridge_index_failure_skips_query_and_propagates_review(self):
        client, server = self.client()
        server.workspace = 'wrong'
        def forbidden_query(item, text):
            self.fail('Query must not run after index failure')
        def semantic(item, text):
            self.assertTrue(item['needs_review'])
            self.assertEqual(item['context'], self.item['context'])
            return deepcopy(self.fixture['report']['results'][0]['semantic_diff'])
        context, text, result = run_semantic_stage(
            self.item,
            context_prepare=lambda item: prepare_index(item, self.registry, client),
            context_work=forbidden_query, text_diff=compute_text_diff, semantic_diff=semantic)
        self.assertEqual(context.issues[0]['code'], 'SERVER_SCOPE_UNVERIFIED')
        self.assertTrue(result['needs_review'])
        self.assertIn('SERVER_SCOPE_UNVERIFIED', result['review_reason'])
        self.assertEqual(text, self.diff)
        self.assertFalse(server.queries)
        client.cleanup()

    def test_bridge_invalid_diff_stops_before_query_and_semantic(self):
        def forbidden(*args):
            self.fail('Invalid diff must not reach query or Semantic')
        wrong = deepcopy(self.diff)
        wrong['amendment_id'] = 'another'
        for diff in [None, wrong]:
            with self.subTest(diff=diff), self.assertRaises(ValueError):
                run_semantic_stage(
                    self.item,
                    context_prepare=lambda item: prepare_index(item, self.registry, None),
                    context_work=forbidden, text_diff=lambda item: diff, semantic_diff=forbidden)

    def test_bridge_retrieval_failure_reaches_semantic_as_review(self):
        client, server = self.client('empty')
        def semantic(item, text):
            self.assertEqual(item['context'], self.item['context'])
            self.assertTrue(item['needs_review'])
            self.assertEqual(text, self.diff)
            return deepcopy(self.fixture['report']['results'][0]['semantic_diff'])
        context, _, result = run_semantic_stage(
            self.item,
            context_prepare=lambda item: prepare_index(item, self.registry, client),
            context_work=lambda item, text: build_context(item, self.registry, client, text_diff=text),
            text_diff=compute_text_diff, semantic_diff=semantic)
        self.assertEqual(context.issues[0]['code'], 'RETRIEVAL_EMPTY_UNCONFIRMED')
        self.assertTrue(result['needs_review'])
        self.assertEqual(len(server.queries), 1)
        client.cleanup()

    def test_real_docx_parser_blocks_to_registry(self):
        from docx import Document
        from backend.app.pipeline import DocumentInput, parse_documents
        inputs = []
        for did, role in [("v1", "BASE"), ("s", "AMENDMENT")]:
            path = Path(self.temporary.name) / f"{did}.docx"
            document = Document()
            document.add_paragraph("Điều 1. Báo cáo")
            document.add_paragraph("Nội dung nguồn dùng kiểm thử.")
            document.save(path)
            inputs.append(DocumentInput(did, role, path.name, path))
        parsed = parse_documents(inputs, Path(self.temporary.name) / "work", monotonic() + 5)
        docs = documents_from_parsed(parsed)
        chunks = build_chunks("parser", docs, {"v1": "v1", "s": "s"})
        registry = SourceRegistry(chunks, docs)
        for chunk in chunks:
            evidence = registry.evidence({"file_path": chunk.file_source, "content": chunk.indexed_text})
            validate_sources(evidence, registry.documents)
        self.assertEqual(docs[0]["blocks"][0]["source_ref"], parsed[0].tree["source_blocks"][0]["source_ref"])

    def test_malformed_chunk_is_source_failure(self):
        for chunk in [None, "text", {"file_path": [], "content": "text"}]:
            with self.assertRaises(ValueError):
                self.registry.evidence(chunk)

    def test_foreign_comparison_ingestion_rejected(self):
        client, server = self.client()
        with self.assertRaisesRegex(RetrievalError, "INDEX_INPUT_INVALID"):
            client.index(build_chunks("another", self.documents, self.versions))
        self.assertFalse(server.calls)

    def test_response_limit(self):
        client, server = self.client()
        client.index(self.chunks)
        object.__setattr__(client.config, "max_response_bytes", 20)
        with self.assertRaisesRegex(RetrievalError, "RETRIEVAL_RESPONSE_LIMIT"):
            client.query("report deadline")

    def test_occupied_or_wrong_version_server_never_uploads(self):
        for index, behavior in enumerate(("occupied", "version")):
            client, server = self.client(url=f"http://localhost:{9800+index}")
            def handle(request, server=server, behavior=behavior):
                response = server(request)
                if request.url.path == "/documents/status_counts" and behavior == "occupied":
                    return httpx.Response(200, json={"status_counts": {"processed": 1}})
                if request.url.path == "/health" and behavior == "version":
                    data = response.json()
                    data["core_version"] = "unknown"
                    return httpx.Response(200, json=data)
                return response
            client.http.close()
            client.http = httpx.Client(base_url=client.config.base_url, transport=httpx.MockTransport(handle))
            with self.assertRaises(RetrievalError):
                client.index(self.chunks)
            self.assertNotIn(("POST", "/documents/texts"), server.calls)


if __name__ == "__main__":
    unittest.main()
